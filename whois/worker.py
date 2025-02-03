import logging
import time

from helpers.logger import init_logger
from whois.data.db.database import Database
from whois.data.repository.device_repository import Device, DeviceRepository
from whois.data.type.bitfield import BitField
from whois.mikrotik import fetch_leases
from whois.settings.production import mikrotik_settings

logger = init_logger("mikrotik-worker")
database = Database()
device_repository = DeviceRepository(database)


def update_devices() -> int:
    logger.info("Updating devices")
    leases = fetch_leases(
        mikrotik_settings.MIKROTIK_URL,
        mikrotik_settings.MIKROTIK_USER,
        mikrotik_settings.MIKROTIK_PASS,
    )
    logger.debug(f"Fetched leases: {leases}")

    for lease in leases:
        device = Device(
            lease.mac_address,
            lease.host_name,
            lease.last_seen,
            lease.client_id,
            BitField(),
        )  # TODO figure out how to pass flags
        logger.debug(f"Processing Device: {device.__repr__()}")
        if device_repository.get_by_mac_address(lease.mac_address):
            device_repository.update(device)
        else:
            device_repository.insert(device)

    return len(leases)


def run_worker():
    if not all(
        [
            mikrotik_settings.MIKROTIK_URL,
            mikrotik_settings.MIKROTIK_USER,
            mikrotik_settings.MIKROTIK_PASS,
        ]
    ):
        raise ValueError("Mikrotik settings not set")

    while True:
        try:
            logger.info("Updating device information")
            count = update_devices()
            logger.info(f"Updated information for {count} devices")
        except Exception:
            logger.exception("Could not update device information")

        time.sleep(mikrotik_settings.WORKER_FREQUENCY_S)


if __name__ == "__main__":
    run_worker()
