"""Pure canonical verdict algebra for provider-free review artifacts.

The parser in this module is deliberately side-effect free.  It interprets a
small, closed terminal-marker grammar without reading repositories, files,
processes, providers, or networks.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from enum import Enum
from typing import Any

TERMINAL_LOGICAL_CELL_LIMIT = 8


class ArtifactKind(str, Enum):
    """Kinds of artifact understood by the G1A.1 verdict kernel."""

    DECISION = "decision"
    COMPLETION = "completion"


class ReviewVerdict(str, Enum):
    """Closed review vocabulary authorised in G1A.1."""

    PASS = "pass"
    REVISION_REQUIRED = "revision_required"


_OBSERVED = "terminal_marker_observed"
_REASON_CODES = frozenset(
    {
        _OBSERVED,
        "missing_authoritative_marker",
        "duplicate_authoritative_markers",
        "conflicting_decision_markers",
        "terminal_marker_not_near_artifact_end",
        "unsupported_decision_marker",
        "unsupported_status_marker",
        "wrong_artifact_kind_marker",
        "legacy_verdict_marker",
        "non_authoritative_marker_context",
        "non_ascii_marker_lexeme",
    }
)
_CANONICAL_COMPLETION = "STATUS: COMPLETE"
_WRAPPERS = ("**", "__", "`", "*", "_")
_HEADING_RE = re.compile(r"#{1,6}\s+(.+)")
_ASCII_MARKER_SEARCH_RE = re.compile(
    r"(?<![A-Za-z0-9_])(?:decision|status|verdict):",
    flags=re.IGNORECASE | re.ASCII,
)
_UNICODE_TOKEN_RE = re.compile(r"([^\W\d_]{6,8}):")
_FENCE_OPEN_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
_BLOCKQUOTE_OR_LIST_PREFIX_RE = re.compile(r"^\s*(?:>+|(?:[-+*]|\d+[.)])\s+)")
_MARKER_TOKENS = ("DECISION", "STATUS", "VERDICT")


@dataclass(frozen=True)
class VerdictAssessment:
    """A non-contradictory assessment of one artifact body.

    Integration authority is a derived property and cannot be supplied by a
    caller.  Construction rejects combinations that would contradict the
    verdict algebra.
    """

    artifact_kind: ArtifactKind
    artifact_valid: bool
    review_verdict: ReviewVerdict | None
    canonical_marker: str | None
    reason_code: str

    def __post_init__(self) -> None:
        if not isinstance(self.artifact_kind, ArtifactKind):
            raise TypeError("artifact_kind must be an ArtifactKind")
        if self.reason_code not in _REASON_CODES:
            raise ValueError(f"unsupported reason_code: {self.reason_code}")

        if not self.artifact_valid:
            if self.review_verdict is not None or self.canonical_marker is not None:
                raise ValueError(
                    "invalid artifacts cannot carry a verdict or canonical marker"
                )
            if self.reason_code == _OBSERVED:
                raise ValueError(
                    "invalid artifacts cannot report an observed terminal marker"
                )
            return

        if self.reason_code != _OBSERVED:
            raise ValueError(
                "valid artifacts must report the observed terminal marker reason"
            )
        if self.artifact_kind is ArtifactKind.COMPLETION:
            if self.review_verdict is not None:
                raise ValueError("completion artifacts cannot carry a review verdict")
            if self.canonical_marker != _CANONICAL_COMPLETION:
                raise ValueError("valid completion artifacts require STATUS: COMPLETE")
            return

        if self.review_verdict is None:
            raise ValueError("valid decision artifacts require a review verdict")
        expected_marker = {
            ReviewVerdict.PASS: "DECISION: PASS",
            ReviewVerdict.REVISION_REQUIRED: "DECISION: REVISION_REQUIRED",
        }[self.review_verdict]
        if self.canonical_marker != expected_marker:
            raise ValueError("decision marker and review verdict disagree")

    @property
    def integration_authorized(self) -> bool:
        """Whether this artifact alone can grant integration authority."""

        return (
            self.artifact_kind is ArtifactKind.DECISION
            and self.artifact_valid
            and self.review_verdict is ReviewVerdict.PASS
        )

    def to_dict(self) -> dict[str, Any]:
        """Return a deterministic JSON-compatible projection."""

        return {
            "artifact_kind": self.artifact_kind.value,
            "artifact_valid": self.artifact_valid,
            "review_verdict": self.review_verdict.value
            if self.review_verdict
            else None,
            "integration_authorized": self.integration_authorized,
            "canonical_marker": self.canonical_marker,
            "reason_code": self.reason_code,
        }

    def to_json(self) -> str:
        """Return stable compact JSON for evidence and regression tests."""

        return json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"))


def _coerce_artifact_kind(artifact_kind: ArtifactKind | str) -> ArtifactKind:
    try:
        return (
            artifact_kind
            if isinstance(artifact_kind, ArtifactKind)
            else ArtifactKind(artifact_kind)
        )
    except ValueError as error:
        raise ValueError(f"unsupported artifact kind: {artifact_kind}") from error


def _normalize_cell(value: str) -> str:
    value = value.strip()
    while value:
        heading = _HEADING_RE.fullmatch(value)
        if heading:
            value = heading.group(1).strip()
            continue
        for wrapper in _WRAPPERS:
            if (
                value.startswith(wrapper)
                and value.endswith(wrapper)
                and len(value) > 2 * len(wrapper)
            ):
                value = value[len(wrapper) : -len(wrapper)].strip()
                break
        else:
            return value
    return value


def _token_looks_like_marker(token: str) -> bool:
    """Detect non-ASCII substitutions without Unicode case canonicalisation."""

    for expected in _MARKER_TOKENS:
        if len(token) != len(expected):
            continue
        if any(character.isascii() for character in token) and all(
            (not observed.isascii())
            or (observed.isalpha() and observed.lower() == wanted.lower())
            for observed, wanted in zip(token, expected, strict=True)
        ):
            return True
    return False


def _marker_like(value: str) -> tuple[bool, bool]:
    """Return ``(marker_like, contains_non_ascii_protocol_text)``."""

    ascii_match = _ASCII_MARKER_SEARCH_RE.search(value)
    if ascii_match:
        candidate_tail = value[ascii_match.start() :]
        return True, not candidate_tail.isascii()
    for match in _UNICODE_TOKEN_RE.finditer(value):
        token = match.group(1)
        if not token.isascii() and _token_looks_like_marker(token):
            return True, True
    return False, False


def _split_html_comments(
    line: str, in_comment: bool
) -> tuple[list[str], list[str], bool]:
    """Split one line into visible and HTML-comment segments."""

    visible: list[str] = []
    hidden: list[str] = []
    cursor = 0
    while cursor < len(line):
        if in_comment:
            end = line.find("-->", cursor)
            if end < 0:
                hidden.append(line[cursor:])
                return visible, hidden, True
            hidden.append(line[cursor : end + 3])
            cursor = end + 3
            in_comment = False
            continue
        start = line.find("<!--", cursor)
        if start < 0:
            visible.append(line[cursor:])
            break
        visible.append(line[cursor:start])
        cursor = start
        in_comment = True
    return visible, hidden, in_comment


def _is_fence_close(line: str, fence_character: str, fence_length: int) -> bool:
    stripped = line.lstrip(" ")
    if len(line) - len(stripped) > 3:
        return False
    marker = fence_character * fence_length
    if not stripped.startswith(marker):
        return False
    remainder = stripped[fence_length:]
    return not remainder.strip(fence_character).strip()


def _visible_logical_cells(body: str) -> tuple[list[str], str | None]:
    """Return closed visible marker cells and any fail-closed context reason."""

    cells: list[str] = []
    in_comment = False
    fence_character: str | None = None
    fence_length = 0
    hidden_marker = False
    non_ascii_marker = False

    for raw_line in body.splitlines():
        if fence_character is not None:
            marker_like, non_ascii = _marker_like(raw_line)
            hidden_marker = hidden_marker or marker_like
            non_ascii_marker = non_ascii_marker or non_ascii
            if _is_fence_close(raw_line, fence_character, fence_length):
                fence_character = None
                fence_length = 0
            continue

        fence_open = _FENCE_OPEN_RE.fullmatch(raw_line)
        if fence_open:
            marker_like, non_ascii = _marker_like(raw_line)
            hidden_marker = hidden_marker or marker_like
            non_ascii_marker = non_ascii_marker or non_ascii
            fence_character = fence_open.group(1)[0]
            fence_length = len(fence_open.group(1))
            continue

        visible_segments, hidden_segments, in_comment = _split_html_comments(
            raw_line, in_comment
        )
        for segment in hidden_segments:
            marker_like, non_ascii = _marker_like(segment)
            hidden_marker = hidden_marker or marker_like
            non_ascii_marker = non_ascii_marker or non_ascii

        visible_line = " ".join(visible_segments)
        indentation = len(visible_line) - len(visible_line.lstrip(" "))
        if visible_line.startswith("\t") or indentation >= 4:
            marker_like, non_ascii = _marker_like(visible_line)
            hidden_marker = hidden_marker or marker_like
            non_ascii_marker = non_ascii_marker or non_ascii
            continue

        trimmed = visible_line.strip()
        marker_like_line, non_ascii_line = _marker_like(visible_line)
        prefixed = _BLOCKQUOTE_OR_LIST_PREFIX_RE.match(visible_line) is not None
        escaped_pipe = r"\|" in visible_line
        explicit_table_row = (
            trimmed.startswith("|")
            and trimmed.endswith("|")
            and not prefixed
            and not escaped_pipe
        )
        rejected_marker_context = marker_like_line and (
            prefixed or escaped_pipe or ("|" in visible_line and not explicit_table_row)
        )
        if rejected_marker_context:
            hidden_marker = True
            non_ascii_marker = non_ascii_marker or non_ascii_line

        candidates: list[str] = []
        if explicit_table_row:
            candidates = trimmed[1:-1].split("|")
        elif trimmed:
            candidates = [trimmed]

        for candidate in candidates:
            normalized = _normalize_cell(candidate)
            if not normalized:
                continue
            marker_like, non_ascii = _marker_like(normalized)
            if marker_like and non_ascii:
                non_ascii_marker = True
            cells.append(normalized)

    if non_ascii_marker:
        return cells, "non_ascii_marker_lexeme"
    if hidden_marker:
        return cells, "non_authoritative_marker_context"
    return cells, None


def _invalid(kind: ArtifactKind, reason_code: str) -> VerdictAssessment:
    return VerdictAssessment(
        artifact_kind=kind,
        artifact_valid=False,
        review_verdict=None,
        canonical_marker=None,
        reason_code=reason_code,
    )


def parse_artifact_verdict(
    body: str, artifact_kind: ArtifactKind | str
) -> VerdictAssessment:
    """Parse exactly one bounded canonical marker from an artifact body."""

    if not isinstance(body, str):
        raise TypeError("body must be a string")
    kind = _coerce_artifact_kind(artifact_kind)
    cells, context_reason = _visible_logical_cells(body)
    if context_reason is not None:
        return _invalid(kind, context_reason)
    supported: list[tuple[int, ArtifactKind, ReviewVerdict | None, str]] = []
    unsupported_decision = False
    unsupported_status = False
    legacy_verdict = False

    for index, cell in enumerate(cells):
        if not cell.isascii():
            continue
        folded = cell.lower()
        if folded == "decision: pass":
            supported.append(
                (index, ArtifactKind.DECISION, ReviewVerdict.PASS, "DECISION: PASS")
            )
        elif folded == "decision: revision_required":
            supported.append(
                (
                    index,
                    ArtifactKind.DECISION,
                    ReviewVerdict.REVISION_REQUIRED,
                    "DECISION: REVISION_REQUIRED",
                )
            )
        elif folded == "status: complete":
            supported.append(
                (index, ArtifactKind.COMPLETION, None, _CANONICAL_COMPLETION)
            )
        elif folded.startswith("decision:"):
            unsupported_decision = True
        elif folded.startswith("status:"):
            unsupported_status = True
        elif folded.startswith("verdict:"):
            legacy_verdict = True

    if legacy_verdict:
        return _invalid(kind, "legacy_verdict_marker")
    if unsupported_decision:
        return _invalid(kind, "unsupported_decision_marker")
    if unsupported_status:
        return _invalid(kind, "unsupported_status_marker")
    if any(marker_kind is not kind for _, marker_kind, _, _ in supported):
        return _invalid(kind, "wrong_artifact_kind_marker")
    if len(supported) > 1:
        verdicts = {verdict for _, _, verdict, _ in supported}
        if kind is ArtifactKind.DECISION and len(verdicts) > 1:
            return _invalid(kind, "conflicting_decision_markers")
        return _invalid(kind, "duplicate_authoritative_markers")
    if not supported:
        return _invalid(kind, "missing_authoritative_marker")

    index, _, verdict, canonical_marker = supported[0]
    tail_start = max(0, len(cells) - TERMINAL_LOGICAL_CELL_LIMIT)
    if index < tail_start:
        return _invalid(kind, "terminal_marker_not_near_artifact_end")
    return VerdictAssessment(
        artifact_kind=kind,
        artifact_valid=True,
        review_verdict=verdict,
        canonical_marker=canonical_marker,
        reason_code=_OBSERVED,
    )


__all__ = [
    "ArtifactKind",
    "ReviewVerdict",
    "VerdictAssessment",
    "parse_artifact_verdict",
]
