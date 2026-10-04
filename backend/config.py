import os
from pathlib import Path

from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parent.parent

load_dotenv(ROOT_DIR / ".env")


APP_NAME = os.getenv("APP_NAME", "BADSHAH AI")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")

OLLAMA_BASE_URL = os.getenv(
    "OLLAMA_BASE_URL",
    "http://127.0.0.1:11434",
)

OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "gemma3:4b",
)

OLLAMA_TIMEOUT = int(
    os.getenv("OLLAMA_TIMEOUT", "120")
)

DATA_DIR = ROOT_DIR / os.getenv(
    "DATA_DIR",
    "data",
)

SCAN_DIR = ROOT_DIR / os.getenv(
    "SCAN_DIR",
    "data/scans",
)

EVIDENCE_DIR = ROOT_DIR / os.getenv(
    "EVIDENCE_DIR",
    "data/evidence",
)

REPORT_DIR = ROOT_DIR / os.getenv(
    "REPORT_DIR",
    "data/reports",
)


def ensure_directories():
    for directory in (
        DATA_DIR,
        SCAN_DIR,
        EVIDENCE_DIR,
        REPORT_DIR,
    ):
        directory.mkdir(
            parents=True,
            exist_ok=True,
        )