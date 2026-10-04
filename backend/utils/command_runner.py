import subprocess
from dataclasses import dataclass


@dataclass
class CommandResult:
    command: str
    returncode: int
    stdout: str
    stderr: str


def run_command(
    command: list[str],
    timeout: int = 30,
) -> CommandResult:

    try:
        process = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            shell=False,
            encoding="utf-8",
            errors="replace",
        )

        return CommandResult(
            command=" ".join(command),
            returncode=process.returncode,
            stdout=process.stdout,
            stderr=process.stderr,
        )

    except subprocess.TimeoutExpired as exc:
        stdout = (
            exc.stdout
            if isinstance(exc.stdout, str)
            else ""
        )

        return CommandResult(
            command=" ".join(command),
            returncode=-1,
            stdout=stdout,
            stderr="Command timed out.",
        )

    except OSError as exc:
        return CommandResult(
            command=" ".join(command),
            returncode=-1,
            stdout="",
            stderr=str(exc),
        )