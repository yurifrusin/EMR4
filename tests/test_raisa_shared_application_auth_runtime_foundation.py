from __future__ import annotations

import ast
import json
from dataclasses import asdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from threading import Barrier, Lock, Thread

import pytest

from app.services.application_auth_runtime import (
    AUTHORED_SYNTHETIC_DATA_CLASS,
    EXCHANGE_AUDIENCE,
    MAX_EXCHANGE_TTL,
    MAX_IDLE_TTL,
    MAX_PARENT_TTL,
    SURFACE_AUDIENCE,
    ApplicationAuthRuntime,
    AuthAuditEvent,
    AuthAuditEventType,
    AuthRuntimeDenied,
    InMemoryAuthAuditSink,
    InMemoryAuthoredSyntheticStore,
    RequiredAuditUnavailable,
    SessionStatus,
    Surface,
    SyntheticPrincipal,
    pkce_s256_challenge,
)
from scripts.raisa_shared_application_auth_runtime_foundation_acceptance import (
    EVIDENCE_PATH,
    run_acceptance,
)


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "app" / "services" / "application_auth_runtime.py"
PLAN_PATH = ROOT / "docs" / "raisa-shared-application-auth-runtime-foundation-plan.md"
THREAT_MODEL_PATH = (
    ROOT
    / "docs"
    / "security"
    / "raisa-shared-application-auth-runtime-foundation-threat-model-delta.md"
)
RECEIPT_PATH = (
    ROOT
    / "orchestration"
    / "agent_inbox"
    / "codex"
    / "raisa-shared-application-auth-runtime-foundation-rehydration-receipt.json"
)
CLOSEOUT_PATH = (
    ROOT / "docs" / "raisa-shared-application-auth-runtime-foundation-closeout.md"
)
ACCEPTANCE_PATH = (
    ROOT
    / "orchestration"
    / "agent_inbox"
    / "codex"
    / "raisa-shared-application-auth-runtime-foundation-sol-acceptance.md"
)
GRAPH_PATH = ROOT / "orchestration" / "continuity" / "emr4-continuity-graph.json"
COMPASS_PATH = ROOT / "orchestration" / "continuity" / "emr4-compass.json"
COMPASS_REPORT_PATH = ROOT / "docs" / "ariadne-compass-current.md"

NOW = datetime(2026, 7, 31, 12, 0, tzinfo=timezone.utc)
ORIGINS = {
    Surface.WORD_DESKTOP: "https://word-desktop.synthetic.invalid",
    Surface.WORD_ONLINE: "https://word-online.synthetic.invalid",
    Surface.NATIVE_DIARY: "https://diary.synthetic.invalid",
}
VERIFIER = "A" * 64
WRONG_VERIFIER = "B" * 64
STATE = "state-synthetic-0123456789abcdef"
NONCE = "nonce-synthetic-0123456789abcdef"


class MutableClock:
    def __init__(self, value: datetime = NOW) -> None:
        self.value = value

    def __call__(self) -> datetime:
        return self.value

    def advance(self, delta: timedelta) -> None:
        self.value += delta


class DeterministicTokenSource:
    def __init__(self) -> None:
        self._counter = 0
        self._lock = Lock()

    def __call__(self, kind: str) -> str:
        with self._lock:
            self._counter += 1
            return f"{kind}-{self._counter:04d}-" + "x" * 48


class ControllableAuditSink(InMemoryAuthAuditSink):
    def __init__(self) -> None:
        super().__init__(data_class=AUTHORED_SYNTHETIC_DATA_CLASS)
        self.fail = False

    def record_batch(self, events: tuple[AuthAuditEvent, ...]) -> None:
        if self.fail:
            raise RuntimeError("synthetic audit outage")
        super().record_batch(events)


def principal() -> SyntheticPrincipal:
    return SyntheticPrincipal(
        user_id="synthetic-user-gp-001",
        practice_id="synthetic-practice-001",
        current_backend_role="GP",
        practitioner_id="synthetic-practitioner-001",
    )


