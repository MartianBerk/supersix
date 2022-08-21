from datetime import datetime as Datetime, timedelta
from typing import List, Optional

from baked.lib.dbaccess.public import DbAccess, AndOrFilterModel
from baked.lib.globals import get_global
from baked.lib.supersix.model import Match, ScheduledMatch
from baked.lib.supersix.service.leagueservice import LeagueService

from .servicemixin import ServiceMixin


class MatchService(ServiceMixin):
    _db = "supersix"
    _table = "MATCHES"
    _model_schema = ["id", "external_id", "league_id", "matchday", "match_date", "match_minute", "status",
                     "home_team", "away_team", "use_match", "home_score", "away_score", "game_number"]

    def __init__(self):
        db_settings = get_global("dbs", self._db)

        self._driver = db_settings.get("driver")
        self._db = DbAccess.connect(self._driver,
                                    self._db,
                                    db_settings.get("location"))
        self._league_service = LeagueService()

    def get(self, match_id):
        columns = {c: None for c in self._db.get_columns(self._table)}
        column_model = self._generate_column_model(self._driver, Match, columns)

        filters = {"id": match_id}
        filter_model = self._generate_filter_model(self._driver, Match, filters)

        match = self._db.get(self._table, column_model, filter_model=filter_model)
        if not match:
            return None

        return Match(**{k: match[0][k] for k in self._model_schema})

    def get_from_external_id(self, external_id):
        columns = {c: None for c in self._db.get_columns(self._table)}
        column_model = self._generate_column_model(self._driver, Match, columns)

        filters = {"external_id": external_id}
        filter_model = self._generate_filter_model(self._driver, Match, filters)

        match = self._db.get(self._table, column_model, filter_model=filter_model)
        if not match:
            return None

        return Match(**{k: match[0][k] for k in self._model_schema})

    def list(self, filters=None):
        columns = {c: None for c in self._db.get_columns(self._table)}
        column_model = self._generate_column_model(self._driver, Match, columns)

        filter_model = self._generate_filter_model(self._driver, Match, filters) if filters else None

        matches = self._db.get(self._table, column_model, filter_model=filter_model)
        return [Match(**{k: m.get(k, None) for k in self._model_schema}) for m in matches]

    def create(self, match):
        exists = match.id and self.get(match.id)
        if exists:
            raise ValueError(f"[{match.matchday}] {match.home_team} vs {match.away_team} already exists")

        match = match.to_dict()

        column_model = self._generate_column_model(self._driver, Match, match)

        match = self._db.insert_get(self._table, column_model)

        return self.get(match["id"])

    def update(self, match):
        match = match.to_dict()

        column_model = self._generate_column_model(self._driver, Match, match)

        self._db.update(self._table, column_model)

        return self.get(match["id"])

    def team_performance(self, team: str, match_date: Datetime):
        columns = {c: None for c in self._db.get_columns(self._table)}
        column_model = self._generate_column_model(self._driver, Match, columns)

        # compile filters independently due to mixin limitations.
        column_class = self._get_column_class(self._driver)
        filter_class = self._get_filter_class(self._driver)

        filters = [
            filter_class(column_class("match_date", Match.get_sql_datatype("match_date"), match_date), "lessthan"),
            "and",
            filter_class(column_class("status", Match.get_sql_datatype("status"), "FINISHED"), "equalto"),
            "and",
            [
                filter_class(column_class("home_team", Match.get_sql_datatype("home_team"), team), "equalto"),
                "or",
                filter_class(column_class("away_team", Match.get_sql_datatype("away_team"), team), "equalto")
            ]
        ]

        filter_model = AndOrFilterModel(filters)

        matches = self._db.get(self._table, column_model, filter_model=filter_model)
        matches = [Match(**match) for match in matches]

        return [
            "WIN" if m.home_team == team and m.home_score > m.away_score else (
                "WIN" if m.away_team == team and m.away_score > m.home_score else (
                    "LOSE" if m.home_team == team and m.home_score < m.away_score else (
                        "LOSE" if m.away_team == team and m.away_score < m.home_score else "DRAW"
                    )
                )
            ) for m in matches[-5:]
        ]

    def head_to_head(self, home_team: str, away_team: str, match_date: Datetime):
        columns = {c: None for c in self._db.get_columns(self._table)}
        column_model = self._generate_column_model(self._driver, Match, columns)

        # compile filters independently due to mixin limitations.
        column_class = self._get_column_class(self._driver)
        filter_class = self._get_filter_class(self._driver)

        filters = [
            filter_class(column_class("match_date", Match.get_sql_datatype("match_date"), match_date), "lessthan"),
            "and",
            filter_class(column_class("status", Match.get_sql_datatype("status"), "FINISHED"), "equalto"),
            "and",
            [
                [
                    filter_class(column_class("home_team", Match.get_sql_datatype("home_team"), home_team), "equalto"),
                    "and",
                    filter_class(column_class("away_team", Match.get_sql_datatype("away_team"), away_team), "equalto")
                ],
                "or",
                [
                    filter_class(column_class("home_team", Match.get_sql_datatype("home_team"), away_team), "equalto"),
                    "and",
                    filter_class(column_class("away_team", Match.get_sql_datatype("away_team"), home_team), "equalto")
                ]
            ]
        ]

        filter_model = AndOrFilterModel(filters)

        matches = self._db.get(self._table, column_model, filter_model=filter_model)
        matches = [Match(**match) for match in matches]

        home_results = []
        away_results = []

        for match in matches[-5:]:
            if match.home_team == home_team and match.home_score > match.away_score:
                home_results.append("WIN")
                away_results.append("LOSE")
            elif match.away_team == home_team and match.away_score > match.home_score:
                home_results.append("WIN")
                away_results.append("LOSE")
            elif match.home_team == away_team and match.home_score > match.away_score:
                home_results.append("LOSE")
                away_results.append("WIN")
            elif match.away_team == away_team and match.away_score > match.home_score:
                home_results.append("LOSE")
                away_results.append("WIN")
            else:
                home_results.append("DRAW")
                away_results.append("DRAW")

        return home_results, away_results

    def match_detail(self, home_team: str, away_team: str, match_date: Datetime):
        # find league
        end_match_date = match_date + timedelta(days=1)
        matches = self.list([
            ("home_team", "equalto", home_team),
            ("away_team", "equalto", away_team),
            ("match_date", "greaterthan", match_date),
            ("match_date", "lessthan", end_match_date)
        ])
        if not matches:
            raise ValueError("Cannot find match.")

        league = self._league_service.get(matches[0].league_id)
        league_table = self._league_service.league_table(league.code)

        home_position, away_position = None, None
        for entry in league_table:
            if entry.team == home_team:
                home_position = entry.position
            elif entry.team == away_team:
                away_position = entry.position

            if home_position and away_position:
                break

        # TODO:
        #  add top & sort to db access.
        #  add paged iterator of sorts to db access (pending support in sqlite3??)

        home_head_to_head, away_head_to_head = self.head_to_head(home_team, away_team, match_date)

        return {
            "league_position": {
                home_team: home_position,
                away_team: away_position
            },
            "team_performance": {
                home_team: self.team_performance(home_team, match_date),
                away_team: self.team_performance(away_team, match_date)
            },
            "head_to_head": {
                home_team: home_head_to_head,
                away_team: away_head_to_head
            }
        }

    def scheduled_matches(self):
        """Get scheduled matches.
        
        Returns:
            List[ScheduledMatch].
        """
        view = "SCHEDULED_MATCHES"

        columns = {c: None for c in self._db.get_columns(view)}
        column_model = self._generate_column_model(self._driver, ScheduledMatch, columns)

        return [ScheduledMatch(**m) for m in self._db.get(view, column_model)]
