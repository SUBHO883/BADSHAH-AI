import json
import platform
import socket
import subprocess
from pathlib import Path

import psutil
import questionary
from rich import box
from rich.panel import Panel
from rich.table import Table

from backend.ai.ollama_client import OllamaClient, OllamaError
from backend.ai.security_agent import SecurityAgent
from backend.commands.bluetooth_commands import scan_bluetooth
from backend.commands.web_commands import run_web_assessment
from backend.commands.wifi_commands import (
    scan_wifi_networks,
    show_adapters,
)
from backend.config import (
    APP_NAME,
    APP_VERSION,
    REPORT_DIR,
    ensure_directories,
)
from backend.scanners.wifi_scanner import (
    discover_wifi_networks,
    get_wifi_adapters,
)
from backend.services.analyzer import (
    local_analysis,
)
from backend.services.evidence import save_evidence
from backend.services.report_generator import generate_report
from backend.utils.command_runner import run_command
from backend.utils.terminal_ui import (
    banner,
    console,
    error,
    info,
    menu,
    section,
    success,
    wait,
    warning,
)


# ============================================================
# INITIALIZATION
# ============================================================

ensure_directories()


# ============================================================
# GENERAL HELPERS
# ============================================================

def pause():
    wait()


def clear():
    console.clear()


def print_header(title: str):
    section(title)


# ============================================================
# SYSTEM INFORMATION
# ============================================================

def system_information():
    clear()
    banner()
    print_header("SYSTEM INFORMATION")

    hostname = socket.gethostname()

    try:
        local_ip = socket.gethostbyname(
            hostname
        )
    except socket.gaierror:
        local_ip = "Unavailable"

    table = Table(
        title="SYSTEM",
        box=box.ROUNDED,
    )

    table.add_column(
        "Property",
        style="bold red",
    )

    table.add_column(
        "Value",
    )

    table.add_row(
        "Application",
        APP_NAME,
    )

    table.add_row(
        "Version",
        APP_VERSION,
    )

    table.add_row(
        "Operating System",
        platform.system(),
    )

    table.add_row(
        "OS Version",
        platform.version(),
    )

    table.add_row(
        "Architecture",
        platform.machine(),
    )

    table.add_row(
        "Python",
        platform.python_version(),
    )

    table.add_row(
        "Hostname",
        hostname,
    )

    table.add_row(
        "Local IP",
        local_ip,
    )

    table.add_row(
        "CPU",
        f"{psutil.cpu_count(logical=True)} logical cores",
    )

    memory = psutil.virtual_memory()

    table.add_row(
        "RAM",
        f"{memory.total / (1024 ** 3):.2f} GB",
    )

    console.print(table)

    # Network adapters
    console.print()

    adapters = psutil.net_if_addrs()

    net_table = Table(
        title="NETWORK INTERFACES",
        box=box.ROUNDED,
    )

    net_table.add_column("Interface")
    net_table.add_column("Address")
    net_table.add_column("Type")

    for interface, addresses in adapters.items():

        for address in addresses:

            if address.family == socket.AF_INET:

                net_table.add_row(
                    interface,
                    address.address,
                    "IPv4",
                )

            elif address.family == socket.AF_INET6:

                net_table.add_row(
                    interface,
                    address.address,
                    "IPv6",
                )

    console.print(net_table)

    pause()


# ============================================================
# OLLAMA STATUS
# ============================================================

def ollama_status():
    clear()
    banner()
    print_header("OLLAMA AI STATUS")

    client = OllamaClient()

    if not client.health():

        console.print(
            Panel(
                "[bold red]OLLAMA OFFLINE[/bold red]\n\n"
                "BADSHAH AI could not connect to:\n"
                f"{client.base_url}",
                border_style="red",
            )
        )

        pause()
        return

    success(
        "Ollama local API is online."
    )

    try:

        models = client.models()

    except OllamaError as exc:

        error(str(exc))

        pause()
        return

    table = Table(
        title="LOCAL OLLAMA MODELS",
        box=box.ROUNDED,
    )

    table.add_column("Model")
    table.add_column("Selected")

    for model in models:

        selected = (
            "YES"
            if model == client.model
            else ""
        )

        table.add_row(
            model,
            selected,
        )

    console.print(table)

    info(
        "Configured Model",
        client.model,
    )

    pause()


