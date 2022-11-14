from datetime import datetime

from baked.lib.model import Model


class WorldCupScore(Model):
    _attributes = {"player": str,
                   "score": int,
                   "bonus": int,
                   "total": int}

    @classmethod
    def attribute_map(cls):
        return cls._attributes

    @classmethod
    def optional_attributes(cls):
        return []

    @classmethod
    def auto_attributes(cls):
        return []

    @classmethod
    def public_attributes(cls):
        return list(cls.attribute_map().keys())

    @classmethod
    def get_sql_datatype(cls, item):
        try:
            return {
                int: "int",
                str: "str"
            }[cls._attributes[item]]

        except KeyError:
            raise ValueError("unknown item")

    def to_dict(self, public_only=False):
        return {
            "player": self.player,
            "score": self.score,
            "bonus": self.bonus,
            "total": self.total
        }

    @property
    def player(self):
        return self._player

    @property
    def score(self):
        return self._score

    @property
    def bonus(self):
        return self._bonus

    @property
    def total(self):
        return self._total
