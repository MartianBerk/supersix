from datetime import datetime, timedelta

from mb.supersix.model import Player, Prediction, Round
from mb.supersix.service import MatchService, PlayerService, PredictionService, RoundService
from mylib.webapi import WebApi


@WebApi.route("/listplayers", open_url=True, methods=["GET"])
def list_players():
    players = PlayerService().list()
    return WebApi.response({"players": [p.to_dict() for p in players]})


@WebApi.route("/listrounds", open_url=True, methods=["GET"])
def list_rounds():
    rounds = RoundService().list()
    return WebApi.response({"rounds": [r.to_dict() for r in rounds]})


@WebApi.route("/listpredictions", open_url=True, methods=["GET"])
def list_predictions():
    predictions = PredictionService().list()
    return WebApi.response({"predictions": [p.to_dict() for p in predictions]})


@WebApi.route("/addplayer", open_url=True, methods=["POST"])
def add_player():
    request = WebApi.request()
    body = request.json

    service = PlayerService()

    new_id = service.next_available_id()

    try:
        player = Player(id=new_id,
                        first_name=body["first_name"],
                        last_name=body["last_name"],
                        join_date=datetime.now())
    except KeyError as e:
        return {"error": True, "message": f"payload missing {str(e)}"}

    player = service.create(player)
    return WebApi.response(player.to_dict())


@WebApi.route("/addround", open_url=True, methods=["POST"])
def add_round():
    request = WebApi.request()
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
    return WebApi.response(round.to_dict())


@WebApi.route("/getround", open_url=True, methods=["GET"])
def get_round():
    request = WebApi.request()
    round = request.args.get("round")
    service = RoundService()

    if round:
        round = service.get(round)
        if not round:
            return {"error": True, "message": "round doesn't exist"}

        return WebApi.response(round.to_dict())

    # get current round
    rounds = service.list([("end_date", "null", None)])
    if not rounds:
        return {"error": True, "message": "no round current in play"}
    elif len(rounds) > 1:
        return {"error": True, "message": "more than one current round found"}

    return WebApi.response(rounds[0].to_dict())


@WebApi.route("/listmatches", open_url=True, methods=["GET"])
def list_matches():
    request = WebApi.request()
    match_date = request.args.get("matchDate")
    if not match_date:
        return WebApi.response({"error": True, "message": "missing matchDate"})

    service = MatchService()

    try:
        start_date = datetime.strptime(match_date, "%d-%m-%Y")
        end_date = start_date + timedelta(days=1)
    except ValueError:
        return {"error": True, "message": "invalid date format, expected dd-mm-yyyy"}

    filters = [("match_date", "greaterthanequalto", start_date), ("match_date", "lessthanequalto", end_date)]
    return WebApi.response({"matches": [m.to_dict() for m in service.list(filters)]})


@WebApi.route("/addmatch", open_url=True, methods=["GET"])
def add_match():
    request = WebApi.request()
    match_id = request.args.get("id")
    if not match_id:
        return WebApi.response({"error": True, "message": "missing id"})

    service = MatchService()

    match = service.get(match_id)
    if not match:
        return {"error": True, "message": "id not found"}

    match.use_match = True
    match = service.update(match)

    return WebApi.response(match.to_dict())


@WebApi.route("/addmatches", open_url=True, methods=["POST"])
def add_matches():
    request = WebApi.request()
    body = request.json

    match_ids = body.get("ids")
    if not match_ids:
        return WebApi.response({"error": True, "message": "missing ids from payload"})

    service = MatchService()
    matches = []

    for mid in match_ids:
        match = service.get(mid)
        match.use_match = True

        matches.append(service.update(match))

    return WebApi.response({"matches": [m.to_dict() for m in matches]})


@WebApi.route("/dropmatch", open_url=True, methods=["GET"])
def drop_match():
    request = WebApi.request()
    match_id = request.args.get("id")
    if not match_id:
        return WebApi.response({"error": True, "message": "missing id"})

    service = MatchService()

    match = service.get(match_id)
    if not match:
        return WebApi.response({"error": True, "message": "id not found"})

    match.use_match = False
    match = service.update(match)

    return WebApi.response(match.to_dict())


@WebApi.route("/addpredictions", open_url=True, methods=["POST"])
def add_predictions():
    request = WebApi.request()
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
                return WebApi.response({"error": True, "message": f"invalid match_id"})
            elif not player:
                return WebApi.response({"error": True, "message": f"invalid player_id"})
            elif not round:
                return WebApi.response({"error": True, "message": f"invalid round_id"})

            prediction = b["prediction"]

            predictions.append({"match": match,
                                "player": player,
                                "round": round,
                                "prediction": prediction})
    except KeyError as e:
        return WebApi.response({"error": True, "message": f"payload missing {str(e)}"})

    new_id = prediction_service.list()
    new_id = new_id[-1].id if new_id else 0

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

    return WebApi.response({"predictions": return_predictions})


@WebApi.route("/dropprediction", open_url=True, methods=["GET"])
def drop_prediction():
    request = WebApi.request()
    prediction_id = request.args.get("id")
    if not prediction_id:
        return WebApi.response({"error": True, "message": "missing id"})

    service = PredictionService()

    prediction = service.get(prediction_id)
    prediction.drop = True

    return WebApi.response(service.update(prediction).to_dict())