def runtime_bundle(
    *,
    clock: MutableClock | None = None,
    audit: ControllableAuditSink | None = None,
    parent_ttl: timedelta = MAX_PARENT_TTL,
    idle_ttl: timedelta = MAX_IDLE_TTL,
    exchange_ttl: timedelta = MAX_EXCHANGE_TTL,
) -> tuple[
    ApplicationAuthRuntime,
    InMemoryAuthoredSyntheticStore,
    ControllableAuditSink,
    MutableClock,
]:
    effective_clock = clock or MutableClock()
    effective_audit = audit or ControllableAuditSink()
    store = InMemoryAuthoredSyntheticStore(
        data_class=AUTHORED_SYNTHETIC_DATA_CLASS
    )
    runtime = ApplicationAuthRuntime(
        store=store,
        audit_sink=effective_audit,
        surface_origins=ORIGINS,
        clock=effective_clock,
        token_source=DeterministicTokenSource(),
        parent_ttl=parent_ttl,
        idle_ttl=idle_ttl,
        exchange_ttl=exchange_ttl,
    )
    return runtime, store, effective_audit, effective_clock


def create_word_session(
    runtime: ApplicationAuthRuntime,
    surface: Surface = Surface.WORD_DESKTOP,
):
    return runtime.create_session(
        principal=principal(),
        surface=surface,
        origin=ORIGINS[surface],
    )


def issue_word_to_diary(
    runtime: ApplicationAuthRuntime,
    surface_session_value: str,
    source_surface: Surface = Surface.WORD_DESKTOP,
):
    return runtime.issue_exchange(
        source_surface_session_value=surface_session_value,
        source_surface=source_surface,
        target_surface=Surface.NATIVE_DIARY,
        source_origin=ORIGINS[source_surface],
        target_origin=ORIGINS[Surface.NATIVE_DIARY],
        audience=EXCHANGE_AUDIENCE,
        state=STATE,
        nonce=NONCE,
        pkce_challenge=pkce_s256_challenge(VERIFIER),
    )


def redeem_word_to_diary(
    runtime: ApplicationAuthRuntime,
    exchange_code: str,
    source_surface: Surface = Surface.WORD_DESKTOP,
    **overrides,
):
    arguments = {
        "exchange_code": exchange_code,
        "source_surface": source_surface,
        "target_surface": Surface.NATIVE_DIARY,
        "source_origin": ORIGINS[source_surface],
        "target_origin": ORIGINS[Surface.NATIVE_DIARY],
        "audience": EXCHANGE_AUDIENCE,
        "state": STATE,
        "nonce": NONCE,
        "pkce_verifier": VERIFIER,
    }
    arguments.update(overrides)
    return runtime.redeem_exchange(**arguments)


def reason_from(callable_) -> str:
    with pytest.raises(AuthRuntimeDenied) as caught:
        callable_()
    return caught.value.reason_code


def test_constructor_is_explicit_synthetic_only_and_ttl_bounded() -> None:
    with pytest.raises(ValueError, match="authored_synthetic"):
        InMemoryAuthoredSyntheticStore(data_class="product")
    with pytest.raises(ValueError, match="authored_synthetic"):
        InMemoryAuthAuditSink(data_class="product")

    store = InMemoryAuthoredSyntheticStore(
        data_class=AUTHORED_SYNTHETIC_DATA_CLASS
    )
    audit = ControllableAuditSink()
    with pytest.raises(ValueError, match="exactly all three"):
        ApplicationAuthRuntime(
            store=store,
            audit_sink=audit,
            surface_origins={Surface.WORD_DESKTOP: ORIGINS[Surface.WORD_DESKTOP]},
        )
    with pytest.raises(ValueError, match="parent_ttl"):
        ApplicationAuthRuntime(
            store=store,
            audit_sink=audit,
            surface_origins=ORIGINS,
            parent_ttl=MAX_PARENT_TTL + timedelta(seconds=1),
        )
    with pytest.raises(ValueError, match="idle_ttl"):
        ApplicationAuthRuntime(
            store=store,
            audit_sink=audit,
            surface_origins=ORIGINS,
            idle_ttl=MAX_IDLE_TTL + timedelta(seconds=1),
        )
    with pytest.raises(ValueError, match="exchange_ttl"):
        ApplicationAuthRuntime(
            store=store,
            audit_sink=audit,
            surface_origins=ORIGINS,
            exchange_ttl=MAX_EXCHANGE_TTL + timedelta(seconds=1),
        )


