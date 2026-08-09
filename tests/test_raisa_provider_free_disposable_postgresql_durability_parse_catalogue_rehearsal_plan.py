from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = (
    ROOT
    / "docs/raisa-provider-free-disposable-postgresql-durability-parse-catalogue-rehearsal-plan.md"
)
DESIGN = (
    ROOT
    / "docs/raisa-provider-free-disposable-postgresql-durability-parse-catalogue-rehearsal-design.md"
)
THREAT = (
    ROOT
    / "docs/security/raisa-provider-free-disposable-postgresql-durability-parse-catalogue-rehearsal-threat-model-delta.md"
)
PARENT_SQL = (
    ROOT
    / "orchestration/continuity/raisa-provider-free-unmounted-durability-inert-ddl-rehearsal"
    / "durability-schema.sql.inert"
)
PARENT_MANIFEST = PARENT_SQL.with_name("render-manifest.json")
RECOVERY = (
    ROOT
    / "docs/raisa-provider-free-disposable-postgresql-durability-parse-catalogue-digest-nullability-recovery.md"
)
ROW_PROJECTION_RECOVERY = (
    ROOT
    / "docs/raisa-provider-free-disposable-postgresql-durability-parse-catalogue-row-composite-projection-order-rebind.md"
)
SPECIAL_FORM_REBIND = (
    ROOT
    / "docs/raisa-provider-free-disposable-postgresql-durability-parse-catalogue-body-special-form-rebind.md"
)
REGISTRATION_RLS_REBIND = (
    ROOT
    / "docs/raisa-provider-free-disposable-postgresql-durability-parse-catalogue-registration-rls-rebind.md"
)
SYSTEM_XMIN_REBIND = (
    ROOT
    / "docs/raisa-provider-free-disposable-postgresql-durability-parse-catalogue-system-xmin-record-projection-rebind.md"
)
SYSTEM_XMIN_ALIAS_REBIND = (
    ROOT
    / "docs/raisa-provider-free-disposable-postgresql-durability-parse-catalogue-system-xmin-explicit-alias-rebind.md"
)
SYSTEM_XMIN_RECORD_ACCESS_REBIND = (
    ROOT
    / "docs/raisa-provider-free-disposable-postgresql-durability-parse-catalogue-system-xmin-record-access-rebind.md"
)
TOP_LEVEL_XID_INSERT_RELOAD_RECOVERY = (
    ROOT
    / "docs/raisa-provider-free-disposable-postgresql-durability-top-level-xid-insert-reload-recovery.md"
)
RLS_LOCK_VISIBILITY_REBIND = (
    ROOT
    / "docs/raisa-provider-free-disposable-postgresql-durability-parse-catalogue-rls-lock-visibility-rebind.md"
)
INTERVAL_CONSTRUCTION_REBIND = (
    ROOT
    / "docs/raisa-provider-free-disposable-postgresql-durability-parse-catalogue-interval-construction-rebind.md"
)
UUID_MINIMUM_REBIND = (
    ROOT
    / "docs/raisa-provider-free-disposable-postgresql-durability-parse-catalogue-uuid-minimum-rebind.md"
)
JSON_KEY_SET_ORDER_RECOVERY = (
    ROOT
    / "docs/raisa-provider-free-disposable-postgresql-durability-json-key-set-order-recovery.md"
)
JSON_KEY_SET_ORDER_REBIND = (
    ROOT
    / "docs/raisa-provider-free-disposable-postgresql-durability-parse-catalogue-json-key-set-order-rebind.md"
)
ALIAS_LOCK_VISIBILITY_REBIND = (
    ROOT
    / "docs/raisa-provider-free-disposable-postgresql-durability-parse-catalogue-"
    "alias-lock-visibility-rebind.md"
)

PARENT_HEAD = "958f8178c872854ab0f8e1c56dbb9fe46afbea22"
PLANNING_BASELINE = "253230a25ab172b90bc5f44772670c7df89b3052"
PARENT_DIGEST = "64cbc2b0e17276387c6815af02a2d0635fc538e3408995c1054ecbc708b5cbae"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _flat(*paths: Path) -> str:
    return " ".join("\n".join(_text(path) for path in paths).split())


def test_plan_binds_exact_accepted_parent_bytes_and_manifest() -> None:
    plan = _flat(
        PLAN,
        RECOVERY,
        ROW_PROJECTION_RECOVERY,
        SPECIAL_FORM_REBIND,
        REGISTRATION_RLS_REBIND,
        SYSTEM_XMIN_REBIND,
        SYSTEM_XMIN_ALIAS_REBIND,
        SYSTEM_XMIN_RECORD_ACCESS_REBIND,
        TOP_LEVEL_XID_INSERT_RELOAD_RECOVERY,
        RLS_LOCK_VISIBILITY_REBIND,
        INTERVAL_CONSTRUCTION_REBIND,
        UUID_MINIMUM_REBIND,
        JSON_KEY_SET_ORDER_RECOVERY,
        JSON_KEY_SET_ORDER_REBIND,
        ALIAS_LOCK_VISIBILITY_REBIND,
    )
    manifest = json.loads(PARENT_MANIFEST.read_text(encoding="utf-8"))

    raw = PARENT_SQL.read_bytes()
    assert b"\r" not in raw.replace(b"\r\n", b"")
    canonical = raw.replace(b"\r\n", b"\n")
    assert hashlib.sha256(canonical).hexdigest() == PARENT_DIGEST
    assert manifest["sql_sha256"] == f"sha256:{PARENT_DIGEST}"
    assert manifest["sql_byte_count"] == 1_392_201
    assert manifest["statement_count"] == 413
    assert manifest["postgresql_major"] == 16
    assert len(manifest["phases"]) == 6
    assert PARENT_HEAD in plan
    assert PLANNING_BASELINE in plan
    assert f"sha256:{PARENT_DIGEST}" in plan
    assert "1,392,201 canonical LF bytes" in plan
    assert "statement count `413`" in plan
    assert "mechanical CRLF-to-LF normalization" in " ".join(plan.split())


