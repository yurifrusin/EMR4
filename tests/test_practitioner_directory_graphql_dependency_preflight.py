import importlib.metadata
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PREFLIGHT = ROOT / "docs" / "api-spine" / "practitioner-directory-graphql-dependency-preflight.json"
PREFLIGHT_MD = ROOT / "docs" / "api-spine" / "practitioner-directory-graphql-dependency-preflight.md"
REQUIREMENTS = ROOT / "requirements.txt"
APP = ROOT / "app"


def _payload() -> dict:
    return json.loads(PREFLIGHT.read_text(encoding="utf-8"))


def _app_text() -> str:
    return "\n".join(
        path.read_text(encoding="utf-8", errors="replace")
        for path in sorted(APP.rglob("*.py"))
    )


def test_dependency_preflight_shape_is_specific():
    payload = _payload()

    assert payload["schema_version"] == "api_spine.practitioner_directory_graphql_dependency_preflight.v1"
    assert payload["sprint"] == 268
    assert payload["decision"] == "approved_dependency_pin_only"
    assert payload["target_field"] == "Query.practice.practitioners"
    assert payload["approval_source"].endswith("practitioner-directory-graphql-runtime-gate.json")


def test_strawberry_dependency_is_pinned_and_importable():
    requirements = REQUIREMENTS.read_text(encoding="utf-8")
    payload = _payload()

    assert "strawberry-graphql[fastapi]==0.320.3" in requirements
    assert payload["dependency"]["package"] == "strawberry-graphql[fastapi]"
    assert payload["dependency"]["pinned_version"] == "0.320.3"
    assert importlib.metadata.version("strawberry-graphql") == "0.320.3"
    assert importlib.metadata.version("graphql-core") == payload["observed_local_install"]["graphql_core"]
    assert importlib.metadata.version("cross-web") == payload["observed_local_install"]["cross_web"]
    from strawberry.fastapi import GraphQLRouter
    from strawberry.extensions import DisableIntrospection, MaxAliasesLimiter, QueryDepthLimiter

    assert GraphQLRouter.__name__ == "GraphQLRouter"
    assert QueryDepthLimiter.__name__ == "QueryDepthLimiter"
    assert MaxAliasesLimiter.__name__ == "MaxAliasesLimiter"
    assert DisableIntrospection.__name__ == "DisableIntrospection"
    assert payload["observed_local_install"]["query_depth_limiter_available"] is True
    assert payload["observed_local_install"]["max_aliases_limiter_available"] is True
    assert payload["observed_local_install"]["disable_introspection_available"] is True


def test_dependency_preflight_does_not_add_endpoint_or_resolver_code():
    payload = _payload()
    app_text = _app_text().lower()

    assert payload["authorized_now"] == {
        "dependency_pin": True,
        "dependency_install_in_dev_environment": True,
        "graphql_endpoint": False,
        "schema_runtime_code": False,
        "resolver_code": False,
        "readiness_flag_changes": False,
    }
    for fragment in (
        "/api/v1/graphql",
        "graphqlrouter(",
        "def resolve_practitioners",
        "practice.practitioners",
    ):
        assert fragment not in app_text


def test_dependency_preflight_keeps_adjacent_gates_false():
    payload = _payload()

    assert all(value is False for value in payload["must_remain_false"].values())
    assert payload["worker_review"]["verdict"] == "PASS"
    assert payload["worker_review"]["new_vulnerabilities_introduced_by_dependency"] is False
    assert payload["next_allowed_step"] == (
        "sprint_269_minimal_graphql_runtime_shell_without_practitioner_resolver"
    )


def test_markdown_records_dependency_only_boundary():
    text = " ".join(PREFLIGHT_MD.read_text(encoding="utf-8").split())

    assert "does not mount `/api/v1/graphql`" in text
    assert "add resolver code" in text
    assert "Next allowed step: Sprint 269" in text
