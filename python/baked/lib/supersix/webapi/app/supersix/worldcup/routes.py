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


#
# These next three functions are all the same, but due to unexplainable caching behaviour on some browsers,
# /worldcup/listpredictions and qatarhero/listpredictions have been added to try and circumvent /getpredictions,
# which used to be a locked URL. Assumption is caching is based on URL, but just incase sub-path is used somehow.
#
@supersix.route("/listpredictions", open_url=True, subdomains=["worldcup"], methods=["GET"])
def worldcup_list_predictions():
    filters = [
        ("drop", "equalto", False)
    ]
    predictions = WorldCupService().list_predictions(filters=filters)
    return response({"predictions": [p.to_dict() for p in predictions]})


@supersix.route("/listpredictions", open_url=True, subdomains=["qatarhero"], methods=["GET"])
def qatarhero_list_predictions():
    filters = [
        ("drop", "equalto", False)
    ]
    predictions = WorldCupService().list_predictions(filters=filters)
    return response({"predictions": [p.to_dict() for p in predictions]})


@supersix.route("/getpredictions", open_url=True, subdomains=["worldcup"], methods=["GET"])
def worldcup_get_predictions():
    filters = [
        ("drop", "equalto", False)
    ]
    predictions = WorldCupService().list_predictions(filters=filters)
    return response({"predictions": [p.to_dict() for p in predictions]})


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
    prediction = WorldCupService().prediction_exists(game, user.data.qatar_hero_player_id)

    return response({"prediction": (prediction.prediction if prediction else None)})


@supersix.route("/addprediction", permissions=["QATARHERO"], subdomains=["worldcup"], methods=["POST"])
def worldcup_add_prediction():
    body = request.json

    # Can this even happen?
    uid = request.cookies.get("bkuid")
    if not uid:
        return response({"error": True, "message": "Not logged in."})

    try:
        match_id = body["game_id"]
        new_prediction = body["prediction"]
        new_extra_time = body.get("extra_time")
        new_penalties = body.get("penalties")

        if new_prediction.lower() == "draw" and (new_extra_time or new_penalties):
            return response({"error": True, "message": "Cannot combine draw with extra time or penalties."})

    except KeyError as e:
        return response({"error": True, "message": f"Missing mandatory value {str(e)}."})

    service = WorldCupService()

    match = service.get_match(match_id)
    if not match:
        return response({"error": True, "message": "Match not found."})

    cutoff = datetime.utcnow() + timedelta(minutes=10)
    if cutoff >= match.match_date:
        return response({"error": True, "message": "Past cutoff for prediction set."})

    user = UserService(APPLICATION).get_from_uid(int(uid))

    if user.data.qatar_hero_player_id != 1 and match_id > 48:
        return response({"error": True, "message": "Knockout stages are locked."})

    # ensure predicition has changed
    prediction = service.prediction_exists(match_id, user.data.qatar_hero_player_id)

    if prediction:
        if prediction.prediction != new_prediction or prediction.extra_time != new_extra_time or prediction.penalties != new_penalties:
            prediction = WorldCupPrediction(
                id=prediction.id,
                player_id=prediction.player_id,
                match_id=prediction.match_id,
                prediction=new_prediction,
                plus_ninety=new_extra_time or new_penalties,
                extra_time=new_extra_time,
                penalties=new_penalties
            )

            service.update_prediction(prediction)
    
    else:
        new_id = service.list_predictions()
        new_id = new_id[-1].id + 1 if new_id else 1  # TODO: handle autoincrement better

        prediction = WorldCupPrediction(
            id=new_id,
            player_id=user.data.qatar_hero_player_id,
            match_id=match.id,
            prediction=new_prediction,
            plus_ninety=new_extra_time or new_penalties,
            extra_time=new_extra_time,
            penalties=new_penalties
        )

        prediction = service.create_prediction(prediction)

    return response(prediction.to_dict())
