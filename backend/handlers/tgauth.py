from telethon.errors import SessionPasswordNeededError,\
    PhoneNumberBannedError, PhoneNumberInvalidError,\
    PhoneCodeExpiredError, PhoneCodeInvalidError, PhoneCodeEmptyError, \
    PhonePasswordProtectedError, PhonePasswordFloodError, FloodWaitError, FloodError
from telethon.utils import parse_phone
from lib.pycnic.errors import HTTP_400, HTTP_500, HTTPError
from lib import db
from handlers.telegram import TelegramHandler


class TGAuth(TelegramHandler):
    def get(self):
        client = self._get_client()

        if not client:
            return {'authorized': False}

        msg = None
        try:
            client.connect()

            if client.is_user_authorized():
                return self._get_info(client)
        except Exception as e:
            self.logger.error('Telegram communication error %s', e)
            msg = str(e)
        finally:
            client.disconnect()

        raise HTTP_500('Internal error', msg)

    def post(self):
        phone = parse_phone(self.request.data.get('phone'))
        code = self.request.data.get('code')
        password = self.request.data.get('password')
        phone_code_hash = None

        if not phone:
            raise HTTP_400('Invalid `phone` value')

        msg = None
        client = self._get_client(phone)
        try:
            if not client.is_connected():
                client.connect()

            # check if already authorized
            if client.is_user_authorized():
                return self._authorized(client, phone)

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
                return self._authorized(client, phone)

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
            client = self._get_client()
            client.connect()
            if client.log_out():
                db.set_phone_number(self.user['id'], None)

        self.response.status_code = 204
        return ''

    def _authorized(self, client, phone):
        db.del_interim_state(phone)
        db.set_phone_number(self.user['id'], phone)
        return self._get_info(client)
