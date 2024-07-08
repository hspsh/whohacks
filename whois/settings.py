import os

from pytz import timezone

SECRET_KEY = os.environ["SECRET_KEY"]
if not SECRET_KEY:
    raise ValueError("No SECRET_KEY set for Flask application")
APP_VERSION = "1.3.1"
APP_TITLE = "👀 kto hakuje"
APP_NAME = "Kto Hakuje"

APP_BASE_URL = "whois.at.hsp.sh"

APP_HOME_URL = "//hsp.sh"
APP_WIKI_URL = "//wiki.hsp.sh/whois"
APP_REPO_URL = "//github.com/hspsh/whohacks"

APP_TIMEZONE = timezone(os.environ.get("APP_TIMEZONE", "Europe/Warsaw"))

MIKROTIK_URL = os.environ.get("MIKROTIK_URL")
MIKROTIK_USER = os.environ.get("MIKROTIK_USER")
MIKROTIK_PASS = os.environ.get("MIKROTIK_PASS")

# mikrtotik ip, or other reporting devices

whitelist = ["192.168.88.1"]
host = "0.0.0.0"
user_flags = {1: "hidden", 2: "name_anonymous"}
device_flags = {1: "hidden", 2: "new", 4: "infrastructure", 8: "esp", 16: "laptop"}

recent_time = {"minutes": 20}
worker_frequency_s = 60

oidc_enabled = True
# OAuth settings
SSO_PROVIDER = os.environ.get("OAUTH_PROVIDER")
SSO_CLIENT_ID = os.environ.get("OAUTH_CLIENT_ID")
SSO_CLIENT_SECRET = os.environ.get("OAUTH_CLIENT_SECRET")

# production
ip_mask = "192.168.88.1-255"
# TODO: better way for handling dev env
# ip_mask = "127.0.0.1"
