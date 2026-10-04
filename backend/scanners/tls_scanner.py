import socket
import ssl
from datetime import datetime
from urllib.parse import urlparse


def scan_tls(url: str):

    parsed = urlparse(url)

    hostname = parsed.hostname

    if not hostname:
        return {
            "error": "Invalid hostname."
        }

    port = parsed.port or 443

    context = ssl.create_default_context()

    result = {
        "hostname": hostname,
        "port": port,
        "timestamp": datetime.now().isoformat(),
    }

    try:

        with socket.create_connection(
            (hostname, port),
            timeout=10,
        ) as sock:

            with context.wrap_socket(
                sock,
                server_hostname=hostname,
            ) as secure_sock:

                cert = secure_sock.getpeercert()

                result["tls_version"] = (
                    secure_sock.version()
                )

                result["cipher"] = (
                    secure_sock.cipher()
                )

                result["certificate_subject"] = str(
                    cert.get("subject")
                )

                result["certificate_issuer"] = str(
                    cert.get("issuer")
                )

                result["certificate_expiry"] = (
                    cert.get("notAfter")
                )

                result["status"] = "success"

    except Exception as exc:

        result["status"] = "error"
        result["error"] = str(exc)

    return result