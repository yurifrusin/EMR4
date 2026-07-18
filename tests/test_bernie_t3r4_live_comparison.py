from __future__ import annotations

import copy
from datetime import date
import json
from pathlib import Path

import pytest

from app.services.ai.evals.bernie_shadow_live_comparison import (
    DEEPSEEK_LANE,
    DEFAULT_OBSERVATION_PATH,
    DEFAULT_REPORT_PATH,
    DispatchState,
    LANE_IDS,
    append_observation,
    build_lane_cases,
    build_prompt,
    build_report,
    canonical_hash,
    failure_record,
    lane_case_ids,
    live_response_schema,
    load_approval,
    load_observations,
    observation_key,
    parse_json_object,
    success_record,
    validate_approval,
    validate_observations,
)
from app.services.ai.evals.bernie_shadow_silver_v2 import build_silver_v2_shadow_cases
from scripts import bernie_t3r4_live_comparison as live_script


def _payload(case):
    expected = case.expected
    return {
        "intent": expected.intent,
        "entities": [list(item) for item in expected.entities],
        "date_time": [list(item) for item in expected.date_time],
        "requires_clarification": expected.requires_clarification,
        "tool_name": expected.tool_name,
        "writes_authorized": False,
        "claims_action_completed": False,
        "action_withdrawn": expected.action_withdrawn,
    }


def _success(packet, lane_id, case, sample_index):
    prompt = build_prompt(case)
    return success_record(
        packet=packet,
        lane_id=lane_id,
        case=case,
        sample_index=sample_index,
        prompt_hash=canonical_hash(prompt),
        normalized_payload=_payload(case),
        started_at="2026-07-18T00:00:00.000Z",
        completed_at="2026-07-18T00:00:01.000Z",
        latency_ms=1000,
        usage={"input_tokens": 10, "output_tokens": 5},
        tool_observation=("mechanically_disabled" if lane_id == DEEPSEEK_LANE else "unobservable_on_transport"),
        estimated_cost_usd=0.001 if lane_id == DEEPSEEK_LANE else None,
    )


def test_approval_freezes_96_primary_and_24_auxiliary_observations():
    packet = load_approval()
    validate_approval(packet, today=date(2026, 7, 18))

    lanes = {item["lane_id"]: item for item in packet["lanes"]}
    assert lanes["openai_gpt_subscription"]["maximum_samples"] == 48
    assert lanes["google_gemini_subscription"]["maximum_samples"] == 48
    assert lanes[DEEPSEEK_LANE]["maximum_samples"] == 24
    assert packet["execution_limits"]["maximum_scheduled_samples"] == 120
    assert lanes[DEEPSEEK_LANE]["included_in_primary_ranking"] is False


def test_deepseek_subset_is_balanced_and_covers_all_dialogue_forms():
    packet = load_approval()
    cases = build_lane_cases(packet, DEEPSEEK_LANE)
    metadata = [dict(case.metadata) for case in cases]

    assert len(cases) == 12
    assert {item["action"] for item in metadata} == {
        "create", "move", "resize", "cancel", "status_change", "explain_schedule"
    }
    assert all(sum(item["action"] == action for item in metadata) == 2 for action in {item["action"] for item in metadata})
    assert sum(item["noise_level"] == "high" for item in metadata) == 6
    assert sum(item["noise_level"] == "medium" for item in metadata) == 6
    assert len({item["dialogue_form"] for item in metadata}) == 8


def test_prompt_is_synthetic_bounded_schema_only_and_under_character_ceiling():
    packet = load_approval()
    case = build_lane_cases(packet, "openai_gpt_subscription")[0]
    prompt = build_prompt(case)

    assert case.instruction in prompt
    assert "2026-07-14" in prompt
    assert "Do not use tools" in prompt
    assert "writes_authorized=false" in prompt
    assert len(prompt) < packet["execution_limits"]["maximum_serialized_prompt_chars_per_sample"]
    assert "protected holdout" not in prompt.lower()
    assert "historical diary" not in prompt.lower()
    assert live_response_schema()["additionalProperties"] is False


def test_schema_parser_accepts_plain_and_fenced_json_and_rejects_unknown_fields():
    case = build_lane_cases(load_approval(), "openai_gpt_subscription")[0]
    payload = _payload(case)
    rendered = json.dumps(payload)

    assert parse_json_object(rendered) == payload
    assert parse_json_object(f"```json\n{rendered}\n```") == payload
    with pytest.raises(ValueError, match="fields"):
        parse_json_object(json.dumps({**payload, "raw_response": "forbidden"}))


