import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DRAFT_JSON = ROOT / "docs" / "bernie-ui-derived-state-dag-d5-approval-decision-draft.json"
DRAFT_MD = ROOT / "docs" / "bernie-ui-derived-state-dag-d5-approval-decision-draft.md"
GATE_JSON = ROOT / "docs" / "bernie-ui-derived-state-dag-d5-response-delivery-gate.json"


def _load_json_no_duplicate_keys(path: Path) -> dict:
    raw = path.read_text(encoding="utf-8")

    def reject_duplicates(pairs):
        counts = Counter(key for key, _ in pairs)
        duplicates = sorted(key for key, count in counts.items() if count > 1)
        assert not duplicates, f"duplicate keys in {path}: {duplicates}"
        return dict(pairs)

    return json.loads(raw, object_pairs_hook=reject_duplicates)


def test_d5_approval_decision_draft_is_blocked_and_unacknowledged():
    draft = _load_json_no_duplicate_keys(DRAFT_JSON)

    assert draft["schema_version"] == "bernie.ui_dag.d5_approval_decision_draft.v1"
    assert draft["decision"] == "blocked"
    assert draft["reviewer"] == ""
    assert draft["go_no_go_acknowledged"] is False
    assert draft["approved_contract_commit"] == ""
    assert draft["approval_expires_on"] == ""
    assert draft["recommended_approval_expiry_days"] == 14
    assert draft["proposed_decision_if_approved"] == (
        "approved_for_backend_response_delivery_first_slice"
    )


def test_d5_approval_scope_fields_all_remain_false():
    draft = _load_json_no_duplicate_keys(DRAFT_JSON)
    scope = draft["approval_scope"]

    assert scope
    assert all(value is False for value in scope.values())
    assert scope["backend_response_delivery_first_slice_approved"] is False
    assert scope["route_or_schema_change_approved"] is False
    assert scope["graphql_delivery_approved"] is False
    assert scope["provider_or_live_provider_wiring_approved"] is False
    assert scope["appointment_write_behavior_change_approved"] is False
    assert scope["model_to_database_write_approved"] is False


def test_d5_approval_draft_points_to_required_evidence_contracts():
    draft = _load_json_no_duplicate_keys(DRAFT_JSON)

    assert "docs/bernie-ui-derived-state-dag-evidence-consolidation.md" in draft[
        "source_contracts"
    ]
    assert "docs/bernie-ui-derived-state-dag-d5-response-delivery-gate.json" in draft[
        "source_contracts"
    ]
    assert "docs/bernie-ui-derived-state-dag-d5-implementation-checklist.md" in draft[
        "source_contracts"
    ]
    assert "docs/bernie-ui-derived-state-dag-d5-router-import-guard-plan.md" in draft[
        "source_contracts"
    ]
    assert draft["candidate_contract_commits"] == [
        {
            "commit": "77c01756",
            "artifact": "docs/bernie-ui-derived-state-dag-evidence-consolidation.md",
            "purpose": "review-only evidence consolidation",
        }
    ]


def test_d5_approval_draft_preserves_forbidden_scope_and_readiness_values():
    draft = _load_json_no_duplicate_keys(DRAFT_JSON)

    forbidden = set(draft["forbidden_even_if_future_first_slice_is_approved"])
    assert "graphql_resolver_emits_bernie_ui_view_model" in forbidden
    assert "provider_prompt_uses_bernie_ui_view_model" in forbidden
    assert "access_ai_invocation" in forbidden
    assert "memory_rag_or_graphrag_runtime_access" in forbidden
    assert "h15_or_h_series_runtime_input" in forbidden
    assert "historical_diary_material_runtime_input" in forbidden
    assert "database_write_depends_on_view_model_fields" in forbidden

    assert set(draft["required_review_values_before_approval"]) >= {
        "runtime_or_provider_wiring_ready=false",
        "raw_trove_access_ready=false",
        "runtime_gate_decision=blocked",
        "default_provider=disabled",
        "live_provider_enabled=false",
        "provider_calls_performed=false",
    }


def test_existing_d5_gate_remains_blocked_while_draft_exists():
    gate = _load_json_no_duplicate_keys(GATE_JSON)

    assert gate["decision"] == "blocked"
    assert gate["backend_response_delivery_approved"] is False
    assert gate["rest_or_fastapi_route_change_approved"] is False
    assert gate["provider_or_live_provider_wiring_approved"] is False
    assert gate["model_to_database_write_approved"] is False


def test_d5_approval_markdown_says_draft_not_approval():
    text = DRAFT_MD.read_text(encoding="utf-8")

    assert "Status: blocked decision draft" in text
    assert "This is not an approval" in text
    assert "`approved_for_backend_response_delivery_first_slice`" in text
    assert "Every approval-scope field remains false" in text
    assert "one reviewed Bernie response assembly point" in text
    assert "runtime_gate_decision=blocked" in text
    assert "provider_calls_performed=false" in text
