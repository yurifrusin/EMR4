from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest
from alembic.config import Config
from alembic.script import ScriptDirectory
from cryptography.fernet import Fernet

from app.models.application_identity_oidc_attempt import (
    ApplicationIdentityOIDCAuthorizationAttempt,
)
from app.services.application_identity_oidc_adapter import (
    AuthorizationAttemptStore,
    EncryptedAuthorizationAttemptStore,
    OIDCTemporarilyUnavailable,
)
from app.services.application_identity_oidc_attempt_database_role import (
    ATTEMPT_TABLE,
    create_oidc_attempt_runtime_role_statements,
    require_oidc_attempt_runtime_role_identifier,
)
from app.services.application_identity_oidc_attempt_store import (
    AuthorizationAttemptDigestKeyring,
    ENVELOPE_VERSION,
    FernetAuthorizationAttemptCipher,
)


ROOT = Path(__file__).resolve().parents[1]
MIGRATION = (
    ROOT
    / "alembic"
    / "versions"
    / "r7s8t9u0v1w2_add_oidc_authorization_attempt_store.py"
)
MODEL = ROOT / "app" / "models" / "application_identity_oidc_attempt.py"
STORE = ROOT / "app" / "services" / "application_identity_oidc_attempt_store.py"
ROLE = (
    ROOT
    / "app"
    / "services"
    / "application_identity_oidc_attempt_database_role.py"
)
ADAPTER = ROOT / "app" / "services" / "application_identity_oidc_adapter.py"
RUNNER = (
    ROOT
    / "scripts"
    / "raisa_postgresql_oidc_authorization_attempt_store_acceptance.py"
)
PLAN = ROOT / "docs" / "raisa-postgresql-oidc-authorization-attempt-store-plan.md"
DESIGN = ROOT / "docs" / "raisa-postgresql-oidc-authorization-attempt-store-design.md"
THREAT = (
    ROOT
    / "docs"
    / "security"
    / "raisa-postgresql-oidc-authorization-attempt-store-threat-model-delta.md"
)
EVIDENCE = (
    ROOT
    / "orchestration"
    / "continuity"
    / "raisa-postgresql-oidc-authorization-attempt-store"
    / "live-local-backend-postgres-evidence.json"
)


def _evidence() -> dict:
    return json.loads(EVIDENCE.read_text(encoding="utf-8"))


def test_adapter_uses_structural_attempt_store_port() -> None:
    source = ADAPTER.read_text(encoding="utf-8")
    assert "class AuthorizationAttemptStore(Protocol)" in source
    assert "attempt_store: AuthorizationAttemptStore" in source
    assert "attempt_store: EncryptedAuthorizationAttemptStore" not in source
    assert AuthorizationAttemptStore is not EncryptedAuthorizationAttemptStore


def test_single_encrypted_attempt_table_has_no_identity_or_token_columns() -> None:
    model = ApplicationIdentityOIDCAuthorizationAttempt
    assert model.__tablename__ == ATTEMPT_TABLE
    assert {column.name for column in model.__table__.columns} == {
        "state_reference_hmac",
        "nonce_reference_hmac",
        "cipher_key_id",
        "ciphertext",
        "envelope_version",
        "created_at",
        "expires_at",
        "data_class",
    }
    source = MODEL.read_text(encoding="utf-8")
    for forbidden in (
        "access_token",
        "refresh_token",
        "authorization_code",
        "tenant_id",
        "object_id",
        "subject",
        "email",
        "binding",
        "practice",
        "session",
        "patient",
        "appointment",
    ):
        assert forbidden not in source.lower()


def test_migration_is_reversible_forced_rls_single_head_descendant() -> None:
    source = MIGRATION.read_text(encoding="utf-8")
    assert 'revision: str = "r7s8t9u0v1w2"' in source
    assert 'down_revision: Union[str, Sequence[str], None] = "q6r7s8t9u0v1"' in source
    assert "FORCE ROW LEVEL SECURITY" in source
    assert source.count("CREATE POLICY app_id_oidc_attempt_runtime_") == 3
    assert "FOR UPDATE" not in source
    assert "GRANT" not in source
    assert "def downgrade()" in source
    config = Config(str(ROOT / "alembic.ini"))
    script = ScriptDirectory.from_config(config)
    heads = script.get_heads()
    assert len(heads) == 1
    lineage = {
        revision.revision
        for revision in script.walk_revisions(base="r7s8t9u0v1w2", head=heads[0])
    }
    assert "r7s8t9u0v1w2" in lineage


def test_capability_role_has_only_exact_attempt_table_privileges() -> None:
    role_name = "emr4_oidc_attempt_runtime_synthetic001"
    assert require_oidc_attempt_runtime_role_identifier(role_name) == role_name
    statements = create_oidc_attempt_runtime_role_statements(role_name)
    joined = "\n".join(statements)
    assert "NOLOGIN" in joined
    assert "NOINHERIT" in joined
    assert "NOBYPASSRLS" in joined
    assert "SELECT, INSERT, DELETE" in joined
    assert "UPDATE" not in joined
    assert "SEQUENCE" not in joined
    assert "FUNCTION" not in joined
    assert joined.count(ATTEMPT_TABLE) == 2
    with pytest.raises(ValueError):
        require_oidc_attempt_runtime_role_identifier("postgres")


