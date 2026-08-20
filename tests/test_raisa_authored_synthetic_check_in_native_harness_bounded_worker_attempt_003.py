from __future__ import annotations

import inspect
import json
from pathlib import Path

from scripts import (
    raisa_authored_synthetic_check_in_native_harness_bounded_worker_monitored_development_rehearsal
    as subject,
)


PLAN = (
    Path(__file__).resolve().parents[1]
    / "docs"
    / "raisa-authored-synthetic-check-in-native-harness-bounded-worker-attempt-003-plan.md"
)
THREAT = (
    Path(__file__).resolve().parents[1]
    / "docs"
    / "security"
    / "raisa-authored-synthetic-check-in-native-harness-bounded-worker-attempt-003-threat-model-delta.md"
)


def test_attempt_three_plan_freezes_the_single_use_cost_and_claim_envelope() -> None:
    text = " ".join(PLAN.read_text(encoding="utf-8").split())
    assert "Date: 2026-08-21" in text
    assert "Status: `frozen`" in text
    assert "at most one provider request" in text
    assert "at most 4,096 output tokens" in text
    assert "300-second upstream request timeout" in text
    assert "420-second native process deadline" in text
    assert "existing user-controlled prepaid DeepSeek balance" in text
    assert "must not claim an enforced dollar cap" in text
    assert "zero automatic retries" in text
    assert "no second worker" in text


def test_attempt_three_plan_records_all_parallelism_lanes() -> None:
    text = PLAN.read_text(encoding="utf-8")
    assert "**DeepSeek Flash:** `planned`, positive leverage" in text
    assert "**Gemini 3.7 Flash/high:** `reserved`, neutral leverage" in text
    assert "**Native subagents:** `declined`, negative leverage" in text
    assert "**GPT Sol:** owns planning" in text


def test_attempt_three_configuration_is_exact_and_isolated() -> None:
    value = subject.attempt_three_configuration()
    assert value["operation_id"] == subject.ATTEMPT_THREE_OPERATION_ID
    assert value["attempt_id"] == "deepseek-native-synthetic-window-worker-003"
    assert value["attempt_root"].as_posix().endswith(
        "/EMR4-worktrees/deepseek-native-synthetic-window-worker-003"
    )
    paths = {
        value[key]
        for key in (
            "checkpoint_path",
            "preparation_path",
            "work_order_path",
            "authority_path",
            "forbidden_path",
            "command_manifest_path",
            "no_database_admission_path",
            "consumed_path",
            "terminal_path",
            "terminal_schema_path",
            "native_report_path",
            "pre_hmr_terminal_path",
        )
    }
    assert all(path.parent == subject.CONTINUITY_ROOT / "attempt-003" for path in paths)
    assert not paths & set(subject.attempt_two_configuration().values())


def test_attempt_three_terminal_schema_is_closed_and_identity_specific() -> None:
    schema = json.loads(
        subject.attempt_three_configuration()["terminal_schema_path"].read_text(
            encoding="utf-8"
        )
    )
    assert schema["additionalProperties"] is False
    assert schema["properties"]["operation_id"]["const"] == (
        "raisa-authored-synthetic-check-in-native-harness-bounded-worker-attempt-003"
    )
    assert schema["properties"]["attempt_id"]["const"] == (
        "deepseek-native-synthetic-window-worker-003"
    )
    assert schema["properties"]["broker"]["properties"]["provider_call_started"][
        "maximum"
    ] == 1
    assert schema["properties"]["automatic_retry_count"]["const"] == 0


def test_attempt_three_cli_is_explicit_and_precedes_every_occupied_action() -> None:
    source = inspect.getsource(subject.main)
    assert 'choices=(2, 3)' in source
    assert "configure_attempt_three()" in source
    assert source.index("configure_attempt_three()") < source.index(
        "value = execute_native()"
    )
    occupied = inspect.getsource(subject.execute_native)
    assert occupied.index("checkpoint = load_checkpoint()") < occupied.index(
        "write_json_exclusive(CONSUMED_PATH"
    )
    assert occupied.index("write_json_exclusive(CONSUMED_PATH") < occupied.index(
        "subprocess.Popen("
    )


def test_attempt_three_machine_authority_records_honest_cost_controls() -> None:
    source = inspect.getsource(subject.prepare_attempt)
    for literal in (
        '"maximum_provider_calls": 1',
        '"maximum_output_tokens": 4096',
        '"maximum_upstream_wall_clock_seconds": 300',
        '"maximum_native_wall_clock_seconds": 420',
        '"provider_spend_source": "existing_user_controlled_prepaid_balance"',
        '"broker_currency_cap_enforced": False',
        '"provider_balance_top_up_authorized": False',
    ):
        assert literal in source


def test_attempt_three_keeps_recovered_pre_hmr_terminal_before_root_cleanup() -> None:
    configuration = subject.attempt_three_configuration()
    assert configuration["pre_hmr_terminal_path"].parent == (
        subject.CONTINUITY_ROOT / "attempt-003"
    )
    source = inspect.getsource(subject.execute_native)
    assert "startup_terminal.build_pre_hmr_terminal(" in source
    assert "startup_terminal.write_pre_hmr_terminal_exclusive(" in source
    assert source.index("startup_terminal.write_pre_hmr_terminal_exclusive(") < (
        source.index("cleanup_passed = remove_exact_attempt_root(root, parent)")
    )
    assert source.index("cleanup_passed = remove_exact_attempt_root(root, parent)") < (
        source.index("write_json_exclusive(TERMINAL_PATH, terminal)")
    )


def test_attempt_three_threat_delta_keeps_product_and_retry_surfaces_closed() -> None:
    text = " ".join(THREAT.read_text(encoding="utf-8").split())
    for phrase in (
        "No retry, resume, fallback, second worker",
        "product/database/real-data access",
        "ordinary-practice enablement",
        "generic-status `Arrived`",
        "production, deployment, release",
        "protected-ref action",
    ):
        assert phrase in text
