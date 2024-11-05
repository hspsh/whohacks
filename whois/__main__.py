import whois.settings as settings
from whois.web import app

app.run(host=settings.host)
