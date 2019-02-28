from os.path import join
from lib.config import config
from lib.pycnic.errors import HTTP_500, HTTPError
from handlers.telegram import TelegramHandler, HTTP_424

class TGChannels(TelegramHandler):
    def get(self):
        client = self._get_client()
        if not client:
            raise HTTP_424('Not authorized in telegram')

        msg = None
        try:
            client.connect()

            if not client.is_user_authorized():
                raise HTTP_424('Not authorized in telegram')

            ret = []
            for dialog in client.get_dialogs():
                if not dialog.is_channel or dialog.is_group:
                    continue

                photo = self._get_photo(client, dialog.entity)
                ret.append({
                    'id': dialog.entity.id,
                    'title': dialog.entity.title,
                    'photo': photo and join(config.get('telegram', 'avatars_path'), photo),
                    'uri': dialog.entity.username
                })

            return ret
        except HTTPError: # passthru
            raise
        except Exception as e:
            self.logger.error('Telegram communication error %s', e)
            msg = str(e)
        finally:
            client.disconnect()

        raise HTTP_500('Internal error', msg)
