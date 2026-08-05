"""Closed-contract acceptance for the model-required Rayleen A4 selector."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path

import pytest

from scripts import model_required_bureau_a4_selector_contracts as contracts
from scripts import model_required_bureau_a4_selector_live as selector_live


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_ROOT = contracts.ARTIFACT_ROOT


def _context() -> dict[str, object]:
    return contracts.load_object(contracts.CONTEXT_PATH)


def _context_proof_time(context: dict[str, object]) -> datetime:
    return datetime.fromisoformat(
        str(context["evaluation_time"]).replace("Z", "+00:00")
    )


def test_exact_vertex_boundary_preserves_reasoning_and_sydney_binding() -> None:
    request = contracts.build_vertex_request(
        contracts.LANE_RAYLEEN,
        _context(),
    )
    generation = request["generationConfig"]
    assert contracts.PROJECT == "bernie-emr4-dev"
    assert contracts.MODEL == "gemini-2.5-flash"
    assert contracts.LOCATION == "australia-southeast1"
    assert contracts.HOSTNAME == (
        "australia-southeast1-aiplatform.googleapis.com"
    )
    assert generation["thinkingConfig"] == {"thinkingBudget": 1024}
    assert generation["maxOutputTokens"] == 2048
    assert generation["candidateCount"] == 1
    assert generation["temperature"] == 0
    assert "tools" not in request
    assert "cachedContent" not in request


def test_provider_prompt_contains_only_request_scoped_opaque_context() -> None:
    context = _context()
    prompt = contracts.build_prompt(contracts.LANE_RAYLEEN, context)
    source = context["source_response"]["data"]["rayleenWaitingRoom"]
    for forbidden in (
        context["request_scope_salt"],
        source["frameId"],
        source["practiceId"],
        source["locationId"],
        *(item["appointmentId"] for item in source["backendFacts"]),
        *(item["practitionerId"] for item in source["backendFacts"]),
        *(item["patientDisplayToken"] for item in source["backendFacts"]),
    ):
        assert forbidden not in prompt
    bounded = contracts.model_context(context)
    assert bounded["practice_ref"].startswith("practice_")
    assert bounded["location_ref"].startswith("location_")
    assert all(
        item["appointment_ref"].startswith("appointment_")
        and item["practitioner_ref"].startswith("practitioner_")
        and item["waiting_area_ref"].startswith("waiting_area_")
        for item in bounded["facts"]
    )


def test_execution_context_materialization_is_current_two_minute_and_bound() -> None:
    observed = datetime(2026, 8, 5, 1, 2, 3, tzinfo=timezone.utc)
    context = contracts.materialize_execution_context(
        _context(), observed_at=observed
    )
    assert context["generated_at"] == "2026-08-05T01:02:03Z"
    assert context["evaluation_time"] == "2026-08-05T01:02:03Z"
    assert context["expires_at"] == "2026-08-05T01:04:03Z"
    frame = context["source_response"]["data"]["rayleenWaitingRoom"]
    assert frame["generatedAt"] == context["generated_at"]
    assert frame["expiresAt"] == context["expires_at"]
    assert frame["backendFacts"][0]["scheduledAt"] == "2026-08-05T00:17:03Z"
    assert frame["backendFacts"][0]["arrivedAt"] == "2026-08-05T00:22:03Z"
    for item in (*frame["backendFacts"], *frame["derivedSignals"]):
        assert item["label"]["observedAt"] == context["generated_at"]
        assert item["label"]["expiresAt"] == context["expires_at"]
    contracts.validate_rayleen_context(context)


def test_execution_context_requires_aware_time() -> None:
    with pytest.raises(contracts.ContractError, match="observed_at_timezone_required"):
        contracts.materialize_execution_context(
            _context(), observed_at=datetime(2026, 8, 5, 1, 2, 3)
        )


def test_fixture_candidate_is_proofread_to_one_display_only_ui_release() -> None:
    context = _context()
    body = contracts.canonical_model_body_fixture(contracts.LANE_RAYLEEN)
    candidate = contracts.wrap_provider_body(
        contracts.LANE_RAYLEEN,
        body,
        context,
    )
    proof = contracts.proofread(
        contracts.LANE_RAYLEEN,
        candidate,
        context,
        proof_time=_context_proof_time(context),
    )
    assert proof["verdict"] == "admitted"
    release = proof["released"]
    assert release["status"] == "display_projection_only"
    assert release["evidence_mode"] == "proofreader_admitted_display_projection"
    assert all(value is False for value in release["authority_ceiling"].values())
    frame = release["response"]["data"]["rayleenWaitingRoom"]
    assert frame["schemaVersion"] == "emr4.waiting_room_context_frame.v1"
    assert frame["projection"] == {
        "kind": "LONGEST_WAIT",
        "selectedCount": 1,
        "practitionerId": "a4000000-0000-4000-8000-000000000021",
        "waitingAreaId": "a4000000-0000-4000-8000-000000000031",
        "focusAppointmentId": "a4000000-0000-4000-8000-000000000011",
        "selectorProvenance": "model_selected_proofreader_admitted",
        "authorityCeiling": "data_only",
        "writesAuthorized": False,
    }
    assert len(frame["backendFacts"]) == 1
    assert {
        signal["appointmentId"] for signal in frame["derivedSignals"]
    } == {frame["backendFacts"][0]["appointmentId"]}


@pytest.mark.parametrize(
    ("mutation", "reason"),
    (
        (
            lambda value: value.update(
                {"focus_appointment_ref": "appointment_" + "f" * 24}
            ),
            "selector_not_grounded",
        ),
        (
            lambda value: value["authority_ceiling"].update({"write": True}),
            "schema_invalid",
        ),
        (
            lambda value: value.update({"context_revision": 1836412046}),
            "schema_invalid",
        ),
    ),
)
def test_proofreader_rejects_invention_authority_and_stale_revision(
    mutation,
    reason: str,
) -> None:
    context = _context()
    body = deepcopy(
        contracts.canonical_model_body_fixture(contracts.LANE_RAYLEEN)
    )
    mutation(body)
    try:
        candidate = contracts.wrap_provider_body(
            contracts.LANE_RAYLEEN,
            body,
            context,
        )
    except contracts.ContractError as error:
        assert str(error).startswith(reason)
        return
    proof = contracts.proofread(
        contracts.LANE_RAYLEEN,
        candidate,
        context,
        proof_time=_context_proof_time(context),
    )
    assert proof["verdict"] == "rejected"
    assert proof["reason_code"] == reason
    assert proof["released"] is None


def test_response_extractor_rejects_thoughts_extra_parts_and_non_json() -> None:
    body = contracts.canonical_model_body_fixture(contracts.LANE_RAYLEEN)
    packet = {
        "candidates": [
            {
                "content": {
                    "parts": [{"text": json.dumps(body, sort_keys=True)}]
                }
            }
        ]
    }
    assert contracts.extract_provider_candidate(packet) == body
    for invalid in (
        {"candidates": [{"content": {"parts": [{"thought": True, "text": "{}"}]}}]},
        {"candidates": [{"content": {"parts": [{"text": "{}"}, {"text": "{}"}]}}]},
        {"candidates": [{"content": {"parts": [{"text": "not-json"}]}}]},
    ):
        with pytest.raises(contracts.ContractError):
            contracts.extract_provider_candidate(invalid)


def test_grounding_recovery_is_materially_distinct_and_keeps_gate_strict() -> None:
    context = _context()
    request = contracts.provider_request_for_attempt(
        contracts.LANE_RAYLEEN,
        context,
        attempt_number=2,
        correction_reason_code="selector_not_grounded",
    )
    prompt = request["contents"][0]["parts"][0]["text"]
    assert "consider only facts whose status is arrived" in prompt
    assert "choose the unique maximum" in prompt
    assert "from that same fact" in prompt
    assert "must be a singleton" in prompt
    assert "keep every authority value false" in prompt
    assert request["generationConfig"] == contracts.build_vertex_request(
        contracts.LANE_RAYLEEN, context
    )["generationConfig"]
    packet = selector_live._request_packet(
        contracts.LANE_RAYLEEN,
        context,
        attempt_number=2,
        correction_of="a4-rayleen-selector-primary-001",
        correction_reason_code="selector_not_grounded",
    )
    assert packet["attempt_id"] == "a4-rayleen-selector-correction-002"
    assert packet["correction_reason_code"] == "selector_not_grounded"

    invalid = deepcopy(
        contracts.canonical_model_body_fixture(contracts.LANE_RAYLEEN)
    )
    invalid["focus_appointment_ref"] = "appointment_" + "f" * 24
    candidate = contracts.wrap_provider_body(
        contracts.LANE_RAYLEEN, invalid, context
    )
    proof = contracts.proofread(
        contracts.LANE_RAYLEEN,
        candidate,
        context,
        proof_time=_context_proof_time(context),
    )
    assert proof["reason_code"] == "selector_not_grounded"
    assert proof["correction_eligible"] is True
    assert proof["released"] is None

    with pytest.raises(contracts.ContractError, match="correction_not_eligible"):
        contracts.correction_request(
            contracts.LANE_RAYLEEN,
            context,
            "context_not_fresh",
            2,
        )


def test_proofreader_admits_just_before_and_rejects_at_expiry() -> None:
    generated = datetime(2026, 8, 5, 1, 2, 3, tzinfo=timezone.utc)
    context = contracts.materialize_execution_context(
        _context(), observed_at=generated
    )
    body = contracts.canonical_model_body_fixture(contracts.LANE_RAYLEEN)
    candidate = contracts.wrap_provider_body(
        contracts.LANE_RAYLEEN, body, context
    )
    just_before = generated + timedelta(minutes=2, microseconds=-1)
    at_expiry = generated + timedelta(minutes=2)
    admitted = contracts.proofread(
        contracts.LANE_RAYLEEN,
        candidate,
        context,
        proof_time=just_before,
    )
    rejected = contracts.proofread(
        contracts.LANE_RAYLEEN,
        candidate,
        context,
        proof_time=at_expiry,
    )
    assert admitted["verdict"] == "admitted"
    assert rejected["verdict"] == "rejected"
    assert rejected["reason_code"] == "context_not_fresh"
    assert rejected["released"] is None


def test_cost_and_attempt_schemas_are_one_lane_two_call_fail_closed() -> None:
    cost = contracts.load_object(contracts.ARTIFACT_ROOT / "cost-ledger.schema.json")
    attempt = contracts.load_object(
        contracts.ARTIFACT_ROOT / "single-use-ledger.schema.json"
    )
    assert cost["properties"]["maximum_provider_calls"]["const"] == 2
    assert cost["properties"]["maximum_cost_usd"]["const"] == 0.5
    assert set(cost["properties"]["lane_calls"]["properties"]) == {
        contracts.LANE_RAYLEEN
    }
    assert attempt["properties"]["fallback_permitted"]["const"] is False


def test_a4_runner_builds_exact_single_lane_packets_and_ledgers() -> None:
    context = _context()
    packet = selector_live._request_packet(
        contracts.LANE_RAYLEEN,
        context,
        attempt_number=1,
        correction_of=None,
        correction_reason_code=None,
    )
    assert packet == {
        "schema_version": "emr4.model_required_bureau_a4.cell_request.v1",
        "lane": contracts.LANE_RAYLEEN,
        "attempt_id": "a4-rayleen-selector-primary-001",
        "ledger_id": "ledger-a4-rayleen-selector-primary-001",
        "policy_id": contracts.POLICY_ID,
        "context_hash": contracts.prefixed_sha256(context),
        "provider_request_hash": contracts.prefixed_sha256(
            contracts.build_vertex_request(contracts.LANE_RAYLEEN, context)
        ),
        "attempt_number": 1,
        "correction_of": None,
        "correction_reason_code": None,
    }
    dry_ledger = selector_live._attempt_ledger(packet, mode="dry-run")
    assert dry_ledger["maximum_provider_calls"] == 0
    assert dry_ledger["reserved_cost_usd"] == 0
    assert dry_ledger["fallback_permitted"] is False
    cost = selector_live._initial_cost_ledger()
    assert cost["lane_calls"] == {contracts.LANE_RAYLEEN: 0}
    assert cost["maximum_provider_calls"] == 2
    assert cost["maximum_cost_usd"] == 0.5


def test_provider_free_isolated_selector_evidence_is_exact() -> None:
    evidence_path = ARTIFACT_ROOT / "provider-free-selector-dry-run-evidence.json"
    cost_path = ARTIFACT_ROOT / "provider-free-selector-cost-ledger.json"
    attempt_path = (
        ARTIFACT_ROOT
        / "rayleen-a4-selector-attempt-1-dry-run-evidence.json"
    )
    ledger_path = ARTIFACT_ROOT / "rayleen-a4-selector-attempt-1-ledger.json"
    audit_path = ARTIFACT_ROOT / "rayleen-a4-selector-attempt-1-audit.jsonl"
    for path in (evidence_path, cost_path, attempt_path, ledger_path, audit_path):
        assert path.is_file()

    evidence = contracts.load_object(evidence_path)
    evidence_hash = evidence.pop("evidence_hash")
    assert evidence_hash == contracts.prefixed_sha256(evidence)
    assert evidence["result"] == "model_required_bureau_a4_provider_free_selector_pass"
    assert evidence["evidence_label"] == "provider_free_authored_synthetic_selector"
    assert evidence["selector_admitted"] is True
    assert evidence["candidate_runtime_provider_call_count"] == 0
    assert evidence["reserved_cost_usd"] == 0
    assert evidence["patient_or_clinical_data_count"] == 0
    assert evidence["provider_tool_call_count"] == 0
    assert evidence["fallback_count"] == 0

    cost = contracts.load_object(cost_path)
    assert cost["status"] == "consumed"
    assert cost["provider_calls_reserved"] == 0
    assert cost["provider_calls_consumed"] == 0
    assert cost["lane_calls"] == {contracts.LANE_RAYLEEN: 0}

    attempt = contracts.load_object(attempt_path)
    attempt_hash = attempt.pop("evidence_hash")
    assert attempt_hash == contracts.prefixed_sha256(attempt)
    assert attempt["result"] == "attempt_pass"
    assert attempt["proofreader_verdict"] == "admitted"
    assert attempt["provider_call_count"] == 0
    assert attempt["provider_contacted"] is False
    assert attempt["cleanup_passed"] is True
    assert all(
        value
        for key, value in attempt["cleanup"].items()
        if key != "daemon_wide_prune_performed"
    )
    assert attempt["cleanup"]["daemon_wide_prune_performed"] is False
    assert attempt["cell_policy"]["credential_environment_present"] is False
    assert attempt["release"]["evidence_mode"] == (
        "proofreader_admitted_display_projection"
    )

    ledger = contracts.load_object(ledger_path)
    contracts.validate_instance(
        ARTIFACT_ROOT / "single-use-ledger.schema.json", ledger
    )
    assert ledger["status"] == "consumed"
    assert ledger["provider_calls_consumed"] == 0

    events = [
        json.loads(line)
        for line in audit_path.read_text(encoding="utf-8").splitlines()
        if line
    ]
    previous = "sha256:" + "0" * 64
    for sequence, event in enumerate(events, start=1):
        material = {key: value for key, value in event.items() if key != "event_hash"}
        assert event["sequence"] == sequence
        assert event["previous_hash"] == previous
        assert event["event_hash"] == contracts.prefixed_sha256(material)
        previous = event["event_hash"]
    event_types = [event["event_type"] for event in events]
    assert event_types.count("provider_call_simulated") == 1
    assert "provider_call_started" not in event_types
    assert event_types.count("proofreader_completed") == 1
    assert event_types.count("release_committed") == 1
