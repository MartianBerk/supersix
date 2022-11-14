from datetime import datetime

from baked.lib.model import Model


class WorldCupMatch(Model):
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
                   "away_score": int,
                   "extra_time": bool,
                   "penalties": bool}

    @classmethod
    def attribute_map(cls):
        return cls._attributes

    @classmethod
    def optional_attributes(cls):
        return ["id", "match_minute", "use_match", "home_score", "away_score", "extra_time", "penalties"]

    @classmethod
    def auto_attributes(cls):
        return []

    @classmethod
    def public_attributes(cls):
        return list(cls.attribute_map().keys())

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

    def to_dict(self, public_only=False):
        return {"id": self.id,
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
                "away_score": self.away_score,
                "extra_time": self.extra_time,
                "penalties": self.penalties}

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

    @match_date.setter
    def match_date(self, value):
        self._match_date = value

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
        return self._use_match or False

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

    @property
    def extra_time(self):
        return self._extra_time

    @extra_time.setter
    def extra_time(self, value):
        self._extra_time = value

    @property
    def penalties(self):
        return self._penalties

    @penalties.setter
    def penalties(self, value):
        self._penalties = value
