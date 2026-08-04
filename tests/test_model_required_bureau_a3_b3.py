"""Provider-free deterministic tests for the Bureau A3/B3 rehearsal.

These tests exercise only repository contracts and pure proofreader/request
builders.  They never open credentials, a provider, a network connection, a
database, Docker, a product route or an actuator.
"""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import shutil
from types import SimpleNamespace

import pytest

from scripts import model_required_bureau_a3_b3_contracts as contracts
from scripts import model_required_bureau_a3_b3_broker as broker
from scripts import model_required_bureau_a3_b3_live as live


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_ROOT = (
    ROOT / "orchestration/continuity/model-required-bureau-a3-b3"
)


def _load(name: str) -> dict:
    value = json.loads((ARTIFACT_ROOT / name).read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _rayleen_context() -> dict:
    return _load("rayleen-a3-context.example.json")


def _rayleen_candidate() -> dict:
    return _load("rayleen-a3-candidate.example.json")


def _davida_context() -> dict:
    return _load("davida-b3-context.example.json")


def _davida_candidate() -> dict:
    return _load("davida-b3-candidate.example.json")


def _rehash_davida_context(context: dict) -> None:
    material = {
        key: value
        for key, value in context.items()
        if key != "content_revision"
    }
    context["content_revision"] = contracts.canonical_sha256(material)


def _rehash_davida_dry_run(context: dict) -> None:
    dry_run = context["dry_run"]
    material = {
        key: value for key, value in dry_run.items() if key != "dry_run_hash"
    }
    dry_run["dry_run_hash"] = contracts.canonical_sha256(material)
    _rehash_davida_context(context)


def _model_body(candidate: dict, schema_name: str) -> dict:
    schema = _load(schema_name)
    return {key: deepcopy(candidate[key]) for key in schema["required"]}


def _assert_schema_objects_closed(value: object, path: str = "$") -> None:
    if isinstance(value, dict):
        if value.get("type") == "object":
            closure = value.get("additionalProperties")
            assert closure is False or closure == {"const": False}, path
        for key, child in value.items():
            _assert_schema_objects_closed(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _assert_schema_objects_closed(child, f"{path}[{index}]")


@pytest.mark.parametrize(
    ("schema_name", "example_name"),
    (
        ("a3-b3-contract.schema.json", "a3-b3-contract.json"),
        ("occupied-authority.schema.json", "occupied-authority.json"),
        (
            "occupied-preflight-blocked.schema.json",
            "occupied-preflight-blocked-evidence.json",
        ),
        (
            "occupied-terminal-interruption.schema.json",
            "occupied-terminal-interruption-evidence.json",
        ),
        ("rayleen-a3-context.schema.json", "rayleen-a3-context.example.json"),
        (
            "rayleen-a3-candidate.schema.json",
            "rayleen-a3-candidate.example.json",
        ),
        ("davida-b3-context.schema.json", "davida-b3-context.example.json"),
        (
            "davida-b3-candidate.schema.json",
            "davida-b3-candidate.example.json",
        ),
    ),
)
def test_contract_and_examples_validate(
    schema_name: str, example_name: str
) -> None:
    contracts.validate_instance(
        ARTIFACT_ROOT / schema_name,
        _load(example_name),
    )


@pytest.mark.parametrize(
    "schema_name",
    (
        "a3-b3-contract.schema.json",
        "rayleen-a3-context.schema.json",
        "rayleen-a3-candidate.schema.json",
        "rayleen-a3-model-body.schema.json",
        "davida-b3-context.schema.json",
        "davida-b3-candidate.schema.json",
        "davida-b3-model-body.schema.json",
        "rayleen-a3-release.schema.json",
        "davida-b3-release.schema.json",
        "occupied-preflight-blocked.schema.json",
        "occupied-terminal-interruption.schema.json",
        "cell-request.schema.json",
        "single-use-ledger.schema.json",
        "cost-ledger.schema.json",
    ),
)
def test_every_json_schema_object_is_closed(schema_name: str) -> None:
    _assert_schema_objects_closed(_load(schema_name))


def test_rayleen_happy_path_releases_exact_grounded_projection() -> None:
    context = _rayleen_context()
    candidate = _rayleen_candidate()

    result = contracts.proofread_rayleen(candidate, context)

    assert result["verdict"] == "admitted"
    assert result["lane"] == contracts.LANE_RAYLEEN
    assert result["correction_eligible"] is False
    release = result["released"]
    assert release["evidence_mode"] == (
        "authored_synthetic_occupied_provider_advisory_rehearsal"
    )
    assert release["status"] == "advisory_only"
    assert release["context_binding"] == {
        "frame_id": context["frame_id"],
        "practice_id": context["practice_id"],
        "location_id": context["location_id"],
        "context_revision": context["context_revision"],
        "evaluation_time": context["evaluation_time"],
        "evaluation_mode": context["evaluation_mode"],
        "expires_at": context["expires_at"],
    }
    assert release["projection"]["focus_appointment_id"] == (
        "31000000-0000-4000-8000-000000000011"
    )
    assert release["projection"]["evidence_appointment_ids"] == [
        "31000000-0000-4000-8000-000000000011",
        "31000000-0000-4000-8000-000000000012",
    ]
    assert all(value is False for value in release["authority_ceiling"].values())


def test_davida_happy_path_releases_exact_dry_run_advisory() -> None:
    context = _davida_context()
    candidate = _davida_candidate()

    result = contracts.proofread_davida(candidate, context)

    assert result["verdict"] == "admitted"
    assert result["lane"] == contracts.LANE_DAVIDA
    assert result["correction_eligible"] is False
    release = result["released"]
    assert release["status"] == "dry_run_advisory_only"
    assert release["context_binding"]["content_revision"] == (
        context["content_revision"]
    )
    assert release["proposal"] == {
        "intent": "dry_run",
        "operation": "PROPOSE_UPDATE_PRACTITIONER_DEFAULT_LOCATION",
        "practitioner_ref": "practitioner-patel",
        "location_ref": "location-north",
        "reason_code": "PRACTICE_ASSIGNMENT_UPDATE",
        "risk_tier": "admin_proposal",
        "response_code": "DRY_RUN_REQUIRES_HUMAN_CONFIRMATION",
        "human_confirmation_required": True,
        "dry_run_proposal_hash": context["dry_run"]["dry_run_hash"],
        "changed_paths": ["practitioner.default_location_ref"],
        "before_state": {
            "practitioner_ref": "practitioner-patel",
            "default_location_ref": "location-south",
        },
        "after_state": {
            "practitioner_ref": "practitioner-patel",
            "default_location_ref": "location-north",
        },
        "source_paths": [
            "practice.active_practitioners",
            "practice.active_locations",
        ],
        "source_label": "authored_synthetic_fixture",
    }
    assert all(value is False for value in release["authority_ceiling"].values())


@pytest.mark.parametrize(
    ("lane", "context_factory", "candidate_factory", "schema_name"),
    (
        (
            contracts.LANE_RAYLEEN,
            _rayleen_context,
            _rayleen_candidate,
            "rayleen-a3-model-body.schema.json",
        ),
        (
            contracts.LANE_DAVIDA,
            _davida_context,
            _davida_candidate,
            "davida-b3-model-body.schema.json",
        ),
    ),
)
def test_selector_body_wrapping_restores_only_host_owned_fields(
    lane: str,
    context_factory,
    candidate_factory,
    schema_name: str,
) -> None:
    context = context_factory()
    expected = candidate_factory()
    body = _model_body(expected, schema_name)
    before = deepcopy(body)

    wrapped = contracts.wrap_provider_body(lane, body, context)

    assert wrapped == expected
    assert body == before
    body_schema = _load(schema_name)
    assert not {
        "schema_version",
        "case_id",
        "context_revision",
        "content_revision",
        "risk_tier",
        "human_confirmation_required",
        "confirmation_authorized",
        "apply_authorized",
        "writes_authorized",
        "success_claimed",
    } & set(body_schema["properties"])


def test_rayleen_stale_revision_and_wrong_selectors_fail_closed() -> None:
    context = _rayleen_context()

    stale = _rayleen_candidate()
    stale["context_revision"] += 1
    result = contracts.proofread_rayleen(stale, context)
    assert result["reason_code"] == "context_revision_mismatch"
    assert result["correction_eligible"] is False
    assert result["released"] is None

    wrong_practitioner = _rayleen_candidate()
    wrong_practitioner["practitioner_id"] = (
        "31000000-0000-4000-8000-000000000099"
    )
    result = contracts.proofread_rayleen(wrong_practitioner, context)
    assert result["reason_code"] == "practitioner_not_grounded"
    assert result["released"] is None

    wrong_focus = _rayleen_candidate()
    wrong_focus["focus_appointment_id"] = (
        "31000000-0000-4000-8000-000000000012"
    )
    result = contracts.proofread_rayleen(wrong_focus, context)
    assert result["reason_code"] == "longest_wait_not_grounded"
    assert result["released"] is None


def test_invalid_context_expiry_is_terminal_for_both_lanes() -> None:
    rayleen_context = _rayleen_context()
    rayleen_context["expires_at"] = rayleen_context["generated_at"]
    result = contracts.proofread_rayleen(
        _rayleen_candidate(), rayleen_context
    )
    assert result["reason_code"] == "context_expiry_invalid"
    assert result["correction_eligible"] is False

    davida_context = _davida_context()
    davida_context["expires_at"] = davida_context["observed_at"]
    _rehash_davida_context(davida_context)
    davida_candidate = _davida_candidate()
    davida_candidate["content_revision"] = davida_context["content_revision"]
    result = contracts.proofread_davida(davida_candidate, davida_context)
    assert result["reason_code"] == "context_expiry_invalid"
    assert result["correction_eligible"] is False


@pytest.mark.parametrize(
    ("context_factory", "candidate_factory", "lane", "boundary"),
    (
        (
            _rayleen_context,
            _rayleen_candidate,
            contracts.LANE_RAYLEEN,
            "generated_at",
        ),
        (
            _rayleen_context,
            _rayleen_candidate,
            contracts.LANE_RAYLEEN,
            "expires_at",
        ),
        (
            _davida_context,
            _davida_candidate,
            contracts.LANE_DAVIDA,
            "observed_at",
        ),
        (
            _davida_context,
            _davida_candidate,
            contracts.LANE_DAVIDA,
            "expires_at",
        ),
    ),
)
def test_authored_synthetic_evaluation_time_is_half_open(
    context_factory,
    candidate_factory,
    lane: str,
    boundary: str,
) -> None:
    context = context_factory()
    context["evaluation_time"] = context[boundary]
    candidate = candidate_factory()
    if lane == contracts.LANE_DAVIDA:
        _rehash_davida_context(context)
        candidate["content_revision"] = context["content_revision"]
    result = contracts.proofread(lane, candidate, context)
    if boundary in {"generated_at", "observed_at"}:
        assert result["verdict"] == "admitted"
    else:
        assert result["reason_code"] == "context_expiry_invalid"


@pytest.mark.parametrize(
    ("mode", "value"),
    (
        ("live", None),
        ("live", "gemini-2.5-flash-002"),
        ("live", "gemini-2.0-flash"),
        ("dry-run", "gemini-2.5-flash"),
    ),
)
def test_unexpected_observed_model_version_fails_closed(
    mode: str, value: str | None
) -> None:
    with pytest.raises(
        broker.BrokerError,
        match="provider_model_version_mismatch",
    ):
        broker._validate_observed_model_version(mode=mode, value=value)


def test_exact_observed_model_versions_are_admitted() -> None:
    broker._validate_observed_model_version(
        mode="live",
        value=contracts.MODEL,
    )
    broker._validate_observed_model_version(
        mode="dry-run",
        value="provider-free-selector-fixture",
    )


@pytest.mark.parametrize(
    ("field", "replacement"),
    (
        ("practitioner_ref", "location-north"),
        ("location_ref", "practitioner-patel"),
    ),
)
def test_davida_cross_kind_selectors_fail_closed(
    field: str, replacement: str
) -> None:
    candidate = _davida_candidate()
    candidate[field] = replacement

    result = contracts.proofread_davida(candidate, _davida_context())

    assert result["verdict"] == "rejected"
    assert result["reason_code"] == "wrong_resource_kind"
    assert result["correction_eligible"] is False
    assert result["released"] is None


def test_davida_candidate_dry_run_hash_mismatch_fails_closed() -> None:
    candidate = _davida_candidate()
    candidate["dry_run_proposal_hash"] = "0" * 64

    result = contracts.proofread_davida(candidate, _davida_context())

    assert result["reason_code"] == "dry_run_hash_mismatch"
    assert result["correction_eligible"] is False
    assert result["released"] is None


def test_davida_tampered_context_dry_run_hash_fails_closed() -> None:
    context = _davida_context()
    context["dry_run"]["dry_run_hash"] = "0" * 64
    _rehash_davida_context(context)
    candidate = _davida_candidate()
    candidate["content_revision"] = context["content_revision"]

    result = contracts.proofread_davida(candidate, context)

    assert result["reason_code"] == "dry_run_hash_invalid"
    assert result["correction_eligible"] is False
    assert result["released"] is None


def test_davida_no_change_fails_before_dry_run_selection_release() -> None:
    candidate = _davida_candidate()
    candidate["location_ref"] = "location-south"

    result = contracts.proofread_davida(candidate, _davida_context())

    assert result["reason_code"] == "no_change"
    assert result["correction_eligible"] is False
    assert result["released"] is None


@pytest.mark.parametrize(
    ("lane", "context_factory", "candidate_factory", "field"),
    (
        (
            contracts.LANE_RAYLEEN,
            _rayleen_context,
            _rayleen_candidate,
            "confirmation_authorized",
        ),
        (
            contracts.LANE_RAYLEEN,
            _rayleen_context,
            _rayleen_candidate,
            "writes_authorized",
        ),
        (
            contracts.LANE_DAVIDA,
            _davida_context,
            _davida_candidate,
            "confirmation_authorized",
        ),
        (
            contracts.LANE_DAVIDA,
            _davida_context,
            _davida_candidate,
            "apply_authorized",
        ),
        (
            contracts.LANE_DAVIDA,
            _davida_context,
            _davida_candidate,
            "writes_authorized",
        ),
        (
            contracts.LANE_DAVIDA,
            _davida_context,
            _davida_candidate,
            "success_claimed",
        ),
    ),
)
def test_authority_reversal_never_releases(
    lane: str,
    context_factory,
    candidate_factory,
    field: str,
) -> None:
    candidate = candidate_factory()
    candidate[field] = True

    result = contracts.proofread(lane, candidate, context_factory())

    assert result["verdict"] == "rejected"
    assert result["reason_code"] == "schema_invalid"
    assert result["released"] is None


@pytest.mark.parametrize(
    ("lane", "context_factory", "candidate_factory", "schema_name"),
    (
        (
            contracts.LANE_RAYLEEN,
            _rayleen_context,
            _rayleen_candidate,
            "rayleen-a3-model-body.schema.json",
        ),
        (
            contracts.LANE_DAVIDA,
            _davida_context,
            _davida_candidate,
            "davida-b3-model-body.schema.json",
        ),
    ),
)
def test_selector_body_cannot_supply_authority(
    lane: str,
    context_factory,
    candidate_factory,
    schema_name: str,
) -> None:
    body = _model_body(candidate_factory(), schema_name)
    body["writes_authorized"] = True

    with pytest.raises(contracts.ContractError, match="schema_invalid"):
        contracts.wrap_provider_body(lane, body, context_factory())


@pytest.mark.parametrize(
    ("lane", "context_factory"),
    (
        (contracts.LANE_RAYLEEN, _rayleen_context),
        (contracts.LANE_DAVIDA, _davida_context),
    ),
)
def test_vertex_request_is_selector_only_with_no_tools_or_cache(
    lane: str, context_factory
) -> None:
    context = context_factory()
    request = contracts.build_vertex_request(lane, context)

    assert set(request) == {"contents", "generationConfig"}
    assert request["contents"] == [
        {
            "role": "user",
            "parts": [{"text": contracts.build_prompt(lane, context)}],
        }
    ]
    config = request["generationConfig"]
    assert set(config) == {
        "temperature",
        "candidateCount",
        "maxOutputTokens",
        "responseMimeType",
        "responseSchema",
    }
    assert config["temperature"] == 0
    assert config["candidateCount"] == 1
    assert config["maxOutputTokens"] == 512
    assert config["responseMimeType"] == "application/json"
    assert config["responseSchema"] == contracts.provider_response_schema(lane)
    assert config["responseSchema"]["required"] == (
        config["responseSchema"]["propertyOrdering"]
    )
    serialized = contracts.canonical_bytes(request)
    assert len(serialized) <= contracts.MAX_PROVIDER_REQUEST_BYTES
    for forbidden in (
        b'"tools"',
        b'"toolConfig"',
        b'"cachedContent"',
        b'"groundingConfig"',
        b'"systemInstruction"',
    ):
        assert forbidden not in serialized


def test_davida_response_schema_binds_exact_dry_run_hash() -> None:
    schema = contracts.provider_response_schema(contracts.LANE_DAVIDA)
    dry_run_hash = _davida_context()["dry_run"]["dry_run_hash"]

    assert schema["properties"]["dry_run_proposal_hash"] == {
        "type": "STRING",
        "enum": [dry_run_hash],
    }
    assert "content_revision" not in schema["properties"]
    assert "authority_ceiling" not in schema["properties"]
    assert "command" not in schema["properties"]


def test_schema_error_is_the_only_correction_ticket_class() -> None:
    context = _rayleen_context()
    candidate = _rayleen_candidate()
    candidate.pop("response_code")

    result = contracts.proofread_rayleen(candidate, context)

    assert result["reason_code"] == "schema_invalid"
    assert result["correction_eligible"] is True
    correction = contracts.correction_request(
        contracts.LANE_RAYLEEN,
        context,
        result["reason_code"],
        attempt_number=2,
    )
    text = correction["contents"][0]["parts"][0]["text"]
    assert text.startswith("CORRECTION_TICKET:")
    assert "same context and task" in text
    assert "Do not change identifiers, meaning or authority" in text

    for reason, attempt in (
        ("context_revision_mismatch", 2),
        ("wrong_resource_kind", 2),
        ("schema_invalid", 1),
        ("schema_invalid", 3),
    ):
        with pytest.raises(contracts.ContractError, match="correction_not_eligible"):
            contracts.correction_request(
                contracts.LANE_RAYLEEN,
                context,
                reason,
                attempt_number=attempt,
            )


def test_bounded_provider_metadata_redacts_raw_material() -> None:
    packet = {
        "rawPrompt": "UNRETAINED_PROMPT_SENTINEL",
        "providerSecret": "UNRETAINED_SECRET_SENTINEL",
        "candidates": [
            {
                "finishReason": "STOP",
                "content": {
                    "parts": [
                        {"text": "UNRETAINED_PROVIDER_TEXT_SENTINEL"}
                    ]
                },
            }
        ],
        "usageMetadata": {
            "promptTokenCount": 101,
            "candidatesTokenCount": 21,
            "thoughtsTokenCount": 3,
            "totalTokenCount": 125,
            "rawCharacters": 999,
            "negative": -1,
            "coerced": "7",
        },
    }

    safe = contracts.bounded_provider_metadata(packet)

    assert safe == {
        "candidate_count": 1,
        "finish_reason": "STOP",
        "usage": {
            "promptTokenCount": 101,
            "candidatesTokenCount": 21,
            "thoughtsTokenCount": 3,
            "totalTokenCount": 125,
        },
        "provider_text_retained": False,
        "raw_prompt_retained": False,
        "raw_response_retained": False,
    }
    serialized = json.dumps(safe, sort_keys=True)
    for sentinel in (
        "UNRETAINED_PROMPT_SENTINEL",
        "UNRETAINED_SECRET_SENTINEL",
        "UNRETAINED_PROVIDER_TEXT_SENTINEL",
    ):
        assert sentinel not in serialized


def test_exact_provider_call_and_authority_envelope_constants() -> None:
    contract = _load("a3-b3-contract.json")
    provider = contract["provider_binding"]
    calls = contract["call_boundary"]

    assert provider == {
        "provider": "google_cloud_vertex_ai",
        "model": contracts.MODEL,
        "project": contracts.PROJECT,
        "service_account": contracts.SERVICE_ACCOUNT,
        "authentication": "existing_keyless_impersonated_service_account_adc",
        "scope": contracts.SCOPE,
        "location": contracts.LOCATION,
        "endpoint_hostname": contracts.HOSTNAME,
        "api_path": contracts.PATH,
        "automatic_fallback": False,
        "global_endpoint": False,
        "provider_tools": False,
        "grounding": False,
        "cached_content": False,
        "provider_managed_cache_disabled_required": True,
    }
    assert calls == {
        "lane_count": 2,
        "primary_calls_per_lane": 1,
        "conditional_corrections_per_lane": 1,
        "maximum_calls_per_lane": contracts.MAX_CALLS_PER_LANE,
        "maximum_calls_total": contracts.MAX_CALLS_TOTAL,
        "maximum_cost_usd": contracts.MAX_COST_USD,
        "serial": True,
        "stop_after_first_admission": True,
        "unchanged_duplicate": False,
        "semantic_retry": False,
    }
    assert contracts.RESERVED_COST_PER_CALL_USD * contracts.MAX_CALLS_TOTAL == (
        contracts.MAX_COST_USD
    )
    assert contract["data_boundary"]["classification"] == (
        "newly_authored_synthetic_only"
    )
    assert all(
        value is False
        for key, value in contract["data_boundary"].items()
        if key != "classification"
    )
    assert all(value is False for value in contract["closed_surfaces"].values())
    assert [(lane["lane"], lane["domain"]) for lane in contract["lanes"]] == [
        ("A3", "rayleen"),
        ("B3", "davida"),
    ]


def test_provider_candidate_extraction_is_one_object_only() -> None:
    body = _model_body(
        _davida_candidate(), "davida-b3-model-body.schema.json"
    )
    packet = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {
                            "text": json.dumps(
                                body, sort_keys=True, separators=(",", ":")
                            )
                        }
                    ]
                }
            }
        ]
    }
    assert contracts.extract_provider_candidate(packet) == body

    duplicated = deepcopy(packet)
    duplicated["candidates"].append(deepcopy(duplicated["candidates"][0]))
    with pytest.raises(
        contracts.ContractError, match="provider_candidate_count_invalid"
    ):
        contracts.extract_provider_candidate(duplicated)


