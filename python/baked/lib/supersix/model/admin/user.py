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
    def attributes(cls, public_only=False):
        attrs = list(cls.attribute_map().keys())
        attrs.extend(list(UserData.attribute_map().keys()))
        attrs.remove("data")

        if public_only:
            public_attrs = cls.public_attributes()
            return [a for a in attrs if a in public_attrs]

        return attrs

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
    def public_attributes(cls):
        return ["email", "user_id", "player_id", "account"]

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

    def to_dict(self, public_only=False):
        obj = {
            "id": self.id,
            "email": self.email,
            "user_id": self.user_id,
            "account": self.account
        }

        if self.data:
            obj.update(self.data.to_dict())

        if public_only:
            public_attrs = self.public_attributes()
            return {k: v for k, v in obj.items() if k in public_attrs}

        return obj

    def update(self, data, data_only=False):
        user_data = {}
        user_data_attrs = UserData.attribute_map()

        for key in data.keys():
            # split user data
            if key in user_data_attrs:
                user_data[k] = data.pop(key)

            elif not data_only:
                # update user
                try:
                    setattr(self, f"_{key}", value)

                except AttributeError:
                    print(f"don't know {key}")
                    pass  # ignore unknown attribute

        # update data
        if self._data is None:
            self._data = UserData.deserialize(**user_data)
        else:
            self._data.update(**user_data)

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
