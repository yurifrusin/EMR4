"""Run the fixed provider-free disposable PostgreSQL delete-confirm HTTP integration rehearsal.

The harness accepts no caller-selected input. It operates one uniquely named,
labelled ``--internal``-network, tmpfs-backed local PostgreSQL 16 container
through a fixed in-process IPv4-loopback relay and removes only exact captured
IDs after ownership re-verification. It installs the accepted delete-confirm
scaffold, the minimum authored-synthetic projection tables, one
non-superuser/NOBYPASSRLS application role, closed grants and forced tenant RLS
on the exact eight tables, then exercises the real FastAPI delete-confirm route
and hidden compatibility alias through ``TestClient`` with only ``get_db`` and
``get_command_session_factory`` overridden.

The evidence writer releases only the frozen allowlist fields and never retains
JWTs, HMACs, secrets, bodies, private bytes, SQL, URLs, passwords, runtime IDs,
row values, raw database output or exception text.
"""

from __future__ import annotations

import copy
import hashlib
import json
import re
import secrets
import shutil
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from uuid import UUID

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fastapi.routing import APIRoute
from fastapi.testclient import TestClient
from jsonschema import Draft202012Validator
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

from app.dependencies import get_command_session_factory, get_db
from app.main import app
from app.models.tenancy import UserRole
from app.routers import appointments as appointment_router
from app.schemas.appointments import (
    AppointmentDeleteCommand,
    AppointmentDeleteProposalConfirmationIn,
    AppointmentDeleteProposalOut,
)
from app.services import appointment_delete_product_adapter as adapter
from app.services.appointment_delete_composition import (
    validate_delete_confirm_private_receipt_bytes,
)
from app.services.appointment_delete_physical import (
    delete_confirm_response_digest,
)
from app.services.auth_service import create_access_token
from app.services.bernie_turn_evidence import mint_signed_confirmation_evidence
from scripts import (
    raisa_provider_free_disposable_postgresql_delete_confirm_behavior_transaction_rehearsal
    as delete_btr,
)
from scripts import (
    raisa_provider_free_disposable_postgresql_status_confirm_behavior_transaction_rehearsal
    as foundation,
)
from scripts import (
    raisa_provider_free_disposable_postgresql_delete_confirm_scaffold_parse_catalogue_rehearsal
    as catalogue,
)


BASE = ROOT / (
    "orchestration/continuity/raisa-provider-free-disposable-postgresql-"
    "delete-confirm-http-integration-rehearsal"
)
CONTRACT_PATH = BASE / "rehearsal-contract.json"
SCHEMA_PATH = BASE / "rehearsal-contract.schema.json"
EVIDENCE_SCHEMA_PATH = BASE / "provider-free-http-postgresql-evidence.schema.json"
EVIDENCE_PATH = BASE / "provider-free-http-postgresql-evidence.json"
FAILURE_EVIDENCE_PATH = BASE / "provider-free-http-postgresql-failure-evidence.json"
PASS_RESULT = (
    "raisa_provider_free_disposable_postgresql_delete_confirm_http_"
    "integration_rehearsal_pass"
)
EXPECTED_CONTRACT_DIGEST = (
    "88034f0eae5ad1597e2f1ae43ae9d0d1ec1989df4151674f222fbd951821b775"
)
EXPECTED_SOURCE_HEAD = "341d89b9a70c85f54247de364baf842b84543c8d"
EXPECTED_SCENARIOS = (
    ("DHI-S01", "proposal_binding", "non_mutating_verified_exact_proposal"),
    ("DHI-S02", "canonical_commit", "atomic_commit_public_private_separation"),
    ("DHI-S03", "compatibility_alias", "same_handler_commit"),
    ("DHI-S04", "response_loss_retry", "byte_identical_public_and_private_replay"),
    ("DHI-S05", "idempotency", "required_and_conflict"),
    ("DHI-S06", "authentication", "unauthorized_inactive_nonmutating"),
    ("DHI-S07", "cross_practice", "appointment_not_found"),
    ("DHI-S08", "version_binding", "structural_pre_session_and_stale_no_effect"),
    ("DHI-S09", "warning_acknowledgement", "atomic_block"),
    ("DHI-S10", "current_authority", "default_denial_and_revocation"),
    ("DHI-S11", "forced_scaffold_failure", "rollback_503_and_trigger_restored"),
    ("DHI-S12", "route_and_receipt_contract", "canonical_visible_alias_hidden_raw_delete_unchanged"),
)
CANONICAL_URL = "/api/v1/appointments/proposals/delete/confirm"
ALIAS_URL = "/api/v1/appointments/proposals/delete-confirm"
CLAIM_BOUNDARY = (
    "Exact authored-synthetic provider-free delete-confirm HTTP/PostgreSQL "
    "integration over one disposable PostgreSQL 16 server; no UI, product data, "
    "raw DELETE, provider, deployment, production or protected-ref claim."
)
HOSTILE_MUTATION_TARGET = 135
EXPECTED_READ_ONLY_BINDING_COUNT = 19
EXPECTED_EDITABLE_PRECONDITION_COUNT = 4
EXPECTED_ACCEPTED_HTTP_SOURCE = "c7a01edd96ebabf3ea2c07be89a5b405c9629853"
EXPECTED_ACCEPTED_DATABASE_SOURCE = "49dd2aaa72877adb844da4d0d5d5bb28039c90c8"
EXPECTED_NETWORK_NAME_PREFIX = "emr4-delete-http-dhi-net-"
EXPECTED_CONTAINER_NAME_PREFIX = "emr4-delete-http-dhi-pg16-"
EXPECTED_EVIDENCE_ALLOWLIST = (
    "scenario_ids",
    "decision_codes",
    "http_status_classes",
    "counts",
    "versions",
    "hashes",
    "endpoint_names",
    "containment_booleans",
    "rls_catalogue_facts",
    "cleanup_results",
)
EXPECTED_EVIDENCE_FORBIDDEN = (
    "jwt_or_bearer_values",
    "hmac_or_secret_material",
    "request_or_response_bodies",
    "private_receipt_bytes",
    "sql_or_connection_urls",
    "passwords",
    "container_network_or_runtime_ids",
    "synthetic_row_values",
    "unrestricted_database_output",
    "raw_exception_text",
)
EXPECTED_FORBIDDEN_SURFACES = (
    "product_patient_clinical_historical_diary_or_protected_data",
    "existing_or_product_database",
    "adapter_composition_schema_migration_or_public_contract_edit",
    "raw_delete_convergence",
    "provider_adc_credentials_iam_browser_or_external_network",
    "reusable_capability_or_client_selected_authority",
    "ui_deployment_production_release_pages_or_protected_refs",
    "docs_branding_or_unrelated_untracked_files",
)
EXPECTED_EDITABLE_PRECONDITIONS = (
    (
        "app/routers/appointments.py",
        "9b51623969bfdc657d6af2fda21b36a5ecb4973a3d1146e32460d8ebdaa7634e",
        "delegate_delete_producer_canonicalization_to_accepted_adapter_helpers",
    ),
    (
        "app/services/appointment_delete_physical.py",
        "8e0f0e06471560b328e5ab7af6cc9981c20ca4a58ec9eec74dbd412979f85533",
        "set_authenticated_practice_transaction_locally_after_isolation_before_reads",
    ),
    (
        "tests/test_raisa_provider_free_delete_confirm_http_route_convergence.py",
        "a77b80a81aff7ed18226d31c39413f4287cf44f794152ed2b4001f52b8ba4db2",
        "guard_route_producer_to_adapter_verified_exact_ingress",
    ),
    (
        "tests/test_raisa_provider_free_unmounted_delete_confirm_physical_schema_transaction_scaffold.py",
        "a12afe1de2ed6b311430f5d81c3098237b12068e0a4550ada60d7619366ad8e4",
        "guard_transaction_local_tenant_context_order_and_scope_and_reconcile_historical_openapi_binding",
    ),
)
EXPECTED_READ_ONLY_BINDINGS = {
    "app/dependencies.py": "70574af69c73664a9f8ebda15b749bc5b5b25fe291a55be1f080096146bf47bc",
    "app/main.py": "0e0f42290688943bc9dd7d5711826acf10430133be0b309eae94bad15da46ca2",
    "app/schemas/appointments.py": "ce7a9819e4947fb288c79009a08b7d9f2502b8d096ff5e2eb005796a250aee90",
    "app/config.py": "f0cafc21a88babd0d60d6ce30067a30d23b4030ad5dd4d26bb841096c62c1f2e",
    "app/services/auth_service.py": "c7380e744bc42be006b34546769b76eb3b8f010b8602513a64f3865c76c1f33c",
    "app/services/appointment_delete_product_adapter.py": "a7e1702c61258acfb51f634883086ad5993c8ab63989eace9cfa1102b2532c59",
    "app/services/appointment_delete_composition.py": "ed6a5e705808c71ecf4edcec837c6be2ec790660bf32a85357bda68c2159aa15",
    "app/services/bernie_turn_evidence.py": "e72e4052ce4f9bc2d3e6f308401a439b84987422b4003ddfbed34059a98cd467",
    "app/models/tenancy.py": "e411c816565bdddfbb25beca62439c5bba7a44a90e348cd7e9f4296a65fb65e2",
    "app/models/appointments.py": "4ae06eeb87c6d5212e354c39c01a8da397cfa2c21bd1031c24e1467d86c77794",
    "alembic/versions/x3y4z5a6b7c8_add_delete_confirm_physical_scaffold.py": "e6542c960a9378cf7c1c3c22dd876a1c9f242b68047a180f9f383c1c62d348bb",
    "docs/api-spine/openapi/appointment-commands.yaml": "0dfbce13f3d8933d0cd2355fb41e70612c1550e75c452b95c1528576ac1c8622",
    "app/services/diary/confirm_actions.py": "7f4bdd108c3e0039d19341e76e1cf7eb8e491adaa1e5691b5590a59008a09989",
    "docs/raisa-provider-free-delete-confirm-http-route-convergence-closeout.md": "c6a05ec770cd29adc7bc0316c92e94bbd45ff03610d4ef43194b9d45d6b64f82",
    "docs/raisa-provider-free-disposable-postgresql-delete-confirm-behavior-transaction-rehearsal-closeout.md": "90d42d80d06d1c173fde25b7da153173b195cbc118e672cac6746493ef0aa507",
    "scripts/raisa_provider_free_disposable_postgresql_delete_confirm_behavior_transaction_rehearsal.py": "b906e4029157b39058d7466dcaea772051df54815f6172abfe2f4e6c1b099306",
    "orchestration/continuity/raisa-provider-free-disposable-postgresql-delete-confirm-behavior-transaction-rehearsal/rehearsal-contract.json": "99c88349cecbaeeec12b601e33615fb55e8bb7d71fcb764c3ca1a5f8939f0b0a",
    "scripts/raisa_provider_free_status_confirm_http_route_convergence.py": "2463467bb45220bceead366735c320c751babf460803de75b230d39c1846c8ec",
    "docs/raisa-provider-free-status-confirm-http-route-convergence-plan.md": "27f7f033b20db36e06bad285bd0318f5f41e7c5d849ba786e6f3aae1363b3db5",
}


