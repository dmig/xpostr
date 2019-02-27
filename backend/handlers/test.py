from handlers.authorized import AuthorizedHandler

class Test(AuthorizedHandler):
    audience = 'authorized'

    def get(self):
        return '"passed"'
