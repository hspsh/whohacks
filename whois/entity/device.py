from dataclasses import dataclass
from enum import Enum

from whois.entity.bitfield import BitField
from whois.entity.iso_date_time import IsoDateTimeField


class DeviceFlags(Enum):
    is_hidden = 1
    is_new = 2
    is_infrastructure = 4
    is_esp = 8
    is_laptop = 16


@dataclass
class Device:
    mac_address: str
    hostname: str
    last_seen: IsoDateTimeField
    owner: int
    flags: BitField
