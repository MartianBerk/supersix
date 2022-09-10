from datetime import datetime, timedelta
import re

from baked.lib.supersix.model import Player, Prediction, Round, RoundWinner
from baked.lib.supersix.service import LeagueService, MatchService, PlayerService, PredictionService, RoundService
from baked.lib.webapi import request, response

from .. import supersix


PERMISSIONS = ["ADMIN"]


@supersix.route("/listleagues", subdomains=["admin"], permissions=PERMISSIONS, methods=["GET"])
def list_leagues():
    leagues = LeagueService().list()
    return response({"leagues": [l.to_dict() for l in leagues]})


@supersix.route("/listplayers", subdomains=["admin"], permissions=PERMISSIONS, methods=["GET"])
def list_players():
    players = PlayerService().list()
    return response({"players": [p.to_dict() for p in players]})


@supersix.route("/listrounds", subdomains=["admin"], permissions=PERMISSIONS, methods=["GET"])
def list_rounds():
    rounds = RoundService().list()
    return response({"rounds": [r.to_dict() for r in rounds]})


@supersix.route("/currentround", subdomains=["admin"], permissions=PERMISSIONS, methods=["GET"])
def current_round():
    round = RoundService().current_round()

    if not round:
        return {"current_round": None}

    round = round.to_dict()
    round["start_date"] = round["start_date"].isoformat()
    round["current_match_date"] = round["current_match_date"].isoformat() if round.get("current_match_date") else None

    return {"current_round": round}


@supersix.route("/historicrounds", subdomains=["admin"], permissions=PERMISSIONS, methods=["GET"])
def historic_rounds():
    rounds = RoundService().historic_rounds()
    rounds.sort(key=lambda x: x.start_date, reverse=True)

    treated_rounds = []
    for round in rounds:
        round = round.to_dict()
        round["start_date"] = round["start_date"].isoformat()
        round["end_date"] = round["end_date"].isoformat()
        treated_rounds.append(round)

    return {"rounds": treated_rounds}


@supersix.route("/listpredictions", subdomains=["admin"], permissions=PERMISSIONS, methods=["GET"])
def list_predictions():
    try:
        round_id = request.args["round"]
        player_id = request.args["playerid"]
        match_date = request.args["matchdate"]

        start_date = datetime.strptime(match_date, "%d-%m-%Y")
        end_date = start_date + timedelta(days=1)

    except KeyError as e:
        return {"error": True, "message": f"missing mandatory value for {str(e)}"}

    except ValueError:
        return {"error": True, "message": "invalid date format, expected dd-mm-yyyy"}

    filters = [
        ("round_id", "equalto", round_id),
        ("player_id", "equalto", player_id),
        ("match_date", "greaterthanequalto", start_date),
        ("match_date", "lessthanequalto", end_date)
    ]

    predictions = PredictionService().list_match_predictions(filters=filters)
    return response({"predictions": [p.to_dict() for p in predictions]})


@supersix.route("/listpredictionsnew", subdomains=["admin"], permissions=PERMISSIONS, methods=["GET"])
def list_predictions_new():
    try:
        match_date = request.args["matchdate"]

        start_date = datetime.strptime(match_date, "%d-%m-%Y")
        end_date = start_date + timedelta(days=1)

    except KeyError as e:
        return {"error": True, "message": f"missing mandatory value for {str(e)}"}

    except ValueError:
        return {"error": True, "message": "invalid date format, expected dd-mm-yyyy"}

    current_round = RoundService().current_round()
    if not current_round:
        return response({"error": True, "message": "Something went wrong, please try again later."})

    filters = [
        ("round_id", "equalto", current_round.round_id),
        ("match_date", "greaterthanequalto", start_date),
        ("match_date", "lessthanequalto", end_date)
    ]

    predictions = PredictionService().list_match_predictions(filters=filters)
    predictions.sort(key=lambda p: f"{p.player_id}-{p.match_id}")

    return response({"predictions": [p.to_dict() for p in predictions]})


