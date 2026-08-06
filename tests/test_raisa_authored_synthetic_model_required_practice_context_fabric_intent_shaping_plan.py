from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / (
    "docs/raisa-authored-synthetic-model-required-practice-context-fabric-"
    "intent-shaping-rehearsal-plan.md"
)
DESIGN = ROOT / (
    "docs/raisa-authored-synthetic-model-required-practice-context-fabric-"
    "intent-shaping-rehearsal-design.md"
)
THREAT = ROOT / (
    "docs/security/raisa-authored-synthetic-model-required-practice-context-"
    "fabric-intent-shaping-rehearsal-threat-model-delta.md"
)


def test_exact_model_region_reasoning_and_accounting_boundary_is_frozen() -> None:
    text = PLAN.read_text(encoding="utf-8")

    for value in (
        "gemini-2.5-flash",
        "bernie-emr4-dev",
        "emr4-bernie-ai-dev@bernie-emr4-dev.iam.gserviceaccount.com",
        "australia-southeast1-aiplatform.googleapis.com",
        "thinkingBudget: 1024",
        "maxOutputTokens: 2048",
        "USD 0.50",
        "at most two cumulative",
        "Fallback | none",
    ):
        assert value in text


def test_model_is_required_but_cannot_select_authority_or_context_content() -> None:
    plan = PLAN.read_text(encoding="utf-8")
    design = DESIGN.read_text(encoding="utf-8")
    threat = THREAT.read_text(encoding="utf-8")

    assert "The model is mandatory" in plan
    assert "No context frame is sent to the provider" in plan
    assert "The model selects one candidate intent" in design
    assert "backend authority binding" in design
    assert "all authority fields are exact false" in threat
    assert "no ContextFrame" in threat


def test_frozen_descendant_preserves_closed_product_and_command_surfaces() -> None:
    combined = "\n".join(
        path.read_text(encoding="utf-8") for path in (PLAN, DESIGN, THREAT)
    ).lower()

    for boundary in (
        "patient",
        "product-derived",
        "database",
        "watcher",
        "command",
        "deployment",
        "production",
        "pages",
        "protected-ref",
        "docs/branding/",
    ):
        assert boundary in combined


def test_live_handover_and_direction_name_the_accepted_plan() -> None:
    handover = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    direction = (ROOT / "docs/raisa-practice-context-fabric-direction.md").read_text(
        encoding="utf-8"
    )
    implementation = (ROOT / "implementation_plan.md").read_text(encoding="utf-8")

    plan_name = PLAN.name
    assert plan_name in handover
    assert plan_name in direction
    assert plan_name in implementation
    assert "**Occupied model-required intent shaping** — **accepted**" in direction
    assert "44f341481b55f99a18a47838da0f2b7e43a2f73e" in direction
