import platform
import re
from datetime import datetime

from backend.models.schemas import ScanResult
from backend.utils.command_runner import run_command


def get_wifi_adapters():
    """
    Detect all physical Wi-Fi adapters on Windows.

    Uses PowerShell Get-NetAdapter because it can detect
    connected and disconnected Wi-Fi adapters.
    """

    if platform.system() != "Windows":
        return []

    powershell_command = (
        "Get-NetAdapter | "
        "Where-Object { "
        "$_.InterfaceDescription -match 'Wi-Fi|Wireless|802.11|WLAN|MediaTek|TP-Link' "
        "-or $_.Name -match '^Wi-Fi' "
        "} | "
        "Select-Object Name, InterfaceDescription, "
        "ifIndex, Status, MacAddress, LinkSpeed, "
        "MediaConnectionState | "
        "ConvertTo-Json -Compress"
    )

    result = run_command(
        [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-Command",
            powershell_command,
        ],
        timeout=20,
    )

    if result.returncode != 0:
        return []

    output = result.stdout.strip()

    if not output:
        return []

    try:
        import json

        data = json.loads(output)

        if isinstance(data, dict):
            data = [data]

        adapters = []

        for item in data:

            adapters.append(
                {
                    "name": str(
                        item.get("Name", "")
                    ),
                    "description": str(
                        item.get(
                            "InterfaceDescription",
                            "",
                        )
                    ),
                    "if_index": str(
                        item.get(
                            "ifIndex",
                            "",
                        )
                    ),
                    "state": str(
                        item.get(
                            "Status",
                            "",
                        )
                    ),
                    "mac": str(
                        item.get(
                            "MacAddress",
                            "",
                        )
                    ),
                    "link_speed": str(
                        item.get(
                            "LinkSpeed",
                            "",
                        )
                    ),
                    "media_state": str(
                        item.get(
                            "MediaConnectionState",
                            "",
                        )
                    ),
                }
            )

        return adapters

    except Exception:
        return []


def get_netsh_wifi_interfaces():
    """
    Read detailed Wi-Fi interface information from netsh.
    This includes connected/disconnected WLAN interfaces.
    """

    if platform.system() != "Windows":
        return []

    result = run_command(
        [
            "netsh",
            "wlan",
            "show",
            "interfaces",
        ],
        timeout=20,
    )

    if result.returncode != 0:
        return []

    lines = result.stdout.splitlines()

    interfaces = []
    current = None

    def value_after_colon(line):
        if ":" not in line:
            return ""

        return line.split(
            ":",
            1,
        )[1].strip()

    for raw_line in lines:

        line = raw_line.strip()

        if not line:
            continue

        # New interface
        if re.match(
            r"^Name\s*:",
            line,
            re.IGNORECASE,
        ):

            if current:
                interfaces.append(current)

            current = {
                "name": value_after_colon(line),
                "description": "",
                "guid": "",
                "mac": "",
                "state": "",
                "ssid": "",
                "bssid": "",
                "band": "",
                "channel": "",
                "radio": "",
                "authentication": "",
                "cipher": "",
                "signal": "",
                "receive_rate": "",
                "transmit_rate": "",
            }

            continue

        if current is None:
            continue

        field_patterns = {
            "description": r"^Description\s*:",
            "guid": r"^GUID\s*:",
            "mac": r"^Physical address\s*:",
            "state": r"^State\s*:",
            "ssid": r"^SSID\s*:",
            "bssid": r"^BSSID\s*:",
            "band": r"^Band\s*:",
            "channel": r"^Channel\s*:",
            "radio": r"^Radio type\s*:",
            "authentication": r"^Authentication\s*:",
            "cipher": r"^Cipher\s*:",
            "signal": r"^Signal\s*:",
            "receive_rate": r"^Receive rate",
            "transmit_rate": r"^Transmit rate",
        }

        for field, pattern in field_patterns.items():

            if re.match(
                pattern,
                line,
                re.IGNORECASE,
            ):

                if field in {
                    "receive_rate",
                    "transmit_rate",
                }:

                    current[field] = value_after_colon(
                        line
                    )

                else:

                    current[field] = value_after_colon(
                        line
                    )

                break

    if current:
        interfaces.append(current)

    return interfaces


