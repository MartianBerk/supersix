from baked.lib.dbaccess import DbAccess
from baked.lib.globals import get_global
from baked.lib.supersix.model import MatchPrediction, Prediction

from .servicemixin import ServiceMixin


class PredictionService(ServiceMixin):
    _db = "supersix"
    _table = "PREDICTIONS"
    _model_schema = ["id", "round_id", "player_id", "match_id", "prediction", "drop"]

    def __init__(self):
        db_settings = get_global("dbs", self._db)

        self._driver = db_settings.get("driver")
        self._db = DbAccess.connect(self._driver,
                                    self._db,
                                    db_settings.get("location"))

    def get(self, prediction_id):
        columns = {c: None for c in self._db.get_columns(self._table)}
        column_model = self._generate_column_model(self._driver, Prediction, columns)

        filters = {"id": prediction_id}
        filter_model = self._generate_filter_model(self._driver, Prediction, filters)

        prediction = self._db.get(self._table, column_model, filter_model=filter_model)
        if not prediction:
            return None

        return Prediction(**{k: prediction[0][k] for k in self._model_schema})

    def prediction_exists(self, round_id, match_id, player_id):
        columns = {c: None for c in self._db.get_columns(self._table)}
        column_model = self._generate_column_model(self._driver, Prediction, columns)

        filters = {"round_id": round_id,
                   "match_id": match_id,
                   "player_id": player_id}
        filter_model = self._generate_filter_model(self._driver, Prediction, filters)

        predictions = self._db.get(self._table, column_model, filter_model=filter_model)
        if predictions:
            return self.get(predictions[0]["id"])

        return None

    def list(self, filters=None):
        if filters and not isinstance(filters, dict):
            raise TypeError("filters must be None or a dict")

        columns = {c: None for c in self._db.get_columns(self._table)}
        column_model = self._generate_column_model(self._driver, Prediction, columns)

        filter_model = self._generate_filter_model(self._driver, Prediction, filters) if filters else None

        predictions = self._db.get(self._table, column_model, filter_model=filter_model)
        return [Prediction(**{k: p.get(k, None) for k in self._model_schema}) for p in predictions]

    def list_match_predictions(self, filters=None):
        table = "MATCHPREDICTIONS"

        if filters and not isinstance(filters, dict):
            raise TypeError("filters must be None or a dict")

        columns = {c: None for c in self._db.get_columns(table)}
        column_model = self._generate_column_model(self._driver, MatchPrediction, columns)

        filter_model = self._generate_filter_model(self._driver, MatchPrediction, filters) if filters else None

        predictions = self._db.get(table, column_model, filter_model=filter_model)
        return [MatchPrediction(**{k: p.get(k, None) for k in self._model_schema}) for p in predictions]

    def create(self, prediction):
        exists = prediction.id and self.get(prediction.id)
        if exists:
            raise ValueError(f"{prediction.id} already exists")

        prediction = prediction.to_dict()

        column_model = self._generate_column_model(self._driver, Prediction, prediction)

        prediction = self._db.insert_get(self._table, column_model)

        return self.get(prediction["id"])

    def update(self, prediction):
        prediction = prediction.to_dict()

        column_model = self._generate_column_model(self._driver, Prediction, prediction)

        self._db.update(self._table, column_model)

        return self.get(prediction["id"])
