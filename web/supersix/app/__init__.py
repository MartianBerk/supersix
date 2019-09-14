from mylib.webapi import app, route


@route("/")
def index():
    return "Hello World"
