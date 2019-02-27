from datetime import datetime, timedelta
# pylint: disable=W0611
from jwt import (encode, decode,
                 ExpiredSignatureError, InvalidAudienceError, InvalidIssuerError, DecodeError)
from lib.config import config


def decode_token(token, audience=None):
    return decode(token, config.get('jwt', 'secret'), audience=audience, algorithms=['HS256'])


def create_token(payload):
    payload['exp'] = datetime.utcnow() + timedelta(
        minutes=config.getint('jwt', 'timeout', fallback=180)
    )

    if 'roles' in payload:
        payload['aud'] = payload['roles']
        del payload['roles']
    return encode(payload, config.get('jwt', 'secret'), algorithm='HS256')
