#
# VK account handlers
#
import asyncio
import logging
import aiohttp
import ujson
from lib import db
from lib.daemon import context
from lib.daemon.core import remove_tg_user, set_phone_number

_logger = logging.getLogger(__name__)

def handle_get_vk_user(vk_user_id: int):
    vk_user_id = int(vk_user_id)
    acct = context.accounts.get(vk_user_id)

    if acct:
        return acct

    # inactive/unknown
    acct = context.accounts[vk_user_id] = dict(db.get_user(vk_user_id))
    return acct

def handle_set_vk_user(user):
    acct = context.accounts.get(int(user['id']))

    if acct:
        _logger.debug('VK user update: %s', user)
        acct.update(user)

    db.save_user(user)

    return True

def handle_remove_vk_user(vk_user_id):
    vk_user_id = int(vk_user_id)
    acct = context.accounts.get(vk_user_id)

    if not acct:
        _logger.info('User not found: %d', vk_user_id)
        return False

    asyncio.ensure_future(remove_tg_user(vk_user_id))\
        .add_done_callback(lambda res: res.result() and db.del_user(vk_user_id))

    return True

def handle_set_phone_number(vk_user_id, phone_number):
    return set_phone_number(int(vk_user_id), phone_number)

async def handle_get_targets(vk_user_id):
    vk_user_id = int(vk_user_id)
    acct = context.accounts.get(vk_user_id)

    if not acct or not acct['access_token']:
        _logger.warning('User not found or empty access_token: %d', vk_user_id)
        return []

    async with aiohttp.ClientSession(raise_for_status=True) as s:
        async with s.get(
                'https://api.vk.com/method/groups.get',
                params={
                    'v': '5.92',
                    'extended': 1,
                    'filter': 'groups,publics',
                    'fields': 'can_post',
                    'count': 1000,
                    'access_token': acct['access_token']
                }
        ) as r:
            r = await r.json(loads=ujson.loads)

    return [{
        'id': g['id'],
        'title': g['name'],
        'photo': g['photo_100'],
        'uri': g['screen_name']
    } for g in r.get('response', {}).get('items', []) if g['can_post']]
