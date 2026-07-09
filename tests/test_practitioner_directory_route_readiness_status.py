import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.practitioner_directory_route_readiness_status import (
    APPROVAL_DECISION,
    STATUS_SCHEMA_VERSION,
    TARGET_ROUTE,
    build_practitioner_directory_route_readiness_status,
)


ROOT = Path(__file__).resolve().parents[1]
APPROVAL = (
    ROOT
    / "docs"
    / "api-spine"
    / "practitioner-directory-rest-route-readiness-approval.json"
)
SNAPSHOT = (
    ROOT
    / "tests"
    / "fixtures"
    / "api_spine_external_readiness"
    / "practitioner_directory_route_readiness_status.json"
)
GLOBAL_SNAPSHOT = (
    ROOT
    / "tests"
    / "fixtures"
    / "api_spine_external_readiness"
    / "blocked_readiness_status.json"
)


def test_route_readiness_status_exposes_approved_route_without_global_flip():
    status = build_practitioner_directory_route_readiness_status()

    assert status["schema_version"] == STATUS_SCHEMA_VERSION
    assert status["target_route"] == TARGET_ROUTE
    assert status["route_readiness_approval_decision"] == APPROVAL_DECISION
    assert status == json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    assert status["rest_route_ready"] is True
    assert status["route_ready_for_authenticated_internal_staff_read_use"] is True
    assert status["approval_expires_on"] == "2026-08-08"
    assert status["global_readiness_snapshot_updated"] is False
    assert status["global_snapshot_rest_route_ready"] is False
    assert status["global_external_read_model_runtime_ready"] is False
    assert status["global_graphql_resolver_ready"] is False
    assert status["global_write_authority_ready"] is False
    assert status["global_provider_or_directory_runtime_ready"] is False


def test_route_readiness_status_preserves_adjacent_gate_boundaries():
    status = build_practitioner_directory_route_readiness_status()

    assert status["adjacent_gate_false_count"] == 8
    assert status["deployment_ready"] is False
    assert status["production_ready"] is False
    assert status["external_patient_client_ready"] is False
    assert "deferred" in status["rate_limit_posture"]
    assert "not database-level RLS" in status["rls_posture"]
    assert "response schema excludes" in status["field_encryption_posture"]
    assert "migrates the global external-readiness DAG" in status["next_migration_step"]


def test_route_readiness_status_cli_outputs_safe_json():
    completed = subprocess.run(
        [sys.executable, "scripts/practitioner_directory_route_readiness_status.py"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    assert json.loads(completed.stdout) == json.loads(SNAPSHOT.read_text(encoding="utf-8"))


def test_route_readiness_status_rejects_wrong_route(tmp_path: Path):
    approval = json.loads(APPROVAL.read_text(encoding="utf-8"))
    approval["target_route"] = "GET /api/v1/practice/practitioners/{id}"
    approval_path = tmp_path / "approval.json"
    approval_path.write_text(json.dumps(approval), encoding="utf-8")

    with pytest.raises(AssertionError):
        build_practitioner_directory_route_readiness_status(approval_path=approval_path)


def test_route_readiness_status_rejects_adjacent_gate_true(tmp_path: Path):
    approval = json.loads(APPROVAL.read_text(encoding="utf-8"))
    approval["must_remain_false"]["deployment_ready"] = True
    approval_path = tmp_path / "approval.json"
    approval_path.write_text(json.dumps(approval), encoding="utf-8")

    with pytest.raises(AssertionError):
        build_practitioner_directory_route_readiness_status(approval_path=approval_path)


def test_route_readiness_status_rejects_expired_approval(tmp_path: Path):
    approval = json.loads(APPROVAL.read_text(encoding="utf-8"))
    approval["approval_expires_on"] = "2026-07-08"
    approval_path = tmp_path / "approval.json"
    approval_path.write_text(json.dumps(approval), encoding="utf-8")

    with pytest.raises(AssertionError):
        build_practitioner_directory_route_readiness_status(approval_path=approval_path)


def test_route_readiness_status_rejects_global_snapshot_flip(tmp_path: Path):
    global_snapshot = json.loads(GLOBAL_SNAPSHOT.read_text(encoding="utf-8"))
    global_snapshot["rest_route_ready"] = True
    global_snapshot_path = tmp_path / "global.json"
    global_snapshot_path.write_text(json.dumps(global_snapshot), encoding="utf-8")

    with pytest.raises(AssertionError):
        build_practitioner_directory_route_readiness_status(
            global_snapshot_path=global_snapshot_path
        )
