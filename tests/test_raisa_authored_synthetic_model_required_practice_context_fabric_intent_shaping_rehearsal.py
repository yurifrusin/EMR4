"""Focused deterministic tests for the model-required intent-shaping rehearsal."""

from __future__ import annotations

import ast
from copy import deepcopy
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, FormatChecker

from scripts.raisa_authored_synthetic_model_required_practice_context_fabric_intent_shaping_contracts import (
    AUTHORITY_KEYS,
    CUE_CODES,
    INTENT_CODES,
    SYNTHETIC_COORDINATE_CODE,
    ContractError,
    build_dry_run_provider_packet,
    build_intent_shaping_request,
    build_vertex_request,
    canonical_model_body_fixture,
    extract_provider_candidate,
    prefixed_sha256,
    proofread_intent_candidate,
    wrap_provider_body,
)
from scripts.raisa_authored_synthetic_model_required_practice_context_fabric_intent_shaping_acceptance import (
    ACCEPTANCE_PATH,
    ARTIFACT_ROOT,
    CONTRACTS_PATH,
    EVIDENCE_PATH,
    RESULT,
    build_evidence,
)
from scripts.raisa_provider_free_practice_context_fabric_bureau_memory_contract import (
    seal,
)
from scripts.raisa_provider_free_practice_context_fabric_intent_shaped_temporal_retrieval_rehearsal import (
    proofread_intent_packet,
)


ROOT = Path(__file__).resolve().parents[1]


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _errors(schema_path: Path, instance: dict) -> list:
    return list(
        Draft202012Validator(
            _load(schema_path), format_checker=FormatChecker()
        ).iter_errors(instance)
    )


def _request() -> dict:
    return build_intent_shaping_request()


def _envelope(
    request: dict,
    body: dict,
    *,
    attempt_id: str = "raisa-intent-shaping-primary-001",
    ledger_id: str = "ledger-raisa-intent-shaping-primary-001",
) -> dict:
    return wrap_provider_body(
        request,
        body,
        attempt_id=attempt_id,
        ledger_id=ledger_id,
        provider_request_hash=prefixed_sha256({"provider": "request"}),
        provider_response_hash="sha256:" + "0" * 64,
        provider_response_shape={
            "candidate_count": 1,
            "finish_reason": "STOP",
            "parts_count": 1,
        },
    )


def test_all_schemas_are_draft_2020_12_and_closed() -> None:
    for name in (
        "intent-shaping-request.schema.json",
        "provider-intent-body.schema.json",
        "model-intent-candidate-envelope.schema.json",
        "cell-request.schema.json",
        "single-use-ledger.schema.json",
        "cost-ledger.schema.json",
        "occupied-rehearsal-evidence.schema.json",
    ):
        schema = _load(ARTIFACT_ROOT / name)
        Draft202012Validator.check_schema(schema)
        assert schema.get("$schema") == "https://json-schema.org/draft/2020-12/schema"
        assert schema.get("additionalProperties") is False


def test_request_fixture_validates_and_is_grounded() -> None:
    request = _request()
    assert _errors(
        ARTIFACT_ROOT / "intent-shaping-request.schema.json", request
    ) == []
    fixture = _load(
        ARTIFACT_ROOT / "authored-synthetic-intent-shaping-request.json"
    )
    assert fixture == request
    assert request["timezone"] == "Australia/Brisbane"
    assert request["reference_date"] == "2026-08-06"
    assert len(request["intent_codes"]) == 5
    assert request["cue_codes"] == list(CUE_CODES)


