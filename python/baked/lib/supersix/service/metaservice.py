from baked.lib.admin.service.userservice import UserService
from baked.lib.dbaccess.public import DbAccess
from baked.lib.globals import get_global
from baked.lib.supersix.model import GameWeek, PlayerXref, TeamXref

from .servicemixin import ServiceMixin


class MetaService(ServiceMixin):
    _db = "supersix"

    def __init__(self):
        db_settings = get_global("dbs", self._db)

        self._driver = db_settings.get("driver")
        self._db = DbAccess.connect(self._driver,
                                    self._db,
                                    db_settings.get("location"))

    def team_xref(self):
        table = "TEAM_XREF"

        columns = {c: None for c in self._db.get_columns(table)}
        column_model = self._generate_column_model(self._driver, TeamXref, columns)

        xref = {}
        for x in self._db.get(table, column_model):
            x = TeamXref(**x)
            xref[x.team_name] = x.xref

        return xref

    def player_xref(self):
        users = UserService("supersix").list()

        xref = {}
        for u in users:
            if u.nickname:
                xref[f"{u.firstname} {u.lastname}"] = u.nickname

        return xref

    def gameweeks(self):
        table = "GAMEWEEKS"

        columns = {c: None for c in self._db.get_columns(table)}
        column_model = self._generate_column_model(self._driver, GameWeek, columns)

        return [GameWeek(**gw).match_date.strftime("%Y-%m-%dT%H:%M:%SZ") for gw in self._db.get(table, column_model)]
