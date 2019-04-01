import logging
import os
try:
    import ujson as json
except ImportError:
    import json
from time import time
import sqlite3
from lib.config import config

_logger = logging.getLogger(__name__)
__connections = {}
__tables = {
    'auth': [
        """auth_interim (
            state varchar(256) not null,
            expire int unsigned not null,
            data text not null,
            primary key (state)
        )""",
    ],
    'main': [
        """vk_users (
            id int unsigned not null,
            fullname varchar(256) not null,
            photo varchar(256),
            phone_number varchar(32),
            access_token varchar(256) not null,
            primary key (id)
        )"""
        """group_connections (
            user_id int unsigned not null,
            tg_id int unsigned not null,
            vk_id int unsigned not null,
            active tinyint not null default 1,
            last_status varchar(256),
            last_update int unsigned,
            primary key (user_id, tg_id, vk_id)
        )"""
    ]
}

def connect(db, ro=False):
    global __connections

    k = db + 'R' if ro else 'W'
    if k in __connections:
        return __connections[k]

    if ro and db + 'W' in __connections:
        return __connections[db + 'W']

    _logger.debug('Creating connection: %s', db)

    __connections[k] = sqlite3.connect(
        'file:' + os.path.abspath(
            config.get('paths', 'db_' + db, fallback='./main')
        ) + ('?mode=ro' if ro else ''),
        check_same_thread=False, uri=True
    )
    __connections[k].row_factory = sqlite3.Row

    cursor = __connections[k].cursor()
    cursor.execute("select count(*) from sqlite_master where type='table'")
    cnt = cursor.fetchone()[0]
    if not cnt:
        if ro:
            raise Exception(f'DB {db} not ready')

        for d in __tables[db]:
            cursor.execute('create table {}'.format(d))
        cursor.connection.commit()
    cursor.close()

    return __connections[k]


def get_cursor(db='main', ro=False) -> sqlite3.Cursor:
    conn = connect(db, ro)
    return conn.cursor()


def get_interim_state(state):
    cursor = get_cursor('auth')

    cursor.execute(
        "SELECT data FROM auth_interim WHERE state = ? AND expire > ?",
        (state, int(time()))
    )

    res = cursor.fetchone()
    cursor.close()

    return json.loads(res[0]) if res else None

def set_interim_state(state, data, timeout=None):
    cursor = get_cursor('auth')

    cursor.execute(
        "SELECT data FROM auth_interim WHERE state = ? AND expire > ?",
        (state, int(time()))
    )
    old_data = cursor.fetchone()
    old_data = json.loads(old_data[0]) if old_data else {}

    old_data.update(data)

    exp = int(time()) + (timeout or config.getint('oauth', 'state_timeout', fallback=20))
    cursor.execute(
        'INSERT OR REPLACE INTO auth_interim VALUES (?, ?, ?)',
        (state, exp, json.dumps(old_data))
    )

    cursor.connection.commit()
    cursor.close()

def del_interim_state(state):
    cursor = get_cursor('auth')
    cursor.execute('DELETE FROM auth_interim WHERE state = ? OR expire <= ?', (state, int(time())))
    cursor.connection.commit()
    cursor.close()


def get_user(user_id):
    cursor = get_cursor()

    cursor.execute(
        'SELECT id, fullname, photo, phone_number, access_token FROM vk_users WHERE id = ?',
        (user_id, )
    )

    res = cursor.fetchone()
    cursor.close()

    return res

def save_user(user):
    cursor = get_cursor()

    cursor.execute(
        'INSERT INTO vk_users (id, fullname, photo, access_token) '
        'VALUES (:id, :fullname, :photo, :access_token) '
        'ON CONFLICT(id) DO UPDATE '
        'SET fullname=excluded.fullname, photo=excluded.photo, access_token=excluded.access_token',
        user
    )

    cursor.connection.commit()
    cursor.close()

def del_user(user_id):
    cursor = get_cursor()

    cursor.execute('DELETE FROM group_connections WHERE user_id = ?', (user_id, ))
    cursor.execute('DELETE FROM vk_users WHERE id = ?', (user_id, ))

    cursor.connection.commit()
    cursor.close()

def set_phone_number(user_id, phone_number):
    cursor = get_cursor()

    cursor.execute(
        'UPDATE vk_users SET phone_number=? WHERE id=?',
        (phone_number, user_id)
    )

    cursor.connection.commit()
    cursor.close()


def get_group_connections(user_id):
    cursor = get_cursor()

    cursor.execute(
        'SELECT vk_id, tg_id, active, last_status, last_update '
        'FROM group_connections WHERE user_id = ?',
        (user_id, )
    )

    res = cursor.fetchall()
    cursor.close()

    return res

def get_group_connection(user_id, vk_id, tg_id):
    cursor = get_cursor()

    cursor.execute(
        'SELECT vk_id, tg_id, active, last_status, last_update '
        'FROM group_connections '
        'WHERE user_id = ? AND tg_id = ? AND vk_id = ?',
        (user_id, tg_id, vk_id)
    )

    res = cursor.fetchone()
    cursor.close()

    return res

def set_group_connection(user_id, vk_id, tg_id, active=True):
    cursor = get_cursor()

    cursor.execute(
        'INSERT INTO group_connections (user_id, vk_id, tg_id, active) VALUES (?, ?, ?, ?) '
        'ON CONFLICT(user_id, vk_id, tg_id) DO UPDATE SET active=excluded.active',
        (user_id, vk_id, tg_id, int(active))
    )

    cursor.connection.commit()
    cursor.close()

def set_group_connection_status(user_id, vk_id, tg_id, status):
    cursor = get_cursor()

    cursor.execute(
        'UPDATE group_connections SET last_status=?, last_update=? '
        'WHERE user_id=? AND vk_id=? AND tg_id=?',
        (status, int(time()), user_id, vk_id, tg_id)
    )

    cursor.connection.commit()
    cursor.close()

def del_group_connection(user_id, vk_id, tg_id):
    cursor = get_cursor()

    cursor.execute(
        'DELETE FROM group_connections WHERE user_id = ? AND vk_id = ? AND tg_id = ?',
        (user_id, vk_id, tg_id)
    )

    cursor.connection.commit()
    cursor.close()
