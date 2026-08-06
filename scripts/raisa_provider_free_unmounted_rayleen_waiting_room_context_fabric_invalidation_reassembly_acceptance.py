"""Generate deterministic evidence for the unmounted Rayleen invalidation seam."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys
from typing import Any, Callable

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.raisa_provider_free_unmounted_rayleen_waiting_room_context_fabric_invalidation_reassembly import (
    EVIDENCE_LABEL,
    SEAM_PACKET_SCHEMA,
    build_authored_synthetic_invalidation_reassembly_packet,
    proofread_invalidation_reassembly_packet,
    validate_invalidation_reassembly_packet,
)


CONTINUITY_DIR = (
    ROOT
    / "orchestration"
    / "continuity"
    / "raisa-provider-free-unmounted-rayleen-waiting-room-context-fabric-invalidation-reassembly"
)
PACKET_SCHEMA_PATH = CONTINUITY_DIR / "seam-packet.schema.json"
EVIDENCE_SCHEMA_PATH = CONTINUITY_DIR / "acceptance-evidence.schema.json"
DEFAULT_PACKET_PATH = CONTINUITY_DIR / "authored-synthetic-seam-packet.json"
DEFAULT_EVIDENCE_PATH = CONTINUITY_DIR / "provider-free-acceptance-evidence.json"
RESULT = (
    "raisa_provider_free_unmounted_rayleen_waiting_room_context_fabric_"
    "invalidation_reassembly_seam_pass"
)
CLAIM_BOUNDARY = (
    "Provider-free authored-synthetic unmounted adapter-to-temporal invalidation "
    "and inert reassembly-handoff evidence only; no real data, live watcher, "
    "source read, persistence, provider, runtime, command, deployment or "
    "production claim."
)


def _sha256_bytes(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(
        (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    )
    temporary.replace(path)


def _mutations() -> list[tuple[str, Callable[[dict[str, Any]], None]]]:
    def top_level_extra(packet: dict[str, Any]) -> None:
        packet["unexpected"] = True

    def bool_generation(packet: dict[str, Any]) -> None:
        packet["fresh_reassembly_instruction"]["session_generation"] = True

    def payload_smuggling(packet: dict[str, Any]) -> None:
        packet["signal"]["payload"] = {"replacement_status": "COMPLETED"}

    def state_rollback(packet: dict[str, Any]) -> None:
        packet["frame_set_state"]["state"] = "CURRENT"
        packet["frame_set_state"]["usable_for_new_reasoning"] = True

    def instruction_execution(packet: dict[str, Any]) -> None:
        packet["fresh_reassembly_instruction"]["execution_enabled"] = True

    def source_read(packet: dict[str, Any]) -> None:
        packet["fresh_reassembly_instruction"]["source_read_executed"] = True

    def returned_data(packet: dict[str, Any]) -> None:
        packet["fresh_reassembly_instruction"]["returns_data"] = True

    def command_authority(packet: dict[str, Any]) -> None:
        packet["fresh_reassembly_instruction"]["command_authority"] = True

    def provider_authority(packet: dict[str, Any]) -> None:
        packet["fresh_reassembly_instruction"]["provider_authority"] = True

    def stale_admission(packet: dict[str, Any]) -> None:
        packet["stale_reassembly_decision"]["decision"] = "ADMIT_NEW_GENERATION"

    def restored_old_set(packet: dict[str, Any]) -> None:
        packet["stale_reassembly_decision"]["old_frame_set_restored"] = True

    def extracted_source_detached(packet: dict[str, Any]) -> None:
        packet["adapter_binding_trace"]["extracted_source_digest"] = (
            "sha256:" + "1" * 64
        )

    def waiting_frame_detached(packet: dict[str, Any]) -> None:
        packet["adapter_binding_trace"]["waiting_frame_digest"] = (
            "sha256:" + "2" * 64
        )

    def waiting_dependency_detached(packet: dict[str, Any]) -> None:
        packet["adapter_binding_trace"]["waiting_dependency_digest"] = (
            "sha256:" + "3" * 64
        )

    def manifest_detached(packet: dict[str, Any]) -> None:
        packet["adapter_binding_trace"]["manifest_digest"] = (
            "sha256:" + "4" * 64
        )

    def waiting_requirement_removed(packet: dict[str, Any]) -> None:
        waiting = packet["adapter_binding_trace"]["waiting_dependency_id"]
        packet["reassembly_requirement"]["required_dependency_ids"] = [
            item
            for item in packet["reassembly_requirement"]["required_dependency_ids"]
            if item != waiting
        ]

    def temporal_immutability_reversed(packet: dict[str, Any]) -> None:
        packet["temporal_trace"]["parent_frame_set_unchanged"] = False

    def parent_release_reversed(packet: dict[str, Any]) -> None:
        packet["parent_proofreader_trace"]["release_decision"] = "BLOCK"

    def instruction_extra(packet: dict[str, Any]) -> None:
        packet["fresh_reassembly_instruction"]["callback"] = "forbidden"

    def duplicate_decision(packet: dict[str, Any]) -> None:
        packet["invalidation_decisions"].append(
            deepcopy(packet["invalidation_decisions"][0])
        )

    return [
        ("unknown_top_level", top_level_extra),
        ("bool_session_generation", bool_generation),
        ("event_payload_smuggling", payload_smuggling),
        ("state_rollback", state_rollback),
        ("instruction_execution", instruction_execution),
        ("source_read_claim", source_read),
        ("returned_data_claim", returned_data),
        ("command_authority", command_authority),
        ("provider_authority", provider_authority),
        ("stale_result_admitted", stale_admission),
        ("old_set_restored", restored_old_set),
        ("extracted_source_detached", extracted_source_detached),
        ("waiting_frame_detached", waiting_frame_detached),
        ("waiting_dependency_detached", waiting_dependency_detached),
        ("manifest_detached", manifest_detached),
        ("waiting_requirement_removed", waiting_requirement_removed),
        ("temporal_immutability_reversed", temporal_immutability_reversed),
        ("parent_release_reversed", parent_release_reversed),
        ("instruction_extra", instruction_extra),
        ("duplicate_decision", duplicate_decision),
    ]


def _negative_reason_codes(packet: dict[str, Any]) -> list[str]:
    results: list[str] = []
    for case_id, mutate in _mutations():
        candidate = deepcopy(packet)
        mutate(candidate)
        result = proofread_invalidation_reassembly_packet(candidate)
        if result["release_decision"] != "BLOCK" or result["released_packet"] is not None:
            raise AssertionError(f"negative case unexpectedly released: {case_id}")
        reason = result["reason_codes"][0]
        results.append(f"{case_id}:{reason}")
    expired = proofread_invalidation_reassembly_packet(
        deepcopy(packet), checked_at=packet["watch_lease"]["expires_at"]
    )
    if expired["release_decision"] != "BLOCK" or expired["released_packet"] is not None:
        raise AssertionError("expired packet unexpectedly released")
    results.append(f"expired_packet:{expired['reason_codes'][0]}")
    return sorted(results)


def build_acceptance_evidence() -> tuple[dict[str, Any], dict[str, Any]]:
    packet = build_authored_synthetic_invalidation_reassembly_packet()
    validate_invalidation_reassembly_packet(packet)
    Draft202012Validator.check_schema(SEAM_PACKET_SCHEMA)
    packet_errors = list(Draft202012Validator(SEAM_PACKET_SCHEMA).iter_errors(packet))
    if packet_errors:
        raise AssertionError(packet_errors)

    binding = packet["adapter_binding_trace"]
    requirement = packet["reassembly_requirement"]
    instruction = packet["fresh_reassembly_instruction"]
    waiting_dependency = next(
        item
        for item in packet["dependency_manifest"]["dependencies"]
        if item["dependency_id"] == binding["waiting_dependency_id"]
    )
    positive_invariants = {
        "parent_current_proofreader_released": packet["parent_proofreader_trace"][
            "release_decision"
        ]
        == "RELEASE",
        "adapter_source_frame_dependency_chain_exact": (
            binding["extracted_source_digest"]
            == waiting_dependency["source_digest"]
            and binding["waiting_frame_digest"]
            == waiting_dependency["frame_digest"]
        ),
        "signal_payload_free": "payload" not in packet["signal"],
        "old_frame_set_byte_immutable": packet["temporal_trace"][
            "parent_frame_set_unchanged"
        ],
        "old_frame_set_retired": (
            packet["frame_set_state"]["state"] == "REASSEMBLY_REQUIRED"
            and packet["frame_set_state"]["usable_for_new_reasoning"] is False
        ),
        "exactly_one_requirement": requirement is not None,
        "waiting_dependency_required": binding["waiting_dependency_id"]
        in requirement["required_dependency_ids"],
        "instruction_inert": (
            instruction["execution_enabled"] is False
            and instruction["source_read_executed"] is False
            and instruction["returns_data"] is False
            and instruction["command_authority"] is False
            and instruction["provider_authority"] is False
        ),
        "stale_request_rejected": packet["stale_reassembly_decision"]["decision"]
        == "REJECT_SUPERSEDED_REQUEST",
    }
    if not all(positive_invariants.values()):
        raise AssertionError(positive_invariants)

    negative_codes = _negative_reason_codes(packet)
    case_count = len(positive_invariants) + 2 + len(negative_codes)
    evidence = {
        "schema_version": "emr4.practice_context_fabric_rayleen_invalidation_reassembly_acceptance.v1",
        "result": RESULT,
        "evidence_label": EVIDENCE_LABEL,
        "case_count": case_count,
        "passed_case_count": case_count,
        "adapter_result_digest": binding["adapter_result_digest"],
        "adapter_binding_digest": binding["adapter_binding_trace_digest"],
        "adapted_parent_frame_set_digest": binding["rebuilt_frame_set_digest"],
        "adapted_parent_proofreader_trace_digest": packet[
            "parent_proofreader_trace"
        ]["proofreader_trace_digest"],
        "manifest_digest": packet["dependency_manifest"]["manifest_digest"],
        "lease_digest": packet["watch_lease"]["lease_digest"],
        "signal_digest": packet["signal"]["signal_digest"],
        "decision_digest": packet["invalidation_decisions"][0]["decision_digest"],
        "checkpoint_digest": packet["committed_checkpoint"]["checkpoint_digest"],
        "state_digest": packet["frame_set_state"]["state_digest"],
        "requirement_digest": requirement["requirement_digest"],
        "instruction_digest": instruction["instruction_digest"],
        "stale_reassembly_decision_digest": packet["stale_reassembly_decision"][
            "reassembly_decision_digest"
        ],
        "temporal_trace_digest": packet["temporal_trace"]["temporal_trace_digest"],
        "seam_proofreader_trace_digest": packet["proofreader_trace"][
            "proofreader_trace_digest"
        ],
        "seam_proofreader_decision": packet["proofreader_trace"][
            "release_decision"
        ],
        "positive_invariants": positive_invariants,
        "negative_reason_codes": negative_codes,
        "zero_action_posture": {
            "provider_calls": 0,
            "network_calls": 0,
            "database_calls": 0,
            "product_api_calls": 0,
            "source_reads": 0,
            "commands_or_writes": 0,
            "watcher_or_event_subscriptions": 0,
            "deployments_or_releases": 0,
            "protected_actions": 0,
        },
        "artifact_hashes": {
            "seam_module": _sha256_file(
                ROOT
                / "scripts"
                / "raisa_provider_free_unmounted_rayleen_waiting_room_context_fabric_invalidation_reassembly.py"
            ),
            "source_adapter_module": _sha256_file(
                ROOT
                / "scripts"
                / "raisa_provider_free_unmounted_rayleen_waiting_room_context_fabric_source_adapter.py"
            ),
            "current_weave_module": _sha256_file(
                ROOT
                / "scripts"
                / "raisa_provider_free_practice_context_fabric_current_operational_weave.py"
            ),
            "temporal_weave_module": _sha256_file(
                ROOT
                / "scripts"
                / "raisa_provider_free_practice_context_fabric_patient_free_temporal_weave.py"
            ),
            "seam_packet_schema": _sha256_file(PACKET_SCHEMA_PATH),
            "acceptance_evidence_schema": _sha256_file(EVIDENCE_SCHEMA_PATH),
        },
        "claim_boundary": CLAIM_BOUNDARY,
    }
    schema = json.loads(EVIDENCE_SCHEMA_PATH.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    errors = list(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(
            evidence
        )
    )
    if errors:
        raise AssertionError(errors)
    return packet, evidence


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--packet-output", type=Path, default=DEFAULT_PACKET_PATH)
    parser.add_argument("--evidence-output", type=Path, default=DEFAULT_EVIDENCE_PATH)
    args = parser.parse_args()

    _write_json(PACKET_SCHEMA_PATH, SEAM_PACKET_SCHEMA)
    packet, evidence = build_acceptance_evidence()
    _write_json(args.packet_output, packet)
    _write_json(args.evidence_output, evidence)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
