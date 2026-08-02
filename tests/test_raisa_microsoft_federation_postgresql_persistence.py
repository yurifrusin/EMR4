from __future__ import annotations

import ast
import json
from pathlib import Path

from alembic.config import Config
from alembic.script import ScriptDirectory

from app.models.application_identity_federation import (
    ApplicationIdentityFederationAuditEvent,
    ApplicationIdentityFederationBinding,
)
from app.services.application_identity_federation import FederationReferenceHasher


ROOT = Path(__file__).resolve().parents[1]
MIGRATION = (
    ROOT
    / "alembic"
    / "versions"
    / "q6r7s8t9u0v1_add_application_identity_federation_persistence.py"
)
MODEL = ROOT / "app" / "models" / "application_identity_federation.py"
SERVICE = (
    ROOT / "app" / "services" / "application_identity_federation_persistence.py"
)
RUNNER = (
    ROOT
    / "scripts"
    / "raisa_microsoft_federation_postgresql_persistence_acceptance.py"
)
PLAN = ROOT / "docs" / "raisa-microsoft-federation-postgresql-persistence-plan.md"
THREAT = (
    ROOT
    / "docs"
    / "security"
    / "raisa-microsoft-federation-postgresql-persistence-threat-model-delta.md"
)
EVIDENCE = (
    ROOT
    / "orchestration"
    / "continuity"
    / "raisa-microsoft-federation-postgresql-persistence"
    / "live-local-backend-postgres-evidence.json"
)
TABLE_NAMES = {
    "application_identity_federation_bindings",
    "application_identity_federation_audit_events",
}


def _evidence() -> dict:
    return json.loads(EVIDENCE.read_text(encoding="utf-8"))


def test_exact_two_table_detached_model_boundary() -> None:
    models = (
        ApplicationIdentityFederationBinding,
        ApplicationIdentityFederationAuditEvent,
    )
    assert {model.__tablename__ for model in models} == TABLE_NAMES
    assert all(model.__table__.schema is None for model in models)
    source = MODEL.read_text(encoding="utf-8")
    assert "hmac-sha256:synthetic-v1" in source
    assert "authored_synthetic" in source
    for forbidden in (
        "access_token",
        "id_token",
        "refresh_token",
        "authorization_code",
        "email = Column",
        "name = Column",
        "users.",
        "practices.",
        "practitioners.",
        "patients.",
        "appointments.",
    ):
        assert forbidden not in source


def test_migration_is_reversible_single_head_descendant() -> None:
    source = MIGRATION.read_text(encoding="utf-8")
    assert 'revision: str = "q6r7s8t9u0v1"' in source
    assert 'down_revision: Union[str, Sequence[str], None] = "p5q6r7s8t9u0"' in source
    assert "def upgrade()" in source
    assert "def downgrade()" in source
    assert "FORCE ROW LEVEL SECURITY" in source
    assert "trg_app_id_fed_audit_append_only" in source
    assert "trg_app_id_fed_binding_terminal" in source
    assert "GRANT" not in source
    config = Config(str(ROOT / "alembic.ini"))
    script = ScriptDirectory.from_config(config)
    heads = script.get_heads()
    assert len(heads) == 1
    assert "q6r7s8t9u0v1" in {
        revision.revision for revision in script.walk_revisions()
    }


def test_repository_is_route_free_and_has_no_network_or_product_import() -> None:
    tree = ast.parse(SERVICE.read_text(encoding="utf-8"))
    imported = {
        alias.name.split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in node.names
    }
    assert imported.isdisjoint(
        {
            "requests",
            "httpx",
            "socket",
            "fastapi",
            "msal",
            "jwt",
            "subprocess",
        }
    )
    router_source = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (ROOT / "app" / "routers").rglob("*.py")
    )
    assert "application_identity_federation_persistence" not in router_source
    assert "PostgresFederationBindingRepository" not in router_source


