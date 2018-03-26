import re
from datetime import timedelta

duration_re = re.compile(
    r'((?P<weeks>\d+?)w)?((?P<days>\d+?)d)?((?P<hours>\d+?)h)?((?P<minutes>\d+?)m)?((?P<seconds>\d+?)s)?')


def parse_duration(duration_str):
    """
    Parse duration of time
    :param duration_str:
    :return: timedelta
    """
    parts = duration_re.match(duration_str)
    if not parts:
        return
    parts = parts.groupdict()
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
    :param dt_now: datetime pointing to actual time
    :param data: data from mikrotik
    :return: list of dicts with keys {"mac_address" "last_seen" "hostname"}
    """
    return [{"mac_address": device['mac'].upper(),
             "last_seen": dt_now - parse_duration(device['last']),
             "hostname": device['name']} for device in data]
