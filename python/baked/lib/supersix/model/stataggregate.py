from datetime import datetime

from baked.lib.model import Model


class StatAggregate(Model):
    _attributes = {"round": int,
                   "player_id": int,
                   "player": str,
                   "match_date": datetime,
                   "matches": int,
                   "correct": int}

    @classmethod
    def attribute_map(cls):
        return cls._attributes

    @classmethod
    def optional_attributes(cls):
        return ["correct"]  # TODO: check sqlitev2 models, possible 0 equating for False and throwing error

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
                datetime: "datetime",
                str: "str"
            }[cls._attributes[item]]

        except KeyError:
            raise ValueError("unknown item")

    def to_dict(self, public_only=False):
        return {
            "round": self.round,
            "player_id": self.player_id,
            "player": self.player,
            "match_date": self.match_date,
            "matches": self.matches,
            "correct": self.correct
        }

    @property
    def round(self):
        return self._round

    @property
    def player_id(self):
        return self._player_id

    @property
    def player(self):
        return self._player

    @property
    def match_date(self):
        return self._match_date

    @property
    def matches(self):
        return self._matches

    @property
    def correct(self):
        return self._correct
