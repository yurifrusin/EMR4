from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs" / "raisa-provider-free-unmounted-delete-confirm-physical-design-architecture-plan.md"
THREAT = (
    ROOT
    / "docs"
    / "security"
    / "raisa-provider-free-unmounted-delete-confirm-physical-design-architecture-threat-model-delta.md"
)


def test_plan_freezes_narrow_unmounted_authority_and_transaction_design() -> None:
    text = PLAN.read_text(encoding="utf-8")
    required = (
        "frozen_for_provider_free_unmounted_architecture",
        "user_capability_grants",
        "appointment.cancel.confirm",
        "appointment.read",
        "authority_generation BIGINT",
        "confirmAppointmentDeleteProposal",
        "delete-confirm",
        "legacy_receipt_not_replayable",
        "audit_contract_version SMALLINT",
        "status_reason_code",
        "cancellation_reason",
        "response_body_canonical_bytes",
        "READ COMMITTED",
        "cumulative 2000 ms",
        "FOR SHARE",
        "FOR UPDATE",
        "INSERT ... ON CONFLICT DO NOTHING RETURNING",
        "implementation_authorized` remains false",
    )
    for marker in required:
        assert marker in text


def test_plan_preserves_closed_surfaces_and_exact_review_allocation() -> None:
    text = PLAN.read_text(encoding="utf-8")
    required = (
        "Raw compatibility delete",
        "GraphQL remains read-only",
        "Events remain non-authoritative acceleration hints",
        "import no application, migration, database, network or provider module",
        "Gemini 3.6 Flash/high remains the frozen",
        "Gemini 3.7 Flash/high is CLI-advertised",
        "never stage `docs/branding/`",
        "explicit-path",
    )
    for marker in required:
        assert marker in text


def test_threat_delta_separates_authority_effect_receipt_and_readback() -> None:
    text = THREAT.read_text(encoding="utf-8")
    required = (
        "Authored-synthetic application-auth state is mistaken for product authority",
        "Existing users receive authority during migration",
        "Revocation races a command",
        "Target enumeration leaks through idempotency",
        "Full appointment data leaks in a command receipt",
        "Lock waits hang or reset per acquisition",
        "Readback is treated as commit proof",
        "`implementation_authorized` remains false",
    )
    for marker in required:
        assert marker in text
