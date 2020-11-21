from datetime import datetime

from mylib.model import Model


class Player(Model):
    _attributes = {"id": int,
                   "first_name": str,
                   "last_name": str,
                   "nickname": str,
                   "join_date": datetime}

    @classmethod
    def attribute_map(cls):
        return cls._attributes

    @classmethod
    def optional_attributes(cls):
        return ["nickname"]

    @classmethod
    def get_sql_datatype(cls, item):
        try:
            return {
                int: "int",
                str: "str",
                datetime: "datetime"
            }[cls._attributes[item]]

        except KeyError:
            raise ValueError("unknown item")

    def to_dict(self):
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "nickname": self.nickname,
            "join_date": self.join_date
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
    def nickname(self):
        return self._nickname

    @property
    def join_date(self):
        return self._join_date
