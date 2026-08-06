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
    build_authored_synthetic_packet,
)
from scripts.raisa_provider_free_practice_context_fabric_patient_free_temporal_weave import (
    TemporalWeaveViolation,
    assess_reassembly_result,
    build_authored_synthetic_temporal_packet,
    build_historical_candidate,
    build_historical_policy,
    derive_dependency_manifest,
    derive_watch_lease,
    make_signal,
    process_signals,
    proofread_temporal_packet,
    select_historical_snapshots,
)
from scripts.raisa_provider_free_practice_context_fabric_patient_free_temporal_weave_acceptance import (
    ACCEPTANCE_PATH,
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


def _parent_manifest_lease() -> tuple[dict, dict, dict]:
    parent = build_authored_synthetic_packet()
    manifest = derive_dependency_manifest(parent)
    return parent, manifest, derive_watch_lease(parent, manifest)


def _signal(
    manifest: dict,
    *,
    signal_id: str = "synthetic:signal:test",
    revision: int = 12,
    previous_position: int = 100,
    position: int = 101,
    aggregate_ref: str = "synthetic:appointment:one",
    location: str = "synthetic:location:brisbane-one",
) -> dict:
    return make_signal(
        signal_id=signal_id,
        event_type="diary.appointment_rescheduled",
        aggregate_ref=aggregate_ref,
        aggregate_revision=revision,
        previous_transaction_position=previous_position,
        transaction_position=position,
        location_refs=[location],
        practitioner_refs=["synthetic:practitioner:one"],
        practice_binding_digest=manifest["practice_binding_digest"],
        occurred_at="2026-08-06T03:00:10Z",
        received_at="2026-08-06T03:00:11Z",
    )


def test_nominal_packet_and_committed_example_validate() -> None:
    schema = _load(SCHEMA_PATH)
    Draft202012Validator.check_schema(schema)
    packet = build_example()
    assert _errors(packet) == []
    assert _load(EXAMPLE_PATH) == packet
    assert packet["proofreader_trace"]["release_decision"] == "RELEASE"
    assert [item["decision"] for item in packet["invalidation_decisions"]] == [
        "REASSEMBLY_REQUIRED",
        "COALESCED",
        "IRRELEVANT",
    ]


def test_relevant_signal_invalidates_without_mutating_parent_and_coalesces() -> None:
    parent = build_authored_synthetic_packet()
    before = deepcopy(parent["frame_set"])
    packet = build_authored_synthetic_temporal_packet()
    assert parent["frame_set"] == before
    assert packet["frame_set_state"]["state"] == "REASSEMBLY_REQUIRED"
    assert packet["frame_set_state"]["usable_for_new_reasoning"] is False
    assert packet["frame_set_state"]["frames_mutated"] is False
    requirement = packet["reassembly_requirement"]
    assert requirement["execution_enabled"] is False
    assert requirement["returns_data"] is False
    assert len(requirement["cause_signal_digests"]) == 2
    assert len(packet["watcher_transitions"]) == len(packet["signals"])
    assert packet["watcher_transitions"][0][
        "reassembly_requirement_emitted"
    ] is True
    assert all(
        transition["fresh_read_executed"] is False
        for transition in packet["watcher_transitions"]
    )


def test_signal_payload_smuggling_is_closed_by_schema_and_engine() -> None:
    parent, manifest, lease = _parent_manifest_lease()
    signal = _signal(manifest)
    signal["payload"] = {"replacement_status": "COMPLETED"}
    signal = _reseal(signal, "signal_digest")
    packet = build_authored_synthetic_temporal_packet()
    packet["signals"][0] = signal
    assert _errors(packet)
    with pytest.raises(TemporalWeaveViolation, match="signal_shape_invalid"):
        process_signals(parent, manifest, lease, [signal])


def test_exact_replay_and_equal_revision_are_suppressed() -> None:
    parent, manifest, lease = _parent_manifest_lease()
    equal = _signal(manifest, signal_id="synthetic:signal:equal", revision=11)
    replay = _signal(
        manifest,
        signal_id="synthetic:signal:replay",
        revision=12,
        position=101,
    )
    _, _, _, decisions, _, _ = process_signals(
        parent, manifest, lease, [replay, replay]
    )
    assert [item["reason_codes"] for item in decisions] == [
        ["DEPENDENCY_MAY_BE_STALE"],
        ["EXACT_REPLAY"],
    ]
    state, requirement, _, decisions, _, _ = process_signals(
        parent, manifest, lease, [equal]
    )
    assert decisions[0]["decision"] == "SUPPRESSED"
    assert decisions[0]["reason_codes"] == ["REVISION_NOT_NEWER"]
    assert state["state"] == "CURRENT"
    assert requirement is None


def test_foreign_practice_and_unrelated_scope_are_suppressed_or_quiet() -> None:
    parent, manifest, lease = _parent_manifest_lease()
    foreign = _signal(manifest)
    foreign["practice_binding_digest"] = "sha256:" + "0" * 64
    foreign = _reseal(foreign, "signal_digest")
    state, _, _, decisions, _, _ = process_signals(
        parent, manifest, lease, [foreign]
    )
    assert state["state"] == "CURRENT"
    assert decisions[0]["reason_codes"] == ["FOREIGN_PRACTICE"]

    unrelated = _signal(
        manifest,
        signal_id="synthetic:signal:unrelated",
        revision=1,
        aggregate_ref="synthetic:appointment:outside",
        location="synthetic:location:outside",
    )
    state, _, _, decisions, _, _ = process_signals(
        parent, manifest, lease, [unrelated]
    )
    assert state["state"] == "CURRENT"
    assert decisions[0]["decision"] == "IRRELEVANT"


@pytest.mark.parametrize(
    ("signal", "expected"),
    [
        ({"previous_position": 100, "position": 102, "revision": 12}, "CURSOR_GAP"),
        ({"previous_position": 100, "position": 101, "revision": 14}, "REVISION_GAP"),
        (
            {"previous_position": 99, "position": 100, "revision": 12},
            "ORDERING_UNCERTAIN",
        ),
    ],
)
def test_cursor_revision_and_ordering_gaps_fail_closed(
    signal: dict, expected: str
) -> None:
    parent, manifest, lease = _parent_manifest_lease()
    candidate = _signal(manifest, **signal)
    state, requirement, _, decisions, transitions, _ = process_signals(
        parent, manifest, lease, [candidate]
    )
    assert decisions[0]["decision"] == expected
    assert state["state"] == "REASSEMBLY_REQUIRED"
    assert requirement is not None
    assert set(requirement["required_dependency_ids"]) == set(
        lease["allowed_dependency_ids"]
    )
    assert transitions[0]["decision"] == expected
    assert transitions[0]["fresh_read_executed"] is False


def test_noninitial_rebaseline_fails_closed_after_one_observation() -> None:
    parent, manifest, lease = _parent_manifest_lease()
    first = _signal(manifest)
    second = _signal(
        manifest,
        signal_id="synthetic:signal:rebaseline",
        revision=13,
        previous_position=101,
        position=102,
    )
    second["baseline_established"] = True
    second = _reseal(second, "signal_digest")
    _, requirement, _, decisions, _, _ = process_signals(
        parent, manifest, lease, [first, second]
    )
    assert decisions[1]["decision"] == "CURSOR_GAP"
    assert decisions[1]["reason_codes"] == ["NONINITIAL_REBASELINE"]
    assert requirement is not None


def test_lease_expiry_and_session_generation_change_block_use() -> None:
    parent, manifest, lease = _parent_manifest_lease()
    signal = _signal(manifest)
    state, _, _, decisions, _, _ = process_signals(
        parent, manifest, lease, [signal], observed_at=lease["expires_at"]
    )
    assert state["state"] == "EXPIRED"
    assert decisions[0]["decision"] == "EXPIRED"

    state, _, _, decisions, _, _ = process_signals(
        parent,
        manifest,
        lease,
        [signal],
        current_session_generation=manifest["session_generation"] + 1,
    )
    assert state["state"] == "REVOKED"
    assert decisions[0]["decision"] == "REVOKED"


def test_stale_async_reassembly_cannot_restore_old_set() -> None:
    packet = build_authored_synthetic_temporal_packet()
    requirement = packet["reassembly_requirement"]
    stale = assess_reassembly_result(
        requirement,
        result_session_generation=requirement["session_generation"],
        result_request_revision=1,
        current_session_generation=requirement["session_generation"],
        current_request_revision=2,
    )
    assert stale["decision"] == "REJECT_SUPERSEDED_REQUEST"
    assert stale["old_frame_set_restored"] is False
    current = assess_reassembly_result(
        requirement,
        result_session_generation=requirement["session_generation"],
        result_request_revision=1,
        current_session_generation=requirement["session_generation"],
        current_request_revision=1,
    )
    assert current["decision"] == "ADMIT_NEW_GENERATION"


def test_bitemporal_selection_distinguishes_known_then_and_corrected_later() -> None:
    packet = build_authored_synthetic_temporal_packet()
    results = packet["historical_results"]
    assert [item["frames"][0]["content"]["waiting_count"] for item in results] == [
        2,
        3,
    ]
    assert all(item["current_truth_authority"] is False for item in results)
    assert all(
        item["event_delivery_ttl_controls_retention"] is False for item in results
    )
    assert all(
        frame["current_truth_authority"] is False
        for result in results
        for frame in result["frames"]
    )


def test_explicit_historical_gap_is_not_absence_evidence() -> None:
    packet = build_authored_synthetic_temporal_packet()
    parent_binding = packet["parent_binding"]
    candidate = build_historical_candidate(known_at="2026-08-06T02:30:00Z")
    candidate["valid_at"] = "2026-08-06T02:15:00Z"
    candidate = _reseal(candidate, "candidate_digest")
    result = select_historical_snapshots(
        candidate,
        build_historical_policy(parent_binding),
        packet["historical_snapshots"],
    )
    assert result["disposition"] == "NO_COVERAGE"
    assert result["frames"] == []
    assert result["missing_coverage_is_not_absence_evidence"] is True


def test_historical_lookback_and_field_policy_only_narrow() -> None:
    packet = build_authored_synthetic_temporal_packet()
    candidate = build_historical_candidate(known_at="2026-08-06T01:00:00Z")
    candidate["requested_fields"] = ["waiting_count"]
    candidate = _reseal(candidate, "candidate_digest")
    result = select_historical_snapshots(
        candidate, packet["historical_policy"], packet["historical_snapshots"]
    )
    assert result["disposition"] == "ADMIT"
    assert set(result["frames"][0]["content"]) == {"waiting_count"}

    too_old = deepcopy(candidate)
    too_old["valid_at"] = "2026-08-04T00:30:00Z"
    too_old = _reseal(too_old, "candidate_digest")
    result = select_historical_snapshots(
        too_old, packet["historical_policy"], packet["historical_snapshots"]
    )
    assert result["disposition"] == "NOT_AVAILABLE"
    assert result["frames"] == []


def test_broken_correction_lineage_and_temporal_overlap_fail_closed() -> None:
    packet = build_authored_synthetic_temporal_packet()
    snapshots = deepcopy(packet["historical_snapshots"])
    corrected = snapshots[1]
    corrected["transaction_time"]["starts_at"] = "2026-08-06T01:59:00Z"
    corrected = _reseal(corrected, "snapshot_digest")
    snapshots[1] = corrected
    with pytest.raises(
        TemporalWeaveViolation, match="correction_transaction_gap_or_overlap"
    ):
        select_historical_snapshots(
            packet["historical_candidates"][0], packet["historical_policy"], snapshots
        )


def test_manifest_and_state_tamper_are_blocked() -> None:
    parent, manifest, lease = _parent_manifest_lease()
    tampered_manifest = deepcopy(manifest)
    tampered_manifest["dependencies"][0]["location_refs"] = [
        "synthetic:location:attacker"
    ]
    tampered_manifest["dependencies"][0] = _reseal(
        tampered_manifest["dependencies"][0], "dependency_digest"
    )
    tampered_manifest = _reseal(tampered_manifest, "manifest_digest")
    with pytest.raises(TemporalWeaveViolation, match="manifest_not_parent_derived"):
        process_signals(
            parent, tampered_manifest, lease, [_signal(manifest)]
        )

    packet = build_authored_synthetic_temporal_packet()
    proof_packet = {key: value for key, value in packet.items() if key != "proofreader_trace"}
    proof_packet["frame_set_state"] = deepcopy(proof_packet["frame_set_state"])
    proof_packet["frame_set_state"]["state"] = "CURRENT"
    trace = proofread_temporal_packet(
        parent, proof_packet, checked_at="2026-08-06T03:01:01Z"
    )
    assert trace["release_decision"] == "BLOCK"


def test_candidate_cannot_supply_authority_or_retention_decisions() -> None:
    candidate = _load(SCHEMA_PATH)["$defs"]["HistoricalCandidate"]
    assert candidate["additionalProperties"] is False
    assert not set(candidate["properties"]).intersection(
        {
            "practice_binding_digest",
            "principal_ref",
            "roles",
            "session_id",
            "retention_class",
            "allowed_retention_classes",
            "authority_binding",
        }
    )


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
    assert set(evidence["authority_and_side_effects"].values()) == {0}
    assert _load(EVIDENCE_PATH) == evidence


def test_artifacts_are_repository_local_and_exclude_branding() -> None:
    paths = [
        SCHEMA_PATH,
        EXAMPLE_PATH,
        EVIDENCE_PATH,
        PLAN_PATH,
        DESIGN_PATH,
        THREAT_PATH,
        ENGINE_PATH,
        ACCEPTANCE_PATH,
        Path(__file__),
    ]
    for path in paths:
        assert path.is_file()
        assert ROOT in path.parents
        assert not path.is_relative_to(ROOT / "docs/branding")
        text = path.read_text(encoding="utf-8")
        assert "C:" + "\\Users\\" not in text
        assert "C:" + "/Users/" not in text
