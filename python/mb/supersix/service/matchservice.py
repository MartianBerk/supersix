from mylib.globals import get_global
from mylib.myodbc.public import MyOdbc

from mb.supersix.model import Match

from .servicemixin import ServiceMixin


class MatchService(ServiceMixin):
    _db = "supersix"
    _table = "MATCHES"
    _model_schema = ["id", "external_id", "league_id", "matchday", "match_date", "match_minute", "status",
                     "home_team", "away_team", "use_match", "home_score", "away_score"]

    def __init__(self):
        db_settings = get_global("dbs", self._db)

        self._driver = db_settings.get("driver")
        self._db = MyOdbc.connect(self._driver,
                                  self._db,
                                  db_settings.get("location"))

    def get(self, match_id):
        columns = {c: None for c in self._db.get_columns(self._table)}
        column_model = self._generate_column_model(self._driver, Match, columns)

        filters = {"id": match_id}
        filter_model = self._generate_filter_model(self._driver, Match, filters)

        match = self._db.get(self._table, column_model, filter_model=filter_model)
        if not match:
            return None

        return Match(**{k: match[0][k] for k in self._model_schema})

    def get_from_external_id(self, external_id):
        columns = {c: None for c in self._db.get_columns(self._table)}
        column_model = self._generate_column_model(self._driver, Match, columns)

        filters = {"external_id": external_id}
        filter_model = self._generate_filter_model(self._driver, Match, filters)

        match = self._db.get(self._table, column_model, filter_model=filter_model)
        if not match:
            return None

        return Match(**{k: match[0][k] for k in self._model_schema})

    def list(self, filters=None):
        columns = {c: None for c in self._db.get_columns(self._table)}
        column_model = self._generate_column_model(self._driver, Match, columns)

        filter_model = self._generate_filter_model(self._driver, Match, filters) if filters else None

        matches = self._db.get(self._table, column_model, filter_model=filter_model)
        return [Match(**{k: m.get(k, None) for k in self._model_schema}) for m in matches]

    def create(self, match):
        exists = match.id and self.get(match.id)
        if exists:
            raise ValueError(f"[{match.matchday}] {match.home_team} vs {match.away_team} already exists")

        match = match.to_dict()

        column_model = self._generate_column_model(self._driver, Match, match)

        match = self._db.insert_get(self._table, column_model)

        return self.get(match["id"])

    def update(self, match):
        match = match.to_dict()

        column_model = self._generate_column_model(self._driver, Match, match)

        self._db.update(self._table, column_model)

        return self.get(match["id"])
