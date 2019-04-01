#! /usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.abspath(__file__ + '/../..'))
from telethon import TelegramClient, sync # pylint: disable=unused-import
from telethon.tl import types
from telethon.utils import parse_phone
# from telethon.helpers import add_surrogate, del_surrogate
from lib.config import config
from lib.xpost import _type_in_list


if len(sys.argv) < 2:
    print('Usage:', os.path.basename(__file__), '<phone> [<tg channel id> [message id]]')
    exit(1)

args = dict(zip(('phone', 'tg_id'), sys.argv[1:]))
message_ids = [] if len(sys.argv) < 4 else list(map(int, sys.argv[3:]))

client = TelegramClient(
    os.path.join(config.get('paths', 'sessions'), parse_phone(args['phone'])),
    config.get('telegram', 'api_id'),
    config.get('telegram', 'api_hash')
)
try:
    client.connect()

    if not client.is_user_authorized():
        print('Not authorized in telegram')
        exit(1)
    client.get_dialogs()

    if message_ids:
        for message in client.iter_messages(client.get_entity(int(args['tg_id'])), ids=message_ids):
            if not message:
                print('Message is None')
                continue

            print(message)

            min_length = config.getint('xpost', 'rich_text_min_length', fallback=256)
            is_rich = bool(message.entities) and bool(_type_in_list(
                message.entities, (types.MessageEntityBold,
                types.MessageEntityItalic, types.MessageEntityPre, types.MessageEntityCode))) and \
                len(message.raw_text) >= min_length

            min_title_length = 16
            max_title_length = min_length // 4
            pos = min(p for p in (
                message.raw_text.find('\n', min_title_length, max_title_length),
                message.raw_text.find('. ', min_title_length, max_title_length),
                message.raw_text.find(', ', min_title_length, max_title_length),
                max_title_length - 3
            ) if p != -1)

            print('Title:', message.raw_text[0:pos] + '...')

            for e, inner_text in message.get_entities_text():
                print(str(e), inner_text)
                if isinstance(e, (types.MessageEntityBold, types.MessageEntityItalic,
                                  types.MessageEntityPre, types.MessageEntityCode,
                                  types.MessageEntityMentionName)):
                    is_rich = True
                    continue
                if isinstance(e, types.MessageEntityTextUrl):
                    print('Url:', e.url)

            print(
                '{} {:4}: {!r}'.format(int(is_rich), len(message.raw_text),
                                       message.text if is_rich else message.raw_text)
            )
            # print(repr(message.text))
            print('CHAT:', message.get_chat())

            fwd = message.forward and message.forward.channel_id and message.forward.get_chat()
            if fwd and fwd.username:
                print('FWD:', fwd)
                print('https://t.me/{}/{}'.format(fwd.username, message.fwd_from.channel_post))

            if not message.media:
                continue

            # print(message.stringify())

            if isinstance(message.media, (
                    types.MessageMediaEmpty, types.MessageMediaGame, types.MessageMediaContact,
                    types.MessageMediaInvoice, types.MessageMediaUnsupported
            )):
                print('Message contains unsupported media')
                continue

            if isinstance(message.media, (types.MessageMediaVenue, types.MessageMediaGeo,
                                          types.MessageMediaGeoLive)):
                print('geo:', message.geo.lat, message.geo.long)
                continue

            if isinstance(message.media, types.MessageMediaPhoto):
                print('photo:', message.photo.id)
                # print(message.photo.stringify())
                continue

            if isinstance(message.media, types.MessageMediaDocument):
                print(message.document.stringify())
                # check types.DocumentAttribute*
                continue

            if isinstance(message.media, types.MessageMediaWebPage) and\
                not isinstance(message.media.webpage, types.WebPageEmpty):
                print('webpage:', message.media.webpage.title, message.media.webpage.url,
                      '🖼' if message.media.webpage.photo else '')
                # if message.media.webpage.photo:
                    # print(client.download_media(message.media.webpage.photo))
                continue

            if isinstance(message.media, types.MessageMediaPoll):
                print(message.poll.poll.question, [a.text for a in message.poll.poll.answers])
                continue

        exit(0)

    if args.get('tg_id'):
        for message in client.iter_messages(client.get_entity(int(args.get('tg_id')))):
            if isinstance(message, types.MessageService):
                continue
            print('{:4d} {:3} {}'.format(
                message.id,
                len(message.entities) if message.entities is not None else '  *',
                repr(message.text)
            ))
            # print(message.entities, message.photo, message.document, message.sticker)
        exit(0)

    for dialog in client.get_dialogs():
        if not dialog.is_channel: # or dialog.is_group:
            continue

        print(dialog.entity.id, dialog.name)
finally:
    client.disconnect()