def test_provider_request_exact_allocation_no_tools_or_cache() -> None:
    request = build_vertex_request(_request())
    generation = request["generationConfig"]
    assert generation["thinkingConfig"] == {"thinkingBudget": 1024}
    assert generation["maxOutputTokens"] == 2048
    assert generation["temperature"] == 0
    assert generation["candidateCount"] == 1
    assert generation["responseMimeType"] == "application/json"
    assert "tools" not in request
    assert "cachedContent" not in request
    assert "systemInstruction" not in request
    prompt = request["contents"][0]["parts"][0]["text"]
    assert (
        "Compare the current waiting-room operational picture" in prompt
    )
    for forbidden in (
        "parent_contract_digest",
        "parent_policy_digest",
        "request_digest",
        "authority_ceiling",
        "candidate_digest",
        "context-fabric-intent-shaped-retrieval.v1",
        "source_catalog",
        "synthetic:intent-candidate",
        "synthetic:binding",
        "CURRENT_OPERATIONAL_AWARENESS",
        "BUREAU_MEMORY",
        "TEMPORAL_OPERATIONAL_RECALL",
        "recent_practice_work",
    ):
        assert forbidden not in prompt


def test_provider_request_size_stays_below_the_frozen_cap() -> None:
    request = build_vertex_request(_request())
    from scripts.raisa_authored_synthetic_model_required_practice_context_fabric_intent_shaping_contracts import (
        MAX_PROVIDER_REQUEST_BYTES,
        canonical_bytes,
    )

    assert len(canonical_bytes(request)) <= MAX_PROVIDER_REQUEST_BYTES
    assert len(canonical_bytes(request)) > 0


def test_safe_telemetry_excludes_raw_and_thought_values() -> None:
    from scripts.raisa_authored_synthetic_model_required_practice_context_fabric_intent_shaping_contracts import (
        bounded_provider_metadata,
    )

    metadata = bounded_provider_metadata(
        {
            "candidates": [
                {
                    "finishReason": "STOP",
                    "content": {
                        "parts": [
                            {
                                "text": "raw model answer that must not be retained",
                                "thought": True,
                            }
                        ]
                    },
                }
            ],
            "usageMetadata": {
                "promptTokenCount": 10,
                "candidatesTokenCount": 5,
                "thoughtsTokenCount": 1024,
                "totalTokenCount": 1039,
            },
            "modelVersion": "gemini-2.5-flash",
        }
    )
    assert metadata["candidate_count"] == 1
    assert metadata["finish_reason"] == "STOP"
    assert metadata["usage"]["thoughtsTokenCount"] == 1024
    assert metadata["provider_text_retained"] is False
    assert metadata["raw_prompt_retained"] is False
    assert metadata["raw_response_retained"] is False
    raw = json.dumps(metadata)
    assert "raw model answer" not in raw
    assert '"thought": true' not in raw
    assert "provider_text_retained" in raw


def test_parent_catalog_recomputes_upstream_proofreaders() -> None:
    from scripts.raisa_provider_free_practice_context_fabric_intent_shaped_temporal_retrieval_rehearsal import (
        IntentRetrievalViolation,
        build_authored_synthetic_sources,
        build_source_catalog,
    )

    sources = build_authored_synthetic_sources()
    sources["current_packet"]["source_envelopes"][0]["payload"]["appointments"][0][
        "status"
    ] = "COMPLETED"
    with pytest.raises(
        IntentRetrievalViolation, match="current_upstream_not_released"
    ):
        build_source_catalog(sources)


def test_source_review_validation_requires_exact_receipt() -> None:
    from scripts.raisa_authored_synthetic_model_required_practice_context_fabric_intent_shaping_live import (
        SOURCE_REVIEW_RECEIPT,
        _validate_source_review,
    )
    from scripts import model_required_bureau_a3_b3_live as live

    hashes = {
        path.relative_to(ROOT).as_posix(): "sha256:" + "0" * 64
        for path in (
            ARTIFACT_ROOT / "intent-shaping-request.schema.json",
            ARTIFACT_ROOT / "provider-intent-body.schema.json",
            ARTIFACT_ROOT / "model-intent-candidate-envelope.schema.json",
            ARTIFACT_ROOT / "cell-request.schema.json",
            ARTIFACT_ROOT / "single-use-ledger.schema.json",
            ARTIFACT_ROOT / "cost-ledger.schema.json",
            ARTIFACT_ROOT / "occupied-rehearsal-evidence.schema.json",
            ARTIFACT_ROOT / "authored-synthetic-intent-shaping-request.json",
        )
    }
    fake_receipt = ARTIFACT_ROOT / ".tmp-source-review-receipt.json"
    fake_receipt.write_text(
        json.dumps(
            {
                "schema_version": "emr4.raisa_intent_shaping.source_review.v1",
                "status": "passed",
                "decision": "pass",
                "independent_read_only_review": True,
                "provider_called": False,
                "source_hashes": hashes,
                "closed_boundary_verified": True,
            },
            sort_keys=True,
        )
    )
    try:
        with pytest.raises(live.LiveError, match="independent_source_review_not_exact"):
            _validate_source_review(fake_receipt)
    finally:
        fake_receipt.unlink(missing_ok=True)
    assert SOURCE_REVIEW_RECEIPT.name.endswith(".json")


