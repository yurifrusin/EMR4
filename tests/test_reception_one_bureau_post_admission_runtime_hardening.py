from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = (
    ROOT
    / "docs"
    / "bernie-reception-one-bureau-post-admission-runtime-hardening-plan.md"
)
THREAT = (
    ROOT
    / "docs"
    / "security"
    / (
        "bernie-reception-one-bureau-post-admission-runtime-hardening-"
        "threat-model-delta.md"
    )
)
EVIDENCE = (
    ROOT
    / "orchestration"
    / "continuity"
    / "reception-one-bureau-post-admission-runtime-hardening"
    / "browser-acceptance-evidence.json"
)
META_GRID = ROOT / "docs" / "diary" / "meta-grid.js"
DIARY_HTML = ROOT / "docs" / "diary" / "diary.html"
GRAPH = ROOT / "orchestration" / "continuity" / "emr4-continuity-graph.json"
COMPASS = ROOT / "orchestration" / "continuity" / "emr4-compass.json"


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_provider_free_browser_acceptance_passes_closed_contract() -> None:
    evidence = _json(EVIDENCE)

    assert evidence["result"] == (
        "reception_one_bureau_post_admission_runtime_hardening_pass"
    )
    assert evidence["evidence_label"] == "route_intercepted_browser"
    assert evidence["data_class"] == "authored_synthetic"
    assert evidence["request_text_retained"] is False
    assert evidence["local_fixture_response_count"] == 6
    assert evidence["blocked_external_hosts"] == [
        "appsforoffice.microsoft.com"
    ]
    assert evidence["provider_calls"] == 0
    assert evidence["credential_reads"] == 0
    assert evidence["database_reads"] == 0
    assert evidence["database_writes"] == 0
    assert evidence["appointment_confirmation_performed"] is False
    assert evidence["appointment_write_performed"] is False
    assert all(evidence["checks"].values())


def test_standard_and_isolated_share_only_admitted_provenance_renderer() -> None:
    evidence = _json(EVIDENCE)
    standard = evidence["standard"]
    isolated = evidence["isolated"]

    assert standard["submitted_modes"] == ["deterministic"]
    assert standard["proposal_visible"] is True
    assert standard["provenance_visible"] is True
    assert "Standard planner" in standard["provenance_text"]
    assert "Proofreader admitted" in standard["provenance_text"]
    assert "0 provider calls" in standard["provenance_text"]
    assert standard["audit_visible"] is False

    assert isolated["submitted_modes"] == ["isolated_vertex"]
    assert isolated["proposal_visible"] is True
    assert isolated["provenance_visible"] is True
    assert "Isolated model" in isolated["provenance_text"]
    assert "Proofreader admitted" in isolated["provenance_text"]
    assert "1 provider call" in isolated["provenance_text"]
    assert isolated["audit_visible"] is True


def test_mode_switch_discards_proposal_provenance_and_audit() -> None:
    evidence = _json(EVIDENCE)

    for case in ("standard", "isolated"):
        after = evidence[case]["after_switch"]
        assert after["proposal_visible"] is False
        assert after["provenance_visible"] is False
        assert after["audit_visible"] is False
        assert after["request_retained"] is True
        assert "previous proposal was cleared" in after["announcement"]


def test_every_malformed_admission_tuple_fails_closed() -> None:
    evidence = _json(EVIDENCE)

    assert set(evidence["mismatch_cases"]) == {
        "planner_mismatch",
        "proofreader_mismatch",
        "call_count_mismatch",
        "audit_reference_mismatch",
    }
    for outcome in evidence["mismatch_cases"].values():
        assert outcome["projection_state"] == "blocked"
        assert outcome["proposal_visible"] is False
        assert outcome["provenance_visible"] is False
        assert outcome["audit_visible"] is False


def test_client_contract_is_exact_and_clears_planner_scoped_state() -> None:
    source = META_GRID.read_text(encoding="utf-8")

    assert 'payload.review?.disposition === "admit"' in source
    assert "responsePlannerMode === requestedPlannerMode" in source
    assert 'requestedPlannerMode === "deterministic"' in source
    assert "providerCalls === 0" in source
    assert 'requestedPlannerMode === "isolated_vertex"' in source
    assert "providerCalls === 1" in source
    assert "runtimeAuditRef !== null" in source
    assert "if (!provenanceContractAdmitted)" in source
    assert "clearPlannerScopedResultForModeChange()" in source
    assert "state.selectedAppointment = null;" in source
    assert 'projectionState: "planner_reselection_required"' in source
    assert "meta-grid.js?v=16" in DIARY_HTML.read_text(encoding="utf-8")


def test_plan_and_threat_delta_keep_provider_and_write_gates_closed() -> None:
    plan = PLAN.read_text(encoding="utf-8")
    threat = THREAT.read_text(encoding="utf-8")

    assert "This tranche makes no provider call and reads no ADC." in plan
    assert "Standard remains the visible zero-provider default." in plan
    assert "The browser has no confirmation or write command." in threat
    assert "no fallback" in threat
    assert "or provider call is permitted in this tranche." in threat


def test_continuity_and_compass_bind_accepted_provider_free_result() -> None:
    graph = _json(GRAPH)
    compass = _json(COMPASS)
    node = next(
        item
        for item in graph["nodes"]
        if item["id"]
        == "reception-one-bureau-post-admission-runtime-hardening"
    )
    assert not any(
        item["id"] == "reception-one-word-online-authenticated-dialog-check"
        for item in compass["decision_horizon"]
    )

    assert graph["graph_revision"] >= 167
    assert compass["source_graph_revision"] == graph["graph_revision"]
    assert compass["map_revision"] >= 148
    assert node["status"] == "accepted"
    assert any(
        item["node_id"] == node["id"]
        for item in compass["journey"]
    )
    assert compass["current_position"]["node_id"] == (
        "raisa-word-online-authenticated-companion-verification"
    )
