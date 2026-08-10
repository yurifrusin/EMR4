"""Deterministic and hostile checks for the disposable PostgreSQL rehearsal."""

from __future__ import annotations

import ast
import copy
import io
import inspect
import json
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft202012Validator

from scripts import (
    raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal as rehearsal,
)
from scripts import (
    raisa_provider_free_unmounted_durability_inert_ddl_rehearsal as ddl_rehearsal,
)

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / (
    "orchestration/continuity/raisa-provider-free-disposable-postgresql-"
    "durability-parse-catalogue-rehearsal"
)
CONTRACT = json.loads((DIR / "rehearsal-contract.json").read_text(encoding="utf-8"))
CHARACTERIZATION_CONTRACT = copy.deepcopy(CONTRACT)
CHARACTERIZATION_CONTRACT["catalogue_expectation"] = {
    "mode": "characterization_only",
    "expected_query_digests": {},
}
CONTRACT_SCHEMA = json.loads(
    (DIR / "rehearsal-contract.schema.json").read_text(encoding="utf-8")
)
PREREQUISITE = json.loads(
    (DIR / "synthetic-prerequisite-contract.json").read_text(encoding="utf-8")
)
PREREQUISITE_SCHEMA = json.loads(
    (DIR / "synthetic-prerequisite-contract.schema.json").read_text(encoding="utf-8")
)
EVIDENCE_SCHEMA = json.loads(
    (DIR / "rehearsal-evidence.schema.json").read_text(encoding="utf-8")
)
CHARACTERIZATION_EVIDENCE = json.loads(
    (
        DIR
        / "provider-free-disposable-postgresql-evidence-catalogue-characterization.json"
    ).read_text(encoding="utf-8")
)
REGISTRATION_RLS_CHARACTERIZATION_EVIDENCE = json.loads(
    (
        DIR
        / "provider-free-disposable-postgresql-evidence-registration-rls-characterization.json"
    ).read_text(encoding="utf-8")
)
SYSTEM_XMIN_CHARACTERIZATION_EVIDENCE_PATH = (
    DIR
    / "provider-free-disposable-postgresql-evidence-system-xmin-characterization.json"
)
SYSTEM_XMIN_CHARACTERIZATION_EVIDENCE = json.loads(
    SYSTEM_XMIN_CHARACTERIZATION_EVIDENCE_PATH.read_text(encoding="utf-8")
)
SYSTEM_XMIN_ALIAS_CHARACTERIZATION_EVIDENCE_PATH = (
    DIR
    / "provider-free-disposable-postgresql-evidence-system-xmin-explicit-alias-characterization.json"
)
SYSTEM_XMIN_ALIAS_CHARACTERIZATION_EVIDENCE = json.loads(
    SYSTEM_XMIN_ALIAS_CHARACTERIZATION_EVIDENCE_PATH.read_text(encoding="utf-8")
)
SYSTEM_XMIN_RECORD_ACCESS_CHARACTERIZATION_EVIDENCE_PATH = (
    DIR
    / "provider-free-disposable-postgresql-evidence-system-xmin-record-access-characterization.json"
)
SYSTEM_XMIN_RECORD_ACCESS_CHARACTERIZATION_EVIDENCE = json.loads(
    SYSTEM_XMIN_RECORD_ACCESS_CHARACTERIZATION_EVIDENCE_PATH.read_text(encoding="utf-8")
)
DIGEST_NULLABILITY_QUERY_DRIFT_EVIDENCE = json.loads(
    (
        DIR
        / "provider-free-disposable-postgresql-evidence-digest-nullability-query-drift.json"
    ).read_text(encoding="utf-8")
)
PRE_DIGEST_NULLABILITY_RECOVERY_EVIDENCE = json.loads(
    (
        DIR
        / "provider-free-disposable-postgresql-evidence-pre-digest-nullability-recovery.json"
    ).read_text(encoding="utf-8")
)
TYPES_PROJECTION_RECONSTRUCTION_EVIDENCE = json.loads(
    (
        DIR
        / "provider-free-disposable-postgresql-evidence-types-projection-reconstruction.json"
    ).read_text(encoding="utf-8")
)
PRE_ROW_PROJECTION_RECOVERY_EVIDENCE = json.loads(
    (
        DIR
        / "provider-free-disposable-postgresql-evidence-pre-row-composite-projection-order-recovery.json"
    ).read_text(encoding="utf-8")
)
ROW_PROJECTION_RECOVERY_EVIDENCE = json.loads(
    (
        DIR
        / "provider-free-disposable-postgresql-evidence-top-level-xid-insert-reload-pass.json"
    ).read_text(encoding="utf-8")
)
RLS_LOCK_VISIBILITY_PASS_EVIDENCE_PATH = (
    DIR / "provider-free-disposable-postgresql-evidence-rls-lock-visibility-pass.json"
)
RLS_LOCK_VISIBILITY_PASS_EVIDENCE = json.loads(
    RLS_LOCK_VISIBILITY_PASS_EVIDENCE_PATH.read_text(encoding="utf-8")
)
TOP_LEVEL_XID_INSERT_RELOAD_CHARACTERIZATION_EVIDENCE_PATH = (
    DIR / "provider-free-disposable-postgresql-evidence-"
    "top-level-xid-insert-reload-characterization.json"
)
TOP_LEVEL_XID_INSERT_RELOAD_CHARACTERIZATION_EVIDENCE = json.loads(
    TOP_LEVEL_XID_INSERT_RELOAD_CHARACTERIZATION_EVIDENCE_PATH.read_text(
        encoding="utf-8"
    )
)
RLS_LOCK_VISIBILITY_CHARACTERIZATION_EVIDENCE_PATH = (
    DIR
    / "provider-free-disposable-postgresql-evidence-rls-lock-visibility-characterization.json"
)
RLS_LOCK_VISIBILITY_CHARACTERIZATION_EVIDENCE = json.loads(
    RLS_LOCK_VISIBILITY_CHARACTERIZATION_EVIDENCE_PATH.read_text(encoding="utf-8")
)
INTERVAL_CONSTRUCTION_CHARACTERIZATION_EVIDENCE_PATH = (
    DIR
    / "provider-free-disposable-postgresql-evidence-interval-construction-characterization.json"
)
INTERVAL_CONSTRUCTION_CHARACTERIZATION_EVIDENCE = json.loads(
    INTERVAL_CONSTRUCTION_CHARACTERIZATION_EVIDENCE_PATH.read_text(encoding="utf-8")
)
INTERVAL_CONSTRUCTION_PASS_EVIDENCE_PATH = (
    DIR / "provider-free-disposable-postgresql-evidence-interval-construction-pass.json"
)
INTERVAL_CONSTRUCTION_PASS_EVIDENCE = json.loads(
    INTERVAL_CONSTRUCTION_PASS_EVIDENCE_PATH.read_text(encoding="utf-8")
)
UUID_MINIMUM_CHARACTERIZATION_EVIDENCE_PATH = (
    DIR
    / "provider-free-disposable-postgresql-evidence-uuid-minimum-characterization.json"
)
UUID_MINIMUM_CHARACTERIZATION_EVIDENCE = json.loads(
    UUID_MINIMUM_CHARACTERIZATION_EVIDENCE_PATH.read_text(encoding="utf-8")
)
UUID_MINIMUM_PASS_EVIDENCE_PATH = (
    DIR / "provider-free-disposable-postgresql-evidence-uuid-minimum-pass.json"
)
UUID_MINIMUM_PASS_EVIDENCE = json.loads(
    UUID_MINIMUM_PASS_EVIDENCE_PATH.read_text(encoding="utf-8")
)
UUID_MINIMUM_EXPECTED_DIGESTS = {
    key: value
    for key, value in UUID_MINIMUM_PASS_EVIDENCE["catalogue"]["query_digests"].items()
    if key not in {"server", "extensions"}
}
JSON_KEY_SET_ORDER_CHARACTERIZATION_EVIDENCE_PATH = (
    DIR
    / "provider-free-disposable-postgresql-evidence-json-key-set-order-characterization.json"
)
JSON_KEY_SET_ORDER_CHARACTERIZATION_EVIDENCE = json.loads(
    JSON_KEY_SET_ORDER_CHARACTERIZATION_EVIDENCE_PATH.read_text(encoding="utf-8")
)
JSON_KEY_SET_ORDER_PASS_EVIDENCE_PATH = (
    DIR / "provider-free-disposable-postgresql-evidence.json"
)
JSON_KEY_SET_ORDER_PASS_EVIDENCE = json.loads(
    JSON_KEY_SET_ORDER_PASS_EVIDENCE_PATH.read_text(encoding="utf-8")
)
ALIAS_LOCK_VISIBILITY_CHARACTERIZATION_EVIDENCE_PATH = (
    DIR
    / "provider-free-disposable-postgresql-evidence-alias-lock-visibility-characterization.json"
)
ALIAS_LOCK_VISIBILITY_CHARACTERIZATION_EVIDENCE = json.loads(
    ALIAS_LOCK_VISIBILITY_CHARACTERIZATION_EVIDENCE_PATH.read_text(encoding="utf-8")
)
ALIAS_LOCK_VISIBILITY_PASS_EVIDENCE_PATH = (
    DIR / "provider-free-disposable-postgresql-evidence-alias-lock-visibility-pass.json"
)
ALIAS_LOCK_VISIBILITY_PASS_EVIDENCE = json.loads(
    ALIAS_LOCK_VISIBILITY_PASS_EVIDENCE_PATH.read_text(encoding="utf-8")
)
DML_NAME_AMBIGUITY_CHARACTERIZATION_EVIDENCE_PATH = (
    DIR
    / "provider-free-disposable-postgresql-evidence-dml-name-ambiguity-characterization.json"
)
DML_NAME_AMBIGUITY_CHARACTERIZATION_EVIDENCE = json.loads(
    DML_NAME_AMBIGUITY_CHARACTERIZATION_EVIDENCE_PATH.read_text(encoding="utf-8")
)
DML_NAME_AMBIGUITY_PASS_EVIDENCE_PATH = (
    DIR
    / "provider-free-disposable-postgresql-evidence-dml-name-ambiguity-exact-pass.json"
)
DML_NAME_AMBIGUITY_PASS_EVIDENCE = json.loads(
    DML_NAME_AMBIGUITY_PASS_EVIDENCE_PATH.read_text(encoding="utf-8")
)
SUBTRANSACTION_XMIN_CHARACTERIZATION_EVIDENCE_PATH = (
    DIR
    / "provider-free-disposable-postgresql-evidence-subtransaction-xmin-characterization.json"
)
SUBTRANSACTION_XMIN_CHARACTERIZATION_EVIDENCE = json.loads(
    SUBTRANSACTION_XMIN_CHARACTERIZATION_EVIDENCE_PATH.read_text(encoding="utf-8")
)
SUBTRANSACTION_XMIN_PASS_EVIDENCE_PATH = (
    DIR
    / "provider-free-disposable-postgresql-evidence-subtransaction-xmin-exact-pass.json"
)
SUBTRANSACTION_XMIN_PASS_EVIDENCE = json.loads(
    SUBTRANSACTION_XMIN_PASS_EVIDENCE_PATH.read_text(encoding="utf-8")
)
SUPPORT_EXECUTE_GRANT_CHARACTERIZATION_EVIDENCE_PATH = (
    DIR
    / "provider-free-disposable-postgresql-evidence-support-execute-grant-characterization.json"
)
SUPPORT_EXECUTE_GRANT_CHARACTERIZATION_EVIDENCE = json.loads(
    SUPPORT_EXECUTE_GRANT_CHARACTERIZATION_EVIDENCE_PATH.read_text(encoding="utf-8")
)
SUPPORT_EXECUTE_GRANT_PASS_EVIDENCE_PATH = (
    DIR
    / "provider-free-disposable-postgresql-evidence-support-execute-grant-exact-pass.json"
)
SUPPORT_EXECUTE_GRANT_PASS_EVIDENCE = json.loads(
    SUPPORT_EXECUTE_GRANT_PASS_EVIDENCE_PATH.read_text(encoding="utf-8")
)
BINDING_RLS_CHARACTERIZATION_EVIDENCE_PATH = (
    DIR
    / "provider-free-disposable-postgresql-evidence-admission-receiver-binding-rls-characterization.json"
)
BINDING_RLS_CHARACTERIZATION_EVIDENCE = json.loads(
    BINDING_RLS_CHARACTERIZATION_EVIDENCE_PATH.read_text(encoding="utf-8")
)
BINDING_RLS_PASS_EVIDENCE_PATH = (
    DIR
    / "provider-free-disposable-postgresql-evidence-admission-receiver-binding-rls-exact-pass.json"
)
BINDING_RLS_PASS_EVIDENCE = json.loads(
    BINDING_RLS_PASS_EVIDENCE_PATH.read_text(encoding="utf-8")
)
INPUT_NAMESPACE_CHARACTERIZATION_EVIDENCE_PATH = (
    DIR
    / "provider-free-disposable-postgresql-input-namespace-characterization-evidence.json"
)
INPUT_NAMESPACE_CHARACTERIZATION_EVIDENCE = json.loads(
    INPUT_NAMESPACE_CHARACTERIZATION_EVIDENCE_PATH.read_text(encoding="utf-8")
)
INPUT_NAMESPACE_EXACT_PASS_EVIDENCE_PATH = (
    DIR / "provider-free-disposable-postgresql-input-namespace-exact-pass-evidence.json"
)
INPUT_NAMESPACE_EXACT_PASS_EVIDENCE = json.loads(
    INPUT_NAMESPACE_EXACT_PASS_EVIDENCE_PATH.read_text(encoding="utf-8")
)
INPUT_NAMESPACE_EXPECTED_QUERY_DIGESTS = {
    key: value
    for key, value in INPUT_NAMESPACE_EXACT_PASS_EVIDENCE["catalogue"][
        "query_digests"
    ].items()
    if key not in {"server", "extensions"}
}
ADMISSION_ROW_SHAPE_CHARACTERIZATION_EVIDENCE_PATH = (
    DIR
    / "provider-free-disposable-postgresql-evidence-admission-row-shape-characterization.json"
)
ADMISSION_ROW_SHAPE_CHARACTERIZATION_EVIDENCE = json.loads(
    ADMISSION_ROW_SHAPE_CHARACTERIZATION_EVIDENCE_PATH.read_text(encoding="utf-8")
)
ADMISSION_ROW_SHAPE_EXPECTED_QUERY_DIGESTS = {
    key: value
    for key, value in ADMISSION_ROW_SHAPE_CHARACTERIZATION_EVIDENCE["catalogue"][
        "query_digests"
    ].items()
    if key not in {"server", "extensions"}
}
ADMISSION_ROW_SHAPE_EXACT_PASS_EVIDENCE_PATH = (
    DIR
    / "provider-free-disposable-postgresql-evidence-admission-row-shape-exact-reproduction.json"
)
ADMISSION_ROW_SHAPE_EXACT_PASS_EVIDENCE = json.loads(
    ADMISSION_ROW_SHAPE_EXACT_PASS_EVIDENCE_PATH.read_text(encoding="utf-8")
)
GENERATION_LOCK_CHARACTERIZATION_EVIDENCE_PATH = (
    DIR
    / "provider-free-disposable-postgresql-evidence-generation-lock-rls-characterization.json"
)
GENERATION_LOCK_CHARACTERIZATION_EVIDENCE = json.loads(
    GENERATION_LOCK_CHARACTERIZATION_EVIDENCE_PATH.read_text(encoding="utf-8")
)
GENERATION_LOCK_EXPECTED_QUERY_DIGESTS = {
    key: value
    for key, value in GENERATION_LOCK_CHARACTERIZATION_EVIDENCE["catalogue"][
        "query_digests"
    ].items()
    if key not in {"server", "extensions"}
}
GENERATION_LOCK_EXACT_PASS_EVIDENCE_PATH = (
    DIR
    / "provider-free-disposable-postgresql-evidence-generation-lock-rls-exact-reproduction.json"
)
GENERATION_LOCK_EXACT_PASS_EVIDENCE = json.loads(
    GENERATION_LOCK_EXACT_PASS_EVIDENCE_PATH.read_text(encoding="utf-8")
)
ANCHOR_LOCK_CHARACTERIZATION_EVIDENCE_PATH = (
    DIR
    / "provider-free-disposable-postgresql-evidence-anchor-lock-rls-characterization.json"
)
ANCHOR_LOCK_CHARACTERIZATION_EVIDENCE = json.loads(
    ANCHOR_LOCK_CHARACTERIZATION_EVIDENCE_PATH.read_text(encoding="utf-8")
)
ANCHOR_LOCK_EXPECTED_QUERY_DIGESTS = {
    key: value
    for key, value in ANCHOR_LOCK_CHARACTERIZATION_EVIDENCE["catalogue"][
        "query_digests"
    ].items()
    if key not in {"server", "extensions"}
}
MANIFEST = json.loads(
    (ROOT / CONTRACT["parent"]["manifest_path"]).read_text(encoding="utf-8")
)
ARTIFACT = rehearsal._canonical_artifact(  # noqa: SLF001 - exact acceptance surface
    (ROOT / CONTRACT["parent"]["artifact_path"]).read_bytes()
)


