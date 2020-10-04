from datetime import datetime

from mb.supersix.model import League
from mb.supersix.service.leagueservice import LeagueService

from .connectors.footballapiconnector import FootballApiConnector


class LeagueExtractor:

    def __init__(self):
        self._system = "supersix"
        self._component = "league-extractor"

        self._connector = FootballApiConnector
        self._league_service = LeagueService()

    def process(self):
        for league in self._connector.collect_leagues():
            league = League(name=league["name"],
                            code=league["code"],
                            start_date=datetime.strptime(league["currentSeason"]["startDate"], "%Y-%m-%d"),
                            current_matchday=league["currentSeason"]["currentMatchday"])

            if not league.start_date or not league.code:
                print(f"skipping {league.name}, missing code/current season")
                continue

            if self._league_service.get(league.id):
                self._league_service.update(league)
                print(f"{league.name} updated")
            else:
                self._league_service.create(league)
                print(f"{league.name} extracted")
