"""Provider-free read-only delete-confirm route-mounting readiness review.

This module performs a bounded, read-only classification review of the
delete-confirm route-mounting readiness state.  It never imports ``app``,
never mounts or calls a route, never opens a database/Docker/SQL/provider/
network surface and never reads configuration values or credentials.

Authority boundary
------------------
Only the exact 23 contract inputs listed in the frozen route-mounting
readiness-review contract and the four freeze artifacts
(docs/raisa-provider-free-read-only-delete-confirm-route-mounting-readiness-review-plan.md,
docs/security/raisa-provider-free-read-only-delete-confirm-route-mounting-readiness-review-threat-model-delta.md,
orchestration/continuity/raisa-provider-free-read-only-delete-confirm-route-mounting-readiness-review/route-mounting-readiness-review-contract.json
and route-mounting-readiness-review-contract.schema.json) are read.

Exact owned outputs
-------------------
1. scripts/raisa_provider_free_read_only_delete_confirm_route_mounting_readiness_review.py
2. tests/test_raisa_provider_free_read_only_delete_confirm_route_mounting_readiness_review.py
3. tests/test_raisa_provider_free_read_only_delete_confirm_route_mounting_readiness_review_plan.py
4. orchestration/continuity/raisa-provider-free-read-only-delete-confirm-route-mounting-readiness-review/provider-free-read-only-evidence.json
5. orchestration/continuity/raisa-provider-free-read-only-delete-confirm-route-mounting-readiness-review/route-mounting-readiness-review-report.md

The review proves all 23 strict UTF-8 canonical-LF (bare-CR rejected) SHA-256
bindings before classifying the twelve frozen dimensions.  The expected
evidence-led matrix is exactly seven ``satisfied``, five ``route_transition_gap``
and zero ``blocking_gap`` dimensions, yielding
``ready_for_bounded_route_convergence_candidate``.  The script fails closed when
the current evidence does not support that matrix.
"""

from __future__ import annotations

import argparse
import ast
import copy
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Tuple

# ---------------------------------------------------------------------------
# Frozen constants (mirror the frozen contract and plan).
# ---------------------------------------------------------------------------

EXPECTED_SCHEMA_VERSION = "raisa.delete_confirm_route_mounting_readiness_review_contract.v1"
EXPECTED_INPUT_HASH_MODE = "strict_utf8_canonical_lf_reject_bare_cr_sha256"
EXPECTED_SOURCE_HEAD = "0e627d7347e4a0370931d29b3e705eefe12fd881"
EXPECTED_CLASSIFICATIONS = ("satisfied", "route_transition_gap", "blocking_gap")

EXPECTED_VERDICT_RULES = {
    "any_blocking_gap": "route_mounting_not_ready",
    "no_blocker_with_transition_gap": "ready_for_bounded_route_convergence_candidate",
    "all_satisfied": "route_convergence_already_complete",
}

EXPECTED_INPUT_PATHS = (
    "app/main.py",
    "app/routers/appointments.py",
    "app/dependencies.py",
    "app/config.py",
    "app/schemas/appointments.py",
    "app/services/diary/confirm_actions.py",
    "app/services/appointment_delete_product_adapter.py",
    "app/services/appointment_delete_composition.py",
    "app/services/appointment_delete_physical.py",
    "app/services/bernie_turn_evidence.py",
    "app/services/appointment_idempotency.py",
    "docs/api-spine/openapi/appointment-commands.yaml",
    "orchestration/api_spine_appointment_command_alignment_inventory.md",
    "tests/test_api_spine_appointment_openapi_drift_guard.py",
    "tests/test_api_spine_appointment_command_alignment_inventory.py",
    "docs/raisa-provider-free-read-only-delete-confirm-route-convergence-review.md",
    "docs/raisa-provider-free-unmounted-delete-confirm-response-compatibility-product-adapter-architecture.md",
    "docs/raisa-provider-free-unmounted-delete-confirm-composition-product-adapter-implementation-closeout.md",
    "docs/raisa-provider-free-status-confirm-http-route-convergence-plan.md",
    "docs/raisa-provider-free-disposable-postgresql-delete-confirm-behavior-transaction-rehearsal-closeout.md",
    "orchestration/continuity/raisa-provider-free-disposable-postgresql-delete-confirm-behavior-transaction-rehearsal/provider-free-behavior-transaction-evidence.json",
    "orchestration/continuity/raisa-delete-confirm-route-convergence-and-ariadne-git-object-resolution/route-convergence-contract.json",
    "orchestration/continuity/raisa-delete-confirm-route-convergence-and-ariadne-git-object-resolution/provider-free-read-only-evidence.json",
)

EXPECTED_DIMENSIONS = (
    (1, "literal_mounting", "satisfied"),
    (2, "canonical_identity_and_alias", "route_transition_gap"),
    (3, "proposal_version_binding_carriage", "route_transition_gap"),
    (4, "server_authority_and_session_ingress", "route_transition_gap"),
    (5, "physical_seam_composition", "satisfied"),
    (6, "locked_current_truth_readmission", "satisfied"),
    (7, "atomic_effect_audit_private_receipt", "satisfied"),
    (8, "public_response_schema", "route_transition_gap"),
    (9, "canonical_public_byte_delivery", "route_transition_gap"),
    (10, "closed_outcome_http_mapping", "satisfied"),
    (11, "raw_delete_isolation", "satisfied"),
    (12, "accepted_postgresql_foundation", "satisfied"),
)

EXPECTED_TRANSITION_GAPS = (
    "canonical_identity_and_alias",
    "proposal_version_binding_carriage",
    "server_authority_and_session_ingress",
    "public_response_schema",
    "canonical_public_byte_delivery",
)

EXPECTED_ACCEPTANCE = {
    "expected_counts": {"satisfied": 7, "route_transition_gap": 5, "blocking_gap": 0},
    "expected_verdict": "ready_for_bounded_route_convergence_candidate",
    "minimum_hostile_mutations": 72,
    "require_exact_dimension_order": True,
    "require_exact_source_citations": True,
    "require_private_public_byte_separation": True,
    "require_no_app_import": True,
}

EXPECTED_FORBIDDEN_SURFACES = (
    "route_edit_mount_call_or_http_transport",
    "schema_model_migration_or_api_spine_edit",
    "database_docker_sql_source_or_watcher_access",
    "capability_product_command_or_product_data",
    "provider_adc_credentials_iam_browser_or_network",
    "ui_deployment_production_release_pages_or_protected_refs",
    "protected_evidence_and_docs_branding",
)

