"""Run the bounded check-in runtime-role and tenant-isolation attestation."""

from __future__ import annotations

import copy
import hashlib
import json
import re
import secrets
import shutil
import sys
import time
import uuid
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from jsonschema import Draft202012Validator, FormatChecker
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import DBAPIError

from scripts import (
    raisa_provider_free_disposable_postgresql_status_confirm_behavior_transaction_rehearsal
    as foundation,
)
from scripts import (
    raisa_provider_free_disposable_postgresql_status_confirm_scaffold_parse_catalogue_rehearsal
    as catalogue,
)


BASE = ROOT / (
    "orchestration/continuity/raisa-provider-free-disposable-postgresql-"
    "default-off-check-in-runtime-role-tenant-isolation-attestation-rehearsal"
)
CONTRACT_PATH = BASE / "rehearsal-contract.json"
CONTRACT_SCHEMA_PATH = BASE / "rehearsal-contract.schema.json"
MANIFEST_SCHEMA_PATH = ROOT / (
    "orchestration/continuity/raisa-provider-free-default-off-check-in-"
    "environment-manifest-secret-posture-architecture/environment-manifest.schema.json"
)
ATTESTATION_SCHEMA_PATH = BASE / "tenant-role-attestation.schema.json"
EVIDENCE_SCHEMA_PATH = BASE / "rehearsal-evidence.schema.json"
ATTESTATION_PATH = BASE / "tenant-role-attestation.json"
EVIDENCE_PATH = BASE / "rehearsal-evidence.json"
FAILURE_PATH = BASE / "rehearsal-failure-evidence.json"

PASS_RESULT = (
    "raisa_provider_free_disposable_postgresql_default_off_check_in_"
    "runtime_role_tenant_isolation_attestation_rehearsal_pass"
)
EVIDENCE_LABEL = (
    "authored_synthetic_provider_free_disposable_postgresql_role_tenant_attestation"
)
ARCHITECTURE_SOURCE = "a1f309a6d52d01f9866432f7e9abb8095788d023"
SOURCE_HEAD = "455e41b8b9038813b290e67c43ce0b3190120988"
CLAIM_BOUNDARY = (
    "Exact authored-synthetic runtime-role attributes and tenant isolation in "
    "one captured disposable PostgreSQL 16 instance only; no product relation, "
    "ordinary enablement, live secret, rotation, rollback, unknown-commit, "
    "production or deployment claim."
)
EXPECTED_SCENARIOS = (
    ("RTA-S01", "manifest_role_binding", "closed_shape_bound"),
    ("RTA-S02", "role_catalogue", "restricted_non_owner_nobypassrls"),
    ("RTA-S03", "forced_rls_catalogue", "admin_owned_exact_policy"),
    ("RTA-S04", "tenant_a_same_scope", "select_insert_update"),
    ("RTA-S05", "tenant_b_same_scope", "select_only_tenant_b"),
    ("RTA-S06", "cross_tenant_read", "zero_rows"),
    ("RTA-S07", "cross_tenant_insert", "sqlstate_42501"),
    ("RTA-S08", "cross_tenant_update_delete", "zero_rows"),
    ("RTA-S09", "tenant_setting_absent", "zero_rows"),
    ("RTA-S10", "tenant_setting_reset", "absent_after_transaction"),
    ("RTA-S11", "admin_role_escalation", "sqlstate_42501"),
    ("RTA-S12", "role_cleanup", "absent_before_teardown"),
)
TENANT_A = uuid.UUID("11111111-1111-4111-8111-111111111111")
TENANT_B = uuid.UUID("22222222-2222-4222-8222-222222222222")
ROW_A = uuid.UUID("aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa1")
ROW_B = uuid.UUID("bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbb2")
ROW_A_INSERT = uuid.UUID("aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa3")
ROW_B_FORBIDDEN = uuid.UUID("bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbb4")
FORBIDDEN_KEYS = {
    "password",
    "secret_value",
    "database_url",
    "connection_url",
    "environment_value",
    "private_key",
    "raw_output",
    "raw_exception",
    "docker_environment",
    "container_name",
    "network_name",
    "local_path",
    "secret_material_sha256",
}


class RehearsalFailure(RuntimeError):
    def __init__(self, stage: str, code: str, detail: str = "") -> None:
        self.stage = stage
        self.code = code
        self.detail = detail
        super().__init__(f"{stage}:{code}")


def _sha256(value: bytes | str) -> str:
    payload = value.encode("utf-8") if isinstance(value, str) else value
    return hashlib.sha256(payload).hexdigest()


def _json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    ).encode("utf-8")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _canonical_source_bytes(path: Path) -> bytes:
    text_value = path.read_bytes().decode("utf-8", errors="strict")
    text_value = text_value.replace("\r\n", "\n")
    if "\r" in text_value:
        raise RehearsalFailure("preflight", "source_bare_cr", str(path.name))
    return text_value.encode("utf-8")


def _leaf_paths(value: Any, prefix: tuple[str | int, ...] = ()) -> list[tuple[str | int, ...]]:
    if isinstance(value, dict):
        paths: list[tuple[str | int, ...]] = []
        for key, item in value.items():
            paths.extend(_leaf_paths(item, prefix + (key,)))
        return paths
    if isinstance(value, list):
        paths = []
        for index, item in enumerate(value):
            paths.extend(_leaf_paths(item, prefix + (index,)))
        return paths
    return [prefix]


