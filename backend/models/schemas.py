from dataclasses import dataclass, field
from typing import Any


@dataclass
class Finding:
    title: str
    severity: str
    description: str
    impact: str
    remediation: str
    verification: str
    evidence: list[str] = field(default_factory=list)


@dataclass
class ScanResult:
    scan_type: str
    target: str
    timestamp: str
    data: dict[str, Any]
    findings: list[Finding] = field(
        default_factory=list
    )