CONTRACT_RELATIVE_PATH = (
    "orchestration/continuity/raisa-provider-free-read-only-delete-confirm-route-mounting-readiness-review"
    "/route-mounting-readiness-review-contract.json"
)
EVIDENCE_RELATIVE_PATH = (
    "orchestration/continuity/raisa-provider-free-read-only-delete-confirm-route-mounting-readiness-review"
    "/provider-free-read-only-evidence.json"
)
REPORT_RELATIVE_PATH = (
    "orchestration/continuity/raisa-provider-free-read-only-delete-confirm-route-mounting-readiness-review"
    "/route-mounting-readiness-review-report.md"
)

RESULT_PASS = "raisa_provider_free_read_only_delete_confirm_route_mounting_readiness_review_pass"
EVIDENCE_SCHEMA_VERSION = "raisa.delete_confirm_route_mounting_readiness_evidence.v1"


class ContractValidationError(RuntimeError):
    """Raised when a contract does not match the frozen contract."""


class EvidenceError(RuntimeError):
    """Raised when the current evidence cannot prove the expected matrix."""


# ---------------------------------------------------------------------------
# Strict UTF-8 canonical-LF hashing with bare-CR rejection.
# ---------------------------------------------------------------------------


def _read_canonical_text(path: Path) -> str:
    """Read a file as strict UTF-8 canonical LF text.

    Rejects any bare carriage-return byte (a ``\r`` not immediately followed by
    ``\n``) and normalises CRLF to LF so hashes are checkout-stable.
    """
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise ValueError(f"cannot read {path}: {exc}") from exc
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(f"non-UTF-8 content in {path}") from exc
    if "\r" in text.replace("\r\n", ""):
        raise ValueError(f"bare CR in {path}")
    return text.replace("\r\n", "\n")


def strict_canonical_lf_sha256(path: Path) -> str:
    """Return the strict UTF-8 canonical-LF SHA-256 of ``path``."""
    return hashlib.sha256(_read_canonical_text(path).encode("utf-8")).hexdigest()


