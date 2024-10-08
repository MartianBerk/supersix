from argparse import ArgumentParser

from baked.lib.supersix.process.extractors.scoreextractor import ScoreExtractor


if __name__ == "__main__":
    parser = ArgumentParser(description="Extract scores")
    parser.add_argument("-l", "--leagues", type=str, nargs="*", help="League code")
    parser.add_argument("-m", "--matchday", type=int, help="Matchday")
    parser.add_argument("-em", "--end_matchday", type=int, help="End Matchday")
    parser.add_argument("-s", "--max_run_seconds", type=int, default=300, help="Max runtime")
    args = vars(parser.parse_args())

    leagues = args.pop("leagues")

    ScoreExtractor(leagues, **args).process()
