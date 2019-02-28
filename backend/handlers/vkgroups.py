from requests_oauthlib import OAuth2Session

from lib.config import config
from handlers.authorized import AuthorizedHandler


class VKGroups(AuthorizedHandler):
    audience = 'authorized'

    def get(self):
        params = dict(config.items('vk'))

        session = OAuth2Session(
            params['client_id'], token={'access_token': self.user['access_token']}
        )
        r = session.get(
            'https://api.vk.com/method/groups.get',
            params={
                'v': '5.92',
                'extended': 1,
                'filter': 'groups,publics', # 'moder',
                'fields': 'can_post',
                'count': 1000,
                'access_token': self.user['access_token']
            }
        ).json()

        return [{
            'id': g['id'],
            'title': g['name'],
            'photo': g['photo_100'],
            'uri': g['screen_name']
            } for g in r.get('response', {}).get('items', []) if g['can_post']]
