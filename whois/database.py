import sqlite3
from datetime import datetime, timedelta

from flask_login import current_user, UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

db = sqlite3.connect('whosdevices.db')


class Device():
    def __init__(self, mac_addr, last_seen, user_id=None):
        assert len(mac_addr) == 17
        self.mac_addr = mac_addr
        self.host_name = None
        self.last_seen = last_seen
        self.user_id = user_id
        self.user_display = None

    def __str__(self):
        return '[{}]'.format(self.mac_addr)

    @staticmethod
    def get_by_mac(cursor, mac_addr):
        """Get device info"""
        cursor.execute(
            'SELECT mac_addr, last_seen, user_id FROM whois_devices WHERE mac_addr=?',
            (mac_addr,))
        try:
            return Device(*cursor.fetchone())
        except TypeError:
            return None

    @staticmethod
    def get_recent(cursor, hours=0, minutes=30, seconds=0):
        """Get recent devices, from last 30 min by default"""
        min_dt = datetime.now() - timedelta(hours=hours, minutes=minutes,
                                            seconds=seconds)

        cursor.execute(
            "SELECT mac_addr, last_seen, user_id FROM whois_devices WHERE last_seen BETWEEN ? AND DATETIME('NOW')",
            (min_dt,))

        return [Device(*row) for row in cursor]

    def claim(self, cursor, new_user_id):
        """Attach user id to given mac address"""
        if self.user_id is None:
            self.user_id = new_user_id
            print(self.owner)
            cursor.execute(
                'UPDATE whois_devices SET user_id=? WHERE mac_addr=?',
                (self.user_id, self.mac_addr))

    def unclaim(self, cursor):
        """Attach user id to given mac address"""
        print('trying to unclaim', current_user.get_id(), self.user_id)
        if (self.user_id == int(current_user.get_id())):
            self.user_id = None
            cursor.execute(
                'UPDATE whois_devices SET user_id=NULL WHERE mac_addr=?',
                (self.mac_addr,))
        else:
            print('failed')

    @property
    def owner(self):
        return self.user_id


class User(UserMixin):
    """docstring for User"""

    def __init__(self, id, login, display_name):
        self.id = id
        self.login = login
        self.display_name = display_name
        self.tags = []

    def __str__(self):
        if 'hidden' in self.tags:
            return None
        elif 'anonymous' in self.tags:
            return 'Anonymous'
        elif self.display_name is not None:
            return self.display_name
        else:
            return self.login

    @staticmethod
    def get_by_id(cursor, user_id):
        cursor.execute(
            'SELECT id, login, display_name FROM whois_users WHERE id=?',
            (user_id,))
        try:
            return User(*cursor.fetchone())
        except TypeError:
            return None

    @staticmethod
    def get_by_login(cursor, login):
        cursor.execute(
            'SELECT id, login, display_name FROM whois_users WHERE login=?',
            (login,))
        try:
            return User(*cursor.fetchone())
        except TypeError:
            return None

    @staticmethod
    def register(cursor, login, display_name, password):
        cursor.execute(
            "INSERT INTO whois_users (login, display_name, password, registered_at, last_login) VALUES (?,?,?,DATETIME('NOW'),DATETIME('NOW'))",
            (login, display_name, password))

    def auth(self, cursor, pwd):
        cursor.execute('SELECT password FROM whois_users WHERE login=?',
                       (self.login,))
        hash = cursor.fetchone()[0]
        if check_password_hash(hash, pwd):
            return True
        else:
            return False

    def set_password(self, cursor, pwd):
        cursor.execute('UPDATE whois_users SET password=? WHERE id=?',
                       (generate_password_hash(pwd), self.id))

    def get_id(self):
        return str(self.id)

    def get_claimed_devices(self, cursor):
        cursor.execute(
            'SELECT mac_addr, last_seen, user_id FROM whois_devices WHERE user_id=?',
            (self.id,))
        return [Device(*row) for row in cursor.fetchall()]