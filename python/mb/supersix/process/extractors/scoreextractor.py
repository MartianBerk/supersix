from datetime import datetime, timedelta
from time import sleep

from mb.supersix.service import LeagueService, MatchService

from .connectors.flashscoreconnector import FlashScoreConnector
from .connectors.footballapiconnector import FootballApiConnector


class ScoreExtractor:
    _CONNECTORS = {
        "PL": FootballApiConnector,
        "ELC": FootballApiConnector,
        "EL1": FlashScoreConnector,
        "EL2": FlashScoreConnector
    }

    def __init__(self, league, matchday=None, max_run_seconds=0):
        if league not in self._CONNECTORS.keys():
            raise ValueError(f"skipping league '{self._league.code}', connector unknown")

        self._league = LeagueService().get_from_league_code(league)
        self._matchday = matchday
        self._max_run_seconds = max_run_seconds

        self._connector = self._CONNECTORS[league.code]
        self._match_service = MatchService()

    def _update_match(self, match):
        match = self._match_service.get_from_external_id(match["id"])
        if not match:
            return None

        match.status = match["status"]
        match.match_minute = match.get("minute") or 90
        match.home_score = match["score"]["fullTime"]["homeTeam"]
        match.away_score = match["score"]["fullTime"]["awayTeam"]

        self._match_service.update(match)

    def process(self):
        print(f"extracting {self._league} scores for matchday {self._matchday or self._league.current_matchday}")
        start = datetime.now()

        if self._matchday:
            for match in self._connector.collect_historical_scores(self._league, self._matchday):
                self._update_match(match)
                print(f"updated {match.home_team} ({match.home_score}) vs {match.away_team} ({match.away_score})")

            return None

        while True:
            for match in self._connector.collect_scores(self._league):
                self._update_match(match)
                print(f"updated {match.home_team} ({match.home_score}) vs {match.away_team} ({match.away_score})")

            if datetime.now() > start + timedelta(seconds=self._max_run_seconds):
                break

            sleep(20)  # throttle