def test_cipher_and_digest_keyrings_are_versioned_bounded_and_fail_closed() -> None:
    old_cipher = Fernet.generate_key()
    new_cipher = Fernet.generate_key()
    cipher = FernetAuthorizationAttemptCipher(
        active_key_id="enc-v2",
        keys={"enc-v1": old_cipher, "enc-v2": new_cipher},
    )
    encrypted = cipher.encrypt(b"authored-synthetic-flow")
    assert encrypted.key_id == "enc-v2"
    assert b"authored-synthetic-flow" not in encrypted.ciphertext
    assert (
        cipher.decrypt(key_id=encrypted.key_id, ciphertext=encrypted.ciphertext)
        == b"authored-synthetic-flow"
    )
    with pytest.raises(OIDCTemporarilyUnavailable) as unknown:
        cipher.decrypt(key_id="enc-v3", ciphertext=encrypted.ciphertext)
    assert unknown.value.reason_code == "authorization_attempt_key_unavailable"

    digests = AuthorizationAttemptDigestKeyring(
        active_key_id="dig-v2",
        keys={"dig-v1": b"a" * 32, "dig-v2": b"b" * 32},
    )
    state = digests.lookup_references(label="state", value="opaque-state-value")
    nonce = digests.lookup_references(label="nonce", value="opaque-state-value")
    assert len(state) == len(nonce) == 2
    assert set(state).isdisjoint(nonce)
    assert state[0].startswith("hmac-sha256:dig-v2:")
    with pytest.raises(ValueError):
        AuthorizationAttemptDigestKeyring(
            active_key_id="dig-v5",
            keys={f"dig-v{index}": bytes([index]) * 32 for index in range(1, 6)},
        )


def test_store_module_is_route_free_provider_free_and_product_detached() -> None:
    tree = ast.parse(STORE.read_text(encoding="utf-8"))
    imported_roots = {
        alias.name.split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in node.names
    }
    assert imported_roots.isdisjoint(
        {"requests", "httpx", "socket", "fastapi", "msal", "jwt"}
    )
    combined_runtime = "\n".join(
        path.read_text(encoding="utf-8")
        for path in [ROOT / "app" / "main.py", *(ROOT / "app" / "routers").rglob("*.py")]
    )
    assert "application_identity_oidc_attempt_store" not in combined_runtime
    assert "PostgresAuthorizationAttemptStore" not in combined_runtime


def test_recorded_disposable_postgresql_acceptance_passes_and_cleans_up() -> None:
    evidence = _evidence()
    assert evidence["result"] == "postgresql_oidc_authorization_attempt_store_pass"
    assert evidence["passed"] is True
    assert evidence["evidence_label"] == "live_local_backend_postgres"
    assert evidence["database"]["name_recorded"] is False
    assert evidence["cleanup"]["database_absent_after"] is True
    assert evidence["cleanup"]["role_absent_after"] is True
    assert evidence["cleanup"]["role_name_recorded"] is False


def test_schema_role_rls_and_raw_residue_acceptance_pass() -> None:
    evidence = _evidence()
    schema = evidence["schema_and_role_contract"]
    assert schema["passed"] is True
    assert schema["forced_rls"] is True
    assert schema["capability_privileges"] == ["DELETE", "INSERT", "SELECT"]
    assert schema["public_select"] is False
    assert schema["session_and_effective_role_separated"] is True
    rls = evidence["rls_and_privilege_probe"]
    assert rls["passed"] is True
    assert rls["outsider_visible_rows"] == 0
    assert rls["outsider_insert_sqlstate"] == "42501"
    assert rls["capability_update_sqlstate"] == "42501"
    residue = evidence["raw_residue_scan"]
    assert residue["active_encrypted_row_present"] is True
    assert residue["matched_sensitive_value_count"] == 0
    assert residue["passed"] is True


def test_atomic_consume_expiry_capacity_rotation_and_tamper_pass() -> None:
    runtime = _evidence()["runtime"]
    assert runtime["passed"] is True
    assert runtime["adapter_concurrency"]["results"] == [
        "authorization_attempt_required",
        "synthetic-object-verified",
    ]
    assert runtime["adapter_concurrency"]["exactly_one_exchange"] is True
    assert runtime["adapter_concurrency"]["exactly_one_verification"] is True
    assert runtime["expiry"] == {
        "boundary_reason": "authorization_attempt_expired",
        "replay_reason": "authorization_attempt_required",
    }
    assert runtime["capacity_and_discard"] == {
        "capacity_reason": "authorization_attempt_capacity",
        "active_after_expiry_purge": 1,
        "active_after_discard": 0,
    }
    assert runtime["collision_reason"] == "authorization_state_collision"
    assert runtime["key_rotation"]["retained_cipher_and_digest_consumed"] is True
    assert runtime["key_rotation"]["missing_cipher_reason"] == (
        "authorization_attempt_key_unavailable"
    )
    assert runtime["tamper"] == {
        "reason": "authorization_attempt_unreadable",
        "replay_reason": "authorization_attempt_required",
    }
    assert runtime["audit_cleanup"]["provider_exchange_count"] == 0


def test_evidence_has_no_database_url_role_name_or_sensitive_value() -> None:
    serialized = json.dumps(_evidence(), sort_keys=True)
    for forbidden in (
        "postgresql://",
        "gp_pms_dev",
        "emr4_oidc_attempt_runtime_",
        "state-0000000000000700",
        "nonce-00000000000000000000000700",
        "verifier-00000000000000000000000000000700",
        "synthetic.raw.id.token",
    ):
        assert forbidden not in serialized


def test_plan_design_threat_and_runner_preserve_closed_boundary() -> None:
    combined = "\n".join(
        path.read_text(encoding="utf-8") for path in (PLAN, DESIGN, THREAT, RUNNER)
    ).lower()
    for required in (
        "delete ... returning",
        "authored-synthetic",
        "forced rls",
        "nologin",
        "provider-free",
        "product read",
        "protected integration",
        "deployment",
        "production",
        "release",
    ):
        assert required in combined
    assert ENVELOPE_VERSION in MODEL.read_text(encoding="utf-8")
    assert "CREATE ROLE" in ROLE.read_text(encoding="utf-8")
