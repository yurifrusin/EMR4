import json
from pathlib import Path

import pytest

import orchestration_harness.programme_admission as pa

from scripts.raisa_ariadne_recovery_preflight import (
    EXPECTED_RISKS,
    _alembic_heads,
    _changed_tracked_paths,
    _remote_baseline_snapshot,
    _risk_ids,
    _verification_phase,
    PreflightError,
    build_task_manifest,
    build_report,
    main,
)


ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "orchestration/programme/current-state.json"


def load_state() -> dict:
    return json.loads(STATE.read_text(encoding="utf-8"))


def test_g0_recovery_preflight_uses_the_current_git_lifecycle_phase() -> None:
    phase = _verification_phase(ROOT, load_state())
    with pytest.raises(PreflightError, match="no implementation task"):
        build_task_manifest(ROOT)
    report = build_report(ROOT, None, phase)

    assert report["status"] == "blocked"
    assert report["phase"] == phase
    assert report["programme_mode"] == "recovery"
    assert report["current_gate"] == "G1A.3"
    assert report["feature_work_eligible"] is False
    assert report["global_gate"] == "red_repair_only"
    assert "programme_admission" in report["failed_checks"]


@pytest.mark.parametrize("task_class", ["product_feature", "g1a", "integration"])
def test_every_out_of_gate_task_class_is_mechanically_blocked(
    task_class: str,
) -> None:
    policy = pa.load_programme_policy(ROOT)
    manifest = {
        "schema_version": pa.TASK_MANIFEST_VERSION,
        "task_id": "closed-candidate-probe",
        "task_class": task_class,
        "programme_gate": "G1A.1",
        "objective": "Prove the owner disposition does not open implementation.",
        "base_commit": "91f1e6e645424a448bdcdfa2adabb86d31fb5f0b",
        "candidate_or_current_head": "91f1e6e645424a448bdcdfa2adabb86d31fb5f0b",
        "allowed_path_roots": [],
        "intended_side_effect_classes": ["repository_read"],
        "forbidden_side_effect_classes": sorted(pa.G1A_FORBIDDEN_EFFECTS),
        "state_digest": policy.state_digest,
        "policy_digest": policy.policy_digest,
    }
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
    assert state["current_gate"] == "G1A.3"
    assert state["current_gate_status"] == "revision_required"
    assert state["active_correction"] == "G1A.3-R0"
    assert state["active_profile"] == pa.G1A3_R0_REVIEW_PENDING_PROFILE
    assert state["g1a_subgate_authority"]["subgates"]["G1A.3"]["owner_exception"][
        "task_generation"
    ] == ("g1a3-r0-review-producer-body-only-ast-replacement-20260830-v1")
    assert state["feature_work_eligible"] is False
    assert state["g0_2_correction"]["status"] == "superseded_revision_required"
    assert state["g0_4_correction"]["status"] == "superseded_revision_required"
    assert state["g0_5_correction"]["status"] == "superseded_revision_required"
    assert state["g0_6_correction"]["status"] == "superseded_revision_required"
    assert state["g0_8_correction"]["status"] == "external_review_passed"
    assert state["g0_8_correction"]["authorized_parent_commit"] == (
        "6e101d15f824f68c3f44d0a3cb44a3aa2afd5b1b"
    )
    assert state["g0_8_correction"]["reviewed_g0_7_tree"] == (
        "00c1af2f47ceee88c10507809f69058c24c6bd85"
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
    assert _changed_tracked_paths(ROOT) <= set(
        pa.load_programme_policy(ROOT).full_range_allowed_paths
    )


def test_r0_has_no_task_and_synthetic_r1_manifest_is_exact(tmp_path: Path) -> None:
    from tests.test_programme_admission import (
        _build_g1a3_r0_transition_repository,
        _git,
    )

    with pytest.raises(PreflightError, match="no implementation task"):
        build_task_manifest(ROOT)

    target, _gatekeeper, _manifest, _r0 = _build_g1a3_r0_transition_repository(tmp_path)
    _git(target, "commit", "--no-verify", "-m", "synthetic R0 to R1 transition")
    manifest = build_task_manifest(target)

    assert manifest["task_class"] == pa.G1A3_R1_TASK_CLASS
    assert set(manifest["allowed_path_roots"]) == pa.G1A3_R1_ALLOWED_PATHS
    assert set(manifest["intended_side_effect_classes"]) == (pa.G1A3_R1_ALLOWED_EFFECTS)
    for entrypoint in ("provider_invocation", "integration"):
        decision = pa.evaluate_programme_admission(
            repo_root=target,
            manifest=manifest,
            entrypoint=entrypoint,
        )
        assert decision.admitted is False


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
