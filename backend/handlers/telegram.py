from lib.config import config
from handlers.authorized import AuthorizedHandler

class TelegramHandler(AuthorizedHandler):
    audience = 'authorized'

    def _set_photo_path(self, item):
        if item.get('photo'):
            # self.logger.debug('Updating path of %s', item)
            item['photo'] = config.get('telegram', 'avatars_path') + '/' + item['photo']
            # self.logger.debug('Updated path of %s', item)
        return item
