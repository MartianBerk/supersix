from datetime import date, datetime


class Player:
    def __init__(self, id=None, first_name=None, last_name=None, join_date=None):
        if not id or not isinstance(id, int):
            raise TypeError("id must be an integer")

        if not first_name or not isinstance(first_name, str):
            raise TypeError("first_name must be a string")

        if not last_name or not isinstance(last_name, str):
            raise TypeError("last_name must be a string")

        if not join_date or not isinstance(join_date, datetime):
            raise TypeError("join_date must be a datetime")

        self._id = id
        self._first_name = first_name
        self._last_name = last_name
        self._join_date = join_date

    def to_dict(self):
        return {
            "id": self._id,
            "first_name": self._first_name,
            "last_name": self._last_name,
            "join_date": self._join_date
        }

    @property
    def id(self):
        return self._id

    @property
    def first_name(self):
        return self._first_name

    @property
    def last_name(self):
        return self._last_name

    @property
    def join_date(self):
        return self._join_date
