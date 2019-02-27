from os.path import join
from lib.config import config
from lib.pycnic.errors import HTTP_500, HTTPError
from handlers.telegram import TelegramHandler, HTTP_424

class TGInfo(TelegramHandler):
    def get(self):
        client = self._get_client()
        if not client:
            return {'authorized': False}

        client.connect()

        return self._get_info(client)
