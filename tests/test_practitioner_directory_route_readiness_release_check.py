import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.practitioner_directory_route_readiness_release_check import (
    RELEASE_CHECK_SCHEMA_VERSION,
    TARGET_ROUTE,
    build_practitioner_directory_route_readiness_release_check,
)


ROOT = Path(__file__).resolve().parents[1]
BOUNDARY = (
    ROOT
    / "docs"
    / "api-spine"
    / "practitioner-directory-route-readiness-consumer-boundary.json"
)


def test_release_check_allows_only_static_ci_consumption():
    report = build_practitioner_directory_route_readiness_release_check()

    assert report["schema_version"] == RELEASE_CHECK_SCHEMA_VERSION
    assert report["target_route"] == TARGET_ROUTE
    assert report["static_release_check_ready"] is True
    assert report["allowed_consumer"] == (
        "static CI or pytest release-gate checks that emit aggregate readiness status"
    )
    assert report["runtime_consumers_allowed"] is False
    assert report["rest_route_ready"] is True
    assert report["global_readiness_snapshot_updated"] is False
    assert report["pause_required"] is False
    assert report["sprint_engine_state"] == "continuing"


def test_release_check_preserves_closed_adjacent_gates():
    report = build_practitioner_directory_route_readiness_release_check()

    assert report["adjacent_gate_false_count"] == 8
    assert report["deployment_ready"] is False
    assert report["production_ready"] is False
    assert report["external_patient_client_ready"] is False
    assert report["global_graphql_resolver_ready"] is False
    assert report["global_provider_or_directory_runtime_ready"] is False
    assert report["global_write_authority_ready"] is False


def test_release_check_cli_outputs_safe_aggregate_json():
    completed = subprocess.run(
        [sys.executable, "scripts/practitioner_directory_route_readiness_release_check.py"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    report = json.loads(completed.stdout)
    assert report == build_practitioner_directory_route_readiness_release_check()
    assert "app/" not in completed.stdout
    assert "provider prompt" not in completed.stdout


def test_release_check_rejects_runtime_consumer_boundary_drift(tmp_path: Path):
    boundary = json.loads(BOUNDARY.read_text(encoding="utf-8"))
    boundary["forbidden_consumers"].remove("production app routers or services")
    boundary_path = tmp_path / "boundary.json"
    boundary_path.write_text(json.dumps(boundary), encoding="utf-8")

    with pytest.raises(ValueError, match="production app routers"):
        build_practitioner_directory_route_readiness_release_check(
            consumer_boundary_path=boundary_path
        )


def test_release_check_rejects_next_step_widening(tmp_path: Path):
    boundary = json.loads(BOUNDARY.read_text(encoding="utf-8"))
    boundary["next_allowed_step"] = "wire runtime consumers"
    boundary_path = tmp_path / "boundary.json"
    boundary_path.write_text(json.dumps(boundary), encoding="utf-8")

    with pytest.raises(ValueError, match="static release-check"):
        build_practitioner_directory_route_readiness_release_check(
            consumer_boundary_path=boundary_path
        )


def test_runtime_app_code_does_not_import_release_check_wrapper():
    forbidden = (
        "practitioner_directory_route_readiness_release_check",
        "build_practitioner_directory_route_readiness_release_check",
    )
    offenders: list[str] = []
    for path in (ROOT / "app").rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        if any(fragment in text for fragment in forbidden):
            offenders.append(str(path.relative_to(ROOT)))

    assert offenders == []
