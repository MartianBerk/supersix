from argparse import ArgumentParser

from baked.lib.supersix.process.loaders.statloader import StatLoader


if __name__ == "__main__":
    parser = ArgumentParser(description="Loads stats")
    parser.add_argument("-da", "--dump_aggregate", action="store_true", help="Dump aggregate stats")
    args = vars(parser.parse_args())

    StatLoader(**args).process()
