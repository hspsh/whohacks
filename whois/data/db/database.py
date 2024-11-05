import os
from typing import Callable

import sqlalchemy as db

from whois.data.db.base import Base
from whois.data.table.device import DeviceTable
from whois.data.table.user import UserTable


class Database:
    """Represents the Database connection."""

    def __init__(self, db_url: str = None):
        if not db_url:
            db_url = os.environ.get("APP_DB_URL", "sqlite:///whohacks.sqlite")
        self.engine = db.create_engine(db_url)
        self.metadata = db.MetaData()
        self.connection = None

        self.user_table = UserTable()
        self.device_table = DeviceTable()
        self.create_db()

    @property
    def is_connected(self) -> bool:
        return self.connection is not None

    def connect(self) -> None:
        self.connection = self.engine.connect()

    def disconnect(self) -> None:
        if not self.connection:
            raise RuntimeError("Cannot close database connection - already closed")
        self.connection.close()

    def create_db(self) -> None:
        """Ensure that the database exists with given schema."""
        Base.metadata.create_all(self.engine)
