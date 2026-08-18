from __future__ import annotations

import json
from pathlib import Path

from orchestration_harness.active_operation import validate_active_operation


ROOT = Path(__file__).resolve().parents[1]
PLAN = (
    ROOT
    / "docs/raisa-provider-free-unmounted-default-off-ordinary-practice-canonical-check-in-admission-control-kernel-rehearsal-plan.md"
)
THREAT = (
    ROOT
    / "docs/security/raisa-provider-free-unmounted-default-off-ordinary-practice-canonical-check-in-admission-control-kernel-rehearsal-threat-model-delta.md"
)
LATCH = ROOT / "orchestration/continuity/ariadne-active-operation-latch/current.json"
RECEIPT = (
    ROOT
    / "orchestration/agent_inbox/codex/raisa-provider-free-unmounted-default-off-ordinary-practice-canonical-check-in-admission-control-kernel-rehearsal-preplanning-receipt.json"
)


def test_plan_freezes_exact_zero_active_record_boundary() -> None:
    text = PLAN.read_text(encoding="utf-8")
    assert "Status: `frozen`" in text
    assert "249609a7f0c7131cff376aef315e1ff7742b44d7" in text
    assert "752b521c59f5b44bf46de0cf776a33ac74b8134d" in text
    assert "zero active ordinary-practice records" in text
    assert "cannot produce ordinary admission" in text
    assert "No `app/**`" in text
    assert "at least 192" in text
    assert "fresh Gemini 3.7 Flash/high" in text
    assert "+10:00 (Australia/Brisbane)" in text


def test_threat_delta_keeps_product_and_clockwork_authority_closed() -> None:
    text = THREAT.read_text(encoding="utf-8")
    assert "Executable ordinary enablement" in text
    assert "Activation through transition" in text
    assert "Unknown-commit false success" in text
    assert "Clockwork authority escalation" in text
    assert "Bureaucratic-weight regression" in text
    assert "No `app/**`" in text


def test_latch_and_receipt_bind_all_five_sources() -> None:
    latch = validate_active_operation(json.loads(LATCH.read_text(encoding="utf-8")))
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    assert latch["operation_id"] == (
        "raisa-provider-free-unmounted-default-off-ordinary-practice-canonical-"
        "check-in-admission-control-kernel-rehearsal"
    )
    assert latch["status"] == "in_progress"
    assert latch["source_head"] == "249609a7f0c7131cff376aef315e1ff7742b44d7"
    assert latch["terminal_response"]["permitted"] is False
    assert "zero_active_ordinary_admission_records" in latch["protected_boundaries"]
    assert receipt["status"] == "passed"
    assert receipt["rehydration_sources"] == [
        "live_handover_current_baton",
        "current_authority_allocation",
        "active_plan_and_acceptance",
        "protected_evidence_boundaries",
        "git_refs_and_worktree",
    ]
    assert [lane["lane_id"] for lane in receipt["parallelism_assessment"]["lanes"]] == [
        "deepseek_flash",
        "gemini_verifier",
        "native_subagents",
    ]


def test_owned_runtime_module_is_outside_product_source() -> None:
    module = ROOT / "orchestration_harness/check_in_admission_control.py"
    assert module.is_file()
    source = module.read_text(encoding="utf-8")
    assert "from app" not in source
    assert "import app" not in source
    assert "sqlalchemy" not in source
    assert "httpx" not in source
    assert "os.environ" not in source
