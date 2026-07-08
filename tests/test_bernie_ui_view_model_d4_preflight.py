from pathlib import Path


PREFLIGHT = Path("docs/bernie-ui-derived-state-dag-d4-preflight.md")


def _compact() -> str:
    return " ".join(PREFLIGHT.read_text(encoding="utf-8").split())


def test_preflight_is_review_only_and_not_wiring():
    text = _compact()

    for phrase in [
        "preflight/review only",
        "No UI wiring",
        "No UI wiring, route wiring, backend response wiring",
        "no production route imports `app.services.bernie.ui_view_model`",
    ]:
        assert phrase in text


def test_preflight_cites_required_blocked_readiness_values():
    text = _compact()

    for phrase in [
        ".venv\\Scripts\\python.exe scripts\\bernie_interpretation_readiness_check.py",
        ".venv\\Scripts\\python.exe scripts\\bernie_provider_boundary_readiness_report.py",
        "runtime_or_provider_wiring_ready=false",
        "raw_trove_access_ready=false",
        "runtime_gate_decision=blocked",
        "default_provider=disabled",
        "live_provider_enabled=false",
        "provider_calls_performed=false",
        "route_behavior_changed=false",
        "database_access_performed=false",
        "memory_or_rag_access_performed=false",
        "historical_diary_material_access_performed=false",
    ]:
        assert phrase in text


def test_preflight_defines_narrow_d4_ui_surface():
    text = _compact()

    for phrase in [
        "renderBernieReview",
        "candidate slot list visibility",
        "pending proposal card visibility",
        "`bernie-review-confirm-button` visibility/enabled state",
        "stale/session warning visibility",
        "success copy visibility after the existing signed REST confirm call reports success",
        "retry/edit or choose-another-time affordances",
        "`renderBernieToolIntentReview`",
        "command payload changes",
        "backend route/response changes",
    ]:
        assert phrase in text


def test_preflight_fixture_matrix_covers_fable_required_states():
    text = _compact()

    for fixture in [
        "candidate_slots_available",
        "proposal_ready",
        "pressed_or_awaiting_backend",
        "backend_confirmed_success",
        "stale_proposal",
        "backend_rejected",
        "ambiguous_identity",
    ]:
        assert fixture in text


def test_preflight_acceptance_preserves_copy_and_command_boundaries():
    text = _compact()

    for phrase in [
        "route-intercepted evidence labels are explicit",
        "no test claims live backend or live provider evidence",
        "`missing_practitioner_id`, generic `Not Found`, `booked`, and `confirmed`",
        "`pressed` and `awaiting_backend` states do not claim success",
        "command payloads still contain existing signed proposal/freshness/evidence fields",
        "do not contain `BernieUiViewModel` fields",
        "`copy_mode`",
        "`confirmation_state`",
        "`freshness_state`",
        "`flags`",
    ]:
        assert phrase in text


def test_preflight_stop_conditions_keep_blocked_gates_closed():
    text = _compact()

    for phrase in [
        "backend route or schema changes",
        "live provider or provider dry-run evidence",
        "new appointment write behavior",
        "model-to-database writes",
        "GraphQL resolver changes",
        "H15/H-series or historical diary runtime inputs",
        "memory/RAG/GraphRAG access",
        "external patient-client exposure",
    ]:
        assert phrase in text
