"""Hostile deterministic tests for the AES-C5 provider-free containment core.

All tests are provider-free, database-free and use newly authored synthetic
values only.  No network, ADC, token, TestClient, SQLAlchemy engine/session or
subprocess is used.
"""

from __future__ import annotations

import contextlib
import copy
import io
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from scripts import (
    raisa_agent_execution_surface_containment_gate_aes_c5_product_runtime_admission as mod,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE_HEAD = "1e2756f15eb3ff3fe051b72855d773b4a82ff6a6"
T0 = datetime(2026, 8, 11, 0, 0, 0, tzinfo=timezone.utc)

UUID_A = "3f2c7b1a-9d8e-4f6a-8b1c-2e5d7a9b0c1d"
UUID_B = "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d"
UUID_C = "6d5c4b3a-2f1e-4d0c-9b8a-7f6e5d4c3b2a"
FIXTURE_UUIDS = [UUID_A, UUID_B, UUID_C]
FIXTURE_NAMES = [
    "Aster Finch",
    "Marlow Quill",
    "Nyra Sol",
    "General Practitioner",
    "Practice Nurse",
]
FIXTURE_ALIASES = [
    "practitioner-choice-001",
    "practitioner-choice-002",
    "practitioner-choice-003",
]

WRONG_DIGEST = "sha256:" + "9" * 64


def _row(**overrides: object) -> dict[str, object]:
    base: dict[str, object] = {
        "id": UUID_A,
        "displayName": "Aster Finch",
        "roleLabel": "General Practitioner",
        "active": True,
        "defaultLocation": None,
    }
    base.update(overrides)
    return base


def _full_rows() -> list[dict[str, object]]:
    return [
        _row(),
        _row(id=UUID_B, displayName="Marlow Quill"),
        _row(
            id=UUID_C,
            displayName="Nyra Sol",
            roleLabel="Practice Nurse",
            defaultLocation=None,
        ),
    ]


def _source_result(rows: list[dict[str, object]]) -> mod.SourceResult:
    return mod.SourceResult(
        rows=rows,
        metadata={
            "fixture_used": True,
            "provider_contacted": False,
            "route": "/api/v1/practice/practitioners",
            "row_count": len(rows),
        },
    )


def _make_packet(text: str) -> mod.ProviderResult:
    return mod.ProviderResult(
        packet={
            "modelVersion": "gemini-2.5-flash",
            "candidates": [
                {
                    "finishReason": "STOP",
                    "content": {
                        "role": "model",
                        "parts": [{"text": text}],
                    },
                }
            ],
            "usageMetadata": {
                "promptTokenCount": 128,
                "candidatesTokenCount": 32,
                "thoughtsTokenCount": 64,
                "totalTokenCount": 224,
            },
        },
        metadata={
            "provider_contacted": False,
            "http_status": 200,
            "latency_ms": 0,
            "provider_text_retained": False,
            "fixture_used": True,
            "request_digest": mod.ZERO_HASH,
            "response_digest": mod.ZERO_HASH,
        },
    )


def _release_text(frame: dict[str, object], **overrides: object) -> str:
    release: dict[str, object] = {
        "decision_code": "active_practitioner_choice_matched",
        "selected_practitioner_ref": frame["target_alias"],
        "context_frame_set_digest": frame["context_frame_set_digest"],
        "command_authority": False,
    }
    release.update(overrides)
    return mod.canonical_bytes(release).decode("utf-8")


def _tmp_paths(tmp_path: Path) -> tuple[Path, Path]:
    return tmp_path / "evidence.json", tmp_path / "ledgers"


def _execute(tmp_path: Path, **kwargs: object) -> dict[str, object]:
    evidence_output, ledger_output = _tmp_paths(tmp_path)
    execution_kwargs: dict[str, object] = {"now": T0}
    execution_kwargs.update(kwargs)
    return mod.execute(
        mode="provider-free",
        source_head=SOURCE_HEAD,
        evidence_output=evidence_output,
        ledger_output=ledger_output,
        **execution_kwargs,
    )


def _walk(value: object):
    if isinstance(value, dict):
        for key, item in value.items():
            yield key, item
            yield from _walk(item)
    elif isinstance(value, list):
        for item in value:
            yield from _walk(item)


def _collect_strings(value: object, found: list[str]) -> None:
    if isinstance(value, dict):
        for item in value.values():
            _collect_strings(item, found)
    elif isinstance(value, list):
        for item in value:
            _collect_strings(item, found)
    elif isinstance(value, str):
        found.append(value)


# ---------------------------------------------------------------------------
# Envelope, inherited digests, generation
# ---------------------------------------------------------------------------

def test_envelope_validates_against_schema_and_frozen_values():
    envelope = mod.validate_envelope()
    assert envelope["schema_version"] == "emr4.aes_c5.product_runtime_envelope.v1"
    assert envelope["source_boundary"]["route"] == "/api/v1/practice/practitioners"


def test_envelope_frozen_value_drift_rejected():
    envelope = mod.validate_envelope()
    drifted = copy.deepcopy(envelope)
    drifted["source_boundary"]["query"] = "activeOnly=false&limit=9&offset=9"
    with pytest.raises(mod.AesC5Error) as exc:
        mod.validate_envelope_values(drifted)
    assert exc.value.reason_code == "product_runtime_envelope_frozen_value_invalid"


def test_envelope_schema_drift_rejected():
    from jsonschema import Draft202012Validator
    schema = json.loads(mod.ENVELOPE_SCHEMA_PATH.read_text(encoding="utf-8"))
    drifted = copy.deepcopy(mod.validate_envelope())
    # The root schema forbids additional top-level properties.
    drifted["forged_extra_top_level"] = True
    errors = list(Draft202012Validator(schema).iter_errors(drifted))
    assert errors


def test_envelope_nested_extra_key_rejected_by_exact_freezer():
    drifted = copy.deepcopy(mod.validate_envelope())
    drifted["source_boundary"]["forged_nested_selector"] = "value"
    with pytest.raises(mod.AesC5Error) as exc:
        mod.validate_envelope_values(drifted)
    assert exc.value.reason_code == "product_runtime_envelope_key_set_invalid"


def test_inherited_artifact_digest_drift_rejected(monkeypatch):
    tampered = dict(mod.INHERITED_ARTIFACT_DIGESTS)
    key = (
        "orchestration/continuity/raisa-agent-execution-surface-"
        "containment-gate-aes-c4/provider-envelope.json"
    )
    tampered[key] = WRONG_DIGEST
    monkeypatch.setattr(mod, "INHERITED_ARTIFACT_DIGESTS", tampered)
    with pytest.raises(mod.AesC5Error) as exc:
        mod.validate_inherited_artifacts()
    assert exc.value.reason_code == "inherited_artifact_digest_mismatch"


def _read_manifest():
    envelope = mod.validate_envelope()
    return mod.build_generation_manifest(
        envelope, capability_class="authoritative_read", now=T0
    )


def _provider_manifest():
    envelope = mod.validate_envelope()
    return mod.build_generation_manifest(
        envelope,
        capability_class="provider_inference",
        now=T0,
        context_frame_set_digest=WRONG_DIGEST,
    )


def test_two_generations_have_one_exact_grant_and_destination_each():
    read_manifest = _read_manifest()
    provider_manifest = _provider_manifest()
    mod.validate_generation(
        read_manifest, expected_capability_class="authoritative_read"
    )
    mod.validate_generation(
        provider_manifest, expected_capability_class="provider_inference"
    )
    assert [g["capability_class"] for g in read_manifest["capability_grants"]] == [
        "authoritative_read"
    ]
    assert [
        g["capability_class"] for g in provider_manifest["capability_grants"]
    ] == ["provider_inference"]
    assert read_manifest["budgets"]["egress"]["max_distinct_destinations"] == 1
    assert provider_manifest["budgets"]["egress"]["max_distinct_destinations"] == 1
    assert read_manifest["generation_id"] != provider_manifest["generation_id"]


def test_both_generation_attempts_pass_exact_c1_schema_without_budget_transfer():
    envelope, frame = _frame()
    read_manifest = _read_manifest()
    read_attempt, _, _ = mod.build_read_attempt(read_manifest, envelope, now=T0)
    assert mod.c1.validate_attempt(read_attempt) == []
    provider_manifest = mod.build_generation_manifest(
        envelope,
        capability_class="provider_inference",
        now=T0,
        context_frame_set_digest=frame["context_frame_set_digest"],
    )
    request = mod.build_vertex_request(frame, envelope)
    provider_attempt, _, _ = mod.build_provider_attempt(
        provider_manifest,
        envelope,
        frame,
        request,
        now=T0,
        observed={counter: 0 for counter in mod.c1.COUNTER_KEYS},
    )
    assert mod.c1.validate_attempt(provider_attempt) == []
    assert all(value == 0 for value in provider_attempt["budget_state"]["observed"].values())
    assert provider_manifest["supply_chain_identity"]["system_contract_digest"] != (
        read_manifest["supply_chain_identity"]["system_contract_digest"]
    )


def test_two_destination_generation_fails_exact_c1_schema():
    envelope = mod.validate_envelope()
    manifest = _read_manifest()
    manifest["budgets"]["egress"]["max_distinct_destinations"] = 2
    manifest["manifest_digest"] = mod.c1.compute_manifest_digest(manifest)
    manifest["supply_chain_identity"]["generation_manifest_digest"] = manifest[
        "manifest_digest"
    ]
    attempt, _, _ = mod.build_read_attempt(manifest, envelope, now=T0)
    assert any(
        "max_distinct_destinations:const" in error
        for error in mod.c1.validate_attempt(attempt)
    )


def test_missing_or_extra_grant_rejected():
    manifest = _read_manifest()
    missing = copy.deepcopy(manifest)
    missing["capability_grants"] = []
    with pytest.raises(mod.AesC5Error) as exc:
        mod.validate_generation(
            missing, expected_capability_class="authoritative_read"
        )
    assert exc.value.reason_code == "generation_schema_invalid"
    extra = copy.deepcopy(manifest)
    extra["capability_grants"].append(mod._provider_grant())
    with pytest.raises(mod.AesC5Error):
        mod.validate_generation(extra, expected_capability_class="authoritative_read")


def test_wrong_grant_class_route_method_provider_destination_rejected():
    cases = [
        (_read_manifest, "authoritative_read", "capability_class", "inert_tool_adapter"),
        (_read_manifest, "authoritative_read", "method", "POST"),
        (_read_manifest, "authoritative_read", "destination_id", "somewhere-else"),
        (_provider_manifest, "provider_inference", "destination_id", "vertex-elsewhere"),
        (_provider_manifest, "provider_inference", "method", "GET"),
        (_provider_manifest, "provider_inference", "audience", "other-audience"),
    ]
    for factory, expected_class, field, value in cases:
        manifest = factory()
        mutated = copy.deepcopy(manifest)
        mutated["capability_grants"][0][field] = value
        with pytest.raises(mod.AesC5Error) as exc:
            mod.validate_generation(
                mutated, expected_capability_class=expected_class
            )
        assert exc.value.reason_code in {
            "generation_schema_invalid",
            "generation_capability_classes_invalid",
            "generation_read_grant_invalid",
            "generation_provider_grant_invalid",
        }


def test_wrong_query_frozen_value_rejected():
    envelope = mod.validate_envelope()
    drifted = copy.deepcopy(envelope)
    drifted["source_boundary"]["query"] = "activeOnly=true&limit=99"
    with pytest.raises(mod.AesC5Error) as exc:
        mod.validate_envelope_values(drifted)
    assert exc.value.reason_code == "product_runtime_envelope_frozen_value_invalid"


# ---------------------------------------------------------------------------
# Candidate-selected operation identity
# ---------------------------------------------------------------------------

def _read_attempt():
    envelope = mod.validate_envelope()
    manifest = _read_manifest()
    attempt, _, _ = mod.build_read_attempt(manifest, envelope, now=T0)
    assert mod.c1.validate_attempt(attempt) == []
    return attempt


@pytest.mark.parametrize(
    "key",
    [
        "url",
        "sql",
        "credential",
        "destination_id",
        "tool_definition",
        "command_route",
        "filesystem_path",
        "cleanup_target",
        "operation_id",
    ],
)
def test_candidate_selector_fields_denied(key):
    attempt = _read_attempt()
    attempt["candidate"]["typed_arguments"][key] = "candidate-forged"
    result = mod.c1.evaluate_attempt(attempt)
    assert result["decision"] == "deny"
    assert result["reason_codes"] == ["operation_identity_candidate_controlled"]


def test_candidate_proposal_selector_field_denied():
    attempt = _read_attempt()
    attempt["candidate"]["proposal_fields"]["url"] = "https://forged"
    result = mod.c1.evaluate_attempt(attempt)
    assert result["decision"] == "deny"
    assert result["reason_codes"] == ["operation_identity_candidate_controlled"]


# ---------------------------------------------------------------------------
# Route response validation
# ---------------------------------------------------------------------------

def test_route_response_wrong_duplicate_malformed_non_uuid_ids():
    envelope = mod.validate_envelope()
    # non-uuid id
    rows = _full_rows()
    rows[0]["id"] = "not-a-uuid"
    mod.validate_route_response(_full_rows(), envelope)
    with pytest.raises(mod.AesC5Error) as exc:
        mod.validate_route_response(rows, envelope)
    assert exc.value.reason_code == "route_response_id_not_uuid"
    # duplicate id
    rows = _full_rows()
    rows[1]["id"] = UUID_A
    with pytest.raises(mod.AesC5Error) as exc:
        mod.validate_route_response(rows, envelope)
    assert exc.value.reason_code == "route_response_duplicate_ids"
    # malformed id (not a string)
    rows = _full_rows()
    rows[0]["id"] = 12345
    with pytest.raises(mod.AesC5Error) as exc:
        mod.validate_route_response(rows, envelope)
    assert exc.value.reason_code == "route_response_id_not_uuid"


def test_route_response_inactive_missing_extra_fourth_row():
    envelope = mod.validate_envelope()
    rows = _full_rows()
    rows[0]["active"] = False
    with pytest.raises(mod.AesC5Error) as exc:
        mod.validate_route_response(rows, envelope)
    assert exc.value.reason_code == "route_response_inactive_row"
    with pytest.raises(mod.AesC5Error) as exc:
        mod.validate_route_response(_full_rows()[:2], envelope)
    assert exc.value.reason_code == "route_response_row_count_invalid"
    with pytest.raises(mod.AesC5Error) as exc:
        mod.validate_route_response(
            _full_rows()
            + [_row(id="7a7a7a7a-0000-4000-8000-000000000000", displayName="Fourth")]
            + [],
            envelope,
        )
    assert exc.value.reason_code == "route_response_row_count_invalid"


def test_route_response_blank_duplicate_oversized_non_string_display_name():
    envelope = mod.validate_envelope()
    rows = _full_rows()
    rows[0]["displayName"] = "   "
    with pytest.raises(mod.AesC5Error) as exc:
        mod.validate_route_response(rows, envelope)
    assert exc.value.reason_code == "route_response_display_name_invalid"
    rows = _full_rows()
    rows[1]["displayName"] = "Aster Finch"
    with pytest.raises(mod.AesC5Error) as exc:
        mod.validate_route_response(rows, envelope)
    assert exc.value.reason_code == "route_response_duplicate_names"
    rows = _full_rows()
    rows[0]["displayName"] = "X" * 81
    with pytest.raises(mod.AesC5Error) as exc:
        mod.validate_route_response(rows, envelope)
    assert exc.value.reason_code == "route_response_display_name_oversized"
    rows = _full_rows()
    rows[0]["displayName"] = 123
    with pytest.raises(mod.AesC5Error) as exc:
        mod.validate_route_response(rows, envelope)
    assert exc.value.reason_code == "route_response_display_name_invalid"


def test_route_response_malformed_oversized_role_label():
    envelope = mod.validate_envelope()
    rows = _full_rows()
    rows[0]["roleLabel"] = ""
    with pytest.raises(mod.AesC5Error) as exc:
        mod.validate_route_response(rows, envelope)
    assert exc.value.reason_code == "route_response_role_label_invalid"
    rows = _full_rows()
    rows[0]["roleLabel"] = "Y" * 41
    with pytest.raises(mod.AesC5Error) as exc:
        mod.validate_route_response(rows, envelope)
    assert exc.value.reason_code == "route_response_role_label_oversized"
    rows = _full_rows()
    rows[0]["roleLabel"] = None
    validated = mod.validate_route_response(rows, envelope)
    minimized, _ = mod.minimize(validated, envelope)
    assert "role_label" not in minimized[0]
    rows = _full_rows()
    rows[0]["roleLabel"] = 5
    with pytest.raises(mod.AesC5Error) as exc:
        mod.validate_route_response(rows, envelope)
    assert exc.value.reason_code == "route_response_role_label_invalid"


def test_route_response_unexpected_field_and_nested_sensitive_rejected():
    envelope = mod.validate_envelope()
    rows = _full_rows()
    rows[0]["email"] = "someone@example.test"
    with pytest.raises(mod.AesC5Error) as exc:
        mod.validate_route_response(rows, envelope)
    assert exc.value.reason_code == "route_response_field_set_invalid"
    rows = _full_rows()
    rows[0]["defaultLocation"] = {"nested": {"address": "secret"}}
    with pytest.raises(mod.AesC5Error) as exc:
        mod.validate_route_response(rows, envelope)
    assert exc.value.reason_code == "route_response_default_location_invalid"


def test_route_response_nullable_or_exact_default_location_object():
    envelope = mod.validate_envelope()
    rows = _full_rows()
    rows[0]["defaultLocation"] = {
        "id": "7a7a7a7a-0000-4000-8000-000000000000",
        "name": "Synthetic Clinic",
    }
    assert mod.validate_route_response(rows, envelope) == rows
    rows[0]["defaultLocation"]["address"] = "forbidden"
    with pytest.raises(mod.AesC5Error) as exc:
        mod.validate_route_response(rows, envelope)
    assert exc.value.reason_code == "route_response_default_location_invalid"


def test_target_alias_mismatch_rejected():
    envelope = mod.validate_envelope()
    rows = _full_rows()
    # Move Marlow Quill to index 0.
    rows[0], rows[1] = rows[1], rows[0]
    with pytest.raises(mod.AesC5Error) as exc:
        mod.minimize(mod.validate_route_response(rows, envelope), envelope)
    assert exc.value.reason_code == "target_display_name_alias_mismatch"


# ---------------------------------------------------------------------------
# Minimized evidence leakage
# ---------------------------------------------------------------------------

def test_minimized_evidence_has_no_raw_uuid_name_or_alias_map(tmp_path):
    evidence = _execute(tmp_path)
    strings: list[str] = []
    _collect_strings(evidence, strings)
    for sensitive in FIXTURE_UUIDS + FIXTURE_NAMES + FIXTURE_ALIASES:
        assert sensitive not in strings
    ledger_dir = tmp_path / "ledgers"
    for ledger_file in ledger_dir.glob("*.json"):
        ledger = json.loads(ledger_file.read_text(encoding="utf-8"))
        ledger_strings: list[str] = []
        _collect_strings(ledger, ledger_strings)
        for sensitive in FIXTURE_UUIDS + FIXTURE_NAMES + FIXTURE_ALIASES:
            assert sensitive not in ledger_strings
    assert evidence["contains_sensitive_values"] is False


def test_frame_and_vertex_request_exclude_uuid_active_location_and_alias_map():
    envelope = mod.validate_envelope()
    rows = mod.source_provider_free_fixture().rows
    minimized, alias_map = mod.minimize(mod.validate_route_response(rows, envelope), envelope)
    frame = mod.build_context_frame_set(
        envelope,
        minimized,
        observed_at=T0,
        source_digest=mod.digest_of(rows),
    )
    request = mod.build_vertex_request(frame, envelope)
    frame_text = json.dumps(frame)
    request_text = json.dumps(request)
    # The opaque practitioner aliases ARE the work-cell refs, so they must be
    # present; the raw UUIDs and the alias-map key must never reach the frame.
    for sensitive in FIXTURE_UUIDS:
        assert sensitive not in frame_text
        assert sensitive not in request_text
    for key in ("active", "defaultLocation", "alias_map", "id", "roleLabel", "displayName"):
        for _key, _value in _walk(frame):
            assert _key != key
        for _key, _value in _walk(request):
            assert _key != key
    assert "display_name" in frame_text
    assert "role_label" in frame_text
    assert alias_map  # broker-side alias map exists but is never in frame/request
    for broker_only in ("/api/v1/practice/practitioners", "source_digest", "observed_at", "expires_at"):
        assert broker_only not in request_text
    # Every minimized alias is grounded in the frame; the alias->UUID map is not.
    for practitioner in frame["practitioners"]:
        assert practitioner["practitioner_ref"] in FIXTURE_ALIASES
    assert "alias_map" not in frame_text


# ---------------------------------------------------------------------------
# ContextFrameSet freshness and digests
# ---------------------------------------------------------------------------

def _frame():
    envelope = mod.validate_envelope()
    rows = mod.source_provider_free_fixture().rows
    minimized, _ = mod.minimize(mod.validate_route_response(rows, envelope), envelope)
    return envelope, mod.build_context_frame_set(
        envelope,
        minimized,
        observed_at=T0,
        source_digest=mod.digest_of(rows),
    )


def test_stale_and_expired_context_frame_rejected():
    _, frame = _frame()
    with pytest.raises(mod.AesC5Error) as exc:
        mod.validate_frame_freshness(frame, T0 + timedelta(seconds=31))
    assert exc.value.reason_code == "source_to_provider_dispatch_age_exceeded"
    with pytest.raises(mod.AesC5Error) as exc:
        mod.validate_frame_freshness(frame, T0 + timedelta(seconds=61))
    assert exc.value.reason_code == "context_frame_set_expired"


def test_stale_source_execute_rejected(tmp_path):
    evidence = _execute(tmp_path, observed_at=T0 - timedelta(seconds=31))
    assert evidence["result"] == "revision_required"
    assert evidence["reason_codes"] == ["source_to_provider_dispatch_age_exceeded"]
    assert evidence["source_ledger"]["status"] == "consumed"
    assert evidence["provider_ledger"]["status"] == "consumed"
    assert evidence["provider_ledger"]["maximum_provider_calls"] == 0
    assert evidence["provider_ledger"]["provider_call_allowances_consumed"] == 0


def test_wrong_source_digest_rejected():
    _, frame = _frame()
    with pytest.raises(mod.AesC5Error) as exc:
        mod.validate_frame_source_digest(frame, WRONG_DIGEST)
    assert exc.value.reason_code == "context_frame_source_digest_mismatch"


def test_wrong_manifest_digest_stops():
    envelope = mod.validate_envelope()
    manifest = _read_manifest()
    attempt, _, _ = mod.build_read_attempt(manifest, envelope, now=T0)
    attempt["current_generation_state"]["current_manifest_digest"] = WRONG_DIGEST
    result = mod.c1.evaluate_attempt(attempt)
    assert result["decision"] == "stop"
    assert result["reason_codes"] == ["supply_chain_identity_mismatch"]


def test_wrong_context_digest_in_provider_release_rejected(tmp_path):
    _, frame = _frame()
    evidence = _execute(
        tmp_path,
        provider_adapter=lambda _req, _frame: _make_packet(
            _release_text(_frame, context_frame_set_digest=WRONG_DIGEST)
        ),
    )
    assert evidence["result"] == "revision_required"
    assert evidence["reason_codes"] == ["provider_release_contract_invalid"]


# ---------------------------------------------------------------------------
# Provider output proofreader
# ---------------------------------------------------------------------------

def test_provider_wrong_target_alias_rejected(tmp_path):
    _, frame = _frame()
    evidence = _execute(
        tmp_path,
        provider_adapter=lambda _req, _frame: _make_packet(
            _release_text(_frame, selected_practitioner_ref="practitioner-choice-003")
        ),
    )
    assert evidence["result"] == "revision_required"
    assert evidence["reason_codes"] == ["provider_release_contract_invalid"]


def test_provider_extra_missing_wrong_output_fields_rejected(tmp_path):
    extra = _execute(
        tmp_path / "extra",
        provider_adapter=lambda _req, _frame: _make_packet(
            _release_text(_frame, summary_code="extra")
        ),
    )
    assert extra["reason_codes"] == ["provider_release_contract_invalid"]
    missing = _execute(
        tmp_path / "missing",
        provider_adapter=lambda _req, _frame: _make_packet(
            _release_text(_frame, context_frame_set_digest=None)
        ),
    )
    assert missing["reason_codes"] == ["provider_release_contract_invalid"]
    wrong_code = _execute(
        tmp_path / "wrong",
        provider_adapter=lambda _req, _frame: _make_packet(
            _release_text(_frame, decision_code="something_else")
        ),
    )
    assert wrong_code["reason_codes"] == ["provider_release_contract_invalid"]


def test_provider_duplicate_json_keys_rejected(tmp_path):
    _, frame = _frame()
    duplicate = (
        '{"decision_code":"active_practitioner_choice_matched",'
        '"decision_code":"active_practitioner_choice_matched",'
        f'"selected_practitioner_ref":"{frame["target_alias"]}",'
        f'"context_frame_set_digest":"{frame["context_frame_set_digest"]}",'
        '"command_authority":false}'
    )
    evidence = _execute(
        tmp_path,
        provider_adapter=lambda _req, _frame: _make_packet(duplicate),
    )
    assert evidence["result"] == "revision_required"
    assert evidence["reason_codes"] == ["provider_candidate_not_json"]


def test_provider_wrong_command_authority_rejected(tmp_path):
    evidence = _execute(
        tmp_path,
        provider_adapter=lambda _req, _frame: _make_packet(
            _release_text(_frame, command_authority=True)
        ),
    )
    assert evidence["result"] == "revision_required"
    assert evidence["reason_codes"] == ["provider_release_contract_invalid"]


def test_provider_model_version_or_finish_mismatch_rejected(tmp_path):
    evidence = _execute(
        tmp_path,
        provider_adapter=lambda _req, _frame: mod.ProviderResult(
            packet={
                "modelVersion": "gemini-2.0-flash",
                "candidates": [{"finishReason": "STOP", "content": {"role": "model", "parts": [{"text": _release_text(_frame)}]}}],
            },
            metadata={"provider_contacted": False, "fixture_used": True},
        ),
    )
    assert evidence["reason_codes"] == ["provider_model_version_mismatch"]


def test_provider_release_selector_key_rejected(tmp_path):
    _, frame = _frame()
    payload = _release_text(frame, url="https://forged")
    # The extra url field makes the whole object differ from the expected
    # closed release; the selector scan also independently rejects it.
    evidence = _execute(
        tmp_path,
        provider_adapter=lambda _req, _frame: _make_packet(payload),
    )
    assert evidence["reason_codes"] == ["provider_release_contract_invalid"]


# ---------------------------------------------------------------------------
# Cumulative budget, lease, authority, revocation, replay
# ---------------------------------------------------------------------------

def test_cumulative_budget_exhaustion_stops(tmp_path):
    observed = {counter: 0 for counter in mod.c1.COUNTER_KEYS}
    observed["model_calls"] = 1
    evidence = _execute(tmp_path, initial_observed=observed)
    assert evidence["result"] == "revision_required"
    assert evidence["reason_codes"] == ["budget_exhausted"]
    observed2 = {counter: 0 for counter in mod.c1.COUNTER_KEYS}
    observed2["request_count"] = 2
    evidence2 = _execute(tmp_path / "b", initial_observed=observed2)
    assert evidence2["reason_codes"] == ["budget_exhausted"]


def test_stale_lease_stops():
    envelope = mod.validate_envelope()
    manifest = _read_manifest()
    attempt, lease, _ = mod.build_read_attempt(manifest, envelope, now=T0)
    lease["expires_at"] = (T0 - timedelta(seconds=1)).isoformat().replace("+00:00", "Z")
    result = mod.c1.evaluate_attempt(attempt)
    assert result["decision"] == "stop"
    assert result["reason_codes"] == ["lease_invalid"]


def test_supersession_authority_change_kill_and_revocation_stop(tmp_path):
    evidence = _execute(tmp_path / "s", current_generation_id="generation-other")
    assert evidence["reason_codes"] == ["generation_superseded"]
    manifest = _read_manifest()
    authority = mod._current_authority_state(manifest)
    authority["purpose_code"] = "different-purpose"
    evidence2 = _execute(tmp_path / "a", current_authority_state=authority)
    assert evidence2["reason_codes"] == ["authority_changed"]
    evidence3 = _execute(tmp_path / "k", kill_switch=True)
    assert evidence3["reason_codes"] == ["external_kill_switch"]
    evidence4 = _execute(tmp_path / "r", revocation_record=_revocation(manifest))
    assert evidence4["reason_codes"] == ["external_kill_switch"]


def _revocation(manifest: dict[str, object]) -> dict[str, object]:
    return {
        "schema_version": "emr4.aes_c0.revocation_record.v1",
        "revocation_id": "revocation-aes-c5-001",
        "generation_id": manifest["generation_id"],
        "manifest_digest": manifest["manifest_digest"],
        "initiated_by": "external_operator",
        "reason_code": "external_stop",
        "effective_at": T0.isoformat().replace("+00:00", "Z"),
        "all_leases_revoked": True,
        "all_aliases_invalidated": True,
        "all_tokens_invalidated": True,
        "all_writable_caches_quarantined": True,
        "all_further_calls_blocked": True,
        "conversation_clear_is_cleanup": False,
        "model_influenced_revocation": False,
        "evidence_digest": mod.ZERO_HASH,
    }


def test_replay_output_already_exists_stops(tmp_path):
    evidence_output, ledger_output = _tmp_paths(tmp_path)
    mod.execute(
        mode="provider-free",
        source_head=SOURCE_HEAD,
        evidence_output=evidence_output,
        ledger_output=ledger_output,
    )
    with pytest.raises(mod.AesC5Error) as exc:
        mod.execute(
            mode="provider-free",
            source_head=SOURCE_HEAD,
            evidence_output=evidence_output,
            ledger_output=ledger_output,
        )
    assert exc.value.reason_code == "output_or_ledger_already_exists"


# ---------------------------------------------------------------------------
# Ledger consumption and cleanup
# ---------------------------------------------------------------------------

def test_ledgers_consumed_and_cleanup_after_allow(tmp_path):
    evidence = _execute(tmp_path)
    assert evidence["result"].endswith("pass")
    assert evidence["source_ledger"]["status"] == "consumed"
    assert evidence["provider_ledger"]["status"] == "consumed"
    assert evidence["cleanup"]["source_ledger_consumed"] is True
    assert evidence["cleanup"]["provider_ledger_consumed"] is True
    assert evidence["cleanup"]["lease_alias_and_token_revoked"] is True
    ledger_dir = tmp_path / "ledgers"
    for name in ("source-ledger.json", "provider-ledger.json"):
        ledger = json.loads((ledger_dir / name).read_text(encoding="utf-8"))
        assert ledger["status"] == "consumed"


def test_ledgers_consumed_after_source_denial(tmp_path):
    evidence = _execute(
        tmp_path,
        source_adapter=lambda: _source_result(_full_rows()[:2]),
    )
    assert evidence["result"] == "revision_required"
    assert evidence["reason_codes"] == ["route_response_row_count_invalid"]
    assert evidence["source_ledger"]["status"] == "consumed"
    assert evidence["provider_ledger"]["status"] == "consumed"


def test_ledgers_consumed_after_provider_failure(tmp_path):
    _, frame = _frame()
    evidence = _execute(
        tmp_path,
        provider_adapter=lambda _req, _frame: _make_packet(
            _release_text(_frame, command_authority=True)
        ),
    )
    assert evidence["reason_codes"] == ["provider_release_contract_invalid"]
    assert evidence["source_ledger"]["status"] == "consumed"
    assert evidence["provider_ledger"]["status"] == "consumed"
    assert evidence["cleanup"]["provider_ledger_consumed"] is True


def test_ledgers_consumed_after_stale_source(tmp_path):
    evidence = _execute(tmp_path, observed_at=T0 - timedelta(seconds=31))
    assert evidence["source_ledger"]["status"] == "consumed"
    assert evidence["provider_ledger"]["status"] == "consumed"


def test_no_residue_after_mode_denial(tmp_path):
    evidence_output, ledger_output = _tmp_paths(tmp_path)
    with pytest.raises(mod.AesC5Error) as exc:
        mod.execute(
            mode="live",
            source_head=SOURCE_HEAD,
            evidence_output=evidence_output,
            ledger_output=ledger_output,
        )
    assert exc.value.reason_code == "local_source_or_live_mode_denied"
    assert not evidence_output.exists()
    assert not ledger_output.exists()


# ---------------------------------------------------------------------------
# CLI live/local-source denial before adapter invocation
# ---------------------------------------------------------------------------

def test_cli_live_mode_denied_before_io(tmp_path):
    evidence_output, ledger_output = _tmp_paths(tmp_path)
    argv = [
        "prog",
        "--mode",
        "live",
        "--source-head",
        SOURCE_HEAD,
        "--evidence-output",
        str(evidence_output),
        "--ledger-output",
        str(ledger_output),
    ]
    captured = io.StringIO()
    with contextlib.redirect_stdout(captured):
        rc = mod.main_with_argv(argv[1:])
    assert rc == 1
    payload = json.loads(captured.getvalue())
    assert payload["reason_code"] == "live_mode_denied"
    assert payload["adapter_invocation_attempted"] is False
    assert not evidence_output.exists()
    assert not ledger_output.exists()


def test_cli_local_source_mode_denied_before_io(tmp_path):
    evidence_output, ledger_output = _tmp_paths(tmp_path)
    argv = [
        "prog",
        "--mode",
        "local-source",
        "--source-head",
        SOURCE_HEAD,
        "--evidence-output",
        str(evidence_output),
        "--ledger-output",
        str(ledger_output),
    ]
    captured = io.StringIO()
    with contextlib.redirect_stdout(captured):
        rc = mod.main_with_argv(argv[1:])
    assert rc == 1
    payload = json.loads(captured.getvalue())
    assert payload["reason_code"] == "local_source_mode_denied"
    assert not evidence_output.exists()
    assert not ledger_output.exists()


def test_execute_live_mode_does_not_invoke_adapters(tmp_path):
    called = {"source": False, "provider": False}

    def source_adapter():
        called["source"] = True
        return mod.source_provider_free_fixture()

    def provider_adapter(_req, _frame):
        called["provider"] = True
        return mod.provider_provider_free_fixture(_req, _frame)

    evidence_output, ledger_output = _tmp_paths(tmp_path)
    with pytest.raises(mod.AesC5Error) as exc:
        mod.execute(
            mode="live",
            source_head=SOURCE_HEAD,
            evidence_output=evidence_output,
            ledger_output=ledger_output,
            source_adapter=source_adapter,
            provider_adapter=provider_adapter,
        )
    assert exc.value.reason_code == "local_source_or_live_mode_denied"
    assert called == {"source": False, "provider": False}


# ---------------------------------------------------------------------------
# Full provider-free happy path
# ---------------------------------------------------------------------------

def test_provider_free_execute_full_pass(tmp_path):
    evidence = _execute(tmp_path)
    assert evidence["result"] == (
        "raisa_agent_execution_surface_containment_gate_aes_c5_"
        "product_runtime_admission_pass"
    )
    assert evidence["reason_codes"] == []
    source_read = evidence["broker_admissions"]["source_read"]
    provider = evidence["broker_admissions"]["provider_inference"]
    assert source_read["decision"] == "allow"
    assert source_read["after_terminal_state"] == "exhausted"
    assert source_read["after_next_operation_permitted"] is False
    assert provider["decision"] == "allow"
    assert provider["after_terminal_state"] == "exhausted"
    assert provider["after_next_operation_permitted"] is False
    assert evidence["proofreader"]["decision"] == "admitted"
    assert evidence["proofreader"]["release_performed"] is True
    assert evidence["proofreader"]["repair_call_permitted"] is False
    assert evidence["operation_counters"]["provider_calls"] == 0
    assert evidence["operation_counters"]["product_reads"] == 0
    assert evidence["operation_counters"]["database_operations"] == 0
    assert evidence["source"]["row_count"] == 3
    assert evidence["source"]["context_digest"] is not None
    assert evidence["source"]["source_digest"] is not None
    assert evidence["manifest_digests"]["source"] != evidence["manifest_digests"][
        "provider"
    ]
    assert evidence["cleanup"]["reusable_capability"] is False
    assert evidence["cleanup"]["further_generation_calls"] is False


def test_provider_free_cli_main_pass(tmp_path):
    evidence_output, ledger_output = _tmp_paths(tmp_path)
    argv = [
        "prog",
        "--mode",
        "provider-free",
        "--source-head",
        SOURCE_HEAD,
        "--evidence-output",
        str(evidence_output),
        "--ledger-output",
        str(ledger_output),
    ]
    captured = io.StringIO()
    with contextlib.redirect_stdout(captured):
        rc = mod.main_with_argv(argv[1:])
    assert rc == 0
    payload = json.loads(captured.getvalue())
    assert payload["result"].endswith("pass")
    assert payload["provider_calls"] == 0
    assert payload["product_reads"] == 0
    assert payload["database_operations"] == 0
    assert evidence_output.exists()
    assert (ledger_output / "source-ledger.json").exists()
    assert (ledger_output / "provider-ledger.json").exists()
