from datetime import datetime

from mb.supersix.service import StatService
from mylib.webapi import WebApi


@WebApi.route("/aggregate", open_url=True, methods=["GET"])
def aggregate_stats():
    request = WebApi.request()
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

    aggregate = {}
    for s in stats:
        if s.player not in aggregate:
            aggregate[s.player] = []

        aggregate[s.player].append({"date": s.match_date,
                                    "score": s.correct,
                                    "matches": s.matches})

    return WebApi.response({"stats": [{"name": k, "scores": v} for k, v in aggregate.items()]})
