from datetime import datetime, timedelta
from time import sleep

from baked.lib.supersix.model import League
from baked.lib.supersix.model.worldcupmatch import WorldCupMatch
from baked.lib.supersix.service import LeagueService
from baked.lib.supersix.service.worldcupservice import WorldCupService

from .connectors.worldcupconnector import WorldCupConnector
from .connectors.footballapiconnector import FootballApiConnector


class WorldCupExtractor:

    _MODES = ["league", "matches", "scores"]
    _LEAGUE_CODE = "WC"

    def __init__(self, mode=None, round=None, end_round=None, max_run_seconds=0):
        if mode not in self._MODES:
            raise ValueError(f"Invalid mode, expecting one of: {', '.join(self._MODES)}")

        self._mode = mode
        self._round = round
        self._end_round = end_round
        self._max_run_seconds = max_run_seconds

    def _process_league(self):
        league_service = LeagueService()
        league = FootballApiConnector.collect_world_cup()
        if league and league.get("code"):  # safety net
            league = League(name=league["name"],
                            code=league["code"],
                            start_date=datetime.strptime(league["currentSeason"]["startDate"], "%Y-%m-%d"),
                            current_matchday=league["currentSeason"]["currentMatchday"])  # TODO: we need to find out how the API handles the final rounds??

            if not league.start_date or not league.code:
                print(f"skipping {league.name}, missing code/current season")
                return None

            existing_league = league_service.get_from_league_code(league.code)
            if existing_league:
                existing_league.current_matchday = league.current_matchday
                existing_league.start_date = league.start_date
                league_service.update(existing_league)
                print(f"{league.name} updated")
            else:
                league_service.create(league)
                print(f"{league.name} extracted")

    def _process_matches(self):
        print(f"running match extractor for round {self._round}")
        print(f"extracting matches for World Cup...")

        league_service = LeagueService()

        for league in league_service.list():
            if league.code != self._LEAGUE_CODE:
                continue

            match_service = WorldCupService()
            connector = WorldCupConnector()

            for match in connector.collect_matches(league, self._round or league.current_matchday, look_ahead=self._end_round or league.current_matchday):
                # possible postponed match?
                if match.get("id"):
                    start_time = datetime.strptime(match["utcDate"], "%Y-%m-%d %H:%M:%S")

                    match = WorldCupMatch(external_id=str(match["id"]),
                                          league_id=league.id,
                                          matchday=match["matchday"],
                                          match_date=start_time,
                                          status=match["status"],
                                          home_team=match["homeTeam"]["name"],
                                          away_team=match["awayTeam"]["name"])

                    existing_match = match_service.get_match_from_external_id(match.external_id)
                    if existing_match:
                        print(f"[{match.matchday}] {match.home_team} vs {match.away_team}, already exists")
                        if existing_match.match_date != match.match_date:
                            print(f"[{match.matchday}] {match.home_team} vs {match.away_team}, match date changed")
                            existing_match.match_date = match.match_date
                            match_service.update_match(existing_match)

                        continue

                    match_service.create_match(match)
                    print(f"[{match.matchday}] {match.home_team} vs {match.away_team} extracted")

                else:
                    # each home/away team combo should happen one time each year, so this should work
                    match_filters = [
                        ("home_team", "equalto", match["homeTeam"]["name"]),
                        ("away_team", "equalto", match["awayTeam"]["name"]),
                        ("matchday", "equalto", match["matchday"]),
                        ("league_id", "equalto", league.id),
                        ("match_date", "greaterthanequalto", league.start_date)
                    ]

                    matches = match_service.list_matches(filters=match_filters)
                    if matches:
                        if len(matches) > 1:
                            print(f"Found {len(matches)} matches with possible postponement for " +
                                    f"{match['homeTeam']['name']} vs {match['awayTeam']['name']} " +
                                    f"on matchday {match['matchday']}, cannot update automatically")

                        else:
                            existing_match = matches[0]
                            existing_match.status = match["status"]
                            print(f"[{existing_match.matchday}] {existing_match.home_team} vs {existing_match.away_team}, postponed")
                            match_service.update_match(existing_match)
                            continue

        print("extraction complete")

    def _update_match(self, league, match_data, match_service):
        match = match_service.get_match_from_external_id(match_data["id"])
        if not match:
            start_time = match_data.get("utcDate")
            if start_time:
                start_time = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")

            match = WorldCupMatch(external_id=str(match_data["id"]),
                                    league_id=league.id,
                                    matchday=match_data["matchday"],
                                    match_date=start_time,
                                    status=match_data["status"],
                                    home_team=match_data["homeTeam"]["name"],
                                    away_team=match_data["awayTeam"]["name"],
                                    extra_time=match_data["extra_time"],
                                    penalties=match_data["penalties"])

            match = match_service.create_match(match)
        else:
            match.status = match_data["status"]

            match_minute = match_data.get("minute")
            if match_minute:
                match.match_minute = match_minute

            match.home_score = match_data["score"]["fullTime"]["homeTeam"]
            match.away_score = match_data["score"]["fullTime"]["awayTeam"]
            match.extra_time = match_data["extra_time"]
            match.penalties = match_data["penalties"]

            match = match_service.update_match(match)

        return match

    def _process_scores(self):
        start = datetime.now()
        league_service = LeagueService()
        leagues = league_service.list()

        if self._round:
            for league in leagues:
                if league.code != self._LEAGUE_CODE:
                    continue

                match_service = WorldCupService()
                connector = WorldCupConnector()

                print(f"extracting {league.name} scores for matchday {self._round} - {self._end_round or self._round}")

                try:
                    matches = connector.collect_historical_scores(league, self._round, self._end_round or self._round)
                except ConnectionError:
                    pass
                else:
                    for match_data in matches:
                        match = self._update_match(league, match_data, match_service)
                        if match:
                            print(f"updated {match.home_team} ({match.home_score}) vs {match.away_team} ({match.away_score}) ({'ET' if match.extra_time else ('P' if match.penalties else '')})")

            return None

        while True:
            for league in leagues:
                if league.code != self._LEAGUE_CODE:
                    continue

                match_service = WorldCupService()
                connector = WorldCupConnector()

                print(f"extracting {league.name} scores for matchday {league.current_matchday}")

                try:
                    scores = connector.collect_scores(league, league.current_matchday, live=True)
                    
                    for match_data in scores:
                        match = self._update_match(league, match_data, match_service)
                        print(f"updated {match.home_team} ({match.home_score}) vs {match.away_team} ({match.away_score})")

                except Exception as e:
                    print(f"extraction issue with {league.name}: {str(e)}. Skipping...")

            if datetime.now() > start + timedelta(seconds=self._max_run_seconds):
                break

            sleep(10)  # throttle

    def process(self):
        getattr(self, f"_process_{self._mode}")()
