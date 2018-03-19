import re
from datetime import timedelta
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
    # print(parts)
    time_params = {}
    for (name, param) in parts.items():
        if param:
            time_params[name] = int(param)

    time_params['days'] = time_params.get('days', 0) + 7 * time_params.get(
        'weeks', 0)
    time_params.pop('weeks', None)

    return timedelta(**time_params)


def parse_mikrotik_data(dt_now, data):
    """
    Returns list of mac address, last seen datetime
    """
    return [{"mac_address": device['mac'].upper(),
             "last_seen": dt_now - parse_duration(device['last']),
             "hostname": device['name']} for device in data]
