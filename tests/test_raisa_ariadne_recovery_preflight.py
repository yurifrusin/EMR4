import json
from pathlib import Path

import pytest

from scripts.raisa_ariadne_recovery_preflight import (
    ALLOWED_G0_TRACKED_PATHS,
    EXPECTED_RISKS,
    _alembic_heads,
    _changed_tracked_paths,
    _remote_baseline_snapshot,
    _risk_ids,
    build_task_manifest,
    build_report,
    main,
)


ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "orchestration/programme/current-state.json"


def load_state() -> dict:
    return json.loads(STATE.read_text(encoding="utf-8"))


def test_g0_recovery_preflight_passes_while_preserving_global_red() -> None:
    report = build_report(ROOT, build_task_manifest(ROOT), "development")

    assert report["status"] == "passed"
    assert report["programme_mode"] == "recovery"
    assert report["current_gate"] == "G0"
    assert report["feature_work_eligible"] is False
    assert report["global_gate"] == "red_repair_only"
    assert report["failed_checks"] == []
    assert all(check["passed"] for check in report["checks"])


@pytest.mark.parametrize("task_class", ["product_feature", "g1a", "integration"])
def test_every_out_of_gate_task_class_is_mechanically_blocked(
    task_class: str,
) -> None:
    manifest = build_task_manifest(ROOT)
    manifest["task_class"] = task_class
    report = build_report(ROOT, manifest, "development")

    assert report["status"] == "blocked"
    assert report["feature_work_eligible"] is False
    assert "programme_admission" in report["failed_checks"]


def test_missing_programme_state_fails_closed(tmp_path: Path, capsys) -> None:
    exit_code = main(
        [
            "--repo-root",
            str(tmp_path),
            "--format",
            "json",
        ]
    )

    report = json.loads(capsys.readouterr().out)
    assert exit_code == 2
    assert report["status"] == "blocked"
    assert report["failed_checks"] == ["programme_state_missing_or_invalid"]


def test_machine_state_freezes_authority_and_forbidden_actions() -> None:
    state = load_state()

    assert state["machine_authoritative"] is True
    assert state["programme_mode"] == "recovery"
    assert state["current_gate"] == "G0"
    assert state["current_gate_status"] == "revision_required"
    assert state["active_correction"] == "G0.6"
    assert state["active_profile"] == "G0.6_CONTROLLER_MAINTENANCE"
    assert state["feature_work_eligible"] is False
    assert state["g0_2_correction"]["status"] == "superseded_revision_required"
    assert state["g0_4_correction"]["status"] == "superseded_revision_required"
    assert state["g0_5_correction"]["status"] == "superseded_revision_required"
    assert state["g0_6_correction"]["status"] in {"in_progress", "review_pending"}
    assert state["g0_6_correction"]["authorized_parent_commit"] == (
        "71e2c5f2f586fa4d1ca8fa9787a4906dbbb997f1"
    )
    assert state["g0_6_correction"]["reviewed_g0_5_tree"] == (
        "ef84162bbc6ef24241678d14e0183b876af3a1e3"
    )
    assert state["g0_2_correction"]["g1a_authorized"] is False
    assert state["recovery_baton"]["base_sha"] == (
        "03e6860394c39086ec1ffb3f2457acc5f7c8b5f9"
    )
    assert state["protected_refs"]["expected_sha"] == (
        "2e34bdad732fdab32fbf778280b3d3c70d66d602"
    )
    assert state["actions_performed"] == {
        "protected_ref_movements": 0,
        "branches_deleted": 0,
        "feature_branches_rebased": 0,
        "prs_closed": 0,
        "prs_merged": 0,
        "pages_runs_triggered": 0,
        "deployments": 0,
        "live_provider_calls": 0,
        "real_patient_data_accesses": 0,
        "product_defects_fixed": 0,
        "g1a_started": False,
    }


def test_pre_g0_branch_inventory_remains_reproducible_after_authorized_push() -> None:
    count, digest, recovery_present, current_count = _remote_baseline_snapshot(ROOT)

    assert count == 135
    assert digest == "1478dc7a8e0a034971d1ee33996e59753469efec30e98576539a409891639730"
    assert current_count == 135 + int(recovery_present)
    assert current_count in {135, 136}


def test_risk_register_has_every_seeded_risk_exactly_once() -> None:
    assert _risk_ids(ROOT) == EXPECTED_RISKS


def test_static_alembic_graph_has_one_recorded_head() -> None:
    assert _alembic_heads(ROOT) == ["x3y4z5a6b7c8"]


def test_tracked_working_changes_cannot_escape_the_g0_allowlist() -> None:
    assert _changed_tracked_paths(ROOT) <= ALLOWED_G0_TRACKED_PATHS


def test_preflight_source_contains_no_write_or_network_primitive() -> None:
    source = (ROOT / "scripts/raisa_ariadne_recovery_preflight.py").read_text(
        encoding="utf-8"
    )

    for forbidden in (
        ".write_text(",
        ".write_bytes(",
        'open("w',
        "open('w",
        "git push",
        "git update-ref",
        "requests.",
        "urllib.request",
        "socket.",
        "psycopg",
        "sqlalchemy",
    ):
        assert forbidden not in source


def test_cli_returns_nonzero_as_positive_block_proof(capsys) -> None:
    exit_code = main(["--format", "json"])
    report = json.loads(capsys.readouterr().out)

    assert exit_code == 2
    assert report["status"] == "blocked"
    assert "programme_admission" in report["failed_checks"]
