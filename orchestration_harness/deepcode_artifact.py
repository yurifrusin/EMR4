"""Strict semantic parsing for tolerant Deep Code artifact presentation."""

from __future__ import annotations

import re
from typing import Any

TAIL_LINE_LIMIT = 8
MARKERS = {
    "decision": {"DECISION: PASS", "DECISION: REVISION_REQUIRED"},
    "completion": {"STATUS: COMPLETE"},
}
PREFIXES = {"decision": "DECISION:", "completion": "STATUS:"}


def normalize_marker_text(value: str) -> str:
    """Remove only harmless whole-line Markdown presentation wrappers."""
    value = value.strip()
    for _ in range(4):
        heading = re.fullmatch(r"#{1,6}\s+(.+)", value)
        if heading:
            value = heading.group(1).strip()
            continue
        changed = False
        for wrapper in ("**", "__", "`", "*", "_"):
            if value.startswith(wrapper) and value.endswith(wrapper) and len(value) > len(wrapper) * 2:
                value = value[len(wrapper) : -len(wrapper)].strip()
                changed = True
                break
        if not changed:
            break
    return value


def _logical_lines(body: str) -> list[str]:
    logical: list[str] = []
    for line in body.splitlines():
        cells = line.split("|") if "|" in line else [line]
        logical.extend(normalize_marker_text(cell) for cell in cells if normalize_marker_text(cell))
    return logical


def parse_artifact_marker(body: str, artifact_kind: str = "decision") -> dict[str, Any]:
    """Return a marker decision without treating arbitrary prose as authority."""
    if artifact_kind not in MARKERS:
        raise ValueError(f"unsupported artifact kind: {artifact_kind}")
    lines = _logical_lines(body)
    tail_start = max(0, len(lines) - TAIL_LINE_LIMIT)
    supported = MARKERS[artifact_kind]
    prefix = PREFIXES[artifact_kind]
    found = [(index, line.upper()) for index, line in enumerate(lines) if line.upper() in supported]
    terminal_lines = [line.upper() for line in lines[tail_start:] if line.upper().startswith(prefix)]
    if len(found) != 1:
        return {
            "valid": False,
            "marker": None,
            "reason": "missing_or_non_unique_terminal_marker",
        }
    index, marker = found[0]
    if index < tail_start:
        return {"valid": False, "marker": None, "reason": "terminal_marker_not_near_artifact_end"}
    if any(line not in supported for line in terminal_lines):
        return {"valid": False, "marker": None, "reason": "unsupported_terminal_marker"}
    if len(terminal_lines) != 1:
        return {"valid": False, "marker": None, "reason": "conflicting_or_duplicate_terminal_markers"}
    return {"valid": True, "marker": marker, "reason": "terminal_marker_observed"}
