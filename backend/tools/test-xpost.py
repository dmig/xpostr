#! /usr/bin/env python3
import sys
import os
import asyncio
import uvloop
from telethon import TelegramClient
from telethon.tl import types
from telethon.utils import parse_phone
sys.path.insert(0, os.path.abspath(__file__ + '../../..'))
from lib.config import config
from lib import db, xpost


async def run(vkuser, message_ids):
    client = TelegramClient(
        os.path.join(config.get('paths', 'sessions'), parse_phone(vkuser['phone_number'])),
        config.get('telegram', 'api_id'),
        config.get('telegram', 'api_hash')
    )
    try:
        await client.connect()

        if not await client.is_user_authorized():
            print('Not authorized in telegram')
            return

        if message_ids:
            # session = ClientSession(raise_for_status=True)
            # session.params['access_token'] = \
            # access_token = '35cbc738eb48434b0cdc4fe18a93d60cd2f33560445b65c8933a6db25ce34b69fe82e9baf657fdd280704'
            access_token = 'd2823192cc962aefb2cd6675109c7ba8583348869a1f3e392d018f3f82d259a1e23d66cfbb1051ae00c48'
                # '47a2326eb4d98cb052832e53401e7f83c6cb80a4234af8229b9440fbd50f89fe24dd75952772fdc3d1184'
                # '4527bb654723ecf72216d44933fc5c2346eca07aaac96da393e4eaec7c28a905ee587aeab6e8d35ea3dbd'
            # vkuser['access_token']
            # session.params['v'] = '5.92'

            async for message in client.iter_messages(
                await client.get_entity(int(args['tg_id'])), ids=message_ids
            ):
                if not message:
                    print('Message is None')
                    continue

                vkmessage = xpost.WallPost(access_token, int(args.get('vk_gid')), message)
                print(await vkmessage.upload())
            return

        if args.get('tg_id'):
            async for message in client.iter_messages(await client.get_entity(int(args.get('tg_id')))):
                if isinstance(message, types.MessageService):
                    continue

                if isinstance(message.media, types.MessageMediaPhoto) or\
                    isinstance(message.media, types.MessageMediaWebPage) and\
                    not isinstance(message.media.webpage, (
                        types.WebPageEmpty, types.WebPageNotModified, types.WebPagePending
                    )) and message.media.webpage.photo:
                    media = '🖼'
                elif isinstance(message.media, types.MessageMediaDocument):
                    media = '📄'
                elif isinstance(message.media, types.MessageMediaWebPage) and\
                    not isinstance(message.media.webpage, (
                        types.WebPageEmpty, types.WebPageNotModified, types.WebPagePending
                    )):
                    media = '🔗'
                elif isinstance(message.media, (types.MessageMediaVenue, types.MessageMediaGeo,
                                                types.MessageMediaGeoLive)):
                    media = '🌏'
                elif isinstance(message.media, types.MessageMediaPoll):
                    media = '❓'
                elif message.media:
                    media = '❌'
                else:
                    media = ' '
                print(message.id, media, repr(message.text))
            return

        async for dialog in client.iter_dialogs():
            if not dialog.is_channel or dialog.is_group:
                continue

            print(dialog.entity.id, dialog.name)
    finally:
        client.disconnect()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('Usage:', os.path.basename(__file__),
            '<vk user id> [<tg channel id> [<vk group id> <tg message id> [<tg message id> ...]]]')
        exit(1)

    args = dict(zip(('vk_id', 'tg_id', 'vk_gid'), sys.argv[1:4]))
    message_ids = [] if len(sys.argv) < 5 else list(map(int, sys.argv[4:]))

    vkuser = db.get_user(args['vk_id'])
    if not vkuser:
        print('Unknown vk user id')
        exit(1)

    if not vkuser['access_token']:
        print('VK token is invalid')
        exit(1)

    if not vkuser['phone_number']:
        print('VK user phone number not set')
        exit(1)

    loop = uvloop.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run(vkuser, message_ids))
