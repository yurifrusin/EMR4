from __future__ import annotations

import copy
import json
from pathlib import Path

import jsonschema
import pytest

from scripts import ariadne_deepseek_in_cell_rehearsal as rehearsal


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_SCHEMA = (
    ROOT
    / "orchestration"
    / "continuity"
    / "ariadne-deepseek-in-cell"
    / "rehearsal-evidence.schema.json"
)
CONTINUITY_GRAPH_PATH = (
    ROOT / "orchestration" / "continuity" / "emr4-continuity-graph.json"
)
COMPASS_PATH = ROOT / "orchestration" / "continuity" / "emr4-compass.json"
AGENTS_PATH = ROOT / "AGENTS.md"


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _canonical_generated_drafts():
    document = _json(rehearsal.WORK_CELL_DOCUMENT_PATH)
    drafts = [
        copy.deepcopy(item)
        for item in document["draft_frames"]
        if item["id"] in rehearsal.PRIMARY_DRAFT_IDS
    ]
    by_id = {item["id"]: item for item in drafts}
    ordered = [by_id[item] for item in rehearsal.PRIMARY_DRAFT_IDS]
    for draft in ordered:
        draft["batch_id"] = "generated-batch-001"
        draft["attempt_id"] = "generated-attempt-001"
        draft["provenance"] = {
            "kind": "model-generated-draft",
            "source": "generated-attempt-001",
        }
    audit = next(
        item for item in ordered if item["output_port_id"] == "port-audit"
    )
    audit["payload"]["attempt_id"] = "generated-attempt-001"
    return ordered


def test_static_contract_passes_without_docker_or_provider():
    result = rehearsal.validate_static()
    assert result["status"] == "passed"
    assert result["context_frame_count"] == 6
    assert result["context_payload_bytes"] <= 4096
    assert result["compiled_prompt_bytes"] <= 32768
    assert result["output_port_count"] == 5


def test_attempt_selects_exact_model_topology_and_empty_tools():
    attempt = _json(rehearsal.ATTEMPT_PATH)
    model = attempt["model_contract"]
    assert model == {
        "topology_id": "in_cell_claude_code_remote_provider_broker_v1",
        "transport": "claude_code_bare",
        "claude_code_package": "@anthropic-ai/claude-code",
        "claude_code_version": "2.1.201",
        "provider": "deepseek",
        "provider_base_url": "https://api.deepseek.com/anthropic",
        "model_id": "deepseek-v4-flash",
        "effort": "high",
        "tools": [],
        "fallback_model": None,
        "session_persistence": False,
        "proofreader_route": "deterministic-proofreader-v1",
        "output_authority": "draft-only",
    }


def test_context_is_exactly_six_opaque_authored_synthetic_frames():
    attempt = _json(rehearsal.ATTEMPT_PATH)
    frames = attempt["context_frames"]
    assert [item["frame_type"] for item in frames] == rehearsal.FRAME_TYPES
    serialised = json.dumps(frames).lower()
    assert "margaret" not in serialised
    assert "medicare" not in serialised
    assert "clinical note" not in serialised
    assert "historical" not in serialised
    assert "protected" not in serialised
    assert all(
        item["practice_id"] == "practice-synth-a"
        and item["principal_id"] == "principal-reception"
        and item["correlation_id"] == "booking-request-001"
        and item["context_revision"] == 7
        for item in frames
    )


def test_output_schema_accepts_canonical_model_generated_drafts():
    schema = _json(rehearsal.OUTPUT_SCHEMA_PATH)
    jsonschema.Draft202012Validator(schema).validate(
        {"drafts": _canonical_generated_drafts()}
    )


def test_output_schema_rejects_command_authority():
    schema = _json(rehearsal.OUTPUT_SCHEMA_PATH)
    drafts = _canonical_generated_drafts()
    drafts[0]["authority_class"] = "command"
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(schema).validate({"drafts": drafts})


def test_output_schema_rejects_direct_extra_field():
    schema = _json(rehearsal.OUTPUT_SCHEMA_PATH)
    drafts = _canonical_generated_drafts()
    drafts[1]["payload"]["approved"] = True
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(schema).validate({"drafts": drafts})


def test_generated_canonical_drafts_pass_existing_proofreader():
    proof = rehearsal._proofread_generated(_canonical_generated_drafts())
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


