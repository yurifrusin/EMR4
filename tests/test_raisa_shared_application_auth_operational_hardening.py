"""Focused provider-free tests for shared-auth operational hardening."""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.routers.application_auth import (
    AUTHENTICATION_UNAVAILABLE,
    REQUEST_NOT_ADMITTED,
    REQUEST_RATE_LIMITED,
    get_application_auth_operational_hardening,
    get_application_auth_transport,
    router,
)
from app.services.application_auth_database_role import (
    create_deployment_login_role_statements,
    require_login_role_identifier,
)
from app.services.application_auth_operational_database import (
    ApplicationAuthPoolPolicy,
    create_application_auth_engine,
)
from app.services.application_auth_operational_hardening import (
    ApplicationAuthOperationalHardening,
    BoundedFixedWindowRateLimiter,
    ProxyTrustPolicy,
    RequiredTransportDenialAuditUnavailable,
    TransportDenialEvent,
)
from app.services.application_auth_runtime import Surface
from app.services.application_auth_transport import (
    CSRF_COOKIE_NAME,
    TransportRequestDenied,
)


NOW = datetime(2026, 8, 1, 4, 5, 6, tzinfo=timezone.utc)
ORIGIN = "https://word-online.synthetic.invalid"
TEST_CLIENT = ("198.51.100.24", 50000)
ROOT = Path(__file__).resolve().parents[1]
RUNNER_PATH = (
    ROOT
    / "scripts"
    / "raisa_shared_application_auth_operational_hardening_acceptance.py"
)
EVIDENCE_PATH = (
    ROOT
    / "orchestration"
    / "continuity"
    / "raisa-shared-application-auth-operational-hardening"
    / "live-local-backend-postgres-operational-evidence.json"
)
PREACCEPTANCE_RECEIPT_PATH = (
    ROOT
    / "orchestration"
    / "agent_inbox"
    / "codex"
    / "raisa-shared-application-auth-operational-hardening-preacceptance-receipt.json"
)
POSTCOMPACTION_RECEIPT_PATH = (
    ROOT
    / "orchestration"
    / "agent_inbox"
    / "codex"
    / "raisa-shared-application-auth-operational-hardening-postcompaction-receipt.json"
)
CLOSEOUT_PATH = (
    ROOT / "docs" / "raisa-shared-application-auth-operational-hardening-closeout.md"
)
SOL_ACCEPTANCE_PATH = (
    ROOT
    / "orchestration"
    / "agent_inbox"
    / "codex"
    / "raisa-shared-application-auth-operational-hardening-sol-acceptance.md"
)
GRAPH_PATH = ROOT / "orchestration" / "continuity" / "emr4-continuity-graph.json"
COMPASS_PATH = ROOT / "orchestration" / "continuity" / "emr4-compass.json"
OPENAPI_PATH = (
    ROOT
    / "docs"
    / "api-spine"
    / "openapi"
    / "application-auth-synthetic-transport.yaml"
)
FIVE_SOURCES = {
    "live_handover_current_baton",
    "current_authority_allocation",
    "active_plan_and_acceptance",
    "protected_evidence_boundaries",
    "git_refs_and_worktree",
}


class _Sink:
    def __init__(self, *, fail: bool = False) -> None:
        self.events: list[TransportDenialEvent] = []
        self.fail = fail

    def record(self, event: TransportDenialEvent) -> None:
        if self.fail:
            raise RequiredTransportDenialAuditUnavailable()
        self.events.append(event)


class _CsrfTransport:
    @staticmethod
    def require_origin(surface: Surface, origin: str | None) -> str:
        if surface is not Surface.WORD_ONLINE or origin != ORIGIN:
            raise TransportRequestDenied()
        return origin

    @staticmethod
    def new_csrf_token() -> str:
        return "csrf." + "c" * 43


