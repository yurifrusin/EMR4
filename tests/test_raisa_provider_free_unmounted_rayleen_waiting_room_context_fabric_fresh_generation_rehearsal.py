from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from scripts.raisa_provider_free_practice_context_fabric_bureau_memory_contract import (
    seal,
)
from scripts.raisa_provider_free_unmounted_rayleen_waiting_room_context_fabric_fresh_generation_rehearsal import (
    EVIDENCE_LABEL,
    FRESH_GENERATION_PACKET_SCHEMA,
    FreshGenerationViolation,
    build_authored_synthetic_fresh_generation_packet,
    proofread_fresh_generation_packet,
    validate_fresh_generation_packet,
)
from scripts.raisa_provider_free_unmounted_rayleen_waiting_room_context_fabric_fresh_generation_rehearsal_acceptance import (
    CONTINUITY_DIR,
    build_acceptance_evidence,
)
from scripts.raisa_provider_free_unmounted_rayleen_waiting_room_context_fabric_invalidation_reassembly import (
    build_authored_synthetic_invalidation_reassembly_packet,
)


MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "raisa_provider_free_unmounted_rayleen_waiting_room_context_fabric_fresh_generation_rehearsal.py"
)


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
    result = proofread_fresh_generation_packet(packet, **kwargs)
    assert result["release_decision"] == "BLOCK"
    assert result["released_packet"] is None
    return result


def test_nominal_packet_is_closed_valid_and_released() -> None:
    packet = build_authored_synthetic_fresh_generation_packet()

    Draft202012Validator.check_schema(FRESH_GENERATION_PACKET_SCHEMA)
    assert not list(
        Draft202012Validator(FRESH_GENERATION_PACKET_SCHEMA).iter_errors(packet)
    )
    validate_fresh_generation_packet(packet)
    assert packet["evidence_label"] == EVIDENCE_LABEL
    assert packet["proofreader_trace"]["release_decision"] == "RELEASE"


def test_public_proofreader_releases_only_a_trusted_deep_copy() -> None:
    packet = build_authored_synthetic_fresh_generation_packet()
    result = proofread_fresh_generation_packet(packet)

    assert result["release_decision"] == "RELEASE"
    assert result["released_packet"] == packet
    result["released_packet"]["new_frame_set_admitted"] = False
    assert packet["new_frame_set_admitted"] is True


def test_distinct_request_revalidates_binding_and_never_widens_grant() -> None:
    trace = build_authored_synthetic_fresh_generation_packet()["authority_trace"]

    assert trace["distinct_need"] is True
    assert trace["monotonic_request_revision"] is True
    assert trace["binding_current"] is True
    assert trace["grant_no_wider"] is True
    assert trace["identity_equal"] is True
    assert {
        "allowed_frame_types",
        "allowed_source_classes",
        "required_source_classes",
        "allowed_fields",
        "allowed_location_refs",
        "effective_time_window",
        "maximum_frames",
        "maximum_items_per_frame",
        "maximum_total_bytes",
        "freshness_seconds",
        "requesting_bureau",
        "purpose_code",
        "binding_digest",
        "session_binding_digest",
        "read_only",
        "command_authority",
        "provider_authority",
    } == set(trace["scope_dimensions_checked"])


def test_predecessor_requirement_and_instruction_must_still_be_current() -> None:
    packet = build_authored_synthetic_fresh_generation_packet()
    validity = packet["predecessor_validity_trace"]

    assert validity["requirement_current"] is True
    assert validity["instruction_current"] is True
    assert validity["execution_authority_created"] is False
    _blocked(packet, checked_at=validity["requirement_expires_at"])


def test_every_requirement_dependency_is_refreshed_independently() -> None:
    trace = build_authored_synthetic_fresh_generation_packet()[
        "required_dependency_refresh_trace"
    ]

    assert trace["complete_coverage"] is True
    assert trace["refreshed_dependency_ids"] == sorted(
        trace["required_dependency_ids"]
    )
    assert {item["frame_type"] for item in trace["refresh_records"]} == {
        "current_diary_projection",
        "current_waiting_room_projection",
    }
    assert all(item["independently_authored"] for item in trace["refresh_records"])
    assert all(
        item["new_source_digest"] != item["old_source_digest"]
        for item in trace["refresh_records"]
    )
    assert trace["event_metadata_used_as_context"] is False
    assert trace["source_read_executed"] is False
    assert trace["product_read_executed"] is False


def test_second_waiting_source_retains_exact_adapter_extractor_chain() -> None:
    trace = build_authored_synthetic_fresh_generation_packet()[
        "required_dependency_refresh_trace"
    ]
    waiting = next(
        item
        for item in trace["refresh_records"]
        if item["frame_type"] == "current_waiting_room_projection"
    )

    assert trace["waiting_source_frame_digest"].startswith("sha256:")
    assert trace["alias_manifest_digest"].startswith("sha256:")
    assert trace["adapter_result_digest"].startswith("sha256:")
    assert trace["adapter_trace_digest"].startswith("sha256:")
    assert trace["extractor_recomputed_source_digest"] == waiting[
        "new_source_digest"
    ]


