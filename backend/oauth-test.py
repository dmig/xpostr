#! /usr/bin/env python3
import logging
import sys
import os
# from pprint import pprint
from requests_oauthlib import OAuth2Session
from lib.config import config

if len(sys.argv) < 2:
    print('Usage:', os.path.basename(__file__), '[callback url]')

params = dict(config.items('vk'))

logging.getLogger().setLevel(logging.DEBUG)
logging.getLogger('requests_oauthlib.oauth2_session').setLevel(logging.DEBUG)

Provider = OAuth2Session(
    params['client_id'],
    scope='groups,offline',
    redirect_uri=params['redirect_uri']
)

if len(sys.argv) < 2:
    # Redirect user for authorization
    authorization_url, state = Provider.authorization_url('https://oauth.vk.com/authorize')
    print('State:', state)
    print('Auth URL:', authorization_url)

elif 'code=' in sys.argv[1]:
    # Get the authorization verifier code from the callback url
    redirect_response = params['redirect_uri'] + sys.argv[1]
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = "1"

    # Fetch the access token
    token = Provider.fetch_token(
        'https://oauth.vk.com/access_token',
        client_secret=params['client_secret'],
        authorization_response=redirect_response
    )

    print('Is authorized:', Provider.authorized)
    # if not token['expires_in']:
    #     token['expires_in'] = 365 * 24 * 60 * 60
    #     token['expires_at'] += token['expires_in']

    #     Provider.token = token

    print('Token:', token)

else:
    token = {'access_token': sys.argv[1]}
    Provider.token = token
    Provider.params['access_token'] = token['access_token']

    # Fetch a protected resource, i.e. user profile
    r = Provider.get('https://api.vk.com/method/users.get', params={'v': '5.92'})
    print('User info:', r.json())

    r = Provider.get('https://api.vk.com/method/groups.get', params={
        'v': '5.92',
        'filter': 'moder',
        'extended': 1,
        'count': 1000
    })
    print('User groups:', r.json())
