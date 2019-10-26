from argparse import ArgumentParser

from mylib.webapi import main, app


if __name__ == "__main__":
    parser = ArgumentParser(description="Start Supersix Web API")
    parser.add_argument("--host", type=str, help="Host IP")
    args = vars(parser.parse_args())

    app.run(**args)
