from datetime import datetime, timedelta
from math import floor

from .footballapiconnector import FootballApiConnector


class WorldCupConnector(FootballApiConnector):

    def _generate_match_id(self, home_team: str, away_team: str, match_date: datetime):
        """
        Generate a match_id by concatenating home-away-season (where season resembles 2020-2021 for example).
        """
        return "-".join([
            home_team,
            away_team,
            str(match_date.year - (1 if match_date.month < 7 else 0)),  # Use July as season cutoff 
            str(match_date.year + (1 if match_date.month > 7 else 0))
        ])

    def _parse_match(self, match):
        """Helper function to parse a match to format it correctly."""
        match_date = datetime.strptime(match["utcDate"], "%Y-%m-%dT%H:%M:%SZ")
        match_id = self._generate_match_id(match["homeTeam"]["name"], match["awayTeam"]["name"], match_date)

        if match["status"] not in ("SCHEDULED", "FINISHED"):
            match["status"] = "In Play"
            match["minute"] = floor((datetime.now() - match_date).seconds / 60)

        elif match["status"] == "FINISHED":
            match["minute"] = 90

        if match["score"]["duration"] == "PENALTY_SHOOTOUT":
            winner = "home" if match["score"]["fullTime"]["homeTeam"] > match["score"]["fullTime"]["awayTeam"] else "away"
            home_score = match["score"]["fullTime"]["homeTeam"] - match["score"]["penalties"]["homeTeam"]
            away_score = match["score"]["fullTime"]["awayTeam"] - match["score"]["penalties"]["awayTeam"]
            match["score"]["fullTime"]["homeTeam"] = home_score + (1 if winner == "home" else 0)
            match["score"]["fullTime"]["awayTeam"] = away_score + (1 if winner == "away" else 0)

        elif match["score"]["duration"] == "PENALTY_SHOOTOUT":
            winner = "home" if match["score"]["fullTime"]["homeTeam"] > match["score"]["fullTime"]["awayTeam"] else "away"
            home_score = match["score"]["fullTime"]["homeTeam"] - match["score"]["extraTime"]["homeTeam"]
            away_score = match["score"]["fullTime"]["awayTeam"] - match["score"]["extraTime"]["awayTeam"]
            match["score"]["fullTime"]["homeTeam"] = home_score + (1 if winner == "home" else 0)
            match["score"]["fullTime"]["awayTeam"] = away_score + (1 if winner == "away" else 0)
        
        match.update({
            "id": match_id,
            "utcDate": match_date.strftime("%Y-%m-%d %H:%M:%S"),
            **(
                {
                    "extra_time": match["score"]["duration"] == "EXTRA_TIME",
                    "penalties": match["score"]["duration"] == "PENALTY_SHOOTOUT"
                } if match["status"] == "FINISHED" else {}
            )
        })

        return match

    def collect_matches(self, league, matchday=None, look_ahead=3):
        matches = super().collect_matches(league, matchday=matchday, look_ahead=look_ahead)
        matches = [self._parse_match(m) for m in matches if all([m["homeTeam"]["name"], m["homeTeam"]["name"]])]

        return matches

    def collect_historical_scores(self, league, start_matchday, end_matchday):
        matches = super().collect_historical_scores(league, start_matchday, end_matchday)
        matches = [self._parse_match(m) for m in matches if m["status"] == "FINISHED"]

        return matches

    def collect_scores(self, league, matchday, live=False):
        matches = super().collect_scores(league)
        matches = [self._parse_match(m) for m in matches if all([m["homeTeam"]["name"], m["homeTeam"]["name"]])]

        return matches
