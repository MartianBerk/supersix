from mylib.globals import get_global
from mylib.myodbc.public import ColumnFactory, ColumnModelFactory, FilterFactory, AndFilterModel, MyOdbc

from mb.supersix.model import League


class LeagueService:
    _db = "supersix"
    _table = "LEAGUES"
    _model_schema = ["id", "name", "start_date", "code", "current_matchday"]

    def __init__(self):
        db_settings = get_global("dbs", self._db)

        self._driver = db_settings.get("driver")
        self._db = MyOdbc.connect(self._driver,
                                  self._db,
                                  db_settings.get("location"))

    def _generate_column_model(self, columns):
        column_class = ColumnFactory.get(self._driver)

        columns = [column_class(c, League.get_sql_datatype(c), value=v) for c, v in columns.items()]
        return ColumnModelFactory.get(self._driver)(columns)

    def _generate_filter_model(self, filters):
        column_model = self._generate_column_model(filters)
        filter_class = FilterFactory.get(self._driver)

        filters = [filter_class(c, "equalto") for c in column_model.columns]
        return AndFilterModel(filters)

    def get(self, league_id):
        columns = {c: None for c in self._db.get_columns(self._table)}
        column_model = self._generate_column_model(columns)

        filters = {"id": league_id}
        filter_model = self._generate_filter_model(filters)

        league = self._db.get(self._table, column_model, filter_model=filter_model)
        if not league:
            return None

        return League(**{k: league[0][k] for k in self._model_schema})

    def get_from_league_code(self, code):
        columns = {c: None for c in self._db.get_columns(self._table)}
        column_model = self._generate_column_model(columns)

        filters = {"code": code}
        filter_model = self._generate_filter_model(filters)

        league = self._db.get(self._table, column_model, filter_model=filter_model)
        if not league:
            return None

        return League(**{k: league[0][k] for k in self._model_schema})

    def list(self, filters=None):
        if filters and not isinstance(filters, dict):
            raise TypeError("filters must be None or a dict")

        columns = {c: None for c in self._db.get_columns(self._table)}
        column_model = self._generate_column_model(columns)

        filter_model = self._generate_filter_model(filters) if filters else None

        leagues = self._db.get(self._table, column_model, filter_model=filter_model)
        return [League(**{k: l.get(k, None) for k in self._model_schema}) for l in leagues]

    def create(self, league):
        exists = league.id and self.get(league.id)
        if exists:
            raise ValueError(f"{league.name} already exists")

        league = league.to_dict()

        column_model = self._generate_column_model(league)

        league = self._db.insert_get(self._table, column_model)

        return self.get(league["id"])

    def update(self, league):
        league = league.to_dict()

        column_model = self._generate_column_model(league)

        self._db.update(self._table, column_model)

        return self.get(league["id"])
