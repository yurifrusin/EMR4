from pathlib import Path

from fastapi.routing import APIRoute

from app.graphql.schema import schema
from app.main import app
from tests.conftest import make_token


ROOT = Path(__file__).resolve().parents[1]
GRAPHQL_APP = ROOT / "app" / "graphql"
SHELL_JSON = ROOT / "docs" / "api-spine" / "practitioner-directory-graphql-runtime-shell.json"


def _graphql_sources() -> str:
    return "\n".join(
        path.read_text(encoding="utf-8", errors="replace")
        for path in sorted(GRAPHQL_APP.rglob("*.py"))
    )


def test_graphql_endpoint_is_mounted_only_at_api_v1_graphql():
    graphql_routes = [
        route
        for route in app.routes
        if isinstance(route, APIRoute) and "graphql" in route.path.lower()
    ]

    assert graphql_routes
    assert {route.path for route in graphql_routes} == {"/api/v1/graphql"}
    assert {method for route in graphql_routes for method in route.methods} == {"GET", "POST"}


def test_graphql_schema_shell_has_query_and_no_mutation_or_practitioners():
    sdl = schema.as_str()

    assert "type Query" in sdl
    assert "graphqlHealth" in sdl
    assert "type Mutation" not in sdl
    assert "type Subscription" not in sdl
    assert "practice" not in sdl
    assert "practitioners" not in sdl


def test_graphql_schema_shell_does_not_expose_sensitive_field_names():
    sdl = schema.as_str().lower()

    for fragment in (
        "ahpra",
        "provider_number",
        "prescriber_number",
        "hpi",
        "practice_id",
        "password",
        "email",
        "phone",
        "address",
    ):
        assert fragment not in sdl


def test_graphql_shell_requires_existing_bearer_auth(client):
    response = client.post(
        "/api/v1/graphql",
        json={"query": "{ graphqlHealth { status service authenticated } }"},
    )

    assert response.status_code == 401


def test_graphql_shell_authenticated_health_uses_context(client, gp_user):
    response = client.post(
        "/api/v1/graphql",
        json={"query": "{ graphqlHealth { status service authenticated } }"},
        headers={"Authorization": f"Bearer {make_token(gp_user)}"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "data": {
            "graphqlHealth": {
                "status": "ok",
                "service": "emr4-graphql",
                "authenticated": True,
            }
        }
    }


def test_graphql_shell_invalid_token_fails_before_execution(client):
    response = client.post(
        "/api/v1/graphql",
        json={"query": "{ graphqlHealth { status } }"},
        headers={"Authorization": "Bearer not.a.valid.token"},
    )

    assert response.status_code == 401


def test_graphql_shell_depth_alias_and_token_guards_are_configured():
    source = _graphql_sources()

    assert "QueryDepthLimiter(max_depth=6)" in source
    assert "MaxAliasesLimiter(max_alias_count=500)" in source
    assert "MaxTokensLimiter(max_token_count=500)" in source


def test_graphql_shell_no_provider_memory_trove_rest_router_or_write_imports():
    source = _graphql_sources().lower()

    for fragment in (
        "app.routers.practice",
        "list_practitioner_directory",
        "provider",
        "access_ai",
        "practice_knowledge",
        "memory",
        "rag",
        "graphrag",
        "h15",
        "h_series",
        "historical_diary",
        "local_data",
        ".add(",
        ".commit(",
        "audit",
    ):
        assert fragment not in source


def test_graphql_shell_evidence_keeps_resolver_and_adjacent_gates_closed():
    import json

    payload = json.loads(SHELL_JSON.read_text(encoding="utf-8"))

    assert payload["schema_version"] == "api_spine.practitioner_directory_graphql_runtime_shell.v1"
    assert payload["sprint"] == 269
    assert payload["decision"] == "approved_minimal_runtime_shell_only"
    assert payload["endpoint_path"] == "/api/v1/graphql"
    assert payload["runtime_shell"] == {
        "dependency_pin": True,
        "endpoint_mounted": True,
        "authenticated_context": True,
        "query_only_schema": True,
        "placeholder_health_field_only": True,
        "practice_practitioners_resolver": False,
    }
    assert all(value is False for value in payload["must_remain_false"].values())
