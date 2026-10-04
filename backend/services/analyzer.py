from typing import Any

from backend.ai.security_agent import SecurityAgent
from backend.services.risk_engine import (
    analyze_web,
    analyze_wifi,
)


SUPPORTED_LOCAL_ANALYSIS = {
    "wifi",
    "web",
}

SUPPORTED_DIAGNOSTICS = {
    "interfaces",
    "routes",
    "wireless_interfaces",
    "network_status",
}


def local_analysis(
    scan_type: str,
    data: dict,
) -> Any:
    """
    Perform deterministic local analysis.

    This layer does not use AI.
    It applies the existing risk-engine rules
    to collected evidence.
    """

    if not isinstance(scan_type, str):
        return {
            "ok": False,
            "error": "scan_type must be a string.",
        }

    scan_type = scan_type.strip().lower()

    if not isinstance(data, dict):
        return {
            "ok": False,
            "error": "data must be a dictionary.",
        }

    if scan_type == "wifi":
        return analyze_wifi(data)

    if scan_type == "web":
        return analyze_web(data)

    return {
        "ok": False,
        "error": "Unsupported local analysis type.",
        "supported_types": sorted(
            SUPPORTED_LOCAL_ANALYSIS
        ),
    }


def ai_analysis(
    scan_type: str,
    target: str,
    data: dict,
) -> str:
    """
    Analyze collected evidence using the local Ollama AI.

    The AI receives evidence only.
    It does not execute commands.
    """

    if not isinstance(scan_type, str):
        raise TypeError("scan_type must be a string.")

    if not isinstance(target, str):
        raise TypeError("target must be a string.")

    if not isinstance(data, dict):
        raise TypeError("data must be a dictionary.")

    scan_type = scan_type.strip().lower()
    target = target.strip()

    if not scan_type:
        raise ValueError("scan_type cannot be empty.")

    if not target:
        target = "local system"

    agent = SecurityAgent()

    return agent.analyze(
        scan_type=scan_type,
        target=target,
        evidence=data,
    )


def diagnostic_analysis(
    diagnostic: str,
    timeout: int = 15,
) -> dict[str, Any]:
    """
    Run one approved system diagnostic and let the
    local AI explain the resulting evidence.

    No arbitrary command is accepted.
    """

    if not isinstance(diagnostic, str):
        return {
            "ok": False,
            "error": "diagnostic must be a string.",
        }

    diagnostic = diagnostic.strip().lower()

    if diagnostic not in SUPPORTED_DIAGNOSTICS:
        return {
            "ok": False,
            "diagnostic": diagnostic,
            "error": "Unsupported diagnostic.",
            "available_diagnostics": sorted(
                SUPPORTED_DIAGNOSTICS
            ),
        }

    if not isinstance(timeout, int):
        return {
            "ok": False,
            "diagnostic": diagnostic,
            "error": "timeout must be an integer.",
        }

    if timeout <= 0:
        return {
            "ok": False,
            "diagnostic": diagnostic,
            "error": "timeout must be greater than 0.",
        }

    agent = SecurityAgent()

    return agent.diagnose_and_explain(
        diagnostic=diagnostic,
        timeout=timeout,
    )


def analyze(
    scan_type: str,
    target: str,
    data: dict,
) -> dict[str, Any]:
    """
    Combined analysis pipeline.

    1. Run deterministic local risk analysis.
    2. Send the same evidence to local AI.
    3. Return both results separately.
    """

    local_result = local_analysis(
        scan_type=scan_type,
        data=data,
    )

    # Do not call AI if local analysis itself failed.
    if isinstance(local_result, dict) and not local_result.get("ok", True):
        return {
            "ok": False,
            "scan_type": scan_type,
            "target": target,
            "local_analysis": local_result,
            "ai_analysis": None,
        }

    ai_result = ai_analysis(
        scan_type=scan_type,
        target=target,
        data=data,
    )

    return {
        "ok": True,
        "scan_type": scan_type.strip().lower(),
        "target": target.strip() if isinstance(target, str) else target,
        "local_analysis": local_result,
        "ai_analysis": ai_result,
    }