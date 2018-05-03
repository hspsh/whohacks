from whois.helpers import *


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


user_fixtures = [[1, 'user12', 'user man'], [2, 'admin', 'system administratot']]
users = list(map(lambda f: UserDummy(*f), user_fixtures))
device_fixtures = [['aa:aa:aa:aa:aa:aa', None, False], ['00:00:00:00:00:00', users[1], True]]
devices = list(map(lambda f: DeviceDummy(*f), device_fixtures))


def test_iterable():
    """
    All functions should return iterable
    :return:
    """
    assert hasattr(filter_anon_names(users), '__len__')
    assert hasattr(filter_hidden(users), '__len__')
    assert hasattr(owners_from_devices(devices), '__len__')
    assert hasattr(unclaimed_devices(devices), '__len__')


def test_hidden():
    """
    Should filter out hidden entities
    :return:
    """
    assert len(filter_hidden(users[:])) is 2
    assert len(filter_hidden(devices[:])) is 1


def test_ip_range():
    """
    ip_range should return if ip is in range
    :return:
    """
    assert ip_range('192.168.88.1-255', '192.168.88.123') is True
    assert ip_range('192.168.88.1-255', '192.168.80.100') is False

