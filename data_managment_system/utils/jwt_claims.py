"""Unverified JWT payload helpers (sid only, never for authorization)."""

import base64
import json
import re

_SID_RE = re.compile(r"^[A-Za-z0-9._-]{1,128}$")


def extract_sid(token: str) -> str:
    """Return the opaque ``sid`` claim from a JWT without verifying it.

    Raises:
        ValueError: If the token is malformed or ``sid`` is missing/invalid.
    """
    try:
        parts = token.split(".")
        if len(parts) != 3:
            raise ValueError("malformed token")
        payload_segment = parts[1]
        padding = "=" * (-len(payload_segment) % 4)
        raw = base64.urlsafe_b64decode(payload_segment + padding)
        payload = json.loads(raw.decode("utf-8"))
    except ValueError:
        raise
    except Exception as exc:
        raise ValueError("malformed token") from exc
    sid = payload.get("sid") if isinstance(payload, dict) else None
    if not isinstance(sid, str) or not _SID_RE.match(sid):
        raise ValueError("invalid sid")
    return sid