def test_principal_references_are_authored_synthetic_and_office_free() -> None:
    with pytest.raises(ValueError, match="authored-synthetic"):
        SyntheticPrincipal(
            user_id="real-user",
            practice_id="synthetic-practice-001",
            current_backend_role="GP",
            practitioner_id="synthetic-practitioner-001",
        )
    fields = set(SyntheticPrincipal.__dataclass_fields__)
    assert fields == {
        "user_id",
        "practice_id",
        "current_backend_role",
        "practitioner_id",
    }
    assert not any("office" in field or "microsoft" in field for field in fields)


@pytest.mark.parametrize("surface", list(Surface))
def test_each_surface_creates_hash_only_parent_and_binding(surface: Surface) -> None:
    runtime, store, audit, _clock = runtime_bundle()
    created = runtime.create_session(
        principal=principal(),
        surface=surface,
        origin=ORIGINS[surface],
    )
    snapshot = store.snapshot()
    assert len(snapshot.parent_sessions) == 1
    assert len(snapshot.surface_sessions) == 1
    parent = snapshot.parent_sessions[0]
    binding = snapshot.surface_sessions[0]
    assert parent.session_reference_hash.startswith("sha256:")
    assert binding.surface_reference_hash.startswith("sha256:")
    assert binding.parent_session_reference_hash == parent.session_reference_hash
    assert binding.surface is surface
    assert binding.origin == ORIGINS[surface]
    assert binding.audience == SURFACE_AUDIENCE
    assert parent.expires_at - parent.created_at == MAX_PARENT_TTL
    assert binding.idle_expires_at - binding.created_at == MAX_IDLE_TTL
    assert binding.expires_at <= parent.expires_at
    stored = repr(snapshot)
    assert created.parent_session_value not in stored
    assert created.surface_session_value not in stored
    assert [event.event_type for event in audit.snapshot()] == [
        AuthAuditEventType.SESSION_CREATED,
        AuthAuditEventType.SURFACE_BOUND,
    ]


def test_surface_validation_uses_exact_binding_and_fresh_server_principal() -> None:
    runtime, _store, _audit, _clock = runtime_bundle()
    created = create_word_session(runtime)
    context = runtime.validate_surface_session(
        surface_session_value=created.surface_session_value,
        surface=Surface.WORD_DESKTOP,
        origin=ORIGINS[Surface.WORD_DESKTOP],
    )
    assert context.user_id == principal().user_id
    assert context.practice_id == principal().practice_id
    assert context.current_backend_role == "GP"
    assert context.practitioner_id == principal().practitioner_id
    assert context.authority_source == "emr4_backend"
    assert context.data_class == AUTHORED_SYNTHETIC_DATA_CLASS

    assert reason_from(
        lambda: runtime.validate_surface_session(
            surface_session_value=created.surface_session_value,
            surface=Surface.WORD_ONLINE,
            origin=ORIGINS[Surface.WORD_ONLINE],
        )
    ) == "surface_session_surface_mismatch"
    assert reason_from(
        lambda: runtime.validate_surface_session(
            surface_session_value=created.surface_session_value,
            surface=Surface.WORD_DESKTOP,
            origin="https://attacker.invalid",
        )
    ) == "surface_session_origin_mismatch"
    assert reason_from(
        lambda: runtime.validate_surface_session(
            surface_session_value=created.surface_session_value,
            surface=Surface.WORD_DESKTOP,
            origin=ORIGINS[Surface.WORD_DESKTOP],
            audience="attacker-api",
        )
    ) == "surface_session_audience_mismatch"