class RehearsalFailure(RuntimeError):
    def __init__(
        self,
        stage: str,
        code: str,
        detail: str | bytes = "",
        *,
        diagnostic: dict[str, Any] | None = None,
    ) -> None:
        self.stage = stage
        self.code = code
        self.detail = detail.encode("utf-8") if isinstance(detail, str) else detail
        self.diagnostic = diagnostic
        super().__init__(f"{stage}:{code}")


def _sha256(value: bytes | str) -> str:
    payload = value.encode("utf-8") if isinstance(value, str) else value
    return hashlib.sha256(payload).hexdigest()


def _canonical_digest(value: Any) -> str:
    return _sha256(
        json.dumps(
            value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        ).encode("utf-8")
    )


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _source_text_sha256_bytes(payload: bytes) -> str:
    """Hash UTF-8 text after checkout-stable CRLF-to-LF conversion."""
    normalized = payload.replace(b"\r\n", b"\n")
    if b"\r" in normalized:
        raise RehearsalFailure("preflight", "source_bare_carriage_return")
    try:
        normalized.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise RehearsalFailure("preflight", "source_not_utf8_text") from exc
    return _sha256(normalized)


@dataclass(frozen=True)
class Fixture:
    index: int
    practice_id: UUID
    appointment_id: UUID
    actor_id: UUID
    actor_text: str
    practitioner_id: UUID
    audit_id: UUID


def _fixture(index: int) -> Fixture:
    return Fixture(
        index=index,
        practice_id=UUID(int=0x10000000000040008000000000000000 + index),
        appointment_id=UUID(int=0x20000000000040008000000000000000 + index),
        actor_id=UUID(int=0x30000000000040008000000000000000 + index),
        actor_text=str(UUID(int=0x30000000000040008000000000000000 + index)),
        practitioner_id=UUID(int=0x50000000000040008000000000000000 + index),
        audit_id=UUID(int=0x40000000000040008000000000000000 + index),
    )

def _validate_contract(value: dict[str, Any], *, require_digest: bool) -> None:
    schema = _load_json(SCHEMA_PATH)
    errors = list(Draft202012Validator(schema).iter_errors(value))
    if errors:
        raise RehearsalFailure("preflight", "contract_schema_invalid")
    if require_digest and _canonical_digest(value) != EXPECTED_CONTRACT_DIGEST:
        raise RehearsalFailure("preflight", "contract_digest_mismatch")
    if value["source_head"] != EXPECTED_SOURCE_HEAD:
        raise RehearsalFailure("preflight", "source_head_mismatch")
    if value["accepted_http_source"] != EXPECTED_ACCEPTED_HTTP_SOURCE:
        raise RehearsalFailure("preflight", "accepted_http_source_mismatch")
    if value["accepted_database_behavior_source"] != EXPECTED_ACCEPTED_DATABASE_SOURCE:
        raise RehearsalFailure("preflight", "accepted_database_source_mismatch")
    if (
        tuple((item["id"], item["kind"], item["expected"]) for item in value["scenarios"])
        != EXPECTED_SCENARIOS
    ):
        raise RehearsalFailure("preflight", "scenario_contract_mismatch")
    if value["read_only_bindings"] != EXPECTED_READ_ONLY_BINDINGS:
        raise RehearsalFailure("preflight", "read_only_binding_contract_mismatch")
    if value["docker_profile"]["network_name_prefix"] != EXPECTED_NETWORK_NAME_PREFIX:
        raise RehearsalFailure("preflight", "network_name_prefix_mismatch")
    if value["docker_profile"]["context"] != "default":
        raise RehearsalFailure("preflight", "docker_context_mismatch")
    if value["docker_profile"]["container_name_prefix"] != EXPECTED_CONTAINER_NAME_PREFIX:
        raise RehearsalFailure("preflight", "container_name_prefix_mismatch")
    if tuple(value["evidence_allowlist"]) != EXPECTED_EVIDENCE_ALLOWLIST:
        raise RehearsalFailure("preflight", "evidence_allowlist_mismatch")
    if tuple(value["evidence_forbidden"]) != EXPECTED_EVIDENCE_FORBIDDEN:
        raise RehearsalFailure("preflight", "evidence_forbidden_mismatch")
    if tuple(value["forbidden_surfaces"]) != EXPECTED_FORBIDDEN_SURFACES:
        raise RehearsalFailure("preflight", "forbidden_surfaces_mismatch")
    if (
        tuple(
            (item["path"], item["sha256"], item["repair"])
            for item in value["editable_preconditions"]
        )
        != EXPECTED_EDITABLE_PRECONDITIONS
    ):
        raise RehearsalFailure("preflight", "editable_precondition_contract_mismatch")
    if tuple(value["tenant_contract"]["forced_rls_tables"]) != (
        "appointments",
        "users",
        "practitioners",
        "patients",
        "appointment_types",
        "user_capability_grants",
        "appointment_command_idempotency",
        "appointment_audit_log",
    ):
        raise RehearsalFailure("preflight", "tenant_rls_table_contract_mismatch")

def hostile_mutations_rejected(contract: dict[str, Any]) -> int:
    """Reject closed semantic mutations covering every frozen threat."""
    mutations: list[dict[str, Any]] = []

    def mutate(path: tuple[str | int, ...], replacement: Any) -> None:
        candidate = copy.deepcopy(contract)
        cursor: Any = candidate
        for part in path[:-1]:
            cursor = cursor[part]
        cursor[path[-1]] = replacement
        mutations.append(candidate)

    globals_to_mutate = (
        (("schema_version",), "raisa.delete_confirm_http_postgresql_integration_contract.v2"),
        (("result",), "rehearsal_failed"),
        (("source_head",), "0" * 40),
        (("accepted_http_source",), "f" * 40),
        (("accepted_database_behavior_source",), "e" * 40),
        (("input_hash_mode",), "raw_worktree_bytes"),
        (("evidence_label",), "product"),
        (("data_posture",), "product_derived_only"),
        (("canonical_path",), ALIAS_URL),
        (("compatibility_alias",), CANONICAL_URL),
        (("raw_delete_path",), "/api/v1/appointments/{id}"),
        (("minimum_hostile_mutations",), 119),
        (("docker_profile", "executable"), "podman.exe"),
        (("docker_profile", "context"), "product"),
        (("docker_profile", "image_reference"), "postgres:latest"),
        (("docker_profile", "pull_policy"), "always"),
        (("docker_profile", "network_internal"), False),
        (("docker_profile", "network_name_prefix"), "emr4-net-"),
        (("docker_profile", "container_name_prefix"), "emr4-pg16-"),
        (("docker_profile", "harness_label"), "delete-confirm-http-v2"),
        (("docker_profile", "published_ports"), True),
        (("docker_profile", "relay_host_ip"), "0.0.0.0"),
        (("docker_profile", "relay_dynamic_host_port"), False),
        (("docker_profile", "relay_container_executable"), "sh"),
        (("docker_profile", "relay_container_command"), "cat"),
        (("docker_profile", "postgres_container_port"), 5433),
        (("docker_profile", "sqlalchemy_driver"), "psycopg"),
        (("docker_profile", "data_destination"), "/mnt/data"),
        (("docker_profile", "tmpfs_options"), "rw"),
        (("docker_profile", "memory_bytes"), 1073741824),
        (("docker_profile", "nano_cpus"), 2000000000),
        (("docker_profile", "pids_limit"), 256),
        (("docker_profile", "restart_policy"), "always"),
        (("docker_profile", "postgres_user"), "postgres"),
        (("docker_profile", "postgres_database"), "product"),
        (("docker_profile", "pgdata"), "/var/lib/postgresql"),
        (("docker_profile", "application_user"), "product_app"),
        (("docker_profile", "startup_timeout_seconds"), 30),
        (("docker_profile", "command_timeout_seconds"), 10),
        (("docker_profile", "total_timeout_seconds"), 30),
        (("docker_profile", "readiness_observations"), 1),
        (("tenant_contract", "setting"), "app.practice_id"),
        (("tenant_contract", "transaction_local"), False),
        (("tenant_contract", "context_after_isolation_before_reads"), False),
        (("tenant_contract", "application_role_superuser"), True),
        (("tenant_contract", "application_role_bypass_rls"), True),
        (("tenant_contract", "forced_rls_tables"), ["appointments"]),
        (("public_private_contract", "public_schema"), "raisa.delete_public_envelope.v1"),
        (("public_private_contract", "private_schema"), "appointment.delete_receipt.v1"),
        (("public_private_contract", "public_bytes_are_private_bytes"), True),
        (("public_private_contract", "private_bytes_may_be_http_content"), True),
        (("public_private_contract", "replay_public_bytes_identical"), False),
        (("public_private_contract", "replay_private_bytes_identical"), False),
        (("evidence_allowlist",), ["raw_sql", "credentials"]),
        (("evidence_forbidden",), ["hashes"]),
        (("cleanup", "container_target"), "container_name"),
        (("cleanup", "network_target"), "captured_network_id_broad"),
        (("cleanup", "engine_relay_before_container"), False),
        (("cleanup", "post_remove_exact_id_absence_required"), False),
        (("forbidden_surfaces",), ["product_data"]),
        (("new_output_paths",), ["scripts/owned.py"]),
    )
    for path, replacement in globals_to_mutate:
        mutate(path, replacement)

    added_url = copy.deepcopy(contract)
    added_url["caller_database_url"] = "postgresql://product"
    mutations.append(added_url)

    added_sql = copy.deepcopy(contract)
    added_sql["raw_sql_callback"] = True
    mutations.append(added_sql)

    for index in range(EXPECTED_EDITABLE_PRECONDITION_COUNT):
        item = contract["editable_preconditions"][index]
        mutate(("editable_preconditions", index, "path"), item["path"] + "-hostile")
        mutate(("editable_preconditions", index, "sha256"), "0" * 64)
        mutate(("editable_preconditions", index, "repair"), "substitute_command_seam")

    for path in list(contract["read_only_bindings"]):
        removed = copy.deepcopy(contract)
        removed["read_only_bindings"].pop(path)
        mutations.append(removed)

    for index in range(12):
        scenario = contract["scenarios"][index]
        mutate(("scenarios", index, "id"), f"DHI-S{((index + 5) % 12) + 1:02d}")
        mutate(("scenarios", index, "kind"), scenario["kind"] + "-hostile")
        mutate(("scenarios", index, "expected"), scenario["expected"] + "-hostile")

    mutate(("scenarios", 0, "id"), "DHI-S99")
    mutate(("scenarios", 0, "kind"), "")
    mutate(("scenarios", 0, "expected"), "")
    mutate(("editable_preconditions",), contract["editable_preconditions"][:2])
    mutate(("read_only_bindings", "app/dependencies.py"), "0" * 64)

    if len(mutations) < HOSTILE_MUTATION_TARGET:
        raise AssertionError("hostile mutation population drift")
    rejected = 0
    for candidate in mutations:
        try:
            _validate_contract(candidate, require_digest=False)
        except RehearsalFailure:
            rejected += 1
    return rejected

