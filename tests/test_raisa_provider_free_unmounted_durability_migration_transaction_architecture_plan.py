from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / (
    "docs/raisa-provider-free-unmounted-durability-migration-transaction-"
    "architecture-plan.md"
)
DESIGN = PLAN.parent / PLAN.name.replace("-plan.md", "-design.md")
THREAT = ROOT / "docs/security" / PLAN.name.replace(
    "-plan.md", "-threat-model-delta.md"
)


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_architecture_plan_has_exact_api_and_non_authority_boundary() -> None:
    joined = "\n".join((text(PLAN), text(DESIGN), text(THREAT))).lower()
    for phrase in (
        "internal async durability architecture only",
        "graphql remains read-only and unchanged",
        "rest/openapi remains the only command plane and gains no operation",
        "existing staff committed-event get route",
        "no subscription",
        "event-triggered fresh read",
        "not executable ddl",
        "no `app/**`",
        "`alembic/**`",
        "database/source/network/provider contact",
        "creates no",
        "no protected evidence",
        "cryptographic authenticity",
    ):
        assert phrase in joined


def test_future_relation_catalogue_is_exact_and_closed() -> None:
    plan = text(PLAN)
    expected = (
        "context_observation_stream_head",
        "diary_context_aggregate_aliases_v1",
        "diary_context_observation_outbox_v1",
        "context_proofread_observation_admission",
        "context_generation_registry_barrier",
        "context_observer_generation",
        "context_durability_checkpoint",
        "context_recovery_anchor",
        "context_classified_observation_receipt",
        "context_frame_generation",
        "context_invalidation_watermark",
        "context_reassembly_obligation",
        "context_durability_lifecycle",
        "context_durability_audit",
        "context_observation_key_interval",
        "context_recovery_pin",
        "context_service_practice_binding",
        "context_retention_policy",
    )
    for relation in expected:
        assert f"`{relation}`" in plan
    for phrase in (
        "json/jsonb",
        "unbounded text",
        "arrays",
        "raw product uuid",
        "no generic work queue or event store",
        "source-row deletion never cascades",
    ):
        assert phrase in plan.lower()


def test_owner_private_alias_bridge_is_the_only_product_identifier_exception() -> None:
    joined = " ".join(
        "\n".join((text(PLAN), text(DESIGN), text(THREAT))).lower().split()
    )
    assert "sole product-identifier exception" in joined
    for phrase in (
        "(practice_id, product_appointment_uuid)",
        "no runtime principal receives direct table dml",
        "receive neither `select` nor the product id",
        "never copied into the outbox",
        "not governed by the three durability retention families",
        "deletion is disabled by default",
        "never cascades",
        "only the opaque alias enters the outbox",
        "no actual product identifier is present or processed in this "
        "architecture-only tranche",
    ):
        assert phrase in joined


def test_authority_binding_and_transactions_are_fail_closed() -> None:
    joined = " ".join("\n".join((text(PLAN), text(DESIGN))).lower().split())
    for phrase in (
        "session_user",
        "exactly one active",
        "connection pool",
        "may not multiplex",
        "caller-set",
        "custom guc",
        "force rls",
        "noinherit",
        "nobypassrls",
        "fixed schema-qualified search path",
        "no dynamic sql",
        "public",
        "read committed",
        "serializable",
        "for update",
        "same transaction",
        "on conflict do nothing",
        "at most three attempts",
        "new_generation_required",
        "rebase_required",
        "retention_execution_enabled: false",
        "producer neither holds the observer key",
        "only the complete stored admission set",
        "never accepts a caller-supplied decision packet",
        "source-membership digest",
        "at most one `primary` plus at most one `conflict`",
        "complete stored admission set",
        "any retained `conflict` sentinel",
        "later conflicting attempts cannot grow storage without bound",
        "concurrent first attempts race",
        "`on conflict do nothing` is not an outcome",
        "sufficient only for fail-closed rebase",
        "next lifecycle transition",
        "exact anchor",
        "receiver-owned immutable `primary` or `conflict` admission appends may continue",
        "coordinator cannot consume the next admission",
    ):
        assert phrase in joined


def test_continuity_and_retention_reject_unsafe_shortcuts() -> None:
    joined = "\n".join((text(PLAN), text(THREAT))).lower()
    for phrase in (
        "postgresql sequences/identities",
        "uuid/time ordering",
        "aggregate_revision",
        "wal lsn",
        "complete non-consumed generation census",
        "registration/rebaseline and purge",
        "three independent retention families",
        "caller cannot supply/filter the census",
        "one immutable total-order journal",
        "decision` and `key_rotation`",
        "bucket from canonical admitted audit history",
        "generation-local metadata",
        "changes no other generation",
    ):
        assert phrase in joined


def test_database_backed_acceptance_is_future_and_adversarial() -> None:
    plan = " ".join(text(PLAN).lower().split())
    for phrase in (
        "disposable local database",
        "authored synthetic opaque coordinates only",
        "rollback after every producer member",
        "concurrent same-stream producers",
        "concurrent coordinators",
        "after authorized source-row",
        "remains visible after source purge",
        "bounds the position to at most two admission rows",
        "without blocking bounded receiver-owned admission appends",
        "post-decision and post-rotation anchors",
        "lifecycle append",
        "cross-practice reads",
        "caller-set practice guc",
        "every non-producer principal and every durability output",
        "separately disabled product-lifecycle action",
        "incomplete/filtered census",
        "disabled mode performs zero connection",
        "this architecture tranche itself performs none",
        "authored-synthetic migration/ddl rehearsal",
    ):
        assert phrase in plan
