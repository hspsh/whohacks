import os
from datetime import datetime, timedelta, timezone

import peewee as pw
from werkzeug.security import check_password_hash, generate_password_hash
from playhouse.db_url import connect


db_url = os.environ.get("APP_DB_URL", "sqlite:///whohacks.sqlite")
db = connect(db_url)


class User(pw.Model):
    id = pw.PrimaryKeyField()
    username = pw.CharField(unique=True)
    _password = pw.CharField(column_name="password", null=True)
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
        user = cls.create(
            username=username, display_name=display_name
        )
        user.password = password
        return user

    @classmethod
    def register_from_sso(cls, username, display_name=None):
        """
        Creates user without any password. Such users can only login via SSO.
        :param username: used in login
        :param display_name: displayed username
        :return: user instance
        """
        user = cls.create(
            username=username, display_name=display_name
        )
        user._password = None
        return user

    def __str__(self):
        if self.is_name_anonymous or self.is_hidden:
            return "anonymous"
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
    def is_sso(self) -> bool:
        return not self._password

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, new_password):
        if len(new_password) < 3:
            raise Exception("too_short")
        else:
            self._password = generate_password_hash(new_password)

    def auth(self, password):
        return check_password_hash(self.password, password)


class IsoDateTimeField(pw.DateTimeField):
    field_type = "DATETIME"

    def db_value(self, value: datetime) -> str:
        if value:
            return value.isoformat()

    def python_value(self, value: str) -> datetime:
        if value:
            return datetime.fromisoformat(value)


class Device(pw.Model):
    mac_address = pw.FixedCharField(primary_key=True, unique=True, max_length=17)
    hostname = pw.CharField(null=True)
    last_seen = IsoDateTimeField()
    owner = pw.ForeignKeyField(
        User, backref="devices", column_name="user_id", null=True
    )
    flags = pw.BitField(null=True)

    is_hidden = flags.flag(1)
    is_new = flags.flag(2)
    is_infrastructure = flags.flag(4)
    is_esp = flags.flag(8)
    is_laptop = flags.flag(16)

    class Meta:
        database = db

    def __str__(self):
        return self.mac_address

    @classmethod
    def get_recent(cls, days=0, hours=0, minutes=30, seconds=0):
        """
        Returns list of last connected devices
        :param hours:
        :param minutes:
        :param seconds:
        :return: list of devices
        """
        recent_time = datetime.now(timezone.utc) - timedelta(
            days=days, hours=hours, minutes=minutes, seconds=seconds
        )
        devices = list(
            cls.select().where(cls.last_seen > recent_time).order_by(cls.last_seen)
        )
        return devices

    @classmethod
    def update_or_create(cls, mac_address, last_seen, hostname=None):
        try:
            res = cls.create(
                mac_address=mac_address, hostname=hostname, last_seen=last_seen
            )

        except pw.IntegrityError:
            res = cls.get(cls.mac_address == mac_address)
            res.last_seen = last_seen
            res.hostname = hostname

        res.save()
