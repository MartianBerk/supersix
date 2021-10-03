from baked.lib.supersix.process.extractors.scoreextractor import ScoreExtractor
from baked.lib.supersix.service.leagueservice import LeagueService


class FinalScoreExtractor:
    """Score extractor designed to run at the end of a gameweek, to get all scores."""

    LOCKED = False

    def __init__(self, league: str):
        """Initialize a new FinalScoreExtractor object."""
        self.league = league

        self._league_service = LeagueService()

    def process(self) -> None:
        """Run main process."""
        league = self._league_service.get_from_league_code(self.league)

        ScoreExtractor(leagues=[league], matchday=league.current_matchday, max_run_seconds=0).process()

        return None
