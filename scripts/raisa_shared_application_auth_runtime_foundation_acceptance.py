"""Generate deterministic provider-free evidence for the auth runtime foundation."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from threading import Barrier, Lock, Thread
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services.application_auth_runtime import (
    AUTHORED_SYNTHETIC_DATA_CLASS,
    EXCHANGE_AUDIENCE,
    ApplicationAuthRuntime,
    AuthAuditEvent,
    AuthRuntimeDenied,
    InMemoryAuthAuditSink,
    InMemoryAuthoredSyntheticStore,
    Surface,
    SyntheticPrincipal,
    pkce_s256_challenge,
)


RUNTIME_PATH = ROOT / "app" / "services" / "application_auth_runtime.py"
PLAN_PATH = ROOT / "docs" / "raisa-shared-application-auth-runtime-foundation-plan.md"
THREAT_MODEL_PATH = (
    ROOT
    / "docs"
    / "security"
    / "raisa-shared-application-auth-runtime-foundation-threat-model-delta.md"
)
PARENT_POLICY_PATH = (
    ROOT
    / "orchestration"
    / "continuity"
    / "raisa-shared-application-auth-clinician-role-boundary"
    / "auth-boundary-policy.json"
)
EVIDENCE_PATH = (
    ROOT
    / "orchestration"
    / "continuity"
    / "raisa-shared-application-auth-runtime-foundation"
    / "provider-free-acceptance-evidence.json"
)

NOW = datetime(2026, 7, 31, 13, 0, tzinfo=timezone.utc)
ORIGINS = {
    Surface.WORD_DESKTOP: "https://word-desktop.synthetic.invalid",
    Surface.WORD_ONLINE: "https://word-online.synthetic.invalid",
    Surface.NATIVE_DIARY: "https://diary.synthetic.invalid",
}
VERIFIER = "A" * 64
STATE = "state-synthetic-0123456789abcdef"
NONCE = "nonce-synthetic-0123456789abcdef"


class AcceptanceClock:
    def __init__(self) -> None:
        self.value = NOW

    def __call__(self) -> datetime:
        return self.value


class AcceptanceTokenSource:
    def __init__(self) -> None:
        self.counter = 0
        self.lock = Lock()

    def __call__(self, kind: str) -> str:
        with self.lock:
            self.counter += 1
            return f"{kind}-{self.counter:04d}-" + "e" * 48


class AcceptanceAuditSink(InMemoryAuthAuditSink):
    def __init__(self) -> None:
        super().__init__(data_class=AUTHORED_SYNTHETIC_DATA_CLASS)
        self.fail = False

    def record_batch(self, events: tuple[AuthAuditEvent, ...]) -> None:
        if self.fail:
            raise RuntimeError("authored-synthetic audit outage")
        super().record_batch(events)


def _principal() -> SyntheticPrincipal:
    return SyntheticPrincipal(
        user_id="synthetic-user-acceptance",
        practice_id="synthetic-practice-acceptance",
        current_backend_role="GP",
        practitioner_id="synthetic-practitioner-acceptance",
    )


def _runtime() -> tuple[
    ApplicationAuthRuntime,
    InMemoryAuthoredSyntheticStore,
    AcceptanceAuditSink,
    AcceptanceClock,
]:
    store = InMemoryAuthoredSyntheticStore(
        data_class=AUTHORED_SYNTHETIC_DATA_CLASS
    )
    audit = AcceptanceAuditSink()
    clock = AcceptanceClock()
    return (
        ApplicationAuthRuntime(
            store=store,
            audit_sink=audit,
            surface_origins=ORIGINS,
            clock=clock,
            token_source=AcceptanceTokenSource(),
        ),
        store,
        audit,
        clock,
    )


def _create(runtime: ApplicationAuthRuntime, surface: Surface):
    surface_slug = surface.value.replace("_", "-")
    return runtime.create_session(
        principal=_principal(),
        surface=surface,
        origin=ORIGINS[surface],
        correlation_id=f"correlation-create-{surface_slug}",
    )


def _issue(runtime: ApplicationAuthRuntime, session_value: str, source: Surface):
    source_slug = source.value.replace("_", "-")
    return runtime.issue_exchange(
        source_surface_session_value=session_value,
        source_surface=source,
        target_surface=Surface.NATIVE_DIARY,
        source_origin=ORIGINS[source],
        target_origin=ORIGINS[Surface.NATIVE_DIARY],
        audience=EXCHANGE_AUDIENCE,
        state=STATE,
        nonce=NONCE,
        pkce_challenge=pkce_s256_challenge(VERIFIER),
        correlation_id=f"correlation-issue-{source_slug}",
    )


def _redeem(
    runtime: ApplicationAuthRuntime,
    code: str,
    source: Surface,
    **overrides: Any,
):
    source_slug = source.value.replace("_", "-")
    values: dict[str, Any] = {
        "exchange_code": code,
        "source_surface": source,
        "target_surface": Surface.NATIVE_DIARY,
        "source_origin": ORIGINS[source],
        "target_origin": ORIGINS[Surface.NATIVE_DIARY],
        "audience": EXCHANGE_AUDIENCE,
        "state": STATE,
        "nonce": NONCE,
        "pkce_verifier": VERIFIER,
        "correlation_id": f"correlation-redeem-{source_slug}",
    }
    values.update(overrides)
    return runtime.redeem_exchange(**values)


def _denial(callable_) -> str:
    try:
        callable_()
    except AuthRuntimeDenied as exc:
        return exc.reason_code
    raise AssertionError("expected a fail-closed denial")


def _sha256(path: Path) -> str:
    return f"sha256:{hashlib.sha256(path.read_bytes()).hexdigest()}"


def _json_safe(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat().replace("+00:00", "Z")
    if hasattr(value, "value"):
        return value.value
    raise TypeError(f"unsupported evidence value: {type(value).__name__}")


def _session_evidence() -> dict[str, Any]:
    outcomes = []
    for surface in Surface:
        runtime, store, audit, _clock = _runtime()
        created = _create(runtime, surface)
        context = runtime.validate_surface_session(
            surface_session_value=created.surface_session_value,
            surface=surface,
            origin=ORIGINS[surface],
            correlation_id=(
                f"correlation-validate-{surface.value.replace('_', '-')}"
            ),
        )
        snapshot = store.snapshot()
        serialized = repr(snapshot) + repr(audit.snapshot())
        outcomes.append(
            {
                "surface": surface.value,
                "decision": "admit",
                "authority_source": context.authority_source,
                "generation": context.generation,
                "parent_ttl_seconds": int(
                    (
                        snapshot.parent_sessions[0].expires_at
                        - snapshot.parent_sessions[0].created_at
                    ).total_seconds()
                ),
                "surface_idle_ttl_seconds": int(
                    (
                        snapshot.surface_sessions[0].idle_expires_at
                        - snapshot.surface_sessions[0].last_observed_at
                    ).total_seconds()
                ),
                "surface_not_after_parent": (
                    snapshot.surface_sessions[0].expires_at
                    <= snapshot.parent_sessions[0].expires_at
                ),
                "raw_parent_stored_or_audited": (
                    created.parent_session_value in serialized
                ),
                "raw_surface_stored_or_audited": (
                    created.surface_session_value in serialized
                ),
            }
        )
    return {
        "case_count": len(outcomes),
        "admitted_surfaces": sorted(item["surface"] for item in outcomes),
        "all_hash_only": all(
            not item["raw_parent_stored_or_audited"]
            and not item["raw_surface_stored_or_audited"]
            for item in outcomes
        ),
        "all_surface_expiry_bounded_by_parent": all(
            item["surface_not_after_parent"] for item in outcomes
        ),
        "outcomes": outcomes,
    }


def _revocation_evidence() -> dict[str, Any]:
    runtime, _store, _audit, _clock = _runtime()
    surface_created = _create(runtime, Surface.WORD_DESKTOP)
    runtime.revoke_surface_session(
        surface_session_value=surface_created.surface_session_value,
        correlation_id="correlation-revoke-surface",
    )
    surface_reason = _denial(
        lambda: runtime.validate_surface_session(
            surface_session_value=surface_created.surface_session_value,
            surface=Surface.WORD_DESKTOP,
            origin=ORIGINS[Surface.WORD_DESKTOP],
        )
    )

    runtime2, _store2, _audit2, _clock2 = _runtime()
    parent_created = _create(runtime2, Surface.WORD_DESKTOP)
    runtime2.revoke_parent_session(
        parent_session_value=parent_created.parent_session_value,
        correlation_id="correlation-revoke-parent",
    )
    parent_reason = _denial(
        lambda: runtime2.validate_surface_session(
            surface_session_value=parent_created.surface_session_value,
            surface=Surface.WORD_DESKTOP,
            origin=ORIGINS[Surface.WORD_DESKTOP],
        )
    )

    runtime3, store3, _audit3, _clock3 = _runtime()
    generation_created = _create(runtime3, Surface.WORD_DESKTOP)
    new_generation = runtime3.advance_principal_generation(
        principal=_principal(),
        reason="role_changed",
        correlation_id="correlation-revoke-generation",
    )
    generation_reason = _denial(
        lambda: runtime3.validate_surface_session(
            surface_session_value=generation_created.surface_session_value,
            surface=Surface.WORD_DESKTOP,
            origin=ORIGINS[Surface.WORD_DESKTOP],
        )
    )
    return {
        "case_count": 3,
        "surface_revocation_reason": surface_reason,
        "parent_revocation_reason": parent_reason,
        "generation_revocation_reason": generation_reason,
        "new_generation": new_generation,
        "generation_parent_status": (
            store3.snapshot().parent_sessions[0].status.value
        ),
        "all_fail_closed": all(
            reason.endswith("revoked")
            for reason in (surface_reason, parent_reason, generation_reason)
        ),
    }


def _exchange_evidence() -> dict[str, Any]:
    admitted = []
    for source in (Surface.WORD_DESKTOP, Surface.WORD_ONLINE):
        runtime, store, audit, _clock = _runtime()
        created = _create(runtime, source)
        issued = _issue(runtime, created.surface_session_value, source)
        before = repr(store.snapshot()) + repr(audit.snapshot())
        redeemed = _redeem(runtime, issued.exchange_code, source)
        replay = _denial(lambda: _redeem(runtime, issued.exchange_code, source))
        after = store.snapshot()
        admitted.append(
            {
                "source_surface": source.value,
                "target_surface": redeemed.target_surface.value,
                "decision": "admit_once",
                "replay_reason": replay,
                "grant_consumed": after.exchange_grants[0].consumed_at == NOW,
                "surface_session_count": len(after.surface_sessions),
                "raw_exchange_code_stored_or_audited": issued.exchange_code in before,
                "raw_state_stored_or_audited": STATE in before,
                "raw_nonce_stored_or_audited": NONCE in before,
                "raw_verifier_stored_or_audited": VERIFIER in before,
            }
        )

    mismatch_inputs = [
        ("source_surface", {"source_surface": Surface.WORD_ONLINE}),
        ("target_surface", {"target_surface": Surface.WORD_ONLINE}),
        ("source_origin", {"source_origin": "https://attacker.invalid"}),
        ("target_origin", {"target_origin": "https://attacker.invalid"}),
        ("audience", {"audience": "attacker-exchange"}),
        ("state", {"state": "wrong-state-0123456789abcdef"}),
        ("nonce", {"nonce": "wrong-nonce-0123456789abcdef"}),
        ("pkce", {"pkce_verifier": "B" * 64}),
    ]
    mismatches = []
    for case_id, overrides in mismatch_inputs:
        runtime, store, _audit, _clock = _runtime()
        created = _create(runtime, Surface.WORD_DESKTOP)
        issued = _issue(runtime, created.surface_session_value, Surface.WORD_DESKTOP)
        before = store.snapshot()
        reason = _denial(
            lambda overrides=overrides: _redeem(
                runtime,
                issued.exchange_code,
                Surface.WORD_DESKTOP,
                **overrides,
            )
        )
        mismatches.append(
            {
                "case_id": case_id,
                "reason": reason,
                "store_unchanged": store.snapshot() == before,
            }
        )

    runtime, store, _audit, _clock = _runtime()
    created = _create(runtime, Surface.WORD_DESKTOP)
    issued = _issue(runtime, created.surface_session_value, Surface.WORD_DESKTOP)
    barrier = Barrier(3)
    successes: list[str] = []
    denials: list[str] = []
    result_lock = Lock()

    def concurrent_redeem() -> None:
        barrier.wait()
        try:
            result = _redeem(
                runtime,
                issued.exchange_code,
                Surface.WORD_DESKTOP,
            )
            with result_lock:
                successes.append(result.target_surface.value)
        except AuthRuntimeDenied as exc:
            with result_lock:
                denials.append(exc.reason_code)

    threads = (Thread(target=concurrent_redeem), Thread(target=concurrent_redeem))
    for thread in threads:
        thread.start()
    barrier.wait()
    for thread in threads:
        thread.join(timeout=5)

    return {
        "admitted_case_count": len(admitted),
        "binding_mismatch_case_count": len(mismatches),
        "all_admitted_exactly_once": all(
            item["grant_consumed"]
            and item["surface_session_count"] == 2
            and item["replay_reason"] == "exchange_already_consumed"
            for item in admitted
        ),
        "all_exchange_material_hash_only": all(
            not item["raw_exchange_code_stored_or_audited"]
            and not item["raw_state_stored_or_audited"]
            and not item["raw_nonce_stored_or_audited"]
            and not item["raw_verifier_stored_or_audited"]
            for item in admitted
        ),
        "all_binding_mismatches_leave_store_unchanged": all(
            item["store_unchanged"] for item in mismatches
        ),
        "concurrent_redemption": {
            "success_count": len(successes),
            "denial_reasons": sorted(denials),
            "surface_session_count": len(store.snapshot().surface_sessions),
            "grant_consumed": (
                store.snapshot().exchange_grants[0].consumed_at == NOW
            ),
        },
        "admitted": admitted,
        "binding_mismatches": mismatches,
    }


def _audit_failure_evidence() -> dict[str, Any]:
    runtime, store, audit, _clock = _runtime()
    audit.fail = True
    before_create = store.snapshot()
    create_reason = _denial(lambda: _create(runtime, Surface.WORD_DESKTOP))
    create_unchanged = store.snapshot() == before_create

    audit.fail = False
    created = _create(runtime, Surface.WORD_DESKTOP)
    issued = _issue(runtime, created.surface_session_value, Surface.WORD_DESKTOP)
    audit.fail = True

    before_redeem = store.snapshot()
    redeem_reason = _denial(
        lambda: _redeem(runtime, issued.exchange_code, Surface.WORD_DESKTOP)
    )
    redeem_unchanged = store.snapshot() == before_redeem

    before_revoke = store.snapshot()
    revoke_reason = _denial(
        lambda: runtime.advance_principal_generation(
            principal=_principal(),
            reason="security_reset",
        )
    )
    revoke_unchanged = store.snapshot() == before_revoke
    return {
        "case_count": 3,
        "create": {"reason": create_reason, "store_unchanged": create_unchanged},
        "redeem": {"reason": redeem_reason, "store_unchanged": redeem_unchanged},
        "revoke": {"reason": revoke_reason, "store_unchanged": revoke_unchanged},
        "all_fail_required_audit_unavailable_without_mutation": all(
            reason == "required_audit_unavailable" and unchanged
            for reason, unchanged in (
                (create_reason, create_unchanged),
                (redeem_reason, redeem_unchanged),
                (revoke_reason, revoke_unchanged),
            )
        ),
    }


def _static_boundary_evidence() -> dict[str, Any]:
    source = RUNTIME_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".")[0])
    forbidden_imports = {
        "fastapi",
        "sqlalchemy",
        "requests",
        "httpx",
        "socket",
        "subprocess",
        "google",
        "jwt",
    }
    router_source = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (ROOT / "app" / "routers").glob("*.py")
    )
    return {
        "forbidden_imports_present": sorted(imports.intersection(forbidden_imports)),
        "router_import_present": "application_auth_runtime" in router_source,
        "module_level_runtime_wiring_present": (
            "ApplicationAuthRuntime(" in (ROOT / "app" / "main.py").read_text(
                encoding="utf-8"
            )
        ),
        "api_router_present": "APIRouter" in source,
        "database_session_present": "SessionLocal" in source,
        "cookie_mutation_present": "set_cookie" in source,
    }


def run_acceptance() -> dict[str, Any]:
    sessions = _session_evidence()
    revocation = _revocation_evidence()
    exchange = _exchange_evidence()
    audit_failure = _audit_failure_evidence()
    static_boundary = _static_boundary_evidence()
    checks = {
        "all_three_surfaces_admitted": sessions["admitted_surfaces"]
        == sorted(surface.value for surface in Surface),
        "sessions_hash_only": sessions["all_hash_only"],
        "surface_expiry_bounded": sessions[
            "all_surface_expiry_bounded_by_parent"
        ],
        "revocation_fails_closed": revocation["all_fail_closed"],
        "exchange_single_use": exchange["all_admitted_exactly_once"],
        "exchange_material_hash_only": exchange[
            "all_exchange_material_hash_only"
        ],
        "exchange_mismatches_fail_closed": exchange[
            "all_binding_mismatches_leave_store_unchanged"
        ],
        "concurrent_exactly_one": (
            exchange["concurrent_redemption"]["success_count"] == 1
            and exchange["concurrent_redemption"]["denial_reasons"]
            == ["exchange_already_consumed"]
            and exchange["concurrent_redemption"]["surface_session_count"] == 2
        ),
        "audit_failure_atomic": audit_failure[
            "all_fail_required_audit_unavailable_without_mutation"
        ],
        "route_database_provider_cookie_wiring_absent": not any(
            (
                static_boundary["forbidden_imports_present"],
                static_boundary["router_import_present"],
                static_boundary["module_level_runtime_wiring_present"],
                static_boundary["api_router_present"],
                static_boundary["database_session_present"],
                static_boundary["cookie_mutation_present"],
            )
        ),
    }
    return {
        "schema_version": "emr4.shared-application-auth-runtime-foundation-evidence.v1",
        "recorded_at": NOW.isoformat().replace("+00:00", "Z"),
        "result": "pass" if all(checks.values()) else "revision_required",
        "mode": "repository_local_route_free_database_free_provider_free",
        "data_class": AUTHORED_SYNTHETIC_DATA_CLASS,
        "source_hashes": {
            "runtime": _sha256(RUNTIME_PATH),
            "plan": _sha256(PLAN_PATH),
            "threat_model_delta": _sha256(THREAT_MODEL_PATH),
            "parent_policy": _sha256(PARENT_POLICY_PATH),
        },
        "checks": checks,
        "sessions": sessions,
        "revocation": revocation,
        "cross_surface_exchange": exchange,
        "required_audit_failure": audit_failure,
        "static_boundary": static_boundary,
        "authority_and_side_effects": {
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
        },
        "claim_boundary": {
            "proves": [
                "An explicit authored-synthetic in-memory service enforces bounded opaque parent and surface sessions across all three surfaces.",
                "Explicit and generation revocation, time bounds and exact surface bindings fail closed.",
                "Word desktop and Word Online exchanges create one native-Diary binding under exact origin, audience, state, nonce, generation and S256-PKCE checks.",
                "Concurrent redemption admits exactly one consumer and required-audit failure leaves state unchanged.",
            ],
            "does_not_prove": [
                "A live login, route, cookie, database-backed or distributed session and revocation implementation.",
                "External identity or Microsoft/Office federation.",
                "Product-derived, patient, health or clinical data safety or authority.",
                "Deployment, production fitness or release readiness.",
            ],
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=EVIDENCE_PATH)
    args = parser.parse_args()
    evidence = run_acceptance()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(evidence, indent=2, sort_keys=True, default=_json_safe) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"output": str(args.output), "result": evidence["result"]}))
    return 0 if evidence["result"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = ["EVIDENCE_PATH", "run_acceptance"]
