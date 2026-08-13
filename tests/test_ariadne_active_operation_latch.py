import copy
import json
from pathlib import Path

import pytest

from orchestration_harness.active_operation import (
    assess_interruption,
    receipt_projection,
    validate_active_operation,
)


ROOT = Path(__file__).resolve().parents[1]
CURRENT = (
    ROOT
    / "orchestration"
    / "continuity"
    / "ariadne-active-operation-latch"
    / "current.json"
)
SCHEMA = CURRENT.with_name("active-operation.schema.json")


def latch() -> dict:
    return json.loads(CURRENT.read_text(encoding="utf-8"))


def in_progress_latch() -> dict:
    value = latch()
    value["status"] = "in_progress"
    value["terminal_response"] = {
        "permitted": False,
        "reason": "unfinished_authorized_operation",
    }
    return value


def test_current_latch_matches_schema_and_pure_validator() -> None:
    jsonschema = pytest.importorskip("jsonschema")
    value = latch()
    jsonschema.validate(value, json.loads(SCHEMA.read_text(encoding="utf-8")))
    assert validate_active_operation(value) == value
    projection = receipt_projection(value)
    assert projection["status"] == value["status"]
    assert projection["terminal_handback_permitted"] is value["terminal_response"][
        "permitted"
    ]
    assert projection["next_executable_stage"] == value["checkpoint"][
        "next_executable_stage"
    ]


@pytest.mark.parametrize(
    ("prompt_class", "decision"),
    [
        ("side_question", "answer_then_resume"),
        ("status_request", "answer_then_resume"),
        ("scope_addition", "merge_then_resume"),
        ("user_decision_response", "merge_then_resume"),
        ("none", "resume_operation"),
    ],
)
def test_non_replacing_interruption_resumes_active_operation(
    prompt_class: str, decision: str
) -> None:
    result = assess_interruption(in_progress_latch(), prompt_class=prompt_class)
    assert result["status"] == "passed"
    assert result["decision"] == decision
    assert result["terminal_handback_permitted"] is False
    assert result["next_executable_stage"]


@pytest.mark.parametrize("prompt_class", ["explicit_pause", "explicit_redirect"])
def test_explicit_pause_or_redirect_requires_latch_update_first(
    prompt_class: str,
) -> None:
    result = assess_interruption(in_progress_latch(), prompt_class=prompt_class)
    assert result["decision"] == "update_latch_before_terminal_or_replacement"
    assert result["terminal_handback_permitted"] is False


def test_terminal_intent_fails_closed_while_work_is_in_progress() -> None:
    result = assess_interruption(
        in_progress_latch(), prompt_class="side_question", terminal_intent=True
    )
    assert result["status"] == "revision_required"
    assert result["terminal_handback_permitted"] is False
    assert result["reasons"] == ["unfinished_authorized_operation"]


def hostile_mutations() -> list[dict]:
    base = in_progress_latch()
    cases: list[dict] = []
    for key in base:
        candidate = copy.deepcopy(base)
        candidate.pop(key)
        cases.append(candidate)
    candidate = copy.deepcopy(base)
    candidate["unexpected"] = True
    cases.append(candidate)
    replacements = [
        (("schema_version",), "v2"),
        (("operation_id",), "Bad operation"),
        (("active_tranche",), ""),
        (("objective",), " "),
        (("status",), "running"),
        (("source_head",), "17add9ba"),
        (("authority_source",), ""),
        (("checkpoint", "completed_stage"), ""),
        (("checkpoint", "next_executable_stage"), None),
        (("checkpoint", "retry_counters", "implementation"), -1),
        (("checkpoint", "retry_counters", "verification"), True),
        (("checkpoint", "settings_fingerprint"), "sha256:short"),
        (
            (
                "interruption_policy",
                "chronological_last_prompt_is_controlling_authority",
            ),
            True,
        ),
        (("interruption_policy", "side_question_behavior"), "replace"),
        (("interruption_policy", "status_request_behavior"), "stop"),
        (("interruption_policy", "scope_addition_behavior"), "replace"),
        (
            ("interruption_policy", "replacement_requires_explicit_pause_or_redirect"),
            False,
        ),
        (("resume_after_compaction",), False),
        (("user_attention", "required"), True),
        (("user_attention", "reason"), "invented fork"),
        (("terminal_response", "permitted"), True),
        (("terminal_response", "reason"), "side question answered"),
        (("protected_boundaries",), []),
        (("protected_boundaries",), ["duplicate", "duplicate"]),
        (("protected_boundaries",), [1]),
    ]
    for path, replacement in replacements:
        candidate = copy.deepcopy(base)
        target = candidate
        for part in path[:-1]:
            target = target[part]
        target[path[-1]] = replacement
        cases.append(candidate)
    return cases


@pytest.mark.parametrize("candidate", hostile_mutations())
def test_at_least_thirty_hostile_latch_mutations_fail_closed(candidate: dict) -> None:
    assert len(hostile_mutations()) >= 30
    with pytest.raises(ValueError):
        validate_active_operation(candidate)
