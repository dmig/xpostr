import logging
from lib.pycnic.core import Handler

class LoggerHandler(Handler):
    logger = None

    def __init__(self):
        if not self.logger:
            self.logger = logging.getLogger(
                '%s.%s' % (self.__class__.__module__, self.__class__.__name__)
            )