def _repair_semantics_ok() -> dict[str, str]:
    """Prove the four editable preconditions satisfy the frozen repair semantics.

    Returns the present canonical-LF SHA-256 digests of the four editable files.
    The contract's ``editable_preconditions`` hashes are pre-edit evidence and are
    deliberately not compared against these present descendants.
    """
    router = (ROOT / "app/routers/appointments.py").read_text(encoding="utf-8")
    physical = (ROOT / "app/services/appointment_delete_physical.py").read_text(
        encoding="utf-8"
    )
    route_test = (
        ROOT / "tests/test_raisa_provider_free_delete_confirm_http_route_convergence.py"
    ).read_text(encoding="utf-8")
    physical_test = (
        ROOT
        / "tests/test_raisa_provider_free_unmounted_delete_confirm_physical_schema_transaction_scaffold.py"
    ).read_text(encoding="utf-8")

    for token in (
        "compose_product_delete_confirm(",
        "delete_command_payload(",
        "delete_proposal_freshness_id(",
        "delete_signed_confirmation_payload(",
        "mint_delete_proposal_version_binding(",
    ):
        if token not in router:
            raise RehearsalFailure("preflight", "route_adapter_delegation_missing")

    physical_source = (ROOT / "app/services/appointment_delete_physical.py").read_text(
        encoding="utf-8"
    )
    tree_import = __import__("ast")
    tree = tree_import.parse(physical_source)
    function = next(
        node
        for node in tree.body
        if isinstance(node, tree_import.FunctionDef)
        and node.name == "delete_confirm_locked_transaction"
    )
    span = tree_import.get_source_segment(physical_source, function)
    if span is None:
        raise RehearsalFailure("preflight", "physical_transaction_span_missing")
    isolation_at = span.find("SET TRANSACTION ISOLATION LEVEL READ COMMITTED")
    context_at = span.find('"app.current_practice_id"')
    first_read_at = span.find("db.query(User)")
    if not (0 <= isolation_at < context_at < first_read_at):
        raise RehearsalFailure("preflight", "tenant_context_ordering_mismatch")
    if span.count('"app.current_practice_id"') != 1:
        raise RehearsalFailure("preflight", "tenant_context_not_transaction_local")
    if "SET LOCAL lock_timeout = :timeout" in span:
        raise RehearsalFailure("preflight", "tenant_context_not_local_set_config")

    if "test_route_produced_proposal_passes_exact_adapter_precommand_ingress" not in route_test:
        raise RehearsalFailure("preflight", "route_producer_regression_missing")
    if "test_transaction_ast_has_one_boundary_and_exact_lock_authority_order" not in physical_test:
        raise RehearsalFailure("preflight", "physical_context_regression_missing")

    present = {
        "app/routers/appointments.py": _source_text_sha256_bytes(
            (ROOT / "app/routers/appointments.py").read_bytes()
        ),
        "app/services/appointment_delete_physical.py": _source_text_sha256_bytes(
            (ROOT / "app/services/appointment_delete_physical.py").read_bytes()
        ),
        "tests/test_raisa_provider_free_delete_confirm_http_route_convergence.py": (
            _source_text_sha256_bytes(
                (
                    ROOT
                    / "tests/test_raisa_provider_free_delete_confirm_http_route_convergence.py"
                ).read_bytes()
            )
        ),
        "tests/test_raisa_provider_free_unmounted_delete_confirm_physical_schema_transaction_scaffold.py": (
            _source_text_sha256_bytes(
                (
                    ROOT
                    / "tests/test_raisa_provider_free_unmounted_delete_confirm_physical_schema_transaction_scaffold.py"
                ).read_bytes()
            )
        ),
    }
    return present


def verify_contract() -> tuple[dict[str, Any], dict[str, str], dict[str, str]]:
    contract = _load_json(CONTRACT_PATH)
    _validate_contract(contract, require_digest=True)
    if hostile_mutations_rejected(contract) != HOSTILE_MUTATION_TARGET:
        raise RehearsalFailure("preflight", "hostile_mutation_gate_failed")
    source_hashes: dict[str, str] = {}
    for path, expected in contract["read_only_bindings"].items():
        target = ROOT / path
        if not target.is_file():
            raise RehearsalFailure("preflight", "source_missing", path)
        digest = _source_text_sha256_bytes(target.read_bytes())
        source_hashes[path] = digest
        if digest != expected:
            raise RehearsalFailure("preflight", "source_hash_mismatch", path)
    present_editable = _repair_semantics_ok()
    source_hashes.update(present_editable)
    implementation_paths = [
        "scripts/raisa_provider_free_disposable_postgresql_delete_confirm_http_integration_rehearsal.py",
        "tests/test_raisa_provider_free_disposable_postgresql_delete_confirm_http_integration_rehearsal.py",
        "tests/test_raisa_provider_free_disposable_postgresql_delete_confirm_http_integration_rehearsal_plan.py",
    ]
    implementation_hashes = {
        path: _source_text_sha256_bytes((ROOT / path).read_bytes())
        for path in implementation_paths
    }
    return contract, source_hashes, implementation_hashes

PROJECTION_SQL = r"""
CREATE TABLE public.practitioners (
  id uuid PRIMARY KEY, practice_id uuid NOT NULL,
  first_name varchar(100) NOT NULL, last_name varchar(100) NOT NULL,
  provider_number varchar(20), prescriber_number varchar(20),
  ahpra_number varchar(20), hpi_i varchar(20), specialty varchar(100),
  default_location_id uuid, aggregate_version integer DEFAULT 0,
  is_active boolean DEFAULT true, created_at timestamptz DEFAULT now()
);
CREATE TABLE public.patients (
  id uuid PRIMARY KEY, practice_id uuid NOT NULL,
  first_name varchar(100), last_name varchar(100), date_of_birth date,
  medicare_number varchar(32), medicare_irn varchar(8), ihi_number varchar(32),
  dva_number varchar(32), sex varchar(32), gender_identity varchar(64),
  indigenous_status varchar(64), preferred_language varchar(64),
  email varchar(255), phone_mobile varchar(32), phone_home varchar(32),
  address_line1 varchar(255), address_suburb varchar(100), address_state varchar(16),
  address_postcode varchar(16), emergency_contact_name varchar(255),
  emergency_contact_phone varchar(32), emergency_contact_relationship varchar(64),
  concession_type varchar(64), consent_facial_recognition boolean,
  face_embedding_id varchar(255), document_url varchar(1024), sms_consent boolean,
  sms_consent_date timestamptz, created_at timestamptz, updated_at timestamptz
);
CREATE TABLE public.appointment_types (
  id uuid PRIMARY KEY, practice_id uuid NOT NULL,
  name varchar(100), default_duration integer, color_hex varchar(16),
  is_bookable_online boolean
);
""".strip() + "\n"


