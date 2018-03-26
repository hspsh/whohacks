from urllib.parse import urlparse, urljoin

from flask import request


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
    return test_url.scheme in (
        'http', 'https') and ref_url.netloc == test_url.netloc