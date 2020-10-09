from datetime import datetime, timedelta

from mb.supersix.model import Player, Prediction, Round
from mb.supersix.service import MatchService, PlayerService, PredictionService, RoundService
from mylib.webapi.webapi import route, request


@route("/listplayers", open_url=True, methods=["GET"])
def list_players():
    players = PlayerService().list()
    return {"players": [p.to_dict() for p in players]}


@route("/listrounds", open_url=True, methods=["GET"])
def list_rounds():
    rounds = RoundService().list()
    return {"rounds": [r.to_dict() for r in rounds]}


@route("/listpredictions", open_url=True, methods=["GET"])
def list_predictions():
    predictions = PredictionService().list()
    return {"predictions": [p.to_dict() for p in predictions]}


@route("/addplayer", open_url=True, methods=["POST"])
def add_player():
    body = request.json

    service = PlayerService()

    players = service.list()
    new_id = len(players) + 1

    try:
        player = Player(id=new_id,
                        first_name=body["first_name"],
                        last_name=body["last_name"],
                        join_date=datetime.now())
    except KeyError as e:
        return {"error": True, "message": f"payload missing {str(e)}"}

    player = service.create(player)
    return player.to_dict()


@route("/addround", open_url=True, methods=["POST"])
def add_round():
    body = request.json

    service = RoundService()

    rounds = service.list()
    new_id = len(rounds) + 1

    try:
        start_date = body["start_date"]
        start_date = datetime.strptime(start_date, "%d-%m-%Y")

        end_date = body.get("end_date")
        if end_date:
            datetime.strptime(end_date, "%d-%m-%Y")

        round = Round(id=new_id,
                      start_date=start_date,
                      end_date=end_date,
                      buy_in_pence=body["buy_in"])
    except KeyError as e:
        return {"error": True, "message": f"payload missing {str(e)}"}
    except ValueError:
        return {"error": True, "message": "invalid date format, expected dd-mm-yyyy"}

    round = service.create(round)
    return round.to_dict()


@route("/getround", open_url=True, methods=["GET"])
def get_round():
    round = request.args.get("round")
    service = RoundService()

    if round:
        round = service.get(round)
        if not round:
            return {"error": True, "message": "round doesn't exist"}

        return round.to_dict()

    # get current round
    rounds = round.list([("end_date", "null", None)])
    if not rounds:
        return {"error": True, "message": "no round current in play"}
    elif len(rounds) > 1:
        return {"error": True, "message": "more than one current round found"}

    return rounds[0].to_dict()


@route("/listmatches", open_url=True, methods=["GET"])
def list_matches():
    match_date = request.args.get("matchDate")
    if not match_date:
        return {"error": True, "message": "missing matchDate"}

    service = MatchService()

    try:
        start_date = datetime.strptime(match_date, "%d-%m-%Y")
        end_date = start_date + timedelta(days=1)
    except ValueError:
        return {"error": True, "message": "invalid date format, expected dd-mm-yyyy"}

    filters = [("match_date", "greaterthanequalto", start_date), ("match_date", "lessthanequalto", end_date)]
    return {"matches": [m.to_dict() for m in service.list(filters)]}


@route("/addmatch", open_url=True, methods=["GET"])
def add_match():
    match_id = request.args.get("id")
    if not match_id:
        return {"error": True, "message": "missing id"}

    service = MatchService()

    match = service.get(match_id)
    if not match:
        return {"error": True, "message": "id not found"}

    match.use_match = True
    match = service.update(match)

    return match.to_dict()


@route("/addmatches", open_url=True, methods=["POST"])
def add_matches():
    body = request.json

    match_ids = body.get("ids")
    if not match_ids:
        return {"error": True, "message": "missing ids from payload"}

    service = MatchService()
    matches = []

    for mid in match_ids:
        match = service.get(mid)
        match.use_match = True

        matches.append(service.update(match))

    return {"matches": [m.to_dict() for m in matches]}


@route("/dropmatch", open_url=True, methods=["GET"])
def drop_match():
    match_id = request.args.get("id")
    if not match_id:
        return {"error": True, "message": "missing id"}

    service = MatchService()

    match = service.get(match_id)
    if not match:
        return {"error": True, "message": "id not found"}

    match.use_match = False
    match = service.update(match)

    return match.to_dict()


@route("/addpredictions", open_url=True, methods=["POST"])
def add_predictions():
    body = request.json

    match_service = MatchService()
    player_service = PlayerService()
    prediction_service = PredictionService()
    round_service = RoundService()

    predictions = []

    try:
        for b in body:
            match = match_service.get(b["match_id"])
            player = player_service.get(b["player_id"])
            round = round_service.get(b["round_id"])

            if not match:
                return {"error": True, "message": f"invalid match_id"}
            elif not player:
                return {"error": True, "message": f"invalid player_id"}
            elif not round:
                return {"error": True, "message": f"invalid round_id"}

            prediction = b["prediction"]

            predictions.append({"match": match,
                                "player": player,
                                "round": round,
                                "prediction": prediction})
    except KeyError as e:
        return {"error": True, "message": f"payload missing {str(e)}"}

    predictions = prediction_service.list()
    new_id = len(predictions)

    return_predictions = []

    for p in predictions:
        new_id = new_id + 1
        prediction_exists = prediction_service.prediction_exists(p["round"].id, p["match"].id, p["player"].id)
        if prediction_exists:
            prediction_exists.drop = False
            prediction_exists = prediction_service.update(prediction_exists)
            return_predictions.append(prediction_exists.to_dict())

        prediction = Prediction(id=new_id,
                                round_id=p["round"].id,
                                player_id=p["player"].id,
                                match_id=p["match"].id,
                                prediction=p["prediction"])

        return_predictions.append(prediction_service.create(prediction).to_dict())

    return {"predictions": return_predictions}


@route("/dropprediction", open_url=True, methods=["GET"])
def drop_prediction():
    prediction_id = request.args.get("id")
    if not prediction_id:
        return {"error": True, "message": "missing id"}

    service = PredictionService()

    prediction = service.get(prediction_id)
    prediction.drop = True

    return service.update(prediction).to_dict()