def _replace_leaf(candidate: Any, path: tuple[str | int, ...], replacement: Any) -> None:
    cursor = candidate
    for part in path[:-1]:
        cursor = cursor[part]
    cursor[path[-1]] = replacement


def _mutated_values(value: Any) -> tuple[Any, Any]:
    if isinstance(value, bool):
        return (not value, "invalid")
    if isinstance(value, int):
        return (-1 if value != -1 else -2, "invalid")
    if isinstance(value, str):
        return ("", value + "-invalid")
    return (None, "invalid")


def _value_at(value: Any, path: tuple[str | int, ...]) -> Any:
    cursor = value
    for part in path:
        cursor = cursor[part]
    return cursor


def _validate_contract(value: dict[str, Any], *, canonical: dict[str, Any]) -> None:
    errors = list(
        Draft202012Validator(_load_json(CONTRACT_SCHEMA_PATH)).iter_errors(value)
    )
    if errors:
        raise RehearsalFailure("preflight", "contract_schema_invalid")
    observed = tuple(
        (item["id"], item["kind"], item["expected"])
        for item in value["scenarios"]
    )
    if observed != EXPECTED_SCENARIOS:
        raise RehearsalFailure("preflight", "scenario_contract_mismatch")
    if value != canonical:
        raise RehearsalFailure("preflight", "contract_noncanonical")


def hostile_contract_mutations_rejected(contract: dict[str, Any]) -> tuple[int, int]:
    attempted = 0
    rejected = 0
    for path in _leaf_paths(contract):
        current = _value_at(contract, path)
        for replacement in _mutated_values(current):
            candidate = copy.deepcopy(contract)
            _replace_leaf(candidate, path, replacement)
            attempted += 1
            try:
                _validate_contract(candidate, canonical=contract)
            except RehearsalFailure:
                rejected += 1
    if attempted < 192 or attempted != rejected:
        raise RehearsalFailure("preflight", "hostile_contract_mutation_gate_failed")
    return attempted, rejected


def verify_contract() -> tuple[dict[str, Any], dict[str, str], tuple[int, int]]:
    contract = _load_json(CONTRACT_PATH)
    _validate_contract(contract, canonical=contract)
    mutations = hostile_contract_mutations_rejected(contract)
    observed: dict[str, str] = {}
    for binding in contract["source_bindings"]:
        path = ROOT / binding["path"]
        if not path.is_file():
            raise RehearsalFailure("preflight", "source_missing", binding["path"])
        digest = _sha256(_canonical_source_bytes(path))
        observed[binding["path"]] = digest
        if digest != binding["sha256"]:
            raise RehearsalFailure("preflight", "source_hash_mismatch", binding["path"])
    return contract, observed, mutations


def build_manifest(physical_role: str) -> dict[str, Any]:
    slots = (
        "database_connection_credential",
        "application_token_signing_key",
        "admission_snapshot_verification_key",
    )
    secret_references = []
    rotation_evidence = []
    for index, slot in enumerate(slots, start=1):
        key_id = f"authored-synthetic-{slot.replace('_', '-')}-key"
        evidence_reference = f"evidence-ref:authored-synthetic/rotation/{slot}"
        secret_references.append(
            {
                "slot_id": slot,
                "provider_namespace": "authored-synthetic-local",
                "secret_reference": f"secret-ref:authored-synthetic/{slot}",
                "key_id": key_id,
                "version": "v1",
                "rotation_policy_reference": "policy-ref:authored-synthetic/rotation-v1",
                "rotation_evidence_reference": evidence_reference,
            }
        )
        rotation_evidence.append(
            {
                "slot_id": slot,
                "evidence_reference": evidence_reference,
                "artifact_sha256": _sha256(f"shape-only-rotation-evidence:{slot}"),
                "authority_git_object": ARCHITECTURE_SOURCE,
                "environment_identifier": "env:authored-synthetic-check-in-role-attestation",
                "admission_snapshot_generation": 1,
                "key_id": key_id,
                "version": "v1",
                "rotation_sequence": index,
                "observed_at": "2026-08-19T00:00:00Z",
                "fresh_until": "2026-08-20T00:00:00Z",
                "independent_verifier_reference": f"evidence-ref:authored-synthetic/verifier/{slot}",
            }
        )
    return {
        "schema_version": "emr4.check-in-ordinary-environment-manifest.v1",
        "manifest_id": "check-in-env-manifest:authored-synthetic-role-attestation",
        "environment": {
            "class": "test",
            "identifier": "env:authored-synthetic-check-in-role-attestation",
        },
        "admission_snapshot_generation": 1,
        "authority_git_object": ARCHITECTURE_SOURCE,
        "practice_scope_reference": "practice-ref:authored-synthetic/check-in-tenant-a",
        "runtime_role": {
            "logical_role_id": "appointment_check_in_ordinary_runtime_v1",
            "database_role_identifier": physical_role,
            "credential_secret_slot_id": "database_connection_credential",
            "non_owner_required": True,
            "nobypassrls_required": True,
            "product_relation_ownership_allowed": False,
            "tenant_attestation_reference": "evidence-ref:authored-synthetic/check-in-role-tenant-attestation",
        },
        "secret_references": secret_references,
        "rotation_evidence": rotation_evidence,
        "break_glass": {
            "mode": "deny_only",
            "state": "inactive",
            "evidence_reference": "evidence-ref:authored-synthetic/break-glass-inactive",
            "bypass_allowed": False,
            "secret_injection_allowed": False,
            "automatic_clear_allowed": False,
        },
        "issued_at": "2026-08-19T00:00:00Z",
        "expires_at": "2026-08-20T00:00:00Z",
    }


