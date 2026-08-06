from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, FormatChecker

from scripts.raisa_provider_free_practice_context_fabric_bureau_memory_contract import (
    canonical_json,
    seal,
)
from scripts.raisa_provider_free_practice_context_fabric_current_operational_weave import (
    assemble_current_operational_weave,
    build_authored_synthetic_packet,
    build_operational_context_need,
    intersect_operational_scope,
    proofread_current_operational_weave,
)
from scripts.raisa_provider_free_unmounted_rayleen_waiting_room_context_fabric_source_adapter import (
    ALIAS_MANIFEST_SCHEMA,
    EVIDENCE_LABEL,
    WaitingRoomSourceAdapterViolation,
    adapt_waiting_room_source,
    build_authored_synthetic_alias_manifest,
    build_authored_synthetic_waiting_room_frame,
)
from scripts.raisa_provider_free_unmounted_rayleen_waiting_room_context_fabric_source_adapter_acceptance import (
    ASSEMBLED_AT,
    build_acceptance_evidence,
)


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_ROOT = (
    ROOT
    / "orchestration"
    / "continuity"
    / "raisa-provider-free-unmounted-rayleen-waiting-room-context-fabric-source-adapter"
)


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _inputs() -> tuple[dict, dict, dict, dict]:
    packet = build_authored_synthetic_packet()
    frame = build_authored_synthetic_waiting_room_frame()
    manifest = build_authored_synthetic_alias_manifest(
        frame, packet["authority_binding"], packet["scope_grant"]
    )
    return frame, packet["authority_binding"], packet["scope_grant"], manifest


def _adapt() -> dict:
    return adapt_waiting_room_source(*_inputs(), assembled_at=ASSEMBLED_AT)


def _reseal(value: dict, digest_field: str) -> None:
    replacement = seal({k: v for k, v in value.items() if k != digest_field}, digest_field)
    value.clear()
    value.update(replacement)


def _replace_waiting_source(packet: dict, envelope: dict) -> list[dict]:
    return [
        envelope if item["frame_type"] == "current_waiting_room_projection" else item
        for item in packet["source_envelopes"]
    ]


def test_adapter_releases_one_minimized_exact_current_source() -> None:
    frame, binding, grant, manifest = _inputs()
    result = adapt_waiting_room_source(
        frame, binding, grant, manifest, assembled_at=ASSEMBLED_AT
    )

    assert result["release_decision"] == "RELEASE"
    assert result["evidence_label"] == EVIDENCE_LABEL
    assert result["read_only"] is True
    assert result["command_authority"] is False
    assert result["provider_authority"] is False
    envelope = result["source_envelope"]
    assert (
        envelope["frame_type"],
        envelope["source_class"],
        envelope["source_contract_id"],
    ) == (
        "current_waiting_room_projection",
        "current_waiting_room",
        "emr4.waiting_room_context_frame.v1",
    )
    assert envelope["payload"]["entries"] == [
        {
            "appointment_ref": "synthetic:appointment:one",
            "practitioner_ref": "synthetic:practitioner:one",
            "status": "ARRIVED",
            "elapsed_wait_minutes": 10,
            "threshold_code": "UNDER_15_MINUTES",
            "longest_wait_rank": 1,
        }
    ]


def test_adapter_output_contains_no_source_identity_or_patient_token() -> None:
    frame, binding, grant, manifest = _inputs()
    released = canonical_json(
        adapt_waiting_room_source(
            frame, binding, grant, manifest, assembled_at=ASSEMBLED_AT
        )
    ).casefold()
    forbidden = {
        frame["frame_id"],
        frame["practice_id"],
        frame["location_id"],
        *(fact["appointment_id"] for fact in frame["backend_facts"]),
        *(fact["practitioner_id"] for fact in frame["backend_facts"]),
        *(fact["patient_display_token"] for fact in frame["backend_facts"]),
        *(
            fact["waiting_area_id"]
            for fact in frame["backend_facts"]
            if fact["waiting_area_id"] is not None
        ),
        *(fact["scheduled_at"] for fact in frame["backend_facts"]),
        *(
            fact["arrived_at"]
            for fact in frame["backend_facts"]
            if fact["arrived_at"] is not None
        ),
        *(source for fact in frame["backend_facts"] for source in fact["label"]["source_ids"]),
    }
    assert all(value.casefold() not in released for value in forbidden)


