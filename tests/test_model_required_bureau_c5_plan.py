from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs/emr4-model-required-bureau-c5-disposable-live-development-recovery-plan.md"
THREAT = (
    ROOT
    / "docs/security/emr4-model-required-bureau-c5-disposable-live-development-recovery-threat-model-delta.md"
)


def _normalized(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


def test_c5_plan_freezes_one_disposable_loopback_target_and_fault() -> None:
    plan = PLAN.read_text(encoding="utf-8")
    assert "`c5_disposable_authored_synthetic`" in plan
    assert "`synthetic:c5-recovery-target`" in plan
    assert "IPv4 `127.0.0.1` only" in plan
    assert "OS-assigned ephemeral port" in plan
    assert "injects exactly one fault by terminating" in plan
    assert "`start-c5-disposable-service.v1`" in plan
    assert "`stop-c5-disposable-service.v1`" in plan


def test_c5_plan_freezes_exact_positive_reasoning_provider_envelope() -> None:
    plan = PLAN.read_text(encoding="utf-8")
    for phrase in (
        "`gemini-2.5-flash`",
        "`bernie-emr4-dev`",
        "`emr4-bernie-ai-dev@bernie-emr4-dev.iam.gserviceaccount.com`",
        "`australia-southeast1`",
        "`australia-southeast1-aiplatform.googleapis.com`",
        "`thinkingBudget: 1024`",
        "`maxOutputTokens: 2048`",
        "USD 0.50 total",
        "no call after admission",
        "Fallback | none",
    ):
        assert phrase in plan


def test_c5_model_never_becomes_authority_or_execution_content() -> None:
    plan = PLAN.read_text(encoding="utf-8")
    assert "has no shell, SQL" in plan
    assert "No model output, approval prose, process return code" in plan
    assert "Only the distinct fresh readback" in plan
    assert "one-use execution-evidence reference" in plan
    assert "Yuri's recorded standing programme approval" in plan


def test_c5_process_capability_is_exact_and_credential_free() -> None:
    combined = _normalized(PLAN) + " " + _normalized(THREAT)
    for phrase in (
        "`-I` isolated mode",
        "minimal explicit environment",
        "cannot inherit cloud credentials",
        "never accepts caller-supplied PID",
        "No shell, PowerShell, `cmd`, command string",
        "loopback-only",
        "task-owned",
    ):
        assert phrase in combined


def test_c5_requires_fresh_readback_rollback_and_complete_cleanup() -> None:
    plan = _normalized(PLAN)
    for phrase in (
        "distinct fresh loopback readback",
        "fresh process observation and HTTP read",
        "distinguish verified rollback from inconclusive rollback",
        "prove the port is no longer listening",
        "remove only the exact task-created temporary directory",
        "no C5 runtime resource remains",
    ):
        assert phrase in plan


def test_c5_claim_and_closed_surfaces_remain_narrow() -> None:
    combined = (PLAN.read_text(encoding="utf-8") + THREAT.read_text(encoding="utf-8")).lower()
    for phrase in (
        "occupied_authored_synthetic_disposable_live_development_recovery",
        "patient",
        "product-derived",
        "ordinary service",
        "real practice database",
        "deployment",
        "production",
        "release",
        "pages",
        "protected evidence",
        "protected-ref",
    ):
        assert phrase in combined


def test_c5_does_not_open_context_fabric_implementation() -> None:
    plan = PLAN.read_text(encoding="utf-8")
    assert "The accepted Practice Context Fabric remains a separate staged direction" in plan
    assert "does not implement `ContextNeed`, `ContextFrameSet`, temporal retention" in plan


def test_c5_requires_deterministic_and_fresh_independent_gates_before_live_action() -> None:
    plan = PLAN.read_text(encoding="utf-8")
    assert "Before any target process or candidate-runtime provider call" in plan
    assert "provider-free tests prove" in plan
    assert "fresh Gemini 3.6 Flash/high Antigravity project" in plan
    assert "Only one `pass` opens a distinct pre-execution receipt" in plan
