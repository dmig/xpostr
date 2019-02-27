from lib import db
from lib.pycnic.errors import HTTP_400
from handlers.authorized import AuthorizedHandler


class Connections(AuthorizedHandler):
    audience = 'authorized'

    def get(self):
        return [dict(zip(c.keys(), c)) \
            for c in db.get_group_connections(self.user['id'])]

    def post(self):
        vk_id = self.request.data.get('vk_id')
        tg_id = self.request.data.get('tg_id')
        active = int(self.request.data.get('active', 1))

        if not (vk_id and tg_id):
            raise HTTP_400('Invalid `vk_id` or `tg_id` value')

        db.set_group_connection(self.user['id'], vk_id, tg_id, active)

        self.response.status_code = 204
        return ''

    def delete(self):
        vk_id = self.request.args.get('vk_id')
        tg_id = self.request.args.get('tg_id')

        if not (vk_id and tg_id):
            raise HTTP_400('Invalid `vk_id` or `tg_id` value')

        db.del_group_connection(self.user['id'], vk_id, tg_id)

        self.response.status_code = 204
        return ''