def test_refresh_never_extends_surface_beyond_parent_absolute_expiry() -> None:
    runtime, store, _audit, clock = runtime_bundle(
        parent_ttl=timedelta(minutes=10),
        idle_ttl=timedelta(minutes=5),
    )
    created = create_word_session(runtime)
    clock.advance(timedelta(minutes=4, seconds=59))
    context = runtime.validate_surface_session(
        surface_session_value=created.surface_session_value,
        surface=Surface.WORD_DESKTOP,
        origin=ORIGINS[Surface.WORD_DESKTOP],
    )
    snapshot = store.snapshot()
    parent = snapshot.parent_sessions[0]
    binding = snapshot.surface_sessions[0]
    expected_idle_expiry = clock.value + timedelta(minutes=5)
    assert context.surface_idle_expires_at == expected_idle_expiry
    assert binding.expires_at == expected_idle_expiry
    assert binding.idle_expires_at == expected_idle_expiry
    assert binding.expires_at <= parent.expires_at


def test_parent_idle_absolute_and_clock_rollback_fail_closed() -> None:
    runtime, store, _audit, clock = runtime_bundle(
        parent_ttl=timedelta(minutes=10),
        idle_ttl=timedelta(minutes=5),
    )
    created = create_word_session(runtime)
    before = store.snapshot()
    clock.advance(timedelta(minutes=5))
    assert reason_from(
        lambda: runtime.validate_surface_session(
            surface_session_value=created.surface_session_value,
            surface=Surface.WORD_DESKTOP,
            origin=ORIGINS[Surface.WORD_DESKTOP],
        )
    ) == "application_session_idle_expired"
    assert store.snapshot() == before

    runtime2, store2, _audit2, clock2 = runtime_bundle(
        parent_ttl=timedelta(minutes=10),
        idle_ttl=timedelta(minutes=10),
    )
    created2 = create_word_session(runtime2)
    before2 = store2.snapshot()
    clock2.advance(timedelta(minutes=10))
    assert reason_from(
        lambda: runtime2.validate_surface_session(
            surface_session_value=created2.surface_session_value,
            surface=Surface.WORD_DESKTOP,
            origin=ORIGINS[Surface.WORD_DESKTOP],
        )
    ) == "application_session_expired"
    assert store2.snapshot() == before2

    runtime3, store3, _audit3, clock3 = runtime_bundle()
    created3 = create_word_session(runtime3)
    before3 = store3.snapshot()
    clock3.value = NOW - timedelta(seconds=1)
    assert reason_from(
        lambda: runtime3.validate_surface_session(
            surface_session_value=created3.surface_session_value,
            surface=Surface.WORD_DESKTOP,
            origin=ORIGINS[Surface.WORD_DESKTOP],
        )
    ) == "clock_rollback_detected"
    assert store3.snapshot() == before3


def test_explicit_surface_parent_and_generation_revocation_fail_closed() -> None:
    runtime, store, _audit, _clock = runtime_bundle()
    created = create_word_session(runtime)
    runtime.revoke_surface_session(
        surface_session_value=created.surface_session_value,
    )
    assert store.snapshot().surface_sessions[0].status is SessionStatus.REVOKED
    assert reason_from(
        lambda: runtime.validate_surface_session(
            surface_session_value=created.surface_session_value,
            surface=Surface.WORD_DESKTOP,
            origin=ORIGINS[Surface.WORD_DESKTOP],
        )
    ) == "surface_session_revoked"

    runtime2, store2, _audit2, _clock2 = runtime_bundle()
    created2 = create_word_session(runtime2)
    runtime2.revoke_parent_session(
        parent_session_value=created2.parent_session_value,
    )
    assert store2.snapshot().parent_sessions[0].status is SessionStatus.REVOKED
    assert reason_from(
        lambda: runtime2.validate_surface_session(
            surface_session_value=created2.surface_session_value,
            surface=Surface.WORD_DESKTOP,
            origin=ORIGINS[Surface.WORD_DESKTOP],
        )
    ) == "application_session_revoked"

    runtime3, store3, _audit3, _clock3 = runtime_bundle()
    created3 = create_word_session(runtime3)
    generation = runtime3.advance_principal_generation(
        principal=principal(),
        reason="role_changed",
    )
    assert generation == created3.generation + 1
    assert store3.snapshot().parent_sessions[0].status is SessionStatus.REVOKED
    assert reason_from(
        lambda: runtime3.validate_surface_session(
            surface_session_value=created3.surface_session_value,
            surface=Surface.WORD_DESKTOP,
            origin=ORIGINS[Surface.WORD_DESKTOP],
        )
    ) == "application_session_revoked"


