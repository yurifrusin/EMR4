from __future__ import annotations

import json
from pathlib import Path

from scripts import ariadne_vertex_sydney_gemini_25_contracts as contracts


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_ROOT = (
    ROOT
    / "orchestration"
    / "continuity"
    / "ariadne-vertex-sydney-gemini-25"
)


def load(name: str) -> dict:
    return json.loads((ARTIFACT_ROOT / name).read_text(encoding="utf-8"))


def test_external_audit_chain_and_zero_call_disposition_are_exact() -> None:
    audit = load("external-audit.json")
    assert contracts.validate_audit_chain(audit["events"])
    assert audit["chain_head"] == audit["events"][-1]["event_hash"]
    assert audit["terminal_rehearsal_result"] == (
        "ariadne_vertex_sydney_gemini_25_adc_preflight_blocked"
    )
    assert audit["provider_result"]["provider_call_made"] is False
    assert audit["attempt"]["occupied_call_started"] is False
    assert audit["ledger"]["durable_rehearsal_ledgers_opened"] == 0
    assert audit["ledger"]["temporary_test_ledgers_consumed"] == 1
    assert audit["proofreader"]["disposition"] == "not_reached"
    assert audit["proofreader"]["released_values"] is None


def test_external_audit_contains_no_disallowed_raw_content() -> None:
    audit = load("external-audit.json")
    observed_keys: set[str] = set()

    def collect_keys(value) -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                observed_keys.add(str(key).casefold())
                collect_keys(child)
        elif isinstance(value, list):
            for child in value:
                collect_keys(child)

    collect_keys(audit)
    assert not observed_keys & {
        "access_token",
        "api_key",
        "chain_of_thought",
        "credential_file",
        "prompt_text",
        "raw_prompt",
        "raw_provider_response",
        "refresh_token",
    }
    assert audit["binding"]["api_key_authentication_used"] is False


def test_independent_audit_accepts_only_the_failed_gate() -> None:
    analysis = load("independent-audit-analysis.json")
    assert analysis["result"] == (
        "ariadne_vertex_sydney_gemini_25_independent_audit_pass"
    )
    assert analysis["terminal_result_accepted"] == (
        "ariadne_vertex_sydney_gemini_25_adc_preflight_blocked"
    )
    assert analysis["verified"]["provider_calls"] == 0
    assert analysis["verified"]["retries"] == 0
    assert analysis["verified"]["task_residue_clear"] is True


def test_adc_restored_audit_chain_and_cache_stop_are_exact() -> None:
    audit = load("adc-restored-external-audit.json")
    assert contracts.validate_audit_chain(audit["events"])
    assert audit["chain_head"] == audit["events"][-1]["event_hash"]
    assert audit["terminal_rehearsal_result"] == (
        "ariadne_vertex_sydney_gemini_25_cache_control_blocked"
    )
    assert audit["provider_result"]["provider_call_made"] is False
    assert audit["attempt"]["occupied_call_started"] is False
    assert audit["ledger"]["durable_rehearsal_ledgers_opened"] == 0
    assert audit["vertex_control_posture"][
        "usable_exact_impersonated_adc_proved"
    ] is True
    assert audit["vertex_control_posture"][
        "provider_in_memory_cache_disabled_verified"
    ] is False
    assert audit["proofreader"]["disposition"] == "not_reached"
    assert audit["proofreader"]["released_values"] is None


def test_adc_restored_audit_artifact_hashes_and_exclusions_are_exact() -> None:
    audit = load("adc-restored-external-audit.json")
    immutable_artifact_paths = {
        "continuation_plan_file_hash": (
            ROOT
            / "docs/ariadne-vertex-sydney-gemini-25-adc-restored-continuation-plan.md"
        ),
        "preflight_evidence_file_hash": (
            ARTIFACT_ROOT / "tranche-3-adc-restored-preflight-evidence.json"
        ),
        "residue_evidence_file_hash": (
            ARTIFACT_ROOT / "adc-restored-closeout-residue-evidence.json"
        ),
    }
    for field, path in immutable_artifact_paths.items():
        assert audit["contract_hashes"][field] == contracts.bytes_hash(
            path.read_bytes()
        )
    # The closed audit binds the source and tests that existed at its closeout.
    # A later, separately authorised cache-control continuation may strengthen
    # those files without rewriting the historical audit node.
    assert audit["contract_hashes"]["preflight_source_file_hash"] == (
        "sha256:4fb0ccca4eac8e89a6c6aa1c392b33b8d3ce179680c09037fd680e8593bf6f3b"
    )
    assert audit["contract_hashes"]["preflight_test_file_hash"] == (
        "sha256:cf85a0c2de419644e43d9d1bb86a8fd03e5246c18f50c6564b02762a133fb873"
    )
    assert audit["binding"]["api_key_authentication_used"] is False
    assert {
        "credentials",
        "access_tokens",
        "refresh_tokens",
        "api_key_information",
        "raw_authentication_responses",
        "raw_cloud_control_responses",
        "raw_prompts",
        "raw_provider_responses",
        "hidden_reasoning",
        "chain_of_thought",
    } <= set(audit["explicit_exclusions"])


