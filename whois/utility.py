import re
from datetime import timedelta, datetime
from urllib.parse import urlparse, urljoin

from flask import request


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in (
    'http', 'https') and ref_url.netloc == test_url.netloc


duration_re = re.compile(
    r'((?P<weeks>\d+?)w)?((?P<days>\d+?)d)?((?P<hours>\d+?)h)?((?P<minutes>\d+?)m)?((?P<seconds>\d+?)s)?')


def parse_duration(duration_str):
    parts = duration_re.match(duration_str)
    if not parts:
        return
    parts = parts.groupdict()
    print(parts)
    time_params = {}
    for (name, param) in parts.items():
        if param:
            time_params[name] = int(param)

    time_params['days'] = time_params.get('days', 0) + 7 * time_params.get(
        'weeks', 0)
    time_params.pop('weeks', None)

    return timedelta(**time_params)


def parse_mikrotik_data(data):
    """Returns list of mac adress, last seen datetime
    >>> parse_mikrtotik_data([{"mac":"11:22:33:44:55:66","name":"Dom",
            "last":"50w6d16h1m10s","status":"waiting"},
            {"mac":"AA:BB:CC:DD:EE:FF","name":"HS",
            "last":"4d1h58m8s","status":"bound"}])
     [('11:22:33:44:55:66', '2018-01-13 21:37'),
     ('AA:BB:CC:DD:EE:FF', '2018-02-20 21:37')]"""
    assert type(data) is list

    dt_now = datetime.now()
    extracted = [(device['mac'].upper(),
                  dt_now - parse_duration(device['last'])) for device in data]
    return extracted