def test_proofreader_rejects_unknown_generated_slot():
    drafts = _canonical_generated_drafts()
    drafts[0]["payload"]["selected_slot_id"] = "slot-invented"
    proof = rehearsal._proofread_generated(drafts)
    ux = next(
        item
        for item in proof["frame_verdicts"]
        if item["draft_id"] == "draft-ux-primary"
    )
    assert proof["status"] == "rejected"
    assert ux["verdict"] == "retryable_grounding_reject"


def test_docker_build_context_is_exact_allowlist():
    assert set(rehearsal.BUILD_CONTEXT_ALLOWLIST) == {
        "Dockerfile",
        "ariadne_deepseek_work_cell_launcher.mjs",
        "ariadne_deepseek_one_use_broker.mjs",
        "attempt.json",
        "output.schema.json",
    }
    assert all(path.is_file() for path in rehearsal.BUILD_CONTEXT_ALLOWLIST.values())


def test_work_cell_launcher_is_toolless_and_sessionless():
    source = rehearsal.LAUNCHER_PATH.read_text(encoding="utf-8")
    required = [
        '"--bare"',
        '"--safe-mode"',
        '"--tools"',
        '"--no-session-persistence"',
        '"--disable-slash-commands"',
        '"--strict-mcp-config"',
        '"--no-chrome"',
        'ANTHROPIC_BASE_URL: "http://broker:8080/anthropic"',
    ]
    for marker in required:
        assert marker in source
    assert '"Read,Glob,Grep,Edit,Write,Bash"' not in source
    assert "DEEPSEEK_API_KEY" not in source
    assert "child.stdin.end(prompt" in source


def test_broker_is_one_path_one_model_one_call_and_caps_tokens():
    source = rehearsal.BROKER_PATH.read_text(encoding="utf-8")
    assert 'const ALLOWED_PATH = "/anthropic/v1/messages"' in source
    assert 'const MODEL_ID = "deepseek-v4-flash"' in source
    assert "providerCallCount >= 1" in source
    assert "const MAX_REQUEST_BYTES = 65_536" in source
    assert "const MAX_OUTPUT_TOKENS = 2_048" in source
    assert "payload.tools.length > 0" in source
    assert "request_body" not in source
    assert "response_body" not in source


def test_dockerfile_pins_claude_package_and_uses_non_root_user():
    source = rehearsal.DOCKERFILE_PATH.read_text(encoding="utf-8")
    assert "ARG CLAUDE_CODE_VERSION=2.1.201" in source
    assert (
        '"@anthropic-ai/claude-code@${CLAUDE_CODE_VERSION}"'
        in source
    )
    assert source.count("USER node") == 2
    assert "COPY . " not in source
    assert "DEEPSEEK_API_KEY" not in source


def test_provider_attempt_requires_explicit_flag_before_any_runtime_check():
    with pytest.raises(
        rehearsal.RehearsalError,
        match="provider-call-authorisation-flag-required",
    ):
        rehearsal.rehearse(authorised=False)


def test_single_use_ledger_refuses_second_consumption(tmp_path, monkeypatch):
    ledger = tmp_path / "ledger.json"
    monkeypatch.setattr(rehearsal, "LEDGER_PATH", ledger)
    first = rehearsal._consume_attempt_ledger()
    assert first["state"] == "consumed"
    with pytest.raises(
        rehearsal.RehearsalError,
        match="single-use-attempt-already-consumed",
    ):
        rehearsal._consume_attempt_ledger()


def test_public_evidence_contract_excludes_raw_content_fields():
    source = Path(rehearsal.__file__).read_text(encoding="utf-8")
    assert '"generated_draft_bodies_committed": False' in source
    assert '"raw_prompt_committed": False' in source
    assert '"raw_provider_response_committed": False' in source
    assert '"chain_of_thought_committed": False' in source
    assert '"drafts": generatedEnvelope?.drafts' not in source


