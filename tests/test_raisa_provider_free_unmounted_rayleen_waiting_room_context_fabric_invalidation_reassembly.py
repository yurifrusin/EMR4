from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from scripts.raisa_provider_free_practice_context_fabric_bureau_memory_contract import (
    ContractViolation,
    canonical_json,
    seal,
)
from scripts.raisa_provider_free_practice_context_fabric_current_operational_weave import (
    build_authored_synthetic_packet,
)
from scripts.raisa_provider_free_unmounted_rayleen_waiting_room_context_fabric_invalidation_reassembly import (
    ASSEMBLED_AT,
    EVIDENCE_LABEL,
    INSTRUCTION_STEPS,
    SEAM_PACKET_SCHEMA,
    build_authored_synthetic_invalidation_reassembly_packet,
    build_invalidation_reassembly_candidate,
    proofread_invalidation_reassembly_candidate,
    proofread_invalidation_reassembly_packet,
    validate_invalidation_reassembly_packet,
)
from scripts.raisa_provider_free_unmounted_rayleen_waiting_room_context_fabric_invalidation_reassembly_acceptance import (
    CONTINUITY_DIR,
    build_acceptance_evidence,
)
from scripts.raisa_provider_free_unmounted_rayleen_waiting_room_context_fabric_source_adapter import (
    adapt_waiting_room_source,
    build_authored_synthetic_alias_manifest,
    build_authored_synthetic_waiting_room_frame,
)


def _inputs() -> tuple[dict, dict, dict, dict]:
    parent = build_authored_synthetic_packet()
    frame = build_authored_synthetic_waiting_room_frame()
    manifest = build_authored_synthetic_alias_manifest(
        frame, parent["authority_binding"], parent["scope_grant"]
    )
    result = adapt_waiting_room_source(
        frame,
        parent["authority_binding"],
        parent["scope_grant"],
        manifest,
        assembled_at=ASSEMBLED_AT,
    )
    return parent, frame, manifest, result


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _reseal(value: dict, field: str) -> None:
    replacement = seal(
        {key: item for key, item in value.items() if key != field}, field
    )
    value.clear()
    value.update(replacement)


def _blocked(packet: dict, *, checked_at: str | None = None) -> dict:
    kwargs = {} if checked_at is None else {"checked_at": checked_at}
    result = proofread_invalidation_reassembly_packet(packet, **kwargs)
    assert result["release_decision"] == "BLOCK"
    assert result["released_packet"] is None
    return result


def test_nominal_packet_is_closed_valid_and_released() -> None:
    packet = build_authored_synthetic_invalidation_reassembly_packet()

    Draft202012Validator.check_schema(SEAM_PACKET_SCHEMA)
    assert list(Draft202012Validator(SEAM_PACKET_SCHEMA).iter_errors(packet)) == []
    validate_invalidation_reassembly_packet(packet)
    assert packet["evidence_label"] == EVIDENCE_LABEL
    assert packet["proofreader_trace"]["release_decision"] == "RELEASE"


def test_public_proofreader_releases_only_a_trusted_deep_copy() -> None:
    packet = build_authored_synthetic_invalidation_reassembly_packet()
    result = proofread_invalidation_reassembly_packet(packet)

    assert result["release_decision"] == "RELEASE"
    assert result["released_packet"] == packet
    result["released_packet"]["new_frame_set_admitted"] = True
    assert packet["new_frame_set_admitted"] is False


def test_adapter_parent_is_rebuilt_and_old_parent_remains_byte_identical() -> None:
    parent, frame, manifest, adapter_result = _inputs()
    before = canonical_json(parent["frame_set"])
    candidate = build_invalidation_reassembly_candidate(
        parent, frame, manifest, adapter_result
    )

    assert canonical_json(parent["frame_set"]) == before
    assert candidate["parent_proofreader_trace"]["release_decision"] == "RELEASE"
    assert candidate["temporal_trace"]["parent_frame_set_unchanged"] is True
    assert candidate["frame_set_state"]["state"] == "REASSEMBLY_REQUIRED"
    assert candidate["frame_set_state"]["usable_for_new_reasoning"] is False
    assert candidate["frame_set_state"]["frames_mutated"] is False


