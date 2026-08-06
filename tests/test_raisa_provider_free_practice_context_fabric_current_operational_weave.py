from __future__ import annotations

import ast
import json
from copy import deepcopy
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, FormatChecker

from scripts.raisa_provider_free_practice_context_fabric_bureau_memory_contract import (
    seal,
)
from scripts.raisa_provider_free_practice_context_fabric_current_operational_weave import (
    FRAME_ORDER,
    OperationalWeaveViolation,
    assemble_current_operational_weave,
    build_operational_context_need,
    intersect_operational_scope,
    proofread_current_operational_weave,
)
from scripts.raisa_provider_free_practice_context_fabric_current_operational_weave_acceptance import (
    DESIGN_PATH,
    ENGINE_PATH,
    EVIDENCE_PATH,
    EXAMPLE_PATH,
    PLAN_PATH,
    RESULT,
    SCHEMA_PATH,
    THREAT_PATH,
    build_evidence,
    build_example,
)


ROOT = Path(__file__).resolve().parents[1]
ASSEMBLED_AT = "2026-08-06T03:00:00Z"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _errors(instance: dict) -> list:
    return list(
        Draft202012Validator(
            _load(SCHEMA_PATH), format_checker=FormatChecker()
        ).iter_errors(instance)
    )


def _reseal(value: dict, field: str) -> dict:
    value.pop(field, None)
    return seal(value, field)


def _inputs(packet: dict) -> tuple[dict, dict, dict, dict, list[dict]]:
    return (
        packet["candidate"],
        packet["context_need"],
        packet["authority_binding"],
        packet["scope_grant"],
        packet["source_envelopes"],
    )


def _replace_source(sources: list[dict], replacement: dict) -> list[dict]:
    return [
        replacement if item["frame_type"] == replacement["frame_type"] else item
        for item in sources
    ]


def test_nominal_packet_and_committed_example_validate() -> None:
    schema = _load(SCHEMA_PATH)
    Draft202012Validator.check_schema(schema)
    packet = build_example()
    assert _errors(packet) == []
    assert _load(EXAMPLE_PATH) == packet
    assert packet["scope_grant"]["decision"] == "ADMIT"
    assert packet["proofreader_trace"]["release_decision"] == "RELEASE"
    assert [item["frame_type"] for item in packet["frame_set"]["frames"]] == list(
        FRAME_ORDER
    )


def test_evidence_passes_with_canonical_external_head_binding() -> None:
    evidence = build_evidence()
    assert evidence["result"] == RESULT
    assert evidence["passed"] is True
    assert evidence["source_binding"] == {
        "mode": "canonical_lf_artifact_hashes_with_external_exact_head_receipt",
        "artifact_count": 7,
        "git_head_self_reference_forbidden": True,
        "checkout_line_endings_normalized": True,
    }
    assert "source_head" not in evidence
    assert set(evidence["authority_and_side_effects"].values()) == {0}
    assert _load(EVIDENCE_PATH) == evidence


def test_candidate_is_closed_and_cannot_supply_backend_authority() -> None:
    candidate = _load(SCHEMA_PATH)["$defs"]["Candidate"]
    assert candidate["additionalProperties"] is False
    assert not set(candidate["properties"]).intersection(
        {
            "principal_ref",
            "practice_id",
            "session_id",
            "roles",
            "authority_binding",
            "consent_codes",
            "retention_days",
        }
    )
    packet = build_example()
    packet["candidate"]["practice_id"] = "synthetic:practice:attacker"
    packet["candidate"] = _reseal(packet["candidate"], "candidate_digest")
    assert _errors(packet)


def test_scope_intersection_only_narrows_every_policy_dimension() -> None:
    packet = build_example()
    candidate = packet["candidate"]
    grant = packet["scope_grant"]
    assert set(grant["allowed_frame_types"]).issubset(
        candidate["requested_frame_types"]
    )
    assert set(grant["allowed_source_classes"]).issubset(
        candidate["source_classes"]
    )
    assert set(grant["required_source_classes"]).issubset(
        candidate["required_source_classes"]
    )
    assert set(grant["allowed_fields"]).issubset(candidate["requested_fields"])
    assert set(grant["allowed_location_refs"]).issubset(
        candidate["requested_location_refs"]
    )
    assert grant["maximum_frames"] <= candidate["maximum_frames"]
    assert grant["maximum_items_per_frame"] <= candidate["maximum_items_per_frame"]
    assert grant["maximum_total_bytes"] <= candidate["maximum_total_bytes"]
    assert grant["freshness_seconds"] <= candidate["freshness_seconds"]
    assert {
        "TIME_WINDOW_NARROWED",
        "ITEM_LIMIT_NARROWED",
        "BYTE_LIMIT_NARROWED",
        "FRESHNESS_NARROWED",
    } <= set(grant["scope_reduction_codes"])