@supersix.route("/addprediction", subdomains=["admin"], permissions=PERMISSIONS, methods=["POST"])
def add_prediction_admin():
    body = request.json

    try:
        new_prediction = body["prediction"]

        match = MatchService().get(body["match_id"])
        player = PlayerService().get(body["player_id"])

        if not match:
            return response({"error": True, "message": f"invalid match_id"})
        elif not player:
            return response({"error": True, "message": f"invalid player_id"})

    except KeyError as e:
        return response({"error": True, "message": f"Missing mandatory value {str(e)}."})

    current_round = RoundService().current_round()
    if not current_round:
        return response({"error": True, "message": "Something went wrong, please try again later."})

    prediction_service = PredictionService()

    # ensure predicition has changed
    prediction = prediction_service.prediction_exists(current_round.round_id, match.id, player.id)

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
        new_id = new_id[-1].id + 1 if new_id else 0  # TODO: handle autoincrement better

        prediction = Prediction(
            id=new_id,
            round_id=current_round.round_id,
            player_id=player.id,
            match_id=match.id,
            prediction=new_prediction
        )

        prediction = prediction_service.create(prediction)

    return response(prediction.to_dict())


@supersix.route("/addplayer", subdomains=["admin"], permissions=PERMISSIONS, methods=["POST"])
def add_player():
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
    return response(player.to_dict())


@supersix.route("/addround", subdomains=["admin"], permissions=PERMISSIONS, methods=["POST"])
def add_round():
    body = request.json

    service = RoundService()

    if service.current_round():
        return {"error": True, "message": "Round already in progress."}

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
    return response(round.to_dict())


@supersix.route("/endround", subdomains=["admin"], permissions=PERMISSIONS, methods=["POST"])
def end_round():
    body = request.json

    service = RoundService()
    rounds = service.list(filters=[("end_date", "null", None)])

    try:
        winner_ids = body["winner_ids"]

        if rounds:
            end_date = body["end_date"]
            end_date = datetime.strptime(end_date, "%d-%m-%Y")
            rounds[0].end_date = end_date

            round_winners = [RoundWinner(round_id=rounds[0].id, player_id=w_id) for w_id in winner_ids]
            service.end(rounds[0], round_winners)

    except KeyError as e:
        return {"error": True, "message": f"payload missing {str(e)}"}

    except ValueError:
        return {"error": True, "message": "invalid date format, expected %d-%m-%Y"}

    return {}


@supersix.route("/getround", subdomains=["admin"], permissions=PERMISSIONS, methods=["GET"])
def get_round():
    round = request.args.get("round")
    service = RoundService()

    if round:
        round = service.get(round)
        if not round:
            return {"error": True, "message": "round doesn't exist"}

        return response(round.to_dict())

    # get current round
    rounds = service.list([("end_date", "null", None)])
    if not rounds:
        return {"error": True, "message": "no round current in play"}
    elif len(rounds) > 1:
        return {"error": True, "message": "more than one current round found"}

    return response(rounds[0].to_dict())


@supersix.route("/listmatches", subdomains=["admin"], permissions=PERMISSIONS, methods=["GET"])
def list_matches():
    match_date = request.args.get("matchDate")
    if not match_date:
        return response({"error": True, "message": "missing matchDate"})

    service = MatchService()

    try:
        start_date = datetime.strptime(match_date, "%d-%m-%Y")
        end_date = start_date + timedelta(days=1)
    except ValueError:
        return {"error": True, "message": "invalid date format, expected dd-mm-yyyy"}

    filters = [("match_date", "greaterthanequalto", start_date), ("match_date", "lessthanequalto", end_date)]
    
    matches = service.list(filters)
    matches.sort(key=lambda m: m.game_number or 0)
    
    return response({"matches": [m.to_dict() for m in matches]})


