from lib.rpc_client import rpc_call
# from pycnic.errors import HTTP_500, HTTPError
from handlers.telegram import TelegramHandler

class TGChannels(TelegramHandler):

    def get(self):
        return list(map(self._set_photo_path, rpc_call('get_sources', self.user['id'], timeout=10)))
