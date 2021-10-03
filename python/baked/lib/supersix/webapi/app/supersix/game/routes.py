from datetime import datetime, timedelta

from baked.lib.supersix.service import MatchService, MetaService, PlayerService, PredictionService, RoundService
from baked.lib.webapi import request, response

from .. import supersix


@supersix.route("/meta", open_url=True, subdomains=["game"], methods=["GET"])
def game_meta():
    service = MetaService()

    return response({"meta": {"teams": service.team_xref(),
                              "players": service.player_xref(),
                              "gameweeks": service.gameweeks()},
                              "next_gameweek": service.next_gameweek()})


@supersix.route("/livematches", open_url=True, subdomains=["game"], methods=["GET"])
def game_live_matches():
    match_date = request.args.get("matchDate")
    if not match_date:
        return response({"error": True, "message": "missing matchDate"})

    try:
        start_date = datetime.strptime(match_date, "%d-%m-%Y")
        end_date = start_date + timedelta(days=1)
    except ValueError:
        return {"error": True, "message": "invalid date format, expected dd-mm-yyyy"}

    filters = [("match_date", "greaterthanequalto", start_date),
               ("match_date", "lessthanequalto", end_date),
               ("use_match", "equalto", True)]

    matches = MatchService().list(filters=filters)
    matches.sort(key=lambda m: m.game_number)
    
    return_matches = []
    for match in matches:
        match_date = match.match_date.strftime("%Y-%m-%dT%H:%M:%SZ")
        return_matches.append({**match.to_dict(keys=["id", "home_team", "away_team", "home_score", "away_score", "status", "match_minute", "game_number"]),
                               "match_date": match_date})

    return response({"matches": return_matches})


@supersix.route("/livescores", open_url=True, subdomains=["game"], methods=["GET"])
def game_live_scores():
    match_date = request.args.get("matchDate")
    if not match_date:
        return response({"error": True, "message": "missing matchDate"})

    try:
        start_date = datetime.strptime(match_date, "%d-%m-%Y")
        end_date = start_date + timedelta(days=1)
    except ValueError:
        return {"error": True, "message": "invalid date format, expected dd-mm-yyyy"}

    filters = [("match_date", "greaterthanequalto", start_date),
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
        prediction_filters = [("match_id", "equalto", m.id), ("drop", "equalto", False)]
        predictions = prediction_service.list(prediction_filters)

        for p in predictions:
            player = players.get(str(p.player_id))
            if not player:
                continue

            correct = True if any([
                m.home_score is not None and m.home_score > m.away_score and p.prediction == "home",
                m.away_score is not None and m.away_score > m.home_score and p.prediction == "away",
                m.home_score is not None and m.home_score == m.away_score and p.prediction == "draw"
            ]) else False

            match = m.to_dict(keys=["home_team", "away_team"])
            match.update({"prediction": p.prediction, "correct": correct, "status": m.status})

            players[str(p.player_id)]["score"] += 1 if correct else 0
            players[str(p.player_id)]["matches"].append(match)

    players = [p for p in players.values()]
    players.sort(key=lambda x: x["score"], reverse=True)

    return response({"scores": players})


@supersix.route("/currentround", open_url=True, subdomains=["game"], methods=["GET"])
def game_current_round():
    service = RoundService()

    round = service.current_round()
    if not round:
        return {}

    return response({"current_round": round.to_dict()})


@supersix.route("/specialmessage", open_url=True, subdomains=["game"], methods=["GET"])
def special_message():
    service = RoundService()

    message = service.get_special_message()
    if not message:
        return {}

    return response({"message": message.message})


@supersix.route("/matchdetail", open_url=True, subdomains=["game"], methods=["GET"])
def match_detail():
    try:
        home_team = request.args["hometeam"]
        away_team = request.args["awayteam"]
        match_date = request.args["matchdate"]

    except KeyError as e:
        return response({"error": True, "message": f"Missing mandatory parameter {str(e)}."})

    try:
        match_date = datetime.strptime(match_date, "%d-%m-%Y")
    except ValueError:
        return {"error": True, "message": "invalid date format, expected dd-mm-yyyy"}

    service = MatchService()

    detail = service.match_detail(home_team, away_team, match_date)

    return response({"match_detail": detail})


@supersix.route("/test", subdomains=["game"], methods=["GET"])
def test():
    return response({"Logged in": True})
