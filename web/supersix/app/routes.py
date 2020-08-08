from datetime import datetime

from mb.supersix.model import Player, Prediction, Round
from mb.supersix.service import MatchService, PlayerService, PredictionService, RoundService
from mylib.webapi import route, request


@route("/listmatches", methods=["GET"])
def list_matches():
    match_date = datetime.now().date()
    match_date = datetime.combine(match_date, datetime.min.time())

    matches = MatchService().list(filters={"match_date": match_date})
    return {"matches": [m.to_dict(keys=["home_team", "away_team", "home_score", "away_score"]) for m in matches]}


@route("/listplayers", methods=["GET"])
def list_players():
    players = PlayerService().list()
    return {"players": [p.to_dict() for p in players]}


@route("/listrounds", methods=["GET"])
def list_rounds():
    rounds = RoundService().list()
    return {"rounds": [r.to_dict() for r in rounds]}


@route("/listpredictions", methods=["GET"])
def list_predictions():
    predictions = PredictionService().list()
    return {"predictions": [p.to_dict() for p in predictions]}


@route("/addplayer", methods=["POST"])
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


@route("/addround", methods=["POST"])
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


@route("/addprediction", methods=["POST"])
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

    predictions = prediction_service.list()
    new_id = len(predictions) + 1

    prediction = Prediction(id=new_id,
                            round_id=round.id,
                            player_id=player.id,
                            match_id=match.id,
                            prediction=prediction)

    # TODO: validate prediction doesn't exist

    prediction = prediction_service.create(prediction)
    return prediction.to_dict()