def test_positive_thinking_evidence_is_required_for_occupied_acceptance() -> None:
    from scripts.raisa_authored_synthetic_model_required_practice_context_fabric_intent_shaping_live import (
        _positive_thinking_evidence,
    )

    assert _positive_thinking_evidence(
        {"usage": {"thoughtsTokenCount": 1024}}
    ) is True
    assert _positive_thinking_evidence(
        {"usage": {"thoughtsTokenCount": 0}}
    ) is False
    assert _positive_thinking_evidence({"usage": {}}) is False
    assert _positive_thinking_evidence({}) is False
    assert _positive_thinking_evidence(
        {"usage": {"thoughtsTokenCount": "1024"}}
    ) is False


def test_broker_safe_provider_metadata_allowlists_part_shape() -> None:
    from scripts.raisa_authored_synthetic_model_required_practice_context_fabric_intent_shaping_broker import (
        _safe_provider_metadata,
    )

    value = {
        "provider_contacted": True,
        "http_status": 200,
        "latency_ms": 42,
        "provider_response_bytes": 512,
        "candidate_count": 1,
        "parts_count": 1,
        "finish_reason": "STOP",
        "discarded_provider_response_sha256": None,
        "usage": {
            "promptTokenCount": 10,
            "candidatesTokenCount": 5,
            "thoughtsTokenCount": 1024,
            "totalTokenCount": 1039,
        },
        "raw_text_that_must_not_retain": "secret",
        "token": "abc",
        "Authorization": "Bearer x",
    }
    safe = _safe_provider_metadata(value)
    raw = json.dumps(safe)
    assert "secret" not in raw
    assert "abc" not in raw
    assert "Bearer" not in raw
    assert safe["parts_count"] == 1
    assert safe["candidate_count"] == 1
    assert safe["http_status"] == 200
    assert safe["usage"]["thoughtsTokenCount"] == 1024


def test_provider_response_schema_is_enum_bounded_and_authority_closed() -> None:
    response_schema = (
        __import__(
            "scripts.raisa_authored_synthetic_model_required_practice_context_fabric_intent_shaping_contracts",
            fromlist=["provider_response_schema"],
        ).provider_response_schema()
    )
    properties = response_schema["properties"]
    assert properties["intent_code"]["enum"] == list(INTENT_CODES)
    assert properties["temporal_coordinate_code"]["enum"] == [
        "NONE",
        SYNTHETIC_COORDINATE_CODE,
    ]
    assert properties["cue_codes"]["maxItems"] == 4
    assert properties["response_code"]["enum"] == ["INTENT_CANDIDATE_ONLY"]
    for key in AUTHORITY_KEYS:
        assert key in properties


def test_dry_run_packet_extracts_one_body_and_zero_call() -> None:
    packet = build_dry_run_provider_packet()
    body = extract_provider_candidate(packet)
    assert body["intent_code"] == "CURRENT_AND_PRIOR_OPERATIONAL_COMPARISON"
    assert body["temporal_coordinate_code"] == SYNTHETIC_COORDINATE_CODE
    assert body["cue_codes"] == list(CUE_CODES)
    assert body["response_code"] == "INTENT_CANDIDATE_ONLY"
    assert packet["modelVersion"] == "provider-free-intent-shaping-fixture"
    assert packet["usageMetadata"]["thoughtsTokenCount"] == 0
    assert packet["candidates"][0]["finishReason"] == "STOP"
    assert len(packet["candidates"][0]["content"]["parts"]) == 1


