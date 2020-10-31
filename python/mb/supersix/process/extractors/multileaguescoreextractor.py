from datetime import datetime, timedelta
from json import dump
from time import sleep

from mb.supersix.model import Match
from mb.supersix.service import LeagueService, MatchService, PlayerService, PredictionService

from .connectors.flashscoreconnectorv2 import FlashScoreConnectorV2


class MultiLeagueScoreExtractor:
    _CONNECTORS = {
        "PL": FlashScoreConnectorV2,
        "ELC": FlashScoreConnectorV2,
        "EL1": FlashScoreConnectorV2,
        "EL2": FlashScoreConnectorV2
    }

    def __init__(self, leagues, matchday=None, max_run_seconds=0, dump_matches=None, dump_scores=None):
        for league in leagues:
            if league not in self._CONNECTORS.keys():
                raise ValueError(f"league '{league}', connector unknown")

        self._leagues = [LeagueService().get_from_league_code(l) for l in leagues]
        self._matchday = matchday
        self._max_run_seconds = max_run_seconds
        self._dump_matches = dump_matches
        self._dump_scores = dump_scores

        self._connectors = {l: self._CONNECTORS[l.code]() for l in self._leagues}
        self._match_service = MatchService()

    def _update_match(self, league, match_data):
        match = self._match_service.get_from_external_id(match_data["id"])
        if not match:
            start_time = datetime.strptime(match_data["utcDate"], "%Y-%m-%dT%H:%M:%SZ")

            match = Match(external_id=str(match_data["id"]),
                          league_id=league.id,
                          matchday=match_data["matchday"],
                          match_date=start_time,
                          status=match_data["status"],
                          home_team=match_data["homeTeam"]["name"],
                          away_team=match_data["awayTeam"]["name"])

            match = self._match_service.create(match)
        else:
            match.status = match_data["status"]

            match_minute = match_data.get("minute")
            if match_minute:
                match.match_minute = match_minute

            match.home_score = match_data["score"]["fullTime"]["homeTeam"]
            match.away_score = match_data["score"]["fullTime"]["awayTeam"]

            match = self._match_service.update(match)

        return match

    def _dump_match_scores(self):
        if not self._dump_matches:
            return

        match_date = datetime.now().date()
        end_date = match_date + timedelta(days=1)

        filters = [("match_date", "greaterthanequalto", match_date),
                   ("match_date", "lessthanequalto", end_date),
                   ("use_match", "equalto", True)]

        matches = MatchService().list(filters=filters)
        matches = [m.to_dict(keys=["id",
                                   "home_team",
                                   "away_team",
                                   "home_score",
                                   "away_score",
                                   "status",
                                   "match_minute",
                                   "match_date"]) for m in matches]

        with open(self._dump_matches, "w") as fh:
            dump(fh, {"matches": matches})

    def _dump_player_scores(self):
        if not self._dump_scores:
            return

        match_date = datetime.now().date()
        end_date = match_date + timedelta(days=1)

        filters = [("match_date", "greaterthanequalto", match_date),
                   ("match_date", "lessthanequalto", end_date),
                   ("use_match", "equalto", True)]

        matches = MatchService().list(filters=filters)
        players = {str(p.id): {"name": f"{p.first_name} {p.last_name}",
                               "matches": [],
                               "score": 0} for p in PlayerService().list()}

        # get predictions for each player/match combination
        prediction_service = PredictionService()

        for m in matches:
            predictions = prediction_service.list({"match_id": m.id})

            for p in predictions:
                player = players.get(str(p.player_id))
                if not player:
                    continue

                correct = True if any([m.home_score and m.home_score > m.away_score and p.prediction == "home",
                                       m.away_score and m.away_score > m.home_score and p.prediction == "away",
                                       m.home_score and m.home_score == m.away_score and p.prediction == "draw"]) else False

                match = m.to_dict(keys=["home_team", "away_team"])
                match.update({"prediction": p.prediction, "correct": correct})

                players[str(p.player_id)]["score"] += 1 if correct else 0
                players[str(p.player_id)]["matches"].append(match)

        players = [p for p in players.values()]
        players.sort(key=lambda x: x["score"], reverse=True)

        with open(self._dump_scores, "w") as fh:
            dump(fh, {"scores": players})

    def process(self):
        start = datetime.now()

        if self._matchday:
            for league in self._leagues:
                print(f"extracting {league.name} scores for matchday {self._matchday}")

                for match in self._connectors[league].collect_historical_scores(league, self._matchday):
                    match = self._update_match(league, match)
                    if match:
                        print(f"updated {match.home_team} ({match.home_score}) vs {match.away_team} ({match.away_score})")

            self._dump_match_scores()
            return None

        while True:
            for league in self._leagues:
                print(f"extracting {league.name} scores for matchday {league.current_matchday}")

                for match in self._connectors[league].collect_scores(league):
                    match = self._update_match(league, match)
                    print(f"updated {match.home_team} ({match.home_score}) vs {match.away_team} ({match.away_score})")

            self._dump_match_scores()

            if datetime.now() > start + timedelta(seconds=self._max_run_seconds):
                break

            sleep(20)  # throttle
