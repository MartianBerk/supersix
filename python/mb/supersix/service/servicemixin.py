from mylib.myodbc.public import ColumnFactory, ColumnModelFactory, FilterFactory, AndFilterModel

from .filtermodel.filtermodelfactory import FilterModelFactory


class ServiceMixin:

    def _generate_column_model(self, driver, model, columns):
        columns = FilterModelFactory.get_columns(columns)
        column_class = ColumnFactory.get(driver)

        columns = [column_class(c.column, model.get_sql_datatype(c.column), value=c.value) for c in columns]
        return ColumnModelFactory.get(driver)(columns)

    def _generate_filter_model(self, driver, model, filters):
        column_model = self._generate_column_model(driver, model, filters)
        filter_class = FilterFactory.get(driver)

        filters = FilterModelFactory.get_filters(filters)
        filters = [filter_class(column_model.columns[i], f.operator) for i, f in enumerate(filters)]
        return AndFilterModel(filters)
