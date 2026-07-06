"""Guard interpretation runtime/provider/trove proposal artifacts."""

from __future__ import annotations

import argparse
from pathlib import Path


READINESS_COMMAND = (
    ".venv\\Scripts\\python.exe scripts\\bernie_interpretation_readiness_check.py"
)
REQUIRED_MARKERS = (
    READINESS_COMMAND,
)
REQUIRED_EXPECTED_VALUES = {
    "runtime_or_provider_wiring_ready": "false",
    "raw_trove_access_ready": "false",
    "runtime_gate_decision": "blocked",
}
TRIGGER_PHRASES = (
    "runtime route wiring",
    "provider prompt wiring",
    "provider dry-run wiring",
    "memory/rag/graphrag use",
    "h15/h-series runtime imports",
    "historical diary material access",
    "runtime/provider/trove proposal",
)


def _iter_markdown_paths(paths: tuple[Path, ...]) -> tuple[Path, ...]:
    discovered: list[Path] = []
    for path in paths:
        if path.is_dir():
            discovered.extend(sorted(path.rglob("*.md")))
        elif path.suffix.lower() == ".md":
            discovered.append(path)
    return tuple(discovered)


def files_missing_readiness_reference(paths: tuple[Path, ...]) -> tuple[Path, ...]:
    """Return proposal-surface files missing required readiness evidence."""

    missing: list[Path] = []
    for path in _iter_markdown_paths(paths):
        text = path.read_text(encoding="utf-8")
        folded = text.casefold()
        if not any(phrase in folded for phrase in TRIGGER_PHRASES):
            continue
        if any(marker.casefold() not in folded for marker in REQUIRED_MARKERS):
            missing.append(path)
            continue
        compact = folded.replace("`", "").replace(" ", "")
        if any(
            f"{key}={value}" not in compact and f"{key}:{value}" not in compact
            for key, value in REQUIRED_EXPECTED_VALUES.items()
        ):
            missing.append(path)
    return tuple(missing)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Require Bernie interpretation readiness evidence in "
            "runtime/provider/trove proposal artifacts."
        )
    )
    parser.add_argument("paths", nargs="+", type=Path)
    args = parser.parse_args()

    missing = files_missing_readiness_reference(tuple(args.paths))
    if missing:
        formatted = "\n".join(f"- {path}" for path in missing)
        raise SystemExit(
            "Missing Bernie interpretation readiness evidence in:\n"
            f"{formatted}\n"
            f"Required command: {READINESS_COMMAND}\n"
            "Required expected values: runtime_or_provider_wiring_ready=false, "
            "raw_trove_access_ready=false, runtime_gate_decision=blocked"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
