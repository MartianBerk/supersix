from baked.lib.model import Model


class LeagueTable(Model):
    _attributes = {"league": str,
                   "season": str,
                   "team": str,
                   "position": int,
                   "matches_played": int,
                   "matches_won": int,
                   "matches_drawn": int,
                   "matches_lost": int,
                   "goals_for": int,
                   "goals_against": int,
                   "goal_difference": int,
                   "points": int}

    @classmethod
    def attribute_map(cls):
        return cls._attributes

    @classmethod
    def optional_attributes(cls):
        return ["positional"]

    @classmethod
    def auto_attributes(cls):
        return []

    @classmethod
    def get_sql_datatype(cls, item):
        try:
            return {
                int: "int",
                str: "str"
            }[cls._attributes[item]]

        except KeyError:
            raise ValueError("unknown item")

    def to_dict(self):
        return {
            "league": self.league,
            "season": self.season,
            "team": self.team,
            "position": self.position,
            "matches_played": self.matches_played,
            "matches_won": self.matches_won,
            "matches_drawn": self.matches_drawn,
            "matches_lost": self.matches_lost,
            "goals_for": self.goals_for,
            "goals_against": self.goals_against,
            "goal_difference": self.goal_difference,
            "points": self.points
        }

    @property
    def league(self):
        return self._league

    @property
    def season(self):
        return self._season

    @property
    def team(self):
        return self._team

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, value):
        self._position = value

    @property
    def matches_played(self):
        return self._matches_played

    @property
    def matches_won(self):
        return self._matches_won

    @property
    def matches_drawn(self):
        return self._matches_drawn

    @property
    def matches_lost(self):
        return self._matches_lost

    @property
    def goals_for(self):
        return self._goals_for

    @property
    def goals_against(self):
        return self._goals_against

    @property
    def goal_difference(self):
        return self._goal_difference

    @property
    def points(self):
        return self._points
