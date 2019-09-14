import requests

from datetime import datetime
from time import sleep

from mylib.supersix.model import League, Match
from mylib.supersix.service import LeagueService, MatchService


class MatchExtractor:
    _URL = "https://api.football-data.org/v2/competitions"
    _KEY = "9c3a13b8586d4ba9af6723ffa1e15c67"  # TODO: secure credential

    def __init__(self, matchdays_ahead=3, leagues=False):
        self._matchdays_ahead = matchdays_ahead
        self._leagues = leagues

        self._league_service = LeagueService()
        self._match_service = MatchService()

        self._matchdays = {}

    def _collect_leagues(self):
        response = requests.get(f"{self._URL}?areas=2072",
                                headers={"X-Auth-Token": self._KEY})
        if response.status_code != 200:
            print(f"[{response.status_code}] {response.text}")
            return []

        response = response.json()
        return response["competitions"]

    def _collect_matches(self, league):
        matches = []
        current_matchday = league.current_matchday or 1

        for i in range(current_matchday, current_matchday + self._matchdays_ahead):
            response = requests.get(f"{self._URL}/{league.code}/matches?matchday={i}",
                                    headers={"X-Auth-Token": self._KEY})
            if response.status_code != 200:
                print(f"[{response.status_code}] {response.text}")
                return []

            response = response.json()
            matches.extend(response["matches"])

            sleep(1)  # throttle

        return matches

    def process(self):
        print(f"running match extractor for {self._matchdays_ahead} days ahead")

        # leagues
        for league in self._collect_leagues():
            league = League(id=league["id"],
                            name=league["name"],
                            start_date=datetime.strptime(league["currentSeason"]["startDate"], "%Y-%m-%d"),
                            code=league["code"],
                            current_matchday=league["currentSeason"]["currentMatchday"])

            if not league.start_date or not league.code:
                print(f"skipping {league.name}, missing code/current season")
                continue

            self._matchdays[league.code] = league.current_matchday

            if self._league_service.get(league.id):
                print(f"skipping {league.name}, already exists")
                continue

            self._league_service.create(league)
            print(f"{league.name} extracted")

        # matches
        for league in self._league_service.list():
            league = League(id=league.id,
                            name=league.name,
                            start_date=league.start_date,
                            code=league.code,
                            current_matchday=league.current_matchday)

            print(f"extracting matches for {league.name}...")
            for match in self._collect_matches(league):
                match = Match(id=match["id"],
                              league_id=league.id,
                              matchday=match["matchday"],
                              match_date=match["utcDate"],
                              home_team=match["homeTeam"]["name"],
                              away_team=match["awayTeam"]["name"])

                if self._match_service.get(match.id):
                    print(f"skipping [{match.matchday}] {match.home_team} vs {match.away_team}, already exists")
                    continue

                self._match_service.create(match)
                print(f"[{match.matchday}] {match.home_team} vs {match.away_team} extracted")

        print("extraction complete")
