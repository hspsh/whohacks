# from datetime import datetime
from whois.database import db, Device, User

db.connect()
db.create_tables([Device, User])

# dm1 = Device.create(mac_address='00:00:00:00:00:00', last_seen=datetime.now())
# dm1.save()
