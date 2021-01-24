from datetime import datetime
from json import dump, load

from baked.lib.globals import get_local
from baked.lib.supersix.service import MetaService


class MetaLoader:
    def __init__(self):
        try:
            # NOTE: this is specific to raspberry pi only via config.
            # TODO: not needed for real use (web apis functioning)
            root_dir = get_local()['root']
            config_path = f"{root_dir}/config/supersix/meta-loader.json"
            with open(config_path, "r") as fh:
                config = load(fh)

            if not config.get("dump_to"):
                raise EnvironmentError("missing dump_to in config")

            dump_to = config.get("dump_to")

        except FileNotFoundError:
            raise EnvironmentError("missing config file")

        self._dump_to = dump_to

        self._service = MetaService()

    def _dump_meta(self):
        team_xref = self._service.team_xref()
        player_xref = self._service.player_xref()
        gameweeks = self._service.gameweeks()

        print(f"dumping meta to {self._dump_to}")
        with open(self._dump_to, "w") as fh:
            dump({"meta": {"teams": team_xref,
                           "players": player_xref,
                           "gameweeks": gameweeks}}, fh)

    def process(self):
        start = datetime.now()

        self._dump_meta()

        delta = datetime.now() - start
        runtime = datetime.min + delta

        print(f"meta loaded in {runtime.strftime('%H:%M:%S')}")