def _manifest_ids(kind: str) -> list[str]:
    return [
        row["identifier"] for row in MANIFEST["ordered_nodes"] if row["kind"] == kind
    ]


def _valid_facts() -> dict[str, Any]:
    role_login = {
        match.group(1): match.group(2) is None
        for match in rehearsal.ROLE_LINE.finditer(ARTIFACT.decode("utf-8"))
    }
    roles = [
        {
            "name": name,
            "login": role_login[name],
            "inherit": False,
            "createdb": False,
            "createrole": False,
            "replication": False,
            "bypassrls": False,
            "superuser": False,
        }
        for name in sorted(_manifest_ids("ROLE"))
    ]
    types = []
    for kind, pg_kind in (("DOMAIN", "d"), ("ENUM", "e"), ("COMPOSITE", "c")):
        types.extend(
            {
                "name": name,
                "type_kind": pg_kind,
                "owner": "context_schema_owner",
            }
            for name in _manifest_ids(kind)
        )
    relations = [
        {
            "name": name,
            "relation_kind": "r",
            "owner": "context_schema_owner",
            "rls_enabled": True,
            "rls_forced": True,
            "acl": "",
        }
        for name in _manifest_ids("TABLE")
    ]
    app_columns = []
    type_name = {
        "uuid": "uuid",
        "text": "text",
        "timestamptz": "timestamp with time zone",
        "integer": "integer",
        "bigint": "bigint",
        "jsonb": "jsonb",
    }
    for table in PREREQUISITE["tables"]:
        for position, column in enumerate(table["columns"], start=1):
            app_columns.append(
                {
                    "relation": "public." + table["name"],
                    "position": position,
                    "name": column["name"],
                    "data_type": type_name[column["type"]],
                    "not_null": not column["nullable"],
                    "default_sql": column["default_sql"] or "",
                }
            )
    app_columns.sort(key=lambda row: (row["relation"], row["position"]))
    fabric_columns = [
        {
            "relation": name,
            "position": 1,
            "name": "synthetic_manifest_bound_column",
            "data_type": "uuid",
            "not_null": True,
            "default_sql": "",
        }
        for name in _manifest_ids("TABLE")
    ]
    function_names = (
        _manifest_ids("SUPPORT_FUNCTION")
        + _manifest_ids("ENTRY_POINT")
        + _manifest_ids("TRIGGER_FUNCTION")
    )
    functions = [
        {
            "name": name,
            "identity_arguments": "",
            "owner": rehearsal.FUNCTION_OWNER_OVERRIDES.get(
                name, "context_schema_owner"
            ),
            "language": "plpgsql",
            "security_definer": True,
            "volatility": "v",
            "strict": False,
            "parallel_safety": "u",
            "configuration": '{"search_path=pg_catalog, emr4_context_fabric"}',
            "acl": "",
        }
        for name in function_names
    ]
    triggers = [
        {
            "name": name,
            "relation": "public.appointments",
            "function": _manifest_ids("TRIGGER_FUNCTION")[index % 14],
            "enabled": "O",
            "deferrable": index >= 7,
            "initially_deferred": index >= 7,
            "definition": "fixed",
        }
        for index, name in enumerate(_manifest_ids("TRIGGER_DECLARATION"))
    ]
    facts: dict[str, Any] = {
        "server": {"server_version_num": 160010, "database": "emr4_synthetic_success"},
        "roles": roles,
        "schema": [
            {"name": "emr4_context_fabric", "owner": "context_schema_owner", "acl": ""}
        ],
        "types": types,
        "relations": relations,
        "columns": sorted(
            app_columns + fabric_columns,
            key=lambda row: (row["relation"], row["position"]),
        ),
        "constraints": [
            {
                "identifier": name,
                "constraint_kind": "c",
                "deferrable": False,
                "initially_deferred": False,
                "definition": "fixed",
            }
            for name in _manifest_ids("CONSTRAINT")
        ],
        "indexes": [
            {
                "name": name,
                "relation": "fixed",
                "unique_index": True,
                "definition": "fixed",
            }
            for name in _manifest_ids("UNIQUE_INDEX")
        ],
        "rls": [
            {"name": name, "enabled": True, "forced": True}
            for name in _manifest_ids("TABLE")
        ],
        "policies": [
            {
                "name": name,
                "relation": "fixed",
                "command": "r",
                "permissive": True,
                "qualification": "fixed",
                "with_check": "",
            }
            for name in _manifest_ids("RLS_POLICY")
        ],
        "functions": functions,
        "triggers": triggers,
        "schema_acl": [],
        "relation_acl": [],
        "function_acl": [],
        "application_relations": [
            {
                "name": "public." + table["name"],
                "owner": PREREQUISITE["owner"],
                "row_count": 0,
            }
            for table in PREREQUISITE["tables"]
        ],
        "extensions": [{"name": "plpgsql", "version": "1.0"}],
    }
    assert set(facts) == set(CONTRACT["catalogue_query_ids"])
    return facts


def _reconstructed_type_facts(*, digest_domain_not_null: bool) -> list[dict[str, Any]]:
    type_catalogue = ddl_rehearsal.derive_effective_catalogue()["effective_structural"][
        "type_catalogue"
    ]
    domain_definitions = {
        "source_contract_code": (
            "CHECK (VALUE = 'diary.appointment_rescheduled.v1'::text)"
        ),
        "digest_sha256": "CHECK (VALUE ~ '^sha256:[0-9a-f]{64}$'::text)",
        "key_id": ("CHECK (VALUE ~ '^[A-Za-z0-9][A-Za-z0-9._:-]{0,126}$'::text)"),
        "frame_mask": "CHECK (VALUE >= 0 AND VALUE <= 3)",
    }
    rows: list[dict[str, Any]] = []
    for domain in type_catalogue["domains"]:
        not_null = domain["not_null_values"]
        if domain["name"] == "digest_sha256":
            not_null = digest_domain_not_null
        rows.append(
            {
                "name": "emr4_context_fabric." + domain["name"],
                "type_kind": "d",
                "owner": "context_schema_owner",
                "domain_base_type": {
                    "text": "text",
                    "smallint": "smallint",
                }[domain["base_type"]],
                "domain_not_null": not_null,
                "domain_default_sql": "",
                "domain_constraints": [
                    {
                        "name": domain["name"] + "_check",
                        "definition": domain_definitions[domain["name"]],
                    }
                ],
                "enum_labels": [],
                "composite_attributes": [],
            }
        )
    for enum in type_catalogue["enums"]:
        rows.append(
            {
                "name": "emr4_context_fabric." + enum["name"],
                "type_kind": "e",
                "owner": "context_schema_owner",
                "domain_base_type": "",
                "domain_not_null": False,
                "domain_default_sql": "",
                "domain_constraints": [],
                "enum_labels": enum["values"],
                "composite_attributes": [],
            }
        )
    for composite in type_catalogue["composites"]:
        attributes = []
        for position, field in enumerate(composite["fields"], start=1):
            data_type = {
                "uuid": "uuid",
                "bigint": "bigint",
                "boolean": "boolean",
            }.get(
                field["data_type"],
                "emr4_context_fabric." + field["data_type"],
            )
            attributes.append(
                {
                    "position": position,
                    "name": field["name"],
                    "data_type": data_type,
                }
            )
        rows.append(
            {
                "name": "emr4_context_fabric." + composite["name"],
                "type_kind": "c",
                "owner": "context_schema_owner",
                "domain_base_type": "",
                "domain_not_null": False,
                "domain_default_sql": "",
                "domain_constraints": [],
                "enum_labels": [],
                "composite_attributes": attributes,
            }
        )
    return sorted(rows, key=lambda row: row["name"])


def test_contract_schemas_are_whole_document_valid() -> None:
    for schema, payload in (
        (CONTRACT_SCHEMA, CONTRACT),
        (PREREQUISITE_SCHEMA, PREREQUISITE),
    ):
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(payload)
    Draft202012Validator.check_schema(EVIDENCE_SCHEMA)
    Draft202012Validator(EVIDENCE_SCHEMA).validate(CHARACTERIZATION_EVIDENCE)


def test_historical_exact_catalogue_digests_bind_revised_types_and_registration_rls() -> (
    None
):
    expected = {
        key: digest
        for key, digest in CHARACTERIZATION_EVIDENCE["catalogue"][
            "query_digests"
        ].items()
        if key not in {"server", "extensions"}
    }
    prior_types_digest = expected["types"]
    original_type_facts = _reconstructed_type_facts(digest_domain_not_null=True)
    revised_type_facts = _reconstructed_type_facts(digest_domain_not_null=False)
    expected["types"] = rehearsal._facts_digest(revised_type_facts)  # noqa: SLF001
    expected["policies"] = REGISTRATION_RLS_CHARACTERIZATION_EVIDENCE["catalogue"][
        "query_digests"
    ]["policies"]
    historical_digests = {
        key: value
        for key, value in ROW_PROJECTION_RECOVERY_EVIDENCE["catalogue"][
            "query_digests"
        ].items()
        if key not in {"server", "extensions"}
    }
    assert historical_digests == expected
    assert ROW_PROJECTION_RECOVERY_EVIDENCE["catalogue"]["expectation_mode"] == (
        "exact_digest_bound"
    )
    assert ROW_PROJECTION_RECOVERY_EVIDENCE["catalogue"]["query_digests"] == {
        **expected,
        "extensions": ROW_PROJECTION_RECOVERY_EVIDENCE["catalogue"]["query_digests"][
            "extensions"
        ],
        "server": ROW_PROJECTION_RECOVERY_EVIDENCE["catalogue"]["query_digests"][
            "server"
        ],
    }
    assert ROW_PROJECTION_RECOVERY_EVIDENCE["catalogue"]["expectation_mode"] == (
        "exact_digest_bound"
    )
    historical_expectation = {
        "mode": "exact_digest_bound",
        "expected_query_digests": expected,
    }
    assert historical_expectation["expected_query_digests"] == historical_digests
    assert prior_types_digest == (
        "sha256:099effe28c033aeec242bcd7b68f0703af558ebedfc4e37875a15ac6f05594f8"
    )
    assert rehearsal._facts_digest(original_type_facts) == prior_types_digest  # noqa: SLF001
    assert expected["types"] == (
        "sha256:8ec5eddfcb4cd14d62f783bfcfeb02004204630510b8913ce769a1c49a2135af"
    )
    assert [
        (before["name"], key, before[key], after[key])
        for before, after in zip(original_type_facts, revised_type_facts, strict=True)
        for key in before
        if before[key] != after[key]
    ] == [
        (
            "emr4_context_fabric.digest_sha256",
            "domain_not_null",
            True,
            False,
        )
    ]
    assert set(expected) == set(CONTRACT["catalogue_query_ids"]) - {
        "server",
        "extensions",
    }
    assert CHARACTERIZATION_EVIDENCE["result"] == "catalogue_characterization_required"
    assert CHARACTERIZATION_EVIDENCE["catalogue"]["expectation_mode"] == (
        "characterization_only"
    )
    assert CHARACTERIZATION_EVIDENCE["cleanup"] == {
        "absence_verified": True,
        "container_id": "a60e76c4608f929b674dcda2140f89155c85b7f806785ba53ae002452eb3a392",
        "removed": True,
        "status": "cleanup_verified",
    }
    revised = {
        key: digest
        for key, digest in REGISTRATION_RLS_CHARACTERIZATION_EVIDENCE["catalogue"][
            "query_digests"
        ].items()
        if key not in {"server", "extensions"}
    }
    assert revised == expected
    assert REGISTRATION_RLS_CHARACTERIZATION_EVIDENCE["result"] == (
        "catalogue_characterization_required"
    )
    assert (
        REGISTRATION_RLS_CHARACTERIZATION_EVIDENCE["catalogue"]["expectation_mode"]
        == "characterization_only"
    )
    assert (
        rehearsal._bytes_sha(  # noqa: SLF001
            (
                DIR
                / "provider-free-disposable-postgresql-evidence-registration-rls-characterization.json"
            ).read_bytes()
        )
        == "d46af8f0ae45f0b79b0ca81a8a09728b046747486399c8ac0646772073657726"
    )
    assert REGISTRATION_RLS_CHARACTERIZATION_EVIDENCE["cleanup"] == {
        "absence_verified": True,
        "container_id": "9047bffc9931cb24b46f7d03ace6a7f1d17bde12aadbbb3a2f06b70fcfbb3689",
        "removed": True,
        "status": "cleanup_verified",
    }

    system_xmin = SYSTEM_XMIN_CHARACTERIZATION_EVIDENCE
    Draft202012Validator(EVIDENCE_SCHEMA).validate(system_xmin)
    assert (
        rehearsal._bytes_sha(  # noqa: SLF001
            SYSTEM_XMIN_CHARACTERIZATION_EVIDENCE_PATH.read_bytes()
        )
        == "a34da84879a7d761bf5365acd9df76da46c296c37d740288ddbe029add9f15b6"
    )
    assert system_xmin["result"] == "catalogue_characterization_required"
    assert system_xmin["catalogue"]["expectation_mode"] == "characterization_only"
    assert {
        key: digest
        for key, digest in system_xmin["catalogue"]["query_digests"].items()
        if key not in {"server", "extensions"}
    } == expected
    assert system_xmin["cleanup"] == {
        "absence_verified": True,
        "container_id": "ffab67da4356cbb71842d38039aff94f0e2c3a7983599cee1f4d1f5f08e5e770",
        "removed": True,
        "status": "cleanup_verified",
    }

    explicit_alias = SYSTEM_XMIN_ALIAS_CHARACTERIZATION_EVIDENCE
    Draft202012Validator(EVIDENCE_SCHEMA).validate(explicit_alias)
    assert (
        rehearsal._bytes_sha(  # noqa: SLF001
            SYSTEM_XMIN_ALIAS_CHARACTERIZATION_EVIDENCE_PATH.read_bytes()
        )
        == "e77af8076d37fa4690a829ece3ecd7b3c3d8a4392285c89ffbc5a2044044ddfa"
    )
    assert explicit_alias["result"] == "catalogue_characterization_required"
    assert explicit_alias["catalogue"]["expectation_mode"] == "characterization_only"
    assert {
        key: digest
        for key, digest in explicit_alias["catalogue"]["query_digests"].items()
        if key not in {"server", "extensions"}
    } == expected
    assert explicit_alias["cleanup"] == {
        "absence_verified": True,
        "container_id": "e10340911ad8afef2f33da41319a1b52994584c2fc958c40b9c7219f5055c63e",
        "removed": True,
        "status": "cleanup_verified",
    }

    direct_record = SYSTEM_XMIN_RECORD_ACCESS_CHARACTERIZATION_EVIDENCE
    Draft202012Validator(EVIDENCE_SCHEMA).validate(direct_record)
    assert (
        rehearsal._bytes_sha(  # noqa: SLF001
            SYSTEM_XMIN_RECORD_ACCESS_CHARACTERIZATION_EVIDENCE_PATH.read_bytes()
        )
        == "ae39e8727abae894914839998f7e2d2a25a2720faa4952d3c7b69b7c822d9f45"
    )
    assert direct_record["result"] == "catalogue_characterization_required"
    assert direct_record["catalogue"]["expectation_mode"] == "characterization_only"
    assert {
        key: digest
        for key, digest in direct_record["catalogue"]["query_digests"].items()
        if key not in {"server", "extensions"}
    } == expected
    assert direct_record["cleanup"] == {
        "absence_verified": True,
        "container_id": "ebfe9cac39aa53c89307d4ef2ed1cdae4878ec21f5da799a93d454f70503905a",
        "removed": True,
        "status": "cleanup_verified",
    }


def test_rls_lock_visibility_characterization_changes_only_policy_digest() -> None:
    evidence = RLS_LOCK_VISIBILITY_CHARACTERIZATION_EVIDENCE
    Draft202012Validator(EVIDENCE_SCHEMA).validate(evidence)
    assert (
        rehearsal._bytes_sha(  # noqa: SLF001
            RLS_LOCK_VISIBILITY_CHARACTERIZATION_EVIDENCE_PATH.read_bytes()
        )
        == "1721544f7031856dc83f5c6e5e4a4921952d10758b055884b3c2189b07ad88ff"
    )
    assert evidence["result"] == "catalogue_characterization_required"
    assert evidence["parent"] == {
        "artifact_byte_count": 1_391_506,
        "artifact_sha256": (
            "sha256:28dc21611c937cfa9d6db5bb58d571b1a267af02377294b16cef029a7e1e4800"
        ),
        "contract_sha256": (
            "sha256:5e44a7625995ed188b257af067d167c8cafe96622179c285a494fcce8312ae0e"
        ),
        "prerequisite_contract_sha256": rehearsal.EXPECTED_PREREQUISITE_SHA256,
        "prerequisite_sql_sha256": (
            "sha256:fab760ba9a1d82987ddb1b89476570f5d06a32d08de99b87476f970ba2628b38"
        ),
        "statement_count": 412,
    }
    assert evidence["catalogue"]["status"] == "characterized"
    assert evidence["catalogue"]["expectation_mode"] == "characterization_only"
    characterized = {
        key: value
        for key, value in evidence["catalogue"]["query_digests"].items()
        if key not in {"server", "extensions"}
    }
    historical = {
        key: value
        for key, value in ROW_PROJECTION_RECOVERY_EVIDENCE["catalogue"][
            "query_digests"
        ].items()
        if key not in {"server", "extensions"}
    }
    assert {key for key in characterized if characterized[key] != historical[key]} == {
        "policies"
    }
    assert characterized["policies"] == (
        "sha256:3e3f043b4c3f103c8170805e0e0aff327c83916010dc0cef727665fa92c8ef03"
    )
    assert evidence["cleanup"] == {
        "absence_verified": True,
        "container_id": (
            "765e0581b624ed61d48f9a6c12b407516cf543b3ce32d519c29d93bae44a48a3"
        ),
        "removed": True,
        "status": "cleanup_verified",
    }


