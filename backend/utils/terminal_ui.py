from rich import box
from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text


console = Console()


def clear_screen():
    console.clear()


def banner():
    clear_screen()

    title = Text()

    title.append(
        "B A D S H A H   A I\n",
        style="bold red",
    )

    title.append(
        "AI CYBER SECURITY LAB",
        style="bold white",
    )

    console.print(
        Panel(
            Align.center(title),
            border_style="red",
            box=box.DOUBLE,
            padding=(1, 4),
        )
    )


def section(title: str):
    console.print()

    console.print(
        Panel(
            f"[bold white]{title}[/bold white]",
            border_style="red",
        )
    )


def menu(items):
    table = Table(
        show_header=False,
        box=box.SIMPLE,
        padding=(0, 2),
    )

    table.add_column(
        "Key",
        style="bold red",
        width=6,
    )

    table.add_column(
        "Option",
        style="white",
    )

    for key, label in items:
        table.add_row(
            f"[{key}]",
            label,
        )

    console.print(table)


def info(label: str, value):
    console.print(
        f"[bold red]{label}[/bold red] : {value}"
    )


def success(message: str):
    console.print(
        f"[bold green][+] {message}[/bold green]"
    )


def warning(message: str):
    console.print(
        f"[bold yellow][!] {message}[/bold yellow]"
    )


def error(message: str):
    console.print(
        f"[bold red][X] {message}[/bold red]"
    )


def wait():
    console.input(
        "\n[dim]Press ENTER to continue...[/dim]"
    )


def show_table(title, columns, rows):
    table = Table(
        title=title,
        box=box.ROUNDED,
    )

    for column in columns:
        table.add_column(
            str(column),
            overflow="fold",
        )

    for row in rows:
        table.add_row(
            *[str(x) for x in row]
        )

    console.print(table)