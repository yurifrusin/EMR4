import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BOUNDARY = ROOT / "docs" / "api-spine" / "practitioner-directory-graphql-release-boundary.json"
BOUNDARY_MD = ROOT / "docs" / "api-spine" / "practitioner-directory-graphql-release-boundary.md"
SNAPSHOT = ROOT / "tests" / "fixtures" / "api_spine_external_readiness" / "blocked_readiness_status.json"
DAG = ROOT / "docs" / "api-spine" / "external-read-model-readiness-dag.json"
APP_GRAPHQL = ROOT / "app" / "graphql"


def _payload() -> dict:
    return json.loads(BOUNDARY.read_text(encoding="utf-8"))


def test_release_boundary_shape_and_decision_are_scoped():
    payload = _payload()

    assert payload["schema_version"] == "api_spine.practitioner_directory_graphql_release_boundary.v1"
    assert payload["sprint"] == 272
    assert payload["decision"] == "proposed_internal_staff_consumer_development_ready_pending_yuri_approval"
    assert payload["reviewer"] == "ariadne"
    assert payload["target_field"] == "Query.practice.practitioners"
    assert payload["endpoint"] == "/api/v1/graphql"
    assert payload["consumer_scope"] == ["authenticated_staff_only", "practice_scoped"]
    assert payload["consumption_mode"] == "graphql_through_existing_endpoint"
    assert payload["allowed_field_set"] == [
        "id",
        "displayName",
        "roleLabel",
        "active",
        "defaultLocation { id, name }",
    ]
    assert payload["allowed_use"]["internal_authenticated_staff_consumer_development"] is False
    assert payload["allowed_use"]["test_harness_use"] is True
    assert payload["allowed_use"]["rest_parity_comparison"] is True
    for key in (
        "external_patient_client_use",
        "production_readiness_claim",
        "deployment_readiness_claim",
        "global_graphql_readiness_claim",
    ):
        assert payload["allowed_use"][key] is False


def test_release_boundary_runtime_scope_names_only_current_fields():
    scope = _payload()["runtime_scope"]

    assert scope["endpoint"] == "/api/v1/graphql"
    assert scope["query_fields_allowed"] == ["graphqlHealth", "practice"]
    assert scope["practice_fields_allowed"] == ["id", "practitioners"]
    assert scope["practitioner_fields_allowed"] == [
        "id",
        "displayName",
        "roleLabel",
        "active",
        "defaultLocation.id",
        "defaultLocation.name",
    ]
    assert scope["mutations_allowed"] is False
    assert scope["subscriptions_allowed"] is False
    assert scope["other_read_roots_allowed"] is False


def test_release_boundary_keeps_all_adjacent_gates_false():
    payload = _payload()
    blockers = payload["release_blockers_remaining"]

    assert all(value is False for value in payload["must_remain_false"].values())
    assert payload["authorized_now"] == {
        "internal_consumer_development": False,
        "readiness_flag_changes": False,
        "deployment_or_production_exposure": False,
        "external_client_access": False,
        "schema_field_expansion": False,
        "write_mutation_or_subscription": False,
        "provider_memory_rag_graphrag_h15_trove": False,
    }
    assert payload["worker_review"]["verdict"] == "PASS"
    assert payload["worker_review"]["approval_required_before_ready"] is True
    assert blockers["global_readiness_snapshot_migration"] == "blocked"
    assert blockers["external_client_contract"] == "blocked"
    assert blockers["mutations"] == "blocked"
    assert blockers["subscriptions"] == "blocked"
    assert blockers["provider_memory_h15_trove"] == "blocked"
    assert blockers["write_authority"] == "blocked"
    assert blockers["rate_limit_review"] == "deferred"
    assert blockers["production_introspection_posture_review"] == "deferred"
    assert blockers["deployment_smoke"] == "deferred"


def test_release_boundary_does_not_change_global_readiness_snapshots():
    snapshot = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    dag = json.loads(DAG.read_text(encoding="utf-8"))

    assert dag["decision"] == "blocked"
    assert all(value is False for value in dag["readiness"].values())
    assert snapshot["dag_decision"] == "blocked"
    for key in (
        "graphql_resolver_ready",
        "external_read_model_runtime_ready",
        "rest_route_ready",
        "runtime_or_memory_ready",
        "write_authority_ready",
        "provider_or_directory_runtime_ready",
    ):
        assert snapshot[key] is False


def test_release_boundary_consumer_constraints_are_explicit():
    constraints = _payload()["required_consumer_constraints"]

    assert constraints == {
        "must_send_existing_bearer_token": True,
        "must_handle_http_401_auth_failures": True,
        "must_handle_graphql_bad_user_input": True,
        "must_handle_graphql_forbidden": True,
        "must_handle_practice_null_on_id_mismatch": True,
        "must_not_request_sensitive_fields": True,
        "must_not_treat_field_as_external_api": True,
        "must_not_require_idempotency_key": True,
    }


def test_release_boundary_requires_yuri_approval_slip():
    approval = _payload()["yuri_approval_slip"]

    assert approval == {
        "required": True,
        "approved_contract_commit": "",
        "go_no_go_acknowledged": False,
        "approval_expires_on": "",
        "sunset_review_required": True,
    }


def test_release_boundary_is_docs_only_no_runtime_change():
    source = "\n".join(
        path.read_text(encoding="utf-8", errors="replace").lower()
        for path in sorted(APP_GRAPHQL.rglob("*.py"))
    )

    assert "mutation" not in source
    assert "subscription" not in source
    assert "app.routers.practice" not in source
    assert "db.query(" not in source
    assert ".commit(" not in source
    assert "provider" not in source
    assert "memory" not in source
    assert "h15" not in source
    assert "historical_diary" not in source


def test_release_boundary_markdown_names_uses_and_blockers():
    text = " ".join(BOUNDARY_MD.read_text(encoding="utf-8").split())

    assert "internal authenticated staff consumer development" in text
    assert "pending Yuri approval" in text
    assert "not global GraphQL readiness" in text
    assert "not deployment readiness" in text
    assert "not external patient-client readiness" in text
    assert "Handle GraphQL `BAD_USER_INPUT`" in text
    assert "Handle GraphQL `FORBIDDEN`" in text
    assert "practice(id:) = null" in text
    assert "mutations" in text
    assert "subscriptions" in text
    assert "Reverse-chaining" in text
    assert "expiry date" in text
