from argparse import ArgumentParser

from baked.lib.supersix.process.extractors.worldcupextractor import WorldCupExtractor


if __name__ == "__main__":
    parser = ArgumentParser(description="Extract World Cup Matches")
    parser.add_argument("-r", "--round", type=int, help="Round")
    parser.add_argument("-er", "--end_round", type=int, help="End Round")
    args = vars(parser.parse_args())

    WorldCupExtractor("matches", max_run_seconds=0, **args).process()