def _guard(
    sink: _Sink,
    *,
    limit: int = 100,
    limiter_clock=lambda: 0.0,
    proxy_policy: ProxyTrustPolicy | None = None,
) -> ApplicationAuthOperationalHardening:
    return ApplicationAuthOperationalHardening(
        proxy_policy=proxy_policy or ProxyTrustPolicy(),
        rate_limiter=BoundedFixedWindowRateLimiter(
            requests_per_window=limit,
            window_seconds=60,
            max_keys=8,
            clock=limiter_clock,
        ),
        denial_audit_sink=sink,
        client_hmac_key=b"operational-hardening-test-key-01",
        clock=lambda: NOW,
    )


def _app(guard: ApplicationAuthOperationalHardening) -> FastAPI:
    application = FastAPI()
    application.include_router(router)
    application.dependency_overrides[
        get_application_auth_operational_hardening
    ] = lambda: guard
    application.dependency_overrides[get_application_auth_transport] = _CsrfTransport
    return application


def _post_csrf(client: TestClient, *, origin: str = ORIGIN, headers=None):
    request_headers = {"Origin": origin}
    if headers:
        request_headers.update(headers)
    return client.post(
        "/api/v1/application-auth/csrf",
        headers=request_headers,
        json={"surface": "word_online"},
    )


