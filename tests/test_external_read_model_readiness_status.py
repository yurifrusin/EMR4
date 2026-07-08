import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.external_read_model_readiness_status import (
    DEFAULT_DAG_PATH,
    DEFAULT_ROOT_INVENTORY_PATH,
    build_readiness_status,
)


ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_PATH = (
    ROOT
    / "tests"
    / "fixtures"
    / "api_spine_external_readiness"
    / "blocked_readiness_status.json"
)

READINESS_FLAGS = {
    "external_read_model_runtime_ready",
    "graphql_resolver_ready",
    "rest_route_ready",
    "provider_or_directory_runtime_ready",
    "runtime_or_memory_ready",
    "write_authority_ready",
    "raw_compat_mode_change_ready",
}

FORBIDDEN_OUTPUT_FRAGMENTS = {
    "query.",
    "/api/",
    "patient_id",
    "practitioner_id",
    "appointment_id",
    "racgp",
    "cochrane",
    "provider prompt",
    "local_data",
    "readiness\": true",
    "decision\": \"approved",
    "runtime_authority\": true",
}


def _snapshot() -> dict[str, object]:
    if not SNAPSHOT_PATH.exists():
        raise ValueError(f"Missing external readiness snapshot: {SNAPSHOT_PATH}")
    return json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))


def test_readiness_status_matches_blocked_snapshot():
    assert build_readiness_status() == _snapshot()


def test_readiness_status_contains_no_payload_or_prompt_fragments():
    serialized = json.dumps(build_readiness_status(), sort_keys=True).casefold()

    for fragment in FORBIDDEN_OUTPUT_FRAGMENTS:
        assert fragment not in serialized


def test_readiness_status_does_not_authorize_runtime():
    status = build_readiness_status()

    assert status["dag_decision"] == "blocked"
    assert status["combined_review_decision"] == "blocked"
    assert status["combined_readiness_review_status"] == "static_complete"
    assert status["blocked_runtime_gate_count"] == 3
    assert status["runtime_authority_node_count"] == 0
    assert all(status[flag] is False for flag in READINESS_FLAGS)
    assert status["pause_required"] is False


def test_readiness_status_cli_outputs_snapshot_json():
    completed = subprocess.run(
        [sys.executable, "scripts/external_read_model_readiness_status.py"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    assert json.loads(completed.stdout) == _snapshot()


def test_readiness_status_rejects_dag_unblocked(tmp_path: Path):
    dag_path = tmp_path / "dag.json"
    dag_path.write_text(
        DEFAULT_DAG_PATH.read_text(encoding="utf-8").replace(
            '"decision": "blocked"', '"decision": "approved"'
        ),
        encoding="utf-8",
    )

    with pytest.raises(AssertionError):
        build_readiness_status(dag_path=dag_path)


def test_readiness_status_rejects_true_readiness_flag(tmp_path: Path):
    dag_path = tmp_path / "dag.json"
    dag_path.write_text(
        DEFAULT_DAG_PATH.read_text(encoding="utf-8").replace(
            '"rest_route_ready": false', '"rest_route_ready": true'
        ),
        encoding="utf-8",
    )

    with pytest.raises(AssertionError):
        build_readiness_status(dag_path=dag_path)


def test_readiness_status_rejects_root_directory_disjunction_drift(tmp_path: Path):
    root_inventory_path = tmp_path / "root.md"
    root_inventory_path.write_text(
        DEFAULT_ROOT_INVENTORY_PATH.read_text(encoding="utf-8").replace(
            "| `Query.directorySearch.RACGP_GUIDELINES` | `none` | `none` | `gap` | `read_model_gap` |",
            "| `Query.directorySearch.RACGP_GUIDELINES` | `GET /api/v1/search-racgp` | `search_racgp` | `partial` | `read_only_route` |",
        ),
        encoding="utf-8",
    )

    with pytest.raises(AssertionError):
        build_readiness_status(root_inventory_path=root_inventory_path)


def test_readiness_status_rejects_missing_dag(tmp_path: Path):
    with pytest.raises(ValueError):
        build_readiness_status(dag_path=tmp_path / "missing.json")


def test_readiness_status_rejects_missing_snapshot(tmp_path: Path):
    missing_snapshot = tmp_path / "missing.json"

    with pytest.raises(ValueError):
        if not missing_snapshot.exists():
            raise ValueError(f"Missing external readiness snapshot: {missing_snapshot}")
