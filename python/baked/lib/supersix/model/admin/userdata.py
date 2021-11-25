from datetime import datetime

from baked.lib.admin.model.idata import IData
from baked.lib.datetime import DATETIME_FORMAT


class UserData(IData):

    _attributes = {
        "key": str,
        "pwd_hash": str,
        "pwd_last_updated": datetime,
        "access_token": str,
        "access_token_expiry": datetime,
        "refresh_token": str,
        "refresh_token_expiry": datetime,
        "last_login": datetime,
        "player_id": int
    }

    @classmethod
    def attribute_map(cls):
        return cls._attributes

    @classmethod
    def optional_attributes(cls):
        return ["access_token",
                "access_token_expiry",
                "last_login",
                "refresh_token",
                "refresh_token_expiry",
                'player_id']

    @classmethod
    def auto_attributes(cls):
        return []

    @classmethod
    def deserialize(cls, **kwargs):
        # date attributes
        date_attrs = {"access_token_expiry": None,
                      "last_login": None,
                      "pwd_last_updated": None,
                      "refresh_token_expiry": None}

        for attr in date_attrs:
            value = kwargs.pop(attr, None)
            if value:
                date_attrs[attr] = datetime.strptime(value, DATETIME_FORMAT)

        kwargs.update(date_attrs)

        return cls(**kwargs)

    def to_dict(self):
        obj = {
            "key": self.key,
            "pwd_hash": self.pwd_hash,
            "pwd_last_updated": self.pwd_last_updated.strftime(DATETIME_FORMAT),
            "access_token": self.access_token,
            "access_token_expiry": None,
            "refresh_token": self.refresh_token,
            "refresh_token_expiry": None,
            "last_login": None,
            "player_id": self.player_id
        }

        # optional date attributes
        for attr in ["access_token_expiry", "last_login", "refresh_token_expiry"]:
            value = getattr(self, attr)
            obj[attr] = value.strftime(DATETIME_FORMAT) if value else None

        return obj

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
    def access_token(self):
        return self._access_token

    @property
    def access_token_expiry(self):
        return self._access_token_expiry

    @property
    def refresh_token(self):
        return self._refresh_token

    @property
    def refresh_token_expiry(self):
        return self._refresh_token_expiry

    @property
    def last_login(self):
        return self._last_login

    @property
    def player_id(self):
        return self._player_id
