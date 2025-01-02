import logging
import os
from typing import Callable

import sqlalchemy as db
from sqlalchemy.orm import Session

from whois.data.db.base import Base
from whois.data.table.device import DeviceTable
from whois.data.table.user import UserTable


class Database:
    """Represents the Database connection."""

    def __init__(self, db_url: str = None):
        if not db_url:
            db_url = os.environ.get("APP_DB_URL", "sqlite:///whohacks.sqlite")
        self.db_name = db_url.split("/")[-1]

        self.logger = logging.getLogger(f"db-{self.db_name}")
        logging.basicConfig(
            format="%(asctime)s %(module)s %(levelname)s: %(message)s",
            datefmt="%m/%d/%Y %I:%M:%S %p",
            level=logging.DEBUG,
            force=True,
        )

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
        self.logger.info(f"Connect to the database for {self.db_name}")
        self.connection = self.engine.connect()

    def disconnect(self) -> None:
        self.logger.info(f"Disconnect to the database for {self.db_name}")
        if not self.connection:
            raise RuntimeError("Cannot close database connection - already closed")
        self.connection.close()

    def create_db(self) -> None:
        """Ensure that the database exists with given schema."""
        self.logger.info(f"Create database {self.db_name}")
        Base.metadata.create_all(self.engine)

    def drop(self) -> None:
        """WARNING: Drops the entire database."""
        self.logger.warning(f"Drop database {self.db_name}")
        if not self.is_connected:
            self.connect()
        Base.metadata.drop_all(self.engine)