def test_rls_lock_visibility_parse_catalogue_evidence_is_exact_pass() -> None:
    evidence = RLS_LOCK_VISIBILITY_PASS_EVIDENCE
    Draft202012Validator(EVIDENCE_SCHEMA).validate(evidence)
    assert (
        rehearsal._bytes_sha(  # noqa: SLF001
            RLS_LOCK_VISIBILITY_PASS_EVIDENCE_PATH.read_bytes()
        )
        == "e417fc377e6b8e9ff723e21e88b40e41b9cfb2424d2fd6122e404c54bf068611"
    )
    assert evidence["result"] == rehearsal.PASS_RESULT
    assert evidence["lifecycle"][-3:] == [
        "catalogue_matched",
        "cleanup_verified",
        "passed",
    ]
    assert evidence["parent"] == {
        "artifact_byte_count": 1_391_506,
        "artifact_sha256": (
            "sha256:28dc21611c937cfa9d6db5bb58d571b1a267af02377294b16cef029a7e1e4800"
        ),
        "contract_sha256": (
            "sha256:2834249d755d83764abf974d524424b958a261f6d8c94808403d4d8bf3a5a1f1"
        ),
        "prerequisite_contract_sha256": rehearsal.EXPECTED_PREREQUISITE_SHA256,
        "prerequisite_sql_sha256": (
            "sha256:fab760ba9a1d82987ddb1b89476570f5d06a32d08de99b87476f970ba2628b38"
        ),
        "statement_count": 412,
    }
    assert evidence["catalogue"]["status"] == "matched"
    assert evidence["catalogue"]["expectation_mode"] == "exact_digest_bound"
    assert {
        key: value
        for key, value in evidence["catalogue"]["query_digests"].items()
        if key not in {"server", "extensions"}
    } == {
        key: value
        for key, value in RLS_LOCK_VISIBILITY_CHARACTERIZATION_EVIDENCE["catalogue"][
            "query_digests"
        ].items()
        if key not in {"server", "extensions"}
    }
    assert evidence["cleanup"] == {
        "absence_verified": True,
        "container_id": (
            "3156fb7876f366dd36bbd52645706aa3d4158526e5e1bcfdaa72ff4c56c3c22f"
        ),
        "removed": True,
        "status": "cleanup_verified",
    }


def test_interval_construction_characterization_is_nonaccepting_and_exactly_cleaned_up() -> (
    None
):
    evidence = INTERVAL_CONSTRUCTION_CHARACTERIZATION_EVIDENCE
    Draft202012Validator(EVIDENCE_SCHEMA).validate(evidence)
    assert (
        rehearsal._bytes_sha(  # noqa: SLF001
            INTERVAL_CONSTRUCTION_CHARACTERIZATION_EVIDENCE_PATH.read_bytes()
        )
        == "257daa83f9d45c9397a3666fa54ee906016fd3fa4924d58af2269f3316b65139"
    )
    assert evidence["result"] == "catalogue_characterization_required"
    assert evidence["catalogue"]["expectation_mode"] == "characterization_only"
    assert evidence["catalogue"]["status"] == "characterized"
    assert evidence["parent"] == {
        "artifact_byte_count": 1_391_614,
        "artifact_sha256": (
            "sha256:c113b2480106441043562412ee3135d2a79bd56c76bb5bc2705734d9e5f8cf51"
        ),
        "contract_sha256": (
            "sha256:11bdc9050bf26bc26cc61037b95911317ffcb7994e532e2f5a28ca742599e2b3"
        ),
        "prerequisite_contract_sha256": rehearsal.EXPECTED_PREREQUISITE_SHA256,
        "prerequisite_sql_sha256": (
            "sha256:fab760ba9a1d82987ddb1b89476570f5d06a32d08de99b87476f970ba2628b38"
        ),
        "statement_count": 412,
    }
    characterized = {
        key: value
        for key, value in evidence["catalogue"]["query_digests"].items()
        if key not in {"server", "extensions"}
    }
    assert characterized == UUID_MINIMUM_EXPECTED_DIGESTS
    assert characterized == {
        key: value
        for key, value in RLS_LOCK_VISIBILITY_PASS_EVIDENCE["catalogue"][
            "query_digests"
        ].items()
        if key not in {"server", "extensions"}
    }
    assert evidence["cleanup"] == {
        "absence_verified": True,
        "container_id": (
            "6b0f34cb1bdd7faa3c6482bbe300e2ecb5f7ed9109890a90f18e846625ce7c8d"
        ),
        "removed": True,
        "status": "cleanup_verified",
    }


def test_interval_construction_parse_catalogue_evidence_is_exact_pass() -> None:
    evidence = INTERVAL_CONSTRUCTION_PASS_EVIDENCE
    Draft202012Validator(EVIDENCE_SCHEMA).validate(evidence)
    assert (
        rehearsal._bytes_sha(  # noqa: SLF001
            INTERVAL_CONSTRUCTION_PASS_EVIDENCE_PATH.read_bytes()
        )
        == "3bb1c5dd63f6b12566869a95abdd1beeaf7a317b045845d5ee4cdcef0eeee4d9"
    )
    assert evidence["result"] == rehearsal.PASS_RESULT
    assert evidence["lifecycle"][-3:] == [
        "catalogue_matched",
        "cleanup_verified",
        "passed",
    ]
    assert evidence["parent"] == {
        "artifact_byte_count": 1_391_614,
        "artifact_sha256": (
            "sha256:c113b2480106441043562412ee3135d2a79bd56c76bb5bc2705734d9e5f8cf51"
        ),
        "contract_sha256": (
            "sha256:e1c3b23bf2731f366a1eab342185a6f26eeb638a0a767fcdd391438b5e116e40"
        ),
        "prerequisite_contract_sha256": rehearsal.EXPECTED_PREREQUISITE_SHA256,
        "prerequisite_sql_sha256": (
            "sha256:fab760ba9a1d82987ddb1b89476570f5d06a32d08de99b87476f970ba2628b38"
        ),
        "statement_count": 412,
    }
    assert evidence["catalogue"]["status"] == "matched"
    assert evidence["catalogue"]["expectation_mode"] == "exact_digest_bound"
    assert {
        key: value
        for key, value in evidence["catalogue"]["query_digests"].items()
        if key not in {"server", "extensions"}
    } == UUID_MINIMUM_EXPECTED_DIGESTS
    assert evidence["cleanup"] == {
        "absence_verified": True,
        "container_id": (
            "338fbb6a1a2294d5370879e226adf10ff83214523b7afc3a093bc74f701beb07"
        ),
        "removed": True,
        "status": "cleanup_verified",
    }


def test_uuid_minimum_characterization_is_nonaccepting_and_exactly_cleaned_up() -> None:
    evidence = UUID_MINIMUM_CHARACTERIZATION_EVIDENCE
    Draft202012Validator(EVIDENCE_SCHEMA).validate(evidence)
    assert (
        rehearsal._bytes_sha(  # noqa: SLF001
            UUID_MINIMUM_CHARACTERIZATION_EVIDENCE_PATH.read_bytes()
        )
        == "db86a77bc81f12a461161c807710ba8a42eabfa76080289704d5819dabee35ba"
    )
    assert evidence["result"] == "catalogue_characterization_required"
    assert evidence["catalogue"]["expectation_mode"] == "characterization_only"
    assert evidence["catalogue"]["status"] == "characterized"
    assert evidence["parent"] == {
        "artifact_byte_count": 1_391_670,
        "artifact_sha256": (
            "sha256:eeabfc39bf0b0c1073f57e97835440b394391161bec3ddc62be6e186fd7af6d8"
        ),
        "contract_sha256": (
            "sha256:988bddb52ede755bccb5a4151c65fc022b34c58785bc74c4aa1cc4fa65d82c37"
        ),
        "prerequisite_contract_sha256": rehearsal.EXPECTED_PREREQUISITE_SHA256,
        "prerequisite_sql_sha256": (
            "sha256:fab760ba9a1d82987ddb1b89476570f5d06a32d08de99b87476f970ba2628b38"
        ),
        "statement_count": 412,
    }
    assert {
        key: value
        for key, value in evidence["catalogue"]["query_digests"].items()
        if key not in {"server", "extensions"}
    } == UUID_MINIMUM_EXPECTED_DIGESTS
    assert evidence["cleanup"] == {
        "absence_verified": True,
        "container_id": (
            "2b6956ba924cb6a06d104f3ba8746a0c5b6a1aa815d1f864d9a87810237d1ef6"
        ),
        "removed": True,
        "status": "cleanup_verified",
    }


def test_uuid_minimum_parse_catalogue_evidence_is_exact_pass() -> None:
    evidence = UUID_MINIMUM_PASS_EVIDENCE
    Draft202012Validator(EVIDENCE_SCHEMA).validate(evidence)
    assert (
        rehearsal._bytes_sha(  # noqa: SLF001
            UUID_MINIMUM_PASS_EVIDENCE_PATH.read_bytes()
        )
        == "f14c406ca460ba893e66fed3150e759f63d9631c976a95fbb03faae7f1f381c8"
    )
    assert evidence["attempt_id"] == "988bb667765158c33e219d8d"
    assert evidence["result"] == rehearsal.PASS_RESULT
    assert evidence["lifecycle"][-3:] == [
        "catalogue_matched",
        "cleanup_verified",
        "passed",
    ]
    assert evidence["parent"] == {
        "artifact_byte_count": 1_391_670,
        "artifact_sha256": (
            "sha256:eeabfc39bf0b0c1073f57e97835440b394391161bec3ddc62be6e186fd7af6d8"
        ),
        "contract_sha256": (
            "sha256:fd8256d4906e79367d280f5ba945c8b2ccb0f01f20790cb43ae68f47496dbdc4"
        ),
        "prerequisite_contract_sha256": rehearsal.EXPECTED_PREREQUISITE_SHA256,
        "prerequisite_sql_sha256": (
            "sha256:fab760ba9a1d82987ddb1b89476570f5d06a32d08de99b87476f970ba2628b38"
        ),
        "statement_count": 412,
    }
    assert evidence["catalogue"]["status"] == "matched"
    assert evidence["catalogue"]["expectation_mode"] == "exact_digest_bound"
    assert {
        key: value
        for key, value in evidence["catalogue"]["query_digests"].items()
        if key not in {"server", "extensions"}
    } == UUID_MINIMUM_EXPECTED_DIGESTS
    assert evidence["cleanup"] == {
        "absence_verified": True,
        "container_id": (
            "d1fa9e1501b07e5079e9bb6c9325e67399dd36ee922795e346fac07120bcc95b"
        ),
        "removed": True,
        "status": "cleanup_verified",
    }


def test_json_key_set_order_characterization_is_nonaccepting_and_exactly_cleaned_up() -> (
    None
):
    evidence = JSON_KEY_SET_ORDER_CHARACTERIZATION_EVIDENCE
    Draft202012Validator(EVIDENCE_SCHEMA).validate(evidence)
    assert (
        rehearsal._bytes_sha(  # noqa: SLF001
            JSON_KEY_SET_ORDER_CHARACTERIZATION_EVIDENCE_PATH.read_bytes()
        )
        == "9e5338986fb4dea8ad5c7f0f0a96e624a525c93e127d507f651e68ca2b5b02b0"
    )
    assert evidence["attempt_id"] == "6033b191fdfb084894b58514"
    assert evidence["result"] == "catalogue_characterization_required"
    assert evidence["lifecycle"][-2:] == [
        "catalogue_characterized",
        "cleanup_verified",
    ]
    assert evidence["parent"] == {
        "artifact_byte_count": 1_391_670,
        "artifact_sha256": (
            "sha256:f4479c772f144973c1a1f373e16e0bcb3543fea6128c8054a282316ce5d02714"
        ),
        "contract_sha256": (
            "sha256:c351ddf9d8f64141d3226b772114c7b2d74bc652268ec4ed12b248e05078da72"
        ),
        "prerequisite_contract_sha256": rehearsal.EXPECTED_PREREQUISITE_SHA256,
        "prerequisite_sql_sha256": (
            "sha256:fab760ba9a1d82987ddb1b89476570f5d06a32d08de99b87476f970ba2628b38"
        ),
        "statement_count": 412,
    }
    characterized = {
        key: value
        for key, value in evidence["catalogue"]["query_digests"].items()
        if key not in {"server", "extensions"}
    }
    assert evidence["catalogue"]["expectation_mode"] == "characterization_only"
    assert evidence["catalogue"]["status"] == "characterized"
    assert characterized == UUID_MINIMUM_EXPECTED_DIGESTS
    assert characterized == UUID_MINIMUM_EXPECTED_DIGESTS
    assert evidence["cleanup"] == {
        "absence_verified": True,
        "container_id": (
            "ef4ca866ac143928bdc59e31f2013c2a57d1f9f4896052a1a42b223e945a8aad"
        ),
        "removed": True,
        "status": "cleanup_verified",
    }


def test_json_key_set_order_parse_catalogue_evidence_is_distinct_exact_pass() -> None:
    evidence = JSON_KEY_SET_ORDER_PASS_EVIDENCE
    Draft202012Validator(EVIDENCE_SCHEMA).validate(evidence)
    assert (
        rehearsal._bytes_sha(  # noqa: SLF001
            JSON_KEY_SET_ORDER_PASS_EVIDENCE_PATH.read_bytes()
        )
        == "97d1385c6b617890cb0f155122e30eb283d49e42af1d44db385a2b9f4a9c2bec"
    )
    assert evidence["attempt_id"] == "40b24076b96417c14b150455"
    assert evidence["result"] == rehearsal.PASS_RESULT
    assert evidence["lifecycle"][-3:] == [
        "catalogue_matched",
        "cleanup_verified",
        "passed",
    ]
    assert evidence["parent"] == {
        "artifact_byte_count": 1_391_670,
        "artifact_sha256": (
            "sha256:f4479c772f144973c1a1f373e16e0bcb3543fea6128c8054a282316ce5d02714"
        ),
        "contract_sha256": (
            "sha256:0037d3d2b11d25cb46b691e6962409b9bf025fe91b3aa1d928b0ac0a29ec0d74"
        ),
        "prerequisite_contract_sha256": rehearsal.EXPECTED_PREREQUISITE_SHA256,
        "prerequisite_sql_sha256": (
            "sha256:fab760ba9a1d82987ddb1b89476570f5d06a32d08de99b87476f970ba2628b38"
        ),
        "statement_count": 412,
    }
    assert evidence["catalogue"]["expectation_mode"] == "exact_digest_bound"
    assert evidence["catalogue"]["status"] == "matched"
    assert {
        key: value
        for key, value in evidence["catalogue"]["query_digests"].items()
        if key not in {"server", "extensions"}
    } == UUID_MINIMUM_EXPECTED_DIGESTS
    assert (
        evidence["catalogue"]["query_digests"]
        == (JSON_KEY_SET_ORDER_CHARACTERIZATION_EVIDENCE["catalogue"]["query_digests"])
    )
    assert evidence["cleanup"] == {
        "absence_verified": True,
        "container_id": (
            "fabe8880296727bcd501f4fb7fe8918829b9695eb2f419950db9165bafefc1ad"
        ),
        "removed": True,
        "status": "cleanup_verified",
    }


def test_alias_lock_visibility_characterization_is_nonaccepting_and_exact() -> None:
    evidence = ALIAS_LOCK_VISIBILITY_CHARACTERIZATION_EVIDENCE
    Draft202012Validator(EVIDENCE_SCHEMA).validate(evidence)
    assert (
        rehearsal._bytes_sha(  # noqa: SLF001
            ALIAS_LOCK_VISIBILITY_CHARACTERIZATION_EVIDENCE_PATH.read_bytes()
        )
        == "32dee447d4c180799ad4afd3b038d715dde9cb6796997dbc3379ceec82f2001a"
    )
    assert evidence["attempt_id"] == "575003a3542e56595336dd59"
    assert evidence["result"] == "catalogue_characterization_required"
    assert evidence["catalogue"]["expectation_mode"] == "characterization_only"
    assert evidence["catalogue"]["kind_counts"]["policies"] == 45
    assert evidence["cleanup"] == {
        "absence_verified": True,
        "container_id": (
            "f3ed6c479e09672673c598e1d7095a3bfece136271c1dae1925f3c1a98f4a748"
        ),
        "removed": True,
        "status": "cleanup_verified",
    }
    previous = JSON_KEY_SET_ORDER_PASS_EVIDENCE["catalogue"]["query_digests"]
    current = evidence["catalogue"]["query_digests"]
    assert {
        key: (previous[key], current[key])
        for key in current
        if previous[key] != current[key]
    } == {
        "policies": (
            "sha256:3e3f043b4c3f103c8170805e0e0aff327c83916010dc0cef727665fa92c8ef03",
            "sha256:51f697aeb94a50f432f6683c9e9c93412eee38853617a113c1ab020216a57168",
        )
    }


