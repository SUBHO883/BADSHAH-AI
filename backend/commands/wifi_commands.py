from rich.table import Table

from backend.scanners.wifi_scanner import (
    discover_wifi_networks,
    get_netsh_wifi_interfaces,
    get_wifi_adapters,
)
from backend.utils.terminal_ui import (
    console,
    error,
    section,
    success,
)


def show_adapters():

    section("WI-FI ADAPTERS")

    adapters = get_wifi_adapters()

    if not adapters:

        error(
            "No Wi-Fi adapters detected."
        )

        console.print(
            "\n[dim]Try running this in PowerShell:[/dim]"
        )

        console.print(
            "Get-NetAdapter"
        )

        return

    table = Table(
        title="PHYSICAL / NETWORK WI-FI ADAPTERS"
    )

    table.add_column("Name")
    table.add_column("Description")
    table.add_column("Status")
    table.add_column("MAC")
    table.add_column("Speed")
    table.add_column("ifIndex")

    for adapter in adapters:

        table.add_row(
            adapter.get(
                "name",
                "-",
            ),
            adapter.get(
                "description",
                "-",
            ),
            adapter.get(
                "state",
                "-",
            ),
            adapter.get(
                "mac",
                "-",
            ),
            adapter.get(
                "link_speed",
                "-",
            ),
            adapter.get(
                "if_index",
                "-",
            ),
        )

    console.print(table)

    console.print()

    interfaces = get_netsh_wifi_interfaces()

    if interfaces:

        interface_table = Table(
            title="WI-FI WLAN INTERFACES"
        )

        interface_table.add_column(
            "Name"
        )
        interface_table.add_column(
            "State"
        )
        interface_table.add_column(
            "SSID"
        )
        interface_table.add_column(
            "BSSID"
        )
        interface_table.add_column(
            "Channel"
        )
        interface_table.add_column(
            "Signal"
        )
        interface_table.add_column(
            "Authentication"
        )
        interface_table.add_column(
            "Cipher"
        )

        for interface in interfaces:

            interface_table.add_row(
                interface.get(
                    "name",
                    "-",
                ),
                interface.get(
                    "state",
                    "-",
                ),
                interface.get(
                    "ssid",
                    "-",
                ),
                interface.get(
                    "bssid",
                    "-",
                ),
                interface.get(
                    "channel",
                    "-",
                ),
                interface.get(
                    "signal",
                    "-",
                ),
                interface.get(
                    "authentication",
                    "-",
                ),
                interface.get(
                    "cipher",
                    "-",
                ),
            )

        console.print(
            interface_table
        )

    success(
        f"Detected {len(adapters)} Wi-Fi adapter(s)."
    )


def scan_wifi_networks():

    section("REAL WI-FI NETWORK DISCOVERY")

    data = discover_wifi_networks()

    if data.get("error"):

        error(
            data["error"]
        )

        return data

    networks = data.get(
        "networks",
        [],
    )

    if not networks:

        error(
            "No Wi-Fi networks discovered."
        )

        console.print(
            "\n[dim]Run this manually to verify Windows Wi-Fi scanning:[/dim]"
        )

        console.print(
            "netsh wlan show networks mode=bssid"
        )

        return data

    table = Table(
        title=(
            f"NEARBY WI-FI NETWORKS "
            f"({len(networks)})"
        )
    )

    table.add_column("SSID")
    table.add_column("Authentication")
    table.add_column("Encryption")
    table.add_column("BSSID")
    table.add_column("Channel")
    table.add_column("Signal")
    table.add_column("Radio")

    for network in networks:

        bssids = network.get(
            "bssids",
            [],
        )

        if not bssids:

            table.add_row(
                network.get(
                    "ssid",
                    "<Hidden>",
                ),
                network.get(
                    "network_authentication",
                    "-",
                ),
                network.get(
                    "network_encryption",
                    "-",
                ),
                "-",
                "-",
                "-",
                "-",
            )

            continue

        for bssid in bssids:

            table.add_row(
                network.get(
                    "ssid",
                    "<Hidden>",
                ),
                network.get(
                    "network_authentication",
                    "-",
                ),
                network.get(
                    "network_encryption",
                    "-",
                ),
                bssid.get(
                    "bssid",
                    "-",
                ),
                bssid.get(
                    "channel",
                    "-",
                ),
                bssid.get(
                    "signal",
                    "-",
                ),
                bssid.get(
                    "radio",
                    "-",
                ),
            )

    console.print(table)

    success(
        f"Discovered {len(networks)} Wi-Fi network(s)."
    )

    return data