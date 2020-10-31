from argparse import ArgumentParser

from mb.supersix.process.extractors.multileaguescoreextractor import MultiLeagueScoreExtractor


if __name__ == "__main__":
    parser = ArgumentParser(description="Extract scores")
    parser.add_argument("-l", "--leagues", type=str, nargs="*", help="League code")
    parser.add_argument("-m", "--matchday", type=int, help="Matchday")
    parser.add_argument("-s", "--max_run_seconds", type=int, default=300, help="Max runtime")
    parser.add_argument("-d", "--dump", type=str, help="Dump score extracts to")
    args = vars(parser.parse_args())

    leagues = args.pop("leagues")

    MultiLeagueScoreExtractor(leagues, **args).process()
