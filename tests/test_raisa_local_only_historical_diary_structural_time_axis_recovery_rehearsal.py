import json
from pathlib import Path
from typing import get_args

import pytest

from orchestration_harness import historical_diary_local_measured_privacy_probe as probe


PLAN = Path(
    "docs/raisa-local-only-historical-diary-structural-time-axis-recovery-rehearsal-plan.md"
)
THREAT = Path(
    "docs/security/raisa-local-only-historical-diary-structural-time-axis-recovery-rehearsal-threat-model-delta.md"
)
GATE = Path(
    "orchestration/continuity/raisa-local-only-historical-diary-structural-time-axis-recovery-rehearsal/historical-derived-scenario-first-use-gate.json"
)


def test_plan_freezes_same_cell_explicit_anchor_and_one_run_boundary():
    plan = PLAN.read_text(encoding="utf-8")
    threat = THREAT.read_text(encoding="utf-8")

    assert "anchor in the same original table cell" in plan
    assert "never infer a time from table row" in plan
    assert "Phase B may run at most once" in plan
    assert "2026-08-24-time-axis-v1" in plan
    assert "gate attaches only at the first reusable historical-derived" in threat


def test_first_use_gate_is_closed_typed_narrow_and_non_transitive():
    gate = json.loads(GATE.read_text(encoding="utf-8"))

    assert gate["status"] == "closed_pending_candidate_specific_evaluation"
    assert gate["activation_trigger"].startswith("before_first_reusable_historical_derived")
    assert gate["decision_vocabulary"] == [
        "blocked",
        "revision_required",
        "admitted_for_exact_declared_artifact_only",
    ]
    assert "wholly_authored_synthetic_tests" in gate["does_not_apply_to"]
    assert "full_40_character_accepted_source_commit" in gate["required_candidate_fields"]
    assert gate["authority"] == {
        "opened_by_this_contract": False,
        "opened_by_time_axis_success": False,
        "provider_model_or_runtime_use": False,
        "product_or_ordinary_practice_use": False,
        "production_deployment_release_pages_or_protected_refs": False,
    }


def test_content_run_terminal_prevents_second_execute(monkeypatch, tmp_path):
    terminal = tmp_path / "content-run-terminal.json"
    terminal.write_text("{}", encoding="utf-8")
    monkeypatch.setattr(probe, "CONTENT_RUN_TERMINAL_PATH", terminal)
    monkeypatch.setattr(
        probe,
        "_load_manifest",
        lambda: pytest.fail("manifest must not load after content run is consumed"),
    )

    with pytest.raises(probe.ProbeError, match="content_run_already_consumed"):
        probe.execute()


def test_projection_schema_remains_exact_as_fresh_attempt_roots_advance():
    assert get_args(probe.PrivateProjection.model_fields["schema_version"].annotation) == (
        "historical_diary.private_derived_grid_projection.v3",
    )
