from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest
import yaml

from scripts.ariadne_antigravity import (
    WorktreeState,
    build_command,
    parse_structured_decision,
    structured_decision_schema,
)
from scripts.ariadne_evidence_gate import (
    COMMAND_MANIFEST_SCHEMA_VERSION,
    DIAGNOSTIC_PACKET_SCHEMA_VERSION,
    admit_command_results,
    assess_diagnostic_packet,
    command_manifest_sha256,
    validate_command_manifest,
)


ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "orchestration" / "harness_settings" / "evidence_led_workflow.yaml"
CF_D2_GATE_ROOT = (
    ROOT / "orchestration" / "continuity" / "ariadne-cf-d2-workflow-fluidity-repair"
)


def _manifest() -> dict:
    return {
        "schema_version": COMMAND_MANIFEST_SCHEMA_VERSION,
        "commands": [
            {"id": "C01", "argv": ["git", "status", "--short", "--branch"]},
            {
                "id": "C02",
                "argv": [
                    r"C:\Python\python.exe",
                    "-m",
                    "pytest",
                    "-q",
                    "tests/test_example.py",
                ],
            },
            {
                "id": "C03",
                "argv": [
                    r"C:\Python\python.exe",
                    "-m",
                    "scripts.verify_repository",
                    "--profile",
                    "fast",
                ],
            },
        ],
    }


def _results(manifest: dict, *, exit_codes: tuple[int, ...] = (0, 0, 0)) -> list[dict]:
    return [
        {"id": command["id"], "argv": command["argv"], "exit_code": exit_code}
        for command, exit_code in zip(manifest["commands"], exit_codes, strict=True)
    ]


def _diagnostic_packet() -> dict:
    return {
        "schema_version": DIAGNOSTIC_PACKET_SCHEMA_VERSION,
        "coordinate": "cfd2_r01_append_anchor_2",
        "hypotheses": [
            {
                "id": "revision_argument",
                "status": "viable",
                "next_observation": "sqlstate_cf_revision",
            },
            {
                "id": "baseline_anchor_digest",
                "status": "viable",
                "next_observation": "sqlstate_cf_digest",
            },
        ],
        "proposed_claim": "necessary_defect",
        "proposed_action": "correction",
        "remaining_diagnostic_attempts": 1,
        "remaining_corrections": 1,
    }


def test_evidence_led_policy_keeps_hard_controls_separate_from_adaptive_flow() -> None:
    policy = yaml.safe_load(POLICY_PATH.read_text(encoding="utf-8"))

    assert policy["schema_version"] == "ariadne.evidence_led_workflow.v1"
    assert "immutable_attempt_evidence" in policy["hard_controls"]
    assert policy["adaptive_flow"]["external_review"].startswith("one_final")
    assert policy["adaptive_flow"]["qualifying_harness_defect"] == (
        "preserve_contain_register_guard_verify_then_resume_active_operation"
    )
    assert policy["adaptive_flow"]["harness_repair_scope"] == (
        "narrowest_repeatable_orchestration_invariant_only"
    )
    assert policy["adaptive_flow"]["harness_repair_user_pause"] == (
        "only_when_existing_user_attention_condition_is_met"
    )
    assert policy["diagnostic_decision"]["coordinate_is_not_assertion"] is True
    assert policy["review_command_evidence"]["representation"] == (
        "ordered_structured_argv"
    )
    assert policy["review_command_evidence"]["shell_wrappers"] == "forbidden"


def test_command_manifest_is_canonical_and_accepts_exact_zero_results() -> None:
    manifest = validate_command_manifest(_manifest())
    digest = command_manifest_sha256(manifest)

    assert digest == command_manifest_sha256(copy.deepcopy(manifest))
    assert len(digest) == 64
    assert admit_command_results(
        manifest=manifest,
        results=_results(manifest),
        decision="pass",
    ) == _results(manifest)


@pytest.mark.parametrize(
    "argv",
    [
        [r"C:\Python\python.exe", r"scripts\run_review.py"],
        ["powershell.exe", "-Command", "git status"],
        ["git", "status", ";", "git", "diff"],
    ],
)
def test_command_manifest_rejects_non_atomic_or_direct_script_commands(
    argv: list[str],
) -> None:
    manifest = _manifest()
    manifest["commands"][0]["argv"] = argv

    with pytest.raises(ValueError):
        validate_command_manifest(manifest)


