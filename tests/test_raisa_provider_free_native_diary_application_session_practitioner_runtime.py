"""Deterministic acceptance for the default-off native-Diary application-session
practitioner runtime adapter (Diary lane runtime step, provider-free).

These tests are provider-free and do not require PostgreSQL.  The live
loopback HTTP/PostgreSQL evidence is owned by the root-serialised acceptance
script ``scripts/raisa_provider_free_native_diary_application_session_practitioner_runtime_acceptance.py``.
"""

from __future__ import annotations

import re
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest
from fastapi import APIRouter, FastAPI
from fastapi.testclient import TestClient
from graphql import parse

import app.graphql.native_diary_application_session_practitioner as adapter
from app.graphql.native_diary_application_session_practitioner import (
    FIXED_QUERY,
    FIXED_VARIABLES,
    PRODUCT_PATH,
    create_native_diary_application_session_app,
)
from app.models.tenancy import Practitioner
from app.schemas.practice import (
    PractitionerDefaultLocationOut,
    PractitionerOut,
)
from app.services.application_auth_runtime import Surface
from scripts.raisa_provider_free_native_diary_application_session_practitioner_runtime_acceptance import (
    PRACTITIONER_SEED_MARKERS,
)


ROOT = Path(__file__).resolve().parents[1]
PLAN = (
    ROOT
    / "docs/raisa-provider-free-native-diary-application-session-practitioner-runtime-plan.md"
)
THREAT = (
    ROOT
    / "docs/security/raisa-provider-free-native-diary-application-session-practitioner-runtime-threat-model-delta.md"
)


class _FakeDB:
    def __init__(self) -> None:
        self.closed = False

    def close(self) -> None:
        self.closed = True


class _FakeBridge:
    def __init__(self) -> None:
        self.db = _FakeDB()
        self.open_calls: list[dict[str, Any]] = []
        self.policy_calls: list[bool] = []

    def open_context(self, **kwargs: Any) -> SimpleNamespace:
        self.open_calls.append(kwargs)
        return SimpleNamespace(
            db=self.db,
            current_user=SimpleNamespace(practice_id="11111111-1111-4111-8111-111111111111"),
        )

    def require_active_directory(
        self,
        _context: Any,
        *,
        active_only: bool,
    ) -> None:
        self.policy_calls.append(active_only)


def _enabled_pair() -> tuple[FastAPI, _FakeBridge]:
    bridge = _FakeBridge()
    return (
        create_native_diary_application_session_app(enabled=True, bridge=bridge),
        bridge,
    )


def test_practitioner_seed_markers_stay_within_model_limits() -> None:
    bounded_columns = {
        "provider_number",
        "prescriber_number",
        "ahpra_number",
        "hpi_i",
    }
    assert set(PRACTITIONER_SEED_MARKERS) == bounded_columns
    for column_name, marker in PRACTITIONER_SEED_MARKERS.items():
        column = Practitioner.__table__.c[column_name]
        limit = column.type.length
        assert isinstance(limit, int) and limit > 0
        assert marker.startswith("SYNTH-ND-")
        assert len(marker) <= limit, (
            f"{column_name} seed marker {marker!r} length {len(marker)} "
            f"exceeds the model String({limit}) column limit"
        )


def test_fixed_request_constants_are_exact() -> None:
    assert FIXED_VARIABLES == {"activeOnly": True, "limit": 200, "offset": 0}

    document = parse(FIXED_QUERY)
    assert len(document.definitions) == 1
    operation = document.definitions[0]
    assert operation.operation.value == "query"
    assert operation.name is not None and operation.name.value == "NativeDiaryPractitioners"
    assert not operation.directives
    assert "practiceId" not in FIXED_QUERY
    assert "practiceId" not in FIXED_VARIABLES

    for marker in (
        "practitioners(activeOnly: $activeOnly, limit: $limit, offset: $offset)",
        "id",
        "displayName",
        "roleLabel",
        "active",
        "defaultLocation",
        "name",
    ):
        assert marker in FIXED_QUERY


def test_disabled_app_has_no_product_route_docs_or_openapi() -> None:
    disabled = create_native_diary_application_session_app(enabled=False)
    with TestClient(disabled) as client:
        assert client.post(PRODUCT_PATH, json={"query": FIXED_QUERY}).status_code == 404
        assert client.get("/docs").status_code == 404
        assert client.get("/redoc").status_code == 404
        assert client.get("/openapi.json").status_code == 404


