from datetime import datetime

from baked.lib.model import Model


class Player(Model):
    _attributes = {"id": int,
                   "first_name": str,
                   "last_name": str,
                   "join_date": datetime,
                   "retired": bool}

    @classmethod
    def attribute_map(cls):
        return cls._attributes

    @classmethod
    def optional_attributes(cls):
        return []

    @classmethod
    def get_sql_datatype(cls, item):
        try:
            return {
                int: "int",
                str: "str",
                datetime: "datetime",
                bool: "bool"
            }[cls._attributes[item]]

        except KeyError:
            raise ValueError("unknown item")

    def to_dict(self):
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "join_date": self.join_date,
            "retired": self.retired
        }

    @property
    def id(self):
        return self._id

    @property
    def first_name(self):
        return self._first_name

    @property
    def last_name(self):
        return self._last_name

    @property
    def join_date(self):
        return self._join_date
    
    @property
    def retired(self):
        return self._retired
