"""Focused deterministic tests for the model-required intent-shaping rehearsal."""

from __future__ import annotations

import ast
from copy import deepcopy
from datetime import datetime, timedelta, timezone
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
    build_prompt,
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
    verify_seal,
)
from scripts.raisa_provider_free_practice_context_fabric_intent_shaped_temporal_retrieval_rehearsal import (
    proofread_intent_packet,
)
from scripts import (
    model_required_bureau_a3_b3_broker as broker,
    raisa_authored_synthetic_model_required_practice_context_fabric_intent_shaping_broker as intent_broker,
    raisa_authored_synthetic_model_required_practice_context_fabric_intent_shaping_contracts as contracts,
    raisa_authored_synthetic_model_required_practice_context_fabric_intent_shaping_live as intent_live,
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


def _cell_request(
    context: dict,
    *,
    attempt_number: int = 1,
    correction_of=None,
    correction_reason_code=None,
) -> dict:
    return intent_live._request_packet(
        contracts.LANE,
        context,
        attempt_number=attempt_number,
        correction_of=correction_of,
        correction_reason_code=correction_reason_code,
    )


class _FakeBrokerState:
    """Minimal broker state for exercising ``intent_broker._execute`` directly.

    Dry-run and live paths are exercised without Docker, credentials or a
    provider transport: the dry-run packet or a stubbed provider call supplies
    the provider response, and the ledger/audit side effects are in-memory.
    """

    def __init__(self, *, mode: str, context: dict, expected_request: dict) -> None:
        self.mode = mode
        self.context = context
        self.expected_request = expected_request
        self.events: list[dict] = []
        self._claimed = False
        self._dry_run_packet_impl = None
        self._provider_call_impl = None

    def claim_once(self) -> None:
        if self._claimed:
            raise broker.BrokerError("broker_already_used")
        self._claimed = True

    def append_event(self, event_type: str, fields: dict) -> None:
        self.events.append({"event_type": event_type, "fields": dict(fields)})

    def consume_ledger(self) -> dict:
        return {"status": "consumed"}

    def _provider_request(self) -> dict:
        return contracts.provider_request_for_attempt(
            self.context,
            attempt_number=self.expected_request["attempt_number"],
            correction_reason_code=self.expected_request[
                "correction_reason_code"
            ],
        )

    def _dry_run_packet(self) -> dict:
        if self._dry_run_packet_impl is not None:
            return self._dry_run_packet_impl()
        return contracts.build_dry_run_provider_packet()

    def _provider_call(self, provider_request: dict):
        if self._provider_call_impl is None:
            raise AssertionError("provider must not be contacted in dry-run")
        return self._provider_call_impl(provider_request)


def _live_call_metadata() -> dict:
    return {
        "provider_contacted": True,
        "http_status": 200,
        "latency_ms": 1,
        "discarded_provider_response_sha256": "sha256:" + "0" * 64,
        "provider_response_bytes": 10,
        "raw_provider_response_retained": False,
    }


def _live_packet(usage: dict) -> dict:
    body = canonical_model_body_fixture(
        "CURRENT_AND_PRIOR_OPERATIONAL_COMPARISON"
    )
    return {
        "candidates": [
            {
                "finishReason": "STOP",
                "content": {"parts": [{"text": json.dumps(body)}]},
            }
        ],
        "usageMetadata": usage,
        "modelVersion": contracts.MODEL,
    }


def _current_head() -> str:
    import subprocess

    return subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        shell=False,
    ).stdout.strip()


def _valid_source_review_receipt(head: str) -> dict:
    return {
        "schema_version": "emr4.raisa_intent_shaping.source_review.v1",
        "status": "passed",
        "decision": "pass",
        "independent_read_only_review": True,
        "provider_called": False,
        "source_hashes": intent_live._review_source_hashes(),
        "closed_boundary_verified": True,
        "head_before": head,
        "head_after": head,
        "dirty_after": False,
    }


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


