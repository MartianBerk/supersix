from datetime import datetime

from baked.lib.model import Model


class MatchPrediction(Model):
    _ATTRIBUTES = {"round_id": int,
                   "player_id": int,
                   "first_name": str,
                   "last_name": str,
                   "match_id": int,
                   "home_team": str,
                   "away_team": str,
                   "match_date": datetime,
                   "prediction": str}

    @classmethod
    def attribute_map(cls):
        return cls._ATTRIBUTES

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
                int: "int",
                str: "str",
                datetime: "datetime"
            }[cls._ATTRIBUTES[item]]

        except KeyError:
            raise ValueError("unknown item")

    def to_dict(self):
        return {
            "round_id": self.round_id,
            "player_id": self.player_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "match_id": self.match_id,
            "home_team": self.home_team,
            "away_team": self.away_team,
            "match_date": self.match_date,
            "prediction": self.prediction
        }

    @property
    def round_id(self):
        return self._round_id

    @property
    def player_id(self):
        return self._player_id

    @property
    def first_name(self):
        return self._first_name

    @property
    def last_name(self):
        return self._last_name

    @property
    def match_id(self):
        return self._match_id

    @property
    def home_team(self):
        return self._home_team

    @property
    def away_team(self):
        return self._away_team

    @property
    def match_date(self):
        return self._match_date

    @property
    def prediction(self):
        return self._prediction
