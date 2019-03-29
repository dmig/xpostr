from lib.rpc_client import rpc_call
# from lib.pycnic.errors import HTTP_500, HTTPError
from handlers.authorized import AuthorizedHandler

class TGChannels(AuthorizedHandler):
    def get(self):
        return rpc_call('get_sources', self.user['id'], timeout=10)
