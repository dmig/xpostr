from lib.rpc_client import rpc_call
from handlers.authorized import AuthorizedHandler

class VKLogout(AuthorizedHandler):
    audience = 'authorized'

    def delete(self):
        rpc_call('remove_vk_user', self.user['id'], timeout=5)

        self.response.status_code = 204
        return ''
