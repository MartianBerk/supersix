from baked.lib.admin.model.iaccount import IAccount
from baked.lib.supersix.model.admin.accountdata import AccountData


class Account(IAccount):

    _attributes = {
        "id": int,
        "account_id": str,
        "data": AccountData
    }

    @classmethod
    def attributes(cls):
        attrs = list(cls.attribute_map().keys())
        attrs.remove("data")

        return attrs

    @classmethod
    def attribute_map(cls):
        return cls._attributes

    @classmethod
    def optional_attributes(cls):
        return ["data"]

    @classmethod
    def auto_attributes(cls):
        return []

    @classmethod
    def get_sql_datatype(cls, item):
        try:
            return {
                "id": "int",
                "account_id": "str"
            }[item]

        except KeyError:
            raise ValueError("unknown item")

    @classmethod
    def identity_columns(self):
        return ["account_id", "id"]

    @classmethod
    def user_service_id_column(cls):
        return "account_id"

    @classmethod
    def get_columns(cls):
        return ["id", "account_id"]

    @classmethod
    def deserialize(cls, **kwargs):
        data = {k: v for k, v in kwargs.items() if k in AccountData.attribute_map()}
        if data:
            data = AccountData.deserialize(**data)

        return cls(data=data, **kwargs)

    def account_file_id(self):
        return self._account_id

    def to_dict(self):
        obj = {
            "id": self.id,
            "account_id": self.account_id
        }

        if self.data:
            obj.update(self.data.to_dict())

        return obj

    def update_data(self, data):
        if self._data is None:
            self._data = AccountData.deserialize(**data)
        else:
            self._data.update(**data)

    @property
    def id(self):
        return self._id

    @property
    def account_id(self):
        return self._account_id

    @property
    def data(self):
        return self._data
