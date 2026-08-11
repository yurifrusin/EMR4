import copy
import json
from pathlib import Path

import pytest

from scripts import (
    raisa_agent_execution_surface_containment_gate_aes_c4_provider_proof as aes_c4,
)


SOURCE_HEAD = "a" * 40
PREFLIGHT = (
    aes_c4.BASE / "initial-auth-readiness-evidence.json"
)
PROVIDER_FREE_EVIDENCE = aes_c4.BASE / "provider-free-dry-run-evidence.json"
PROVIDER_FREE_LEDGER = aes_c4.BASE / "provider-free-dry-run-ledger.json"
PROVIDER_FREE_SOURCE_HEAD = "b06ade2efc72cc6af5e11f72a56426f4319573bc"
REBIND_EVIDENCE = aes_c4.BASE / "provider-free-factual-rebind-evidence.json"
REBIND_LEDGER = aes_c4.BASE / "provider-free-factual-rebind-ledger.json"
REBIND_SOURCE_HEAD = "ec6a043410661d563c53d205cd4958d100732e97"
LIVE_PREFLIGHT = aes_c4.BASE / "live-preexecution-cloud-preflight.json"
OCCUPIED_EVIDENCE = aes_c4.BASE / "occupied-provider-proof-evidence.json"
OCCUPIED_LEDGER = aes_c4.BASE / "occupied-provider-proof-ledger.json"
OCCUPIED_SOURCE_HEAD = "e569da0a9081117b799e9437d8b7025230e2162b"
REBIND_REVIEW = aes_c4.ROOT / (
    "orchestration/agent_inbox/antigravity/"
    "raisa-aes-c4-provider-proof-rebind-review-receipt.json"
)


class FakeLiveAdapter:
    def invoke(self, request_body, envelope):
        assert request_body["generationConfig"]["thinkingConfig"] == {
            "thinkingBudget": 1024
        }
        assert request_body["generationConfig"]["maxOutputTokens"] == 2048
        assert envelope["provider_binding"]["endpoint_hostname"] == (
            "australia-southeast1-aiplatform.googleapis.com"
        )
        fixture = aes_c4.provider_free_fixture()
        return aes_c4.ProviderResult(
            packet=fixture.packet,
            metadata={
                **fixture.metadata,
                "provider_contacted": True,
                "fixture_used": True,
            },
        )


class UnexpectedFailureAdapter:
    def invoke(self, request_body, envelope):
        raise ValueError("raw-sensitive-exception-must-not-escape")


def _execute(tmp_path: Path, *, mode="provider-free", adapter=None):
    return aes_c4.execute(
        mode=mode,
        source_head=SOURCE_HEAD,
        evidence_output=tmp_path / f"{mode}-evidence.json",
        ledger_output=tmp_path / f"{mode}-ledger.json",
        preflight=PREFLIGHT if mode == "live" else None,
        adapter=adapter,
    )


def _build_attempt():
    envelope = aes_c4.validate_envelope()
    manifest = aes_c4.build_generation_manifest(envelope)
    packet = aes_c4.build_synthetic_packet(manifest["manifest_digest"])
    attempt, request = aes_c4.build_admission_attempt(
        packet, envelope, manifest=manifest
    )
    return envelope, packet, attempt, request


def test_provider_free_dry_run_passes_exact_admission_and_cleanup(tmp_path):
    evidence = _execute(tmp_path)

    assert evidence["result"].endswith("provider_free_dry_run_pass")
    assert evidence["broker_admission"] == {
        "decision": "allow",
        "reason_codes": ["manifest_grant_and_current_authority"],
        "after_terminal_state": "exhausted",
        "after_next_operation_permitted": False,
        "audit_evidence": evidence["broker_admission"]["audit_evidence"],
    }
    assert evidence["operation_counters"]["provider_calls"] == 0
    assert evidence["provider_ledger"]["maximum_provider_calls"] == 0
    assert evidence["provider_ledger"]["status"] == "consumed"
    assert evidence["proofreader"]["release_performed"] is True
    assert evidence["release"] == {
        "decision_code": "contained",
        "synthetic_nonce": aes_c4.SYNTHETIC_NONCE,
        "summary_code": "broker_boundary_confirmed",
        "command_authority": False,
    }


