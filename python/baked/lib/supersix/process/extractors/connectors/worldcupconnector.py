from datetime import datetime, timedelta
from pytz import timezone, utc
from bs4 import BeautifulSoup
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from re import compile

from .flashscoreconnectorv2 import FlashScoreConnectorV2


class WorldCupConnector(FlashScoreConnectorV2):
    _LEAGUE_MAP = {
        "WC": ("world", "world-cup",)
    }

    def collect_matches(self, league, matchday=None, look_ahead=3):
        current_matchday = matchday or league.current_matchday or 1
        matchday_to = current_matchday + look_ahead
        matchdays = [
            f"Round {m}" if m < 4 else {
                4: "1/8-finals",
                5: "Quarter-finals",
                6: "Semi-finals",
                7: "3rd place",
                8: "Final"
            }[m] 
            for m in range(current_matchday, matchday_to)
        ]

        content = self._fetch_content(league.code, content_type="fixtures")
        table = content.find("div", attrs={"class": "sportName"})

        matches = []
        round_regex = compile(r"Round \d")
        finals_regex = compile(r"1\/8-finals|Quarter-finals|Semi-finals|Final")
        now = datetime.now()

        collect = None
        finals = None
        match_divs = table.find_all("div", attrs={"class": ["event__round", "event__match"]}) or []
        for div in match_divs:
            if round_regex.match(div.text):
                if div.text in matchdays:
                    collect = div.text
                    finals = None
                else:
                    collect = None
                    finals = None

            elif finals_regex.match(div.text):
                if div.text in matchdays:
                    collect = div.text
                    finals = True
                else:
                    collect = None
                    finals = None

            if collect:
                if finals:
                    matchday = {
                        "1/8-finals": 4,
                        "Quarter-finals": 5,
                        "Semi-finals": 6,
                        "3rd place": 7,
                        "Final": 8
                    }[collect]
                else:
                    matchday = int(collect.replace("Round ", ""))

                home_team_div = div.find("div", attrs={"class": ["event__participant--home"]})
                away_team_div = div.find("div", attrs={"class": ["event__participant--away"]})

                postponed_div = div.find("div", attrs={"class": ["event__stage--block"]})

                if postponed_div and postponed_div.text == "Postp":
                    # Postponed matches no longer have date/time associated with them. Return what we can and the extractor
                    # will have to try and find the match in the database to change the status for.
                    matches.append({"matchday": matchday,
                                    "status": "POSTPONED",
                                    "homeTeam": {"name": home_team_div.text},
                                    "awayTeam": {"name": away_team_div.text}})

                else:
                    match_date_div = div.find("div", attrs={"class": ["event__time"]})
                    if all([match_date_div, home_team_div, away_team_div]):
                        match_date = datetime.strptime(match_date_div.text, "%d.%m. %H:%M")
                        match_date = match_date.replace(year=now.year + (1 if match_date.month < now.month else 0))
                        match_date = self._matchdate_toutc(match_date)
                        match_date_str = match_date.strftime("%Y-%m-%d %H:%M:%S")

                        matches.append({"id": self._generate_match_id(home_team_div.text, away_team_div.text, match_date),
                                        "matchday": matchday,
                                        "utcDate": match_date_str,
                                        "status": "SCHEDULED",
                                        "homeTeam": {"name": home_team_div.text},
                                        "awayTeam": {"name": away_team_div.text}})

        return matches

    def collect_historical_scores(self, league, start_matchday, end_matchday):
        content = self._fetch_content(league.code, content_type="results")
        table = content.find("div", attrs={"class": "sportName"})

        matches = []
        round_regex = compile(r"Round \d")
        finals_regex = compile(r"^1\/8-finals|Quarter-finals|Semi-finals|Final$")
        now = datetime.now()
        
        rounds = [
            f"Round {md}" if md < 4 else {
                4: "1/8-finals",
                5: "Quarter-final",
                6: "Semi-final",
                7: "Final"
            }[md] 
            for md in range(start_matchday, end_matchday + 1, 1)
        ]

        for div in table.find_all("div", attrs={"class": ["event__round", "event__match"]}):
            collect = None

            if round_regex.match(div.text):
                if div.text in rounds:
                    collect = div.text

            elif finals_regex.match(div.text):
                if div.text in rounds:
                    collect = div.text

            if collect:
                if round_regex.match(div.text):
                    continue

                elif finals_regex.match(div.text):
                    continue

                match_date = div.find("div", attrs={"class": "event__time"}).text
                extra_time = None
                penalties = None

                # Flash score denotes extra time or penalities in the same div as the match date.
                if match_date[-3:].lower() == "pen":
                    penalties = True
                    match_date = match_date[:-3]
                elif match_date[-3:].lower() == "aet":
                    extra_time = True
                    match_date = match_date[:-3]

                match_date = datetime.strptime(match_date, "%d.%m. %H:%M")
                match_date = match_date.replace(year=now.year)
                match_date = self._matchdate_toutc(match_date)
                match_date_str = match_date.strftime("%Y-%m-%d %H:%M:%S")

                matchday = int(collect.replace("Round ", ""))

                home_team = div.find("div", attrs={"class": "event__participant--home"}).text
                away_team = div.find("div", attrs={"class": "event__participant--away"}).text

                home_score = div.find("div", attrs={"class": "event__score--home"}).text
                away_score = div.find("div", attrs={"class": "event__score--away"}).text
                
                # check fix to ensure postponed matches aren't processed.
                try:
                    int(home_score)
                    int(away_score)
                except ValueError:
                    continue

                matches.append({"id": self._generate_match_id(home_team, away_team, match_date),
                                "matchday": matchday,
                                "utcDate": match_date_str,
                                "status": "FINISHED",
                                "homeTeam": {"name": home_team},
                                "awayTeam": {"name": away_team},
                                "score": {
                                    "fullTime": {
                                        "homeTeam": home_score.strip(),
                                        "awayTeam": away_score.strip()}
                                    },
                                "extra_time": extra_time,
                                "penalties": penalties
                                })

        return matches

    def collect_scores(self, league, matchday, live=False):
        if not live:
            return self.collect_historical_scores(league, matchday, matchday)

        content = self._fetch_content(league.code)
        table = content.find("div", attrs={"class": "sportName"})

        matches = []

        for div in table.find_all("div", attrs={"class": "event__match"}):
            event_stage = div.find("div", attrs={"class": "event__stage"})
            if not event_stage:
                continue

            detail = div.find("div", attrs={"class": "event__stage--block"}).text
            extra_time = None
            penalties = None

            # Flash score denotes extra time or penalities in the same div as the match date.
            if detail.lower() == "after pen.":
                penalties = True
            elif detail.lower() == "after aet.":
                extra_time = True

            minute = 0
            status = event_stage.text
            if status != "Finished":
                if status == "Half Time":
                    minute = 45
                else:
                    try:
                        minute = int(status)

                    except ValueError:
                        pass
                
                status = "In Play"
            else:
                minute = 90

            status = status.upper()

            home_score = div.find("div", attrs={"class": "event__score--home"}).text
            away_score = div.find("div", attrs={"class": "event__score--away"}).text
            
            # check fix to ensure postponed matches aren't processed.
            try:
                int(home_score)
                int(away_score)
            except ValueError:
                continue

            home_team = div.find("div", attrs={"class": "event__participant--home"}).text
            away_team = div.find("div", attrs={"class": "event__participant--away"}).text

            # It's possible for 'GOAL' to appear in the home_team name if just gone in.
            # Due to the nature of team names, this is safe. Even even the word goal were to appear in a team name, it won't be all caps. 
            home_team = home_team.replace("GOAL", "")

            matches.append({"id": self._generate_match_id(home_team, away_team, datetime.utcnow()),
                            "status": status,
                            "homeTeam": {"name": home_team},
                            "awayTeam": {"name": away_team},
                            "score": {
                            "fullTime": {
                                "homeTeam": home_score.strip(),
                                "awayTeam": away_score.strip()}
                            },
                            "minute": minute,
                            "extra_time": extra_time, 
                            "penalties": penalties})

        return matches