def test_all_schema_positions_are_structurally_bounded() -> None:
    def _walk(value, path="$") -> None:
        if isinstance(value, dict):
            if value.get("type") == "object":
                additional = value.get("additionalProperties")
                typed_map = (
                    isinstance(additional, dict)
                    and "propertyNames" in value
                    and type(value.get("maxProperties")) is int
                )
                assert additional is False or typed_map, path
            if value.get("type") == "array":
                assert "items" in value, path
            for key, item in value.items():
                _walk(item, f"{path}.{key}")
        elif isinstance(value, list):
            for index, item in enumerate(value):
                _walk(item, f"{path}[{index}]")

    for path in ARTIFACT_ROOT.glob("*.schema.json"):
        _walk(_load(path))


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
    assert "uniqueItems" not in json.dumps(generation["responseSchema"])
    local_schema = _load(ARTIFACT_ROOT / "provider-intent-body.schema.json")
    assert local_schema["properties"]["cue_codes"]["uniqueItems"] is True
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


def test_prompt_requires_canonical_cue_codes_order() -> None:
    intent_request = _request()
    vertex_request = build_vertex_request(intent_request)
    prompt = vertex_request["contents"][0]["parts"][0]["text"]
    assert build_prompt(intent_request) == prompt
    assert (
        "Return cue_codes in the canonical CUE_CODES order displayed above."
        in prompt
    )
    cue_block = prompt.split("CUE_CODES:", 1)[1].split(
        "Return cue_codes", 1
    )[0]
    assert cue_block.strip() == ", ".join(intent_request["cue_codes"])


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


