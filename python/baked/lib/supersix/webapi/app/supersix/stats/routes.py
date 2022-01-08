from datetime import datetime

from baked.lib.supersix.service import RoundService, StatService
from baked.lib.webapi import request, response

from .. import supersix


@supersix.route("/aggregate", open_url=True, subdomains=["stats"], methods=["GET"])
def aggregate_stats():
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    try:
        if start_date:
            start_date = datetime.strptime(start_date, "%d-%m-%Y")

        if end_date:
            end_date = datetime.strptime(end_date, "%d-%m-%Y")

    except ValueError:
        return {"error": True, "message": "invalid date format, expected dd-mm-yyyy"}

    service = StatService()
    stats = service.aggregate_stats(start_date=start_date, end_date=end_date)

    return_stats = []

    for s in stats:
        return_stats.append(
            {
                "playerid": s.player_id,
                "name": s.player,
                "scores": {
                    "date": s.match_date,
                    "score": s.correct,
                    "matches": s.matches
                }
            }
        )

    return response({"stats": return_stats})

    # aggregate = {}
    # for s in stats:
    #     if s.player not in aggregate:
    #         aggregate[s.player] = []

    #     aggregate[s.player_id].append({"name": s.player,
    #                                    "date": s.match_date,
    #                                    "score": s.correct,
    #                                    "matches": s.matches})

    # return response({"stats": [{"player_id": k, "name": k, "scores": v} for k, v in aggregate.items()]})


@supersix.route("/winners", open_url=True, subdomains=["stats"], methods=["GET"])
def winners():
    rounds = RoundService().historic_rounds()
    rounds.sort(key=lambda x: x.start_date, reverse=True)

    treated_rounds = []
    for round in rounds:
        round = round.to_dict()
        round["start_date"] = round["start_date"].isoformat()
        round["end_date"] = round["end_date"].isoformat()
        treated_rounds.append(round)

    return {"rounds": treated_rounds}