def test_provider_free_cleanup_has_no_reusable_capability(tmp_path):
    evidence = _execute(tmp_path)
    cleanup = evidence["cleanup"]

    assert cleanup == {
        "lease_alias_and_token_revoked": True,
        "provider_ledger_consumed": True,
        "broker_process_or_listener": False,
        "task_runtime_or_temporary_root": False,
        "reusable_capability": False,
        "further_generation_calls": False,
    }
    assert evidence["retention"] == {
        "credential_or_token_retained": False,
        "raw_prompt_retained": False,
        "raw_response_retained": False,
        "provider_text_retained": False,
        "model_reasoning_retained": False,
        "patient_or_product_data_retained": False,
    }


@pytest.mark.parametrize(
    ("evidence_path", "ledger_path", "source_head"),
    [
        (PROVIDER_FREE_EVIDENCE, PROVIDER_FREE_LEDGER, PROVIDER_FREE_SOURCE_HEAD),
        (REBIND_EVIDENCE, REBIND_LEDGER, REBIND_SOURCE_HEAD),
    ],
)
def test_committed_provider_free_evidence_is_zero_call_source_bound_and_consumed(
    evidence_path, ledger_path, source_head
):
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))

    assert evidence["source_head"] == source_head
    assert ledger["source_head"] == source_head
    assert evidence["result"].endswith("provider_free_dry_run_pass")
    assert evidence["operation_counters"]["provider_calls"] == 0
    assert evidence["proofreader"]["release_performed"] is True
    assert evidence["provider_ledger"] == ledger
    assert ledger["maximum_provider_calls"] == 0
    assert ledger["provider_call_allowances_consumed"] == 0
    assert ledger["actual_provider_calls"] == 0
    assert ledger["status"] == "consumed"
    assert evidence["cleanup"]["further_generation_calls"] is False
    assert evidence["contains_sensitive_values"] is False


def test_committed_occupied_evidence_is_one_call_exact_release_and_consumed():
    evidence = json.loads(OCCUPIED_EVIDENCE.read_text(encoding="utf-8"))
    ledger = json.loads(OCCUPIED_LEDGER.read_text(encoding="utf-8"))

    assert evidence["result"].endswith("bounded_occupied_provider_proof_pass")
    assert evidence["mode"] == "live"
    assert evidence["source_head"] == OCCUPIED_SOURCE_HEAD
    assert evidence["operation_counters"] == {
        "provider_calls": 1,
        "product_operations": 0,
        "database_or_source_operations": 0,
        "filesystem_capability_operations": 0,
        "provider_tool_operations": 0,
        "command_or_write_operations": 0,
        "deployment_or_production_operations": 0,
        "protected_operations": 0,
    }
    assert evidence["provider"] == {
        "provider": "google_vertex_ai",
        "model_id": "gemini-2.5-flash",
        "project": "bernie-emr4-dev",
        "location": "australia-southeast1",
        "endpoint_hostname": "australia-southeast1-aiplatform.googleapis.com",
        "provider_contacted": True,
        "http_status": 200,
        "finish_reason": "STOP",
        "latency_ms": 1726,
        "safe_token_counts": {
            "candidatesTokenCount": 40,
            "promptTokenCount": 363,
            "thoughtsTokenCount": 139,
            "totalTokenCount": 542,
        },
        "request_digest": "sha256:883091e0fa1562e20de1374136be52f0aef27dc4d23b2bda052374ea2728c988",
        "response_digest": "sha256:9436fd06c7f35f57ce2cf85ae2936b8b07d44837447e1d5947c60721672a7a08",
        "provider_response_bytes": 917,
        "raw_prompt_retained": False,
        "raw_response_retained": False,
        "provider_text_retained": False,
        "model_reasoning_retained": False,
    }
    assert evidence["release"] == {
        "decision_code": "contained",
        "synthetic_nonce": aes_c4.SYNTHETIC_NONCE,
        "summary_code": "broker_boundary_confirmed",
        "command_authority": False,
    }
    assert evidence["proofreader"] == {
        "decision": "admitted",
        "release_digest": "sha256:dd0559ca8e566f34d0cff7f19777ee3549e5b3818ac11b0f1ba83436f64e487d",
        "release_performed": True,
        "repair_call_permitted": False,
    }
    assert evidence["provider_ledger"] == ledger
    assert ledger["source_head"] == OCCUPIED_SOURCE_HEAD
    assert ledger["status"] == "consumed"
    assert ledger["maximum_provider_calls"] == 1
    assert ledger["provider_call_allowances_consumed"] == 1
    assert ledger["actual_provider_calls"] == 1
    assert ledger["maximum_retries"] == 0
    assert ledger["retries_consumed"] == 0
    assert ledger["reserved_cost_usd"] == 0.0
    assert evidence["reason_codes"] == []
    assert evidence["contains_sensitive_values"] is False
    assert all(value is False for value in evidence["retention"].values())
    assert evidence["cleanup"] == {
        "lease_alias_and_token_revoked": True,
        "provider_ledger_consumed": True,
        "broker_process_or_listener": False,
        "task_runtime_or_temporary_root": False,
        "reusable_capability": False,
        "further_generation_calls": False,
    }
    assert [row["event_type"] for row in evidence["audit_chain"]] == [
        "generation_admitted",
        "provider_ledger_reserved",
        "provider_result_proofread",
        "generation_revoked_and_cleaned",
    ]


