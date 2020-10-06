from mylib.globals import get_global
from mylib.myodbc.public import ColumnFactory, ColumnModelFactory, FilterFactory, AndFilterModel, MyOdbc

from mb.supersix.model import Match


class MatchService:
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

    def _generate_column_model(self, columns):
        column_class = ColumnFactory.get(self._driver)

        columns = [column_class(c, Match.get_sql_datatype(c), value=v) for c, v in columns.items()]
        return ColumnModelFactory.get(self._driver)(columns)

    def _generate_filter_model(self, filters):
        column_model = self._generate_column_model(filters)
        filter_class = FilterFactory.get(self._driver)

        filters = [filter_class(c, "equalto") for c in column_model.columns]
        return AndFilterModel(filters)

    def get(self, match_id):
        columns = {c: None for c in self._db.get_columns(self._table)}
        column_model = self._generate_column_model(columns)

        filters = {"id": match_id}
        filter_model = self._generate_filter_model(filters)

        match = self._db.get(self._table, column_model, filter_model=filter_model)
        if not match:
            return None

        return Match(**{k: match[0][k] for k in self._model_schema})

    def get_from_external_id(self, external_id):
        columns = {c: None for c in self._db.get_columns(self._table)}
        column_model = self._generate_column_model(columns)

        filters = {"external_id": external_id}
        filter_model = self._generate_filter_model(filters)

        match = self._db.get(self._table, column_model, filter_model=filter_model)
        if not match:
            return None

        return Match(**{k: match[0][k] for k in self._model_schema})

    def list(self, filters=None):
        if filters and not isinstance(filters, dict):
            raise TypeError("filters must be None or a dict")

        columns = {c: None for c in self._db.get_columns(self._table)}
        column_model = self._generate_column_model(columns)

        filter_model = self._generate_filter_model(filters) if filters else None

        matches = self._db.get(self._table, column_model, filter_model=filter_model)
        return [Match(**{k: m.get(k, None) for k in self._model_schema}) for m in matches]

    def create(self, match):
        exists = match.id and self.get(match.id)
        if exists:
            raise ValueError(f"[{match.matchday}] {match.home_team} vs {match.away_team} already exists")

        match = match.to_dict()

        column_model = self._generate_column_model(match)

        match = self._db.insert_get(self._table, column_model)

        return self.get(match["id"])

    def update(self, match):
        match = match.to_dict()

        column_model = self._generate_column_model(match)

        self._db.upsert(self._table, column_model)

        return self.get(match["id"])
