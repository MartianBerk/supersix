from datetime import datetime

from baked.lib.supersix.model import Match
from baked.lib.supersix.service import LeagueService, MatchService

from .connectors.flashscoreconnectorv2 import FlashScoreConnectorV2


class MatchExtractor:

    def __init__(self, matchday=None, matchdays_ahead=3, league=None):
        self._league = league
        self._matchday = matchday
        self._matchdays_ahead = matchdays_ahead

        self._system = "supersix"
        self._component = "match-extractor"

        self._league_service = LeagueService()
        self._match_service = MatchService()
        self._connector = FlashScoreConnectorV2()

    def process(self):
        print(f"running match extractor for {self._matchdays_ahead} days ahead")

        # leagues
        for league in self._league_service.list():
            if self._league and league.code != self._league:
                continue

            print(f"extracting matches for {league.name}...")

            for match in self._connector.collect_matches(league, self._matchday, look_ahead=self._matchdays_ahead):
                # possible postponed match?
                if match.get("id"):
                    start_time = datetime.strptime(match["utcDate"], "%Y-%m-%d %H:%M:%S")

                    match = Match(external_id=str(match["id"]),
                                  league_id=league.id,
                                  matchday=match["matchday"],
                                  match_date=start_time,
                                  status=match["status"],
                                  home_team=match["homeTeam"]["name"],
                                  away_team=match["awayTeam"]["name"])

                    existing_match = self._match_service.get_from_external_id(match.external_id)
                    if existing_match:
                        print(f"[{match.matchday}] {match.home_team} vs {match.away_team}, already exists")
                        if existing_match.match_date != match.match_date:
                            print(f"[{match.matchday}] {match.home_team} vs {match.away_team}, match date changed")
                            existing_match.match_date = match.match_date
                            self._match_service.update(existing_match)

                        continue

                    self._match_service.create(match)
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

                    matches = self._match_service.list(filters=match_filters)
                    if matches:
                        if len(matches) > 1:
                            print(f"Found {len(matches)} matches with possible postponement for " +
                                  f"{match['homeTeam']['name']} vs {match['awayTeam']['name']} " +
                                  f"on matchday {match['matchday']}, cannot update automatically")

                        else:
                            existing_match = matches[0]
                            existing_match.status = match["status"]
                            print(f"[{existing_match.matchday}] {existing_match.home_team} vs {existing_match.away_team}, postponed")
                            self._match_service.update(existing_match)
                            continue

        print("extraction complete")
