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
            if not league.get("code"):
                continue  # safety net

            league = League(name=league["name"],
                            code=league["code"],
                            start_date=datetime.strptime(league["currentSeason"]["startDate"], "%Y-%m-%d"),
                            current_matchday=league["currentSeason"]["currentMatchday"])

            if not league.start_date or not league.code:
                print(f"skipping {league.name}, missing code/current season")
                continue

            existing_league = self._league_service.get_from_league_code(league.code)
            if existing_league:
                existing_league.current_matchday = league.current_matchday
                self._league_service.update(existing_league)
                print(f"{league.name} updated")
            else:
                self._league_service.create(league)
                print(f"{league.name} extracted")