def _assert_redacted(value: Any, *, forbidden_values: tuple[str, ...] = ()) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            if key.lower() in FORBIDDEN_KEYS:
                raise RehearsalFailure("evidence", "forbidden_evidence_field", key)
            _assert_redacted(item, forbidden_values=forbidden_values)
        return
    if isinstance(value, list):
        for item in value:
            _assert_redacted(item, forbidden_values=forbidden_values)
        return
    if isinstance(value, str):
        lowered = value.lower()
        if "postgresql://" in lowered or "postgresql+" in lowered:
            raise RehearsalFailure("evidence", "connection_url_leaked")
        for forbidden in forbidden_values:
            if forbidden and forbidden in value:
                raise RehearsalFailure("evidence", "credential_value_leaked")


def _validate_manifest(
    value: dict[str, Any], *, physical_role: str, canonical: dict[str, Any]
) -> None:
    validator = Draft202012Validator(
        _load_json(MANIFEST_SCHEMA_PATH), format_checker=FormatChecker()
    )
    if list(validator.iter_errors(value)):
        raise RehearsalFailure("manifest", "manifest_schema_invalid")
    if value["runtime_role"]["database_role_identifier"] != physical_role:
        raise RehearsalFailure("manifest", "physical_role_binding_mismatch")
    if value["authority_git_object"] != ARCHITECTURE_SOURCE:
        raise RehearsalFailure("manifest", "authority_git_object_mismatch")
    if value["expires_at"] <= value["issued_at"]:
        raise RehearsalFailure("manifest", "manifest_freshness_invalid")
    _assert_redacted(value)
    if value != canonical:
        raise RehearsalFailure("manifest", "manifest_noncanonical")


def hostile_manifest_mutations_rejected(manifest: dict[str, Any], physical_role: str) -> tuple[int, int]:
    attempted = 0
    rejected = 0
    for path in _leaf_paths(manifest):
        current = _value_at(manifest, path)
        for replacement in _mutated_values(current):
            candidate = copy.deepcopy(manifest)
            _replace_leaf(candidate, path, replacement)
            attempted += 1
            try:
                _validate_manifest(
                    candidate, physical_role=physical_role, canonical=manifest
                )
            except RehearsalFailure:
                rejected += 1
    secret_candidate = copy.deepcopy(manifest)
    secret_candidate["secret_references"][0]["password"] = "forbidden"
    attempted += 1
    try:
        _validate_manifest(
            secret_candidate, physical_role=physical_role, canonical=manifest
        )
    except RehearsalFailure:
        rejected += 1
    if attempted < 64 or attempted != rejected:
        raise RehearsalFailure("manifest", "hostile_manifest_mutation_gate_failed")
    return attempted, rejected


def _runtime_profile(contract: dict[str, Any], admin_password: str) -> dict[str, Any]:
    profile = copy.deepcopy(contract["containment_profile"])
    profile.pop("admin_password_source")
    profile.pop("runtime_password_source")
    profile["postgres_password"] = admin_password
    return profile


def _application_engine(
    host_port: int, profile: dict[str, Any], physical_role: str, runtime_password: str
) -> Engine:
    url = (
        f"postgresql+{profile['sqlalchemy_driver']}://{physical_role}:"
        f"{runtime_password}@{profile['relay_host_ip']}:{host_port}/"
        f"{profile['postgres_database']}"
    )
    engine = create_engine(
        url,
        pool_size=1,
        max_overflow=0,
        pool_pre_ping=True,
        connect_args={"connect_timeout": 5, "application_name": "emr4_checkin_role_attest"},
    )
    with engine.connect() as connection:
        row = connection.execute(
            text(
                "SELECT current_user, rolcanlogin, rolsuper, rolcreatedb, "
                "rolcreaterole, rolinherit, rolreplication, rolbypassrls "
                "FROM pg_roles WHERE rolname=current_user"
            )
        ).one()
    if tuple(row) != (physical_role, True, False, False, False, False, False, False):
        engine.dispose()
        raise RehearsalFailure("role", "application_role_identity_mismatch")
    return engine


