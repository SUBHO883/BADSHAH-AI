import os
import platform
import shutil
import subprocess
from pathlib import Path
from typing import Any

LINUX_COMMANDS = {
    "interfaces": ["ip", "-br", "link"],
    "routes": ["ip", "route"],
    "wireless_interfaces": ["iw", "dev"],
    "network_status": ["nmcli", "device", "status"],
}

WINDOWS_DIAGNOSTICS = [
    "interfaces",
    "routes",
    "wireless_interfaces",
    "network_status",
]


def _find_windows_powershell() -> str | None:
    """Locate PowerShell even when it is absent from PATH."""
    candidates = [
        shutil.which("powershell.exe"),
        shutil.which("powershell"),
        shutil.which("pwsh.exe"),
        shutil.which("pwsh"),
    ]

    system_root = Path(os.environ.get("SystemRoot", r"C:\Windows"))

    candidates.extend(
        [
            str(
                system_root
                / "System32"
                / "WindowsPowerShell"
                / "v1.0"
                / "powershell.exe"
            ),
            str(
                system_root
                / "Sysnative"
                / "WindowsPowerShell"
                / "v1.0"
                / "powershell.exe"
            ),
        ]
    )

    for candidate in candidates:
        if not candidate:
            continue

        try:
            if Path(candidate).is_file():
                return candidate
        except (OSError, ValueError):
            continue

    return None


def _find_windows_executable(name: str) -> str | None:
    """Locate a Windows executable using PATH or System32."""
    executable = shutil.which(name)

    if executable:
        return executable

    system_root = Path(os.environ.get("SystemRoot", r"C:\Windows"))

    candidates = [
        system_root / "System32" / name,
        system_root / "System32" / f"{name}.exe",
    ]

    for candidate in candidates:
        try:
            if candidate.is_file():
                return str(candidate)
        except (OSError, ValueError):
            continue

    return None


def _windows_command(
    diagnostic: str,
) -> tuple[list[str] | None, str | None]:
    """Build an approved, non-destructive Windows diagnostic."""
    if diagnostic == "interfaces":
        powershell = _find_windows_powershell()

        if powershell:
            return [
                powershell,
                "-NoLogo",
                "-NoProfile",
                "-NonInteractive",
                "-Command",
                (
                    "Get-NetAdapter | "
                    "Format-Table Name, Status, MacAddress, "
                    "LinkSpeed -AutoSize"
                ),
            ], None

        netsh = _find_windows_executable("netsh")

        if netsh:
            return [
                netsh,
                "interface",
                "show",
                "interface",
            ], None

        return None, (
            "Could not locate PowerShell or netsh. "
            "Check your Windows installation and PATH."
        )

    if diagnostic == "routes":
        route = _find_windows_executable("route")

        if route:
            return [route, "print"], None

        return None, "Could not locate the Windows route executable."

    if diagnostic == "wireless_interfaces":
        netsh = _find_windows_executable("netsh")

        if netsh:
            return [
                netsh,
                "wlan",
                "show",
                "interfaces",
            ], None

        return None, "Could not locate the Windows netsh executable."

    if diagnostic == "network_status":
        ipconfig = _find_windows_executable("ipconfig")
        if ipconfig:
            return [ipconfig, "/all"], None

        netsh = _find_windows_executable("netsh")
        if netsh:
            return [
                netsh,
                "wlan",
                "show",
                "interfaces",
            ], None

        return None, "Could not locate a supported network status command."

    return None, "Unknown diagnostic."


def run_diagnostic(
    diagnostic: str,
    timeout: int = 15,
) -> dict[str, Any]:
    """
    Run a predefined system diagnostic on Windows or Linux.

    Only registered diagnostics are allowed.
    Arbitrary shell commands are never executed.
    """
    if not isinstance(diagnostic, str):
        return {
            "ok": False,
            "error": "Diagnostic must be a string.",
        }

    diagnostic = diagnostic.strip().lower()
    if not diagnostic:
        return {
            "ok": False,
            "diagnostic": diagnostic,
            "error": "Diagnostic must be a non-empty string.",
        }

    system = platform.system().lower()

    if not isinstance(timeout, int) or isinstance(timeout, bool):
        return {
            "ok": False,
            "diagnostic": diagnostic,
            "error": "Timeout must be an integer.",
        }

    if not 1 <= timeout <= 60:
        return {
            "ok": False,
            "diagnostic": diagnostic,
            "error": "Timeout must be between 1 and 60 seconds.",
        }

    if system == "linux":
        command = LINUX_COMMANDS.get(diagnostic)

        if command is None:
            return {
                "ok": False,
                "diagnostic": diagnostic,
                "error": "Unknown diagnostic.",
                "available_diagnostics": sorted(LINUX_COMMANDS),
            }

    elif system == "windows":
        command, error = _windows_command(diagnostic)

        if error:
            return {
                "ok": False,
                "diagnostic": diagnostic,
                "error": error,
            }

        if command is None:
            return {
                "ok": False,
                "diagnostic": diagnostic,
                "error": "Unknown diagnostic.",
                "available_diagnostics": WINDOWS_DIAGNOSTICS,
            }

    else:
        return {
            "ok": False,
            "diagnostic": diagnostic,
            "error": f"Unsupported operating system: {system}",
        }

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            shell=False,
            encoding="utf-8",
            errors="replace",
            check=False,
        )

        return {
            "ok": result.returncode == 0,
            "diagnostic": diagnostic,
            "command": command,
            "returncode": result.returncode,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
        }

    except FileNotFoundError:
        return {
            "ok": False,
            "diagnostic": diagnostic,
            "command": command,
            "error": f"Executable not found: {command[0]}",
        }

    except subprocess.TimeoutExpired:
        return {
            "ok": False,
            "diagnostic": diagnostic,
            "command": command,
            "error": f"Diagnostic timed out after {timeout} seconds.",
        }

    except OSError as exc:
        return {
            "ok": False,
            "diagnostic": diagnostic,
            "command": command,
            "error": f"Operating system error: {exc}",
        }
