from datetime import datetime

from baked.lib.model import Model


class Round(Model):
    _attributes = {"id": int,
                   "start_date": datetime,
                   "end_date": datetime,
                   "buy_in_pence": int}

    @classmethod
    def attribute_map(cls):
        return cls._attributes

    @classmethod
    def optional_attributes(cls):
        return ["end_date", "winners"]

    @classmethod
    def get_sql_datatype(cls, item):
        try:
            return {
                int: "int",
                datetime: "datetime"
            }[cls._attributes[item]]

        except KeyError:
            raise ValueError("unknown item")

    def to_dict(self):
        return {
            "id": self.id,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "buy_in_pence": self.buy_in_pence
        }

    @property
    def id(self):
        return self._id

    @property
    def start_date(self):
        return self._start_date

    @property
    def end_date(self):
        return self._end_date

    @end_date.setter
    def end_date(self, value):
        self._end_date = value

    @property
    def buy_in_pence(self):
        return self._buy_in_pence
