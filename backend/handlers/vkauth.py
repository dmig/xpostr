from requests_oauthlib import OAuth2Session

import lib.db as db
from lib.config import config
from lib.pycnic.errors import HTTP_400, HTTP_401, HTTP_500
from handlers.logger import LoggerHandler

class VKAuth(LoggerHandler):
    def get(self):
        state = self.request.args.get('state')

        # final stage
        if state:
            return self._final_stage(state)

        params = dict(config.items('vk'))

        Session = OAuth2Session(
            params['client_id'],
            scope='groups,offline',
            redirect_uri=params['redirect_uri']
        )

        # first stage
        authorization_url, state = Session.authorization_url(
            'https://oauth.vk.com/authorize', state=state
        )
        back_url = self.request.args.get('back_url')
        db.set_interim_state(state, {'provider': 'VK', 'back_url': back_url})

        return {'auth_url': authorization_url}

    def _final_stage(self, state):
        info = db.get_interim_state(state)
        if not info:
            raise HTTP_400('Invalid `state` parameter')

        if 'auth_results' in info:
            db.del_interim_state(state)
            res = info['auth_results']

            if res['ok']:
                # self.response.set_header('Authorization', 'Bearer ' + res['token'])
                # self.response.status_code = 303
                # self.response.set_header('Location', info.get('back_url', '/'))

                return {'token': 'Bearer ' + res['token']}

            raise HTTP_401(res['message'], res['code'])
        raise HTTP_500('Internal error')
