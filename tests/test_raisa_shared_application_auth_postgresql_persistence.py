"""Acceptance for the bounded authored-synthetic PostgreSQL auth tranche."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

from app.models.application_auth import (
    ApplicationAuthAuditEvent,
    ApplicationAuthExchangeGrant,
    ApplicationAuthParentSession,
    ApplicationAuthPrincipalGeneration,
    ApplicationAuthSurfaceSession,
)


ROOT = Path(__file__).resolve().parents[1]
RUNNER_PATH = (
    ROOT
    / "scripts"
    / "raisa_shared_application_auth_postgresql_persistence_acceptance.py"
)
EVIDENCE_PATH = (
    ROOT
    / "orchestration"
    / "continuity"
    / "raisa-shared-application-auth-postgresql-persistence"
    / "live-local-backend-postgres-evidence.json"
)
PLAN_PATH = ROOT / "docs" / "raisa-shared-application-auth-postgresql-persistence-plan.md"
THREAT_PATH = (
    ROOT
    / "docs"
    / "security"
    / "raisa-shared-application-auth-postgresql-persistence-threat-model-delta.md"
)
RECEIPT_PATH = (
    ROOT
    / "orchestration"
    / "agent_inbox"
    / "codex"
    / "raisa-shared-application-auth-postgresql-persistence-postcompaction-receipt.json"
)
MIGRATION_PATH = (
    ROOT
    / "alembic"
    / "versions"
    / "o4p5q6r7s8t9_add_application_auth_persistence.py"
)
MODEL_PATH = ROOT / "app" / "models" / "application_auth.py"
SERVICE_PATH = ROOT / "app" / "services" / "application_auth_persistence.py"
CLOSEOUT_PATH = (
    ROOT / "docs" / "raisa-shared-application-auth-postgresql-persistence-closeout.md"
)
ACCEPTANCE_PATH = (
    ROOT
    / "orchestration"
    / "agent_inbox"
    / "codex"
    / "raisa-shared-application-auth-postgresql-persistence-sol-acceptance.md"
)
GRAPH_PATH = ROOT / "orchestration" / "continuity" / "emr4-continuity-graph.json"
COMPASS_PATH = ROOT / "orchestration" / "continuity" / "emr4-compass.json"
COMPASS_REPORT_PATH = ROOT / "docs" / "ariadne-compass-current.md"
TABLE_NAMES = {
    "application_auth_principal_generations",
    "application_auth_parent_sessions",
    "application_auth_surface_sessions",
    "application_auth_exchange_grants",
    "application_auth_audit_events",
}
FIVE_SOURCES = {
    "live_handover_current_baton",
    "current_authority_allocation",
    "active_plan_and_acceptance",
    "protected_evidence_boundaries",
    "git_refs_and_worktree",
}


def _load_runner():
    spec = importlib.util.spec_from_file_location(
        "raisa_shared_auth_postgresql_acceptance", RUNNER_PATH
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def disposable_acceptance() -> dict[str, object]:
    return _load_runner().run_acceptance(output_path=None)


def test_exact_five_table_model_boundary() -> None:
    models = (
        ApplicationAuthPrincipalGeneration,
        ApplicationAuthParentSession,
        ApplicationAuthSurfaceSession,
        ApplicationAuthExchangeGrant,
        ApplicationAuthAuditEvent,
    )
    assert {model.__tablename__ for model in models} == TABLE_NAMES
    assert all(model.__table__.schema is None for model in models)


def test_models_are_hash_only_synthetic_and_product_detached() -> None:
    source = MODEL_PATH.read_text(encoding="utf-8")
    assert "^synthetic-[a-z0-9-]{1,64}$" in source
    assert "^sha256:[0-9a-f]{64}$" in source
    assert "authored_synthetic" in source
    for forbidden_table in (
        "users.",
        "practices.",
        "practitioners.",
        "patients.",
        "appointments.",
        "consultations.",
    ):
        assert forbidden_table not in source


def test_migration_is_reversible_single_head_descendant() -> None:
    source = MIGRATION_PATH.read_text(encoding="utf-8")
    assert 'revision: str = "o4p5q6r7s8t9"' in source
    assert 'down_revision: Union[str, Sequence[str], None] = "n3o4p5q6r7s8"' in source
    assert "def upgrade()" in source
    assert "def downgrade()" in source
    assert 'ALTER TABLE "{table_name}" FORCE ROW LEVEL SECURITY' in source
    assert (
        'ALTER TABLE "application_auth_audit_events" FORCE ROW LEVEL SECURITY'
        in source
    )
    assert 'ALTER TABLE "{table_name}" NO FORCE ROW LEVEL SECURITY' in source
    assert "trg_application_auth_audit_append_only" in source
    assert "trg_application_auth_generation_monotonic" in source
    assert "trg_application_auth_exchange_consumption_terminal" in source


def test_persistence_adapter_remains_unmounted_and_provider_free() -> None:
    source = SERVICE_PATH.read_text(encoding="utf-8")
    assert "ApplicationAuthRuntime" in source
    assert "PostgresApplicationAuthRuntime" in source
    for forbidden in (
        "fastapi",
        "APIRouter",
        "Cookie",
        "Set-Cookie",
        "requests",
        "httpx",
        "socket",
        "subprocess",
        "google.cloud",
        "vertexai",
        "OfficeRuntime",
        "Microsoft Graph",
    ):
        assert forbidden not in source


def test_no_router_imports_the_persistence_adapter() -> None:
    router_sources = "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted((ROOT / "app" / "routers").glob("*.py"))
    )
    assert "application_auth_persistence" not in router_sources
    assert "PostgresApplicationAuthRuntime" not in router_sources


def test_five_source_postcompaction_receipt_passes() -> None:
    receipt = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))
    assert receipt["status"] == "passed"
    assert receipt["rehydrated_from_receipt"] is True
    assert set(receipt["rehydration_sources"]) == FIVE_SOURCES
    assert receipt["worker_dispatch_permitted"] is False
    git_state = receipt["source_evidence"]["git_refs_and_worktree"]
    assert git_state["HEAD"] == "8fa732592fbee4f57c322b13d9d8ff89fcc7fa33"
    assert git_state["protected_refs_unchanged_after_fetch"] is True


def test_plan_and_threat_model_preserve_closed_boundaries() -> None:
    combined = PLAN_PATH.read_text(encoding="utf-8") + THREAT_PATH.read_text(
        encoding="utf-8"
    )
    for required in (
        "disposable authored-synthetic",
        "single-use exchange",
        "metadata-only audit",
        "row-level security",
        "routes",
        "cookies",
        "product-derived",
        "production",
        "release",
    ):
        assert required in combined
    assert "Version: 8fa732592fbee4f57c322b13d9d8ff89fcc7fa33" in combined


def test_live_local_postgresql_acceptance_passes(
    disposable_acceptance: dict[str, object],
) -> None:
    assert disposable_acceptance["passed"] is True
    assert (
        disposable_acceptance["result"]
        == "raisa_shared_application_auth_postgresql_persistence_pass"
    )
    assert disposable_acceptance["evidence_label"] == "live_local_backend_postgres"
    assert disposable_acceptance["cleanup"]["database_absent_after"] is True


def test_database_single_use_audit_and_rls_gates_pass(
    disposable_acceptance: dict[str, object],
) -> None:
    runtime = disposable_acceptance["runtime"]
    assert runtime["concurrency"]["exactly_one_consumer"] is True
    assert runtime["audit_atomicity"]["state_and_audit_unchanged"] is True
    assert runtime["postgres_guards"]["passed"] is True
    assert runtime["rls"]["passed"] is True
    assert runtime["raw_secret_scan"]["matched_raw_value_count"] == 0


def test_migration_and_orm_contract_passes(
    disposable_acceptance: dict[str, object],
) -> None:
    migration = disposable_acceptance["migration"]
    assert migration["upgrade_passed"] is True
    assert migration["downgrade_passed"] is True
    assert migration["reupgrade_passed"] is True
    assert migration["current_head_exact"] is True
    assert migration["orm_migration_drift_absent"] is True
    schema = disposable_acceptance["schema_contract"]
    assert schema["forced_rls_table_count"] == 5
    assert schema["policy_count"] == 6
    assert all(schema["model_database_column_matches"].values())


def test_recorded_evidence_is_bounded_and_clean() -> None:
    evidence = json.loads(EVIDENCE_PATH.read_text(encoding="utf-8"))
    serialized = json.dumps(evidence, sort_keys=True)
    assert evidence["passed"] is True
    assert evidence["database"]["name_recorded"] is False
    assert evidence["cleanup"]["database_absent_after"] is True
    assert "postgresql://" not in serialized
    assert "gp_pms_dev" not in serialized
    assert "gp_pms_test" not in serialized
    side_effects = evidence["side_effect_counts"]
    for key, value in side_effects.items():
        if key.startswith("database_"):
            continue
        assert value == 0


def test_closeout_continuity_and_compass_bind_persistence_pass() -> None:
    result = "raisa_shared_application_auth_postgresql_persistence_pass"
    graph = json.loads(GRAPH_PATH.read_text(encoding="utf-8"))
    compass = json.loads(COMPASS_PATH.read_text(encoding="utf-8"))
    node = next(
        item
        for item in graph["nodes"]
        if item["id"] == "raisa-shared-application-auth-postgresql-persistence"
    )
    assert graph["graph_revision"] == 183
    assert node["status"] == "accepted"
    assert node["relationships"] == [
        {
            "node_id": "raisa-shared-application-auth-runtime-foundation",
            "relation": "builds_on",
        }
    ]
    assert compass["map_revision"] == 164
    assert compass["source_graph_revision"] == 183
    assert compass["current_position"]["node_id"] == node["id"]
    assert "shared-application-auth-postgresql-persistence" not in {
        item["id"] for item in compass["decision_horizon"]
    }
    assert "shared-application-auth-runtime-role-secure-transport" in {
        item["id"] for item in compass["decision_horizon"]
    }
    assert result in CLOSEOUT_PATH.read_text(encoding="utf-8")
    assert result in ACCEPTANCE_PATH.read_text(encoding="utf-8")
    report = COMPASS_REPORT_PATH.read_text(encoding="utf-8")
    assert "Compass map revision 164" in report
    assert "continuity graph revision 183" in report