def test_source_review_binds_exact_head_and_tracked_worktree(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    acceptance_rel = (
        "scripts/"
        "raisa_authored_synthetic_model_required_practice_context_fabric_intent_shaping_acceptance.py"
    )
    head = _current_head()
    monkeypatch.setattr(
        intent_live.live, "_tracked_worktree_clean", lambda: True
    )

    def _write(name: str, receipt: dict) -> Path:
        path = tmp_path / name
        path.write_text(json.dumps(receipt), encoding="utf-8")
        return path

    # A valid receipt at the current candidate HEAD passes.
    ok = _write("ok.json", _valid_source_review_receipt(head))
    assert (
        intent_live._validate_source_review(ok, expected_path=ok)["decision"]
        == "pass"
    )

    # Wrong HEAD fails closed.
    wrong_head = _write(
        "wrong-head.json",
        _valid_source_review_receipt("sha256:" + "0" * 64),
    )
    with pytest.raises(
        intent_live.live.LiveError, match="independent_source_review_not_exact"
    ):
        intent_live._validate_source_review(wrong_head, expected_path=wrong_head)

    # Dirty review fails closed.
    dirty = _valid_source_review_receipt(head)
    dirty["dirty_after"] = True
    dirty_path = _write("dirty.json", dirty)
    with pytest.raises(
        intent_live.live.LiveError, match="independent_source_review_not_exact"
    ):
        intent_live._validate_source_review(dirty_path, expected_path=dirty_path)

    # head_before != head_after fails closed.
    unequal = _valid_source_review_receipt(head)
    unequal["head_after"] = "sha256:" + "0" * 64
    unequal_path = _write("unequal.json", unequal)
    with pytest.raises(
        intent_live.live.LiveError, match="independent_source_review_not_exact"
    ):
        intent_live._validate_source_review(
            unequal_path, expected_path=unequal_path
        )

    # Missing acceptance generator hash fails closed.
    missing = _valid_source_review_receipt(head)
    missing["source_hashes"] = {
        key: value
        for key, value in missing["source_hashes"].items()
        if key != acceptance_rel
    }
    missing_path = _write("missing-acceptance.json", missing)
    with pytest.raises(
        intent_live.live.LiveError, match="independent_source_review_not_exact"
    ):
        intent_live._validate_source_review(
            missing_path, expected_path=missing_path
        )

    # Stale acceptance generator hash fails closed.
    stale = _valid_source_review_receipt(head)
    stale["source_hashes"] = dict(stale["source_hashes"])
    stale["source_hashes"][acceptance_rel] = "sha256:" + "0" * 64
    stale_path = _write("stale-acceptance.json", stale)
    with pytest.raises(
        intent_live.live.LiveError, match="independent_source_review_not_exact"
    ):
        intent_live._validate_source_review(stale_path, expected_path=stale_path)

    # Tracked worktree drift fails closed while untracked files remain
    # permitted (the monkeypatched clean check is False only here).
    monkeypatch.setattr(
        intent_live.live, "_tracked_worktree_clean", lambda: False
    )
    drift_path = _write("tracked-drift.json", _valid_source_review_receipt(head))
    with pytest.raises(
        intent_live.live.LiveError, match="independent_source_review_not_exact"
    ):
        intent_live._validate_source_review(
            drift_path, expected_path=drift_path
        )


def test_reviewed_sources_include_the_acceptance_generator() -> None:
    reviewed = {
        path.relative_to(ROOT).as_posix()
        for path in intent_live.REVIEWED_SOURCE_PATHS
    }
    assert (
        "scripts/"
        "raisa_authored_synthetic_model_required_practice_context_fabric_intent_shaping_acceptance.py"
        in reviewed
    )
    assert (
        "scripts/"
        "raisa_authored_synthetic_model_required_practice_context_fabric_intent_shaping_contracts.py"
        in reviewed
    )
    assert (
        "tests/"
        "test_raisa_authored_synthetic_model_required_practice_context_fabric_intent_shaping_rehearsal.py"
        in reviewed
    )
    assert len(reviewed) >= 13


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


@pytest.mark.parametrize(
    "usage",
    (
        {
            "promptTokenCount": 0,
            "candidatesTokenCount": 0,
            "thoughtsTokenCount": 0,
            "totalTokenCount": 0,
        },
        {"promptTokenCount": 0, "candidatesTokenCount": 0, "totalTokenCount": 0},
        {
            "promptTokenCount": 0,
            "candidatesTokenCount": 0,
            "thoughtsTokenCount": "1024",
            "totalTokenCount": 0,
        },
    ),
)
def test_live_non_positive_thinking_is_terminal_preproof_and_no_release(
    usage: dict,
) -> None:
    context = _request()
    packet = _cell_request(context)
    state = _FakeBrokerState(mode="live", context=context, expected_request=packet)
    state._provider_call_impl = lambda _provider_request: (
        _live_packet(usage),
        _live_call_metadata(),
    )
    with pytest.raises(
        broker.BrokerError, match="positive_thinking_evidence_required"
    ) as excinfo:
        intent_broker._execute(state, packet)
    assert excinfo.value.reason_code == "positive_thinking_evidence_required"
    assert excinfo.value.metadata.get("provider_contacted") is True
    assert state._claimed is True
    event_types = [event["event_type"] for event in state.events]
    assert "provider_call_completed" in event_types
    assert "release_committed" not in event_types
    assert "proofreader_completed" not in event_types
    assert contracts.positive_thinking_evidence(
        {"usage": usage}
    ) is False


def test_dry_run_zero_thinking_remains_eligible() -> None:
    context = _request()
    packet = _cell_request(context)
    state = _FakeBrokerState(mode="dry-run", context=context, expected_request=packet)
    result = intent_broker._execute(state, packet)
    assert result["status"] == "completed"
    assert result["proofreader"]["verdict"] == "admitted"
    assert result["release"] is not None
    assert state.events[-1]["event_type"] == "release_committed"
    assert result["provider_metadata"]["usage"]["thoughtsTokenCount"] == 0


def test_schema_invalid_provider_body_reaches_eligible_correction_path() -> None:
    context = _request()
    packet = _cell_request(context)
    state = _FakeBrokerState(mode="dry-run", context=context, expected_request=packet)
    invalid_body = deepcopy(
        canonical_model_body_fixture(
            "CURRENT_AND_PRIOR_OPERATIONAL_COMPARISON"
        )
    )
    invalid_body["prose"] = "unexpected field value"
    expected_hash = prefixed_sha256(invalid_body)
    state._dry_run_packet_impl = lambda: {
        "candidates": [
            {
                "finishReason": "STOP",
                "content": {
                    "parts": [{"text": json.dumps(invalid_body)}]
                },
            }
        ],
        "usageMetadata": {
            "promptTokenCount": 0,
            "candidatesTokenCount": 0,
            "thoughtsTokenCount": 0,
            "totalTokenCount": 0,
        },
        "modelVersion": contracts.DRY_RUN_MODEL_VERSION,
    }
    result = intent_broker._execute(state, packet)
    assert result["status"] == "completed"
    assert result["release"] is None
    assert result["proofreader"]["reason_code"] == (
        "provider_body_schema_invalid"
    )
    assert result["proofreader"]["correction_eligible"] is True
    assert result["proofreader"]["candidate_hash"] == expected_hash
    # The invalid object is hashed and discarded; no release is created and no
    # unexpected field name or value survives in audit/evidence.
    assert "release_committed" not in [
        event["event_type"] for event in state.events
    ]
    audit_raw = json.dumps(state.events)
    assert "unexpected field value" not in audit_raw
    assert "prose" not in audit_raw
    result_raw = json.dumps(result)
    assert "unexpected field value" not in result_raw
    assert "prose" not in result_raw


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
    assert "uniqueItems" not in properties["cue_codes"]
    assert properties["response_code"]["enum"] == ["INTENT_CANDIDATE_ONLY"]
    for key in AUTHORITY_KEYS:
        assert key in properties


def test_fresh_live_request_is_short_lived_and_broker_enforced() -> None:
    now = datetime(2026, 8, 6, 7, 30, tzinfo=timezone.utc)
    request = intent_live._fresh_live_request(now=now)
    assert request["issued_at"] == "2026-08-06T07:30:00Z"
    assert request["expires_at"] == "2026-08-06T07:40:00Z"
    assert _errors(
        ARTIFACT_ROOT / "intent-shaping-request.schema.json", request
    ) == []
    intent_broker._validate_live_request_freshness(request, now=now)
    intent_broker._validate_live_request_freshness(
        request, now=now + timedelta(seconds=599)
    )
    with pytest.raises(broker.BrokerError, match="live_request_not_fresh"):
        intent_broker._validate_live_request_freshness(
            request, now=now + timedelta(seconds=600)
        )
    with pytest.raises(broker.BrokerError, match="live_request_not_fresh"):
        intent_broker._validate_live_request_freshness(
            request, now=now - timedelta(seconds=1)
        )
    with pytest.raises(broker.BrokerError, match="live_request_clock_invalid"):
        intent_broker._validate_live_request_freshness(
            request, now=datetime(2026, 8, 6, 7, 30)
        )
    wrong_lifetime = build_intent_shaping_request(
        issued_at="2026-08-06T07:30:00Z",
        expires_at="2026-08-06T07:39:59Z",
    )
    with pytest.raises(broker.BrokerError, match="live_request_lifetime_invalid"):
        intent_broker._validate_live_request_freshness(
            wrong_lifetime, now=now
        )


def test_committed_provider_free_request_fixture_remains_deterministic() -> None:
    assert build_intent_shaping_request() == _load(
        ARTIFACT_ROOT / "authored-synthetic-intent-shaping-request.json"
    )
    with pytest.raises(
        intent_live.live.LiveError,
        match="live_request_date_outside_frozen_plan",
    ):
        intent_live._fresh_live_request(
            now=datetime(2026, 8, 7, tzinfo=timezone.utc)
        )


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


def test_release_is_immutable_after_envelope_zeroisation() -> None:
    request = _request()
    body = canonical_model_body_fixture(
        "CURRENT_AND_PRIOR_OPERATIONAL_COMPARISON"
    )
    envelope = _envelope(request, body)
    proof = proofread_intent_candidate(request, envelope, ground_to_case=True)
    assert proof["verdict"] == "admitted"
    release = proof["released"]
    nested_envelope = deepcopy(release["model_intent_candidate_envelope"])
    nested_body = deepcopy(release["model_intent_candidate_envelope"]["body"])
    nested_parent_packet = deepcopy(release["parent_packet"])
    nested_parent_trace = deepcopy(release["parent_proofreader_trace"])

    # Simulate broker zeroisation after admission.
    envelope["body"].clear()
    envelope.clear()

    # The released envelope, nested body and parent material remain intact.
    assert release["model_intent_candidate_envelope"] == nested_envelope
    assert release["model_intent_candidate_envelope"]["body"] == nested_body
    assert release["parent_packet"] == nested_parent_packet
    assert release["parent_proofreader_trace"] == nested_parent_trace
    assert (
        release["model_intent_candidate_envelope"]["body"]["intent_code"]
        == "CURRENT_AND_PRIOR_OPERATIONAL_COMPARISON"
    )
    assert release["model_intent_candidate_envelope"]["body"]["cue_codes"] == list(
        CUE_CODES
    )

    # Both the release digest and the nested envelope digest remain valid.
    verify_seal(release, "release_digest")
    verify_seal(release["model_intent_candidate_envelope"], "envelope_digest")
    contracts.validate_release_integrity(release)


def test_release_integrity_rejects_nested_tamper_even_after_outer_reseal() -> None:
    request = _request()
    body = canonical_model_body_fixture(
        "CURRENT_AND_PRIOR_OPERATIONAL_COMPARISON"
    )
    proof = proofread_intent_candidate(
        request, _envelope(request, body), ground_to_case=True
    )
    tampered = deepcopy(proof["released"])
    tampered["model_intent_candidate_envelope"]["body"]["cue_codes"].pop()
    tampered.pop("release_digest")
    tampered = seal(tampered, "release_digest")
    with pytest.raises(ContractError, match="release_integrity_invalid"):
        contracts.validate_release_integrity(tampered)


def test_final_attempt_summary_is_closed_digest_only(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    request = _request()
    body = canonical_model_body_fixture(
        "CURRENT_AND_PRIOR_OPERATIONAL_COMPARISON"
    )
    release = proofread_intent_candidate(
        request, _envelope(request, body), ground_to_case=True
    )["released"]
    evidence_path = (
        tmp_path
        / "orchestration/continuity"
        / "raisa-authored-synthetic-model-required-practice-context-fabric-intent-shaping-rehearsal"
        / "rayleen-context-fabric-intent-shaping-attempt-1-dry-run-evidence.json"
    )
    evidence_path.parent.mkdir(parents=True)
    evidence_path.write_text('{"sealed":"attempt"}\n', encoding="utf-8")
    monkeypatch.setattr(intent_live, "ROOT", tmp_path)
    monkeypatch.setattr(
        intent_live.live,
        "_attempt_paths",
        lambda *_args, **_kwargs: {"evidence": evidence_path},
    )
    attempt = {
        "result": "attempt_pass",
        "mode": "dry-run",
        "lane": contracts.LANE,
        "attempt_id": "raisa-intent-shaping-primary-001",
        "attempt_number": 1,
        "provider_contacted": False,
        "provider_call_count": 0,
        "proofreader_verdict": "admitted",
        "proofreader_reason_code": None,
        "correction_eligible": False,
        "cleanup_passed": True,
        "evidence_hash": prefixed_sha256({"sealed": "attempt"}),
        "release": release,
        "provider_metadata": {"raw": "must not survive"},
    }
    summary = intent_live._attempt_summary(attempt)
    raw = json.dumps(summary)
    assert "provider_metadata" not in summary
    assert "release" not in summary
    assert "must not survive" not in raw
    assert summary["release_digest"] == release["release_digest"]
    assert summary["parent_packet_digest"] == (
        release["parent_packet"]["contract_digest"]
    )
    schema = _load(ARTIFACT_ROOT / "occupied-rehearsal-evidence.schema.json")
    summary_schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$defs": schema["$defs"],
        **schema["$defs"]["attempt_summary"],
    }
    assert list(
        Draft202012Validator(summary_schema).iter_errors(summary)
    ) == []


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
