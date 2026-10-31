"""Outbound HTTP that never hands credentials to a host the user did not choose.

``urllib`` follows redirects and copies every header, ``Authorization`` and API-key headers included, to
the new address. A provider, mod, MCP server or remote agent that redirects to another host would then
receive the user's key. ``urlopen`` here follows redirects only within the same host (an http -> https
upgrade on that host is allowed) and refuses the rest.
"""

from __future__ import annotations

import urllib.error
import urllib.parse
import urllib.request
from typing import Any


def same_site(a: str, b: str) -> bool:
    """True when both URLs point at the same host and port (scheme may be upgraded from http to https)."""
    pa, pb = urllib.parse.urlsplit(a), urllib.parse.urlsplit(b)
    port = {"http": 80, "https": 443}
    if (pa.hostname or "").lower() != (pb.hostname or "").lower():
        return False
    if pa.scheme == "https" and pb.scheme == "http":
        return False  # never downgrade
    same_port = (pa.port or port.get(pa.scheme)) == (pb.port or port.get(pb.scheme))
    upgrade = pa.scheme == "http" and pb.scheme == "https" and not pa.port and not pb.port
    return same_port or upgrade


class _SameSiteRedirects(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # type: ignore[no-untyped-def]
        if not same_site(req.full_url, newurl):
            host = urllib.parse.urlsplit(newurl).hostname or newurl
            raise urllib.error.HTTPError(
                req.full_url, code, f"Refused a redirect to another host ({host}) so the API key is not sent there",
                headers, fp)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


_OPENER = urllib.request.build_opener(_SameSiteRedirects)


def urlopen(request: urllib.request.Request | str, timeout: float | None = None) -> Any:
    """Like ``urllib.request.urlopen``, but redirects to another host are refused."""
    return _OPENER.open(request, timeout=timeout)


__all__ = ["same_site", "urlopen"]
