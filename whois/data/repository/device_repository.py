from datetime import datetime, timedelta, timezone
from typing import List

from sqlalchemy.orm import Session

from whois.data.db.database import Database
from whois.data.db.mapper.device_mapper import (
    device_to_devicetable_mapper,
    devicetable_to_device_mapper,
)
from whois.data.table.device import DeviceTable
from whois.entity.device import Device


class DeviceRepository:

    def __init__(self, database: Database) -> None:
        self.database = database

    def insert(self, device: Device) -> None:
        with Session(self.database.engine) as session:
            session.add(device_to_devicetable_mapper(device))
            session.commit()

    def update(self, device: Device) -> None:
        with Session(self.database.engine) as session:
            device_orm = (
                session.query(DeviceTable)
                .where(DeviceTable.mac_address == device.mac_address)
                .one()
            )
            device_orm.hostname = device.hostname
            device_orm.last_seen = device.last_seen
            device_orm.owner = device.owner
            device_orm.flags = device.flags
            session.commit()

    def get_by_mac_address(self, mac_address: str) -> Device:
        with Session(self.database.engine) as session:
            device_orm = (
                session.query(DeviceTable)
                .where(DeviceTable.mac_address == mac_address)
                .one()
            )
            return map(devicetable_to_device_mapper, device_orm)

    def get_all(self) -> List[Device]:
        with Session(self.database.engine) as session:
            devices_orm = session.query(DeviceTable).all()
            return list(map(devicetable_to_device_mapper, devices_orm))
