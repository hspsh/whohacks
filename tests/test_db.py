import logging
from copy import copy
from datetime import datetime, timedelta
from unittest import TestCase

from helpers.logger import init_logger
from whois.data.db.database import Database
from whois.data.repository.device_repository import DeviceRepository
from whois.entity.device import Device


class TestMikrotik(TestCase):

    def setUp(self):
        self.logger = init_logger(__name__)
        self.logger.addHandler(logging.FileHandler(f"{__name__}.log"))

        self.db = Database("sqlite:///whohacks.test.sqlite")
        self.db.drop()
        self.db.create_db()
        self.device_repository = DeviceRepository(self.db)

    def test_create_device(self):
        device = Device("mock_mac", "device_host", datetime.now(), owner=0, flags=0)
        self.device_repository.insert(device)

    def test_update_device(self):
        device1 = Device("mac1", "device1", datetime.now(), owner=0, flags=0)
        self.device_repository.insert(device1)
        device2 = copy(device1)
        new_last_seen = datetime.now() - timedelta(days=1)
        device2.last_seen = new_last_seen
        self.device_repository.update(device2)

        result_device = self.device_repository.get_by_mac_address("mac1")
        assert result_device == device2