@pytest.mark.parametrize(
    "source_surface",
    [Surface.WORD_DESKTOP, Surface.WORD_ONLINE],
)
def test_word_exchange_creates_one_valid_native_diary_binding(
    source_surface: Surface,
) -> None:
    runtime, store, _audit, _clock = runtime_bundle()
    created = create_word_session(runtime, source_surface)
    issued = issue_word_to_diary(
        runtime,
        created.surface_session_value,
        source_surface,
    )
    before_redeem = store.snapshot()
    grant = before_redeem.exchange_grants[0]
    stored = repr(before_redeem)
    assert issued.exchange_code not in stored
    assert STATE not in stored
    assert NONCE not in stored
    assert VERIFIER not in stored
    assert grant.grant_reference_hash.startswith("sha256:")
    assert grant.state_hash.startswith("sha256:")
    assert grant.nonce_hash.startswith("sha256:")
    assert issued.expires_at - grant.issued_at <= MAX_EXCHANGE_TTL

    redeemed = redeem_word_to_diary(
        runtime,
        issued.exchange_code,
        source_surface,
    )
    after_redeem = store.snapshot()
    assert len(after_redeem.surface_sessions) == 2
    assert after_redeem.exchange_grants[0].consumed_at == NOW
    assert redeemed.target_surface is Surface.NATIVE_DIARY
    context = runtime.validate_surface_session(
        surface_session_value=redeemed.target_surface_session_value,
        surface=Surface.NATIVE_DIARY,
        origin=ORIGINS[Surface.NATIVE_DIARY],
    )
    assert context.surface is Surface.NATIVE_DIARY
    assert context.user_id == principal().user_id


def test_exchange_replay_is_terminal_and_creates_no_extra_surface() -> None:
    runtime, store, _audit, _clock = runtime_bundle()
    created = create_word_session(runtime)
    issued = issue_word_to_diary(runtime, created.surface_session_value)
    redeem_word_to_diary(runtime, issued.exchange_code)
    before_replay = store.snapshot()
    assert reason_from(
        lambda: redeem_word_to_diary(runtime, issued.exchange_code)
    ) == "exchange_already_consumed"
    assert store.snapshot() == before_replay


@pytest.mark.parametrize(
    ("overrides", "expected_reason"),
    [
        (
            {"source_surface": Surface.WORD_ONLINE},
            "exchange_source_surface_mismatch",
        ),
        (
            {"target_surface": Surface.WORD_ONLINE},
            "exchange_target_surface_mismatch",
        ),
        (
            {"source_origin": "https://attacker.invalid"},
            "exchange_source_origin_mismatch",
        ),
        (
            {"target_origin": "https://attacker.invalid"},
            "exchange_target_origin_mismatch",
        ),
        ({"audience": "attacker-exchange"}, "exchange_audience_mismatch"),
        ({"state": "wrong-state-0123456789abcdef"}, "exchange_state_mismatch"),
        ({"nonce": "wrong-nonce-0123456789abcdef"}, "exchange_nonce_mismatch"),
        ({"pkce_verifier": WRONG_VERIFIER}, "exchange_pkce_mismatch"),
    ],
)
def test_exchange_binding_mismatches_do_not_consume_or_bind(
    overrides: dict,
    expected_reason: str,
) -> None:
    runtime, store, _audit, _clock = runtime_bundle()
    created = create_word_session(runtime)
    issued = issue_word_to_diary(runtime, created.surface_session_value)
    before = store.snapshot()
    assert reason_from(
        lambda: redeem_word_to_diary(
            runtime,
            issued.exchange_code,
            **overrides,
        )
    ) == expected_reason
    assert store.snapshot() == before


