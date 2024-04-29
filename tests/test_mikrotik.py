from datetime import timedelta

from whois.mikrotik import parse_duration


def test_parse_duration():
    data = (
        ("50w", timedelta(days=(50 * 7))),
        ("2d", timedelta(days=2)),
        ("1w3d", timedelta(days=10)),
        ("12h", timedelta(hours=12)),
        (
            "50w6d16h1m10s",
            timedelta(days=(6 + 50 * 7), hours=16, minutes=1, seconds=10),
        ),
        ("4d1h58m8s", timedelta(days=4, hours=1, minutes=58, seconds=8)),
    )

    for case, expected in data:
        result = parse_duration(case)
        assert result == expected