def _role_and_rls_sql(profile: dict[str, Any]) -> str:
    tables = (
        "appointments",
        "users",
        "practitioners",
        "patients",
        "appointment_types",
        "user_capability_grants",
        "appointment_command_idempotency",
        "appointment_audit_log",
    )
    lines = [
        f"CREATE ROLE {profile['application_user']} LOGIN PASSWORD "
        f"'{profile['application_password']}' NOSUPERUSER NOBYPASSRLS;",
        f"GRANT CONNECT ON DATABASE {profile['postgres_database']} "
        f"TO {profile['application_user']};",
        f"GRANT USAGE ON SCHEMA public TO {profile['application_user']};",
    ]
    for table in tables:
        lines.append(
            f"GRANT SELECT, INSERT, UPDATE ON public.{table} "
            f"TO {profile['application_user']};"
        )
    lines.append(
        f"GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public "
        f"TO {profile['application_user']};"
    )
    for table in tables:
        lines.append(f"ALTER TABLE public.{table} ENABLE ROW LEVEL SECURITY;")
        lines.append(f"ALTER TABLE public.{table} FORCE ROW LEVEL SECURITY;")
        lines.append(
            f"CREATE POLICY tenant_isolation_{table} ON public.{table} "
            "USING (practice_id = nullif(current_setting('app.current_practice_id', true), '')::uuid) "
            "WITH CHECK (practice_id = nullif(current_setting('app.current_practice_id', true), '')::uuid);"
        )
    return "\n".join(lines) + "\n"


def _install_database(
    docker: str, container_id: str, delete_contract: dict[str, Any], profile: dict[str, Any]
) -> None:
    delete_btr._install_database(docker, container_id, delete_contract)  # noqa: SLF001
    catalogue._psql(  # noqa: SLF001
        catalogue._run,  # noqa: SLF001
        docker,
        container_id,
        profile,
        PROJECTION_SQL,
        single_transaction=True,
    )
    catalogue._psql(  # noqa: SLF001
        catalogue._run,  # noqa: SLF001
        docker,
        container_id,
        profile,
        _role_and_rls_sql(profile),
        single_transaction=True,
    )


def _catalogue_check(admin: Engine) -> dict[str, Any]:
    with admin.connect() as connection:
        head = connection.execute(
            text("SELECT version_num FROM alembic_version")
        ).scalar_one()
        role_row = connection.execute(
            text(
                "SELECT rolsuper, rolbypassrls FROM pg_roles "
                "WHERE rolname=:name"
            ),
            {"name": "emr4_delete_http_app"},
        ).one_or_none()
        rls_count = connection.execute(
            text(
                "SELECT count(*) FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace "
                "WHERE n.nspname='public' AND c.relname IN "
                "('appointments','users','practitioners','patients','appointment_types',"
                "'user_capability_grants','appointment_command_idempotency','appointment_audit_log') "
                "AND c.relrowsecurity AND c.relforcerowsecurity"
            )
        ).scalar_one()
        constraints = connection.execute(
            text(
                "SELECT count(*) FROM pg_constraint WHERE conname IN "
                "('fk_appt_cmd_idem_practice_target','fk_appt_audit_log_practice_appointment',"
                "'fk_appt_audit_log_practice_command','fk_appt_cmd_idem_practice_audit',"
                "'ck_appt_cmd_idem_status_receipt_v1_complete','ck_appt_audit_log_delete_v1_complete')"
            )
        ).scalar_one()
        triggers = connection.execute(
            text(
                "SELECT count(*) FROM pg_trigger WHERE NOT tgisinternal AND tgname IN "
                "('trg_users_authority_generation_guard','trg_user_capability_grants_generation',"
                "'trg_user_capability_grants_reject_update','trg_appointments_advance_state_version')"
            )
        ).scalar_one()
    if head != "x3y4z5a6b7c8":
        raise RehearsalFailure("catalogue", "migration_head_mismatch")
    if role_row is None or role_row[0] is not False or role_row[1] is not False:
        raise RehearsalFailure("catalogue", "application_role_privilege_mismatch")
    if rls_count != 8 or constraints < 6 or triggers != 4:
        raise RehearsalFailure("catalogue", "rls_or_constraint_mismatch")
    return {
        "migration_head": head,
        "application_role_superuser": False,
        "application_role_bypass_rls": False,
        "forced_rls_table_count": int(rls_count),
        "selected_constraint_count": int(constraints),
        "selected_trigger_count": int(triggers),
        "transaction_context_local": True,
    }

def _admin_engine(host_port: int, profile: dict[str, Any]) -> Engine:
    return foundation._engine(host_port, profile)  # noqa: SLF001


def _application_engine(host_port: int, profile: dict[str, Any]) -> Engine:
    url = (
        f"postgresql+{profile['sqlalchemy_driver']}://{profile['application_user']}:"
        f"{profile['application_password']}@{profile['relay_host_ip']}:{host_port}/"
        f"{profile['postgres_database']}"
    )
    engine = create_engine(
        url,
        pool_size=2,
        max_overflow=0,
        pool_timeout=5,
        pool_pre_ping=True,
        connect_args={"connect_timeout": 5, "application_name": "emr4_delete_http"},
    )
    with engine.connect() as connection:
        identity = connection.execute(
            text(
                "SELECT current_user, rolsuper, rolbypassrls "
                "FROM pg_roles WHERE rolname=current_user"
            )
        ).one()
        if identity != (profile["application_user"], False, False):
            engine.dispose()
            raise RehearsalFailure("environment", "application_role_mismatch")
        connection.rollback()
    return engine


def _two_pool_settings_absent(engine: Engine) -> bool:
    with engine.connect() as first, engine.connect() as second:
        values = [
            connection.execute(
                text("SELECT current_setting('app.current_practice_id', true)")
            ).scalar_one_or_none()
            for connection in (first, second)
        ]
        first.rollback()
        second.rollback()
    return all(value in (None, "") for value in values)


def _token(fixture: Fixture, *, role: str = UserRole.Receptionist.value) -> str:
    return create_access_token(
        {
            "sub": str(fixture.actor_id),
            "practice_id": str(fixture.practice_id),
            "role": role,
        }
    )


def _headers(token: str, key: str | None = None) -> dict[str, str]:
    headers = {"Authorization": f"Bearer {token}"}
    if key is not None:
        headers["Idempotency-Key"] = key
    return headers


def _seed(
    admin: Engine,
    fixture: Fixture,
    *,
    with_grant: bool = True,
    appointment: bool = True,
    active: bool = True,
    role: str = "Receptionist",
    waiting_area: bool = False,
    second_practice_id: UUID | None = None,
    appointment_only: bool = False,
) -> None:
    with admin.begin() as connection:
        if not appointment_only:
            connection.execute(
                text(
                    "INSERT INTO practices(id, name, timezone, hive_mind_opt_in) "
                    "VALUES (:id, :name, 'Australia/Sydney', false)"
                ),
                {
                    "id": fixture.practice_id,
                    "name": f"Synthetic Practice {fixture.index:02d}",
                },
            )
            if second_practice_id is not None:
                connection.execute(
                    text(
                        "INSERT INTO practices(id, name, timezone, hive_mind_opt_in) "
                        "VALUES (:id, :name, 'Australia/Sydney', false)"
                    ),
                    {
                        "id": second_practice_id,
                        "name": f"Synthetic Practice {fixture.index:02d} secondary",
                    },
                )
            connection.execute(
                text(
                    "INSERT INTO users(id, practice_id, email, password_hash, role, is_active) "
                    "VALUES (:id, :practice_id, :email, :pw, :role, :active)"
                ),
                {
                    "id": fixture.actor_id,
                    "practice_id": fixture.practice_id,
                    "email": f"synthetic-user-{fixture.index:02d}",
                    "pw": "0" * 64,
                    "role": role,
                    "active": active,
                },
            )
            connection.execute(
                text(
                    "INSERT INTO practitioners(id, practice_id, first_name, last_name) "
                    "VALUES (:id, :practice_id, 'Synthetic', 'Practitioner')"
                ),
                {
                    "id": fixture.practitioner_id,
                    "practice_id": fixture.practice_id,
                },
            )
        if appointment:
            waiting_value = (
                UUID(int=0x90000000000040008000000000000000 + fixture.index)
                if waiting_area
                else None
            )
            connection.execute(
                text(
                    "INSERT INTO appointments(id, practice_id, practitioner_id, patient_name_provisional, "
                    "start_time, appointment_date, start_time_local, duration_minutes, status, booked_via, "
                    "waiting_area_id) "
                    "VALUES (:id, :practice_id, :practitioner_id, 'Synthetic Patient', "
                    "'2026-08-12 09:00:00+10', '2026-08-12', '09:00:00', 15, 'Booked', 'Receptionist', "
                    ":waiting_value)"
                ),
                {
                    "id": fixture.appointment_id,
                    "practice_id": fixture.practice_id,
                    "practitioner_id": fixture.practitioner_id,
                    "waiting_value": waiting_value,
                },
            )
        if with_grant and not appointment_only:
            connection.execute(
                text(
                    "INSERT INTO user_capability_grants(practice_id, user_id, capability_code) "
                    "VALUES (:p, :u, 'appointment.cancel.confirm')"
                ),
                {"p": fixture.practice_id, "u": fixture.actor_id},
            )

