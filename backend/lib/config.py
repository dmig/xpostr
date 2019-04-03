import logging
import os
from configparser import ConfigParser, NoOptionError, NoSectionError

__all__ = ['config', 'NoOptionError', 'NoSectionError']

config = None

if not config:
    config = ConfigParser()
    config.read((
        os.path.abspath(__file__ + '/../../config.ini'),
        os.path.abspath(__file__ + '/../../local.ini')
    ))

    logging.basicConfig(format='%(asctime)s %(levelname).1s %(name)s %(message)s')
    logging.captureWarnings(True)
    root = logging.getLogger()
    root.setLevel(
        logging.DEBUG if config.getboolean('globals', 'debug', fallback=False) else logging.INFO
    )
    if config.getboolean('globals', 'debug_requests', fallback=False):
        import http.client as http_client
        http_client.HTTPConnection.debuglevel = 1
        logger = logging.getLogger("requests.packages.urllib3")
        logger.setLevel(logging.DEBUG)
        logger.propagate = True

    logger = logging.getLogger("telethon")
    logger.setLevel(logging.DEBUG \
        if config.getboolean('globals', 'debug_telethon', fallback=False) else logging.INFO)
