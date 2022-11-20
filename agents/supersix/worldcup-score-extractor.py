from argparse import ArgumentParser

from baked.lib.supersix.process.extractors.worldcupextractor import WorldCupExtractor


if __name__ == "__main__":
    parser = ArgumentParser(description="Extract World Cup Scores")
    parser.add_argument("-r", "--round", type=int, help="Round")
    parser.add_argument("-er", "--end_round", type=int, help="End Round")
    parser.add_argument("-s", "--max_run_seconds", type=int, default=0, help="Max runtime")
    args = vars(parser.parse_args())

    WorldCupExtractor("scores", **args).process()
