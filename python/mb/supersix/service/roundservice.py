from mylib.globals import get_global
from mylib.myodbc.public import MyOdbc

from mb.supersix.model import CurrentRound, Round

from .servicemixin import ServiceMixin


class RoundService(ServiceMixin):
    _db = "supersix"
    _table = "ROUNDS"
    _model_schema = ["id", "start_date", "end_date", "buy_in_pence", "winner_id"]

    def __init__(self):
        db_settings = get_global("dbs", self._db)

        self._driver = db_settings.get("driver")
        self._db = MyOdbc.connect(self._driver,
                                  self._db,
                                  db_settings.get("location"))

    def current_round(self):
        table = "CURRENT_ROUND"

        columns = {c: None for c in self._db.get_columns(table)}
        column_model = self._generate_column_model(self._driver, CurrentRound, columns)

        round = self._db.get(table, column_model)
        if not round:
            return None

        return CurrentRound(**round[0])

    def get(self, round_id):
        columns = {c: None for c in self._db.get_columns(self._table)}
        column_model = self._generate_column_model(self._driver, Round, columns)

        filters = {"id": round_id}
        filter_model = self._generate_filter_model(self._driver, Round, filters)

        round = self._db.get(self._table, column_model, filter_model=filter_model)
        if not round:
            return None

        return Round(**{k: round[0][k] for k in self._model_schema})

    def list(self, filters=None):
        columns = {c: None for c in self._db.get_columns(self._table)}
        column_model = self._generate_column_model(self._driver, Round, columns)

        filter_model = self._generate_filter_model(self._driver, Round, filters) if filters else None

        rounds = self._db.get(self._table, column_model, filter_model=filter_model)
        return [Round(**{k: r.get(k, None) for k in self._model_schema}) for r in rounds]

    def create(self, round):
        exists = self.get(round.id)
        if exists:
            raise ValueError(f"{round.id} already exists")

        round = round.to_dict()

        column_model = self._generate_column_model(self._driver, Round, round)

        round = self._db.insert_get(self._table, column_model)

        return self.get(round["id"])

    def update(self, round):
        round = round.to_dict()

        column_model = self._generate_column_model(self._driver, Round, round)

        self._db.update(self._table, column_model)

        return self.get(round["id"])
