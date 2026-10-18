import logging
import os
from datetime import datetime

from baked.lib.supersix.process.extractors.leagueextractor import LeagueExtractor


def init_logging():
    log_dir = "/tmp/supersix/logs"
    os.makedirs("/tmp/supersix/logs", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    log_file = f"{log_dir}/supersix-leagueextractor-{timestamp}.log"

    logger = logging.getLogger("supersix.leagueextractor")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


if __name__ == "__main__":
    # logger = init_logging()
    # logger.info("Starting LeagueExtractor")
    LeagueExtractor().process()