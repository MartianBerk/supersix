from baked.lib.webapi import WebApi

supersix = WebApi.bind_app("supersix")

from .admin import routes
from .game import routes
from .stats import routes
from .user import routes
from .worldcup import routes
