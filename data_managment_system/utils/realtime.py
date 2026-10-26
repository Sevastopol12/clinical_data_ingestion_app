"""Pure helpers for realtime session-refresh decisions (no Reflex, no I/O)."""

from __future__ import annotations

from datetime import datetime


def should_refresh(
    *,
    expires_in: int,
    refresh_expires_at: datetime | None,
    now: datetime,
) -> bool:
    """Decide whether a ``session.expiring`` frame can actually be acted on.

    Refreshing rotates the access token *and* its paired refresh token. The sid may
    still be alive, but an expired refresh token cannot rotate: the backend answers
    ``refresh_invalid`` and ultimately closes with 4401. So we only ask for a refresh
    while the refresh token is still in the future, the warning window is positive,
    and both datetimes carry a timezone (naive values cannot be compared safely).
    """
    if expires_in <= 0 or refresh_expires_at is None:
        return False
    if (
        refresh_expires_at.tzinfo is None
        or refresh_expires_at.utcoffset() is None
        or now.tzinfo is None
        or now.utcoffset() is None
    ):
        return False
    return refresh_expires_at > now
