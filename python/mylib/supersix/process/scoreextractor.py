import requests

from mylib.supersix.service import MatchService


class ScoreExtractor:
    _URL = "https://api.football-data.org/v2/competitions"
    _KEY = "9c3a13b8586d4ba9af6723ffa1e15c67"  # TODO: secure credential

    def __init__(self, league, matchday):
        self._league = league
        self._matchday = matchday

        self._match_service = MatchService()

    # TODO: test... not sure how "realtime" the scores are
    def _collect_matches(self):
        response = requests.get(f"{self._URL}/{self._league}/matches?matchday={self._matchday}",
                                headers={"X-Auth-Token": self._KEY})
        if response.status_code != 200:
            print(f"[{response.status_code}] {response.text}")
            return []

        response = response.json()
        return response["matches"]

    def process(self):
        print(f"extracting {self._league} scores for matchday {self._matchday}")

        for match in self._collect_matches():
            home = match["score"]["fullTime"]["homeTeam"]
            away = match["score"]["fullTime"]["awayTeam"]

            match = self._match_service.get(match["id"])

            match.home_score = home
            match.away_score = away

            self._match_service.update(match)
            print(f"updated {match.home_team} ({match.home_score}) vs {match.away_team} ({match.away_score})")