@pytest.mark.parametrize(
    ("mutation", "reason"),
    (
        (lambda value: value.update({"intent_code": "CURRENT_OPERATIONAL_STATUS"}), "intent_not_grounded"),
        (lambda value: value.update({"temporal_coordinate_code": "NONE"}), "intent_not_grounded"),
        (
            lambda value: value.update(
                {
                    "cue_codes": [
                        "CURRENT_STATE_REQUESTED",
                        "PRIOR_STATE_REQUESTED",
                        "VALID_TIME_1030",
                    ]
                }
            ),
            "intent_not_grounded",
        ),
    ),
)
def test_occupied_grounding_rejects_wrong_intent_coordinate_and_missing_cue(
    mutation, reason: str
) -> None:
    request = _request()
    body = deepcopy(
        canonical_model_body_fixture(
            "CURRENT_AND_PRIOR_OPERATIONAL_COMPARISON"
        )
    )
    mutation(body)
    envelope = _envelope(request, body)
    proof = proofread_intent_candidate(request, envelope, ground_to_case=True)
    assert proof["verdict"] == "rejected"
    assert proof["reason_code"] == reason
    assert proof["released"] is None


def test_extra_cue_fails_closed_schema() -> None:
    request = _request()
    body = deepcopy(
        canonical_model_body_fixture(
            "CURRENT_AND_PRIOR_OPERATIONAL_COMPARISON"
        )
    )
    body["cue_codes"] = [
        "CURRENT_STATE_REQUESTED",
        "PRIOR_STATE_REQUESTED",
        "VALID_TIME_1030",
        "KNOWLEDGE_CUTOFF_1230",
        "PRIOR_STATE_REQUESTED",
    ]
    with pytest.raises((ContractError, ValueError)):
        _envelope(request, body)


def test_prose_and_true_authority_are_blocked() -> None:
    request = _request()
    body = deepcopy(
        canonical_model_body_fixture(
            "CURRENT_AND_PRIOR_OPERATIONAL_COMPARISON"
        )
    )
    prose = deepcopy(body)
    prose["prose"] = "free-text explanation"
    with pytest.raises((ContractError, ValueError)):
        _envelope(request, prose)
    authority = deepcopy(body)
    authority["write"] = True
    blocked = False
    try:
        envelope = _envelope(request, authority)
    except (ContractError, ValueError):
        blocked = True
    if not blocked:
        proof = proofread_intent_candidate(
            request, envelope, ground_to_case=True
        )
        assert proof["verdict"] == "rejected"


def test_unknown_intent_is_rejected_by_closed_schema() -> None:
    request = _request()
    body = deepcopy(
        canonical_model_body_fixture(
            "CURRENT_AND_PRIOR_OPERATIONAL_COMPARISON"
        )
    )
    body["intent_code"] = "INVENTED_INTENT"
    with pytest.raises((ContractError, ValueError)):
        _envelope(request, body)


def test_all_five_fixtures_traverse_the_unchanged_parent_engine() -> None:
    request = _request()
    for intent in INTENT_CODES:
        body = canonical_model_body_fixture(intent)
        envelope = _envelope(request, body)
        proof = proofread_intent_candidate(
            request, envelope, ground_to_case=False
        )
        assert proof["verdict"] == "admitted", intent
        release = proof["released"]
        assert (
            release["parent_proofreader_trace"]["release_decision"] == "RELEASE"
        )
        assert release["read_only"] is True
        assert release["provider_authority"] is False
        assert release["command_authority"] is False
        parent = release["parent_packet"]
        assert parent["proofreader_trace"]["release_decision"] == "RELEASE"


