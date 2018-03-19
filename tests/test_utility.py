from datetime import datetime, timedelta

from whois.utility import parse_mikrotik_data, parse_duration


def test_parse_duration():
    data = (("50w", timedelta(days=(50 * 7))),
            ("2d", timedelta(days=2)),
            ("1w3d", timedelta(days=10)),
            ("12h", timedelta(hours=12)),
            ("50w6d16h1m10s", timedelta(days=(6 + 50 * 7), hours=16, minutes=1,
                                        seconds=10)),
            ("4d1h58m8s", timedelta(days=4, hours=1, minutes=58, seconds=8)))

    for case, expected in data:
        result = parse_duration(case)
        assert result == expected


def test_parse_mikrotik_data():
    dt = datetime(2018, 6, 10, 13, 40, 10)
    data = (
        ([{"mac": "11:22:33:44:55:66", "name": "Dom",
           "last": "50w6d16h1m10s", "status": "waiting"},
          {"mac": "AA:BB:CC:DD:EE:FF", "name": "HS",
           "last": "4d1h58m8s", "status": "bound"}],
         [{"mac_address": "11:22:33:44:55:66", "hostname": "Dom",
           "last_seen": dt - timedelta(days=(6 + 50 * 7), hours=16, minutes=1,
                                       seconds=10)},
          {"mac_address": "AA:BB:CC:DD:EE:FF", "hostname": "HS",
           "last_seen": dt - timedelta(days=4, hours=1, minutes=58,
                                       seconds=8)}]),
        ([{"mac": "11:BB:33:44:55:FF", "name": "boy",
           "last": "5h11m10s", "status": "bound"}],
         [{"mac_address": "11:BB:33:44:55:FF", "hostname": "boy",
           "last_seen": dt - timedelta(hours=5, minutes=11, seconds=10)}]),
    )

    for case, expected in data:
        result = parse_mikrotik_data(dt, case)
        assert result == expected, result


def test_len_parse_mikrotik_data():
    dt = datetime(2018, 6, 10, 13, 40, 10)
    data = (
        ([{"mac": "11:22:33:44:55:66", "name": "Dom",
           "last": "50w6d16h1m10s", "status": "waiting"},
          {"mac": "AA:BB:CC:DD:EE:FF", "name": "HS",
           "last": "4d1h58m8s", "status": "bound"}], 2),
        ([{"mac": "11:22:33:44:55:66", "name": "Dom",
           "last": "50w6d16h1m10s", "status": "waiting"}], 1)
    )

    for case, expected in data:
        result = parse_mikrotik_data(dt, case)
        assert len(result) == expected
