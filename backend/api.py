#! /usr/bin/env python3
# http://pycnic.nullism.com/docs/

from lib.pycnic.core import WSGI
from lib.config import config
from handlers.vkauth import VKAuth
from handlers.vkgroups import VKGroups
from handlers.vkinfo import VKInfo
from handlers.tgauth import TGAuth
from handlers.tgchannels import TGChannels
from handlers.connections import Connections
from handlers.test import Test


class app(WSGI):
    headers = [
        ("Access-Control-Allow-Origin", "*"),
        ("Access-Control-Allow-Methods", "GET,POST,DELETE"),
        ("Access-Control-Allow-Headers", "Accept,Authorization,Content-Type"),
    ]

    routes = [
        ('/login', VKAuth()),
        ('/vkcb', VKAuth()),
        ('/vkuser', VKInfo()),

        ('/tgauth', TGAuth()),
        ('/tguser', TGAuth()),

        ('/targets', VKGroups()),
        ('/sources', TGChannels()),
        ('/connections', Connections()),

        ('/test', Test()),
    ]
    debug = config.getboolean('globals', 'debug', fallback=False)
