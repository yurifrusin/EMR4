from __future__ import annotations

import json
import uuid
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

import app.graphql.schema as graphql_schema
from app.graphql.application_auth_product import (
    create_application_session_practitioner_directory_router,
)
from app.schemas.practice import (
    PractitionerDefaultLocationOut,
    PractitionerOut,
)
from app.services.application_auth_product_read import (
    ProductReadAuthorizationFailed,
    SyntheticProductPrincipalBinding,
    SyntheticProductPrincipalRegistry,
)
from app.services.application_auth_product_read_database_role import (
    create_product_read_capability_statements,
    create_product_read_login_statements,
)
from app.services.application_auth_product_read_operational import (
    ProductReadPoolPolicy,
)
from app.services.application_auth_runtime import (
    PRACTITIONER_DIRECTORY_ACTION,
    PRACTITIONER_DIRECTORY_POLICY_VERSION,
    PRACTITIONER_DIRECTORY_RESOURCE_TYPE,
    AuthAuditEventType,
    AuthRuntimeDenied,
    RequiredAuditUnavailable,
    Surface,
)
from tests.test_raisa_shared_application_auth_runtime_foundation import (
    ORIGINS,
    create_word_session,
    principal,
    runtime_bundle,
)


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs/raisa-provider-free-session-practitioner-directory-read-bridge-plan.md"
DESIGN = ROOT / "docs/raisa-provider-free-session-practitioner-directory-read-bridge-design.md"
THREAT = ROOT / "docs/security/raisa-provider-free-session-practitioner-directory-read-bridge-threat-model-delta.md"
MIGRATION = ROOT / "alembic/versions/u0v1w2x3y4z5_extend_auth_audit_for_directory_read.py"
RECEIPT = ROOT / "orchestration/agent_inbox/codex/raisa-provider-free-session-practitioner-directory-read-bridge-rehydration-receipt.json"
FIVE_SOURCES = {
    "live_handover_current_baton",
    "current_authority_allocation",
    "active_plan_and_acceptance",
    "protected_evidence_boundaries",
    "git_refs_and_worktree",
}


def test_runtime_admits_exact_active_directory_policy_and_audits_before_release() -> None:
    runtime, _store, audit, _clock = runtime_bundle()
    created = create_word_session(runtime)

    context = runtime.authorize_practitioner_directory_read(
        surface_session_value=created.surface_session_value,
        surface=Surface.WORD_DESKTOP,
        origin=ORIGINS[Surface.WORD_DESKTOP],
        fresh_principal=principal(),
        fresh_user_active=True,
        resource_practice_id=principal().practice_id,
        active_only=True,
        correlation_id="correlation-directory-allowed",
    )

    assert context.user_id == principal().user_id
    event = audit.snapshot()[-1]
    assert event.event_type is AuthAuditEventType.AUTHORIZATION_ALLOWED
    assert event.action == PRACTITIONER_DIRECTORY_ACTION
    assert event.resource_type == PRACTITIONER_DIRECTORY_RESOURCE_TYPE
    assert event.policy_version == PRACTITIONER_DIRECTORY_POLICY_VERSION
    assert event.reason_codes == ("active_practitioner_directory_authorized",)


@pytest.mark.parametrize(
    ("overrides", "reason"),
    [
        ({"fresh_user_active": False}, "fresh_product_user_inactive"),
        ({"fresh_principal": None}, "fresh_product_user_inactive"),
        (
            {"resource_practice_id": "synthetic-practice-other"},
            "resource_practice_mismatch",
        ),
        ({"active_only": False}, "inactive_practitioner_directory_closed"),
    ],
)
def test_runtime_denies_stale_scope_and_inactive_enumeration_with_audit(
    overrides: dict[str, object],
    reason: str,
) -> None:
    runtime, _store, audit, _clock = runtime_bundle()
    created = create_word_session(runtime)
    arguments = {
        "surface_session_value": created.surface_session_value,
        "surface": Surface.WORD_DESKTOP,
        "origin": ORIGINS[Surface.WORD_DESKTOP],
        "fresh_principal": principal(),
        "fresh_user_active": True,
        "resource_practice_id": principal().practice_id,
        "active_only": True,
        "correlation_id": "correlation-directory-denied",
    }
    arguments.update(overrides)

    with pytest.raises(AuthRuntimeDenied) as caught:
        runtime.authorize_practitioner_directory_read(**arguments)

    assert caught.value.reason_code == reason
    event = audit.snapshot()[-1]
    assert event.event_type is AuthAuditEventType.AUTHORIZATION_DENIED
    assert event.policy_version == PRACTITIONER_DIRECTORY_POLICY_VERSION
    assert event.reason_codes == (reason,)