def test_alias_lock_visibility_exact_reproduction_is_distinct_pass() -> None:
    evidence = ALIAS_LOCK_VISIBILITY_PASS_EVIDENCE
    Draft202012Validator(EVIDENCE_SCHEMA).validate(evidence)
    assert (
        rehearsal._bytes_sha(  # noqa: SLF001
            ALIAS_LOCK_VISIBILITY_PASS_EVIDENCE_PATH.read_bytes()
        )
        == "9f61fb3da219159491a9ac73125ec0d93bed0c72ed0f435182964169c7a6e027"
    )
    assert evidence["attempt_id"] == "c0deb58ac4fea820eec366ff"
    assert evidence["result"] == rehearsal.PASS_RESULT
    assert evidence["catalogue"]["expectation_mode"] == "exact_digest_bound"
    assert evidence["catalogue"]["status"] == "matched"
    assert (
        evidence["catalogue"]["query_digests"]
        == (
            ALIAS_LOCK_VISIBILITY_CHARACTERIZATION_EVIDENCE["catalogue"][
                "query_digests"
            ]
        )
    )
    assert evidence["parent"]["contract_sha256"] == (
        "sha256:554f70e0dc1e61fa0d831e6b9023bb35f57052323fea2513f6353c111d9a8178"
    )
    assert evidence["cleanup"] == {
        "absence_verified": True,
        "container_id": (
            "209b8b6f2a4e862a1ceaa9fddca8cb8b7f9252d55594b19cee5a6b6be786cc89"
        ),
        "removed": True,
        "status": "cleanup_verified",
    }
    assert (
        evidence["cleanup"]["container_id"]
        != (JSON_KEY_SET_ORDER_CHARACTERIZATION_EVIDENCE["cleanup"]["container_id"])
    )


def test_dml_name_ambiguity_characterization_is_exact_nonaccepting_parent() -> None:
    evidence = DML_NAME_AMBIGUITY_CHARACTERIZATION_EVIDENCE
    Draft202012Validator(EVIDENCE_SCHEMA).validate(evidence)
    assert (
        rehearsal._bytes_sha(  # noqa: SLF001
            DML_NAME_AMBIGUITY_CHARACTERIZATION_EVIDENCE_PATH.read_bytes()
        )
        == "3bf66870cf80edc507b191d6022a5e3d22f3b7f3073c9ae4e696fed2fc54155c"
    )
    assert evidence["attempt_id"] == "1dcabd0341a3770703633468"
    assert evidence["result"] == "catalogue_characterization_required"
    assert evidence["catalogue"]["expectation_mode"] == "characterization_only"
    assert evidence["catalogue"]["status"] == "characterized"
    assert evidence["parent"] == {
        "artifact_byte_count": 1_427_373,
        "artifact_sha256": (
            "sha256:b2e476995848b64d819ae6c545d5b8c9b93707288993a0120d09d19c503230dc"
        ),
        "contract_sha256": (
            "sha256:ad1a34dd0f94ea72351fe14ec9c2221c9cb24656ed18a345d41c1ab78127975d"
        ),
        "prerequisite_contract_sha256": rehearsal.EXPECTED_PREREQUISITE_SHA256,
        "prerequisite_sql_sha256": (
            "sha256:fab760ba9a1d82987ddb1b89476570f5d06a32d08de99b87476f970ba2628b38"
        ),
        "statement_count": 413,
    }
    exact_digests = {
        key: value
        for key, value in evidence["catalogue"]["query_digests"].items()
        if key not in {"server", "extensions"}
    }
    assert exact_digests == {
        key: value
        for key, value in SUBTRANSACTION_XMIN_PASS_EVIDENCE["catalogue"][
            "query_digests"
        ].items()
        if key not in {"server", "extensions"}
    }
    assert exact_digests == {
        key: value
        for key, value in ALIAS_LOCK_VISIBILITY_PASS_EVIDENCE["catalogue"][
            "query_digests"
        ].items()
        if key not in {"server", "extensions"}
    }
    assert evidence["cleanup"] == {
        "absence_verified": True,
        "container_id": (
            "a90453f42aa6c3fe2afd8dd2403f9f85bc60803d087ea2c0849116754897f339"
        ),
        "removed": True,
        "status": "cleanup_verified",
    }


def test_subtransaction_xmin_characterization_is_exact_nonaccepting_parent() -> None:
    evidence = SUBTRANSACTION_XMIN_CHARACTERIZATION_EVIDENCE
    Draft202012Validator(EVIDENCE_SCHEMA).validate(evidence)
    assert (
        rehearsal._bytes_sha(  # noqa: SLF001
            SUBTRANSACTION_XMIN_CHARACTERIZATION_EVIDENCE_PATH.read_bytes()
        )
        == "4d140704d33624e90737022e5f9d095559152bd56554514ccebc73222d845750"
    )
    assert evidence["attempt_id"] == "25b98f1da5c8de4d06188a70"
    assert evidence["result"] == "catalogue_characterization_required"
    assert evidence["catalogue"]["expectation_mode"] == "characterization_only"
    assert evidence["catalogue"]["status"] == "characterized"
    assert evidence["parent"] == {
        "artifact_byte_count": 1_416_483,
        "artifact_sha256": (
            "sha256:03150dfec61944df8f26ca2473200afa49e88ddcf9d9fce950320a2a98bd96e0"
        ),
        "contract_sha256": (
            "sha256:5c5a3093b7815bde2e14765ef37ba087fedebd326c0a3eaefa0f745f9b3cd254"
        ),
        "prerequisite_contract_sha256": rehearsal.EXPECTED_PREREQUISITE_SHA256,
        "prerequisite_sql_sha256": (
            "sha256:fab760ba9a1d82987ddb1b89476570f5d06a32d08de99b87476f970ba2628b38"
        ),
        "statement_count": 413,
    }
    exact_digests = {
        key: value
        for key, value in evidence["catalogue"]["query_digests"].items()
        if key not in {"server", "extensions"}
    }
    assert exact_digests == {
        key: value
        for key, value in SUBTRANSACTION_XMIN_PASS_EVIDENCE["catalogue"][
            "query_digests"
        ].items()
        if key not in {"server", "extensions"}
    }
    assert exact_digests == {
        key: value
        for key, value in DML_NAME_AMBIGUITY_CHARACTERIZATION_EVIDENCE["catalogue"][
            "query_digests"
        ].items()
        if key not in {"server", "extensions"}
    }
    assert evidence["cleanup"] == {
        "absence_verified": True,
        "container_id": (
            "8e351be5609f7d01eb18919321eb42ff02736ef64c68c8affa422356ed1eb9d9"
        ),
        "removed": True,
        "status": "cleanup_verified",
    }


def test_subtransaction_xmin_exact_reproduction_is_distinct_pass() -> None:
    evidence = SUBTRANSACTION_XMIN_PASS_EVIDENCE
    Draft202012Validator(EVIDENCE_SCHEMA).validate(evidence)
    assert (
        rehearsal._bytes_sha(  # noqa: SLF001
            SUBTRANSACTION_XMIN_PASS_EVIDENCE_PATH.read_bytes()
        )
        == "cb439eefe9eb243eb4eccda144ac51218d9e26ba71c0dd14402ee066b7c1fb14"
    )
    characterization = SUBTRANSACTION_XMIN_CHARACTERIZATION_EVIDENCE
    assert evidence["attempt_id"] == "4ec417dfc5e16ad6e462e66d"
    assert evidence["attempt_id"] != characterization["attempt_id"]
    assert evidence["result"] == rehearsal.PASS_RESULT
    assert evidence["catalogue"]["expectation_mode"] == "exact_digest_bound"
    assert evidence["catalogue"]["status"] == "matched"
    assert (
        evidence["catalogue"]["query_digests"]
        == characterization["catalogue"]["query_digests"]
    )
    assert evidence["parent"]["contract_sha256"] == (
        "sha256:3dc318e64b9c30817c0e2cdca650fc284ae3d2f35e93e697d0cac5368fecbd03"
    )
    assert evidence["lifecycle"][-3:] == [
        "catalogue_matched",
        "cleanup_verified",
        "passed",
    ]
    assert evidence["cleanup"] == {
        "absence_verified": True,
        "container_id": (
            "f784718297efd8d11250a2a34bbf7a25627036d2fcb9c745fb6c56e954f6e517"
        ),
        "removed": True,
        "status": "cleanup_verified",
    }
    assert (
        evidence["cleanup"]["container_id"]
        != characterization["cleanup"]["container_id"]
    )


def test_support_execute_grant_characterization_is_exact_and_narrow() -> None:
    evidence = SUPPORT_EXECUTE_GRANT_CHARACTERIZATION_EVIDENCE
    Draft202012Validator(EVIDENCE_SCHEMA).validate(evidence)
    assert (
        rehearsal._bytes_sha(  # noqa: SLF001
            SUPPORT_EXECUTE_GRANT_CHARACTERIZATION_EVIDENCE_PATH.read_bytes()
        )
        == "d0724ebd4a0caa07ee032ca031d54af1e99934d6966f45838d2fbe4450b588de"
    )
    assert evidence["attempt_id"] == "1c99cb094789272b4fdfeec7"
    assert evidence["result"] == "catalogue_characterization_required"
    assert evidence["catalogue"]["expectation_mode"] == "characterization_only"
    assert evidence["catalogue"]["status"] == "characterized"
    assert evidence["parent"] == {
        "artifact_byte_count": 1_419_518,
        "artifact_sha256": (
            "sha256:934237c4525bf193999039aa1ad00ca815081152d32a6105f3cf730310695461"
        ),
        "contract_sha256": (
            "sha256:501b886da9d0d549e71a619f1fbf01ce2c619fa987bfc6ff74445dadb24f03a2"
        ),
        "prerequisite_contract_sha256": rehearsal.EXPECTED_PREREQUISITE_SHA256,
        "prerequisite_sql_sha256": (
            "sha256:fab760ba9a1d82987ddb1b89476570f5d06a32d08de99b87476f970ba2628b38"
        ),
        "statement_count": 421,
    }
    characterized = {
        key: value
        for key, value in evidence["catalogue"]["query_digests"].items()
        if key not in {"server", "extensions"}
    }
    previous = {
        key: value
        for key, value in SUBTRANSACTION_XMIN_CHARACTERIZATION_EVIDENCE["catalogue"][
            "query_digests"
        ].items()
        if key not in {"server", "extensions"}
    }
    changed = {
        key for key, value in characterized.items() if previous.get(key) != value
    }
    expected_at_support_repair = dict(INPUT_NAMESPACE_EXPECTED_QUERY_DIGESTS)
    expected_at_support_repair["functions"] = (
        "sha256:5f7063b8f2a5d11c4088e5f66b9649f9842b977c1c8d0ccfaa8fcdb1d4d19c7d"
    )
    expected_at_support_repair["policies"] = (
        "sha256:51f697aeb94a50f432f6683c9e9c93412eee38853617a113c1ab020216a57168"
    )
    assert characterized == expected_at_support_repair
    assert set(characterized) == set(INPUT_NAMESPACE_EXPECTED_QUERY_DIGESTS)
    assert {
        key
        for key, value in characterized.items()
        if INPUT_NAMESPACE_EXPECTED_QUERY_DIGESTS[key] != value
    } == {"functions", "policies"}
    assert changed == {"function_acl", "functions"}
    assert characterized["function_acl"] == (
        "sha256:dba3aa331a66e608ac22e434b24637050e5f89f5e63fd653a51201df58a520f3"
    )
    assert characterized["functions"] == (
        "sha256:5f7063b8f2a5d11c4088e5f66b9649f9842b977c1c8d0ccfaa8fcdb1d4d19c7d"
    )
    assert evidence["cleanup"] == {
        "absence_verified": True,
        "container_id": (
            "df7b8805d021f8b27b685b24d1d2e91cb3fd2ac5797ce0595e632d62c7ba36bb"
        ),
        "removed": True,
        "status": "cleanup_verified",
    }


def test_admission_receiver_binding_rls_characterization_is_exact_and_narrow() -> None:
    evidence = BINDING_RLS_CHARACTERIZATION_EVIDENCE
    Draft202012Validator(EVIDENCE_SCHEMA).validate(evidence)
    assert (
        rehearsal._bytes_sha(  # noqa: SLF001
            BINDING_RLS_CHARACTERIZATION_EVIDENCE_PATH.read_bytes()
        )
        == "41f065c805fdc3cc140ded68baf180bfd88ae3c34bbcd962cc140e9d359d814d"
    )
    assert evidence["attempt_id"] == "bef2c8193761c8bcee4e5af2"
    assert evidence["result"] == "catalogue_characterization_required"
    assert evidence["catalogue"]["expectation_mode"] == "characterization_only"
    assert evidence["catalogue"]["status"] == "characterized"
    assert evidence["parent"] == {
        "artifact_byte_count": 1_419_573,
        "artifact_sha256": (
            "sha256:1d53c7ac1cd9a9fb19faafcca0ebcf8dacadf238f62df873d2d3fc78c657b407"
        ),
        "contract_sha256": (
            "sha256:8cb7862d66ce805d8af2d4aea96e8e46df92040cfc44a263da6d3245b5a3f02c"
        ),
        "prerequisite_contract_sha256": rehearsal.EXPECTED_PREREQUISITE_SHA256,
        "prerequisite_sql_sha256": (
            "sha256:fab760ba9a1d82987ddb1b89476570f5d06a32d08de99b87476f970ba2628b38"
        ),
        "statement_count": 421,
    }
    characterized = {
        key: value
        for key, value in evidence["catalogue"]["query_digests"].items()
        if key not in {"server", "extensions"}
    }
    predecessor = {
        key: value
        for key, value in SUPPORT_EXECUTE_GRANT_PASS_EVIDENCE["catalogue"][
            "query_digests"
        ].items()
        if key not in {"server", "extensions"}
    }
    expected_at_binding_repair = dict(INPUT_NAMESPACE_EXPECTED_QUERY_DIGESTS)
    expected_at_binding_repair["functions"] = (
        "sha256:5f7063b8f2a5d11c4088e5f66b9649f9842b977c1c8d0ccfaa8fcdb1d4d19c7d"
    )
    assert characterized == expected_at_binding_repair
    assert {
        key for key, value in characterized.items() if predecessor.get(key) != value
    } == {"policies"}
    assert characterized["policies"] == (
        "sha256:5bd0a6629eaa4a734e01d786781ea62121e887581b38558b33677bd79c752a0f"
    )
    assert evidence["cleanup"] == {
        "absence_verified": True,
        "container_id": (
            "a1d64af025b200578f73cb020e357befc8176969534fd8a006eb3dfe137952e4"
        ),
        "removed": True,
        "status": "cleanup_verified",
    }


def test_admission_receiver_binding_rls_exact_reproduction_is_distinct_pass() -> None:
    evidence = BINDING_RLS_PASS_EVIDENCE
    characterization = BINDING_RLS_CHARACTERIZATION_EVIDENCE
    Draft202012Validator(EVIDENCE_SCHEMA).validate(evidence)
    assert (
        rehearsal._bytes_sha(BINDING_RLS_PASS_EVIDENCE_PATH.read_bytes())  # noqa: SLF001
        == "bf842570457b09c78dd4e7685b618af535fea71d6f0093f27d1699c9876471c9"
    )
    assert evidence["attempt_id"] == "bdc767620bfcaeb8d693be3e"
    assert evidence["attempt_id"] != characterization["attempt_id"]
    assert evidence["result"] == rehearsal.PASS_RESULT
    assert evidence["catalogue"]["expectation_mode"] == "exact_digest_bound"
    assert evidence["catalogue"]["status"] == "matched"
    assert {
        key: value
        for key, value in evidence["catalogue"]["query_digests"].items()
        if key not in {"server", "extensions"}
    } == {
        **INPUT_NAMESPACE_EXPECTED_QUERY_DIGESTS,
        "functions": (
            "sha256:5f7063b8f2a5d11c4088e5f66b9649f9842b977c1c8d0ccfaa8fcdb1d4d19c7d"
        ),
    }
    assert evidence["parent"] == {
        "artifact_byte_count": 1_419_573,
        "artifact_sha256": (
            "sha256:1d53c7ac1cd9a9fb19faafcca0ebcf8dacadf238f62df873d2d3fc78c657b407"
        ),
        "contract_sha256": (
            "sha256:cf746ed8824ef8853677020e90083c2b4bfe1b4096a36ad7735cfeabf0eb4b91"
        ),
        "prerequisite_contract_sha256": rehearsal.EXPECTED_PREREQUISITE_SHA256,
        "prerequisite_sql_sha256": (
            "sha256:fab760ba9a1d82987ddb1b89476570f5d06a32d08de99b87476f970ba2628b38"
        ),
        "statement_count": 421,
    }
    assert evidence["cleanup"] == {
        "absence_verified": True,
        "container_id": (
            "2cbe41c2589b2abd175f4807d89efcc14e0321738790ce92365fe9af60099ad7"
        ),
        "removed": True,
        "status": "cleanup_verified",
    }
    assert (
        evidence["cleanup"]["container_id"]
        != characterization["cleanup"]["container_id"]
    )


