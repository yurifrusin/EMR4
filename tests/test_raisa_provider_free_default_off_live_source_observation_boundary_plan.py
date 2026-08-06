from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs/raisa-provider-free-default-off-live-source-observation-boundary-plan.md"
DESIGN = ROOT / "docs/raisa-provider-free-default-off-live-source-observation-boundary-design.md"
THREAT = (
    ROOT
    / "docs/security/raisa-provider-free-default-off-live-source-observation-boundary-threat-model-delta.md"
)


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_boundary_is_architecture_only_provider_free_and_default_off() -> None:
    joined = "\n".join((_text(PLAN), _text(DESIGN), _text(THREAT))).lower()
    for phrase in (
        "architecture-only",
        "provider-free",
        "default-off",
        "observer is not truth",
        "returns_data: false",
        "read_authority: false",
        "provider_authority: false",
        "command_authority: false",
        "persistence_authority: false",
    ):
        assert phrase in joined


def test_three_authority_planes_are_separate() -> None:
    plan = _text(PLAN)
    for phrase in (
        "Observation plane",
        "Temporal classification plane",
        "Fresh-read plane",
        "No plane may inherit",
        "Observer identity, binding, policy, checkpoint and signal are ineligible",
    ):
        assert phrase in plan


def test_typed_contracts_and_minimum_coordinates_are_frozen() -> None:
    plan = _text(PLAN)
    for name in (
        "LiveSourceObservationPolicy",
        "LiveSourceObserverBinding",
        "CommittedChangeObservation",
        "SyntheticObservationClassificationActivation",
        "ObservationAdmissionDecision",
        "ObservationToTemporalSignalTrace",
        "ObservationContinuityRequirement",
        "TemporalSignalEnvelope",
        "ContextReassemblyRequirement",
        "FreshContextReassemblyInstruction",
    ):
        assert f"`{name}`" in plan
    for phrase in (
        "monotonic transaction/outbox position",
        "observer generation",
        "aggregate revision",
        "practice-binding digest",
        "opaque aggregate reference",
        "binding, policy, source-contract",
        "alias-registry and impact-policy digests",
    ):
        assert phrase in plan


def test_payload_and_ordering_fail_closed() -> None:
    joined = "\n".join((_text(PLAN), _text(DESIGN), _text(THREAT))).lower()
    for phrase in (
        "payload-free",
        "patient identifier",
        "free text",
        "before/after",
        "replacement context",
        "wall-clock time",
        "full invalidation",
        "new baseline",
        "overflow",
        "restart uncertainty",
    ):
        assert phrase in joined


def test_baseline_precedes_frame_binding_and_recovery_is_monotonic() -> None:
    joined = "\n".join((_text(PLAN), _text(DESIGN))).lower()
    for phrase in (
        "establish a monotonic source baseline",
        "bind a newly assembled frame generation",
        "cannot make already invalidated context current again",
        "cannot return retired context to `current`",
    ):
        assert phrase in joined


def test_api_spine_remains_read_event_command_separated() -> None:
    plan = _text(PLAN)
    for phrase in (
        "GraphQL remains a scoped read/context graph",
        "REST/OpenAPI remains the sole command plane",
        "async metadata may announce committed change",
        "No GraphQL field, subscription, REST path, OpenAPI operation",
    ):
        assert phrase in plan


def test_future_durability_is_required_but_not_claimed() -> None:
    joined = "\n".join((_text(PLAN), _text(DESIGN), _text(THREAT))).lower()
    for phrase in (
        "durable classified checkpoint",
        "atomic persistence",
        "makes no no-loss claim",
        "architecture makes no persistence claim",
        "checkpoint durability",
    ):
        assert phrase in joined


def test_disabled_and_pending_requirement_rules_are_fail_closed() -> None:
    joined = "\n".join((_text(PLAN), _text(DESIGN), _text(THREAT))).lower()
    for phrase in (
        "zero source connection",
        "credential acquisition",
        "cursor movement",
        "exactly one pending requirement",
        "coalesce",
        "read storm",
    ):
        assert phrase in joined


def test_event_cannot_supply_impact_or_no_loss_cursor() -> None:
    joined = "\n".join((_text(PLAN), _text(DESIGN), _text(THREAT))).lower()
    for phrase in (
        "event-supplied `temporalsignalenvelope`",
        "sealed manifest",
        "(occurred_at, event_id)",
        "does not establish a no-loss",
        "unknown impact",
        "bounded full invalidation",
        "mandatory event/schema/aggregate floor",
        "omission can never narrow",
    ):
        assert phrase in joined


def test_metadata_channels_are_canonical_and_backend_issued() -> None:
    joined = "\n".join((_text(PLAN), _text(DESIGN), _text(THREAT))).lower()
    for phrase in (
        "domain-separated keyed digest",
        "backend-issued registered alias",
        "sha256:[0-9a-f]{64}",
        "maximum 96",
        "closed enums",
        "non-boolean integers",
        "source-supplied selector digests",
        "correlation ids",
        "reason strings",
    ):
        assert phrase in joined


def test_synthetic_positive_path_cannot_enable_live_observer() -> None:
    joined = "\n".join((_text(PLAN), _text(DESIGN), _text(THREAT))).lower()
    for phrase in (
        "activation_mode: authored_synthetic_rehearsal",
        "source_connection: false",
        "credential_acquisition: false",
        "cursor_persistence: false",
        "current policy remains disabled",
        "no synthetic artifact can enable a source connection",
        "observer_disabled",
        "be accepted with `live` evidence mode",
    ):
        assert phrase in joined


def test_forbidden_runtime_surfaces_remain_closed() -> None:
    joined = "\n".join((_text(PLAN), _text(THREAT))).lower()
    for phrase in (
        "no `app/**`",
        "no `docs/diary/**`",
        "graphql schema change",
        "database migration/table/trigger",
        "outbox/feed/watcher/listener",
        "background worker",
        "checkpoint store",
        "product source read",
        "patient/product/protected data",
        "command/write",
        "deployment",
        "production",
        "release",
        "pages",
        "protected-ref movement",
        "preserve and exclude `docs/branding/`",
    ):
        assert phrase in joined


def test_next_descendant_remains_unmounted_and_authored_synthetic() -> None:
    plan = _text(PLAN)
    assert "provider-free,\nunmounted, authored-synthetic" in plan
    assert "pure typed constructors, validators, admission" in plan
    assert "the rehearsal may not\nmount a source, database, feed, watcher, listener" in plan
