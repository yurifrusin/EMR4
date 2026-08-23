import inspect
import json
from pathlib import Path

from orchestration_harness import historical_diary_local_measured_privacy_probe as probe


PLAN = Path(
    "docs/raisa-local-only-historical-diary-leading-explicit-time-token-bounded-measurement-rehearsal-plan.md"
)
THREAT = Path(
    "docs/security/raisa-local-only-historical-diary-leading-explicit-time-token-bounded-measurement-rehearsal-threat-model-delta.md"
)
CONTRACT = Path(
    "orchestration/continuity/raisa-provider-free-authored-synthetic-historical-diary-leading-explicit-time-token-recovery-rehearsal/next-tranche-contract.json"
)
EXTRACTOR = Path("scripts/historical_diary_local_measured_privacy_probe.ps1")


def test_plan_contract_and_threat_freeze_one_fresh_v3_terminal():
    plan = PLAN.read_text(encoding="utf-8")
    threat = THREAT.read_text(encoding="utf-8")
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))

    assert "2026-08-24-leading-token-v3" in plan
    assert "There is no second bind" in plan
    assert "No second content run" in plan
    assert "first-use gate remains `closed_pending_candidate_specific_evaluation`" in plan
    assert "A fresh measurement becomes another retry loop" in threat
    assert contract["source_boundary"]["new_attempt_root"].endswith(
        "2026-08-24-leading-token-v3"
    )
    assert contract["execution"] == {
        "metadata_bind_attempts": 1,
        "content_runs": 1,
        "content_retry_authorized": False,
        "controller_timeout_seconds": 1800,
        "exact_parent_word_cleanup": True,
        "count_only_progress": True,
    }


def test_python_and_word_extractor_bind_only_literal_v3_attempt_root():
    expected = (
        probe.REPO_ROOT
        / "local_data/historical-diary-trove/measured-probes/2026-08-24-leading-token-v3"
    )
    python_source = Path(probe.__file__).read_text(encoding="utf-8")
    powershell_source = EXTRACTOR.read_text(encoding="utf-8")

    assert probe.ATTEMPT_ROOT == expected
    assert "2026-08-24-leading-token-v3" in python_source
    assert "2026-08-24-story-coordinate-v2" not in python_source
    assert "2026-08-24-leading-token-v3" in powershell_source
    assert "2026-08-24-story-coordinate-v2" not in powershell_source


def test_execute_retains_1800_second_parent_ceiling_and_historical_profile():
    source = inspect.getsource(probe.execute)

    assert "timeout_seconds=1800" in source
    assert "HistoricalMeasuredProbe" in source


def test_measurement_keeps_parser_admission_and_first_use_closed():
    source = inspect.getsource(probe.project_and_measure)
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))

    assert "leading_time_count" in source
    assert "explicit_time_source_count" in source
    assert 'time_mapping = "leading_explicit_time_token"' in source
    assert contract["first_use_gate"] == {
        "status": "closed_pending_candidate_specific_evaluation",
        "opened_by_measurement_success": False,
        "candidate_evaluation_deferred_until_a_specific_useful_derivative_exists": True,
    }
