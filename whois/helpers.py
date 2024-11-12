import logging
from datetime import datetime, timedelta, timezone
from functools import wraps
from typing import List
from urllib.parse import urljoin, urlparse

from flask import abort, request

from whois.entity.device import Device
from whois.settings.settings_template import AppSettings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Helpers:

    def __init__(self, app_settings: AppSettings):
        self.app_settings = app_settings
        self.ip_mask = app_settings.IP_MASK

    def owners_from_devices(self, devices):
        return set(filter(None, map(lambda d: d.owner, devices)))

    def filter_hidden(self, entities):
        return list(filter(lambda e: not e.is_hidden, entities))

    def filter_anon_names(self, users):
        return list(filter(lambda u: not u.is_name_anonymous, users))

    def unclaimed_devices(self, devices):
        return list(filter(lambda d: d.owner is None, devices))

    def is_safe_url(self, target):
        ref_url = urlparse(request.host_url)
        test_url = urlparse(urljoin(request.host_url, target))
        return (
            test_url.scheme in ("http", "https") and ref_url.netloc == test_url.netloc
        )

    def ip_range(self, mask, address):
        """
        Checks if given address is in space defined by mask
        :param mask: string for ex. '192.168.88.1-255'
        :param address:
        :return: boolean
        """
        ip_parts = address.split(".")
        for index, current_range in enumerate(mask.split(".")):
            if "-" in current_range:
                mini, maxi = map(int, current_range.split("-"))
            else:
                mini = maxi = int(current_range)
            if not (mini <= int(ip_parts[index]) <= maxi):
                return False
        return True

    def in_space_required(self, f):
        def decorator(f):
            @wraps(f)
            def func(*a, **kw):
                if request.headers.getlist("X-Forwarded-For"):
                    ip_addr = request.headers.getlist("X-Forwarded-For")[0]
                    logger.info(
                        "forward from %s to %s",
                        request.remote_addr,
                        request.headers.getlist("X-Forwarded-For")[0],
                    )
                else:
                    ip_addr = request.remote_addr

                if not self.ip_range(self.ip_mask, ip_addr):
                    logger.error("{} request from outside".format(ip_addr))
                    abort(403)
                else:
                    logger.info("{} is in allowed ip range".format(ip_addr))
                    return f(*a, **kw)

            return func

        return decorator(f)
