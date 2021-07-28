from datetime import datetime as Datetime

from baked.lib.dbaccess.public import DbAccess, AndOrFilterModel
from baked.lib.globals import get_global
from baked.lib.supersix.model import LeagueTable, Match

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

    def league_table(self, season: str, league: str):
        table = "LEAGUE_TABLE"

        columns = {c: None for c in self._db.get_columns(table)}
        column_model = self._generate_column_model(self._driver, LeagueTable, columns)

        filters = {"season": season, "league": league}
        filter_model = self._generate_filter_model(self._driver, LeagueTable, filters)

        league_table = self._db.get(table, column_model, filter_model=filter_model)
        if not league_table:
            return []

        return [LeagueTable(position=i, **entry) for i, entry in enumerate(league_table)]

    def team_performance(self, team: str, match_date: Datetime):
        columns = {c: None for c in self._db.get_columns(self._table)}
        column_model = self._generate_column_model(self._driver, Match, columns)

        # compile filters independently due to mixin limitations.
        column_class = self._get_column_class(self._driver)
        filter_class = self._get_filter_class(self._driver)

        filters = [
            filter_class(column_class("match_date", Match.get_sql_datatype("match_date"), match_date), "lessthan"),
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
        matches.sort(key=lambda m: m.match_date, reverse=True)

        return [
            "WIN" if m.home_team == team and m.home_score > m.away_score else (
                "WIN" if m.away_team == team and m.away_score > m.home_score else (
                    "LOSE" if m.home_team == team and m.home_score < m.away_score else (
                        "LOSE" if m.away_team == team and m.away_score < m.home_score else "DRAW"
                    )
                )
            ) for m in matches[0: 5]
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
        matches.sort(key=lambda m: m.match_date, reverse=True)

        home_results = []
        away_results = []

        for match in matches[0: 5]:
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

    def match_detail(self, season: str, league: str, home_team: str, away_team: str, match_date: Datetime):
        league_table = self.league_table(season, league)

        home_position, away_position = None, None
        for entry in league_table:
            if entry.team == home_team:
                home_position = entry.position
            elif entry.team == away_team:
                away_position = entry.position

            if home_position and away_position:
                break

        # TODO: team_performance and head_to_head:
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
