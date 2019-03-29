#! /usr/bin/env python3
import asyncio
import sys
import os
sys.path.append(os.path.abspath(__file__ + '/..'))
from telethon import TelegramClient, events
from telethon.errors import SessionPasswordNeededError, PhoneNumberUnoccupiedError
from telethon.utils import parse_phone
from backend.lib.config import config

if len(sys.argv) < 2:
    print('Usage:', os.path.basename(__file__), '<phone> [<code> <code hash> [2FA password]]')
    exit(1)

def _print_message(event):
    msg = event.message # pylint: disable=redefined-outer-name
    print(msg.date.isoformat(' '), msg.message, type(msg.media))

async def main():
    client = TelegramClient(
        os.path.join(config.get('paths', 'sessions'), parse_phone(sys.argv[1])),
        config.get('telegram', 'api_id'),
        config.get('telegram', 'api_hash'),
        loop=asyncio.get_event_loop()
    )

    try:
        # client.session.set_dc(2, '149.154.167.40', 443)
        await client.connect()
        # print('Auth key =', (client.session.auth_key.key.hex()))

        if not await client.is_user_authorized():
            args = dict(zip(('phone', 'code', 'phone_code_hash', 'password'), sys.argv[1:]))
            try:
                resp = await client.sign_in(**args)
                if not args.get('code'):
                    print('Code hash:', resp.phone_code_hash)
                    if not resp.phone_registered:
                        print('Phone is not registered')
            except PhoneNumberUnoccupiedError:
                # client._phone = args.get('phone')
                # client._phone_code_hash[client._phone] = args.get('phone_code_hash')
                await client.sign_up(first_name='dmig', **args)
            except SessionPasswordNeededError:
                print('2FA password required')
        else:
            me = await client.get_me()
            print(me)
            # client.add_event_handler(
            #     _print_message,
            #     events.NewMessage(chats=1174949488, incoming=True)
            # )
            # await asyncio.sleep(3)
            # client.remove_event_handler(
            #     _print_message,
            #     events.NewMessage(chats=1174949488, incoming=True)
            # )
            # print(client.download_profile_photo(me))
            # print(me.photo)

        print('Is authorized:', await client.is_user_authorized())
    finally:
        # client.disconnect()
        del client

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    finally:
        loop.close()
