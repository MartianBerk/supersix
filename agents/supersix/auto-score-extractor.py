from argparse import ArgumentParser

from baked.lib.supersix.process.extractors.autoscoreextractor import AutoScoreExtractor


if __name__ == "__main__":
    parser = ArgumentParser(description="Extract scores by checking for inbound kick offs and triggering the score extractor.")
    parser.add_argument("-s", "--max_run_seconds", type=int, default=300, help="Max runtime")
    args = vars(parser.parse_args())

    AutoScoreExtractor(**args).process()
