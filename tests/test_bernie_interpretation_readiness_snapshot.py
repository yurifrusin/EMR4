"""Golden blocked-readiness snapshot for the Bernie interpretation harness."""

import json
from pathlib import Path

from scripts.bernie_interpretation_readiness_check import build_readiness_status


SNAPSHOT_PATH = Path(
    "tests/fixtures/bernie_interpretation_readiness/blocked_readiness_status.json"
)


def _snapshot():
    return json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))


def test_generated_readiness_status_matches_blocked_snapshot():
    assert build_readiness_status() == _snapshot()


def test_readiness_snapshot_remains_non_authorizing():
    snapshot = _snapshot()

    assert snapshot["runtime_gate_decision"] == "blocked"
    assert snapshot["runtime_or_provider_wiring_ready"] is False
    assert snapshot["raw_trove_access_ready"] is False
    assert snapshot["sprint_engine_state"] == "continuing"


def test_readiness_snapshot_contains_no_payload_or_prompt_fragments():
    serialized = SNAPSHOT_PATH.read_text(encoding="utf-8").casefold()

    for fragment in [
        "book an appointment",
        "which patient",
        "ignore the rules",
        "patient_id",
        "practitioner_id",
        "appointment_id",
        "payload",
        "/api/",
        "local_data",
        "h15",
        "h_series",
    ]:
        assert fragment not in serialized
