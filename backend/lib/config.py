import logging
import os
from configparser import ConfigParser, NoOptionError, NoSectionError
import http.client as http_client

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
        http_client.HTTPConnection.debuglevel = 1
        requests_log = logging.getLogger("requests.packages.urllib3")
        requests_log.setLevel(logging.DEBUG)
        requests_log.propagate = True
