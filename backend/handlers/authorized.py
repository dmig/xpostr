from lib.pycnic.errors import HTTP_401, HTTP_403, HTTP_500
from lib.rpc_client import rpc_call
from lib import jwt_auth
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
                payload = jwt_auth.decode_token(token, self.audience)
                user_id = payload.get('id')

                user = rpc_call('get_vk_user', user_id)

                if not user:
                    raise HTTP_403("Access denied")
            except jwt_auth.DecodeError as e:
                self.logger.warning(e)
                raise HTTP_401("Unable to parse authentication token")
            except jwt_auth.ExpiredSignatureError:
                if 'guest' not in self.audience:
                    raise HTTP_401("Expired token")
            except jwt_auth.InvalidAudienceError:
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
