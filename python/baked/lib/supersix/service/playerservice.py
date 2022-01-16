from baked.lib.dbaccess.public import DbAccess
from baked.lib.globals import get_global
from baked.lib.supersix.model import MaxPlayerId, Player, PlayerXref
from baked.lib.supersix.service.metaservice import MetaService

from .servicemixin import ServiceMixin


class PlayerService(ServiceMixin):
    _db = "supersix"
    _table = "PLAYERS"
    _model_schema = ["id", "first_name", "last_name", "join_date"]

    def __init__(self):
        db_settings = get_global("dbs", self._db)

        self._driver = db_settings.get("driver")
        self._db = DbAccess.connect(self._driver,
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

    def next_available_id(self):
        table = "MAX_PLAYER_ID"
        columns = {c: None for c in self._db.get_columns(table)}
        column_model = self._generate_column_model(self._driver, MaxPlayerId, columns)

        max_player = self._db.get(table, column_model)[0]

        return max_player["id"] + 1

    def update_player_nickname(self, player_id, nickname):
        player = self.get(player_id)

        if not player:
            return None

        xref = PlayerXref(player_name=f"{player.first_name} {player.last_name}", xref=nickname)

        MetaService().update_player_xref(xref)

        return player
