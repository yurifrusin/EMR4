"""Guard interpretation runtime/provider/trove proposal artifacts."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path


READINESS_COMMAND = (
    ".venv\\Scripts\\python.exe scripts\\bernie_interpretation_readiness_check.py"
)
PROVIDER_BOUNDARY_COMMAND = (
    ".venv\\Scripts\\python.exe scripts\\bernie_provider_boundary_readiness_report.py"
)
REQUIRED_MARKERS = (
    READINESS_COMMAND,
)
REQUIRED_EXPECTED_VALUES = {
    "runtime_or_provider_wiring_ready": "false",
    "raw_trove_access_ready": "false",
    "runtime_gate_decision": "blocked",
}
PROVIDER_BOUNDARY_EXPECTED_VALUES = {
    "default_provider": "disabled",
    "runtime_or_provider_wiring_ready": "false",
    "live_provider_enabled": "false",
    "provider_calls_performed": "false",
    "route_behavior_changed": "false",
    "database_access_performed": "false",
    "memory_or_rag_access_performed": "false",
    "historical_diary_material_access_performed": "false",
}
TRIGGER_PHRASES = (
    "runtime route wiring",
    "runtime route integration",
    "route integration",
    "provider prompt wiring",
    "provider prompt integration",
    "provider dry-run wiring",
    "provider dry run wiring",
    "provider dry-run integration",
    "provider integration",
    "live provider",
    "memory/rag/graphrag use",
    "memory/rag",
    "graphrag",
    "access ai",
    "access-ai",
    "h15/h-series runtime imports",
    "h15 runtime imports",
    "h-series runtime imports",
    "historical diary material access",
    "historical diary access",
    "historical diary trove",
    "raw-trove access",
    "raw diary",
    "local_data",
    "local data",
    "runtime/provider/trove proposal",
    "bernie booking interpreter provider boundary",
    "provider-boundary proposal",
    "provider boundary proposal",
    "live-provider",
    "live provider enablement",
    "model selection",
    "model upgrade",
    "provider aliasing",
    "alias provider",
)
PROVIDER_BOUNDARY_TRIGGER_PHRASES = (
    "bernie booking interpreter provider boundary",
    "provider-boundary proposal",
    "provider boundary proposal",
    "provider prompt wiring",
    "provider prompt integration",
    "provider dry-run wiring",
    "provider dry run wiring",
    "provider dry-run integration",
    "provider integration",
    "live provider",
    "live-provider",
    "live provider enablement",
    "model selection",
    "model upgrade",
    "provider aliasing",
    "alias provider",
)


@dataclass(frozen=True)
class ProposalSurfaceGuardFindings:
    missing_readiness: tuple[Path, ...]
    unreadable_markdown: tuple[tuple[Path, str], ...]


def _iter_markdown_paths(paths: tuple[Path, ...]) -> tuple[Path, ...]:
    discovered: list[Path] = []
    for path in paths:
        if path.is_dir():
            discovered.extend(sorted(path.rglob("*.md")))
        elif path.suffix.lower() == ".md":
            discovered.append(path)
    return tuple(discovered)


def _read_markdown_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def scan_proposal_surface(paths: tuple[Path, ...]) -> ProposalSurfaceGuardFindings:
    """Return proposal-surface files missing evidence or unreadable as UTF-8."""

    missing: list[Path] = []
    unreadable: list[tuple[Path, str]] = []
    for path in _iter_markdown_paths(paths):
        try:
            text = _read_markdown_text(path)
        except UnicodeDecodeError as exc:
            unreadable.append((path, str(exc)))
            continue
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
            continue
        if any(phrase in folded for phrase in PROVIDER_BOUNDARY_TRIGGER_PHRASES):
            if PROVIDER_BOUNDARY_COMMAND.casefold() not in folded:
                missing.append(path)
                continue
            if any(
                f"{key}={value}" not in compact and f"{key}:{value}" not in compact
                for key, value in PROVIDER_BOUNDARY_EXPECTED_VALUES.items()
            ):
                missing.append(path)
    return ProposalSurfaceGuardFindings(
        missing_readiness=tuple(missing),
        unreadable_markdown=tuple(unreadable),
    )


def files_missing_readiness_reference(paths: tuple[Path, ...]) -> tuple[Path, ...]:
    """Return proposal-surface files missing evidence or unreadable as UTF-8."""

    findings = scan_proposal_surface(paths)
    return findings.missing_readiness + tuple(
        path for path, _error in findings.unreadable_markdown
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Require Bernie interpretation readiness evidence in "
            "runtime/provider/trove proposal artifacts."
        )
    )
    parser.add_argument("paths", nargs="+", type=Path)
    args = parser.parse_args()

    findings = scan_proposal_surface(tuple(args.paths))
    if findings.missing_readiness or findings.unreadable_markdown:
        sections: list[str] = []
        if findings.missing_readiness:
            formatted = "\n".join(f"- {path}" for path in findings.missing_readiness)
            sections.append(
                "Missing Bernie interpretation readiness evidence in:\n"
                f"{formatted}"
            )
        if findings.unreadable_markdown:
            formatted = "\n".join(
                f"- {path}: {error}"
                for path, error in findings.unreadable_markdown
            )
            sections.append(
                "Unreadable markdown files; convert to UTF-8 before relying on "
                f"this guard:\n{formatted}"
            )
        raise SystemExit(
            "\n".join(sections)
            + "\n"
            f"Required command: {READINESS_COMMAND}\n"
            "Required expected values: runtime_or_provider_wiring_ready=false, "
            "raw_trove_access_ready=false, runtime_gate_decision=blocked\n"
            "Provider-boundary proposals also require command: "
            f"{PROVIDER_BOUNDARY_COMMAND}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
