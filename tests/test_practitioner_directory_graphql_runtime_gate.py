import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "docs" / "api-spine" / "practitioner-directory-graphql-runtime-gate.json"
GATE_MD = ROOT / "docs" / "api-spine" / "practitioner-directory-graphql-runtime-gate.md"
APP = ROOT / "app"


def _payload() -> dict:
    return json.loads(GATE.read_text(encoding="utf-8"))


def _app_text() -> str:
    return "\n".join(
        path.read_text(encoding="utf-8", errors="replace")
        for path in sorted(APP.rglob("*.py"))
    )


def test_runtime_gate_shape_records_yuri_packet_only_approval():
    payload = _payload()

    assert payload["schema_version"] == "api_spine.practitioner_directory_graphql_runtime_gate.v1"
    assert payload["sprint"] == 267
    assert payload["reviewer"] == "yuri"
    assert payload["decision"] == "approved_for_gate_packet_only"
    assert payload["target_field"] == "Query.practice.practitioners"
    assert payload["approval_source"]["kind"] == "explicit_yuri_chat_authorization"
    assert "resolver code still blocked" in payload["approval_source"]["statement"]


def test_runtime_choice_is_defined_but_dependency_and_endpoint_remain_blocked():
    payload = _payload()

    assert payload["selected_runtime_library"]["library"] == "strawberry-graphql"
    assert payload["selected_runtime_library"]["dependency_install_authorized"] is False
    assert payload["selected_runtime_library"]["exact_version_selection_deferred"] is True
    assert payload["future_runtime_surface"]["endpoint_path"] == "/api/v1/graphql"
    assert payload["future_runtime_surface"]["endpoint_authorized_now"] is False
    assert payload["future_runtime_surface"]["mutations_allowed"] is False
    assert payload["future_runtime_surface"]["subscriptions_allowed"] is False
    assert payload["future_runtime_surface"]["introspection_production_allowed"] is False
    candidates = {row["library"]: row["status"] for row in payload["runtime_library_candidates"]}
    assert candidates == {
        "strawberry-graphql": "preferred",
        "ariadne": "declined_for_first_slice",
        "graphene": "declined_for_first_slice",
    }


def test_authorized_now_blocks_all_runtime_code_and_readiness_changes():
    payload = _payload()

    assert payload["authorized_now"] == {
        "gate_packet": True,
        "dependency_install": False,
        "graphql_endpoint": False,
        "schema_runtime_code": False,
        "resolver_code": False,
        "readiness_flag_changes": False,
    }
    assert all(value is False for value in payload["must_remain_false"].values())


def test_auth_error_depth_cost_and_resolver_contract_are_complete():
    payload = _payload()

    assert payload["auth_error_model"]["auth_context_source"].startswith("Authorization bearer token")
    assert payload["auth_error_model"]["missing_or_invalid_token_error"] == "UNAUTHENTICATED"
    assert payload["auth_error_model"]["active_only_false_without_admin_owner_error"] == "FORBIDDEN"
    assert payload["auth_error_model"]["limit_or_offset_invalid_error"] == "BAD_USER_INPUT"
    assert payload["auth_error_model"]["internal_exception_error"] == "INTERNAL_ERROR"
    assert payload["auth_error_model"]["raw_sql_error_exposure_allowed"] is False
    assert payload["auth_error_model"]["stack_trace_exposure_allowed"] is False

    depth_cost = payload["depth_cost_posture"]
    assert depth_cost["development_depth_limit_required_before_endpoint_mount"] is True
    assert depth_cost["development_cost_limit_required_before_endpoint_mount"] is True
    assert depth_cost["proposed_development_max_depth"] == 6
    assert depth_cost["proposed_development_cost_budget"] == 500
    assert depth_cost["alias_repetition_must_count_against_cost"] is True
    assert depth_cost["introspection_dev_test_allowed"] is True
    assert depth_cost["introspection_production_allowed"] is False
    assert depth_cost["practice_practitioners_default_limit"] == 50
    assert depth_cost["practice_practitioners_max_limit"] == 200
    assert depth_cost["practice_practitioners_default_offset"] == 0

    security = payload["dependency_security_risk_assessment"]
    assert security["new_dependency_surface"] is True
    assert security["known_cve_review_required_before_dependency_install"] is True
    assert security["fastapi_pydantic_sqlalchemy_conflict_check_required"] is True

    contract = payload["resolver_contract"]
    assert contract["sole_data_path"].endswith("list_practitioner_directory")
    assert contract["rest_router_import_allowed"] is False
    assert contract["independent_sqlalchemy_query_allowed"] is False
    assert contract["provider_access_ai_memory_rag_graphrag_allowed"] is False
    assert contract["writes_or_audit_writes_allowed"] is False
    assert "ahpra_number" in contract["sensitive_fields_forbidden"]


def test_required_implementation_test_matrix_is_explicit():
    tests = set(_payload()["required_test_matrix"])

    assert len(tests) >= 25
    assert {
        "test_graphql_runtime_dependency_is_explicit_and_pinned",
        "test_graphql_endpoint_is_mounted_only_at_api_v1_graphql",
        "test_graphql_schema_has_query_and_no_mutation",
        "test_query_practice_practitioners_requires_auth",
        "test_default_limit_returns_at_most_50_practitioners",
        "test_limit_200_returns_at_most_200_practitioners",
        "test_offset_skips_ordered_practitioners",
        "test_practitioners_limit_and_offset_bounds",
        "test_active_only_false_requires_admin_or_practice_owner",
        "test_active_only_false_with_admin_or_owner_returns_inactive",
        "test_sensitive_fields_absent_from_schema_and_response",
        "test_resolver_uses_shared_read_service_only",
        "test_resolver_does_not_call_rest_route_over_http",
        "test_resolver_does_not_import_rest_router_modules",
        "test_resolver_does_not_perform_independent_sqlalchemy_query",
        "test_depth_and_cost_limits_fail_closed",
        "test_alias_repetition_counts_against_cost_budget",
        "test_unhandled_resolver_exception_maps_to_internal_error",
    }.issubset(tests)


def test_no_graphql_runtime_code_or_dependency_was_added_by_gate_packet():
    app_text = _app_text().lower()
    dependency_text = "\n".join(
        path.read_text(encoding="utf-8", errors="replace").lower()
        for pattern in ("pyproject.toml", "requirements*.txt")
        for path in ROOT.glob(pattern)
    )

    for fragment in (
        "import strawberry",
        "from strawberry",
        "import graphene",
        "from graphene",
        "import ariadne",
        "from ariadne",
        "graphqlrouter",
        "/api/v1/graphql",
        "def resolve_practitioners",
    ):
        assert fragment not in app_text
    for package in ("strawberry-graphql", "graphene", "ariadne"):
        assert package not in dependency_text


def test_markdown_restates_gate_packet_boundary():
    text = " ".join(GATE_MD.read_text(encoding="utf-8").split())

    assert "does not add a GraphQL dependency" in text
    assert "Dependency installation is not authorized" in text
    assert "GraphQL resolver readiness remains false" in text
    assert "must be a thin facade" in text
    assert "max depth `6`" in text
    assert "cost budget `500`" in text
    assert "Ariadne" in text
    assert "Graphene" in text
