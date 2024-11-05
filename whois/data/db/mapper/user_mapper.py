from whois.data.table.user import UserTable
from whois.entity.user import User


def user_to_usertable_mapper(user: User) -> UserTable:
    return UserTable(
        id=user.id,
        username=user.username,
        password=user._password,
        display_name=user.display_name,
        flags=user.flags,
    )


def usertable_to_user_mapper(user: UserTable) -> User:
    return User(
        id=user.id,
        username=user.username,
        _password=user.password,
        display_name=user.display_name,
        flags=user.flags,
    )
