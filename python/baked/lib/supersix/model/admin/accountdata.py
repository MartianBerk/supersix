from abc import abstractmethod

from baked.lib.model import Model


class AccountData(Model):

    @classmethod
    def attributes(cls):
        return []

    @classmethod
    @abstractmethod
    def attribute_map(cls):
        return {}

    @classmethod
    @abstractmethod
    def optional_attributes(cls):
        return []

    @classmethod
    @abstractmethod
    def auto_attributes(cls):
        return []

    @classmethod
    @abstractmethod
    def deserialize(cls, **kwargs):
        return cls(**kwargs)

    @abstractmethod
    def to_dict(self):
        return {}
