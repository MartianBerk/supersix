import requests

from mylib.supersix.model import Match
from mylib.supersix.service import LeagueService, MatchService


class ScoreExtractor:
    _URL = "https://api.football-data.org/v2/competitions"
    _KEY = "9c3a13b8586d4ba9af6723ffa1e15c67"  # TODO: secure credential

    def __init__(self, matchday):
        self._matchday = matchday

        self._league_service = LeagueService()
        self._match_service = MatchService()

    # TODO: test... not sure how "realtime" the scores are
    def _collect_matches(self, league):
        response = requests.get(f"{self._URL}/{league.code}/matches?matchday={self._matchday}",
                                headers={"X-Auth-Token": self._KEY})
        if response.status_code != 200:
            print(f"[{response.status_code}] {response.text}")
            return []

        response = response.json()
        return response["matches"]

    def process(self):
        print(f"extracting scores for matchday {self._matchday}")

        for league in self._league_service.list():
            for match in self._collect_matches(league):
                match = Match(id=match["id"],
                              home_score=match["score"]["fullTime"]["homeTeam"],
                              away_score=match["score"]["fullTime"]["homeTeam"])

                match = self._match_service.update(match, keys=["id", "home_score", "away_score"])
                print(f"updated {match.home_team} ({match.home_score}) vs {match.away_team} ({match.away_score})")


if __name__ == "__main__":
    ScoreExtractor(5).process()