def test_runtime_profile_is_no_pull_no_network_no_mount_and_exact_owned() -> None:
    combined = _flat(PLAN, DESIGN, THREAT)

    for required in (
        "exact locally present image reference `postgres:16-bookworm`",
        "`--pull=never`",
        "`--network=none`",
        "no published or exposed host port",
        "no bind mount, named volume, workspace mount or Docker socket mount",
        "PostgreSQL data on one container-local tmpfs",
        "cryptographically random per-run cleanup nonce",
        "no `POSTGRES_HOST_AUTH_METHOD=trust`",
        "argument vector with `shell=False`",
        "must not list global containers, images, volumes or networks",
    ):
        assert required in combined


def test_only_four_empty_synthetic_prerequisites_are_allowed() -> None:
    combined = _flat(PLAN, DESIGN)

    for relation in (
        "`public.appointments`",
        "`public.appointment_command_idempotency`",
        "`public.appointment_audit_log`",
        "`public.diary_committed_events`",
    ):
        assert relation in combined

    for required in (
        "There are no rows, patient identifiers, product values",
        "`xmin` is never created",
        "owners are captured before",
        "must remain unchanged afterwards",
        "minimum keys",
    ):
        assert required in combined


def test_sql_admission_is_atomic_and_behavior_execution_remains_closed() -> None:
    combined = _flat(PLAN, DESIGN, THREAT)

    for required in (
        "`ON_ERROR_STOP=1`",
        "`--single-transaction`",
        "`--file=-`",
        "plain implicit stdin is forbidden",
        "fixed synthetic invalid top-level statement",
        "rollback case must run first",
        "roles are cluster-scoped rather than database-scoped",
        "cluster-wide accepted-role absence",
        "does not execute any function or trigger behavior",
        "never invokes a function with `SELECT`/`CALL`",
        "PostgreSQL function creation does not prove every embedded SQL branch",
    ):
        assert required in combined


def test_catalogue_readback_closes_expected_inventory_and_privileges() -> None:
    combined = _flat(PLAN, DESIGN)

    for required in (
        "exact four domains, nineteen enums, nine composites",
        "thirty-two owned fabric types/domains",
        "exact eighteen fabric relations",
        "exact forty-four policies",
        "exact eight roles",
        "one support function, nine entry functions and fourteen trigger functions",
        "exact fourteen trigger declarations",
        "seven ordinary immediate triggers and seven constraint/deferred triggers",
        "no runtime schema `CREATE`",
        "no runtime trigger-function `EXECUTE`",
        "zero application-relation owner changes",
        "zero extension additions",
    ):
        assert required in combined


def test_cleanup_is_exact_id_and_fails_closed_on_ownership_uncertainty() -> None:
    combined = _flat(PLAN, DESIGN, THREAT)

    for required in (
        "Before removal the harness inspects the exact captured container ID",
        "both exact ownership labels and nonce",
        "If ownership cannot be reverified",
        "`cleanup_ownership_unverified`",
        "must not substitute a name, prefix, list or label query",
        "force-removes only that exact ID",
        "exact-ID post-inspect proves absence",
    ):
        assert required in combined


def test_claim_boundary_and_forbidden_surfaces_are_explicit() -> None:
    combined = _flat(PLAN, DESIGN, THREAT)

    for required in (
        "provider-free database-backed authored-synthetic behavior/transaction rehearsal",
        "no migration, operational database, durable data, credential",
        "application/API/Diary change",
        "patient/product/protected data",
        "provider product call",
        "deployment, production, release, Pages rebuild or protected-ref movement",
        "`docs/branding/`",
    ):
        assert required in combined


def test_standing_continuation_and_worker_allocation_are_recorded() -> None:
    combined = _flat(PLAN, DESIGN)

    assert (
        "Sol owns planning, implementation, the serial disposable runtime" in combined
    )
    assert "fresh Gemini 3.6 Flash/high Antigravity context" in combined
    assert "immediately enters the next dependency-satisfied planned gate" in combined


def test_rollback_precedes_success_and_psql_file_stdin_is_mandatory() -> None:
    plan = _text(PLAN)
    flat_plan = " ".join(plan.split())
    design = _text(DESIGN)

    assert flat_plan.index("rollback case must run first") < flat_plan.index(
        "Only after that proof may it install prerequisites in the success"
    )
    states = (
        "rollback_database_ready ->\nrollback_prerequisites_installed -> "
        "rollback_case_matched ->\nsuccess_database_ready"
    )
    assert states in design
    assert "`--file=-`" in plan
    assert "single-\ntransaction mode applies only with `-c`/`-f`" in plan