@pytest.mark.parametrize(
    "parts",
    (None, [], [{"text": "{}"}, {"text": "{}"}]),
)
def test_provider_content_shape_failure_is_exact_and_not_a_correction(
    parts: object,
) -> None:
    candidate: dict[str, object] = {}
    if parts is not None:
        candidate["content"] = {"parts": parts}
    packet = {"candidates": [candidate]}

    with pytest.raises(contracts.ContractError, match="provider_content_invalid"):
        contracts.extract_provider_candidate(packet)
    with pytest.raises(contracts.ContractError, match="correction_not_eligible"):
        contracts.correction_request(
            contracts.LANE_RAYLEEN,
            _rayleen_context(),
            "provider_content_invalid",
            attempt_number=2,
        )


def test_broker_rejection_preserves_exact_terminal_reason_and_safe_metadata() -> None:
    packet = live._request_packet(
        contracts.LANE_RAYLEEN,
        _rayleen_context(),
        attempt_number=1,
        correction_of=None,
        correction_reason_code=None,
    )
    state = SimpleNamespace(mode="live", expected_request=packet)
    safe_provider = {
        "provider_contacted": True,
        "http_status": 200,
        "candidate_count": 1,
        "finish_reason": "MAX_TOKENS",
        "raw_provider_response_retained": False,
        "unapproved_raw_field": "must not survive",
    }
    error = broker.BrokerError(
        "provider_content_invalid",
        metadata={
            "provider_contacted": True,
            "provider_metadata": safe_provider,
        },
    )

    event, response = broker._safe_rejection_records(state, error)

    expected_provider = {
        key: value
        for key, value in safe_provider.items()
        if key != "unapproved_raw_field"
    }
    assert event == {
        "reason_code": "provider_content_invalid",
        "provider_retry": False,
        "correction_eligible": False,
        "provider_contacted": True,
        "provider_metadata": expected_provider,
    }
    assert response["reason_code"] == "provider_content_invalid"
    assert response["correction_eligible"] is False
    assert response["release"] is None
    assert response["proofreader"] == {
        "verdict": "not_reached",
        "reason_code": "provider_content_invalid",
        "correction_eligible": False,
    }
    assert response["provider_metadata"] == expected_provider
    assert "unapproved_raw_field" not in response["metadata"]