def test_one_payload_free_signal_emits_one_inert_requirement() -> None:
    packet = build_authored_synthetic_invalidation_reassembly_packet()

    assert "payload" not in packet["signal"]
    assert len(packet["invalidation_decisions"]) == 1
    assert packet["invalidation_decisions"][0]["decision"] == (
        "REASSEMBLY_REQUIRED"
    )
    requirement = packet["reassembly_requirement"]
    assert requirement["execution_enabled"] is False
    assert requirement["returns_data"] is False
    waiting_dependency = packet["adapter_binding_trace"]["waiting_dependency_id"]
    assert waiting_dependency in requirement["required_dependency_ids"]


def test_fresh_instruction_is_complete_ordered_and_non_executable() -> None:
    instruction = build_authored_synthetic_invalidation_reassembly_packet()[
        "fresh_reassembly_instruction"
    ]

    assert instruction["ordered_steps"] == INSTRUCTION_STEPS
    assert instruction["execution_enabled"] is False
    assert instruction["source_read_executed"] is False
    assert instruction["returns_data"] is False
    assert instruction["command_authority"] is False
    assert instruction["provider_authority"] is False


def test_stale_request_is_rejected_without_restoring_old_set() -> None:
    decision = build_authored_synthetic_invalidation_reassembly_packet()[
        "stale_reassembly_decision"
    ]

    assert decision["decision"] == "REJECT_SUPERSEDED_REQUEST"
    assert decision["old_frame_set_restored"] is False


def test_fully_resealed_adapter_provenance_detachment_is_rejected() -> None:
    parent, frame, manifest, adapter_result = _inputs()
    adapter_result["adapter_trace"]["binding_digest"] = "sha256:" + "1" * 64
    _reseal(adapter_result["adapter_trace"], "adapter_trace_digest")
    _reseal(adapter_result, "adapter_result_digest")

    with pytest.raises(ContractViolation, match="provenance_mismatch"):
        build_invalidation_reassembly_candidate(
            parent, frame, manifest, adapter_result
        )


def test_unknown_nested_field_blocks_even_when_object_is_resealed() -> None:
    packet = build_authored_synthetic_invalidation_reassembly_packet()
    packet["fresh_reassembly_instruction"]["callback"] = "run_read"
    _reseal(packet["fresh_reassembly_instruction"], "instruction_digest")

    _blocked(packet)


def test_bool_as_integer_blocks_even_when_instruction_is_resealed() -> None:
    packet = build_authored_synthetic_invalidation_reassembly_packet()
    packet["fresh_reassembly_instruction"]["request_revision"] = True
    _reseal(packet["fresh_reassembly_instruction"], "instruction_digest")

    _blocked(packet)


def test_event_payload_smuggling_blocks_even_when_signal_is_resealed() -> None:
    packet = build_authored_synthetic_invalidation_reassembly_packet()
    packet["signal"]["payload"] = {"replacement_status": "COMPLETED"}
    _reseal(packet["signal"], "signal_digest")

    _blocked(packet)


def test_resealed_state_rollback_blocks() -> None:
    packet = build_authored_synthetic_invalidation_reassembly_packet()
    packet["frame_set_state"]["state"] = "CURRENT"
    packet["frame_set_state"]["usable_for_new_reasoning"] = True
    _reseal(packet["frame_set_state"], "state_digest")

    _blocked(packet)


def test_resealed_executable_instruction_flags_block() -> None:
    packet = build_authored_synthetic_invalidation_reassembly_packet()
    packet["fresh_reassembly_instruction"]["execution_enabled"] = True
    packet["fresh_reassembly_instruction"]["source_read_executed"] = True
    packet["fresh_reassembly_instruction"]["command_authority"] = True
    _reseal(packet["fresh_reassembly_instruction"], "instruction_digest")

    _blocked(packet)


