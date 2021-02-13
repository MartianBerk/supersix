from datetime import datetime

from baked.lib.model import Model


class HistoricRound(Model):
    _attributes = {"round_id": int,
                   "start_date": datetime,
                   "end_date": datetime,
                   "matches": int,
                   "players": int,
                   "jackpot": int,
                   "winner": str}

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
                datetime: "datetime",
                str: "str"
            }[cls._attributes[item]]

        except KeyError:
            raise ValueError("unknown item")

    def to_dict(self):
        return {
            "round_id": self.round_id,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "matches": self.matches,
            "players": self.players,
            "jackpot": self.jackpot,
            "winner": self.winner
        }

    @property
    def round_id(self):
        return self._round_id

    @property
    def start_date(self):
        return self._start_date

    @property
    def end_date(self):
        return self._end_date

    @property
    def matches(self):
        return self._matches

    @property
    def players(self):
        return self._players

    @property
    def jackpot(self):
        return self._jackpot

    @property
    def winner(self):
        return self._winner