def test_expired_and_revoked_parent_exchanges_fail_without_consumption() -> None:
    runtime, store, _audit, clock = runtime_bundle(
        exchange_ttl=timedelta(seconds=10)
    )
    created = create_word_session(runtime)
    issued = issue_word_to_diary(runtime, created.surface_session_value)
    before = store.snapshot()
    clock.advance(timedelta(seconds=10))
    assert reason_from(
        lambda: redeem_word_to_diary(runtime, issued.exchange_code)
    ) == "exchange_expired"
    assert store.snapshot() == before

    runtime2, store2, _audit2, _clock2 = runtime_bundle()
    created2 = create_word_session(runtime2)
    issued2 = issue_word_to_diary(runtime2, created2.surface_session_value)
    runtime2.advance_principal_generation(
        principal=principal(),
        reason="user_deactivated",
    )
    before2 = store2.snapshot()
    assert reason_from(
        lambda: redeem_word_to_diary(runtime2, issued2.exchange_code)
    ) == "exchange_parent_session_inactive"
    assert store2.snapshot() == before2


def test_concurrent_exchange_redemption_admits_exactly_one_consumer() -> None:
    runtime, store, _audit, _clock = runtime_bundle()
    created = create_word_session(runtime)
    issued = issue_word_to_diary(runtime, created.surface_session_value)
    barrier = Barrier(3)
    successes: list[str] = []
    denials: list[str] = []
    result_lock = Lock()

    def redeem() -> None:
        barrier.wait()
        try:
            result = redeem_word_to_diary(runtime, issued.exchange_code)
            with result_lock:
                successes.append(result.target_surface_session_value)
        except AuthRuntimeDenied as exc:
            with result_lock:
                denials.append(exc.reason_code)

    threads = [Thread(target=redeem), Thread(target=redeem)]
    for thread in threads:
        thread.start()
    barrier.wait()
    for thread in threads:
        thread.join(timeout=5)

    assert len(successes) == 1
    assert denials == ["exchange_already_consumed"]
    assert len(store.snapshot().surface_sessions) == 2
    assert store.snapshot().exchange_grants[0].consumed_at == NOW


def test_required_audit_failure_rolls_back_create_refresh_and_issue() -> None:
    audit = ControllableAuditSink()
    runtime, store, _audit, clock = runtime_bundle(audit=audit)
    audit.fail = True
    before_create = store.snapshot()
    with pytest.raises(RequiredAuditUnavailable):
        create_word_session(runtime)
    assert store.snapshot() == before_create

    audit.fail = False
    created = create_word_session(runtime)
    clock.advance(timedelta(minutes=1))
    before_refresh = store.snapshot()
    audit.fail = True
    with pytest.raises(RequiredAuditUnavailable):
        runtime.validate_surface_session(
            surface_session_value=created.surface_session_value,
            surface=Surface.WORD_DESKTOP,
            origin=ORIGINS[Surface.WORD_DESKTOP],
        )
    assert store.snapshot() == before_refresh

    before_issue = store.snapshot()
    with pytest.raises(RequiredAuditUnavailable):
        issue_word_to_diary(runtime, created.surface_session_value)
    assert store.snapshot() == before_issue


def test_required_audit_failure_leaves_grant_unconsumed_and_revocation_unchanged() -> None:
    audit = ControllableAuditSink()
    runtime, store, _audit, _clock = runtime_bundle(audit=audit)
    created = create_word_session(runtime)
    issued = issue_word_to_diary(runtime, created.surface_session_value)

    before_redeem = store.snapshot()
    audit.fail = True
    with pytest.raises(RequiredAuditUnavailable):
        redeem_word_to_diary(runtime, issued.exchange_code)
    assert store.snapshot() == before_redeem

    with pytest.raises(RequiredAuditUnavailable):
        runtime.revoke_parent_session(
            parent_session_value=created.parent_session_value,
        )
    assert store.snapshot() == before_redeem

    with pytest.raises(RequiredAuditUnavailable):
        runtime.advance_principal_generation(
            principal=principal(),
            reason="security_reset",
        )
    assert store.snapshot() == before_redeem


