from datetime import datetime, timedelta

import peewee as pw
from werkzeug.security import check_password_hash, generate_password_hash

db = pw.SqliteDatabase('whoisdevices.db')


class User(pw.Model):
    id = pw.PrimaryKeyField()
    username = pw.CharField(unique=True)
    _password = pw.CharField(column_name='password')
    display_name = pw.CharField()
    flags = pw.BitField(null=True)

    is_hidden = flags.flag(1)
    is_name_anonymous = flags.flag(2)


    class Meta:
        database = db

    @classmethod
    def register(cls, username, password, display_name=None):
        """
        Creates user and hashes his password
        :param username: used in login
        :param password: plain text to be hashed
        :param display_name: displayed username
        :return: user instance
        """
        # TODO: ehh
        user = cls.create(username=username, _password='todo', display_name=display_name)
        user.password = password
        return user

    def __str__(self):
        if self.is_name_anonymous or self.is_hidden:
            return 'anonymous'
        else:
            return self.display_name

    @property
    def is_active(self):
        return self.username is not None

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        """
        Needed by flask login
        :return:
        """
        return False

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, new_password):
        self._password = generate_password_hash(new_password)

    def auth(self, password):
        return check_password_hash(self.password, password)


class Device(pw.Model):
    mac_address = pw.FixedCharField(primary_key=True, unique=True,
                                    max_length=17)
    hostname = pw.CharField(null=True)
    last_seen = pw.DateTimeField()
    owner = pw.ForeignKeyField(User, backref='devices',
                               column_name='user_id', null=True)
    flags = pw.BitField(null=True)

    is_hidden = flags.flag(1)
    is_new = flags.flag(2)
    is_infrastructure = flags.flag(4)
    is_esp = flags.flag(8)

    class Meta:
        database = db

    @classmethod
    def get_recent(cls, hours=0, minutes=30, seconds=0):
        """
        Returns list of last connected devices
        :param hours:
        :param minutes:
        :param seconds:
        :return: list of devices
        """
        recent_time = datetime.now() - timedelta(hours=hours, minutes=minutes,
                                                 seconds=seconds)
        devices = list(
            cls.select().where(cls.last_seen > recent_time).order_by(
                cls.last_seen))
        return devices

    @classmethod
    def update_or_create(cls, mac_address, last_seen, hostname=None):
        try:
            res = cls.get(cls.mac_address == mac_address)
        # TODO exception
        except:
            res = cls.create(mac_address=mac_address, hostname=hostname,
                             last_seen=last_seen)

        res.last_seen = last_seen
        res.save()