def test_disabled_app_opens_no_db_or_session() -> None:
    bridge = _FakeBridge()
    disabled = create_native_diary_application_session_app(enabled=False, bridge=bridge)
    with TestClient(disabled) as client:
        assert client.post(PRODUCT_PATH, json={"query": FIXED_QUERY}).status_code == 404
    assert bridge.open_calls == []


def test_factory_requires_literal_true_enablement() -> None:
    for value in (False, 0, 1, None, "yes"):
        app = create_native_diary_application_session_app(enabled=value)
        assert not any(route.path == PRODUCT_PATH for route in app.routes)
        assert app.openapi_url is None
        assert app.docs_url is None


def test_enabled_app_requires_bridge() -> None:
    with pytest.raises(ValueError):
        create_native_diary_application_session_app(enabled=True, bridge=None)


def test_enabled_factory_binds_exact_native_diary_surface(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, Any] = {}

    def fake_router(*, bridge: Any, surface: Surface) -> APIRouter:
        captured["bridge"] = bridge
        captured["surface"] = surface
        router = APIRouter()

        @router.post(PRODUCT_PATH)
        def _product_route() -> dict[str, str]:
            return {"ok": "route-present"}

        return router

    monkeypatch.setattr(
        adapter,
        "create_application_session_practitioner_directory_router",
        fake_router,
    )
    bridge = _FakeBridge()
    app = create_native_diary_application_session_app(enabled=True, bridge=bridge)
    assert captured["surface"] is Surface.NATIVE_DIARY
    assert captured["bridge"] is bridge
    assert any(route.path == PRODUCT_PATH for route in app.routes)


def test_enabled_app_has_no_docs_or_openapi() -> None:
    app, _bridge = _enabled_pair()
    assert app.openapi_url is None
    assert app.docs_url is None
    assert app.redoc_url is None


def test_pre_auth_guard_rejects_non_post() -> None:
    app, bridge = _enabled_pair()
    with TestClient(app) as client:
        response = client.get(PRODUCT_PATH)
    assert response.status_code == 403
    assert response.headers["cache-control"] == "no-store"
    assert bridge.open_calls == []


def test_pre_auth_guard_rejects_wrong_content_type() -> None:
    app, bridge = _enabled_pair()
    with TestClient(app) as client:
        response = client.post(
            PRODUCT_PATH,
            content='{"query":"x"}',
            headers={"content-type": "text/plain"},
        )
    assert response.status_code == 403
    assert response.headers["cache-control"] == "no-store"
    assert bridge.open_calls == []


def test_pre_auth_guard_rejects_malformed_json() -> None:
    app, bridge = _enabled_pair()
    with TestClient(app) as client:
        response = client.post(
            PRODUCT_PATH,
            content="{not json",
            headers={"content-type": "application/json"},
        )
    assert response.status_code == 403
    assert bridge.open_calls == []


def test_pre_auth_guard_rejects_extra_json_key() -> None:
    app, bridge = _enabled_pair()
    with TestClient(app) as client:
        response = client.post(
            PRODUCT_PATH,
            json={"query": FIXED_QUERY, "variables": FIXED_VARIABLES, "operationName": "X"},
        )
    assert response.status_code == 403
    assert response.headers["cache-control"] == "no-store"
    assert bridge.open_calls == []


def test_pre_auth_guard_rejects_practice_id() -> None:
    app, bridge = _enabled_pair()
    with TestClient(app) as client:
        response = client.post(
            PRODUCT_PATH,
            json={
                "query": FIXED_QUERY,
                "variables": {**FIXED_VARIABLES, "practiceId": "synthetic-practice-other"},
            },
        )
    assert response.status_code == 403
    assert bridge.open_calls == []


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("activeOnly", False),
        ("limit", 201),
        ("limit", 1),
        ("offset", 1),
        ("offset", -1),
    ],
)
def test_pre_auth_guard_rejects_pagination_drift(field: str, value: Any) -> None:
    app, bridge = _enabled_pair()
    with TestClient(app) as client:
        response = client.post(
            PRODUCT_PATH,
            json={
                "query": FIXED_QUERY,
                "variables": {**FIXED_VARIABLES, field: value},
            },
        )
    assert response.status_code == 403
    assert bridge.open_calls == []


