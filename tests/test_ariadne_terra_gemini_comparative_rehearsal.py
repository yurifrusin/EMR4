from __future__ import annotations

import copy
import json
import tempfile
from pathlib import Path

import jsonschema
import pytest

from scripts import ariadne_terra_gemini_comparative_rehearsal as rehearsal


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _canonical_drafts():
    document = _json(rehearsal.WORK_CELL_DOCUMENT_PATH)
    by_id = {
        item["id"]: copy.deepcopy(item)
        for item in document["draft_frames"]
        if item["id"] in rehearsal.PRIMARY_DRAFT_IDS
    }
    order = [
        "draft-ux-primary",
        "draft-human-primary",
        "draft-audit-primary",
        "draft-orchestrator-primary",
        "draft-advisory-primary",
    ]
    drafts = [by_id[item] for item in order]
    for draft in drafts:
        draft["batch_id"] = "generated-batch-001"
        draft["attempt_id"] = "generated-attempt-001"
        draft["provenance"] = {
            "kind": "model-generated-draft",
            "source": "generated-attempt-001",
        }
    next(
        item for item in drafts if item["id"] == "draft-audit-primary"
    )["payload"]["attempt_id"] = "generated-attempt-001"
    return drafts


def test_static_contract_passes_without_container_or_provider():
    result = rehearsal.validate_static()
    assert result["status"] == "passed"
    assert result["context_frame_count"] == 6
    assert result["prompt_bytes"] <= 32768
    assert result["provider_call_performed"] is False
    assert result["prompt_transmitted"] is False


def test_shared_task_projection_removes_transport_and_neutralises_label():
    source = _json(rehearsal.SOURCE_ATTEMPT_PATH)
    projected = rehearsal.shared_task()
    assert "model_contract" in source
    assert "model_contract" not in projected
    source.pop("model_contract")
    source["schema_version"] = "ariadne.provider_neutral_comparison_task.v1"
    assert projected == source


def test_frozen_lane_order_models_endpoints_and_no_substitution():
    manifest = _json(rehearsal.MANIFEST_PATH)
    assert [
        (
            item["lane_id"],
            item["model_id"],
            item["host"],
            item["path"],
        )
        for item in manifest["lanes"]
    ] == [
        (
            "terra",
            "gpt-5.6-terra",
            "api.openai.com",
            "/v1/responses",
        ),
        (
            "gemini",
            "gemini-3.5-flash",
            "generativelanguage.googleapis.com",
            "/v1beta/models/gemini-3.5-flash:generateContent",
        ),
    ]
    assert "aiplatform.googleapis.com" not in json.dumps(manifest)


def test_provider_schema_and_full_schema_accept_canonical_drafts():
    envelope = {"drafts": _canonical_drafts()}
    for path in (rehearsal.PROVIDER_SCHEMA_PATH, rehearsal.FULL_SCHEMA_PATH):
        jsonschema.Draft202012Validator(_json(path)).validate(envelope)


def test_full_schema_rejects_safe_looking_but_wrong_port_pairing():
    drafts = _canonical_drafts()
    drafts[0]["output_port_id"] = "port-advisory"
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(
            _json(rehearsal.FULL_SCHEMA_PATH)
        ).validate({"drafts": drafts})


def test_existing_deterministic_proofreader_passes_canonical_generated_form():
    proof = rehearsal._proofread(_canonical_drafts())
    assert proof["status"] == "passed"
    assert proof["disposition"] == "release-verified-outputs"
    assert proof["released_edge_count"] == 5
    assert proof["repair_receipt_count"] == 0
    assert [item["verdict"] for item in proof["frame_verdicts"]] == [
        "pass_to_downstream",
        "pass_to_human_gate",
        "pass_to_downstream",
        "pass_to_downstream",
        "pass_to_human_gate",
    ]


def test_prompt_material_is_provider_neutral_and_deterministic():
    first = rehearsal.prompt_material()
    second = rehearsal.prompt_material()
    assert first["hashes"] == second["hashes"]
    prompt = first["prompt"].lower()
    system = first["system_prompt"].lower()
    for marker in (
        "gpt-5.6-terra",
        "gemini-3.5-flash",
        "openai",
        "google",
        "deepseek",
    ):
        assert marker not in prompt
        assert marker not in system
    assert "model_contract" not in prompt


def test_full_schema_prompt_projection_changes_metadata_not_constraints():
    source = _json(rehearsal.FULL_SCHEMA_PATH)
    projected = rehearsal.provider_neutral_full_schema()
    assert projected["$id"].endswith(
        "ariadne-provider-neutral-work-cell-output.schema.json"
    )
    assert projected["title"] == (
        "Ariadne Provider-Neutral Work-Cell Draft Envelope"
    )
    source["$id"] = projected["$id"]
    source["title"] = projected["title"]
    assert projected == source


