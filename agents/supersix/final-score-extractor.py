from argparse import ArgumentParser

from baked.lib.supersix.process.extractors.finalscoreextractor import FinalScoreExtractor


if __name__ == "__main__":
    parser = ArgumentParser(description="Extract the final scores for a given league.")
    parser.add_argument("-l", "--league", type=str, required=True, help="League")
    args = parser.parse_args()

    FinalScoreExtractor(args.league).process()
