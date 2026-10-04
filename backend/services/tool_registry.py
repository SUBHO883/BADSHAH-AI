from backend.platforms.detector import (
    detect_available_tools,
    detect_platform,
)


TOOL_INFO = {
    "ip": {
        "purpose": "Network interfaces and routing",
        "platforms": ["linux"],
        "capability": "network_diagnostics",
    },
    "iw": {
        "purpose": "Wireless interface information",
        "platforms": ["linux"],
        "capability": "wireless_diagnostics",
    },
    "nmcli": {
        "purpose": "NetworkManager connection status",
        "platforms": ["linux"],
        "capability": "connection_diagnostics",
    },
    "airmon-ng": {
        "purpose": "Wireless interface diagnostics",
        "platforms": ["linux"],
        "capability": "wireless_diagnostics",
    },
    "airodump-ng": {
        "purpose": "Wireless traffic observation in authorized labs",
        "platforms": ["linux"],
        "capability": "wireless_analysis",
    },
    "nmap": {
        "purpose": "Network and service assessment",
        "platforms": ["linux", "windows", "macos"],
        "capability": "network_assessment",
    },
    "tshark": {
        "purpose": "Network packet analysis",
        "platforms": ["linux", "windows", "macos"],
        "capability": "packet_analysis",
    },
    "testssl.sh": {
        "purpose": "TLS configuration assessment",
        "platforms": ["linux"],
        "capability": "web_assessment",
    },
    "nikto": {
        "purpose": "Authorized web-server assessment",
        "platforms": ["linux"],
        "capability": "web_assessment",
    },
    "ollama": {
        "purpose": "Local AI inference",
        "platforms": ["linux", "windows", "macos"],
        "capability": "local_ai",
    },
}


def get_tool_inventory() -> dict:
    """Return detected OS and available security tools."""

    system_info = detect_platform()
    installed = detect_available_tools()

    family = system_info["os_family"]

    tools = []

    for name, info in TOOL_INFO.items():
        path = installed.get(name)

        tools.append({
            "name": name,
            "purpose": info["purpose"],
            "capability": info["capability"],
            "installed": bool(path),
            "path": path,
            "supported_on_current_os": (
                family in info["platforms"]
            ),
        })

    return {
        "system": system_info,
        "tools": tools,
    }