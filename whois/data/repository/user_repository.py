from typing import List

from sqlalchemy.orm import Session

from whois.data.db.database import Database
from whois.data.db.mapper.user_mapper import (
    user_to_usertable_mapper,
    usertable_to_user_mapper,
)
from whois.data.table.user import UserTable
from whois.entity.user import User


class UserRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def insert(self, user: User) -> None:
        with Session(self.database.engine) as session:
            session.add(user_to_usertable_mapper(user))
            session.commit()

    def update(self, user: User) -> None:
        with Session(self.database.engine) as session:
            user_orm = session.query(UserTable).where(UserTable.id == user.id).one()
            user_orm.username = user.username
            user_orm.password = user.password
            user_orm.display_name = user.display_name
            user_orm.flags = user.flags
            session.commit()

    def get_all(self) -> List[User]:
        with Session(self.database.engine) as session:
            users_orm = session.query(UserTable).all()
            return list(map(usertable_to_user_mapper, users_orm))

    def get_by_username(self, username: str) -> User:
        with Session(self.database.engine) as session:
            user_orm = (
                session.query(UserTable).where(UserTable.username == username).one()
            )

            return usertable_to_user_mapper(user_orm)

    def get_by_id(self, id: int) -> User:
        with Session(self.database.engine) as session:
            user_orm = session.query(UserTable).where(UserTable.id == id).one()

            return usertable_to_user_mapper(user_orm)
