from requests import Session
from lib import jwt_auth
from lib.config import config
from lib.errors import VKException
from lib.rpc_client import rpc_call
from lib.pycnic.errors import HTTP_403, HTTP_500
from handlers.logger import LoggerHandler

class VKAuth(LoggerHandler):
    def get(self):
        code = self.request.args.get('code')

        # final stage
        if code:
            return self._final_stage(code)
        elif self.request.args.get('error'):
            self.logger.info('Error response from VK: %s', self.request.args)

            raise HTTP_403(
                self.request.args.get('error_description'),
                self.request.args.get('error_reason', self.request.args.get('error'))
            )

        # first stage
        client_id = config.get('vk', 'client_id')

        return {
            'auth_url': 'https://oauth.vk.com/authorize?display=page&v=5.92'
                        '&scope=wall,photos,video,pages,docs,groups,offline'
                        '&redirect_uri=https://api.vk.com/blank.html'
                        '&response_type=code&revoke=1'
                        f'&client_id={client_id}'
        }

    def _final_stage(self, code):
        client_id = config.get('vk', 'client_id')
        client_secret = config.get('vk', 'client_secret')
        vksession = Session()
        try:
            resp = vksession.get(
                'https://oauth.vk.com/access_token?'
                'redirect_uri=https://api.vk.com/blank.html'
                f'&client_id={client_id}&client_secret={client_secret}&code={code}'
            )
            resp.raise_for_status()

            auth = resp.json()
            if not auth.get('access_token'):
                raise VKException(auth)

            resp = vksession.get(
                'https://api.vk.com/method/users.get',
                params={
                    'v': '5.92',
                    'user_ids': auth['user_id'],
                    'fields': 'photo_100',
                    'access_token': auth['access_token']
                }
            )
            resp.raise_for_status()
            user = resp.json()
            if user.get('error'):
                raise VKException(user)

            user = user.get('response', {})
            user = {
                'id': user[0]['id'],
                'fullname':\
                    (user[0].get('first_name', '') + ' ' + user[0].get('last_name', '')).strip(),
                'photo': user[0].get('photo_100'),
                'access_token': auth['access_token']
            } if user else {}

            res = rpc_call('set_vk_user', user)

            token = jwt_auth.create_token({
                'id': auth['user_id'],
                'aud': 'authorized'
            })

            self.logger.info('Issued JWT: %s', token)

            return {'ok': True, 'token': token.decode("utf-8")}
        except VKException as e:
            self.logger.warning('Error authorizing user on VK: %s', e)

            raise HTTP_403(e.message, e.code)
        except Exception as e:
            self.logger.exception('Error authorizing user on VK: %s', e)
        finally:
            vksession.close()

        raise HTTP_500('Internal error')
