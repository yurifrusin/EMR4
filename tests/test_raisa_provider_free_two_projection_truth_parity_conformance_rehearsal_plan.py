from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs/raisa-provider-free-two-projection-truth-parity-conformance-rehearsal-plan.md"
THREAT = ROOT / "docs/security/raisa-provider-free-two-projection-truth-parity-conformance-rehearsal-threat-model-delta.md"
LATCH = ROOT / "orchestration/continuity/ariadne-active-operation-latch/current.json"


def test_plan_freezes_projection_neutral_truth_parity_boundary() -> None:
    text = PLAN.read_text(encoding="utf-8")
    for phrase in (
        "truth parity, not feature parity",
        "exactly `conventional_grid` and `reception_one`",
        "route_intercepted_browser",
        "safe",
        "cancelled",
        "blocked",
        "stale",
        "failed",
        "committed",
        "byte-for-byte equal",
        "Do not repair product behavior",
        "not a runtime session",
        "explicit-path staging only",
    ):
        assert phrase in text


def test_plan_keeps_api_and_authority_surfaces_closed() -> None:
    text = (PLAN.read_text(encoding="utf-8") + "\n" + THREAT.read_text(encoding="utf-8")).lower()
    for phrase in (
        "graphql remains read-only",
        "existing appointment-status",
        "no product javascript/css/html",
        "no live backend",
        "product/patient/clinical data",
        "protected-ref",
    ):
        assert phrase in text


def test_active_latch_remains_bound_to_rehearsal_source_and_boundary() -> None:
    latch = json.loads(LATCH.read_text(encoding="utf-8"))
    assert latch["operation_id"] == "raisa-provider-free-two-projection-truth-parity-conformance-rehearsal"
    assert latch["status"] in {"in_progress", "blocked"}
    if latch["status"] == "in_progress":
        assert latch["source_head"] == "fbb2fd1822f73b2469fc774eb001af31dfdfa85b"
        assert latch["resume_after_compaction"] is True
        assert latch["terminal_response"] == {
            "permitted": False,
            "reason": "unfinished_authorized_operation",
        }
    else:
        assert latch["source_head"] == "18aa4b613d735a68a7f6f2e55d34e498176c9935"
        assert latch["resume_after_compaction"] is False
        assert latch["user_attention"]["required"] is True
        assert latch["terminal_response"]["permitted"] is True
    assert "evidence_trace_not_runtime_contract" in latch["protected_boundaries"]
