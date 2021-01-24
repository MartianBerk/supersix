from datetime import datetime
from json import dump, load

from baked.lib.globals.setting import get_local
from baked.lib.supersix.service import RoundService


class CurrentRoundLoader:
    def __init__(self):
        try:
            # NOTE: this is specific to raspberry pi only via config.
            # TODO: not needed for real use (web apis functioning)
            root_dir = get_local()['root']
            config_path = f"{root_dir}/config/mb/supersix/currentround-loader.json"
            with open(config_path, "r") as fh:
                config = load(fh)

            if not config.get("dump_to"):
                raise EnvironmentError("missing dump_to in config")

            dump_to = config.get("dump_to")

        except FileNotFoundError:
            raise EnvironmentError("missing config file")

        self._dump_to = dump_to

        self._service = RoundService()

    def _dump_current_round(self):
        round = self._service.current_round()

        if not round:
            return None

        round = round.to_dict()
        round["start_date"] = round["start_date"].isoformat()
        round["current_match_date"] = round["current_match_date"].isoformat()

        print(f"dumping current round to {self._dump_to}")
        with open(self._dump_to, "w") as fh:
            dump({"current_round": round}, fh)

    def process(self):
        start = datetime.now()

        self._dump_current_round()

        delta = datetime.now() - start
        runtime = datetime.min + delta

        print(f"current round loaded in {runtime.strftime('%H:%M:%S')}")