def test_only_unaffected_exact_fresh_sources_carry_forward() -> None:
    trace = build_authored_synthetic_fresh_generation_packet()[
        "carry_forward_trace"
    ]

    assert trace["carried_frame_types"] == [
        "active_practitioner_directory",
        "private_application_session_state",
    ]
    assert trace["all_eligible"] is True
    assert trace["persistence_used"] is False
    assert trace["retention_authority"] is False
    for item in trace["carry_records"]:
        assert item["source_digest_before"] == item["source_digest_after"]
        assert item["canonical_bytes_unchanged"] is True
        assert item["unaffected"] is True
        assert item["granted"] is True
        assert item["coherent_session"] is True
        assert item["unexpired"] is True


def test_new_current_weave_is_distinct_linked_and_released() -> None:
    packet = build_authored_synthetic_fresh_generation_packet()
    old = build_authored_synthetic_invalidation_reassembly_packet()

    assert packet["current_proofreader_trace"]["release_decision"] == "RELEASE"
    assert packet["new_frame_set"]["frame_set_id"] != old[
        "reassembly_requirement"
    ]["superseded_frame_set_id"]
    assert packet["new_frame_set"]["frame_set_digest"] != old[
        "reassembly_requirement"
    ]["superseded_frame_set_digest"]
    assert packet["new_frame_set"]["source_trace_digest"] == packet[
        "new_source_trace"
    ]["source_trace_digest"]
    assert packet["new_weave_trace"]["frame_set_digest"] == packet[
        "new_frame_set"
    ]["frame_set_digest"]


def test_new_manifest_and_lease_are_derived_not_inherited() -> None:
    packet = build_authored_synthetic_fresh_generation_packet()
    old = build_authored_synthetic_invalidation_reassembly_packet()

    assert packet["new_dependency_manifest"]["parent_frame_set_digest"] == packet[
        "new_frame_set"
    ]["frame_set_digest"]
    assert packet["new_dependency_manifest"]["manifest_digest"] != old[
        "dependency_manifest"
    ]["manifest_digest"]
    assert packet["new_watch_lease"]["manifest_digest"] == packet[
        "new_dependency_manifest"
    ]["manifest_digest"]
    assert packet["new_watch_lease"]["lease_digest"] != old["watch_lease"][
        "lease_digest"
    ]


def test_new_generation_admits_and_old_result_is_rejected() -> None:
    packet = build_authored_synthetic_fresh_generation_packet()
    admission = packet["fresh_generation_admission"]
    rejection = packet["older_result_rejection"]

    assert admission["admission_decision"] == "ADMIT_NEW_GENERATION"
    assert admission["frame_set_digest"] == packet["new_frame_set"][
        "frame_set_digest"
    ]
    assert admission["released_trusted_deep_copy_only"] is True
    assert admission["runtime_state_mounted"] is False
    assert admission["persistence_used"] is False
    assert rejection["decision"] == "REJECT_SUPERSEDED_REQUEST"
    assert rejection["old_frame_set_restored"] is False


def test_both_completion_orders_converge_without_rollback() -> None:
    packet = build_authored_synthetic_fresh_generation_packet()
    traces = packet["completion_order_traces"]

    assert {item["completion_order"] for item in traces} == {
        "OLDER_THEN_NEWER",
        "NEWER_THEN_OLDER",
    }
    assert all(
        item["final_frame_set_digest"] == packet["new_frame_set"][
            "frame_set_digest"
        ]
        for item in traces
    )
    assert all(item["rollback_occurred"] is False for item in traces)
    assert all(item["old_frame_set_restored"] is False for item in traces)


def test_old_generation_remains_byte_identical_retired_and_distinct() -> None:
    trace = build_authored_synthetic_fresh_generation_packet()[
        "old_generation_immutability_trace"
    ]

    assert trace["old_frame_set_bytes_before"] == trace[
        "old_frame_set_bytes_after"
    ]
    assert trace["old_frame_set_bytes_unchanged"] is True
    assert trace["old_generation_state"] == "RETIRED"
    assert trace["distinct_generation"] is True
    assert trace["old_frame_set_restored"] is False


def test_recursively_unknown_key_blocks_even_when_parent_is_resealed() -> None:
    packet = build_authored_synthetic_fresh_generation_packet()
    packet["fresh_generation_admission"]["callback"] = "run_read"
    _reseal(packet["fresh_generation_admission"], "admission_digest")

    _blocked(packet)
    with pytest.raises(FreshGenerationViolation, match="closed_keys_mismatch"):
        validate_fresh_generation_packet(packet)


