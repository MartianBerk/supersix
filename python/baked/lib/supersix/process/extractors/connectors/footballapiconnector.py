import requests

from datetime import datetime
from time import sleep

from .abstractconnector import AbstractConnector


class FootballApiConnector(AbstractConnector):
    _URL = "https://api.football-data.org/v2/competitions"
    _KEY = "9c3a13b8586d4ba9af6723ffa1e15c67"  # TODO: secure credential

    @classmethod
    def collect_leagues(cls):
        response = requests.get(f"{cls._URL}?areas=2072", headers={"X-Auth-Token": cls._KEY})
        if response.status_code != 200:
            print(f"[{response.status_code}] {response.text}")
            return []

        response = response.json()
        return response["competitions"]

    @classmethod
    def collect_world_cup(cls):
        """A special function to collect specifically the world cup."""
        response = requests.get(f"{cls._URL}?areas=2267", headers={"X-Auth-Token": cls._KEY})
        if response.status_code != 200:
            print(f"[{response.status_code}] {response.text}")
            return []

        response = response.json()
        for comp in response["competitions"]:
            if comp["code"] == "WC":
                return comp

    @staticmethod
    def _generate_match_id(home_team: str, away_team: str, match_date: datetime):
        """
        Generate a match_id by concatenating home-away-season (where season resembles 2020-2021 for example).
        """
        return "-".join([
            home_team,
            away_team,
            str(match_date.year - (1 if match_date.month < 7 else 0)),  # Use July as season cutoff 
            str(match_date.year + (1 if match_date.month > 7 else 0))
        ])

    @staticmethod
    def _parse_match(match):
        """Helper function to parse a match to format it correctly."""
        match_date = datetime.strptime(match["utcDate"], "%Y-%m-%dT%H:%M:%SZ")
        match_id = FootballApiConnector._generate_match_id(match["homeTeam"]["name"], match["awayTeam"]["name"], match_date)
        
        match.update({
            "id": match_id,
            "utcDate": match_date.strftime("%Y-%m-%d %H:%M:%S"),
            "extra_time": match["score"]["duration"] == "EXTRA_TIME",
            "penalties": match["score"]["duration"] == "PENALTY_SHOOTOUT"
        })

        return match

    @classmethod
    def collect_matches(cls, league, matchday=None, look_ahead=3):
        matches = []
        current_matchday = matchday or league.current_matchday or 1

        for i in range(current_matchday, current_matchday + look_ahead):
            response = requests.get(f"{cls._URL}/{league.code}/matches?matchday={i}", headers={"X-Auth-Token": cls._KEY})
            if response.status_code != 200:
                print(f"[{response.status_code}] {response.text}")
                return []

            response = response.json()
            matches.extend(response["matches"])

            sleep(1)  # throttle

        return matches

    @classmethod
    def collect_historical_scores(cls, league, matchday):
        response = requests.get(f"{cls._URL}/{league.code}/matches?matchday={matchday}",
                                headers={"X-Auth-Token": cls._KEY})
        if response.status_code != 200:
            print(f"[{response.status_code}] {response.text}")
            return []

        response = response.json()
        matches = response["matches"]
        matches = [cls._parse_match(m) for m in matches]

        return matches

    @classmethod
    def collect_scores(cls, league, matchday=None):
        if matchday:
            return cls.collect_historical_scores(league, matchday)

        response = requests.get(f"{cls._URL}/{league.code}/matches?matchday={league.current_matchday}",
                                headers={"X-Auth-Token": cls._KEY})
        if response.status_code != 200:
            print(f"[{response.status_code}] {response.text}")
            return []

        response = response.json()
        matches = response["matches"]
        matches = [cls._parse_match(m) for m in matches]

        return matches
