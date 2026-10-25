"""Proposed identical parent/child allowlist guard for one read-only list query.

This file is source for two separately reviewed transport successors. It is
not imported by either active transport and grants no execution authority.
"""

from datetime import date
import re

BASE = "/api/v1/appointments"
DIARY_QUERY = re.compile(
    r"date_from=(\d{4}-\d{2}-\d{2})T00%3A00%3A00%2B10%3A00"
    r"&date_to=(\d{4}-\d{2}-\d{2})T00%3A00%3A00%2B10%3A00\Z"
)


def valid_diary_list_path(method: object, path: object) -> bool:
    if method != "GET" or type(path) is not str or len(path) > 180:
        return False
    if any(ord(ch) < 33 or ord(ch) > 126 for ch in path):
        return False
    if not path.startswith(BASE + "?"):
        return False
    match = DIARY_QUERY.fullmatch(path[len(BASE) + 1:])
    if match is None:
        return False
    try:
        first, last = (date.fromisoformat(value) for value in match.groups())
    except (ValueError, OverflowError):
        return False
    return 1 <= (last - first).days <= 7
