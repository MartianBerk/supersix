from datetime import datetime

from baked.lib.model import Model


class League(Model):
    _attributes = {"id": int,
                   "name": str,
                   "start_date": datetime,
                   "code": str,
                   "current_matchday": int}

    @classmethod
    def attribute_map(cls):
        return cls._attributes

    @classmethod
    def optional_attributes(cls):
        return ["id", "current_matchday"]

    @classmethod
    def get_sql_datatype(cls, item):
        try:
            return {
                int: "int",
                str: "str",
                datetime: "datetime",
            }[cls._attributes[item]]

        except KeyError:
            raise ValueError("unknown item")

    def to_dict(self, keys=None):
        data = {"id": self.id,
                "code": self.code,
                "start_date": self.start_date,
                "name": self.name,
                "current_matchday": self.current_matchday}

        if keys:
            try:
                return {k: data[k] for k in keys}
            except KeyError as e:
                raise KeyError(f"{e} is in invalid key")

        return data

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def start_date(self):
        return self._start_date
    
    @start_date.setter
    def start_date(self, value):
        self._start_date = value

    @property
    def code(self):
        return self._code

    @property
    def current_matchday(self):
        return self._current_matchday

    @current_matchday.setter
    def current_matchday(self, value):
        self._current_matchday = value
