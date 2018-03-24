from whois.web import app
import whois.settings as settings

app.run(host=settings.host)
