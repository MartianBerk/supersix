from datetime import datetime

from mylib.supersix.service import MatchService
from mylib.webapi import app, route


@route("/matches")
def index():
    matches = MatchService().list(columns=["home_team", "away_team", "home_score", "away_score"],
                                  filters={"match_date": datetime.now().date()})
    return {"matches": [m.to_dict() for m in matches]}
