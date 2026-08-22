from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / (
    "docs/raisa-provider-free-read-only-post-check-in-admission-control-"
    "programme-orientation-plan.md"
)
THREAT = ROOT / (
    "docs/security/raisa-provider-free-read-only-post-check-in-admission-control-"
    "programme-orientation-threat-model-delta.md"
)


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_plan_is_timestamped_full_head_bound_and_read_only() -> None:
    plan = _text(PLAN)
    head = "\n".join(plan.splitlines()[:24])
    assert "Date: 2026-08-22" in head
    assert "Timestamp: 2026-08-22T" in head
    assert "+10:00 (Australia/Brisbane)" in head
    assert "ea05e120d0974542a5a56b2ffde5df0a9494f217" in head
    assert "frozen_for_read_only_execution" in head
    assert "Reasoning level: Extra High" in plan


def test_plan_requires_graph_non_membership_and_exact_absent_target() -> None:
    plan = _text(PLAN)
    for phrase in (
        "operation ID is already recorded",
        "its operation ID is absent",
        "orchestration_harness/check_in_rollout_runbook.py",
        "canonical-check-in-rollout-kill-switch-rollback-runbook.json",
        "the named API-Spine manifest is absent",
        "No application, configuration, OpenAPI/GraphQL, manifest",
    ):
        assert phrase in plan or phrase in _text(THREAT)


def test_api_spine_and_parallelism_boundaries_are_explicit() -> None:
    plan = _text(PLAN)
    for phrase in (
        "typed REST/OpenAPI proposal/confirmation command",
        "GraphQL mutation",
        "declarative API-Spine manifest",
        "DeepSeek V4 Flash/high: `declined`",
        "Gemini 3.7 Flash/high: `reserved`",
        "Native subagents: `declined`",
        "Parallel work packages: none",
    ):
        assert phrase in plan


def test_plan_keeps_every_material_gate_closed() -> None:
    corpus = (_text(PLAN) + _text(THREAT)).lower()
    for phrase in (
        "no ordinary-practice enablement",
        "generic-status `arrived`",
        "waiting-area movement",
        "no product runtime authority",
        "protected refs",
        "preserve `docs/branding/`",
        "explicit-path staging only",
    ):
        assert phrase in corpus