def test_out_of_scope_bureau_returns_uniform_not_available() -> None:
    packet = build_example()
    binding = deepcopy(packet["authority_binding"])
    binding["allowed_bureaus"] = ["DAVIDA"]
    binding = _reseal(binding, "binding_digest")
    need = build_operational_context_need(
        packet["candidate"], binding, assembled_at=ASSEMBLED_AT
    )
    grant = intersect_operational_scope(
        packet["candidate"], need, binding, assembled_at=ASSEMBLED_AT
    )
    assert grant["decision"] == "NOT_AVAILABLE"
    assert grant["allowed_frame_types"] == []
    assert grant["allowed_fields"] == []
    assert grant["maximum_total_bytes"] == 0
    assert grant["scope_reduction_codes"] == ["SCOPE_NOT_AVAILABLE"]


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        ("practice", "source_practice_mismatch"),
        ("session", "source_session_mismatch"),
        ("location", "source_location_not_granted"),
        ("stale", "source_stale"),
        ("expired", "source_expired"),
        ("superseded", "source_superseded"),
        ("pairing", "source_contract_pairing_invalid"),
    ],
)
def test_hostile_source_substitution_or_age_fails_closed(
    mutation: str, message: str
) -> None:
    packet = build_example()
    sources = deepcopy(packet["source_envelopes"])
    grant = packet["scope_grant"]
    target = sources[0]
    if mutation == "practice":
        target["practice_id"] = "synthetic:practice:other"
    elif mutation == "session":
        target["session_binding_digest"] = "sha256:" + "0" * 64
    elif mutation == "location":
        target["location_refs"] = ["synthetic:location:other"]
    elif mutation == "stale":
        target["observed_at"] = "2026-08-06T02:59:00Z"
        target["expires_at"] = "2026-08-06T03:02:00Z"
        grant = deepcopy(grant)
        grant["freshness_seconds"] = 30
        grant = _reseal(grant, "grant_digest")
    elif mutation == "expired":
        target["expires_at"] = ASSEMBLED_AT
    elif mutation == "superseded":
        target["supersession_state"] = "SUPERSEDED"
    elif mutation == "pairing":
        target["source_contract_id"] = "emr4.waiting_room_context_frame.v1"
    sources[0] = _reseal(target, "source_digest")
    with pytest.raises(OperationalWeaveViolation, match=message):
        assemble_current_operational_weave(
            packet["candidate"],
            packet["context_need"],
            packet["authority_binding"],
            grant,
            sources,
            assembled_at=ASSEMBLED_AT,
        )


def test_missing_and_duplicate_required_sources_fail_closed() -> None:
    packet = build_example()
    sources = packet["source_envelopes"]
    with pytest.raises(OperationalWeaveViolation, match="required_source_missing"):
        assemble_current_operational_weave(
            *_inputs(packet)[:4], sources[:-1], assembled_at=ASSEMBLED_AT
        )
    with pytest.raises(OperationalWeaveViolation, match="duplicate_source_frame"):
        assemble_current_operational_weave(
            *_inputs(packet)[:4], [*sources, sources[0]], assembled_at=ASSEMBLED_AT
        )


