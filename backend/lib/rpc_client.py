import logging
import asyncio
import uvloop
from aiorpc import RPCClient
from lib.config import config
from lib.daemon.handlers import pack_params, unpack_params

logger = logging.getLogger(__name__)

def rpc_call(method, *args, timeout=3):
    """
    Dumb sync RPC client wrapper
    """
    server_socket = config.get('paths', 'daemon_socket')

    loop = uvloop.new_event_loop()
    asyncio.set_event_loop(loop)
    logger.debug('Calling: %s', server_socket)

    client = RPCClient(path=server_socket, timeout=timeout,
                       pack_params=pack_params, unpack_params=unpack_params)
    result = loop.run_until_complete(client.call_once(method, *args))

    logger.debug('Done: %r', result)
    return result