def test_input_namespace_characterization_is_exact_and_changes_only_functions() -> None:
    evidence = INPUT_NAMESPACE_CHARACTERIZATION_EVIDENCE
    Draft202012Validator(EVIDENCE_SCHEMA).validate(evidence)
    assert (
        rehearsal._bytes_sha(  # noqa: SLF001
            INPUT_NAMESPACE_CHARACTERIZATION_EVIDENCE_PATH.read_bytes()
        )
        == "75700e214ac4b155602fe584f1fd0cbbe64c86426c51f449ae31a0e22b867971"
    )
    assert evidence["attempt_id"] == "a8eab7307b3f1913a8d5d992"
    assert evidence["result"] == "catalogue_characterization_required"
    assert evidence["catalogue"]["expectation_mode"] == "characterization_only"
    assert evidence["catalogue"]["status"] == "characterized"
    assert evidence["parent"] == {
        "artifact_byte_count": 1_448_546,
        "artifact_sha256": (
            "sha256:8756f315a3f1112551550141c1fff83d047ff24103b357e97ddb17b0c805e470"
        ),
        "contract_sha256": (
            "sha256:9c5975701655a8785d89cd3adc96e02be26eaf560f6bcc5e43d8fd8b529dfe10"
        ),
        "prerequisite_contract_sha256": rehearsal.EXPECTED_PREREQUISITE_SHA256,
        "prerequisite_sql_sha256": (
            "sha256:fab760ba9a1d82987ddb1b89476570f5d06a32d08de99b87476f970ba2628b38"
        ),
        "statement_count": 421,
    }
    characterized = {
        key: value
        for key, value in evidence["catalogue"]["query_digests"].items()
        if key not in {"server", "extensions"}
    }
    predecessor = {
        key: value
        for key, value in BINDING_RLS_PASS_EVIDENCE["catalogue"][
            "query_digests"
        ].items()
        if key not in {"server", "extensions"}
    }
    assert characterized == INPUT_NAMESPACE_EXPECTED_QUERY_DIGESTS
    assert {
        key for key, value in characterized.items() if predecessor.get(key) != value
    } == {"functions"}
    assert evidence["cleanup"] == {
        "absence_verified": True,
        "container_id": (
            "5ef5d8a9209a84f5033bc995f4c974eb2160e72ac3ed93cc9ec487c194c83ff7"
        ),
        "removed": True,
        "status": "cleanup_verified",
    }


def test_input_namespace_exact_reproduction_is_distinct_pass() -> None:
    evidence = INPUT_NAMESPACE_EXACT_PASS_EVIDENCE
    characterization = INPUT_NAMESPACE_CHARACTERIZATION_EVIDENCE
    Draft202012Validator(EVIDENCE_SCHEMA).validate(evidence)
    assert (
        rehearsal._bytes_sha(  # noqa: SLF001
            INPUT_NAMESPACE_EXACT_PASS_EVIDENCE_PATH.read_bytes()
        )
        == "0ec5fb64d9b431e313067e2f550e052d947fecdc8dffa98809df44adb711a528"
    )
    assert evidence["attempt_id"] == "5edadc6475cfe1fc633eb8ff"
    assert evidence["attempt_id"] != characterization["attempt_id"]
    assert evidence["result"] == rehearsal.PASS_RESULT
    assert evidence["catalogue"]["expectation_mode"] == "exact_digest_bound"
    assert evidence["catalogue"]["status"] == "matched"
    assert {
        key: value
        for key, value in evidence["catalogue"]["query_digests"].items()
        if key not in {"server", "extensions"}
    } == INPUT_NAMESPACE_EXPECTED_QUERY_DIGESTS
    assert evidence["parent"] == {
        "artifact_byte_count": 1_448_546,
        "artifact_sha256": (
            "sha256:8756f315a3f1112551550141c1fff83d047ff24103b357e97ddb17b0c805e470"
        ),
        "contract_sha256": (
            "sha256:e783fedb13785672cad84c76984f39ec6ec0b7bb3787ca9b33fb61db1f59fc68"
        ),
        "prerequisite_contract_sha256": rehearsal.EXPECTED_PREREQUISITE_SHA256,
        "prerequisite_sql_sha256": (
            "sha256:fab760ba9a1d82987ddb1b89476570f5d06a32d08de99b87476f970ba2628b38"
        ),
        "statement_count": 421,
    }
    assert evidence["cleanup"] == {
        "absence_verified": True,
        "container_id": (
            "3a2d0797eb78d0b392485b4034e87d7b1119ddb49b5c683e6bc726a48c909997"
        ),
        "removed": True,
        "status": "cleanup_verified",
    }
    assert (
        evidence["cleanup"]["container_id"]
        != characterization["cleanup"]["container_id"]
    )


def test_support_execute_grant_exact_reproduction_is_distinct_pass() -> None:
    evidence = SUPPORT_EXECUTE_GRANT_PASS_EVIDENCE
    Draft202012Validator(EVIDENCE_SCHEMA).validate(evidence)
    assert (
        rehearsal._bytes_sha(  # noqa: SLF001
            SUPPORT_EXECUTE_GRANT_PASS_EVIDENCE_PATH.read_bytes()
        )
        == "51608c55dd7a491f7ca20d822881e7d06c2e594aa968aa7d99a754ca0100eca5"
    )
    characterization = SUPPORT_EXECUTE_GRANT_CHARACTERIZATION_EVIDENCE
    assert evidence["attempt_id"] == "044a7267b0e4b0f89d24b95c"
    assert evidence["attempt_id"] != characterization["attempt_id"]
    assert evidence["result"] == rehearsal.PASS_RESULT
    assert evidence["catalogue"]["expectation_mode"] == "exact_digest_bound"
    assert evidence["catalogue"]["status"] == "matched"
    assert (
        evidence["catalogue"]["query_digests"]
        == characterization["catalogue"]["query_digests"]
    )
    assert evidence["parent"]["contract_sha256"] == (
        "sha256:d9237e6db14e314de5e2981be1073575db2e512ed1eff44b1f9ebf8b044c17bc"
    )
    assert evidence["lifecycle"][-3:] == [
        "catalogue_matched",
        "cleanup_verified",
        "passed",
    ]
    assert evidence["cleanup"] == {
        "absence_verified": True,
        "container_id": (
            "ab6b5d7b32023c184174fd10a653e05bf367c79fe6cd1ce5a79463802525cac4"
        ),
        "removed": True,
        "status": "cleanup_verified",
    }
    assert (
        evidence["cleanup"]["container_id"]
        != characterization["cleanup"]["container_id"]
    )


def test_dml_name_ambiguity_exact_reproduction_is_distinct_pass() -> None:
    evidence = DML_NAME_AMBIGUITY_PASS_EVIDENCE
    Draft202012Validator(EVIDENCE_SCHEMA).validate(evidence)
    assert (
        rehearsal._bytes_sha(  # noqa: SLF001
            DML_NAME_AMBIGUITY_PASS_EVIDENCE_PATH.read_bytes()
        )
        == "122d2db7ec577875c1477eee6a4fa0c51dc9117ce0c23bc3704aa43f4c791ca0"
    )
    assert evidence["attempt_id"] == "26f530dab9ed13ba20500267"
    assert (
        evidence["attempt_id"]
        != DML_NAME_AMBIGUITY_CHARACTERIZATION_EVIDENCE["attempt_id"]
    )
    assert evidence["result"] == rehearsal.PASS_RESULT
    assert evidence["catalogue"]["expectation_mode"] == "exact_digest_bound"
    assert evidence["catalogue"]["status"] == "matched"
    assert (
        evidence["catalogue"]["query_digests"]
        == DML_NAME_AMBIGUITY_CHARACTERIZATION_EVIDENCE["catalogue"]["query_digests"]
    )
    assert evidence["parent"]["contract_sha256"] == (
        "sha256:f696bc57c3bbe6e25fc6f817aff337ef85b199bffff66fbf33ffa327c982e673"
    )
    assert evidence["lifecycle"][-3:] == [
        "catalogue_matched",
        "cleanup_verified",
        "passed",
    ]
    assert evidence["cleanup"] == {
        "absence_verified": True,
        "container_id": (
            "a26898ce851b1eab61039023466c2e9802227ae4b223faaa0d1cc48c58e0db76"
        ),
        "removed": True,
        "status": "cleanup_verified",
    }
    assert (
        evidence["cleanup"]["container_id"]
        != (DML_NAME_AMBIGUITY_CHARACTERIZATION_EVIDENCE["cleanup"]["container_id"])
    )


def test_digest_nullability_query_drift_is_preserved_fail_closed() -> None:
    evidence = DIGEST_NULLABILITY_QUERY_DRIFT_EVIDENCE
    Draft202012Validator(EVIDENCE_SCHEMA).validate(evidence)
    Draft202012Validator(EVIDENCE_SCHEMA).validate(
        PRE_DIGEST_NULLABILITY_RECOVERY_EVIDENCE
    )

    assert evidence["result"] == "rehearsal_failed"
    assert evidence["lifecycle"][-2:] == ["artifact_admitted", "cleanup_verified"]
    assert evidence["environment"]["failure"] == {
        "code": "exact_query_digest",
        "detail_digest": "sha256:" + rehearsal._bytes_sha(b"types"),  # noqa: SLF001
        "stage": "catalogue",
    }
    assert evidence["parent"]["artifact_sha256"] == (
        "sha256:9407b8b641488b8c48ad51ef58c7ca2c3c15e83dca89da58de8f5726aef69f65"
    )
    assert evidence["cleanup"]["removed"] is True
    assert evidence["cleanup"]["absence_verified"] is True


def test_incomplete_types_projection_retry_is_preserved_fail_closed() -> None:
    evidence = TYPES_PROJECTION_RECONSTRUCTION_EVIDENCE
    Draft202012Validator(EVIDENCE_SCHEMA).validate(evidence)

    assert evidence["result"] == "rehearsal_failed"
    assert evidence["lifecycle"][-2:] == ["artifact_admitted", "cleanup_verified"]
    assert evidence["environment"]["failure"] == {
        "code": "exact_query_digest",
        "detail_digest": "sha256:" + rehearsal._bytes_sha(b"types"),  # noqa: SLF001
        "stage": "catalogue",
    }
    assert evidence["parent"]["contract_sha256"] == (
        "sha256:3e4b5d6498a746723361d64e75a0cd0aacfcc816c60a63908e78e75a45ed3b2c"
    )
    assert evidence["cleanup"]["removed"] is True
    assert evidence["cleanup"]["absence_verified"] is True


def test_pre_row_projection_recovery_parse_catalogue_pass_is_preserved() -> None:
    evidence = PRE_ROW_PROJECTION_RECOVERY_EVIDENCE
    Draft202012Validator(EVIDENCE_SCHEMA).validate(evidence)

    assert (
        rehearsal._bytes_sha(  # noqa: SLF001
            (
                DIR
                / "provider-free-disposable-postgresql-evidence-pre-row-composite-projection-order-recovery.json"
            ).read_bytes()
        )
        == "3ef47b7a14b2581b6c7bf1732594b1e1c322a90e07ec7d43e2e5b5006b1a3281"
    )

    assert evidence["result"] == (
        "raisa_provider_free_disposable_postgresql_durability_"
        "parse_catalogue_rehearsal_pass"
    )
    assert evidence["lifecycle"][-3:] == [
        "catalogue_matched",
        "cleanup_verified",
        "passed",
    ]
    assert evidence["catalogue"]["query_digests"]["types"] == (
        "sha256:8ec5eddfcb4cd14d62f783bfcfeb02004204630510b8913ce769a1c49a2135af"
    )
    assert evidence["parent"]["contract_sha256"] == (
        "sha256:b1900c96779ff4225be286b51e0c8ecd0b6034177f08deff9d415e9a10c822cb"
    )
    assert evidence["cleanup"]["removed"] is True
    assert evidence["cleanup"]["absence_verified"] is True


def test_system_xmin_record_access_recovery_parse_catalogue_evidence_is_exact_pass() -> (
    None
):
    evidence = ROW_PROJECTION_RECOVERY_EVIDENCE
    Draft202012Validator(EVIDENCE_SCHEMA).validate(evidence)
    assert (
        rehearsal._bytes_sha(  # noqa: SLF001
            (
                DIR
                / "provider-free-disposable-postgresql-evidence-top-level-xid-insert-reload-pass.json"
            ).read_bytes()
        )
        == "83ea56186636b2ffb7dfce8c3d8d303bc489fce8d9e5301ccbe0e3b8cde0629a"
    )

    assert evidence["result"] == rehearsal.PASS_RESULT
    assert evidence["lifecycle"][-3:] == [
        "catalogue_matched",
        "cleanup_verified",
        "passed",
    ]
    assert evidence["parent"] == {
        "artifact_byte_count": 1_391_453,
        "artifact_sha256": (
            "sha256:25744edad60b0f76083cb6bb0d35a077b58cb9cad1fcff23089d2bcb064107cb"
        ),
        "contract_sha256": (
            "sha256:d482ab2c4b96e3bfa854e4c723e9891c2b4b8ac9670db2f73729207ede345919"
        ),
        "prerequisite_contract_sha256": rehearsal.EXPECTED_PREREQUISITE_SHA256,
        "prerequisite_sql_sha256": (
            "sha256:fab760ba9a1d82987ddb1b89476570f5d06a32d08de99b87476f970ba2628b38"
        ),
        "statement_count": 412,
    }
    assert evidence["catalogue"]["status"] == "matched"
    assert evidence["catalogue"]["expectation_mode"] == "exact_digest_bound"
    historical_digests = {
        key: value
        for key, value in evidence["catalogue"]["query_digests"].items()
        if key not in {"server", "extensions"}
    }
    assert set(historical_digests) == set(CONTRACT["catalogue_query_ids"]) - {
        "server",
        "extensions",
    }
    assert historical_digests["policies"] == (
        "sha256:7c847b9d0e153bb02101bc3704d33d72e8aefdf4cfc911e0b092149393cc1b37"
    )
    assert evidence["environment"]["image"] == {
        "id": (
            "sha256:64154d0babcb1741988719e703419af0382b19953706149f9872fbd0f438efa8"
        ),
        "pull_attempted": False,
        "reference": "postgres:16-bookworm",
    }
    assert evidence["cleanup"] == {
        "absence_verified": True,
        "container_id": (
            "9aafcf3721ae6922a36478232aad8898b88d280b315dc2c7740fe2b7256e8d64"
        ),
        "removed": True,
        "status": "cleanup_verified",
    }


def test_top_level_xid_insert_reload_characterization_is_exact_and_nonpassing() -> None:
    evidence = TOP_LEVEL_XID_INSERT_RELOAD_CHARACTERIZATION_EVIDENCE
    Draft202012Validator(EVIDENCE_SCHEMA).validate(evidence)

    assert (
        rehearsal._bytes_sha(  # noqa: SLF001
            TOP_LEVEL_XID_INSERT_RELOAD_CHARACTERIZATION_EVIDENCE_PATH.read_bytes()
        )
        == "3f09cfa15c305eea8279947d84e36901f574265cf599cc4d838b2441251c8979"
    )
    assert evidence["result"] == "catalogue_characterization_required"
    assert evidence["parent"]["artifact_sha256"] == (
        "sha256:25744edad60b0f76083cb6bb0d35a077b58cb9cad1fcff23089d2bcb064107cb"
    )
    assert evidence["parent"]["artifact_byte_count"] == 1_391_453
    assert evidence["parent"]["contract_sha256"] == (
        "sha256:03b7a1a808f52ced4dff5e48740fff1bb1e83d0233e84fdb855f58a80bae2860"
    )
    assert evidence["catalogue"]["expectation_mode"] == "characterization_only"
    assert evidence["catalogue"]["status"] == "characterized"
    assert {
        key: value
        for key, value in evidence["catalogue"]["query_digests"].items()
        if key not in {"server", "extensions"}
    } == {
        key: value
        for key, value in ROW_PROJECTION_RECOVERY_EVIDENCE["catalogue"][
            "query_digests"
        ].items()
        if key not in {"server", "extensions"}
    }
    assert evidence["cleanup"] == {
        "absence_verified": True,
        "container_id": (
            "71334f0c3cb06532cff801ee52f6b5fe163663046ce0417f3c7bab75ad3b6aaa"
        ),
        "removed": True,
        "status": "cleanup_verified",
    }