def test_occupied_comparison_selects_current_and_historical() -> None:
    request = _request()
    body = canonical_model_body_fixture(
        "CURRENT_AND_PRIOR_OPERATIONAL_COMPARISON"
    )
    envelope = _envelope(request, body)
    proof = proofread_intent_candidate(request, envelope, ground_to_case=True)
    assert proof["verdict"] == "admitted"
    components = [
        item["component_code"]
        for item in proof["released"]["parent_packet"]["frame_set"][
            "components"
        ]
    ]
    assert components == ["CURRENT_OPERATIONAL", "HISTORICAL_OPERATIONAL"]


def test_trusted_wrapper_supplies_parent_authority_and_bureau() -> None:
    request = _request()
    body = canonical_model_body_fixture(
        "CURRENT_AND_PRIOR_OPERATIONAL_COMPARISON"
    )
    envelope = _envelope(request, body)
    proof = proofread_intent_candidate(request, envelope, ground_to_case=True)
    candidate = proof["released"]["parent_candidate"]
    assert candidate["requesting_bureau"] == "RAYLEEN"
    assert candidate["read_only"] is True
    assert candidate["provider_authority"] is False
    assert candidate["command_authority"] is False
    for forbidden in (
        "principal_ref",
        "practice_id",
        "role_codes",
        "location_refs",
        "session_id",
        "retention_days",
    ):
        assert forbidden not in candidate


def test_envelope_and_request_digest_tamper_are_blocked() -> None:
    request = _request()
    body = canonical_model_body_fixture(
        "CURRENT_AND_PRIOR_OPERATIONAL_COMPARISON"
    )
    envelope = _envelope(request, body)

    not_resealed = deepcopy(envelope)
    not_resealed["body"]["intent_code"] = "CURRENT_OPERATIONAL_STATUS"
    proof = proofread_intent_candidate(
        request, not_resealed, ground_to_case=True
    )
    assert proof["verdict"] == "rejected"
    assert proof["reason_code"] == "envelope_digest_mismatch"

    resealed = deepcopy(envelope)
    resealed["body"]["intent_code"] = "CURRENT_OPERATIONAL_STATUS"
    resealed.pop("envelope_digest")
    resealed = seal(resealed, "envelope_digest")
    proof = proofread_intent_candidate(request, resealed, ground_to_case=True)
    assert proof["verdict"] == "rejected"
    assert proof["reason_code"] == "intent_not_grounded"

    tampered_request = deepcopy(request)
    tampered_request["parent_policy_digest"] = "sha256:" + "0" * 64
    tampered_request.pop("request_digest")
    tampered_request = seal(tampered_request, "request_digest")
    proof = proofread_intent_candidate(
        tampered_request, envelope, ground_to_case=True
    )
    assert proof["verdict"] == "rejected"
    assert proof["reason_code"] in {
        "request_hash_mismatch",
        "schema_invalid",
        "request_digest_mismatch",
    }


def test_parent_same_packet_proofreader_blocks_content_tamper() -> None:
    request = _request()
    body = canonical_model_body_fixture(
        "CURRENT_AND_PRIOR_OPERATIONAL_COMPARISON"
    )
    envelope = _envelope(request, body)
    proof = proofread_intent_candidate(request, envelope, ground_to_case=True)
    parent = proof["released"]["parent_packet"]
    bare = {
        key: deepcopy(value)
        for key, value in parent.items()
        if key not in {"proofreader_trace", "contract_digest"}
    }
    bare["frame_set"]["components"][0]["facts"][0]["value"] = "OTHER"
    trace = proofread_intent_packet(
        bare, checked_at="2026-08-06T03:01:01Z"
    )
    assert trace["release_decision"] == "BLOCK"


