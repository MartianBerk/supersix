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
    def public_attributes(cls):
        return ["account_id"]

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

    def to_dict(self, public_only=False):
        obj = {
            "id": self.id,
            "account_id": self.account_id
        }

        if self.data:
            obj.update(self.data.to_dict())

        if public_only:
            public_attrs = self.public_attributes()
            return {k: v for k, v in obj.items() if k in public_attrs}

        return obj

    def update(self, data, data_only=False):
        account_data = {}
        account_data_attrs = AccountData.attribute_map()

        for key, value in data.items():
            # split user data
            if key in account_data_attrs:
                account_data[key] = value

            elif not data_only:
                # update account
                try:
                    setattr(self, f"_{key}", value)

                except AttributeError:
                    print(f"don't know {key}")
                    pass  # ignore unknown attribute

        # update data
        if self._data is None:
            self._data = AccountData.deserialize(**account_data)
        else:
            self._data.update(**account_data)

    @property
    def id(self):
        return self._id

    @property
    def account_id(self):
        return self._account_id

    @property
    def data(self):
        return self._data
