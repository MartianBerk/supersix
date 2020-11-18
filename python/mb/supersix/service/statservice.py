from mylib.globals import get_global
from mylib.myodbc.public import MyOdbc

from mb.supersix.model import StatAggregate

from .servicemixin import ServiceMixin


class StatService(ServiceMixin):
    _db = "supersix"

    def __init__(self):
        db_settings = get_global("dbs", self._db)

        self._driver = db_settings.get("driver")
        self._db = MyOdbc.connect(self._driver,
                                  self._db,
                                  db_settings.get("location"))

    def aggregate_stats(self, start_date=None, end_date=None):
        table = "PLAYER_STATS_AGG"

        columns = {c: None for c in self._db.get_columns(table)}
        column_model = self._generate_column_model(self._driver, StatAggregate, columns)

        filters = []

        if start_date:
            filters.append(("match_date", "greaterthanequalto", start_date))

        if end_date:
            filters.append(("match_date", "lessthanequalto", end_date))

        filter_model = self._generate_filter_model(self._driver, StatAggregate, filters) if filters else None

        stats = self._db.get(table, column_model, filter_model=filter_model)
        return [StatAggregate(**s) for s in stats]