# ============================================================
# WIFI LAB
# ============================================================

def wifi_adapter_details():
    clear()
    banner()
    show_adapters()
    pause()


def wifi_discovery():
    clear()
    banner()

    data = scan_wifi_networks()

    if data:
        save_evidence(
            "wifi_discovery",
            "local_wifi_environment",
            data,
        )

    pause()


def wifi_full_assessment():
    clear()
    banner()

    print_header(
        "FULL WI-FI SECURITY ASSESSMENT"
    )

    adapters = get_wifi_adapters()

    discovery = discover_wifi_networks()

    data = {
        "adapters": adapters,
        "discovery": discovery,
    }

    if discovery.get("error"):

        error(
            discovery["error"]
        )

        pause()
        return

    # Display adapter count
    info(
        "Wi-Fi Adapters",
        len(adapters),
    )

    # Display network count
    info(
        "Nearby Networks",
        discovery.get(
            "count",
            0,
        ),
    )

    # Local security analysis
    findings = local_analysis(
        "wifi",
        data,
    )

    console.print()

    print_header(
        "LOCAL SECURITY FINDINGS"
    )

    if not findings:

        success(
            "No local rule-based Wi-Fi findings detected."
        )

    else:

        for number, finding in enumerate(
            findings,
            1,
        ):

            console.print(
                Panel(
                    (
                        f"[bold]Title:[/bold] "
                        f"{finding.title}\n\n"
                        f"[bold]Severity:[/bold] "
                        f"{finding.severity}\n\n"
                        f"[bold]Description:[/bold] "
                        f"{finding.description}\n\n"
                        f"[bold]Impact:[/bold] "
                        f"{finding.impact}\n\n"
                        f"[bold]Remediation:[/bold] "
                        f"{finding.remediation}\n\n"
                        f"[bold]Verification:[/bold] "
                        f"{finding.verification}"
                    ),
                    title=f"FINDING {number}",
                    border_style="red",
                )
            )

    # Save evidence
    evidence_path = save_evidence(
        "wifi_assessment",
        "local_wifi_environment",
        data,
    )

    success(
        f"Evidence saved: {evidence_path}"
    )

    # Optional AI analysis
    ai_text = ""

    use_ai = questionary.confirm(
        "Run Ollama AI analysis on this evidence?",
        default=True,
    ).ask()

    if use_ai:

        try:

            agent = SecurityAgent()

            console.print(
                "\n[bold yellow]Running local AI analysis...[/bold yellow]"
            )

            ai_text = agent.analyze(
                "wifi",
                "local_wifi_environment",
                data,
            )

            console.print(
                Panel(
                    ai_text,
                    title="BADSHAH AI ANALYSIS",
                    border_style="red",
                )
            )

        except Exception as exc:

            error(
                f"AI analysis failed: {exc}"
            )

    # Report
    report_path = generate_report(
        "wifi_assessment",
        "local_wifi_environment",
        data,
        findings,
        ai_text,
    )

    success(
        f"Report saved: {report_path}"
    )

    pause()


def wifi_lab():
    while True:

        clear()
        banner()

        print_header(
            "WI-FI SECURITY LAB"
        )

        menu(
            [
                (
                    "1",
                    "Detect Wi-Fi adapters",
                ),
                (
                    "2",
                    "Discover nearby Wi-Fi networks",
                ),
                (
                    "3",
                    "Full Wi-Fi security assessment",
                ),
                (
                    "0",
                    "Back",
                ),
            ]
        )

        choice = questionary.select(
            "Select option:",
            choices=[
                "1",
                "2",
                "3",
                "0",
            ],
        ).ask()

        if choice == "1":
            wifi_adapter_details()

        elif choice == "2":
            wifi_discovery()

        elif choice == "3":
            wifi_full_assessment()

        elif choice == "0":
            return


# ============================================================
# BLUETOOTH LAB
# ============================================================

def bluetooth_lab():

    clear()
    banner()

    scan_bluetooth()

    pause()


# ============================================================
# WEBSITE LAB
# ============================================================

