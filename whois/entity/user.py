from dataclasses import dataclass
from enum import Enum

from werkzeug.security import check_password_hash, generate_password_hash

from whois.entity.bitfield import BitField


class UserFlags(Enum):
    is_hidden = 1
    is_name_anonymous = 2


@dataclass
class User:
    username: str
    display_name: str
    id: int = None
    flags: BitField = BitField()
    _password: str = None

    def __str__(self):
        if self.is_name_anonymous or self.is_hidden:
            return "anonymous"
        else:
            return self.display_name

    def get_id(self) -> int:
        """Get the user id. Required by flask login."""
        return self.id

    @property
    def is_hidden(self) -> bool:
        return self.flags.has_flag(UserFlags.is_hidden.value)

    @property
    def is_name_anonymous(self) -> bool:
        return self.flags.has_flag(UserFlags.is_name_anonymous.value)

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
    def password(self) -> str:
        return self._password

    @password.setter
    def password(self, new_password: str):
        if len(new_password) < 3:
            raise Exception(
                "Password is too short. It should contain at least 3 characters."
            )
        else:
            self._password = generate_password_hash(new_password)

    def auth(self, password: str) -> bool:
        return check_password_hash(self._password, password)
