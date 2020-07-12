from datetime import datetime

from mb.supersix.model import Player, Prediction, Round
from mb.supersix.service import MatchService, PlayerService, PredictionService, RoundService
from mylib.webapi import route, request


@route("/listmatches", methods=["GET"])
def list_matches():
    matches = MatchService().list(filters={"match_date": datetime.now().date()})
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
                        join_date=datetime.now().date())
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
        round = Round(id=new_id,
                      start_date=body["start_date"],
                      end_date=body["end_date"],
                      buy_in_pence=body["buy_in"])
    except KeyError as e:
        return {"error": True, "message": f"payload missing {str(e)}"}

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

    prediction = prediction_service.create(prediction)
    return prediction.to_dict()
