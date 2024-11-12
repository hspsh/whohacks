from unittest import TestCase

from whois.helpers import Helpers
from whois.settings.testing import app_settings


class UserDummy:
    def __init__(self, id, username, display_name):
        self.id = id
        self.username = username
        self.display_name = display_name
        self.is_name_anonymous = True
        self.is_hidden = False


class DeviceDummy:
    def __init__(self, mac, owner, hidden):
        self.mac_address = mac
        self.owner = owner
        self.is_hidden = hidden


user_fixtures = [[1, "user12", "user man"], [2, "admin", "system administratot"]]
users = list(map(lambda f: UserDummy(*f), user_fixtures))
device_fixtures = [
    ["aa:aa:aa:aa:aa:aa", None, False],
    ["00:00:00:00:00:00", users[1], True],
]
devices = list(map(lambda f: DeviceDummy(*f), device_fixtures))
helpers = Helpers(app_settings)


class TestHelpers(TestCase):

    def test_iterable(self):
        """
        All functions should return iterable
        :return:
        """
        assert hasattr(helpers.filter_anon_names(users), "__len__")
        assert hasattr(helpers.filter_hidden(users), "__len__")
        assert hasattr(helpers.owners_from_devices(devices), "__len__")
        assert hasattr(helpers.unclaimed_devices(devices), "__len__")

    def test_hidden(self):
        """
        Should filter out hidden entities
        :return:
        """
        assert len(helpers.filter_hidden(users[:])) == 2
        assert len(helpers.filter_hidden(devices[:])) == 1

    def test_ip_range(self):
        """
        ip_range should return if ip is in range
        :return:
        """
        assert helpers.ip_range("192.168.88.1-255", "192.168.88.123") is True
        assert helpers.ip_range("192.168.88.1-255", "192.168.80.100") is False