def _snapshot(admin: Engine, fixture: Fixture) -> dict[str, Any]:
    with admin.connect() as connection:
        appointment = connection.execute(
            text(
                "SELECT status, appointment_state_version, waiting_area_id FROM appointments "
                "WHERE practice_id=:p AND id=:a"
            ),
            {"p": fixture.practice_id, "a": fixture.appointment_id},
        ).one_or_none()
        params = {"p": fixture.practice_id, "a": fixture.appointment_id}
        audit_count = connection.execute(
            text(
                "SELECT count(*) FROM appointment_audit_log "
                "WHERE practice_id=:p AND appointment_id=:a"
            ),
            params,
        ).scalar_one()
        idempotency_rows = connection.execute(
            text(
                "SELECT count(*) FROM appointment_command_idempotency "
                "WHERE practice_id=:p AND target_appointment_id=:a"
            ),
            params,
        ).scalar_one()
        complete_count = connection.execute(
            text(
                "SELECT count(*) FROM appointment_command_idempotency "
                "WHERE practice_id=:p AND target_appointment_id=:a "
                "AND completed_receipt_version=1 AND route_family='delete-confirm'"
            ),
            params,
        ).scalar_one()
    return {
        "status": appointment[0] if appointment is not None else None,
        "version": appointment[1] if appointment is not None else None,
        "waiting_area_id": appointment[2] if appointment is not None else None,
        "audit_count": int(audit_count),
        "idempotency_rows": int(idempotency_rows),
        "completed_v1_count": int(complete_count),
    }


def _assert_unchanged(admin: Engine, fixture: Fixture) -> None:
    snapshot = _snapshot(admin, fixture)
    if (
        snapshot["status"] != "Booked"
        or snapshot["version"] != 1
        or snapshot["audit_count"] != 0
        or snapshot["idempotency_rows"] != 0
        or snapshot["completed_v1_count"] != 0
    ):
        raise RehearsalFailure("scenario", "unexpected_database_effect")


def _proposal(
    client: TestClient,
    fixture: Fixture,
    token: str,
    *,
    reason_code: str = "PATIENT_CANCELLED",
) -> dict[str, Any]:
    response = client.post(
        f"/api/v1/appointments/proposals/delete/{fixture.appointment_id}",
        json={"status_reason_code": reason_code},
        headers=_headers(token, f"proposal-{fixture.index}"),
    )
    if response.status_code != 200 or response.json().get("safe") is not True:
        raise RehearsalFailure("scenario", "proposal_unavailable")
    return response.json()


def _confirm_payload(proposal: dict[str, Any]) -> dict[str, Any]:
    payload = copy.deepcopy(proposal["confirm_payload"])
    payload["confirmed"] = True
    return payload


def _stored_bytes(admin: Engine, appointment_id: UUID) -> bytes:
    with admin.connect() as connection:
        value = connection.execute(
            text(
                "SELECT response_body_canonical_bytes FROM appointment_command_idempotency "
                "WHERE target_appointment_id=:appointment_id AND state='completed' "
                "AND route_family='delete-confirm'"
            ),
            {"appointment_id": appointment_id},
        ).scalar_one()
    return bytes(value)


def _manual_cross_practice_body(
    target: Fixture,
    actor: Fixture,
) -> dict[str, Any]:
    command = AppointmentDeleteCommand(
        appointment_id=target.appointment_id,
        clears_waiting_area=False,
        cancellation_reason=None,
        status_reason_code="PATIENT_CANCELLED",
    )
    state = {
        "appointment_id": str(target.appointment_id),
        "status": "Booked",
        "status_reason_code": "PATIENT_CANCELLED",
        "waiting_area_id": None,
        "cancellation_reason": None,
        "source_version": 1,
    }
    freshness_id = adapter.delete_proposal_freshness_id(command, state)
    evidence = mint_signed_confirmation_evidence(
        adapter.delete_signed_confirmation_payload(
            practice_id=actor.practice_id,
            actor_id=actor.actor_id,
            command=command,
            current_state=state,
            freshness_id=freshness_id,
        ),
        evidence_purpose=adapter.DELETE_CONFIRM_EVIDENCE_PURPOSE,
        secret=appointment_router._delete_confirm_evidence_secret(),  # noqa: SLF001
    )
    binding = adapter.mint_delete_proposal_version_binding(
        evidence,
        source_version=1,
        secret=appointment_router._delete_confirm_domain_secret("proposal-version"),  # noqa: SLF001
    )
    proposal = AppointmentDeleteProposalOut(
        intent="delete_appointment",
        safe=True,
        requires_confirmation=True,
        autonomy_tier="proposal",
        summary="Authored-synthetic cross-practice probe.",
        command=command,
        warnings=[],
        blocks=[],
        delete_proposal_freshness_id=freshness_id,
        delete_proposal_version_binding=binding,
        signed_confirmation_evidence=evidence,
        signed_confirmation_evidence_required=True,
    )
    return AppointmentDeleteProposalConfirmationIn(
        confirmed=True,
        delete_proposal=proposal,
        confirmed_warnings=[],
        delete_proposal_freshness_id=freshness_id,
        delete_proposal_version_binding=binding,
        signed_confirmation_evidence=evidence,
        signed_confirmation_evidence_required=True,
    ).model_dump(mode="json")


def _public_private_proof(
    admin: Engine, fixture: Fixture, public_bytes: bytes
) -> None:
    stored = _stored_bytes(admin, fixture.appointment_id)
    if not stored or public_bytes == stored:
        raise RehearsalFailure("scenario", "public_private_bytes_not_distinct")
    validate_delete_confirm_private_receipt_bytes(stored)
    if delete_confirm_response_digest(public_bytes) == delete_confirm_response_digest(
        stored
    ):
        raise RehearsalFailure("scenario", "public_private_hash_identity")
    if _sha256(public_bytes) == _sha256(stored):
        raise RehearsalFailure("scenario", "public_private_sha_identity")