def test_adc_restored_independent_audit_accepts_only_cache_stop() -> None:
    analysis = load("adc-restored-independent-audit-analysis.json")
    assert analysis["result"] == (
        "ariadne_vertex_sydney_gemini_25_adc_restored_independent_audit_pass"
    )
    assert analysis["terminal_result_accepted"] == (
        "ariadne_vertex_sydney_gemini_25_cache_control_blocked"
    )
    assert analysis["reviewed_revision_binding"] == {
        "continuity_graph_revision": 37,
        "compass_map_revision": 24,
        "continuity_compass_revision_bound": True,
        "rendered_compass_exact": True,
    }
    assert analysis["verified"]["repository_only_tests_passed"] == 36
    assert analysis["verified"]["provider_calls"] == 0
    assert analysis["verified"]["retries"] == 0
    assert analysis["verified"][
        "durable_rehearsal_or_occupied_ledgers_opened"
    ] == 0
    assert analysis["verified"]["sensitive_raw_content_identified"] is False
    assert any(
        "does not prove that caching was positively observed enabled" in limit
        for limit in analysis["proof_limits"]
    )


def test_cache_disabled_primary_external_audit_is_exact() -> None:
    audit = load("cache-disabled-external-audit.json")
    assert audit["audit_result"] == (
        "ariadne_vertex_sydney_gemini_25_external_audit_pass"
    )
    assert audit["terminal_rehearsal_result"] == (
        "ariadne_vertex_sydney_gemini_25_occupied_rehearsal_revision_required"
    )
    assert audit["attempt"]["primary_occupied_call_count"] == 1
    assert audit["attempt"]["retry_count"] == 0
    assert audit["attempt"]["retry_eligible"] is False
    assert audit["binding"] == {
        "provider": "google_vertex_ai",
        "model_id": "gemini-2.5-flash",
        "project": "bernie-emr4-dev",
        "service_account": (
            "emr4-bernie-ai-dev@bernie-emr4-dev.iam.gserviceaccount.com"
        ),
        "authentication": "keyless_impersonated_service_account_adc",
        "api_key_authentication_used": False,
        "location": "australia-southeast1",
        "endpoint_hostname": (
            "australia-southeast1-aiplatform.googleapis.com"
        ),
        "automatic_fallback": False,
        "provider_tools": False,
    }
    assert audit["provider_result"]["http_status"] == 400
    assert audit["provider_result"]["normalized_status"] == "INVALID_ARGUMENT"
    assert audit["provider_result"]["field_violation_paths"] == []
    assert audit["provider_result"]["token_usage"] is None
    assert audit["proofreader"]["disposition"] == "not_reached"
    assert audit["proofreader"]["released_values"] is None
    assert audit["ledger"]["status"] == "consumed"
    assert audit["ledger"]["provider_calls_consumed"] == 1
    assert not any(audit["cleanup"].values())


def test_cache_disabled_primary_audit_artifact_hashes_are_exact() -> None:
    audit = load("cache-disabled-external-audit.json")
    paths = {
        "occupied_evidence": ARTIFACT_ROOT / "occupied-primary-evidence.json",
        "occupied_ledger": ARTIFACT_ROOT / "occupied-primary-ledger.json",
        "occupied_hash_chain": (
            ARTIFACT_ROOT / "occupied-primary-external-audit.jsonl"
        ),
        "pre_attempt_control_evidence": (
            ARTIFACT_ROOT / "pre-attempt-tranche-3-evidence.json"
        ),
        "real_isolation_evidence": (
            ARTIFACT_ROOT / "tranche-4-real-isolation-evidence.json"
        ),
        "pre_attempt_receipt": (
            ROOT
            / "orchestration/agent_inbox/codex/"
            "ariadne-vertex-sydney-gemini-25-cache-disabled-"
            "preattempt-receipt.json"
        ),
    }
    for field, path in paths.items():
        assert audit["artifact_hashes"][field] == contracts.bytes_hash(
            path.read_bytes()
        )


def test_every_provider_free_tranche4_ledger_is_consumed() -> None:
    ledgers = sorted(ARTIFACT_ROOT.glob("tranche-4-*-single-use-ledger.json"))
    ledgers.append(ARTIFACT_ROOT / "tranche-4-single-use-ledger.json")
    assert len(ledgers) == 8
    for path in ledgers:
        ledger = json.loads(path.read_text(encoding="utf-8"))
        assert ledger["status"] == "consumed"
        assert ledger["provider_calls_consumed"] == 0