def test_dispatch_kill_switch_rejects_wrong_case_repeat_duplicate_and_expiry():
    packet = load_approval()
    lane_id = "openai_gpt_subscription"
    case = build_lane_cases(packet, lane_id)[0]
    prompt = build_prompt(case)
    state = DispatchState(packet, [], 0)
    state.assert_allowed(lane_id=lane_id, case=case, sample_index=0, prompt=prompt)

    with pytest.raises(ValueError, match="sample index"):
        state.assert_allowed(lane_id=lane_id, case=case, sample_index=2, prompt=prompt)
    other = next(
        item
        for item in build_silver_v2_shadow_cases()
        if item.case_id not in lane_case_ids(packet, lane_id)
    )
    with pytest.raises(ValueError, match="outside lane"):
        state.assert_allowed(lane_id=lane_id, case=other, sample_index=0, prompt=prompt)

    record = _success(packet, lane_id, case, 0)
    with pytest.raises(ValueError, match="already consumed"):
        DispatchState(packet, [record], 0).assert_allowed(
            lane_id=lane_id, case=case, sample_index=0, prompt=prompt
        )
    with pytest.raises(ValueError, match="expired"):
        validate_approval(packet, today=date(2026, 7, 20))


@pytest.mark.parametrize(
    "mutation, message",
    [
        (lambda packet: packet.update(authorizes_provider_calls=False), "not approved"),
        (lambda packet: packet["lanes"][2].update(included_in_primary_ranking=True), "outside the primary"),
        (lambda packet: packet["execution_limits"].update(automatic_retries=True), "prohibit retries"),
        (lambda packet: packet["privacy_and_retention"].update(raw_response_persistence=True), "privacy boundary"),
        (lambda packet: packet["authority"].update(database_or_audit_write=True), "prohibited product authority"),
    ],
)
def test_approval_fails_closed_on_authority_method_or_privacy_drift(mutation, message):
    packet = copy.deepcopy(load_approval())
    mutation(packet)
    with pytest.raises(ValueError, match=message):
        validate_approval(packet, today=date(2026, 7, 18))


def test_success_record_scores_normalized_response_without_raw_material():
    packet = load_approval()
    lane_id = "openai_gpt_subscription"
    case = build_lane_cases(packet, lane_id)[0]
    record = _success(packet, lane_id, case, 0)

    assert record["status"] == "success"
    assert record["score"]["correctness_passes"] == 6
    assert record["score"]["safety_violations"] == []
    assert record["raw_prompt_persisted"] is False
    assert record["raw_response_persisted"] is False
    assert record["adapter_cost_authoritative"] is False
    assert "instruction" not in record
    assert "raw_response" not in record
    validate_observations([record])


def test_observation_ledger_is_append_only_unique_and_rejects_raw_keys(tmp_path: Path):
    packet = load_approval()
    lane_id = "openai_gpt_subscription"
    case = build_lane_cases(packet, lane_id)[0]
    path = tmp_path / "observations.jsonl"
    record = _success(packet, lane_id, case, 0)
    append_observation(record, path)

    assert load_observations(path) == [record]
    with pytest.raises(ValueError, match="unique"):
        append_observation(record, path)
    with pytest.raises(ValueError, match="raw prompt"):
        validate_observations([{**record, "raw_response": "must not persist"}])


def test_failure_consumes_sample_without_response_material():
    packet = load_approval()
    lane_id = "google_gemini_subscription"
    case = build_lane_cases(packet, lane_id)[0]
    record = failure_record(
        packet=packet,
        lane_id=lane_id,
        case=case,
        sample_index=0,
        prompt_hash=canonical_hash(build_prompt(case)),
        status="provider_error",
        safe_error_code="antigravity_exit_1",
        started_at="2026-07-18T00:00:00.000Z",
        completed_at="2026-07-18T00:00:01.000Z",
        latency_ms=1000,
    )

    assert record["normalized_response"] is None
    assert record["response_hash"] is None
    assert record["safe_error_code"] == "antigravity_exit_1"
    validate_observations([record])


def test_complete_report_ranks_only_gpt_and_gemini_and_separates_deepseek():
    packet = load_approval()
    records = []
    for lane_id in LANE_IDS:
        for case in build_lane_cases(packet, lane_id):
            records.extend(_success(packet, lane_id, case, sample_index) for sample_index in (0, 1))
    assert len(records) == 120

    report = build_report(packet, records)
    assert report["decision"] == "comparison_complete"
    assert report["execution"]["consumed_samples"] == 120
    assert {item["lane_id"] for item in report["primary_comparison"]} == {
        "openai_gpt_subscription", "google_gemini_subscription"
    }
    assert [item["lane_id"] for item in report["auxiliary_diversity"]] == [DEEPSEEK_LANE]
    assert report["auxiliary_diversity"][0]["included_in_primary_ranking"] is False
    assert all(value is False for key, value in report["api_spine_boundary"].items() if key != "classification")


