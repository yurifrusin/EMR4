"""Validate the source-bound default-off runtime-instrumentation architecture."""

from __future__ import annotations

import ast
import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Callable

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_DIR = (
    ROOT
    / "orchestration"
    / "continuity"
    / "raisa-provider-free-default-off-runtime-instrumentation-architecture"
)
CONTRACT_PATH = CONTRACT_DIR / "contract.json"
SCHEMA_PATH = CONTRACT_DIR / "contract.schema.json"
ROUTE_SOURCE_PATH = ROOT / "app/routers/appointments.py"
CONFIG_PATH = ROOT / "app/config.py"
DEPENDENCIES_PATH = ROOT / "app/dependencies.py"
MAIN_PATH = ROOT / "app/main.py"

EXPECTED_SOURCE_HEAD = "42e3f9a6df86210be2e7a3709118ad53ba496e98"
EXPECTED_SOURCES = {
    "app/routers/appointments.py": "ca6261323cb58a27c585a9d9fa851fc9ec4064d8a0f5a0441a9e696b13bd0b09",
    "app/config.py": "f0cafc21a88babd0d60d6ce30067a30d23b4030ad5dd4d26bb841096c62c1f2e",
    "app/dependencies.py": "d44f777f742074f0ee4717d599d7ee71dd6343c7096c87793149c727c1c4b0a9",
    "app/main.py": "dedcb8fe3eb3f76a915d2303da45d404a42fd926e687a73cb30245c744132130",
    "app/middleware/error_handler.py": "d63ec6a2ec76d00cb9bdcb8dd74edcaee52034837cc94db158e8529a358f7ef7",
    "tests/test_appointment_raw_compat.py": "af448fa32bd420bf134e09a7e72f107ca9bbec1c75c986f3494d96dbccdb972b",
    "docs/api-spine/legacy-compatibility-write-deprecation-map.md": "ca7325d4d68dedf5705424dddd4a5ed53cf4395fd2ea4915a0ae633caae64ed7",
    "orchestration/continuity/raisa-provider-free-unmounted-default-off-shadow-comparison-architecture/contract.json": "bbef6febf7046521dbc7112d25cfa7984c4acaa3a059872abd0bf183aecc2c81",
    "docs/raisa-provider-free-unmounted-authored-synthetic-shadow-comparison-rehearsal-closeout.md": "2a290dad9d6410421c44a62f0c575422bc417b541f534c866c304ee7e0dcbb7d",
    "orchestration/continuity/raisa-provider-free-unmounted-authored-synthetic-shadow-comparison-rehearsal/provider-free-authored-synthetic-shadow-comparison-evidence.json": "1e325571d66c683aca319b7efa19654105c88b19f19315a3a7db788d35edc2a9",
}
EXPECTED_ROUTES = {
    "raw_compat_create": {
        "family_id": "appointment_create", "method": "POST",
        "path": "/api/v1/appointments", "canonical_operation_id": "confirmAppointmentCreateProposal",
        "handler": "create_appointment", "handler_line_start": 1074, "handler_line_end": 1089,
        "command_helper": "_create_appointment_from_body", "helper_line_start": 936,
        "helper_line_end": 1011, "success_status": 201, "response_model": "AppointmentOut",
        "current_result_form": "direct_helper_return",
        "future_stage_rewrite": "assign_local_result_stage_then_return_same_object",
    },
    "raw_compat_update": {
        "family_id": "appointment_update", "method": "PUT",
        "path": "/api/v1/appointments/{appointment_id}", "canonical_operation_id": "confirmAppointmentUpdateProposal",
        "handler": "update_appointment", "handler_line_start": 5268, "handler_line_end": 5281,
        "command_helper": "_apply_appointment_update", "helper_line_start": 5138,
        "helper_line_end": 5264, "success_status": 200, "response_model": "AppointmentOut",
        "current_result_form": "direct_helper_return",
        "future_stage_rewrite": "assign_local_result_stage_then_return_same_object",
    },
    "raw_compat_status": {
        "family_id": "appointment_status", "method": "PATCH",
        "path": "/api/v1/appointments/{appointment_id}/status", "canonical_operation_id": "confirmAppointmentStatusProposal",
        "handler": "update_appointment_status", "handler_line_start": 5386, "handler_line_end": 5402,
        "command_helper": "_apply_appointment_status_update", "helper_line_start": 2871,
        "helper_line_end": 2908, "success_status": 200, "response_model": "AppointmentOut",
        "current_result_form": "direct_helper_return",
        "future_stage_rewrite": "assign_local_result_stage_then_return_same_object",
    },
    "raw_compat_delete": {
        "family_id": "appointment_delete", "method": "DELETE",
        "path": "/api/v1/appointments/{appointment_id}", "canonical_operation_id": "confirmAppointmentDeleteProposal",
        "handler": "cancel_appointment", "handler_line_start": 5574, "handler_line_end": 5590,
        "command_helper": "_apply_appointment_delete", "helper_line_start": 5532,
        "helper_line_end": 5570, "success_status": 204, "response_model": "none",
        "current_result_form": "helper_call_then_implicit_none",
        "future_stage_rewrite": "retain_implicit_none_after_stage",
    },
}
SCAFFOLD_STAGE_CONSTANTS = {
    "raw_compat_create": "RAW_COMPAT_CREATE_SHADOW_ADAPTER_ID",
    "raw_compat_update": "RAW_COMPAT_UPDATE_SHADOW_ADAPTER_ID",
    "raw_compat_status": "RAW_COMPAT_STATUS_SHADOW_ADAPTER_ID",
    "raw_compat_delete": "RAW_COMPAT_DELETE_SHADOW_ADAPTER_ID",
}
EXPECTED_PROJECTION_FIELDS = [
    "schema_version", "architecture_generation_digest", "route_adapter_id",
    "canonical_operation_id", "practice_scope_digest", "actor_digest", "actor_role",
    "session_digest", "purpose", "target_shape", "target_digest",
    "conflict_domain_digest", "command_digest", "precondition_present",
    "precondition_version", "precondition_digest", "confirmation_present",
    "confirmation_mode", "confirmation_reference_digest", "idempotency_present",
    "idempotency_key_digest", "canonicalization_version", "correlation_digest",
    "request_shape_digest",
]
EXPECTED_RECORD_FIELDS = [
    "schema_version", "architecture_generation_digest", "configuration_digest",
    "route_adapter_id", "canonical_operation_id", "practice_scope_digest",
    "correlation_digest", "request_shape_digest", "adapter_result", "gap_codes",
    "mismatch_field_codes", "comparison_class", "timing_category",
    "overflow_category", "recorded_at",
]
EXPECTED_FEEDBACK_EDGES = [
    "shadow_to_request_admission", "shadow_to_authorization", "shadow_to_http_status",
    "shadow_to_response_body", "shadow_to_response_headers", "shadow_to_transaction",
    "shadow_to_mutation", "shadow_to_mutation_audit", "shadow_to_retry",
    "shadow_to_latency_budget", "shadow_to_kernel_eligibility", "shadow_to_client_behavior",
]
EXPECTED_IMPLEMENTATION_GATE = [
    "provider_free_globally_disabled_typed_scaffold",
    "source_ast_and_import_dependency_proof",
    "disabled_path_zero_context_digest_and_handoff_calls",
    "authored_synthetic_live_local_route_byte_parity",
    "commit_audit_and_error_path_parity",
    "final_asgi_send_before_offer_order_proof",
    "single_assignment_take_clear_and_failure_containment",
    "complete_owned_runtime_cleanup",
]
EXPECTED_SEQUENCE = [
    "provider_free_default_off_instrumentation_scaffold",
    "ordinary_and_fallback_client_proposal_confirm_parity",
    "raw_status_kernel_convergence", "raw_delete_kernel_convergence",
    "raw_update_kernel_convergence", "create_schedule_fence_selection_and_proof",
    "raw_create_kernel_convergence",
]


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_contract() -> dict[str, Any]:
    return _load(CONTRACT_PATH)


