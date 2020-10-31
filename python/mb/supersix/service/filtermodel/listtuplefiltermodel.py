from .ifiltermodel import IFilterModel
from .model import Column, Filter


class ListTupleFilterModel(IFilterModel):
    @staticmethod
    def columns(filters):
        return [Column(f[0], f[2]) for f in filters]

    @staticmethod
    def filters(filters):
        return [Filter(f[0], f[1], f[2]) for f in filters]
