"""Validate the provider-free AES-C0 architecture and authored-synthetic packet."""

from __future__ import annotations

import argparse
import copy
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[1]
BASE = (
    ROOT
    / "orchestration/continuity/"
    "raisa-agent-execution-surface-containment-gate-aes-c0"
)
CONTRACT_PATH = BASE / "architecture-contract.json"
SCHEMA_PATH = BASE / "architecture-contract.schema.json"
EXAMPLES_PATH = BASE / "authored-synthetic-contract-examples.json"

MESSAGE_DEFS = {
    "generation_manifest": "GenerationManifest",
    "capability_lease": "CapabilityLease",
    "budget_state": "BudgetState",
    "broker_decision": "BrokerDecision",
    "revocation_record": "RevocationRecord",
    "audit_evidence": "AuditEvidenceEnvelope",
}

LEASEABLE_CLASSES = {
    "provider_inference",
    "authoritative_read",
    "inert_tool_adapter",
}
ALWAYS_DENIED = {
    "generic_network",
    "filesystem",
    "database_or_sql",
    "shell_or_process",
    "cloud_or_container_metadata",
    "repository_or_ci_write",
    "provider_executed_tool",
    "runtime_or_deployment_control",
    "product_command",
    "credential_enumeration",
}
BUDGET_DIMENSIONS = {
    "reasoning": {"model_calls", "model_tokens"},
    "information": {"input_bytes", "output_bytes", "source_count"},
    "egress": {
        "request_count",
        "request_bytes",
        "response_bytes",
        "total_bytes",
        "distinct_destinations",
        "redirects",
    },
    "action": {
        "broker_operations",
        "inert_tool_operations",
        "product_mutations",
        "command_confirmations",
    },
    "denial": {"denied_operations", "boundary_probes", "repeated_failures"},
    "time": {"elapsed_ms"},
}
STOP_CONDITIONS = {
    "reasoning_budget_exhausted",
    "information_budget_exhausted",
    "egress_budget_exhausted",
    "action_budget_exhausted",
    "denial_budget_exhausted",
    "elapsed_time_exhausted",
    "boundary_probe_detected",
    "authority_changed",
    "generation_superseded",
    "supply_chain_identity_mismatch",
    "external_kill_switch",
}


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def _json_key(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _resolve_ref(root_schema: dict[str, Any], reference: str) -> dict[str, Any]:
    prefix = "#/$defs/"
    if not reference.startswith(prefix):
        raise ValueError(f"unsupported schema reference: {reference}")
    value = root_schema["$defs"][reference[len(prefix) :]]
    if not isinstance(value, dict):
        raise ValueError(f"schema reference is not an object: {reference}")
    return value


def _is_type(value: Any, expected: str) -> bool:
    return {
        "object": isinstance(value, dict),
        "array": isinstance(value, list),
        "string": isinstance(value, str),
        "integer": isinstance(value, int) and not isinstance(value, bool),
        "boolean": isinstance(value, bool),
    }.get(expected, False)


def _valid_datetime(value: str) -> bool:
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return True


def validate_instance(
    value: Any,
    schema: dict[str, Any],
    *,
    root_schema: dict[str, Any],
    path: str = "$",
) -> list[str]:
    """Validate the closed JSON-Schema subset used by AES-C0."""

    if "$ref" in schema:
        return validate_instance(
            value,
            _resolve_ref(root_schema, schema["$ref"]),
            root_schema=root_schema,
            path=path,
        )

    errors: list[str] = []
    expected_type = schema.get("type")
    if isinstance(expected_type, str) and not _is_type(value, expected_type):
        return [f"{path}:type:{expected_type}"]
    if "const" in schema and value != schema["const"]:
        errors.append(f"{path}:const")
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}:enum")

    if isinstance(value, dict):
        required = set(schema.get("required", []))
        missing = required - set(value)
        for key in sorted(missing):
            errors.append(f"{path}:missing:{key}")
        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            for key in sorted(set(value) - set(properties)):
                errors.append(f"{path}:extra:{key}")
        for key, child in value.items():
            child_schema = properties.get(key)
            if isinstance(child_schema, dict):
                errors.extend(
                    validate_instance(
                        child,
                        child_schema,
                        root_schema=root_schema,
                        path=f"{path}.{key}",
                    )
                )

    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0):
            errors.append(f"{path}:minItems")
        maximum = schema.get("maxItems")
        if isinstance(maximum, int) and len(value) > maximum:
            errors.append(f"{path}:maxItems")
        if schema.get("uniqueItems") and len({_json_key(item) for item in value}) != len(
            value
        ):
            errors.append(f"{path}:uniqueItems")
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, child in enumerate(value):
                errors.extend(
                    validate_instance(
                        child,
                        item_schema,
                        root_schema=root_schema,
                        path=f"{path}[{index}]",
                    )
                )

    if isinstance(value, str):
        pattern = schema.get("pattern")
        if isinstance(pattern, str) and re.fullmatch(pattern, value) is None:
            errors.append(f"{path}:pattern")
        if schema.get("format") == "date-time" and not _valid_datetime(value):
            errors.append(f"{path}:date-time")

    if isinstance(value, int) and not isinstance(value, bool):
        minimum = schema.get("minimum")
        if isinstance(minimum, int) and value < minimum:
            errors.append(f"{path}:minimum")
    return errors


