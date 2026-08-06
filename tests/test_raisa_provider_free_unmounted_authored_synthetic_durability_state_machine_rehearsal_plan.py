from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs" / (
    "raisa-provider-free-unmounted-authored-synthetic-durability-state-machine-"
    "rehearsal-plan.md"
)
DESIGN = ROOT / "docs" / (
    "raisa-provider-free-unmounted-authored-synthetic-durability-state-machine-"
    "rehearsal-design.md"
)
THREAT = ROOT / "docs" / "security" / (
    "raisa-provider-free-unmounted-authored-synthetic-durability-state-machine-"
    "rehearsal-threat-model-delta.md"
)


def _flat(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


def test_plan_freezes_parent_result_and_exact_claim_boundary() -> None:
    text = _flat(PLAN)
    for phrase in (
        "raisa_provider_free_unmounted_source_specific_durability_architecture_pass",
        "raisa_provider_free_unmounted_authored_synthetic_durability_state_machine_rehearsal_pass",
        "provider_free_unmounted_authored_synthetic_durability_state_machine_rehearsal",
        "does not prove a table, migration, source observation",
        "migration-and-transaction architecture",
    ):
        assert phrase in text


def test_plan_freezes_exact_state_machine_semantics() -> None:
    text = _flat(PLAN)
    for phrase in (
        "CONTIGUOUS_ADMIT",
        "CONTIGUOUS_NO_INTERSECTION",
        "CONTIGUOUS_FULL_INVALIDATION",
        "Caller input cannot assert redelivery",
        "constant-time comparison",
        "REBASE_REQUIRED",
        "last contiguous position is held",
        "current_diary_projection",
        "current_waiting_room_projection",
        "ONE`, `TWO_TO_FOUR`, `FIVE_PLUS",
        "five member-by-member atomic rollback injections",
        "minimum checkpoint",
        "NEW_GENERATION_REQUIRED",
        "RecoveryAnchor",
        "complete non-consumed-generation census",
        "future-position-fenced atomic transition",
    ):
        assert phrase.lower() in text.lower()


def test_design_and_threat_delta_preserve_non_authority() -> None:
    design = _flat(DESIGN).lower()
    threat = _flat(THREAT).lower()
    for phrase in (
        "pure state transition algebra",
        "fault selector",
        "no database object",
        "no reverse edge",
        "inert eligibility decision",
    ):
        assert phrase in design
    for phrase in (
        "caller declares a duplicate",
        "checkpoint advances after a partial failure",
        "wall clock or existing event ttl",
        "key bytes leak into evidence",
        "passing rehearsal is claimed as live durability",
        "no protected holdout",
        "caller omits the slowest generation",
        "corrupt restart state supplies its own",
        "routine key rotation changes history",
    ):
        assert phrase in threat


def test_plan_owns_only_pure_rehearsal_artifacts() -> None:
    text = _flat(PLAN).lower()
    for phrase in (
        "no `app/**`",
        "no `alembic/**`",
        "no `docs/diary/**`",
        "provider/model/external retrieval: none",
        "database, source, network or browser contact: none",
        "no operational checkpoint",
        "no filesystem state store",
        "docs/branding/",
    ):
        assert phrase.lower() in text
