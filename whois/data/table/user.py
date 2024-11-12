from sqlalchemy import Column, Integer, String

from whois.data.db.base import Base
from whois.data.type.bitfield import BitField


class UserTable(Base):
    """Represents the 'user' table in the database.

    Columns:
        id: int (Primary key)
        username: str (Unique)
        password: str (Nullable)
        display_name: str
        flags: BitField (Nullable)
    """

    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    password = Column(String, nullable=True)
    display_name = Column(String)
    flags = Column(BitField, nullable=True)
