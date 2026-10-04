import platform
import shutil
import socket
from pathlib import Path


def detect_platform() -> dict:
    """Identify the operating system and runtime."""

    system = platform.system().lower()

    if system == "windows":
        os_family = "windows"
    elif system == "linux":
        os_family = "linux"
    elif system == "darwin":
        os_family = "macos"
    else:
        os_family = "unknown"

    is_wsl = False

    if os_family == "linux":
        try:
            release = Path(
                "/proc/sys/kernel/osrelease"
            ).read_text(
                encoding="utf-8"
            ).lower()

            version = Path(
                "/proc/version"
            ).read_text(
                encoding="utf-8"
            ).lower()

            is_wsl = (
                "microsoft" in release
                or "microsoft" in version
            )

        except OSError:
            pass

    distro = {}

    if os_family == "linux":
        try:
            import platform as platform_module

            if hasattr(
                platform_module,
                "freedesktop_os_release",
            ):
                distro = (
                    platform_module.freedesktop_os_release()
                )

        except (OSError, AttributeError):
            distro = {}

    return {
        "os_family": os_family,
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "architecture": platform.machine(),
        "python_version": platform.python_version(),
        "hostname": socket.gethostname(),
        "is_wsl": is_wsl,
        "distribution": distro.get(
            "PRETTY_NAME",
            "Unknown",
        ),
    }


def detect_available_tools() -> dict:
    """Check which relevant command-line tools exist."""

    candidates = [
        "ip",
        "iw",
        "nmcli",
        "airmon-ng",
        "airodump-ng",
        "nmap",
        "tshark",
        "wireshark",
        "testssl.sh",
        "nikto",
        "ollama",
        "powershell",
        "powershell.exe",
    ]

    return {
        name: shutil.which(name)
        for name in candidates
    }