"""Generate deterministic evidence for the unmounted Rayleen fresh generation."""

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

from scripts.raisa_provider_free_unmounted_rayleen_waiting_room_context_fabric_fresh_generation_rehearsal import (
    EVIDENCE_LABEL,
    FRESH_GENERATION_PACKET_SCHEMA,
    build_authored_synthetic_fresh_generation_packet,
    proofread_fresh_generation_packet,
    validate_fresh_generation_packet,
)


CONTINUITY_DIR = (
    ROOT
    / "orchestration"
    / "continuity"
    / "raisa-provider-free-unmounted-rayleen-waiting-room-context-fabric-fresh-generation-rehearsal"
)
PACKET_SCHEMA_PATH = CONTINUITY_DIR / "fresh-generation-packet.schema.json"
EVIDENCE_SCHEMA_PATH = CONTINUITY_DIR / "acceptance-evidence.schema.json"
DEFAULT_PACKET_PATH = CONTINUITY_DIR / "authored-synthetic-fresh-generation-packet.json"
DEFAULT_EVIDENCE_PATH = CONTINUITY_DIR / "provider-free-acceptance-evidence.json"
RESULT = (
    "raisa_provider_free_unmounted_rayleen_waiting_room_context_fabric_"
    "fresh_generation_rehearsal_pass"
)
CLAIM_BOUNDARY = (
    "Provider-free authored-synthetic unmounted retire-to-new-generation and "
    "deterministic supersession evidence only; no real data, live watcher, "
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
    def unknown_top_level(packet: dict[str, Any]) -> None:
        packet["unexpected"] = True

    def bool_request_revision(packet: dict[str, Any]) -> None:
        packet["fresh_generation_admission"]["current_request_revision"] = True

    def authority_widened(packet: dict[str, Any]) -> None:
        packet["authority_trace"]["grant_no_wider"] = False

    def predecessor_validity_reversed(packet: dict[str, Any]) -> None:
        packet["predecessor_validity_trace"]["requirement_current"] = False

    def request_not_distinct(packet: dict[str, Any]) -> None:
        packet["authority_trace"]["distinct_need"] = False

    def diary_refresh_missing(packet: dict[str, Any]) -> None:
        trace = packet["required_dependency_refresh_trace"]
        trace["refreshed_dependency_ids"] = [
            item
            for item in trace["refreshed_dependency_ids"]
            if "diary" not in item
        ]
        trace["refresh_records"] = [
            item
            for item in trace["refresh_records"]
            if item["frame_type"] != "current_diary_projection"
        ]

    def event_used_as_truth(packet: dict[str, Any]) -> None:
        packet["required_dependency_refresh_trace"][
            "event_metadata_used_as_context"
        ] = True

    def product_read_claim(packet: dict[str, Any]) -> None:
        packet["product_read_executed"] = True

    def source_read_claim(packet: dict[str, Any]) -> None:
        packet["source_read_executed"] = True

    def carried_source_expired(packet: dict[str, Any]) -> None:
        packet["carry_forward_trace"]["carry_records"][0]["unexpired"] = False

    def carried_source_changed(packet: dict[str, Any]) -> None:
        packet["carry_forward_trace"]["carry_records"][0][
            "source_digest_after"
        ] = "sha256:" + "1" * 64

    def adapter_detached(packet: dict[str, Any]) -> None:
        packet["required_dependency_refresh_trace"]["adapter_result_digest"] = (
            "sha256:" + "2" * 64
        )

    def current_proofreader_blocked(packet: dict[str, Any]) -> None:
        packet["current_proofreader_trace"]["release_decision"] = "BLOCK"

    def new_frame_collides(packet: dict[str, Any]) -> None:
        immutable = packet["old_generation_immutability_trace"]
        packet["new_frame_set"]["frame_set_id"] = immutable["old_frame_set_id"]

    def manifest_detached(packet: dict[str, Any]) -> None:
        packet["fresh_generation_admission"]["manifest_digest"] = (
            "sha256:" + "3" * 64
        )

    def lease_detached(packet: dict[str, Any]) -> None:
        packet["fresh_generation_admission"]["lease_digest"] = (
            "sha256:" + "4" * 64
        )

    def admission_rejected(packet: dict[str, Any]) -> None:
        packet["fresh_generation_admission"]["admission_decision"] = (
            "REJECT_SUPERSEDED_REQUEST"
        )

    def supplied_copy_released(packet: dict[str, Any]) -> None:
        packet["fresh_generation_admission"][
            "released_trusted_deep_copy_only"
        ] = False

    def older_result_admitted(packet: dict[str, Any]) -> None:
        packet["older_result_rejection"]["decision"] = "ADMIT_NEW_GENERATION"

    def ordering_rollback(packet: dict[str, Any]) -> None:
        packet["completion_order_traces"][1]["rollback_occurred"] = True

    def old_frame_restored(packet: dict[str, Any]) -> None:
        packet["old_generation_immutability_trace"]["old_frame_set_restored"] = True

    def old_frame_mutated(packet: dict[str, Any]) -> None:
        packet["old_generation_immutability_trace"]["old_frame_set_bytes_after"] = (
            "sha256:" + "5" * 64
        )

    def runtime_mounted(packet: dict[str, Any]) -> None:
        packet["runtime_state_mounted"] = True

    def listener_mounted(packet: dict[str, Any]) -> None:
        packet["listener_mounted"] = True

    def command_authority(packet: dict[str, Any]) -> None:
        packet["command_authority"] = True

    def provider_called(packet: dict[str, Any]) -> None:
        packet["provider_called"] = True

    return [
        ("unknown_top_level", unknown_top_level),
        ("bool_request_revision", bool_request_revision),
        ("authority_widened", authority_widened),
        ("predecessor_validity_reversed", predecessor_validity_reversed),
        ("request_not_distinct", request_not_distinct),
        ("diary_refresh_missing", diary_refresh_missing),
        ("event_used_as_truth", event_used_as_truth),
        ("product_read_claim", product_read_claim),
        ("source_read_claim", source_read_claim),
        ("carried_source_expired", carried_source_expired),
        ("carried_source_changed", carried_source_changed),
        ("adapter_detached", adapter_detached),
        ("current_proofreader_blocked", current_proofreader_blocked),
        ("new_frame_collides", new_frame_collides),
        ("manifest_detached", manifest_detached),
        ("lease_detached", lease_detached),
        ("admission_rejected", admission_rejected),
        ("supplied_copy_released", supplied_copy_released),
        ("older_result_admitted", older_result_admitted),
        ("ordering_rollback", ordering_rollback),
        ("old_frame_restored", old_frame_restored),
        ("old_frame_mutated", old_frame_mutated),
        ("runtime_mounted", runtime_mounted),
        ("listener_mounted", listener_mounted),
        ("command_authority", command_authority),
        ("provider_called", provider_called),
    ]


def _negative_reason_codes(packet: dict[str, Any]) -> list[str]:
    results: list[str] = []
    for case_id, mutate in _mutations():
        candidate = deepcopy(packet)
        mutate(candidate)
        result = proofread_fresh_generation_packet(candidate)
        if result["release_decision"] != "BLOCK" or result["released_packet"] is not None:
            raise AssertionError(f"negative case unexpectedly released: {case_id}")
        results.append(f"{case_id}:{result['reason_codes'][0]}")
    expired = proofread_fresh_generation_packet(
        deepcopy(packet), checked_at=packet["new_watch_lease"]["expires_at"]
    )
    if expired["release_decision"] != "BLOCK" or expired["released_packet"] is not None:
        raise AssertionError("expired packet unexpectedly released")
    results.append(f"expired_packet:{expired['reason_codes'][0]}")
    predecessor_expired = proofread_fresh_generation_packet(
        deepcopy(packet),
        checked_at=packet["predecessor_validity_trace"][
            "requirement_expires_at"
        ],
    )
    if (
        predecessor_expired["release_decision"] != "BLOCK"
        or predecessor_expired["released_packet"] is not None
    ):
        raise AssertionError("expired predecessor requirement unexpectedly released")
    results.append(
        "expired_predecessor_requirement:"
        + predecessor_expired["reason_codes"][0]
    )
    return sorted(results)


def build_acceptance_evidence() -> tuple[dict[str, Any], dict[str, Any]]:
    packet = build_authored_synthetic_fresh_generation_packet()
    validate_fresh_generation_packet(packet)
    Draft202012Validator.check_schema(FRESH_GENERATION_PACKET_SCHEMA)
    packet_errors = list(
        Draft202012Validator(FRESH_GENERATION_PACKET_SCHEMA).iter_errors(packet)
    )
    if packet_errors:
        raise AssertionError(packet_errors)

    authority = packet["authority_trace"]
    refresh = packet["required_dependency_refresh_trace"]
    carry = packet["carry_forward_trace"]
    admission = packet["fresh_generation_admission"]
    immutable = packet["old_generation_immutability_trace"]
    refreshed_frame_types = {
        item["frame_type"] for item in refresh["refresh_records"]
    }
    positive_invariants = {
        "predecessor_reconstructed": packet["predecessor_packet_digest"].startswith(
            "sha256:"
        ),
        "predecessor_requirement_and_instruction_current": (
            packet["predecessor_validity_trace"]["requirement_current"] is True
            and packet["predecessor_validity_trace"]["instruction_current"] is True
            and packet["predecessor_validity_trace"][
                "execution_authority_created"
            ]
            is False
        ),
        "requirement_refresh_coverage_exact": (
            refresh["required_dependency_ids"] == refresh["refreshed_dependency_ids"]
            and refresh["complete_coverage"] is True
        ),
        "event_metadata_not_used_as_truth": refresh[
            "event_metadata_used_as_context"
        ]
        is False,
        "authority_no_wider": (
            authority["binding_current"] is True
            and authority["grant_no_wider"] is True
            and authority["identity_equal"] is True
        ),
        "diary_and_waiting_sources_new": refreshed_frame_types
        == {"current_diary_projection", "current_waiting_room_projection"},
        "adapter_extractor_chain_exact": refresh["adapter_result_digest"].startswith(
            "sha256:"
        )
        and refresh["extractor_recomputed_source_digest"]
        == next(
            item["new_source_digest"]
            for item in refresh["refresh_records"]
            if item["frame_type"] == "current_waiting_room_projection"
        ),
        "unaffected_carry_forward_exact": carry["all_eligible"] is True
        and all(
            item["canonical_bytes_unchanged"]
            and item["unaffected"]
            and item["granted"]
            and item["coherent_session"]
            and item["unexpired"]
            for item in carry["carry_records"]
        ),
        "current_proofreader_released": packet["current_proofreader_trace"][
            "release_decision"
        ]
        == "RELEASE",
        "new_frame_set_distinct": immutable["distinct_generation"] is True
        and immutable["old_frame_set_digest"]
        != packet["new_frame_set"]["frame_set_digest"],
        "new_temporal_objects_rederived": (
            packet["new_dependency_manifest"]["parent_frame_set_digest"]
            == packet["new_frame_set"]["frame_set_digest"]
            and packet["new_watch_lease"]["manifest_digest"]
            == packet["new_dependency_manifest"]["manifest_digest"]
        ),
        "new_generation_admitted": admission["admission_decision"]
        == "ADMIT_NEW_GENERATION",
        "older_result_rejected": packet["older_result_rejection"]["decision"]
        == "REJECT_SUPERSEDED_REQUEST",
        "both_orders_converge": all(
            item["final_frame_set_digest"] == packet["new_frame_set"]["frame_set_digest"]
            and item["rollback_occurred"] is False
            and item["old_frame_set_restored"] is False
            for item in packet["completion_order_traces"]
        ),
        "old_generation_immutable_and_retired": (
            immutable["old_frame_set_bytes_unchanged"] is True
            and immutable["old_generation_state"] == "RETIRED"
            and immutable["old_frame_set_restored"] is False
        ),
    }
    if not all(positive_invariants.values()):
        raise AssertionError(positive_invariants)

    negative_codes = _negative_reason_codes(packet)
    case_count = len(positive_invariants) + 2 + len(negative_codes)
    evidence = {
        "schema_version": "emr4.practice_context_fabric_rayleen_fresh_generation_acceptance.v1",
        "result": RESULT,
        "evidence_label": EVIDENCE_LABEL,
        "case_count": case_count,
        "passed_case_count": case_count,
        "predecessor_packet_digest": packet["predecessor_packet_digest"],
        "requirement_digest": packet["predecessor_requirement_digest"],
        "instruction_digest": packet["predecessor_instruction_digest"],
        "predecessor_validity_trace_digest": packet[
            "predecessor_validity_trace"
        ]["predecessor_validity_trace_digest"],
        "authority_trace_digest": authority["authority_trace_digest"],
        "refresh_trace_digest": refresh["refresh_trace_digest"],
        "carry_forward_trace_digest": carry["carry_forward_trace_digest"],
        "adapter_result_digest": refresh["adapter_result_digest"],
        "new_frame_set_digest": packet["new_frame_set"]["frame_set_digest"],
        "new_source_trace_digest": packet["new_source_trace"]["source_trace_digest"],
        "new_current_proofreader_trace_digest": packet["current_proofreader_trace"][
            "proofreader_trace_digest"
        ],
        "new_manifest_digest": packet["new_dependency_manifest"]["manifest_digest"],
        "new_lease_digest": packet["new_watch_lease"]["lease_digest"],
        "admission_digest": admission["admission_digest"],
        "older_result_rejection_digest": packet["older_result_rejection"][
            "reassembly_decision_digest"
        ],
        "old_then_new_trace_digest": packet["completion_order_traces"][0][
            "ordering_trace_digest"
        ],
        "new_then_old_trace_digest": packet["completion_order_traces"][1][
            "ordering_trace_digest"
        ],
        "immutability_trace_digest": immutable["immutability_trace_digest"],
        "fresh_generation_proofreader_trace_digest": packet["proofreader_trace"][
            "proofreader_trace_digest"
        ],
        "fresh_generation_proofreader_decision": packet["proofreader_trace"][
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
            "fresh_generation_module": _sha256_file(
                ROOT
                / "scripts"
                / "raisa_provider_free_unmounted_rayleen_waiting_room_context_fabric_fresh_generation_rehearsal.py"
            ),
            "invalidation_seam_module": _sha256_file(
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
            "fresh_generation_packet_schema": _sha256_file(PACKET_SCHEMA_PATH),
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

    _write_json(PACKET_SCHEMA_PATH, FRESH_GENERATION_PACKET_SCHEMA)
    packet, evidence = build_acceptance_evidence()
    _write_json(args.packet_output, packet)
    _write_json(args.evidence_output, evidence)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
