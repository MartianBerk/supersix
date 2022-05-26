from baked.lib.model import Model


class Prediction(Model):
    _VALID_PREDICTIONS = ["home", "away", "draw", "void"]
    _ATTRIBUTES = {"id": int,
                   "round_id": int,
                   "player_id": int,
                   "match_id": int,
                   "prediction": str,
                   "drop": bool}

    @classmethod
    def attribute_map(cls):
        return cls._ATTRIBUTES

    @classmethod
    def optional_attributes(cls):
        return ["drop"]

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
            "round_id": self.round_id,
            "player_id": self.player_id,
            "match_id": self.match_id,
            "prediction": self.prediction,
            "drop": self.drop
        }

    @property
    def id(self):
        return self._id

    @property
    def round_id(self):
        return self._round_id

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
    def drop(self):
        return self._drop or False

    @drop.setter
    def drop(self, value):
        self._drop = value