def test_consumed_attempt_closed_revision_required_without_provider_call():
    evidence = _json(rehearsal.EVIDENCE_PATH)
    ledger = _json(rehearsal.LEDGER_PATH)
    assert evidence["status"] == "revision_required"
    assert evidence["result"] == rehearsal.REVISION_RESULT
    assert evidence["reason_codes"] == [
        "claude-process-failed",
        "provider-call-count-not-exactly-one",
    ]
    assert (
        evidence["evidence_label"]
        == "provider_transport_attempt_authored_synthetic_no_provider_call"
    )
    assert evidence["attempt"]["authority_consumed"] is True
    assert evidence["attempt"]["model_process_started"] is True
    assert evidence["attempt"]["provider_call_count"] == 0
    assert evidence["topology"]["provider_request_forwarded"] is False
    assert evidence["topology"]["provider_inference_completed"] is False
    assert evidence["schema_validation"] == "not-presented"
    assert evidence["proofreader"] is None
    assert evidence["generated_draft_hashes"] == []
    assert all(evidence["cleanup"].values())
    assert ledger["state"] == "consumed"
    assert ledger["retry_authorised"] is False


def test_rejected_broker_request_was_not_forwarded():
    evidence = _json(rehearsal.EVIDENCE_PATH)
    events = evidence["broker_events"]
    assert [item["event"] for item in events] == [
        "broker-ready",
        "broker-request-rejected",
    ]
    assert events[1]["reason_code"] == "method-or-path-not-allowlisted"
    assert not any(item["event"] == "provider-call-started" for item in events)


def test_runtime_policy_kept_provider_key_out_of_cell_and_all_products_closed():
    evidence = _json(rehearsal.EVIDENCE_PATH)
    cell = evidence["effective_policy"]["work_cell"]
    broker = evidence["effective_policy"]["broker"]
    network = evidence["effective_policy"]["internal_network"]
    assert "DEEPSEEK_API_KEY" not in cell["environment_keys"]
    assert "DEEPSEEK_API_KEY" in broker["environment_keys"]
    assert cell["read_only_root"] is True
    assert cell["cap_drop"] == ["ALL"]
    assert cell["mount_count"] == 0
    assert cell["published_port_count"] == 0
    assert network["internal"] is True
    assert not any(evidence["product_connections"].values())


def test_runtime_source_hashes_still_match_executed_container_inputs():
    evidence = _json(rehearsal.EVIDENCE_PATH)
    assert evidence["source_hashes"] == rehearsal.source_hashes()
    assert (
        evidence["evidence_correction"]["runtime_observations_changed"] is False
    )


def test_runtime_evidence_validates_against_draft_2020_12_schema():
    schema = _json(EVIDENCE_SCHEMA)
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(schema).validate(
        _json(rehearsal.EVIDENCE_PATH)
    )


def test_continuity_records_rejected_consumed_attempt_without_acceptance():
    graph = _json(CONTINUITY_GRAPH_PATH)
    assert graph["graph_revision"] == 23
    node = next(
        item
        for item in graph["nodes"]
        if item["id"] == "ariadne-deepseek-in-cell-generated-draft-rehearsal"
    )
    assert node["status"] == "rejected"
    assert node["evidence"]["acceptances"] == []
    assert node["contract_evidence"] == []
    assert any(
        "No provider request was forwarded" in note
        for note in node["authority"]["notes"]
    )
    assert any(
        "fresh Yuri decision" in gate for gate in node["unresolved_gates"]
    )


def test_compass_blocks_retry_behind_fresh_gateway_diagnostic_decision():
    compass = _json(COMPASS_PATH)
    assert compass["map_revision"] == 11
    assert compass["source_graph_revision"] == 23
    horizon = next(
        item
        for item in compass["programme_support_horizon"]
        if item["id"] == "ariadne-first-generated-draft-rehearsal"
    )
    assert horizon["status"] == "blocked"
    assert "provider-blocked diagnostic" in horizon["strategic_question"]
    decisions = {
        item["id"]: item for item in compass["user_owned_decisions"]
    }
    assert "authorize-generated-draft-gateway-diagnostic-or-retry" in decisions
    assert "second occupied model/provider attempt" in decisions[
        "authorize-generated-draft-gateway-diagnostic-or-retry"
    ]["required_before"]


def test_live_handover_preserves_consumed_authority_and_no_retry_boundary():
    handover = AGENTS_PATH.read_text(encoding="utf-8")
    assert (
        "ariadne_deepseek_in_cell_generated_draft_rehearsal_revision_required"
        in handover
    )
    assert "No request reached DeepSeek" in handover
    assert "do not retry" in handover
    assert "occupied-process authority is consumed" in handover
