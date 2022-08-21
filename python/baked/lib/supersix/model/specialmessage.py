from baked.lib.model import Model


class SpecialMessage(Model):
    _attributes = {"id": int,
                   "message": str,
                   "retired": bool}

    @classmethod
    def attribute_map(cls):
        return cls._attributes

    @classmethod
    def optional_attributes(cls):
        return ["retired"]

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
            }[cls._attributes[item]]

        except KeyError:
            raise ValueError("unknown item")

    def to_dict(self, public_only=False):
        return {
            "id": self.id,
            "message": self.message,
            "retired": self.retired
        }

    @property
    def id(self):
        return self._id

    @property
    def message(self):
        return self._message
    
    @property
    def retired(self):
        return self._retired or False
    
    @retired.setter
    def retired(self, value):
        self._retired = value
