from backend.scanners.web_scanner import (
    scan_website,
)
from backend.services.analyzer import (
    ai_analysis,
    local_analysis,
)
from backend.services.evidence import (
    save_evidence,
)
from backend.services.report_generator import (
    generate_report,
)
from backend.utils.terminal_ui import (
    error,
    info,
    section,
    success,
)


def run_web_assessment(url: str):

    section(
        f"WEBSITE SECURITY ASSESSMENT: {url}"
    )

    data = scan_website(url)

    if data.get("error"):

        error(data["error"])

        return None

    info(
        "HTTP Status",
        data.get("status_code"),
    )

    info(
        "Final URL",
        data.get("final_url"),
    )

    info(
        "Page Title",
        data.get("title"),
    )

    info(
        "Discovered Links",
        len(data.get("links", [])),
    )

    info(
        "Forms",
        len(data.get("forms", [])),
    )

    findings = local_analysis(
        "web",
        data,
    )

    evidence_path = save_evidence(
        "web",
        url,
        data,
    )

    success(
        f"Evidence saved: {evidence_path}"
    )

    ai_text = ""

    try:

        ai_text = ai_analysis(
            "web",
            url,
            data,
        )

    except Exception as exc:

        error(
            f"AI analysis failed: {exc}"
        )

    report_path = generate_report(
        "web",
        url,
        data,
        findings,
        ai_text,
    )

    success(
        f"Report saved: {report_path}"
    )

    return {
        "data": data,
        "findings": findings,
        "report": str(report_path),
    }