"""Provider-free deterministic tests for the Bureau A3/B3 rehearsal.

These tests exercise only repository contracts and pure proofreader/request
builders.  They never open credentials, a provider, a network connection, a
database, Docker, a product route or an actuator.
"""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path

import pytest

from scripts import model_required_bureau_a3_b3_contracts as contracts
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