def _install_probe(
    admin: Engine,
    *,
    profile: dict[str, Any],
    physical_role: str,
    runtime_password: str,
) -> None:
    if not re.fullmatch(r"emr4_checkin_ord_[0-9a-f]{16}", physical_role):
        raise RehearsalFailure("role", "physical_role_identifier_invalid")
    if not re.fullmatch(r"[0-9a-f]{64}", runtime_password):
        raise RehearsalFailure("role", "runtime_credential_shape_invalid")
    sql = f"""
REVOKE ALL ON SCHEMA public FROM PUBLIC;
CREATE SCHEMA check_in_role_probe AUTHORIZATION {profile['postgres_user']};
CREATE TABLE check_in_role_probe.tenant_probe (
  practice_id uuid NOT NULL,
  row_id uuid PRIMARY KEY,
  marker text NOT NULL
);
ALTER TABLE check_in_role_probe.tenant_probe ENABLE ROW LEVEL SECURITY;
ALTER TABLE check_in_role_probe.tenant_probe FORCE ROW LEVEL SECURITY;
CREATE POLICY check_in_role_probe_tenant ON check_in_role_probe.tenant_probe
  USING (practice_id = nullif(current_setting('app.current_practice_id', true), '')::uuid)
  WITH CHECK (practice_id = nullif(current_setting('app.current_practice_id', true), '')::uuid);
CREATE ROLE {physical_role} LOGIN PASSWORD '{runtime_password}'
  NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOREPLICATION NOBYPASSRLS;
GRANT CONNECT ON DATABASE {profile['postgres_database']} TO {physical_role};
GRANT USAGE ON SCHEMA check_in_role_probe TO {physical_role};
GRANT SELECT, INSERT, UPDATE, DELETE ON check_in_role_probe.tenant_probe TO {physical_role};
"""
    with admin.begin() as connection:
        for statement in [part.strip() for part in sql.split(";") if part.strip()]:
            connection.execute(text(statement))
        connection.execute(
            text(
                "INSERT INTO check_in_role_probe.tenant_probe(practice_id,row_id,marker) "
                "VALUES (:tenant_a,:row_a,'tenant-a'),(:tenant_b,:row_b,'tenant-b')"
            ),
            {
                "tenant_a": TENANT_A,
                "row_a": ROW_A,
                "tenant_b": TENANT_B,
                "row_b": ROW_B,
            },
        )


def _role_catalogue(
    admin: Engine, *, physical_role: str, profile: dict[str, Any]
) -> tuple[dict[str, Any], dict[str, Any]]:
    with admin.connect() as connection:
        role = connection.execute(
            text(
                "SELECT rolcanlogin, rolsuper, rolcreatedb, rolcreaterole, "
                "rolinherit, rolreplication, rolbypassrls "
                "FROM pg_roles WHERE rolname=:role"
            ),
            {"role": physical_role},
        ).one()
        memberships = connection.execute(
            text(
                "SELECT count(*) FROM pg_auth_members m JOIN pg_roles r ON r.oid=m.member "
                "WHERE r.rolname=:role"
            ),
            {"role": physical_role},
        ).scalar_one()
        owned_databases = connection.execute(
            text(
                "SELECT count(*) FROM pg_database d JOIN pg_roles r ON r.oid=d.datdba "
                "WHERE r.rolname=:role"
            ),
            {"role": physical_role},
        ).scalar_one()
        owned_schemas = connection.execute(
            text(
                "SELECT count(*) FROM pg_namespace n JOIN pg_roles r ON r.oid=n.nspowner "
                "WHERE r.rolname=:role"
            ),
            {"role": physical_role},
        ).scalar_one()
        owned_relations = connection.execute(
            text(
                "SELECT count(*) FROM pg_class c JOIN pg_roles r ON r.oid=c.relowner "
                "WHERE r.rolname=:role"
            ),
            {"role": physical_role},
        ).scalar_one()
        owned_functions = connection.execute(
            text(
                "SELECT count(*) FROM pg_proc p JOIN pg_roles r ON r.oid=p.proowner "
                "WHERE r.rolname=:role"
            ),
            {"role": physical_role},
        ).scalar_one()
        policy_bindings = connection.execute(
            text(
                "SELECT count(*) FROM pg_policy p, pg_roles r "
                "WHERE r.rolname=:role AND r.oid=ANY(p.polroles)"
            ),
            {"role": physical_role},
        ).scalar_one()
        product_privileges = connection.execute(
            text(
                "SELECT count(*) FROM information_schema.table_privileges "
                "WHERE grantee=:role AND table_schema <> 'check_in_role_probe'"
            ),
            {"role": physical_role},
        ).scalar_one()
        grants = sorted(
            connection.execute(
                text(
                    "SELECT privilege_type FROM information_schema.table_privileges "
                    "WHERE grantee=:role AND table_schema='check_in_role_probe' "
                    "AND table_name='tenant_probe'"
                ),
                {"role": physical_role},
            ).scalars()
        )
        public_usage = connection.execute(
            text("SELECT has_schema_privilege(:role, 'public', 'USAGE')"),
            {"role": physical_role},
        ).scalar_one()
        probe = connection.execute(
            text(
                "SELECT r.rolname, c.relrowsecurity, c.relforcerowsecurity "
                "FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace "
                "JOIN pg_roles r ON r.oid=c.relowner "
                "WHERE n.nspname='check_in_role_probe' AND c.relname='tenant_probe'"
            )
        ).one()
        policy = connection.execute(
            text(
                "SELECT polname, polcmd, pg_get_expr(polqual,polrelid), "
                "pg_get_expr(polwithcheck,polrelid) FROM pg_policy "
                "WHERE polname='check_in_role_probe_tenant'"
            )
        ).one()
    expected_flags = (True, False, False, False, False, False, False)
    counts = (
        memberships,
        owned_databases,
        owned_schemas,
        owned_relations,
        owned_functions,
        policy_bindings,
        product_privileges,
    )
    if tuple(role) != expected_flags or counts != (0, 0, 0, 0, 0, 0, 0):
        raise RehearsalFailure("catalogue", "restricted_role_contract_mismatch")
    if grants != ["DELETE", "INSERT", "SELECT", "UPDATE"] or public_usage is not False:
        raise RehearsalFailure("catalogue", "role_grant_contract_mismatch")
    if tuple(probe) != (profile["postgres_user"], True, True):
        raise RehearsalFailure("catalogue", "probe_rls_owner_mismatch")
    if policy[0] != "check_in_role_probe_tenant" or policy[1] != "*":
        raise RehearsalFailure("catalogue", "probe_policy_catalogue_mismatch")
    expression = str(policy[2])
    with_check = str(policy[3])
    if expression != with_check or "app.current_practice_id" not in expression:
        raise RehearsalFailure("catalogue", "probe_policy_expression_mismatch")
    return (
        {
            "login": bool(role[0]),
            "superuser": bool(role[1]),
            "create_database": bool(role[2]),
            "create_role": bool(role[3]),
            "inherit": bool(role[4]),
            "replication": bool(role[5]),
            "bypass_rls": bool(role[6]),
            "memberships": int(memberships),
            "owned_databases": int(owned_databases),
            "owned_schemas": int(owned_schemas),
            "owned_relations": int(owned_relations),
            "owned_functions": int(owned_functions),
            "policy_role_bindings": int(policy_bindings),
            "product_relation_privileges": int(product_privileges),
            "probe_grants": grants,
        },
        {
            "admin_owned": True,
            "rls_enabled": True,
            "rls_forced": True,
            "policy_count": 1,
            "policy_expression_sha256": _sha256(expression),
            "policy_with_check_matches": True,
        },
    )


