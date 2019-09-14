import requests

from mylib.supersix.model import League, Match
from mylib.supersix.service import LeagueService, MatchService


class MatchExtractor:
    _URL = "https://api.football-data.org/v2/competitions"
    _KEY = "9c3a13b8586d4ba9af6723ffa1e15c67"  # secure credential

    def __init__(self, days_ahead=21, leagues=False):
        self._days_ahead = days_ahead
        self._leagues = leagues

        self._league_service = LeagueService()
        self._match_service = MatchService()

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
            for league in self._collect_leagues():
                league = League(league["id"], league["name"], league["currentSeason"]["startDate"], code=league["code"])
                if not league.get("currentSeason") or not league.get("code"):
                    print(f"skipping {league.name}, missing code/current season")
                    continue

                if self._league_service.get(league):
                    print(f"skipping {league.name}, already exists")
                    continue

                self._league_service.create(league)
                print(f"{league.name} extracted")

        for league in self._league_service.list():
            league = League(league["id"], league["name"], league["currentSeason"]["startDate"], code=league["code"])
            if not league.code:  # TODO: improve DB filtering to include NULL/NOT NULL
                print(f"skipping {league.name}, missing code")
                continue

            print(f"extracting matches for {league.name}...")
            for match in self._collect_matches():
                print(match)


if __name__ == "__main__":
    MatchExtractor(leagues=True).process()
