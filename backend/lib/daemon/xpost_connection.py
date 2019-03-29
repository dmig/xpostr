from time import time
# pylint: disable=no-member,attribute-defined-outside-init

class Connection:
    __slots__ = 'tg_id', 'vk_id', 'last_update', 'last_status', 'active'

    def __init__(self, **kwargs):
        for k in self.__slots__:
            self.__setattr__(k, kwargs.get(k))

    def __eq__(self, other):
        return self.tg_id == other.tg_id and self.vk_id == other.vk_id

    def __repr__(self):
        return '{}({}, {}, {}, {}, {})'.format(
            self.__class__.__name__, self.tg_id, self.vk_id, self.active, self.last_update,
            self.last_status if not self.last_status or len(self.last_status) < 8\
                else self.last_status[:8] + '...'
        )

    def as_dict(self):
        return {k: getattr(self, k) for k in self.__slots__}

    def set_status(self, status):
        self.last_status = status
        self.last_update = int(time())
