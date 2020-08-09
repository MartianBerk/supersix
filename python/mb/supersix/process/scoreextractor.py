import requests

from argparse import ArgumentParser
from datetime import datetime, timedelta
from time import sleep

from mb.supersix.service import MatchService


class ScoreExtractor:
    _URL = "https://api.football-data.org/v2/competitions"
    _KEY = "9c3a13b8586d4ba9af6723ffa1e15c67"  # TODO: secure credential

    def __init__(self, league, matchday, max_run_seconds=0):
        self._league = league
        self._matchday = matchday
        self._max_run_seconds = max_run_seconds

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
        start = datetime.now()

        while True:
            for match in self._collect_matches():
                home = match["score"]["fullTime"]["homeTeam"]
                away = match["score"]["fullTime"]["awayTeam"]

                matches = self._match_service.list(filters={"id": match["id"], "use_match": 1})  # TODO: update mylib to handle bool
                if not matches:
                    continue

                match = matches[0]

                match.home_score = home
                match.away_score = away

                self._match_service.update(match)
                print(f"updated {match.home_team} ({match.home_score}) vs {match.away_team} ({match.away_score})")

            if datetime.now() > start + timedelta(seconds=self._max_run_seconds):
                break

            sleep(20)  # throttle


if __name__ == "__main__":
    parser = ArgumentParser(description="Score extractor")
    parser.add_argument("-l", "--league", type=str, help="League code to extract")
    parser.add_argument("-m", "--matchday", type=int, help="Matchday")
    parser.add_argument("-s", "--max_run_seconds", type=int, default=0, help="Run for seconds.")
    args = vars(parser.parse_args())

    ScoreExtractor(**args).process()