def website_lab():

    clear()
    banner()

    print_header(
        "AUTHORIZED WEBSITE SECURITY LAB"
    )

    console.print(
        Panel(
            "[yellow]Use this module only against websites "
            "you own or are explicitly authorized to assess.[/yellow]\n\n"
            "The assessment performs non-destructive checks "
            "such as HTTP/TLS information, security headers, "
            "basic link discovery and form inventory.",
            border_style="yellow",
        )
    )

    console.print()

    url = questionary.text(
        "Enter authorized website URL:"
    ).ask()

    if not url:

        warning(
            "No URL entered."
        )

        pause()
        return

    try:

        run_web_assessment(url)

    except Exception as exc:

        error(
            f"Website assessment failed: {exc}"
        )

    pause()


# ============================================================
# COMMAND / DIAGNOSTIC LAB
# ============================================================

def run_diagnostic(
    title: str,
    command: list[str],
):

    clear()
    banner()

    print_header(title)

    result = run_command(
        command,
        timeout=30,
    )

    info(
        "Command",
        result.command,
    )

    info(
        "Return Code",
        result.returncode,
    )

    console.print()

    if result.stdout:

        console.print(
            Panel(
                result.stdout,
                title="OUTPUT",
                border_style="red",
            )
        )

    if result.stderr:

        console.print(
            Panel(
                result.stderr,
                title="ERROR / STDERR",
                border_style="yellow",
            )
        )

    pause()


def diagnostic_lab():

    while True:

        clear()
        banner()

        print_header(
            "COMMAND / DIAGNOSTIC LAB"
        )

        menu(
            [
                (
                    "1",
                    "IP configuration",
                ),
                (
                    "2",
                    "IP configuration - full",
                ),
                (
                    "3",
                    "Routing table",
                ),
                (
                    "4",
                    "ARP table",
                ),
                (
                    "5",
                    "Active network connections",
                ),
                (
                    "6",
                    "Network interfaces",
                ),
                (
                    "0",
                    "Back",
                ),
            ]
        )

        choice = questionary.select(
            "Select diagnostic:",
            choices=[
                "1",
                "2",
                "3",
                "4",
                "5",
                "6",
                "0",
            ],
        ).ask()

        if choice == "1":

            run_diagnostic(
                "IP CONFIGURATION",
                ["ipconfig"],
            )

        elif choice == "2":

            run_diagnostic(
                "FULL IP CONFIGURATION",
                ["ipconfig", "/all"],
            )

        elif choice == "3":

            run_diagnostic(
                "ROUTING TABLE",
                ["route", "print"],
            )

        elif choice == "4":

            run_diagnostic(
                "ARP TABLE",
                ["arp", "-a"],
            )

        elif choice == "5":

            run_diagnostic(
                "ACTIVE NETWORK CONNECTIONS",
                ["netstat", "-ano"],
            )

        elif choice == "6":

            run_diagnostic(
                "NETWORK INTERFACES",
                [
                    "powershell",
                    "-NoProfile",
                    "-Command",
                    "Get-NetAdapter | "
                    "Format-Table -AutoSize",
                ],
            )

        elif choice == "0":
            return


# ============================================================
# AI SECURITY ASSISTANT
# ============================================================

def ai_assistant():

    clear()
    banner()

    print_header(
        "BADSHAH AI SECURITY ASSISTANT"
    )

    client = OllamaClient()

    if not client.health():

        error(
            "Ollama is not available."
        )

        info(
            "Expected API",
            client.base_url,
        )

        pause()
        return

    agent = SecurityAgent()

    console.print(
        Panel(
            "Local Ollama AI assistant is ready.\n\n"
            "Ask cybersecurity, system-security or "
            "defensive assessment questions.\n\n"
            "Type 'exit' to return.",
            border_style="red",
        )
    )

    while True:

        message = questionary.text(
            "You:"
        ).ask()

        if message is None:
            return

        message = message.strip()

        if not message:
            continue

        if message.lower() in {
            "exit",
            "quit",
            "back",
        }:
            return

        console.print(
            "\n[bold red]BADSHAH AI:[/bold red]"
        )

        try:

            answer = agent.chat(
                message
            )

            console.print(answer)

        except OllamaError as exc:

            error(str(exc))

        except Exception as exc:

            error(
                f"Unexpected AI error: {exc}"
            )

        console.print()


# ============================================================
# REPORT CENTER
# ============================================================

