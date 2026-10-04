from rich.table import Table

from backend.scanners.bluetooth_scanner import (
    discover_bluetooth,
)
from backend.utils.terminal_ui import (
    console,
    error,
    section,
    success,
)


def scan_bluetooth():

    section("BLUETOOTH DISCOVERY")

    data = discover_bluetooth()

    if data.get("error"):

        error(data["error"])

        return data

    devices = data.get(
        "devices",
        [],
    )

    table = Table()

    table.add_column("Name")
    table.add_column("Address")
    table.add_column("Details")

    for device in devices:

        table.add_row(
            device["name"],
            device["address"],
            device["details"],
        )

    console.print(table)

    success(
        f"Discovered {len(devices)} Bluetooth device(s)."
    )

    return data