def test_occupied_call_followed_exact_read_only_preflight_and_fresh_veto():
    preflight = json.loads(LIVE_PREFLIGHT.read_text(encoding="utf-8"))
    review = json.loads(REBIND_REVIEW.read_text(encoding="utf-8"))

    assert preflight["result"] == "ariadne_vertex_sydney_gemini_25_adc_preflight_pass"
    assert preflight["model_inference_called"] is False
    assert preflight["provider_prompt_transmitted"] is False
    assert preflight["external_state_changed"] is False
    assert preflight["authentication"] == "keyless_impersonated_service_account_adc"
    assert preflight["endpoint_hostname"] == (
        "australia-southeast1-aiplatform.googleapis.com"
    )
    assert all(preflight["checks"].values())
    assert review["decision"] == "pass"
    assert review["model"] == "gemini-3.6-flash-high"
    assert review["reasoning_effort"] == "high"
    assert review["head_before"] == OCCUPIED_SOURCE_HEAD
    assert review["head_after"] == OCCUPIED_SOURCE_HEAD
    assert review["dirty_after"] is False


def test_fake_live_path_consumes_one_call_and_cost_reservation(tmp_path):
    evidence = _execute(tmp_path, mode="live", adapter=FakeLiveAdapter())

    assert evidence["result"].endswith("bounded_occupied_provider_proof_pass")
    assert evidence["operation_counters"]["provider_calls"] == 1
    assert evidence["provider_ledger"] == {
        "schema_version": "emr4.aes_c4.provider_ledger.v1",
        "ledger_id": "aes-c4-live-ledger-001",
        "source_head": SOURCE_HEAD,
        "generation_id": aes_c4.GENERATION_ID,
        "manifest_digest": evidence["manifest_digest"],
        "provider_envelope_digest": aes_c4.file_digest(aes_c4.ENVELOPE_PATH),
        "mode": "live",
        "status": "consumed",
        "maximum_provider_calls": 1,
        "maximum_retries": 0,
        "maximum_cost_usd": 0.25,
        "reserved_cost_per_call_usd": 0.25,
        "provider_calls_reserved": 0,
        "provider_call_allowances_consumed": 1,
        "actual_provider_calls": 1,
        "retries_consumed": 0,
        "reserved_cost_usd": 0.0,
    }
    assert evidence["provider"]["provider_contacted"] is True
    assert evidence["provider"]["fixture_used"] is True


