import logging

from whois.app import WhohacksApp
from whois.data.db.database import Database
from whois.settings.production import app_settings, mikrotik_settings

database = Database()

whois = WhohacksApp(app_settings, mikrotik_settings, database)
app = whois.app
