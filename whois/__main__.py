from whois.whois import app
from whois.database import db

c = db.cursor()

c.execute(
    'CREATE TABLE IF NOT EXISTS whois_users (id INTEGER PRIMARY KEY AUTOINCREMENT, display_name VARCHAR(100), login VARCHAR(32) UNIQUE, password VARCHAR(64), registered_at DATETIME, last_login DATETIME)')
c.execute(
    'CREATE TABLE IF NOT EXISTS whois_devices (mac_addr VARCHAR(17) PRIMARY KEY UNIQUE, last_seen DATETIME, user_id INTEGER, tags VARCHAR(32))')

db.commit()

app.run()
