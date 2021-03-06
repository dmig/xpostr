import asyncio
import functools
import logging
import os
from time import time
from typing import Awaitable
from telethon.utils import parse_phone
from telethon import TelegramClient, events, types
from lib import db, xpost, errors
from lib.config import config
from lib.daemon import context
from lib.daemon.xpost_connection import Connection

_logger = logging.getLogger(__name__)

async def add_connection(vk_user_id: int, conn: Connection):
    client: TelegramClient = await get_client(vk_user_id)

    handler = context.event_handlers[(vk_user_id, conn.vk_id)] = \
        functools.partial(repost_message, vk_user_id, conn.vk_id)

    client.add_event_handler(
        handler, events.NewMessage(chats=(conn.tg_id,))
    )
    context.connections.setdefault(vk_user_id, []).append(conn)

def remove_connection(vk_user_id, connection):
    client: TelegramClient = context.clients.get(vk_user_id)
    if client:
        handler = context.event_handlers.get((vk_user_id, connection.vk_id))
        if not handler:
            _logger.error('Missing event handler: %d, %d', vk_user_id, connection.vk_id)
            return

        client.remove_event_handler(
            handler, events.NewMessage(chats=(connection.tg_id,))
        )
    else:
        _logger.warning('Client not available')

    context.connections[vk_user_id].remove(connection)

    if not context.connections[vk_user_id]:
        remove_client(vk_user_id)

def get_connection(vk_user_id: int, vk_group_id: int, tg_channel_id: int, load=False) -> Connection:
    vk_user_id = int(vk_user_id)
    vk_group_id = int(vk_group_id)
    tg_channel_id = int(tg_channel_id)
    conn = Connection(vk_id=vk_group_id, tg_id=tg_channel_id)

    try:
        lst = context.connections.get(vk_user_id, [])
        i = lst.index(conn)
        return lst[i]
    except ValueError:
        if load:
            cn = db.get_group_connection(vk_user_id, vk_group_id, tg_channel_id)
            if cn:
                _logger.debug(
                    'Loaded connection from db: %d, %d, %d', vk_user_id, vk_group_id, tg_channel_id
                )
                return Connection(**cn)
        return conn

def set_connection_status(vk_user_id: int, vk_group_id: int, tg_channel_id: int, status):
    conn = get_connection(vk_user_id, vk_group_id, tg_channel_id)

    conn.last_status = status # pylint: disable=attribute-defined-outside-init
    conn.last_update = time() # pylint: disable=attribute-defined-outside-init

    _logger.debug('Set connection status %s', conn)

    db.set_group_connection_status(vk_user_id, vk_group_id, tg_channel_id, status)


async def get_client(vk_user_id: int, event_loop=None) -> Awaitable[TelegramClient]:
    vk_user_id = int(vk_user_id)
    client: TelegramClient = context.clients.get(vk_user_id)
    if client:
        return client

    phone_number = context.accounts.get(vk_user_id, {}).get('phone_number')
    if not phone_number:
        _logger.debug('User id: %r, Accounts: %s', vk_user_id, context.accounts)
        raise errors.UnknownUser('Unknown vk_user_id or empty phone_number')

    if event_loop is None:
        event_loop = asyncio.get_event_loop()

    _logger.debug('Creating client for VK user %d', vk_user_id)
    context.clients[vk_user_id] = client = TelegramClient(
        os.path.join(config.get('paths', 'sessions'), parse_phone(phone_number)),
        config.get('telegram', 'api_id'),
        config.get('telegram', 'api_hash'),
        loop=event_loop
    )

    try:
        await client.connect()
        if not await client.is_user_authorized():
            raise errors.UnauthorizedException(
                f'VK user_id {vk_user_id} is not authorized in Telegram'
            )

        return client
    except:
        await client.disconnect()
        raise

def remove_client(vk_user_id: int):
    client: TelegramClient = context.clients.get(vk_user_id)
    if not client:
        return

    _logger.debug('Disconnecting Telegram client for %d', vk_user_id)
    # BUG client.disconnect() returns None on shutdown
    asyncio.ensure_future(client._disconnect_coro())

    del context.clients[vk_user_id]

async def logout_client(vk_user_id: int):
    client: TelegramClient = context.clients.get(vk_user_id)
    if not client:
        return

    if not await client.is_user_authorized():
        return

    await client.log_out()
    remove_client(vk_user_id)


def set_phone_number(vk_user_id: int, phone_number):
    acct = context.accounts.get(vk_user_id)

    if not acct:
        _logger.warning('User not found: %d', vk_user_id)
        return False

    acct['phone_number'] = phone_number

    db.set_phone_number(vk_user_id, phone_number)
    return True