def test_audit_records_have_required_metadata_and_no_forbidden_fields_or_values() -> None:
    runtime, _store, audit, _clock = runtime_bundle()
    created = create_word_session(runtime)
    issued = issue_word_to_diary(runtime, created.surface_session_value)
    redeemed = redeem_word_to_diary(runtime, issued.exchange_code)
    runtime.validate_surface_session(
        surface_session_value=redeemed.target_surface_session_value,
        surface=Surface.NATIVE_DIARY,
        origin=ORIGINS[Surface.NATIVE_DIARY],
    )

    required = {
        "event_type",
        "occurred_at",
        "correlation_id",
        "session_reference_hash",
        "user_id",
        "practice_id",
        "current_backend_role",
        "surface",
        "action",
        "resource_type",
        "policy_version",
        "decision",
        "reason_codes",
    }
    forbidden = {
        "password",
        "bearer_token",
        "access_token",
        "cookie",
        "exchange_code",
        "pkce_verifier",
        "microsoft_account_identifier",
        "microsoft_tenant_identifier",
        "document_identifier",
        "request_content",
        "patient_data",
        "clinical_data",
    }
    events = audit.snapshot()
    assert events
    for event in events:
        payload = asdict(event)
        assert required <= set(payload)
        assert not forbidden.intersection(payload)
        assert event.session_reference_hash.startswith("sha256:")
    serialized = repr(events)
    for raw_value in (
        created.parent_session_value,
        created.surface_session_value,
        issued.exchange_code,
        redeemed.target_surface_session_value,
        VERIFIER,
        STATE,
        NONCE,
    ):
        assert raw_value not in serialized


def test_denials_and_safe_snapshots_do_not_echo_raw_secrets() -> None:
    runtime, store, _audit, _clock = runtime_bundle()
    raw = "surface-secret-" + "q" * 64
    with pytest.raises(AuthRuntimeDenied) as caught:
        runtime.validate_surface_session(
            surface_session_value=raw,
            surface=Surface.WORD_DESKTOP,
            origin=ORIGINS[Surface.WORD_DESKTOP],
        )
    assert raw not in str(caught.value)
    assert raw not in repr(store.snapshot())


def test_audit_correlation_and_principal_metadata_are_bounded() -> None:
    runtime, store, audit, _clock = runtime_bundle()
    with pytest.raises(AuthRuntimeDenied) as caught:
        runtime.create_session(
            principal=principal(),
            surface=Surface.WORD_DESKTOP,
            origin=ORIGINS[Surface.WORD_DESKTOP],
            correlation_id="correlation-secret value copied from a token",
        )
    assert caught.value.reason_code == "correlation_id_invalid"
    assert store.snapshot().parent_sessions == ()
    assert audit.snapshot() == ()

    with pytest.raises(ValueError, match="known backend role"):
        SyntheticPrincipal(
            user_id="synthetic-user-001",
            practice_id="synthetic-practice-001",
            current_backend_role="GP with embedded metadata",
            practitioner_id="synthetic-practitioner-001",
        )
    with pytest.raises(ValueError, match="authored-synthetic"):
        SyntheticPrincipal(
            user_id="synthetic-user-" + "x" * 100,
            practice_id="synthetic-practice-001",
            current_backend_role="GP",
            practitioner_id="synthetic-practitioner-001",
        )


def test_pkce_s256_matches_rfc_7636_reference_vector() -> None:
    verifier = "dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk"
    assert pkce_s256_challenge(verifier) == (
        "E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM"
    )
    assert reason_from(
        lambda: pkce_s256_challenge("too-short")
    ) == "exchange_pkce_verifier_invalid"


