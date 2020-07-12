from mylib.globals import get_global
from mylib.myodbc import MyOdbc

from mb.supersix.model import Round


class RoundService:
    _db = "supersix"
    _table = "ROUNDS"
    _model_schema = ["id", "start_date", "end_date", "buy_in_pence", "winner_id"]

    def __init__(self):
        db_settings = get_global("dbs", self._db)

        self._db = MyOdbc.connect(db_settings.get("driver"),
                                  self._db,
                                  db_settings.get("location"))

    def get(self, round_id):
        round = self._db.get(self._table, where={"id": round_id})
        if not round:
            return None

        return Round(**{k: round[0][k] for k in self._model_schema})

    def list(self, filters=None):
        if filters and not isinstance(filters, dict):
            raise TypeError("filters must be None or a dict")

        rounds = self._db.get(self._table, where=filters)
        return [Round(**{k: r.get(k, None) for k in self._model_schema}) for r in rounds]

    def create(self, round):
        exists = self.get(round.id)
        if exists:
            raise ValueError(f"{round.id} already exists")

        self._db.upsert(self._table, round.to_dict())

        return self.get(round.id)

    def update(self, round):
        self._db.upsert(self._table, round.to_dict())

        return self.get(round.id)
