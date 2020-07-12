from mylib.globals import get_global
from mylib.myodbc import MyOdbc

from mb.supersix.model import Prediction


class PredictionService:
    _db = "supersix"
    _table = "PREDICTIONS"
    _model_schema = ["id", "round_id", "player_id", "match_id", "prediction"]

    def __init__(self):
        db_settings = get_global("dbs", self._db)

        self._db = MyOdbc.connect(db_settings.get("driver"),
                                  self._db,
                                  db_settings.get("location"))

    def get(self, prediction_id):
        prediction = self._db.get(self._table, where={"id": prediction_id})
        if not prediction:
            return None

        return Prediction(**{k: prediction[0][k] for k in self._model_schema})

    def list(self, filters=None):
        if filters and not isinstance(filters, dict):
            raise TypeError("filters must be None or a dict")

        predictions = self._db.get(self._table, where=filters)
        return [Prediction(**{k: p.get(k, None) for k in self._model_schema}) for p in predictions]

    def create(self, prediction):
        exists = self.get(prediction.id)
        if exists:
            raise ValueError(f"{prediction.id} already exists")

        self._db.upsert(self._table, prediction.to_dict())

        return self.get(prediction.id)

    def update(self, prediction):
        self._db.upsert(self._table, prediction.to_dict())

        return self.get(prediction.id)
