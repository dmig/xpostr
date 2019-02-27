from handlers.authorized import AuthorizedHandler


class VKInfo(AuthorizedHandler):
    audience = 'authorized'

    def get(self):
        return {k:self.user[k] for k in ('id', 'fullname', 'photo')}
