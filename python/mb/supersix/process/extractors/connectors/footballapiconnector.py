import requests

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
    def collect_matches(cls, league, look_ahead=3):
        matches = []
        current_matchday = league.current_matchday or 1

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

        return matches
