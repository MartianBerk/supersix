from datetime import datetime

from baked.lib.model import Model


class Match(Model):
    _attributes = {"id": int,
                   "external_id": str,
                   "league_id": int,
                   "matchday": int,
                   "match_date": datetime,
                   "match_minute": int,
                   "status": str,
                   "home_team": str,
                   "away_team": str,
                   "use_match": bool,
                   "home_score": int,
                   "away_score": int}

    @classmethod
    def attribute_map(cls):
        return cls._attributes

    @classmethod
    def optional_attributes(cls):
        return ["id", "match_minute", "use_match", "home_score", "away_score"]

    @classmethod
    def get_sql_datatype(cls, item):
        try:
            return {
                int: "int",
                str: "str",
                datetime: "datetime",
                bool: "bool"
            }[cls._attributes[item]]

        except KeyError:
            raise ValueError("unknown item")

    def to_dict(self, keys=None):
        data = {"id": self.id,
                "external_id": self.external_id,
                "league_id": self.league_id,
                "matchday": self.matchday,
                "match_date": self.match_date,
                "match_minute": self.match_minute,
                "status": self.status,
                "home_team": self.home_team,
                "away_team": self.away_team,
                "use_match": self.use_match,
                "home_score": self.home_score,
                "away_score": self.away_score}

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
    def external_id(self):
        return self._external_id

    @property
    def league_id(self):
        return self._league_id

    @property
    def matchday(self):
        return self._matchday

    @property
    def match_date(self):
        return self._match_date

    @property
    def match_minute(self):
        return self._match_minute

    @match_minute.setter
    def match_minute(self, value):
        self._match_minute = value

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        self._status = value

    @property
    def home_team(self):
        return self._home_team

    @property
    def away_team(self):
        return self._away_team

    @property
    def use_match(self):
        return self._use_match

    @use_match.setter
    def use_match(self, value):
        self._use_match = value

    @property
    def home_score(self):
        return self._home_score

    @home_score.setter
    def home_score(self, value):
        self._home_score = value

    @property
    def away_score(self):
        return self._away_score

    @away_score.setter
    def away_score(self, value):
        self._away_score = value