def test_parent_artifact_and_manifest_are_exact_before_docker() -> None:
    contract, prerequisite, manifest, artifact = rehearsal._validate_contracts()  # noqa: SLF001
    assert contract == CONTRACT
    assert prerequisite == PREREQUISITE
    assert manifest == MANIFEST
    assert len(artifact) == 1_435_884
    assert rehearsal._bytes_sha(artifact) == CONTRACT["parent"]["artifact_sha256"]  # noqa: SLF001
    assert len(manifest["ordered_nodes"]) == 398
    assert rehearsal._canonical_sha(CONTRACT) == rehearsal.EXPECTED_CONTRACT_SHA256  # noqa: SLF001
    assert (  # noqa: SLF001
        rehearsal._canonical_sha(PREREQUISITE) == rehearsal.EXPECTED_PREREQUISITE_SHA256
    )


def test_admission_row_shape_characterization_is_immutable_and_exactly_rebound() -> (
    None
):
    evidence = ADMISSION_ROW_SHAPE_CHARACTERIZATION_EVIDENCE

    Draft202012Validator(EVIDENCE_SCHEMA).validate(evidence)
    assert (
        rehearsal._bytes_sha(  # noqa: SLF001
            ADMISSION_ROW_SHAPE_CHARACTERIZATION_EVIDENCE_PATH.read_bytes()
        )
        == "fc2268693334c03d6aed78efca8f58d1ba654c1cd0f32709a1ef2d24fd1a5c63"
    )
    assert evidence["attempt_id"] == "2fb9bbacbd4cd172aec49c51"
    assert evidence["result"] == "catalogue_characterization_required"
    assert evidence["catalogue"]["expectation_mode"] == "characterization_only"
    assert evidence["parent"]["contract_sha256"] == (
        "sha256:a34fb46701396f9626a11f94024e233637e381f15e50d10bbec3cba6f1c4a0fa"
    )
    assert evidence["parent"]["artifact_sha256"] == (
        "sha256:ca22e47e847409f1ae8a81f62dd7f5f8402a43176d9015211f657204460fbdbb"
    )
    assert evidence["cleanup"] == {
        "absence_verified": True,
        "container_id": (
            "6515210c07830a7d6df037d12887ecf05961b5c34323e378a3186a9a2f4cd600"
        ),
        "removed": True,
        "status": "cleanup_verified",
    }
    assert ADMISSION_ROW_SHAPE_EXPECTED_QUERY_DIGESTS == {
        key: value
        for key, value in evidence["catalogue"]["query_digests"].items()
        if key not in {"server", "extensions"}
    }
    assert CONTRACT["catalogue_expectation"] == {
        "mode": "exact_digest_bound",
        "expected_query_digests": ANCHOR_LOCK_EXPECTED_QUERY_DIGESTS,
    }
    assert {
        "mode": "exact_digest_bound",
        "expected_query_digests": ADMISSION_ROW_SHAPE_EXPECTED_QUERY_DIGESTS,
    } != CONTRACT["catalogue_expectation"]


def test_admission_row_shape_exact_reproduction_is_immutable_and_complete() -> None:
    evidence = ADMISSION_ROW_SHAPE_EXACT_PASS_EVIDENCE

    Draft202012Validator(EVIDENCE_SCHEMA).validate(evidence)
    assert (
        rehearsal._bytes_sha(  # noqa: SLF001
            ADMISSION_ROW_SHAPE_EXACT_PASS_EVIDENCE_PATH.read_bytes()
        )
        == "041ccbf16d22b80872a397968470c8e215625350e31c87511789775cd2bbb2ce"
    )
    assert evidence["attempt_id"] == "1b606b88bd168f7e48d65224"
    assert evidence["result"] == rehearsal.PASS_RESULT
    assert evidence["catalogue"]["expectation_mode"] == "exact_digest_bound"
    assert evidence["parent"]["contract_sha256"] == (
        "sha256:b81be9b783ba102a663fd3244ee4d1a81c4a2320745aa6f6eac537821b6e1e79"
    )
    assert evidence["parent"]["artifact_sha256"] == (
        "sha256:ca22e47e847409f1ae8a81f62dd7f5f8402a43176d9015211f657204460fbdbb"
    )
    assert {
        key: value
        for key, value in evidence["catalogue"]["query_digests"].items()
        if key not in {"server", "extensions"}
    } == ADMISSION_ROW_SHAPE_EXPECTED_QUERY_DIGESTS
    assert evidence["cleanup"] == {
        "absence_verified": True,
        "container_id": (
            "633a6466452e93679526a61265854d1d32bb0b8c2a454a549c6d847845dd51ee"
        ),
        "removed": True,
        "status": "cleanup_verified",
    }


def test_generation_lock_characterization_is_immutable_and_exactly_bound() -> None:
    evidence = GENERATION_LOCK_CHARACTERIZATION_EVIDENCE

    Draft202012Validator(EVIDENCE_SCHEMA).validate(evidence)
    assert (
        rehearsal._bytes_sha(  # noqa: SLF001
            GENERATION_LOCK_CHARACTERIZATION_EVIDENCE_PATH.read_bytes()
        )
        == "78c157c72243036d395c3bcff30f778fa8b1032bb98eec9a32b37110efbcf536"
    )
    assert evidence["attempt_id"] == "7ab702e5fa8cd5c75a7a8e6c"
    assert evidence["result"] == "catalogue_characterization_required"
    assert evidence["catalogue"]["status"] == "characterized"
    assert evidence["catalogue"]["expectation_mode"] == "characterization_only"
    assert evidence["parent"] == {
        "artifact_byte_count": 1435252,
        "artifact_sha256": (
            "sha256:aa26f92671a18d927e423f9d7df80973a19a87f32d49d85cc3f3d55f6808e8e9"
        ),
        "contract_sha256": (
            "sha256:aea61c7344f6b4990fed848994f63a0f42788c807477fbed1ce1d845dd579227"
        ),
        "prerequisite_contract_sha256": (
            "sha256:0cafc71c8368b227fdb626df386b6ebdac659a77c279901ac2a3e4aa844c0b11"
        ),
        "prerequisite_sql_sha256": (
            "sha256:fab760ba9a1d82987ddb1b89476570f5d06a32d08de99b87476f970ba2628b38"
        ),
        "statement_count": 421,
    }
    assert evidence["cleanup"] == {
        "absence_verified": True,
        "container_id": (
            "aa3d7ccc5a542e2a4531d371405e9ceeee091b0372edeacd1643b76478a87496"
        ),
        "removed": True,
        "status": "cleanup_verified",
    }
    assert GENERATION_LOCK_EXPECTED_QUERY_DIGESTS == {
        key: value
        for key, value in evidence["catalogue"]["query_digests"].items()
        if key not in {"server", "extensions"}
    }
    assert {
        key
        for key, value in GENERATION_LOCK_EXPECTED_QUERY_DIGESTS.items()
        if ADMISSION_ROW_SHAPE_EXPECTED_QUERY_DIGESTS[key] != value
    } == {"policies"}
    assert (
        evidence["catalogue"]["kind_counts"]
        == (ADMISSION_ROW_SHAPE_EXACT_PASS_EVIDENCE["catalogue"]["kind_counts"])
    )
    assert CONTRACT["catalogue_expectation"] == {
        "mode": "exact_digest_bound",
        "expected_query_digests": ANCHOR_LOCK_EXPECTED_QUERY_DIGESTS,
    }


def test_generation_lock_exact_reproduction_is_immutable_and_complete() -> None:
    evidence = GENERATION_LOCK_EXACT_PASS_EVIDENCE

    Draft202012Validator(EVIDENCE_SCHEMA).validate(evidence)
    assert (
        rehearsal._bytes_sha(  # noqa: SLF001
            GENERATION_LOCK_EXACT_PASS_EVIDENCE_PATH.read_bytes()
        )
        == "c82ebc7a0ec45ab2d01b55e33f14adaf120a2f65d9e7f151757a65e4d482e68b"
    )
    assert evidence["attempt_id"] == "9f71b0e4f0c8f99ab8a6f2d1"
    assert evidence["result"] == rehearsal.PASS_RESULT
    assert evidence["catalogue"]["status"] == "matched"
    assert evidence["catalogue"]["expectation_mode"] == "exact_digest_bound"
    assert evidence["parent"] == {
        "artifact_byte_count": 1435252,
        "artifact_sha256": (
            "sha256:aa26f92671a18d927e423f9d7df80973a19a87f32d49d85cc3f3d55f6808e8e9"
        ),
        "contract_sha256": (
            "sha256:dbedcaf7628a68859412d898e86292b2366209941d18f58363c45174b6fc60ba"
        ),
        "prerequisite_contract_sha256": (
            "sha256:0cafc71c8368b227fdb626df386b6ebdac659a77c279901ac2a3e4aa844c0b11"
        ),
        "prerequisite_sql_sha256": (
            "sha256:fab760ba9a1d82987ddb1b89476570f5d06a32d08de99b87476f970ba2628b38"
        ),
        "statement_count": 421,
    }
    assert (
        evidence["catalogue"]["query_digests"]
        == (GENERATION_LOCK_CHARACTERIZATION_EVIDENCE["catalogue"]["query_digests"])
    )
    assert (
        evidence["catalogue"]["kind_counts"]
        == (GENERATION_LOCK_CHARACTERIZATION_EVIDENCE["catalogue"]["kind_counts"])
    )
    assert evidence["cleanup"] == {
        "absence_verified": True,
        "container_id": (
            "fdd29923e074419b93706b89131e384fff13a46d9717cab12458cfcf8c70a59d"
        ),
        "removed": True,
        "status": "cleanup_verified",
    }


def test_anchor_lock_characterization_is_immutable_and_exactly_bound() -> None:
    evidence = ANCHOR_LOCK_CHARACTERIZATION_EVIDENCE

    Draft202012Validator(EVIDENCE_SCHEMA).validate(evidence)
    assert (
        rehearsal._bytes_sha(  # noqa: SLF001
            ANCHOR_LOCK_CHARACTERIZATION_EVIDENCE_PATH.read_bytes()
        )
        == "e1568e1218fc9663b1490349828a7ea40f5da933e9db0b7b7271164c8981e968"
    )
    assert evidence["attempt_id"] == "9c293b77a2ebc1364f602f17"
    assert evidence["result"] == "catalogue_characterization_required"
    assert evidence["catalogue"]["status"] == "characterized"
    assert evidence["catalogue"]["expectation_mode"] == "characterization_only"
    assert evidence["parent"] == {
        "artifact_byte_count": 1_435_884,
        "artifact_sha256": (
            "sha256:550336e145eac6ac004447d05ea3e72d970f6d8283d3af2689aed62cfff92bc6"
        ),
        "contract_sha256": (
            "sha256:9f99140c0871db3374ca1d7971d5000a56491d70ab2a2bbd4a593a8df1f66663"
        ),
        "prerequisite_contract_sha256": (
            "sha256:0cafc71c8368b227fdb626df386b6ebdac659a77c279901ac2a3e4aa844c0b11"
        ),
        "prerequisite_sql_sha256": (
            "sha256:fab760ba9a1d82987ddb1b89476570f5d06a32d08de99b87476f970ba2628b38"
        ),
        "statement_count": 422,
    }
    assert evidence["cleanup"] == {
        "absence_verified": True,
        "container_id": (
            "84066c4614b605a9150ab304155e9f64523fe1aecb4c773452ef9900e9937dd0"
        ),
        "removed": True,
        "status": "cleanup_verified",
    }
    assert CONTRACT["catalogue_expectation"] == {
        "mode": "exact_digest_bound",
        "expected_query_digests": ANCHOR_LOCK_EXPECTED_QUERY_DIGESTS,
    }
    assert {
        key
        for key, value in ANCHOR_LOCK_EXPECTED_QUERY_DIGESTS.items()
        if GENERATION_LOCK_EXPECTED_QUERY_DIGESTS[key] != value
    } == {"policies"}
    assert evidence["catalogue"]["kind_counts"]["policies"] == 46
    assert evidence["catalogue"]["kind_counts"] == {
        **GENERATION_LOCK_CHARACTERIZATION_EVIDENCE["catalogue"]["kind_counts"],
        "policies": 46,
    }


def test_exact_catalogue_kind_population_is_frozen() -> None:
    assert CONTRACT["manifest_kind_counts"] == {
        "ROLE": 8,
        "SCHEMA": 1,
        "DOMAIN": 4,
        "ENUM": 19,
        "COMPOSITE": 9,
        "TABLE": 18,
        "CONSTRAINT": 81,
        "UNIQUE_INDEX": 4,
        "SUPPORT_FUNCTION": 1,
        "RLS_ENABLE": 18,
        "RLS_FORCE": 18,
        "RLS_POLICY": 46,
        "TYPE_OWNER": 32,
        "RELATION_OWNER": 18,
        "ENTRY_POINT": 9,
        "TRIGGER_FUNCTION": 14,
        "TRIGGER_DECLARATION": 14,
        "REVOKE": 43,
        "GRANT": 41,
    }


def test_type_owner_population_is_exact_one_to_one() -> None:
    typed = set(
        _manifest_ids("DOMAIN") + _manifest_ids("ENUM") + _manifest_ids("COMPOSITE")
    )
    owners = set(_manifest_ids("TYPE_OWNER"))
    assert len(typed) == len(owners) == 32
    assert typed == owners


def test_prerequisite_contract_is_exactly_four_empty_minimum_shapes() -> None:
    assert [table["name"] for table in PREREQUISITE["tables"]] == [
        "appointments",
        "appointment_command_idempotency",
        "appointment_audit_log",
        "diary_committed_events",
    ]
    assert all(
        "xmin" not in [column["name"] for column in table["columns"]]
        for table in PREREQUISITE["tables"]
    )
    assert set(PREREQUISITE["forbidden"]) >= {
        "rows",
        "patient_identifiers",
        "product_values",
        "triggers",
        "policies",
        "grants",
        "application_behavior",
    }


def test_prerequisite_sql_has_no_behavior_or_authority() -> None:
    sql = rehearsal.render_prerequisite_sql(PREREQUISITE).decode("utf-8")
    assert sql.count("CREATE TABLE public.") == 4
    assert "INSERT" not in sql
    assert "CREATE TRIGGER" not in sql
    assert "CREATE POLICY" not in sql
    assert "GRANT " not in sql
    assert "xmin" not in sql


def test_prerequisite_renderer_rejects_xmin_and_unknown_defaults() -> None:
    hostile = copy.deepcopy(PREREQUISITE)
    hostile["tables"][0]["columns"].append(
        {"name": "xmin", "type": "uuid", "nullable": False, "default_sql": None}
    )
    with pytest.raises(rehearsal.RehearsalFailure, match="prerequisite_columns"):
        rehearsal.render_prerequisite_sql(hostile)
    hostile = copy.deepcopy(PREREQUISITE)
    hostile["tables"][0]["columns"][0]["default_sql"] = "nextval('hostile')"
    with pytest.raises(rehearsal.RehearsalFailure, match="unsafe_default"):
        rehearsal.render_prerequisite_sql(hostile)


def test_windows_crlf_is_the_only_artifact_normalization() -> None:
    assert rehearsal._canonical_artifact(b"a\r\nb\r\n") == b"a\nb\n"  # noqa: SLF001
    with pytest.raises(rehearsal.RehearsalFailure, match="lone_carriage_return"):
        rehearsal._canonical_artifact(b"a\rb\n")  # noqa: SLF001


def test_artifact_contains_no_transaction_control_or_psql_meta_commands() -> None:
    text = rehearsal._outside_dollar_quoted(ARTIFACT.decode("utf-8"))  # noqa: SLF001
    assert rehearsal.FORBIDDEN_ARTIFACT_TX.search(text) is None
    assert rehearsal.FORBIDDEN_META.search(text) is None


def test_run_argv_is_networkless_no_pull_no_mount_and_bounded() -> None:
    argv = rehearsal.docker_argv(
        rehearsal.DockerOperation.RUN,
        docker=r"C:\Program Files\Docker\docker.exe",
        profile=CONTRACT["docker_profile"],
        name="emr4-cf-pg16-catalogue-0123456789abcdef",
        nonce="0" * 32,
    )
    rehearsal.assert_closed_argv(argv, rehearsal.DockerOperation.RUN)
    assert "--pull=never" in argv
    assert "--network=none" in argv
    assert "--tmpfs" in argv
    assert "--publish" not in argv and "--volume" not in argv and "-v" not in argv
    assert "POSTGRES_HOST_AUTH_METHOD=trust" not in argv
    assert argv[-1] == "postgres:16-bookworm"


def test_psql_file_argv_binds_atomic_stdin_mode() -> None:
    argv = rehearsal.docker_argv(
        rehearsal.DockerOperation.PSQL_FILE,
        docker=r"C:\Docker\docker.exe",
        profile=CONTRACT["docker_profile"],
        container_id="a" * 64,
        database="emr4_synthetic_rollback",
    )
    rehearsal.assert_closed_argv(argv, rehearsal.DockerOperation.PSQL_FILE)
    assert argv.count("--file=-") == 1
    assert argv.count("--single-transaction") == 1
    assert argv.count("ON_ERROR_STOP=1") == 1
    assert "--command" not in argv


