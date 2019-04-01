from lib.rpc_client import rpc_call
from handlers.telegram import TelegramHandler

class TGChannels(TelegramHandler):

    def get(self):
        res = list(map(self._set_photo_path, rpc_call('get_sources', self.user['id'], timeout=10)))
        res.sort(key=lambda item: item['title'])
        return res
