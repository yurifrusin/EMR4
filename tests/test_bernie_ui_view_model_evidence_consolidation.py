from pathlib import Path


DOC = Path("docs/bernie-ui-derived-state-dag-evidence-consolidation.md")


def _text() -> str:
    return DOC.read_text(encoding="utf-8")


def test_evidence_consolidation_preserves_review_only_status_and_api_spine_boundary():
    text = _text()

    assert "Status: review-only consolidation" in text
    assert "read/display contract" in text
    assert "REST/OpenAPI confirm commands own appointment writes" in text
    assert "must never appear in a confirm payload" in text
    assert "model-to-database writes" in text


def test_evidence_consolidation_names_proven_selector_and_ui_evidence():
    text = _text()

    assert "app/services/bernie/ui_view_model.py" in text
    assert "tests/test_bernie_ui_view_model.py" in text
    assert "test_bernie_ui_view_model_proposal_ready_drives_display_without_payload_leak" in text
    assert "test_bernie_ui_view_model_candidate_slots_win_over_legacy_blocked_status" in text
    assert "test_bernie_ui_view_model_non_ready_states_do_not_show_confirm_or_success" in text
    assert "test_bernie_ui_view_model_clarification_blocks_legacy_confirmable_payload" in text
    assert "test_bernie_ui_view_model_identity_ambiguous_blocks_confirm_and_shows_choices" in text


def test_evidence_consolidation_labels_route_intercepted_not_live():
    text = _text()

    assert "route-intercepted Playwright evidence" in text
    assert 'response["evidence_label"] =' in text
    assert "unexpected write" in text
    assert "not live backend evidence" in text
    assert "not live provider evidence" in text
    assert "No current D4/D5 evidence proves production route emission" in text
    assert "trigger the D5 gate review" in text


def test_evidence_consolidation_restates_payload_and_write_authority_boundary():
    text = _text()

    assert "display-only state" in text
    assert "carries no write authority" in text
    assert "confirm_endpoint" in text
    assert "confirm_payload" in text
    assert "turn_ref" in text
    assert "candidate_freshness_id" in text
    assert "proposal_freshness_id" in text
    assert "writes_authorized" in text
    assert "appointment_id" in text
    assert "no appointment has been made yet" in text


def test_evidence_consolidation_keeps_d5_delivery_and_runtime_gates_blocked():
    text = _text()

    for phrase in [
        "production route emission of `BernieUiViewModel`",
        "GraphQL resolver delivery",
        "provider prompt or live-provider wiring",
        "memory/RAG/GraphRAG runtime access",
        "H15/H-series or historical diary runtime inputs",
        "confirm payload changes",
        "appointment write behavior changes",
        "external patient-client exposure",
        "runtime_or_provider_wiring_ready=false",
        "raw_trove_access_ready=false",
        "runtime_gate_decision=blocked",
        "default_provider=disabled",
        "live_provider_enabled=false",
        "provider_calls_performed=false",
    ]:
        assert phrase in text


def test_evidence_consolidation_points_to_next_review_block_before_approval():
    text = _text()

    assert "Sprint 246" in text
    assert "approval-decision draft" in text
    assert "Sprint 247" in text
    assert "backend delivery test plan" in text
    assert "Sprint 248 readiness snapshot" in text
    assert "Keep D5 blocked" in text
    assert "Approve narrow D5 slice" in text
    assert "Approve D5 with extra readiness margin" in text
    assert "recommended next real move after Sprints 246-248" in text
    assert "Until that explicit approval exists" in text
