from datetime import datetime

from mylib.supersix.service import MatchService
from mylib.webapi import app, route


@route("/matches")
def index():
    now = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    matches = MatchService().list(columns=["home_team", "away_team", "home_score", "away_score"],
                                  filters={"match_date": now})
    return {"matches": [m.to_dict() for m in matches]}
