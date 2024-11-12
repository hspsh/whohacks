import logging
import time
from datetime import datetime, timezone

from whois.data.db.database import Device, db
from whois.mikrotik import fetch_leases
from whois.settings import production

logger = logging.getLogger("mikrotik-worker")


def update_devices() -> int:
    leases = fetch_leases(
        production.MIKROTIK_URL, production.MIKROTIK_USER, production.MIKROTIK_PASS
    )

    for lease in leases:
        with db.atomic():
            last_seen_date = datetime.now(timezone.utc) - lease.last_seen
            Device.update_or_create(
                mac_address=lease.mac_address,
                last_seen=last_seen_date,
                hostname=lease.host_name,
            )

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