@supersix.route("/listmatchesnew", subdomains=["admin"], permissions=PERMISSIONS, methods=["GET"])
def list_matches_new():
    service = MatchService()
    now = datetime.now()

    # default filters to the next month in advance
    filters = [
        ("match_date", "greaterthan", now),
        ("match_date", "lessthan", now + timedelta(days=31))
    ]

    matches = service.list(filters)
    matches.sort(key=lambda m: m.game_number or 0)
    
    return response({"matches": [m.to_dict() for m in matches]})



@supersix.route("/getmatch", subdomains=["admin"], permissions=PERMISSIONS, methods=["GET"])
def get_match():
    match_id = request.args.get("id")
    if not match_id:
        return response({"error": True, "message": "missing id"})

    service = MatchService()

    match = service.get(match_id)
    if not match:
        return response({"error": True, "message": f"No match found for id {match_id}"})
    
    return response(match.to_dict())


@supersix.route("/addmatch", subdomains=["admin"], permissions=PERMISSIONS, methods=["POST"])
def add_match():
    payload = request.json
    if not payload:
        return {}

    try:
        service = MatchService()

        # First, is it a valid match that hasn't already been selected?
        match = service.get(payload["id"])
        if not match:
            return response({"error": True, "message": f"No match found for id {payload['id']}"})

        elif match.use_match and payload["game_number"] != match.game_number:
            return response({"error": True, "message": f"Match already selected as game number {match.game_number}"})

        elif payload["game_number"] < 1 or payload["game_number"] > 6:
            return response({"error": True, "message": f"Invalid game_number, must be between 1 and 6."})

        # Second, is there space for a new match?
        start_date = match.match_date.date()
        end_date = start_date + timedelta(days=1)
        filters = [("match_date", "greaterthanequalto", start_date),
                   ("match_date", "lessthanequalto", end_date),
                   ("use_match", "equalto", True)]

        current_matches = service.list(filters=filters)

        if len(current_matches) == 6:
            return response({"error": True, "message": f"Six matches already submitted for {str(start_date)}. Drop a match first."})

        # Third, if game number already exists, drop it.
        game_number = payload["game_number"]
        for existing_match in current_matches:
            if existing_match.game_number == game_number:
                existing_match.use_match = 0
                service.update(existing_match)

        # Lastly, add new match.
        match.game_number = game_number
        match.use_match = True
        service.update(match)

    except KeyError as e:
        return response({"error": True, "message": f"missing mandatory value in match for {str(e)}"})

    except ValueError:
        return {"error": True, "message": "invalid date format, expected dd-mm-yyyy"}

    return response(match.to_dict())


@supersix.route("/addmatches", subdomains=["admin"], permissions=PERMISSIONS, methods=["POST"])
def add_matches():
    match_date = request.args.get("matchDate")
    if not match_date:
        return response({"error": True, "message": "missing matchDate"})

    matches = request.json

    if not matches:
        return {}
    elif len(matches) != 6:
        return response({"error": True, "message": "must submit 6 matches"})

    try:
        # validate game_numbers are 1 - 6
        if sum([m["game_number"] for m in matches]) != 21:
            return response({"error": True, "message": "game_numbers must be 1 - 6"})

        service = MatchService()

        # TODO: look to improve this
        # undo any selected current matches for the date
        start_date = datetime.strptime(match_date, "%d-%m-%Y")
        end_date = start_date + timedelta(days=1)
        filters = [("match_date", "greaterthanequalto", start_date),
                   ("match_date", "lessthanequalto", end_date),
                   ("use_match", "equalto", True)]

        current_matches = service.list(filters=filters)
        for match in current_matches:
            match.use_match = 0
            service.update(match)

        valid_matches = []

        for match in matches:
            match_id = match["id"]
            game_number = match["game_number"]

            match = service.get(match_id)
            if not match:
                return response({"error": True, "message": f"no match found for id {match_id}"})

            match.use_match = True
            match.game_number = game_number

            valid_matches.append(match)

        for i, match in enumerate(valid_matches):
            valid_matches[i] = service.update(match)

        return response({"matches": [m.to_dict() for m in valid_matches]})

    except KeyError as e:
        return response({"error": True, "message": f"missing mandatory value in match for {str(e)}"})

    except ValueError:
        return {"error": True, "message": "invalid date format, expected dd-mm-yyyy"}


