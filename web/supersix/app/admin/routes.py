from datetime import datetime

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


@route("/listmatches", open_url=True, methods=["GET"])
def list_matches():
    service = MatchService()

    # TODO: filtering by date or matchday
    return {"matches": [m.to_dict() for m in service.list()]}


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


@route("/addprediction", open_url=True, methods=["POST"])
def add_prediction():
    body = request.json

    match_service = MatchService()
    player_service = PlayerService()
    prediction_service = PredictionService()
    round_service = RoundService()

    try:
        match = match_service.get(body["match_id"])
        player = player_service.get(body["player_id"])
        round = round_service.get(body["round_id"])

        if not match:
            return {"error": True, "message": f"invalid match_id"}
        elif not player:
            return {"error": True, "message": f"invalid player_id"}
        elif not round:
            return {"error": True, "message": f"invalid round_id"}

        prediction = body["prediction"]
    except KeyError as e:
        return {"error": True, "message": f"payload missing {str(e)}"}

    prediction_exists = prediction_service.prediction_exists(round.id, match.id, player.id)
    if prediction_exists:
        prediction_exists.drop = False
        prediction_exists = prediction_service.update(prediction_exists)
        return prediction_exists.to_dict()

    predictions = prediction_service.list()
    new_id = len(predictions) + 1

    prediction = Prediction(id=new_id,
                            round_id=round.id,
                            player_id=player.id,
                            match_id=match.id,
                            prediction=prediction)

    prediction = prediction_service.create(prediction)
    return prediction.to_dict()


@route("/dropprediction", open_url=True, methods=["GET"])
def drop_prediction():
    prediction_id = request.args.get("id")
    if not prediction_id:
        return {"error": True, "message": "missing id"}

    service = PredictionService()

    prediction = service.get(prediction_id)
    prediction.drop = True

    return service.update(prediction).to_dict()
