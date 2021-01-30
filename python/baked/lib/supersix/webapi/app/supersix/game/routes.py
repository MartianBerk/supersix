from datetime import datetime, timedelta

from baked.lib.supersix.service import MatchService, PlayerService, PredictionService
from baked.lib.webapi import response

from .. import supersix


@supersix.route("/livematches", open_url=True, subdomains=["game"], methods=["GET"])
def live_matches():
    match_date = datetime.now().date()
    end_date = match_date + timedelta(days=1)

    filters = [("match_date", "greaterthanequalto", match_date),
               ("match_date", "lessthanequalto", end_date),
               ("use_match", "equalto", True)]

    matches = MatchService().list(filters=filters)
    matches.sort(key=lambda m: m.game_number)
    matches = [m.to_dict(keys=["id", "home_team", "away_team", "home_score", "away_score", "status", "match_minute", "match_date", "game_number"]) for m in matches]

    return response({"matches": matches})


@supersix.route("/livescores", open_url=True, subdomains=["game"], methods=["GET"])
def live_scores():
    match_date = datetime.now().date()
    end_date = match_date + timedelta(days=1)

    filters = [("match_date", "greaterthanequalto", match_date),
               ("match_date", "lessthanequalto", end_date),
               ("use_match", "equalto", True)]

    matches = MatchService().list(filters=filters)
    matches.sort(key=lambda m: m.game_number)

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

            correct = True if any([m.home_score and m.home_score > m.away_score and p.prediction == "home",
                                   m.away_score and m.away_score > m.home_score and p.prediction == "away",
                                   m.home_score and m.home_score == m.away_score and p.prediction == "draw"]) else False

            match = m.to_dict(keys=["home_team", "away_team"])
            match.update({"prediction": p.prediction, "correct": correct, "status": m.status})

            players[str(p.player_id)]["score"] += 1 if correct else 0
            players[str(p.player_id)]["matches"].append(match)

    players = [p for p in players.values()]
    players.sort(key=lambda x: x["score"], reverse=True)

    return response({"scores": players})