def test_python_bool_as_integer_blocks_even_when_trace_is_resealed() -> None:
    packet = build_authored_synthetic_fresh_generation_packet()
    packet["fresh_generation_admission"]["current_request_revision"] = True
    _reseal(packet["fresh_generation_admission"], "admission_digest")

    _blocked(packet)
    with pytest.raises(FreshGenerationViolation, match="closed_type_mismatch"):
        validate_fresh_generation_packet(packet)


@pytest.mark.parametrize(
    ("path", "value", "digest_field"),
    [
        (
            ("authority_trace", "grant_no_wider"),
            False,
            "authority_trace_digest",
        ),
        (
            ("required_dependency_refresh_trace", "complete_coverage"),
            False,
            "refresh_trace_digest",
        ),
        (
            ("required_dependency_refresh_trace", "event_metadata_used_as_context"),
            True,
            "refresh_trace_digest",
        ),
        (
            ("carry_forward_trace", "all_eligible"),
            False,
            "carry_forward_trace_digest",
        ),
        (
            ("fresh_generation_admission", "admission_decision"),
            "BLOCK",
            "admission_digest",
        ),
        (
            ("older_result_rejection", "decision"),
            "ADMIT_NEW_GENERATION",
            "reassembly_decision_digest",
        ),
        (
            ("old_generation_immutability_trace", "old_frame_set_bytes_unchanged"),
            False,
            "immutability_trace_digest",
        ),
    ],
)
def test_resealed_authority_refresh_carry_admission_or_rollback_tamper_blocks(
    path: tuple[str, str], value: object, digest_field: str
) -> None:
    packet = build_authored_synthetic_fresh_generation_packet()
    target = packet[path[0]]
    target[path[1]] = value
    _reseal(target, digest_field)

    _blocked(packet)


def test_expiry_blocks_atomic_release() -> None:
    packet = build_authored_synthetic_fresh_generation_packet()
    _blocked(packet, checked_at=packet["new_frame_set"]["expires_at"])


def test_all_product_runtime_execution_provider_and_command_flags_are_false() -> None:
    packet = build_authored_synthetic_fresh_generation_packet()
    false_flags = {
        "product_read_executed",
        "source_read_executed",
        "listener_mounted",
        "runtime_state_mounted",
        "filesystem_effects",
        "network_effects",
        "database_effects",
        "subprocess_effects",
        "persistence_used",
        "command_authority",
        "command_executed",
        "provider_authority",
        "provider_called",
    }

    assert all(packet[field] is False for field in false_flags)
    assert packet["read_only"] is True


def test_module_has_no_product_network_database_subprocess_or_effect_surface() -> None:
    tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))
    modules = set()
    calls = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name.split(".", 1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module.split(".", 1)[0])
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                calls.add(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                calls.add(node.func.attr)
    assert not modules.intersection(
        {
            "app",
            "boto3",
            "google",
            "httpx",
            "os",
            "pathlib",
            "requests",
            "socket",
            "sqlalchemy",
            "subprocess",
        }
    )
    assert not calls.intersection(
        {
            "Popen",
            "commit",
            "connect",
            "execute",
            "open",
            "request",
            "run",
            "write_bytes",
            "write_text",
        }
    )


def test_committed_packet_and_evidence_reproduce_exactly() -> None:
    packet, evidence = build_acceptance_evidence()

    assert packet == _json(
        CONTINUITY_DIR / "authored-synthetic-fresh-generation-packet.json"
    )
    assert evidence == _json(
        CONTINUITY_DIR / "provider-free-acceptance-evidence.json"
    )
    assert evidence["case_count"] == evidence["passed_case_count"] == 45
    evidence_schema = _json(CONTINUITY_DIR / "acceptance-evidence.schema.json")
    assert list(Draft202012Validator(evidence_schema).iter_errors(evidence)) == []
    assert (
        _json(CONTINUITY_DIR / "fresh-generation-packet.schema.json")
        == FRESH_GENERATION_PACKET_SCHEMA
    )


def test_committed_artifact_hashes_match_direct_bytes() -> None:
    evidence = _json(CONTINUITY_DIR / "provider-free-acceptance-evidence.json")
    root = CONTINUITY_DIR.parents[2]
    expected_paths = {
        "fresh_generation_module": root
        / "scripts"
        / "raisa_provider_free_unmounted_rayleen_waiting_room_context_fabric_fresh_generation_rehearsal.py",
        "invalidation_seam_module": root
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
        "fresh_generation_packet_schema": CONTINUITY_DIR
        / "fresh-generation-packet.schema.json",
        "acceptance_evidence_schema": CONTINUITY_DIR
        / "acceptance-evidence.schema.json",
    }
    assert evidence["artifact_hashes"] == {
        name: _sha256(path) for name, path in expected_paths.items()
    }
