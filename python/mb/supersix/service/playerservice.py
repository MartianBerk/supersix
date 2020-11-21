from mylib.globals import get_global
from mylib.myodbc.public import MyOdbc

from mb.supersix.model import Player

from .servicemixin import ServiceMixin


class PlayerService(ServiceMixin):
    _db = "supersix"
    _table = "PLAYERS"
    _model_schema = ["id", "first_name", "last_name", "nickname", "join_date"]

    def __init__(self):
        db_settings = get_global("dbs", self._db)

        self._driver = db_settings.get("driver")
        self._db = MyOdbc.connect(self._driver,
                                  self._db,
                                  db_settings.get("location"))

    def get(self, player_id):
        columns = {c: None for c in self._db.get_columns(self._table)}
        column_model = self._generate_column_model(self._driver, Player, columns)

        filters = {"id": player_id}
        filter_model = self._generate_filter_model(self._driver, Player, filters)

        player = self._db.get(self._table, column_model, filter_model=filter_model)
        if not player:
            return None

        return Player(**{k: player[0][k] for k in self._model_schema})

    def list(self, filters=None):
        if filters and not isinstance(filters, dict):
            raise TypeError("filters must be None or a dict")

        columns = {c: None for c in self._db.get_columns(self._table)}
        column_model = self._generate_column_model(self._driver, Player, columns)

        filter_model = self._generate_filter_model(self._driver, Player, filters) if filters else None

        players = self._db.get(self._table, column_model, filter_model=filter_model)
        return [Player(**{k: p.get(k, None) for k in self._model_schema}) for p in players]

    def create(self, player):
        exists = player.id and self.get(player.id)
        if exists:
            raise ValueError(f"{player.id} already exists")

        player = player.to_dict()

        column_model = self._generate_column_model(self._driver, Player, player)

        player = self._db.insert_get(self._table, column_model)

        return self.get(player["id"])

    def update(self, player):
        player = player.to_dict()

        column_model = self._generate_column_model(self._driver, Player, player)

        self._db.update(self._table, column_model)

        return self.get(player["id"])
