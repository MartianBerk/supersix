from baked.lib.dbaccess.public import DbAccess, AndOrFilterModel
from baked.lib.globals import get_global
from baked.lib.supersix.model.worldcupmatch import WorldCupMatch
from baked.lib.supersix.model.worldcupprediction import WorldCupPrediction
from baked.lib.supersix.model.worldcupscore import WorldCupScore
from baked.lib.supersix.service.leagueservice import LeagueService

from .servicemixin import ServiceMixin


class WorldCupService(ServiceMixin):
    _db = "supersix"
    _matches_table = "WORLDCUP_MATCHES"
    _predictions_table = "WORLDCUP_PREDICTIONS"
    _scores_table = "WORLDCUP_SCORES"
    _match_model_schema = ["id", "external_id", "league_id", "matchday", "match_date", "match_minute", "status",
                           "home_team", "away_team", "use_match", "home_score", "away_score", "extra_time", "penalties"]
    _prediction_model_schema = ["id", "player_id", "match_id", "prediction", "extra_time", "penalties", "drop"]

    def __init__(self):
        db_settings = get_global("dbs", self._db)

        self._driver = db_settings.get("driver")
        self._db = DbAccess.connect(self._driver,
                                    self._db,
                                    db_settings.get("location"))
        self._league_service = LeagueService()

    def get_match(self, match_id):
        columns = {c: None for c in self._db.get_columns(self._matches_table)}
        column_model = self._generate_column_model(self._driver, WorldCupMatch, columns)

        filters = {"id": match_id}
        filter_model = self._generate_filter_model(self._driver, WorldCupMatch, filters)

        match = self._db.get(self._matches_table, column_model, filter_model=filter_model)
        if not match:
            return None

        return WorldCupMatch(**{k: match[0][k] for k in self._match_model_schema})

    def get_match_from_external_id(self, external_id):
        columns = {c: None for c in self._db.get_columns(self._matches_table)}
        column_model = self._generate_column_model(self._driver, WorldCupMatch, columns)

        filters = {"external_id": external_id}
        filter_model = self._generate_filter_model(self._driver, WorldCupMatch, filters)

        match = self._db.get(self._matches_table, column_model, filter_model=filter_model)
        if not match:
            return None

        return WorldCupMatch(**{k: match[0][k] for k in self._match_model_schema})

    def list_matches(self, filters=None):
        columns = {c: None for c in self._db.get_columns(self._matches_table)}
        column_model = self._generate_column_model(self._driver, WorldCupMatch, columns)

        filter_model = self._generate_filter_model(self._driver, WorldCupMatch, filters) if filters else None

        matches = self._db.get(self._matches_table, column_model, filter_model=filter_model)
        return [WorldCupMatch(**{k: m.get(k, None) for k in self._match_model_schema}) for m in matches]

    def create_match(self, match):
        exists = match.id and self.get_match(match.id)
        if exists:
            raise ValueError(f"[{match.matchday}] {match.home_team} vs {match.away_team} already exists")

        match = match.to_dict()

        column_model = self._generate_column_model(self._driver, WorldCupMatch, match)

        match = self._db.insert_get(self._matches_table, column_model)

        return self.get_match(match["id"])

    def update_match(self, match):
        match = match.to_dict()

        column_model = self._generate_column_model(self._driver, WorldCupMatch, match)

        self._db.update(self._matches_table, column_model)

        return self.get_match(match["id"])

    def list_scores(self):
        columns = {c: None for c in self._db.get_columns(self._scores_table)}
        column_model = self._generate_column_model(self._driver, WorldCupScore, columns)

        scores = self._db.get(self._scores_table, column_model)
        return [WorldCupScore(**s) for s in scores]

    def prediction_exists(self, match_id, player_id):
        columns = {c: None for c in self._db.get_columns(self._predictions_table)}
        column_model = self._generate_column_model(self._driver, WorldCupPrediction, columns)

        filters = [("match_id", "equalto", match_id),
                   ("player_id", "equalto", player_id),
                   ("drop", "equalto", False)]
        filter_model = self._generate_filter_model(self._driver, WorldCupPrediction, filters)

        predictions = self._db.get(self._predictions_table, column_model, filter_model=filter_model)
        if predictions:
            return self.get(predictions[0]["id"])

        return None

    def create_prediction(self, prediction):
        exists = prediction.id and self.get(prediction.id)
        if exists:
            raise ValueError(f"{prediction.id} already exists")

        prediction = prediction.to_dict()

        column_model = self._generate_column_model(self._driver, WorldCupPrediction, prediction)

        prediction = self._db.insert_get(self._predictions_table, column_model)

        return self.get(prediction["id"])

    def update_prediction(self, prediction):
        prediction = prediction.to_dict()

        column_model = self._generate_column_model(self._driver, WorldCupPrediction, prediction)

        self._db.update(self._predictions_table, column_model)

        return self.get(prediction["id"])

    def list_predictions(self, filters=None):
        columns = {c: None for c in self._db.get_columns(self._predictions_table)}
        column_model = self._generate_column_model(self._driver, WorldCupPrediction, columns)

        filter_model = self._generate_filter_model(self._driver, WorldCupPrediction, filters) if filters else None

        predictions = self._db.get(self._predictions_table, column_model, filter_model=filter_model)
        return [WorldCupPrediction(**{k: p.get(k, None) for k in self._prediction_model_schema}) for p in predictions]
