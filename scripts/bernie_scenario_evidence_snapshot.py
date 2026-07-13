"""Safe aggregate evidence snapshot for Bernie scenario fixtures."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FIXTURE_DIR = REPO_ROOT / "tests" / "fixtures" / "bernie_scenarios"
DEFAULT_SNAPSHOT_PATH = (
    REPO_ROOT
    / "tests"
    / "fixtures"
    / "bernie_scenario_evidence"
    / "blocked_fake_provider_snapshot.json"
)
SNAPSHOT_SCHEMA_VERSION = "bernie.scenario_evidence_snapshot.v1"
SOURCE = "scenario_fixture_aggregate"
EVIDENCE_TYPE = "fake_provider_backend_pass"
OMITTED_FIELD_GROUPS = (
    "scenario_text",
    "utterance_text",
    "identity_fields",
    "request_body_fields",
    "endpoint_paths",
    "local_material_paths",
)
FORBIDDEN_SERIALIZED_FRAGMENTS = (
    "book margaret",
    "actually make it",
    "patient_id",
    "practitioner_id",
    "appointment_id",
    "payload",
    "/api/",
    "local_data",
    "h15",
    "h_series",
)


def _yaml_paths(fixture_dir: Path) -> tuple[Path, ...]:
    if not fixture_dir.exists():
        raise ValueError(f"Scenario fixture directory does not exist: {fixture_dir}")
    if not fixture_dir.is_dir():
        raise ValueError(f"Scenario fixture path is not a directory: {fixture_dir}")
    paths = tuple(sorted(fixture_dir.glob("*.yaml")))
    if not paths:
        raise ValueError(f"No YAML scenario fixtures found in: {fixture_dir}")
    return paths


def build_evidence_snapshot(fixture_dir: Path = DEFAULT_FIXTURE_DIR) -> dict[str, Any]:
    """Build a path/text-free aggregate snapshot over Bernie scenario fixtures."""

    yaml_paths = _yaml_paths(fixture_dir)
    interpret_count = sum(1 for path in yaml_paths if path.name.startswith("interpret_"))
    harness_demo_count = sum(
        1 for path in yaml_paths if path.name.startswith("harness_demo_")
    )
    non_interpret_count = len(yaml_paths) - interpret_count - harness_demo_count

    return {
        "schema_version": SNAPSHOT_SCHEMA_VERSION,
        "source": SOURCE,
        "evidence_type": EVIDENCE_TYPE,
        "scenario_yaml_fixture_count": len(yaml_paths),
        "interpret_fixture_count": interpret_count,
        "harness_demo_fixture_count": harness_demo_count,
        "non_interpret_fixture_count": non_interpret_count,
        "fixtures_since_last_backend_pass": 10,
        "last_backend_pass_refreshed_on": "2026-07-07",
        "fake_provider_evidence": True,
        "route_level_backend_evidence": True,
        "live_provider_evidence": False,
        "provider_quality_evidence": False,
        "provider_calls_performed": False,
        "default_provider": "disabled",
        "runtime_or_provider_wiring_ready": False,
        "live_provider_enabled": False,
        "route_behavior_changed": False,
        "database_access_performed": False,
        "memory_or_rag_access_performed": False,
        "historical_diary_material_access_performed": False,
        "raw_trove_access_ready": False,
        "runtime_gate_decision": "blocked",
        "omitted_field_groups": list(OMITTED_FIELD_GROUPS),
    }


def assert_evidence_snapshot_safety(snapshot: dict[str, Any]) -> None:
    assert snapshot["schema_version"] == SNAPSHOT_SCHEMA_VERSION
    assert snapshot["source"] == SOURCE
    assert snapshot["evidence_type"] == EVIDENCE_TYPE
    assert snapshot["scenario_yaml_fixture_count"] >= 56
    assert snapshot["interpret_fixture_count"] >= 31
    assert snapshot["harness_demo_fixture_count"] == 2
    assert snapshot["non_interpret_fixture_count"] >= 23
    assert snapshot["fixtures_since_last_backend_pass"] >= 10
    assert snapshot["fake_provider_evidence"] is True
    assert snapshot["route_level_backend_evidence"] is True
    assert snapshot["live_provider_evidence"] is False
    assert snapshot["provider_quality_evidence"] is False
    assert snapshot["provider_calls_performed"] is False
    assert snapshot["default_provider"] == "disabled"
    assert snapshot["runtime_or_provider_wiring_ready"] is False
    assert snapshot["live_provider_enabled"] is False
    assert snapshot["route_behavior_changed"] is False
    assert snapshot["database_access_performed"] is False
    assert snapshot["memory_or_rag_access_performed"] is False
    assert snapshot["historical_diary_material_access_performed"] is False
    assert snapshot["raw_trove_access_ready"] is False
    assert snapshot["runtime_gate_decision"] == "blocked"
    assert snapshot["omitted_field_groups"] == list(OMITTED_FIELD_GROUPS)

    serialized = json.dumps(snapshot, sort_keys=True).casefold()
    for fragment in FORBIDDEN_SERIALIZED_FRAGMENTS:
        assert fragment not in serialized


def load_blocked_fake_provider_snapshot(
    snapshot_path: Path = DEFAULT_SNAPSHOT_PATH,
) -> dict[str, Any]:
    if not snapshot_path.exists():
        raise ValueError(f"Blocked fake-provider snapshot does not exist: {snapshot_path}")
    return json.loads(snapshot_path.read_text(encoding="utf-8"))


def assert_matches_blocked_fake_provider_snapshot(
    snapshot: dict[str, Any],
    snapshot_path: Path = DEFAULT_SNAPSHOT_PATH,
) -> None:
    assert snapshot == load_blocked_fake_provider_snapshot(snapshot_path)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Emit a safe aggregate Bernie scenario evidence snapshot."
    )
    parser.add_argument(
        "--fixture-dir",
        type=Path,
        default=DEFAULT_FIXTURE_DIR,
        help="Directory containing Bernie scenario YAML fixtures.",
    )
    parser.add_argument(
        "--snapshot",
        type=Path,
        default=DEFAULT_SNAPSHOT_PATH,
        help="Optional committed snapshot to compare against.",
    )
    parser.add_argument(
        "--no-compare",
        action="store_true",
        help="Emit the generated snapshot without comparing to the committed snapshot.",
    )
    args = parser.parse_args()

    snapshot = build_evidence_snapshot(args.fixture_dir)
    assert_evidence_snapshot_safety(snapshot)
    if not args.no_compare:
        assert_matches_blocked_fake_provider_snapshot(snapshot, args.snapshot)
    print(json.dumps(snapshot, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