def test_required_audit_failure_releases_no_allow_decision() -> None:
    runtime, _store, audit, _clock = runtime_bundle()
    created = create_word_session(runtime)
    before = audit.snapshot()
    audit.fail = True

    with pytest.raises(RequiredAuditUnavailable):
        runtime.authorize_practitioner_directory_read(
            surface_session_value=created.surface_session_value,
            surface=Surface.WORD_DESKTOP,
            origin=ORIGINS[Surface.WORD_DESKTOP],
            fresh_principal=principal(),
            fresh_user_active=True,
            resource_practice_id=principal().practice_id,
            active_only=True,
        )

    assert audit.snapshot() == before


def test_synthetic_product_registry_is_closed_immutable_input() -> None:
    binding = SyntheticProductPrincipalBinding(
        user_ref="synthetic-user-directory-one",
        practice_ref="synthetic-practice-directory-one",
        user_id=uuid.uuid4(),
        practice_id=uuid.uuid4(),
    )
    registry = SyntheticProductPrincipalRegistry((binding,))

    assert registry.resolve(
        user_ref=binding.user_ref,
        practice_ref=binding.practice_ref,
    ) is binding
    assert registry.resolve(
        user_ref="synthetic-user-unknown",
        practice_ref=binding.practice_ref,
    ) is None
    with pytest.raises(ValueError, match="bounded synthetic"):
        SyntheticProductPrincipalBinding(
            user_ref="real-user",
            practice_ref=binding.practice_ref,
            user_id=uuid.uuid4(),
            practice_id=uuid.uuid4(),
        )


def test_product_read_role_is_finite_exact_column_and_non_inheriting() -> None:
    capability = "emr4_product_read_runtime_authored01"
    login = "emr4_product_read_login_authored01"
    statements = create_product_read_capability_statements(capability)
    sql = "\n".join(statements).lower()

    assert "nologin" in statements[0].lower()
    assert "noinherit" in statements[0].lower()
    assert "nobypassrls" in statements[0].lower()
    assert "select (id, practice_id, role, practitioner_id, is_active)" in sql
    assert "first_name, last_name, specialty, default_location_id" in sql
    assert "select (id, practice_id, name, is_active)" in sql
    assert all(
        prohibited not in sql
        for prohibited in (
            "provider_number",
            "prescriber_number",
            "ahpra_number",
            "hpi_i",
            "email",
            "phone",
            "insert on",
            "update on",
            "delete on",
        )
    )

    login_sql = create_product_read_login_statements(login, capability)
    assert "noinherit" in login_sql[0].lower()
    assert "connection limit 2" in login_sql[0].lower()
    assert ProductReadPoolPolicy().pool_size == 2


class _FakeDB:
    def __init__(self) -> None:
        self.closed = False

    def close(self) -> None:
        self.closed = True


class _FakeBridge:
    def __init__(self) -> None:
        self.db = _FakeDB()
        self.open_calls: list[dict[str, object]] = []
        self.policy_calls: list[bool] = []

    def open_context(self, **kwargs):
        self.open_calls.append(kwargs)
        return SimpleNamespace(
            db=self.db,
            current_user=SimpleNamespace(
                practice_id=uuid.UUID("11111111-1111-4111-8111-111111111111")
            ),
        )

    def require_active_directory(self, _context, *, active_only: bool) -> None:
        self.policy_calls.append(active_only)
        if not active_only:
            raise ProductReadAuthorizationFailed()


def _product_test_app(bridge: _FakeBridge) -> FastAPI:
    application = FastAPI()
    application.include_router(
        create_application_session_practitioner_directory_router(
            bridge=bridge,  # type: ignore[arg-type]
            surface=Surface.WORD_ONLINE,
        )
    )
    return application