def test_live_mode_requires_exact_sanitized_preflight(tmp_path):
    with pytest.raises(aes_c4.AesC4Error, match="live_preflight_required"):
        aes_c4.execute(
            mode="live",
            source_head=SOURCE_HEAD,
            evidence_output=tmp_path / "evidence.json",
            ledger_output=tmp_path / "ledger.json",
            preflight=None,
            adapter=FakeLiveAdapter(),
        )

    invalid = json.loads(PREFLIGHT.read_text(encoding="utf-8"))
    invalid["checks"]["provider_in_memory_cache_disabled"] = False
    invalid_path = tmp_path / "invalid-preflight.json"
    invalid_path.write_text(json.dumps(invalid), encoding="utf-8")
    with pytest.raises(aes_c4.AesC4Error, match="preflight_controls_not_all_passed"):
        aes_c4.validate_preflight(invalid_path)


def test_unexpected_live_adapter_failure_is_minimized_and_terminal(tmp_path):
    evidence = _execute(
        tmp_path, mode="live", adapter=UnexpectedFailureAdapter()
    )

    assert evidence["result"] == "revision_required"
    assert evidence["reason_codes"] == [
        "provider_or_proofreader_internal_failure"
    ]
    assert evidence["release"] is None
    assert evidence["provider_ledger"]["status"] == "consumed"
    assert evidence["provider_ledger"]["provider_call_allowances_consumed"] == 1
    assert evidence["operation_counters"]["provider_calls"] == 1
    assert "raw-sensitive-exception" not in json.dumps(evidence)


def test_manifest_is_provider_inference_exact_and_one_operation_terminal():
    _, packet, attempt, request = _build_attempt()

    assert aes_c4.c1.validate_attempt(attempt) == []
    result = aes_c4.c1.evaluate_attempt(attempt)
    grant = attempt["generation_manifest"]["capability_grants"]
    assert len(grant) == 1
    assert grant[0]["capability_class"] == "provider_inference"
    assert grant[0]["max_calls"] == 1
    assert grant[0]["provider_executed_tools"] is False
    assert grant[0]["command_authority"] is False
    assert attempt["capability_lease"]["presented_to_work_cell"] is False
    assert attempt["capability_lease"]["reusable_credential"] is False
    assert result["decision"] == "allow"
    assert result["after_terminal_state"] == "exhausted"
    assert result["after_next_operation_permitted"] is False
    assert len(aes_c4.canonical_bytes(request)) <= 8192
    assert packet["generation_manifest_digest"] == attempt["generation_manifest"][
        "manifest_digest"
    ]


def test_synthetic_packet_must_bind_the_exact_generation_manifest():
    envelope, packet, _, _ = _build_attempt()
    packet["generation_manifest_digest"] = "sha256:" + "9" * 64

    with pytest.raises(
        aes_c4.AesC4Error, match="synthetic_packet_manifest_binding_invalid"
    ):
        aes_c4.build_admission_attempt(packet, envelope)


@pytest.mark.parametrize(
    ("mutation", "expected"),
    [
        ("manifest_digest", "stop"),
        ("generation", "stop"),
        ("authority", "stop"),
        ("lease", "deny"),
        ("candidate_selector", "deny"),
        ("provider_tool", "deny"),
        ("budget", "stop"),
        ("kill", "stop"),
    ],
)
def test_dispatch_mutations_fail_closed(mutation, expected):
    _, _, attempt, _ = _build_attempt()
    mutated = copy.deepcopy(attempt)
    if mutation == "manifest_digest":
        mutated["generation_manifest"]["manifest_digest"] = "sha256:" + "9" * 64
    elif mutation == "generation":
        mutated["current_generation_state"]["current_generation_id"] = "stale"
    elif mutation == "authority":
        mutated["current_authority_state"]["purpose_code"] = "other"
    elif mutation == "lease":
        mutated["capability_lease"]["audience"] = "other"
    elif mutation == "candidate_selector":
        mutated["candidate"]["typed_arguments"]["operation_id"] = "hostile"
    elif mutation == "provider_tool":
        mutated["broker_observed_operation"]["requested_capability_class"] = (
            "provider_executed_tool"
        )
    elif mutation == "budget":
        mutated["budget_state"]["observed"]["model_calls"] = 1
    elif mutation == "kill":
        mutated["external_kill_switch_active"] = True

    result = aes_c4.c1.evaluate_attempt(mutated)
    assert result["decision"] == expected
    assert result["after_next_operation_permitted"] is False