def discover_wifi_networks():
    """
    Discover nearby Wi-Fi networks using:

        netsh wlan show networks mode=bssid

    This is read-only discovery.
    """

    if platform.system() != "Windows":

        return {
            "platform": platform.system(),
            "timestamp": datetime.now().isoformat(),
            "count": 0,
            "networks": [],
            "error": (
                "Wi-Fi discovery currently "
                "supports Windows."
            ),
        }

    result = run_command(
        [
            "netsh",
            "wlan",
            "show",
            "networks",
            "mode=bssid",
        ],
        timeout=30,
    )

    if result.returncode != 0:

        return {
            "platform": "Windows",
            "timestamp": datetime.now().isoformat(),
            "count": 0,
            "networks": [],
            "error": (
                result.stderr.strip()
                or result.stdout.strip()
                or "netsh Wi-Fi discovery failed."
            ),
        }

    lines = result.stdout.splitlines()

    networks = []
    current_network = None
    current_bssid = None

    for raw_line in lines:

        line = raw_line.strip()

        if not line:
            continue

        # -----------------------------
        # SSID
        # -----------------------------

        ssid_match = re.match(
            r"^SSID\s+\d+\s*:\s*(.*)$",
            line,
            re.IGNORECASE,
        )

        if ssid_match:

            if current_network:
                networks.append(
                    current_network
                )

            ssid = ssid_match.group(1).strip()

            current_network = {
                "ssid": ssid,
                "network_authentication": "",
                "network_encryption": "",
                "bssids": [],
            }

            current_bssid = None

            continue

        if current_network is None:
            continue

        # -----------------------------
        # Authentication
        # -----------------------------

        if re.match(
            r"^Authentication\s*:",
            line,
            re.IGNORECASE,
        ):

            current_network[
                "network_authentication"
            ] = line.split(
                ":",
                1,
            )[1].strip()

            continue

        # -----------------------------
        # Encryption
        # -----------------------------

        if re.match(
            r"^Encryption\s*:",
            line,
            re.IGNORECASE,
        ):

            current_network[
                "network_encryption"
            ] = line.split(
                ":",
                1,
            )[1].strip()

            continue

        # -----------------------------
        # BSSID
        # -----------------------------

        bssid_match = re.match(
            r"^BSSID\s+\d+\s*:\s*(.*)$",
            line,
            re.IGNORECASE,
        )

        if bssid_match:

            bssid = bssid_match.group(1).strip()

            current_bssid = {
                "bssid": bssid,
                "signal": "",
                "radio": "",
                "channel": "",
            }

            current_network[
                "bssids"
            ].append(
                current_bssid
            )

            continue

        if current_bssid is None:
            continue

        # -----------------------------
        # Signal
        # -----------------------------

        if re.match(
            r"^Signal\s*:",
            line,
            re.IGNORECASE,
        ):

            current_bssid[
                "signal"
            ] = line.split(
                ":",
                1,
            )[1].strip()

            continue

        # -----------------------------
        # Radio
        # -----------------------------

        if re.match(
            r"^Radio type\s*:",
            line,
            re.IGNORECASE,
        ):

            current_bssid[
                "radio"
            ] = line.split(
                ":",
                1,
            )[1].strip()

            continue

        # -----------------------------
        # Channel
        # -----------------------------

        if re.match(
            r"^Channel\s*:",
            line,
            re.IGNORECASE,
        ):

            current_bssid[
                "channel"
            ] = line.split(
                ":",
                1,
            )[1].strip()

            continue

    if current_network:
        networks.append(
            current_network
        )

    return {
        "platform": "Windows",
        "timestamp": datetime.now().isoformat(),
        "count": len(networks),
        "networks": networks,
    }


def scan_wifi():
    """
    Complete read-only Wi-Fi assessment.
    """

    adapters = get_wifi_adapters()

    interfaces = get_netsh_wifi_interfaces()

    discovery = discover_wifi_networks()

    return ScanResult(
        scan_type="wifi_discovery",
        target="local_wifi_environment",
        timestamp=datetime.now().isoformat(),
        data={
            "adapters": adapters,
            "interfaces": interfaces,
            "discovery": discovery,
        },
    )