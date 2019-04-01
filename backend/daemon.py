#! /usr/bin/env python3

import asyncio
import logging
import os
import uvloop
from aiorpc import serve
from lib.config import config
from lib.daemon import core, handlers

logger = logging.getLogger('xpostr-daemon')

if __name__ == "__main__":
    loop = uvloop.new_event_loop()
    assert loop is not None
    asyncio.set_event_loop(loop)

    # preload data from DB
    # ... and create Telegram clients
    core.init(loop)
    handlers.init()

    server_socket = config.get('paths', 'daemon_socket')
    # Each client connection will create a new protocol instance
    coro = asyncio.start_unix_server(serve, path=server_socket)
    server = loop.run_until_complete(coro)

    # Serve requests until Ctrl+C is pressed
    logger.info('Listening on %s', server.sockets[0].getsockname())
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        logger.info('Got interrupt, shutting down')
    finally:
        # Close the server
        server.close()
        loop.run_until_complete(server.wait_closed())
        core.shutdown()
        # BUG have to wait until Telethon disconnects
        loop.run_until_complete(asyncio.wait(asyncio.Task.all_tasks(loop)))
        loop.close()
        if os.path.exists(server_socket):
            os.unlink(server_socket)
    logger.info('Done')
