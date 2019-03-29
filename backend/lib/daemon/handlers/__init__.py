from aiorpc import register, msgpack_init
from lib.daemon.xpost_connection import Connection
from . import common
from . import connections
from . import tg
from . import vk

def _pack_connection(obj):
    if isinstance(obj, Connection):
        return obj.as_dict() # {'__connection__': True, 'data': obj.as_dict()}

    return obj

def _unpack_connection(obj):
    if '__connection__' in obj:
        return Connection(**obj['data'])

    return obj

pack_params = {'default': _pack_connection}
unpack_params = {'use_list': False} # 'object_hook': _unpack_connection,

def init():
    for m in (common, connections, tg, vk):
        for fn in m.__dict__:
            if not hasattr(m.__dict__[fn], "__call__") or not fn.startswith('handle_'):
                continue

            register(fn[7:], m.__dict__[fn])

    msgpack_init(pack_params=pack_params, unpack_params=unpack_params)

__all__ = ['pack_params', 'unpack_params', 'init']
