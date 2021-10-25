from datetime import datetime, timedelta
from pathlib import Path
from time import sleep

from baked.lib.globals import get_global
from baked.lib.supersix.process.extractors.scoreextractor import ScoreExtractor
from baked.lib.supersix.service.matchservice import MatchService


class AutoScoreExtractor:
    """Score extractor to check the state of games and auto-initiate ScoreExtractor when required."""

    def __init__(self, max_run_seconds=0):
        """Initialize a new AutoScoreExtractor object."""
        self._max_run_seconds = max_run_seconds
        self._service = MatchService()

    def _get_lock_file(self):
        db_settings = get_global("dbs", "supersix")
        db_share_location = db_settings.get("location")

        lock_file = ".supersix-auto-extractor.lock"

        return Path(db_share_location, lock_file)

    def lock(self) -> None:
        lock_file = self._get_lock_file()
        lock_file.touch(exists_ok=True)

    def unlock(self) -> None:
        lock_file = self._get_lock_file()
        lock_file.unlink(missing_ok=True)

    def is_locked(self) -> bool:
        lock_file = self._get_lock_file()
        return lock_file.exists()

    def process(self) -> None:
        """Run main process."""
        start = datetime.now()

        if self.is_locked():
            return None

        # run until max_run_seconds expires
        while True:
            now = datetime.now()
            matches = self._service.scheduled_matches()

            if matches:
                match_date = matches[0].match_date  # all games should be the same, but even if not, so long as this agent runs regularly, all good.

                if match_date - now <= timedelta(minutes=1):
                    self.lock()

                    max_run = 7200  # 2 hours
                    leagues = list(set([m.league for m in matches]))

                    ScoreExtractor(leagues=leagues, max_run_seconds=max_run).process()

                    self.unlock()
                    break

            if datetime.now() > start + timedelta(seconds=self._max_run_seconds):
                break

            sleep(60)  # throttle

        return None
