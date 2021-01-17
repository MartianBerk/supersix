from mylib.webapi import bind_app

supersix = bind_app("supersix")

from .admin import routes
from .game import routes
from .stats import routes
