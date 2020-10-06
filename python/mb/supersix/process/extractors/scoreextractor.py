from datetime import datetime, timedelta
from time import sleep

from mb.supersix.model import Match
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
            raise ValueError(f"skipping league '{league.code}', connector unknown")

        self._league = LeagueService().get_from_league_code(league)
        self._matchday = matchday
        self._max_run_seconds = max_run_seconds

        self._connector = self._CONNECTORS[self._league.code]
        self._match_service = MatchService()

    def _update_match(self, match_data):
        match = self._match_service.get_from_external_id(match_data["id"])
        if not match:
            start_time = datetime.strptime(match_data["utcDate"], "%Y-%m-%dT%H:%M:%SZ")

            match = Match(external_id=str(match_data["id"]),
                          league_id=self._league.id,
                          matchday=match_data["matchday"],
                          match_date=start_time,
                          status=match_data["status"],
                          home_team=match_data["homeTeam"]["name"],
                          away_team=match_data["awayTeam"]["name"])

            match = self._match_service.create(match)
        else:
            match.status = match_data["status"]
            match.match_minute = match_data.get("minute") or 90
            match.home_score = match_data["score"]["fullTime"]["homeTeam"]
            match.away_score = match_data["score"]["fullTime"]["awayTeam"]

            match = self._match_service.update(match)

        return match

    def process(self):
        print(f"extracting {self._league.name} scores for matchday {self._matchday or self._league.current_matchday}")
        start = datetime.now()

        if self._matchday:
            for match in self._connector.collect_historical_scores(self._league, self._matchday):
                match = self._update_match(match)
                if match:
                    print(f"updated {match.home_team} ({match.home_score}) vs {match.away_team} ({match.away_score})")

            return None

        while True:
            for match in self._connector.collect_scores(self._league):
                match = self._update_match(match)
                print(f"updated {match.home_team} ({match.home_score}) vs {match.away_team} ({match.away_score})")

            if datetime.now() > start + timedelta(seconds=self._max_run_seconds):
                break

            sleep(20)  # throttle
