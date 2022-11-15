from datetime import datetime, timedelta

from baked.lib.admin.service.userservice import UserService
from baked.lib.supersix.model.prediction import Prediction
from baked.lib.supersix.service import MatchService, PlayerService, PredictionService, RoundService
from baked.lib.webapi import request, response

from .. import supersix


APPLICATION = "supersix"
PERMISSIONS = ["PLAYER"]


@supersix.route("/getprediction", subdomains=["user"], permissions=PERMISSIONS, methods=["GET"])
def get_prediction():
    game = request.args.get("gameId")
    if not game:
        return response({"error": True, "message": "Missing mandatory value for gameId."})

    # Can this even happen?
    uid = request.cookies.get("bkuid")
    if not uid:
        return response({"error": True, "message": "Not logged in."})

    user = UserService(APPLICATION).get_from_uid(int(uid))
    current_round = RoundService().current_round()
    prediction = PredictionService().prediction_exists(current_round.round_id, game, user.data.player_id)

    return response({"prediction": (prediction.prediction if prediction else None)})


@supersix.route("/addprediction", subdomains=["user"], permissions=PERMISSIONS, methods=["POST"])
def add_prediction():
    body = request.json

    # Can this even happen?
    uid = request.cookies.get("bkuid")
    if not uid:
        return response({"error": True, "message": "Not logged in."})

    try:
        game = body["game_id"]
        new_prediction = body["prediction"]

    except KeyError as e:
        return response({"error": True, "message": "Missing mandatory value {str(e)}."})

    prediction_service = PredictionService()

    current_round = RoundService().current_round()
    if not current_round:
        return response({"error": True, "message": "Something went wrong, please try again later."})

    match = MatchService().get(game)
    if not match:
        return response({"error": True, "message": "Game not found."})

    cutoff = datetime.utcnow() + timedelta(hours=1)
    if cutoff >= match.match_date:
        return response({"error": True, "message": "Past cutoff for prediction set."})

    user = UserService(APPLICATION).get_from_uid(int(uid))

    # ensure predicition has changed
    prediction = prediction_service.prediction_exists(current_round.round_id, game, user.data.player_id)

    if prediction:
        if prediction.prediction != new_prediction:
            prediction = Prediction(
                id=prediction.id,
                round_id=prediction.round_id,
                player_id=prediction.player_id,
                match_id=prediction.match_id,
                prediction=new_prediction
            )

            prediction_service.update(prediction)
    
    else:
        new_id = prediction_service.list()
        new_id = new_id[-1].id + 1 if new_id else 1  # TODO: handle autoincrement better

        prediction = Prediction(
            id=new_id,
            round_id=current_round.round_id,
            player_id=user.data.player_id,
            match_id=match.id,
            prediction=new_prediction
        )

        prediction = prediction_service.create(prediction)

    return response(prediction.to_dict())


@supersix.route("/updatedetails", subdomains=["user"], permissions=PERMISSIONS, methods=["POST"])
def update_details():
    body = request.json

    # Can this even happen?
    uid = request.cookies.get("bkuid")
    if not uid:
        return response({"error": True, "message": "Not logged in."})

    user_service = UserService(APPLICATION)
    user = user_service.get_from_uid(int(uid))

    fields = ["email"]
    update = {}
    for field in fields:
        value = body.get(field)
        if value:
            update[field] = value

    if update:
        user.update(update)
        user_service.update(user)

    rtn_user = user.to_dict(public_only=True)

    nickname = body.get("nickname")
    if nickname:
        # nickname not handled in user but in player xref in meta
        PlayerService().update_player_nickname(user.data.player_id, nickname)
        rtn_user["nickname"] = nickname

    return response(rtn_user)
