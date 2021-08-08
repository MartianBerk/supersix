from baked.lib.dbaccess.public import DbAccess
from baked.lib.globals import get_global
from baked.lib.supersix.model import League, LeagueTable

from .servicemixin import ServiceMixin


class LeagueService(ServiceMixin):
    _db = "supersix"
    _table = "LEAGUES"
    _model_schema = ["id", "name", "start_date", "code", "current_matchday"]

    def __init__(self):
        db_settings = get_global("dbs", self._db)

        self._driver = db_settings.get("driver")
        self._db = DbAccess.connect(self._driver,
                                    self._db,
                                    db_settings.get("location"))

    def get(self, league_id):
        columns = {c: None for c in self._db.get_columns(self._table)}
        column_model = self._generate_column_model(self._driver, League, columns)

        filters = {"id": league_id}
        filter_model = self._generate_filter_model(self._driver, League, filters)

        league = self._db.get(self._table, column_model, filter_model=filter_model)
        if not league:
            return None

        return League(**{k: league[0][k] for k in self._model_schema})

    def get_from_league_code(self, code):
        columns = {c: None for c in self._db.get_columns(self._table)}
        column_model = self._generate_column_model(self._driver, League, columns)

        filters = {"code": code}
        filter_model = self._generate_filter_model(self._driver, League, filters)

        league = self._db.get(self._table, column_model, filter_model=filter_model)
        if not league:
            return None

        return League(**{k: league[0][k] for k in self._model_schema})

    def list(self, filters=None):
        if filters and not isinstance(filters, dict):
            raise TypeError("filters must be None or a dict")

        columns = {c: None for c in self._db.get_columns(self._table)}
        column_model = self._generate_column_model(self._driver, League, columns)

        filter_model = self._generate_filter_model(self._driver, League, filters) if filters else None

        leagues = self._db.get(self._table, column_model, filter_model=filter_model)
        return [League(**{k: l.get(k, None) for k in self._model_schema}) for l in leagues]

    def create(self, league):
        exists = league.id and self.get(league.id)
        if exists:
            raise ValueError(f"{league.name} already exists")

        league = league.to_dict()

        column_model = self._generate_column_model(self._driver, League, league)

        league = self._db.insert_get(self._table, column_model)

        return self.get(league["id"])

    def update(self, league):
        league = league.to_dict()

        column_model = self._generate_column_model(self._driver, League, league)

        self._db.update(self._table, column_model)

        return self.get(league["id"])

    def league_table(self, league_code: str, season: str = None):
        table = "LEAGUE_TABLE"

        # use current season if not supplied
        if not season:
            league = self.get_from_league_code(league_code)
            season = "/".join([league.start_date.strftime("%Y"), str(int(league.start_date.strftime("%y")) + 1)])

        columns = {c: None for c in self._db.get_columns(table)}
        column_model = self._generate_column_model(self._driver, LeagueTable, columns)

        filters = {"season": season, "league": league_code}
        filter_model = self._generate_filter_model(self._driver, LeagueTable, filters)

        league_table = self._db.get(table, column_model, filter_model=filter_model)
        if not league_table:
            return []

        # calculate position based on points/goal_difference against nearest neighbour.
        complete_league_table = []
        for i, team in enumerate(league_table):
            if all([i > 0,
                    league_table[i-1]["points"] == team["points"],
                    league_table[i-1]["goal_difference"] == team["goal_difference"]]):
                team["position"] = league_table[i-1]['position']

                if not league_table[i-1]['position'].startswith("T"):
                    league_table[i-1]["position"] = f"T{league_table[i-1]['position']}"
                    complete_league_table[-1] = LeagueTable(**league_table[i-1])
            else:
                team["position"] = str(i + 1)

            complete_league_table.append(LeagueTable(**team))

        return complete_league_table
