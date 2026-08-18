"""Provider-free, repository-static ordinary-practice check-in readiness review.

The reviewer reads only the 28 exact contract inputs.  It imports no ``app``
module and opens no route, database, Docker, SQL, browser, provider or network
surface.  Passing proves the exact inventory and not-ready verdict, not product
admission.
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
from typing import Any, Callable


SCHEMA_VERSION = "raisa.ordinary_practice_check_in_admission_readiness_review_contract.v1"
EVIDENCE_SCHEMA_VERSION = (
    "raisa.ordinary_practice_check_in_admission_readiness_review_evidence.v1"
)
SOURCE_HEAD = "8fe889764e778c21bd051f30549f77c8db425e7c"
HASH_MODE = "strict_utf8_canonical_lf_reject_bare_cr_sha256"
CLASSIFICATIONS = ("satisfied", "blocking_gap", "operational_evidence_gap")
VERDICT_RULES = {
    "any_non_satisfied": "not_ready_for_ordinary_practice_admission",
    "all_satisfied": "ready_for_bounded_ordinary_practice_admission_candidate",
}
NEXT_TRANCHE = (
    "raisa-provider-free-default-off-ordinary-practice-canonical-check-in-"
    "admission-control-architecture"
)
RESULT = (
    "raisa_provider_free_read_only_ordinary_practice_canonical_check_in_"
    "admission_readiness_review_pass"
)

INPUT_PATHS = (
    "app/config.py",
    "app/database.py",
    "app/dependencies.py",
    "app/services/auth_service.py",
    "app/routers/appointments.py",
    "app/schemas/appointments.py",
    "app/services/appointment_check_in_product_adapter.py",
    "app/services/appointment_idempotency.py",
    "app/services/diary_committed_events.py",
    "app/models/appointments.py",
    "app/models/tenancy.py",
    "app/models/diary.py",
    "alembic/versions/m2n3o4p5q6r7_add_bernie_durable_authority.py",
    "alembic/versions/n3o4p5q6r7s8_add_reception_one_committed_events.py",
    "alembic/versions/v1w2x3y4z5a6_add_a5_check_in_runtime.py",
    "docs/api-spine/openapi/appointment-commands.yaml",
    "orchestration/api_spine_adr.md",
    "orchestration/api_spine_programme.md",
    "orchestration/api_spine_appointment_command_alignment_inventory.md",
    "docs/raisa-provider-free-default-off-canonical-check-in-route-adapter-"
    "convergence-rehearsal-plan.md",
    "docs/security/raisa-provider-free-default-off-canonical-check-in-route-"
    "adapter-convergence-rehearsal-threat-model-delta.md",
    "docs/raisa-provider-free-default-off-canonical-check-in-route-adapter-"
    "convergence-rehearsal-closeout.md",
    "orchestration/agent_inbox/codex/raisa-default-off-check-in-route-adapter-"
    "sol-acceptance.md",
    "tests/test_model_required_bureau_a5_1_check_in_runtime.py",
    "tests/test_raisa_provider_free_default_off_canonical_check_in_route_adapter_"
    "convergence.py",
    "tests/test_api_spine_appointment_openapi_drift_guard.py",
    "tests/test_api_spine_artifacts.py",
    ".env.example",
)

DIMENSIONS = (
    (1, "current_default_off_and_empty_ordinary_posture", "satisfied"),
    (2, "ordinary_practice_admission_control", "blocking_gap"),
    (3, "api_spine_contract_and_route_identity", "satisfied"),
    (4, "authentication_and_dual_receptionist_authorization", "satisfied"),
    (5, "tenant_isolation_and_runtime_database_role", "operational_evidence_gap"),
    (6, "idempotency_evidence_and_replay", "satisfied"),
    (
        7,
        "atomic_effect_rollback_and_unknown_commit_recovery",
        "operational_evidence_gap",
    ),
    (8, "append_only_audit_and_committed_event", "satisfied"),
    (9, "ordinary_rollout_kill_switch_and_rollback_runbook", "blocking_gap"),
    (10, "non_phi_observability_and_alerting", "blocking_gap"),
    (
        11,
        "environment_manifest_and_operational_secret_posture",
        "operational_evidence_gap",
    ),
    (12, "client_cutover_and_waiting_area_separation", "satisfied"),
)

EXPECTED_COUNTS = {
    "satisfied": 6,
    "blocking_gap": 3,
    "operational_evidence_gap": 3,
}
EXPECTED_ACCEPTANCE = {
    "expected_counts": EXPECTED_COUNTS,
    "expected_verdict": "not_ready_for_ordinary_practice_admission",
    "expected_next_tranche": NEXT_TRANCHE,
    "minimum_hostile_mutations": 120,
    "require_exact_dimension_order": True,
    "require_exact_source_citations": True,
    "require_no_app_import": True,
    "require_no_runtime_surface": True,
}
FORBIDDEN_SURFACES = (
    "ordinary_practice_enablement_or_feature_flag_change",
    "product_code_configuration_route_database_or_api_spine_edit",
    "generic_status_arrived_grammar_client_or_waiting_area_movement",
    "product_patient_clinical_historical_or_protected_data",
    "provider_harness_retry_credential_iam_or_network",
    "production_deployment_release_pages_or_protected_refs",
    "docs_branding_and_unrelated_untracked_files",
)

BASE = (
    "orchestration/continuity/raisa-provider-free-read-only-ordinary-practice-"
    "canonical-check-in-admission-readiness-review"
)
CONTRACT_PATH = f"{BASE}/admission-readiness-review-contract.json"
EVIDENCE_PATH = f"{BASE}/provider-free-read-only-evidence.json"
REPORT_PATH = f"{BASE}/admission-readiness-review-report.md"


class ContractError(RuntimeError):
    """The frozen machine contract or a source binding changed."""


class EvidenceError(RuntimeError):
    """Current exact source cannot prove the frozen classification."""


def canonical_text(path: Path) -> str:
    raw = path.read_bytes()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ContractError(f"non-UTF-8 source: {path}") from exc
    if "\r" in text.replace("\r\n", ""):
        raise ContractError(f"bare CR source: {path}")
    return text.replace("\r\n", "\n")


def canonical_sha256(path: Path) -> str:
    return hashlib.sha256(canonical_text(path).encode("utf-8")).hexdigest()


def load_contract(root: Path) -> dict[str, Any]:
    return json.loads((root / CONTRACT_PATH).read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ContractError(message)


def validate_contract(contract: dict[str, Any], root: Path) -> None:
    require(
        set(contract)
        == {
            "schema_version",
            "source_head",
            "input_hash_mode",
            "inputs",
            "classifications",
            "verdict_rules",
            "dimensions",
            "acceptance",
            "forbidden_surfaces",
        },
        "top-level keys changed",
    )
    require(contract["schema_version"] == SCHEMA_VERSION, "schema version changed")
    require(contract["source_head"] == SOURCE_HEAD, "source HEAD changed")
    require(re.fullmatch(r"[0-9a-f]{40}", contract["source_head"]) is not None, "invalid source HEAD")
    require(contract["input_hash_mode"] == HASH_MODE, "hash mode changed")
    require(tuple(contract["classifications"]) == CLASSIFICATIONS, "classifications changed")
    require(contract["verdict_rules"] == VERDICT_RULES, "verdict rules changed")
    require(contract["acceptance"] == EXPECTED_ACCEPTANCE, "acceptance changed")
    require(tuple(contract["forbidden_surfaces"]) == FORBIDDEN_SURFACES, "forbidden surfaces changed")

    inputs = contract["inputs"]
    require(isinstance(inputs, list) and len(inputs) == 28, "input count changed")
    require(
        tuple(item.get("path") for item in inputs) == INPUT_PATHS,
        "input path order changed",
    )
    for item in inputs:
        require(set(item) == {"path", "sha256"}, "input shape changed")
        require(re.fullmatch(r"[0-9a-f]{64}", item["sha256"]) is not None, "invalid input hash")
        require(
            canonical_sha256(root / item["path"]) == item["sha256"],
            f"source hash changed: {item['path']}",
        )

    dimensions = contract["dimensions"]
    require(isinstance(dimensions, list) and len(dimensions) == 12, "dimension count changed")
    observed = []
    for item in dimensions:
        require(
            set(item) == {"order", "id", "expected_classification", "question"},
            "dimension shape changed",
        )
        require(isinstance(item["question"], str) and item["question"], "empty dimension question")
        observed.append((item["order"], item["id"], item["expected_classification"]))
    require(tuple(observed) == DIMENSIONS, "dimension order or classification changed")


def load_texts(contract: dict[str, Any], root: Path) -> dict[str, str]:
    return {item["path"]: canonical_text(root / item["path"]) for item in contract["inputs"]}


def function_body(source: str, name: str) -> str:
    tree = ast.parse(source)
    lines = source.splitlines()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            return "\n".join(lines[node.lineno - 1 : node.end_lineno])
    raise EvidenceError(f"function missing: {name}")


def present(texts: dict[str, str], path: str, needle: str, marker: str, markers: list[str]) -> None:
    if needle not in texts[path]:
        raise EvidenceError(f"{marker}: marker missing from {path}")
    markers.append(marker)


def absent(texts: dict[str, str], paths: tuple[str, ...], needles: tuple[str, ...], marker: str, markers: list[str]) -> None:
    for path in paths:
        lowered = texts[path].lower()
        for needle in needles:
            if needle.lower() in lowered:
                raise EvidenceError(f"{marker}: unexpected {needle!r} in {path}")
    markers.append(marker)


Proof = Callable[[dict[str, str]], tuple[str, list[str], list[str]]]


def prove_1(texts: dict[str, str]) -> tuple[str, list[str], list[str]]:
    markers: list[str] = []
    present(texts, "app/config.py", "rayleen_a5_check_in_enabled: bool = False", "feature_flag_defaults_false", markers)
    present(texts, "app/config.py", 'rayleen_a5_check_in_synthetic_practice_ids: str = ""', "synthetic_allowlist_defaults_empty", markers)
    present(texts, "app/routers/appointments.py", "if not settings.rayleen_a5_check_in_enabled:", "flag_denial_precedes_route_work", markers)
    absent(
        texts,
        ("app/config.py", "app/routers/appointments.py", ".env.example"),
        ("rayleen_a5_check_in_ordinary", "check_in_ordinary_practice_ids"),
        "ordinary_practice_setting_absent",
        markers,
    )
    return "satisfied", ["app/config.py", "app/routers/appointments.py", ".env.example"], markers


def prove_2(texts: dict[str, str]) -> tuple[str, list[str], list[str]]:
    markers: list[str] = []
    present(texts, "app/routers/appointments.py", '"The authenticated practice is not an authored-synthetic "', "gate_is_explicitly_synthetic_only", markers)
    present(texts, "app/routers/appointments.py", '"A5.1 allowlisted practice."', "gate_names_only_the_synthetic_allowlist", markers)
    present(texts, "app/config.py", "rayleen_a5_check_in_synthetic_practice_ids", "only_named_check_in_allowlist_is_synthetic", markers)
    absent(
        texts,
        ("app/config.py", "app/routers/appointments.py", ".env.example"),
        ("ordinary_practice_admission", "ordinary_practice_ids", "ordinary_check_in_enabled"),
        "separate_ordinary_admission_control_missing",
        markers,
    )
    return "blocking_gap", ["app/config.py", "app/routers/appointments.py", ".env.example"], markers


def prove_3(texts: dict[str, str]) -> tuple[str, list[str], list[str]]:
    markers: list[str] = []
    openapi = "docs/api-spine/openapi/appointment-commands.yaml"
    router = "app/routers/appointments.py"
    present(texts, openapi, "/appointments/proposals/check-in/confirm:", "canonical_confirm_path_documented", markers)
    present(texts, openapi, "operationId: confirmAppointmentCheckInProposal", "operation_id_documented", markers)
    present(texts, openapi, "$ref: \"#/components/schemas/AppointmentCheckInConfirmationCommand\"", "typed_request_documented", markers)
    present(texts, openapi, "$ref: \"#/components/schemas/AppointmentConfirmCheckInResult\"", "typed_response_documented", markers)
    handler = function_body(texts[router], "confirm_check_in_proposal_route")
    if "operation_id=\"confirmAppointmentCheckInProposal\"" not in texts[router] or "compose_product_check_in(" not in handler:
        raise EvidenceError("mounted route identity or adapter delegation missing")
    markers.extend(["mounted_operation_id_exact", "accepted_adapter_delegated_once"])
    present(texts, "docs/raisa-provider-free-default-off-canonical-check-in-route-adapter-convergence-rehearsal-closeout.md", "Accepted reviewed source: `c82c3a741053a9c8da260aa62e1a968af22bb54e`", "route_convergence_exactly_accepted", markers)
    return "satisfied", [openapi, router, "app/schemas/appointments.py", "docs/raisa-provider-free-default-off-canonical-check-in-route-adapter-convergence-rehearsal-closeout.md"], markers


def prove_4(texts: dict[str, str]) -> tuple[str, list[str], list[str]]:
    markers: list[str] = []
    present(texts, "app/routers/appointments.py", "current_user: User = Depends(require_role(UserRole.Receptionist))", "route_requires_receptionist", markers)
    present(texts, "app/dependencies.py", "if user.practice_id != token_data.practice_id:", "token_user_practice_match_required", markers)
    present(texts, "app/dependencies.py", "User.is_active == True", "active_user_required", markers)
    present(texts, "app/services/appointment_check_in_product_adapter.py", "if not _valid_receptionist(authenticated_actor, server_practice_id):", "adapter_rechecks_ingress_receptionist", markers)
    present(texts, "app/services/appointment_check_in_product_adapter.py", "current_actor = dependencies.load_current_actor(", "transaction_actor_reloaded", markers)
    present(texts, "app/services/appointment_check_in_product_adapter.py", 'return _stop("current_authority_revoked"', "revoked_authority_stops", markers)
    return "satisfied", ["app/routers/appointments.py", "app/dependencies.py", "app/services/auth_service.py", "app/services/appointment_check_in_product_adapter.py"], markers


def prove_5(texts: dict[str, str]) -> tuple[str, list[str], list[str]]:
    markers: list[str] = []
    migration = "alembic/versions/m2n3o4p5q6r7_add_bernie_durable_authority.py"
    events = "alembic/versions/n3o4p5q6r7s8_add_reception_one_committed_events.py"
    present(texts, "app/dependencies.py", "SELECT set_config('app.current_practice_id', :practice_id, true)", "request_sets_transaction_practice", markers)
    present(texts, "app/routers/appointments.py", "Appointment.practice_id == practice_id", "appointment_queries_are_practice_scoped", markers)
    present(texts, migration, 'ALTER TABLE "{table_name}" FORCE ROW LEVEL SECURITY', "appointments_and_idempotency_forced_rls_helper", markers)
    present(texts, migration, '"appointment_command_idempotency_practice_all"', "idempotency_rls_policy_applied", markers)
    present(texts, migration, 'ALTER TABLE "appointment_audit_log" FORCE ROW LEVEL SECURITY', "audit_forced_rls", markers)
    present(texts, events, 'ALTER TABLE "diary_committed_events" FORCE ROW LEVEL SECURITY', "event_forced_rls", markers)
    absent(
        texts,
        ("app/database.py", ".env.example"),
        ("nobypassrls", "runtime_database_role", "non_owner_role"),
        "ordinary_runtime_role_attestation_absent",
        markers,
    )
    return "operational_evidence_gap", ["app/database.py", "app/dependencies.py", "app/routers/appointments.py", migration, events, ".env.example"], markers


def prove_6(texts: dict[str, str]) -> tuple[str, list[str], list[str]]:
    markers: list[str] = []
    service = "app/services/appointment_idempotency.py"
    adapter = "app/services/appointment_check_in_product_adapter.py"
    migration = "alembic/versions/v1w2x3y4z5a6_add_a5_check_in_runtime.py"
    present(texts, service, "def claim_appointment_check_in_command(", "dedicated_check_in_claim", markers)
    present(texts, service, "uq_appt_cmd_idem_practice_actor_operation_key", "practice_actor_operation_key_identity", markers)
    present(texts, service, "evidence_replay_rejected", "different_key_evidence_reuse_rejected", markers)
    present(texts, adapter, 'if kind == "replay":', "same_key_replay_classified_before_effect", markers)
    present(texts, adapter, 'return _stop("stored_replay_invalid"', "invalid_stored_replay_fails_closed", markers)
    present(texts, migration, "uq_appt_cmd_idem_evidence_hash", "database_unique_evidence_constraint", markers)
    return "satisfied", [service, adapter, migration, "tests/test_model_required_bureau_a5_1_check_in_runtime.py"], markers


def prove_7(texts: dict[str, str]) -> tuple[str, list[str], list[str]]:
    markers: list[str] = []
    adapter = "app/services/appointment_check_in_product_adapter.py"
    tests = "tests/test_raisa_provider_free_default_off_canonical_check_in_route_adapter_convergence.py"
    present(texts, adapter, "_rollback(dependencies)", "precommit_stops_rollback", markers)
    present(texts, adapter, '"commit_outcome_unknown"', "commit_uncertainty_releases_no_success", markers)
    present(texts, adapter, '"committed_readback_unavailable"', "readback_uncertainty_releases_no_success", markers)
    present(texts, adapter, "committed=None", "uncertain_outcome_is_explicit", markers)
    present(texts, tests, "commit_outcome_unknown", "commit_failure_regression_present", markers)
    absent(
        texts,
        (adapter, "app/routers/appointments.py", "app/config.py", ".env.example"),
        ("unknown_commit_runbook", "commit_outcome_unknown_alert", "check_in_recovery_runbook"),
        "ordinary_unknown_commit_runbook_and_alert_absent",
        markers,
    )
    return "operational_evidence_gap", [adapter, tests, "app/routers/appointments.py", "app/config.py", ".env.example"], markers


def prove_8(texts: dict[str, str]) -> tuple[str, list[str], list[str]]:
    markers: list[str] = []
    audit = "alembic/versions/m2n3o4p5q6r7_add_bernie_durable_authority.py"
    events = "alembic/versions/n3o4p5q6r7s8_add_reception_one_committed_events.py"
    adapter = "app/services/appointment_check_in_product_adapter.py"
    present(texts, audit, "trg_appointment_audit_log_append_only", "audit_append_only_trigger", markers)
    present(texts, events, "trg_diary_committed_events_append_only", "event_append_only_trigger", markers)
    present(texts, adapter, "audit = dependencies.write_audit(plan=audit_plan)", "one_command_bound_audit_staged", markers)
    present(texts, adapter, "event = dependencies.write_event(plan=event_plan)", "one_committed_event_staged", markers)
    present(texts, adapter, '"reason_codes": ["appointment_checked_in"]', "patient_free_event_payload", markers)
    present(texts, adapter, "if not _patient_free(response_body):", "patient_free_receipt_enforced", markers)
    return "satisfied", [audit, events, adapter, "app/services/diary_committed_events.py"], markers


def prove_9(texts: dict[str, str]) -> tuple[str, list[str], list[str]]:
    markers: list[str] = []
    present(texts, "app/config.py", "rayleen_a5_check_in_enabled: bool = False", "existing_global_synthetic_kill_switch_defaults_off", markers)
    present(texts, "app/config.py", "rayleen_a5_check_in_synthetic_practice_ids", "existing_allowlist_is_synthetic_not_ordinary", markers)
    absent(
        texts,
        ("app/config.py", "app/routers/appointments.py", ".env.example"),
        ("ordinary_rollout", "ordinary_practice_ids", "check_in_rollback_runbook", "check_in_rollout_state"),
        "ordinary_rollout_state_kill_switch_and_runbook_missing",
        markers,
    )
    return "blocking_gap", ["app/config.py", "app/routers/appointments.py", ".env.example"], markers


def prove_10(texts: dict[str, str]) -> tuple[str, list[str], list[str]]:
    markers: list[str] = []
    present(texts, "app/services/appointment_check_in_product_adapter.py", "CHECK_IN_AUDIT_EVIDENCE", "audit_evidence_exists_but_is_not_telemetry", markers)
    present(texts, "app/services/diary_committed_events.py", "CHECK_IN_EVENT_TYPE", "committed_event_exists_but_is_not_monitoring", markers)
    absent(
        texts,
        ("app/config.py", "app/routers/appointments.py", "app/services/appointment_check_in_product_adapter.py", ".env.example"),
        ("import logging", "logger.", "prometheus", "opentelemetry", "sentry_sdk", "check_in_attempt_total", "commit_outcome_unknown_total"),
        "non_phi_metrics_and_alerts_missing",
        markers,
    )
    return "blocking_gap", ["app/config.py", "app/routers/appointments.py", "app/services/appointment_check_in_product_adapter.py", "app/services/diary_committed_events.py", ".env.example"], markers


def prove_11(texts: dict[str, str]) -> tuple[str, list[str], list[str]]:
    markers: list[str] = []
    present(texts, "app/config.py", "SECRET_KEY must be set to a strong, unique value", "non_dev_default_secret_fails_closed", markers)
    present(texts, ".env.example", "ENVIRONMENT=dev", "environment_is_documented", markers)
    present(texts, ".env.example", "DATABASE_URL=", "database_url_is_documented", markers)
    present(texts, ".env.example", "SECRET_KEY=", "secret_key_is_documented", markers)
    absent(
        texts,
        (".env.example", "app/database.py"),
        ("RAYLEEN_A5_CHECK_IN", "NOBYPASSRLS", "runtime_database_role"),
        "a5_settings_and_runtime_role_evidence_absent",
        markers,
    )
    return "operational_evidence_gap", ["app/config.py", "app/database.py", ".env.example"], markers


def prove_12(texts: dict[str, str]) -> tuple[str, list[str], list[str]]:
    markers: list[str] = []
    plan = "docs/raisa-provider-free-default-off-canonical-check-in-route-adapter-convergence-rehearsal-plan.md"
    closeout = "docs/raisa-provider-free-default-off-canonical-check-in-route-adapter-convergence-rehearsal-closeout.md"
    present(texts, "app/routers/appointments.py", "waiting_area_move_not_supported", "waiting_area_move_remains_blocked", markers)
    present(texts, "app/routers/appointments.py", "Omitted/null preserves an existing area and never removes or moves it.", "waiting_area_assignment_and_preservation_bounded", markers)
    present(texts, plan, "first-party", "plan_keeps_first_party_client_closed", markers)
    present(texts, plan, "waiting-area movement", "plan_keeps_waiting_area_movement_closed", markers)
    present(texts, closeout, "first-party client and waiting-area move/removal remain unchanged and closed", "accepted_closeout_keeps_client_cutover_separate", markers)
    return "satisfied", ["app/routers/appointments.py", plan, closeout], markers


PROVERS: dict[int, Proof] = {
    1: prove_1,
    2: prove_2,
    3: prove_3,
    4: prove_4,
    5: prove_5,
    6: prove_6,
    7: prove_7,
    8: prove_8,
    9: prove_9,
    10: prove_10,
    11: prove_11,
    12: prove_12,
}


def prove_dimensions(texts: dict[str, str]) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for order, dimension_id, expected in DIMENSIONS:
        classification, citations, markers = PROVERS[order](texts)
        if classification != expected:
            raise EvidenceError(f"{dimension_id}: {classification} != {expected}")
        results.append(
            {
                "order": order,
                "id": dimension_id,
                "classification": classification,
                "citations": sorted(set(citations)),
                "markers": markers,
            }
        )
    return results


def hostile_mutations(contract: dict[str, Any], root: Path) -> int:
    mutations: list[dict[str, Any]] = []
    for index in range(len(contract["inputs"])):
        candidate = copy.deepcopy(contract)
        del candidate["inputs"][index]
        mutations.append(candidate)
        candidate = copy.deepcopy(contract)
        candidate["inputs"][index]["path"] = "AGENTS.md"
        mutations.append(candidate)
        candidate = copy.deepcopy(contract)
        digest = candidate["inputs"][index]["sha256"]
        candidate["inputs"][index]["sha256"] = ("0" if digest[0] != "0" else "1") + digest[1:]
        mutations.append(candidate)
    for index, dimension in enumerate(contract["dimensions"]):
        for alternative in CLASSIFICATIONS:
            if alternative == dimension["expected_classification"]:
                continue
            candidate = copy.deepcopy(contract)
            candidate["dimensions"][index]["expected_classification"] = alternative
            mutations.append(candidate)
        candidate = copy.deepcopy(contract)
        del candidate["dimensions"][index]
        mutations.append(candidate)
    global_changes = (
        ("schema_version", "mutated"),
        ("source_head", "0" * 40),
        ("input_hash_mode", "mutated"),
        ("classifications", ["satisfied"]),
        ("verdict_rules", {"all_satisfied": "mutated"}),
        ("acceptance", {}),
        ("forbidden_surfaces", []),
    )
    for key, value in global_changes:
        candidate = copy.deepcopy(contract)
        candidate[key] = value
        mutations.append(candidate)
    candidate = copy.deepcopy(contract)
    candidate["extra"] = True
    mutations.append(candidate)

    rejected = 0
    for candidate in mutations:
        try:
            validate_contract(candidate, root)
        except (ContractError, OSError, KeyError, TypeError):
            rejected += 1
        else:
            raise EvidenceError("hostile contract mutation escaped validation")
    return rejected


def build_evidence(
    contract: dict[str, Any],
    dimensions: list[dict[str, Any]],
    rejected: int,
) -> dict[str, Any]:
    counts = Counter(item["classification"] for item in dimensions)
    ordered_counts = {name: counts.get(name, 0) for name in CLASSIFICATIONS}
    if ordered_counts != EXPECTED_COUNTS:
        raise EvidenceError(f"unexpected dimension counts: {ordered_counts}")
    verdict = (
        VERDICT_RULES["any_non_satisfied"]
        if any(value for key, value in ordered_counts.items() if key != "satisfied")
        else VERDICT_RULES["all_satisfied"]
    )
    if verdict != EXPECTED_ACCEPTANCE["expected_verdict"]:
        raise EvidenceError(f"unexpected verdict: {verdict}")
    if rejected < EXPECTED_ACCEPTANCE["minimum_hostile_mutations"]:
        raise EvidenceError(f"only {rejected} hostile mutations rejected")
    return {
        "schema_version": EVIDENCE_SCHEMA_VERSION,
        "result": RESULT,
        "source_head": SOURCE_HEAD,
        "accepted_route_source": "c82c3a741053a9c8da260aa62e1a968af22bb54e",
        "source_bindings": {item["path"]: item["sha256"] for item in contract["inputs"]},
        "dimensions": dimensions,
        "dimension_counts": ordered_counts,
        "blocking_gaps": [item["id"] for item in dimensions if item["classification"] == "blocking_gap"],
        "operational_evidence_gaps": [item["id"] for item in dimensions if item["classification"] == "operational_evidence_gap"],
        "verdict": verdict,
        "next_tranche": NEXT_TRANCHE,
        "hostile_mutations_rejected": rejected,
        "closed_boundaries": {
            "app_imported": False,
            "route_called": False,
            "database_opened": False,
            "docker_used": False,
            "sql_executed": False,
            "browser_opened": False,
            "provider_called": False,
            "network_opened": False,
            "product_code_changed": False,
            "practice_enabled": False,
        },
    }


def render_report(evidence: dict[str, Any]) -> str:
    lines = [
        "# Provider-free read-only ordinary-practice canonical check-in admission-readiness review report",
        "",
        "Date: 2026-08-18",
        "",
        "Timestamp: 2026-08-18T22:34:05.3641972+10:00 (Australia/Brisbane)",
        "",
        "Status: frozen evidence",
        "",
        f"Result: `{evidence['result']}`",
        "",
        f"Verdict: `{evidence['verdict']}`",
        "",
        "## Outcome",
        "",
        "The accepted canonical check-in command core is not ready for ordinary-practice admission. Its typed API contract, dual Receptionist authorization, tenant-scoped transaction, idempotency/evidence, append-only audit/event and bounded client/waiting-area separation are present. Ordinary-practice admission control, selected-practice rollout/rollback and non-PHI observability are missing; runtime database-role, unknown-commit recovery and environment evidence remain unproved.",
        "",
        "The authored-synthetic allowlist is not an ordinary-practice admission mechanism and cannot be repurposed. Default denial remains unchanged.",
        "",
        "## Source boundary",
        "",
        "All 28 strict UTF-8 canonical-LF (bare-CR rejected) SHA-256 bindings matched before classification.",
        "",
        "| Path | SHA-256 |",
        "|---|---|",
    ]
    for path, digest in evidence["source_bindings"].items():
        lines.append(f"| `{path}` | `{digest}` |")
    lines.extend(
        [
            "",
            "## Dimension matrix",
            "",
            "| Order | Dimension | Classification | Source citations | Markers |",
            "|---:|---|---|---|---|",
        ]
    )
    for item in evidence["dimensions"]:
        citations = "; ".join(f"`{value}`" for value in item["citations"])
        markers = "; ".join(item["markers"])
        lines.append(
            f"| {item['order']} | `{item['id']}` | `{item['classification']}` | {citations} | {markers} |"
        )
    counts = evidence["dimension_counts"]
    lines.extend(
        [
            "",
            "## Counts and gaps",
            "",
            f"Satisfied: {counts['satisfied']}; blocking gaps: {counts['blocking_gap']}; operational-evidence gaps: {counts['operational_evidence_gap']}.",
            "",
            "Blocking gaps:",
            "",
        ]
    )
    lines.extend(f"- `{value}`" for value in evidence["blocking_gaps"])
    lines.extend(["", "Operational-evidence gaps:", ""])
    lines.extend(f"- `{value}`" for value in evidence["operational_evidence_gaps"])
    lines.extend(
        [
            "",
            "## Narrowest successor",
            "",
            f"`{evidence['next_tranche']}`",
            "",
            "That successor is architecture-only and remains default-off. It may specify separate ordinary versus authored-synthetic admission controls, non-PHI observability, runtime-role evidence, kill-switch and rollback prerequisites. It may not enable a practice or edit product code/configuration.",
            "",
            "## Hostile mutation suite",
            "",
            f"Rejected {evidence['hostile_mutations_rejected']} deterministic hostile contract mutations (minimum 120).",
            "",
            "## Closed boundaries",
            "",
            "| Boundary | Value |",
            "|---|---|",
        ]
    )
    for key, value in evidence["closed_boundaries"].items():
        lines.append(f"| {key} | {value} |")
    lines.extend(
        [
            "",
            "No `app` module was imported; no route, database, Docker, SQL, browser, provider or network surface was opened. No practice was enabled and no product source changed.",
            "",
        ]
    )
    return "\n".join(lines)


def write_outputs(root: Path, evidence: dict[str, Any]) -> None:
    evidence_path = root / EVIDENCE_PATH
    report_path = root / REPORT_PATH
    evidence_path.parent.mkdir(parents=True, exist_ok=True)
    evidence_path.write_text(
        json.dumps(evidence, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    report_path.write_text(render_report(evidence), encoding="utf-8", newline="\n")


def run_review(root: Path | None = None, *, release: bool = True) -> dict[str, Any]:
    root = Path(root) if root is not None else Path(__file__).resolve().parents[1]
    contract = load_contract(root)
    validate_contract(contract, root)
    texts = load_texts(contract, root)
    dimensions = prove_dimensions(texts)
    rejected = hostile_mutations(contract, root)
    evidence = build_evidence(contract, dimensions, rejected)
    if release:
        write_outputs(root, evidence)
    return evidence


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args(argv)
    try:
        run_review(args.repo_root, release=not args.no_write)
    except (ContractError, EvidenceError, OSError, json.JSONDecodeError) as exc:
        print(f"FAIL_CLOSED: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
