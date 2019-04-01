#
# TG -> VK connection handlers
#
import asyncio
import logging
from lib import db
from lib.daemon.xpost_connection import Connection
from lib.daemon import context
from lib.daemon.core import get_connection, add_connection, remove_connection

_logger = logging.getLogger(__name__)

async def handle_get_user_connections(vk_user_id: int):
    vk_user_id = int(vk_user_id)
    lst = context.connections.get(vk_user_id)

    if lst is None:
        lst = context.connections[vk_user_id] = []
        conns = []
        for c in db.get_group_connections(vk_user_id):
            conn = Connection(**c)
            if c['active']:
                conns.append(add_connection(vk_user_id, conn))

        await asyncio.wait(conns)

    return lst

async def handle_set_connection(vk_user_id: int, vk_group_id: int, tg_channel_id: int, active=True):
    vk_user_id = int(vk_user_id)
    vk_group_id = int(vk_group_id)
    tg_channel_id = int(tg_channel_id)
    conn = get_connection(vk_user_id, vk_group_id, tg_channel_id, True)

    if conn.active == active:
        _logger.warning('Duplicate connection: %s', conn)
        return True

    conn.active = active # pylint: disable=attribute-defined-outside-init

    if active:
        await add_connection(vk_user_id, conn)
        _logger.debug('Added connection %s', conn)
    else:
        remove_connection(vk_user_id, conn)
        _logger.debug('Changed connection %s', conn)

    db.set_group_connection(vk_user_id, vk_group_id, tg_channel_id, active)

    return True

def handle_remove_connection(vk_user_id: int, vk_group_id: int, tg_channel_id: int):
    vk_user_id = int(vk_user_id)
    vk_group_id = int(vk_group_id)
    tg_channel_id = int(tg_channel_id)
    conn = Connection(vk_id=vk_group_id, tg_id=tg_channel_id)

    if conn not in context.connections.get(vk_user_id, []):
        _logger.warning('Connection not found: %s', conn)
        return False

    remove_connection(vk_user_id, conn)

    _logger.debug('Removed connection %s', conn)

    db.del_group_connection(vk_user_id, vk_group_id, tg_channel_id)

    return True
