from datetime import datetime, timedelta
from time import sleep

from baked.lib.supersix.process.extractors.scoreextractor import ScoreExtractor
from baked.lib.supersix.service.matchservice import MatchService


class AutoScoreExtractor:
    """Score extractor to check the state of games and auto-initiate ScoreExtractor when required."""

    def __init__(self, max_run_seconds=0):
        """Initialize a new AutoScoreExtractor object."""
        self._max_run_seconds = max_run_seconds
        self._service = MatchService()

    def process(self):
        """Run main process."""
        start = datetime.now()

        # run until max_run_seconds expires
        while True:
            matches = self._service.scheduled_matches()

            if matches:
                match_date = matches[0].match_date  # all games should be the same, but even if not, so long as this agent runs regularly, all good.

                if match_date - start <= timedelta(minutes=1):
                    max_run = 7200  # 2 hours
                    ScoreExtractor(leagues=[m.league for m in matches], max_run_seconds=max_run).process()
                    break

            if datetime.now() > start + timedelta(seconds=self._max_run_seconds):
                break

            sleep(60)  # throttle
