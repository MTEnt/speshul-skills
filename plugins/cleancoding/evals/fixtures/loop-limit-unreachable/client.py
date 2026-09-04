"""Client for the internal licensing service."""

import urllib.request


def license_status(host: str = "http://licensing.internal.invalid:9") -> str:
    with urllib.request.urlopen(host + "/status", timeout=0.5) as response:  # noqa: S310
        return response.read().decode("utf-8")
