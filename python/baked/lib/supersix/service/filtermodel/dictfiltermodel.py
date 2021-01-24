from .ifiltermodel import IFilterModel
from .model import Column, Filter


class DictFilterModel(IFilterModel):
    @staticmethod
    def columns(filters):
        return [Column(k, v) for k, v in filters.items()]

    @staticmethod
    def filters(filters):
        return [Filter(k, "equalto", v) for k, v in filters.items()]
