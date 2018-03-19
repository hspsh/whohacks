from datetime import datetime

from whois.database import pw_db, DeviceModel

pw_db.create_tables([DeviceModel])

dm1 = DeviceModel.create(mac_address='00:00:00:00:00:00', last_seen=datetime.now())
dm1.save()