import logging
from functools import wraps
from urllib.parse import urlparse, urljoin

from flask import request, abort
from whois.settings import ip_mask

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def owners_from_devices(devices):
    return set(filter(None, map(lambda d: d.owner, devices)))


def filter_hidden(entities):
    return list(filter(lambda e: not e.is_hidden, entities))


def filter_anon_names(users):
    return list(filter(lambda u: not u.is_name_anonymous, users))


def unclaimed_devices(devices):
    return list(filter(lambda d: d.owner is None, devices))


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ("http", "https") and ref_url.netloc == test_url.netloc


# TODO: taken from SO
def ip_range(mask, address):
    ip_parts = address.split(".")
    for index, current_range in enumerate(mask.split(".")):
        if "-" in current_range:
            mini, maxi = map(int, current_range.split("-"))
        else:
            mini = maxi = int(current_range)
        if not (mini <= int(ip_parts[index]) <= maxi):
            return False
    return True


def in_space_required():
    def decorator(f):
        @wraps(f)
        def func(*a, **kw):
            if not ip_range(ip_mask, request.remote_addr):
                logger.error("{} request from outside".format(request.remote_addr))
                abort(403)
            else:
                logger.info("{} is in allowed ip range".format(request.remote_addr))
                return f(*a, **kw)

        return func

    return decorator
