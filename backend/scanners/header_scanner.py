import requests


SECURITY_HEADERS = {
    "strict-transport-security": (
        "Helps enforce HTTPS connections."
    ),
    "content-security-policy": (
        "Helps reduce browser-side injection impact."
    ),
    "x-content-type-options": (
        "Reduces MIME-sniffing behavior."
    ),
    "referrer-policy": (
        "Controls referrer information."
    ),
    "permissions-policy": (
        "Restricts browser capabilities."
    ),
}


def scan_headers(url: str):

    try:

        response = requests.get(
            url,
            timeout=15,
            allow_redirects=True,
            headers={
                "User-Agent": (
                    "BADSHAH-AI-Security-Scanner/1.0"
                )
            },
        )

        headers = {
            key.lower(): value
            for key, value
            in response.headers.items()
        }

        present = {}
        missing = {}

        for name, description in SECURITY_HEADERS.items():

            if name in headers:

                present[name] = {
                    "value": headers[name],
                    "description": description,
                }

            else:

                missing[name] = description

        return {
            "status_code": response.status_code,
            "final_url": response.url,
            "server": headers.get(
                "server",
                "",
            ),
            "content_type": headers.get(
                "content-type",
                "",
            ),
            "security_headers": present,
            "missing_security_headers": missing,
        }

    except requests.RequestException as exc:

        return {
            "error": str(exc)
        }