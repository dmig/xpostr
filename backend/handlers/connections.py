from pycnic.errors import HTTP_400
from lib.rpc_client import rpc_call
from handlers.authorized import AuthorizedHandler


class Connections(AuthorizedHandler):
    audience = 'authorized'

    def get(self):
        return list(rpc_call('get_user_connections', self.user['id']))

    def post(self):
        vk_id = self.request.data.get('vk_id')
        tg_id = self.request.data.get('tg_id')
        active = int(self.request.data.get('active', 1))

        if not (vk_id and tg_id):
            raise HTTP_400('Invalid `vk_id` or `tg_id` value')

        rpc_call('set_connection', self.user['id'], vk_id, tg_id, active)

        self.response.status_code = 204
        return ''

    def delete(self):
        vk_id = self.request.args.get('vk_id')
        tg_id = self.request.args.get('tg_id')

        if not (vk_id and tg_id):
            raise HTTP_400('Invalid `vk_id` or `tg_id` value')

        rpc_call('remove_connection', self.user['id'], vk_id, tg_id)

        self.response.status_code = 204
        return ''
