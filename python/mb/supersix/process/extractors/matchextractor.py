from datetime import datetime

from mb.supersix.model import Match
from mb.supersix.service import LeagueService, MatchService

from .connectors.flashscoreconnector import FlashScoreConnector
from .connectors.footballapiconnector import FootballApiConnector


class MatchExtractor:
    _CONNECTORS = {
        "PL": FlashScoreConnector,
        "ELC": FlashScoreConnector,
        "EL1": FlashScoreConnector,
        "EL2": FlashScoreConnector
    }

    def __init__(self, matchdays_ahead=3, league=None):
        if league and league not in self._CONNECTORS:
            raise ValueError(f"league '{league}' not recognised")

        self._league = league
        self._matchdays_ahead = matchdays_ahead

        self._system = "supersix"
        self._component = "match-extractor"

        self._league_service = LeagueService()
        self._match_service = MatchService()

    def process(self):
        print(f"running match extractor for {self._matchdays_ahead} days ahead")

        # leagues
        for league in self._league_service.list():
            if self._league and league.code != self._league:
                continue

            if league.code not in self._CONNECTORS:
                print(f"skipping league '{league.code}', connector unknown")
                continue

            print(f"extracting matches for {league.name}...")

            connector = self._CONNECTORS[league.code]
            for match in connector.collect_matches(league, look_ahead=self._matchdays_ahead):
                start_time = datetime.strptime(match["utcDate"], "%Y-%m-%dT%H:%M:%SZ")

                match = Match(external_id=str(match["id"]),
                              league_id=league.id,
                              matchday=match["matchday"],
                              match_date=start_time,
                              status=match["status"],
                              home_team=match["homeTeam"]["name"],
                              away_team=match["awayTeam"]["name"])

                if self._match_service.get_from_external_id(match.external_id):
                    print(f"skipping [{match.matchday}] {match.home_team} vs {match.away_team}, already exists")
                    continue

                self._match_service.create(match)
                print(f"[{match.matchday}] {match.home_team} vs {match.away_team} extracted")

        print("extraction complete")
