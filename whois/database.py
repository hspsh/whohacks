import sqlite3

import peewee as pw
from datetime import datetime, timedelta

from flask_login import current_user, UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

db = pw.SqliteDatabase('whoisdevices.db')

class User(pw.Model, UserMixin):
    id = pw.PrimaryKeyField()
    username = pw.CharField(unique=True)
    password = pw.CharField()


    class Meta:
        database = db

    def __init__(self, id, login, display_name):
        pass

    @staticmethod
    def get_by_login(cursor, login):
        pass

    @staticmethod
    def register(cursor, login, display_name, password):
        pass

    def auth(self, cursor, pwd):
        pass

    def set_password(self, cursor, pwd):
        pass

    def get_id(self):
        pass

    def get_claimed_devices(self, cursor):
        pass



class Device(pw.Model):
    mac_address = pw.FixedCharField(primary_key=True, unique=True, max_length=17)
    hostname = pw.CharField()
    last_seen = pw.DateTimeField()
    owner = pw.ForeignKeyField(User, backref='devices')
    flags = pw.BitField()

    is_hidden = flags.flag(1)

    class Meta:
        database = db

    @staticmethod
    def get_by_mac(cursor, mac_addr):
        """Get device info"""
        pass

    @staticmethod
    def get_recent(cursor, hours=0, minutes=30, seconds=0):
        """Get recent devices, from last 30 min by default"""
        pass

    def claim(self, cursor, new_user_id):
        """Attach user id to given mac address"""
        pass

    def unclaim(self, cursor):
        """Attach user id to given mac address"""
        pass


def post_last_seen_devices(cursor, devices):
    """POST last seen devices to db, update last seen date if exists"""
    for dev in devices:
        assert type(dev[0]) is str
        assert len(dev[0]) == 17
        assert type(dev[1]) is datetime

    cursor.executemany('''INSERT INTO whois_devices (mac_addr, last_seen) VALUES (?,?) 
        ON DUPLICATE KEY UPDATE
        last_seen = VALUES(last_seen)''', devices)