@pytest.mark.parametrize(
    ("frame_type", "path", "value", "message"),
    [
        (
            "current_waiting_room_projection",
            ("payload", "entries", 0, "appointment_ref"),
            "synthetic:appointment:missing",
            "waiting_appointment_not_in_diary",
        ),
        (
            "current_diary_projection",
            ("payload", "appointments", 0, "practitioner_ref"),
            "synthetic:practitioner:missing",
            "practitioner_not_in_active_directory",
        ),
        (
            "private_application_session_state",
            ("payload", "visible_diary_date"),
            "2026-08-07",
            "session_visible_diary_mismatch",
        ),
        (
            "private_application_session_state",
            ("payload", "focus_appointment_ref"),
            "synthetic:appointment:missing",
            "session_focus_not_in_diary",
        ),
    ],
)
def test_cross_source_incoherence_fails_closed(
    frame_type: str, path: tuple, value: str, message: str
) -> None:
    packet = build_example()
    target = deepcopy(
        next(item for item in packet["source_envelopes"] if item["frame_type"] == frame_type)
    )
    cursor = target
    for key in path[:-1]:
        cursor = cursor[key]
    cursor[path[-1]] = value
    target = _reseal(target, "source_digest")
    sources = _replace_source(deepcopy(packet["source_envelopes"]), target)
    with pytest.raises(OperationalWeaveViolation, match=message):
        assemble_current_operational_weave(
            *_inputs(packet)[:4], sources, assembled_at=ASSEMBLED_AT
        )


def test_backend_field_policy_removes_ungranted_optional_disclosure() -> None:
    packet = build_example()
    binding = deepcopy(packet["authority_binding"])
    binding["allowed_fields"] = [
        "diary_status",
        "waiting_status",
        "session_visible_diary",
    ]
    binding = _reseal(binding, "binding_digest")
    need = build_operational_context_need(
        packet["candidate"], binding, assembled_at=ASSEMBLED_AT
    )
    grant = intersect_operational_scope(
        packet["candidate"], need, binding, assembled_at=ASSEMBLED_AT
    )
    frame_set, _, _ = assemble_current_operational_weave(
        packet["candidate"],
        need,
        binding,
        grant,
        packet["source_envelopes"],
        assembled_at=ASSEMBLED_AT,
    )
    diary = frame_set["frames"][0]["content"]["appointments"][0]
    waiting = frame_set["frames"][1]["content"]["entries"][0]
    directory = frame_set["frames"][2]["content"]["practitioners"][0]
    session = frame_set["frames"][3]["content"]
    assert set(diary) == {"appointment_ref", "status"}
    assert set(waiting) == {"appointment_ref", "status"}
    assert set(directory) == {"practitioner_ref", "active"}
    assert set(session) == {
        "session_generation",
        "request_revision",
        "supersession_state",
        "visible_diary_date",
        "visible_location_ref",
    }


def test_same_packet_tamper_and_expiry_block_atomic_release() -> None:
    packet = build_example()
    tampered = deepcopy(packet["frame_set"])
    tampered["frames"][0]["content"]["appointments"][0]["status"] = "COMPLETED"
    trace = proofread_current_operational_weave(
        *_inputs(packet),
        tampered,
        packet["source_trace"],
        packet["weave_trace"],
        assembled_at=ASSEMBLED_AT,
    )
    assert trace["release_decision"] == "BLOCK"
    assert any("PACKET_INVALID" in item for item in trace["reason_codes"])

    expired = proofread_current_operational_weave(
        *_inputs(packet),
        packet["frame_set"],
        packet["source_trace"],
        packet["weave_trace"],
        assembled_at=ASSEMBLED_AT,
        proofread_at="2026-08-06T03:02:00Z",
    )
    assert expired["release_decision"] == "BLOCK"
    assert "FRAME_SET_EXPIRED" in expired["reason_codes"]


def test_engine_has_no_product_or_side_effect_surface() -> None:
    tree = ast.parse(ENGINE_PATH.read_text(encoding="utf-8"))
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


def test_artifacts_are_repository_local_and_exclude_branding() -> None:
    paths = [
        SCHEMA_PATH,
        EXAMPLE_PATH,
        EVIDENCE_PATH,
        PLAN_PATH,
        DESIGN_PATH,
        THREAT_PATH,
        ENGINE_PATH,
        Path(__file__),
    ]
    windows_profile_prefix = "C:" + "\\Users\\"
    posix_profile_prefix = "C:" + "/Users/"
    for path in paths:
        assert path.is_file()
        assert ROOT in path.parents
        assert not path.is_relative_to(ROOT / "docs/branding")
        text = path.read_text(encoding="utf-8")
        assert windows_profile_prefix not in text
        assert posix_profile_prefix not in text