@supersix.route("/dropmatch", subdomains=["admin"], permissions=PERMISSIONS, methods=["GET"])
def drop_match():
    match_id = request.args.get("id")
    if not match_id:
        return response({"error": True, "message": "missing id"})

    service = MatchService()

    match = service.get(match_id)
    if not match:
        return response({"error": True, "message": "id not found"})

    match.game_number = None
    match.use_match = False
    match = service.update(match)

    return response(match.to_dict())


@supersix.route("/addpredictions", subdomains=["admin"], permissions=PERMISSIONS, methods=["POST"])
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
                return response({"error": True, "message": f"invalid match_id"})
            elif not player:
                return response({"error": True, "message": f"invalid player_id"})
            elif not round:
                return response({"error": True, "message": f"invalid round_id"})

            prediction = b["prediction"]

            predictions.append({"match": match,
                                "player": player,
                                "round": round,
                                "prediction": prediction})
    except KeyError as e:
        return response({"error": True, "message": f"payload missing {str(e)}"})

    new_id = prediction_service.list()
    new_id = new_id[-1].id if new_id else 0

    return_predictions = []

    for p in predictions:
        new_id = new_id + 1
        prediction_exists = prediction_service.prediction_exists(p["round"].id, p["match"].id, p["player"].id)
        if prediction_exists:
            prediction_exists.drop = True
            prediction_service.update(prediction_exists)

        prediction = Prediction(id=new_id,
                                round_id=p["round"].id,
                                player_id=p["player"].id,
                                match_id=p["match"].id,
                                prediction=p["prediction"])

        return_predictions.append(prediction_service.create(prediction).to_dict())

    return response({"predictions": return_predictions})


@supersix.route("/dropprediction", subdomains=["admin"], permissions=PERMISSIONS, methods=["GET"])
def drop_prediction():
    prediction_id = request.args.get("id")
    if not prediction_id:
        return response({"error": True, "message": "missing id"})

    service = PredictionService()

    prediction = service.get(prediction_id)
    prediction.drop = True

    return response(service.update(prediction).to_dict())


@supersix.route("/setspecialmessage", subdomains=["admin"], permissions=PERMISSIONS, methods=["POST"])
def set_special_message():
    body = request.json
    message = body.get("message")

    if not message:
        return {}

    service = RoundService()

    try:
        message = service.set_special_message(message)
        return response({"message": message.message})

    except ValueError as e:
        return response({"error": True, "message": str(e)})


@supersix.route("/getspecialmessage", subdomains=["admin"], permissions=PERMISSIONS, methods=["GET"])
def get_special_message():
    service = RoundService()

    message = service.get_special_message()
    if not message:
        return {}

    return response({"message": message.message})


@supersix.route("/endspecialmessage", subdomains=["admin"], permissions=PERMISSIONS, methods=["GET"])
def end_special_message():
    service = RoundService()

    service.end_special_message()

    return {}


@supersix.route("dropplayer", subdomains=["admin"], permissions=PERMISSIONS, methods=["GET"])
def drop_player():
    player_id = request.args.get("id")

    if player_id:
        service = PlayerService()

        player = service.get(player_id)
        if player:
            player.retired = True
            service.update(player)

            return player.to_dict()

    return {}


@supersix.route("reactivateplayer", subdomains=["admin"], permissions=PERMISSIONS, methods=["GET"])
def reactivate_player():
    player_id = request.args.get("id")

    if player_id:
        service = PlayerService()

        player = service.get(player_id)
        if player:
            player.retired = False
            service.update(player)

            return player.to_dict()

    return {}
