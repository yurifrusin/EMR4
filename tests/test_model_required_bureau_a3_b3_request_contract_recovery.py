from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import subprocess

import pytest

from scripts import model_required_bureau_a3_b3_contracts as parent
from scripts import model_required_bureau_a3_b3_recovery_contracts as recovery
from scripts import model_required_bureau_a3_b3_recovery_acceptance as acceptance
from scripts import model_required_bureau_a3_b3_recovery_live as recovery_live


ROOT = Path(__file__).resolve().parents[1]


def _context(lane: str) -> dict:
    path = (
        recovery.RAYLEEN_CONTEXT_PATH
        if lane == recovery.LANE_RAYLEEN
        else recovery.DAVIDA_CONTEXT_PATH
    )
    return recovery.load_object(path)


@pytest.mark.parametrize("lane", sorted(recovery.LANES))
def test_first_request_uses_bounded_positive_reasoning_and_headroom(
    lane: str,
) -> None:
    context = _context(lane)
    old = parent.build_vertex_request(lane, context)
    new = recovery.build_vertex_request(lane, context)
    expected = deepcopy(old)
    expected["generationConfig"]["maxOutputTokens"] = 2048
    expected["generationConfig"]["thinkingConfig"] = {"thinkingBudget": 1024}
    assert new == expected
    assert new["generationConfig"]["maxOutputTokens"] == 2048
    assert new["generationConfig"]["thinkingConfig"] == {"thinkingBudget": 1024}
    assert new["generationConfig"]["responseSchema"] == old[
        "generationConfig"
    ]["responseSchema"]
    assert new["contents"] == old["contents"]
    assert recovery.prefixed_sha256(new) != recovery.prefixed_sha256(old)


def test_recovery_ids_policy_and_parent_ledger_are_distinct() -> None:
    packet = recovery_live._request_packet(
        recovery.LANE_RAYLEEN,
        _context(recovery.LANE_RAYLEEN),
        attempt_number=1,
        correction_of=None,
        correction_reason_code=None,
    )
    ledger = recovery_live._initial_cost_ledger()
    assert packet["policy_id"] == recovery.POLICY_ID
    assert packet["attempt_id"].startswith("a3-b3-recovery-")
    assert packet["ledger_id"].startswith("ledger-a3-b3-recovery-")
    assert ledger["tranche_id"].endswith("request-contract-recovery-001")
    assert recovery.ARTIFACT_ROOT != parent.ARTIFACT_ROOT


@pytest.mark.parametrize(
    ("candidate", "reason"),
    [
        ({}, "provider_content_missing"),
        ({"content": None}, "provider_content_invalid"),
        ({"content": {}}, "provider_parts_invalid"),
        ({"content": {"parts": []}}, "provider_parts_empty"),
        (
            {"content": {"parts": [{"text": "{}"}, {"text": "{}"}]}},
            "provider_parts_count_invalid",
        ),
        (
            {"content": {"parts": [{"text": "hidden", "thought": True}]}},
            "provider_part_thought_invalid",
        ),
        (
            {"content": {"parts": [{"functionCall": {"name": "x"}}]}},
            "provider_part_non_text_invalid",
        ),
    ],
)
def test_response_shape_failures_are_precise_and_closed(
    candidate: dict, reason: str
) -> None:
    with pytest.raises(recovery.ContractError, match=f"^{reason}$"):
        recovery.extract_provider_candidate({"candidates": [candidate]})


def test_safe_shape_metadata_contains_no_provider_values() -> None:
    packet = {
        "candidates": [
            {
                "finishReason": "MAX_TOKENS",
                "content": {
                    "parts": [
                        {"text": "secret-provider-text"},
                        {"thought": True, "text": "secret-thought"},
                    ]
                },
            }
        ],
        "promptFeedback": {"blockReason": "SAFETY", "blockReasonMessage": "secret"},
        "usageMetadata": {
            "promptTokenCount": 100,
            "candidatesTokenCount": 0,
            "thoughtsTokenCount": 512,
            "totalTokenCount": 612,
        },
    }
    safe = recovery.bounded_provider_metadata(packet)
    assert safe["finish_reason"] == "MAX_TOKENS"
    assert safe["parts_count"] == 2
    assert safe["part_kinds"] == ["text", "thought"]
    assert safe["text_utf8_bytes"] == len("secret-provider-text".encode())
    assert safe["prompt_block_reason"] == "SAFETY"
    serialized = json.dumps(safe)
    assert "secret-provider-text" not in serialized
    assert "secret-thought" not in serialized
    assert "blockReasonMessage" not in serialized


def test_valid_single_text_part_still_uses_strict_json_object() -> None:
    body = {"intent": "filter"}
    packet = {"candidates": [{"content": {"parts": [{"text": json.dumps(body)}]}}]}
    assert recovery.extract_provider_candidate(packet) == body


def test_recovery_runtime_names_do_not_collide_with_historical_names() -> None:
    names = recovery_live._names(recovery.LANE_RAYLEEN, 1)
    historical = {
        "network": "emr4-a3-b3-rayleen-1-internal",
        "relay_container": "emr4-a3-b3-rayleen-1-relay",
        "cell_container": "emr4-a3-b3-rayleen-1-cell",
        "relay_image": "emr4-a3-b3-rayleen-1-relay:v1",
        "cell_image": "emr4-a3-b3-rayleen-1-cell:v1",
    }
    assert set(names.values()).isdisjoint(historical.values())


def test_committed_provider_free_recovery_evidence_passes_acceptance() -> None:
    result = acceptance.run_acceptance(require_dry_run=True)
    assert result["passed"] is True
    assert result["result"].endswith("recovery_acceptance_pass")


def test_recovery_audit_namespace_is_lf_stable_in_fresh_windows_worktrees() -> None:
    result = subprocess.run(
        [
            "git",
            "check-attr",
            "eol",
            "--",
            (
                "orchestration/continuity/"
                "model-required-bureau-a3-b3-request-contract-recovery/"
                "rayleen-a3-attempt-1-audit.jsonl"
            ),
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        shell=False,
    )
    assert result.stdout.strip().endswith("eol: lf")