def test_command_results_reject_substitution_reordering_and_masked_failure() -> None:
    manifest = validate_command_manifest(_manifest())
    substituted = _results(manifest)
    substituted[1]["argv"] = [*substituted[1]["argv"], "tests/test_extra.py"]
    with pytest.raises(ValueError, match="exactly match"):
        admit_command_results(
            manifest=manifest,
            results=substituted,
            decision="pass",
        )

    reordered = list(reversed(_results(manifest)))
    with pytest.raises(ValueError, match="exactly match"):
        admit_command_results(
            manifest=manifest,
            results=reordered,
            decision="pass",
        )

    with pytest.raises(ValueError, match="every command exit code"):
        admit_command_results(
            manifest=manifest,
            results=_results(manifest, exit_codes=(1, 0, 0)),
            decision="pass",
        )


def test_diagnostic_gate_rejects_exclusive_cause_with_two_viable_hypotheses() -> None:
    packet = _diagnostic_packet()
    packet["proposed_claim"] = "exclusive_cause"

    decision = assess_diagnostic_packet(packet)

    assert decision["status"] == "revision_required"
    assert "exclusive_cause_not_isolated" in decision["reasons"]


def test_diagnostic_gate_rejects_correction_without_distinct_next_evidence() -> None:
    packet = _diagnostic_packet()
    for hypothesis in packet["hypotheses"]:
        hypothesis["next_observation"] = "same_nonzero_null_sqlstate"

    decision = assess_diagnostic_packet(packet)

    assert decision["status"] == "revision_required"
    assert "correction_would_not_create_discriminating_evidence" in decision["reasons"]


def test_cf_d2_retrospective_gate_rejects_the_insufficient_correction() -> None:
    packet = json.loads(
        (CF_D2_GATE_ROOT / "cf-d2-anchor-diagnostic-decision-packet.json").read_text(
            encoding="utf-8"
        )
    )
    committed = json.loads(
        (CF_D2_GATE_ROOT / "cf-d2-anchor-diagnostic-decision.json").read_text(
            encoding="utf-8"
        )
    )

    assert assess_diagnostic_packet(packet) == committed
    assert committed["status"] == "revision_required"
    assert committed["reasons"] == [
        "correction_would_not_create_discriminating_evidence"
    ]


def test_diagnostic_gate_allows_necessary_correction_that_discriminates_next() -> None:
    decision = assess_diagnostic_packet(_diagnostic_packet())

    assert decision == {
        "schema_version": "ariadne.evidence-gate-decision.v1",
        "status": "proceed",
        "coordinate": "cfd2_r01_append_anchor_2",
        "viable_hypothesis_ids": ["revision_argument", "baseline_anchor_digest"],
        "distinct_observations": ["sqlstate_cf_revision", "sqlstate_cf_digest"],
        "reasons": [],
    }


def test_diagnostic_gate_makes_explicit_stop_a_valid_terminal_outcome() -> None:
    packet = _diagnostic_packet()
    packet["proposed_claim"] = "observation_only"
    packet["proposed_action"] = "stop"
    packet["remaining_diagnostic_attempts"] = 0
    packet["remaining_corrections"] = 0

    decision = assess_diagnostic_packet(packet)

    assert decision["status"] == "stop"
    assert decision["reasons"] == []


def test_antigravity_manifest_schema_and_parser_bind_exact_command_results() -> None:
    manifest = validate_command_manifest(_manifest())
    schema = structured_decision_schema(manifest)
    state = WorktreeState(
        root=ROOT,
        branch="codex/example",
        head="0" * 40,
        dirty=False,
    )
    command = build_command(
        packet="Review the candidate.",
        state=state,
        model="gemini-3.6-flash-high",
        os_sandbox=False,
        command_manifest=manifest,
    )

    assert schema["required"] == ["decision", "review", "command_results"]
    command_results_schema = schema["properties"]["command_results"]
    assert command_results_schema["minItems"] == 3
    assert command_results_schema["maxItems"] == 3
    assert "prefixItems" not in command_results_schema
    assert command_results_schema["items"]["properties"]["id"] == {
        "enum": ["C01", "C02", "C03"]
    }
    assert command_results_schema["items"]["properties"]["argv"]["items"] == {
        "type": "string"
    }
    assert "BOUND COMMAND MANIFEST" in command[command.index("-p") + 1]

    envelope = {
        "decision": "pass",
        "review": "All exact commands passed.",
        "command_results": _results(manifest),
    }
    assert parse_structured_decision(
        json.dumps(envelope),
        manifest,
    )["command_results"] == _results(manifest)

    envelope["command_results"][0]["exit_code"] = 1
    with pytest.raises(RuntimeError, match="exactly one schema-valid"):
        parse_structured_decision(json.dumps(envelope), manifest)
