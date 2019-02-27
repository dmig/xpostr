import os
from hashlib import md5
from glob import glob
from telethon import TelegramClient, events, sync # pylint: disable=unused-import
from telethon.utils import parse_phone
from telethon.tl import types
from lib.pycnic.errors import HTTPNumeric
from lib.config import config
from handlers.authorized import AuthorizedHandler

class HTTP_424(HTTPNumeric):
    status_code = 424

class TelegramHandler(AuthorizedHandler):
    audience = 'authorized'

    def _get_client(self, phone_number=None):
        if not phone_number:
            phone_number = self.user['phone_number']

        if not phone_number:
            return None

        return TelegramClient(
            os.path.join(config.get('paths', 'sessions'), parse_phone(phone_number)),
            config.get('telegram', 'api_id'),
            config.get('telegram', 'api_hash')
        )

    def _get_photo(self, client, user):
        if not user.photo or isinstance(
                user.photo, (types.UserProfilePhotoEmpty, types.ChatPhotoEmpty)):
            return None

        photo = user.photo.photo_small if isinstance(user.photo, types.ChatPhoto) else user.photo

        # self.logger.info(
        #     'Photo: %d dc_id=%d, vol_id=%d, local_id=%d, secret=%d',
        #     user.id, photo.dc_id, photo.volume_id, photo.local_id, photo.secret
        # )

        filename = '{0}.{1}.jpg'.format(
            user.id,
            md5('{e.dc_id}.{e.volume_id}.{e.local_id}.{e.secret}'.format(e=photo).encode('utf-8'))
            .hexdigest()
        )
        filepath = os.path.join(config.get('paths', 'avatars'), filename)

        if not os.path.exists(filepath):
            # if file was updated, remove old one
            for f in glob(os.path.join(config.get('paths', 'avatars'), str(user.id) + '*.jpg')):
                os.unlink(f)

            client.download_profile_photo(user, file=filepath, download_big=False)

        return filename

    def _get_info(self, client):
        me = client.get_me()

        return {
            'authorized': True,
            'fullname': (me.first_name + ' ' + (me.last_name or '')).strip(),
            'username': me.username,
            'photo': self._get_photo(client, me)
        }
