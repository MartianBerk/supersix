from baked.lib.dbaccess.public import DbAccess
from baked.lib.globals import get_global
from baked.lib.supersix.model import CurrentRound, HistoricRound, Round, RoundWinner

from .servicemixin import ServiceMixin


class RoundService(ServiceMixin):
    _db = "supersix"
    _table = "ROUNDS"
    _model_schema = ["id", "start_date", "end_date", "buy_in_pence", "winners"]

    def __init__(self):
        db_settings = get_global("dbs", self._db)

        self._driver = db_settings.get("driver")
        self._db = DbAccess.connect(self._driver,
                                    self._db,
                                    db_settings.get("location"))

    def _merge_winners(self, round):
        table = "ROUND_WINNERS"

        columns = {c: None for c in self._db.get_columns(table)}
        column_model = self._generate_column_model(self._driver, RoundWinner, columns)

        winners = self._db.get(table, column_model)
        if winners:
            round.winners = winners

        return round

    def current_round(self):
        table = "CURRENT_ROUND"

        columns = {c: None for c in self._db.get_columns(table)}
        column_model = self._generate_column_model(self._driver, CurrentRound, columns)

        round = self._db.get(table, column_model)
        if not round:
            return None

        return CurrentRound(**round[0])

    def historic_rounds(self):
        table = "HISTORIC_ROUNDS"

        columns = {c: None for c in self._db.get_columns(table)}
        column_model = self._generate_column_model(self._driver, HistoricRound, columns)

        rounds = self._db.get(table, column_model)

        return [HistoricRound(**r) for r in rounds]

    def get(self, round_id):
        columns = {c: None for c in self._db.get_columns(self._table)}
        column_model = self._generate_column_model(self._driver, Round, columns)

        filters = {"id": round_id}
        filter_model = self._generate_filter_model(self._driver, Round, filters)

        round = self._db.get(self._table, column_model, filter_model=filter_model)
        if not round:
            return None

        round = Round(**round[0])
        round = self._merge_winners(round)

        return Round(**{k: round[k] for k in self._model_schema})

    def list(self, filters=None):
        columns = {c: None for c in self._db.get_columns(self._table)}
        column_model = self._generate_column_model(self._driver, Round, columns)

        filter_model = self._generate_filter_model(self._driver, Round, filters) if filters else None

        rounds = self._db.get(self._table, column_model, filter_model=filter_model)

        for round in rounds:
            round = Round(**round)
            self._merge_winners(round)

        return [Round(**{k: r.get(k, None) for k in self._model_schema}) for r in rounds]

    def create(self, round):
        exists = self.get(round.id)
        if exists:
            raise ValueError(f"{round.id} already exists")

        round = round.to_dict()

        column_model = self._generate_column_model(self._driver, Round, round)

        round = self._db.insert_get(self._table, column_model)

        return self.get(round["id"])

    # TODO: decommission
    def update(self, round):
        round = round.to_dict()

        column_model = self._generate_column_model(self._driver, Round, round)

        self._db.update(self._table, column_model)

        return self.get(round["id"])

    # TODO: Allow bulk submission to DB
    def end(self, round, round_winners):
        round = round.to_dict()
        column_model = self._generate_column_model(self._driver, Round, round)
        self._db.update(self._table, column_model)

        round_winners = [rw.to_dict() for rw in round_winners]
        for rw in round_winners:
            column_model = self._generate_column_model(self._driver, RoundWinner, rw)
            self._db.update("ROUND_WINNERS", column_model)

        return self.get(round["id"])