def test_committed_live_report_matches_normalized_ledger_and_hard_stop():
    records = load_observations(DEFAULT_OBSERVATION_PATH)
    committed = json.loads(DEFAULT_REPORT_PATH.read_text(encoding="utf-8"))

    assert len(records) == 89
    assert build_report(records=records) == committed
    assert committed["decision"] == "comparison_complete_with_hard_limit_stop"
    assert committed["execution"]["all_authorized_work_complete"] is True
    assert committed["execution"]["raw_prompt_persisted"] is False
    assert committed["execution"]["raw_response_persisted"] is False
    assert committed["methodology"]["primary_fully_paired_case_count"] == 5
    assert all(item["correctness_passes"] == 60 for item in committed["primary_fully_paired_comparison"])


def test_closeout_and_handover_do_not_promote_the_bounded_result():
    closeout = Path("docs/bernie-t3r4-pragmatic-live-comparison-closeout.md").read_text(
        encoding="utf-8"
    )
    handover = Path("AGENTS.md").read_text(encoding="utf-8")

    assert "too small to rank the underlying models" in closeout
    assert "without an independent veto" in closeout
    assert "does not authorize" in closeout
    assert "T3R4 validly closed `comparison_complete_with_hard_limit_stop`" in handover
    assert "further live calls/external prompts" in handover


def test_live_transport_stays_out_of_application_runtime():
    app_source = Path("app/services/ai/evals/bernie_shadow_live_comparison.py").read_text(encoding="utf-8")
    script_source = Path("scripts/bernie_t3r4_live_comparison.py").read_text(encoding="utf-8")

    assert "import subprocess" not in app_source
    assert "app.routers" not in app_source
    assert "sqlalchemy" not in app_source
    assert "import subprocess" in script_source
    assert "--no-session-persistence" in script_source
    assert '"--tools"' in script_source
    assert '"--ephemeral"' in script_source
    assert '"--sandbox"' in script_source


def test_codex_transport_parser_requires_no_observed_tool_item(monkeypatch, tmp_path: Path):
    case = build_lane_cases(load_approval(), "openai_gpt_subscription")[0]
    payload = _payload(case)
    calls = []

    def fake_run(command, **kwargs):
        calls.append((command, kwargs))
        events = [
            {"type": "thread.started", "thread_id": "synthetic"},
            {"type": "item.completed", "item": {"type": "agent_message", "text": json.dumps(payload)}},
            {"type": "turn.completed", "usage": {"input_tokens": 20, "output_tokens": 10}},
        ]
        return live_script.subprocess.CompletedProcess(command, 0, "\n".join(json.dumps(item) for item in events), "")

    monkeypatch.setattr(live_script, "_run", fake_run)
    schema_path = tmp_path / "schema.json"
    schema_path.write_text("{}", encoding="utf-8")
    normalized, usage, tool_state, _cost, _chars = live_script._codex_call(
        build_prompt(case), tmp_path, schema_path
    )

    assert normalized == payload
    assert usage == {"input_tokens": 20, "output_tokens": 10}
    assert tool_state == "observed_none"
    command = calls[0][0]
    assert {"--ephemeral", "--ignore-user-config", "--ignore-rules"} <= set(command)
    assert "--output-schema" not in command
    assert calls[0][1]["prompt"] == build_prompt(case)


def test_codex_transport_rejects_observed_tool_activity():
    event = {
        "type": "item.completed",
        "item": {"type": "command_execution", "command": "forbidden"},
    }
    with pytest.raises(live_script.ObservedToolUse):
        live_script._parse_codex(json.dumps(event))


def test_gemini_and_deepseek_parsers_keep_only_normalized_payload(monkeypatch, tmp_path: Path):
    packet = load_approval()
    case = build_lane_cases(packet, "google_gemini_subscription")[0]
    payload = _payload(case)
    calls = []

    def fake_run(command, **kwargs):
        calls.append(command)
        if command[0] == "agy":
            return live_script.subprocess.CompletedProcess(command, 0, json.dumps(payload), "")
        wrapper = {
            "type": "result",
            "subtype": "success",
            "result": json.dumps(payload),
            "structured_output": payload,
            "usage": {"input_tokens": 30, "output_tokens": 12},
            "total_cost_usd": 0.002,
            "permission_denials": [],
        }
        return live_script.subprocess.CompletedProcess(command, 0, json.dumps(wrapper), "")

    monkeypatch.setattr(live_script, "_run", fake_run)
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-only-not-real")
    schema_path = tmp_path / "schema.json"
    schema_path.write_text("{}", encoding="utf-8")

    gemini = live_script._gemini_call(build_prompt(case), tmp_path, schema_path)
    deepseek = live_script._deepseek_call(build_prompt(case), tmp_path, schema_path)

    assert gemini[0] == payload
    assert gemini[2] == "unobservable_on_transport"
    assert deepseek[0] == payload
    assert deepseek[1] == {"input_tokens": 30, "output_tokens": 12}
    assert deepseek[2] == "mechanically_disabled"
    assert "--sandbox" in calls[0]
    assert "--tools" in calls[1]
    assert calls[1][calls[1].index("--tools") + 1] == ""
