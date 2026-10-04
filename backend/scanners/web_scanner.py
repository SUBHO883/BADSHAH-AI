from datetime import datetime
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from backend.scanners.header_scanner import (
    scan_headers,
)
from backend.scanners.tls_scanner import (
    scan_tls,
)


def normalize_url(url: str):

    url = url.strip()

    if not url:
        raise ValueError(
            "URL cannot be empty."
        )

    if not url.startswith(
        ("http://", "https://")
    ):
        url = "https://" + url

    return url


def scan_website(url: str):

    url = normalize_url(url)

    result = {
        "target": url,
        "timestamp": datetime.now().isoformat(),
    }

    try:

        response = requests.get(
            url,
            timeout=15,
            allow_redirects=True,
            headers={
                "User-Agent":
                    "BADSHAH-AI-Security-Scanner/1.0"
            },
        )

        result["status_code"] = (
            response.status_code
        )

        result["final_url"] = str(
            response.url
        )

        result["response_headers"] = dict(
            response.headers
        )

        final_url = str(response.url)

        if final_url.startswith("https://"):

            result["tls"] = scan_tls(
                final_url
            )

        else:

            result["tls"] = {
                "status": "not_applicable"
            }

        result["header_analysis"] = (
            scan_headers(
                final_url
            )
        )

        soup = BeautifulSoup(
            response.text,
            "html.parser",
        )

        title = (
            soup.title.string.strip()
            if (
                soup.title
                and soup.title.string
            )
            else ""
        )

        result["title"] = title

        links = []

        for anchor in soup.find_all(
            "a",
            href=True,
        ):

            links.append(
                urljoin(
                    final_url,
                    anchor["href"],
                )
            )

        result["links"] = list(
            dict.fromkeys(links)
        )[:100]

        forms = []

        for form in soup.find_all("form"):

            forms.append(
                {
                    "method": form.get(
                        "method",
                        "GET",
                    ).upper(),
                    "action": urljoin(
                        final_url,
                        form.get(
                            "action",
                            "",
                        ),
                    ),
                    "inputs": [
                        {
                            "name": item.get(
                                "name"
                            ),
                            "type": item.get(
                                "type",
                                "text",
                            ),
                        }
                        for item in form.find_all(
                            "input"
                        )
                    ],
                }
            )

        result["forms"] = forms

        return result

    except requests.RequestException as exc:

        result["error"] = str(exc)

        return result