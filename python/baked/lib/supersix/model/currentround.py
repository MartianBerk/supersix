from datetime import datetime

from baked.lib.model import Model


class CurrentRound(Model):
    _attributes = {"round_id": int,
                   "start_date": datetime,
                   "current_match_date": datetime,
                   "matches": int,
                   "players": int,
                   "jackpot": int}

    @classmethod
    def attribute_map(cls):
        return cls._attributes

    @classmethod
    def optional_attributes(cls):
        return ["current_match_date", "matches", "jackpot"]

    @classmethod
    def auto_attributes(cls):
        return []

    @classmethod
    def get_sql_datatype(cls, item):
        try:
            return {
                int: "int",
                datetime: "datetime",
            }[cls._attributes[item]]

        except KeyError:
            raise ValueError("unknown item")

    def to_dict(self):
        return {
            "round_id": self.round_id,
            "start_date": self.start_date,
            "current_match_date": self.current_match_date,
            "matches": self.matches,
            "players": self.players,
            "jackpot": self.jackpot
        }

    @property
    def round_id(self):
        return self._round_id

    @property
    def start_date(self):
        return self._start_date

    @property
    def current_match_date(self):
        return self._current_match_date

    @property
    def matches(self):
        return self._matches

    @property
    def players(self):
        return self._players

    @property
    def jackpot(self):
        return self._jackpot