def test_keyed_component_references_are_domain_separated() -> None:
    hasher = FederationReferenceHasher(
        b"authored-synthetic-persistence-hmac-key-000000000001"
    )
    tenant = hasher.component_reference(
        label="tenant", value="synthetic-tenant-001"
    )
    subject = hasher.component_reference(
        label="subject", value="synthetic-tenant-001"
    )
    assert tenant != subject
    assert tenant.startswith("hmac-sha256:synthetic-v1:")
    assert "synthetic-tenant-001" not in tenant


def test_recorded_disposable_postgresql_acceptance_passes_and_cleans_up() -> None:
    evidence = _evidence()
    assert evidence["passed"] is True
    assert (
        evidence["result"]
        == "raisa_microsoft_federation_postgresql_persistence_pass"
    )
    assert evidence["evidence_label"] == "live_local_backend_postgres"
    assert evidence["database"]["name_recorded"] is False
    assert evidence["cleanup"]["exact_database_drop_attempted"] is True
    assert evidence["cleanup"]["database_absent_after"] is True


def test_migration_schema_rls_and_trigger_contract_passes() -> None:
    evidence = _evidence()
    migration = evidence["migration"]
    assert migration["base_revision"] == "p5q6r7s8t9u0"
    assert migration["head_revision"] == "q6r7s8t9u0v1"
    assert migration["upgrade_passed"] is True
    assert migration["downgrade_passed"] is True
    assert migration["reupgrade_passed"] is True
    assert migration["current_head_exact"] is True
    assert migration["orm_migration_drift_absent"] is True
    schema = evidence["schema_contract"]
    assert schema["table_count"] == 2
    assert set(schema["forced_rls"]) == TABLE_NAMES
    assert set(schema["forced_rls"].values()) == {True}
    assert schema["policy_count"] == 3
    assert all(schema["model_database_column_matches"].values())


def test_uniqueness_revocation_audit_atomicity_and_guards_pass() -> None:
    runtime = _evidence()["runtime"]
    assert runtime["durability"]["resolved_after_fresh_repository"] is True
    assert runtime["durability"]["revoked_version"] == 2
    assert runtime["durability"]["resolution_denied_after_revoke"] is True
    assert runtime["concurrency"]["exactly_one_binding_created"] is True
    assert runtime["concurrency"]["results"] == ["binding_conflict", "created"]
    assert runtime["audit_atomicity"]["failure_reason"] == "required_audit_unavailable"
    assert runtime["audit_atomicity"]["state_and_audit_unchanged"] is True
    assert runtime["postgres_guards"]["passed"] is True
    assert set(runtime["postgres_guards"]["sqlstates"].values()) == {"55000"}


def test_rls_and_raw_identity_non_leakage_pass() -> None:
    runtime = _evidence()["runtime"]
    assert runtime["rls"]["passed"] is True
    assert set(runtime["rls"]["without_context"].values()) == {0}
    assert runtime["rls"]["foreign_binding_rows_visible"] == 0
    assert runtime["rls"]["role_absent_after_rollback"] is True
    assert runtime["raw_identity_scan"]["matched_raw_value_count"] == 0
    serialized = json.dumps(_evidence(), sort_keys=True)
    assert "postgresql://" not in serialized
    assert "gp_pms_dev" not in serialized
    assert "synthetic-tenant-001" not in serialized


def test_only_disposable_database_side_effects_are_nonzero() -> None:
    side_effects = _evidence()["side_effect_counts"]
    for key, value in side_effects.items():
        if key.startswith("database_"):
            continue
        assert value == 0


def test_plan_threat_and_runner_preserve_exact_closed_boundary() -> None:
    combined = "\n".join(
        path.read_text(encoding="utf-8") for path in (PLAN, THREAT, RUNNER)
    ).lower()
    for required in (
        "disposable",
        "authored-synthetic",
        "keyed hmac",
        "row-level security",
        "append-only",
        "no durable role",
        "product read",
        "deployment",
        "production",
        "release",
    ):
        assert required in combined
