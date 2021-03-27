from datetime import datetime, timedelta
from time import sleep

from baked.lib.supersix.model import Match
from baked.lib.supersix.service import LeagueService, MatchService, PlayerService, PredictionService, RoundService

from .connectors.flashscoreconnectorv2 import FlashScoreConnectorV2


class ScoreExtractor:
    _CONNECTORS = {
        "PL": FlashScoreConnectorV2,
        "ELC": FlashScoreConnectorV2,
        "EL1": FlashScoreConnectorV2,
        "EL2": FlashScoreConnectorV2
    }

    def __init__(self, leagues=None, matchday=None, max_run_seconds=0):
        leagues = leagues or []
        for league in leagues:
            if league not in self._CONNECTORS.keys():
                raise ValueError(f"league '{league}', connector unknown")

        self._leagues = [LeagueService().get_from_league_code(l) for l in leagues]
        self._matchday = matchday
        self._max_run_seconds = max_run_seconds

        self._connectors = {l: self._CONNECTORS[l.code]() for l in self._leagues}
        self._match_service = MatchService()

    def _update_match(self, league, match_data):
        match = self._match_service.get_from_external_id(match_data["id"])
        if not match:
            start_time = match_data.get("utcDate")
            if start_time:
                start_time = datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%SZ")

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

    def process(self):
        start = datetime.now()

        if self._matchday:
            for league in self._leagues:
                print(f"extracting {league.name} scores for matchday {self._matchday}")

                try:
                    matches = self._connectors[league].collect_historical_scores(league, self._matchday)
                except ConnectionError:
                    pass
                else:
                    for match in matches:
                        match = self._update_match(league, match)
                        if match:
                            print(f"updated {match.home_team} ({match.home_score}) vs {match.away_team} ({match.away_score})")

            return None

        while True:
            for league in self._leagues:
                print(f"extracting {league.name} scores for matchday {league.current_matchday}")

                try:
                    scores = self._connectors[league].collect_scores(league)
                    
                    for match in scores:
                        match = self._update_match(league, match)
                        print(f"updated {match.home_team} ({match.home_score}) vs {match.away_team} ({match.away_score})")

                except Exception as e:
                    print(f"extraction issue with {league.name}: {str(e)}. Skipping...")

            if datetime.now() > start + timedelta(seconds=self._max_run_seconds):
                break

            sleep(10)  # throttle
