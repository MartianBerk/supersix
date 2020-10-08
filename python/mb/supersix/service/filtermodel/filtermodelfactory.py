from .dictfiltermodel import DictFilterModel
from .listtuplefiltermodel import ListTupleFilterModel


class FilterModelFactory:
    @staticmethod
    def _get_class(data):
        if isinstance(data, dict):
            return DictFilterModel

        if isinstance(data, list):
            if all(isinstance(d, tuple) and len(d) == 3 for d in data):
                return ListTupleFilterModel

        raise TypeError("columns/filters datatype is unknown")

    @staticmethod
    def get_columns(columns):
        return FilterModelFactory._get_class(columns).columns(columns)

    @staticmethod
    def get_filters(filters):
        return FilterModelFactory._get_class(filters).filters(filters)
