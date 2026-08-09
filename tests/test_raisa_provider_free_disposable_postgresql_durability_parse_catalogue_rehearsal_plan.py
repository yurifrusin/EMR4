from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess


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
    ROOT / "docs/raisa-provider-free-disposable-postgresql-durability-parse-catalogue-"
    "alias-lock-visibility-rebind.md"
)
DML_NAME_AMBIGUITY_REBIND = (
    ROOT / "docs/raisa-provider-free-disposable-postgresql-durability-parse-catalogue-"
    "dml-name-ambiguity-rebind.md"
)
SUBTRANSACTION_XMIN_REBIND = (
    ROOT / "docs/raisa-provider-free-disposable-postgresql-durability-parse-catalogue-"
    "subtransaction-xmin-rebind.md"
)
SUPPORT_EXECUTE_GRANT_REBIND = (
    ROOT / "docs/raisa-provider-free-disposable-postgresql-durability-parse-catalogue-"
    "support-execute-grant-rebind.md"
)
BINDING_RLS_REBIND = (
    ROOT / "docs/raisa-provider-free-disposable-postgresql-durability-parse-catalogue-"
    "admission-receiver-binding-rls-rebind.md"
)
INPUT_NAMESPACE_REBIND = (
    ROOT / "docs/raisa-provider-free-disposable-postgresql-durability-"
    "parse-catalogue-input-namespace-rebind.md"
)
ADMISSION_ROW_SHAPE_REBIND = (
    ROOT
    / "docs/raisa-provider-free-disposable-postgresql-durability-parse-catalogue-admission-row-shape-rebind.md"
)

PARENT_HEAD = "c8ab7602e16e24453dbf909597b4f702a2388416"
PLANNING_BASELINE = "253230a25ab172b90bc5f44772670c7df89b3052"
PARENT_DIGEST = "ca22e47e847409f1ae8a81f62dd7f5f8402a43176d9015211f657204460fbdbb"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _flat(*paths: Path) -> str:
    return " ".join("\n".join(_text(path) for path in paths).split())


def test_parent_head_is_an_exact_resolvable_commit() -> None:
    completed = subprocess.run(
        ["git", "rev-parse", "--verify", f"{PARENT_HEAD}^{{commit}}"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0
    assert completed.stdout.strip() == PARENT_HEAD


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
        DML_NAME_AMBIGUITY_REBIND,
        SUBTRANSACTION_XMIN_REBIND,
        SUPPORT_EXECUTE_GRANT_REBIND,
        BINDING_RLS_REBIND,
        INPUT_NAMESPACE_REBIND,
        ADMISSION_ROW_SHAPE_REBIND,
    )
    manifest = json.loads(PARENT_MANIFEST.read_text(encoding="utf-8"))

    raw = PARENT_SQL.read_bytes()
    assert b"\r" not in raw.replace(b"\r\n", b"")
    canonical = raw.replace(b"\r\n", b"\n")
    assert hashlib.sha256(canonical).hexdigest() == PARENT_DIGEST
    assert manifest["sql_sha256"] == f"sha256:{PARENT_DIGEST}"
    assert manifest["sql_byte_count"] == 1_435_142
    assert manifest["statement_count"] == 421
    assert manifest["postgresql_major"] == 16
    assert len(manifest["phases"]) == 6
    assert PARENT_HEAD in plan
    assert PLANNING_BASELINE in plan
    assert f"sha256:{PARENT_DIGEST}" in plan
    assert "1,435,142" in plan
    assert "statement count `421`" in plan
    assert "mechanical CRLF-to-LF normalization" in " ".join(plan.split())
    assert "3bf66870cf80edc507b191d6022a5e3d22f3b7f3073c9ae4e696fed2fc54155c" in plan
    assert "4d140704d33624e90737022e5f9d095559152bd56554514ccebc73222d845750" in plan
    assert "3dc318e64b9c30817c0e2cdca650fc284ae3d2f35e93e697d0cac5368fecbd03" in plan
    assert "cb439eefe9eb243eb4eccda144ac51218d9e26ba71c0dd14402ee066b7c1fb14" in plan
    assert "f696bc57c3bbe6e25fc6f817aff337ef85b199bffff66fbf33ffa327c982e673" in plan
    assert "122d2db7ec577875c1477eee6a4fa0c51dc9117ce0c23bc3704aa43f4c791ca0" in plan
    assert "Distinct attempt `26f530dab9ed13ba20500267`" in plan
    assert "d0724ebd4a0caa07ee032ca031d54af1e99934d6966f45838d2fbe4450b588de" in plan
    assert "d9237e6db14e314de5e2981be1073575db2e512ed1eff44b1f9ebf8b044c17bc" in plan
    assert "41f065c805fdc3cc140ded68baf180bfd88ae3c34bbcd962cc140e9d359d814d" in plan
    assert "cf746ed8824ef8853677020e90083c2b4bfe1b4096a36ad7735cfeabf0eb4b91" in plan
    assert "e783fedb13785672cad84c76984f39ec6ec0b7bb3787ca9b33fb61db1f59fc68" in plan


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
