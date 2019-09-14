class League:
    def __init__(self, id, code, name):
        self._id = id
        self._code = code
        self._name = name

    def to_dict(self, keys=None):
        data = {"id": self._id,
                "code": self._code,
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
    def code(self):
        return self._code

    @property
    def name(self):
        return self._name
