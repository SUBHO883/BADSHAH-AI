from backend.models.schemas import Finding


def analyze_wifi(data: dict):

    findings = []

    discovery = data.get(
        "discovery",
        {},
    )

    for network in discovery.get(
        "networks",
        [],
    ):

        auth = network.get(
            "network_authentication",
            "",
        ).lower()

        encryption = network.get(
            "network_encryption",
            "",
        ).lower()

        ssid = network.get(
            "ssid",
            "",
        )

        evidence = [
            f"SSID: {ssid}",
            f"Authentication: {auth}",
            f"Encryption: {encryption}",
        ]

        if (
            "open" in auth
            or "open" in encryption
            or not auth
        ):

            findings.append(
                Finding(
                    title=(
                        f"Open/unknown Wi-Fi security: "
                        f"{ssid}"
                    ),
                    severity="HIGH",
                    description=(
                        "The network appears to have "
                        "no clearly identified wireless "
                        "authentication/encryption."
                    ),
                    impact=(
                        "Unprotected wireless traffic "
                        "may be exposed to nearby users."
                    ),
                    remediation=(
                        "Use WPA2-Personal/AES or "
                        "WPA3 with a strong unique "
                        "passphrase."
                    ),
                    verification=(
                        "Repeat the Wi-Fi discovery "
                        "scan and verify the reported "
                        "authentication and encryption."
                    ),
                    evidence=evidence,
                )
            )

        elif "wep" in encryption:

            findings.append(
                Finding(
                    title=(
                        f"Legacy WEP configuration: "
                        f"{ssid}"
                    ),
                    severity="CRITICAL",
                    description=(
                        "WEP is a legacy wireless "
                        "security mechanism."
                    ),
                    impact=(
                        "WEP does not provide modern "
                        "wireless security."
                    ),
                    remediation=(
                        "Replace WEP with WPA2-AES "
                        "or WPA3."
                    ),
                    verification=(
                        "Repeat the discovery scan "
                        "after changing the configuration."
                    ),
                    evidence=evidence,
                )
            )

    return findings


def analyze_web(data: dict):

    findings = []

    header_data = data.get(
        "header_analysis",
        {},
    )

    missing = header_data.get(
        "missing_security_headers",
        {},
    )

    if missing:

        findings.append(
            Finding(
                title=(
                    "Missing recommended "
                    "HTTP security headers"
                ),
                severity="MEDIUM",
                description=(
                    "One or more commonly recommended "
                    "browser security headers were not "
                    "observed."
                ),
                impact=(
                    "Missing headers can reduce browser-side "
                    "defense-in-depth."
                ),
                remediation=(
                    "Review and deploy appropriate "
                    "security headers based on application "
                    "requirements."
                ),
                verification=(
                    "Repeat the header scan and inspect "
                    "the HTTP response headers."
                ),
                evidence=[
                    str(item)
                    for item in missing.keys()
                ],
            )
        )

    final_url = data.get(
        "final_url",
        "",
    )

    if final_url.startswith(
        "http://"
    ):

        findings.append(
            Finding(
                title="Website served over HTTP",
                severity="HIGH",
                description=(
                    "The final observed URL uses "
                    "unencrypted HTTP."
                ),
                impact=(
                    "Traffic can be exposed or modified "
                    "by network attackers."
                ),
                remediation=(
                    "Enable HTTPS and redirect HTTP "
                    "traffic to HTTPS."
                ),
                verification=(
                    "Repeat the scan and verify the "
                    "final URL is HTTPS."
                ),
                evidence=[
                    f"Final URL: {final_url}"
                ],
            )
        )

    return findings