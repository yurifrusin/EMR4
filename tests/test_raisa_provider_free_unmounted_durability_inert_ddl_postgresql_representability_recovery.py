from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RECOVERY = (
    ROOT
    / "docs/raisa-provider-free-unmounted-durability-inert-ddl-rehearsal-postgresql-representability-recovery.md"
)
PLAN = (
    ROOT / "docs/raisa-provider-free-unmounted-durability-inert-ddl-rehearsal-plan.md"
)
DESIGN = (
    ROOT / "docs/raisa-provider-free-unmounted-durability-inert-ddl-rehearsal-design.md"
)
THREAT = (
    ROOT
    / "docs/security/raisa-provider-free-unmounted-durability-inert-ddl-rehearsal-threat-model-delta.md"
)
BODY = (
    ROOT
    / "orchestration/continuity/raisa-provider-free-unmounted-durability-function-trigger-body-architecture/function-trigger-body-architecture-contract.json"
)


def _flat(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


def _walk(value: object):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from _walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk(child)


def test_recovery_preserves_parent_and_closes_effective_population() -> None:
    body = json.loads(BODY.read_text(encoding="utf-8"))
    recovery = _flat(RECOVERY)

    assert (
        body["contract_sha256"]
        == "sha256:9ef411aa353ba6b39d9fbbd769d94ef5a9237bb7c6aa031dbdafce1bfa62ce83"
    )
    assert len(body["body_programs"]) == 22
    for required in (
        "nine entry points, fourteen trigger functions, fourteen trigger declarations and twenty-three programs",
        "cf_guard_appointment_update_v1",
        "trg_cf_appointment_guard",
        "every one of its 22 programs",
    ):
        assert required in recovery


def test_recovery_names_all_six_unrepresentable_trigger_xmin_expressions() -> None:
    body = json.loads(BODY.read_text(encoding="utf-8"))
    trigger_xmin = [
        node
        for node in _walk(body["body_programs"])
        if node.get("kind") == "TRIGGER_COLUMN" and node.get("column") == "xmin"
    ]

    assert len(trigger_xmin) == 6
    recovery = _flat(RECOVERY)
    for required in (
        "RESELECT_BEFORE_TRIGGER_OLD_XMIN",
        "REMOVE_DEFERRED_APPOINTMENT_OLD_XMIN",
        "REMOVE_DEFERRED_EVENT_DELETE_OLD_XMIN",
        "REMOVE_DEFERRED_OUTBOX_DELETE_OLD_XMIN",
        "No trigger row-image field named `xmin`",
    ):
        assert required in recovery


def test_recovery_closes_count_dependency_trigger_and_owner_lowering() -> None:
    combined = " ".join(_flat(path) for path in (RECOVERY, PLAN, DESIGN, THREAT))
    for required in (
        "coalesce(pg_catalog.array_length(set, 1), 0)::pg_catalog.bigint",
        "support helper",
        "CREATE CONSTRAINT TRIGGER",
        "CREATE SCHEMA ... AUTHORIZATION context_schema_owner",
        "all eighteen fabric relations",
        "Application relation owners are untouched",
        "Unknown lock modes fail",
    ):
        assert required in combined


def test_recovery_keeps_later_database_gate_closed() -> None:
    combined = " ".join(_flat(path) for path in (RECOVERY, PLAN, DESIGN, THREAT))
    for required in (
        "does not prove server parse",
        "No SQL execution",
        "database/source contact",
        "patient/product data",
        "runtime wiring",
        "Pages",
        "protected-ref",
    ):
        assert required in combined