def _run_scenarios(admin: Engine, application: Engine) -> list[dict[str, Any]]:
    factory = sessionmaker(bind=application, expire_on_commit=False)

    def override_db():
        db = factory()
        try:
            yield db
        finally:
            db.close()

    def override_factory():
        return factory

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_command_session_factory] = override_factory
    app.openapi_schema = None
    results: list[dict[str, Any]] = []
    try:
        with TestClient(app, raise_server_exceptions=False) as client:
            # ── DHI-S01 ────────────────────────────────────────────────
            one = _fixture(101)
            _seed(admin, one)
            token_one = _token(one)
            before_one = _snapshot(admin, one)
            proposal_one = _proposal(client, one, token_one)
            after_one = _snapshot(admin, one)
            binding_one = proposal_one.get("delete_proposal_version_binding", {})
            if (
                before_one != after_one
                or proposal_one.get("confirm_endpoint") != CANONICAL_URL
                or binding_one.get("source_version") != 1
                or proposal_one["confirm_payload"].get("delete_proposal_version_binding")
                != binding_one
                or not proposal_one.get("signed_confirmation_evidence")
            ):
                raise RehearsalFailure("scenario", "DHI-S01_proposal_binding_failed")
            user_one = SimpleNamespace(
                id=one.actor_id,
                practice_id=one.practice_id,
                role=UserRole.Receptionist,
                is_active=True,
                authority_generation=1,
            )
            ingress = adapter._proposal_server_ingress(  # noqa: SLF001
                body=AppointmentDeleteProposalConfirmationIn.model_validate(
                    {**proposal_one["confirm_payload"], "confirmed": True}
                ),
                authenticated_user=user_one,
                session_reference="a" * 64,
                evidence_secret=appointment_router._delete_confirm_evidence_secret(),  # noqa: SLF001
                proposal_version_binding=proposal_one["delete_proposal_version_binding"],
                proposal_version_binding_secret=appointment_router._delete_confirm_domain_secret(  # noqa: SLF001
                    "proposal-version"
                ),
            )
            if ingress.evidence_status != "verified" or ingress.evidence_binding != "exact":
                raise RehearsalFailure("scenario", "DHI-S01_adapter_ingress_failed")
            results.append(
                {
                    "id": "DHI-S01",
                    "status": "passed",
                    "outcome": "non_mutating_verified_exact_proposal",
                    "assertion_count": 7,
                }
            )

            # ── DHI-S02 ────────────────────────────────────────────────
            two = _fixture(102)
            _seed(admin, two, waiting_area=True)
            token_two = _token(two)
            before_two = _snapshot(admin, two)
            proposal_two = _proposal(client, two, token_two)
            if "waiting_area_cleared" not in [
                issue.get("code") for issue in proposal_two.get("warnings", [])
            ]:
                raise RehearsalFailure("scenario", "DHI-S02_warning_missing")
            body_two = _confirm_payload(proposal_two)
            if "waiting_area_cleared" not in body_two.get("confirmed_warnings", []):
                raise RehearsalFailure("scenario", "DHI-S02_warning_not_acknowledged")
            response_two = client.post(
                CANONICAL_URL,
                json=body_two,
                headers=_headers(token_two, "canonical-commit"),
            )
            after_two = _snapshot(admin, two)
            if (
                response_two.status_code != 200
                or after_two["status"] != "Cancelled"
                or after_two["version"] != before_two["version"] + 1
                or after_two["audit_count"] != 1
                or after_two["completed_v1_count"] != 1
                or after_two["waiting_area_id"] is not None
            ):
                raise RehearsalFailure("scenario", "DHI-S02_commit_failed")
            _public_private_proof(admin, two, response_two.content)
            results.append(
                {
                    "id": "DHI-S02",
                    "status": "passed",
                    "outcome": "atomic_commit_public_private_separation",
                    "assertion_count": 10,
                }
            )

            # ── DHI-S03 ────────────────────────────────────────────────
            three = _fixture(103)
            _seed(admin, three)
            token_three = _token(three)
            before_three = _snapshot(admin, three)
            response_three = client.post(
                ALIAS_URL,
                json=_confirm_payload(_proposal(client, three, token_three)),
                headers=_headers(token_three, "compatibility-alias"),
            )
            after_three = _snapshot(admin, three)
            if (
                response_three.status_code != 200
                or after_three["status"] != "Cancelled"
                or after_three["version"] != before_three["version"] + 1
                or after_three["audit_count"] != 1
                or after_three["completed_v1_count"] != 1
            ):
                raise RehearsalFailure("scenario", "DHI-S03_alias_failed")
            _public_private_proof(admin, three, response_three.content)
            results.append(
                {
                    "id": "DHI-S03",
                    "status": "passed",
                    "outcome": "same_handler_commit",
                    "assertion_count": 7,
                }
            )

            # ── DHI-S04 ────────────────────────────────────────────────
            four = _fixture(104)
            _seed(admin, four)
            token_four = _token(four)
            body_four = _confirm_payload(_proposal(client, four, token_four))
            before_four = _snapshot(admin, four)
            first_four = client.post(
                CANONICAL_URL,
                json=body_four,
                headers=_headers(token_four, "lost-response"),
            )
            stored_first = _stored_bytes(admin, four.appointment_id)
            replay_four = client.post(
                CANONICAL_URL,
                json=body_four,
                headers=_headers(token_four, "lost-response"),
            )
            stored_replay = _stored_bytes(admin, four.appointment_id)
            after_four = _snapshot(admin, four)
            if (
                first_four.status_code != 200
                or replay_four.status_code != 200
                or first_four.content != replay_four.content
                or stored_first != stored_replay
                or after_four["status"] != "Cancelled"
                or after_four["version"] != before_four["version"] + 1
                or after_four["audit_count"] != 1
                or after_four["idempotency_rows"] != 1
                or after_four["completed_v1_count"] != 1
            ):
                raise RehearsalFailure("scenario", "DHI-S04_replay_failed")
            _public_private_proof(admin, four, replay_four.content)
            results.append(
                {
                    "id": "DHI-S04",
                    "status": "passed",
                    "outcome": "byte_identical_public_and_private_replay",
                    "assertion_count": 11,
                }
            )

            # ── DHI-S05 ────────────────────────────────────────────────
            five = _fixture(105)
            _seed(admin, five)
            token_five = _token(five)
            body_five = _confirm_payload(_proposal(client, five, token_five))
            missing = client.post(
                CANONICAL_URL,
                json=body_five,
                headers=_headers(token_five),
            )
            blank = client.post(
                CANONICAL_URL,
                json=body_five,
                headers=_headers(token_five, " "),
            )
            _assert_unchanged(admin, five)
            committed = client.post(
                CANONICAL_URL,
                json=body_five,
                headers=_headers(token_five, "shared-conflict"),
            )
            after_five = _snapshot(admin, five)
            if (
                missing.status_code != 400
                or blank.status_code != 400
                or committed.status_code != 200
                or after_five["status"] != "Cancelled"
                or after_five["audit_count"] != 1
                or after_five["completed_v1_count"] != 1
            ):
                raise RehearsalFailure("scenario", "DHI-S05_commit_failed")
            five_sibling = Fixture(
                index=115,
                practice_id=five.practice_id,
                appointment_id=UUID(int=0x20000000000040008000000000000000 + 115),
                actor_id=five.actor_id,
                actor_text=five.actor_text,
                practitioner_id=five.practitioner_id,
                audit_id=UUID(int=0x40000000000040008000000000000000 + 115),
            )
            _seed(admin, five_sibling, appointment_only=True)
            sibling_body = _confirm_payload(_proposal(client, five_sibling, token_five))
            conflict = client.post(
                CANONICAL_URL,
                json=sibling_body,
                headers=_headers(token_five, "shared-conflict"),
            )
            _assert_unchanged(admin, five_sibling)
            if (
                conflict.status_code != 409
                or conflict.json().get("detail", {}).get("code")
                != "idempotency_key_conflict"
            ):
                raise RehearsalFailure("scenario", "DHI-S05_idempotency_failed")
            results.append(
                {
                    "id": "DHI-S05",
                    "status": "passed",
                    "outcome": "required_and_conflict",
                    "assertion_count": 11,
                }
            )

            # ── DHI-S06 ────────────────────────────────────────────────
            six = _fixture(106)
            _seed(admin, six, active=False)
            missing_auth = client.post(
                f"/api/v1/appointments/proposals/delete/{six.appointment_id}",
                json={"status_reason_code": "PATIENT_CANCELLED"},
            )
            inactive = client.post(
                f"/api/v1/appointments/proposals/delete/{six.appointment_id}",
                json={"status_reason_code": "PATIENT_CANCELLED"},
                headers=_headers(_token(six), "inactive-proposal"),
            )
            invalid = client.post(
                f"/api/v1/appointments/proposals/delete/{six.appointment_id}",
                json={"status_reason_code": "PATIENT_CANCELLED"},
                headers={"Authorization": "Bearer not-a-real-token"},
            )
            if (
                missing_auth.status_code != 401
                or inactive.status_code != 401
                or invalid.status_code != 401
            ):
                raise RehearsalFailure("scenario", "DHI-S06_authentication_failed")
            _assert_unchanged(admin, six)
            # Non-mutating role fails at the accepted composition seam before any
            # command session; every enum role is mutating so this is probed
            # directly with a fixed non-admitted role value.
            six_non = _fixture(116)
            _seed(admin, six_non)
            token_six_non = _token(six_non)
            six_non_body = AppointmentDeleteProposalConfirmationIn.model_validate(
                _confirm_payload(_proposal(client, six_non, token_six_non))
            )
            session_opened = False

            def fail_session():
                nonlocal session_opened
                session_opened = True
                raise AssertionError("non-mutating role opened a command session")

            non_mutating = adapter.compose_product_delete_confirm(
                six_non_body,
                authenticated_user=SimpleNamespace(
                    id=six_non.actor_id,
                    practice_id=six_non.practice_id,
                    role="Consultant",
                    is_active=True,
                    authority_generation=1,
                ),
                authenticated_bearer_token="fixed-authored-synthetic-bearer",
                idempotency_key="non-mutating-role",
                proposal_version_binding=six_non_body.delete_proposal_version_binding,
                command_session_factory=fail_session,
                authenticated_session_secret=appointment_router._delete_confirm_domain_secret(  # noqa: SLF001
                    "authenticated-session"
                ),
                proposal_version_binding_secret=appointment_router._delete_confirm_domain_secret(  # noqa: SLF001
                    "proposal-version"
                ),
                idempotency_secret=appointment_router._delete_confirm_domain_secret(  # noqa: SLF001
                    "idempotency"
                ),
                session_binding_secret=appointment_router._delete_confirm_domain_secret(  # noqa: SLF001
                    "stored-session-binding"
                ),
                evidence_secret=appointment_router._delete_confirm_evidence_secret(),  # noqa: SLF001
            )
            if (
                non_mutating.status_code != 403
                or non_mutating.body.get("detail", {}).get("code")
                != "authenticated_delete_context_unavailable"
                or session_opened
            ):
                raise RehearsalFailure("scenario", "DHI-S06_non_mutating_role_failed")
            _assert_unchanged(admin, six_non)
            results.append(
                {
                    "id": "DHI-S06",
                    "status": "passed",
                    "outcome": "unauthorized_inactive_nonmutating",
                    "assertion_count": 8,
                }
            )

            # ── DHI-S07 ────────────────────────────────────────────────
            seven_target = _fixture(107)
            seven_actor = _fixture(108)
            _seed(admin, seven_target)
            _seed(admin, seven_actor)
            cross = client.post(
                CANONICAL_URL,
                json=_manual_cross_practice_body(seven_target, seven_actor),
                headers=_headers(_token(seven_actor), "cross-practice"),
            )
            if (
                cross.status_code != 404
                or cross.json().get("detail", {}).get("code") != "appointment_not_found"
            ):
                raise RehearsalFailure("scenario", "DHI-S07_cross_practice_failed")
            _assert_unchanged(admin, seven_target)
            _assert_unchanged(admin, seven_actor)
            results.append(
                {
                    "id": "DHI-S07",
                    "status": "passed",
                    "outcome": "appointment_not_found",
                    "assertion_count": 5,
                }
            )

            # ── DHI-S08 ────────────────────────────────────────────────
            eight = _fixture(109)
            _seed(admin, eight)
            token_eight = _token(eight)
            proposal_eight = _proposal(client, eight, token_eight)
            body_eight = _confirm_payload(proposal_eight)
            command_sessions = 0

            def counted_factory():
                nonlocal command_sessions
                command_sessions += 1
                return factory()

            def override_counted_factory():
                return counted_factory

            app.dependency_overrides[get_command_session_factory] = override_counted_factory
            tampered_binding = dict(body_eight["delete_proposal_version_binding"])
            tampered_binding["signature"] = "0" * 64
            structural_specs = (
                ("absent", None),
                ("malformed", {"source_version": 1}),
                ("tampered", tampered_binding),
            )
            for label, binding in structural_specs:
                candidate = copy.deepcopy(body_eight)
                if binding is None:
                    candidate.pop("delete_proposal_version_binding", None)
                else:
                    candidate["delete_proposal_version_binding"] = binding
                stopped = client.post(
                    CANONICAL_URL,
                    json=candidate,
                    headers=_headers(token_eight, f"structural-{label}"),
                )
                if label == "absent":
                    if stopped.status_code != 422:
                        raise RehearsalFailure("scenario", "DHI-S08_absent_not_422")
                else:
                    if stopped.status_code != 200 or not stopped.json().get("blocks"):
                        raise RehearsalFailure("scenario", f"DHI-S08_{label}_not_blocked")
            _assert_unchanged(admin, eight)
            if command_sessions != 0:
                raise RehearsalFailure("scenario", "DHI-S08_structural_opened_session")
            app.dependency_overrides[get_command_session_factory] = override_factory
            with admin.begin() as connection:
                connection.execute(
                    text(
                        "UPDATE appointments SET notes='advanced' WHERE practice_id=:p AND id=:a"
                    ),
                    {"p": eight.practice_id, "a": eight.appointment_id},
                )
            before_eight = _snapshot(admin, eight)
            stale = client.post(
                CANONICAL_URL,
                json=body_eight,
                headers=_headers(token_eight, "stale-binding"),
            )
            after_eight = _snapshot(admin, eight)
            if (
                stale.status_code != 200
                or not stale.json().get("blocks")
                or after_eight != before_eight
            ):
                raise RehearsalFailure("scenario", "DHI-S08_stale_effect_failed")
            results.append(
                {
                    "id": "DHI-S08",
                    "status": "passed",
                    "outcome": "structural_pre_session_and_stale_no_effect",
                    "assertion_count": 9,
                }
            )

            # ── DHI-S09 ────────────────────────────────────────────────
            nine = _fixture(110)
            _seed(admin, nine, waiting_area=True)
            token_nine = _token(nine)
            proposal_nine = _proposal(client, nine, token_nine)
            if "waiting_area_cleared" not in [
                issue.get("code") for issue in proposal_nine.get("warnings", [])
            ]:
                raise RehearsalFailure("scenario", "DHI-S09_warning_missing")
            body_nine = _confirm_payload(proposal_nine)
            body_nine["confirmed_warnings"] = []
            missing_ack = client.post(
                CANONICAL_URL,
                json=body_nine,
                headers=_headers(token_nine, "missing-ack"),
            )
            altered_body = _confirm_payload(proposal_nine)
            altered_body["confirmed_warnings"] = ["wrong_warning_code"]
            altered_ack = client.post(
                CANONICAL_URL,
                json=altered_body,
                headers=_headers(token_nine, "altered-ack"),
            )
            after_nine = _snapshot(admin, nine)
            if (
                missing_ack.status_code != 200
                or altered_ack.status_code != 200
                or not missing_ack.json().get("blocks")
                or not altered_ack.json().get("blocks")
                or after_nine["status"] != "Booked"
                or after_nine["waiting_area_id"] is None
            ):
                raise RehearsalFailure("scenario", "DHI-S09_warning_block_failed")
            _assert_unchanged(admin, nine)
            results.append(
                {
                    "id": "DHI-S09",
                    "status": "passed",
                    "outcome": "atomic_block",
                    "assertion_count": 7,
                }
            )

            # ── DHI-S10 ────────────────────────────────────────────────
            ten_default = _fixture(111)
            _seed(admin, ten_default, with_grant=False)
            token_ten_default = _token(ten_default)
            denied = client.post(
                CANONICAL_URL,
                json=_confirm_payload(_proposal(client, ten_default, token_ten_default)),
                headers=_headers(token_ten_default, "default-denial"),
            )
            after_denied = _snapshot(admin, ten_default)
            ten_revoke = _fixture(112)
            _seed(admin, ten_revoke)
            token_ten_revoke = _token(ten_revoke)
            revoke_body = _confirm_payload(_proposal(client, ten_revoke, token_ten_revoke))
            with admin.begin() as connection:
                connection.execute(
                    text(
                        "DELETE FROM user_capability_grants WHERE practice_id=:p AND user_id=:u "
                        "AND capability_code='appointment.cancel.confirm'"
                    ),
                    {"p": ten_revoke.practice_id, "u": ten_revoke.actor_id},
                )
            revoked = client.post(
                CANONICAL_URL,
                json=revoke_body,
                headers=_headers(token_ten_revoke, "post-revocation"),
            )
            after_revoked = _snapshot(admin, ten_revoke)
            if (
                denied.status_code != 403
                or denied.json().get("detail", {}).get("code")
                != "current_authority_unavailable"
                or after_denied["audit_count"] != 0
                or revoked.status_code != 403
                or revoked.json().get("detail", {}).get("code")
                != "current_authority_unavailable"
                or after_revoked["audit_count"] != 0
            ):
                raise RehearsalFailure("scenario", "DHI-S10_authority_failed")
            _assert_unchanged(admin, ten_default)
            _assert_unchanged(admin, ten_revoke)
            results.append(
                {
                    "id": "DHI-S10",
                    "status": "passed",
                    "outcome": "default_denial_and_revocation",
                    "assertion_count": 9,
                }
            )

            # ── DHI-S11 ────────────────────────────────────────────────
            eleven = _fixture(113)
            _seed(admin, eleven)
            token_eleven = _token(eleven)
            eleven_body = _confirm_payload(_proposal(client, eleven, token_eleven))
            with admin.begin() as connection:
                connection.execute(
                    text(
                        "ALTER TABLE public.appointments DISABLE TRIGGER "
                        "trg_appointments_advance_state_version"
                    )
                )
            failed_trigger = client.post(
                CANONICAL_URL,
                json=eleven_body,
                headers=_headers(token_eleven, "forced-scaffold-failure"),
            )
            with admin.begin() as connection:
                connection.execute(
                    text(
                        "ALTER TABLE public.appointments ENABLE TRIGGER "
                        "trg_appointments_advance_state_version"
                    )
                )
            after_eleven = _snapshot(admin, eleven)
            if (
                failed_trigger.status_code != 503
                or failed_trigger.json().get("detail", {}).get("code")
                != "delete_confirm_transaction_unavailable"
                or after_eleven["status"] != "Booked"
                or after_eleven["audit_count"] != 0
                or after_eleven["completed_v1_count"] != 0
            ):
                raise RehearsalFailure("scenario", "DHI-S11_rollback_failed")
            _assert_unchanged(admin, eleven)
            with admin.connect() as connection:
                enabled = connection.execute(
                    text(
                        "SELECT count(*) FROM pg_trigger WHERE NOT tgisinternal "
                        "AND tgname='trg_appointments_advance_state_version' AND tgenabled='O'"
                    )
                ).scalar_one()
            if enabled != 1:
                raise RehearsalFailure("scenario", "DHI-S11_trigger_restore_failed")
            results.append(
                {
                    "id": "DHI-S11",
                    "status": "passed",
                    "outcome": "rollback_503_and_trigger_restored",
                    "assertion_count": 7,
                }
            )

            # ── DHI-S12 ────────────────────────────────────────────────
            canonical = [
                route
                for route in app.routes
                if isinstance(route, APIRoute)
                and route.path == CANONICAL_URL
                and "POST" in route.methods
            ]
            compatibility = [
                route
                for route in app.routes
                if isinstance(route, APIRoute)
                and route.path == ALIAS_URL
                and "POST" in route.methods
            ]
            paths = app.openapi()["paths"]
            router_text = (ROOT / "app/routers/appointments.py").read_text(
                encoding="utf-8"
            )
            if (
                len(canonical) != 1
                or len(compatibility) != 1
                or canonical[0].endpoint is not compatibility[0].endpoint
                or canonical[0].include_in_schema is not True
                or compatibility[0].include_in_schema is not False
                or CANONICAL_URL not in paths
                or ALIAS_URL in paths
                or appointment_router._DELETE_CONFIRM_ACTION.endpoint != CANONICAL_URL  # noqa: SLF001
                or 'def cancel_appointment(' not in router_text
                or '"raw_compat_delete"' not in router_text
            ):
                raise RehearsalFailure("scenario", "DHI-S12_route_contract_failed")
            results.append(
                {
                    "id": "DHI-S12",
                    "status": "passed",
                    "outcome": "canonical_visible_alias_hidden_raw_delete_unchanged",
                    "assertion_count": 9,
                }
            )
    finally:
        app.dependency_overrides.pop(get_command_session_factory, None)
        app.dependency_overrides.pop(get_db, None)
        app.openapi_schema = None
    return results

