from baked.lib.dbaccess.public import (ColumnFactory,
                                       ColumnModelFactory,
                                       FilterFactory,
                                       AndFilterModel,
                                       AndOrFilterModel,
                                       OrFilterModel)

from .filtermodel.filtermodelfactory import FilterModelFactory


class ServiceMixin:

    def _generate_column_model(self, driver, model, columns):
        columns = FilterModelFactory.get_columns(columns)
        column_class = ColumnFactory.get(driver)

        columns = [column_class(c.column, model.get_sql_datatype(c.column), value=c.value) for c in columns]
        return ColumnModelFactory.get(driver)(columns)

    def _get_column_class(self, driver):
        return ColumnFactory.get(driver)

    def _get_filter_class(self, driver):
        return FilterFactory.get(driver)

    def _generate_filter_model(self, driver, model, filters, model_type="and"):
        filter_class = FilterFactory.get(driver)

        column_model = self._generate_column_model(driver, model, filters)

        filters = FilterModelFactory.get_filters(filters)
        filters = [filter_class(column_model.columns[i], f.operator) for i, f in enumerate(filters)]

        if model_type == "and":
            return AndFilterModel(filters)
        elif model_type == "or":
            return OrFilterModel(filters)

        raise ValueError("unknown model_type")
