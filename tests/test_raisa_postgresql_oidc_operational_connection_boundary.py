from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest
from cryptography.fernet import Fernet

from app.services.application_identity_oidc_attempt_database_role import (
    create_oidc_attempt_deployment_login_statements,
    require_oidc_attempt_login_role_identifier,
)
from app.services.application_identity_oidc_attempt_operational import (
    AuthorizationAttemptKeyReference,
    AuthorizationAttemptRuntimeKeyConfiguration,
    AuthorizationAttemptSecretReference,
    OIDCAttemptPoolPolicy,
    create_oidc_attempt_operational_engine,
    resolve_authorization_attempt_cryptography,
)


ROOT = Path(__file__).resolve().parents[1]
MODULE = (
    ROOT
    / "app"
    / "services"
    / "application_identity_oidc_attempt_operational.py"
)
ROLE_MODULE = (
    ROOT
    / "app"
    / "services"
    / "application_identity_oidc_attempt_database_role.py"
)
PLAN = ROOT / "docs" / "raisa-postgresql-oidc-operational-connection-boundary-plan.md"
DESIGN = (
    ROOT / "docs" / "raisa-postgresql-oidc-operational-connection-boundary-design.md"
)
THREAT = (
    ROOT
    / "docs"
    / "security"
    / "raisa-postgresql-oidc-operational-connection-boundary-threat-model-delta.md"
)
RUNNER = (
    ROOT
    / "scripts"
    / "raisa_postgresql_oidc_operational_connection_boundary_acceptance.py"
)
EVIDENCE = (
    ROOT
    / "orchestration"
    / "continuity"
    / "raisa-postgresql-oidc-operational-connection-boundary"
    / "live-local-backend-postgres-operational-evidence.json"
)
RECEIPT = (
    ROOT
    / "orchestration"
    / "agent_inbox"
    / "codex"
    / "raisa-postgresql-oidc-operational-connection-boundary-rehydration-receipt.json"
)
PREACCEPTANCE_RECEIPT = RECEIPT.with_name(
    "raisa-postgresql-oidc-operational-connection-boundary-preacceptance-receipt.json"
)
PREPUSH_RECEIPT = RECEIPT.with_name(
    "raisa-postgresql-oidc-operational-connection-boundary-prepush-receipt.json"
)
FIVE_SOURCES = {
    "live_handover_current_baton",
    "current_authority_allocation",
    "active_plan_and_acceptance",
    "protected_evidence_boundaries",
    "git_refs_and_worktree",
}


class _Provider:
    provider_namespace = "syntheticvault"

    def __init__(self, values: dict[str, bytes], *, fail: bool = False) -> None:
        self.values = values
        self.fail = fail
        self.calls: list[str] = []

    def resolve_bytes(self, reference: AuthorizationAttemptSecretReference) -> bytes:
        self.calls.append(reference.reference)
        if self.fail:
            raise RuntimeError(f"do not leak {reference.reference}")
        return self.values[reference.reference]


def _reference(key_id: str, suffix: str) -> AuthorizationAttemptKeyReference:
    return AuthorizationAttemptKeyReference(
        key_id=key_id,
        secret=AuthorizationAttemptSecretReference(
            provider_namespace="syntheticvault",
            reference=f"projects/synthetic/secrets/{suffix}/versions/1",
        ),
    )


def _configuration() -> AuthorizationAttemptRuntimeKeyConfiguration:
    return AuthorizationAttemptRuntimeKeyConfiguration(
        provider_namespace="syntheticvault",
        active_cipher_key_id="enc_v1",
        cipher_keys=(_reference("enc_v1", "enc-one"),),
        active_digest_key_id="dig_v1",
        digest_keys=(_reference("dig_v1", "dig-one"),),
    )


def _evidence() -> dict:
    return json.loads(EVIDENCE.read_text(encoding="utf-8"))


def test_login_contract_is_finite_inert_noinherit_and_membership_only() -> None:
    login = "emr4_oidc_attempt_login_synthetic01"
    capability = "emr4_oidc_attempt_runtime_synthetic01"
    statements = create_oidc_attempt_deployment_login_statements(
        login,
        capability,
        connection_limit=2,
    )
    assert statements == (
        'CREATE ROLE "emr4_oidc_attempt_login_synthetic01" LOGIN PASSWORD NULL '
        "NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOREPLICATION "
        "NOBYPASSRLS CONNECTION LIMIT 2",
        'GRANT "emr4_oidc_attempt_runtime_synthetic01" TO '
        '"emr4_oidc_attempt_login_synthetic01"',
    )
    serialized = "\n".join(statements)
    for forbidden in ("GRANT SELECT", "GRANT INSERT", "GRANT DELETE", "CREATE TABLE"):
        assert forbidden not in serialized