def test_module_has_no_route_database_provider_cookie_or_process_wiring() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported_roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_roots.add(node.module.split(".")[0])
    assert not imported_roots.intersection(
        {
            "fastapi",
            "sqlalchemy",
            "requests",
            "httpx",
            "socket",
            "subprocess",
            "google",
            "jwt",
        }
    )
    assert "APIRouter" not in source
    assert "Depends(" not in source
    assert "SessionLocal" not in source
    assert "set_cookie" not in source
    assert "localStorage" not in source
    assert "Authorization" not in source
    assert "ApplicationAuthRuntime(" not in (
        ROOT / "app" / "main.py"
    ).read_text(encoding="utf-8")
    router_source = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (ROOT / "app" / "routers").glob("*.py")
    )
    assert "application_auth_runtime" not in router_source


def test_plan_threat_model_and_receipt_freeze_the_closed_boundary() -> None:
    plan = PLAN_PATH.read_text(encoding="utf-8")
    threat_model = THREAT_MODEL_PATH.read_text(encoding="utf-8")
    receipt = RECEIPT_PATH.read_text(encoding="utf-8")
    assert "route-free" in plan
    assert "product-derived reads remain closed" in plan
    assert "Concurrent" in threat_model or "concurrent" in threat_model
    assert "audit" in threat_model.lower()
    assert (
        "Version: 8fa732592fbee4f57c322b13d9d8ff89fcc7fa33"
        in threat_model
    )
    for source in (
        "live_handover_current_baton",
        "current_authority_allocation",
        "active_plan_and_acceptance",
        "protected_evidence_boundaries",
        "git_refs_and_worktree",
    ):
        assert source in receipt
    assert '"worker_dispatch_permitted": false' in receipt


def test_provider_free_acceptance_evidence_matches_runtime() -> None:
    generated = run_acceptance()
    stored = json.loads(EVIDENCE_PATH.read_text(encoding="utf-8"))
    assert generated == stored
    assert generated["result"] == "pass"
    assert generated["checks"] and all(generated["checks"].values())
    assert generated["authority_and_side_effects"] == {
        "provider_calls": 0,
        "identity_provider_calls": 0,
        "microsoft_graph_or_office_identity_calls": 0,
        "cloud_or_iam_mutations": 0,
        "fastapi_or_graphql_route_calls": 0,
        "cookie_issuances": 0,
        "database_reads": 0,
        "database_writes": 0,
        "product_data_reads": 0,
        "patient_or_clinical_data_fields": 0,
        "appointment_commands": 0,
        "microphone_accesses": 0,
        "document_mutations": 0,
        "deployments": 0,
    }


def test_closeout_continuity_and_compass_bind_runtime_foundation_pass() -> None:
    result = "raisa_shared_application_auth_runtime_foundation_pass"
    graph = json.loads(GRAPH_PATH.read_text(encoding="utf-8"))
    compass = json.loads(COMPASS_PATH.read_text(encoding="utf-8"))
    node = next(
        item
        for item in graph["nodes"]
        if item["id"] == "raisa-shared-application-auth-runtime-foundation"
    )
    assert graph["graph_revision"] >= 182
    assert node["id"] == "raisa-shared-application-auth-runtime-foundation"
    assert node["status"] == "accepted"
    assert node["relationships"] == [
        {
            "node_id": "raisa-shared-application-auth-clinician-role-boundary",
            "relation": "builds_on",
        }
    ]
    assert compass["map_revision"] >= 163
    assert compass["source_graph_revision"] == graph["graph_revision"]
    assert compass["current_position"]["node_id"] == (
        "raisa-shared-application-auth-postgresql-persistence"
    )
    assert "shared-application-auth-runtime-foundation" not in {
        item["id"] for item in compass["decision_horizon"]
    }
    assert "shared-application-auth-postgresql-persistence" not in {
        item["id"] for item in compass["decision_horizon"]
    }
    assert "shared-application-auth-runtime-role-secure-transport" in {
        item["id"] for item in compass["decision_horizon"]
    }
    assert result in CLOSEOUT_PATH.read_text(encoding="utf-8")
    assert result in ACCEPTANCE_PATH.read_text(encoding="utf-8")
    report = COMPASS_REPORT_PATH.read_text(encoding="utf-8")
    assert f"Compass map revision {compass['map_revision']}" in report
    assert f"continuity graph revision {graph['graph_revision']}" in report
