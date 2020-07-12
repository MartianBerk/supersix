class Prediction:
    _VALID_PREDICTIONS = ["home", "away", "draw"]

    def __init__(self, id=None, round_id=None, player_id=None, match_id=None, prediction=None):
        if not id or not isinstance(id, int):
            raise TypeError("id must be an integer")

        if not round_id or not isinstance(round_id, int):
            raise TypeError("round_id must be an integer")

        if player_id and not isinstance(player_id, int):
            raise TypeError("player_id must be an integer")

        if not match_id or not isinstance(match_id, int):
            raise TypeError("match_id must be an integer")

        if not prediction or not prediction in self._VALID_PREDICTIONS:
            raise TypeError(f"prediction must be one of {', '.join(self._VALID_PREDICTIONS)}")

        self._id = id
        self._round_id = round_id
        self._player_id = player_id
        self._match_id = match_id
        self._prediction = prediction

    def to_dict(self):
        return {
            "id": self._id,
            "round_id": self._round_id,
            "player_id": self._player_id,
            "match_id": self._match_id,
            "prediction": self._prediction
        }

    @property
    def id(self):
        return self._id

    @property
    def round_id(self):
        return self._round_id

    @property
    def player_id(self):
        return self._player_id

    @property
    def match_id(self):
        return self._match_id

    @property
    def prediction(self):
        return self._prediction
