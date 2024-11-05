import logging

from whois.data.db.database import Device, User, db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("db_create")

# logger.info("connect to db at {}".format(os.environ.get("DB_PATH", "whoisdevices.db")))
db.connect()
logger.info("creating tables")
db.create_tables([Device, User])

# dm1 = Device.create(mac_address='00:00:00:00:00:00', last_seen=datetime.now())
# dm1.save()
