"""Lint source-safe historical diary docs and tests for semantic drift."""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path


DEFAULT_SCAN_ROOTS = (Path("tests"), Path("docs"))
SCAN_SUFFIXES = {".py", ".md", ".yaml", ".yml", ".json"}
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
    issues: list[LeakageIssue] = []
    for path in _iter_scan_files(paths):
        issues.extend(lint_text(path, path.read_text(encoding="utf-8-sig")))
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


def _iter_scan_files(paths: list[Path]):
    for path in paths:
        if path.is_file():
            if path.suffix.lower() in SCAN_SUFFIXES:
                yield path
            continue
        if not path.is_dir():
            continue
        for candidate in path.rglob("*"):
            if candidate.is_file() and candidate.suffix.lower() in SCAN_SUFFIXES:
                yield candidate


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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", type=Path, default=list(DEFAULT_SCAN_ROOTS))
    args = parser.parse_args()

    assert_no_leakage(args.paths)
    print("historical diary leakage lint safe")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
