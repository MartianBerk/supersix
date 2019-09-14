class Match:
    def __init__(self, id=None, league_id=None, matchday=None, match_date=None,
                 home_team=None, away_team=None, home_score=None, away_score=None):
        if not id or not league_id or not matchday or not match_date or not home_team or not away_team:
            raise ValueError("id, league_id, matchday, match_date, home_team and away_team are mandatory")

        self._id = id
        self._league_id = league_id
        self._matchday = matchday
        self._match_date = match_date
        self._home_team = home_team
        self._away_team = away_team
        self._home_score = home_score
        self._away_score = away_score

    def to_dict(self, keys=None):
        data = {"id": self._id,
                "league_id": self._league_id,
                "matchday": self._matchday,
                "match_date": self._match_date,
                "home_team": self._home_team,
                "away_team": self._away_team,
                "home_score": self._home_score,
                "away_score": self._away_score}

        if keys:
            for k in data.keys():
                if k not in keys:
                    data.pop(k)

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
    def home_team(self):
        return self._home_team

    @property
    def away_team(self):
        return self._away_team

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
