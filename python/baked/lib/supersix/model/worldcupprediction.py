from baked.lib.model import Model


class WorldCupPrediction(Model):
    _VALID_PREDICTIONS = ["home", "away", "draw", "void"]
    _ATTRIBUTES = {"id": int,
                   "player_id": int,
                   "match_id": int,
                   "prediction": str,
                   "plus_ninety": bool,
                   "extra_time": bool,
                   "penalties": bool,
                   "drop": bool}

    @classmethod
    def attribute_map(cls):
        return cls._ATTRIBUTES

    @classmethod
    def optional_attributes(cls):
        return ["drop", "extra_time", "penalties"]

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
                str: "str",
                bool: "bool"
            }[cls._ATTRIBUTES[item]]

        except KeyError:
            raise ValueError("unknown item")

    def to_dict(self, public_only=False):
        return {
            "id": self.id,
            "player_id": self.player_id,
            "match_id": self.match_id,
            "prediction": self.prediction,
            "plus_ninety": self.plus_ninety,
            "extra_time": self.extra_time,
            "penalties": self.penalties,
            "drop": self.drop
        }

    @property
    def id(self):
        return self._id

    @property
    def player_id(self):
        return self._player_id

    @property
    def match_id(self):
        return self._match_id

    @property
    def prediction(self):
        return self._prediction

    @property
    def plus_ninety(self):
        return self._plus_ninety

    @property
    def extra_time(self):
        return self._extra_time

    @property
    def penalties(self):
        return self._penalties

    @property
    def drop(self):
        return self._drop or False

    @drop.setter
    def drop(self, value):
        self._drop = value