def test_adapter_source_replaces_only_waiting_envelope_and_parent_proofreader_releases() -> None:
    packet = build_authored_synthetic_packet()
    result = _adapt()
    sources = _replace_waiting_source(packet, result["source_envelope"])
    frame_set, source_trace, weave_trace = assemble_current_operational_weave(
        packet["candidate"],
        packet["context_need"],
        packet["authority_binding"],
        packet["scope_grant"],
        sources,
        assembled_at=ASSEMBLED_AT,
    )
    proofreader = proofread_current_operational_weave(
        packet["candidate"],
        packet["context_need"],
        packet["authority_binding"],
        packet["scope_grant"],
        sources,
        frame_set,
        source_trace,
        weave_trace,
        assembled_at=ASSEMBLED_AT,
    )

    assert proofreader["release_decision"] == "RELEASE"
    assert [source["frame_type"] for source in sources] == [
        "current_diary_projection",
        "current_waiting_room_projection",
        "active_practitioner_directory",
        "private_application_session_state",
    ]
    waiting = next(
        frame
        for frame in frame_set["frames"]
        if frame["frame_type"] == "current_waiting_room_projection"
    )
    assert waiting["content"]["entries"][0]["elapsed_wait_minutes"] == 10


def test_missing_arrival_remains_explicit_and_optional_values_are_not_invented() -> None:
    packet = build_authored_synthetic_packet()
    candidate = deepcopy(packet["candidate"])
    candidate["requested_fields"] = [
        field
        for field in candidate["requested_fields"]
        if field not in {"waiting_elapsed_minutes", "waiting_threshold_code"}
    ]
    _reseal(candidate, "candidate_digest")
    binding = packet["authority_binding"]
    context_need = build_operational_context_need(
        candidate, binding, assembled_at=ASSEMBLED_AT
    )
    grant = intersect_operational_scope(
        candidate, context_need, binding, assembled_at=ASSEMBLED_AT
    )
    frame = build_authored_synthetic_waiting_room_frame()
    fact = frame["backend_facts"][0]
    fact["arrived_at"] = None
    label = deepcopy(fact["label"])
    frame["derived_signals"] = [
        {
            "kind": "flow_exception",
            "appointment_id": fact["appointment_id"],
            "value": "missing_arrival_timestamp",
            "derived_by": "deterministic_projection_engine",
            "label": label,
        }
    ]
    manifest = build_authored_synthetic_alias_manifest(frame, binding, grant)
    result = adapt_waiting_room_source(
        frame, binding, grant, manifest, assembled_at=ASSEMBLED_AT
    )
    entry = result["source_envelope"]["payload"]["entries"][0]
    assert entry["flow_exception_code"] == "MISSING_ARRIVAL_TIMESTAMP"
    assert "elapsed_wait_minutes" not in entry
    assert "threshold_code" not in entry

    sources = _replace_waiting_source(packet, result["source_envelope"])
    frame_set, source_trace, weave_trace = assemble_current_operational_weave(
        candidate,
        context_need,
        binding,
        grant,
        sources,
        assembled_at=ASSEMBLED_AT,
    )
    proofreader = proofread_current_operational_weave(
        candidate,
        context_need,
        binding,
        grant,
        sources,
        frame_set,
        source_trace,
        weave_trace,
        assembled_at=ASSEMBLED_AT,
    )
    assert proofreader["release_decision"] == "RELEASE"
    waiting = next(
        item
        for item in frame_set["frames"]
        if item["frame_type"] == "current_waiting_room_projection"
    )
    projected = waiting["content"]["entries"][0]
    assert "elapsed_wait_minutes" not in projected
    assert "threshold_code" not in projected


@pytest.mark.parametrize(
    ("mutator", "reason"),
    [
        (lambda frame: frame.__setitem__("unexpected", True), "source_schema_invalid"),
        (
            lambda frame: frame["derived_signals"][0].__setitem__("value", 99),
            "source_signal_not_grounded",
        ),
        (
            lambda frame: frame["derived_signals"].append(
                deepcopy(frame["derived_signals"][0])
            ),
            "duplicate_source_signal",
        ),
        (
            lambda frame: frame["derived_signals"][0].__setitem__(
                "appointment_id", "22000000-0000-4000-8000-000000000001"
            ),
            "orphan_source_signal",
        ),
        (
            lambda frame: frame.__setitem__(
                "expires_at", "2026-08-06T03:02:31Z"
            ),
            "source_ttl_invalid",
        ),
    ],
)
def test_source_schema_and_signal_tamper_fail_closed(mutator, reason: str) -> None:
    frame, binding, grant, manifest = _inputs()
    mutator(frame)
    with pytest.raises(WaitingRoomSourceAdapterViolation, match=reason):
        adapt_waiting_room_source(
            frame, binding, grant, manifest, assembled_at=ASSEMBLED_AT
        )