def test_explicit_graphql_factory_reuses_exact_projection_and_closes_context(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    practitioner_id = uuid.UUID("22222222-2222-4222-8222-222222222222")
    location_id = uuid.UUID("33333333-3333-4333-8333-333333333333")
    monkeypatch.setattr(
        graphql_schema,
        "list_practitioner_directory",
        lambda **_kwargs: [
            PractitionerOut(
                id=practitioner_id,
                displayName="Synthetic Directory",
                roleLabel="GP",
                active=True,
                defaultLocation=PractitionerDefaultLocationOut(
                    id=location_id,
                    name="Synthetic Clinic",
                ),
            )
        ],
    )
    bridge = _FakeBridge()
    with TestClient(_product_test_app(bridge)) as client:
        response = client.post(
            "/api/v1/application-auth/product/graphql",
            json={
                "query": "{ practice { practitioners { id displayName roleLabel active defaultLocation { id name } } } }"
            },
            headers={
                "Origin": ORIGINS[Surface.WORD_ONLINE],
                "X-EMR4-CSRF": "csrf." + "c" * 43,
            },
            cookies={
                "__Host-emr4-application-session": "ass." + "s" * 48,
                "__Host-emr4-application-csrf": "csrf." + "c" * 43,
            },
        )

    assert response.status_code == 200, response.text
    assert response.headers["cache-control"] == "no-store"
    assert response.json()["data"]["practice"]["practitioners"] == [
        {
            "id": str(practitioner_id),
            "displayName": "Synthetic Directory",
            "roleLabel": "GP",
            "active": True,
            "defaultLocation": {
                "id": str(location_id),
                "name": "Synthetic Clinic",
            },
        }
    ]
    assert bridge.policy_calls == [True]
    assert bridge.db.closed is True


def test_application_session_bridge_denies_inactive_enumeration_before_read(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    reads = 0

    def forbidden_read(**_kwargs):
        nonlocal reads
        reads += 1
        return []

    monkeypatch.setattr(
        graphql_schema,
        "list_practitioner_directory",
        forbidden_read,
    )
    bridge = _FakeBridge()
    with TestClient(_product_test_app(bridge)) as client:
        response = client.post(
            "/api/v1/application-auth/product/graphql",
            json={
                "query": "{ practice { practitioners(activeOnly: false) { id } } }"
            },
        )

    assert response.status_code == 200
    assert response.json()["errors"][0]["extensions"]["code"] == "FORBIDDEN"
    assert reads == 0
    assert bridge.policy_calls == [False]


@pytest.mark.parametrize(
    "query",
    [
        "{ graphqlHealth { status } }",
        "{ practice { id } }",
        "{ p: practice { practitioners { id } } }",
        "{ practice { practitioners { alias: id } } }",
        "query Q { practice { ...Directory } } fragment Directory on Practice { practitioners { id } }",
        "mutation { practice { practitioners { id } } }",
    ],
)
def test_product_router_rejects_every_non_exact_graphql_surface_before_auth(
    query: str,
) -> None:
    bridge = _FakeBridge()
    with TestClient(_product_test_app(bridge)) as client:
        response = client.post(
            "/api/v1/application-auth/product/graphql",
            json={"query": query},
        )

    assert response.status_code == 403
    assert bridge.open_calls == []


def test_product_router_disables_graphql_queries_via_get() -> None:
    bridge = _FakeBridge()
    with TestClient(_product_test_app(bridge)) as client:
        response = client.get(
            "/api/v1/application-auth/product/graphql",
            params={
                "query": "{ practice { practitioners { id } } }",
            },
        )

    assert response.status_code == 403
    assert bridge.open_calls == []


def test_migration_graphql_boundary_and_five_source_receipt_are_exact() -> None:
    migration = MIGRATION.read_text(encoding="utf-8")
    assert 'revision: str = "u0v1w2x3y4z5"' in migration
    assert 'down_revision: Union[str, Sequence[str], None] = "t9u0v1w2x3y4"' in migration
    assert "auth.authorization_allowed" in migration
    assert PRACTITIONER_DIRECTORY_POLICY_VERSION in migration
    assert "def downgrade()" in migration

    main_source = (ROOT / "app/main.py").read_text(encoding="utf-8")
    adapter_source = (
        ROOT / "app/graphql/application_auth_product.py"
    ).read_text(encoding="utf-8")
    assert "application_auth_product" not in main_source
    assert "GraphQLRouter" in adapter_source
    assert "Mutation" not in adapter_source
    assert "allow_queries_via_get=False" in adapter_source
    assert "_require_exact_directory_operation" in adapter_source

    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    assert receipt["status"] == "passed"
    assert set(receipt["rehydration_sources"]) == FIVE_SOURCES
    assert all(path.is_file() for path in (PLAN, DESIGN, THREAT))
