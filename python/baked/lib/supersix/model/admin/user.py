from baked.lib.admin.model.iuser import IUser
from baked.lib.supersix.model.admin.userdata import UserData


class User(IUser):

    _attributes = {
        "id": int,
        "account": str,  # TODO: update to Account Model
        "email": str,
        "user_id": str,
        "data": UserData
    }

    @classmethod
    def attributes(cls):
        attrs = cls.attribute_map()
        attrs.pop("data")

        return list(attrs.keys())

    @classmethod
    def attribute_map(cls):
        return cls._attributes

    @classmethod
    def optional_attributes(cls):
        return ["data", "email"]

    @classmethod
    def auto_attributes(cls):
        automation_rules = cls.automation_rules()
        return [rule["column"] for rule in automation_rules["create"]]

    @classmethod
    def get_sql_datatype(cls, item):
        try:
            return {
                "id": "int",
                "account": 'str',
                "email": "str",
                "user_id": "str"
            }[item]

        except KeyError:
            raise ValueError("unknown item")

    @classmethod
    def identity_columns(self):
        return ["email", "user_id", "id"]

    @classmethod
    def get_columns(cls):
        return ["id", "account", "email", "user_id"]

    @classmethod
    def automation_rules(cls):
        return {
            "create": [
                {
                    "column": "id",
                    "rule": "autoincrement_id"
                }
            ]
        }

    @classmethod
    def deserialize(cls, **kwargs):
        data = {k: v for k, v in kwargs.items() if k in UserData.attribute_map()}
        if data:
            data = UserData.deserialize(**data)

        return cls(data=data, **kwargs)

    def user_file_id(self):
        return self.user_id

    def to_dict(self):
        obj = {
            "id": self.id,
            "email": self.email,
            "user_id": self.user_id,
            "account": self.account
        }

        if self.data:
            obj.update(self.data.to_dict())

        return obj

    def update_data(self, data):
        if self._data is None:
            self._data = UserData.deserialize(**data)
        else:
            self._data.update(**data)

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value

    @property
    def account(self):
        return self._account

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, value):
        self._email = value

    @property
    def user_id(self):
        return self._user_id

    @user_id.setter
    def user_id(self, value):
        self._user_id = value

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        self.update_data(value)

    @property
    def key(self):
        return self._data.key

    @property
    def pwd_hash(self):
        return self._data.pwd_hash

    @property
    def pwd_last_updated(self):
        return self._data.pwd_last_updated
