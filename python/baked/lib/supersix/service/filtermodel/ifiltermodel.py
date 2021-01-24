from abc import ABCMeta, abstractmethod


class IFilterModel(metaclass=ABCMeta):
    @staticmethod
    @abstractmethod
    def columns(filters):
        """Return columns as a list of tuples [(column, value), ...]."""
        raise NotImplementedError()

    @staticmethod
    @abstractmethod
    def filters(filters):
        """Return filters as a list of tuples [(column, operator, value), ...]."""
        raise NotImplementedError()
