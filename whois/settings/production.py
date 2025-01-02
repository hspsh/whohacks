import os

from pytz import timezone

from whois.settings.settings_template import AppSettings, MikrotikSettings

try:
    from importlib.metadata import version
    _version = version('whois')
except Exception:
    _version = "unknown"


if not os.environ["SECRET_KEY"]:
    raise ValueError("No SECRET_KEY set for Flask application")

if not os.environ.get("APP_IP_MASK", None):
    raise ValueError("ERROR: APP_IP_MASK environment variable was not set!")

app_settings = AppSettings(
    SECRET_KEY=os.environ["SECRET_KEY"],
    APP_VERSION=_version,
    APP_TITLE="👀 kto hakuje",
    APP_NAME="Kto Hakuje",
    APP_BASE_URL="whois.at.hsp.sh",
    APP_HOME_URL="//hsp.sh",
    APP_WIKI_URL="//wiki.hsp.sh/whois",
    APP_REPO_URL="//github.com/hspsh/whohacks",
    APP_TIMEZONE=timezone(os.environ.get("APP_TIMEZONE", "Europe/Warsaw")),
    SSO_CLIENT_ID=os.environ.get("OAUTH_CLIENT_ID"),
    SSO_CLIENT_SECRET=os.environ.get("OAUTH_CLIENT_SECRET"),
    APP_OAUTH_OPENID=os.environ.get("APP_OAUTH_OPENID"),
    IP_MASK=os.environ.get("APP_IP_MASK", None),
    OIDC_ENABLED=True,
    RECENT_TIME={"minutes": 20},
)


mikrotik_settings = MikrotikSettings(
    MIKROTIK_URL=os.environ.get("APP_MIKROTIK_URL"),
    MIKROTIK_USER=os.environ.get("APP_MIKROTIK_USER"),
    MIKROTIK_PASS=os.environ.get("APP_MIKROTIK_PASS"),
    WHITELIST=["192.168.88.1"],
    HOST="0.0.0.0",
    USER_FLAGS={1: "hidden", 2: "name_anonymous"},
    DEVICE_FLAGS={1: "hidden", 2: "new", 4: "infrastructure", 8: "esp", 16: "laptop"},
    WORKER_FREQUENCY_S=60,
)