@pytest.mark.parametrize(
    ("lane", "context_factory"),
    (
        (contracts.LANE_RAYLEEN, _rayleen_context),
        (contracts.LANE_DAVIDA, _davida_context),
    ),
)
def test_cell_request_binds_exact_context_and_provider_request_hash(
    lane: str, context_factory
) -> None:
    context = context_factory()
    packet = live._request_packet(
        lane,
        context,
        attempt_number=1,
        correction_of=None,
        correction_reason_code=None,
    )
    expected_request = contracts.provider_request_for_attempt(
        lane,
        context,
        attempt_number=1,
        correction_reason_code=None,
    )
    assert packet["context_hash"] == contracts.prefixed_sha256(context)
    assert packet["provider_request_hash"] == contracts.prefixed_sha256(
        expected_request
    )
    contracts.validate_instance(live.CELL_REQUEST_SCHEMA, packet)


def test_correction_request_is_hash_distinct_and_exactly_bound() -> None:
    context = _rayleen_context()
    primary = live._request_packet(
        contracts.LANE_RAYLEEN,
        context,
        attempt_number=1,
        correction_of=None,
        correction_reason_code=None,
    )
    correction = live._request_packet(
        contracts.LANE_RAYLEEN,
        context,
        attempt_number=2,
        correction_of=primary["attempt_id"],
        correction_reason_code="schema_invalid",
    )
    assert correction["context_hash"] == primary["context_hash"]
    assert correction["provider_request_hash"] != primary["provider_request_hash"]
    with pytest.raises(contracts.ContractError, match="attempt_contract_invalid"):
        contracts.provider_request_for_attempt(
            contracts.LANE_RAYLEEN,
            context,
            attempt_number=2,
            correction_reason_code="wrong_resource_kind",
        )


