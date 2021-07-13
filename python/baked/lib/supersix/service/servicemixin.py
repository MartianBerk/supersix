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

    def _generate_filter_model(self, driver, model, filters, model_type="and"):
        filter_class = FilterFactory.get(driver)

        # TODO: this can be cleaner - refactor all filtering to handle and, or and and/or
        # special filter constructor for and/or
        if model_type == "andor":
            filter_model_filters = []
            for filter in filters:
                if isinstance(filter, str):
                    filter_model_filters.append(filter)
                else:
                    column_model = self._generate_column_model(driver, model, filter)

                    filtered = FilterModelFactory.get_filters(filter)
                    filtered = [filter_class(column_model.columns[i], f.operator) for i, f in enumerate(filtered)]

                    sub_filter_model_filters = []
                    for i, filter in enumerate(filtered):
                        sub_filter_model_filters.extend([filter, "and"] if i < len(filtered) - 1 else [filter])

                    filter_model_filters.append(sub_filter_model_filters)

            return AndOrFilterModel(filter_model_filters)

        column_model = self._generate_column_model(driver, model, filters)

        filters = FilterModelFactory.get_filters(filters)
        filters = [filter_class(column_model.columns[i], f.operator) for i, f in enumerate(filters)]

        if model_type == "and":
            return AndFilterModel(filters)
        elif model_type == "or":
            return OrFilterModel(filters)

        raise ValueError("unknown model_type")
