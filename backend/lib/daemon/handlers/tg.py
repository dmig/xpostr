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
from lib import db
from lib.config import config
from lib.daemon import context
from lib.daemon.core import get_client, logout_client, remove_connection, catch_task_exception

_logger = logging.getLogger(__name__)

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
        if catch_task_exception(p[0]):
            continue

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

async def handle_remove_tg_user(vk_user_id: int):
    vk_user_id = int(vk_user_id)
    client: TelegramClient = context.clients.get(vk_user_id)
    if not client:
        return False

    for conn in context.connections.get(vk_user_id, []):
        remove_connection(vk_user_id, conn)
        db.del_group_connection(vk_user_id, conn.vk_id, conn.tg_id)

    await logout_client(vk_user_id)
    db.set_phone_number(vk_user_id, None)
    return True

#region private funcs
async def _get_photo(client: TelegramClient, entity: Union[types.User, types.Channel, types.Chat]):
    if not entity.photo or isinstance(
            entity.photo, (types.UserProfilePhotoEmpty, types.ChatPhotoEmpty)):
        return None

    photo = entity.photo.photo_small if isinstance(entity.photo, types.ChatPhoto) else entity.photo

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
        try:
            await client.download_profile_photo(entity, file=filepath, download_big=False)
        except Exception as e:
            _logger.exception('Photo download exception: %r', e)
            filename = None

    return filename
#endregion
