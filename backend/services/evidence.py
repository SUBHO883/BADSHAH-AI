import json
from datetime import datetime

from backend.config import EVIDENCE_DIR


def save_evidence(
    scan_type: str,
    target: str,
    data: dict,
):

    EVIDENCE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    safe_target = "".join(
        char if char.isalnum() else "_"
        for char in target
    )[:80]

    filename = (
        f"{scan_type}_"
        f"{safe_target}_"
        f"{timestamp}.json"
    )

    path = EVIDENCE_DIR / filename

    path.write_text(
        json.dumps(
            data,
            indent=2,
            ensure_ascii=False,
            default=str,
        ),
        encoding="utf-8",
    )

    return path