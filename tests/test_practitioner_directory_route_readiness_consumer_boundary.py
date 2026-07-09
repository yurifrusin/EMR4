import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BOUNDARY = (
    ROOT
    / "docs"
    / "api-spine"
    / "practitioner-directory-route-readiness-consumer-boundary.json"
)
BOUNDARY_MD = (
    ROOT
    / "docs"
    / "api-spine"
    / "practitioner-directory-route-readiness-consumer-boundary.md"
)
RELEASE_GATES = ROOT / "orchestration" / "bernie_release_gates.md"
STATUS_FIXTURE = (
    "tests/fixtures/api_spine_external_readiness/"
    "practitioner_directory_route_readiness_status.json"
)


def _boundary() -> dict:
    return json.loads(BOUNDARY.read_text(encoding="utf-8"))


def test_route_readiness_consumer_boundary_allows_only_static_surfaces():
    payload = _boundary()

    assert payload["schema_version"] == (
        "api_spine.practitioner_directory_route_readiness_consumer_boundary.v1"
    )
    assert payload["decision"] == (
        "route_scoped_readiness_status_may_feed_static_release_checks_only"
    )
    assert payload["source_status"] == STATUS_FIXTURE
    assert payload["target_route"] == "GET /api/v1/practice/practitioners"
    assert all(
        any(token in consumer for token in ("docs", "orchestration", "CI", "release"))
        for consumer in payload["allowed_consumers"]
    )


def test_route_readiness_consumer_boundary_forbids_runtime_surfaces():
    payload = _boundary()
    forbidden = " ".join(payload["forbidden_consumers"]).lower()

    for fragment in (
        "production app routers",
        "provider",
        "office add-in runtime ui",
        "deployment",
        "external patient-client",
        "global external-readiness dag",
        "write authority",
    ):
        assert fragment in forbidden
    assert all(value is False for value in payload["must_remain_false"].values())


def test_runtime_app_code_does_not_consume_route_readiness_status():
    forbidden_fragments = {
        "practitioner_directory_route_readiness_status",
        "practitioner_directory_route_readiness_status.json",
    }
    app_sources = [
        path
        for path in (ROOT / "app").rglob("*.py")
        if "__pycache__" not in path.parts
    ]

    assert app_sources
    for path in app_sources:
        text = path.read_text(encoding="utf-8")
        for fragment in forbidden_fragments:
            assert fragment not in text, f"{fragment} leaked into {path}"


def test_consumer_boundary_markdown_restates_no_runtime_rule():
    text = " ".join(BOUNDARY_MD.read_text(encoding="utf-8").split())

    assert "static review and release-check surfaces only" in text
    assert "must not become runtime behavior" in text
    assert "Runtime app code under `app/` must not import" in text
    assert "broader external-readiness, GraphQL, provider, memory, write" in text


def test_release_gates_require_route_readiness_preflight_before_runtime_use():
    text = " ".join(RELEASE_GATES.read_text(encoding="utf-8").split())

    assert "Practitioner Directory Route Readiness Gate" in text
    assert (
        ".venv\\Scripts\\python.exe scripts\\practitioner_directory_route_readiness_status.py"
        in text
    )
    for expected in (
        "rest_route_ready=true",
        "global_readiness_snapshot_updated=false",
        "adjacent_gate_false_count=8",
        "deployment_ready=false",
        "production_ready=false",
        "external_patient_client_ready=false",
        "pause_required=false",
        "sprint_engine_state=continuing",
    ):
        assert expected in text
    assert "pause for explicit review" in text
