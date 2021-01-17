from mylib.webapi import WebApi

supersix = WebApi.bind("supersix")

from .admin import routes
from .game import routes
from .stats import routes