def test_build_context_preserves_every_expected_sealed_hash_byte_for_byte():
    material = rehearsal.prompt_material()
    with tempfile.TemporaryDirectory(
        prefix="ariadne-comparison-hash-test-"
    ) as raw:
        target = Path(raw)
        rehearsal._copy_build_context(target)
        actual = {
            "shared_task_sha256": rehearsal.sha256_bytes(
                (target / "shared-task.json").read_bytes()
            ),
            "full_output_schema_sha256": rehearsal.sha256_bytes(
                (target / "full-output.schema.json").read_bytes()
            ),
            "provider_output_schema_sha256": rehearsal.sha256_bytes(
                rehearsal.js_json(
                    _json(target / "provider-output.schema.json")
                ).encode()
            ),
            "system_prompt_sha256": rehearsal.sha256_bytes(
                material["system_prompt"].encode()
            ),
            "prompt_sha256": rehearsal.sha256_bytes(
                material["prompt"].encode()
            ),
        }
        assert actual == material["hashes"]
        assert b"\r\n" not in (target / "full-output.schema.json").read_bytes()


def test_broker_fixes_one_path_call_budget_and_exact_upstreams():
    source = rehearsal.BROKER_PATH.read_text(encoding="utf-8")
    assert 'const ALLOWED_PATH = "/infer"' in source
    assert 'model: "gpt-5.6-terra"' in source
    assert 'model: "gemini-3.5-flash"' in source
    assert 'host: "api.openai.com"' in source
    assert 'host: "generativelanguage.googleapis.com"' in source
    assert "providerCallCount >= 1" in source
    assert "providerCallCount += 1" in source
    assert "max_output_tokens: MAX_OUTPUT_TOKENS" in source
    assert "maxOutputTokens: MAX_OUTPUT_TOKENS" in source
    assert "tools: []" in source
    assert "store: false" in source
    assert "response_body" not in source
    assert "prompt:" not in source


def test_work_cell_has_no_provider_key_sdk_cli_or_model_identity():
    source = rehearsal.LAUNCHER_PATH.read_text(encoding="utf-8")
    for forbidden in (
        "OPENAI_API_KEY",
        "GEMINI_API_KEY",
        "GOOGLE_API_KEY",
        "gpt-5.6-terra",
        "gemini-3.5-flash",
        "@google/genai",
        "openai",
        "child_process",
    ):
        assert forbidden not in source
    assert 'path: "/infer"' in source
    assert 'hostname: "broker"' in source


def test_dockerfile_uses_non_root_fixed_launchers_and_no_wildcard_copy():
    source = rehearsal.DOCKERFILE_PATH.read_text(encoding="utf-8")
    assert source.count("USER node") == 2
    assert "COPY . " not in source
    assert "API_KEY" not in source
    assert 'CMD ["node", "/opt/ariadne/broker.mjs"]' in source
    assert 'CMD ["node", "/opt/ariadne/launcher.mjs"]' in source


def test_live_run_fails_before_consumption_when_both_credentials_absent(
    monkeypatch,
):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    before = {
        lane: _json(rehearsal.SOURCE_DIR / f"{lane}-single-use-ledger.json")
        for lane in ("terra", "gemini")
    }
    with pytest.raises(
        rehearsal.RehearsalError,
        match="both-provider-credentials-required-before-consumption",
    ):
        rehearsal.run_live(authorised=True)
    after = {
        lane: _json(rehearsal.SOURCE_DIR / f"{lane}-single-use-ledger.json")
        for lane in ("terra", "gemini")
    }
    assert after == before


def test_live_run_requires_explicit_flag_before_credential_check():
    with pytest.raises(
        rehearsal.RehearsalError,
        match="explicit-authorisation-flag-required",
    ):
        rehearsal.run_live(authorised=False)


def test_fresh_attempt_consumed_new_ledgers_without_resetting_attempt_one():
    authority = _json(rehearsal.FRESH_ATTEMPT_PATH)
    old_terra = _json(rehearsal.TERRA_LEDGER_PATH)
    fresh_terra = _json(rehearsal.FRESH_TERRA_LEDGER_PATH)
    fresh_gemini = _json(rehearsal.FRESH_GEMINI_LEDGER_PATH)
    assert authority["runtime_attempt_id"] == "comparative-runtime-attempt-002"
    assert old_terra["state"] == "consumed"
    assert fresh_terra["state"] == "consumed"
    assert fresh_gemini["state"] == "consumed"
    assert fresh_terra["runtime_attempt_id"] == (
        "comparative-runtime-attempt-002"
    )
    assert fresh_gemini["runtime_attempt_id"] == (
        "comparative-runtime-attempt-002"
    )


