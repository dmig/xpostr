#! /usr/bin/env python3
# http://pycnic.nullism.com/docs/

from pycnic.core import WSGI
from lib.config import config
from handlers.vkauth import VKAuth
from handlers.vklogout import VKLogout
from handlers.vkgroups import VKGroups
from handlers.vkinfo import VKInfo
from handlers.tgauth import TGAuth
from handlers.tgchannels import TGChannels
from handlers.connections import Connections
from handlers.test import Test

__version__ = '0.2.1'

class app(WSGI):
    routes = [
        ('/vkauth', VKAuth()),
        ('/vklogout', VKLogout()),
        ('/vkuser', VKInfo()),

        ('/tgauth', TGAuth()),
        ('/tguser', TGAuth()),

        ('/targets', VKGroups()),
        ('/sources', TGChannels()),
        ('/connections', Connections()),

        ('/test', Test()),
    ]
    debug = config.getboolean('globals', 'debug', fallback=False)
