from datetime import datetime, timedelta

from baked.lib.admin.service.userservice import UserService
from baked.lib.supersix.model.worldcupprediction import WorldCupPrediction
from baked.lib.supersix.service import MatchService, PlayerService, PredictionService
from baked.lib.supersix.service.worldcupservice import WorldCupService
from baked.lib.webapi import request, response

from .. import supersix


APPLICATION = "supersix"


@supersix.route("/matches", open_url=True, subdomains=["worldcup"], methods=["GET"])
def worldcup_matches():
    matches = WorldCupService().list_matches()
    matches.sort(key=lambda m: m.match_date)
    
    return_matches = []
    for match in matches:
        match_date = match.match_date.strftime("%Y-%m-%dT%H:%M:%SZ")
        match = match.to_dict()
        (match.pop(k) for k in match.keys() if k not in ["id", "home_team", "away_team", "home_score", "away_score", "status", "match_minute", "extra_time", "penalties"])
        return_matches.append({**match, "match_date": match_date})

    return response({"matches": return_matches})


@supersix.route("/scores", open_url=True, subdomains=["worldcup"], methods=["GET"])
def worldcup_scores():
    scores = WorldCupService().list_scores()
    return response({"scores": [s.to_dict() for s in scores]})


@supersix.route("/getprediction", permissions=["QATARHERO"], subdomains=["worldcup"], methods=["GET"])
def worldcup_get_prediction():
    game = request.args.get("gameId")
    if not game:
        return response({"error": True, "message": "Missing mandatory value for gameId."})

    # Can this even happen?
    uid = request.cookies.get("bkuid")
    if not uid:
        return response({"error": True, "message": "Not logged in."})

    user = UserService(APPLICATION).get_from_uid(int(uid))
    prediction = PredictionService().prediction_exists(game, user.data.qatar_hero_player_id)

    return response({"prediction": (prediction.prediction if prediction else None)})


@supersix.route("/addprediction", permissions=["QATARHERO"], subdomains=["worldcup"], methods=["GET"])
def worldcup_add_prediction():
    body = request.json

    # Can this even happen?
    uid = request.cookies.get("bkuid")
    if not uid:
        return response({"error": True, "message": "Not logged in."})

    try:
        match = body["game_id"]
        new_prediction = body["prediction"]
        new_extra_time = body["extra_time"]
        new_penalties = body["penalties"]

        if new_prediction.lower() == "draw" and (new_extra_time or new_penalties):
            return response({"error": True, "message": "Cannot combine draw with extra time or penalties."})

    except KeyError as e:
        return response({"error": True, "message": f"Missing mandatory value {str(e)}."})

    service = WorldCupService()

    match = service.get_match(match)
    if not match:
        return response({"error": True, "message": "Match not found."})

    cutoff = datetime.utcnow() + timedelta(hours=1)
    if cutoff >= match.match_date:
        return response({"error": True, "message": "Past cutoff for prediction set."})

    user = UserService(APPLICATION).get_from_uid(int(uid))

    # ensure predicition has changed
    prediction = service.prediction_exists(match, user.data.qatar_hero_player_id)

    if prediction:
        if prediction.prediction != new_prediction:
            prediction = WorldCupPrediction(
                id=prediction.id,
                player_id=prediction.player_id,
                match_id=prediction.match_id,
                prediction=new_prediction,
                extra_time=new_extra_time,
                penalties=new_penalties
            )

            service.update_prediction(prediction)
    
    else:
        new_id = service.list_predictions()
        new_id = new_id[-1].id + 1 if new_id else 0  # TODO: handle autoincrement better

        prediction = WorldCupPrediction(
            id=new_id,
            player_id=user.data.player_id,
            match_id=match.id,
            prediction=new_prediction,
            extra_time=new_extra_time,
            penalties=new_penalties
        )

        prediction = service.create_prediction(prediction)

    return response(prediction.to_dict())


# @supersix.route("/scores", open_url=True, subdomains=["worldcup"], methods=["GET"])
# def game_live_scores():
#     match_date = request.args.get("matchDate")
#     if not match_date:
#         return response({"error": True, "message": "missing matchDate"})

#     try:
#         start_date = datetime.strptime(match_date, "%d-%m-%Y")
#         end_date = start_date + timedelta(days=1)
#     except ValueError:
#         return {"error": True, "message": "invalid date format, expected dd-mm-yyyy"}

#     filters = [("match_date", "greaterthanequalto", start_date),
#                ("match_date", "lessthanequalto", end_date),
#                ("use_match", "equalto", True)]

#     matches = MatchService().list(filters=filters)
#     matches.sort(key=lambda m: m.game_number)

#     players = {p.id: {"id": p.id,
#                       "name": f"{p.first_name} {p.last_name}",
#                       "matches": [],
#                       "score": 0} for p in PlayerService().list()}

#     # get predictions for each player/match combination
#     prediction_service = PredictionService()

#     for m in matches:
#         prediction_filters = [("match_id", "equalto", m.id), ("drop", "equalto", False)]
#         predictions = prediction_service.list(prediction_filters)

#         for p in predictions:
#             player = players.get(p.player_id)
#             if not player:
#                 continue

#             correct = True if any([
#                 m.home_score is not None and m.home_score > m.away_score and p.prediction == "home",
#                 m.away_score is not None and m.away_score > m.home_score and p.prediction == "away",
#                 m.home_score is not None and m.home_score == m.away_score and p.prediction == "draw"
#             ]) else False

#             match = m.to_dict()
#             (match.pop(k) for k in match.keys() if k not in ["home_team", "away_team"])
#             match.update({"prediction": p.prediction, "correct": correct, "status": m.status})

#             players[p.player_id]["score"] += 1 if correct else 0
#             players[p.player_id]["matches"].append(match)

#     players = [p for p in players.values()]
#     players.sort(key=lambda x: x["score"], reverse=True)

#     return response({"scores": players})
