from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from whois.entity.bitfield import BitField


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
    last_seen: datetime
    owner: int
    flags: BitField

    @property
    def is_hidden(self) -> bool:
        return self.flags.has_flag(DeviceFlags.is_hidden.value)