@pytest.mark.parametrize(
    "query",
    [
        "mutation { practice { practitioners { id } } }",
        "{ __schema { types { name } } }",
        "query Q { practice { practitioners { id } } }",
        "query Q { practice { ...D } } fragment D on Practice { practitioners { id } }",
        "query NativeDiaryPractitioners($activeOnly: Boolean!, $limit: Int!, $offset: Int!) { practice { practitioners(activeOnly: $activeOnly, limit: $limit, offset: $offset) { id } } }",
        "query NativeDiaryPractitioners($activeOnly: Boolean!, $limit: Int!, $offset: Int!) { practice { practitioners(activeOnly: $activeOnly, limit: $limit, offset: $offset) { id displayName roleLabel active phone defaultLocation { id name } } } }",
        "query NativeDiaryPractitioners($activeOnly: Boolean!, $limit: Int!, $offset: Int!) @skip(if: false) { practice { practitioners(activeOnly: $activeOnly, limit: $limit, offset: $offset) { id displayName roleLabel active defaultLocation { id name } } } }",
    ],
)
def test_pre_auth_guard_rejects_query_drift(query: str) -> None:
    app, bridge = _enabled_pair()
    with TestClient(app) as client:
        response = client.post(
            PRODUCT_PATH,
            json={"query": query, "variables": FIXED_VARIABLES},
        )
    assert response.status_code == 403
    assert response.headers["cache-control"] == "no-store"
    assert bridge.open_calls == []


def test_pre_auth_guard_rejects_alias() -> None:
    aliased = FIXED_QUERY.replace("      id\n", "      alias: id\n")
    app, bridge = _enabled_pair()
    with TestClient(app) as client:
        response = client.post(
            PRODUCT_PATH,
            json={"query": aliased, "variables": FIXED_VARIABLES},
        )
    assert response.status_code == 403
    assert bridge.open_calls == []


def test_pre_auth_guard_rejects_oversized_body() -> None:
    app, bridge = _enabled_pair()
    oversized = '{"query":"' + "x" * 9000 + '"}'
    with TestClient(app) as client:
        response = client.post(
            PRODUCT_PATH,
            content=oversized,
            headers={"content-type": "application/json"},
        )
    assert response.status_code == 403
    assert response.headers["cache-control"] == "no-store"
    assert bridge.open_calls == []


def test_pre_auth_guard_lets_exact_request_through_to_bridge(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import app.graphql.schema as graphql_schema

    monkeypatch.setattr(
        graphql_schema,
        "list_practitioner_directory",
        lambda **_kwargs: [
            PractitionerOut(
                id="22222222-2222-4222-8222-222222222222",
                displayName="Synthetic Diary",
                roleLabel="GP",
                active=True,
                defaultLocation=PractitionerDefaultLocationOut(
                    id="33333333-3333-4333-8333-333333333333",
                    name="Synthetic Clinic",
                ),
            )
        ],
    )
    app, bridge = _enabled_pair()
    with TestClient(app) as client:
        response = client.post(
            PRODUCT_PATH,
            json={"query": FIXED_QUERY, "variables": FIXED_VARIABLES},
        )

    assert response.status_code == 200, response.text
    assert response.headers["cache-control"] == "no-store"
    assert len(bridge.open_calls) == 1
    assert bridge.open_calls[0]["surface"] is Surface.NATIVE_DIARY
    assert bridge.policy_calls == [True]
    assert bridge.db.closed is True
    rows = response.json()["data"]["practice"]["practitioners"]
    assert set(rows[0]) == {"id", "displayName", "roleLabel", "active", "defaultLocation"}
    assert set(rows[0]["defaultLocation"]) == {"id", "name"}


def test_adapter_imports_no_forbidden_dependency_surfaces() -> None:
    source = (ROOT / "app/graphql/native_diary_application_session_practitioner.py").read_text(
        encoding="utf-8"
    )

    assert "office_consumer" not in source
    assert "bernie" not in source.lower()
    assert "davida" not in source.lower()
    assert "proofreader" not in source.lower()
    assert "bearer" not in source
    assert "localstorage" not in source.lower()
    assert "rest_fallback" not in source.lower()
    assert "app.main" not in source
    assert re.search(r"create_application_session_practitioner_directory_router", source) is not None


def test_public_artifacts_state_runtime_limits() -> None:
    assert PLAN.is_file() and THREAT.is_file()
    combined = "\n".join(
        path.read_text(encoding="utf-8").lower() for path in (PLAN, THREAT)
    )

    assert "default-off" in combined
    assert "native diary" in combined
    assert "docs/branding/" in combined
    assert "live_local_backend_postgres" in combined
    assert "in-flight" in combined
    assert "does not prove rejection of an already-returned" in combined
    assert "no provider" in combined
    assert "no browser" in combined
    assert "no real identity" in combined