def test_single_use_attempt_ledgers_are_closed_and_mode_exact() -> None:
    packet = live._request_packet(
        contracts.LANE_DAVIDA,
        _davida_context(),
        attempt_number=1,
        correction_of=None,
        correction_reason_code=None,
    )
    dry = live._attempt_ledger(packet, mode="dry-run")
    occupied = live._attempt_ledger(packet, mode="live")
    assert (dry["maximum_provider_calls"], dry["reserved_cost_usd"]) == (0, 0)
    assert (occupied["maximum_provider_calls"], occupied["reserved_cost_usd"]) == (
        1,
        contracts.RESERVED_COST_PER_CALL_USD,
    )
    contracts.validate_instance(live.ATTEMPT_LEDGER_SCHEMA, dry)
    contracts.validate_instance(live.ATTEMPT_LEDGER_SCHEMA, occupied)


def test_parent_cost_ledger_blocks_lane_and_cumulative_overflow() -> None:
    ledger = live._initial_cost_ledger()
    ledger = live._reserve_cost(ledger, contracts.LANE_RAYLEEN, mode="live")
    ledger = live._reserve_cost(ledger, contracts.LANE_RAYLEEN, mode="live")
    with pytest.raises(live.LiveError, match="lane_call_ceiling_exceeded"):
        live._reserve_cost(ledger, contracts.LANE_RAYLEEN, mode="live")
    ledger = live._reserve_cost(ledger, contracts.LANE_DAVIDA, mode="live")
    ledger = live._reserve_cost(ledger, contracts.LANE_DAVIDA, mode="live")
    assert ledger["provider_calls_reserved"] == contracts.MAX_CALLS_TOTAL
    assert ledger["reserved_cost_usd"] == contracts.MAX_COST_USD
    with pytest.raises(live.LiveError, match="lane_call_ceiling_exceeded"):
        live._reserve_cost(ledger, contracts.LANE_DAVIDA, mode="live")