def validate_schema(schema: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
        errors.append("schema:draft")
    if schema.get("additionalProperties") is not False:
        errors.append("schema:root_not_closed")
    expected_defs = {
        "Digest",
        "Identifier",
        "Timestamp",
        "CapabilityGrant",
        "ReasoningBudget",
        "InformationBudget",
        "EgressBudget",
        "ActionBudget",
        "DenialBudget",
        "TimeBudget",
        "BudgetLimits",
        "BudgetCounters",
        "SupplyChainIdentity",
        *MESSAGE_DEFS.values(),
    }
    if set(schema.get("$defs", {})) != expected_defs:
        errors.append("schema:defs_not_exact")
    for name in MESSAGE_DEFS.values():
        definition = schema.get("$defs", {}).get(name, {})
        if definition.get("additionalProperties") is not False:
            errors.append(f"schema:{name}:not_closed")
        if not definition.get("required"):
            errors.append(f"schema:{name}:required_missing")
    return errors


def _exact_keys(value: dict[str, Any], keys: set[str], label: str) -> list[str]:
    return [] if set(value) == keys else [f"{label}:keys_not_exact"]


def validate_contract(
    contract: dict[str, Any], schema: dict[str, Any]
) -> list[str]:
    errors = validate_instance(contract, schema, root_schema=schema)
    errors.extend(validate_schema(schema))

    boundary = contract.get("authority_boundary", {})
    expected_boundary_keys = {
        "runtime_implementation",
        "provider_call",
        "product_or_patient_data",
        "credential_or_iam",
        "network_or_metadata_access",
        "database_or_source_access",
        "tool_execution",
        "command_or_write",
        "deployment_or_production",
        "release_or_pages",
        "protected_ref_movement",
    }
    errors.extend(_exact_keys(boundary, expected_boundary_keys, "authority_boundary"))
    if any(boundary.get(key) is not False for key in expected_boundary_keys):
        errors.append("authority_boundary:opening_detected")

    trust = contract.get("trust_boundaries", [])
    trust_ids = {item.get("boundary_id") for item in trust if isinstance(item, dict)}
    if trust_ids != {
        "authorized_surface_to_authority_kernel",
        "context_assembler_to_work_cell",
        "work_cell_to_proofreader",
        "proofreader_to_capability_broker",
        "broker_to_exact_adapter",
        "adapter_to_external_or_product_system",
        "proposal_to_rest_command_plane",
        "telemetry_to_external_stop_control",
    }:
        errors.append("trust_boundaries:not_exact")
    for item in trust:
        if set(item) != {
            "boundary_id",
            "from",
            "to",
            "enforcement_owner",
            "model_controls_boundary",
        }:
            errors.append("trust_boundaries:keys_not_exact")
        if item.get("model_controls_boundary") is not False:
            errors.append("trust_boundaries:model_control")

    classes = contract.get("capability_classes", {})
    errors.extend(
        _exact_keys(
            classes,
            {"leaseable", "non_leaseable_outputs", "always_denied"},
            "capability_classes",
        )
    )
    leaseable = classes.get("leaseable", [])
    if {item.get("class_id") for item in leaseable} != LEASEABLE_CLASSES:
        errors.append("capability_classes:leaseable_not_exact")
    for item in leaseable:
        if item.get("broker_resolves_operation_identity") is not True:
            errors.append("capability_classes:broker_resolution_missing")
        for key in (
            "candidate_selects_operation_identity",
            "command_authority",
            "provider_executed_tools",
        ):
            if item.get(key) is not False:
                errors.append(f"capability_classes:{key}")
    if set(classes.get("always_denied", [])) != ALWAYS_DENIED:
        errors.append("capability_classes:denied_not_exact")
    output = classes.get("non_leaseable_outputs", [])
    if len(output) != 1 or output[0] != {
        "class_id": "typed_proposal_egress",
        "destination": "deterministic_proofreader_only",
        "executable": False,
        "command_authority": False,
    }:
        errors.append("capability_classes:proposal_egress_not_exact")

    influence = contract.get("candidate_influence_policy", {})
    high_risk = {
        "adapter_id",
        "operation_id",
        "destination_id",
        "url",
        "method",
        "credential",
        "filesystem_path",
        "sql",
        "executable",
        "tool_definition",
        "command_route",
        "cleanup_target",
        "policy_amendment",
    }
    if high_risk - set(influence.get("candidate_must_not_supply", [])):
        errors.append("candidate_influence:high_risk_gap")
    if set(influence.get("candidate_may_supply", [])) & high_risk:
        errors.append("candidate_influence:high_risk_allowed")
    for key in (
        "template_interpretation",
        "path_dereference",
        "url_fetch_from_content",
        "executable_deserialization",
    ):
        if influence.get(key) is not False:
            errors.append(f"candidate_influence:{key}")
    if influence.get("context_and_memory_are_inert") is not True:
        errors.append("candidate_influence:context_not_inert")

    manifest = contract.get("generation_manifest_policy", {})
    for key in (
        "immutable_per_generation",
        "policy_change_requires_new_generation",
        "one_bureau_per_generation",
        "one_work_cell_per_generation",
        "principal_purpose_binding_required",
        "current_authority_recheck_required",
        "exact_capability_grants_required",
    ):
        if manifest.get(key) is not True:
            errors.append(f"generation_manifest:{key}")
    for key in (
        "work_cell_receives_manifest_as_authority",
        "work_cell_receives_lease_or_credential",
    ):
        if manifest.get(key) is not False:
            errors.append(f"generation_manifest:{key}")
    if set(manifest.get("required_stop_conditions", [])) != STOP_CONDITIONS:
        errors.append("generation_manifest:stop_conditions_not_exact")

    budget = contract.get("budget_policy", {})
    dimensions = budget.get("dimensions", [])
    if {item.get("dimension") for item in dimensions} != set(BUDGET_DIMENSIONS):
        errors.append("budget:dimensions_not_exact")
    for item in dimensions:
        dimension = item.get("dimension")
        if set(item.get("counters", [])) != BUDGET_DIMENSIONS.get(dimension, set()):
            errors.append(f"budget:{dimension}:counters")
        if item.get("cumulative") is not True:
            errors.append(f"budget:{dimension}:not_cumulative")
    for key in (
        "encoded_compressed_chunked_and_exception_channels_share_egress_budget",
        "denied_attempts_are_counted",
        "exhaustion_stops_before_next_operation",
    ):
        if budget.get(key) is not True:
            errors.append(f"budget:{key}")
    if budget.get("budgets_transfer_between_generations") is not False:
        errors.append("budget:cross_generation_transfer")
    for key, expected in (
        ("maximum_distinct_destinations_per_generation", 1),
        ("maximum_redirects_per_generation", 0),
        ("maximum_product_mutations_per_generation", 0),
        ("maximum_command_confirmations_per_generation", 0),
    ):
        if budget.get(key) != expected:
            errors.append(f"budget:{key}")

    routes = contract.get("route_classification", {})
    if set(routes) != {
        "graphql_query",
        "event_signal",
        "access_ai_provider_invocation",
        "rest_openapi_command",
        "sql_or_database_connection",
    }:
        errors.append("routes:not_exact")
    graphql = routes.get("graphql_query", {})
    if (
        graphql.get("classification") != "read_only_context_plane"
        or graphql.get("work_cell_direct_access") is not False
        or graphql.get("generic_broker_query") is not False
        or graphql.get("typed_adapter_only") is not True
        or graphql.get("current_authority_required") is not True
        or graphql.get("command_authority") is not False
    ):
        errors.append("routes:graphql_boundary")
    event = routes.get("event_signal", {})
    if (
        event.get("current_truth") is not False
        or event.get("capability_lease") is not False
        or event.get("fresh_authorized_read_required") is not True
        or event.get("command_authority") is not False
    ):
        errors.append("routes:event_boundary")
    access_ai = routes.get("access_ai_provider_invocation", {})
    if (
        access_ai.get("frontend_direct_access") is not False
        or access_ai.get("work_cell_direct_credential") is not False
        or access_ai.get("provider_executed_tools") is not False
        or access_ai.get("proofreader_release_required") is not True
    ):
        errors.append("routes:access_ai_boundary")
    command = routes.get("rest_openapi_command", {})
    if (
        command.get("work_cell_direct_access") is not False
        or command.get("broker_may_prepare_proposal") is not True
        or command.get("broker_may_confirm_command") is not False
        or not all(
            command.get(key) is True
            for key in (
                "current_authorization_required",
                "human_or_policy_gate_required",
                "idempotency_required",
                "audit_required",
                "deterministic_readback_required",
            )
        )
    ):
        errors.append("routes:rest_command_boundary")
    sql = routes.get("sql_or_database_connection", {})
    if (
        sql.get("work_cell_direct_access") is not False
        or sql.get("generic_broker_access") is not False
        or sql.get("command_authority") is not False
    ):
        errors.append("routes:sql_boundary")

    fallback = contract.get("fallback_policy", {})
    if set(fallback.get("intelligent_release_requires", [])) != {
        "admitted_provider_model_result",
        "current_authorized_typed_context",
        "deterministic_proofreader_admission",
    }:
        errors.append("fallback:release_requirements")
    if fallback.get("provider_unavailable_state") != "intelligence_unavailable":
        errors.append("fallback:unavailable_state")
    for key in (
        "ordinary_manual_product_controls_remain_available",
        "preconfigured_infrastructure_safeguards_continue",
        "alternate_provider_requires_new_generation_and_separate_acceptance",
    ):
        if fallback.get(key) is not True:
            errors.append(f"fallback:{key}")
    for key in (
        "silent_provider_fallback",
        "silent_model_fallback",
        "deterministic_equivalent_intelligence_fallback",
    ):
        if fallback.get(key) is not False:
            errors.append(f"fallback:{key}")

    revocation = contract.get("revocation_and_kill_switch", {})
    if revocation.get("owner") != "external_control_plane":
        errors.append("revocation:owner")
    if revocation.get("model_may_disable_or_delay") is not False:
        errors.append("revocation:model_influence")
    if set(revocation.get("revocation_scope", [])) != {
        "all_generation_leases",
        "all_generation_aliases",
        "all_generation_tokens",
        "all_generation_writable_caches",
        "all_further_generation_calls",
    }:
        errors.append("revocation:scope")
    for key in (
        "conversation_clear_is_revocation",
        "fresh_model_context_is_revocation",
        "suspected_escape_reuses_work_cell",
    ):
        if revocation.get(key) is not False:
            errors.append(f"revocation:{key}")
    for key in ("evidence_preservation_required", "quarantine_required"):
        if revocation.get(key) is not True:
            errors.append(f"revocation:{key}")

    supply = contract.get("supply_chain_identity", {})
    if supply.get("digest_algorithm") != "sha256":
        errors.append("supply_chain:digest")
    if set(supply.get("required_identities", [])) != {
        "runtime_image_digest",
        "model_provider_contract_digest",
        "system_contract_digest",
        "adapter_artifact_digest",
        "generation_manifest_digest",
    }:
        errors.append("supply_chain:identities")
    for key in (
        "verify_before_generation_start",
        "verify_at_broker_admission",
        "identity_mismatch_stops_generation",
    ):
        if supply.get(key) is not True:
            errors.append(f"supply_chain:{key}")
    for key in ("work_cell_repository_write_credential", "work_cell_ci_cd_credential"):
        if supply.get(key) is not False:
            errors.append(f"supply_chain:{key}")

    evidence = contract.get("audit_evidence_policy", {})
    expected_allowed = set(schema["$defs"]["AuditEvidenceEnvelope"]["properties"])
    if set(evidence.get("allowed_fields", [])) != expected_allowed:
        errors.append("evidence:allowed_fields")
    required_forbidden = {
        "raw_prompt",
        "model_reasoning",
        "raw_provider_response",
        "credential",
        "access_token",
        "environment_variables",
        "file_contents",
        "source_code",
        "sql",
        "patient_identifier",
        "patient_or_product_value",
        "licensed_full_text",
        "raw_exception_message",
        "unrestricted_log",
    }
    if set(evidence.get("forbidden_fields", [])) != required_forbidden:
        errors.append("evidence:forbidden_fields")
    for key in (
        "reason_codes_are_closed",
        "counts_are_cumulative",
        "digests_are_version_bound",
        "contains_sensitive_values_must_be_false",
    ):
        if evidence.get(key) is not True:
            errors.append(f"evidence:{key}")

    registry = contract.get("schema_registry", [])
    if {item.get("message_type") for item in registry} != set(MESSAGE_DEFS.values()):
        errors.append("schema_registry:types")
    for item in registry:
        expected = f"architecture-contract.schema.json#/$defs/{item.get('message_type')}"
        if item.get("schema_ref") != expected or set(item) != {
            "message_type",
            "schema_ref",
        }:
            errors.append("schema_registry:reference")

    next_descendant = contract.get("next_descendant", {})
    if next_descendant != {
        "id": "aes-c1-provider-free-admission-rehearsal",
        "runtime": False,
        "provider_call": False,
        "product_or_patient_data": False,
        "tool_or_command": False,
        "requires_fresh_frozen_plan": True,
    }:
        errors.append("next_descendant:boundary")
    return sorted(set(errors))


def _ceiling_pairs(limits: dict[str, Any]) -> dict[str, int]:
    return {
        "model_calls": limits["reasoning"]["max_model_calls"],
        "model_tokens": limits["reasoning"]["max_model_tokens"],
        "input_bytes": limits["information"]["max_input_bytes"],
        "output_bytes": limits["information"]["max_output_bytes"],
        "source_count": limits["information"]["max_source_count"],
        "request_count": limits["egress"]["max_requests"],
        "request_bytes": limits["egress"]["max_request_bytes"],
        "response_bytes": limits["egress"]["max_response_bytes"],
        "total_bytes": limits["egress"]["max_total_bytes"],
        "distinct_destinations": limits["egress"]["max_distinct_destinations"],
        "redirects": limits["egress"]["max_redirects"],
        "broker_operations": limits["action"]["max_broker_operations"],
        "inert_tool_operations": limits["action"]["max_inert_tool_operations"],
        "product_mutations": limits["action"]["max_product_mutations"],
        "command_confirmations": limits["action"]["max_command_confirmations"],
        "denied_operations": limits["denial"]["max_denials"],
        "boundary_probes": limits["denial"]["max_boundary_probes"],
        "repeated_failures": limits["denial"]["max_repeated_failures"],
        "elapsed_ms": limits["time"]["max_elapsed_ms"],
    }


def _forbidden_keys(value: Any, forbidden: set[str], path: str = "$") -> list[str]:
    errors: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            if key in forbidden:
                errors.append(f"{path}:forbidden:{key}")
            errors.extend(_forbidden_keys(child, forbidden, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            errors.extend(_forbidden_keys(child, forbidden, f"{path}[{index}]"))
    return errors


def validate_examples(
    examples: dict[str, Any],
    contract: dict[str, Any],
    schema: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    errors.extend(
        _exact_keys(
            examples,
            {"schema_version", "evidence_mode", "messages"},
            "examples",
        )
    )
    if examples.get("schema_version") != "emr4.aes_c0.authored_synthetic_examples.v1":
        errors.append("examples:schema_version")
    if examples.get("evidence_mode") != "authored_synthetic_provider_free":
        errors.append("examples:evidence_mode")
    messages = examples.get("messages", {})
    if set(messages) != set(MESSAGE_DEFS):
        errors.append("examples:message_set")
        return errors
    for key, definition_name in MESSAGE_DEFS.items():
        errors.extend(
            validate_instance(
                messages[key],
                schema["$defs"][definition_name],
                root_schema=schema,
                path=f"$.messages.{key}",
            )
        )

    manifest = messages["generation_manifest"]
    lease = messages["capability_lease"]
    budget = messages["budget_state"]
    decision = messages["broker_decision"]
    revocation = messages["revocation_record"]
    evidence = messages["audit_evidence"]
    generation_ids = {
        manifest["generation_id"],
        lease["generation_id"],
        budget["generation_id"],
        decision["generation_id"],
        revocation["generation_id"],
        evidence["generation_id"],
    }
    if len(generation_ids) != 1:
        errors.append("examples:generation_mismatch")
    if {
        manifest["manifest_id"],
        lease["manifest_id"],
        budget["manifest_id"],
    } != {manifest["manifest_id"]}:
        errors.append("examples:manifest_id_mismatch")
    if {
        manifest["manifest_digest"],
        decision["manifest_digest"],
        revocation["manifest_digest"],
        evidence["manifest_digest"],
        manifest["supply_chain_identity"]["generation_manifest_digest"],
    } != {manifest["manifest_digest"]}:
        errors.append("examples:manifest_digest_mismatch")

    grants = {item["capability_id"]: item for item in manifest["capability_grants"]}
    grant = grants.get(lease["capability_id"])
    if grant is None:
        errors.append("examples:lease_grant_missing")
    elif (
        grant["capability_class"] != lease["capability_class"]
        or grant["audience"] != lease["audience"]
        or grant["capability_id"] != decision["capability_id"]
        or grant["capability_class"] != decision["capability_class"]
    ):
        errors.append("examples:grant_lease_decision_mismatch")
    if lease["authority_binding_digest"] != manifest["authority_binding_digest"]:
        errors.append("examples:authority_binding_mismatch")
    lease_expiry = datetime.fromisoformat(lease["expires_at"].replace("Z", "+00:00"))
    manifest_expiry = datetime.fromisoformat(
        manifest["expires_at"].replace("Z", "+00:00")
    )
    if lease_expiry > manifest_expiry:
        errors.append("examples:lease_outlives_manifest")
    if budget["ceilings"] != manifest["budgets"]:
        errors.append("examples:budget_ceiling_mismatch")
    ceilings = _ceiling_pairs(budget["ceilings"])
    exhausted = False
    for key, value in budget["observed"].items():
        if value > ceilings[key]:
            errors.append(f"examples:budget_exceeded:{key}")
        # A deliberately disabled capability has a zero ceiling. Observing zero
        # does not itself exhaust the generation; a positive ceiling reached by
        # a cumulative counter does.
        if ceilings[key] > 0 and value >= ceilings[key]:
            exhausted = True
    if exhausted and (
        budget["terminal_state"] != "exhausted"
        or budget["next_operation_permitted"] is not False
    ):
        errors.append("examples:budget_exhaustion_not_terminal")
    if decision["decision"] == "allow" and not all(
        (
            decision["proofreader_admitted"],
            decision["current_authority_checked"],
            decision["manifest_and_lease_match"],
            decision["operation_identity_broker_resolved"],
            not decision["candidate_supplied_operation_identity"],
            not decision["command_authority"],
        )
    ):
        errors.append("examples:allow_without_all_gates")
    if not all(
        revocation[key] is True
        for key in (
            "all_leases_revoked",
            "all_aliases_invalidated",
            "all_tokens_invalidated",
            "all_writable_caches_quarantined",
            "all_further_calls_blocked",
        )
    ):
        errors.append("examples:incomplete_revocation")
    if (
        revocation["conversation_clear_is_cleanup"] is not False
        or revocation["model_influenced_revocation"] is not False
    ):
        errors.append("examples:model_owned_cleanup")
    forbidden = set(contract["audit_evidence_policy"]["forbidden_fields"])
    errors.extend(_forbidden_keys(evidence, forbidden, "$.messages.audit_evidence"))
    if set(evidence) != set(contract["audit_evidence_policy"]["allowed_fields"]):
        errors.append("examples:evidence_fields_not_exact")
    if evidence["contains_sensitive_values"] is not False:
        errors.append("examples:sensitive_evidence")
    return sorted(set(errors))


def _set_path(value: dict[str, Any], path: tuple[Any, ...], replacement: Any) -> None:
    target: Any = value
    for part in path[:-1]:
        target = target[part]
    target[path[-1]] = replacement


def _delete_path(value: dict[str, Any], path: tuple[Any, ...], _: Any) -> None:
    target: Any = value
    for part in path[:-1]:
        target = target[part]
    del target[path[-1]]


def _append_path(value: dict[str, Any], path: tuple[Any, ...], item: Any) -> None:
    target: Any = value
    for part in path:
        target = target[part]
    target.append(item)


def hostile_mutations() -> list[tuple[str, str, Callable[..., None], tuple[Any, ...], Any]]:
    return [
        ("runtime_open", "contract", _set_path, ("authority_boundary", "runtime_implementation"), True),
        ("provider_open", "contract", _set_path, ("authority_boundary", "provider_call"), True),
        ("trust_boundary_removed", "contract", _delete_path, ("trust_boundaries", 7), None),
        ("model_controls_boundary", "contract", _set_path, ("trust_boundaries", 3, "model_controls_boundary"), True),
        ("generic_network_leaseable", "contract", _set_path, ("capability_classes", "leaseable", 0, "class_id"), "generic_network"),
        ("candidate_selects_identity", "contract", _set_path, ("capability_classes", "leaseable", 0, "candidate_selects_operation_identity"), True),
        ("provider_tools_enabled", "contract", _set_path, ("capability_classes", "leaseable", 0, "provider_executed_tools"), True),
        ("class_command_authority", "contract", _set_path, ("capability_classes", "leaseable", 0, "command_authority"), True),
        ("generic_network_not_denied", "contract", _delete_path, ("capability_classes", "always_denied", 0), None),
        ("candidate_url_allowed", "contract", _append_path, ("candidate_influence_policy", "candidate_may_supply"), "url"),
        ("context_executable", "contract", _set_path, ("candidate_influence_policy", "context_and_memory_are_inert"), False),
        ("manifest_mutable", "contract", _set_path, ("generation_manifest_policy", "immutable_per_generation"), False),
        ("lease_visible_to_cell", "contract", _set_path, ("generation_manifest_policy", "work_cell_receives_lease_or_credential"), True),
        ("stop_condition_removed", "contract", _delete_path, ("generation_manifest_policy", "required_stop_conditions", 0), None),
        ("budget_dimension_removed", "contract", _delete_path, ("budget_policy", "dimensions", 5), None),
        ("redirect_allowed", "contract", _set_path, ("budget_policy", "maximum_redirects_per_generation"), 1),
        ("product_mutation_budget", "contract", _set_path, ("budget_policy", "maximum_product_mutations_per_generation"), 1),
        ("graphql_command", "contract", _set_path, ("route_classification", "graphql_query", "command_authority"), True),
        ("event_current_truth", "contract", _set_path, ("route_classification", "event_signal", "current_truth"), True),
        ("broker_confirms_command", "contract", _set_path, ("route_classification", "rest_openapi_command", "broker_may_confirm_command"), True),
        ("deterministic_fallback", "contract", _set_path, ("fallback_policy", "deterministic_equivalent_intelligence_fallback"), True),
        ("model_delays_kill_switch", "contract", _set_path, ("revocation_and_kill_switch", "model_may_disable_or_delay"), True),
        ("repository_credential", "contract", _set_path, ("supply_chain_identity", "work_cell_repository_write_credential"), True),
        ("raw_prompt_not_forbidden", "contract", _delete_path, ("audit_evidence_policy", "forbidden_fields", 0), None),
        ("grant_command_authority", "examples", _set_path, ("messages", "generation_manifest", "capability_grants", 0, "command_authority"), True),
        ("grant_candidate_identity", "examples", _set_path, ("messages", "generation_manifest", "capability_grants", 0, "candidate_selects_operation_identity"), True),
        ("lease_presented", "examples", _set_path, ("messages", "capability_lease", "presented_to_work_cell"), True),
        ("reusable_credential", "examples", _set_path, ("messages", "capability_lease", "reusable_credential"), True),
        ("example_redirect", "examples", _set_path, ("messages", "generation_manifest", "budgets", "egress", "max_redirects"), 1),
        ("example_product_mutation", "examples", _set_path, ("messages", "budget_state", "observed", "product_mutations"), 1),
        ("candidate_supplied_decision_identity", "examples", _set_path, ("messages", "broker_decision", "candidate_supplied_operation_identity"), True),
        ("incomplete_revocation", "examples", _set_path, ("messages", "revocation_record", "all_leases_revoked"), False),
        ("sensitive_evidence", "examples", _set_path, ("messages", "audit_evidence", "contains_sensitive_values"), True),
        ("raw_prompt_evidence", "examples", _set_path, ("messages", "audit_evidence", "raw_prompt"), "forbidden"),
        ("cross_generation_lease", "examples", _set_path, ("messages", "capability_lease", "generation_id"), "generation-synthetic-002"),
        ("manifest_digest_detached", "examples", _set_path, ("messages", "generation_manifest", "supply_chain_identity", "generation_manifest_digest"), "sha256:9999999999999999999999999999999999999999999999999999999999999999"),
        ("observed_over_ceiling", "examples", _set_path, ("messages", "budget_state", "observed", "request_count"), 2),
    ]


def validate_hostile_mutations(
    contract: dict[str, Any], examples: dict[str, Any], schema: dict[str, Any]
) -> tuple[list[str], list[str]]:
    rejected: list[str] = []
    admitted: list[str] = []
    for name, target_name, mutate, path, value in hostile_mutations():
        candidate_contract = copy.deepcopy(contract)
        candidate_examples = copy.deepcopy(examples)
        target = candidate_contract if target_name == "contract" else candidate_examples
        mutate(target, path, value)
        errors = [
            *validate_contract(candidate_contract, schema),
            *validate_examples(candidate_examples, candidate_contract, schema),
        ]
        (rejected if errors else admitted).append(name)
    return rejected, admitted


def _digest(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def build_report() -> dict[str, Any]:
    contract = _load(CONTRACT_PATH)
    schema = _load(SCHEMA_PATH)
    examples = _load(EXAMPLES_PATH)
    canonical_errors = [
        *validate_contract(contract, schema),
        *validate_examples(examples, contract, schema),
    ]
    rejected, admitted = validate_hostile_mutations(contract, examples, schema)
    reasons = sorted(set(canonical_errors))
    if admitted:
        reasons.append("hostile_mutations_admitted:" + ",".join(admitted))
    return {
        "schema_version": "emr4.aes_c0.acceptance_report.v1",
        "status": "passed" if not reasons else "revision_required",
        "evidence_mode": "authored_synthetic_provider_free",
        "runtime_started": False,
        "provider_calls": 0,
        "product_or_patient_data": False,
        "canonical_error_count": len(canonical_errors),
        "hostile_mutation_count": len(hostile_mutations()),
        "hostile_mutation_rejected_count": len(rejected),
        "hostile_mutation_admitted": admitted,
        "reasons": reasons,
        "artifact_digests": {
            CONTRACT_PATH.relative_to(ROOT).as_posix(): _digest(CONTRACT_PATH),
            SCHEMA_PATH.relative_to(ROOT).as_posix(): _digest(SCHEMA_PATH),
            EXAMPLES_PATH.relative_to(ROOT).as_posix(): _digest(EXAMPLES_PATH),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    report = build_report()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