@pytest.mark.parametrize(
    "role",
    (
        "postgres",
        "emr4_oidc_attempt_runtime_synthetic01",
        "emr4_oidc_attempt_login_BADVALUE",
        'emr4_oidc_attempt_login_xxxxxxxx" SUPERUSER',
    ),
)
def test_login_identifier_is_exact_and_injection_safe(role: str) -> None:
    with pytest.raises(ValueError):
        require_oidc_attempt_login_role_identifier(role)


def test_pool_policy_rejects_unbounded_and_role_exceeding_values() -> None:
    with pytest.raises(ValueError):
        OIDCAttemptPoolPolicy(pool_size=0)
    with pytest.raises(ValueError):
        OIDCAttemptPoolPolicy(pool_size=3, max_overflow=2, login_connection_limit=4)
    policy = OIDCAttemptPoolPolicy(
        pool_size=2,
        max_overflow=1,
        pool_timeout_seconds=0.25,
        pool_recycle_seconds=60,
        login_connection_limit=3,
    )
    assert policy.pool_size + policy.max_overflow == policy.login_connection_limit


def test_pool_factory_rejects_target_role_and_session_option_bypass_before_connect() -> None:
    kwargs = {
        "login_role": "emr4_oidc_attempt_login_synthetic01",
        "capability_role": "emr4_oidc_attempt_runtime_synthetic01",
    }
    with pytest.raises(ValueError, match="PostgreSQL"):
        create_oidc_attempt_operational_engine("sqlite:///synthetic.db", **kwargs)
    with pytest.raises(ValueError, match="exact OIDC attempt LOGIN"):
        create_oidc_attempt_operational_engine(
            "postgresql://postgres@127.0.0.1:5434/synthetic",
            **kwargs,
        )
    with pytest.raises(ValueError, match="prohibited session option"):
        create_oidc_attempt_operational_engine(
            "postgresql://emr4_oidc_attempt_login_synthetic01@127.0.0.1:5434/"
            "synthetic?options=-c%20role%3Dpostgres",
            **kwargs,
        )


def test_secret_configuration_contains_references_not_material_and_is_bounded() -> None:
    configuration = _configuration()
    assert configuration.active_cipher_key_id == "enc_v1"
    assert configuration.active_digest_key_id == "dig_v1"
    assert not any(isinstance(value, bytes) for value in configuration.__dict__.values())
    with pytest.raises(ValueError):
        AuthorizationAttemptSecretReference(
            provider_namespace="syntheticvault",
            reference="https://secret.invalid/raw=value",
        )
    duplicated = _reference("dig_v1", "enc-one")
    with pytest.raises(ValueError, match="references must be unique"):
        AuthorizationAttemptRuntimeKeyConfiguration(
            provider_namespace="syntheticvault",
            active_cipher_key_id="enc_v1",
            cipher_keys=(_reference("enc_v1", "enc-one"),),
            active_digest_key_id="dig_v1",
            digest_keys=(duplicated,),
        )


def test_key_provider_resolves_exact_material_and_rejects_cross_use() -> None:
    configuration = _configuration()
    enc_ref = configuration.cipher_keys[0].secret.reference
    dig_ref = configuration.digest_keys[0].secret.reference
    provider = _Provider(
        {
            enc_ref: Fernet.generate_key(),
            dig_ref: b"d" * 32,
        }
    )
    resolved = resolve_authorization_attempt_cryptography(configuration, provider)
    envelope = resolved.cipher.encrypt(b"authored-synthetic-attempt")
    assert resolved.cipher.decrypt(
        key_id=envelope.key_id,
        ciphertext=envelope.ciphertext,
    ) == b"authored-synthetic-attempt"
    assert provider.calls == [enc_ref, dig_ref]

    shared = b"x" * 44
    with pytest.raises(ValueError, match="must be separate"):
        resolve_authorization_attempt_cryptography(
            configuration,
            _Provider({enc_ref: shared, dig_ref: shared}),
        )

    duplicate_configuration = AuthorizationAttemptRuntimeKeyConfiguration(
        provider_namespace="syntheticvault",
        active_cipher_key_id="enc_v1",
        cipher_keys=(
            _reference("enc_v1", "enc-one"),
            _reference("enc_v2", "enc-two"),
        ),
        active_digest_key_id="dig_v1",
        digest_keys=(_reference("dig_v1", "dig-one"),),
    )
    duplicate_cipher = Fernet.generate_key()
    duplicate_references = {
        item.key_id: item.secret.reference
        for item in duplicate_configuration.cipher_keys
    }
    duplicate_digest_ref = duplicate_configuration.digest_keys[0].secret.reference
    with pytest.raises(ValueError, match="material is duplicated"):
        resolve_authorization_attempt_cryptography(
            duplicate_configuration,
            _Provider(
                {
                    duplicate_references["enc_v1"]: duplicate_cipher,
                    duplicate_references["enc_v2"]: duplicate_cipher,
                    duplicate_digest_ref: b"z" * 32,
                }
            ),
        )


