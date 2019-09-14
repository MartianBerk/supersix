from mylib.globals import get_global
from mylib.myodbc import MyOdbc

from mylib.supersix.model import League


class LeagueService:
    _db = "SUPERSIX"
    _table = "LEAGUES"
    _model_schema = ["id", "name", "start_date", "code", "current_matchday"]

    def __init__(self):
        db_settings = get_global("dbs", self._db)

        self._db = MyOdbc.connect(db_settings.get("driver"),
                                  self._db,
                                  db_settings.get("location"))

    def get(self, league_id):
        league = self._db.get(self._table, where={"id": league_id})
        if not league:
            return None

        return League(**{k: league[0][k] for k in self._model_schema})

    def list(self, columns=None, filters=None):
        if columns and not isinstance(columns, list):
            raise TypeError("columns must be None or a list")

        if filters and not isinstance(filters, dict):
            raise TypeError("filters must be None or a dict")

        leagues = self._db.get(self._table, columns=columns, where=filters)
        return [League(**{k: l[k] for k in self._model_schema}) for l in leagues]

    def create(self, league):
        exists = self.get(league.id)
        if exists:
            raise ValueError(f"{league.name} already exists")

        self._db.upsert(self._table, league.to_dict())
