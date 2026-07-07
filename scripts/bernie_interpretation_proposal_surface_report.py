"""Safe aggregate report for Bernie proposal-surface guard scans."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.bernie_interpretation_proposal_surface_guard import (
    PROVIDER_BOUNDARY_COMMAND,
    READINESS_COMMAND,
    _iter_markdown_paths,
    scan_proposal_surface,
)


REPORT_SCHEMA_VERSION = "bernie.proposal_surface_guard_report.v1"
REPORT_SOURCE = "proposal_surface_aggregate"
BOUNDARIES = {
    "provider_calls": "prohibited",
    "route_calls": "prohibited",
    "database_access": "prohibited",
    "raw_trove_access": "prohibited",
    "runtime_memory": "prohibited",
}
OMITTED_FIELDS = [
    "paths",
    "filenames",
    "decode_error_text",
    "trigger_phrase_text",
]


def build_proposal_surface_report(paths: tuple[Path, ...]) -> dict[str, Any]:
    markdown_paths = _iter_markdown_paths(paths)
    findings = scan_proposal_surface(paths)
    missing_count = len(findings.missing_readiness)
    unreadable_count = len(findings.unreadable_markdown)

    return {
        "schema_version": REPORT_SCHEMA_VERSION,
        "source": REPORT_SOURCE,
        "scanned_markdown_count": len(markdown_paths),
        "trigger_phrase_hit_count": findings.trigger_phrase_hit_count,
        "missing_readiness_count": missing_count,
        "unreadable_markdown_count": unreadable_count,
        "total_fail_closed_findings_count": missing_count + unreadable_count,
        "readiness_command_name": READINESS_COMMAND,
        "provider_boundary_command_name": PROVIDER_BOUNDARY_COMMAND,
        "boundaries": BOUNDARIES,
        "omitted_fields": OMITTED_FIELDS,
        "runtime_or_provider_wiring_ready": False,
        "provider_calls_performed": False,
        "database_access_performed": False,
        "historical_diary_material_access_performed": False,
    }


def assert_proposal_surface_report_safety(report: dict[str, Any]) -> None:
    assert report["schema_version"] == REPORT_SCHEMA_VERSION
    assert report["source"] == REPORT_SOURCE
    count_fields = (
        "scanned_markdown_count",
        "trigger_phrase_hit_count",
        "missing_readiness_count",
        "unreadable_markdown_count",
        "total_fail_closed_findings_count",
    )
    for field in count_fields:
        assert isinstance(report[field], int)
        assert report[field] >= 0
    assert report["trigger_phrase_hit_count"] <= report["scanned_markdown_count"]
    assert report["total_fail_closed_findings_count"] == (
        report["missing_readiness_count"] + report["unreadable_markdown_count"]
    )
    assert report["readiness_command_name"] == READINESS_COMMAND
    assert report["provider_boundary_command_name"] == PROVIDER_BOUNDARY_COMMAND
    assert report["boundaries"] == BOUNDARIES
    assert report["omitted_fields"] == OMITTED_FIELDS
    assert report["runtime_or_provider_wiring_ready"] is False
    assert report["provider_calls_performed"] is False
    assert report["database_access_performed"] is False
    assert report["historical_diary_material_access_performed"] is False
    forbidden_fields = {
        "paths",
        "files",
        "missing_readiness",
        "unreadable_markdown",
        "document_text",
        "text",
    }
    assert forbidden_fields.isdisjoint(report)
    serialized = json.dumps(report, sort_keys=True).casefold()
    forbidden_fragments = (
        "local_data",
        "__pycache__",
        "docs\\",
        "tests\\",
        "c:",
        "d:",
        "utf-8",
        "unicodedecodeerror",
        "decode error",
        "codec",
        ".md",
    )
    for fragment in forbidden_fragments:
        assert fragment not in serialized


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Emit a safe aggregate Bernie proposal-surface guard report."
    )
    parser.add_argument("paths", nargs="+", type=Path)
    args = parser.parse_args()

    report = build_proposal_surface_report(tuple(args.paths))
    assert_proposal_surface_report_safety(report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
