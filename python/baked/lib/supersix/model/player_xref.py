from baked.lib.model import Model


class PlayerXref(Model):
    _attributes = {"player_name": str,
                   "xref": str}

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
                str: "str"
            }[cls._attributes[item]]

        except KeyError:
            raise ValueError("unknown item")

    def to_dict(self):
        return {
            "player_name": self.player_name,
            "xref": self.xref
        }

    @property
    def player_name(self):
        return self._player_name

    @property
    def xref(self):
        return self._xref
