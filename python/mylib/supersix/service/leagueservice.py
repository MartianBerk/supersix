from mylib.globals import get_global
from mylib.myodbc import MyOdbc


class LeagueService:
    _db = "SUPERSIX"
    _table = "LEAGUES"

    def __init__(self):
        db_settings = get_global("dbs", self._db)

        self._db = MyOdbc.connect(db_settings.get("driver"),
                                  self._db,
                                  db_settings.get("location"))

    def get(self, league):
        return self._db.get(self._table, where={"id": league.id})

    def list(self):
        return self._db.get(self._table)

    def create(self, league):
        exists = self.get(league)
        if exists:
            raise ValueError(f"{league.name} already exists")

        self._db.upsert(self._table, league.to_dict())
