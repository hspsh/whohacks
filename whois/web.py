import logging

from whois.app import WhohacksApp
from whois.data.db.database import Database
from whois.settings.production import app_settings, mikrotik_settings

database = Database()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

whois = WhohacksApp(app_settings, mikrotik_settings, database, logger)
app = whois.app
