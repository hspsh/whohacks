from whois.settings.production import mikrotik_settings
from whois.web import app

app.run(host=mikrotik_settings.HOST)
