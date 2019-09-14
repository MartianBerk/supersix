class League:
    def __init__(self, id=None, name=None, start_date=None, code=None):
        if not id or not name:
            raise ValueError("id and name are mandatory")

        self._id = id
        self._code = code
        self._start_date = start_date
        self._name = name

    def to_dict(self, keys=None):
        data = {"id": self._id,
                "code": self._code,
                "start_date": self._start_date,
                "name": self._name}

        if keys:
            for k in data.keys():
                if k not in keys:
                    data.pop(k)

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
