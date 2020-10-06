from mylib.myodbc.public import ColumnFactory, ColumnModelFactory, FilterFactory, AndFilterModel

from mb.supersix.model import Match


class ServiceMixin:

    def _generate_column_model(self, driver, columns):
        column_class = ColumnFactory.get(driver)

        columns = [column_class(c, Match.get_sql_datatype(c), value=v) for c, v in columns.items()]
        return ColumnModelFactory.get(driver)(columns)

    def _generate_filter_model(self, driver, filters):
        column_model = self._generate_column_model(driver, filters)
        filter_class = FilterFactory.get(driver)

        filters = [filter_class(c, "equalto") for c in column_model.columns]
        return AndFilterModel(filters)