def _canonical_lf_hash_bytes(data: bytes) -> str:
    """Hash a byte string with the same canonical-LF/bare-CR rules.

    Used by the hostile hash-mode unit tests without touching the filesystem.
    """
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("non-UTF-8 content") from exc
    if "\r" in text.replace("\r\n", ""):
        raise ValueError("bare CR")
    return hashlib.sha256(text.replace("\r\n", "\n").encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Contract loading and validation.
# ---------------------------------------------------------------------------


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ContractValidationError(f"cannot read contract {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ContractValidationError(f"invalid JSON in {path}: {exc}") from exc


def load_contract(repo_root: Path) -> Dict[str, Any]:
    return _load_json(repo_root / CONTRACT_RELATIVE_PATH)


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ContractValidationError(message)


def validate_contract(contract: Dict[str, Any], repo_root: Path) -> None:
    """Validate a contract against the frozen contract and live file hashes.

    Every check is deterministic.  Any divergence raises
    :class:`ContractValidationError`, which is how the hostile mutation suite
    counts a rejected mutation.
    """
    top_keys = {
        "schema_version",
        "source_head",
        "input_hash_mode",
        "inputs",
        "classifications",
        "verdict_rules",
        "dimensions",
        "acceptance",
        "forbidden_surfaces",
    }
    _require(set(contract) == top_keys, "top-level contract keys changed")
    _require(contract.get("schema_version") == EXPECTED_SCHEMA_VERSION, "schema_version changed")
    _require(
        isinstance(contract.get("source_head"), str)
        and re.fullmatch(r"[0-9a-f]{40}", contract["source_head"]) is not None,
        "source_head is not a 40-hex commit",
    )
    _require(contract["source_head"] == EXPECTED_SOURCE_HEAD, "source_head changed")
    _require(contract.get("input_hash_mode") == EXPECTED_INPUT_HASH_MODE, "input_hash_mode changed")
    _require(tuple(contract.get("classifications", ())) == EXPECTED_CLASSIFICATIONS, "classifications changed")
    _require(contract.get("verdict_rules") == EXPECTED_VERDICT_RULES, "verdict_rules changed")

    # Inputs: exact frozen paths, in exact order, with a 64-hex sha256 each.
    inputs = contract.get("inputs")
    _require(isinstance(inputs, list) and len(inputs) == 23, "inputs count is not 23")
    paths: List[str] = []
    for item in inputs:
        _require(
            isinstance(item, dict) and set(item) == {"path", "sha256"},
            "input entry shape changed",
        )
        _require(
            isinstance(item.get("sha256"), str) and re.fullmatch(r"[0-9a-f]{64}", item["sha256"]) is not None,
            "input sha256 is not 64-hex",
        )
        paths.append(item["path"])
    _require(tuple(paths) == EXPECTED_INPUT_PATHS, "input path set/order changed")

    # Dimensions: exactly 12, exact order, exact ids/classifications.
    dimensions = contract.get("dimensions")
    _require(isinstance(dimensions, list) and len(dimensions) == 12, "dimensions count is not 12")
    dim_tuples: List[Tuple[int, str, str]] = []
    for dim in dimensions:
        _require(
            isinstance(dim, dict) and set(dim) == {"order", "id", "expected_classification", "question"},
            "dimension shape changed",
        )
        _require(isinstance(dim["order"], int), "dimension order must be int")
        _require(isinstance(dim["id"], str), "dimension id must be str")
        _require(
            dim["expected_classification"] in EXPECTED_CLASSIFICATIONS,
            "dimension classification not in vocabulary",
        )
        _require(isinstance(dim["question"], str) and dim["question"], "dimension question invalid")
        dim_tuples.append((dim["order"], dim["id"], dim["expected_classification"]))
    _require(tuple(dim_tuples) == EXPECTED_DIMENSIONS, "dimensions order/id/classification changed")

    # Acceptance and forbidden surfaces.
    _require(contract.get("acceptance") == EXPECTED_ACCEPTANCE, "acceptance fields changed")
    _require(
        tuple(contract.get("forbidden_surfaces", ())) == EXPECTED_FORBIDDEN_SURFACES,
        "forbidden_surfaces changed",
    )

    # Live file hash bindings (all 23).
    for item in inputs:
        path = repo_root / item["path"]
        try:
            actual = strict_canonical_lf_sha256(path)
        except (OSError, ValueError) as exc:
            raise ContractValidationError(f"cannot hash {item['path']}: {exc}") from exc
        _require(actual == item["sha256"], f"sha256 mismatch for {item['path']}")


# ---------------------------------------------------------------------------
# Source text loading.
# ---------------------------------------------------------------------------


def load_source_texts(contract: Dict[str, Any], repo_root: Path) -> Dict[str, str]:
    texts: Dict[str, str] = {}
    for item in contract["inputs"]:
        texts[item["path"]] = _read_canonical_text(repo_root / item["path"])
    return texts


def _text(texts: Dict[str, str], path: str) -> str:
    return texts.get(path, "")


def _extract_function_body(source: str, func_name: str) -> str:
    """Return the exact source slice of one top-level function.

    Uses only the standard-library ``ast`` module; no ``app`` import.
    """
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        raise EvidenceError(func_name, f"source is not parseable: {exc}") from exc
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == func_name:
            lines = source.splitlines()
            return "\n".join(lines[node.lineno - 1 : node.end_lineno])
    raise EvidenceError(func_name, f"function {func_name!r} not found in source")


# ---------------------------------------------------------------------------
# Per-dimension evidence proofs.
# ---------------------------------------------------------------------------


def _prove_literal_mounting(texts: Dict[str, str]) -> Tuple[str, List[str], List[str]]:
    main = _text(texts, "app/main.py")
    router = _text(texts, "app/routers/appointments.py")
    inventory = _text(texts, "orchestration/api_spine_appointment_command_alignment_inventory.md")
    markers: List[str] = []
    if "app.include_router(appointments.router)" not in main:
        raise EvidenceError("literal_mounting", "appointments router not included in app/main.py")
    markers.append("appointments_router_included")
    if '"/proposals/delete-confirm"' not in router:
        raise EvidenceError("literal_mounting", "historical delete-confirm route not mounted")
    markers.append("historical_delete_confirm_route_mounted")
    if "def confirm_delete_proposal_route(" not in router:
        raise EvidenceError("literal_mounting", "delete-confirm handler missing")
    markers.append("delete_confirm_handler_present")
    if "POST /api/v1/appointments/proposals/delete-confirm" not in inventory:
        raise EvidenceError("literal_mounting", "API Spine inventory missing delete-confirm route")
    markers.append("api_spine_inventory_lists_delete_confirm")
    return (
        "satisfied",
        [
            "app/main.py",
            "app/routers/appointments.py",
            "orchestration/api_spine_appointment_command_alignment_inventory.md",
        ],
        markers,
    )


def _prove_canonical_identity_and_alias(texts: Dict[str, str]) -> Tuple[str, List[str], List[str]]:
    router = _text(texts, "app/routers/appointments.py")
    openapi = _text(texts, "docs/api-spine/openapi/appointment-commands.yaml")
    inventory = _text(texts, "orchestration/api_spine_appointment_command_alignment_inventory.md")
    drift_guard = _text(texts, "tests/test_api_spine_appointment_openapi_drift_guard.py")
    confirm_actions = _text(texts, "app/services/diary/confirm_actions.py")
    markers: List[str] = []
    if '"/proposals/delete/confirm"' in router:
        raise EvidenceError("canonical_identity_and_alias", "canonical delete-confirm route unexpectedly mounted")
    markers.append("canonical_delete_confirm_not_mounted")
    if '"/proposals/delete-confirm"' not in router:
        raise EvidenceError("canonical_identity_and_alias", "hyphenated alias not mounted")
    markers.append("hyphenated_alias_mounted")
    if "/appointments/proposals/delete/confirm:" not in openapi:
        raise EvidenceError("canonical_identity_and_alias", "canonical path not documented in OpenAPI")
    markers.append("canonical_path_documented_in_openapi")
    if "confirmAppointmentDeleteProposal" not in openapi:
        raise EvidenceError("canonical_identity_and_alias", "operation id not aligned")
    markers.append("operation_id_aligned")
    if "/appointments/proposals/delete/confirm" not in inventory:
        raise EvidenceError("canonical_identity_and_alias", "inventory missing canonical drift")
    markers.append("inventory_documents_canonical_drift")
    if "/appointments/proposals/delete/confirm" not in drift_guard:
        raise EvidenceError("canonical_identity_and_alias", "drift guard missing canonical path")
    markers.append("drift_guard_tracks_canonical_path")
    if "delete-confirm" not in confirm_actions:
        raise EvidenceError("canonical_identity_and_alias", "diary confirm action endpoint missing")
    markers.append("diary_confirm_action_uses_hyphenated_endpoint")
    return (
        "route_transition_gap",
        [
            "app/routers/appointments.py",
            "docs/api-spine/openapi/appointment-commands.yaml",
            "orchestration/api_spine_appointment_command_alignment_inventory.md",
            "tests/test_api_spine_appointment_openapi_drift_guard.py",
            "app/services/diary/confirm_actions.py",
        ],
        markers,
    )


def _prove_proposal_version_binding_carriage(texts: Dict[str, str]) -> Tuple[str, List[str], List[str]]:
    adapter = _text(texts, "app/services/appointment_delete_product_adapter.py")
    router = _text(texts, "app/routers/appointments.py")
    architecture = _text(
        texts,
        "docs/raisa-provider-free-unmounted-delete-confirm-response-compatibility-product-adapter-architecture.md",
    )
    handler = _extract_function_body(router, "confirm_delete_proposal_route")
    markers: List[str] = []
    if "def mint_delete_proposal_version_binding(" not in adapter:
        raise EvidenceError("proposal_version_binding_carriage", "adapter missing delete version-binding mint")
    markers.append("adapter_mints_delete_version_binding")
    if "def verify_delete_proposal_version_binding(" not in adapter:
        raise EvidenceError("proposal_version_binding_carriage", "adapter missing delete version-binding verify")
    markers.append("adapter_verifies_delete_version_binding")
    if "raisa.delete_proposal_version_binding.v1" not in architecture:
        raise EvidenceError("proposal_version_binding_carriage", "architecture missing opaque version-binding schema")
    markers.append("architecture_requires_opaque_version_binding")
    if "mint_delete_proposal_version_binding" in router:
        raise EvidenceError("proposal_version_binding_carriage", "router unexpectedly mints delete version binding")
    markers.append("route_does_not_mint_delete_version_binding")
    if "proposal_version_binding" in handler:
        raise EvidenceError("proposal_version_binding_carriage", "delete handler unexpectedly carries version binding")
    markers.append("delete_handler_does_not_carry_version_binding")
    return (
        "route_transition_gap",
        [
            "app/services/appointment_delete_product_adapter.py",
            "app/routers/appointments.py",
            "docs/raisa-provider-free-unmounted-delete-confirm-response-compatibility-product-adapter-architecture.md",
        ],
        markers,
    )


def _prove_server_authority_and_session_ingress(texts: Dict[str, str]) -> Tuple[str, List[str], List[str]]:
    deps = _text(texts, "app/dependencies.py")
    router = _text(texts, "app/routers/appointments.py")
    adapter = _text(texts, "app/services/appointment_delete_product_adapter.py")
    evidence = _text(
        texts,
        "orchestration/continuity/raisa-delete-confirm-route-convergence-and-ariadne-git-object-resolution/provider-free-read-only-evidence.json",
    )
    handler = _extract_function_body(router, "confirm_delete_proposal_route")
    markers: List[str] = []
    if "def get_command_session_factory(" not in deps:
        raise EvidenceError("server_authority_and_session_ingress", "dependency missing command-session factory")
    markers.append("command_session_factory_available")
    if "def get_current_user(" not in deps:
        raise EvidenceError("server_authority_and_session_ingress", "dependency missing current-user resolver")
    markers.append("current_user_resolver_available")
    required = (
        "authenticated_session_secret",
        "proposal_version_binding_secret",
        "idempotency_secret",
        "session_binding_secret",
        "evidence_secret",
        "command_session_factory",
    )
    for needle in required:
        if needle not in adapter:
            raise EvidenceError("server_authority_and_session_ingress", f"adapter requires {needle}")
    markers.append("adapter_requires_server_secrets_and_session_factory")
    if "get_command_session_factory" in handler:
        raise EvidenceError("server_authority_and_session_ingress", "delete handler unexpectedly uses command-session factory")
    markers.append("delete_handler_does_not_use_command_session_factory")
    if "authenticated_bearer_token" in handler:
        raise EvidenceError("server_authority_and_session_ingress", "delete handler unexpectedly uses bearer token")
    markers.append("delete_handler_does_not_use_bearer_token")
    if "compose_product_delete_confirm" in router:
        raise EvidenceError("server_authority_and_session_ingress", "route unexpectedly invokes delete product adapter")
    markers.append("route_does_not_invoke_delete_product_adapter")
    if "command_session_available_but_unused" not in evidence:
        raise EvidenceError("server_authority_and_session_ingress", "prior evidence missing command-session-unused check")
    markers.append("prior_evidence_command_session_unused")
    return (
        "route_transition_gap",
        [
            "app/dependencies.py",
            "app/routers/appointments.py",
            "app/services/appointment_delete_product_adapter.py",
            "orchestration/continuity/raisa-delete-confirm-route-convergence-and-ariadne-git-object-resolution/provider-free-read-only-evidence.json",
        ],
        markers,
    )


def _prove_physical_seam_composition(texts: Dict[str, str]) -> Tuple[str, List[str], List[str]]:
    adapter = _text(texts, "app/services/appointment_delete_product_adapter.py")
    composition = _text(texts, "app/services/appointment_delete_composition.py")
    markers: List[str] = []
    if "transaction_factory: TransactionFactory = delete_confirm_locked_transaction" not in adapter:
        raise EvidenceError("physical_seam_composition", "adapter does not default to physical transaction")
    markers.append("adapter_defaults_to_physical_transaction")
    if "transaction_factory: TransactionFactory = delete_confirm_locked_transaction" not in composition:
        raise EvidenceError("physical_seam_composition", "composition does not default to physical transaction")
    markers.append("composition_defaults_to_physical_transaction")
    if "from app.services.appointment_delete_physical import" not in adapter:
        raise EvidenceError("physical_seam_composition", "adapter does not import physical seam")
    markers.append("adapter_imports_physical_seam")
    return (
        "satisfied",
        [
            "app/services/appointment_delete_product_adapter.py",
            "app/services/appointment_delete_composition.py",
        ],
        markers,
    )


def _prove_locked_current_truth_readmission(texts: Dict[str, str]) -> Tuple[str, List[str], List[str]]:
    composition = _text(texts, "app/services/appointment_delete_composition.py")
    adapter = _text(texts, "app/services/appointment_delete_product_adapter.py")
    markers: List[str] = []
    if "locked_server_factory(decision.appointment, server_ingress)" not in composition:
        raise EvidenceError("locked_current_truth_readmission", "composition does not re-admit locked appointment")
    markers.append("locked_appointment_readmitted")
    if "def _locked_server_ingress(" not in adapter:
        raise EvidenceError("locked_current_truth_readmission", "adapter missing locked server ingress")
    markers.append("locked_server_ingress_builds_current_state")
    if "def appointment_delete_state(" not in adapter:
        raise EvidenceError("locked_current_truth_readmission", "adapter missing current-state builder")
    markers.append("source_version_readmitted")
    if "locked effect binding mismatch" not in adapter:
        raise EvidenceError("locked_current_truth_readmission", "adapter missing locked binding check")
    markers.append("locked_binding_verified")
    return (
        "satisfied",
        [
            "app/services/appointment_delete_composition.py",
            "app/services/appointment_delete_product_adapter.py",
        ],
        markers,
    )


def _prove_atomic_effect_audit_private_receipt(texts: Dict[str, str]) -> Tuple[str, List[str], List[str]]:
    adapter = _text(texts, "app/services/appointment_delete_product_adapter.py")
    composition = _text(texts, "app/services/appointment_delete_composition.py")
    physical = _text(texts, "app/services/appointment_delete_physical.py")
    markers: List[str] = []
    if "def _stage_effect(" not in adapter:
        raise EvidenceError("atomic_effect_audit_private_receipt", "adapter missing staged effect")
    markers.append("atomic_cancellation_staged")
    if "audit_contract_version=DELETE_CONFIRM_RECEIPT_VERSION" not in adapter:
        raise EvidenceError("atomic_effect_audit_private_receipt", "adapter missing attributable delete audit")
    markers.append("attributable_delete_audit_written")
    if "def _stage_completed_receipt(" not in composition:
        raise EvidenceError("atomic_effect_audit_private_receipt", "composition missing receipt completion")
    markers.append("six_field_private_receipt_completed")
    if "def canonical_delete_confirm_response_bytes(" not in physical:
        raise EvidenceError("atomic_effect_audit_private_receipt", "physical missing canonical receipt serializer")
    markers.append("canonical_private_receipt_serialized")
    if "def _delete_write_set_complete(" not in physical:
        raise EvidenceError("atomic_effect_audit_private_receipt", "physical missing write-set verifier")
    markers.append("write_set_verified_before_commit")
    return (
        "satisfied",
        [
            "app/services/appointment_delete_product_adapter.py",
            "app/services/appointment_delete_composition.py",
            "app/services/appointment_delete_physical.py",
        ],
        markers,
    )


def _prove_public_response_schema(texts: Dict[str, str]) -> Tuple[str, List[str], List[str]]:
    schemas = _text(texts, "app/schemas/appointments.py")
    composition = _text(texts, "app/services/appointment_delete_composition.py")
    architecture = _text(
        texts,
        "docs/raisa-provider-free-unmounted-delete-confirm-response-compatibility-product-adapter-architecture.md",
    )
    markers: List[str] = []
    if "appointment: Optional[AppointmentOut] = None" not in schemas:
        raise EvidenceError("public_response_schema", "current response schema no longer exposes AppointmentOut")
    markers.append("current_schema_exposes_appointment_out")
    if 'DELETE_CONFIRM_PUBLIC_SCHEMA = "raisa.delete_confirm_public_envelope.v1"' not in composition:
        raise EvidenceError("public_response_schema", "public envelope schema missing")
    markers.append("minimal_public_envelope_schema_frozen")
    if "def canonical_delete_confirm_envelope_bytes(" not in composition:
        raise EvidenceError("public_response_schema", "canonical envelope serializer missing")
    markers.append("canonical_envelope_serializer_available")
    if "current full appointment response is retired" not in architecture:
        raise EvidenceError("public_response_schema", "architecture does not retire full appointment response")
    markers.append("architecture_retires_appointment_out")
    return (
        "route_transition_gap",
        [
            "app/schemas/appointments.py",
            "app/services/appointment_delete_composition.py",
            "docs/raisa-provider-free-unmounted-delete-confirm-response-compatibility-product-adapter-architecture.md",
        ],
        markers,
    )


def _prove_canonical_public_byte_delivery(texts: Dict[str, str]) -> Tuple[str, List[str], List[str]]:
    composition = _text(texts, "app/services/appointment_delete_composition.py")
    router = _text(texts, "app/routers/appointments.py")
    architecture = _text(
        texts,
        "docs/raisa-provider-free-unmounted-delete-confirm-response-compatibility-product-adapter-architecture.md",
    )
    handler = _extract_function_body(router, "confirm_delete_proposal_route")
    markers: List[str] = []
    if "def delete_confirm_envelope_projection(" not in composition:
        raise EvidenceError("canonical_public_byte_delivery", "public projection missing")
    markers.append("public_projection_from_private_bytes")
    if "def canonical_delete_confirm_envelope_bytes(" not in composition:
        raise EvidenceError("canonical_public_byte_delivery", "canonical envelope bytes missing")
    markers.append("canonical_envelope_bytes_available")
    if "json.loads(public_bytes)" not in composition:
        raise EvidenceError("canonical_public_byte_delivery", "composition does not deliver public bytes")
    markers.append("composition_delivers_public_bytes")
    if "response_body = AppointmentConfirmDeleteProposalOut(" not in handler:
        raise EvidenceError("canonical_public_byte_delivery", "first delivery no longer reconstructs model")
    markers.append("route_first_delivery_reconstructs_model")
    if "_handle_create_confirm_idempotency_decision" not in handler:
        raise EvidenceError("canonical_public_byte_delivery", "replay no longer uses generic stored json")
    markers.append("route_replay_uses_generic_stored_json")
    if "identical canonical HTTP bytes on first/retry" not in architecture:
        raise EvidenceError("canonical_public_byte_delivery", "architecture does not require byte-identical first/retry")
    markers.append("architecture_requires_identical_first_and_retry_bytes")
    return (
        "route_transition_gap",
        [
            "app/services/appointment_delete_composition.py",
            "app/routers/appointments.py",
            "docs/raisa-provider-free-unmounted-delete-confirm-response-compatibility-product-adapter-architecture.md",
        ],
        markers,
    )


def _prove_closed_outcome_http_mapping(texts: Dict[str, str]) -> Tuple[str, List[str], List[str]]:
    adapter = _text(texts, "app/services/appointment_delete_product_adapter.py")
    composition = _text(texts, "app/services/appointment_delete_composition.py")
    markers: List[str] = []
    for outcome in (
        '"current_authority_unavailable"',
        '"appointment_not_found"',
        '"idempotency_key_conflict"',
        '"delete_confirm_transaction_unavailable"',
    ):
        if outcome not in composition:
            raise EvidenceError("closed_outcome_http_mapping", f"composition missing {outcome}")
    markers.append("composition_maps_403_404_409_503")
    if "def _map_admission_stop(" not in adapter:
        raise EvidenceError("closed_outcome_http_mapping", "adapter missing admission-stop mapper")
    markers.append("admission_stops_mapped_to_closed_status")
    return (
        "satisfied",
        [
            "app/services/appointment_delete_product_adapter.py",
            "app/services/appointment_delete_composition.py",
        ],
        markers,
    )


def _prove_raw_delete_isolation(texts: Dict[str, str]) -> Tuple[str, List[str], List[str]]:
    router = _text(texts, "app/routers/appointments.py")
    inventory = _text(texts, "orchestration/api_spine_appointment_command_alignment_inventory.md")
    markers: List[str] = []
    if '@router.delete("/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)' not in router:
        raise EvidenceError("raw_delete_isolation", "raw DELETE route missing")
    markers.append("raw_delete_route_present")
    if "raw_compat_delete" not in router:
        raise EvidenceError("raw_delete_isolation", "raw compat delete evidence tag missing")
    markers.append("raw_compat_delete_tag_used")
    if "legacy compatibility delete" not in inventory:
        raise EvidenceError("raw_delete_isolation", "inventory does not classify raw DELETE as compatibility write")
    markers.append("inventory_classifies_raw_delete_as_compatibility")
    if "appointment_delete_product_adapter" in router or "appointment_delete_physical" in router:
        raise EvidenceError("raw_delete_isolation", "raw DELETE shares kernel authority")
    markers.append("raw_delete_does_not_import_kernel")
    return (
        "satisfied",
        [
            "app/routers/appointments.py",
            "orchestration/api_spine_appointment_command_alignment_inventory.md",
        ],
        markers,
    )


def _prove_accepted_postgresql_foundation(texts: Dict[str, str]) -> Tuple[str, List[str], List[str]]:
    evidence = _text(
        texts,
        "orchestration/continuity/raisa-provider-free-disposable-postgresql-delete-confirm-behavior-transaction-rehearsal/provider-free-behavior-transaction-evidence.json",
    )
    closeout = _text(
        texts,
        "docs/raisa-provider-free-disposable-postgresql-delete-confirm-behavior-transaction-rehearsal-closeout.md",
    )
    markers: List[str] = []
    if "raisa_provider_free_disposable_postgresql_delete_confirm_behavior_transaction_rehearsal_pass" not in evidence:
        raise EvidenceError("accepted_postgresql_foundation", "303 evidence result missing")
    markers.append("serial_behavior_evidence_accepted")
    for token in ("nine_authority_groups_verified", "eleven_transaction_groups_verified", "cleanup_verified"):
        if token not in evidence:
            raise EvidenceError("accepted_postgresql_foundation", f"303 evidence missing {token}")
    markers.append("nine_authority_and_eleven_transaction_groups_verified")
    if "Status: `accepted`" not in closeout:
        raise EvidenceError("accepted_postgresql_foundation", "closeout not accepted")
    markers.append("closeout_accepted")
    return (
        "satisfied",
        [
            "orchestration/continuity/raisa-provider-free-disposable-postgresql-delete-confirm-behavior-transaction-rehearsal/provider-free-behavior-transaction-evidence.json",
            "docs/raisa-provider-free-disposable-postgresql-delete-confirm-behavior-transaction-rehearsal-closeout.md",
        ],
        markers,
    )


_DIMENSION_PROVERS = {
    1: _prove_literal_mounting,
    2: _prove_canonical_identity_and_alias,
    3: _prove_proposal_version_binding_carriage,
    4: _prove_server_authority_and_session_ingress,
    5: _prove_physical_seam_composition,
    6: _prove_locked_current_truth_readmission,
    7: _prove_atomic_effect_audit_private_receipt,
    8: _prove_public_response_schema,
    9: _prove_canonical_public_byte_delivery,
    10: _prove_closed_outcome_http_mapping,
    11: _prove_raw_delete_isolation,
    12: _prove_accepted_postgresql_foundation,
}


def run_evidence_checks(texts: Dict[str, str]) -> List[Dict[str, Any]]:
    """Run the twelve ordered dimension proofs and return structured results."""
    results: List[Dict[str, Any]] = []
    for order, dim_id, expected_classification in EXPECTED_DIMENSIONS:
        prover = _DIMENSION_PROVERS.get(order)
        if prover is None:
            raise EvidenceError(dim_id, f"no prover registered for order {order}")
        classification, citations, markers = prover(texts)
        if classification != expected_classification:
            raise EvidenceError(
                dim_id,
                f"evidence proved {classification!r} but contract expects {expected_classification!r}",
            )
        results.append(
            {
                "order": order,
                "id": dim_id,
                "classification": classification,
                "citations": sorted(set(citations)),
                "markers": markers,
            }
        )
    return results


# ---------------------------------------------------------------------------
# Private/public byte separation proof.
# ---------------------------------------------------------------------------


def prove_private_public_byte_separation(texts: Dict[str, str]) -> Tuple[bool, List[str]]:
    """Prove the six-field private stored receipt bytes are never the public body.

    The composition derives ``public_bytes`` through
    ``canonical_delete_confirm_envelope_bytes`` over the validated public
    projection and carries the private receipt bytes only as
    ``stored_response_bytes``.  A future route must therefore use
    ``canonical_delete_confirm_envelope_bytes`` for both first delivery and
    replay and must never return the private six-field receipt bytes directly.
    """
    composition = _text(texts, "app/services/appointment_delete_composition.py")
    architecture = _text(
        texts,
        "docs/raisa-provider-free-unmounted-delete-confirm-response-compatibility-product-adapter-architecture.md",
    )
    markers: List[str] = []
    if "public_bytes = canonical_delete_confirm_envelope_bytes(" not in composition:
        raise EvidenceError("private_public_byte_separation", "composition does not serialize public envelope")
    markers.append("public_bytes_derived_from_public_projection")
    if "json.loads(public_bytes)" not in composition:
        raise EvidenceError("private_public_byte_separation", "public body not derived from public bytes")
    markers.append("public_body_is_public_bytes")
    if "stored_response_bytes" not in composition:
        raise EvidenceError("private_public_byte_separation", "private stored bytes not carried separately")
    markers.append("private_stored_bytes_carried_separately")
    if "The stored six-field receipt is command truth. The public response is a" not in architecture:
        raise EvidenceError("private_public_byte_separation", "architecture missing private/public separation")
    markers.append("architecture_private_truth_public_projection")
    return True, markers


# ---------------------------------------------------------------------------
# Hostile mutation suite.
# ---------------------------------------------------------------------------


def _generate_mutations(contract: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Deterministically generate hostile contract mutations."""
    mutations: List[Dict[str, Any]] = []

    def add(mutated: Dict[str, Any]) -> None:
        mutations.append(mutated)

    inputs = contract["inputs"]
    dimensions = contract["dimensions"]

    # A1: remove each input.
    for i in range(len(inputs)):
        m = copy.deepcopy(contract)
        del m["inputs"][i]
        add(m)

    # A2: duplicate each input.
    for i in range(len(inputs)):
        m = copy.deepcopy(contract)
        m["inputs"].append(copy.deepcopy(m["inputs"][i]))
        add(m)

    # A3: flip the first hex character of each input sha256.
    for i in range(len(inputs)):
        m = copy.deepcopy(contract)
        old = m["inputs"][i]["sha256"]
        m["inputs"][i]["sha256"] = ("0" if old[0] != "0" else "1") + old[1:]
        add(m)

    # A4: change each input path to a non-frozen existing path.
    for i in range(len(inputs)):
        m = copy.deepcopy(contract)
        m["inputs"][i]["path"] = "app/database.py"
        add(m)

    # B1: change each dimension expected_classification to another value.
    for i in range(len(dimensions)):
        for alt in EXPECTED_CLASSIFICATIONS:
            if alt == dimensions[i]["expected_classification"]:
                continue
            m = copy.deepcopy(contract)
            m["dimensions"][i]["expected_classification"] = alt
            add(m)

    # B2: swap adjacent dimensions.
    for i in range(len(dimensions) - 1):
        m = copy.deepcopy(contract)
        m["dimensions"][i], m["dimensions"][i + 1] = m["dimensions"][i + 1], m["dimensions"][i]
        add(m)

    # B3: mutate each dimension id.
    for i in range(len(dimensions)):
        m = copy.deepcopy(contract)
        m["dimensions"][i]["id"] = m["dimensions"][i]["id"] + "_mutated"
        add(m)

    # B4: remove each dimension.
    for i in range(len(dimensions)):
        m = copy.deepcopy(contract)
        del m["dimensions"][i]
        add(m)

    return mutations


def _generate_global_mutations(contract: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Deterministically generate global/acceptance hostile mutations."""
    mutations: List[Dict[str, Any]] = []

    def add(mutated: Dict[str, Any]) -> None:
        mutations.append(mutated)

    m = copy.deepcopy(contract)
    m["schema_version"] = "raisa.mutated.v1"
    add(m)

    m = copy.deepcopy(contract)
    m["source_head"] = "0" * 40
    add(m)

    m = copy.deepcopy(contract)
    m["input_hash_mode"] = "mutated"
    add(m)

    m = copy.deepcopy(contract)
    m["classifications"] = ["satisfied"]
    add(m)

    m = copy.deepcopy(contract)
    m["verdict_rules"] = {"any_blocking_gap": "mutated"}
    add(m)

    m = copy.deepcopy(contract)
    m["acceptance"]["expected_counts"]["satisfied"] = 6
    add(m)

    m = copy.deepcopy(contract)
    m["acceptance"]["expected_counts"]["route_transition_gap"] = 4
    add(m)

    m = copy.deepcopy(contract)
    m["acceptance"]["expected_counts"]["blocking_gap"] = 1
    add(m)

    m = copy.deepcopy(contract)
    m["acceptance"]["expected_verdict"] = "route_mounting_not_ready"
    add(m)

    m = copy.deepcopy(contract)
    m["acceptance"]["minimum_hostile_mutations"] = 71
    add(m)

    m = copy.deepcopy(contract)
    m["acceptance"]["require_exact_dimension_order"] = False
    add(m)

    m = copy.deepcopy(contract)
    m["acceptance"]["require_exact_source_citations"] = False
    add(m)

    m = copy.deepcopy(contract)
    m["acceptance"]["require_private_public_byte_separation"] = False
    add(m)

    m = copy.deepcopy(contract)
    m["acceptance"]["require_no_app_import"] = False
    add(m)

    m = copy.deepcopy(contract)
    m["forbidden_surfaces"] = []
    add(m)

    m = copy.deepcopy(contract)
    m["extra_key"] = True
    add(m)

    return mutations


def run_hostile_mutations(contract: Dict[str, Any], repo_root: Path) -> int:
    """Run the deterministic hostile mutation suite and return rejections.

    Every generated mutation must be rejected by :func:`validate_contract`.  If
    any mutation is not rejected the review fails closed.
    """
    mutations = _generate_mutations(contract) + _generate_global_mutations(contract)
    rejected = 0
    for mutated in mutations:
        try:
            validate_contract(mutated, repo_root)
        except ContractValidationError:
            rejected += 1
        else:
            raise EvidenceError(
                "hostile_mutation_suite",
                "a generated hostile contract mutation was not rejected",
            )
    return rejected


# ---------------------------------------------------------------------------
# Result building, JSON release, and Markdown report.
# ---------------------------------------------------------------------------


def _compute_verdict(counts: Dict[str, int]) -> str:
    blocking = counts.get("blocking_gap", 0)
    transition = counts.get("route_transition_gap", 0)
    if blocking > 0:
        return EXPECTED_VERDICT_RULES["any_blocking_gap"]
    if transition > 0:
        return EXPECTED_VERDICT_RULES["no_blocker_with_transition_gap"]
    # All-satisfied would contradict the currently mounted router and is unsupported.
    raise EvidenceError(
        "verdict_matrix",
        "all-satisfied matrix is unsupported and would contradict the mounted router",
    )


def build_results(
    contract: Dict[str, Any],
    dimension_results: List[Dict[str, Any]],
    private_public_markers: List[str],
    mutation_count: int,
) -> Dict[str, Any]:
    counts: Dict[str, int] = Counter(d["classification"] for d in dimension_results)
    ordered_counts = {
        "satisfied": counts.get("satisfied", 0),
        "route_transition_gap": counts.get("route_transition_gap", 0),
        "blocking_gap": counts.get("blocking_gap", 0),
    }
    expected_counts = EXPECTED_ACCEPTANCE["expected_counts"]
    if ordered_counts != expected_counts:
        raise EvidenceError("verdict_matrix", f"dimension counts {ordered_counts} != {expected_counts}")
    verdict = _compute_verdict(ordered_counts)
    if verdict != EXPECTED_ACCEPTANCE["expected_verdict"]:
        raise EvidenceError("verdict_matrix", f"verdict {verdict} != expected")
    if mutation_count < EXPECTED_ACCEPTANCE["minimum_hostile_mutations"]:
        raise EvidenceError(
            "hostile_mutation_suite",
            f"mutation rejections {mutation_count} < {EXPECTED_ACCEPTANCE['minimum_hostile_mutations']}",
        )
    if not private_public_markers:
        raise EvidenceError("private_public_byte_separation", "no separation markers recorded")
    if tuple(d["id"] for d in dimension_results if d["classification"] == "route_transition_gap") != EXPECTED_TRANSITION_GAPS:
        raise EvidenceError("verdict_matrix", "transition-gap dimensions are not exactly the five expected")

    dimensions = [
        {
            "order": d["order"],
            "id": d["id"],
            "classification": d["classification"],
            "citations": d["citations"],
            "markers": d["markers"],
        }
        for d in dimension_results
    ]
    source_bindings = {item["path"]: item["sha256"] for item in contract["inputs"]}

    return {
        "schema_version": EVIDENCE_SCHEMA_VERSION,
        "result": RESULT_PASS,
        "source_head": contract["source_head"],
        "source_bindings": source_bindings,
        "dimension_counts": ordered_counts,
        "dimensions": dimensions,
        "transition_gaps": list(EXPECTED_TRANSITION_GAPS),
        "satisfied_dimensions": [
            d["id"] for d in dimension_results if d["classification"] == "satisfied"
        ],
        "private_public_byte_separation": True,
        "private_public_byte_separation_markers": private_public_markers,
        "hostile_mutations_rejected": mutation_count,
        "verdict": verdict,
        "closed_boundaries": {
            "app_imported": False,
            "database_opened": False,
            "route_called": False,
            "docker_used": False,
            "sql_executed": False,
            "network_opened": False,
        },
    }


def _write_lf(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def write_evidence_json(repo_root: Path, results: Dict[str, Any]) -> None:
    text = json.dumps(results, indent=2, ensure_ascii=True, sort_keys=True) + "\n"
    _write_lf(repo_root / EVIDENCE_RELATIVE_PATH, text)


def render_report(results: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("# Provider-free read-only delete-confirm route-mounting readiness review report")
    lines.append("")
    lines.append("Date: 2026-08-17")
    lines.append("Timestamp: 2026-08-17T00:46:11.8521710+10:00 (Australia/Brisbane)")
    lines.append("")
    lines.append("Status: frozen evidence")
    lines.append("")
    lines.append(f"Result: `{results['result']}`")
    lines.append("")
    lines.append(f"Verdict: `{results['verdict']}`")
    lines.append("")
    lines.append("## Source boundary")
    lines.append("")
    lines.append("All 23 strict UTF-8 canonical-LF (bare-CR rejected) SHA-256 bindings match before classification.")
    lines.append("")
    lines.append("| Path | SHA-256 |")
    lines.append("|---|---|")
    for path, digest in results["source_bindings"].items():
        lines.append(f"| `{path}` | `{digest}` |")
    lines.append("")
    lines.append("## Dimension matrix (exact order)")
    lines.append("")
    lines.append("| Order | Dimension | Classification | Source citations | Markers |")
    lines.append("|---|---|---|---|---|")
    for dim in results["dimensions"]:
        citations = "; ".join(f"`{c}`" for c in dim["citations"])
        markers = "; ".join(dim["markers"])
        lines.append(f"| {dim['order']} | `{dim['id']}` | `{dim['classification']}` | {citations} | {markers} |")
    lines.append("")
    counts = results["dimension_counts"]
    lines.append(
        "## Counts\n\n"
        f"satisfied: {counts['satisfied']}, "
        f"route_transition_gap: {counts['route_transition_gap']}, "
        f"blocking_gap: {counts['blocking_gap']}\n"
    )
    lines.append("## Transition gaps (exactly five, none implemented)")
    lines.append("")
    for gap in results["transition_gaps"]:
        lines.append(f"- `{gap}`")
    lines.append("")
    lines.append("## Private/public byte separation")
    lines.append("")
    lines.append(
        "Proven. The stored six-field private receipt is command truth and is carried "
        "separately as `stored_response_bytes`. The public HTTP envelope is derived "
        "through `delete_confirm_envelope_projection` plus "
        "`canonical_delete_confirm_envelope_bytes`. The future route must never return "
        "the private six-field receipt bytes directly as the public HTTP envelope; it "
        "must serialize `canonical_delete_confirm_envelope_bytes` over the validated "
        "public projection for both first delivery and replay."
    )
    lines.append("")
    markers = "; ".join(results["private_public_byte_separation_markers"])
    lines.append(f"Separation markers: {markers}")
    lines.append("")
    lines.append("## Hostile mutation suite")
    lines.append("")
    lines.append(
        f"Deterministic hostile contract mutations rejected: "
        f"{results['hostile_mutations_rejected']} (minimum required: 72)."
    )
    lines.append("")
    lines.append("## Closed boundaries")
    lines.append("")
    lines.append("| Boundary | Value |")
    lines.append("|---|---|")
    for key, value in results["closed_boundaries"].items():
        lines.append(f"| {key} | {value} |")
    lines.append("")
    lines.append(
        "No `app` module was imported; no route was mounted or called; no database, "
        "Docker, SQL, provider, network or credential surface was opened."
    )
    lines.append("")
    return "\n".join(lines)


def write_report_md(repo_root: Path, results: Dict[str, Any]) -> None:
    _write_lf(repo_root / REPORT_RELATIVE_PATH, render_report(results))


# ---------------------------------------------------------------------------
# Orchestration.
# ---------------------------------------------------------------------------


def run_review(repo_root: Path | None = None, write_outputs: bool = True) -> Dict[str, Any]:
    """Run the full read-only review and return the evidence results dict."""
    if repo_root is None:
        repo_root = Path(__file__).resolve().parents[1]
    repo_root = Path(repo_root)
    contract = load_contract(repo_root)
    validate_contract(contract, repo_root)
    texts = load_source_texts(contract, repo_root)
    dimension_results = run_evidence_checks(texts)
    separation_proven, separation_markers = prove_private_public_byte_separation(texts)
    if not separation_proven:
        raise EvidenceError("private_public_byte_separation", "separation not proven")
    mutation_count = run_hostile_mutations(contract, repo_root)
    results = build_results(contract, dimension_results, separation_markers, mutation_count)
    if write_outputs:
        write_evidence_json(repo_root, results)
        write_report_md(repo_root, results)
    return results


def _main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Provider-free read-only delete-confirm route-mounting readiness review"
    )
    parser.add_argument(
        "--repo-root",
        default=str(Path(__file__).resolve().parents[1]),
        help="Repository root (defaults to the parent of this script)",
    )
    parser.add_argument(
        "--no-write",
        action="store_true",
        help="Compute the review without writing released evidence/report files",
    )
    args = parser.parse_args(argv)
    try:
        run_review(repo_root=Path(args.repo_root), write_outputs=not args.no_write)
    except (ContractValidationError, EvidenceError) as exc:
        print(f"FAIL_CLOSED: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
