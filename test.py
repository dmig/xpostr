#! /usr/bin/env python3
# coding=utf8

import os
from telethon import TelegramClient, events, sync # pylint: disable=unused-import
# from telethon.sessions.sqlite import EXTENSION
from telethon.tl import types
from lib.config import config

async def print_message(event):
    msg = event.message # pylint: disable=redefined-outer-name
    print(msg.date.isoformat(' '), 'media message:' if msg.media else '', msg.message)
    print(msg)

# print([os.path.splitext(os.path.basename(f))[0]
#         for f in os.listdir(config.get('paths', 'sessions')) if f.endswith(EXTENSION)])

with TelegramClient(
        os.path.abspath(
            config.get('paths', 'sessions') + '/' +
            config.get('telegram', 'session_name', fallback='test')
        ),
        config.get('telegram', 'api_id'),
        config.get('telegram', 'api_hash')
    ) as client:
    client.start() #bot_token=config.get('telegram', 'bot_token')
    # me = client.get_me()
    # print(me.stringify())

    for dialog in client.get_dialogs():
        if not dialog.is_channel:
            continue

        if isinstance(dialog.entity.photo, types.ChatPhotoEmpty):
            print(dialog.entity.id, dialog.entity.title)
        else:
            fn = os.path.join(
                config.get('paths', 'avatars'), 'channel-' + str(dialog.entity.id) + '.jpg'
            )

            if not os.path.exists(fn):
                fn = client.download_profile_photo(dialog.entity, fn, download_big=False)
            print(dialog.entity.id, dialog.entity.title, '🖕', fn)

        msg = dialog.message.message
        if msg:
            print(' ', msg[:75] + '...' if len(msg) > 78 else msg)

    # channel = client.get_entity('https://t.me/huytest')
    # print(channel.stringify())
    # print(client.get_messages(channel, 5))

    # client.add_event_handler(print_message, events.NewMessage(chats=(1174949488), incoming=True))
    # client.catch_up()
    # print('event handlers:', client.list_event_handlers())
    # client.run_until_disconnected()
