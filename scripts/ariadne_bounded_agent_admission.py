#!/usr/bin/env python3
"""Validate the non-executing Ariadne bounded agent-admission design.

This module has no adapter or actuator. It validates the committed
authored-synthetic design, evaluates a fixed negative-case vocabulary and
compiles inert dry-run manifests.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_PATH = (
    ROOT
    / "orchestration"
    / "continuity"
    / "ariadne-bounded-agent-admission-example.json"
)
MANIFEST_PATH = (
    ROOT
    / "orchestration"
    / "continuity"
    / "ariadne-bounded-agent-admission-dry-run-manifests.json"
)
EVIDENCE_PATH = (
    ROOT
    / "orchestration"
    / "continuity"
    / "ariadne-bounded-agent-admission-evidence.json"
)
PREDECESSOR_PATH = (
    ROOT
    / "orchestration"
    / "continuity"
    / "ariadne-bounded-cognitive-work-cell-example.json"
)

EXPECTED_SCHEMA_VERSION = "ariadne.bounded_agent_admission.v1"
EXPECTED_BOUNDARY = (
    "provider_neutral_non_executing_generated_cognition_admission_design"
)
EXPECTED_EGRESS = "deterministic-proofreader-v1"
EXPECTED_PURPOSE = "prepare-authored-synthetic-appointment-availability-drafts"
EXPECTED_SCOPE = {
    "practice_id": "practice-synth-a",
    "principal_id": "principal-reception",
    "correlation_id": "booking-request-001",
    "context_revision": 7,
    "purpose": EXPECTED_PURPOSE,
}
EXPECTED_SOURCE_LABELS = {
    "staff_selected",
    "authenticated_scope_fixture",
    "fixture_authoritative_fact",
    "fixture_evaluated_policy",
}
EXPECTED_SENSITIVITIES = {
    "authored-synthetic-internal",
    "authored-synthetic-restricted",
}
EXPECTED_TOPOLOGIES = {
    "in-cell-local",
    "host-brokered-local",
    "remote-provider-broker",
}
EXPECTED_PORTS = {
    (
        "port-ux",
        "booking-ux-projection-candidate.v1",
        "candidate",
    ),
    (
        "port-human-review",
        "booking-human-review-candidate.v1",
        "candidate",
    ),
    ("port-audit", "work-cell-audit-evidence.v1", "evidence"),
    ("port-orchestrator", "work-cell-outcome.v1", "evidence"),
    ("port-advisory", "booking-explanation-advisory.v1", "advisory"),
}
PAYLOAD_KEYS = {
    "synthetic-request-scope.v1": {
        "request_kind",
        "duration_minutes",
        "request_text",
    },
    "principal-scope.v1": {"role", "allowed_task"},
    "patient-candidate-context.v1": {"candidate_ids", "identity_verified"},
    "practitioner-context.v1": {
        "practitioner_ids",
        "selected_practitioner_id",
    },
    "availability-context.v1": {
        "slot_ids",
        "practitioner_id",
        "duration_minutes",
        "availability_revision",
    },
    "evaluated-appointment-policy.v1": {
        "allowed_duration_minutes",
        "human_confirmation_required",
        "command_authority",
    },
}
FORBIDDEN_KEY_PARTS = {
    "api_key",
    "credential",
    "password",
    "access_token",
    "connection_string",
    "dsn",
    "endpoint",
    "raw_prompt",
    "raw_response",
    "chain_of_thought",
}


class AdmissionDesignError(ValueError):
    """Raised when the inert design fails closed."""


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _sha256_bytes(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def _sha256_json(value: Any) -> str:
    return _sha256_bytes(_canonical_bytes(value))


def _load_json(path: Path) -> dict[str, Any]:
    loaded = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise AdmissionDesignError("document-root-must-be-object")
    return loaded


def load_document() -> dict[str, Any]:
    """Load only the fixed repository-local authored-synthetic document."""
    return _load_json(EXAMPLE_PATH)


def _walk_keys(value: Any) -> list[str]:
    keys: list[str] = []
    if isinstance(value, dict):
        for key, nested in value.items():
            keys.append(str(key).lower())
            keys.extend(_walk_keys(nested))
    elif isinstance(value, list):
        for nested in value:
            keys.extend(_walk_keys(nested))
    return keys


def _validate_source_bindings(document: dict[str, Any]) -> None:
    for binding in document["source_bindings"]:
        relative = Path(binding["path"])
        if relative.is_absolute() or ".." in relative.parts:
            raise AdmissionDesignError("source-binding-path-not-repository-local")
        path = ROOT / relative
        if not path.is_file() or path.is_symlink():
            raise AdmissionDesignError("source-binding-not-fixed-regular-file")
        observed = _sha256_bytes(path.read_bytes())
        if observed != binding["sha256"]:
            raise AdmissionDesignError("source-binding-hash-mismatch")


def _validate_predecessor_ports(document: dict[str, Any]) -> None:
    predecessor = _load_json(PREDECESSOR_PATH)
    predecessor_ports = {
        (port["id"], port["frame_type"], port["authority_ceiling"])
        for port in predecessor["output_ports"]
    }
    current_ports = {
        (port["port_id"], port["frame_type"], port["authority_ceiling"])
        for port in document["instruction_policy"]["allowed_output_ports"]
    }
    if predecessor_ports != EXPECTED_PORTS or current_ports != EXPECTED_PORTS:
        raise AdmissionDesignError("accepted-output-port-drift")


def _frame_payload_metrics(frame: dict[str, Any]) -> tuple[int, str]:
    payload_bytes = _canonical_bytes(frame["payload"])
    return len(payload_bytes), _sha256_bytes(payload_bytes)


def _context_digest(frames: list[dict[str, Any]]) -> str:
    return _sha256_json(frames)


def _observed_input_bytes(frames: list[dict[str, Any]]) -> int:
    return sum(_frame_payload_metrics(frame)[0] for frame in frames)


def validate_document(document: dict[str, Any]) -> dict[str, Any]:
    """Validate semantic invariants without executing an adapter."""
    if document.get("schema_version") != EXPECTED_SCHEMA_VERSION:
        raise AdmissionDesignError("schema-version-mismatch")
    if document.get("boundary_classification") != EXPECTED_BOUNDARY:
        raise AdmissionDesignError("boundary-classification-mismatch")
    if any(document["closed_connections"].values()):
        raise AdmissionDesignError("closed-connection-opened")

    _validate_source_bindings(document)
    _validate_predecessor_ports(document)

    instruction = document["instruction_policy"]
    if document["instruction_policy_digest"] != _sha256_json(instruction):
        raise AdmissionDesignError("instruction-policy-digest-mismatch")
    if instruction["evidence_semantics"] != "data_only_never_policy_or_capability":
        raise AdmissionDesignError("evidence-semantics-drift")
    if instruction["sole_egress_route"] != EXPECTED_EGRESS:
        raise AdmissionDesignError("proofreader-egress-drift")
    if set(instruction["allowed_context_frame_types"]) != set(PAYLOAD_KEYS):
        raise AdmissionDesignError("context-frame-allowlist-drift")

    topologies = document["topology_catalogue"]
    if {item["topology_id"] for item in topologies} != EXPECTED_TOPOLOGIES:
        raise AdmissionDesignError("topology-catalogue-drift")
    for item in topologies:
        if item["selected"] or item["configured"] or item["execution_enabled"]:
            raise AdmissionDesignError("topology-must-remain-unselected")

    frames = document["context_frames"]
    frame_ids = [frame["frame_id"] for frame in frames]
    if len(frame_ids) != len(set(frame_ids)):
        raise AdmissionDesignError("duplicate-context-frame-id")
    for frame in frames:
        if frame["frame_type"] not in PAYLOAD_KEYS:
            raise AdmissionDesignError("context-frame-type-not-allowlisted")
        if set(frame["payload"]) != PAYLOAD_KEYS[frame["frame_type"]]:
            raise AdmissionDesignError("context-frame-payload-shape-mismatch")
        if frame["source_label"] not in EXPECTED_SOURCE_LABELS:
            raise AdmissionDesignError("context-source-label-not-allowlisted")
        if frame["sensitivity"] not in EXPECTED_SENSITIVITIES:
            raise AdmissionDesignError("context-sensitivity-not-allowlisted")
        for key, expected in EXPECTED_SCOPE.items():
            if frame[key] != expected:
                raise AdmissionDesignError("context-scope-mismatch")
        if frame["freshness"]["status"] != "current":
            raise AdmissionDesignError("context-frame-not-current")
        size, digest = _frame_payload_metrics(frame)
        if frame["canonical_bytes"] != size:
            raise AdmissionDesignError("context-frame-byte-count-mismatch")
        if frame["payload_sha256"] != digest:
            raise AdmissionDesignError("context-frame-payload-hash-mismatch")

    forbidden_hits = {
        key
        for key in _walk_keys([frame["payload"] for frame in frames])
        for part in FORBIDDEN_KEY_PARTS
        if part in key
    }
    if forbidden_hits:
        raise AdmissionDesignError("forbidden-secret-or-diagnostic-key")

    envelope = document["admission_envelope"]
    for flag in (
        "execution_enabled",
        "agent_attached",
        "model_selected",
        "provider_selected",
        "transport_selected",
        "container_started",
    ):
        if envelope[flag]:
            raise AdmissionDesignError("non-executing-envelope-flag-opened")
    if envelope["mode"] != "design-only":
        raise AdmissionDesignError("envelope-mode-drift")
    for key, expected in EXPECTED_SCOPE.items():
        if envelope["scope"][key] != expected:
            raise AdmissionDesignError("envelope-scope-mismatch")
    policy_binding = envelope["policy_binding"]
    if (
        policy_binding["policy_id"] != instruction["policy_id"]
        or policy_binding["policy_revision"] != instruction["policy_revision"]
        or policy_binding["implementation_generation"]
        != instruction["implementation_generation"]
        or policy_binding["instruction_policy_digest"]
        != document["instruction_policy_digest"]
        or policy_binding["container_generation"] is not None
        or policy_binding["container_generation_status"]
        != "unassigned-until-runtime-authorised"
    ):
        raise AdmissionDesignError("policy-binding-mismatch")

    binding = envelope["context_binding"]
    if binding["frame_ids"] != frame_ids:
        raise AdmissionDesignError("context-frame-order-or-binding-mismatch")
    if binding["context_digest"] != _context_digest(frames):
        raise AdmissionDesignError("context-digest-mismatch")
    if binding["observed_input_bytes"] != _observed_input_bytes(frames):
        raise AdmissionDesignError("observed-input-byte-count-mismatch")

    budgets = envelope["budgets"]
    if len(frames) > budgets["maximum_context_frames"]:
        raise AdmissionDesignError("maximum-context-frames-exceeded")
    if binding["observed_input_bytes"] > budgets["maximum_input_bytes"]:
        raise AdmissionDesignError("maximum-input-bytes-exceeded")
    if budgets["maximum_output_drafts"] != len(EXPECTED_PORTS):
        raise AdmissionDesignError("output-draft-cap-mismatch")
    if budgets["maximum_attempts_per_context_revision"] != 2:
        raise AdmissionDesignError("attempt-cap-mismatch")

    token_budget = envelope["token_budget"]
    if token_budget != {
        "status": "unresolved-until-model-and-tokenizer-selected",
        "value": None,
        "unit": None,
        "model_independent_caps_remain_binding": True,
    }:
        raise AdmissionDesignError("token-budget-must-remain-unresolved")

    capabilities = envelope["capabilities"]
    if capabilities["tools"] or capabilities["secrets"]:
        raise AdmissionDesignError("capability-list-not-empty")
    if any(
        value
        for key, value in capabilities.items()
        if key not in {"tools", "secrets"}
    ):
        raise AdmissionDesignError("ambient-capability-opened")

    output = envelope["output_contract"]
    if set(output["allowed_port_ids"]) != {item[0] for item in EXPECTED_PORTS}:
        raise AdmissionDesignError("output-port-binding-drift")
    if (
        output["requested_authority"] != "draft-only"
        or output["egress_route"] != EXPECTED_EGRESS
        or output["direct_downstream_delivery"]
        or output["direct_human_gate_delivery"]
    ):
        raise AdmissionDesignError("draft-only-proofreader-egress-drift")

    expected_case_ids = [case["case_id"] for case in document["validation_cases"]]
    if len(expected_case_ids) != len(set(expected_case_ids)):
        raise AdmissionDesignError("duplicate-validation-case-id")
    case_results = evaluate_cases(document)
    for case, result in zip(document["validation_cases"], case_results, strict=True):
        if result["decision"] != case["expected_decision"]:
            raise AdmissionDesignError("validation-case-decision-mismatch")
        if result["reason_codes"] != case["expected_reason_codes"]:
            raise AdmissionDesignError("validation-case-reason-mismatch")

    posture = document["evidence_posture"]
    if any(
        posture[key]
        for key in (
            "raw_context_logged",
            "raw_generation_logged",
            "chain_of_thought_logged",
            "runtime_claim",
        )
    ):
        raise AdmissionDesignError("evidence-posture-overclaim")

    return {
        "status": "valid",
        "case_count": len(case_results),
        "source_binding_count": len(document["source_bindings"]),
        "topology_count": len(topologies),
        "context_frame_count": len(frames),
        "output_port_count": len(EXPECTED_PORTS),
    }


def _refresh_mutated_context(candidate: dict[str, Any]) -> None:
    for frame in candidate["context_frames"]:
        size, digest = _frame_payload_metrics(frame)
        frame["canonical_bytes"] = size
        frame["payload_sha256"] = digest
    binding = candidate["admission_envelope"]["context_binding"]
    binding["context_digest"] = _context_digest(candidate["context_frames"])
    binding["observed_input_bytes"] = _observed_input_bytes(
        candidate["context_frames"]
    )


def _frame_by_id(candidate: dict[str, Any], frame_id: str) -> dict[str, Any]:
    matches = [
        frame for frame in candidate["context_frames"] if frame["frame_id"] == frame_id
    ]
    if len(matches) != 1:
        raise AdmissionDesignError("mutation-frame-id-not-found")
    return matches[0]


def _apply_case_mutation(
    candidate: dict[str, Any], mutation: dict[str, Any]
) -> None:
    kind = mutation["kind"]
    envelope = candidate["admission_envelope"]
    if kind == "none":
        return
    if kind == "replace-request-text":
        frame = _frame_by_id(candidate, "input-request-scope")
        frame["payload"]["request_text"] = mutation["value"]
    elif kind == "select-transport":
        envelope["transport_selected"] = True
        for topology in candidate["topology_catalogue"]:
            if topology["topology_id"] == mutation["topology_id"]:
                topology["selected"] = True
    elif kind == "set-token-budget":
        envelope["token_budget"] = {
            "status": "resolved",
            "value": mutation["value"],
            "unit": mutation["unit"],
            "model_independent_caps_remain_binding": True,
        }
    elif kind == "enable-capability":
        envelope["capabilities"][mutation["capability"]] = True
    elif kind == "set-frame-field":
        _frame_by_id(candidate, mutation["frame_id"])[mutation["field"]] = mutation[
            "value"
        ]
    elif kind == "set-freshness-status":
        _frame_by_id(candidate, mutation["frame_id"])["freshness"]["status"] = (
            mutation["value"]
        )
    elif kind == "repeat-request-text":
        frame = _frame_by_id(candidate, "input-request-scope")
        frame["payload"]["request_text"] *= mutation["factor"]
    elif kind == "set-output-observation":
        envelope["budgets"]["observed_output_drafts"] = mutation["drafts"]
        envelope["budgets"]["observed_output_bytes"] = mutation["bytes"]
    elif kind == "cancel-and-present-late-completion":
        envelope["attempt_state"]["status"] = "cancelled"
        envelope["attempt_state"]["cancelled"] = True
        envelope["attempt_state"]["late_completion_presented"] = True
    elif kind == "set-egress-route":
        envelope["output_contract"]["egress_route"] = mutation["value"]
        envelope["output_contract"]["direct_human_gate_delivery"] = True
    elif kind == "set-output-authority":
        envelope["output_contract"]["requested_authority"] = mutation["value"]
    else:
        raise AdmissionDesignError("unknown-case-mutation")
    _refresh_mutated_context(candidate)


def _case_result(
    case_id: str, decision: str, reason_codes: list[str]
) -> dict[str, Any]:
    return {
        "case_id": case_id,
        "decision": decision,
        "reason_codes": reason_codes,
    }


def evaluate_case(document: dict[str, Any], case: dict[str, Any]) -> dict[str, Any]:
    """Evaluate one fixed authored-synthetic mutation without an agent."""
    candidate = copy.deepcopy(document)
    mutation = case["mutation"]
    _apply_case_mutation(candidate, mutation)
    envelope = candidate["admission_envelope"]
    case_id = case["case_id"]

    if envelope["transport_selected"] or any(
        topology["selected"]
        or topology["configured"]
        or topology["execution_enabled"]
        for topology in candidate["topology_catalogue"]
    ):
        return _case_result(
            case_id,
            "reject_transport_selection",
            ["transport-selection-not-authorised"],
        )
    token = envelope["token_budget"]
    if token["status"] != "unresolved-until-model-and-tokenizer-selected" or any(
        token[key] is not None for key in ("value", "unit")
    ):
        return _case_result(
            case_id,
            "reject_token_policy",
            ["tokenizer-and-model-unselected"],
        )
    capabilities = envelope["capabilities"]
    if capabilities["tools"] or capabilities["secrets"] or any(
        value
        for key, value in capabilities.items()
        if key not in {"tools", "secrets"}
    ):
        return _case_result(
            case_id,
            "reject_capability_expansion",
            ["capability-not-authorised"],
        )
    for frame in candidate["context_frames"]:
        if frame["practice_id"] != envelope["scope"]["practice_id"]:
            return _case_result(
                case_id,
                "reject_scope_mismatch",
                ["practice-scope-mismatch"],
            )
        if frame["principal_id"] != envelope["scope"]["principal_id"]:
            return _case_result(
                case_id,
                "reject_scope_mismatch",
                ["principal-scope-mismatch"],
            )
        if frame["frame_type"] not in PAYLOAD_KEYS:
            return _case_result(
                case_id,
                "reject_context_type",
                ["context-frame-type-not-allowlisted"],
            )
        if frame["sensitivity"] not in EXPECTED_SENSITIVITIES:
            return _case_result(
                case_id,
                "reject_context_sensitivity",
                ["context-sensitivity-not-allowlisted"],
            )
        if frame["freshness"]["status"] != "current":
            return _case_result(
                case_id,
                "reject_stale_context",
                ["context-frame-not-current"],
            )
    budgets = envelope["budgets"]
    if envelope["context_binding"]["observed_input_bytes"] > budgets[
        "maximum_input_bytes"
    ]:
        return _case_result(
            case_id,
            "reject_input_budget",
            ["maximum-input-bytes-exceeded"],
        )
    if budgets["observed_output_drafts"] > budgets["maximum_output_drafts"]:
        return _case_result(
            case_id,
            "reject_output_budget",
            ["maximum-output-drafts-exceeded"],
        )
    if budgets["observed_output_bytes"] > budgets["maximum_output_bytes"]:
        return _case_result(
            case_id,
            "reject_output_budget",
            ["maximum-output-bytes-exceeded"],
        )
    state = envelope["attempt_state"]
    if (
        state["cancelled"]
        or state["superseded"]
        or state["late_completion_presented"]
        or state["status"] != "not-started"
    ):
        return _case_result(
            case_id,
            "reject_cancelled_or_late",
            ["attempt-terminal-before-egress"],
        )
    output = envelope["output_contract"]
    if (
        output["egress_route"] != EXPECTED_EGRESS
        or output["direct_downstream_delivery"]
        or output["direct_human_gate_delivery"]
    ):
        return _case_result(
            case_id,
            "reject_egress_bypass",
            ["proofreader-is-sole-egress"],
        )
    if output["requested_authority"] != "draft-only":
        return _case_result(
            case_id,
            "reject_output_authority",
            ["draft-authority-ceiling-exceeded"],
        )

    if candidate["instruction_policy_digest"] != _sha256_json(
        candidate["instruction_policy"]
    ):
        raise AdmissionDesignError("case-mutated-instruction-policy")
    if mutation["kind"] == "replace-request-text":
        return _case_result(
            case_id,
            "design_valid",
            ["evidence-instruction-treated-as-data", "policy-digest-unchanged"],
        )
    return _case_result(
        case_id,
        "design_valid",
        ["bounded-non-executing-design"],
    )


def evaluate_cases(document: dict[str, Any]) -> list[dict[str, Any]]:
    return [evaluate_case(document, case) for case in document["validation_cases"]]


def compile_manifests(document: dict[str, Any]) -> dict[str, Any]:
    """Compile deterministic inert manifests with no adapter coordinates."""
    source_hash = _sha256_bytes(EXAMPLE_PATH.read_bytes())
    envelope = document["admission_envelope"]
    instruction = document["instruction_policy"]
    common = {
        "dry_run": True,
        "execution_enabled": False,
        "default_decision": "deny",
        "source_document_sha256": source_hash,
    }
    manifests = [
        {
            **common,
            "manifest_id": "agent-admission-posture-v1",
            "agent_attached": False,
            "model_selected": False,
            "provider_selected": False,
            "transport_selected": False,
            "container_started": False,
        },
        {
            **common,
            "manifest_id": "agent-context-contract-v1",
            "purpose": EXPECTED_PURPOSE,
            "context_revision": envelope["scope"]["context_revision"],
            "allowed_frame_types": instruction["allowed_context_frame_types"],
            "maximum_context_frames": envelope["budgets"][
                "maximum_context_frames"
            ],
            "maximum_input_bytes": envelope["budgets"]["maximum_input_bytes"],
            "context_digest": envelope["context_binding"]["context_digest"],
            "evidence_semantics": instruction["evidence_semantics"],
        },
        {
            **common,
            "manifest_id": "agent-topology-catalogue-v1",
            "candidates": [
                {
                    "topology_id": item["topology_id"],
                    "selected": False,
                    "configured": False,
                    "execution_enabled": False,
                }
                for item in document["topology_catalogue"]
            ],
        },
        {
            **common,
            "manifest_id": "agent-resource-budget-v1",
            "maximum_output_drafts": envelope["budgets"][
                "maximum_output_drafts"
            ],
            "maximum_output_bytes": envelope["budgets"]["maximum_output_bytes"],
            "maximum_attempts_per_context_revision": envelope["budgets"][
                "maximum_attempts_per_context_revision"
            ],
            "token_budget_status": envelope["token_budget"]["status"],
            "token_budget_value": None,
        },
        {
            **common,
            "manifest_id": "agent-cancellation-v1",
            "terminal_states": ["cancelled", "expired", "superseded"],
            "late_completion_decision": "reject-before-proofreader",
            "fresh_context_requires_new_attempt": True,
        },
        {
            **common,
            "manifest_id": "agent-egress-v1",
            "sole_egress_route": EXPECTED_EGRESS,
            "allowed_output_ports": [
                item["port_id"] for item in instruction["allowed_output_ports"]
            ],
            "output_authority": "draft-only",
            "direct_downstream_delivery": False,
            "direct_human_gate_delivery": False,
            "command_authority": False,
        },
    ]
    return {
        "schema_version": "ariadne.bounded_agent_admission_manifests.v1",
        "protocol_id": document["protocol_id"],
        "source_document_sha256": source_hash,
        "manifest_count": len(manifests),
        "manifests": manifests,
    }


def build_evidence(document: dict[str, Any]) -> dict[str, Any]:
    validation = validate_document(document)
    manifests = compile_manifests(document)
    cases = evaluate_cases(document)
    return {
        "schema_version": "ariadne.bounded_agent_admission_evidence.v1",
        "result": "ariadne_bounded_agent_admission_design_pass",
        "evidence_label": "authored_synthetic_non_executing_agent_admission_design",
        "protocol_source_sha256": _sha256_bytes(EXAMPLE_PATH.read_bytes()),
        "instruction_policy_digest": document["instruction_policy_digest"],
        "context_digest": document["admission_envelope"]["context_binding"][
            "context_digest"
        ],
        "manifest_bundle_sha256": _sha256_json(manifests),
        "source_bindings": document["source_bindings"],
        "counts": validation,
        "case_results": cases,
        "runtime_posture": {
            "agent_attached": False,
            "model_selected": False,
            "provider_selected": False,
            "transport_selected": False,
            "prompt_or_context_transmitted": False,
            "container_started": False,
            "network_opened": False,
            "secret_used": False,
            "product_connection_opened": False,
            "command_executed": False,
        },
        "unproved": [
            "model-behaviour",
            "model-specific-prompt-injection-resilience",
            "tokenizer-accounting",
            "inference-runtime-isolation",
            "live-context-authorisation",
            "product-runtime-behaviour",
        ],
    }


def _trace(document: dict[str, Any]) -> str:
    validation = validate_document(document)
    return "\n".join(
        [
            "# Ariadne bounded agent-admission design trace",
            "",
            "- status: valid",
            "- mode: design-only",
            "- execution-enabled: false",
            "- transport-selected: false",
            "- model-selected: false",
            "- provider-selected: false",
            f"- topology-candidates: {validation['topology_count']}",
            f"- context-frames: {validation['context_frame_count']}",
            f"- output-ports: {validation['output_port_count']}",
            f"- adversarial-cases: {validation['case_count']}",
            "- sole-egress: deterministic-proofreader",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the inert Ariadne agent-admission design."
    )
    parser.add_argument(
        "command", choices=("validate", "compile-manifests", "trace")
    )
    args = parser.parse_args()
    document = load_document()
    if args.command == "validate":
        result = validate_document(document)
        print(
            "status=valid "
            f"cases={result['case_count']} "
            "execution_enabled=false"
        )
    elif args.command == "compile-manifests":
        validate_document(document)
        print(json.dumps(compile_manifests(document), indent=2, sort_keys=True))
    else:
        print(_trace(document))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