def test_provider_free_cost_reservation_consumes_no_call_or_budget() -> None:
    ledger = live._initial_cost_ledger()
    observed = live._reserve_cost(
        ledger, contracts.LANE_RAYLEEN, mode="dry-run"
    )
    assert observed == ledger
    assert observed is not ledger


def test_blocked_preflight_evidence_binds_exact_open_reservation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    relative_root = Path(
        "orchestration/continuity/model-required-bureau-a3-b3"
    )
    isolated_root = tmp_path / relative_root
    isolated_root.mkdir(parents=True)
    cost_ledger_path = isolated_root / "occupied-rehearsal-cost-ledger.json"
    blocked_evidence_path = isolated_root / "occupied-preflight-blocked-evidence.json"
    historical_open_ledger = live._reserve_cost(
        live._initial_cost_ledger(), contracts.LANE_RAYLEEN, mode="live"
    )
    live._write_json(cost_ledger_path, historical_open_ledger)
    shutil.copyfile(
        ARTIFACT_ROOT / "occupied-preflight-blocked-evidence.json",
        blocked_evidence_path,
    )
    monkeypatch.setattr(live, "ROOT", tmp_path)
    monkeypatch.setattr(live, "ARTIFACT_ROOT", isolated_root)
    observed = live._resume_preflight_blocked_cost_ledger(
        cost_ledger_path=cost_ledger_path,
        blocked_evidence_path=blocked_evidence_path,
    )
    assert observed == historical_open_ledger
    assert observed["provider_calls_reserved"] == 1
    assert observed["provider_calls_consumed"] == 0
    assert observed["lane_calls"] == {
        contracts.LANE_RAYLEEN: 1,
        contracts.LANE_DAVIDA: 0,
    }


