class League:
    def __init__(self, id=None, name=None, start_date=None, code=None, current_matchday=None):
        if not name or not code:
            raise ValueError("name and code are mandatory")

        self._id = id
        self._code = code
        self._start_date = start_date
        self._name = name
        self._current_matchday = current_matchday

    def to_dict(self, keys=None):
        data = {"id": self._id,
                "code": self._code,
                "start_date": self._start_date,
                "name": self._name,
                "current_matchday": self._current_matchday}

        if keys:
            try:
                return {k: data[k] for k in keys}
            except KeyError as e:
                raise KeyError(f"{e} is in invalid key")

        return data

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def start_date(self):
        return self._start_date

    @property
    def code(self):
        return self._code

    @property
    def current_matchday(self):
        return self._current_matchday
