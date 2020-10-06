from mylib.myodbc.public import ColumnFactory, ColumnModelFactory, FilterFactory, AndFilterModel


class ServiceMixin:

    def _generate_column_model(self, driver, model, columns):
        column_class = ColumnFactory.get(driver)

        columns = [column_class(c, model.get_sql_datatype(c), value=v) for c, v in columns.items()]
        return ColumnModelFactory.get(driver)(columns)

    def _generate_filter_model(self, driver, model, filters):
        column_model = self._generate_column_model(driver, model, filters)
        filter_class = FilterFactory.get(driver)

        filters = [filter_class(c, "equalto") for c in column_model.columns]
        return AndFilterModel(filters)