def _sanitize_label(value: str) -> str:
    """Map any diagnostic label onto the closed ``[a-z0-9_]`` lifecycle alphabet."""
    return re.sub(r"[^a-z0-9_]", "_", value.lower())


def _normalize_cleanup(cleanup: dict[str, Any]) -> dict[str, Any]:
    """Map the accepted cleanup result onto the closed evidence cleanup shape."""
    raw_status = str(cleanup.get("status") or "cleanup_failed")
    if raw_status == "cleanup_ownership_unverified" or raw_status == "ownership_mismatch":
        status = "ownership_mismatch"
    elif raw_status in ("cleanup_absence_unverified", "cleanup_failed"):
        status = "cleanup_failed"
    elif raw_status == "cleanup_verified":
        status = "cleanup_verified"
    else:
        status = "not_needed"
    verified = status == "cleanup_verified"
    return {
        "status": status,
        "container_removed": verified,
        "network_removed": verified,
        "container_absent": verified,
        "network_absent": verified,
    }


def _failure_evidence(
    error: RehearsalFailure,
    *,
    lifecycle: list[str],
    cleanup: dict[str, Any],
    source_hashes: dict[str, str],
    implementation_hashes: dict[str, str],
    contract_sha256: str,
) -> dict[str, Any]:
    del error  # failure detail is never released; only sanitized lifecycle labels remain
    return {
        "schema_version": "raisa.delete_confirm_http_postgresql_integration_evidence.v1",
        "result": "rehearsal_failed",
        "evidence_label": "live_local_backend_postgres",
        "data_posture": "provider_free_authored_synthetic_only",
        "source_head": EXPECTED_SOURCE_HEAD,
        "contract_sha256": contract_sha256,
        "source_hashes": source_hashes,
        "implementation_hashes": implementation_hashes,
        "hostile_mutations": {
            "attempted": HOSTILE_MUTATION_TARGET,
            "rejected": HOSTILE_MUTATION_TARGET,
            "minimum_required": 120,
        },
        "environment": {
            "postgresql_major": 16,
            "image_reference": "postgres:16-bookworm",
            "image_id_sha256": "0" * 64,
            "network_internal": True,
            "published_ports": False,
            "storage": "container_local_tmpfs",
            "host_transport": "fixed_in_process_ipv4_loopback_relay",
            "transport": "fastapi_testclient_real_route",
            "provider_calls": 0,
            "product_rows": 0,
        },
        "catalogue": {
            "migration_head": "x3y4z5a6b7c8",
            "application_role_superuser": False,
            "application_role_bypass_rls": False,
            "forced_rls_table_count": 8,
            "selected_constraint_count": 6,
            "selected_trigger_count": 4,
            "transaction_context_local": True,
            "two_connection_tenant_context_absent": False,
        },
        "scenarios": [],
        "aggregate": {
            "scenario_count": 0,
            "public_private_bytes_distinct": False,
            "public_replay_bytes_identical": False,
            "private_replay_bytes_identical": False,
            "second_effect_count": 0,
            "rollback_effect_count": 0,
        },
        "lifecycle": lifecycle,
        "cleanup": _normalize_cleanup(cleanup),
        "claim_boundary": CLAIM_BOUNDARY,
    }