def test_key_provider_failure_is_fixed_and_does_not_echo_reference() -> None:
    configuration = _configuration()
    reference = configuration.cipher_keys[0].secret.reference
    with pytest.raises(ValueError) as exc_info:
        resolve_authorization_attempt_cryptography(
            configuration,
            _Provider({}, fail=True),
        )
    assert str(exc_info.value) == "authorization-attempt secret resolution failed"
    assert reference not in str(exc_info.value)


def test_operational_module_is_dormant_route_free_and_has_verified_reset() -> None:
    source = MODULE.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported_roots = {
        alias.name.split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in node.names
    }
    assert imported_roots.isdisjoint({"fastapi", "msal", "authlib", "requests", "httpx"})
    assert '@event.listens_for(engine, "checkout")' in source
    assert '@event.listens_for(engine, "reset")' in source
    assert "RESET ROLE" in source
    assert "RESET ALL" in source
    assert "pool_reset_on_return=None" in source
    combined_application = "\n".join(
        path.read_text(encoding="utf-8")
        for path in [ROOT / "app" / "main.py", *(ROOT / "app" / "routers").glob("*.py")]
    )
    assert "application_identity_oidc_attempt_operational" not in combined_application


def test_live_local_operational_evidence_passes_and_proves_cleanup() -> None:
    evidence = _evidence()
    assert evidence["result"] == "postgresql_oidc_operational_connection_boundary_pass"
    assert evidence["passed"] is True
    assert evidence["evidence_label"] == "live_local_backend_postgres"
    assert evidence["direct_login_denial"] == {
        "passed": True,
        "select_sqlstate": "42501",
    }
    assert evidence["cleanup"]["passed"] is True
    assert evidence["cleanup"]["database_absent_after"] is True
    assert evidence["cleanup"]["login_role_absent_after"] is True
    assert evidence["cleanup"]["capability_role_absent_after"] is True


def test_live_pool_reset_exhaustion_rotation_and_residue_proofs_pass() -> None:
    evidence = _evidence()
    runtime = evidence["operational_runtime"]
    for field in (
        "session_and_effective_roles_exact",
        "physical_connection_reused",
        "settings_restored_after_committed_contamination",
        "checkin_reset_observed",
        "checkout_timeout_observed",
        "checkout_timeout_within_bound",
        "key_resolution_sequence_exact",
        "fresh_runtime_consumed_retained_keys",
    ):
        assert runtime[field] is True
    assert runtime["pool_size"] + runtime["max_overflow"] <= runtime[
        "login_connection_limit"
    ]
    assert runtime["unique_secret_reference_count"] == 4
    assert evidence["raw_residue_scan"]["active_encrypted_row_present"] is True
    assert evidence["raw_residue_scan"]["matched_sensitive_value_count"] == 0
    assert evidence["evidence_sensitive_match_count"] == 0


def test_plan_threat_runner_and_receipt_preserve_closed_boundary() -> None:
    combined = "\n".join(
        path.read_text(encoding="utf-8") for path in (PLAN, DESIGN, THREAT, RUNNER)
    ).lower()
    for required in (
        "password null",
        "noinherit",
        "reset role",
        "reset all",
        "provider-free",
        "product read",
        "protected integration",
        "deployment",
        "production",
        "release",
    ):
        assert required in combined
    role_source = ROLE_MODULE.read_text(encoding="utf-8")
    assert "CONNECTION LIMIT" in role_source
    for receipt_path in (RECEIPT, PREACCEPTANCE_RECEIPT, PREPUSH_RECEIPT):
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        assert receipt["status"] == "passed"
        assert receipt["rehydrated_from_receipt"] is True
        assert set(receipt["rehydration_sources"]) == FIVE_SOURCES
        assert set(receipt["source_evidence"]) == FIVE_SOURCES
