from argparse import ArgumentParser

from baked.lib.supersix.webapi import SupersixApi


if __name__ == "__main__":
    parser = ArgumentParser(description="Supersix Web API.")
    parser.add_argument("--host", type=str, required=False, help="Host")
    parser.add_argument("--port", type=str, required=False, help="Port")
    args = parser.parse_args()

    SupersixApi.run(standalone=True, host=args.host, port=args.port)
