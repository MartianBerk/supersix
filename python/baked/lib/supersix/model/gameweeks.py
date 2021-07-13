from datetime import datetime

from baked.lib.model import Model


class GameWeeks(Model):
    _attributes = {"match_date": datetime}

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
    def get_sql_datatype(cls, item):
        try:
            return {
                datetime: "datetime"
            }[cls._attributes[item]]

        except KeyError:
            raise ValueError("unknown item")

    def to_dict(self):
        return {
            "match_date": self.match_date
        }

    @property
    def match_date(self):
        return self._match_date