def _load_runner():
    spec = importlib.util.spec_from_file_location(
        "raisa_shared_auth_operational_hardening_acceptance",
        RUNNER_PATH,
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def disposable_acceptance() -> dict[str, object]:
    return _load_runner().run_acceptance(output_path=None)


def test_login_role_contract_is_inert_separate_and_bounded() -> None:
    capability = "emr4_application_auth_runtime_accept01"
    login = "emr4_application_auth_login_accept01"
    statements = create_deployment_login_role_statements(
        login,
        capability,
        connection_limit=4,
    )
    assert statements == (
        'CREATE ROLE "emr4_application_auth_login_accept01" LOGIN PASSWORD NULL '
        "NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOREPLICATION "
        "NOBYPASSRLS CONNECTION LIMIT 4",
        'GRANT "emr4_application_auth_runtime_accept01" TO '
        '"emr4_application_auth_login_accept01"',
    )
    serialized = "\n".join(statements).lower()
    assert "password null" in serialized
    assert "create table" not in serialized
    assert "grant select" not in serialized
    assert "bypassrls" in serialized
    assert "nobypassrls" in serialized


@pytest.mark.parametrize(
    "value",
    (
        "postgres",
        "emr4_application_auth_runtime_wrong",
        "emr4_application_auth_login_BADVALUE",
        'emr4_application_auth_login_xxxxxxxx" SUPERUSER',
    ),
)
def test_login_role_name_rejects_unbounded_identifiers(value: str) -> None:
    with pytest.raises(ValueError):
        require_login_role_identifier(value)


def test_pool_policy_rejects_unbounded_or_role_exceeding_values() -> None:
    with pytest.raises(ValueError):
        ApplicationAuthPoolPolicy(pool_size=0)
    with pytest.raises(ValueError):
        ApplicationAuthPoolPolicy(pool_size=3, max_overflow=2, login_connection_limit=4)
    policy = ApplicationAuthPoolPolicy(
        pool_size=2,
        max_overflow=1,
        pool_timeout_seconds=0.25,
        pool_recycle_seconds=60,
        login_connection_limit=3,
    )
    assert policy.pool_size + policy.max_overflow == policy.login_connection_limit


def test_pool_factory_rejects_owner_or_non_postgresql_urls_before_connect() -> None:
    with pytest.raises(ValueError, match="PostgreSQL"):
        create_application_auth_engine(
            "sqlite:///synthetic.db",
            login_role="emr4_application_auth_login_accept01",
            capability_role="emr4_application_auth_runtime_accept01",
        )
    with pytest.raises(ValueError, match="exact deployment login"):
        create_application_auth_engine(
            "postgresql://postgres:secret@127.0.0.1:5434/synthetic",
            login_role="emr4_application_auth_login_accept01",
            capability_role="emr4_application_auth_runtime_accept01",
        )


def test_proxy_policy_uses_direct_peer_without_forwarded_headers() -> None:
    policy = ProxyTrustPolicy()
    assert policy.resolve_client(
        direct_peer="2001:db8::1",
        headers={},
    ) == "2001:db8::1"


def test_proxy_policy_accepts_one_exact_https_hop() -> None:
    policy = ProxyTrustPolicy.from_cidrs(["10.42.0.0/16"])
    assert policy.resolve_client(
        direct_peer="10.42.3.4",
        headers={
            "x-forwarded-for": "198.51.100.9",
            "x-forwarded-proto": "https",
        },
    ) == "198.51.100.9"


@pytest.mark.parametrize(
    ("direct_peer", "headers"),
    (
        (
            "198.51.100.5",
            {"x-forwarded-for": "203.0.113.1", "x-forwarded-proto": "https"},
        ),
        (
            "10.42.0.7",
            {
                "x-forwarded-for": "198.51.100.1, 198.51.100.2",
                "x-forwarded-proto": "https",
            },
        ),
        (
            "10.42.0.7",
            {"x-forwarded-for": "198.51.100.1", "x-forwarded-proto": "http"},
        ),
        ("10.42.0.7", {}),
        ("198.51.100.5", {"forwarded": "for=203.0.113.1;proto=https"}),
        (None, {}),
    ),
)
def test_proxy_policy_rejects_spoof_chains_and_ambiguity(
    direct_peer: str | None,
    headers: dict[str, str],
) -> None:
    policy = ProxyTrustPolicy.from_cidrs(["10.42.0.0/16"])
    with pytest.raises(TransportRequestDenied):
        policy.resolve_client(direct_peer=direct_peer, headers=headers)


def test_rate_limiter_is_bounded_and_audits_first_block_only() -> None:
    now = [1.0]
    limiter = BoundedFixedWindowRateLimiter(
        requests_per_window=1,
        window_seconds=10,
        max_keys=2,
        clock=lambda: now[0],
    )
    keys = ["sha256:" + character * 64 for character in "abc"]
    assert limiter.check(keys[0]).allowed is True
    first_block = limiter.check(keys[0])
    second_block = limiter.check(keys[0])
    assert first_block.allowed is False and first_block.audit_required is True
    assert second_block.allowed is False and second_block.audit_required is False
    limiter.check(keys[1])
    limiter.check(keys[2])
    assert limiter.live_key_count() == 2
    now[0] = 11.0
    assert limiter.check(keys[0]).allowed is True


def test_origin_denial_is_retained_without_raw_network_or_request_values() -> None:
    sink = _Sink()
    with TestClient(
        _app(_guard(sink)),
        base_url=ORIGIN,
        client=TEST_CLIENT,
    ) as client:
        response = _post_csrf(client, origin="https://foreign.synthetic.invalid")
    assert response.status_code == 403
    assert response.json() == {"detail": REQUEST_NOT_ADMITTED}
    assert len(sink.events) == 1
    event = sink.events[0]
    assert event.reason_code == "transport_request_not_admitted"
    assert event.action == "auth.transport.csrf"
    serialized = repr(asdict(event))
    for raw in (
        "198.51.100.24",
        "foreign.synthetic.invalid",
        "csrf.",
        "x-forwarded-for",
    ):
        assert raw not in serialized
    assert event.client_reference_hash.startswith("sha256:")
    assert len(event.client_reference_hash) == 71


def test_untrusted_forwarded_spoof_is_denied_and_retained() -> None:
    sink = _Sink()
    with TestClient(
        _app(_guard(sink)),
        base_url=ORIGIN,
        client=TEST_CLIENT,
    ) as client:
        response = _post_csrf(
            client,
            headers={
                "X-Forwarded-For": "203.0.113.55",
                "X-Forwarded-Proto": "https",
            },
        )
    assert response.status_code == 403
    assert response.json() == {"detail": REQUEST_NOT_ADMITTED}
    assert len(sink.events) == 1
    assert "203.0.113.55" not in repr(asdict(sink.events[0]))


def test_duplicate_forwarded_headers_are_rejected_before_rate_admission() -> None:
    sink = _Sink()
    proxy = ProxyTrustPolicy.from_cidrs(["10.42.0.0/16"])
    with TestClient(
        _app(_guard(sink, proxy_policy=proxy)),
        base_url=ORIGIN,
        client=("10.42.0.7", 50000),
    ) as client:
        response = client.post(
            "/api/v1/application-auth/csrf",
            headers=[
                ("Origin", ORIGIN),
                ("X-Forwarded-For", "198.51.100.1"),
                ("X-Forwarded-For", "198.51.100.2"),
                ("X-Forwarded-Proto", "https"),
            ],
            json={"surface": "word_online"},
        )
    assert response.status_code == 403
    assert response.json() == {"detail": REQUEST_NOT_ADMITTED}
    assert len(sink.events) == 1


def test_first_rate_block_is_retained_and_later_blocks_do_not_amplify_audit() -> None:
    sink = _Sink()
    guard = _guard(sink, limit=1)
    with TestClient(
        _app(guard),
        base_url=ORIGIN,
        client=TEST_CLIENT,
    ) as client:
        admitted = _post_csrf(client)
        first = _post_csrf(client)
        second = _post_csrf(client)
    assert admitted.status_code == 200
    for response in (first, second):
        assert response.status_code == 429
        assert response.json() == {"detail": REQUEST_RATE_LIMITED}
        assert response.headers["retry-after"] == "60"
        assert response.headers["cache-control"] == "no-store"
        assert response.headers.get_list("set-cookie") == []
    assert [event.reason_code for event in sink.events] == ["transport_rate_limited"]


def test_required_denial_audit_outage_stays_closed_as_generic_503() -> None:
    sink = _Sink(fail=True)
    with TestClient(
        _app(_guard(sink)),
        base_url=ORIGIN,
        client=TEST_CLIENT,
    ) as client:
        response = _post_csrf(client, origin="https://foreign.synthetic.invalid")
    assert response.status_code == 503
    assert response.json() == {"detail": AUTHENTICATION_UNAVAILABLE}
    assert response.headers["cache-control"] == "no-store"
    assert response.headers.get_list("set-cookie") == []


def test_failed_rate_denial_audit_is_retried_before_later_429_release() -> None:
    sink = _Sink(fail=True)
    guard = _guard(sink, limit=1)
    with TestClient(
        _app(guard),
        base_url=ORIGIN,
        client=TEST_CLIENT,
    ) as client:
        assert _post_csrf(client).status_code == 200
        failed_audit = _post_csrf(client)
        sink.fail = False
        retried_audit = _post_csrf(client)
        coalesced = _post_csrf(client)
    assert failed_audit.status_code == 503
    assert retried_audit.status_code == 429
    assert coalesced.status_code == 429
    assert [event.reason_code for event in sink.events] == ["transport_rate_limited"]


def test_successful_request_keeps_existing_cookie_contract_and_no_denial_audit() -> None:
    sink = _Sink()
    with TestClient(
        _app(_guard(sink)),
        base_url=ORIGIN,
        client=TEST_CLIENT,
    ) as client:
        response = _post_csrf(client)
    assert response.status_code == 200
    cookie = response.headers.get_list("set-cookie")[0].lower()
    assert cookie.startswith(f"{CSRF_COOKIE_NAME.lower()}=")
    assert all(value in cookie for value in ("secure", "httponly", "partitioned"))
    assert sink.events == []


def test_disposable_live_local_operational_acceptance_passes(
    disposable_acceptance: dict[str, object],
) -> None:
    assert disposable_acceptance["passed"] is True
    assert disposable_acceptance["result"] == (
        "raisa_shared_application_auth_operational_hardening_pass"
    )
    assert disposable_acceptance["cleanup"]["passed"] is True
    assert disposable_acceptance["bounded_pool"]["passed"] is True
    assert disposable_acceptance["retained_denial_audit"]["passed"] is True


def test_recorded_operational_evidence_is_target_and_raw_value_free() -> None:
    evidence = json.loads(EVIDENCE_PATH.read_text(encoding="utf-8"))
    serialized = json.dumps(evidence, sort_keys=True)
    assert evidence["passed"] is True
    assert evidence["evidence_raw_or_target_match_count"] == 0
    assert evidence["cleanup"]["database_absent_after"] is True
    assert evidence["cleanup"]["login_role_absent_after"] is True
    assert evidence["cleanup"]["capability_role_absent_after"] is True
    assert evidence["retained_denial_audit"]["raw_value_match_count"] == 0
    for forbidden in (
        "postgresql://",
        "emr4_auth_transport_acceptance_",
        "emr4_application_auth_login_",
        "emr4_application_auth_runtime_",
    ):
        assert forbidden not in serialized


def test_preacceptance_receipt_names_five_sources_and_disables_workers() -> None:
    receipt = json.loads(PREACCEPTANCE_RECEIPT_PATH.read_text(encoding="utf-8"))
    assert receipt["status"] == "passed"
    assert receipt["rehydrated_from_receipt"] is True
    assert set(receipt["rehydration_sources"]) == FIVE_SOURCES
    assert receipt["worker_dispatch_permitted"] is False
    assert receipt["revision_binding"] == {
        "continuity_graph_revision_expected": 185,
        "compass_map_revision_expected": 166,
        "compass_source_graph_revision_expected": 185,
        "rendered_compass_exact_validation_required": True,
    }


def test_openapi_records_rate_and_operational_nonproduction_limits() -> None:
    import yaml

    contract = yaml.safe_load(OPENAPI_PATH.read_text(encoding="utf-8"))
    hardening = contract["x-emr4-operational-hardening"]
    assert hardening["deployment_role"]["credential_in_repository"] is False
    assert hardening["proxy"]["default_trusted_networks"] == []
    assert hardening["proxy"]["forwarded_identity_grants_auth_authority"] is False
    assert hardening["rate_limit"]["distributed_or_production_proof"] is False
    assert hardening["database_pool"]["production_proof"] is False
    assert all(
        path_item["post"]["responses"]["429"]["$ref"]
        == "#/components/responses/RequestRateLimited"
        for path_item in contract["paths"].values()
    )


def test_postcompaction_receipt_rehydrates_all_sources_without_workers() -> None:
    receipt = json.loads(POSTCOMPACTION_RECEIPT_PATH.read_text(encoding="utf-8"))
    assert receipt["status"] == "passed"
    assert receipt["rehydrated_from_receipt"] is True
    assert set(receipt["rehydration_sources"]) == FIVE_SOURCES
    assert receipt["worker_dispatch_permitted"] is False


def test_closeout_and_sol_acceptance_preserve_claim_limits() -> None:
    closeout = CLOSEOUT_PATH.read_text(encoding="utf-8")
    acceptance = SOL_ACCEPTANCE_PATH.read_text(encoding="utf-8")
    normalized_closeout = " ".join(closeout.split())
    result = "raisa_shared_application_auth_operational_hardening_pass"
    assert result in closeout
    assert result in acceptance
    for required in (
        "151 focused",
        "193 expanded",
        "12 serial",
        "No commit, push, pull request, staging operation or protected-ref movement",
        "It does not prove internet-scale or distributed abuse resistance",
    ):
        assert required in normalized_closeout
    assert "Nine Dependabot alerts" in acceptance
    assert "No GitHub alert or setting changed" in acceptance


def test_continuity_preserves_the_revision_185_operational_result() -> None:
    graph = json.loads(GRAPH_PATH.read_text(encoding="utf-8"))
    compass = json.loads(COMPASS_PATH.read_text(encoding="utf-8"))
    node = next(
        item
        for item in graph["nodes"]
        if item["id"] == "raisa-shared-application-auth-operational-hardening"
    )
    assert graph["graph_revision"] >= 185
    assert node["id"] == "raisa-shared-application-auth-operational-hardening"
    assert node["status"] == "accepted"
    assert compass["map_revision"] >= 166
    assert compass["source_graph_revision"] == graph["graph_revision"]
    assert any(item["node_id"] == node["id"] for item in compass["journey"])
