from argparse import ArgumentParser

from mb.supersix.process.extractors.scoreextractor import ScoreExtractor


if __name__ == "__main__":
    parser = ArgumentParser(description="Extract scores")
    parser.add_argument("-l", "--league", type=str, help="League code")
    parser.add_argument("-m", "--matchday", type=int, help="Matchday")
    parser.add_argument("-s", "--max_run_seconds", type=int, help="Max runtime")
    args = vars(parser.parse_args())

    league = args.pop("league")

    ScoreExtractor(league, **args).process()
