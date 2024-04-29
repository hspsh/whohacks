import re
from dataclasses import dataclass, fields
from datetime import timedelta
from urllib.parse import urljoin

import requests
from requests.auth import HTTPBasicAuth


@dataclass
class MikrotikDhcpLease:
    # flags
    disabled: bool
    radius: bool
    dynamic: bool
    blocked: bool

    address: str
    mac_address: str
    client_id: str
    address_lists: str  # seems unused
    server: str
    dhcp_option: str
    status: str
    expires_after: timedelta
    last_seen: timedelta
    active_address: str
    active_mac_address: str
    active_client_id: str
    active_server: str
    host_name: str


def fetch_leases(url: str, user: str, password: str) -> list[MikrotikDhcpLease]:
    auth = HTTPBasicAuth(user, password)
    resp = requests.get(urljoin(url, "rest/ip/dhcp-server/lease"), auth=auth)
    assert resp.ok

    return parse_leases(resp.json())


def parse_leases(leases: dict) -> list[MikrotikDhcpLease]:
    dhcp_leases = []

    for lease in leases:
        data = {
            key.replace("-", "_"): value for key, value in lease.items() if key != ".id"
        }

        parsed = {
            field.name: parse_value(data.get(field.name), field.type)
            for field in fields(MikrotikDhcpLease)
        }

        dhcp_leases.append(MikrotikDhcpLease(**parsed))

    return dhcp_leases


def parse_value(value: str | None, field_type: type) -> str | timedelta | None:
    if not value:
        return

    if field_type is timedelta:
        return parse_duration(value)

    if field_type is bool:
        return value == "true"

    return value


duration_re = re.compile(
    r"((?P<weeks>\d+?)w)?((?P<days>\d+?)d)?((?P<hours>\d+?)h)?((?P<minutes>\d+?)m)?((?P<seconds>\d+?)s)?"
)


def parse_duration(duration_str: str | None) -> timedelta | None:
    """
    Parse duration of time
    """
    if not duration_str:
        return

    parts = duration_re.match(duration_str)
    if not parts:
        return
    parts = parts.groupdict()
    time_params = {}
    for name, param in parts.items():
        if param:
            time_params[name] = int(param)

    time_params["days"] = time_params.get("days", 0) + 7 * time_params.get("weeks", 0)
    time_params.pop("weeks", None)

    return timedelta(**time_params)
