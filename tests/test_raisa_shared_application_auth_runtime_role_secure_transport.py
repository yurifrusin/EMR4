"""Acceptance for the authorised shared-auth runtime-role/transport tranche."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest
import yaml

from app.schemas.application_auth_transport import (
    ExchangeIssueRequest,
    ExchangeRedeemRequest,
)
from app.services.application_auth_database_role import (
    AUDIT_SEQUENCE,
    AUDIT_TABLE,
    RESOLVER_SIGNATURE,
    STATE_TABLES,
    create_runtime_role_statements,
)


ROOT = Path(__file__).resolve().parents[1]
PLAN_PATH = (
    ROOT
    / "docs"
    / "raisa-shared-application-auth-runtime-role-secure-transport-plan.md"
)
THREAT_PATH = (
    ROOT
    / "docs"
    / "security"
    / "raisa-shared-application-auth-runtime-role-secure-transport-threat-model-delta.md"
)
OPENAPI_PATH = (
    ROOT
    / "docs"
    / "api-spine"
    / "openapi"
    / "application-auth-synthetic-transport.yaml"
)
MIGRATION_PATH = (
    ROOT
    / "alembic"
    / "versions"
    / "p5q6r7s8t9u0_add_application_auth_runtime_bootstrap.py"
)
ROLE_PATH = ROOT / "app" / "services" / "application_auth_database_role.py"
ROLE_RUNTIME_PATH = ROOT / "app" / "services" / "application_auth_role_runtime.py"
TRANSPORT_PATH = ROOT / "app" / "services" / "application_auth_transport.py"
ROUTER_PATH = ROOT / "app" / "routers" / "application_auth.py"
MAIN_PATH = ROOT / "app" / "main.py"
RUNNER_PATH = (
    ROOT
    / "scripts"
    / "raisa_shared_application_auth_runtime_role_secure_transport_acceptance.py"
)
EVIDENCE_PATH = (
    ROOT
    / "orchestration"
    / "continuity"
    / "raisa-shared-application-auth-runtime-role-secure-transport"
    / "live-local-backend-postgres-transport-evidence.json"
)
CLOSEOUT_PATH = (
    ROOT
    / "docs"
    / "raisa-shared-application-auth-runtime-role-secure-transport-closeout.md"
)
SOL_ACCEPTANCE_PATH = (
    ROOT
    / "orchestration"
    / "agent_inbox"
    / "codex"
    / "raisa-shared-application-auth-runtime-role-secure-transport-sol-acceptance.md"
)
PREACCEPTANCE_RECEIPT_PATH = (
    ROOT
    / "orchestration"
    / "agent_inbox"
    / "codex"
    / "raisa-shared-application-auth-runtime-role-secure-transport-preacceptance-receipt.json"
)
GRAPH_PATH = ROOT / "orchestration" / "continuity" / "emr4-continuity-graph.json"
COMPASS_PATH = ROOT / "orchestration" / "continuity" / "emr4-compass.json"
COMPASS_REPORT_PATH = ROOT / "docs" / "ariadne-compass-current.md"
AGENTS_PATH = ROOT / "AGENTS.md"
RECEIPT_PATH = (
    ROOT
    / "orchestration"
    / "agent_inbox"
    / "codex"
    / "raisa-shared-application-auth-runtime-role-secure-transport-cross-pc-resume-receipt.json"
)
FIVE_SOURCES = {
    "live_handover_current_baton",
    "current_authority_allocation",
    "active_plan_and_acceptance",
    "protected_evidence_boundaries",
    "git_refs_and_worktree",
}


def _load_runner():
    spec = importlib.util.spec_from_file_location(
        "raisa_shared_auth_runtime_role_transport_acceptance", RUNNER_PATH
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def disposable_acceptance() -> dict[str, object]:
    return _load_runner().run_acceptance(output_path=None)


def test_fresh_cross_pc_receipt_names_all_five_sources_and_disables_workers() -> None:
    receipt = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))
    assert receipt["status"] == "passed"
    assert receipt["rehydrated_from_receipt"] is True
    assert set(receipt["rehydration_sources"]) == FIVE_SOURCES
    assert receipt["worker_dispatch_permitted"] is False
    git_state = receipt["source_evidence"]["git_refs_and_worktree"]
    assert git_state["HEAD"] == "2ae8f2173276147e59be361e0182f6cb4b7453fa"
    assert git_state["remote_task_branch"] == git_state["HEAD"]
    assert git_state["protected_refs_unchanged"] is True


def test_plan_and_threat_model_keep_exact_closed_boundaries() -> None:
    combined = PLAN_PATH.read_text(encoding="utf-8") + THREAT_PATH.read_text(
        encoding="utf-8"
    )
    for required in (
        "default-off",
        "authored-synthetic",
        "least-privilege",
        "CSRF",
        "Secure HttpOnly",
        "non-enumerating",
        "product-derived",
        "external identity",
        "production",
        "release",
    ):
        assert required in combined
    assert "raisa_shared_application_auth_postgresql_persistence_pass" in combined


def test_openapi_contract_is_default_off_and_exactly_seven_post_routes() -> None:
    contract = yaml.safe_load(OPENAPI_PATH.read_text(encoding="utf-8"))
    assert contract["openapi"] == "3.1.0"
    assert (
        contract["x-emr4-authority-boundary"]["status"]
        == "default_off_authored_synthetic_only"
    )
    assert set(contract["paths"]) == {
        "/csrf",
        "/synthetic/session",
        "/session/validate",
        "/session/rotate",
        "/session/logout",
        "/exchange/issue",
        "/exchange/redeem",
    }
    assert all(set(path_item) == {"post"} for path_item in contract["paths"].values())
    assert contract["x-emr4-cookie-contract"]["raw_parent_in_client"] is False
    assert contract["x-emr4-cookie-contract"]["raw_surface_in_json"] is False


def test_exchange_request_models_reject_non_word_to_diary_surfaces() -> None:
    common = {
        "source_surface": "word_online",
        "target_surface": "native_diary",
        "source_origin": "https://word-online.synthetic.invalid",
        "target_origin": "https://diary.synthetic.invalid",
        "state": "state-authored-synthetic",
        "nonce": "nonce-authored-synthetic",
        "pkce_challenge": "c" * 43,
        "pkce_verifier": "v" * 43,
        "exchange_code": "exchange." + "e" * 43,
    }
    issue = ExchangeIssueRequest.model_validate(
        {key: common[key] for key in (
            "source_surface",
            "target_surface",
            "target_origin",
            "state",
            "nonce",
            "pkce_challenge",
        )}
    )
    redeem = ExchangeRedeemRequest.model_validate(
        {key: common[key] for key in (
            "exchange_code",
            "source_surface",
            "target_surface",
            "source_origin",
            "state",
            "nonce",
            "pkce_verifier",
        )}
    )
    assert issue.source_surface.value == "word_online"
    assert issue.target_surface.value == "native_diary"
    assert redeem.target_surface.value == "native_diary"
    for model, payload in (
        (ExchangeIssueRequest, {**issue.model_dump(), "source_surface": "native_diary"}),
        (ExchangeRedeemRequest, {**redeem.model_dump(), "target_surface": "word_desktop"}),
    ):
        with pytest.raises(ValueError):
            model.model_validate(payload)


def test_resolver_migration_is_narrow_reversible_and_public_closed() -> None:
    source = MIGRATION_PATH.read_text(encoding="utf-8")
    assert 'revision: str = "p5q6r7s8t9u0"' in source
    assert 'down_revision: Union[str, Sequence[str], None] = "o4p5q6r7s8t9"' in source
    assert "SECURITY DEFINER" in source
    assert "SET search_path = ''" in source
    assert "('parent', 'surface', 'exchange')" in source
    assert "^sha256:[0-9a-f]{64}$" in source
    assert "LIMIT 1" in source
    assert "REVOKE ALL ON FUNCTION" in source
    assert "DROP FUNCTION IF EXISTS" in source


def test_role_contract_has_exact_positive_and_negative_posture() -> None:
    role_name = "emr4_application_auth_runtime_1234abcd"
    statements = "\n".join(create_runtime_role_statements(role_name))
    assert "NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE" in statements
    assert "NOINHERIT NOREPLICATION NOBYPASSRLS" in statements
    assert "GRANT USAGE ON SCHEMA public" in statements
    assert "GRANT SELECT, INSERT, UPDATE ON TABLE" in statements
    assert f'public."{AUDIT_TABLE}"' in statements
    assert f'public."{AUDIT_SEQUENCE}"' in statements
    assert RESOLVER_SIGNATURE in statements
    for forbidden_grant in (
        "GRANT DELETE",
        "GRANT TRUNCATE",
        "GRANT REFERENCES",
        "GRANT TRIGGER",
        "GRANT CREATE",
    ):
        assert forbidden_grant not in statements
    assert set(STATE_TABLES) == {
        "application_auth_principal_generations",
        "application_auth_parent_sessions",
        "application_auth_surface_sessions",
        "application_auth_exchange_grants",
    }


def test_transport_is_mounted_but_has_no_environment_enable_switch() -> None:
    main_source = MAIN_PATH.read_text(encoding="utf-8")
    router_source = ROUTER_PATH.read_text(encoding="utf-8")
    transport_source = TRANSPORT_PATH.read_text(encoding="utf-8")
    assert "app.include_router(application_auth.router)" in main_source
    assert "get_application_auth_transport" in router_source
    assert "application_auth_transport_unavailable" in router_source
    assert "os.environ" not in router_source
    assert "settings." not in router_source
    assert "localStorage" not in router_source + transport_source
    assert "Authorization" not in router_source


def test_role_runtime_adds_timeouts_context_and_one_policy_engine() -> None:
    source = ROLE_RUNTIME_PATH.read_text(encoding="utf-8")
    for required in (
        "statement_timeout",
        "lock_timeout",
        "idle_in_transaction_session_timeout",
        "app.current_practice_ref",
        "ApplicationAuthTransportRuntime",
        "RoleScopedPostgresApplicationAuthRuntime",
    ):
        assert required in source
    for forbidden in (
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


def test_disposable_live_local_transport_acceptance_passes(
    disposable_acceptance: dict[str, object],
) -> None:
    assert disposable_acceptance["passed"] is True
    assert (
        disposable_acceptance["result"]
        == "raisa_shared_application_auth_runtime_role_secure_transport_pass"
    )
    assert (
        disposable_acceptance["evidence_label"]
        == "live_local_backend_postgres_transport"
    )
    assert disposable_acceptance["cleanup"]["passed"] is True


def test_live_role_resolver_and_migration_gates_pass(
    disposable_acceptance: dict[str, object],
) -> None:
    assert disposable_acceptance["migration"]["passed"] is True
    privileges = disposable_acceptance["privilege_matrix"]
    assert privileges["passed"] is True
    assert privileges["product_privilege_hits"] == 0
    assert privileges["role_properties"] == {
        "login": False,
        "superuser": False,
        "createdb": False,
        "createrole": False,
        "replication": False,
        "bypass_rls": False,
        "inherit": False,
    }
    resolver = disposable_acceptance["resolver"]
    assert resolver["passed"] is True
    assert resolver["public_execute"] is False


def test_live_transport_lifecycle_and_failure_matrices_pass(
    disposable_acceptance: dict[str, object],
) -> None:
    transport = disposable_acceptance["transport"]
    assert transport["passed"] is True
    assert transport["origin_matrix"]["all_generic_403"] is True
    assert all(transport["lifecycle"].values())
    assert transport["audit_atomicity"]["passed"] is True
    assert transport["role_scope"]["passed"] is True


def test_recorded_evidence_is_secret_free_and_fully_cleaned() -> None:
    evidence = json.loads(EVIDENCE_PATH.read_text(encoding="utf-8"))
    serialized = json.dumps(evidence, sort_keys=True)
    assert evidence["passed"] is True
    assert evidence["database"]["name_recorded"] is False
    assert evidence["role"]["name_recorded"] is False
    assert evidence["cleanup"]["database_absent_after"] is True
    assert evidence["cleanup"]["role_absent_after"] is True
    assert evidence["raw_secret_scan"]["matched_raw_value_count"] == 0
    assert evidence["raw_secret_scan"]["evidence_artifact_match_count"] == 0
    for forbidden in (
        "postgresql://",
        "gp_pms_dev",
        "gp_pms_test",
        "emr4_auth_transport_acceptance_",
        "emr4_application_auth_runtime_",
    ):
        assert forbidden not in serialized


def test_all_external_and_product_side_effect_counts_are_zero() -> None:
    evidence = json.loads(EVIDENCE_PATH.read_text(encoding="utf-8"))
    for key, value in evidence["side_effect_counts"].items():
        if key.startswith("database_"):
            continue
        assert value == 0


def test_preacceptance_receipt_is_five_source_and_non_dispatching() -> None:
    receipt = json.loads(PREACCEPTANCE_RECEIPT_PATH.read_text(encoding="utf-8"))
    assert receipt["status"] == "passed"
    assert receipt["rehydrated_from_receipt"] is True
    assert set(receipt["rehydration_sources"]) == FIVE_SOURCES
    assert receipt["worker_dispatch_permitted"] is False
    assert receipt["revision_binding"] == {
        "continuity_graph_revision_expected": 184,
        "compass_map_revision_expected": 165,
        "compass_source_graph_revision_expected": 184,
        "rendered_compass_exact_validation_required": True,
    }


def test_closeout_and_sol_acceptance_preserve_claim_limits() -> None:
    combined = CLOSEOUT_PATH.read_text(encoding="utf-8") + SOL_ACCEPTANCE_PATH.read_text(
        encoding="utf-8"
    )
    for required in (
        "raisa_shared_application_auth_runtime_role_secure_transport_pass",
        "default-off",
        "authored-synthetic",
        "No real identity",
        "product",
        "production",
        "release",
    ):
        assert required in combined
    assert "No commit, push, pull request" in combined


def test_continuity_preserves_accepted_transport_node_and_handover() -> None:
    graph = json.loads(GRAPH_PATH.read_text(encoding="utf-8"))
    compass = json.loads(COMPASS_PATH.read_text(encoding="utf-8"))
    transport_id = "raisa-shared-application-auth-runtime-role-secure-transport"
    node = next(item for item in graph["nodes"] if item["id"] == transport_id)
    journey = next(item for item in compass["journey"] if item["node_id"] == transport_id)
    assert graph["graph_revision"] >= 184
    assert node["status"] == "accepted"
    assert node["relationships"] == [
        {
            "node_id": "raisa-shared-application-auth-postgresql-persistence",
            "relation": "builds_on",
        }
    ]
    assert compass["map_revision"] >= 165
    assert compass["source_graph_revision"] == graph["graph_revision"]
    assert journey["lineage_parent"] == (
        "raisa-shared-application-auth-postgresql-persistence"
    )
    report = COMPASS_REPORT_PATH.read_text(encoding="utf-8")
    handover = AGENTS_PATH.read_text(encoding="utf-8")
    assert "runtime-role/transport descendant" in report
    assert "runtime-role and secure transport acceptance" in handover
    assert "The tranche is not accepted" not in handover
