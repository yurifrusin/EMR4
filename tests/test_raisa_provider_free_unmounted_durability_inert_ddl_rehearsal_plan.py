from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs/raisa-provider-free-unmounted-durability-inert-ddl-rehearsal-plan.md"
DESIGN = ROOT / "docs/raisa-provider-free-unmounted-durability-inert-ddl-rehearsal-design.md"
THREAT = (
    ROOT
    / "docs/security/raisa-provider-free-unmounted-durability-inert-ddl-rehearsal-threat-model-delta.md"
)
RECOVERY = (
    ROOT
    / "docs/raisa-provider-free-unmounted-durability-inert-ddl-rehearsal-plan-recovery.md"
)
CURRENT_BODY_REBIND = (
    ROOT
    / "docs/raisa-provider-free-disposable-postgresql-durability-system-xmin-record-projection-recovery.md"
)
STRUCTURAL_PARENT = (
    ROOT
    / "orchestration/continuity/raisa-provider-free-unmounted-durability-migration-transaction-architecture"
    / "migration-transaction-architecture-contract.json"
)
BODY_PARENT = (
    ROOT
    / "orchestration/continuity/raisa-provider-free-unmounted-durability-function-trigger-body-architecture"
    / "function-trigger-body-architecture-contract.json"
)

PLAN_STRUCTURAL_DIGEST = (
    "sha256:4b0ec20ba00010a1034c6d3c5eedfe8de3f329d7cd5ef495e5878689cdaacba8"
)
PLAN_BODY_DIGEST = (
    "sha256:b3eaa041dc96a6117957b9dd9bde0205afd1023fc521b3183410e7b3c4b8b1b1"
)
CURRENT_STRUCTURAL_DIGEST = (
    "sha256:d481b991fa2d6835babe8372722d00775b31432802bdf9ec40e007369b0d34c6"
)
CURRENT_BODY_DIGEST = (
    "sha256:8ede994ba6f9bbeade0eb015bb9dd23dade21934e7c70fa6885a4a67654aab18"
)


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _flat(value: str) -> str:
    return " ".join(value.split())


def test_plan_binds_both_exact_accepted_parents_and_postgresql_16() -> None:
    plan = _text(PLAN)
    structural = json.loads(STRUCTURAL_PARENT.read_text(encoding="utf-8"))
    body = json.loads(BODY_PARENT.read_text(encoding="utf-8"))

    assert structural["contract_sha256"] == CURRENT_STRUCTURAL_DIGEST
    assert body["contract_sha256"] == CURRENT_BODY_DIGEST
    assert structural["postgresql_target"]["major"] == 16
    assert PLAN_STRUCTURAL_DIGEST in plan
    assert PLAN_BODY_DIGEST in plan
    rebind = _text(CURRENT_BODY_REBIND)
    assert CURRENT_STRUCTURAL_DIGEST in rebind
    assert CURRENT_BODY_DIGEST in rebind
    assert "c55d25d6c9704ae4612ef2d123158f71302ab411" in plan
    assert "a93d07405ad35d7d6c0603065625c17ec14ab23e" in plan


def test_plan_freezes_inert_fixed_outputs_and_no_external_parser() -> None:
    plan = _flat(_text(PLAN))
    design = _flat(_text(DESIGN))

    for required in (
        "durability-schema.sql.inert",
        "one closed JSON render manifest",
        "No new dependency, package download, external parser",
        "no caller-selected contract or output path",
        "standard-library-only",
        "two isolated renders produce byte-identical SQL and manifest artifacts",
    ):
        assert required in plan

    assert "The module imports only Python's standard library" in design
    assert "It has no `subprocess`, `socket`, `os.system`" in design


def test_plan_closes_digest_race_retry_and_privilege_lowering() -> None:
    plan = _flat("\n".join((_text(PLAN), _text(RECOVERY))))

    for required in (
        "type-tagged, byte-length-prefixed value",
        "Null has one distinct marker",
        "UTC with six fractional digits",
        "INSERT_OR_RELOAD_COMPARE",
        "must not use `ON CONFLICT DO NOTHING`",
        "`F_CARDINALITY`, SQLSTATE `CF004`",
        "handler reads `CONSTRAINT_NAME`",
        "PROPAGATE_RETRYABLE",
        "not an exception handler",
        "`PUBLIC` execute is revoked before any exact runtime execute grant",
        "Trigger functions have no runtime execute grant",
        "may not emit application DDL or DML",
    ):
        assert required in plan


def test_recovery_reconciles_declared_and_observed_opcode_populations() -> None:
    combined = _flat("\n".join((_text(PLAN), _text(DESIGN), _text(RECOVERY))))

    for required in (
        "22 declared/21 observed instruction opcodes",
        "`DERIVE_BINDING` as the sole unobserved form",
        "34 declared/34 observed expression opcodes",
        "replacement independent challenge",
    ):
        assert required in combined


def test_recovery_closes_parent_omission_activation_boundary() -> None:
    combined = _flat("\n".join((_text(PLAN), _text(DESIGN), _text(RECOVERY))))

    for required in (
        "supersede only those two omission flags",
        "fixed-path inert rendering",
        "does not activate execution, migration, runtime or product authority",
    ):
        assert required in combined


def test_six_phase_order_and_population_are_explicit() -> None:
    plan = _text(PLAN)

    assert "exactly six ordered phases" in plan
    positions = [
        plan.index("1. exact role/schema/type/relation/constraint/index/forced-RLS"),
        plan.index("2. the nine entry-point functions"),
        plan.index("3. the fourteen effective trigger functions"),
        plan.index("4. the fourteen effective trigger declarations"),
        plan.index("5. `PUBLIC` revocation"),
        plan.index("6. non-executed catalogue and privilege expectation comments"),
    ]
    assert positions == sorted(positions)
    assert "forty-four forced-RLS policies" in plan
    assert "twenty-five invariant-enforcement bindings" in plan


def test_static_claim_is_calibrated_and_next_database_gate_is_separate() -> None:
    combined = _flat("\n".join((_text(PLAN), _text(DESIGN), _text(THREAT))))

    for required in (
        "not equivalence to a PostgreSQL server parse",
        "does not prove that PostgreSQL parses or accepts it",
        "provider-free disposable local PostgreSQL parse/catalogue rehearsal",
        "No database or external SQL parser is used",
        "no SQL execution/application, Alembic migration",
        "no database adapter",
    ):
        assert required in combined


def test_forbidden_product_runtime_and_protected_surfaces_are_explicit() -> None:
    combined = _flat("\n".join((_text(PLAN), _text(DESIGN), _text(THREAT))))

    for required in (
        "Patient/product/protected/historical-PHI data: none",
        "application/API/Diary",
        "provider product",
        "runtime wiring",
        "deployment",
        "Pages",
        "protected-ref",
        "`docs/branding/`",
    ):
        assert required in combined