def test_ready_sql_argv_is_noninteractive_and_connection_bounded() -> None:
    argv = rehearsal.docker_argv(
        rehearsal.DockerOperation.READY_SQL,
        docker=r"C:\Docker\docker.exe",
        profile=CONTRACT["docker_profile"],
        container_id="a" * 64,
    )
    rehearsal.assert_closed_argv(argv, rehearsal.DockerOperation.READY_SQL)
    assert argv[:4] == [
        r"C:\Docker\docker.exe",
        "exec",
        "a" * 64,
        "env",
    ]
    assert "-i" not in argv
    assert "PGCONNECT_TIMEOUT=2" in argv
    assert argv[-1] == "SELECT pg_catalog.current_setting('server_version_num');"
    assert "::" not in argv[-1]


@pytest.mark.parametrize(
    "token",
    [
        "pull",
        "build",
        "login",
        "compose",
        "ps",
        "images",
        "system",
        "prune",
        "ls",
        "list",
        "--privileged",
        "--network=host",
        "-p",
        "--publish",
        "--volume",
        "-v",
    ],
)
def test_hostile_docker_tokens_are_rejected(token: str) -> None:
    with pytest.raises(rehearsal.RehearsalFailure, match="forbidden_token"):
        rehearsal.assert_closed_argv(
            [r"C:\Docker\docker.exe", "container", "inspect", token],
            rehearsal.DockerOperation.ID_INSPECT,
        )


def test_globs_and_docker_socket_are_rejected() -> None:
    for value in ("*", "?", "/var/run/docker.sock"):
        with pytest.raises(rehearsal.RehearsalFailure, match="forbidden_path_or_glob"):
            rehearsal.assert_closed_argv(
                [r"C:\Docker\docker.exe", "container", "inspect", value],
                rehearsal.DockerOperation.ID_INSPECT,
            )


def test_pull_and_network_fallback_values_are_rejected() -> None:
    for token, code in (
        ("--pull=always", "forbidden_pull_policy"),
        ("--network=bridge", "forbidden_network_mode"),
    ):
        with pytest.raises(rehearsal.RehearsalFailure, match=code):
            rehearsal.assert_closed_argv(
                [r"C:\Docker\docker.exe", "run", token],
                rehearsal.DockerOperation.RUN,
            )


def test_subprocess_boundary_is_argv_only_and_shell_false() -> None:
    source = inspect.getsource(rehearsal._subprocess_runner)  # noqa: SLF001
    assert "shell=False" in source
    assert "CREATE_NO_WINDOW" in source
    assert "os.system" not in source
    assert "subprocess.run(" not in source
    assert ".communicate(" not in source
    assert "threading.Thread" in source


