import logging
import time
from datetime import datetime, timezone

from whois.data.db.database import Database
from whois.data.repository.device_repository import DeviceRepository, Device
from whois.mikrotik import fetch_leases
from whois.settings import production

logger = logging.getLogger("mikrotik-worker")
database = Database()
device_repository = DeviceRepository(database)

def update_devices() -> int:
    leases = fetch_leases(
        production.MIKROTIK_URL, production.MIKROTIK_USER, production.MIKROTIK_PASS
    )

    for lease in leases:
        device = Device(lease.mac_address, lease.host_name, lease.last_seen)
        if device_repository.get_by_mac_address(lease.mac_address):
            device_repository.update(device)
        else:
            device_repository.insert(device)

    return len(leases)


def run_worker():
    if not all(
        [production.MIKROTIK_URL, production.MIKROTIK_USER, production.MIKROTIK_PASS]
    ):
        raise ValueError("Mikrotik settings not set")

    while True:
        try:
            logger.info("Updating device information")
            count = update_devices()
            logger.info(f"Updated information for {count} devices")
        except Exception:
            logger.exception("Could not update device information")

        time.sleep(production.worker_frequency_s)


if __name__ == "__main__":
    logging.basicConfig(
        format="[%(asctime)s] %(name)s [%(levelname)s]: %(msg)s",
        level=logging.INFO,
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    run_worker()
