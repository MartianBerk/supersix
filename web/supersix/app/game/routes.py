from datetime import datetime

from mb.supersix.service import MatchService, PlayerService, PredictionService
from mylib.webapi import route


@route("livematches", methods=["GET"])
def live_matches():
    match_date = datetime.now().date()
    match_date = datetime.combine(match_date, datetime.min.time())

    matches = MatchService().list(filters={"match_date": match_date})
    return {"matches": [m.to_dict(keys=["home_team", "away_team", "home_score", "away_score"]) for m in matches]}


@route("livescores", methods=["GET"])
def live_scores():
    match_date = datetime.now().date()
    match_date = datetime.combine(match_date, datetime.min.time())

    match_date = datetime(year=2020, month=7, day=18)  # TODO: remove after testing

    matches = MatchService().list(filters={"match_date": match_date})
    players = {p.id: f"{p.first_name} {p.last_name}" for p in PlayerService().list()}

    # get predictions for each player/match combination
    prediction_service = PredictionService()

    data = {"scores": {p.id: {"name": f"{p.first_name} {p.last_name}"} for p in players}}

    for m in matches:
        predictions = prediction_service.list({"match_id": m.id})

        for p in predictions:
            player = players.get(p.player_id)
            if not player:
                continue

            data["scores"][player.id][m.id] = m.to_dict(keys=["home_team", "away_team"])
            data["scores"][player.id][m.id].update({
                "prediction": p.prediction,
                "correct": True if any([m.home_score > m.away_score and p.prediction == "home",
                                        m.away_score > m.home_score and p.prediction == "away",
                                        m.home_score == m.away_score and p.prediction == "draw"]) else False
            })

    return data
