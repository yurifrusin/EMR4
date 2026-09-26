"""Lint source-safe historical diary docs and tests for semantic drift."""

from __future__ import annotations

import argparse
import os
import re
import stat
import sys
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).absolute().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.python_source_state import (  # noqa: E402
    SourceStateError,
    _literal_path,
    load_source_state,
)


SCAN_SUFFIXES = {".py", ".md", ".yaml", ".yml", ".json", ".toml", ".txt"}
RELEVANT_PATH_PARTS = {
    "h_series",
    "h-series",
    "historical_diary",
    "historical-diary",
}
NEUTRAL_EVENT_CLASSES = {
    "no_structural_change",
    "small_content_delta",
    "large_unexplained_delta",
    "time_grid_delta",
    "strong_diary_grid",
}
FORBIDDEN_PROMOTION_PHRASES = {
    "booked",
    "booking burst",
    "cancelled appointment",
    "moved appointment",
    "patient arrived",
    "normal surgery day",
    "patient checked in",
    "waiting room",
}
SEMANTIC_FRAME_WORDS = {
    "appointment",
    "booking",
    "booked",
    "cancelled",
    "moved",
    "patient",
    "receptionist",
    "surgery day",
    "waiting room",
}
PERMISSION_WORDS = {
    "allow",
    "allows",
    "enable",
    "enables",
    "permission",
    "permits",
    "strictness",
}
POLICY_CONTEXT_WORDS = {
    "blocked",
    "do not",
    "forbidden",
    "infer",
    "leakage",
    "lint",
    "must not",
    "prohibited",
    "reject",
    "risk",
    "should not",
}
POLICY_DOC_PARTS = {
    "docs/adversarial/",
    "docs/historical-diary-trove-",
    "docs/receptionist_review_r",
    "tests/test_historical_diary_output_safety.py",
    "tests/test_historical_diary_leakage_lint.py",
}
FUNCTION_DRIFT_RE = re.compile(
    r"\bdef\s+test_[a-z0-9_]*(?:h_series|historical_diary)[a-z0-9_]*"
    r"(?:booking|appointment|patient|receptionist|cancel|move|arrive)[a-z0-9_]*\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class LeakageIssue:
    path: Path
    line: int
    reason: str

    def format(self) -> str:
        return f"{self.path}:{self.line}: {self.reason}"


class HistoricalDiaryLeakageLintError(ValueError):
    def __init__(self, issues: list[LeakageIssue]) -> None:
        self.issues = issues
        super().__init__("\n".join(issue.format() for issue in issues))


def lint_paths(paths: list[Path]) -> list[LeakageIssue]:
    if type(paths) is not list or not paths:
        raise SourceStateError("empty_literal_lint_selection")
    issues: list[LeakageIssue] = []
    seen: set[str] = set()
    selected: list[Path] = []
    for supplied in paths:
        if not isinstance(supplied, Path):
            raise SourceStateError("invalid_literal_lint_path")
        raw = os.fspath(supplied).replace("\\", "/")
        if supplied.is_absolute():
            if raw.startswith("//"):
                raise SourceStateError("invalid_literal_lint_path")
            if re.match(r"[A-Za-z]:/", raw):
                tail = raw[3:]
            elif raw.startswith("/"):
                tail = raw[1:]
            else:
                raise SourceStateError("invalid_literal_lint_path")
            try:
                _literal_path(tail)
            except SourceStateError as exc:
                raise SourceStateError("invalid_literal_lint_path") from exc
        else:
            _literal_path(raw)
        path = supplied.absolute()
        if path.suffix.lower() not in SCAN_SUFFIXES:
            raise SourceStateError("unsupported_literal_lint_suffix")
        key = str(path).casefold()
        if key in seen:
            raise SourceStateError("duplicate_literal_lint_path")
        seen.add(key)
        selected.append(path)
    for path in selected:
        issues.extend(lint_text(path, _read_regular_text(path)))
    return issues


def lint_text(path: Path, text: str) -> list[LeakageIssue]:
    issues: list[LeakageIssue] = []
    lines = text.splitlines()
    relevant = _is_relevant_path(path)
    policy_path = _is_policy_path(path)
    in_promotion_constant = False

    for index, line in enumerate(lines, start=1):
        lower = line.lower()
        if "forbidden_promotion" in lower:
            in_promotion_constant = True
        if in_promotion_constant:
            if "}" in line:
                in_promotion_constant = False
            continue

        if not policy_path and FUNCTION_DRIFT_RE.search(line):
            issues.append(
                LeakageIssue(
                    path,
                    index,
                    "test name combines H-series/historical diary with receptionist semantics",
                )
            )

        if relevant and not policy_path and not _is_policy_context(lower):
            promotions = sorted(
                phrase for phrase in FORBIDDEN_PROMOTION_PHRASES if phrase in lower
            )
            if promotions:
                issues.append(
                    LeakageIssue(
                        path,
                        index,
                        f"semantic promotion wording outside policy context: {promotions}",
                    )
                )

            if "deterministic_uses" in lower and any(
                word in lower for word in PERMISSION_WORDS
            ):
                issues.append(
                    LeakageIssue(
                        path,
                        index,
                        "deterministic_uses must stay metadata, not permission logic",
                    )
                )

    if policy_path:
        return issues

    for index, window in _line_windows(lines, size=3):
        lower_window = " ".join(window).lower()
        if _is_policy_context(lower_window):
            continue
        if any(event in lower_window for event in NEUTRAL_EVENT_CLASSES) and any(
            word in lower_window for word in SEMANTIC_FRAME_WORDS
        ):
            issues.append(
                LeakageIssue(
                    path,
                    index,
                    "neutral H-series class is framed as booking/reception semantics",
                )
            )

    return issues


def assert_no_leakage(paths: list[Path]) -> None:
    issues = lint_paths(paths)
    if issues:
        raise HistoricalDiaryLeakageLintError(issues)


def _read_regular_text(path: Path) -> str:
    """Read one named regular file; never expand a directory or redirection."""
    components = [*reversed(path.parents), path]
    before = []
    for index, component in enumerate(components):
        try:
            row = component.lstat()
        except OSError as exc:
            raise SourceStateError("missing_literal_lint_path") from exc
        if (stat.S_ISLNK(row.st_mode)
                or getattr(row, "st_file_attributes", 0) & 0x400):
            raise SourceStateError("literal_lint_redirection")
        if not (stat.S_ISDIR(row.st_mode) if index < len(components) - 1
                else stat.S_ISREG(row.st_mode)):
            raise SourceStateError("literal_lint_not_regular")
        before.append((row.st_dev, row.st_ino, row.st_mode, row.st_size,
                       row.st_mtime_ns, row.st_ctime_ns,
                       getattr(row, "st_file_attributes", 0),
                       getattr(row, "st_reparse_tag", 0)))
    if before[-1][3] > 4 * 1024 * 1024:
        raise SourceStateError("literal_lint_file_too_large")
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
        with os.fdopen(descriptor, "rb") as handle:
            opened = os.fstat(handle.fileno())
            if (opened.st_dev, opened.st_ino, opened.st_mode, opened.st_size) != (
                before[-1][0], before[-1][1], before[-1][2], before[-1][3]
            ):
                raise SourceStateError("literal_lint_file_replaced")
            raw = handle.read(4 * 1024 * 1024 + 1)
    except OSError as exc:
        raise SourceStateError("literal_lint_unreadable") from exc
    after = []
    for component in components:
        try:
            row = component.lstat()
        except OSError as exc:
            raise SourceStateError("literal_lint_file_replaced") from exc
        if (stat.S_ISLNK(row.st_mode)
                or getattr(row, "st_file_attributes", 0) & 0x400):
            raise SourceStateError("literal_lint_redirection")
        after.append((row.st_dev, row.st_ino, row.st_mode, row.st_size,
                      row.st_mtime_ns, row.st_ctime_ns,
                      getattr(row, "st_file_attributes", 0),
                      getattr(row, "st_reparse_tag", 0)))
    if before != after or len(raw) != before[-1][3]:
        raise SourceStateError("literal_lint_file_replaced")
    try:
        return raw.decode("utf-8-sig")
    except UnicodeError as exc:
        raise SourceStateError("literal_lint_decode_failed") from exc


def _is_relevant_path(path: Path) -> bool:
    normalized = path.as_posix().lower()
    return any(part in normalized for part in RELEVANT_PATH_PARTS)


def _is_policy_path(path: Path) -> bool:
    normalized = path.as_posix().lower()
    return any(part in normalized for part in POLICY_DOC_PARTS)


def _is_policy_context(text: str) -> bool:
    return any(word in text for word in POLICY_CONTEXT_WORDS)


def _line_windows(lines: list[str], *, size: int):
    for index in range(len(lines)):
        yield index + 1, lines[index : index + size]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selection", required=True)
    parser.add_argument("--selection-sha256", required=True)
    args = parser.parse_args(argv)
    try:
        state = load_source_state(args.selection,
                                  manifest_sha256=args.selection_sha256,
                                  repo_root=REPO_ROOT)
        issues = []
        for path in state["phases"]["leakage"]:
            try:
                text = state["selected_bytes"][path].decode("utf-8-sig")
            except UnicodeError as exc:
                raise SourceStateError("literal_lint_decode_failed") from exc
            issues.extend(lint_text(Path(path), text))
        if issues:
            raise HistoricalDiaryLeakageLintError(issues)
    except (SourceStateError, HistoricalDiaryLeakageLintError) as exc:
        print(f"[historical_diary_lint_failure] {exc}", file=sys.stderr)
        return 1
    print("historical diary leakage lint safe for literal selection")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
