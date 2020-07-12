from mylib.globals import get_global
from mylib.myodbc import MyOdbc

from mb.supersix.model import Player


class PlayerService:
    _db = "supersix"
    _table = "PLAYERS"
    _model_schema = ["id", "first_name", "last_name", "join_date"]

    def __init__(self):
        db_settings = get_global("dbs", self._db)

        self._db = MyOdbc.connect(db_settings.get("driver"),
                                  self._db,
                                  db_settings.get("location"))

    def get(self, player_id):
        player = self._db.get(self._table, where={"id": player_id})
        if not player:
            return None

        return Player(**{k: player[0][k] for k in self._model_schema})

    def list(self, filters=None):
        if filters and not isinstance(filters, dict):
            raise TypeError("filters must be None or a dict")

        players = self._db.get(self._table, where=filters)
        return [Player(**{k: p.get(k, None) for k in self._model_schema}) for p in players]

    def create(self, player):
        exists = self.get(player.id)
        if exists:
            raise ValueError(f"{player.id} already exists")

        self._db.upsert(self._table, player.to_dict())

        return self.get(player.id)

    def update(self, player):
        self._db.upsert(self._table, player.to_dict())

        return self.get(player.id)
