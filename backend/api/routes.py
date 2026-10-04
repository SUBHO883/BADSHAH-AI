from typing import Any, Literal

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from backend.config import APP_NAME, APP_VERSION
from backend.scanners.wifi_scanner import (
    discover_wifi_networks,
    get_wifi_adapters,
)
from backend.ai.security_agent import SecurityAgent
from backend.services.tool_registry import get_tool_inventory
from backend.services.analyzer import (
    analyze as run_analysis,
    diagnostic_analysis,
)


router = APIRouter()

# Keep one agent instance so chat history can persist
# while this API process is running.
_agent = SecurityAgent()


# --------------------------------------------------
# REQUEST MODELS
# --------------------------------------------------

class ChatRequest(BaseModel):
    message: str = Field(
        ...,
        min_length=1,
        max_length=12000,
        description="Message for BADSHAH AI",
    )


class AnalysisRequest(BaseModel):
    scan_type: Literal["wifi", "web"]
    target: str = Field(
        default="local system",
        max_length=500,
    )
    evidence: dict[str, Any]


# --------------------------------------------------
# HEALTH
# --------------------------------------------------

@router.get("/health")
def health():
    """Check whether the API is responding."""

    return {
        "status": "ok",
        "app": APP_NAME,
        "version": APP_VERSION,
    }


# --------------------------------------------------
# ENVIRONMENT
# --------------------------------------------------

@router.get("/environment")
def environment():
    """Return detected platform and available tool inventory."""

    try:
        return get_tool_inventory()

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Environment detection failed: {exc}",
        ) from exc


# --------------------------------------------------
# AI CHAT
# --------------------------------------------------

@router.post("/chat")
def chat(request: ChatRequest):
    """Send a message to the local BADSHAH AI model."""

    message = request.message.strip()

    if not message:
        raise HTTPException(
            status_code=422,
            detail="Message cannot be empty.",
        )

    try:
        answer = _agent.chat(message)

        return {
            "ok": True,
            "message": message,
            "response": answer,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=(
                "BADSHAH AI could not generate a response. "
                "Check whether Ollama is running and the "
                "configured model is available."
            ),
        ) from exc


# --------------------------------------------------
# SYSTEM DIAGNOSTICS
# --------------------------------------------------

@router.post("/diagnostics/{diagnostic}")
def diagnostics(
    diagnostic: str,
    timeout: int = Query(default=15, ge=1, le=60),
):
    """
    Run an approved, read-only system diagnostic.

    Only registered diagnostic names are accepted.
    """

    diagnostic = diagnostic.strip().lower()

    try:
        result = diagnostic_analysis(
            diagnostic=diagnostic,
            timeout=timeout,
        )

        return result

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Diagnostic request failed: {exc}",
        ) from exc


# --------------------------------------------------
# EVIDENCE ANALYSIS
# --------------------------------------------------

@router.post("/analyze")
def analyze(request: AnalysisRequest):
    """
    Analyze supplied Wi-Fi or web assessment evidence.

    This endpoint analyzes supplied evidence. It does not
    automatically scan arbitrary external targets.
    """

    target = request.target.strip() or "local system"

    try:
        result = run_analysis(
            scan_type=request.scan_type,
            target=target,
            data=request.evidence,
        )

        return result

    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=(
                "Evidence analysis failed. Check the supplied "
                "evidence, risk-engine implementation, and "
                "Ollama availability."
            ),
        ) from exc


# --------------------------------------------------
# EXISTING WI-FI ENDPOINTS
# --------------------------------------------------

@router.get("/wifi/adapters")
def wifi_adapters():
    """Return available Wi-Fi adapters."""

    try:
        return {
            "adapters": get_wifi_adapters(),
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Wi-Fi adapter discovery failed: {exc}",
        ) from exc


@router.get("/wifi/discovery")
def wifi_discovery():
    """Discover nearby Wi-Fi networks where supported."""

    try:
        return discover_wifi_networks()

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Wi-Fi discovery failed: {exc}",
        ) from exc