def test_binding_grant_and_alias_authority_tamper_fail_closed() -> None:
    frame, binding, grant, manifest = _inputs()
    binding["roles"] = ["GP"]
    _reseal(binding, "binding_digest")
    with pytest.raises(WaitingRoomSourceAdapterViolation, match="grant_binding_mismatch"):
        adapt_waiting_room_source(
            frame, binding, grant, manifest, assembled_at=ASSEMBLED_AT
        )

    frame, binding, grant, manifest = _inputs()
    grant["command_authority"] = True
    _reseal(grant, "grant_digest")
    with pytest.raises(WaitingRoomSourceAdapterViolation, match="adapter_authority_invalid"):
        adapt_waiting_room_source(
            frame, binding, grant, manifest, assembled_at=ASSEMBLED_AT
        )

    frame, binding, grant, manifest = _inputs()
    manifest["appointment_aliases"] = []
    _reseal(manifest, "alias_manifest_digest")
    with pytest.raises(WaitingRoomSourceAdapterViolation, match="alias_manifest_not_complete"):
        adapt_waiting_room_source(
            frame, binding, grant, manifest, assembled_at=ASSEMBLED_AT
        )


def test_alias_manifest_schema_is_recursively_closed() -> None:
    frame, binding, grant, manifest = _inputs()
    manifest["appointment_aliases"][0]["extra"] = True
    errors = list(
        Draft202012Validator(
            ALIAS_MANIFEST_SCHEMA, format_checker=FormatChecker()
        ).iter_errors(manifest)
    )
    assert errors
    with pytest.raises(
        WaitingRoomSourceAdapterViolation, match="alias_manifest_schema_invalid"
    ):
        adapt_waiting_room_source(
            frame, binding, grant, manifest, assembled_at=ASSEMBLED_AT
        )


def test_output_expiry_is_minimum_and_byte_limit_is_enforced() -> None:
    frame, binding, grant, manifest = _inputs()
    manifest["expires_at"] = "2026-08-06T03:00:30Z"
    _reseal(manifest, "alias_manifest_digest")
    result = adapt_waiting_room_source(
        frame, binding, grant, manifest, assembled_at=ASSEMBLED_AT
    )
    assert result["source_envelope"]["expires_at"] == "2026-08-06T03:00:30Z"

    frame, binding, grant, manifest = _inputs()
    manifest["maximum_output_bytes"] = 1024
    _reseal(manifest, "alias_manifest_digest")
    with pytest.raises(
        WaitingRoomSourceAdapterViolation,
        match="adapter_output_byte_limit_exceeded",
    ):
        adapt_waiting_room_source(
            frame, binding, grant, manifest, assembled_at=ASSEMBLED_AT
        )


def test_committed_fixture_and_acceptance_evidence_are_reproducible_and_closed() -> None:
    frame, evidence = build_acceptance_evidence()
    assert _json(ARTIFACT_ROOT / "authored-synthetic-waiting-room-frame.json") == frame
    assert _json(ARTIFACT_ROOT / "provider-free-acceptance-evidence.json") == evidence
    schema = _json(ARTIFACT_ROOT / "adapter-result.schema.json")
    assert not list(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(
            evidence
        )
    )
    assert evidence["case_count"] == evidence["passed_case_count"] == 13
    assert all(value == 0 for value in evidence["zero_action_posture"].values())


def test_adapter_has_no_product_runtime_or_provider_dependency() -> None:
    source = (
        ROOT
        / "scripts"
        / "raisa_provider_free_unmounted_rayleen_waiting_room_context_fabric_source_adapter.py"
    ).read_text(encoding="utf-8")
    forbidden = [
        "app.services.diary.rayleen_waiting_room_projection",
        "sqlalchemy",
        "requests.",
        "httpx",
        "subprocess",
        "vertex",
        "generateContent",
        "@router",
    ]
    assert all(token not in source for token in forbidden)