def load_schema() -> dict[str, Any]:
    return _load(SCHEMA_PATH)


def _functions(path: Path) -> dict[str, ast.FunctionDef | ast.AsyncFunctionDef]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    return {
        node.name: node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }


def _called_names(node: ast.AST) -> list[str]:
    names: list[str] = []
    for child in ast.walk(node):
        if not isinstance(child, ast.Call):
            continue
        if isinstance(child.func, ast.Name):
            names.append(child.func.id)
        elif isinstance(child.func, ast.Attribute):
            names.append(child.func.attr)
    return names


def _handler_result_form(node: ast.FunctionDef | ast.AsyncFunctionDef, helper: str) -> str:
    returns = [child for child in ast.walk(node) if isinstance(child, ast.Return)]
    for result in returns:
        if isinstance(result.value, ast.Call):
            name = result.value.func.id if isinstance(result.value.func, ast.Name) else None
            if name == helper:
                return "direct_helper_return"
    if helper in _called_names(node) and not returns:
        return "helper_call_then_implicit_none"
    return "other"


def _call_name(call: ast.Call) -> str | None:
    if isinstance(call.func, ast.Name):
        return call.func.id
    return None


def _authorized_scaffold_handler(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
    *,
    adapter_id: str,
    helper: str,
) -> bool:
    """Recognize only the accepted dormant descendant of an original route seam."""
    helper_indexes: list[int] = []
    stage_indexes: list[int] = []
    return_indexes: list[int] = []
    for index, statement in enumerate(node.body):
        if isinstance(statement, ast.Assign) and isinstance(statement.value, ast.Call):
            if _call_name(statement.value) == helper:
                if not (
                    len(statement.targets) == 1
                    and isinstance(statement.targets[0], ast.Name)
                    and statement.targets[0].id == "result"
                ):
                    return False
                helper_indexes.append(index)
        elif isinstance(statement, ast.Expr) and isinstance(statement.value, ast.Call):
            if _call_name(statement.value) == helper:
                helper_indexes.append(index)
            call = statement.value
            if (
                isinstance(call.func, ast.Attribute)
                and isinstance(call.func.value, ast.Name)
                and call.func.value.id == "shadow_instrumentation_runtime"
                and call.func.attr == "try_stage"
            ):
                if not (
                    len(call.args) == 1
                    and isinstance(call.args[0], ast.Name)
                    and call.args[0].id == SCAFFOLD_STAGE_CONSTANTS[adapter_id]
                    and not call.keywords
                ):
                    return False
                stage_indexes.append(index)
        elif isinstance(statement, ast.Return):
            return_indexes.append(index)

    if len(helper_indexes) != 1 or len(stage_indexes) != 1:
        return False
    helper_index = helper_indexes[0]
    stage_index = stage_indexes[0]
    if adapter_id == "raw_compat_delete":
        return not return_indexes and stage_index == helper_index + 1
    return (
        len(return_indexes) == 1
        and stage_index == helper_index + 1
        and return_indexes[0] == stage_index + 1
        and isinstance(node.body[return_indexes[0]].value, ast.Name)
        and node.body[return_indexes[0]].value.id == "result"
    )


