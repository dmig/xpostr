class VKException(Exception):
    def __init__(self, error):
        self.message = error.get('error_msg', error.get('error_description'))
        self.code = error.get('error_code', error.get('error'))
        self.extra = error.get('request_params', error.get('error_reason'))
        super().__init__(self.message, self.code, self.extra)

# pylint: disable=multiple-statements
class XPostrException(Exception): pass
class MissingParam(Exception): pass
class AuthorizedSuccessfully(XPostrException): pass
class UnknownUser(XPostrException): pass
class UnauthorizedException(XPostrException): pass
class StartupException(XPostrException): pass
