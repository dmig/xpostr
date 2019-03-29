from lib.rpc_client import rpc_call
from handlers.authorized import AuthorizedHandler


class VKGroups(AuthorizedHandler):
    audience = 'authorized'

    def get(self):
        return rpc_call('get_targets', self.user['id'], timeout=5)
