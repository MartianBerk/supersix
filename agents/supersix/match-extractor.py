from argparse import ArgumentParser

from baked.lib.supersix.process.extractors.matchextractor import MatchExtractor


if __name__ == "__main__":
    parser = ArgumentParser(description="Extract matches")
    parser.add_argument("-m", "--matchday", type=int, help="Matchday")
    parser.add_argument("-ma", "--matchdays_ahead", type=int, default=3, help="Matchdays ahead")
    parser.add_argument("-l", "--league", type=str, help="Extract for specific league")
    args = vars(parser.parse_args())

    MatchExtractor(**args).process()
