#
# TG account handlers
#
import asyncio
import logging
import os
from glob import glob
from hashlib import md5
from typing import Union, List, Tuple
from telethon import TelegramClient
from telethon.tl import types
from lib.config import config
from lib.daemon.core import get_client, catch_task_exception, remove_tg_user

_logger = logging.getLogger(__name__)

async def handle_dump_message(vk_user_id: int, tg_channel_id: int, *message_ids):
    c = await get_client(vk_user_id)
    await c.get_dialogs()

    ret = [m.to_dict() if m else m async for m in c.iter_messages(
        await c.get_entity(int(tg_channel_id)),
        ids=list(map(int, message_ids))
    )]

    return ret

async def handle_get_sources(vk_user_id: int):
    client = await get_client(vk_user_id)

    ret = []
    photos: List[Tuple[asyncio.Task, dict]] = []
    async for dialog in client.iter_dialogs():
        if not dialog.is_channel or dialog.is_group:
            continue

        record = {
            'id': dialog.entity.id,
            'title': dialog.entity.title,
            'photo': None,
            'uri': dialog.entity.username
        }
        photos.append((asyncio.ensure_future(_get_photo(client, dialog.entity)), record))
        ret.append(record)

    await asyncio.wait([p[0] for p in photos])

    for p in photos:
        p[1]['photo'] = p[0].result()

    return ret

async def handle_get_tg_user(vk_user_id: int):
    client = await get_client(vk_user_id)
    if not await client.is_user_authorized():
        return {'authorized': False}

    me = await client.get_me()

    return {
        'authorized': True,
        'fullname': (me.first_name + ' ' + (me.last_name or '')).strip(),
        'username': me.username,
        'photo': await _get_photo(client, me)
    }

async def handle_is_tg_authorized(vk_user_id: int):
    client = await get_client(vk_user_id)
    return await client.is_user_authorized()


async def handle_remove_tg_user(vk_user_id: int):
    return await remove_tg_user(int(vk_user_id))

#region private funcs
async def _get_photo(client: TelegramClient, entity: Union[types.User, types.Channel, types.Chat]):
    if not entity.photo or isinstance(
            entity.photo, (types.UserProfilePhotoEmpty, types.ChatPhotoEmpty)):
        return None

    photo = entity.photo.photo_small\
        if isinstance(entity.photo, (types.ChatPhoto, types.UserProfilePhoto))\
        else entity.photo

    filename = '{0}.{1}.jpg'.format(
        entity.id,
        md5('{e.dc_id}.{e.volume_id}.{e.local_id}.{e.secret}'.format(e=photo).encode('utf-8'))
        .hexdigest()
    )
    filepath = os.path.join(config.get('paths', 'avatars'), filename)

    if not os.path.exists(filepath):
        # if file was updated, remove old one
        for f in glob(os.path.join(config.get('paths', 'avatars'), str(entity.id) + '*.jpg')):
            os.unlink(f)

        asyncio.ensure_future(
            client.download_profile_photo(entity, file=filepath, download_big=False)
        ).add_done_callback(catch_task_exception)

    return filename
#endregion