def test_repair_external_audit_is_exact_and_stops_on_success() -> None:
    audit = load("repair-external-audit.json")
    assert audit["audit_result"] == (
        "ariadne_vertex_sydney_gemini_25_repair_external_audit_pass"
    )
    assert audit["terminal_rehearsal_result"] == (
        "ariadne_vertex_sydney_gemini_25_occupied_rehearsal_pass"
    )
    assert audit["attempt"]["successful_attempt_provider_calls"] == 1
    assert audit["attempt"]["blind_identical_retries"] == 0
    assert audit["attempt"]["calls_after_success"] == 0
    assert audit["provider_result"]["http_status"] == 200
    assert audit["provider_result"]["latency_ms"] == 1108
    assert audit["provider_result"]["token_usage"] == {
        "prompt_tokens": 176,
        "candidate_tokens": 50,
        "total_tokens": 226,
    }
    assert audit["proofreader"]["disposition"] == "released"
    assert audit["proofreader"]["findings"] == []
    assert audit["proofreader"]["safe_repairs"] == []
    assert audit["proofreader"]["released_authored_synthetic_values"] == {
        "summary": "Project Lark has 5 tiles: 3 blue and 2 green.",
        "total_tiles": 5,
        "risk_level": "none",
        "evidence_ids": ["fact_alpha", "fact_beta"],
    }
    assert audit["lineage"]["repair_002_occupied_ledger"]["status"] == (
        "consumed"
    )
    assert audit["lineage"]["repair_002_occupied_ledger"][
        "provider_calls_consumed"
    ] == 1
    assert audit["lineage"]["total_occupied_calls"] == 3
    assert audit["lineage"]["all_opened_ledgers_consumed"] is True
    assert audit["lineage"]["further_call_disposition"] == "closed_on_success"
    assert not any(audit["cleanup"].values())


def test_repair_external_audit_artifact_hashes_are_exact() -> None:
    audit = load("repair-external-audit.json")
    paths = {
        "successful_occupied_evidence": (
            ARTIFACT_ROOT / "repair-002-occupied-evidence.json"
        ),
        "successful_occupied_ledger": (
            ARTIFACT_ROOT / "repair-002-occupied-ledger.json"
        ),
        "successful_occupied_hash_chain": (
            ARTIFACT_ROOT / "repair-002-occupied-audit.jsonl"
        ),
        "successful_precall_gate": (
            ARTIFACT_ROOT / "repair-002-precall-gate-evidence.json"
        ),
        "successful_dry_run_evidence": (
            ARTIFACT_ROOT / "repair-003-dry-run-evidence.json"
        ),
        "successful_dry_run_ledger": (
            ARTIFACT_ROOT / "repair-003-dry-run-ledger.json"
        ),
        "successful_dry_run_hash_chain": (
            ARTIFACT_ROOT / "repair-003-dry-run-audit.jsonl"
        ),
        "failed_setup_dry_run_ledger": (
            ARTIFACT_ROOT / "repair-002-dry-run-ledger.json"
        ),
        "failed_setup_dry_run_hash_chain": (
            ARTIFACT_ROOT / "repair-002-dry-run-audit.jsonl"
        ),
        "same_session_tranche_3_evidence": (
            ARTIFACT_ROOT / "repair-tranche-3-preflight-evidence.json"
        ),
        "iterative_authority_contract": (
            ARTIFACT_ROOT / "iterative-repair-contract.json"
        ),
        "closeout_residue_evidence": (
            ARTIFACT_ROOT / "repair-closeout-residue-evidence.json"
        ),
        "prior_failed_occupied_evidence": (
            ARTIFACT_ROOT / "repair-occupied-evidence.json"
        ),
        "prior_failed_occupied_ledger": (
            ARTIFACT_ROOT / "repair-occupied-ledger.json"
        ),
        "prior_failed_occupied_hash_chain": (
            ARTIFACT_ROOT / "repair-occupied-audit.jsonl"
        ),
    }
    for field, path in paths.items():
        assert audit["artifact_hashes"][field] == contracts.bytes_hash(
            path.read_bytes()
        )


def test_repair_occupied_chain_and_independent_audit_are_exact() -> None:
    events = [
        json.loads(line)
        for line in (
            ARTIFACT_ROOT / "repair-002-occupied-audit.jsonl"
        ).read_text(encoding="utf-8").splitlines()
        if line
    ]
    assert contracts.validate_audit_chain(events)
    audit = load("repair-external-audit.json")
    assert audit["typewriter_keys"]["chain_head"] == events[-1]["event_hash"]
    assert audit["typewriter_keys"]["event_count"] == 8
    analysis = load("repair-independent-audit-analysis.json")
    assert analysis["result"].endswith("_pass")
    assert analysis["terminal_result_accepted"].endswith(
        "_occupied_rehearsal_pass"
    )
    assert analysis["verified"]["total_lineage_occupied_calls"] == 3
    assert analysis["verified"]["blind_identical_retries"] == 0
    assert analysis["verified"]["calls_after_success"] == 0
    assert analysis["verified"]["proofreader_reached"] is True
    assert analysis["verified"]["release_reached"] is True
    assert analysis["verified"]["sensitive_raw_content_identified"] is False


def test_every_repair_run_ledger_is_consumed() -> None:
    for name in (
        "repair-tranche-4-dry-run-ledger.json",
        "repair-occupied-ledger.json",
        "repair-002-dry-run-ledger.json",
        "repair-003-dry-run-ledger.json",
        "repair-002-occupied-ledger.json",
    ):
        ledger = load(name)
        assert ledger["status"] == "consumed"
