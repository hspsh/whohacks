import atexit
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler as Scheduler
from whois.settings import log_frequency_time
from whois.database import History, Device
from whois.helpers import owners_from_devices, filter_hidden, unclaimed_devices


cron = Scheduler(daemon=True)
cron.start()


@cron.scheduled_job(**log_frequency_time)
def log_presence():
    now = datetime.now()
    recent = Device.get_recent(**log_frequency_time)
    visible_devices = filter_hidden(recent)
    uc = len(filter_hidden(owners_from_devices(visible_devices)))
    udc = len(unclaimed_devices(visible_devices))
    ndc = len(visible_devices) - udc
    History.create(
        datetime=now, user_count=uc, unknown_device_count=udc, known_device_count=ndc
    )


atexit.register(lambda: cron.shutdown(wait=False))
