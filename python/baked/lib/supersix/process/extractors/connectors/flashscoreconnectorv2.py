from datetime import datetime, timedelta
from pytz import timezone, utc
from bs4 import BeautifulSoup
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from re import compile

from .abstractconnector import AbstractConnector


class FlashScoreConnectorV2(AbstractConnector):
    _URL_PATTERN = "https://www.flashscore.com/football/england/%s/"
    _LEAGUE_MAP = {
        "PL": "premier-league",
        "ELC": "championship",
        "EL1": "league-one",
        "EL2": "league-two"
    }
    _REFRESH_CONNECTION_SECS = 300

    def __init__(self):
        self.__connector = None
        self._league_connections = {}

    def _get_connection(self):
        options = Options()
        options.add_argument("--headless")
        return Chrome(options=options)

    def _fetch_content(self, league, content_type=None):
        if content_type and content_type not in ["fixtures", "results"]:
            raise ValueError("invalid content_type")
        elif league not in self._LEAGUE_MAP:
            raise ValueError("invalid league")

        if league not in self._league_connections:
            print(f"connecting to {league}")
            url = (self._URL_PATTERN % self._LEAGUE_MAP[league])
            if content_type:
                url = url + f"{content_type}/"

            connection = self._get_connection()
            connection.get(url)
            self._league_connections[league] = {"connection": connection,
                                                "last_refresh": datetime.now()}
        elif datetime.now() > self._league_connections[league]["last_refresh"] + timedelta(seconds=self._REFRESH_CONNECTION_SECS):
            print(f"refreshing connection to {league}")
            url = (self._URL_PATTERN % self._LEAGUE_MAP[league])
            if content_type:
                url = url + f"{content_type}/"

            self._league_connections[league]["connection"].get(url)
            self._league_connections[league]["last_refresh"] = datetime.now()

        html = self._league_connections[league]["connection"].page_source
        return BeautifulSoup(html, "lxml")

    @staticmethod
    def _matchdate_toutc(match_date):
        tz = timezone("Europe/London")
        match_date = tz.localize(match_date)

        return match_date.astimezone(utc)

    def collect_leagues(self):
        raise NotImplementedError("collect_leagues not supported")

    def collect_matches(self, league, matchday=None, look_ahead=3):
        current_matchday = matchday or league.current_matchday or 1
        matchday_to = current_matchday + look_ahead
        matchdays = [f"Round {m}" for m in range(current_matchday, matchday_to)]

        content = self._fetch_content(league.code, content_type="fixtures")
        table = content.find("div", attrs={"class": "sportName"})

        matches = []
        round_regex = compile(r"Round \d")
        match_regex = compile(r"(\d+\.\d+\. \d+:\d+)(.+)-(.+)")
        now = datetime.now()

        collect = None
        match_divs = table.find_all("div", attrs={"class": ["event__round", "event__match"]}) or []
        for div in match_divs:
            if round_regex.match(div.text):
                if div.text in matchdays:
                    collect = div.text
                else:
                    collect = None

            if collect:
                m = match_regex.match(div.text)
                if m:
                    match_date = datetime.strptime(m.group(1), "%d.%m. %H:%M")
                    match_date = match_date.replace(year=now.year + (1 if match_date.month < now.month else 0))
                    match_date = self._matchdate_toutc(match_date)
                    match_date = match_date.strftime("%Y-%m-%dT%H:%M:%SZ")

                    matches.append({"id": "-".join([m.group(2), m.group(3)]),
                                    "matchday": int(collect.replace("Round ", "")),
                                    "utcDate": match_date,
                                    "status": "SCHEDULED",
                                    "homeTeam": {"name": m.group(2)},
                                    "awayTeam": {"name": m.group(3)}})

        return matches

    def collect_historical_scores(self, league, matchday):
        content = self._fetch_content(league.code, content_type="results")
        table = content.find("div", attrs={"class": "sportName"})

        matches = []
        round_regex = compile(r"Round \d")
        now = datetime.now()

        collect = None
        for div in table.find_all("div", attrs={"class": ["event__round", "event__match"]}):
            if round_regex.match(div.text):
                if div.text == f"Round {matchday}":
                    collect = div.text
                else:
                    collect = None

            if collect:
                if round_regex.match(div.text):
                    continue

                match_date = div.find("div", attrs={"class": "event__time"}).text
                match_date = datetime.strptime(match_date, "%d.%m. %H:%M")
                match_date = match_date.replace(year=now.year + (1 if match_date.month < now.month else 0))
                match_date = self._matchdate_toutc(match_date)
                match_date = match_date.strftime("%Y-%m-%dT%H:%M:%SZ")

                scores = div.find("div", attrs={"class": "event__scores"}).text
                scores = scores.replace(" ", "")
                home_score, away_score = scores.split("-")

                home_team = div.find("div", attrs={"class": "event__participant--home"}).text
                away_team = div.find("div", attrs={"class": "event__participant--away"}).text

                matches.append({"id": "-".join([home_team, away_team]),
                                "matchday": int(collect.replace("Round ", "")),
                                "utcDate": match_date,
                                "status": "FINISHED",
                                "homeTeam": {"name": home_team},
                                "awayTeam": {"name": away_team},
                                "score": {
                                    "fullTime": {
                                        "homeTeam": home_score.strip(),
                                        "awayTeam": away_score.strip()}
                                    }
                                })

        return matches

    def collect_scores(self, league, matchday=None):
        if matchday:
            return self.collect_historical_scores(league, matchday)

        content = self._fetch_content(league.code)
        table = content.find("div", attrs={"class": "event--live"})

        matches = []

        for div in table.find_all("div", attrs={"class": "event__match"}):
            event_stage = div.find("div", attrs={"class": "event__stage"})
            if not event_stage:
                continue

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

            scores = div.find("div", attrs={"class": "event__scores"}).text
            scores = scores.replace("\xa0", "")
            home_score, away_score = scores.split("-")

            home_team = div.find("div", attrs={"class": "event__participant--home"}).text
            away_team = div.find("div", attrs={"class": "event__participant--away"}).text

            matches.append({"id": "-".join([home_team, away_team]),
                            "status": status,
                            "homeTeam": {"name": home_team},
                            "awayTeam": {"name": away_team},
                            "score": {
                            "fullTime": {
                                "homeTeam": home_score.strip(),
                                "awayTeam": away_score.strip()}
                            },
                            "minute": minute})

        return matches
