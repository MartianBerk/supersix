from datetime import datetime
from typing import List

from baked.lib.admin.model.iuserdata import IUserData
from baked.lib.admin.model.userpermission import UserPermission
from baked.lib.datetime import DATETIME_FORMAT


class UserData(IUserData):

    _attributes = {
        "key": str,
        "pwd_hash": str,
        "pwd_last_updated": datetime,
        "access_token_hash": str,
        "access_token_expiry": datetime,
        "refresh_token_hash": str,
        "refresh_token_expiry": datetime,
        "reset_pwd_token_hash": str,
        "reset_pwd_token_expiry": datetime,
        "last_login": datetime,
        "player_id": int,
        "qatar_hero_player_id": int,
        "permissions": List[UserPermission],
        "acl_resource_id": int
    }

    @classmethod
    def attribute_map(cls):
        return cls._attributes

    @classmethod
    def optional_attributes(cls):
        return ["key",
                "pwd_hash",
                "pwd_last_updated",
                "access_token_hash",
                "access_token_expiry",
                "last_login",
                "refresh_token_hash",
                "refresh_token_expiry",
                "reset_pwd_token_hash",
                "reset_pwd_token_expiry",
                "player_id",
                "qatar_hero_player_id",
                "permissions",
                "acl_resource_id"]

    @classmethod
    def auto_attributes(cls):
        return []

    @classmethod
    def public_attributes(cls):
        return ["last_login"]

    # TODO: This should be in Model and standardized.
    @classmethod
    def deserialize(cls, **kwargs):
        # date attributes
        attr_map = cls.attribute_map()
        date_attrs = {"access_token_expiry": None,
                      "last_login": None,
                      "pwd_last_updated": None,
                      "refresh_token_expiry": None,
                      "reset_pwd_token_expiry": None}

        for attr in date_attrs:
            value = kwargs.pop(attr, None)
            if value:
                date_attrs[attr] = datetime.strptime(value, DATETIME_FORMAT)

        # cast values
        for key, value in kwargs.items():
            # special handling for permissions
            if key == "permissions":
                kwargs[key] = [UserPermission(**v) for v in value]

            if value and attr_map[key] == int and isinstance(value, str):
                kwargs[key] = int(value)

        kwargs.update(date_attrs)

        return cls(**kwargs)

    def to_dict(self, public_only=False):
        self.permissions.sort(key=lambda p: p.name)
        
        obj = {
            "key": self.key,
            "pwd_hash": self.pwd_hash,
            "access_token_hash": self.access_token_hash,
            "access_token_expiry": self.access_token_expiry,
            "refresh_token_hash": self.refresh_token_hash,
            "refresh_token_expiry": self.refresh_token_expiry,
            "reset_pwd_token_hash": self.reset_pwd_token_hash,
            "reset_pwd_token_expiry": self.reset_pwd_token_expiry,
            "last_login": self.last_login,
            "player_id": self.player_id,
            "qatar_hero_player_id": self.qatar_hero_player_id,
            "permissions": [
                up.to_dict() for up in self.permissions
            ],
            "acl_resource_id": self.acl_resource_id
        }

        if public_only:
            public_attrs = self.public_attributes()
            return {k: v for k, v in obj.items() if k in public_attrs}

        return obj

    def serialize(self, public_only=False):
        self.permissions.sort(key=lambda p: p.name)
        permissions = self.permissions.serialize()

        user_data_dict = self.to_dict(public_only=public_only)
        user_data_dict["permissions"] = permissions

        return user_data_dict

    def update(self, **kwargs):
        for key, value in kwargs.items():
            try:
                setattr(self, f"_{key}", value)

            except AttributeError:
                print(f"don't know {key}")
                pass  # ignore unknown attribute

    @property
    def key(self):
        return self._key

    @property
    def pwd_hash(self):
        return self._pwd_hash

    @property
    def pwd_last_updated(self):
        return self._pwd_last_updated

    @property
    def access_token_hash(self):
        return self._access_token_hash

    @property
    def access_token_expiry(self):
        return self._access_token_expiry

    @property
    def refresh_token_hash(self):
        return self._refresh_token_hash

    @property
    def refresh_token_expiry(self):
        return self._refresh_token_expiry

    @property
    def last_login(self):
        return self._last_login

    @property
    def player_id(self):
        return self._player_id

    @property
    def qatar_hero_player_id(self):
        return self._qatar_hero_player_id

    @property
    def reset_pwd_token_hash(self):
        return self._reset_pwd_token_hash

    @property
    def reset_pwd_token_expiry(self):
        return self._reset_pwd_token_expiry

    @property
    def permissions(self) -> List[UserPermission]:
        if self._permissions is None:
            self._permissions = []

        return self._permissions
    
    @property
    def acl_resource_id(self) -> str:
        return self._acl_resource_id