def test_fresh_attempt_requires_explicit_flag_and_both_credentials(
    monkeypatch,
):
    with pytest.raises(
        rehearsal.RehearsalError,
        match="explicit-fresh-attempt-authorisation-required",
    ):
        rehearsal.run_fresh_attempt(authorised=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    before = (
        _json(rehearsal.FRESH_TERRA_LEDGER_PATH),
        _json(rehearsal.FRESH_GEMINI_LEDGER_PATH),
    )
    with pytest.raises(
        rehearsal.RehearsalError,
        match="both-provider-credentials-required-before-fresh-consumption",
    ):
        rehearsal.run_fresh_attempt(authorised=True)
    after = (
        _json(rehearsal.FRESH_TERRA_LEDGER_PATH),
        _json(rehearsal.FRESH_GEMINI_LEDGER_PATH),
    )
    assert after == before


def test_public_evidence_source_excludes_raw_content_fields():
    source = Path(rehearsal.__file__).read_text(encoding="utf-8")
    assert '"raw_prompt_recorded": False' in source
    assert '"raw_provider_response_recorded": False' in source
    assert '"draft_payload_recorded": False' in source
    assert '"provider_secret_recorded": False' in source
    assert '"drafts": drafts' not in source


def test_provider_free_preflight_evidence_has_no_call_or_residue():
    evidence = _json(rehearsal.PREFLIGHT_EVIDENCE_PATH)
    assert evidence["status"] == "passed"
    assert evidence["provider_call_performed"] is False
    assert evidence["prompt_transmitted"] is False
    assert evidence["credential_gates"]["both_present"] == all(
        evidence["credential_gates"]["lane_presence"].values()
    )
    assert evidence["credential_gates"]["credential_values_recorded"] is False
    assert all(
        all(result.values()) for result in evidence["cleanup"].values()
    )
    for lane in ("terra", "gemini"):
        cell = evidence["lane_policies"][lane]["cell"]
        broker = evidence["lane_policies"][lane]["broker"]
        assert cell["user"] == "node"
        assert cell["read_only_root"] is True
        assert cell["published_port_count"] == 0
        assert {item["destination"] for item in cell["mounts"]} == {
            "/run/secrets/broker_token"
        }
        assert {item["destination"] for item in broker["mounts"]} == {
            "/run/secrets/broker_token",
            "/run/secrets/provider_key",
        }


def test_attempt2_preflight_uses_corrected_hashes_and_new_images():
    evidence = _json(rehearsal.FRESH_PREFLIGHT_EVIDENCE_PATH)
    assert evidence["status"] == "passed"
    assert evidence["credential_gates"]["both_present"] is True
    assert evidence["provider_call_performed"] is False
    assert evidence["prompt_transmitted"] is False
    assert evidence["static"]["shared_hashes"] == (
        rehearsal.prompt_material()["hashes"]
    )
    assert all(
        all(result.values()) for result in evidence["cleanup"].values()
    )
    assert evidence["build"]["image_ids"]["terra"] == (
        evidence["build"]["image_ids"]["gemini"]
    )


def test_attempt2_runtime_evidence_records_two_calls_no_drafts_and_cleanup():
    evidence = _json(rehearsal.FRESH_COMPARISON_EVIDENCE_PATH)
    assert evidence["result"] == (
        "ariadne_terra_gemini_comparative_rehearsal_"
        "attempt2_revision_required"
    )
    assert evidence["shared_hash_match"] is True
    assert evidence["retry_performed"] is False
    assert evidence["fallback_performed"] is False
    assert evidence["cross_model_input"] is False
    assert evidence["voting"] is False

    expected_statuses = {"terra": 500, "gemini": 400}
    for lane_id, provider_status in expected_statuses.items():
        lane = evidence["lanes"][lane_id]
        assert lane["ledger"]["state"] == "consumed"
        assert lane["status"] == "revision_required"
        assert lane["reason_codes"] == ["provider-non-success"]
        events = lane["broker_events"]
        starts = [item for item in events if item["event"] == "provider-call-started"]
        completions = [
            item for item in events if item["event"] == "provider-call-completed"
        ]
        assert len(starts) == 1
        assert len(completions) == 1
        assert starts[0]["provider_call_count"] == 1
        assert completions[0]["provider_call_count"] == 1
        assert completions[0]["provider_status"] == provider_status
        assert lane["generated_draft_count"] == 0
        assert lane["provider_schema_status"] == "not-presented"
        assert lane["full_schema_status"] == "not-presented"
        assert lane["proofreader"] is None
        assert all(lane["cleanup"].values())

    assert evidence["raw_prompt_recorded"] is False
    assert evidence["raw_provider_response_recorded"] is False
    assert evidence["draft_payload_recorded"] is False
    assert evidence["provider_secret_recorded"] is False
    assert evidence["product_or_database_access"] is False
    assert evidence["downstream_delivery"] is False
