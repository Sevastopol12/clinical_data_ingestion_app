import re

from unidecode import unidecode  # pyright: ignore[reportAttributeAccessIssue]

_SEPARATORS = re.compile(r"[^a-z0-9]+")


def normalize_column_name(value: object) -> str:
    """Return a lowercase snake-case column name or reject blank names."""
    # TODO(verify D8): Vietnamese, unidecode maps đ -> d
    normalized = _SEPARATORS.sub("_", unidecode(str(value)).lower().strip()).strip("_")
    if not normalized:
        raise ValueError("Column name must contain at least one letter or digit")
    return normalized


__all__ = ["normalize_column_name"]
