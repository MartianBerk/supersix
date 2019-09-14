import requests

from mylib.supersix.model import League, Match
from mylib.supersix.service import LeagueService


class MatchExtractor:
    _URL = "https://api.football-data.org/v2/competitions"
    _KEY = "9c3a13b8586d4ba9af6723ffa1e15c67"  # secure credential

    def __init__(self, days_ahead=21, leagues=False):
        self._days_ahead = days_ahead
        self._leagues = leagues

    def _collect_leagues(self):
        response = requests.get(f"{self._URL}?areas=2072")
        if response.status_code != 200:
            raise ConnectionError(f"[{response.status_code}] {response.text}")

        response = response.json()
        return response["competitions"]

    def _collect_matches(self):
        return []

    def process(self):
        print(f"running match extractor for {self._days_ahead} days ahead")

        if self._leagues:
            print("extracting leagues...")
            league_service = LeagueService()
            for league in self._collect_leagues():
                league = League(league["id"], league["code"], league["name"])
                if league_service.get(league):
                    print(f"skipping {league.name}, already extracted")

                league_service.create(league)
                print(f"{league.name} extracted")

        print("extracting matches...")
        for match in self._collect_matches():
            pass


if __name__ == "__main__":
    MatchExtractor(leagues=True).process()