def test_resealed_stale_result_admission_blocks() -> None:
    packet = build_authored_synthetic_invalidation_reassembly_packet()
    packet["stale_reassembly_decision"]["decision"] = "ADMIT_NEW_GENERATION"
    packet["stale_reassembly_decision"]["old_frame_set_restored"] = True
    _reseal(packet["stale_reassembly_decision"], "reassembly_decision_digest")

    _blocked(packet)


@pytest.mark.parametrize(
    "field",
    [
        "extracted_source_digest",
        "waiting_frame_digest",
        "waiting_dependency_digest",
        "manifest_digest",
    ],
)
def test_resealed_source_frame_dependency_detachment_blocks(field: str) -> None:
    packet = build_authored_synthetic_invalidation_reassembly_packet()
    packet["adapter_binding_trace"][field] = "sha256:" + "2" * 64
    _reseal(packet["adapter_binding_trace"], "adapter_binding_trace_digest")

    _blocked(packet)


def test_expired_packet_blocks_without_release() -> None:
    packet = build_authored_synthetic_invalidation_reassembly_packet()
    _blocked(packet, checked_at=packet["watch_lease"]["expires_at"])


def test_lower_level_proofreader_reconstructs_candidate_and_releases() -> None:
    parent, frame, manifest, adapter_result = _inputs()
    candidate = build_invalidation_reassembly_candidate(
        parent, frame, manifest, adapter_result
    )
    result = proofread_invalidation_reassembly_candidate(
        parent, frame, manifest, adapter_result, deepcopy(candidate)
    )

    assert result["release_decision"] == "RELEASE"
    assert result["released_packet"] is not None
    assert result["released_packet"]["proofreader_trace"]["release_decision"] == (
        "RELEASE"
    )


def test_committed_packet_and_evidence_reproduce_exactly() -> None:
    packet, evidence = build_acceptance_evidence()

    assert packet == _json(CONTINUITY_DIR / "authored-synthetic-seam-packet.json")
    assert evidence == _json(
        CONTINUITY_DIR / "provider-free-acceptance-evidence.json"
    )
    assert evidence["case_count"] == evidence["passed_case_count"] == 32
    evidence_schema = _json(CONTINUITY_DIR / "acceptance-evidence.schema.json")
    assert list(Draft202012Validator(evidence_schema).iter_errors(evidence)) == []
    assert _json(CONTINUITY_DIR / "seam-packet.schema.json") == SEAM_PACKET_SCHEMA


def test_committed_artifact_hashes_match_direct_bytes() -> None:
    evidence = _json(CONTINUITY_DIR / "provider-free-acceptance-evidence.json")
    root = CONTINUITY_DIR.parents[2]
    expected_paths = {
        "seam_module": root
        / "scripts"
        / "raisa_provider_free_unmounted_rayleen_waiting_room_context_fabric_invalidation_reassembly.py",
        "source_adapter_module": root
        / "scripts"
        / "raisa_provider_free_unmounted_rayleen_waiting_room_context_fabric_source_adapter.py",
        "current_weave_module": root
        / "scripts"
        / "raisa_provider_free_practice_context_fabric_current_operational_weave.py",
        "temporal_weave_module": root
        / "scripts"
        / "raisa_provider_free_practice_context_fabric_patient_free_temporal_weave.py",
        "seam_packet_schema": CONTINUITY_DIR / "seam-packet.schema.json",
        "acceptance_evidence_schema": CONTINUITY_DIR
        / "acceptance-evidence.schema.json",
    }
    assert evidence["artifact_hashes"] == {
        name: _sha256(path) for name, path in expected_paths.items()
    }


def test_seam_imports_no_product_runtime_or_effectful_client() -> None:
    root = CONTINUITY_DIR.parents[2]
    source = (
        root
        / "scripts"
        / "raisa_provider_free_unmounted_rayleen_waiting_room_context_fabric_invalidation_reassembly.py"
    ).read_text(encoding="utf-8")

    for forbidden in (
        "from app",
        "import app",
        "requests",
        "httpx",
        "sqlalchemy",
        "subprocess",
        "socket",
        "vertexai",
        "google.cloud",
    ):
        assert forbidden not in source
