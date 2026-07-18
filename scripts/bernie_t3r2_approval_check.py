"""Validate the blocked T3R2 synthetic live-comparison approval packet."""

from __future__ import annotations

from collections import Counter
import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services.ai.evals.bernie_shadow_silver_v2 import (
    build_silver_v2_shadow_cases,
    build_t3r1_shadow_report,
)
from scripts.bernie_shadow_live_gate_check import assert_gate_blocked, load_gate


DEFAULT_PACKET_PATH = ROOT / "docs" / "bernie-t3r2-synthetic-live-comparison-approval.json"
SCHEMA_VERSION = "emr4.bernie.t3r2_live_comparison_approval.v1"
ACTIONS = ("create", "move", "resize", "cancel", "status_change", "explain_schedule")
FORMS = (
    "one_shot",
    "clarification",
    "correction",
    "reversal",
    "ellipsis",
    "anaphora",
    "repeated_request",
    "session_restart",
)


def _canonical_hash(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return "sha256:" + hashlib.sha256(raw.encode("utf-8")).hexdigest()


def load_packet(path: Path = DEFAULT_PACKET_PATH) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("T3R2 approval packet must be a JSON object")
    return payload


def expected_selection() -> tuple[Any, ...]:
    cases = build_silver_v2_shadow_cases()
    selected = []
    for action_index, action in enumerate(ACTIONS):
        for form_index, dialogue_form in enumerate(FORMS):
            if (action_index + form_index) % 2:
                continue
            noise = "high" if (action_index + form_index) % 4 == 0 else "medium"
            candidates = sorted(
                (
                    case
                    for case in cases
                    if dict(case.metadata)["action"] == action
                    and dict(case.metadata)["dialogue_form"] == dialogue_form
                    and dict(case.metadata)["noise_level"] == noise
                ),
                key=lambda case: case.case_id,
            )
            if not candidates:
                raise AssertionError(f"missing selection cell: {action}/{dialogue_form}/{noise}")
            selected.append(candidates[0])
    return tuple(selected)


def assert_packet_blocked(packet: dict[str, Any]) -> None:
    assert_gate_blocked(load_gate())
    assert packet["schema_version"] == SCHEMA_VERSION
    assert packet["decision"] == "blocked"
    assert packet["authorizes_provider_calls"] is False
    assert packet["requires_explicit_yuri_approval"] is True

    lanes = packet["candidate_lanes"]
    assert len(lanes) == 2
    assert {lane["lane_id"] for lane in lanes} == {
        "openai_gpt_subscription",
        "google_gemini_subscription",
    }
    assert all(lane["access_basis"] == "subscription_plan" for lane in lanes)
    assert all(lane["exact_resolved_model_revision"] is None for lane in lanes)
    assert all(lane["silent_fallback_allowed"] is False for lane in lanes)
    assert all(lane["approved"] is False for lane in lanes)

    selected = expected_selection()
    selected_ids = [case.case_id for case in selected]
    population = packet["population"]
    assert population["selected_case_ids"] == selected_ids
    assert population["selection_hash"] == _canonical_hash(selected_ids)
    assert population["case_count"] == len(selected) == 24
    t3r1 = build_t3r1_shadow_report()
    assert population["source_projection_hash"] == t3r1["projection"]["projection_hash"]

    metadata = [dict(case.metadata) for case in selected]
    assert population["by_action"] == dict(sorted(Counter(item["action"] for item in metadata).items()))
    assert population["by_dialogue_form"] == dict(
        sorted(Counter(item["dialogue_form"] for item in metadata).items())
    )
    assert population["by_noise_level"] == dict(
        sorted(Counter(item["noise_level"] for item in metadata).items())
    )

    limits = packet["execution_limits"]
    assert limits["max_scheduled_samples"] == 24 * 2 * 2 == 96
    assert limits["max_attempts_per_scheduled_sample"] == 1
    assert limits["automatic_retries"] is False
    assert limits["provider_error_counts_as_consumed_sample"] is True
    assert limits["max_serialized_prompt_chars_per_sample"] == 12000
    assert limits["max_response_chars_per_sample"] == 4000
    assert limits["max_wall_clock_minutes"] == 120

    cost = packet["cost_control"]
    assert cost["marginal_dollar_cost_required"] is False
    assert cost["explicit_run_approval_required"] is True
    assert cost["explicit_run_approval_granted"] is False

    privacy = packet["privacy_and_retention"]
    assert privacy["synthetic_corpus_only"] is True
    assert privacy["persist_normalized_response_and_hash_only"] is True
    assert privacy["provider_account_retention_reviewed"] is False
    assert privacy["privacy_and_retention_approved"] is False
    forbidden_inputs = (
        "patient_or_practice_data_allowed",
        "historical_diary_material_allowed",
        "protected_holdout_material_allowed",
        "external_corpus_material_allowed",
        "raw_prompt_commit",
        "raw_response_commit",
        "raw_response_local_persistence",
    )
    assert all(privacy[field] is False for field in forbidden_inputs)

    kill_switch = packet["kill_switch"]
    assert kill_switch["pre_call_gate_check_required"] is True
    assert kill_switch["automatic_retry_loop_allowed"] is False
    assert kill_switch["implementation_verified"] is False
    assert kill_switch["reviewed"] is False

    evidence = packet["evidence_protocol"]
    assert evidence["exact_resolved_model_revision_required"] is True
    assert evidence["model_quality_claim_authorized"] is False
    assert evidence["promotion_claim_authorized"] is False
    assert all(value is False for value in packet["authority"].values())
    assert packet["approval"] == {
        "reviewer": "",
        "approved_on": "",
        "approval_expires_on": "",
        "decision": "blocked",
    }


def build_status(path: Path = DEFAULT_PACKET_PATH) -> dict[str, Any]:
    packet = load_packet(path)
    assert_packet_blocked(packet)
    return {
        "schema_version": "emr4.bernie.t3r2_approval_status.v1",
        "decision": "blocked",
        "selected_case_count": packet["population"]["case_count"],
        "candidate_lane_count": len(packet["candidate_lanes"]),
        "maximum_scheduled_samples": packet["execution_limits"]["max_scheduled_samples"],
        "provider_calls_performed": False,
        "external_calls_ready": False,
        "awaiting": [
            "exact_model_revisions",
            "privacy_and_retention_approval",
            "kill_switch_verification",
            "explicit_yuri_run_approval",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packet", type=Path, default=DEFAULT_PACKET_PATH)
    args = parser.parse_args()
    print(json.dumps(build_status(args.packet), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
