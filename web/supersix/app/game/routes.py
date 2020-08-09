from datetime import datetime

from mb.supersix.service import MatchService, PlayerService, PredictionService
from mylib.webapi import route


@route("/livematches", methods=["GET"])
def live_matches():
    match_date = datetime.now().date()
    match_date = datetime.combine(match_date, datetime.min.time())

    matches = MatchService().list(filters={"match_date": match_date})
    matches = [m.to_dict(keys=["home_team", "away_team", "home_score", "away_score", "status", "match_minute"]) for m in matches]

    return {"matches": matches}


@route("/livescores", methods=["GET"])
def live_scores():
    match_date = datetime.now().date()
    match_date = datetime.combine(match_date, datetime.min.time())

    match_date = datetime(year=2020, month=7, day=11)  # TODO: remove after testing

    matches = MatchService().list(filters={"match_date": match_date})
    players = {str(p.id): {"name": f"{p.first_name} {p.last_name}",
                           "matches": [],
                           "score": 0} for p in PlayerService().list()}

    # get predictions for each player/match combination
    prediction_service = PredictionService()

    for m in matches:
        predictions = prediction_service.list({"match_id": m.id})

        for p in predictions:
            player = players.get(str(p.player_id))
            if not player:
                continue

            correct = True if any([m.home_score > m.away_score and p.prediction == "home",
                                   m.away_score > m.home_score and p.prediction == "away",
                                   m.home_score == m.away_score and p.prediction == "draw"]) else False

            match = m.to_dict(keys=["home_team", "away_team"])
            match.update({"prediction": p.prediction, "correct": correct})

            players[str(p.player_id)]["score"] += 1 if correct else 0
            players[str(p.player_id)]["matches"].append(match)

    players = [p for p in players.values()]
    players.sort(key=lambda x: x["score"], reverse=True)

    return {"scores": players}
