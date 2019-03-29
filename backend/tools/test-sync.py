#! /usr/bin/env python3
# coding=utf8

import os
import sys
from telethon import TelegramClient, events, sync
from telethon.utils import parse_phone
from telethon.tl import types
from backend.lib.config import config

async def print_message(event):
    msg = event.message # pylint: disable=redefined-outer-name
    print(msg.date.isoformat(' '), msg.message, type(event), type(msg), type(msg.media))

def start(client: TelegramClient):
    # client.start() #bot_token=config.get('telegram', 'bot_token')
    client.connect()
    # me = client.get_me()
    # print(me.stringify())

    for dialog in client.iter_dialogs():
        if not dialog.is_channel:
            continue

        if isinstance(dialog.entity.photo, types.ChatPhotoEmpty):
            print(dialog.entity.id, dialog.entity.title)
        else:
            fn = os.path.join(
                config.get('paths', 'avatars'), 'channel-' + str(dialog.entity.id) + '.jpg'
            )

            # if not os.path.exists(fn):
            #     fn = client.download_profile_photo(dialog.entity, fn, download_big=False)
            print(dialog.entity.id, dialog.entity.title, '🖕', fn)

        msg = dialog.message.message
        if msg:
            print(' ', msg[:75] + '...' if len(msg) > 78 else msg)

    # channel = client.get_entity('https://t.me/huytest')
    # print(channel.stringify())
    # print(client.get_messages(channel, 5))

    client.add_event_handler(print_message, events.NewMessage(chats=1332837514, incoming=True))
    client.catch_up()
    print('event handlers:', client.list_event_handlers())

def stop(client):
    client.disconnect()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('Usage:', os.path.basename(__file__), '<phone_number>')
        exit(1)

    client = TelegramClient(
            os.path.abspath(
                config.get('paths', 'sessions') + '/' + parse_phone(sys.argv[1])
            ),
            config.get('telegram', 'api_id'),
            config.get('telegram', 'api_hash')
        )
    try:
        start(client)
        client.run_until_disconnected()
    finally:
        stop(client)
