from mylib.globals import get_global
from mylib.myodbc import MyOdbc

from mylib.supersix.model import Match


class MatchService:
    _db = "SUPERSIX"
    _table = "matches"
    _model_schema = ["id", "league_id", "matchday", "match_date", "home_team", "away_team", "home_score", "away_score"]

    def __init__(self):
        db_settings = get_global("dbs", self._db)

        self._db = MyOdbc.connect(db_settings.get("driver"),
                                  self._db,
                                  db_settings.get("location"))

    def get(self, match_id):
        match = self._db.get(self._table, where={"id": match_id})
        if not match:
            return None

        return Match(**{k: match[0][k] for k in self._model_schema})

    def list(self, filters=None):
        if filters and not isinstance(filters, dict):
            raise TypeError("filters must be None or a dict")

        matches = self._db.get(self._table, where=filters)
        return [Match(**{k: m.get(k, None) for k in self._model_schema}) for m in matches]

    def create(self, match):
        exists = self.get(match.id)
        if exists:
            raise ValueError(f"[{match.matchday}] {match.home_team} vs {match.away_team} already exists")

        self._db.upsert(self._table, match.to_dict())

        return self.get(match.id)

    def update(self, match, keys=None):
        self._db.upsert(self._table, match.to_dict(keys=keys))

        return self.get(match.id)
