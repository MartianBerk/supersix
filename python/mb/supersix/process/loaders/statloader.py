from datetime import datetime
from json import dump, load

from mb.supersix.service import StatService
from mylib.globals.setting import get_local


class StatLoader:
    def __init__(self, dump_aggregate=False):
        if dump_aggregate:
            try:
                # NOTE: this is specific to raspberry pi only via config.
                # TODO: not needed for real use (web apis functioning)
                root_dir = get_local()['root']
                config_path = f"{root_dir}/config/mb/supersix/stat-loader.json"
                with open(config_path, "r") as fh:
                    config = load(fh)

                if dump_aggregate and not config.get("dump_aggregate_to"):
                    raise EnvironmentError("missing dump_aggregate_to in config")

                dump_aggregate = config.get("dump_aggregate_to") if dump_aggregate else None

            except FileNotFoundError:
                raise EnvironmentError("missing config file")

        self._dump_aggregate = dump_aggregate

        self._service = StatService()

    def _dump_aggregate_stats(self):
        if not self._dump_aggregate:
            return

        stats = self._service.aggregate_stats()

        aggregate = {}
        for s in stats:
            if s.player not in aggregate:
                aggregate[s.player] = []

            aggregate[s.player].append({"date": s.match_date.isoformat(),
                                        "score": s.correct,
                                        "matches": s.matches})

        print(f"dumping aggregate stats to {self._dump_aggregate}")
        with open(self._dump_aggregate, "w") as fh:
            dump({"stats": [{"name": k, "scores": v} for k, v in aggregate.items()]}, fh)

    def process(self):
        start = datetime.now()

        self._dump_aggregate_stats()

        delta = datetime.now() - start
        runtime = datetime.min + delta

        print(f"stats loaded in {runtime.strftime('%H:%M:%S')}")