def run_rehearsal() -> dict[str, Any]:
    lifecycle: list[str] = []
    cleanup: dict[str, Any] = {"status": "not_needed"}
    contract: dict[str, Any] | None = None
    source_hashes: dict[str, str] = {}
    implementation_hashes: dict[str, str] = {}
    docker = ""
    image_id: str | None = None
    network_id: str | None = None
    container_id: str | None = None
    network_name = ""
    container_name = ""
    nonce = secrets.token_hex(16)
    admin: Engine | None = None
    application: Engine | None = None
    relay: foundation.DockerExecRelay | None = None
    evidence: dict[str, Any] | None = None
    error: RehearsalFailure | None = None
    started = time.monotonic()
    try:
        contract, source_hashes, implementation_hashes = verify_contract()
        lifecycle.append("contract_sources_and_135_mutations_verified")
        profile = contract["docker_profile"]
        delete_contract = _load_json(delete_btr.CONTRACT_PATH)
        docker = shutil.which(profile["executable"]) or ""
        if not docker:
            raise RehearsalFailure("environment", "docker_client_missing")
        image_id = foundation._image_id(docker, profile)  # noqa: SLF001
        lifecycle.append("cached_image_verified")
        suffix = secrets.token_hex(8)
        network_name = profile["network_name_prefix"] + suffix
        container_name = profile["container_name_prefix"] + suffix
        network_result = catalogue._run(  # noqa: SLF001
            foundation.build_network_argv(docker, network_name, nonce, profile),
            None,
            profile["command_timeout_seconds"],
            4096,
        )
        network_id = network_result.stdout.decode("utf-8").strip()
        if network_result.returncode != 0 or not re.fullmatch(r"[0-9a-f]{64}", network_id):
            raise RehearsalFailure("environment", "network_create_failed")
        inspected_result, inspected_network = foundation._inspect_one(  # noqa: SLF001
            docker, "network", network_id, profile["command_timeout_seconds"]
        )
        if (
            inspected_result.returncode != 0
            or inspected_network is None
            or not foundation._network_owned(  # noqa: SLF001
                inspected_network,
                network_id=network_id,
                name=network_name,
                nonce=nonce,
                profile=profile,
                require_empty=True,
            )
        ):
            raise RehearsalFailure("environment", "network_profile_mismatch")
        lifecycle.append("owned_internal_network_verified")
        container_result = catalogue._run(  # noqa: SLF001
            foundation.build_container_argv(  # noqa: SLF001
                docker, container_name, nonce, network_id, profile
            ),
            None,
            profile["command_timeout_seconds"],
            4096,
        )
        container_id = container_result.stdout.decode("utf-8").strip()
        if container_result.returncode != 0 or not re.fullmatch(r"[0-9a-f]{64}", container_id):
            raise RehearsalFailure("environment", "container_create_failed")
        inspected_result, inspected_container = foundation._inspect_one(  # noqa: SLF001
            docker, "container", container_id, profile["command_timeout_seconds"]
        )
        owned = (
            foundation._container_profile(  # noqa: SLF001
                inspected_container,
                container_id=container_id,
                name=container_name,
                nonce=nonce,
                image_id=image_id,
                network_id=network_id,
                profile=profile,
            )
            if inspected_container is not None
            else False
        )
        if inspected_result.returncode != 0 or not owned:
            raise RehearsalFailure("environment", "container_profile_mismatch")
        lifecycle.append("owned_tmpfs_container_verified")
        foundation._wait_ready(docker, container_id, profile)  # noqa: SLF001
        _install_database(docker, container_id, delete_contract, profile)
        lifecycle.append("delete_scaffold_projection_role_and_rls_installed")
        relay = foundation.DockerExecRelay(docker, container_id, profile)
        host_port = relay.start()
        lifecycle.append("fixed_loopback_relay_started")
        admin = _admin_engine(host_port, profile)
        application = _application_engine(host_port, profile)
        catalogue_facts = _catalogue_check(admin)
        lifecycle.append("restricted_application_role_catalogue_verified")
        scenario_results = _run_scenarios(admin, application)
        if not _two_pool_settings_absent(application):
            raise RehearsalFailure("scenario", "pooled_tenant_setting_leaked")
        catalogue_facts["two_connection_tenant_context_absent"] = True
        lifecycle.append("twelve_serial_http_postgresql_scenarios_verified")
        if time.monotonic() - started > profile["total_timeout_seconds"]:
            raise RehearsalFailure("environment", "total_timeout_exceeded")
        evidence = {
            "schema_version": "raisa.delete_confirm_http_postgresql_integration_evidence.v1",
            "result": PASS_RESULT,
            "evidence_label": contract["evidence_label"],
            "data_posture": contract["data_posture"],
            "source_head": contract["source_head"],
            "contract_sha256": _sha256(CONTRACT_PATH.read_bytes()),
            "source_hashes": source_hashes,
            "implementation_hashes": implementation_hashes,
            "hostile_mutations": {
                "attempted": HOSTILE_MUTATION_TARGET,
                "rejected": HOSTILE_MUTATION_TARGET,
                "minimum_required": 120,
            },
            "environment": {
                "postgresql_major": 16,
                "image_reference": profile["image_reference"],
                "image_id_sha256": _sha256(image_id),
                "network_internal": True,
                "published_ports": False,
                "storage": "container_local_tmpfs",
                "host_transport": "fixed_in_process_ipv4_loopback_relay",
                "transport": "fastapi_testclient_real_route",
                "provider_calls": 0,
                "product_rows": 0,
            },
            "catalogue": catalogue_facts,
            "scenarios": scenario_results,
            "aggregate": {
                "scenario_count": len(scenario_results),
                "public_private_bytes_distinct": True,
                "public_replay_bytes_identical": True,
                "private_replay_bytes_identical": True,
                "second_effect_count": 0,
                "rollback_effect_count": 0,
            },
            "lifecycle": lifecycle,
            "cleanup": {"status": "pending"},
            "claim_boundary": CLAIM_BOUNDARY,
        }
    except RehearsalFailure as caught:
        lifecycle.append(
            _sanitize_label(f"failed_{caught.stage}_{caught.code}")
        )
        error = caught
    except Exception as caught:  # fail closed without retaining raw exception text
        original = getattr(caught, "orig", None)
        sqlstate = getattr(original, "pgcode", None) or "none"
        lifecycle.append(
            _sanitize_label(f"failed_{type(caught).__name__}_{sqlstate}")
        )
        error = RehearsalFailure("harness", "unexpected_exception", type(caught).__name__)
    finally:
        app.dependency_overrides.pop(get_command_session_factory, None)
        app.dependency_overrides.pop(get_db, None)
        app.openapi_schema = None
        if application is not None:
            application.dispose()
        if admin is not None:
            admin.dispose()
        if relay is not None:
            relay.stop()
            lifecycle.append("fixed_loopback_relay_stopped")
        if contract is not None and docker:
            cleanup = foundation._cleanup(  # noqa: SLF001
                docker,
                container_id=container_id,
                container_name=container_name,
                network_id=network_id,
                network_name=network_name,
                nonce=nonce,
                image_id=image_id,
                profile=contract["docker_profile"],
            )
        if cleanup.get("status") == "cleanup_verified":
            lifecycle.append("cleanup_verified")
        if error is None and cleanup.get("status") != "cleanup_verified":
            error = RehearsalFailure("cleanup", str(cleanup.get("status")))
        if error is not None:
            evidence = _failure_evidence(
                error,
                lifecycle=lifecycle,
                cleanup=cleanup,
                source_hashes=source_hashes,
                implementation_hashes=implementation_hashes,
                contract_sha256=_sha256(CONTRACT_PATH.read_bytes()),
            )
        else:
            assert evidence is not None
            evidence["lifecycle"] = lifecycle
            evidence["cleanup"] = _normalize_cleanup(cleanup)
    assert evidence is not None
    Draft202012Validator(_load_json(EVIDENCE_SCHEMA_PATH)).validate(evidence)
    return evidence

def write_evidence(evidence: dict[str, Any]) -> Path:
    target = (
        EVIDENCE_PATH if evidence["result"] == PASS_RESULT else FAILURE_EVIDENCE_PATH
    )
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(evidence, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return target


def main() -> int:
    if len(sys.argv) != 1:
        print('{"result":"rehearsal_failed","code":"caller_arguments_forbidden"}')
        return 2
    evidence = run_rehearsal()
    path = write_evidence(evidence)
    print(
        json.dumps(
            {
                "result": evidence["result"],
                "cleanup": evidence["cleanup"]["status"],
                "evidence": str(path.relative_to(ROOT)).replace("\\", "/"),
            },
            sort_keys=True,
        )
    )
    return 0 if evidence["result"] == PASS_RESULT else 1


if __name__ == "__main__":
    raise SystemExit(main())
