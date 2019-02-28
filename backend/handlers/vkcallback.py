from urllib.parse import urlencode
from requests_oauthlib import OAuth2Session

import lib.db as db
import lib.jwt_auth as jwt_auth
from lib.config import config
from lib.pycnic.errors import HTTP_400
from handlers.logger import LoggerHandler

class VKCallback(LoggerHandler):
    def get(self):
        state = self.request.args.get('state')
        error = self.request.args.get('error')
        code = self.request.args.get('code')

        if state:
            info = db.get_interim_state(state)
            if not info:
                raise HTTP_400('Invalid `state` parameter')

        if error:
            self.logger.warning('Error response from VK: %s', self.request.args)

            db.set_interim_state(state, {'auth_results': {
                'ok': False,
                'code': error,
                'message': self.request.args.get('error_description')
            }})
            self.response.status_code = 303
            self.response.set_header('Location', '/#' + urlencode({'login_state': state}))

            return ''

        params = dict(config.items('vk'))

        Session = OAuth2Session(
            params['client_id'],
            scope='groups,offline',
            redirect_uri=params['redirect_uri']
        )

        user = None
        try:
            token = Session.fetch_token(
                'https://oauth.vk.com/access_token',
                client_secret=params['client_secret'],
                code=code, state=state, include_client_id=True
            )

            # HACK workaround for VK infinite token
            if not token['expires_in']:
                token['expires_in'] = 10 * 365 * 24 * 60 * 60
                token['expires_at'] += token['expires_in']

                Session.token = token

            user = self.user_info(Session)
        except Exception as e:
            self.logger.warning('Error authorizing user on VK: %s', e)

        if user and user.get('id'):
            db.save_user(user)

            token = jwt_auth.create_token({
                'id': user['id'],
                'aud': 'authorized'
            })
            res = {'ok': True, 'token': token.decode("utf-8")}

            self.logger.info('Issued JWT: %s', token)
        else:
            self.logger.warning('Error getting user info on VK')
            res = {
                'ok': False,
                'code': 'internal_error',
                'message': 'Error getting user info'
            }
        db.set_interim_state(state, {'auth_results': res})

        self.response.status_code = 303
        self.response.set_header('Location', '/#' + urlencode({'login_state': state}))

        return ''

    @staticmethod
    def user_info(gw):
        r = gw.get(
            'https://api.vk.com/method/users.get',
            params={
                'v': '5.92',
                'user_ids': gw.token['user_id'],
                'fields': 'photo_100',
                'access_token': gw.token['access_token']
            }
        ).json()
        r = r.get('response', [])
        r = r[0] if r else {}
        return {
            'id': gw.token['user_id'],
            'fullname': (r.get('first_name', '') + ' ' + r.get('last_name', '')).strip(),
            'photo': r.get('photo_100'),
            'access_token': gw.token['access_token']
        }