async def remove_tg_user(vk_user_id: int):
    client: TelegramClient = context.clients.get(vk_user_id)
    if not client:
        return False

    for conn in context.connections.get(vk_user_id, []):
        remove_connection(vk_user_id, conn)
        db.del_group_connection(vk_user_id, conn.vk_id, conn.tg_id)

    await logout_client(vk_user_id)
    set_phone_number(vk_user_id, None)
    return True


def catch_task_exception(task: asyncio.Task):
    exc = task.exception()
    if not exc:
        return False
    _logger.exception('Task exception: %r', exc, stack_info=task.get_stack())
    return True

async def repost_message(vk_user_id: int, vk_group_id: int, event):
    access_token = context.accounts.get(vk_user_id, {}).get('access_token')
    if not access_token:
        _logger.error('Can\'t repost: %d `access_token` is missing', vk_user_id)
        return

    msg = event if not event or isinstance(event, types.Message) else event.message
    if msg is None:
        _logger.warning('Message not available for %d %d', vk_user_id, vk_group_id)
        return

    try:
        xposter = xpost.WallPost(access_token, vk_group_id, msg)
        m_id = await xposter.upload()
        status = f'success: https://vk.com/wall-{vk_group_id}_{m_id}'
    except Exception as e:
        _logger.exception('Repost failed: %d/%d', msg.to_id.channel_id, msg.id)
        status = str(e)

    await event.client.send_read_acknowledge(msg.to_id, message=msg)
    set_connection_status(vk_user_id, vk_group_id, msg.to_id.channel_id, status)


#region init and shutdown
def init(event_loop: asyncio.AbstractEventLoop):
    cursor = db.get_cursor()

    cursor.execute(
        'SELECT id, fullname, photo, phone_number, access_token FROM vk_users '
        'WHERE phone_number IS NOT NULL AND phone_number != ""'
        'AND access_token IS NOT NULL AND access_token != ""'
    )
    for acc in cursor.fetchall():
        _logger.debug('Creating account for VK user %d', acc['id'])
        context.accounts[acc['id']] = {f:acc[f] for f in acc.keys()}

    cursor.execute(
        'SELECT user_id vk_user_id, tg_id, active, vk_id, last_update, last_status '
        'FROM group_connections gc '
        'JOIN vk_users vu ON gc.user_id=vu.id '
        'WHERE vu.phone_number IS NOT NULL AND vu.phone_number != "" '
        'AND vu.access_token IS NOT NULL AND vu.access_token != ""'
    )

    clients = []
    conns = []
    for conn in cursor.fetchall():
        clients.append(asyncio.ensure_future(
            get_client(conn['vk_user_id'], event_loop), loop=event_loop
        ))
        if conn['active']:
            _logger.debug('Creating connection: %d -> %d ', conn['tg_id'], conn['vk_id'])
            conns.append(asyncio.ensure_future(
                add_connection(conn['vk_user_id'], Connection(**conn)), loop=event_loop
            ))

    cursor.close()

    if not clients:
        return

    # make sure to initialize clients first, because we're outside of event_loop
    event_loop.run_until_complete(asyncio.wait(clients, loop=event_loop))

    exc = False
    for cl in clients:
        if catch_task_exception(cl):
            ex = cl.exception()
            if isinstance(ex, errors.UnauthorizedException):
                _logger.warning(str(ex))
            else:
                exc |= True

    if exc:
        raise errors.StartupException('Failed to initalize clients')

    # precache dialogs, not to get ValueError when calling get_entity
    dialogs = []
    for cl in context.clients.values():
        dialogs.append(asyncio.ensure_future(cl.get_dialogs(), loop=event_loop))

    event_loop.run_until_complete(asyncio.wait(dialogs, loop=event_loop))

    if conns:
        event_loop.run_until_complete(asyncio.wait(conns, loop=event_loop))

    exc = False
    for c in conns:
        exc |= catch_task_exception(c)

    if exc:
        raise errors.StartupException('Failed to initalize connections')

    if config.getboolean('telegram', 'catch_up', fallback=True):
        event_loop.run_until_complete(asyncio.wait([
            client.catch_up() for client in context.clients.values()
        ], loop=event_loop))

def shutdown():
    _logger.debug(
        'Shutting down %d clients and %d connections',
        len(context.clients), len(context.connections)
    )
    for vk_user_id in context.connections:
        while context.connections[vk_user_id]:
            # shift() imitation
            conn = context.connections[vk_user_id][0]
            remove_connection(vk_user_id, conn)
#endregion
