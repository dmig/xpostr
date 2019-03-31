import os
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError,\
    PhoneNumberBannedError, PhoneNumberInvalidError,\
    PhoneCodeExpiredError, PhoneCodeInvalidError, PhoneCodeEmptyError, \
    PhonePasswordProtectedError, PhonePasswordFloodError, FloodWaitError, FloodError
from telethon.utils import parse_phone
from pycnic.errors import HTTP_400, HTTP_500, HTTPError
from lib import db
from lib.config import config
from lib.rpc_client import rpc_call
from handlers.telegram import TelegramHandler


class TGAuth(TelegramHandler):

    def get(self):
        return self._set_photo_path(rpc_call('get_tg_user', self.user['id']))

    def post(self):
        phone = parse_phone(self.request.data.get('phone'))

        if phone == self.user['phone_number']:
            return self.get()

        code = self.request.data.get('code')
        password = self.request.data.get('password')
        phone_code_hash = None

        if not phone:
            raise HTTP_400('Invalid `phone` value')

        msg = None
        try:
            client = TelegramClient(
                os.path.join(config.get('paths', 'sessions'), parse_phone(phone)),
                config.get('telegram', 'api_id'),
                config.get('telegram', 'api_hash')
            )
            if not client.is_connected():
                client.connect()

            # check if already authorized
            if client.is_user_authorized():
                return self._authorized(phone)

            # 2nd step
            if code:
                t = db.get_interim_state(phone)
                if not t:
                    raise HTTP_400('Invalid `phone` value')
                phone_code_hash = t['phone_code_hash']

            resp = client.sign_in(
                phone, code, password=password, phone_code_hash=phone_code_hash
            )

            # 2nd/3rd step success
            if code and client.is_user_authorized():
                return self._authorized(phone)

            # 1st step
            if not resp.phone_registered:
                db.del_interim_state(phone)
                raise HTTP_400('Phone number is not registered')

            db.set_interim_state(phone, {
                'provider': 'Telegram',
                'phone_code_hash': resp.phone_code_hash
            })
            return {
                'authorized': False,
                'code': True
            }
        # TODO handle potential sqlite connection timeout
        except SessionPasswordNeededError:
            return {
                'authorized': False,
                '2fa': True
            }
        except (PhoneNumberBannedError, PhoneNumberInvalidError,
                PhoneCodeExpiredError, PhoneCodeInvalidError, PhoneCodeEmptyError,
                PhonePasswordProtectedError, PhonePasswordFloodError, FloodWaitError,
                FloodError) as e:
            db.del_interim_state(phone)
            raise HTTP_400(str(e))
        except HTTPError: # passthru
            raise
        except Exception as e:
            self.logger.error('Telegram communication error %s', e)
            msg = str(e)
            raise
        finally:
            client.disconnect()

        raise HTTP_500('Internal error', msg)

    def delete(self):
        if self.user['phone_number']:
            rpc_call('remove_tg_user', self.user['id'])

        self.response.status_code = 204
        return ''


    def _authorized(self, phone):
        db.del_interim_state(phone)
        rpc_call('set_phone_number', self.user['id'], phone)
        return self.get()