def test_release_digest_recomputation_detects_tamper() -> None:
    request = _request()
    body = canonical_model_body_fixture(
        "CURRENT_AND_PRIOR_OPERATIONAL_COMPARISON"
    )
    envelope = _envelope(request, body)
    proof = proofread_intent_candidate(request, envelope, ground_to_case=True)
    release = proof["released"]
    tampered = deepcopy(release)
    tampered["read_only"] = False
    tampered.pop("release_digest")
    tampered = seal(tampered, "release_digest")
    material = {
        key: value for key, value in tampered.items() if key != "release_digest"
    }
    assert tampered["release_digest"] == prefixed_sha256(material)
    original_material = {
        key: value
        for key, value in release.items()
        if key != "release_digest"
    }
    assert release["release_digest"] == prefixed_sha256(original_material)
    assert tampered["release_digest"] != release["release_digest"]


def test_correction_requests_are_distinct_and_bounded() -> None:
    request = _request()
    contracts = __import__(
        "scripts.raisa_authored_synthetic_model_required_practice_context_fabric_intent_shaping_contracts",
        fromlist=["correction_request", "provider_request_for_attempt"],
    )
    primary = contracts.build_vertex_request(request)
    schema_correction = contracts.correction_request(
        request, "provider_body_schema_invalid", 2
    )
    grounding_correction = contracts.correction_request(
        request, "intent_not_grounded", 2
    )
    assert prefixed_sha256(primary) != prefixed_sha256(schema_correction)
    assert prefixed_sha256(primary) != prefixed_sha256(grounding_correction)
    assert prefixed_sha256(schema_correction) != prefixed_sha256(
        grounding_correction
    )
    assert schema_correction["generationConfig"] == primary["generationConfig"]
    with pytest.raises(ContractError, match="correction_not_eligible"):
        contracts.correction_request(request, "authority_ceiling_invalid", 2)
    with pytest.raises(ContractError, match="correction_not_eligible"):
        contracts.correction_request(request, "intent_not_grounded", 1)


def test_cost_and_ledger_schemas_enforce_two_call_and_050_ceiling() -> None:
    cost = _load(ARTIFACT_ROOT / "cost-ledger.schema.json")
    ledger = _load(ARTIFACT_ROOT / "single-use-ledger.schema.json")
    cell = _load(ARTIFACT_ROOT / "cell-request.schema.json")
    assert cost["properties"]["maximum_provider_calls"]["const"] == 2
    assert cost["properties"]["maximum_cost_usd"]["const"] == 0.5
    assert set(cost["properties"]["lane_calls"]["properties"]) == {
        "rayleen_context_fabric_intent_shaping"
    }
    assert ledger["properties"]["fallback_permitted"]["const"] is False
    assert ledger["properties"]["reserved_cost_usd"]["enum"] == [0, 0.25]
    assert cell["properties"]["lane"]["const"] == (
        "rayleen_context_fabric_intent_shaping"
    )
    assert cell["properties"]["attempt_number"]["enum"] == [1, 2]


def test_pure_contracts_have_no_application_provider_or_command_surface() -> None:
    tree = ast.parse(CONTRACTS_PATH.read_text(encoding="utf-8"))
    forbidden_imports = {
        "app",
        "boto3",
        "google",
        "httpx",
        "os",
        "requests",
        "socket",
        "sqlalchemy",
        "subprocess",
    }
    imports = {
        alias.name.split(".", 1)[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    imports |= {
        node.module.split(".", 1)[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module
    }
    assert not imports.intersection(forbidden_imports)
    text = CONTRACTS_PATH.read_text(encoding="utf-8")
    assert "Mutation" not in text
    assert "Subscription" not in text
    assert "CREATE TABLE" not in text


def test_evidence_passes_and_is_reproducible() -> None:
    evidence = build_evidence()
    assert evidence["result"] == RESULT
    assert evidence["passed"] is True
    assert evidence["evidence_label"] == (
        "provider_free_authored_synthetic_model_intent_shaping"
    )
    assert set(evidence["authority_and_side_effects"].values()) == {0}
    assert evidence["source_binding"]["artifact_count"] >= 13
    assert ACCEPTANCE_PATH.exists()
    if EVIDENCE_PATH.exists():
        assert _load(EVIDENCE_PATH) == evidence
