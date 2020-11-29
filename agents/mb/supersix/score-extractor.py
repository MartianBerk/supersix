from argparse import ArgumentParser

from mb.supersix.process.extractors.scoreextractor import ScoreExtractor


if __name__ == "__main__":
    parser = ArgumentParser(description="Extract scores")
    parser.add_argument("-l", "--leagues", type=str, nargs="*", help="League code")
    parser.add_argument("-m", "--matchday", type=int, help="Matchday")
    parser.add_argument("-s", "--max_run_seconds", type=int, default=300, help="Max runtime")
    parser.add_argument("-dm", "--dump_matches", action="store_true", help="Dump match score extracts")
    parser.add_argument("-ds", "--dump_scores", action="store_true", help="Dump player score extracts")
    parser.add_argument("-dd", "--dump_date", type=str, help="Dump matches/scores for given date")
    args = vars(parser.parse_args())

    leagues = args.pop("leagues")

    ScoreExtractor(leagues, **args).process()
