from mylib.globals import get_global
from mylib.myodbc.public import MyOdbc

from mb.supersix.model import TeamXref

from .servicemixin import ServiceMixin


class MetaService(ServiceMixin):
    _db = "supersix"

    def __init__(self):
        db_settings = get_global("dbs", self._db)

        self._driver = db_settings.get("driver")
        self._db = MyOdbc.connect(self._driver,
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