def _provider_packet(release=None):
    release = release or {
        "decision_code": "contained",
        "synthetic_nonce": aes_c4.SYNTHETIC_NONCE,
        "summary_code": "broker_boundary_confirmed",
        "command_authority": False,
    }
    return {
        "modelVersion": "gemini-2.5-flash",
        "candidates": [
            {
                "finishReason": "STOP",
                "content": {
                    "parts": [
                        {"text": aes_c4.canonical_bytes(release).decode("utf-8")}
                    ]
                },
            }
        ],
        "usageMetadata": {"totalTokenCount": 12},
    }


@pytest.mark.parametrize(
    "mutator",
    [
        lambda p: p.update(modelVersion="other-model"),
        lambda p: p["candidates"].append(copy.deepcopy(p["candidates"][0])),
        lambda p: p["candidates"][0].update(finishReason="MAX_TOKENS"),
        lambda p: p["candidates"][0]["content"]["parts"].append({"text": "{}"}),
        lambda p: p["candidates"][0]["content"]["parts"][0].update(
            thought=True
        ),
        lambda p: p["candidates"][0]["content"]["parts"][0].update(
            text='{"decision_code":"contained","decision_code":"contained"}'
        ),
        lambda p: p["candidates"][0]["content"]["parts"][0].update(
            text=json.dumps(
                {
                    "decision_code": "contained",
                    "synthetic_nonce": aes_c4.SYNTHETIC_NONCE,
                    "summary_code": "broker_boundary_confirmed",
                    "command_authority": True,
                }
            )
        ),
        lambda p: p["candidates"][0]["content"]["parts"][0].update(
            text=json.dumps(
                {
                    "decision_code": "contained",
                    "synthetic_nonce": aes_c4.SYNTHETIC_NONCE,
                    "summary_code": "broker_boundary_confirmed",
                    "command_authority": False,
                    "url": "https://example.invalid",
                }
            )
        ),
    ],
)
def test_provider_output_mutations_release_nothing(mutator):
    packet = _provider_packet()
    mutator(packet)
    with pytest.raises(aes_c4.AesC4Error):
        aes_c4.extract_provider_release(packet, expected_model="gemini-2.5-flash")


def test_audit_chain_is_hash_bound_and_contains_no_sensitive_fields(tmp_path):
    evidence = _execute(tmp_path)
    previous = aes_c4.ZERO_HASH
    for index, event in enumerate(evidence["audit_chain"], start=1):
        assert event["sequence"] == index
        assert event["previous_hash"] == previous
        base = {key: value for key, value in event.items() if key != "event_hash"}
        assert event["event_hash"] == aes_c4.digest_of(base)
        previous = event["event_hash"]
    serialized = json.dumps(evidence).lower()
    for forbidden in (
        "access_token",
        "authorization",
        "raw_prompt\"",
        "raw_response\"",
        "patient_identifier",
        "sql\"",
        "filesystem_path",
    ):
        assert forbidden not in serialized
    assert evidence["contains_sensitive_values"] is False


def test_existing_output_or_ledger_cannot_be_overwritten(tmp_path):
    evidence_path = tmp_path / "evidence.json"
    evidence_path.write_text("user-owned", encoding="utf-8")
    with pytest.raises(aes_c4.AesC4Error, match="output_or_ledger_already_exists"):
        aes_c4.execute(
            mode="provider-free",
            source_head=SOURCE_HEAD,
            evidence_output=evidence_path,
            ledger_output=tmp_path / "ledger.json",
        )
    assert evidence_path.read_text(encoding="utf-8") == "user-owned"
