#! /usr/bin/env python3
import sys
import os
sys.path.append(os.path.abspath(__file__ + '/..'))
from telethon import TelegramClient, sync # pylint: disable=unused-import
from telethon.errors import SessionPasswordNeededError, PhoneNumberUnoccupiedError
from telethon.utils import parse_phone
from lib.config import config

if len(sys.argv) < 2:
    print('Usage:', os.path.basename(__file__), '<phone> [<code> <code hash> [2FA password]]')
    exit(1)

client = TelegramClient(
    os.path.join(config.get('paths', 'sessions'), parse_phone(sys.argv[1])),
    config.get('telegram', 'api_id'),
    config.get('telegram', 'api_hash')
)
delete_session = False
try:
    client.session.set_dc(2, '149.154.167.40', 443)
    if not client.is_connected():
        client.connect()
        print('Auth key =', (client.session.auth_key.key.hex()))

    if not client.is_user_authorized():
        args = dict(zip(('phone', 'code', 'phone_code_hash', 'password'), sys.argv[1:]))
        try:
            resp = client.sign_in(**args)
            if not args.get('code'):
                print('Code hash:', resp.phone_code_hash)
                if not resp.phone_registered:
                    print('Phone is not registered')
        except PhoneNumberUnoccupiedError:
            client._phone = args.get('phone')
            client._phone_code_hash[client._phone] = args.get('phone_code_hash')
            client.sign_up(args.get('code'), 'dmig')
        except SessionPasswordNeededError:
            print('2FA password required')
    else:
        me = client.get_me()
        print(me)
        # print(client.download_profile_photo(me))
        # print(me.photo)

    print('Is authorized:', client.is_user_authorized())
except:
    delete_session = True
    raise
finally:
    client.disconnect()
    # if delete_session:
    #     client.session.delete()
