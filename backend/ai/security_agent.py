from typing import Any

from backend.ai.ollama_client import OllamaClient
from backend.ai.prompts import (
    build_analysis_prompt,
    build_chat_prompt,
)
from backend.services.command_service import run_diagnostic
from backend.services.tool_registry import get_tool_inventory


class SecurityAgent:
    """
    BADSHAH AI security agent.

    Features:
    - Local AI chat through Ollama
    - Platform and installed-tool awareness
    - Approved, read-only system diagnostics
    - AI-based explanation of collected evidence

    Arbitrary shell commands are never executed.
    """

    ALLOWED_DIAGNOSTICS = {
        "interfaces",
        "routes",
        "wireless_interfaces",
        "network_status",
    }

    def __init__(self) -> None:
        self.client = OllamaClient()
        self.history: list[dict[str, str]] = []

    # --------------------------------------------------
    # ENVIRONMENT
    # --------------------------------------------------

    def get_environment(self) -> dict[str, Any]:
        """Return detected platform and installed tools."""

        try:
            inventory = get_tool_inventory()

            installed_tools = [
                item["name"]
                for item in inventory.get("tools", [])
                if item.get("installed", False)
            ]

            return {
                "system": inventory.get("system", {}),
                "installed_security_tools": installed_tools,
            }

        except Exception as exc:
            return {
                "error": str(exc),
            }

    # --------------------------------------------------
    # NORMAL AI CHAT
    # --------------------------------------------------

    def chat(self, message: str) -> str:
        """Send a message to the local Ollama model."""

        if not isinstance(message, str):
            raise TypeError("message must be a string.")

        message = message.strip()

        if not message:
            return "Please enter a message."

        environment = self.get_environment()

        prompt = build_chat_prompt(
            message=message,
            history=self.history,
            environment=environment,
        )

        answer = self.client.generate(prompt)

        if not isinstance(answer, str):
            answer = str(answer)

        self.history.extend(
            [
                {
                    "role": "user",
                    "content": message,
                },
                {
                    "role": "assistant",
                    "content": answer,
                },
            ]
        )

        # Keep recent conversation history.
        self.history = self.history[-40:]

        return answer

    # --------------------------------------------------
    # SECURITY EVIDENCE ANALYSIS
    # --------------------------------------------------

    def analyze(
        self,
        scan_type: str,
        target: str,
        evidence: dict[str, Any],
    ) -> str:
        """
        Analyze supplied evidence using local Ollama AI.

        This method preserves compatibility with
        backend.services.analyzer.
        """

        if not isinstance(scan_type, str):
            raise TypeError("scan_type must be a string.")

        if not isinstance(target, str):
            raise TypeError("target must be a string.")

        if not isinstance(evidence, dict):
            raise TypeError("evidence must be a dictionary.")

        scan_type = scan_type.strip().lower()
        target = target.strip()

        if not scan_type:
            raise ValueError("scan_type cannot be empty.")

        if not target:
            target = "local system"

        prompt = build_analysis_prompt(
            scan_type=scan_type,
            target=target,
            evidence=evidence,
        )

        answer = self.client.generate(prompt)

        return str(answer)

    # --------------------------------------------------
    # SAFE SYSTEM DIAGNOSTICS
    # --------------------------------------------------

    def diagnose(
        self,
        diagnostic: str,
        timeout: int = 15,
    ) -> dict[str, Any]:
        """
        Run an approved diagnostic.

        Only predefined diagnostic names are accepted.
        """

        if not isinstance(diagnostic, str):
            return {
                "ok": False,
                "error": "Diagnostic must be a string.",
            }

        diagnostic = diagnostic.strip().lower()

        if diagnostic not in self.ALLOWED_DIAGNOSTICS:
            return {
                "ok": False,
                "diagnostic": diagnostic,
                "error": "Diagnostic is not allowed.",
                "available_diagnostics": sorted(
                    self.ALLOWED_DIAGNOSTICS
                ),
            }

        try:
            result = run_diagnostic(
                diagnostic=diagnostic,
                timeout=timeout,
            )

            return {
                "ok": bool(result.get("ok", False)),
                "diagnostic": diagnostic,
                "result": result,
            }

        except Exception as exc:
            return {
                "ok": False,
                "diagnostic": diagnostic,
                "error": str(exc),
            }

    # --------------------------------------------------
    # EXPLAIN DIAGNOSTIC RESULTS
    # --------------------------------------------------

    def explain_diagnostic(
        self,
        diagnostic: str,
        result: dict[str, Any],
    ) -> str:
        """Explain diagnostic evidence using local AI."""

        if not isinstance(diagnostic, str):
            raise TypeError("diagnostic must be a string.")

        if not isinstance(result, dict):
            raise TypeError("result must be a dictionary.")

        diagnostic = diagnostic.strip().lower()

        if diagnostic not in self.ALLOWED_DIAGNOSTICS:
            raise ValueError(
                f"Unsupported diagnostic: {diagnostic}"
            )

        prompt = build_analysis_prompt(
            scan_type=diagnostic,
            target="local system",
            evidence=result,
        )

        answer = self.client.generate(prompt)

        return str(answer)

    # --------------------------------------------------
    # DIAGNOSE AND EXPLAIN
    # --------------------------------------------------

    def diagnose_and_explain(
        self,
        diagnostic: str,
        timeout: int = 15,
    ) -> dict[str, Any]:
        """
        Run an approved diagnostic and explain its results.

        The diagnostic runs first. Ollama receives the
        resulting evidence and does not execute commands.
        """

        diagnostic_result = self.diagnose(
            diagnostic=diagnostic,
            timeout=timeout,
        )

        if not diagnostic_result.get("ok", False):
            return {
                "ok": False,
                "diagnostic": diagnostic,
                "result": diagnostic_result,
                "analysis": None,
            }

        try:
            analysis = self.explain_diagnostic(
                diagnostic=diagnostic,
                result=diagnostic_result,
            )

            return {
                "ok": True,
                "diagnostic": diagnostic,
                "result": diagnostic_result,
                "analysis": analysis,
            }

        except Exception as exc:
            return {
                "ok": False,
                "diagnostic": diagnostic,
                "result": diagnostic_result,
                "analysis": None,
                "error": (
                    "Diagnostic succeeded, but AI analysis failed: "
                    f"{exc}"
                ),
            }