def test_blocked_preflight_resume_rejects_ledger_hash_drift(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(live, "ROOT", tmp_path)
    relative = Path(
        "orchestration/continuity/model-required-bureau-a3-b3/"
        "occupied-rehearsal-cost-ledger.json"
    )
    cost_ledger_path = tmp_path / relative
    cost_ledger_path.parent.mkdir(parents=True)
    monkeypatch.setattr(live, "ARTIFACT_ROOT", cost_ledger_path.parent)
    ledger = live._reserve_cost(
        live._initial_cost_ledger(), contracts.LANE_RAYLEEN, mode="live"
    )
    cost_ledger_path.write_text(json.dumps(ledger), encoding="utf-8")
    blocked = _load("occupied-preflight-blocked-evidence.json")
    blocked["cost_ledger_sha256"] = live._file_hash(cost_ledger_path)
    blocked_evidence_path = tmp_path / "blocked.json"
    blocked_evidence_path.write_text(json.dumps(blocked), encoding="utf-8")

    admitted = live._resume_preflight_blocked_cost_ledger(
        cost_ledger_path=cost_ledger_path,
        blocked_evidence_path=blocked_evidence_path,
    )
    assert admitted == ledger

    ledger["provider_calls_consumed"] = 1
    cost_ledger_path.write_text(json.dumps(ledger), encoding="utf-8")
    with pytest.raises(live.LiveError, match="preflight_resume_binding_invalid"):
        live._resume_preflight_blocked_cost_ledger(
            cost_ledger_path=cost_ledger_path,
            blocked_evidence_path=blocked_evidence_path,
        )


def test_resume_reuses_rayleen_reservation_without_double_counting(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output_path = tmp_path / "occupied-evidence.json"
    cost_ledger_path = tmp_path / "occupied-cost-ledger.json"
    blocked_evidence_path = tmp_path / "blocked.json"
    source_review_path = tmp_path / "review.json"
    initial = live._reserve_cost(
        live._initial_cost_ledger(), contracts.LANE_RAYLEEN, mode="live"
    )
    cost_ledger_path.write_text(json.dumps(initial), encoding="utf-8")

    monkeypatch.setattr(
        live,
        "_resume_preflight_blocked_cost_ledger",
        lambda **_kwargs: deepcopy(initial),
    )
    monkeypatch.setattr(
        live,
        "_validate_source_review",
        lambda _path: {"model": "gemini-3.6-flash-high"},
    )
    monkeypatch.setattr(
        live,
        "_run_preflight",
        lambda _path: {"result": "preflight_pass"},
    )
    monkeypatch.setattr(
        live,
        "_run_attempt",
        lambda **kwargs: {
            "lane": kwargs["lane"],
            "proofreader_verdict": "admitted",
            "provider_call_count": 1,
        },
    )

    result = live.run_tranche(
        mode="live",
        output_path=output_path,
        cost_ledger_path=cost_ledger_path,
        source_review_path=source_review_path,
        resume_preflight_blocked_evidence_path=blocked_evidence_path,
    )
    ledger = json.loads(cost_ledger_path.read_text(encoding="utf-8"))
    assert result["candidate_runtime_provider_call_count"] == 2
    assert ledger["provider_calls_reserved"] == 2
    assert ledger["provider_calls_consumed"] == 2
    assert ledger["reserved_cost_usd"] == 0.5
    assert ledger["lane_calls"] == {
        contracts.LANE_RAYLEEN: 1,
        contracts.LANE_DAVIDA: 1,
    }
    assert ledger["status"] == "consumed"


@pytest.mark.parametrize(
    "lane", (contracts.LANE_RAYLEEN, contracts.LANE_DAVIDA)
)
def test_provider_free_and_occupied_attempt_artifacts_are_disjoint(
    lane: str,
) -> None:
    dry = live._attempt_paths(lane, 1, mode="dry-run")
    occupied = live._attempt_paths(lane, 1, mode="live")

    assert set(dry) == {"ledger", "audit", "evidence", "preflight"}
    assert set(occupied) == set(dry)
    assert dry["ledger"] != occupied["ledger"]
    assert dry["audit"] != occupied["audit"]
    assert dry["evidence"] != occupied["evidence"]
    assert dry["preflight"] == occupied["preflight"]
    assert "occupied" not in dry["ledger"].name
    assert "occupied" in occupied["ledger"].name


def test_current_terminal_audit_is_preproof_and_non_correction_eligible() -> None:
    events = live._read_events(
        ARTIFACT_ROOT / "rayleen-a3-attempt-1-occupied-audit.jsonl"
    )

    result = live._classify_attempt_events(events, mode="live")

    assert result == {
        "terminal_preproof_rejection": True,
        "reason_code": "provider_content_invalid",
        "correction_eligible": False,
        "provider_metadata": None,
    }
    tampered = deepcopy(events)
    tampered[-1]["fields"]["provider_contacted"] = False
    with pytest.raises(live.LiveError, match="broker_rejection_evidence_invalid"):
        live._classify_attempt_events(tampered, mode="live")


def test_terminal_rayleen_attempt_closes_parent_and_never_starts_davida(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output_path = tmp_path / "occupied-evidence.json"
    cost_ledger_path = tmp_path / "occupied-cost-ledger.json"
    blocked_evidence_path = tmp_path / "blocked.json"
    source_review_path = tmp_path / "review.json"
    initial = live._reserve_cost(
        live._initial_cost_ledger(), contracts.LANE_RAYLEEN, mode="live"
    )
    cost_ledger_path.write_text(json.dumps(initial), encoding="utf-8")
    calls: list[tuple[str, int]] = []

    monkeypatch.setattr(
        live,
        "_resume_preflight_blocked_cost_ledger",
        lambda **_kwargs: deepcopy(initial),
    )
    monkeypatch.setattr(
        live,
        "_validate_source_review",
        lambda _path: {"model": "gemini-3.6-flash-high"},
    )
    monkeypatch.setattr(
        live,
        "_run_preflight",
        lambda _path: {"result": "preflight_pass"},
    )

    def terminal_attempt(**kwargs: object) -> dict:
        lane = str(kwargs["lane"])
        attempt_number = int(kwargs["attempt_number"])
        calls.append((lane, attempt_number))
        return {
            "lane": lane,
            "attempt_number": attempt_number,
            "proofreader_verdict": "not_reached",
            "proofreader_reason_code": "provider_content_invalid",
            "correction_eligible": False,
            "provider_call_count": 1,
            "release": None,
        }

    monkeypatch.setattr(live, "_run_attempt", terminal_attempt)

    result = live.run_tranche(
        mode="live",
        output_path=output_path,
        cost_ledger_path=cost_ledger_path,
        source_review_path=source_review_path,
        resume_preflight_blocked_evidence_path=blocked_evidence_path,
    )
    ledger = json.loads(cost_ledger_path.read_text(encoding="utf-8"))

    assert calls == [(contracts.LANE_RAYLEEN, 1)]
    assert result["result"] == (
        "model_required_bureau_a3_b3_occupied_terminal_rejection"
    )
    assert result["combined_pass"] is False
    assert result["davida_b3_started"] is False
    assert result["candidate_runtime_provider_call_count"] == 1
    assert ledger["status"] == "consumed"
    assert ledger["provider_calls_reserved"] == 1
    assert ledger["provider_calls_consumed"] == 1


def test_interrupted_terminal_reconciliation_is_provider_free_and_idempotent(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    artifact_root = (
        tmp_path / "orchestration/continuity/model-required-bureau-a3-b3"
    )
    artifact_root.mkdir(parents=True)
    for name in (
        "occupied-preflight-blocked-evidence.json",
        "occupied-terminal-interruption-evidence.json",
        "occupied-rehearsal-cost-ledger.json",
        "rayleen-a3-attempt-1-preflight.json",
        "rayleen-a3-attempt-1-occupied-ledger.json",
        "rayleen-a3-attempt-1-occupied-audit.jsonl",
    ):
        shutil.copyfile(ARTIFACT_ROOT / name, artifact_root / name)
    monkeypatch.setattr(live, "ARTIFACT_ROOT", artifact_root)
    monkeypatch.setattr(
        live, "SOURCE_REVIEW_RECEIPT", tmp_path / "review.json"
    )
    monkeypatch.setattr(live, "_git_head", lambda: "reconciliation-head")
    monkeypatch.setattr(live, "_tracked_worktree_clean", lambda: True)
    monkeypatch.setattr(live, "_paths_match_head", lambda _paths: True)
    monkeypatch.setattr(
        live,
        "_historical_source_review",
        lambda _path, current_head: {
            "model": "gemini-3.6-flash-high",
            "head_before": (
                "61ca38545ad01d2470f8b5b668dd746b88d113a2"
            ),
        },
    )
    monkeypatch.setattr(
        live,
        "_exact_runtime_absence",
        lambda _lane, _attempt: {
            "cell_container_absent": True,
            "relay_container_absent": True,
            "internal_network_absent": True,
            "cell_image_absent": True,
            "relay_image_absent": True,
        },
    )
    output_path = artifact_root / "occupied-rehearsal-evidence.json"
    cost_path = artifact_root / "occupied-rehearsal-cost-ledger.json"

    first = live.reconcile_terminal_failure(
        output_path=output_path,
        cost_ledger_path=cost_path,
        source_review_path=tmp_path / "review.json",
    )
    second = live.reconcile_terminal_failure(
        output_path=output_path,
        cost_ledger_path=cost_path,
        source_review_path=tmp_path / "review.json",
    )
    ledger = json.loads(cost_path.read_text(encoding="utf-8"))
    attempt = json.loads(
        (
            artifact_root
            / "rayleen-a3-attempt-1-occupied-evidence.json"
        ).read_text(encoding="utf-8")
    )

    assert first == second
    assert first["reconciliation_was_provider_free"] is True
    assert first["candidate_runtime_provider_call_count"] == 1
    assert first["terminal_reason_code"] == "provider_content_invalid"
    assert first["correction_eligible"] is False
    assert first["davida_b3_started"] is False
    assert ledger["status"] == "consumed"
    assert ledger["provider_calls_consumed"] == 1
    assert attempt["result"] == "attempt_terminal_rejection"
    assert attempt["provider_metadata_status"] == "not_durably_recorded"
    assert attempt["current_runtime_residue_absent"] is True
    assert attempt["original_attempt_cleanup_evidence_status"] == (
        "not_durably_recorded_beyond_immutable_interruption_assertion"
    )

    monkeypatch.setattr(
        live,
        "_historical_source_review",
        lambda _path, current_head: {
            "model": "gemini-3.6-flash-high",
            "head_before": "stale-review-head",
        },
    )
    with pytest.raises(
        live.LiveError, match="historical_source_review_head_not_exact"
    ):
        live.reconcile_terminal_failure(
            output_path=output_path,
            cost_ledger_path=cost_path,
            source_review_path=tmp_path / "review.json",
        )
    monkeypatch.setattr(
        live,
        "_historical_source_review",
        lambda _path, current_head: {
            "model": "gemini-3.6-flash-high",
            "head_before": (
                "61ca38545ad01d2470f8b5b668dd746b88d113a2"
            ),
        },
    )

    unexpected = artifact_root / "rayleen-a3-attempt-3-occupied-ledger.json"
    unexpected.write_text("{}\n", encoding="utf-8")
    with pytest.raises(
        live.LiveError, match="terminal_reconciliation_later_attempt_present"
    ):
        live.reconcile_terminal_failure(
            output_path=output_path,
            cost_ledger_path=cost_path,
            source_review_path=tmp_path / "review.json",
        )


def test_terminal_reconciliation_requires_canonical_paths(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    artifact_root = tmp_path / "canonical"
    monkeypatch.setattr(live, "ARTIFACT_ROOT", artifact_root)
    monkeypatch.setattr(
        live, "SOURCE_REVIEW_RECEIPT", tmp_path / "review.json"
    )

    with pytest.raises(
        live.LiveError, match="terminal_reconciliation_path_binding_invalid"
    ):
        live.reconcile_terminal_failure(
            output_path=tmp_path / "other-output.json",
            cost_ledger_path=artifact_root
            / "occupied-rehearsal-cost-ledger.json",
            source_review_path=tmp_path / "review.json",
        )


def test_terminal_reconciliation_requires_head_exact_tracked_inputs(
    tmp_path: Path,
) -> None:
    assert live._paths_match_head(
        [ROOT / "scripts/model_required_bureau_a3_b3_contracts.py"]
    )
    outside = tmp_path / "untracked.json"
    outside.write_text("{}\n", encoding="utf-8")
    assert live._paths_match_head([outside]) is False
