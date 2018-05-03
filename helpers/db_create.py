import os
import logging
from datetime import datetime
from whois.database import db, Device, User

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info('connect to db at {}'.format(os.environ.get('DB_PATH', 'whoisdevices.db')))
db.connect()
logger.info('creating tables')
db.create_tables([Device, User])

dm1 = Device.create(mac_address='00:00:00:00:00:00', last_seen=datetime.now())
dm1.save()
