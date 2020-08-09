class Match:
    def __init__(self, id=None, league_id=None, matchday=None, match_date=None, start_time=None, status=None,
                 home_team=None, away_team=None, use_match=None, home_score=None, away_score=None):
        if not id or not league_id or not matchday or not match_date or not start_time or not status or not home_team or not away_team:
            raise ValueError("id, league_id, matchday, match_date, start_time, status, home_team and away_team are mandatory")

        self._id = id
        self._league_id = league_id
        self._matchday = matchday
        self._match_date = match_date
        self._start_time = start_time
        self._status = status
        self._home_team = home_team
        self._away_team = away_team
        self._use_match = use_match
        self._home_score = home_score
        self._away_score = away_score

    def to_dict(self, keys=None):
        data = {"id": self._id,
                "league_id": self._league_id,
                "matchday": self._matchday,
                "match_date": self._match_date,
                "start_time": self._start_time,
                "status": self._status,
                "home_team": self._home_team,
                "away_team": self._away_team,
                "use_match": self._use_match,
                "home_score": self._home_score,
                "away_score": self._away_score}

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
    def league_id(self):
        return self._league_id

    @property
    def matchday(self):
        return self._matchday

    @property
    def match_date(self):
        return self._match_date

    @property
    def start_time(self):
        return self._start_time

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
