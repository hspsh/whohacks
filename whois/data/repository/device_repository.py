from datetime import datetime, timedelta, timezone
from typing import List

from sqlalchemy.orm import Session

from helpers.logger import init_logger
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
        self.logger = init_logger("DeviceRepository")

    def insert(self, device: Device) -> None:
        self.logger.debug(f'Insert device: "{device.__repr__()}"')
        with Session(self.database.engine) as session:
            session.add(device_to_devicetable_mapper(device))
            session.commit()

    def update(self, device: Device) -> None:
        self.logger.debug(f'Update device: "{device.__repr__()}"')
        with Session(self.database.engine) as session:
            device_orm = (
                session.query(DeviceTable)
                .where(DeviceTable.mac_address == device.mac_address)
                .one()
            )
            device_orm.hostname = device.hostname
            device_orm.last_seen = device.last_seen.python_value
            device_orm.owner = device.owner
            device_orm.flags = device.flags
            session.commit()

    def get_by_mac_address(self, mac_address: str) -> Device:
        self.logger.debug(f'Seach device by mac address: "{mac_address}"')
        with Session(self.database.engine) as session:
            device_orm = (
                session.query(DeviceTable)
                .where(DeviceTable.mac_address == mac_address)
                .one()
            )
            return next(map(devicetable_to_device_mapper, [device_orm]))

    def get_all(self) -> List[Device]:
        self.logger.debug("Get all devices")
        with Session(self.database.engine) as session:
            devices_orm = session.query(DeviceTable).all()
            return list(map(devicetable_to_device_mapper, devices_orm))

    def get_by_user_id(self, user_id: int) -> List[Device]:
        self.logger.debug(f'Seach device by user ID: "{user_id}"')
        with Session(self.database.engine) as session:
            devices_orm = (
                session.query(DeviceTable).where(DeviceTable.owner == user_id).all()
            )
            if len(devices_orm) > 0:
                return list(map(devicetable_to_device_mapper, devices_orm))
            else:
                return list()

    def get_recent(self, delta: timedelta) -> List[Device]:
        self.logger.debug(f'Get recent devices with delta="{delta}"')
        with Session(self.database.engine) as session:
            recent_time = datetime.now(timezone.utc) - delta
            devices_orm = (
                session.query(DeviceTable)
                .filter(DeviceTable.last_seen > recent_time)
                .all()
            )
            if len(devices_orm) > 0:
                return list(map(devicetable_to_device_mapper, devices_orm))
            else:
                return list()
