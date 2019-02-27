from lib.pycnic.errors import HTTP_401, HTTP_403, HTTP_500
import lib.jwt_auth as auth
from lib import db
from handlers.logger import LoggerHandler


class AuthorizedHandler(LoggerHandler):
    # must be overriden in ancestor
    audience = 'none'
    user = None

    def __init__(self):
        super().__init__()
        if isinstance(self.audience, str):
            self.audience = [self.audience]

    def before(self):
        if self.request.method == 'OPTIONS':
            return

        user = None
        token = self._parse_auth_header()
        if token:
            try:
                payload = auth.decode_token(token, self.audience)
                user_id = payload.get('id')
                user = db.get_user(user_id)

                if not user:
                    raise HTTP_403("Access denied")
            except auth.DecodeError as e:
                self.logger.warning(e)
                raise HTTP_401("Unable to parse authentication token")
            except auth.ExpiredSignatureError:
                if 'guest' not in self.audience:
                    raise HTTP_401("Expired token")
            except auth.InvalidAudienceError:
                raise HTTP_403("Incorrect claims")
            except Exception as e:
                self.logger.exception(e)
                raise HTTP_500("Unable to parse authentication token")
        elif 'guest' not in self.audience:
            raise HTTP_403("Access denied")

        self.user = user or {}

    def _parse_auth_header(self):
        """Obtains the access token from the Authorization Header
        """
        header = self.request.get_header("Authorization")
        # skip 'Bearer ' prefix
        return header[7:] if header else None

    def _load_user_roles(self):
        return ['guest', 'authorized']
