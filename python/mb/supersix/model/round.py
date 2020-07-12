from datetime import datetime


class Round:
    def __init__(self, id=None, start_date=None, end_date=None, buy_in_pence=None, winner_id=None):
        if not id or not isinstance(id, int):
            raise TypeError("id must be an integer")

        if not start_date or not isinstance(start_date, datetime):
            raise TypeError("start_date must be a datetime")

        if end_date and not isinstance(end_date, datetime):
            raise TypeError("end_date must be a datetime")

        if not buy_in_pence or not isinstance(buy_in_pence, int):
            raise TypeError("buy_in_pence must be an integer")

        if winner_id and not isinstance(winner_id, int):
            raise TypeError("winner must be an integer")

        self._id = id
        self._start_date = start_date
        self._end_date = end_date
        self._buy_in_pence = buy_in_pence
        self._winner_id = winner_id

    def to_dict(self):
        return {
            "id": self._id,
            "start_date": self._start_date,
            "end_date": self._end_date,
            "buy_in_pence": self._buy_in_pence,
            "winner_id": self._winner_id
        }

    @property
    def id(self):
        return self._id

    @property
    def start_date(self):
        return self._start_date

    @property
    def end_date(self):
        return self._end_date

    @property
    def buy_in_pence(self):
        return self._buy_in_pence

    @property
    def winner_id(self):
        return self._winner_id