def test_subprocess_output_is_bounded_during_pipe_read(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeProcess:
        def __init__(self) -> None:
            self.stdin = None
            self.stdout = io.BytesIO(b"x" * 2049)
            self.stderr = io.BytesIO(b"")
            self.returncode = 0

        def wait(self, timeout: float | None = None) -> int:
            del timeout
            return self.returncode

        def kill(self) -> None:
            self.returncode = -9

        def poll(self) -> int:
            return self.returncode

    monkeypatch.setattr(
        rehearsal.subprocess, "Popen", lambda *args, **kwargs: FakeProcess()
    )
    with pytest.raises(rehearsal.RehearsalFailure, match="output_cap_exceeded"):
        rehearsal._subprocess_runner(  # noqa: SLF001
            [r"C:\Docker\docker.exe", "container", "inspect", "fixed"],
            None,
            1.0,
            1024,
        )


def test_absolute_execution_deadline_caps_calls_and_fails_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    observed: list[float] = []

    def runner(
        argv: list[str], stdin: bytes | None, timeout: float, cap: int
    ) -> rehearsal.ProcessResult:
        del argv, stdin, cap
        observed.append(timeout)
        return rehearsal.ProcessResult(0, b"", b"")

    monkeypatch.setattr(rehearsal.time, "monotonic", lambda: 10.0)
    bounded = rehearsal._with_total_deadline(runner, 12.5)  # noqa: SLF001
    bounded(["docker.exe"], None, 30, 1024)
    assert observed == [2.5]
    monkeypatch.setattr(rehearsal.time, "monotonic", lambda: 12.5)
    with pytest.raises(rehearsal.RehearsalFailure, match="total_timeout"):
        bounded(["docker.exe"], None, 30, 1024)


def test_postgres_readiness_requires_continuous_authenticated_sql() -> None:
    profile = copy.deepcopy(CONTRACT["docker_profile"])
    profile["startup_timeout_seconds"] = 5
    profile["readiness_stability_seconds"] = 0.5
    profile["readiness_probe_interval_seconds"] = 0.25
    current = 0.0
    ready_attempts = 0
    sql_attempts = 0
    calls: list[list[str]] = []
    observation: dict[str, Any] = {}

    def clock() -> float:
        return current

    def sleeper(delay: float) -> None:
        nonlocal current
        current += delay

    def runner(
        argv: list[str], stdin: bytes | None, timeout: float, cap: int
    ) -> rehearsal.ProcessResult:
        nonlocal ready_attempts, sql_attempts
        del stdin, timeout, cap
        calls.append(argv)
        if "pg_isready" in argv:
            ready_attempts += 1
            if ready_attempts == 2:
                return rehearsal.ProcessResult(1, b"", b"bootstrap handoff")
            return rehearsal.ProcessResult(0, b"accepting connections\n", b"")
        assert "current_setting('server_version_num')" in argv[-1]
        sql_attempts += 1
        return rehearsal.ProcessResult(0, b"160010\n", b"")

    rehearsal._wait_for_stable_postgres(  # noqa: SLF001
        runner,
        r"C:\Docker\docker.exe",
        "a" * 64,
        profile,
        observation=observation,
        clock=clock,
        sleeper=sleeper,
    )
    assert ready_attempts == 5
    assert sql_attempts == 4
    assert current == 1.0
    assert all("CREATE" not in " ".join(call) for call in calls)
    assert observation["status"] == "stable"
    assert observation["pg_isready_attempts"] == 5
    assert observation["pg_isready_successes"] == 4
    assert observation["sql_probe_attempts"] == 4
    assert observation["sql_probe_successes"] == 4
    assert observation["continuous_success_ms"] == 500
    assert observation["last_sql_failure_class"] == "none"


def test_postgres_readiness_translates_sql_probe_process_timeout() -> None:
    profile = copy.deepcopy(CONTRACT["docker_profile"])
    observation: dict[str, Any] = {}

    def runner(
        argv: list[str], stdin: bytes | None, timeout: float, cap: int
    ) -> rehearsal.ProcessResult:
        del stdin, timeout, cap
        if "pg_isready" in argv:
            return rehearsal.ProcessResult(0, b"accepting connections\n", b"")
        raise rehearsal.RehearsalFailure("process", "timeout", "synthetic")

    with pytest.raises(rehearsal.RehearsalFailure) as captured:
        rehearsal._wait_for_stable_postgres(  # noqa: SLF001
            runner,
            r"C:\Docker\docker.exe",
            "a" * 64,
            profile,
            observation=observation,
        )
    assert captured.value.stage == "postgres"
    assert captured.value.code == "readiness_probe_timeout"
    assert captured.value.detail == "ready_sql"
    assert observation["status"] == "probe_timeout"
    assert observation["timed_out_operation"] == "ready_sql"
    assert observation["pg_isready_attempts"] == 1
    assert observation["pg_isready_successes"] == 1
    assert observation["sql_probe_attempts"] == 1
    assert observation["sql_probe_successes"] == 0


@pytest.mark.parametrize(
    ("stderr", "expected"),
    [
        (b"ERROR: syntax error at or near cast", "sql_syntax"),
        (b'FATAL: role "synthetic" does not exist', "role_missing"),
        (b'FATAL: database "synthetic" does not exist', "database_missing"),
        (b"FATAL: password authentication failed", "password_authentication_failed"),
        (b"FATAL: Peer authentication failed", "peer_authentication_failed"),
        (b"fe_sendauth: no password supplied", "password_missing"),
        (b"connection refused", "connection_refused"),
        (b"No such file or directory", "socket_missing"),
        (b"server closed the connection unexpectedly", "server_handoff"),
        (b"executable file not found", "command_unavailable"),
        (b"authored synthetic unknown", "unclassified"),
    ],
)
def test_readiness_failure_classifier_is_closed(stderr: bytes, expected: str) -> None:
    assert rehearsal._readiness_failure_class(stderr) == expected  # noqa: SLF001


@pytest.mark.parametrize(
    ("stdout", "expected"),
    [
        (b"160000", True),
        (b"160010\n", True),
        (b"169999\r\n", True),
        (b"150010\n", False),
        (b"170001\n", False),
        (b"16000\n", False),
        (b"1600000\n", False),
        (b" 160010\n", False),
        (b"160010 \n", False),
        (b"160010\n\n", False),
        (b"160010\n160010\n", False),
        (b"server_version_num\n160010\n", False),
        (b"16a010\n", False),
        (b"", False),
    ],
)
def test_postgres_16_version_output_is_exact(stdout: bytes, expected: bool) -> None:
    assert rehearsal._is_postgres_16_version_output(stdout) is expected  # noqa: SLF001


def test_observed_sqlstates_are_closed_sorted_and_deduplicated() -> None:
    stderr = (
        b"psql:<stdin>:8: ERROR:  42P01: relation missing\n"
        b"DETAIL: raw authored synthetic detail\n"
        b"psql:<stdin>:9: FATAL:  28000: role rejected\n"
        b"psql:<stdin>:10: ERROR:  42P01: repeated\n"
        b"ERROR:  not-a-code: ignored\n"
    )
    assert rehearsal._observed_sqlstates(stderr) == ["28000", "42P01"]  # noqa: SLF001


def test_artifact_rejection_evidence_is_bounded_and_value_free() -> None:
    raw = (
        b"psql:<stdin>:500: ERROR:  42883: raw authored-synthetic detail\n"
        b"LINE 12: private authored SQL\n"
        b"POSITION: 4321\n"
        b"CONTEXT: compilation of PL/pgSQL function near line 7\n"
        b"LOCATION: private implementation detail\n"
    )
    bounded = rehearsal._bounded_psql_rejection(  # noqa: SLF001
        rehearsal.ProcessResult(3, b"ignored stdout", raw),
        max_error_line=1000,
        max_error_position=5000,
    )

    assert bounded == {
        "status": "rejected",
        "psql_exit": 3,
        "observed_sqlstates": ["42883"],
        "error_lines": [500],
        "statement_lines": [12],
        "positions": [4321],
        "context_lines": [7],
        "stderr": rehearsal._bounded_digest(raw),  # noqa: SLF001
    }
    rendered = json.dumps(bounded)
    assert "authored-synthetic detail" not in rendered
    assert "implementation detail" not in rendered


def test_artifact_rejection_line_evidence_is_closed_to_authored_input() -> None:
    raw = (
        b"psql:<stdin>:41: ERROR:  42601: bounded\n"
        b"psql:<stdin>:5000: ERROR:  42P01: outside authored input\n"
        b"psql:other.sql:20: ERROR:  42883: wrong source\n"
    )
    bounded = rehearsal._bounded_psql_rejection(  # noqa: SLF001
        rehearsal.ProcessResult(3, b"", raw),
        max_error_line=100,
        max_error_position=1000,
    )
    assert bounded["error_lines"] == [41]
    assert bounded["observed_sqlstates"] == ["42601", "42883", "42P01"]


def test_postgres_readiness_caps_each_probe_to_startup_deadline() -> None:
    profile = copy.deepcopy(CONTRACT["docker_profile"])
    profile["startup_timeout_seconds"] = 1
    profile["readiness_stability_seconds"] = 0
    current = 0.0
    observed_timeouts: list[float] = []

    def clock() -> float:
        return current

    def runner(
        argv: list[str], stdin: bytes | None, timeout: float, cap: int
    ) -> rehearsal.ProcessResult:
        nonlocal current
        del stdin, cap
        observed_timeouts.append(timeout)
        if "pg_isready" in argv:
            current = 0.75
            return rehearsal.ProcessResult(0, b"accepting connections\n", b"")
        return rehearsal.ProcessResult(0, b"160010\n", b"")

    rehearsal._wait_for_stable_postgres(  # noqa: SLF001
        runner,
        r"C:\Docker\docker.exe",
        "a" * 64,
        profile,
        clock=clock,
        sleeper=lambda _delay: None,
    )
    assert observed_timeouts == [1.0, 0.25]


def test_module_has_no_database_cloud_http_or_environment_input_import() -> None:
    tree = ast.parse(Path(rehearsal.__file__).read_text(encoding="utf-8"))
    imports = {
        alias.name.split(".", 1)[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    } | {
        node.module.split(".", 1)[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module
    }
    assert not imports.intersection(
        {
            "sqlalchemy",
            "psycopg",
            "requests",
            "httpx",
            "socket",
            "google",
            "boto3",
            "alembic",
        }
    )


def test_query_transport_sets_read_only_and_uses_file_stdin() -> None:
    captured: dict[str, Any] = {}

    def runner(
        argv: list[str], stdin: bytes | None, timeout: int, cap: int
    ) -> rehearsal.ProcessResult:
        captured.update(argv=argv, stdin=stdin, timeout=timeout, cap=cap)
        return rehearsal.ProcessResult(0, b"[]\n", b"")

    result = rehearsal._query_json(  # noqa: SLF001
        runner,
        r"C:\Docker\docker.exe",
        "a" * 64,
        "emr4_synthetic_success",
        CONTRACT["docker_profile"],
        "SELECT '[]'::json::text",
    )
    assert result == []
    assert captured["stdin"].startswith(b"SET TRANSACTION READ ONLY;\n")
    assert "--file=-" in captured["argv"]
    assert "--single-transaction" in captured["argv"]


def test_catalogue_projection_matches_every_frozen_population() -> None:
    result = rehearsal._assert_catalogue(  # noqa: SLF001
        _valid_facts(), MANIFEST, PREREQUISITE, CHARACTERIZATION_CONTRACT
    )
    assert result["kind_counts"] == {
        "roles": 8,
        "types": 32,
        "relations": 18,
        "columns": 52,
        "constraints": 81,
        "indexes": 4,
        "policies": 46,
        "functions": 24,
        "triggers": 14,
    }
    assert set(result["query_ids"]) == set(CONTRACT["catalogue_query_ids"])


def test_catalogue_queries_project_every_definition_and_authority_surface() -> None:
    types_sql = rehearsal.CATALOGUE_SQL["types"]
    columns_sql = rehearsal.CATALOGUE_SQL["columns"]
    constraints_sql = rehearsal.CATALOGUE_SQL["constraints"]
    policies_sql = rehearsal.CATALOGUE_SQL["policies"]
    functions_sql = rehearsal.CATALOGUE_SQL["functions"]
    triggers_sql = rehearsal.CATALOGUE_SQL["triggers"]
    assert all(
        field in types_sql
        for field in (
            "domain_base_type",
            "domain_not_null",
            "domain_default_sql",
            "domain_constraints",
            "enum_labels",
            "composite_attributes",
        )
    )
    assert "c.relkind = 'r'" in columns_sql
    assert "con.contype <> 't'" in constraints_sql
    assert "con.contype IN" not in constraints_sql
    assert "polroles" in policies_sql and "AS roles" in policies_sql
    assert "pg_get_function_identity_arguments" in functions_sql
    assert "pg_get_function_result" in functions_sql
    assert "proconfig" in functions_sql and "prosecdef" in functions_sql
    assert all(
        field in triggers_sql
        for field in (
            "timing",
            "level",
            "fires_insert",
            "fires_delete",
            "fires_update",
            "fires_truncate",
            "pg_get_triggerdef",
        )
    )


def test_characterization_cannot_pass_and_exact_digests_reject_definition_drift() -> (
    None
):
    facts = _valid_facts()
    characterized = rehearsal._assert_catalogue(  # noqa: SLF001
        facts, MANIFEST, PREREQUISITE, CHARACTERIZATION_CONTRACT
    )
    assert characterized["expectation_mode"] == "characterization_only"
    bound = copy.deepcopy(CONTRACT)
    bound["catalogue_expectation"] = {
        "mode": "exact_digest_bound",
        "expected_query_digests": {
            key: characterized["query_digests"][key]
            for key in CONTRACT["catalogue_query_ids"]
            if key not in {"server", "extensions"}
        },
    }
    exact = rehearsal._assert_catalogue(  # noqa: SLF001
        facts, MANIFEST, PREREQUISITE, bound
    )
    assert exact["expectation_mode"] == "exact_digest_bound"
    hostile = copy.deepcopy(facts)
    hostile["constraints"][0]["definition"] = "CHECK (false)"
    with pytest.raises(rehearsal.RehearsalFailure, match="exact_query_digest"):
        rehearsal._assert_catalogue(  # noqa: SLF001
            hostile, MANIFEST, PREREQUISITE, bound
        )


@pytest.mark.parametrize(
    "surface",
    [
        "schema_acl_text",
        "domain_definition",
        "relation_acl_text",
        "fabric_column",
        "index_definition",
        "policy_expression",
        "function_attribute",
        "trigger_definition",
        "relation_grant",
        "function_grant",
    ],
)
def test_exact_digest_binding_rejects_same_population_drift(surface: str) -> None:
    facts = _valid_facts()
    digests = {
        key: rehearsal._facts_digest(value)  # noqa: SLF001
        for key, value in facts.items()
        if key not in {"server", "extensions"}
    }
    bound = copy.deepcopy(CONTRACT)
    bound["catalogue_expectation"] = {
        "mode": "exact_digest_bound",
        "expected_query_digests": digests,
    }
    if surface == "schema_acl_text":
        facts["schema"][0]["acl"] = "hostile"
    elif surface == "domain_definition":
        facts["types"][0]["domain_constraints"] = [
            {"name": "same_name", "definition": "CHECK (false)"}
        ]
    elif surface == "relation_acl_text":
        facts["relations"][0]["acl"] = "hostile"
    elif surface == "fabric_column":
        fabric = next(
            row
            for row in facts["columns"]
            if row["relation"].startswith("emr4_context_fabric.")
        )
        fabric["default_sql"] = "hostile"
    elif surface == "index_definition":
        facts["indexes"][0]["definition"] = "CREATE UNIQUE INDEX same_name ON hostile"
    elif surface == "policy_expression":
        facts["policies"][0]["qualification"] = "false"
    elif surface == "function_attribute":
        facts["functions"][0]["security_definer"] = False
    elif surface == "trigger_definition":
        facts["triggers"][0]["definition"] = "CREATE TRIGGER same_name hostile"
    elif surface == "relation_grant":
        facts["relation_acl"].append(
            {
                "relation": "emr4_context_fabric.context_frame_generation",
                "grantee": "context_observer",
                "privilege": "SELECT",
                "grantable": False,
            }
        )
    elif surface == "function_grant":
        facts["function_acl"].append(
            {
                "function": "emr4_context_fabric.apply_durability_transition_v1",
                "grantee": "context_observer",
                "privilege": "EXECUTE",
                "grantable": False,
            }
        )
    with pytest.raises(rehearsal.RehearsalFailure, match="exact_query_digest"):
        rehearsal._assert_catalogue(  # noqa: SLF001
            facts, MANIFEST, PREREQUISITE, bound
        )


@pytest.mark.parametrize(
    ("field", "code"),
    [
        ("roles", "role_population"),
        ("types", "type_population"),
        ("relations", "relation_population"),
        ("constraints", "constraint_population"),
        ("indexes", "index_population"),
        ("policies", "policy_population"),
        ("functions", "function_population"),
        ("triggers", "trigger_population"),
        ("application_relations", "application_relation_population"),
    ],
)
def test_catalogue_population_mutations_fail_closed(field: str, code: str) -> None:
    facts = _valid_facts()
    facts[field] = facts[field][1:]
    with pytest.raises(rehearsal.RehearsalFailure, match=code):
        rehearsal._assert_catalogue(  # noqa: SLF001
            facts, MANIFEST, PREREQUISITE, CHARACTERIZATION_CONTRACT
        )


def test_constraint_population_diagnostic_is_value_free_and_exact() -> None:
    expected = rehearsal._expected_sets(MANIFEST)["CONSTRAINT"]  # noqa: SLF001
    rows = _valid_facts()["constraints"]
    removed = rows.pop()
    unexpected_identifier = "emr4_context_fabric.synthetic.unexpected_constraint"
    rows.append(
        {
            "identifier": unexpected_identifier,
            "constraint_kind": "z",
            "deferrable": False,
            "initially_deferred": False,
            "definition": "private definition",
        }
    )

    diagnostic = rehearsal._constraint_population_diagnostic(  # noqa: SLF001
        rows, expected
    )
    assert diagnostic["expected_count"] == len(expected)
    assert diagnostic["actual_count"] == len(expected)
    assert diagnostic["missing_count"] == 1
    assert diagnostic["unexpected_count"] == 1
    assert diagnostic["missing_identifiers_sha256"] == rehearsal._facts_digest(  # noqa: SLF001
        [removed["identifier"]]
    )
    assert diagnostic["unexpected_identifiers_sha256"] == rehearsal._facts_digest(  # noqa: SLF001
        [unexpected_identifier]
    )
    assert set(diagnostic["expected_kind_counts"]) == {"c", "f", "other", "p", "u"}
    assert set(diagnostic["actual_kind_counts"]) == {"c", "f", "other", "p", "u"}
    assert diagnostic["expected_kind_counts"]["other"] == 0
    assert diagnostic["actual_kind_counts"]["other"] == 1
    rendered = json.dumps(diagnostic)
    assert removed["identifier"] not in rendered
    assert unexpected_identifier not in rendered
    assert "private definition" not in rendered


def test_function_owner_exception_is_exact_and_position_closed() -> None:
    facts = _valid_facts()
    admission = next(
        row
        for row in facts["functions"]
        if row["name"] == "emr4_context_fabric.admit_proofread_observation_v1"
    )
    assert admission["owner"] == "context_admission_receiver"
    rehearsal._assert_catalogue(  # noqa: SLF001
        facts, MANIFEST, PREREQUISITE, CHARACTERIZATION_CONTRACT
    )

    admission["owner"] = "context_schema_owner"
    with pytest.raises(rehearsal.RehearsalFailure, match="function_attributes"):
        rehearsal._assert_catalogue(  # noqa: SLF001
            facts, MANIFEST, PREREQUISITE, CHARACTERIZATION_CONTRACT
        )

    facts = _valid_facts()
    ordinary = next(
        row
        for row in facts["functions"]
        if row["name"] != "emr4_context_fabric.admit_proofread_observation_v1"
    )
    ordinary["owner"] = "context_admission_receiver"
    with pytest.raises(rehearsal.RehearsalFailure, match="function_attributes"):
        rehearsal._assert_catalogue(  # noqa: SLF001
            facts, MANIFEST, PREREQUISITE, CHARACTERIZATION_CONTRACT
        )


def test_public_acl_and_runtime_schema_create_fail_closed() -> None:
    facts = _valid_facts()
    facts["schema_acl"] = [
        {"grantee": "PUBLIC", "privilege": "USAGE", "grantable": False}
    ]
    with pytest.raises(rehearsal.RehearsalFailure, match="public_acl"):
        rehearsal._assert_catalogue(  # noqa: SLF001
            facts, MANIFEST, PREREQUISITE, CHARACTERIZATION_CONTRACT
        )
    facts = _valid_facts()
    facts["schema_acl"] = [
        {"grantee": "context_producer", "privilege": "CREATE", "grantable": False}
    ]
    with pytest.raises(rehearsal.RehearsalFailure, match="runtime_schema_create_acl"):
        rehearsal._assert_catalogue(  # noqa: SLF001
            facts, MANIFEST, PREREQUISITE, CHARACTERIZATION_CONTRACT
        )


def test_application_owner_rows_and_column_shape_fail_closed() -> None:
    for mutation in ("owner", "rows", "columns"):
        facts = _valid_facts()
        if mutation == "owner":
            facts["application_relations"][0]["owner"] = "context_schema_owner"
        elif mutation == "rows":
            facts["application_relations"][0]["row_count"] = 1
        else:
            facts["columns"] = facts["columns"][1:]
        with pytest.raises(rehearsal.RehearsalFailure):
            rehearsal._assert_catalogue(  # noqa: SLF001
                facts, MANIFEST, PREREQUISITE, CHARACTERIZATION_CONTRACT
            )


def _owned_inspect() -> dict[str, Any]:
    profile = CONTRACT["docker_profile"]
    return {
        "Id": "a" * 64,
        "Name": "/emr4-cf-pg16-catalogue-0123456789abcdef",
        "Image": "sha256:" + "b" * 64,
        "Config": {
            "Image": profile["image_reference"],
            "Env": [
                f"POSTGRES_USER={profile['postgres_user']}",
                f"POSTGRES_PASSWORD={profile['postgres_password']}",
                f"POSTGRES_DB={profile['postgres_database']}",
                f"PGDATA={profile['pgdata']}",
            ],
            "Labels": {
                "com.emr4.harness": profile["ownership_labels"]["com.emr4.harness"],
                "com.emr4.cleanup-nonce": "0" * 32,
            },
        },
        "HostConfig": {
            "NetworkMode": "none",
            "Binds": None,
            "PortBindings": {},
            "Privileged": False,
            "Memory": 768 * 1024 * 1024,
            "NanoCpus": 1_000_000_000,
            "PidsLimit": 192,
            "RestartPolicy": {"Name": "no"},
            "Tmpfs": {"/var/lib/postgresql/data": "rw,noexec,nosuid,size=536870912"},
        },
        "Mounts": [{"Type": "tmpfs", "Destination": "/var/lib/postgresql/data"}],
    }


def test_cleanup_ownership_requires_every_exact_fact() -> None:
    profile = CONTRACT["docker_profile"]
    kwargs = {
        "container_id": "a" * 64,
        "name": "emr4-cf-pg16-catalogue-0123456789abcdef",
        "nonce": "0" * 32,
        "image_id": "sha256:" + "b" * 64,
        "profile": profile,
    }
    assert rehearsal._container_owned(_owned_inspect(), **kwargs)  # noqa: SLF001
    for mutate in (
        "id",
        "name",
        "label",
        "image",
        "network",
        "mount",
        "privileged",
        "memory",
        "cpu",
        "pids",
        "tmpfs",
        "port",
        "environment",
        "unexpected_mount",
    ):
        payload = _owned_inspect()
        if mutate == "id":
            payload["Id"] = "c" * 64
        elif mutate == "name":
            payload["Name"] = "/other"
        elif mutate == "label":
            payload["Config"]["Labels"]["com.emr4.cleanup-nonce"] = "other"
        elif mutate == "image":
            payload["Image"] = "sha256:" + "c" * 64
        elif mutate == "network":
            payload["HostConfig"]["NetworkMode"] = "bridge"
        elif mutate == "mount":
            payload["Mounts"].append({"Type": "bind", "Destination": "/workspace"})
        elif mutate == "privileged":
            payload["HostConfig"]["Privileged"] = True
        elif mutate == "memory":
            payload["HostConfig"]["Memory"] = 0
        elif mutate == "cpu":
            payload["HostConfig"]["NanoCpus"] = 0
        elif mutate == "pids":
            payload["HostConfig"]["PidsLimit"] = 0
        elif mutate == "tmpfs":
            payload["HostConfig"]["Tmpfs"] = {
                "/var/lib/postgresql/data": "rw,size=536870912"
            }
        elif mutate == "port":
            payload["HostConfig"]["PortBindings"] = {"5432/tcp": [{"HostPort": "5432"}]}
        elif mutate == "environment":
            payload["Config"]["Env"] = []
        elif mutate == "unexpected_mount":
            payload["Mounts"] = [{"Type": "npipe", "Destination": "/other"}]
        assert not rehearsal._container_owned(payload, **kwargs)  # noqa: SLF001
    for malformed in (
        {"Config": None, "HostConfig": {}, "Mounts": []},
        {"Config": {}, "HostConfig": None, "Mounts": []},
        {"Config": {}, "HostConfig": {}, "Mounts": None},
        {"Config": {"Labels": []}, "HostConfig": {}, "Mounts": []},
    ):
        assert not rehearsal._container_owned(malformed, **kwargs)  # noqa: SLF001


def test_cleanup_ownership_accepts_docker_desktop_empty_mounts_projection() -> None:
    profile = CONTRACT["docker_profile"]
    payload = _owned_inspect()
    payload["Mounts"] = []
    assert rehearsal._container_owned(  # noqa: SLF001
        payload,
        container_id="a" * 64,
        name="emr4-cf-pg16-catalogue-0123456789abcdef",
        nonce="0" * 32,
        image_id="sha256:" + "b" * 64,
        profile=profile,
    )


def test_exact_absence_requires_documented_no_such_object() -> None:
    assert rehearsal._is_exact_absence(  # noqa: SLF001
        rehearsal.ProcessResult(1, b"", b"Error: No such object: abc")
    )
    assert not rehearsal._is_exact_absence(  # noqa: SLF001
        rehearsal.ProcessResult(1, b"", b"daemon unavailable")
    )
    assert not rehearsal._is_exact_absence(rehearsal.ProcessResult(0, b"{}", b""))  # noqa: SLF001
    assert rehearsal._is_exact_absence(  # noqa: SLF001
        rehearsal.ProcessResult(
            1,
            b"",
            b"Error response from daemon: No such container: exact-owned-name",
        )
    )


def test_exact_owned_cleanup_uses_only_captured_id() -> None:
    calls: list[list[str]] = []
    responses = [
        rehearsal.ProcessResult(0, json.dumps(_owned_inspect()).encode("utf-8"), b""),
        rehearsal.ProcessResult(0, b"a" * 64 + b"\n", b""),
        rehearsal.ProcessResult(1, b"", b"Error: No such object: " + b"a" * 64),
    ]

    def runner(
        argv: list[str], stdin: bytes | None, timeout: int, cap: int
    ) -> rehearsal.ProcessResult:
        del stdin, timeout, cap
        calls.append(argv)
        return responses.pop(0)

    result = rehearsal._cleanup(  # noqa: SLF001
        runner,
        r"C:\Docker\docker.exe",
        "a" * 64,
        "emr4-cf-pg16-catalogue-0123456789abcdef",
        "0" * 32,
        "sha256:" + "b" * 64,
        CONTRACT["docker_profile"],
    )
    assert result["status"] == "cleanup_verified"
    assert calls[1] == [
        r"C:\Docker\docker.exe",
        "container",
        "rm",
        "--force",
        "a" * 64,
    ]
    assert all("prune" not in call and "ls" not in call for call in calls)


def test_environment_stop_never_calls_docker_or_writes_evidence(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(rehearsal.shutil, "which", lambda _name: None)

    def forbidden_runner(
        argv: list[str], stdin: bytes | None, timeout: int, cap: int
    ) -> rehearsal.ProcessResult:
        del argv, stdin, timeout, cap
        raise AssertionError("runner must not be reached")

    evidence = rehearsal.run_rehearsal(runner=forbidden_runner)
    assert evidence["result"] == "environment_unavailable"
    assert evidence["lifecycle"] == ["parent_verified"]
    assert evidence["cleanup"]["status"] == "not_needed"
    assert evidence["environment"]["failure"]["code"] == "docker_client_missing"
    Draft202012Validator(EVIDENCE_SCHEMA).validate(evidence)


def test_failed_exact_rerun_cannot_overwrite_last_accepted_evidence(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    accepted = tmp_path / "accepted.json"
    characterized = tmp_path / "characterized.json"
    failed = tmp_path / "failed.json"
    accepted.write_text("accepted-before\n", encoding="utf-8")
    characterized.write_text("characterized-before\n", encoding="utf-8")
    failed.write_text("failed-before\n", encoding="utf-8")
    monkeypatch.setattr(rehearsal, "EVIDENCE_PATH", accepted)
    monkeypatch.setattr(rehearsal, "CHARACTERIZATION_EVIDENCE_PATH", characterized)
    monkeypatch.setattr(rehearsal, "FAILURE_EVIDENCE_PATH", failed)

    failed_target = rehearsal.write_evidence({"result": "rehearsal_failed"})
    assert failed_target == failed
    assert accepted.read_text(encoding="utf-8") == "accepted-before\n"
    assert characterized.read_text(encoding="utf-8") == "characterized-before\n"
    assert json.loads(failed.read_text(encoding="utf-8")) == {
        "result": "rehearsal_failed"
    }

    characterized_target = rehearsal.write_evidence(
        {"result": "catalogue_characterization_required"}
    )
    assert characterized_target == characterized
    assert accepted.read_text(encoding="utf-8") == "accepted-before\n"
    assert json.loads(characterized.read_text(encoding="utf-8")) == {
        "result": "catalogue_characterization_required"
    }
    assert json.loads(failed.read_text(encoding="utf-8")) == {
        "result": "rehearsal_failed"
    }

    passed_target = rehearsal.write_evidence({"result": rehearsal.PASS_RESULT})
    assert passed_target == accepted
    assert json.loads(accepted.read_text(encoding="utf-8")) == {
        "result": rehearsal.PASS_RESULT
    }


def test_evidence_result_classes_have_distinct_repository_targets() -> None:
    assert (
        len(
            {
                rehearsal.EVIDENCE_PATH.resolve(),
                rehearsal.CHARACTERIZATION_EVIDENCE_PATH.resolve(),
                rehearsal.FAILURE_EVIDENCE_PATH.resolve(),
            }
        )
        == 3
    )


def test_evidence_schema_accepts_bounded_environment_stop() -> None:
    payload = {
        "schema_version": "emr4.disposable-postgresql-durability-rehearsal-evidence.v1",
        "result": "environment_unavailable",
        "evidence_mode": rehearsal.EVIDENCE_MODE,
        "attempt_id": "authored-synthetic",
        "parent": {},
        "environment": {
            "failure": {"stage": "environment", "code": "docker_client_missing"}
        },
        "lifecycle": ["parent_verified"],
        "rollback": {"status": "not_started"},
        "catalogue": {"status": "not_started"},
        "cleanup": {"status": "not_needed"},
        "claim_boundary": rehearsal.CLAIM_BOUNDARY,
    }
    Draft202012Validator(EVIDENCE_SCHEMA).validate(payload)


def test_main_rejects_all_caller_selected_arguments(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(rehearsal.sys, "argv", ["harness", "--image", "other"])
    assert rehearsal.main() == 2
