from baked.lib.model import Model


class RoundWinner(Model):
    _attributes = {"round_id": int,
                   "player_id": int}

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
                int: "int"
            }[cls._attributes[item]]

        except KeyError:
            raise ValueError("unknown item")

    def to_dict(self):
        return {
            "round_id": self.round_id,
            "player_id": self.player_id
        }

    @property
    def round_id(self):
        return self._round_id

    @property
    def player_id(self):
        return self._player_id
