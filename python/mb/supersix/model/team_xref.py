from mylib.model import Model


class TeamXref(Model):
    _attributes = {"team_name": str,
                   "ref": str}

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
            "team_name": self.team_name,
            "xref": self.xref
        }

    @property
    def team_name(self):
        return self._team_name

    @property
    def xref(self):
        return self._xref
