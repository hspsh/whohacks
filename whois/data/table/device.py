from sqlalchemy import Column, ForeignKey
from sqlalchemy.types import VARCHAR, Integer, String

from whois.data.db.base import Base
from whois.data.type.bitfield import BitField
from whois.data.type.iso_date_time_field import IsoDateTimeField


class DeviceTable(Base):
    """Represents the 'device' table in the database.

    Columns:
        mac_address: str(17) (Primary key)
        hostname: str (Unique)
        last_seen: IsoDateTimeField
        owner: int (Foreign Key -> user.id)
        flags: BitField (Nullable)
    """

    __tablename__ = "device"

    mac_address = Column(VARCHAR(17), primary_key=True, unique=True)
    hostname = Column(String, nullable=True)
    last_seen = Column(IsoDateTimeField)
    owner = Column(Integer, ForeignKey("user.id"), nullable=True, name="user_id")
    flags = Column(BitField, nullable=True)

    def __str__(self) -> str:
        return str(self.mac_address)