def _sqlstate(error: BaseException) -> str:
    original = getattr(error, "orig", None)
    return str(
        getattr(original, "pgcode", None)
        or getattr(original, "sqlstate", None)
        or "none"
    )


def _set_tenant(connection: Any, tenant: uuid.UUID) -> None:
    observed = connection.execute(
        text("SELECT set_config('app.current_practice_id', :tenant, true)"),
        {"tenant": str(tenant)},
    ).scalar_one()
    if observed != str(tenant):
        raise RehearsalFailure("scenario", "transaction_local_tenant_set_failed")


def _scenario_result(identifier: str, observed: str | int | bool) -> dict[str, Any]:
    return {"id": identifier, "status": "passed", "observed": observed}


def _run_scenarios(
    application: Engine,
    *,
    manifest: dict[str, Any],
    role_catalogue: dict[str, Any],
    probe_catalogue: dict[str, Any],
    profile: dict[str, Any],
) -> list[dict[str, Any]]:
    results = [
        _scenario_result("RTA-S01", _sha256(_json_bytes(manifest))),
        _scenario_result("RTA-S02", role_catalogue["bypass_rls"] is False),
        _scenario_result("RTA-S03", probe_catalogue["rls_forced"]),
    ]
    with application.begin() as connection:
        _set_tenant(connection, TENANT_A)
        visible_a = connection.execute(
            text("SELECT practice_id FROM check_in_role_probe.tenant_probe ORDER BY row_id")
        ).scalars().all()
        if visible_a != [TENANT_A]:
            raise RehearsalFailure("scenario", "same_tenant_a_initial_visibility")
        connection.execute(
            text(
                "INSERT INTO check_in_role_probe.tenant_probe(practice_id,row_id,marker) "
                "VALUES (:tenant,:row_id,'tenant-a-inserted')"
            ),
            {"tenant": TENANT_A, "row_id": ROW_A_INSERT},
        )
        updated_a = connection.execute(
            text(
                "UPDATE check_in_role_probe.tenant_probe SET marker='tenant-a-updated' "
                "WHERE row_id=:row_id"
            ),
            {"row_id": ROW_A_INSERT},
        ).rowcount
        if updated_a != 1:
            raise RehearsalFailure("scenario", "same_tenant_a_update_failed")
        cross_read = connection.execute(
            text(
                "SELECT count(*) FROM check_in_role_probe.tenant_probe "
                "WHERE practice_id=:tenant_b"
            ),
            {"tenant_b": TENANT_B},
        ).scalar_one()
        insert_state = "none"
        try:
            with connection.begin_nested():
                connection.execute(
                    text(
                        "INSERT INTO check_in_role_probe.tenant_probe(practice_id,row_id,marker) "
                        "VALUES (:tenant,:row_id,'forbidden-cross-tenant')"
                    ),
                    {"tenant": TENANT_B, "row_id": ROW_B_FORBIDDEN},
                )
        except DBAPIError as caught:
            insert_state = _sqlstate(caught)
        if insert_state != "42501":
            raise RehearsalFailure("scenario", "cross_tenant_insert_not_denied", insert_state)
        cross_update = connection.execute(
            text(
                "UPDATE check_in_role_probe.tenant_probe SET marker='forbidden-update' "
                "WHERE practice_id=:tenant_b"
            ),
            {"tenant_b": TENANT_B},
        ).rowcount
        cross_delete = connection.execute(
            text(
                "DELETE FROM check_in_role_probe.tenant_probe WHERE practice_id=:tenant_b"
            ),
            {"tenant_b": TENANT_B},
        ).rowcount
    results.extend(
        [
            _scenario_result("RTA-S04", updated_a),
            _scenario_result("RTA-S06", int(cross_read)),
            _scenario_result("RTA-S07", insert_state),
            _scenario_result("RTA-S08", int(cross_update + cross_delete)),
        ]
    )
    if cross_read != 0 or cross_update != 0 or cross_delete != 0:
        raise RehearsalFailure("scenario", "cross_tenant_visibility_or_mutation")
    with application.begin() as connection:
        _set_tenant(connection, TENANT_B)
        visible_b = connection.execute(
            text("SELECT practice_id FROM check_in_role_probe.tenant_probe ORDER BY row_id")
        ).scalars().all()
    if visible_b != [TENANT_B]:
        raise RehearsalFailure("scenario", "same_tenant_b_visibility")
    results.append(_scenario_result("RTA-S05", len(visible_b)))
    with application.connect() as connection:
        setting = connection.execute(
            text("SELECT current_setting('app.current_practice_id', true)")
        ).scalar_one_or_none()
        absent_visibility = connection.execute(
            text("SELECT count(*) FROM check_in_role_probe.tenant_probe")
        ).scalar_one()
    if setting not in (None, "") or absent_visibility != 0:
        raise RehearsalFailure("scenario", "tenant_setting_leaked")
    results.extend(
        [
            _scenario_result("RTA-S09", int(absent_visibility)),
            _scenario_result("RTA-S10", True),
        ]
    )
    escalation_state = "none"
    with application.begin() as connection:
        try:
            with connection.begin_nested():
                connection.execute(text(f"SET ROLE {profile['postgres_user']}"))
        except DBAPIError as caught:
            escalation_state = _sqlstate(caught)
    if escalation_state != "42501":
        raise RehearsalFailure("scenario", "admin_role_escalation_not_denied", escalation_state)
    results.append(_scenario_result("RTA-S11", escalation_state))
    return sorted(results, key=lambda item: item["id"])


