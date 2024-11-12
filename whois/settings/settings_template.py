import os
from dataclasses import dataclass

from pytz import timezone


@dataclass
class MikrotikSettings:
    MIKROTIK_URL: str
    MIKROTIK_USER: str
    MIKROTIK_PASS: str

    WHITELIST: list
    HOST: str
    USER_FLAGS: dict
    DEVICE_FLAGS: dict

    WORKER_FREQUENCY_S: int


@dataclass
class AppSettings:
    APP_VERSION: str
    APP_TITLE: str
    APP_NAME: str

    APP_BASE_URL: str
    APP_HOME_URL: str
    APP_WIKI_URL: str
    APP_REPO_URL: str

    SECRET_KEY: str

    APP_TIMEZONE: timezone
    RECENT_TIME: dict

    SSO_CLIENT_ID: str
    SSO_CLIENT_SECRET: str
    APP_OAUTH_OPENID: str

    IP_MASK: str
    OIDC_ENABLED: bool
