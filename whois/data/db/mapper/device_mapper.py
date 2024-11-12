from whois.data.table.device import DeviceTable
from whois.entity.device import Device


def device_to_devicetable_mapper(device: Device) -> DeviceTable:
    return DeviceTable(
        mac_address=device.mac_address,
        hostname=device.username,
        last_seen=device.last_seen,
        owner=device.owner,
        flags=device.flags,
    )


def devicetable_to_device_mapper(device: DeviceTable) -> Device:
    return Device(
        mac_address=device.mac_address,
        hostname=device.username,
        last_seen=device.last_seen,
        owner=device.owner,
        flags=device.flags,
    )
