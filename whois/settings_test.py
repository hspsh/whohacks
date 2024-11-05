import os

from pytz import timezone

APP_VERSION = "1.5.0"
APP_TITLE = "👀 kto hakuje"
APP_NAME = "Kto Hakuje"

APP_BASE_URL = "whois.at.hsp.sh"

APP_HOME_URL = "//hsp.sh"
APP_WIKI_URL = "//wiki.hsp.sh/whois"
APP_REPO_URL = "//github.com/hspsh/whohacks"

APP_TIMEZONE = timezone(os.environ.get("APP_TIMEZONE", "Europe/Warsaw"))

# mikrtotik ip, or other reporting devices
whitelist = ["192.168.88.1"]
host = "0.0.0.0"
user_flags = {1: "hidden", 2: "name_anonymous"}
device_flags = {1: "hidden", 2: "new", 4: "infrastructure", 8: "esp", 16: "laptop"}

recent_time = {"minutes": 20}
worker_frequency_s = 60

oidc_enabled = True

SECRET_KEY = "test_key"
ip_mask = "127.0.0.1:5000"