def _scaffold_descendant_present() -> bool:
    return (
        (ROOT / "app/services/diary/shadow_instrumentation.py").is_file()
        and (ROOT / "app/middleware/shadow_instrumentation.py").is_file()
        and "ShadowAfterSendMiddleware" in MAIN_PATH.read_text(encoding="utf-8")
    )


def source_errors(packet: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    functions = _functions(ROUTE_SOURCE_PATH)
    route_rows = {row["adapter_id"]: row for row in packet["source_inventory"]["route_seams"]}
    if set(route_rows) != set(EXPECTED_ROUTES):
        errors.append("source_route_set_mismatch")
        return errors
    for adapter_id, expected in EXPECTED_ROUTES.items():
        row = route_rows[adapter_id]
        for key, value in expected.items():
            if row.get(key) != value:
                errors.append(f"route_contract_mismatch:{adapter_id}:{key}")
        handler = functions.get(expected["handler"])
        helper = functions.get(expected["command_helper"])
        if handler is None or helper is None:
            errors.append(f"route_function_missing:{adapter_id}")
            continue
        original_shape = (
            (handler.lineno, handler.end_lineno)
            == (expected["handler_line_start"], expected["handler_line_end"])
            and (helper.lineno, helper.end_lineno)
            == (expected["helper_line_start"], expected["helper_line_end"])
            and _handler_result_form(handler, expected["command_helper"])
            == expected["current_result_form"]
        )
        scaffold_shape = _authorized_scaffold_handler(
            handler,
            adapter_id=adapter_id,
            helper=expected["command_helper"],
        )
        if not original_shape and not scaffold_shape:
            errors.append(f"handler_not_original_or_authorized_scaffold:{adapter_id}")
        helper_calls = _called_names(helper)
        if "_write_audit" not in helper_calls or "commit" not in helper_calls:
            errors.append(f"helper_audit_commit_missing:{adapter_id}")
        if helper_calls.index("_write_audit") > helper_calls.index("commit"):
            errors.append(f"helper_commit_before_audit:{adapter_id}")
        args = {arg.arg for arg in handler.args.args + handler.args.kwonlyargs}
        if "request" in args:
            errors.append(f"request_context_already_present:{adapter_id}")
    dep_functions = _functions(DEPENDENCIES_PATH)
    auth = dep_functions.get("get_current_user")
    if auth is None:
        errors.append("get_current_user_missing")
    else:
        auth_args = {arg.arg for arg in auth.args.args + auth.args.kwonlyargs}
        if "request" in auth_args or "session" in auth_args or "correlation" in auth_args:
            errors.append("unsafe_source_context_claim")
    if 'appointment_raw_compat_mode: Literal["audit", "header", "off"] = "audit"' not in CONFIG_PATH.read_text(encoding="utf-8"):
        errors.append("raw_compat_default_changed")
    main_text = MAIN_PATH.read_text(encoding="utf-8")
    cors_registration = "app.add_middleware(\n    CORSMiddleware"
    error_index = main_text.find("app.add_middleware(ErrorHandlerMiddleware)")
    cors_index = main_text.find(cors_registration)
    shadow_index = main_text.find("app.add_middleware(\n    ShadowAfterSendMiddleware")
    original_middleware = 0 <= error_index < cors_index and shadow_index == -1
    scaffold_middleware = 0 <= error_index < cors_index < shadow_index
    if not original_middleware and not scaffold_middleware:
        errors.append("middleware_order_changed")
    return errors


def semantic_errors(packet: dict[str, Any], *, verify_source_files: bool = False) -> list[str]:
    errors: list[str] = []
    if packet["source_head"] != EXPECTED_SOURCE_HEAD:
        errors.append("source_head_mismatch")
    bindings = {row["path"]: row["sha256"] for row in packet["source_bindings"]}
    if bindings != EXPECTED_SOURCES:
        errors.append("source_bindings_mismatch")
    if verify_source_files:
        live_source_errors = source_errors(packet)
        scaffold_descendant = _scaffold_descendant_present() and not live_source_errors
        for path, digest in EXPECTED_SOURCES.items():
            source = ROOT / path
            authorized_mutable_path = scaffold_descendant and path in {
                "app/routers/appointments.py",
                "app/main.py",
            }
            if (
                not source.is_file()
                or (_hash(source) != digest and not authorized_mutable_path)
            ):
                errors.append(f"source_file_hash_mismatch:{path}")
        errors.extend(live_source_errors)

    inventory = packet["source_inventory"]
    route_rows = {row["adapter_id"]: row for row in inventory["route_seams"]}
    if set(route_rows) != set(EXPECTED_ROUTES):
        errors.append("route_contract_set_mismatch")
    else:
        for adapter_id, expected in EXPECTED_ROUTES.items():
            for key, value in expected.items():
                if route_rows[adapter_id].get(key) != value:
                    errors.append(f"route_contract_mismatch:{adapter_id}:{key}")
    helper = inventory["raw_compat_helper"]
    if helper != {
        "function": "_raw_compat_evidence_and_headers", "line_start": 277,
        "line_end": 299, "setting": "appointment_raw_compat_mode",
        "default": "audit", "shadow_authority": False,
    }:
        errors.append("raw_compat_helper_mismatch")
    shared = inventory["shared_route_facts"]
    expected_shared = {
        "authenticated_user_dependency": "require_role_via_get_current_user",
        "request_parameter_present": False, "server_session_reference_present": False,
        "server_correlation_reference_present": False, "shadow_setting_present": False,
        "shadow_middleware_present": False,
        "current_user_middleware_order": ["CORSMiddleware", "ErrorHandlerMiddleware"],
    }
    if shared != expected_shared:
        errors.append("shared_route_facts_mismatch")

    completion = packet["primary_completion"]
    if completion["route_stage_primary_state"] != "transaction_audit_and_logical_result_complete_response_not_yet_serialized":
        errors.append("route_stage_primary_state_overclaimed")
    if completion["handoff_primary_state"] != "final_asgi_response_body_frame_successfully_sent":
        errors.append("handoff_before_response_send")
    if completion["route_local_observer_call_permitted"] or not completion["post_send_handoff_required"]:
        errors.append("route_local_observer_open")

    config = packet["generation_configuration"]
    expected_config = {
        "model": "immutable_process_start_generation",
        "amendment": "new_generation_and_static_review", "required_status": "current",
        "global_default": "disabled", "practice_allowlist_default": [],
        "route_allowlist_default": [], "digest_key_reference_default": None,
        "database_or_network_lookup": False, "separate_from_setting": "appointment_raw_compat_mode",
        "raw_compat_setting_shadow_authority": False,
        "external_disable_latch": "monotonic_false_to_true_disable_only",
        "missing_unknown_stale_or_revoked": "disabled_no_stage",
        "enablement_authority_granted": False,
    }
    if config != expected_config:
        errors.append("generation_configuration_mismatch")

    context = packet["request_context"]
    if context["required_fields"] != [
        "practice_id", "actor_id", "actor_role", "authenticated_session_reference",
        "server_correlation_reference",
    ]:
        errors.append("request_context_fields_mismatch")
    if context["provenance"] != "server_created_and_authenticated_only" or context["missing_context"] != "disabled_no_stage":
        errors.append("request_context_fail_closed_mismatch")
    if any(context[key] != "forbidden" for key in (
        "bearer_token_hashing", "inbound_correlation_authority",
        "actor_practice_session_synthesis", "direct_identifier_fallback",
    )):
        errors.append("request_context_fallback_open")

    stage = packet["route_staging_phase"]
    if stage["stage_point"] != "after_command_helper_success_before_route_return":
        errors.append("stage_point_mismatch")
    if stage["admission_order"] != [
        "read_immutable_generation", "global_enabled_short_circuit", "generation_current",
        "external_disable_clear", "safe_server_context_present", "practice_digest_allowlisted",
        "exact_route_allowlisted", "digest_key_reference_available",
        "build_minimized_projection", "single_assignment_request_cell_store",
    ]:
        errors.append("stage_admission_order_mismatch")
    if not stage["global_disabled_short_circuit_before_raw_input_read"] or stage["input_read_before_full_admission"]:
        errors.append("stage_reads_before_admission")
    if any(stage[key] for key in ("adapter_invoked", "observer_invoked", "sink_invoked", "retry")):
        errors.append("stage_runtime_or_retry_open")
    if stage["return_channel"] != "none":
        errors.append("stage_return_channel_open")

    finalizer = packet["post_response_finalizer"]
    expected_finalizer = {
        "type": "ShadowAfterSendFinalizer",
        "mount": "outermost_user_asgi_middleware_around_existing_cors_and_error_stack",
        "message_trigger": "http.response.body_with_more_body_false",
        "send_order": "await_original_send_success_before_handoff",
        "cell_operation": "atomic_take_and_clear_at_most_once", "offer_port": "offer_nowait",
        "offer_awaited": False, "offer_result_channel": "none", "retry": False,
        "failure": "contain_after_response_send", "no_cell": "no_operation",
        "send_callable_passed_to_offer": False, "response_material_passed_to_offer": False,
    }
    if finalizer != expected_finalizer:
        errors.append("post_response_finalizer_mismatch")

    projection = packet["projection"]
    if projection["allowed_fields"] != EXPECTED_PROJECTION_FIELDS:
        errors.append("projection_field_set_mismatch")
    if projection["identity_encoding"] != "domain_separated_versioned_hmac":
        errors.append("projection_identity_encoding_mismatch")
    if projection["free_text_inputs"] or projection["response_inputs"]:
        errors.append("projection_sensitive_input_open")
    if projection["request_shape_derivation"] != "allowlisted_field_names_and_closed_type_labels_only":
        errors.append("request_shape_derivation_mismatch")
    if projection["command_digest_derivation"] != "allowlisted_non_free_text_structural_values_only":
        errors.append("command_digest_derivation_mismatch")
    if projection["raw_input_retention"] or projection["digest_key_exposed"]:
        errors.append("projection_retention_or_key_open")
    forbidden = set(projection["forbidden_inputs"])
    if set(projection["allowed_fields"]) & forbidden or not {
        "appointment_reason_free_text", "appointment_note_free_text", "raw_request_body",
        "raw_response_body", "response_headers", "bearer_token", "credential",
    } <= forbidden:
        errors.append("projection_forbidden_input_mismatch")

    record = packet["diagnostic_record"]
    if record["allowed_fields"] != EXPECTED_RECORD_FIELDS:
        errors.append("diagnostic_field_set_mismatch")
    if record["authority"] != "diagnostic_only_non_authoritative_lossy":
        errors.append("diagnostic_authority_mismatch")
    if any(record[key] for key in ("command_outcome", "audit_or_truth_record", "persistence_selected")):
        errors.append("diagnostic_effect_open")

    modules = packet["capability_modules"]
    required_forbidden = {
        "generation_reader": {"database", "network", "provider", "credential_value", "command"},
        "route_stage": {"observer", "adapter", "sink", "database", "transaction", "response_writer", "audit_writer", "event", "kernel", "command"},
        "after_send_finalizer": {"route_handler", "database", "transaction", "response_body", "response_headers", "send_callable_to_offer", "audit_writer", "event", "kernel", "command"},
        "downstream_observer": {"route_handler", "request", "response", "database", "source", "audit_writer", "event", "kernel", "command"},
    }
    for module, required in required_forbidden.items():
        if not required <= set(modules[module]["forbidden"]):
            errors.append(f"capability_boundary_open:{module}")
    if packet["forbidden_feedback_edges"] != EXPECTED_FEEDBACK_EDGES:
        errors.append("forbidden_feedback_edges_mismatch")
    if packet["future_implementation_gate"] != EXPECTED_IMPLEMENTATION_GATE:
        errors.append("future_implementation_gate_mismatch")
    if packet["future_evidence_sequence"] != EXPECTED_SEQUENCE:
        errors.append("future_evidence_sequence_mismatch")
    if any(packet["claim_boundary"].values()):
        errors.append("claim_boundary_not_zero")
    if any(packet["effect_boundary"].values()):
        errors.append("effect_boundary_not_zero")
    return sorted(set(errors))


def validate_contract(packet: dict[str, Any], *, verify_source_files: bool = False) -> list[str]:
    schema = load_schema()
    Draft202012Validator.check_schema(schema)
    schema_errors = sorted(
        f"schema:{error.json_path}:{error.message}"
        for error in Draft202012Validator(schema).iter_errors(packet)
    )
    try:
        semantic = semantic_errors(packet, verify_source_files=verify_source_files)
    except (KeyError, TypeError, ValueError, IndexError, json.JSONDecodeError) as error:
        semantic = [f"semantic_validation_failed:{type(error).__name__}"]
    return sorted(set(schema_errors + semantic))


def hostile_mutations(packet: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    mutations: list[tuple[str, Callable[[dict[str, Any]], None]]] = [
        ("source_head", lambda p: p.__setitem__("source_head", "0" * 40)),
        ("source_hash", lambda p: p["source_bindings"][0].__setitem__("sha256", "0" * 64)),
        ("source_removed", lambda p: p["source_bindings"].pop()),
        ("application_edit", lambda p: p["claim_boundary"].__setitem__("application_source_edited", True)),
        ("runtime_created", lambda p: p["claim_boundary"].__setitem__("runtime_instrumentation_created", True)),
        ("product_data", lambda p: p["claim_boundary"].__setitem__("product_or_patient_data_used", True)),
        ("route_removed", lambda p: p["source_inventory"]["route_seams"].pop()),
        ("route_handler", lambda p: p["source_inventory"]["route_seams"][0].__setitem__("handler", "other")),
        ("route_line", lambda p: p["source_inventory"]["route_seams"][0].__setitem__("handler_line_start", 1)),
        ("route_result", lambda p: p["source_inventory"]["route_seams"][3].__setitem__("current_result_form", "direct_helper_return")),
        ("raw_helper_default", lambda p: p["source_inventory"]["raw_compat_helper"].__setitem__("default", "header")),
        ("shadow_setting_claim", lambda p: p["source_inventory"]["shared_route_facts"].__setitem__("shadow_setting_present", True)),
        ("request_claim", lambda p: p["source_inventory"]["shared_route_facts"].__setitem__("request_parameter_present", True)),
        ("route_stage_sealed", lambda p: p["primary_completion"].__setitem__("route_stage_primary_state", "response_sealed")),
        ("handoff_pre_send", lambda p: p["primary_completion"].__setitem__("handoff_primary_state", "before_send")),
        ("route_observer", lambda p: p["primary_completion"].__setitem__("route_local_observer_call_permitted", True)),
        ("post_send_not_required", lambda p: p["primary_completion"].__setitem__("post_send_handoff_required", False)),
        ("mutable_generation", lambda p: p["generation_configuration"].__setitem__("model", "mutable")),
        ("global_enabled", lambda p: p["generation_configuration"].__setitem__("global_default", "enabled")),
        ("practice_allowed", lambda p: p["generation_configuration"]["practice_allowlist_default"].append("x")),
        ("route_allowed", lambda p: p["generation_configuration"]["route_allowlist_default"].append("raw_compat_status")),
        ("key_default", lambda p: p["generation_configuration"].__setitem__("digest_key_reference_default", "key")),
        ("database_flag", lambda p: p["generation_configuration"].__setitem__("database_or_network_lookup", True)),
        ("compat_controls_shadow", lambda p: p["generation_configuration"].__setitem__("raw_compat_setting_shadow_authority", True)),
        ("kill_enables", lambda p: p["generation_configuration"].__setitem__("external_disable_latch", "enable_or_disable")),
        ("enablement_authority", lambda p: p["generation_configuration"].__setitem__("enablement_authority_granted", True)),
        ("session_removed", lambda p: p["request_context"]["required_fields"].remove("authenticated_session_reference")),
        ("token_hash", lambda p: p["request_context"].__setitem__("bearer_token_hashing", "allowed")),
        ("inbound_correlation", lambda p: p["request_context"].__setitem__("inbound_correlation_authority", "allowed")),
        ("context_fallback", lambda p: p["request_context"].__setitem__("missing_context", "synthesize")),
        ("stage_before_success", lambda p: p["route_staging_phase"].__setitem__("stage_point", "before_commit")),
        ("admission_reordered", lambda p: p["route_staging_phase"]["admission_order"].reverse()),
        ("reads_before_admission", lambda p: p["route_staging_phase"].__setitem__("input_read_before_full_admission", True)),
        ("adapter_invoked", lambda p: p["route_staging_phase"].__setitem__("adapter_invoked", True)),
        ("observer_invoked", lambda p: p["route_staging_phase"].__setitem__("observer_invoked", True)),
        ("stage_return", lambda p: p["route_staging_phase"].__setitem__("return_channel", "observer_result")),
        ("send_after_offer", lambda p: p["post_response_finalizer"].__setitem__("send_order", "handoff_before_send")),
        ("offer_awaited", lambda p: p["post_response_finalizer"].__setitem__("offer_awaited", True)),
        ("offer_result", lambda p: p["post_response_finalizer"].__setitem__("offer_result_channel", "handler")),
        ("offer_retry", lambda p: p["post_response_finalizer"].__setitem__("retry", True)),
        ("send_exposed", lambda p: p["post_response_finalizer"].__setitem__("send_callable_passed_to_offer", True)),
        ("response_exposed", lambda p: p["post_response_finalizer"].__setitem__("response_material_passed_to_offer", True)),
        ("projection_removed", lambda p: p["projection"]["allowed_fields"].pop()),
        ("free_text_input", lambda p: p["projection"]["free_text_inputs"].append("reason")),
        ("response_input", lambda p: p["projection"]["response_inputs"].append("body")),
        ("shape_raw", lambda p: p["projection"].__setitem__("request_shape_derivation", "raw_values")),
        ("command_free_text", lambda p: p["projection"].__setitem__("command_digest_derivation", "all_values")),
        ("raw_retained", lambda p: p["projection"].__setitem__("raw_input_retention", True)),
        ("key_exposed", lambda p: p["projection"].__setitem__("digest_key_exposed", True)),
        ("record_removed", lambda p: p["diagnostic_record"]["allowed_fields"].pop()),
        ("record_authority", lambda p: p["diagnostic_record"].__setitem__("authority", "source_truth")),
        ("record_persisted", lambda p: p["diagnostic_record"].__setitem__("persistence_selected", True)),
        ("route_stage_command", lambda p: p["capability_modules"]["route_stage"]["forbidden"].remove("command")),
        ("finalizer_response", lambda p: p["capability_modules"]["after_send_finalizer"]["forbidden"].remove("response_body")),
        ("observer_kernel", lambda p: p["capability_modules"]["downstream_observer"]["forbidden"].remove("kernel")),
        ("feedback_removed", lambda p: p["forbidden_feedback_edges"].pop()),
        ("gate_removed", lambda p: p["future_implementation_gate"].pop()),
        ("sequence_reordered", lambda p: p["future_evidence_sequence"].reverse()),
        ("effect_runtime", lambda p: p["effect_boundary"].__setitem__("runtime_import_or_execution", True)),
        ("effect_response", lambda p: p["effect_boundary"].__setitem__("response_or_audit_change", True)),
    ]
    results: list[tuple[str, dict[str, Any]]] = []
    for name, mutate in mutations:
        candidate = copy.deepcopy(packet)
        mutate(candidate)
        results.append((name, candidate))
    return results


def build_report(packet: dict[str, Any] | None = None) -> dict[str, Any]:
    packet = load_contract() if packet is None else packet
    errors = validate_contract(packet, verify_source_files=True)
    mutants = hostile_mutations(packet)
    escaped = [name for name, mutant in mutants if not validate_contract(mutant)]
    if escaped:
        errors.append("hostile_mutation_escaped:" + ",".join(escaped))
    return {
        "schema_version": "emr4.default-off-runtime-instrumentation-architecture-report.v1",
        "status": "passed" if not errors else "failed", "reasons": sorted(set(errors)),
        "source_head": packet["source_head"],
        "raw_route_count": len(packet["source_inventory"]["route_seams"]),
        "phase_count": 2,
        "projection_field_count": len(packet["projection"]["allowed_fields"]),
        "record_field_count": len(packet["diagnostic_record"]["allowed_fields"]),
        "forbidden_feedback_edge_count": len(packet["forbidden_feedback_edges"]),
        "hostile_mutation_count": len(mutants),
        "hostile_mutation_escape_count": len(escaped),
        "application_source_edited": False, "runtime_instrumentation_created": False,
        "provider_or_network_used": False, "command_or_write_performed": False,
    }


def main() -> int:
    report = build_report()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