def get_report_files():

    REPORT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    return sorted(
        REPORT_DIR.rglob("*.txt"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )


def report_center():

    while True:

        clear()
        banner()

        print_header(
            "REPORT CENTER"
        )

        reports = get_report_files()

        if not reports:

            warning(
                "No reports have been generated yet."
            )

        else:

            table = Table(
                title=f"REPORTS ({len(reports)})",
                box=box.ROUNDED,
            )

            table.add_column("#")
            table.add_column("Report")
            table.add_column("Size")
            table.add_column("Path")

            for index, report in enumerate(
                reports,
                1,
            ):

                try:
                    size = report.stat().st_size
                except OSError:
                    size = 0

                table.add_row(
                    str(index),
                    report.name,
                    f"{size} bytes",
                    str(report),
                )

            console.print(table)

        console.print()

        choices = [
            "Open latest report",
            "Refresh",
            "Back",
        ]

        choice = questionary.select(
            "Report action:",
            choices=choices,
        ).ask()

        if choice == "Open latest report":

            if not reports:

                warning(
                    "There are no reports to open."
                )

                pause()
                continue

            latest = reports[0]

            try:

                content = latest.read_text(
                    encoding="utf-8"
                )

                clear()
                banner()

                print_header(
                    latest.name
                )

                console.print(
                    Panel(
                        content,
                        border_style="red",
                    )
                )

                pause()

            except OSError as exc:

                error(
                    f"Could not read report: {exc}"
                )

                pause()

        elif choice == "Refresh":

            continue

        elif choice == "Back":

            return


# ============================================================
# API SERVER
# ============================================================

def start_api_server():

    clear()
    banner()

    print_header(
        "LOCAL API SERVER"
    )

    console.print(
        Panel(
            "BADSHAH AI FastAPI server\n\n"
            "Host: 127.0.0.1\n"
            "Port: 8000\n\n"
            "API endpoints:\n"
            "/\n"
            "/api/health\n"
            "/api/wifi/adapters\n"
            "/api/wifi/discovery\n\n"
            "Press CTRL+C to stop the server.",
            border_style="red",
        )
    )

    try:

        import uvicorn

        uvicorn.run(
            "backend.main:app",
            host="127.0.0.1",
            port=8000,
            reload=False,
        )

    except KeyboardInterrupt:

        pass

    except Exception as exc:

        error(
            f"API server error: {exc}"
        )

        pause()


# ============================================================
# MAIN MENU
# ============================================================

def main():

    ensure_directories()

    while True:

        clear()
        banner()

        console.print(
            Panel(
                f"[bold]Version:[/bold] {APP_VERSION}\n"
                "[bold]Mode:[/bold] Local AI + Defensive Security Assessment",
                border_style="red",
            )
        )

        console.print()

        menu(
            [
                (
                    "1",
                    "Wi-Fi Security Lab",
                ),
                (
                    "2",
                    "Bluetooth Security Lab",
                ),
                (
                    "3",
                    "Website Security Lab",
                ),
                (
                    "4",
                    "Command / Diagnostic Lab",
                ),
                (
                    "5",
                    "AI Security Assistant",
                ),
                (
                    "6",
                    "Report Center",
                ),
                (
                    "7",
                    "System Information",
                ),
                (
                    "8",
                    "Ollama AI Status",
                ),
                (
                    "9",
                    "Start Local API Server",
                ),
                (
                    "0",
                    "Exit",
                ),
            ]
        )

        choice = questionary.select(
            "BADSHAH AI > Select:",
            choices=[
                "1",
                "2",
                "3",
                "4",
                "5",
                "6",
                "7",
                "8",
                "9",
                "0",
            ],
        ).ask()

        if choice == "1":

            wifi_lab()

        elif choice == "2":

            bluetooth_lab()

        elif choice == "3":

            website_lab()

        elif choice == "4":

            diagnostic_lab()

        elif choice == "5":

            ai_assistant()

        elif choice == "6":

            report_center()

        elif choice == "7":

            system_information()

        elif choice == "8":

            ollama_status()

        elif choice == "9":

            start_api_server()

        elif choice == "0":

            clear()

            console.print(
                Panel(
                    "[bold red]BADSHAH AI shutting down...[/bold red]\n\n"
                    "Security lab session ended.",
                    border_style="red",
                )
            )

            break


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()