def _drop_role(admin: Engine, physical_role: str) -> bool:
    if not re.fullmatch(r"emr4_checkin_ord_[0-9a-f]{16}", physical_role):
        return False
    with admin.begin() as connection:
        connection.execute(text(f"DROP OWNED BY {physical_role}"))
        connection.execute(text(f"DROP ROLE {physical_role}"))
        remaining = connection.execute(
            text("SELECT count(*) FROM pg_roles WHERE rolname=:role"),
            {"role": physical_role},
        ).scalar_one()
    return remaining == 0


def _failure_evidence(
    error: RehearsalFailure, lifecycle: list[str], cleanup: dict[str, Any]
) -> dict[str, Any]:
    return {
        "schema_version": "emr4.check-in-runtime-role-tenant-isolation-attestation-failure.v1",
        "result": "rehearsal_failed",
        "evidence_label": EVIDENCE_LABEL,
        "source_head": SOURCE_HEAD,
        "failure": {
            "stage": error.stage,
            "code": error.code,
            "detail_sha256": _sha256(error.detail),
        },
        "lifecycle": lifecycle,
        "cleanup": cleanup,
        "claim_boundary": CLAIM_BOUNDARY,
    }


def run_rehearsal() -> tuple[dict[str, Any], dict[str, Any] | None]:
    lifecycle: list[str] = []
    cleanup: dict[str, Any] = {"status": "not_needed"}
    contract: dict[str, Any] | None = None
    source_hashes: dict[str, str] = {}
    contract_mutations = (0, 0)
    manifest_mutations = (0, 0)
    docker = ""
    image_id: str | None = None
    network_id: str | None = None
    container_id: str | None = None
    network_name = ""
    container_name = ""
    nonce = secrets.token_hex(16)
    physical_role = "emr4_checkin_ord_" + secrets.token_hex(8)
    admin_password = secrets.token_hex(32)
    runtime_password = secrets.token_hex(32)
    role_created = False
    role_absent = False
    admin: Engine | None = None
    application: Engine | None = None
    relay: foundation.DockerExecRelay | None = None
    attestation: dict[str, Any] | None = None
    evidence: dict[str, Any] | None = None
    error: RehearsalFailure | None = None
    started = time.monotonic()
    profile: dict[str, Any] | None = None
    try:
        contract, source_hashes, contract_mutations = verify_contract()
        lifecycle.append("contract_sources_and_hostile_mutations_verified")
        manifest = build_manifest(physical_role)
        _validate_manifest(manifest, physical_role=physical_role, canonical=manifest)
        manifest_mutations = hostile_manifest_mutations_rejected(manifest, physical_role)
        manifest_sha256 = _sha256(_json_bytes(manifest))
        lifecycle.append("closed_ephemeral_manifest_and_mutations_verified")
        docker = shutil.which(contract["containment_profile"]["executable"]) or ""
        if not docker:
            raise RehearsalFailure("environment", "docker_client_missing")
        profile = _runtime_profile(contract, admin_password)
        image_id = foundation._image_id(docker, profile)  # noqa: SLF001
        lifecycle.append("cached_postgresql_16_image_verified")
        suffix = secrets.token_hex(8)
        network_name = profile["network_name_prefix"] + suffix
        container_name = profile["container_name_prefix"] + suffix
        network_result = catalogue._run(  # noqa: SLF001
            foundation.build_network_argv(docker, network_name, nonce, profile),
            None,
            profile["command_timeout_seconds"],
            4096,
        )
        network_id = network_result.stdout.decode("utf-8").strip()
        if network_result.returncode != 0 or not re.fullmatch(r"[0-9a-f]{64}", network_id):
            raise RehearsalFailure("environment", "network_create_failed")
        inspected_result, inspected = foundation._inspect_one(  # noqa: SLF001
            docker, "network", network_id, profile["command_timeout_seconds"]
        )
        if (
            inspected_result.returncode != 0
            or inspected is None
            or not foundation._network_owned(  # noqa: SLF001
                inspected,
                network_id=network_id,
                name=network_name,
                nonce=nonce,
                profile=profile,
                require_empty=True,
            )
        ):
            raise RehearsalFailure("environment", "network_profile_mismatch")
        lifecycle.append("owned_internal_network_verified")
        container_result = catalogue._run(  # noqa: SLF001
            foundation.build_container_argv(
                docker, container_name, nonce, network_id, profile
            ),
            None,
            profile["command_timeout_seconds"],
            4096,
        )
        container_id = container_result.stdout.decode("utf-8").strip()
        if container_result.returncode != 0 or not re.fullmatch(r"[0-9a-f]{64}", container_id):
            raise RehearsalFailure("environment", "container_create_failed")
        inspected_result, inspected = foundation._inspect_one(  # noqa: SLF001
            docker, "container", container_id, profile["command_timeout_seconds"]
        )
        if (
            inspected_result.returncode != 0
            or inspected is None
            or not foundation._container_profile(  # noqa: SLF001
                inspected,
                container_id=container_id,
                name=container_name,
                nonce=nonce,
                image_id=image_id,
                network_id=network_id,
                profile=profile,
            )
        ):
            raise RehearsalFailure("environment", "container_profile_mismatch")
        lifecycle.append("owned_tmpfs_container_verified")
        foundation._wait_ready(docker, container_id, profile)  # noqa: SLF001
        lifecycle.append("postgresql_16_readiness_verified")
        relay = foundation.DockerExecRelay(docker, container_id, profile)
        host_port = relay.start()
        lifecycle.append("fixed_loopback_relay_started")
        admin = foundation._engine(host_port, profile)  # noqa: SLF001
        _install_probe(
            admin,
            profile=profile,
            physical_role=physical_role,
            runtime_password=runtime_password,
        )
        role_created = True
        lifecycle.append("admin_owned_forced_rls_probe_and_role_installed")
        application = _application_engine(
            host_port, profile, physical_role, runtime_password
        )
        role_catalogue, probe_catalogue = _role_catalogue(
            admin, physical_role=physical_role, profile=profile
        )
        lifecycle.append("restricted_role_and_forced_rls_catalogue_verified")
        scenario_results = _run_scenarios(
            application,
            manifest=manifest,
            role_catalogue=role_catalogue,
            probe_catalogue=probe_catalogue,
            profile=profile,
        )
        lifecycle.append("same_tenant_success_and_cross_tenant_denials_verified")
        application.dispose()
        application = None
        role_absent = _drop_role(admin, physical_role)
        if not role_absent:
            raise RehearsalFailure("cleanup", "role_absence_unverified")
        role_created = False
        scenario_results.append(_scenario_result("RTA-S12", True))
        scenario_results = sorted(scenario_results, key=lambda item: item["id"])
        if [item["id"] for item in scenario_results] != [
            item[0] for item in EXPECTED_SCENARIOS
        ]:
            raise RehearsalFailure("scenario", "scenario_release_order_mismatch")
        lifecycle.append("physical_role_absent_before_teardown")
        if time.monotonic() - started > profile["total_timeout_seconds"]:
            raise RehearsalFailure("environment", "total_timeout_exceeded")
        attestation = {
            "schema_version": "emr4.check-in-tenant-role-attestation.v1",
            "evidence_reference": "evidence-ref:authored-synthetic/check-in-role-tenant-attestation",
            "evidence_label": EVIDENCE_LABEL,
            "authority_git_object": ARCHITECTURE_SOURCE,
            "environment_identifier": manifest["environment"]["identifier"],
            "practice_scope_reference": manifest["practice_scope_reference"],
            "admission_snapshot_generation": manifest["admission_snapshot_generation"],
            "manifest_sha256": manifest_sha256,
            "logical_role_id": manifest["runtime_role"]["logical_role_id"],
            "physical_role_identifier": physical_role,
            "role_catalogue": role_catalogue,
            "probe_catalogue": probe_catalogue,
            "scenarios": scenario_results,
            "role_absent_before_teardown": True,
            "ordinary_admission_release_count": 0,
            "claim_boundary": CLAIM_BOUNDARY,
        }
        _assert_redacted(
            attestation, forbidden_values=(admin_password, runtime_password)
        )
        Draft202012Validator(_load_json(ATTESTATION_SCHEMA_PATH)).validate(attestation)
    except RehearsalFailure as caught:
        lifecycle.append(f"failed_{caught.stage}_{caught.code}")
        error = caught
    except Exception as caught:  # sanitize unexpected runtime failures
        lifecycle.append(f"failed_harness_{type(caught).__name__}_{_sqlstate(caught)}")
        error = RehearsalFailure(
            "harness", "unexpected_exception", f"{type(caught).__name__}:{_sqlstate(caught)}"
        )
    finally:
        if application is not None:
            application.dispose()
        if admin is not None and role_created:
            try:
                role_absent = _drop_role(admin, physical_role)
                if role_absent:
                    lifecycle.append("failure_path_physical_role_absent")
            except Exception:
                lifecycle.append("failure_path_role_cleanup_unverified")
        if admin is not None:
            admin.dispose()
        if relay is not None:
            relay.stop()
            lifecycle.append("fixed_loopback_relay_stopped")
        if contract is not None and docker and profile is not None:
            cleanup = foundation._cleanup(  # noqa: SLF001
                docker,
                container_id=container_id,
                container_name=container_name,
                network_id=network_id,
                network_name=network_name,
                nonce=nonce,
                image_id=image_id,
                profile=profile,
            )
        cleanup["role_absent_before_teardown"] = role_absent
        if cleanup.get("status") == "cleanup_verified":
            lifecycle.append("captured_container_and_network_absent")
        if error is None and (
            cleanup.get("status") != "cleanup_verified" or not role_absent
        ):
            error = RehearsalFailure("cleanup", "exact_cleanup_unverified")
    if error is not None:
        failure = _failure_evidence(error, lifecycle, cleanup)
        _assert_redacted(
            failure, forbidden_values=(admin_password, runtime_password)
        )
        return failure, None
    assert contract is not None and attestation is not None and image_id is not None
    evidence = {
        "schema_version": "emr4.check-in-runtime-role-tenant-isolation-attestation-evidence.v1",
        "result": PASS_RESULT,
        "evidence_label": EVIDENCE_LABEL,
        "source_head": contract["source_head"],
        "accepted_environment_architecture_source": ARCHITECTURE_SOURCE,
        "contract_sha256": _sha256(_canonical_source_bytes(CONTRACT_PATH)),
        "source_hashes": source_hashes,
        "manifest_sha256": attestation["manifest_sha256"],
        "attestation_artifact": str(ATTESTATION_PATH.relative_to(ROOT)).replace("\\", "/"),
        "attestation_sha256": _sha256(_json_bytes(attestation)),
        "hostile_mutations": {
            "contract_attempted": contract_mutations[0],
            "contract_rejected": contract_mutations[1],
            "manifest_attempted": manifest_mutations[0],
            "manifest_rejected": manifest_mutations[1],
            "escapes": 0,
        },
        "environment": {
            "postgresql_major": 16,
            "image_reference": contract["containment_profile"]["image_reference"],
            "image_id_sha256": _sha256(image_id),
            "network_internal": True,
            "published_ports": False,
            "storage": "container_local_tmpfs",
            "host_transport": "fixed_in_process_ipv4_loopback_relay",
            "provider_calls": 0,
            "product_rows": 0,
            "live_secrets": 0,
        },
        "lifecycle": lifecycle,
        "cleanup": cleanup,
        "closed_boundaries": contract["closed_boundaries"],
        "claim_boundary": CLAIM_BOUNDARY,
    }
    _assert_redacted(evidence, forbidden_values=(admin_password, runtime_password))
    Draft202012Validator(_load_json(EVIDENCE_SCHEMA_PATH)).validate(evidence)
    return evidence, attestation


def write_evidence(
    evidence: dict[str, Any], attestation: dict[str, Any] | None
) -> Path:
    BASE.mkdir(parents=True, exist_ok=True)
    if evidence["result"] == PASS_RESULT:
        assert attestation is not None
        ATTESTATION_PATH.write_bytes(_json_bytes(attestation))
        EVIDENCE_PATH.write_bytes(_json_bytes(evidence))
        return EVIDENCE_PATH
    FAILURE_PATH.write_bytes(_json_bytes(evidence))
    return FAILURE_PATH


def main() -> int:
    if len(sys.argv) != 1:
        print('{"result":"rehearsal_failed","code":"caller_arguments_forbidden"}')
        return 2
    evidence, attestation = run_rehearsal()
    target = write_evidence(evidence, attestation)
    print(
        json.dumps(
            {
                "result": evidence["result"],
                "cleanup": evidence["cleanup"].get("status"),
                "evidence": str(target.relative_to(ROOT)).replace("\\", "/"),
            },
            sort_keys=True,
        )
    )
    return 0 if evidence["result"] == PASS_RESULT else 1


if __name__ == "__main__":
    raise SystemExit(main())
