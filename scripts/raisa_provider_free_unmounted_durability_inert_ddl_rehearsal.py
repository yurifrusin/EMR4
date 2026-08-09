"""Provider-free unmounted durability inert DDL rehearsal renderer.

This module deterministically lowers the two immutable accepted durability
contracts into one repository-local PostgreSQL 16 inert SQL evidence artifact
plus a closed typed render manifest.  It never executes, applies, parses or
connects the output and never contacts a database, provider, product, network
or external parser.

Imports are limited to the Python standard library plus the accepted pure body
builder surfaces.  There is deliberately no subprocess, socket, http, database,
SQLAlchemy/psycopg, Alembic, provider or environment-selected output surface.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

if __package__ in (None, ""):  # pragma: no cover - script entry point
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.raisa_provider_free_unmounted_durability_function_trigger_body_architecture_builder import (
    APPLICATION_COLUMNS,
    FABRIC,
    PARENT_DIGEST,
    PG,
    build_catalogue,
    build_effective_roles,
    build_signatures,
    build_trigger_declarations,
)
import scripts.raisa_provider_free_unmounted_durability_function_trigger_body_architecture_builder as body_dsl

ROOT = Path(__file__).resolve().parents[1]
STRUCTURAL_DIR = ROOT / (
    "orchestration/continuity/raisa-provider-free-unmounted-durability-"
    "migration-transaction-architecture"
)
BODY_DIR = ROOT / (
    "orchestration/continuity/raisa-provider-free-unmounted-durability-"
    "function-trigger-body-architecture"
)
OUTPUT_DIR = ROOT / (
    "orchestration/continuity/raisa-provider-free-unmounted-durability-"
    "inert-ddl-rehearsal"
)

STRUCTURAL_PATH = STRUCTURAL_DIR / "migration-transaction-architecture-contract.json"
STRUCTURAL_SCHEMA_PATH = (
    STRUCTURAL_DIR / "migration-transaction-architecture-contract.schema.json"
)
BODY_PATH = BODY_DIR / "function-trigger-body-architecture-contract.json"
BODY_SCHEMA_PATH = BODY_DIR / "function-trigger-body-architecture-contract.schema.json"

LOWERING_CONTRACT_PATH = OUTPUT_DIR / "lowering-contract.json"
LOWERING_SCHEMA_PATH = OUTPUT_DIR / "lowering-contract.schema.json"
SQL_INERT_PATH = OUTPUT_DIR / "durability-schema.sql.inert"
MANIFEST_PATH = OUTPUT_DIR / "render-manifest.json"

BODY_DIGEST = "sha256:6c4230c2d6c245087a789fbabb058dce4f6a42b747429ec8256ef0d994e5ad1b"
STRUCTURAL_SOURCE_HEAD = "338c30ddb01561ce97a4b9837317e771b555c221"
BODY_SOURCE_HEAD = "987f64a9f68c8dec2b99d5d39aa74e28411a82fa"

SCHEMA_NAME = "emr4_context_fabric"
HEADER_LINE = (
    "-- durability-schema.sql.inert -- inert evidence artifact; never execute or apply"
)
UNIT_SEPARATOR = chr(31)
TERMINAL_NEWLINE = "\n"

APPOINTMENT_GUARD_ID = FABRIC + "cf_guard_appointment_update_v1"
APPOINTMENT_GUARD_TRIGGER_ID = "trg_cf_appointment_guard"
CLAIM = "public.appointment_command_idempotency"
APPOINTMENT = "public.appointments"
EVENT = "public.diary_committed_events"
BINDING = FABRIC + "context_service_practice_binding"
OUTBOX = FABRIC + "diary_context_observation_outbox_v1"
DIGEST_DOMAIN_NAME = "digest_sha256"

RECOVERY_SPEC: dict[str, Any] = {
    "id": "postgresql_16_representability_recovery_v1",
    "immutable_body_parent_sha256": BODY_DIGEST,
    "effective_population": {
        "entry_points": 9,
        "trigger_functions": 14,
        "trigger_declarations": 14,
        "programs": 23,
    },
    "operation_order": [
        "RELAX_DIGEST_DOMAIN_NULLABILITY",
        "ADD_APPOINTMENT_GUARD_SIGNATURE",
        "ADD_APPOINTMENT_GUARD_PROGRAM",
        "ADD_APPOINTMENT_GUARD_DECLARATION",
        "ADD_APPOINTMENT_PRODUCER_APPLICABILITY",
        "RESELECT_BEFORE_TRIGGER_OLD_XMIN",
        "REMOVE_DEFERRED_APPOINTMENT_OLD_XMIN",
        "REMOVE_DEFERRED_EVENT_DELETE_OLD_XMIN",
        "REMOVE_DEFERRED_OUTBOX_DELETE_OLD_XMIN",
    ],
    "operations": [
        {
            "id": "RELAX_DIGEST_DOMAIN_NULLABILITY",
            "affected_ids": [FABRIC + DIGEST_DOMAIN_NAME],
            "old_fragment_sha256": "sha256:5f00a27475a8b38a8168fda1a91f371c25c5666fd7028ef334873b3a7f24db89",
            "new_fragment_sha256": "sha256:7c5c7e3bee71b953863b744de868b797439498fbea56b6e8f13ac969fd598e6c",
        },
        {
            "id": "ADD_APPOINTMENT_GUARD_SIGNATURE",
            "affected_ids": [APPOINTMENT_GUARD_ID],
            "old_fragment_sha256": "sha256:74234e98afe7498fb5daf1f36ac2d78acc339464f950703b8c019892f982b90b",
            "new_fragment_sha256": "sha256:07f2b92081c159d265f57b9e24369151eecb341c22018698dd0853d5aa6591e6",
        },
        {
            "id": "ADD_APPOINTMENT_GUARD_PROGRAM",
            "affected_ids": [APPOINTMENT_GUARD_ID],
            "old_fragment_sha256": "sha256:74234e98afe7498fb5daf1f36ac2d78acc339464f950703b8c019892f982b90b",
            "new_fragment_sha256": "sha256:0a71713cc088aed4cde4f4b65b086bfba4115d5dcca6096db614e192d2e47d40",
        },
        {
            "id": "ADD_APPOINTMENT_GUARD_DECLARATION",
            "affected_ids": [APPOINTMENT_GUARD_TRIGGER_ID],
            "old_fragment_sha256": "sha256:74234e98afe7498fb5daf1f36ac2d78acc339464f950703b8c019892f982b90b",
            "new_fragment_sha256": "sha256:35aa5965d38becd6b83d2920b479411ae6a2c7b7e96971d9c9c3d20f9574a2bf",
        },
        {
            "id": "ADD_APPOINTMENT_PRODUCER_APPLICABILITY",
            "affected_ids": [
                APPOINTMENT_GUARD_ID + ".update.applicability",
                FABRIC + "cf_fence_appointment_update_v1.update.applicability",
            ],
            "old_fragment_sha256": "sha256:e4c2ddc0124055547cc36e8052814d397f8f2a0cb713abfa185496e052e2b790",
            "new_fragment_sha256": "sha256:ba2a1310e5e1ff91137c31136810aea0eb4dd88cc9634ce7d5e1f4b8ef0a33c1",
        },
        {
            "id": "RESELECT_BEFORE_TRIGGER_OLD_XMIN",
            "affected_ids": [
                FABRIC + "cf_guard_claim_v1",
                APPOINTMENT_GUARD_ID,
                FABRIC + "cf_guard_event_v1",
                FABRIC + "cf_guard_outbox_v1",
            ],
            "sites": [
                {
                    "function": FABRIC + "cf_guard_claim_v1",
                    "source_node_id": FABRIC + "cf_guard_claim_v1.update.provenance",
                    "effective_node_id": FABRIC + "cf_guard_claim_v1.update.provenance",
                    "reselect_node_id": FABRIC + "cf_guard_claim_v1.recovery.old-xmin",
                    "old_expression_sha256": "sha256:08fd97bb6b7b9996026ecc8ba334ca0d55ec1bbeeac4f88062ff87d20a51cda8",
                    "new_expression_sha256": "sha256:941586a95cdd549b1a7f0b6b75c041b426ae22dc382f1b9a24d02b52dda4ad37",
                    "new_reselect_sha256": "sha256:bc00c1f9a5c8eecd30a41dd993c82c09b6ec2cadbf345670efca986127042d60",
                },
                {
                    "function": APPOINTMENT_GUARD_ID,
                    "source_function": FABRIC + "cf_fence_appointment_update_v1",
                    "source_node_id": FABRIC
                    + "cf_fence_appointment_update_v1.update.second",
                    "effective_node_id": APPOINTMENT_GUARD_ID + ".update.second",
                    "reselect_node_id": APPOINTMENT_GUARD_ID + ".update.old-xmin",
                    "old_expression_sha256": "sha256:d97a5294f62ca12ef02025de4f592201a98d3f8c2542b212bae6d647d992f3f0",
                    "new_expression_sha256": "sha256:56d5bc359c78cefe48a03967a73075cda836a4bdc7395acd678542a6677b74d4",
                    "new_reselect_sha256": "sha256:22bb81f4fca7a939006244195d0a3403ed0a395bdd9c3e799f3e82b7d7ee248c",
                },
                {
                    "function": FABRIC + "cf_guard_event_v1",
                    "source_node_id": FABRIC + "cf_guard_event_v1.delete.current",
                    "effective_node_id": FABRIC + "cf_guard_event_v1.delete.current",
                    "reselect_node_id": FABRIC + "cf_guard_event_v1.recovery.old-xmin",
                    "old_expression_sha256": "sha256:8343e25ea71d2f2263b638fb812116883c73ffac1a0f81f171902b05afa81847",
                    "new_expression_sha256": "sha256:8cf18bb1b0eeaae8b9ba12187bd50b0601e8b27d6a65a80c5af9f64933b08622",
                    "new_reselect_sha256": "sha256:c1db20b40e5e4f6750eafe4dd92ababa811a86c2f4c9630beac0ba07a46aa6b6",
                },
                {
                    "function": FABRIC + "cf_guard_outbox_v1",
                    "source_node_id": FABRIC + "cf_guard_outbox_v1.delete.authorized",
                    "effective_node_id": FABRIC
                    + "cf_guard_outbox_v1.delete.authorized",
                    "reselect_node_id": FABRIC + "cf_guard_outbox_v1.recovery.old-xmin",
                    "old_expression_sha256": "sha256:74b4174d9d93aa858c0721ef8bb993f182c623ce25040c236278aa89674bba28",
                    "new_expression_sha256": "sha256:07fa6a39ca79c58d49dc1ed68d3e938e291154a7d61c610a712f262a5660755b",
                    "new_reselect_sha256": "sha256:d6b228f826a81b20003c5aa71f4c4d028b3c930d23dae6ad644bc44f51307902",
                },
            ],
            "old_fragment_sha256": "sha256:e649dbd6f6ea492b364e56f46fcb450a18b267bcb9a708754608a1b03dfba629",
            "new_fragment_sha256": "sha256:6ccd3839cd4ddc205890c768069d77852e2c3c6bd9c6f31fb01ec0439520c401",
        },
        {
            "id": "REMOVE_DEFERRED_APPOINTMENT_OLD_XMIN",
            "affected_ids": [
                FABRIC + "cf_fence_appointment_update_v1",
                FABRIC + "cf_fence_appointment_update_v1.update.second",
            ],
            "old_fragment_sha256": "sha256:39f4c39f8454896e9c6c1104a3155e803bb390b9de0cf7afccdbef93adfcbd09",
            "new_fragment_sha256": "sha256:74234e98afe7498fb5daf1f36ac2d78acc339464f950703b8c019892f982b90b",
            "paired_guard_dependency_sha256": "sha256:dd33cc1c3d0c405096216e535e4ee69266f4405e6e0895bd38db03eb0283214b",
        },
        {
            "id": "REMOVE_DEFERRED_EVENT_DELETE_OLD_XMIN",
            "affected_ids": [
                FABRIC + "cf_fence_event_v1",
                FABRIC + "cf_fence_event_v1.delete.current",
            ],
            "old_fragment_sha256": "sha256:961274faab2a843556892479e5d835ab1e00c0f0eacafb10dceeb6e43fcae477",
            "new_fragment_sha256": "sha256:74234e98afe7498fb5daf1f36ac2d78acc339464f950703b8c019892f982b90b",
            "paired_guard_dependency_sha256": "sha256:30138f0dcf56d193caefbbd99bbef3a3f93f7430b517ee6e6bcccf6ff7df5a2f",
        },
        {
            "id": "REMOVE_DEFERRED_OUTBOX_DELETE_OLD_XMIN",
            "affected_ids": [
                FABRIC + "cf_fence_outbox_v1",
                FABRIC + "cf_fence_outbox_v1.delete.authorized",
            ],
            "old_fragment_sha256": "sha256:18406df993fe586ff09922a61e66def24aa4180dbb16256b1851b149d2c174fa",
            "new_fragment_sha256": "sha256:1acea17412e0736832a7721bda825b255df8841b8bdaf0e0c97c11071340b317",
            "paired_guard_dependency_sha256": "sha256:95a448af9d0c77c2dbbaef75d09dde878163511996dba501d5513b33a8b10943",
        },
    ],
    "keyed_xmin_reselects": [
        {
            "function": FABRIC + "cf_guard_claim_v1",
            "relation": CLAIM,
            "key_columns": ["practice_id", "id"],
            "timing": "BEFORE",
            "cardinality_failure": {"id": "F_CARDINALITY", "sqlstate": "CF004"},
        },
        {
            "function": APPOINTMENT_GUARD_ID,
            "relation": APPOINTMENT,
            "key_columns": ["practice_id", "id"],
            "timing": "BEFORE",
            "cardinality_failure": {"id": "F_CARDINALITY", "sqlstate": "CF004"},
        },
        {
            "function": FABRIC + "cf_guard_event_v1",
            "relation": EVENT,
            "key_columns": ["practice_id", "id"],
            "timing": "BEFORE",
            "cardinality_failure": {"id": "F_CARDINALITY", "sqlstate": "CF004"},
        },
        {
            "function": FABRIC + "cf_guard_outbox_v1",
            "relation": OUTBOX,
            "key_columns": [
                "practice_id",
                "source_contract_id",
                "stream_id",
                "stream_epoch",
                "transaction_position",
            ],
            "timing": "BEFORE",
            "cardinality_failure": {"id": "F_CARDINALITY", "sqlstate": "CF004"},
        },
    ],
    "paired_guard_dependencies": [
        {
            "fence": FABRIC + "cf_fence_appointment_update_v1",
            "guard": APPOINTMENT_GUARD_ID,
            "discharged_fact": "old_row_xmin_not_current_xid_before_update",
        },
        {
            "fence": FABRIC + "cf_fence_event_v1",
            "guard": FABRIC + "cf_guard_event_v1",
            "discharged_fact": "deleted_event_xmin_not_current_xid",
        },
        {
            "fence": FABRIC + "cf_fence_outbox_v1",
            "guard": FABRIC + "cf_guard_outbox_v1",
            "discharged_fact": "deleted_outbox_xmin_not_current_xid",
        },
    ],
    "appointment_applicability": {
        "source": "single_complete_set_read",
        "zero": "inert",
        "one": "proof_required",
        "multiple": {"failure_id": "F_CARDINALITY", "sqlstate": "CF004"},
        "arbitrary_stream_selection": False,
    },
    "database_contact": False,
    "executable_ddl": False,
}


def sha256_hex(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _json_seal(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"))
    return "sha256:" + sha256_hex(encoded.encode("utf-8"))


def canonical_digest(value: dict[str, Any], field: str = "contract_sha256") -> str:
    payload = copy.deepcopy(value)
    payload.pop(field, None)
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_utf8_lf(path: Path, text: str) -> None:
    if not text.endswith("\n"):
        text = text + "\n"
    path.write_text(text, encoding="utf-8", newline="\n")


def _sha256_path(path: Path) -> str:
    return "sha256:" + sha256_hex(path.read_bytes())


APPLICATION_RELATIONS = frozenset(
    name.removeprefix("public.") for name in APPLICATION_COLUMNS
)


def _fabric(relation: str) -> str:
    if relation.startswith("public.") or relation.startswith(FABRIC):
        return relation
    if relation in APPLICATION_RELATIONS:
        return "public." + relation
    return FABRIC + relation


def _unqualified(identifier: str) -> str:
    return identifier.rsplit(".", 1)[-1]


def _ident(identifier: str) -> str:
    """Deterministic PostgreSQL identifier emission (unquoted, validated)."""
    if not re.fullmatch(r"[a-zA-Z_][a-zA-Z0-9_]*", identifier):
        return '"' + identifier.replace('"', '""') + '"'
    return identifier


PLPGSQL_SYMBOL_ALIASES = {
    # PRIMARY is accepted as a PL/pgSQL declaration name but is reserved when
    # the embedded SQL parser reaches a qualified record-field reference.
    # Preserve the accepted logical contract name and lower only its physical
    # function-local spelling.
    "primary": "cf_primary_admission",
}


def _symbol_ident(identifier: str) -> str:
    """Emit one physical PL/pgSQL symbol without changing logical contract IDs."""
    return _ident(PLPGSQL_SYMBOL_ALIASES.get(identifier, identifier))


def _type_sql(type_name: str) -> str:
    """Normalize a qualified type to PostgreSQL SQL type text."""
    physical_catalog_types = {
        "pg_catalog.boolean": "pg_catalog.bool",
        "pg_catalog.bigint": "pg_catalog.int8",
        "pg_catalog.integer": "pg_catalog.int4",
        "pg_catalog.smallint": "pg_catalog.int2",
    }
    if type_name == "pg_catalog.trigger":
        return "trigger"
    if type_name.endswith("[]"):
        base = _type_sql(type_name[:-2])
        return base + "[]"
    if type_name.startswith("pg_catalog."):
        return physical_catalog_types.get(type_name, type_name)
    if type_name.startswith("public."):
        return type_name
    if type_name.startswith(FABRIC):
        return type_name
    builtins = {
        "boolean",
        "bigint",
        "name",
        "smallint",
        "timestamptz",
        "uuid",
        "text",
        "integer",
        "jsonb",
        "xid",
        "trigger",
    }
    if type_name in builtins:
        qualified = PG + type_name
        return physical_catalog_types.get(qualified, qualified)
    if type_name in APPLICATION_RELATIONS:
        return "public." + type_name
    return FABRIC + type_name


# ---------------------------------------------------------------------------
# Parent binding and effective catalogue derivation
# ---------------------------------------------------------------------------

STREAM_RELATIONS = {
    "context_service_practice_binding",
    "diary_context_aggregate_aliases_v1",
    "context_retention_policy",
}

REWRITE_COORDINATES_RELATIONS = {
    "diary_context_aggregate_aliases_v1",
    "context_retention_policy",
    "diary_context_observation_outbox_v1",
}


def load_and_bind_parents() -> dict[str, Any]:
    """Read both immutable parent contracts, verifying canonical hashes."""
    structural = _read_json(STRUCTURAL_PATH)
    body = _read_json(BODY_PATH)
    if structural["contract_sha256"] != PARENT_DIGEST:
        raise ValueError("structural parent hash mismatch")
    if body["contract_sha256"] != BODY_DIGEST:
        raise ValueError("body parent hash mismatch")
    if body["parent_binding"]["contract_sha256"] != PARENT_DIGEST:
        raise ValueError("body parent binding hash mismatch")
    if body["parent_binding"]["path"] != (
        "orchestration/continuity/raisa-provider-free-unmounted-durability-"
        "migration-transaction-architecture/migration-transaction-architecture-"
        "contract.json"
    ):
        raise ValueError("body parent binding path mismatch")
    return {"structural": structural, "body": body}


def _effective_relation_catalogue(structural: dict[str, Any]) -> list[dict[str, Any]]:
    relations = copy.deepcopy(structural["relation_catalogue"]["relations"])
    for rel in relations:
        name = rel["name"]
        columns = rel["columns"]
        colnames = {row["name"] for row in columns}
        if name in STREAM_RELATIONS and "stream_id" not in colnames:
            columns.append(
                {
                    "name": "stream_id",
                    "data_type": "uuid",
                    "nullable": False,
                    "default_sql": None,
                }
            )
            colnames.add("stream_id")
        if name == "context_observer_generation" and "terminal_reason" not in colnames:
            columns.append(
                {
                    "name": "terminal_reason",
                    "data_type": "generation_terminal_reason",
                    "nullable": True,
                    "default_sql": None,
                }
            )
            colnames.add("terminal_reason")
        if "xmin" not in colnames:
            columns.append(
                {
                    "name": "xmin",
                    "data_type": "xid",
                    "nullable": False,
                    "default_sql": None,
                }
            )
            colnames.add("xmin")
        pk = rel["primary_key"]
        if name in REWRITE_COORDINATES_RELATIONS and "stream_id" not in pk["columns"]:
            if "source_contract_id" in pk["columns"]:
                idx = pk["columns"].index("source_contract_id") + 1
                pk["columns"].insert(idx, "stream_id")
        for unique in rel["unique_constraints"]:
            cols = unique["columns"]
            if name in REWRITE_COORDINATES_RELATIONS and "stream_id" not in cols:
                if "source_contract_id" in cols:
                    idx = cols.index("source_contract_id") + 1
                    cols.insert(idx, "stream_id")
        for fk in rel["foreign_keys"]:
            cols = fk["columns"]
            refs = fk["references_columns"]
            if name in REWRITE_COORDINATES_RELATIONS and "stream_id" not in cols:
                if "source_contract_id" in cols:
                    idx = cols.index("source_contract_id") + 1
                    cols.insert(idx, "stream_id")
                    refs.insert(idx, "stream_id")
    return relations


def _effective_rls_policies(structural: dict[str, Any]) -> list[dict[str, Any]]:
    policies = copy.deepcopy(structural["rls_policy_catalogue"]["policies"])
    marker = ", transaction_timestamp())"
    for pol in policies:
        for key in ("using_sql", "with_check_sql"):
            sql = pol.get(key)
            if sql and "session_binding_allows_v1(" in sql:
                if marker in sql and ", stream_id," not in sql:
                    sql = sql.replace(marker, ", stream_id, transaction_timestamp())")
                    pol[key] = sql
    return policies


def _effective_support_function(structural: dict[str, Any]) -> dict[str, Any]:
    support = copy.deepcopy(structural["support_functions"][0])
    support["inputs"] = copy.deepcopy(support["inputs"])
    support["inputs"].insert(
        -1,
        {"name": "requested_stream_id", "mode": "IN", "data_type": "uuid"},
    )
    body = support["body_sql"]
    if "binding.stream_id = requested_stream_id" not in body:
        marker = "AND binding.source_contract_id = requested_source_contract_id"
        body = body.replace(
            marker,
            marker + " AND binding.stream_id = requested_stream_id",
        )
    support["body_sql"] = body
    return support


def _effective_type_catalogue(structural: dict[str, Any]) -> dict[str, Any]:
    types = copy.deepcopy(structural["type_catalogue"])
    types["enums"] = copy.deepcopy(types["enums"]) + [
        {
            "name": "durability_transition_result_kind",
            "values": [
                "RECEIPT_APPLIED",
                "RECEIPT_REPLAYED",
                "REBASE_APPLIED",
                "TERMINAL_REPLAYED",
            ],
        },
        {
            "name": "source_retention_reason",
            "values": [
                "ELIGIBLE",
                "EXECUTION_DISABLED",
                "CHECKPOINT_LAG",
                "ACTIVE_PIN",
                "KEY_OVERLAP",
                "GRACE_PENDING",
                "AMBIGUOUS_CENSUS",
                "NO_NON_CONSUMED_GENERATION",
            ],
        },
    ]
    types["composites"] = copy.deepcopy(types["composites"]) + [
        {
            "name": "durability_transition_result_v1",
            "fields": [
                {
                    "name": "result_kind",
                    "data_type": "durability_transition_result_kind",
                },
                {"name": "checkpoint_state", "data_type": "checkpoint_state"},
                {"name": "source_position", "data_type": "bigint"},
                {"name": "decision", "data_type": "observation_decision"},
                {"name": "reason_code", "data_type": "observation_reason"},
                {
                    "name": "checkpoint_disposition",
                    "data_type": "checkpoint_disposition",
                },
                {"name": "lifecycle_revision", "data_type": "bigint"},
                {"name": "evidence_digest", "data_type": "digest_sha256"},
            ],
        },
    ]
    for composite in types["composites"]:
        if composite["name"] == "generation_registration_v1":
            if not any(
                item["name"] == "initial_key_interval" for item in composite["fields"]
            ):
                composite["fields"].append(
                    {
                        "name": "initial_key_interval",
                        "data_type": "future_key_interval_v1",
                    }
                )
        if composite["name"] == "context_source_retention_eligibility_v1":
            for item in composite["fields"]:
                if item["name"] == "reason_code":
                    item["data_type"] = "source_retention_reason"
    return types


def _effective_entry_points(structural: dict[str, Any]) -> list[dict[str, Any]]:
    entries = copy.deepcopy(structural["entry_points"])
    for entry in entries:
        if entry["name"] == "apply_durability_transition_v1":
            entry["output"]["data_type"] = "durability_transition_result_v1"
    return entries


def apply_recovery(structural: dict[str, Any]) -> dict[str, Any]:
    """Apply the accepted closed 26-operation recovery to a deep copy."""
    effective = copy.deepcopy(structural)
    effective["relation_catalogue"]["relations"] = _effective_relation_catalogue(
        structural
    )
    effective["rls_policy_catalogue"]["policies"] = _effective_rls_policies(structural)
    effective["support_functions"] = [_effective_support_function(structural)]
    effective["type_catalogue"] = _effective_type_catalogue(structural)
    effective["entry_points"] = _effective_entry_points(structural)
    roles = copy.deepcopy(structural["role_matrix"])
    for role in roles:
        role["role"] = FABRIC + role["role"]
        role["owns_relations"] = [FABRIC + item for item in role["owns_relations"]]
        role["owns_functions"] = [FABRIC + item for item in role["owns_functions"]]
        role["execute_entry_points"] = [
            FABRIC + item for item in role["execute_entry_points"]
        ]
        role["direct_table_select"] = [
            item if item.startswith("public.") else FABRIC + item
            for item in role["direct_table_select"]
        ]
        for grant in role["direct_table_dml"]:
            grant["relation"] = FABRIC + grant["relation"]
    owner = next(row for row in roles if row["role"] == FABRIC + "context_schema_owner")
    owner["direct_table_select"] = list(APPLICATION_COLUMNS)
    receiver = next(
        row for row in roles if row["role"] == FABRIC + "context_admission_receiver"
    )
    if (
        FABRIC + "context_service_practice_binding"
        not in receiver["direct_table_select"]
    ):
        receiver["direct_table_select"].append(
            FABRIC + "context_service_practice_binding"
        )
    effective["role_matrix"] = roles
    return effective


def _constraint_index(effective: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    """Map each relation id to its enforcing primary/unique constraint rows."""
    constraints: dict[str, list[dict[str, Any]]] = {}
    for rel in effective["relation_catalogue"]["relations"]:
        rid = _fabric(rel["name"])
        rows: list[dict[str, Any]] = []
        pk = rel.get("primary_key")
        if pk and pk.get("columns"):
            rows.append(
                {
                    "kind": "PRIMARY_KEY",
                    "name": pk["name"],
                    "columns": list(pk["columns"]),
                }
            )
        for unique in rel.get("unique_constraints", []):
            rows.append(
                {
                    "kind": unique["kind"],
                    "name": unique["name"],
                    "columns": list(unique["columns"]),
                }
            )
        constraints[rid] = rows
    for rid in APPLICATION_COLUMNS:
        constraints.setdefault(rid, [])
    return constraints


def derive_effective_catalogue(
    loaded: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Independently derive one EffectiveCatalogueV1 and reconcile it."""
    parents = loaded if loaded is not None else load_and_bind_parents()
    structural = parents["structural"]
    body = parents["body"]
    if structural.get("contract_sha256") != PARENT_DIGEST:
        raise ValueError("structural parent hash mismatch")
    if body.get("contract_sha256") != BODY_DIGEST:
        raise ValueError("body parent hash mismatch")
    if body.get("parent_binding", {}).get("contract_sha256") != PARENT_DIGEST:
        raise ValueError("body parent binding hash mismatch")
    recovery_ids = [
        op["id"] for op in body["structural_feasibility_recovery_v1"]["operations"]
    ]
    if recovery_ids != [f"REC{idx:02d}" for idx in range(1, 27)]:
        raise ValueError("unexpected recovery operation catalogue")
    effective = apply_recovery(structural)
    digest_domains = [
        domain
        for domain in effective["type_catalogue"]["domains"]
        if domain["name"] == DIGEST_DOMAIN_NAME
    ]
    if len(digest_domains) != 1 or digest_domains[0].get("not_null_values") is not True:
        raise ValueError("digest domain nullability source drift")
    digest_domains[0]["not_null_values"] = False

    catalogue = build_catalogue(structural)
    signatures = build_signatures(structural)
    roles = build_effective_roles(structural)
    declarations = build_trigger_declarations(structural)

    if catalogue != body["qualified_identifier_catalogue"]:
        raise ValueError("effective qualified identifier catalogue mismatch")
    if signatures != body["effective_parent_summary"]["effective_signatures"]:
        raise ValueError("effective signatures mismatch")
    if roles != body["effective_parent_summary"]["effective_roles"]:
        raise ValueError("effective roles mismatch")
    if declarations != body["effective_parent_summary"]["trigger_declarations"]:
        raise ValueError("effective trigger declarations mismatch")

    relations = catalogue["relations"]
    column_types = catalogue["column_types"]
    composite_fields = catalogue["composite_fields"]
    relation_rows = {
        _fabric(rel["name"]): rel
        for rel in effective["relation_catalogue"]["relations"]
    }
    return {
        "effective_structural": effective,
        "relations": relations,
        "relation_rows": relation_rows,
        "column_types": column_types,
        "composite_fields": composite_fields,
        "types": sorted(catalogue["types"]),
        "constraints": _constraint_index(effective),
        "roles": roles,
        "signatures": signatures,
        "trigger_declarations": declarations,
        "rls_policies": effective["rls_policy_catalogue"]["policies"],
        "support_functions": effective["support_functions"],
        "entry_points": effective["entry_points"],
        "trigger_function_catalogue": effective["trigger_function_catalogue"],
        "invariants": effective["invariant_enforcement_catalogue"],
        "recovery_operations": body["structural_feasibility_recovery_v1"]["operations"],
    }


def reconcile_catalogue(effective: dict[str, Any]) -> None:
    """Reconcile the effective catalogue against both accepted summaries."""
    body = _read_json(BODY_PATH)
    if effective["relations"] != body["qualified_identifier_catalogue"]["relations"]:
        raise ValueError("relations mismatch")
    if (
        effective["column_types"]
        != body["qualified_identifier_catalogue"]["column_types"]
    ):
        raise ValueError("column types mismatch")
    if (
        effective["composite_fields"]
        != body["qualified_identifier_catalogue"]["composite_fields"]
    ):
        raise ValueError("composite fields mismatch")
    if effective["roles"] != body["effective_parent_summary"]["effective_roles"]:
        raise ValueError("role summary mismatch")
    if (
        effective["trigger_declarations"]
        != body["effective_parent_summary"]["trigger_declarations"]
    ):
        raise ValueError("trigger declaration summary mismatch")


# ---------------------------------------------------------------------------
# Closed PostgreSQL-16 representability recovery
# ---------------------------------------------------------------------------

_RESELECT_KEY_TYPES: dict[str, list[tuple[str, str]]] = {
    CLAIM: [("practice_id", PG + "uuid"), ("id", PG + "uuid")],
    APPOINTMENT: [("practice_id", PG + "uuid"), ("id", PG + "uuid")],
    EVENT: [("practice_id", PG + "uuid"), ("id", PG + "uuid")],
    OUTBOX: [
        ("practice_id", PG + "uuid"),
        ("source_contract_id", FABRIC + "source_contract_code"),
        ("stream_id", PG + "uuid"),
        ("stream_epoch", PG + "bigint"),
        ("transaction_position", PG + "bigint"),
    ],
}


def _find_node(nodes: list[dict[str, Any]], node_id: str) -> dict[str, Any]:
    for node in nodes:
        if node["node_id"] == node_id:
            return node
        operands = node["operands"]
        children: list[list[dict[str, Any]]] = []
        if node["op"] == "IF":
            children.extend([operands["then"], operands["else"]])
        elif node["op"] == "SWITCH_TG_OP":
            children.extend(arm["nodes"] for arm in operands["arms"])
            children.append(operands["default"])
        elif node["op"] == "FOR_EACH":
            children.append(operands["nodes"])
        for child in children:
            try:
                return _find_node(child, node_id)
            except KeyError:
                pass
    raise KeyError(node_id)


def _trigger_arm(program: dict[str, Any], tg_op: str) -> list[dict[str, Any]]:
    switch = next(
        node for node in program["ast"]["nodes"] if node["op"] == "SWITCH_TG_OP"
    )
    return next(
        arm["nodes"] for arm in switch["operands"]["arms"] if arm["tg_op"] == tg_op
    )


def _replace_values(value: Any, predicate: Any, replacement: Any) -> Any:
    if isinstance(value, dict):
        if predicate(value):
            return copy.deepcopy(
                replacement(value) if callable(replacement) else replacement
            )
        return {
            key: _replace_values(child, predicate, replacement)
            for key, child in value.items()
        }
    if isinstance(value, list):
        return [_replace_values(child, predicate, replacement) for child in value]
    return value


def _is_trigger_xmin(value: dict[str, Any], relation: str | None = None) -> bool:
    return (
        value.get("op") == "REF"
        and value.get("kind") == "TRIGGER_COLUMN"
        and value.get("image") == "OLD"
        and value.get("column") == "xmin"
        and (relation is None or value.get("relation") == relation)
    )


def _contains_trigger_xmin(value: Any) -> bool:
    if isinstance(value, dict):
        return _is_trigger_xmin(value) or any(
            _contains_trigger_xmin(child) for child in value.values()
        )
    if isinstance(value, list):
        return any(_contains_trigger_xmin(child) for child in value)
    return False


def _system_xmin(symbol: str, relation: str) -> dict[str, Any]:
    return {
        "op": "SYSTEM_XMIN",
        "row": body_dsl.local_ref(symbol, relation),
        "type": PG + "xid",
    }


def _keyed_xmin_read(node_id: str, relation: str, output_symbol: str) -> dict[str, Any]:
    pairs = _RESELECT_KEY_TYPES[relation]
    predicate = body_dsl.all_of(
        *[
            body_dsl.eq(
                body_dsl.source_column(relation, column, type_name),
                body_dsl.trigger_column_ref("OLD", relation, column, type_name),
            )
            for column, type_name in pairs
        ]
    )
    return body_dsl.select_node(
        node_id,
        relation=relation,
        columns=["xmin"],
        predicate=predicate,
        cardinality="EXACTLY_ONE",
        output_symbol=output_symbol,
        order_by=[column for column, _ in pairs],
    )


def _count_expr(symbol: str, relation: str) -> dict[str, Any]:
    return {
        "op": "COUNT",
        "operand": body_dsl.local_ref(symbol, relation + "[]"),
        "type": PG + "bigint",
    }


def _replace_appointment_binding_refs(value: Any) -> Any:
    def replacement(item: dict[str, Any]) -> dict[str, Any]:
        column = item["column"]
        if column == "practice_id":
            return body_dsl.trigger_column_ref(
                "NEW", APPOINTMENT, "practice_id", PG + "uuid"
            )
        if column == "source_contract_id":
            return body_dsl.const(
                FABRIC + "source_contract_code", "diary.appointment_rescheduled.v1"
            )
        if column == "stream_id":
            return body_dsl.local_ref("producer_stream", PG + "uuid")
        raise ValueError("unclosed appointment binding field " + column)

    return _replace_values(
        value,
        lambda item: (
            item.get("op") == "REF"
            and item.get("kind") == "ROW_COLUMN"
            and item.get("symbol") == "binding"
            and item.get("relation") == BINDING
            and item.get("column") in {"practice_id", "source_contract_id", "stream_id"}
        ),
        replacement,
    )


def _producer_binding_set_read(
    node_id: str, original_select: dict[str, Any]
) -> dict[str, Any]:
    operands = original_select["operands"]
    return body_dsl.select_node(
        node_id,
        relation=BINDING,
        columns=copy.deepcopy(operands["columns"]),
        predicate=copy.deepcopy(operands["predicate"]),
        cardinality="COMPLETE_SET",
        output_symbol="producer_bindings",
        order_by=[row["column"] for row in operands.get("order_by", [])],
        set_read=True,
    )


def _producer_stream_let(node_id: str) -> dict[str, Any]:
    return body_dsl.let_node(
        node_id,
        "producer_stream",
        PG + "uuid",
        {
            "op": "MIN_FIELD",
            "source": body_dsl.local_ref("producer_bindings", BINDING + "[]"),
            "field": "stream_id",
            "type": PG + "uuid",
        },
    )


def _recover_immediate_xmin(
    program: dict[str, Any], relation: str, symbol: str, insertion: list[dict[str, Any]]
) -> None:
    program["symbols"].append(body_dsl.node_symbol(symbol, relation))
    insertion.insert(
        0,
        _keyed_xmin_read(program["id"] + ".recovery.old-xmin", relation, symbol),
    )
    program["ast"] = _replace_values(
        program["ast"],
        lambda item: _is_trigger_xmin(item, relation),
        _system_xmin(symbol, relation),
    )


def _build_appointment_guard(
    original_binding_census: dict[str, Any],
    original_support: dict[str, Any],
    original_context: dict[str, Any],
) -> dict[str, Any]:
    count = _count_expr("producer_bindings", BINDING)
    zero = body_dsl.eq(count, body_dsl.const(PG + "bigint", 0))
    one = body_dsl.eq(count, body_dsl.const(PG + "bigint", 1))
    support = _replace_appointment_binding_refs(copy.deepcopy(original_support))
    support["node_id"] = APPOINTMENT_GUARD_ID + ".update.binding.support"
    context = copy.deepcopy(original_context)
    context["node_id"] = APPOINTMENT_GUARD_ID + ".context"
    context = _replace_values(
        context,
        lambda item: item.get("op") == "CONST" and item.get("value") == "AFTER",
        body_dsl.const(PG + "text", "BEFORE"),
    )
    select_bindings = _producer_binding_set_read(
        APPOINTMENT_GUARD_ID + ".update.binding.select", original_binding_census
    )
    old_read = _keyed_xmin_read(
        APPOINTMENT_GUARD_ID + ".update.old-xmin", APPOINTMENT, "old_appointment"
    )
    not_current = body_dsl.unary(
        "NOT",
        body_dsl.eq(
            _system_xmin("old_appointment", APPOINTMENT), body_dsl.current_xid32()
        ),
    )
    applicable = [
        body_dsl.assert_node(
            APPOINTMENT_GUARD_ID + ".update.binding.cardinality", one, "F_CARDINALITY"
        ),
        _producer_stream_let(APPOINTMENT_GUARD_ID + ".update.binding.stream"),
        support,
        body_dsl.assert_node(
            APPOINTMENT_GUARD_ID + ".update.binding.assert",
            body_dsl.local_ref("binding_allowed", PG + "boolean"),
            "F_BINDING_DENIED",
        ),
        old_read,
        body_dsl.assert_node(
            APPOINTMENT_GUARD_ID + ".update.second", not_current, "F_SECOND_UPDATE"
        ),
        body_dsl.node(APPOINTMENT_GUARD_ID + ".update.return", "RETURN_NEW"),
    ]
    update = [
        select_bindings,
        body_dsl.node(
            APPOINTMENT_GUARD_ID + ".update.applicability",
            "IF",
            condition=zero,
            then=[body_dsl.node(APPOINTMENT_GUARD_ID + ".update.inert", "RETURN_NEW")],
            **{"else": applicable},
            convergence="ALL_TERMINAL",
        ),
    ]
    switch = body_dsl.node(
        APPOINTMENT_GUARD_ID + ".switch",
        "SWITCH_TG_OP",
        arms=[{"tg_op": "UPDATE", "nodes": update}],
        default=[
            body_dsl.node(
                APPOINTMENT_GUARD_ID + ".switch.default.raise",
                "RAISE",
                failure_id="F_TRIGGER_CONTEXT",
            )
        ],
        convergence="ALL_TERMINAL",
    )
    return body_dsl.body(
        APPOINTMENT_GUARD_ID,
        "TRIGGER_FUNCTION",
        APPOINTMENT_GUARD_ID,
        [
            body_dsl.node_symbol("producer_bindings", BINDING + "[]"),
            body_dsl.node_symbol("producer_stream", PG + "uuid"),
            body_dsl.node_symbol("binding_allowed", PG + "boolean"),
            body_dsl.node_symbol("old_appointment", APPOINTMENT),
        ],
        [context, switch],
    )


def _program(body: dict[str, Any], program_id: str) -> dict[str, Any]:
    return next(
        program for program in body["body_programs"] if program["id"] == program_id
    )


def _predicate(body: dict[str, Any], program_id: str, node_id: str) -> dict[str, Any]:
    node = _find_node(_program(body, program_id)["ast"]["nodes"], node_id)
    operands = node["operands"]
    if "predicate" in operands:
        return operands["predicate"]
    return operands["condition"]


def _recovery_operation_evidence(
    immutable_body: dict[str, Any],
    effective_body: dict[str, Any],
    base_effective: dict[str, Any],
    recovered_effective: dict[str, Any],
) -> list[dict[str, Any]]:
    """Seal every position-specific representability transform."""
    guard_signature = next(
        row
        for row in recovered_effective["signatures"]["trigger_functions"]
        if row["id"] == APPOINTMENT_GUARD_ID
    )
    guard_declaration = next(
        row
        for row in recovered_effective["trigger_declarations"]
        if row["id"] == APPOINTMENT_GUARD_TRIGGER_ID
    )
    source_fence = _program(immutable_body, FABRIC + "cf_fence_appointment_update_v1")
    effective_guard = _program(effective_body, APPOINTMENT_GUARD_ID)
    effective_fence = _program(
        effective_body, FABRIC + "cf_fence_appointment_update_v1"
    )
    source_applicability = _trigger_arm(source_fence, "UPDATE")
    effective_applicability = {
        "guard": _trigger_arm(effective_guard, "UPDATE"),
        "fence": _trigger_arm(effective_fence, "UPDATE"),
    }

    reselect_sites = [
        {
            "function": FABRIC + "cf_guard_claim_v1",
            "source_node_id": FABRIC + "cf_guard_claim_v1.update.provenance",
            "effective_node_id": FABRIC + "cf_guard_claim_v1.update.provenance",
            "reselect_node_id": FABRIC + "cf_guard_claim_v1.recovery.old-xmin",
        },
        {
            "function": APPOINTMENT_GUARD_ID,
            "source_function": FABRIC + "cf_fence_appointment_update_v1",
            "source_node_id": FABRIC + "cf_fence_appointment_update_v1.update.second",
            "effective_node_id": APPOINTMENT_GUARD_ID + ".update.second",
            "reselect_node_id": APPOINTMENT_GUARD_ID + ".update.old-xmin",
        },
        {
            "function": FABRIC + "cf_guard_event_v1",
            "source_node_id": FABRIC + "cf_guard_event_v1.delete.current",
            "effective_node_id": FABRIC + "cf_guard_event_v1.delete.current",
            "reselect_node_id": FABRIC + "cf_guard_event_v1.recovery.old-xmin",
        },
        {
            "function": FABRIC + "cf_guard_outbox_v1",
            "source_node_id": FABRIC + "cf_guard_outbox_v1.delete.authorized",
            "effective_node_id": FABRIC + "cf_guard_outbox_v1.delete.authorized",
            "reselect_node_id": FABRIC + "cf_guard_outbox_v1.recovery.old-xmin",
        },
    ]
    for site in reselect_sites:
        source_function = site.get("source_function", site["function"])
        site["old_expression_sha256"] = _json_seal(
            _predicate(immutable_body, source_function, site["source_node_id"])
        )
        site["new_expression_sha256"] = _json_seal(
            _predicate(effective_body, site["function"], site["effective_node_id"])
        )
        site["new_reselect_sha256"] = _json_seal(
            _find_node(
                _program(effective_body, site["function"])["ast"]["nodes"],
                site["reselect_node_id"],
            )
        )

    dependencies = {
        row["fence"]: row for row in RECOVERY_SPEC["paired_guard_dependencies"]
    }
    deferred_removals = []
    for operation_id, fence, source_node_id in (
        (
            "REMOVE_DEFERRED_APPOINTMENT_OLD_XMIN",
            FABRIC + "cf_fence_appointment_update_v1",
            FABRIC + "cf_fence_appointment_update_v1.update.second",
        ),
        (
            "REMOVE_DEFERRED_EVENT_DELETE_OLD_XMIN",
            FABRIC + "cf_fence_event_v1",
            FABRIC + "cf_fence_event_v1.delete.current",
        ),
        (
            "REMOVE_DEFERRED_OUTBOX_DELETE_OLD_XMIN",
            FABRIC + "cf_fence_outbox_v1",
            FABRIC + "cf_fence_outbox_v1.delete.authorized",
        ),
    ):
        source_node = _find_node(
            _program(immutable_body, fence)["ast"]["nodes"], source_node_id
        )
        try:
            effective_node = _find_node(
                _program(effective_body, fence)["ast"]["nodes"], source_node_id
            )
        except KeyError:
            effective_node = None
        deferred_removals.append(
            {
                "id": operation_id,
                "affected_ids": [fence, source_node_id],
                "old_fragment_sha256": _json_seal(source_node),
                "new_fragment_sha256": _json_seal(effective_node),
                "paired_guard_dependency_sha256": _json_seal(dependencies[fence]),
            }
        )

    digest_domain = next(
        domain
        for domain in recovered_effective["effective_structural"]["type_catalogue"][
            "domains"
        ]
        if domain["name"] == DIGEST_DOMAIN_NAME
    )
    source_digest_domain = copy.deepcopy(digest_domain)
    source_digest_domain["not_null_values"] = True
    operations = [
        {
            "id": "RELAX_DIGEST_DOMAIN_NULLABILITY",
            "affected_ids": [FABRIC + DIGEST_DOMAIN_NAME],
            "old_fragment_sha256": _json_seal(source_digest_domain),
            "new_fragment_sha256": _json_seal(digest_domain),
        },
        {
            "id": "ADD_APPOINTMENT_GUARD_SIGNATURE",
            "affected_ids": [APPOINTMENT_GUARD_ID],
            "old_fragment_sha256": _json_seal(None),
            "new_fragment_sha256": _json_seal(guard_signature),
        },
        {
            "id": "ADD_APPOINTMENT_GUARD_PROGRAM",
            "affected_ids": [APPOINTMENT_GUARD_ID],
            "old_fragment_sha256": _json_seal(None),
            "new_fragment_sha256": _json_seal(effective_guard),
        },
        {
            "id": "ADD_APPOINTMENT_GUARD_DECLARATION",
            "affected_ids": [APPOINTMENT_GUARD_TRIGGER_ID],
            "old_fragment_sha256": _json_seal(None),
            "new_fragment_sha256": _json_seal(guard_declaration),
        },
        {
            "id": "ADD_APPOINTMENT_PRODUCER_APPLICABILITY",
            "affected_ids": [
                APPOINTMENT_GUARD_ID + ".update.applicability",
                FABRIC + "cf_fence_appointment_update_v1.update.applicability",
            ],
            "old_fragment_sha256": _json_seal(source_applicability),
            "new_fragment_sha256": _json_seal(effective_applicability),
        },
        {
            "id": "RESELECT_BEFORE_TRIGGER_OLD_XMIN",
            "affected_ids": [site["function"] for site in reselect_sites],
            "sites": reselect_sites,
            "old_fragment_sha256": _json_seal(
                [site["old_expression_sha256"] for site in reselect_sites]
            ),
            "new_fragment_sha256": _json_seal(
                [
                    [site["new_expression_sha256"], site["new_reselect_sha256"]]
                    for site in reselect_sites
                ]
            ),
        },
        *deferred_removals,
    ]
    if [row["id"] for row in operations] != RECOVERY_SPEC["operation_order"]:
        raise ValueError("representability recovery operation-order drift")
    if APPOINTMENT_GUARD_ID in {
        row["id"] for row in base_effective["signatures"]["trigger_functions"]
    }:
        raise ValueError(
            "appointment guard unexpectedly present in immutable catalogue"
        )
    return operations


def derive_effective_body(
    immutable_body: dict[str, Any], effective: dict[str, Any]
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Apply the sole closed representability recovery to immutable parents."""
    if immutable_body.get("contract_sha256") != BODY_DIGEST:
        raise ValueError("representability recovery body hash mismatch")
    body = copy.deepcopy(immutable_body)
    recovered = copy.deepcopy(effective)

    programs = {program["id"]: program for program in body["body_programs"]}

    claim = programs[FABRIC + "cf_guard_claim_v1"]
    claim_exact = _find_node(
        claim["ast"]["nodes"], FABRIC + "cf_guard_claim_v1.update.exact"
    )
    _recover_immediate_xmin(
        claim, CLAIM, "reselected_old_claim", claim_exact["operands"]["then"]
    )

    event_guard = programs[FABRIC + "cf_guard_event_v1"]
    event_exact = _find_node(
        event_guard["ast"]["nodes"], FABRIC + "cf_guard_event_v1.delete.exact"
    )
    _recover_immediate_xmin(
        event_guard,
        EVENT,
        "reselected_old_event",
        event_exact["operands"]["then"],
    )

    outbox_guard = programs[FABRIC + "cf_guard_outbox_v1"]
    _recover_immediate_xmin(
        outbox_guard,
        OUTBOX,
        "reselected_old_outbox",
        _trigger_arm(outbox_guard, "DELETE"),
    )

    appointment_fence = programs[FABRIC + "cf_fence_appointment_update_v1"]
    update_arm = _trigger_arm(appointment_fence, "UPDATE")
    if len(update_arm) != 2:
        raise ValueError("appointment applicability arm shape drift")
    original_binding_census = copy.deepcopy(update_arm[0])
    credential_branch = update_arm[1]
    if (
        original_binding_census.get("op") != "SELECT_SET"
        or credential_branch.get("op") != "IF"
    ):
        raise ValueError("appointment applicability census shape drift")
    credential_then = credential_branch["operands"]["then"]
    original_binding_select = _find_node(
        credential_then,
        FABRIC + "cf_fence_appointment_update_v1.update.binding.select",
    )
    original_support = copy.deepcopy(
        _find_node(
            credential_then,
            FABRIC + "cf_fence_appointment_update_v1.update.binding.support",
        )
    )
    if original_binding_select.get("op") != "SELECT_EXACT":
        raise ValueError("appointment exact binding selection shape drift")
    remainder = [
        copy.deepcopy(node)
        for node in credential_then
        if node["node_id"]
        not in {
            FABRIC + "cf_fence_appointment_update_v1.update.binding.select",
            FABRIC + "cf_fence_appointment_update_v1.update.second",
        }
    ]
    remainder = _replace_appointment_binding_refs(remainder)
    appointment_fence["symbols"] = [
        sym
        for sym in appointment_fence["symbols"]
        if sym["id"] not in {"binding", "binding_matches"}
    ]
    appointment_fence["symbols"].extend(
        [
            body_dsl.node_symbol("producer_bindings", BINDING + "[]"),
            body_dsl.node_symbol("producer_stream", PG + "uuid"),
        ]
    )
    count = _count_expr("producer_bindings", BINDING)
    recovered_update = [
        _producer_binding_set_read(
            appointment_fence["id"] + ".update.applicability.select",
            original_binding_census,
        ),
        body_dsl.node(
            appointment_fence["id"] + ".update.applicability",
            "IF",
            condition=body_dsl.eq(count, body_dsl.const(PG + "bigint", 0)),
            then=[
                body_dsl.node(
                    appointment_fence["id"] + ".update.applicability.inert",
                    "RETURN_NULL",
                )
            ],
            **{
                "else": [
                    body_dsl.assert_node(
                        appointment_fence["id"] + ".update.applicability.cardinality",
                        body_dsl.eq(count, body_dsl.const(PG + "bigint", 1)),
                        "F_CARDINALITY",
                    ),
                    _producer_stream_let(
                        appointment_fence["id"] + ".update.applicability.stream"
                    ),
                    *remainder,
                ]
            },
            convergence="ALL_TERMINAL",
        ),
    ]
    update_arm[:] = recovered_update

    event_fence = programs[FABRIC + "cf_fence_event_v1"]
    event_delete = _find_node(
        event_fence["ast"]["nodes"], FABRIC + "cf_fence_event_v1.delete.exact"
    )
    event_delete["operands"]["then"] = [
        body_dsl.node(
            FABRIC + "cf_fence_event_v1.delete.paired-guard-return", "RETURN_NULL"
        )
    ]

    outbox_fence = programs[FABRIC + "cf_fence_outbox_v1"]
    outbox_authorized = _find_node(
        outbox_fence["ast"]["nodes"],
        FABRIC + "cf_fence_outbox_v1.delete.authorized",
    )
    condition = outbox_authorized["operands"]["condition"]
    if condition.get("op") != "AND":
        raise ValueError("outbox paired-guard condition shape drift")
    observable = [
        operand
        for operand in condition["operands"]
        if not _contains_trigger_xmin(operand)
    ]
    if len(observable) != len(condition["operands"]) - 1:
        raise ValueError("outbox deferred xmin recovery cardinality drift")
    condition["operands"] = observable

    guard_program = _build_appointment_guard(
        original_binding_census,
        original_support,
        appointment_fence["ast"]["nodes"][0],
    )
    appointment_index = next(
        index
        for index, program in enumerate(body["body_programs"])
        if program["id"] == appointment_fence["id"]
    )
    body["body_programs"].insert(appointment_index, guard_program)
    body["renderer_order"].insert(appointment_index, APPOINTMENT_GUARD_ID)

    matrix_index = next(
        index
        for index, row in enumerate(body["trigger_applicability_return_matrix"])
        if row["function"] == appointment_fence["id"]
    )
    body["trigger_applicability_return_matrix"].insert(
        matrix_index,
        {
            "function": APPOINTMENT_GUARD_ID,
            "trigger": APPOINTMENT_GUARD_TRIGGER_ID,
            "relation": APPOINTMENT,
            "timing": "BEFORE",
            "events": ["UPDATE"],
            "old_on": ["UPDATE"],
            "new_on": ["UPDATE"],
            "returns": {"UPDATE": "RETURN_NEW_OR_RAISE"},
            "read_only": True,
            "lock_free": True,
            "sibling_call_free": True,
        },
    )
    body["call_graph"]["nodes"].append(APPOINTMENT_GUARD_ID)
    body["call_graph"]["nodes"].sort()
    body["call_graph"]["edges"].append(
        {"from": APPOINTMENT_GUARD_ID, "to": FABRIC + "session_binding_allows_v1"}
    )
    trigger_signatures = recovered["signatures"]["trigger_functions"]
    fence_signature_index = next(
        index
        for index, signature in enumerate(trigger_signatures)
        if signature["id"] == appointment_fence["id"]
    )
    guard_signature = copy.deepcopy(trigger_signatures[fence_signature_index])
    guard_signature["id"] = APPOINTMENT_GUARD_ID
    guard_signature["invariant_ids"] = ["current_xid_provenance_v1"]
    trigger_signatures.insert(fence_signature_index, guard_signature)

    declarations = recovered["trigger_declarations"]
    fence_declaration_index = next(
        index
        for index, declaration in enumerate(declarations)
        if declaration["function"] == appointment_fence["id"]
    )
    declarations.insert(
        fence_declaration_index,
        {
            "id": APPOINTMENT_GUARD_TRIGGER_ID,
            "relation": APPOINTMENT,
            "timing": "BEFORE",
            "row_level": True,
            "events": ["UPDATE"],
            "deferrable": False,
            "initially_deferred": False,
            "function": APPOINTMENT_GUARD_ID,
            "invariant_ids": ["current_xid_provenance_v1"],
        },
    )
    recovered["postgresql_representability_recovery_applied"] = True
    operation_evidence = _recovery_operation_evidence(
        immutable_body, body, effective, recovered
    )
    if (
        RECOVERY_SPEC["operations"]
        and operation_evidence != RECOVERY_SPEC["operations"]
    ):
        raise ValueError("representability recovery fragment-seal drift")
    applied_recovery = copy.deepcopy(RECOVERY_SPEC)
    applied_recovery["operations"] = operation_evidence
    body["postgresql_16_representability_recovery_v1"] = applied_recovery

    direct_xmin = [
        (program["id"], expr)
        for program in body["body_programs"]
        for expr in _walk_program_expressions(program)
        if expr.get("op") == "REF"
        and expr.get("kind") == "TRIGGER_COLUMN"
        and expr.get("column") == "xmin"
    ]
    if direct_xmin:
        raise ValueError(
            "effective body retains trigger-row xmin in "
            + ", ".join(
                program_id + ":" + expr.get("column", "")
                for program_id, expr in direct_xmin
            )
        )
    expected = RECOVERY_SPEC["effective_population"]
    if len(body["body_programs"]) != expected["programs"]:
        raise ValueError("effective program population mismatch")
    if len(trigger_signatures) != expected["trigger_functions"]:
        raise ValueError("effective trigger-function population mismatch")
    if len(declarations) != expected["trigger_declarations"]:
        raise ValueError("effective trigger-declaration population mismatch")
    return body, recovered


# ---------------------------------------------------------------------------
# Expression rendering
# ---------------------------------------------------------------------------

CURRENT_XID32_SQL = (
    "((((pg_catalog.pg_current_xact_id()::pg_catalog.text)::pg_catalog.int8 "
    "& 4294967295)::pg_catalog.text)::pg_catalog.xid)"
)

DIGEST_OPCODE_SET = frozenset(
    {
        "ADD",
        "AND",
        "ARRAY_CONST",
        "CANONICAL_DIGEST",
        "CASE",
        "COMPOSITE_CONSTRUCT",
        "CONST",
        "COUNT",
        "CURRENT_XID32",
        "EQ",
        "FIELD",
        "GEN_RANDOM_UUID",
        "GT",
        "GTE",
        "IS_DISTINCT_FROM",
        "IS_NOT_NULL",
        "IS_NULL",
        "JSON_GET_CAST",
        "JSON_KEYS_EXACT",
        "LT",
        "LTE",
        "MIN_FIELD",
        "NE",
        "NOT",
        "OR",
        "REF",
        "SESSION_USER",
        "SET_CONTAINS_KEY",
        "SET_COVERS_KEYS",
        "SUBTRACT",
        "SYSTEM_XMIN",
        "TIMESTAMP_ADD_MINUTES",
        "TIMESTAMP_ADD_SECONDS",
        "TRANSACTION_TIMESTAMP",
    }
)


def _literal_text(value: str) -> str:
    return "'" + str(value).replace("'", "''") + "'"


def _literal(value: Any, type_name: str) -> str:
    if isinstance(value, list):
        raise ValueError("array value must use ARRAY_CONST, not _literal")
    base = type_name[:-2] if type_name.endswith("[]") else type_name
    if value is None:
        return "NULL::" + _type_sql(type_name)
    text = _literal_text(value)
    if base == "pg_catalog.boolean":
        return ("TRUE" if value else "FALSE") + "::" + _type_sql(base)
    if base in ("pg_catalog.bigint", "pg_catalog.integer", "pg_catalog.smallint"):
        return str(value) + "::" + _type_sql(base)
    return text + "::" + _type_sql(base)


def _canonical_text_sql(operand: dict[str, Any]) -> str:
    """Canonical value SQL for a digest operand."""
    type_name = operand["type"]
    base = type_name[:-2] if type_name.endswith("[]") else type_name
    op = render_expr(operand)
    if base == "pg_catalog.uuid":
        return "pg_catalog.lower((" + op + ")::pg_catalog.text)"
    if base == "pg_catalog.boolean":
        return "(CASE WHEN (" + op + ") THEN 'true' ELSE 'false' END)::pg_catalog.text"
    if base == "pg_catalog.timestamptz":
        fmt = 'YYYY-MM-DD"T"HH24:MI:SS.US"Z"'
        return "pg_catalog.to_char((" + op + " AT TIME ZONE 'UTC'), '" + fmt + "')"
    if base == "pg_catalog.jsonb":
        return "((" + op + ")::pg_catalog.text)"
    return "(" + op + ")::pg_catalog.text"


def _digest_frame_sql(type_name: str, operand: dict[str, Any] | None) -> str:
    """One type-tagged byte-length-prefixed digest frame."""
    type_text = _literal_text(type_name)
    tlen = str(len(type_name.encode("utf-8")))
    if operand is None:
        return "(" + tlen + " || ':' || " + type_text + " || ':' || '-1')"
    value_sql = _canonical_text_sql(operand)
    vlen = (
        "pg_catalog.octet_length(pg_catalog.convert_to("
        + value_sql
        + ", 'UTF8'::pg_catalog.name))"
    )
    value_frame = (
        "("
        + tlen
        + " || ':' || "
        + type_text
        + " || ':' || "
        + vlen
        + "::pg_catalog.text || ':' || "
        + value_sql
        + ")"
    )
    null_frame = "(" + tlen + " || ':' || " + type_text + " || ':' || '-1')"
    return (
        "(CASE WHEN ("
        + render_expr(operand)
        + " IS NULL) THEN "
        + null_frame
        + " ELSE "
        + value_frame
        + " END)"
    )


def _render_digest(expr: dict[str, Any]) -> str:
    profile = expr["profile"]
    operands = expr["operands"]
    profile_type = "profile"
    ptlen = str(len(profile_type.encode("utf-8")))
    plen = str(len(profile.encode("utf-8")))
    profile_frame = (
        "("
        + ptlen
        + " || ':' || "
        + _literal_text(profile_type)
        + " || ':' || "
        + plen
        + " || ':' || "
        + _literal_text(profile)
        + ")"
    )
    parts = [profile_frame]
    for operand in operands:
        parts.append(_digest_frame_sql(operand["type"], operand))
    sep = "pg_catalog.chr(31)"
    preimage = (" || " + sep + " || ").join(parts)
    return (
        "('sha256:' || pg_catalog.encode("
        "pg_catalog.sha256(pg_catalog.convert_to("
        + preimage
        + ", 'UTF8'::pg_catalog.name)), 'hex'))::emr4_context_fabric.digest_sha256"
    )


def _render_array_const(expr: dict[str, Any]) -> str:
    element_type = expr["type"][:-2]
    items = ", ".join(_literal(item, element_type) for item in expr["values"])
    return "ARRAY[" + items + "]::" + _type_sql(expr["type"])


def _render_case(expr: dict[str, Any]) -> str:
    parts = ["CASE"]
    for arm in expr["arms"]:
        parts.append(
            "WHEN " + render_expr(arm["when"]) + " THEN " + render_expr(arm["then"])
        )
    parts.append("ELSE " + render_expr(expr["else"]))
    parts.append("END")
    return "(" + " ".join(parts) + ")"


def _render_composite(expr: dict[str, Any]) -> str:
    items = ", ".join(render_expr(field["value"]) for field in expr["fields"])
    return "(ROW(" + items + "))::" + _type_sql(expr["type"])


def _render_json_keys_exact(expr: dict[str, Any]) -> str:
    source = render_expr(expr["source"])
    keys = ", ".join(_literal_text(key) for key in expr["keys"])
    keys_sql = "ARRAY[" + keys + "]::pg_catalog.text[]"
    actual = (
        "(SELECT pg_catalog.array_agg(k.k ORDER BY k.k) "
        "FROM pg_catalog.jsonb_object_keys(" + source + ") AS k(k))"
    )
    return (
        "(("
        + source
        + " IS NOT NULL) AND (COALESCE("
        + actual
        + ", ARRAY[]::pg_catalog.text[]) = "
        + keys_sql
        + "))"
    )


def _render_ref_like(ref: dict[str, Any]) -> str:
    if "op" in ref:
        return render_expr(ref)
    kind = ref["kind"]
    if kind == "LOCAL":
        return _symbol_ident(ref["symbol"])
    if kind == "INPUT":
        return _symbol_ident(ref["symbol"])
    raise ValueError("unknown bare symbol kind " + kind)


def _render_set_contains_key(expr: dict[str, Any]) -> str:
    set_sql = _render_ref_like(expr["set"])
    source_rel = _fabric(expr["source_relation"])
    pairs = " AND ".join(
        "s."
        + _ident(pair["set_column"])
        + " = "
        + source_rel
        + "."
        + _ident(pair["source_column"])
        for pair in expr["key_pairs"]
    )
    return (
        "(EXISTS (SELECT 1 FROM pg_catalog.unnest("
        + set_sql
        + ") AS s WHERE "
        + pairs
        + "))"
    )


def _render_set_covers_keys(expr: dict[str, Any]) -> str:
    required = _render_ref_like(expr["required"])
    evidence = _render_ref_like(expr["evidence"])
    pairs = " AND ".join(
        "e."
        + _ident(pair["evidence_column"])
        + " = r."
        + _ident(pair["required_column"])
        for pair in expr["key_pairs"]
    )
    return (
        "(NOT EXISTS (SELECT 1 FROM pg_catalog.unnest("
        + required
        + ") AS r WHERE NOT EXISTS (SELECT 1 FROM pg_catalog.unnest("
        + evidence
        + ") AS e WHERE "
        + pairs
        + ")))"
    )


def _render_ref(expr: dict[str, Any]) -> str:
    kind = expr["kind"]
    if kind == "SOURCE_COLUMN":
        return _fabric(expr["relation"]) + "." + _ident(expr["column"])
    if kind == "SYSTEM":
        field = expr["field"]
        if field == "SESSION_USER":
            return "session_user"
        return field
    if kind == "ROW_COLUMN":
        return _symbol_ident(expr["symbol"]) + "." + _ident(expr["column"])
    if kind in ("LOCAL", "INPUT"):
        return _symbol_ident(expr["symbol"])
    if kind == "TRIGGER_COLUMN":
        return _ident(expr["image"]) + "." + _ident(expr["column"])
    raise ValueError("unknown REF kind " + kind)


def render_expr(expr: dict[str, Any]) -> str:
    op = expr["op"]
    if op == "SEQUENCE":
        raise ValueError("SEQUENCE is not an expression")
    if op == "REF":
        return _render_ref(expr)
    if op == "FIELD":
        return "(" + render_expr(expr["source"]) + ")." + _ident(expr["field"])
    if op == "CONST":
        return _literal(expr["value"], expr["type"])
    if op == "AND":
        return "(" + " AND ".join(render_expr(x) for x in expr["operands"]) + ")"
    if op == "OR":
        return "(" + " OR ".join(render_expr(x) for x in expr["operands"]) + ")"
    if op == "NOT":
        return "(NOT " + render_expr(expr["operand"]) + ")"
    if op == "IS_NULL":
        return "(" + render_expr(expr["operand"]) + " IS NULL)"
    if op == "IS_NOT_NULL":
        return "(" + render_expr(expr["operand"]) + " IS NOT NULL)"
    if op == "IS_DISTINCT_FROM":
        return (
            "("
            + render_expr(expr["left"])
            + " IS DISTINCT FROM "
            + render_expr(expr["right"])
            + ")"
        )
    if op == "ADD":
        return (
            "(" + render_expr(expr["left"]) + " + " + render_expr(expr["right"]) + ")"
        )
    if op == "SUBTRACT":
        return (
            "(" + render_expr(expr["left"]) + " - " + render_expr(expr["right"]) + ")"
        )
    if op in ("EQ", "NE", "GT", "GTE", "LT", "LTE"):
        left = render_expr(expr["left"])
        right = render_expr(expr["right"])
        operator = {
            "EQ": "=",
            "NE": "<>",
            "GT": ">",
            "GTE": ">=",
            "LT": "<",
            "LTE": "<=",
        }[op]
        return "(" + left + " " + operator + " " + right + ")"
    if op == "COUNT":
        return (
            "(COALESCE(pg_catalog.array_length("
            + render_expr(expr["operand"])
            + ", 1), 0)::"
            + _type_sql("pg_catalog.bigint")
            + ")"
        )
    if op == "ARRAY_CONST":
        return _render_array_const(expr)
    if op == "CASE":
        return _render_case(expr)
    if op == "COMPOSITE_CONSTRUCT":
        return _render_composite(expr)
    if op == "CANONICAL_DIGEST":
        return _render_digest(expr)
    if op == "GEN_RANDOM_UUID":
        return "pg_catalog.gen_random_uuid()"
    if op == "CURRENT_XID32":
        return CURRENT_XID32_SQL
    if op == "SYSTEM_XMIN":
        row = expr["row"]
        if row.get("op") != "REF" or row.get("kind") != "LOCAL":
            raise ValueError("SYSTEM_XMIN requires a local exact-read record")
        return render_expr(row) + ".xmin"
    if op == "TRANSACTION_TIMESTAMP":
        return "pg_catalog.transaction_timestamp()"
    if op == "JSON_GET_CAST":
        return (
            "(("
            + render_expr(expr["source"])
            + " ->> "
            + _literal_text(expr["key"])
            + ")::"
            + _type_sql(expr["target_type"])
            + ")"
        )
    if op == "JSON_KEYS_EXACT":
        return _render_json_keys_exact(expr)
    if op == "SET_CONTAINS_KEY":
        return _render_set_contains_key(expr)
    if op == "SET_COVERS_KEYS":
        return _render_set_covers_keys(expr)
    if op == "MIN_FIELD":
        return (
            "(SELECT pg_catalog.min(s."
            + _ident(expr["field"])
            + ") FROM pg_catalog.unnest("
            + render_expr(expr["source"])
            + ") AS s)"
        )
    if op == "TIMESTAMP_ADD_MINUTES":
        return (
            "("
            + render_expr(expr["left"])
            + " + ("
            + render_expr(expr["right"])
            + " * pg_catalog.make_interval(mins => 1)))"
        )
    if op == "TIMESTAMP_ADD_SECONDS":
        return (
            "("
            + render_expr(expr["left"])
            + " + ("
            + render_expr(expr["right"])
            + " * pg_catalog.make_interval(secs => 1)))"
        )
    raise ValueError("unknown expression opcode " + op)


def digest_preimage(
    profile: str, operand_types: list[str], operand_values: list[Any]
) -> str:
    """Python reference encoder for a digest preimage (UTF-8 text)."""

    def canonical_text(value: Any, type_name: str) -> str:
        base = type_name[:-2] if type_name.endswith("[]") else type_name
        if base == "pg_catalog.boolean":
            return "true" if value else "false"
        if base == "pg_catalog.uuid":
            return str(value).lower()
        if base == "pg_catalog.timestamptz":
            dt = value
            return dt.strftime("%Y-%m-%dT%H:%M:%S.%f") + "Z"
        return str(value)

    def frame(type_name: str, value: Any, is_null: bool) -> str:
        type_bytes = type_name.encode("utf-8")
        if is_null:
            return f"{len(type_bytes)}:{type_name}:-1"
        value_text = canonical_text(value, type_name)
        value_bytes = value_text.encode("utf-8")
        return f"{len(type_bytes)}:{type_name}:{len(value_bytes)}:{value_text}"

    parts = [frame("profile", profile, False)]
    for type_name, value in zip(operand_types, operand_values, strict=True):
        parts.append(frame(type_name, value, value is None))
    return UNIT_SEPARATOR.join(parts)


# ---------------------------------------------------------------------------
# PL/pgSQL statement rendering
# ---------------------------------------------------------------------------

CARDINALITY_FAILURE = (
    "RAISE EXCEPTION USING ERRCODE = 'CF004', "
    "MESSAGE = 'required_row_missing_or_ambiguous'"
)

_LOCK_MODE_SQL = {
    "FOR_KEY_SHARE": "FOR KEY SHARE",
    "FOR_SHARE": "FOR SHARE",
    "FOR_NO_KEY_UPDATE": "FOR NO KEY UPDATE",
    "FOR_UPDATE": "FOR UPDATE",
}


def _order_sql(order_by: list[dict[str, Any]] | None, relation: str) -> str:
    if not order_by:
        return ""
    rel = _fabric(relation)
    parts = [
        rel + "." + _ident(row["column"]) + " " + row["direction"] for row in order_by
    ]
    return ", ".join(parts)


def _select_columns(relation: str, columns: list[str]) -> str:
    rel = _fabric(relation)
    return ", ".join(
        rel + "." + _ident(col) + (" AS " + _ident(col) if col == "xmin" else "")
        for col in columns
    )


def _relation_user_columns(ctx: dict[str, Any], relation: str) -> list[str]:
    """Ordered user columns (system ``xmin`` excluded) of a relation."""
    rid = _fabric(relation)
    rel_rows = ctx["effective"]["relation_rows"].get(rid)
    if rel_rows is not None:
        return [col["name"] for col in rel_rows["columns"] if col["name"] != "xmin"]
    col_types = ctx["effective"]["column_types"].get(rid, {})
    return [name for name in col_types if name != "xmin"]


def _verify_positional_row_projections(
    body: dict[str, Any], effective: dict[str, Any]
) -> None:
    """Fail closed when a row-composite assignment can shift column values."""
    ctx = {"effective": effective}
    for program in body["body_programs"]:
        for instruction in _walk_program_nodes(program):
            op = instruction["op"]
            operands = instruction["operands"]
            columns: list[str] | None = None
            if (
                op in {"SELECT_EXACT", "LOCK_EXACT"}
                and "output_symbol" in operands
                and "xmin" not in operands.get("columns", [])
            ):
                columns = operands.get("columns")
            elif (
                op in {"INSERT", "INSERT_OR_RELOAD_COMPARE", "UPDATE"}
                and "output_symbol" in operands
            ):
                columns = operands.get("returning_columns")
            if columns is None:
                continue
            expected = _relation_user_columns(ctx, operands["relation"])
            if columns != expected:
                raise ValueError(
                    "positional row projection order mismatch at "
                    + instruction["node_id"]
                )


def _exactly_one_block(body: str, indent: int) -> str:
    pad = "    " * indent
    return (
        pad
        + "BEGIN\n"
        + body
        + "\n"
        + pad
        + "EXCEPTION\n"
        + pad
        + "    WHEN NO_DATA_FOUND THEN\n"
        + pad
        + "        "
        + CARDINALITY_FAILURE
        + ";\n"
        + pad
        + "    WHEN TOO_MANY_ROWS THEN\n"
        + pad
        + "        "
        + CARDINALITY_FAILURE
        + ";\n"
        + pad
        + "END"
    )


def _emit_select_exact(
    node: dict[str, Any], ctx: dict[str, Any], indent: int
) -> list[str]:
    ops = node["operands"]
    rel = _fabric(ops["relation"])
    cols = _select_columns(ops["relation"], ops["columns"])
    pred = render_expr(ops["predicate"]) if "predicate" in ops else "TRUE"
    out = _symbol_ident(ops["output_symbol"])
    order = _order_sql(ops.get("order_by"), ops["relation"])
    order_clause = " ORDER BY " + order if order else ""
    body = (
        "SELECT "
        + cols
        + " INTO STRICT "
        + out
        + " FROM "
        + rel
        + " WHERE "
        + pred
        + order_clause
        + ";"
    )
    return [_exactly_one_block(body, indent) + ";"]


def _emit_lock_exact(
    node: dict[str, Any], ctx: dict[str, Any], indent: int
) -> list[str]:
    ops = node["operands"]
    rel = _fabric(ops["relation"])
    cols = _select_columns(ops["relation"], ops["columns"])
    pred = render_expr(ops["predicate"]) if "predicate" in ops else "TRUE"
    out = _symbol_ident(ops["output_symbol"])
    if ops["mode"] not in _LOCK_MODE_SQL:
        raise ValueError("unknown lock mode " + str(ops["mode"]))
    lock_sql = _LOCK_MODE_SQL[ops["mode"]]
    body = (
        "SELECT "
        + cols
        + " INTO STRICT "
        + out
        + " FROM "
        + rel
        + " WHERE "
        + pred
        + " "
        + lock_sql
        + ";"
    )
    return [_exactly_one_block(body, indent) + ";"]


def _emit_select_set(
    node: dict[str, Any], ctx: dict[str, Any], indent: int
) -> list[str]:
    ops = node["operands"]
    rel = _fabric(ops["relation"])
    out_type = _type_sql(ctx["symbol_types"].get(ops["output_symbol"], "text"))
    row_type = out_type[:-2] if out_type.endswith("[]") else out_type
    pred = render_expr(ops["predicate"]) if "predicate" in ops else "TRUE"
    out = _symbol_ident(ops["output_symbol"])
    projected = set(ops.get("columns", []))
    column_types = ctx["effective"]["column_types"].get(rel, {})
    row_items: list[str] = []
    for col in _relation_user_columns(ctx, ops["relation"]):
        if col in projected:
            row_items.append(rel + "." + _ident(col))
        else:
            row_items.append("NULL::" + _type_sql(column_types[col]))
    row_expr = "(ROW(" + ", ".join(row_items) + "))::" + row_type
    order = _order_sql(ops.get("order_by"), ops["relation"])
    order_clause = " ORDER BY " + order if order else ""
    sql = (
        "SELECT COALESCE(pg_catalog.array_agg("
        + row_expr
        + order_clause
        + "), ARRAY[]::"
        + out_type
        + ")\n"
        + "        INTO "
        + out
        + "\n"
        + "    FROM "
        + rel
        + " WHERE "
        + pred
        + ";"
    )
    pad = "    " * indent
    return [
        pad + "    " + line if i > 0 else pad + line
        for i, line in enumerate(sql.splitlines())
    ]


def _emit_let(node: dict[str, Any], ctx: dict[str, Any], indent: int) -> list[str]:
    ops = node["operands"]
    pad = "    " * indent
    return [
        pad
        + _symbol_ident(ops["output_symbol"])
        + " := "
        + render_expr(ops["expression"])
        + ";"
    ]


def _emit_assert(node: dict[str, Any], ctx: dict[str, Any], indent: int) -> list[str]:
    ops = node["operands"]
    failure = ctx["failures"][ops["failure_id"]]
    pad = "    " * indent
    pred = render_expr(ops["predicate"])
    return [
        pad + "IF NOT (" + pred + ") THEN",
        pad
        + "    RAISE EXCEPTION USING ERRCODE = '"
        + failure["sqlstate"]
        + "', MESSAGE = '"
        + failure["reason_code"]
        + "';",
        pad + "END IF;",
    ]


def _emit_raise(node: dict[str, Any], ctx: dict[str, Any], indent: int) -> list[str]:
    ops = node["operands"]
    failure = ctx["failures"][ops["failure_id"]]
    pad = "    " * indent
    return [
        pad
        + "RAISE EXCEPTION USING ERRCODE = '"
        + failure["sqlstate"]
        + "', MESSAGE = '"
        + failure["reason_code"]
        + "';"
    ]


def _emit_return_row(
    node: dict[str, Any], ctx: dict[str, Any], indent: int
) -> list[str]:
    pad = "    " * indent
    return [pad + "RETURN " + _symbol_ident(node["operands"]["source_symbol"]) + ";"]


def _emit_return_terminal(
    node: dict[str, Any], ctx: dict[str, Any], indent: int
) -> list[str]:
    pad = "    " * indent
    op = node["op"]
    value = {"RETURN_NEW": "NEW", "RETURN_OLD": "OLD", "RETURN_NULL": "NULL"}[op]
    return [pad + "RETURN " + value + ";"]


def _emit_call_support(
    node: dict[str, Any], ctx: dict[str, Any], indent: int
) -> list[str]:
    ops = node["operands"]
    pad = "    " * indent
    args = ", ".join(render_expr(arg) for arg in ops["arguments"])
    return [
        pad
        + _symbol_ident(ops["output_symbol"])
        + " := "
        + _fabric(ops["function"])
        + "("
        + args
        + ");"
    ]


def _emit_assert_isolation(
    node: dict[str, Any], ctx: dict[str, Any], indent: int
) -> list[str]:
    pad = "    " * indent
    required = node["operands"]["required"]
    expected = {
        "READ_COMMITTED": "read committed",
        "SERIALIZABLE": "serializable",
    }.get(required)
    if expected is None:
        raise ValueError("unknown isolation level " + required)
    failure = ctx["failures"]["F_STATE"]
    return [
        pad
        + "IF NOT (pg_catalog.current_setting('transaction_isolation') = '"
        + expected
        + "') THEN",
        pad
        + "    RAISE EXCEPTION USING ERRCODE = '"
        + failure["sqlstate"]
        + "', MESSAGE = '"
        + failure["reason_code"]
        + "';",
        pad + "END IF;",
    ]


def _emit_insert(node: dict[str, Any], ctx: dict[str, Any], indent: int) -> list[str]:
    ops = node["operands"]
    rel = _fabric(ops["relation"])
    columns = ", ".join(_ident(b["column"]) for b in ops["bindings"])
    values = ", ".join(render_expr(b["value"]) for b in ops["bindings"])
    returning = ", ".join(_ident(c) for c in ops["returning_columns"])
    pad = "    " * indent
    return [
        pad
        + "INSERT INTO "
        + rel
        + " ("
        + columns
        + ") VALUES ("
        + values
        + ")\n"
        + pad
        + "    RETURNING "
        + returning
        + " INTO "
        + _symbol_ident(ops["output_symbol"])
        + ";",
        pad + "IF NOT FOUND THEN",
        pad + "    " + CARDINALITY_FAILURE + ";",
        pad + "END IF;",
    ]


def _emit_update(node: dict[str, Any], ctx: dict[str, Any], indent: int) -> list[str]:
    ops = node["operands"]
    rel = _fabric(ops["relation"])
    sets = ", ".join(
        _ident(b["column"]) + " = " + render_expr(b["value"])
        for b in ops["set_bindings"]
    )
    pred = render_expr(ops["predicate"]) if "predicate" in ops else "TRUE"
    returning = ", ".join(_ident(c) for c in ops["returning_columns"])
    body = (
        "UPDATE "
        + rel
        + " SET "
        + sets
        + " WHERE "
        + pred
        + " RETURNING "
        + returning
        + " INTO STRICT "
        + _symbol_ident(ops["output_symbol"])
        + ";"
    )
    return [_exactly_one_block(body, indent) + ";"]


def _emit_delete_source(
    node: dict[str, Any], ctx: dict[str, Any], indent: int
) -> list[str]:
    ops = node["operands"]
    rel = _fabric(ops["relation"])
    pred = render_expr(ops["predicate"]) if "predicate" in ops else "TRUE"
    keys = ops["key_columns"]
    order = ", ".join(rel + "." + _ident(col) for col in keys)
    key_list = ", ".join(rel + "." + _ident(col) for col in keys)
    key_eq = " AND ".join("d." + _ident(col) + " = s." + _ident(col) for col in keys)
    out = _symbol_ident(ops["output_symbol"])
    pad = "    " * indent
    return [
        pad + "WITH selected_keys AS (",
        pad + "    SELECT " + key_list + " FROM " + rel,
        pad + "    WHERE " + pred,
        pad + "    ORDER BY " + order,
        pad + "    LIMIT " + str(ops["max_rows"]),
        pad + "), deleted AS (",
        pad + "    DELETE FROM " + rel + " AS d USING selected_keys AS s",
        pad + "    WHERE " + key_eq,
        pad + "    RETURNING d." + _ident(keys[0]),
        pad + ")",
        pad + "SELECT pg_catalog.count(*) INTO " + out + " FROM deleted;",
    ]


def _derive_conflict_constraint(
    effective: dict[str, Any], relation: str, conflict_key_columns: list[str]
) -> str:
    rows = effective["constraints"].get(_fabric(relation), [])
    # ON CONFLICT ON CONSTRAINT requires a real PostgreSQL constraint, not a
    # standalone unique index. The enforcing constraint must be exactly one at
    # the highest priority level.
    for kind in ("PRIMARY_KEY", "UNIQUE_CONSTRAINT"):
        matches = [
            row
            for row in rows
            if row["kind"] == kind and row["columns"] == list(conflict_key_columns)
        ]
        if len(matches) == 1:
            return matches[0]["name"]
        if len(matches) > 1:
            break
    raise ValueError(
        "conflict key does not map to exactly one enforcing constraint: " + relation
    )


def _emit_insert_or_reload_compare(
    node: dict[str, Any], ctx: dict[str, Any], indent: int
) -> list[str]:
    ops = node["operands"]
    rel = _fabric(ops["relation"])
    columns = ", ".join(_ident(b["column"]) for b in ops["bindings"])
    values = ", ".join(render_expr(b["value"]) for b in ops["bindings"])
    returning = ", ".join(_ident(c) for c in ops["returning_columns"])
    constraint_name = _derive_conflict_constraint(
        ctx["effective"], ops["relation"], ops["conflict_key_columns"]
    )
    conflict_predicates = []
    for col in ops["conflict_key_columns"]:
        value_expr = next(b["value"] for b in ops["bindings"] if b["column"] == col)
        conflict_predicates.append(
            rel + "." + _ident(col) + " = " + render_expr(value_expr)
        )
    winner_pred = render_expr(ops["winner_predicate"])
    reload_pred = " AND ".join(conflict_predicates + [winner_pred])
    winner_cols = ", ".join(rel + "." + _ident(c) for c in ops["winner_columns"])
    pad = "    " * indent
    lines = [
        pad
        + "INSERT INTO "
        + rel
        + " ("
        + columns
        + ") VALUES ("
        + values
        + ")\n"
        + pad
        + "    ON CONFLICT ON CONSTRAINT "
        + constraint_name
        + " DO NOTHING\n"
        + pad
        + "    RETURNING "
        + returning
        + " INTO "
        + _symbol_ident(ops["output_symbol"])
        + ";",
        pad + "IF NOT FOUND THEN",
        pad + "    BEGIN",
        pad
        + "        SELECT "
        + winner_cols
        + " INTO STRICT "
        + _symbol_ident(ops["output_symbol"])
        + "\n"
        + pad
        + "        FROM "
        + rel
        + "\n"
        + pad
        + "        WHERE "
        + reload_pred
        + ";",
        pad + "    EXCEPTION",
        pad + "        WHEN NO_DATA_FOUND THEN",
        pad + "            " + CARDINALITY_FAILURE + ";",
        pad + "        WHEN TOO_MANY_ROWS THEN",
        pad + "            " + CARDINALITY_FAILURE + ";",
        pad + "    END;",
        pad + "END IF;",
    ]
    return lines


def _emit_if(node: dict[str, Any], ctx: dict[str, Any], indent: int) -> list[str]:
    ops = node["operands"]
    pad = "    " * indent
    # Retry-marker elimination: condition is constant false and then is exactly
    # one PROPAGATE_RETRYABLE with the canonical 40001/40P01 no-internal-retry set.
    condition = ops["condition"]
    if (
        condition.get("op") == "CONST"
        and condition.get("type") == "pg_catalog.boolean"
        and condition.get("value") is False
        and len(ops["then"]) == 1
        and ops["then"][0]["op"] == "PROPAGATE_RETRYABLE"
    ):
        marker = ops["then"][0]["operands"]
        if (
            marker.get("sqlstates") != ["40001", "40P01"]
            or marker.get("internal_retry") is not False
        ):
            raise ValueError("non-canonical retry marker")
        return emit_nodes(ops["else"], indent, ctx)
    lines = [pad + "IF (" + render_expr(condition) + ") THEN"]
    lines.extend(emit_nodes(ops["then"], indent + 1, ctx))
    lines.append(pad + "ELSE")
    lines.extend(emit_nodes(ops["else"], indent + 1, ctx))
    lines.append(pad + "END IF;")
    return lines


def _emit_switch_tg_op(
    node: dict[str, Any], ctx: dict[str, Any], indent: int
) -> list[str]:
    ops = node["operands"]
    pad = "    " * indent
    lines: list[str] = []
    for idx, arm in enumerate(ops["arms"]):
        keyword = "IF" if idx == 0 else "ELSIF"
        lines.append(pad + keyword + " (TG_OP = '" + arm["tg_op"] + "') THEN")
        lines.extend(emit_nodes(arm["nodes"], indent + 1, ctx))
    lines.append(pad + "ELSE")
    lines.extend(emit_nodes(ops["default"], indent + 1, ctx))
    lines.append(pad + "END IF;")
    return lines


def _emit_for_each(node: dict[str, Any], ctx: dict[str, Any], indent: int) -> list[str]:
    ops = node["operands"]
    pad = "    " * indent
    lines = [
        pad
        + "FOREACH "
        + _ident(ops["row_symbol"])
        + " IN ARRAY "
        + _ident(ops["set_symbol"])
        + " LOOP"
    ]
    lines.extend(emit_nodes(ops["nodes"], indent + 1, ctx))
    lines.append(pad + "END LOOP;")
    return lines


def emit_nodes(
    nodes: list[dict[str, Any]], indent: int, ctx: dict[str, Any]
) -> list[str]:
    lines: list[str] = []
    for node in nodes:
        op = node["op"]
        if op == "SELECT_EXACT":
            lines.extend(_emit_select_exact(node, ctx, indent))
        elif op == "LOCK_EXACT":
            lines.extend(_emit_lock_exact(node, ctx, indent))
        elif op == "SELECT_SET":
            lines.extend(_emit_select_set(node, ctx, indent))
        elif op == "LET":
            lines.extend(_emit_let(node, ctx, indent))
        elif op == "ASSERT":
            lines.extend(_emit_assert(node, ctx, indent))
        elif op == "RAISE":
            lines.extend(_emit_raise(node, ctx, indent))
        elif op == "RETURN_ROW":
            lines.extend(_emit_return_row(node, ctx, indent))
        elif op == "RETURN_COMPOSITE":
            lines.extend(_emit_return_row(node, ctx, indent))
        elif op in ("RETURN_NEW", "RETURN_OLD", "RETURN_NULL"):
            lines.extend(_emit_return_terminal(node, ctx, indent))
        elif op == "CALL_SUPPORT":
            lines.extend(_emit_call_support(node, ctx, indent))
        elif op == "ASSERT_ISOLATION":
            lines.extend(_emit_assert_isolation(node, ctx, indent))
        elif op == "INSERT":
            lines.extend(_emit_insert(node, ctx, indent))
        elif op == "INSERT_OR_RELOAD_COMPARE":
            lines.extend(_emit_insert_or_reload_compare(node, ctx, indent))
        elif op == "UPDATE":
            lines.extend(_emit_update(node, ctx, indent))
        elif op == "DELETE_SOURCE":
            lines.extend(_emit_delete_source(node, ctx, indent))
        elif op == "IF":
            lines.extend(_emit_if(node, ctx, indent))
        elif op == "SWITCH_TG_OP":
            lines.extend(_emit_switch_tg_op(node, ctx, indent))
        elif op == "FOR_EACH":
            lines.extend(_emit_for_each(node, ctx, indent))
        elif op == "PROPAGATE_RETRYABLE":
            raise ValueError("retry marker not eliminated")
        else:
            raise ValueError("unknown instruction opcode " + op)
    return lines


def _walk_nodes(nodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for node in nodes:
        out.append(node)
        op = node["op"]
        ops = node["operands"]
        if op == "IF":
            out.extend(_walk_nodes(ops["then"]))
            out.extend(_walk_nodes(ops["else"]))
        elif op == "SWITCH_TG_OP":
            for arm in ops["arms"]:
                out.extend(_walk_nodes(arm["nodes"]))
            out.extend(_walk_nodes(ops["default"]))
        elif op == "FOR_EACH":
            out.extend(_walk_nodes(ops["nodes"]))
    return out


def _walk_program_nodes(program: dict[str, Any]) -> list[dict[str, Any]]:
    return _walk_nodes(program["ast"]["nodes"])


def _walk_program_expressions(program: dict[str, Any]) -> list[dict[str, Any]]:
    def walk(value: Any) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        if isinstance(value, dict):
            if "op" in value and "node_id" not in value:
                out.append(value)
            for child in value.values():
                out.extend(walk(child))
        elif isinstance(value, list):
            for child in value:
                out.extend(walk(child))
        return out

    return walk(program["ast"])


# ---------------------------------------------------------------------------
# Function and phase rendering
# ---------------------------------------------------------------------------

DOLLAR_TAG = "durability_inert"


def _split_qualified(identifier: str) -> tuple[str, str]:
    return identifier.rsplit(".", 1)


def _render_signature_args(inputs: list[dict[str, Any]]) -> str:
    return ", ".join(
        _symbol_ident(item["name"]) + " " + _type_sql(item["type"]) for item in inputs
    )


def _xmin_read_symbols(program: dict[str, Any]) -> set[str]:
    """Symbols filled by an exact read whose projection includes system xmin."""
    out: set[str] = set()
    for node in _walk_program_nodes(program):
        if node["op"] == "SELECT_EXACT":
            ops = node["operands"]
            if "xmin" in ops.get("columns", []):
                out.add(ops["output_symbol"])
    return out


def _render_function_body(program: dict[str, Any], ctx: dict[str, Any]) -> str:
    symbols = program["symbols"]
    physical_symbols = [_symbol_ident(sym["id"]) for sym in symbols]
    if len(set(physical_symbols)) != len(physical_symbols):
        raise ValueError("physical PL/pgSQL symbol alias collision")
    ctx["symbol_types"] = {sym["id"]: sym["type"] for sym in symbols}
    xmin_syms = _xmin_read_symbols(program)
    decls: list[str] = []
    for sym in symbols:
        if sym["source"].get("kind") == "INPUT":
            continue
        if sym["id"] in xmin_syms:
            # System xmin is not a member of a table composite; a record local
            # preserves product/system-column projections for SYSTEM_XMIN reads.
            decls.append(_symbol_ident(sym["id"]) + " record;")
        else:
            decls.append(_symbol_ident(sym["id"]) + " " + _type_sql(sym["type"]) + ";")
    lines = ["DECLARE"]
    lines.extend("    " + item for item in decls)
    lines.append("BEGIN")
    lines.extend(emit_nodes(program["ast"]["nodes"], 1, ctx))
    lines.append("END;")
    return "\n".join(lines)


def _render_function_attributes(signature: dict[str, Any]) -> str:
    parts = [
        "LANGUAGE " + signature["language"],
        signature["volatility"],
    ]
    if signature.get("security_definer"):
        parts.append("SECURITY DEFINER")
    if signature.get("strict"):
        parts.append("STRICT")
    parts.append("PARALLEL " + signature["parallel_safety"])
    parts.append(
        "SET search_path = " + ", ".join(signature.get("search_path", ["pg_catalog"]))
    )
    return " ".join(parts) + ";"


def _render_program_function(
    program: dict[str, Any], signature: dict[str, Any], ctx: dict[str, Any]
) -> str:
    schema, fname = _split_qualified(program["id"])
    args = _render_signature_args(signature["inputs"])
    ret = _type_sql(signature["output"]["type"])
    body = _render_function_body(program, ctx)
    lines = [
        "CREATE FUNCTION " + schema + "." + _ident(fname) + "(" + args + ")",
        "RETURNS " + ret,
        "AS $" + DOLLAR_TAG + "$",
        body,
        "$" + DOLLAR_TAG + "$",
        _render_function_attributes(signature),
    ]
    owner = signature.get("owner")
    if owner:
        lines.append(
            "ALTER FUNCTION "
            + schema
            + "."
            + _ident(fname)
            + "("
            + args
            + ") OWNER TO "
            + _role_name(owner)
            + ";"
        )
    return "\n".join(lines)


def _render_support_function(effective: dict[str, Any]) -> str:
    signature = effective["signatures"]["support"]
    schema, fname = _split_qualified(signature["id"])
    args = _render_signature_args(signature["inputs"])
    body = effective["support_functions"][0]["body_sql"]
    owner = signature.get("owner")
    lines = [
        "CREATE FUNCTION " + schema + "." + _ident(fname) + "(" + args + ")",
        "RETURNS " + _type_sql(signature["output"]["type"]),
        "AS $" + DOLLAR_TAG + "$",
        "    " + body + ";",
        "$" + DOLLAR_TAG + "$",
        "LANGUAGE sql STABLE SECURITY DEFINER STRICT PARALLEL RESTRICTED "
        "SET search_path = pg_catalog, emr4_context_fabric;",
    ]
    if owner:
        lines.append(
            "ALTER FUNCTION "
            + schema
            + "."
            + _ident(fname)
            + "("
            + args
            + ") OWNER TO "
            + _role_name(owner)
            + ";"
        )
    return "\n".join(lines)


def _role_name(qualified_role: str) -> str:
    return qualified_role.rsplit(".", 1)[-1]


def _render_roles(effective: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    for role in effective["roles"]:
        name = _role_name(role["role"])
        flags = []
        flags.append("LOGIN" if role["login"] else "NOLOGIN")
        flags.append("NOINHERIT" if role["noinherit"] else "INHERIT")
        flags.append("CREATEDB" if role["createdb"] else "NOCREATEDB")
        flags.append("CREATEROLE" if role["createrole"] else "NOCREATEROLE")
        flags.append("REPLICATION" if role["replication"] else "NOREPLICATION")
        flags.append("BYPASSRLS" if not role["nobypassrls"] else "NOBYPASSRLS")
        lines.append("CREATE ROLE " + name + " " + " ".join(flags) + ";")
    return lines


def _ordered_composites(composites: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return the stable dependency-safe PostgreSQL composite CREATE order."""
    by_name = {row["name"]: row for row in composites}
    if len(by_name) != len(composites):
        raise ValueError("duplicate composite type")
    dependencies: dict[str, set[str]] = {}
    for row in composites:
        refs: set[str] = set()
        for field in row["fields"]:
            data_type = field["data_type"]
            while data_type.endswith("[]"):
                data_type = data_type[:-2]
            candidate = _unqualified(data_type)
            if candidate in by_name:
                refs.add(candidate)
        dependencies[row["name"]] = refs

    remaining = list(composites)
    emitted: set[str] = set()
    ordered: list[dict[str, Any]] = []
    while remaining:
        for index, row in enumerate(remaining):
            if dependencies[row["name"]].issubset(emitted):
                ordered.append(row)
                emitted.add(row["name"])
                remaining.pop(index)
                break
        else:
            blocked = ",".join(row["name"] for row in remaining)
            raise ValueError("composite dependency cycle: " + blocked)
    return ordered


def _render_types(effective: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    type_cat = effective["effective_structural"]["type_catalogue"]
    for domain in type_cat["domains"]:
        lines.append(
            "CREATE DOMAIN "
            + SCHEMA_NAME
            + "."
            + _ident(domain["name"])
            + " AS "
            + _type_sql(domain["base_type"])
        )
        if domain["not_null_values"]:
            lines.append("    NOT NULL")
        lines.append(
            "    CONSTRAINT "
            + _ident(domain["name"] + "_check")
            + " CHECK ("
            + domain["check_sql"]
            + ");"
        )
    for enum in type_cat["enums"]:
        values = ", ".join(_literal_text(value) for value in enum["values"])
        lines.append(
            "CREATE TYPE "
            + SCHEMA_NAME
            + "."
            + _ident(enum["name"])
            + " AS ENUM ("
            + values
            + ");"
        )
    for composite in _ordered_composites(type_cat["composites"]):
        fields = ",\n    ".join(
            _ident(item["name"]) + " " + _type_sql(item["data_type"])
            for item in composite["fields"]
        )
        lines.append(
            "CREATE TYPE "
            + SCHEMA_NAME
            + "."
            + _ident(composite["name"])
            + " AS (\n    "
            + fields
            + "\n);"
        )
    return lines


def _render_relations(effective: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    relations = effective["effective_structural"]["relation_catalogue"]["relations"]

    # Establish every relation before any constraint can name another one.
    # This is cycle-safe and keeps the accepted catalogue order within each
    # statement family.
    for rel in relations:
        rid = _fabric(rel["name"])
        column_types = effective["column_types"][rid]
        col_lines = []
        for col in rel["columns"]:
            if col["name"] == "xmin":
                if col != {
                    "name": "xmin",
                    "data_type": "xid",
                    "nullable": False,
                    "default_sql": None,
                }:
                    raise ValueError("modeled system xmin shape drift")
                # xmin is an implicitly defined PostgreSQL system column.  It
                # remains in the typed model for provenance reads but must not
                # be emitted as a user-defined CREATE TABLE column.
                continue
            colname = _ident(col["name"])
            coltype = _type_sql(column_types[col["name"]])
            null_sql = "" if col["nullable"] else " NOT NULL"
            default_sql = ""
            if col.get("default_sql"):
                default_sql = " DEFAULT " + col["default_sql"]
            col_lines.append("    " + colname + " " + coltype + null_sql + default_sql)
        lines.append("CREATE TABLE " + rid + " (")
        lines.append(",\n".join(col_lines))
        lines.append(");")

    # Referenced keys must all exist before any foreign key is admitted.
    for rel in relations:
        rid = _fabric(rel["name"])
        pk = rel.get("primary_key")
        if pk and pk.get("columns"):
            cols = ", ".join(_ident(c) for c in pk["columns"])
            lines.append(
                "ALTER TABLE "
                + rid
                + " ADD CONSTRAINT "
                + _ident(pk["name"])
                + " PRIMARY KEY ("
                + cols
                + ");"
            )
        for unique in rel.get("unique_constraints", []):
            cols = ", ".join(_ident(c) for c in unique["columns"])
            if unique["kind"] == "UNIQUE_INDEX":
                predicate = ""
                if unique.get("predicate_sql"):
                    predicate = " WHERE (" + unique["predicate_sql"] + ")"
                lines.append(
                    "CREATE UNIQUE INDEX "
                    + _ident(unique["name"])
                    + " ON "
                    + rid
                    + " ("
                    + cols
                    + ")"
                    + predicate
                    + ";"
                )
            else:
                lines.append(
                    "ALTER TABLE "
                    + rid
                    + " ADD CONSTRAINT "
                    + _ident(unique["name"])
                    + " UNIQUE ("
                    + cols
                    + ");"
                )

    for rel in relations:
        rid = _fabric(rel["name"])
        for fk in rel.get("foreign_keys", []):
            cols = ", ".join(_ident(c) for c in fk["columns"])
            refs = ", ".join(_ident(c) for c in fk["references_columns"])
            ref_rel = _fabric(fk["references_relation"])
            deferrable = ""
            if fk.get("deferrable"):
                deferrable = " DEFERRABLE"
            lines.append(
                "ALTER TABLE "
                + rid
                + " ADD CONSTRAINT "
                + _ident(fk["name"])
                + " FOREIGN KEY ("
                + cols
                + ") REFERENCES "
                + ref_rel
                + " ("
                + refs
                + ") ON DELETE "
                + fk["on_delete"]
                + deferrable
                + ";"
            )

    for rel in relations:
        rid = _fabric(rel["name"])
        for check in rel.get("check_constraints", []):
            lines.append(
                "ALTER TABLE "
                + rid
                + " ADD CONSTRAINT "
                + _ident(check["name"])
                + " CHECK ("
                + check["expression_sql"]
                + ");"
            )
    return lines


def _render_rls(effective: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    for rel in effective["effective_structural"]["relation_catalogue"]["relations"]:
        rid = _fabric(rel["name"])
        if rel["rls_enabled"]:
            lines.append("ALTER TABLE " + rid + " ENABLE ROW LEVEL SECURITY;")
        if rel["rls_forced"]:
            lines.append("ALTER TABLE " + rid + " FORCE ROW LEVEL SECURITY;")
    for pol in effective["rls_policies"]:
        relation = _fabric(pol["relation"])
        roles = ", ".join(pol["roles"])
        command = " FOR " + pol["command"] if pol["command"] != "ALL" else ""
        parts = [
            "CREATE POLICY "
            + _ident(pol["id"])
            + " ON "
            + relation
            + command
            + " TO "
            + roles
        ]
        if pol.get("using_sql"):
            parts.append("    USING (" + pol["using_sql"] + ")")
        if pol.get("with_check_sql"):
            parts.append("    WITH CHECK (" + pol["with_check_sql"] + ")")
        lines.append("\n".join(parts) + ";")
    return lines


def _render_fabric_owner_transfers(effective: dict[str, Any]) -> list[str]:
    """Emit exact final fabric owners; application objects are never targets."""
    lines: list[str] = []
    type_cat = effective["effective_structural"]["type_catalogue"]
    for domain in type_cat["domains"]:
        lines.append(
            "ALTER DOMAIN "
            + SCHEMA_NAME
            + "."
            + _ident(domain["name"])
            + " OWNER TO context_schema_owner;"
        )
    for row in [*type_cat["enums"], *type_cat["composites"]]:
        lines.append(
            "ALTER TYPE "
            + SCHEMA_NAME
            + "."
            + _ident(row["name"])
            + " OWNER TO context_schema_owner;"
        )
    for relation in effective["effective_structural"]["relation_catalogue"][
        "relations"
    ]:
        lines.append(
            "ALTER TABLE "
            + _fabric(relation["name"])
            + " OWNER TO context_schema_owner;"
        )
    return lines


def _render_revokes_grants(effective: dict[str, Any], ctx: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    lines.append("REVOKE ALL ON SCHEMA " + SCHEMA_NAME + " FROM PUBLIC;")
    for rid in sorted(effective["relations"]):
        if rid.startswith("public."):
            continue
        lines.append("REVOKE ALL ON TABLE " + rid + " FROM PUBLIC;")
    signatures = effective["signatures"]
    func_ids = [signatures["support"]["id"]]
    func_ids.extend(entry["id"] for entry in signatures["entry_points"])
    func_ids.extend(trig["id"] for trig in signatures["trigger_functions"])
    for fid in func_ids:
        schema, fname = _split_qualified(fid)
        sig = _signature_by_id(effective, fid)
        args = _render_signature_args(sig["inputs"])
        lines.append(
            "REVOKE ALL ON FUNCTION "
            + schema
            + "."
            + _ident(fname)
            + "("
            + args
            + ") FROM PUBLIC;"
        )
    for role in effective["roles"]:
        name = _role_name(role["role"])
        lines.append("GRANT USAGE ON SCHEMA " + SCHEMA_NAME + " TO " + name + ";")
        for rel in role.get("direct_table_select", []):
            lines.append("GRANT SELECT ON TABLE " + rel + " TO " + name + ";")
        for grant in role.get("direct_table_dml", []):
            privileges = ", ".join(grant["privileges"])
            lines.append(
                "GRANT "
                + privileges
                + " ON TABLE "
                + grant["relation"]
                + " TO "
                + name
                + ";"
            )
        for fid in role.get("execute_entry_points", []):
            schema, fname = _split_qualified(fid)
            sig = _signature_by_id(effective, fid)
            args = _render_signature_args(sig["inputs"])
            lines.append(
                "GRANT EXECUTE ON FUNCTION "
                + schema
                + "."
                + _ident(fname)
                + "("
                + args
                + ") TO "
                + name
                + ";"
            )
    support = signatures["support"]
    for role in support.get("execute_roles", []):
        name = _role_name(role)
        schema, fname = _split_qualified(support["id"])
        args = _render_signature_args(support["inputs"])
        lines.append(
            "GRANT EXECUTE ON FUNCTION "
            + schema
            + "."
            + _ident(fname)
            + "("
            + args
            + ") TO "
            + name
            + ";"
        )
    return lines


def _signature_by_id(effective: dict[str, Any], function_id: str) -> dict[str, Any]:
    signatures = effective["signatures"]
    if function_id == signatures["support"]["id"]:
        return signatures["support"]
    for entry in signatures["entry_points"]:
        if entry["id"] == function_id:
            return entry
    for trig in signatures["trigger_functions"]:
        if trig["id"] == function_id:
            return trig
    raise ValueError("unknown function id " + function_id)


def _render_phase6_comments(effective: dict[str, Any]) -> list[str]:
    rel_count = len([r for r in effective["relations"] if not r.startswith("public.")])
    return [
        "-- phase 6 non-executed catalogue and privilege expectation comments",
        "-- postgresql_major: 16",
        "-- fabric_schema: " + SCHEMA_NAME,
        "-- fabric_relations: " + str(rel_count),
        "-- rls_policies: " + str(len(effective["rls_policies"])),
        "-- roles: " + str(len(effective["roles"])),
        "-- entry_points: 9",
        "-- trigger_functions: 14",
        "-- trigger_declarations: 14",
        "-- effective_programs: 23",
        "-- paired_guard_dependencies: 3",
        "-- fabric_type_owner: context_schema_owner",
        "-- fabric_relation_owner: context_schema_owner",
        "-- support_functions: 1",
        "-- application_relations_reference_only: 4",
        "-- trigger_function_runtime_execute: 0",
    ]


def _verify_opcode_populations(body: dict[str, Any]) -> None:
    declared_instructions = set(body["typed_ir_contract"]["instruction_opcodes"])
    declared_expressions = set(body["typed_ir_contract"]["expression_opcodes"])
    observed_instructions: set[str] = set()
    observed_expressions: set[str] = set()
    for program in body["body_programs"]:
        for node in _walk_program_nodes(program):
            observed_instructions.add(node["op"])
        for expr in _walk_program_expressions(program):
            if expr["op"] == "SEQUENCE":
                continue
            observed_expressions.add(expr["op"])
            if (
                expr.get("op") == "REF"
                and expr.get("kind") == "SYSTEM"
                and expr.get("field") == "SESSION_USER"
            ):
                observed_expressions.add("SESSION_USER")
    if len(declared_instructions) != 22:
        raise ValueError("instruction opcode declaration count mismatch")
    if len(declared_expressions) != 34:
        raise ValueError("expression opcode declaration count mismatch")
    if observed_instructions != declared_instructions - {"DERIVE_BINDING"}:
        raise ValueError("observed instruction population mismatch")
    if observed_expressions != declared_expressions:
        raise ValueError("observed expression population mismatch")


# ---------------------------------------------------------------------------
# Render plan, manifest and main render
# ---------------------------------------------------------------------------

RENDERER_VERSION = "2.0.10"
PHASE_HEADERS: dict[int, str] = {
    1: (
        "PHASE 1 -- exact role/schema/type/relation/constraint/index/forced-RLS "
        "catalogue and the sole support helper"
    ),
    2: "PHASE 2 -- the nine entry-point functions in accepted renderer order",
    3: "PHASE 3 -- the fourteen effective trigger functions in recovered renderer order",
    4: "PHASE 4 -- the fourteen effective trigger declarations in recovered order",
    5: (
        "PHASE 5 -- PUBLIC revocation followed by the exact owner, receiver and "
        "runtime grants"
    ),
    6: "PHASE 6 -- non-executed catalogue and privilege expectation comments",
}


def _phase_separator(phase: int) -> str:
    return "-- " + "=" * 74


def _phase_header(phase: int) -> str:
    return "-- " + PHASE_HEADERS[phase]


def _phase_end(phase: int) -> str:
    return "-- END " + PHASE_HEADERS[phase]


def _render_phase1(
    effective: dict[str, Any], ctx: dict[str, Any], plan: dict[str, Any]
) -> list[str]:
    lines: list[str] = []
    lines.extend(_render_phase1_roles(effective, plan))
    lines.append(
        "CREATE SCHEMA " + SCHEMA_NAME + " AUTHORIZATION context_schema_owner;"
    )
    plan["ordered_nodes"].append({"kind": "SCHEMA", "identifier": SCHEMA_NAME})
    type_lines = _render_types(effective)
    lines.extend(type_lines)
    for line in type_lines:
        if line.startswith("CREATE DOMAIN "):
            plan["ordered_nodes"].append(
                {"kind": "DOMAIN", "identifier": line.split()[2]}
            )
        elif line.startswith("CREATE TYPE ") and " AS ENUM" in line:
            plan["ordered_nodes"].append(
                {"kind": "ENUM", "identifier": line.split()[2]}
            )
        elif line.startswith("CREATE TYPE ") and " AS (" in line:
            plan["ordered_nodes"].append(
                {"kind": "COMPOSITE", "identifier": line.split()[2]}
            )
    rel_lines = _render_relations(effective)
    lines.extend(rel_lines)
    for line in rel_lines:
        if line.startswith("CREATE TABLE "):
            plan["ordered_nodes"].append(
                {"kind": "TABLE", "identifier": line.split()[2]}
            )
        elif line.startswith("ALTER TABLE ") and " ADD CONSTRAINT " in line:
            rid = line.split()[2]
            name = line.split(" ADD CONSTRAINT ")[1].split(" ")[0]
            plan["ordered_nodes"].append(
                {"kind": "CONSTRAINT", "identifier": rid + "." + name}
            )
        elif line.startswith("CREATE UNIQUE INDEX "):
            name = line.split()[3]
            plan["ordered_nodes"].append({"kind": "UNIQUE_INDEX", "identifier": name})
    support = effective["support_functions"][0]
    lines.extend(_render_support_function(effective).splitlines())
    plan["ordered_nodes"].append(
        {"kind": "SUPPORT_FUNCTION", "identifier": FABRIC + support["name"]}
    )
    rls_lines = _render_rls(effective)
    lines.extend(rls_lines)
    for line in rls_lines:
        if line.startswith("ALTER TABLE ") and " ENABLE ROW LEVEL SECURITY" in line:
            plan["ordered_nodes"].append(
                {"kind": "RLS_ENABLE", "identifier": line.split()[2]}
            )
        elif line.startswith("ALTER TABLE ") and " FORCE ROW LEVEL SECURITY" in line:
            plan["ordered_nodes"].append(
                {"kind": "RLS_FORCE", "identifier": line.split()[2]}
            )
        elif line.startswith("CREATE POLICY "):
            plan["ordered_nodes"].append(
                {"kind": "RLS_POLICY", "identifier": line.split()[2]}
            )
    owner_lines = _render_fabric_owner_transfers(effective)
    lines.extend(owner_lines)
    for line in owner_lines:
        kind = "RELATION_OWNER" if line.startswith("ALTER TABLE ") else "TYPE_OWNER"
        plan["ordered_nodes"].append({"kind": kind, "identifier": line.split()[2]})
    return lines


def _render_phase2(
    effective: dict[str, Any], ctx: dict[str, Any], plan: dict[str, Any]
) -> list[str]:
    lines: list[str] = []
    entries = effective["signatures"]["entry_points"]
    body_programs = {prog["id"]: prog for prog in ctx["body"]["body_programs"]}
    for entry in entries:
        program = body_programs[entry["id"]]
        lines.append(_render_program_function(program, entry, ctx))
        plan["ordered_nodes"].append({"kind": "ENTRY_POINT", "identifier": entry["id"]})
    return lines


def _render_phase3(
    effective: dict[str, Any], ctx: dict[str, Any], plan: dict[str, Any]
) -> list[str]:
    lines: list[str] = []
    triggers = effective["signatures"]["trigger_functions"]
    body_programs = {prog["id"]: prog for prog in ctx["body"]["body_programs"]}
    for trig in triggers:
        program = body_programs[trig["id"]]
        lines.append(_render_program_function(program, trig, ctx))
        plan["ordered_nodes"].append(
            {"kind": "TRIGGER_FUNCTION", "identifier": trig["id"]}
        )
    return lines


def _render_phase4(
    effective: dict[str, Any], ctx: dict[str, Any], plan: dict[str, Any]
) -> list[str]:
    lines: list[str] = []
    for declaration in effective["trigger_declarations"]:
        relation = declaration["relation"]
        events = " OR ".join(declaration["events"])
        timing = declaration["timing"]
        level = "ROW" if declaration["row_level"] else "STATEMENT"
        schema, fname = _split_qualified(declaration["function"])
        if declaration["deferrable"]:
            if timing != "AFTER" or level != "ROW":
                raise ValueError("constraint trigger must be AFTER FOR EACH ROW")
            initial = (
                "INITIALLY DEFERRED"
                if declaration["initially_deferred"]
                else "INITIALLY IMMEDIATE"
            )
            lines.append(
                "CREATE CONSTRAINT TRIGGER "
                + _ident(declaration["id"])
                + " "
                + timing
                + " "
                + events
                + " ON "
                + relation
                + "\n    DEFERRABLE "
                + initial
                + "\n    FOR EACH ROW\n    EXECUTE FUNCTION "
                + schema
                + "."
                + _ident(fname)
                + "();"
            )
        else:
            if declaration["initially_deferred"]:
                raise ValueError("non-deferrable trigger cannot be initially deferred")
            lines.append(
                "CREATE TRIGGER "
                + _ident(declaration["id"])
                + " "
                + timing
                + " "
                + events
                + " ON "
                + relation
                + "\n    FOR EACH "
                + level
                + "\n    EXECUTE FUNCTION "
                + schema
                + "."
                + _ident(fname)
                + "();"
            )
        plan["ordered_nodes"].append(
            {"kind": "TRIGGER_DECLARATION", "identifier": declaration["id"]}
        )
    return lines


def _render_phase1_roles(effective: dict[str, Any], plan: dict[str, Any]) -> list[str]:
    lines = _render_roles(effective)
    for line in lines:
        if line.startswith("CREATE ROLE "):
            plan["ordered_nodes"].append(
                {"kind": "ROLE", "identifier": line.split()[2]}
            )
    return lines


def _collect_digest_profiles(body: dict[str, Any]) -> list[dict[str, Any]]:
    profiles: dict[str, list[list[str]]] = {}
    for program in body["body_programs"]:
        for expr in _walk_program_expressions(program):
            if expr.get("op") == "CANONICAL_DIGEST":
                prof = expr["profile"]
                tup = [operand["type"] for operand in expr["operands"]]
                profiles.setdefault(prof, [])
                if tup not in profiles[prof]:
                    profiles[prof].append(tup)
    out = []
    for prof, tuples in sorted(profiles.items()):
        for tup in sorted(tuples):
            out.append({"profile": prof, "operand_types": tup})
    return out


def _digest_vectors(body: dict[str, Any]) -> list[dict[str, Any]]:
    """Authored-synthetic digest edge vectors for static comparison."""
    vectors: list[dict[str, Any]] = []
    profiles = _collect_digest_profiles(body)
    if profiles:
        p = profiles[0]
        types = p["operand_types"]
        null_row = [None for _ in types]
        vectors.append(
            {
                "profile": p["profile"],
                "operand_types": types,
                "values": null_row,
                "preimage": digest_preimage(p["profile"], types, null_row),
            }
        )
    vectors.append(
        {
            "profile": "edge.null_vs_empty",
            "operand_types": ["pg_catalog.text"],
            "values": [None],
            "preimage": digest_preimage(
                "edge.null_vs_empty", ["pg_catalog.text"], [None]
            ),
        }
    )
    vectors.append(
        {
            "profile": "edge.empty_text",
            "operand_types": ["pg_catalog.text"],
            "values": [""],
            "preimage": digest_preimage("edge.empty_text", ["pg_catalog.text"], [""]),
        }
    )
    vectors.append(
        {
            "profile": "edge.uuid_case",
            "operand_types": ["pg_catalog.uuid"],
            "values": ["A0EEBC99-9C0B-4EF8-BB6D-6BB9BD380A11"],
            "preimage": digest_preimage(
                "edge.uuid_case",
                ["pg_catalog.uuid"],
                ["A0EEBC99-9C0B-4EF8-BB6D-6BB9BD380A11"],
            ),
        }
    )
    vectors.append(
        {
            "profile": "edge.boolean",
            "operand_types": ["pg_catalog.boolean"],
            "values": [True],
            "preimage": digest_preimage("edge.boolean", ["pg_catalog.boolean"], [True]),
        }
    )
    return vectors


def _phase_line_spans(sql_text: str) -> dict[str, dict[str, int]]:
    lines = sql_text.splitlines()
    spans: dict[str, dict[str, int]] = {}
    for line in lines:
        if line.startswith("-- PHASE "):
            phase = line.split()[2]
            spans.setdefault(phase, {})
        elif line.startswith("-- END PHASE "):
            phase = line.split()[3]
            spans.setdefault(phase, {})
    for idx, line in enumerate(lines, start=1):
        if line.startswith("-- PHASE "):
            phase = line.split()[2]
            spans.setdefault(phase, {})["start"] = idx
        elif line.startswith("-- END PHASE "):
            phase = line.split()[3]
            spans.setdefault(phase, {})["end"] = idx
    return spans


def build_render_manifest(
    effective: dict[str, Any], sql_text: str, plan: dict[str, Any], ctx: dict[str, Any]
) -> dict[str, Any]:
    body = ctx["body"]
    effective_digest_payload = {
        "relations": effective["relations"],
        "column_types": effective["column_types"],
        "composite_fields": effective["composite_fields"],
        "types": effective["types"],
        "roles": effective["roles"],
        "trigger_declarations": effective["trigger_declarations"],
        "signatures": effective["signatures"],
        "representability_recovery": RECOVERY_SPEC,
    }
    effective_digest = canonical_digest(effective_digest_payload, "__none__")
    sql_bytes = sql_text.encode("utf-8")
    statement_count = len(_extract_top_level_statements(sql_text))
    body_program_accounting = []
    for program in body["body_programs"]:
        node_count = len(_walk_program_nodes(program))
        expr_count = len(_walk_program_expressions(program)) - 1
        instr_counts: dict[str, int] = {}
        for node in _walk_program_nodes(program):
            instr_counts[node["op"]] = instr_counts.get(node["op"], 0) + 1
        body_program_accounting.append(
            {
                "id": program["id"],
                "kind": program["kind"],
                "node_count": node_count,
                "expression_count": expr_count,
                "instruction_counts": instr_counts,
            }
        )
    return {
        "schema_version": "raisa.context_fabric.durability_inert_ddl_rehearsal.render_manifest.v1",
        "renderer_version": RENDERER_VERSION,
        "artifact": str(SQL_INERT_PATH.relative_to(ROOT)).replace("\\", "/"),
        "sql_sha256": "sha256:" + sha256_hex(sql_bytes),
        "sql_byte_count": len(sql_bytes),
        "statement_count": statement_count,
        "structural_parent": {
            "path": str(STRUCTURAL_PATH.relative_to(ROOT)).replace("\\", "/"),
            "contract_sha256": PARENT_DIGEST,
            "source_head": STRUCTURAL_SOURCE_HEAD,
        },
        "body_parent": {
            "path": str(BODY_PATH.relative_to(ROOT)).replace("\\", "/"),
            "contract_sha256": BODY_DIGEST,
            "source_head": BODY_SOURCE_HEAD,
        },
        "postgresql_16_representability_recovery_v1": copy.deepcopy(RECOVERY_SPEC),
        "effective_catalogue_digest": effective_digest,
        "postgresql_major": 16,
        "phases": [
            {"phase": 1, "header": PHASE_HEADERS[1], "span": {}},
            {"phase": 2, "header": PHASE_HEADERS[2], "span": {}},
            {"phase": 3, "header": PHASE_HEADERS[3], "span": {}},
            {"phase": 4, "header": PHASE_HEADERS[4], "span": {}},
            {"phase": 5, "header": PHASE_HEADERS[5], "span": {}},
            {"phase": 6, "header": PHASE_HEADERS[6], "span": {}},
        ],
        "phase_spans": _phase_line_spans(sql_text),
        "ordered_nodes": plan["ordered_nodes"],
        "body_program_accounting": body_program_accounting,
        "immutable_parent_program_count": 22,
        "effective_program_count": len(body["body_programs"]),
        "opcode_populations": {
            "declared_instruction_opcodes": len(
                body["typed_ir_contract"]["instruction_opcodes"]
            ),
            "observed_instruction_opcodes": len(_observed_instruction_opcodes(body)),
            "declared_expression_opcodes": len(
                body["typed_ir_contract"]["expression_opcodes"]
            ),
            "observed_expression_opcodes": len(_observed_expression_opcodes(body)),
            "absent_instruction_opcode": "DERIVE_BINDING",
        },
        "digest_profiles": _collect_digest_profiles(body),
        "digest_vectors": _digest_vectors(body),
        "catalogue_assertions": {
            "fabric_relations": len(
                [r for r in effective["relations"] if not r.startswith("public.")]
            ),
            "rls_policies": len(effective["rls_policies"]),
            "roles": len(effective["roles"]),
            "entry_points": len(effective["signatures"]["entry_points"]),
            "trigger_functions": len(effective["signatures"]["trigger_functions"]),
            "trigger_declarations": len(effective["trigger_declarations"]),
            "support_functions": 1,
            "application_relations_reference_only": len(APPLICATION_COLUMNS),
            "insert_or_reload_compare": _count_instruction(
                body, "INSERT_OR_RELOAD_COMPARE"
            ),
            "derive_binding_occurrences": _count_instruction(body, "DERIVE_BINDING"),
            "trigger_function_runtime_execute": 0,
            "schema_owner": "context_schema_owner",
            "fabric_type_owner_count": len(
                effective["effective_structural"]["type_catalogue"]["domains"]
                + effective["effective_structural"]["type_catalogue"]["enums"]
                + effective["effective_structural"]["type_catalogue"]["composites"]
            ),
            "fabric_relation_owner_count": 18,
            "application_owner_changes": 0,
            "runtime_schema_create_grants": 0,
        },
        "dependency_assertions": {
            "support_helper_precedes_all_rls_policies": True,
            "paired_guard_dependencies": copy.deepcopy(
                RECOVERY_SPEC["paired_guard_dependencies"]
            ),
        },
        "owner_assertions": {
            "schema": {SCHEMA_NAME: "context_schema_owner"},
            "types": [
                {
                    "id": FABRIC + row["name"],
                    "owner": "context_schema_owner",
                }
                for row in (
                    effective["effective_structural"]["type_catalogue"]["domains"]
                    + effective["effective_structural"]["type_catalogue"]["enums"]
                    + effective["effective_structural"]["type_catalogue"]["composites"]
                )
            ],
            "relations": [
                {
                    "id": FABRIC + row["name"],
                    "owner": "context_schema_owner",
                }
                for row in effective["effective_structural"]["relation_catalogue"][
                    "relations"
                ]
            ],
            "application_relation_owner_changes": [],
            "runtime_schema_create_grants": [],
        },
    }


def _verify_trigger_terminals(body: dict[str, Any]) -> None:
    """Verify trigger row-image and terminal legality before emission."""
    matrix = {
        row["function"]: row for row in body["trigger_applicability_return_matrix"]
    }
    for program in body["body_programs"]:
        if program["kind"] != "TRIGGER_FUNCTION":
            for node in _walk_program_nodes(program):
                if node["op"] in ("RETURN_NEW", "RETURN_OLD", "RETURN_NULL"):
                    raise ValueError(
                        "entry point uses trigger terminal in " + program["id"]
                    )
            continue
        row = matrix[program["id"]]
        for switch in _walk_program_nodes(program):
            if switch["op"] != "SWITCH_TG_OP":
                continue
            for arm in switch["operands"]["arms"]:
                tg_op = arm["tg_op"]
                legal = row.get("returns", {}).get(tg_op, "")
                for node in _walk_nodes(arm["nodes"]):
                    if node["op"] == "RETURN_NEW" and "RETURN_NEW" not in legal:
                        raise ValueError(
                            "RETURN_NEW not legal for " + tg_op + " in " + program["id"]
                        )
                    if node["op"] == "RETURN_OLD" and "RETURN_OLD" not in legal:
                        raise ValueError(
                            "RETURN_OLD not legal for " + tg_op + " in " + program["id"]
                        )
                    if node["op"] == "RETURN_NULL" and "RETURN_NULL" not in legal:
                        raise ValueError(
                            "RETURN_NULL not legal for "
                            + tg_op
                            + " in "
                            + program["id"]
                        )


def _registered_sqlstates(body: dict[str, Any]) -> set[str]:
    return {failure["sqlstate"] for failure in body["failure_registry"]}


def _observed_instruction_opcodes(body: dict[str, Any]) -> set[str]:
    out: set[str] = set()
    for program in body["body_programs"]:
        for node in _walk_program_nodes(program):
            out.add(node["op"])
    return out


def _observed_expression_opcodes(body: dict[str, Any]) -> set[str]:
    out: set[str] = set()
    for program in body["body_programs"]:
        for expr in _walk_program_expressions(program):
            if expr["op"] != "SEQUENCE":
                out.add(expr["op"])
            if (
                expr.get("op") == "REF"
                and expr.get("kind") == "SYSTEM"
                and expr.get("field") == "SESSION_USER"
            ):
                out.add("SESSION_USER")
    return out


def _count_instruction(body: dict[str, Any], opcode: str) -> int:
    total = 0
    for program in body["body_programs"]:
        for node in _walk_program_nodes(program):
            if node["op"] == opcode:
                total += 1
    return total


def render_inert(
    effective: dict[str, Any] | None = None,
    loaded: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Produce the canonical SQL text, manifest and render plan."""
    if loaded is None:
        loaded = load_and_bind_parents()
    if effective is None:
        effective = derive_effective_catalogue(loaded)
    reconcile_catalogue(effective)
    immutable_body = loaded["body"]
    _verify_opcode_populations(immutable_body)
    _verify_trigger_terminals(immutable_body)
    body, effective = derive_effective_body(immutable_body, effective)
    _verify_trigger_terminals(body)
    _verify_positional_row_projections(body, effective)
    ctx: dict[str, Any] = {
        "effective": effective,
        "failures": {f["id"]: f for f in body["failure_registry"]},
        "body": body,
        "symbol_types": {},
    }
    plan: dict[str, Any] = {
        "ordered_nodes": [],
        "recovery": copy.deepcopy(RECOVERY_SPEC),
    }
    lines: list[str] = []
    lines.append("-- " + HEADER_LINE)
    lines.append(
        "-- generated_by: raisa_provider_free_unmounted_durability_inert_ddl_rehearsal"
    )
    lines.append("-- renderer_version: " + RENDERER_VERSION)
    lines.append("-- do_not_execute: true")
    lines.append("")

    for phase in range(1, 7):
        lines.append(_phase_separator(phase))
        lines.append(_phase_header(phase))
        lines.append(_phase_separator(phase))
        if phase == 1:
            lines.extend(_render_phase1(effective, ctx, plan))
        elif phase == 2:
            lines.extend(_render_phase2(effective, ctx, plan))
        elif phase == 3:
            lines.extend(_render_phase3(effective, ctx, plan))
        elif phase == 4:
            lines.extend(_render_phase4(effective, ctx, plan))
        elif phase == 5:
            grant_lines = _render_revokes_grants(effective, ctx)
            lines.extend(grant_lines)
            for line in grant_lines:
                if line.startswith("REVOKE "):
                    plan["ordered_nodes"].append(
                        {"kind": "REVOKE", "identifier": line[:60]}
                    )
                elif line.startswith("GRANT "):
                    plan["ordered_nodes"].append(
                        {"kind": "GRANT", "identifier": line[:60]}
                    )
        elif phase == 6:
            lines.extend(_render_phase6_comments(effective))
        lines.append(_phase_end(phase))
        lines.append("")

    sql_text = "\n".join(lines)
    if not sql_text.endswith("\n"):
        sql_text += "\n"
    manifest = build_render_manifest(effective, sql_text, plan, ctx)
    return {
        "sql_text": sql_text,
        "manifest": manifest,
        "plan": plan,
        "ctx": ctx,
        "effective": effective,
        "effective_body": body,
        "loaded": loaded,
    }


# ---------------------------------------------------------------------------
# Lowering contract and whole-contract Schema
# ---------------------------------------------------------------------------

STATEMENT_FAMILIES = {
    "catalogue": [
        "CREATE ROLE",
        "CREATE SCHEMA",
        "CREATE DOMAIN",
        "CREATE TYPE",
        "CREATE TABLE",
        "ALTER TABLE",
        "CREATE UNIQUE INDEX",
        "CREATE POLICY",
        "ALTER TABLE ... ENABLE ROW LEVEL SECURITY",
        "ALTER TABLE ... FORCE ROW LEVEL SECURITY",
        "CREATE FUNCTION",
        "ALTER FUNCTION",
        "ALTER DOMAIN ... OWNER TO",
        "ALTER TYPE ... OWNER TO",
        "ALTER TABLE ... OWNER TO",
    ],
    "bodies": ["CREATE FUNCTION", "ALTER FUNCTION"],
    "triggers": ["CREATE TRIGGER", "CREATE CONSTRAINT TRIGGER"],
    "privileges": ["REVOKE", "GRANT"],
    "assertions": ["-- phase 6"],
}


def build_lowering_contract(
    effective: dict[str, Any] | None = None,
    loaded: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if loaded is None:
        loaded = load_and_bind_parents()
    immutable_body = loaded["body"]
    base_effective = derive_effective_catalogue(loaded)
    body, effective = derive_effective_body(immutable_body, base_effective)
    return {
        "schema_version": "raisa.context_fabric.durability_inert_ddl_rehearsal.lowering_contract.v2",
        "status": "postgresql_representability_recovery_candidate",
        "postgresql_target": {
            "major": 16,
            "producer_isolation": "READ COMMITTED",
            "coordinator_isolation": "SERIALIZABLE",
        },
        "parents": {
            "structural": {
                "path": str(STRUCTURAL_PATH.relative_to(ROOT)).replace("\\", "/"),
                "schema_path": str(STRUCTURAL_SCHEMA_PATH.relative_to(ROOT)).replace(
                    "\\", "/"
                ),
                "contract_sha256": PARENT_DIGEST,
                "source_head": STRUCTURAL_SOURCE_HEAD,
            },
            "body": {
                "path": str(BODY_PATH.relative_to(ROOT)).replace("\\", "/"),
                "schema_path": str(BODY_SCHEMA_PATH.relative_to(ROOT)).replace(
                    "\\", "/"
                ),
                "contract_sha256": BODY_DIGEST,
                "source_head": BODY_SOURCE_HEAD,
            },
        },
        "postgresql_16_representability_recovery_v1": copy.deepcopy(RECOVERY_SPEC),
        "outputs": {
            "sql_inert": str(SQL_INERT_PATH.relative_to(ROOT)).replace("\\", "/"),
            "render_manifest": str(MANIFEST_PATH.relative_to(ROOT)).replace("\\", "/"),
            "lowering_contract": str(LOWERING_CONTRACT_PATH.relative_to(ROOT)).replace(
                "\\", "/"
            ),
            "lowering_schema": str(LOWERING_SCHEMA_PATH.relative_to(ROOT)).replace(
                "\\", "/"
            ),
        },
        "phases": [
            {"phase": 1, "family": "catalogue"},
            {"phase": 2, "family": "entry_point_bodies"},
            {"phase": 3, "family": "trigger_function_bodies"},
            {"phase": 4, "family": "trigger_declarations"},
            {"phase": 5, "family": "privileges"},
            {"phase": 6, "family": "assertions"},
        ],
        "statement_families": STATEMENT_FAMILIES,
        "opcode_populations": {
            "declared_instruction_opcodes": len(
                body["typed_ir_contract"]["instruction_opcodes"]
            ),
            "observed_instruction_opcodes": len(_observed_instruction_opcodes(body)),
            "absent_instruction_opcode": "DERIVE_BINDING",
            "declared_expression_opcodes": len(
                body["typed_ir_contract"]["expression_opcodes"]
            ),
            "observed_expression_opcodes": len(_observed_expression_opcodes(body)),
        },
        "digest_profiles": _collect_digest_profiles(body),
        "catalogue_assertions": {
            "fabric_relations": len(
                [r for r in effective["relations"] if not r.startswith("public.")]
            ),
            "rls_policies": len(effective["rls_policies"]),
            "roles": len(effective["roles"]),
            "support_functions": 1,
            "entry_points": len(effective["signatures"]["entry_points"]),
            "trigger_functions": len(effective["signatures"]["trigger_functions"]),
            "trigger_declarations": len(effective["trigger_declarations"]),
            "invariant_enforcement_bindings": len(effective["invariants"]),
            "effective_programs": 23,
            "fabric_type_owners": len(
                effective["effective_structural"]["type_catalogue"]["domains"]
                + effective["effective_structural"]["type_catalogue"]["enums"]
                + effective["effective_structural"]["type_catalogue"]["composites"]
            ),
            "fabric_relation_owners": 18,
            "application_owner_changes": 0,
            "runtime_schema_create_grants": 0,
        },
        "rules": {
            "raw_sql": False,
            "dynamic_execution": False,
            "transaction_control": False,
            "internal_retry": False,
            "unqualified_identifiers": False,
            "on_conflict_do_nothing": False,
            "when_others": False,
            "extension_or_file_or_network": False,
            "trigger_row_image_system_columns": False,
            "unknown_lock_mode_fallback": False,
        },
    }


def build_lowering_schema() -> dict[str, Any]:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "https://emr4.local/schemas/raisa/durability-inert-ddl-lowering-contract.schema.json",
        "title": "Provider-free unmounted durability inert DDL lowering contract",
        "type": "object",
        "additionalProperties": False,
        "required": [
            "schema_version",
            "status",
            "postgresql_target",
            "parents",
            "postgresql_16_representability_recovery_v1",
            "outputs",
            "phases",
            "statement_families",
            "opcode_populations",
            "digest_profiles",
            "catalogue_assertions",
            "rules",
        ],
        "properties": {
            "schema_version": {
                "const": "raisa.context_fabric.durability_inert_ddl_rehearsal.lowering_contract.v2"
            },
            "status": {"const": "postgresql_representability_recovery_candidate"},
            "postgresql_target": {
                "type": "object",
                "additionalProperties": False,
                "required": ["major", "producer_isolation", "coordinator_isolation"],
                "properties": {
                    "major": {"const": 16},
                    "producer_isolation": {"const": "READ COMMITTED"},
                    "coordinator_isolation": {"const": "SERIALIZABLE"},
                },
            },
            "parents": {
                "type": "object",
                "additionalProperties": False,
                "required": ["structural", "body"],
                "properties": {
                    "structural": {"$ref": "#/$defs/parent_binding"},
                    "body": {"$ref": "#/$defs/parent_binding"},
                },
            },
            "postgresql_16_representability_recovery_v1": {
                "const": copy.deepcopy(RECOVERY_SPEC)
            },
            "outputs": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "sql_inert",
                    "render_manifest",
                    "lowering_contract",
                    "lowering_schema",
                ],
                "properties": {
                    "sql_inert": {
                        "const": "orchestration/continuity/raisa-provider-free-unmounted-durability-inert-ddl-rehearsal/durability-schema.sql.inert"
                    },
                    "render_manifest": {
                        "const": "orchestration/continuity/raisa-provider-free-unmounted-durability-inert-ddl-rehearsal/render-manifest.json"
                    },
                    "lowering_contract": {
                        "const": "orchestration/continuity/raisa-provider-free-unmounted-durability-inert-ddl-rehearsal/lowering-contract.json"
                    },
                    "lowering_schema": {
                        "const": "orchestration/continuity/raisa-provider-free-unmounted-durability-inert-ddl-rehearsal/lowering-contract.schema.json"
                    },
                },
            },
            "phases": {
                "type": "array",
                "minItems": 6,
                "maxItems": 6,
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["phase", "family"],
                    "properties": {
                        "phase": {"type": "integer", "minimum": 1, "maximum": 6},
                        "family": {"type": "string"},
                    },
                },
            },
            "statement_families": {
                "type": "object",
                "additionalProperties": {"type": "array", "items": {"type": "string"}},
            },
            "opcode_populations": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "declared_instruction_opcodes",
                    "observed_instruction_opcodes",
                    "absent_instruction_opcode",
                    "declared_expression_opcodes",
                    "observed_expression_opcodes",
                ],
                "properties": {
                    "declared_instruction_opcodes": {"const": 22},
                    "observed_instruction_opcodes": {"const": 21},
                    "absent_instruction_opcode": {"const": "DERIVE_BINDING"},
                    "declared_expression_opcodes": {"const": 34},
                    "observed_expression_opcodes": {"const": 34},
                },
            },
            "digest_profiles": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["profile", "operand_types"],
                    "properties": {
                        "profile": {"type": "string"},
                        "operand_types": {"type": "array", "items": {"type": "string"}},
                    },
                },
            },
            "catalogue_assertions": {
                "type": "object",
                "additionalProperties": {"type": "integer"},
            },
            "rules": {
                "type": "object",
                "additionalProperties": {"type": "boolean"},
            },
        },
        "$defs": {
            "parent_binding": {
                "type": "object",
                "additionalProperties": False,
                "required": ["path", "schema_path", "contract_sha256", "source_head"],
                "properties": {
                    "path": {"type": "string"},
                    "schema_path": {"type": "string"},
                    "contract_sha256": {"type": "string"},
                    "source_head": {"type": "string"},
                },
            }
        },
    }


# ---------------------------------------------------------------------------
# Independent static recognizer (closed subset)
# ---------------------------------------------------------------------------

FORBIDDEN_TOP_LEVEL_PREFIXES = (
    "BEGIN",
    "COMMIT",
    "ROLLBACK",
    "SAVEPOINT",
    "RELEASE",
    "DO ",
    "COPY ",
    "INSERT ",
    "UPDATE ",
    "DELETE ",
    "TRUNCATE ",
    "SET ROLE",
    "CREATE EXTENSION",
    "CREATE SERVER",
    "CREATE FOREIGN",
    "CREATE PROCEDURE",
    "CREATE PUBLICATION",
    "CREATE SUBSCRIPTION",
    "CREATE USER MAPPING",
    "DROP ",
    "ALTER ROLE",
    "LISTEN ",
    "NOTIFY ",
    "SELECT ",
    "VACUUM ",
    "ANALYZE ",
    "REINDEX ",
    "GRANT ",
)

FORBIDDEN_BODY_TOKENS = (
    "COPY ",
    "pg_read_file",
    "pg_write_file",
    "pg_ls_dir",
    "dblink",
    "pg_notify",
    "LISTEN ",
    "NOTIFY ",
    "CREATE EXTENSION",
    "CREATE SERVER",
    "CREATE FOREIGN",
    "CREATE PROCEDURE",
    "SECURITY INVOKER",
    "ON CONFLICT DO NOTHING",
    "WHEN OTHERS",
)

REGISTERED_SQLSTATES = frozenset(
    {
        "CF001",
        "CF002",
        "CF003",
        "CF004",
        "CF101",
        "CF102",
        "CF103",
        "CF104",
        "CF105",
        "CF201",
        "CF202",
        "CF203",
        "CF301",
        "CF302",
        "CF303",
        "CF401",
        "CF402",
        "CF403",
        "CF501",
        "CF502",
        "CF601",
        "CF602",
        "CF603",
        "CF604",
        "CF605",
    }
)


class RecognitionIssue:
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"RecognitionIssue({self.code!r}, {self.message!r})"


class RecognitionReport:
    def __init__(self, valid: bool, issues: list[RecognitionIssue]):
        self.valid = valid
        self.issues = issues


def _strip_leading_comments(stmt: str) -> str:
    lines = stmt.splitlines()
    while lines and (lines[0].lstrip().startswith("--") or lines[0].strip() == ""):
        lines.pop(0)
    return "\n".join(lines).strip()


def _extract_top_level_statements(text: str) -> list[str]:
    """Split text into top-level statements, respecting SQL lexical states."""
    statements: list[str] = []
    state = "normal"
    i = 0
    n = len(text)
    depth = 0
    start = 0
    dollar_tag: str | None = None
    while i < n:
        ch = text[i]
        if state == "normal":
            if text.startswith("--", i):
                nl = text.find("\n", i)
                i = n if nl == -1 else nl
                continue
            if text.startswith("/*", i):
                end = text.find("*/", i + 2)
                i = n if end == -1 else end + 2
                continue
            if ch == "'":
                state = "string"
            elif ch == '"':
                state = "quoted"
            elif ch == "$":
                match = re.match(r"\$([A-Za-z_][A-Za-z0-9_]*)?\$", text[i:])
                if match:
                    dollar_tag = match.group(0)
                    state = "dollar"
                    i += len(dollar_tag)
                    continue
            elif ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
                if depth < 0:
                    return statements
            elif ch == ";" and depth == 0:
                stmt = _strip_leading_comments(text[start:i])
                if stmt:
                    statements.append(stmt)
                start = i + 1
        elif state == "string":
            if ch == "'":
                if i + 1 < n and text[i + 1] == "'":
                    i += 1
                else:
                    state = "normal"
        elif state == "quoted":
            if ch == '"':
                if i + 1 < n and text[i + 1] == '"':
                    i += 1
                else:
                    state = "normal"
        elif state == "dollar":
            if dollar_tag is not None and text.startswith(dollar_tag, i):
                state = "normal"
                i += len(dollar_tag) - 1
        i += 1
    tail = _strip_leading_comments(text[start:])
    if tail:
        statements.append(tail)
    return statements


def _check_balanced(text: str) -> list[RecognitionIssue]:
    issues: list[RecognitionIssue] = []
    for ch in text:
        if ord(ch) < 32 and ch not in "\n\t":
            issues.append(
                RecognitionIssue("control_character", "control character in artifact")
            )
            break
    state = "normal"
    depth = 0
    dollar_tag: str | None = None
    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        if state == "normal":
            if text.startswith("--", i):
                nl = text.find("\n", i)
                i = n if nl == -1 else nl
                continue
            if text.startswith("/*", i):
                end = text.find("*/", i + 2)
                i = n if end == -1 else end + 2
                continue
            if ch == "'":
                state = "string"
            elif ch == '"':
                state = "quoted"
            elif ch == "$":
                match = re.match(r"\$([A-Za-z_][A-Za-z0-9_]*)?\$", text[i:])
                if match:
                    dollar_tag = match.group(0)
                    state = "dollar"
                    i += len(dollar_tag)
                    continue
            elif ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
                if depth < 0:
                    issues.append(
                        RecognitionIssue("unbalanced_parenthesis", "negative depth")
                    )
                    break
        elif state == "string":
            if ch == "'":
                if i + 1 < n and text[i + 1] == "'":
                    i += 1
                else:
                    state = "normal"
        elif state == "quoted":
            if ch == '"':
                if i + 1 < n and text[i + 1] == '"':
                    i += 1
                else:
                    state = "normal"
        elif state == "dollar":
            if dollar_tag is not None and text.startswith(dollar_tag, i):
                state = "normal"
                i += len(dollar_tag) - 1
        i += 1
    if state != "normal":
        issues.append(
            RecognitionIssue(
                "unterminated_literal", "unterminated literal or dollar body"
            )
        )
    if depth != 0:
        issues.append(
            RecognitionIssue("unbalanced_parenthesis", "unbalanced parentheses")
        )
    return issues


ACCEPTED_FUNCTION_IDS = {
    "emr4_context_fabric.session_binding_allows_v1",
    "emr4_context_fabric.project_update_confirm_reschedule_v1",
    "emr4_context_fabric.admit_proofread_observation_v1",
    "emr4_context_fabric.apply_durability_transition_v1",
    "emr4_context_fabric.register_observer_generation_v1",
    "emr4_context_fabric.append_recovery_anchor_v1",
    "emr4_context_fabric.rotate_observation_key_v1",
    "emr4_context_fabric.consume_observer_generation_v1",
    "emr4_context_fabric.evaluate_source_retention_v1",
    "emr4_context_fabric.purge_source_rows_v1",
    "emr4_context_fabric.cf_guard_claim_v1",
    "emr4_context_fabric.cf_fence_claim_v1",
    "emr4_context_fabric.cf_guard_appointment_update_v1",
    "emr4_context_fabric.cf_fence_appointment_update_v1",
    "emr4_context_fabric.cf_guard_audit_v1",
    "emr4_context_fabric.cf_fence_audit_v1",
    "emr4_context_fabric.cf_guard_event_v1",
    "emr4_context_fabric.cf_fence_event_v1",
    "emr4_context_fabric.cf_guard_alias_v1",
    "emr4_context_fabric.cf_fence_alias_v1",
    "emr4_context_fabric.cf_guard_stream_head_v1",
    "emr4_context_fabric.cf_fence_stream_head_v1",
    "emr4_context_fabric.cf_guard_outbox_v1",
    "emr4_context_fabric.cf_fence_outbox_v1",
}

TRIGGER_FUNCTION_IDS = frozenset(
    {
        "emr4_context_fabric.cf_guard_claim_v1",
        "emr4_context_fabric.cf_fence_claim_v1",
        "emr4_context_fabric.cf_guard_appointment_update_v1",
        "emr4_context_fabric.cf_fence_appointment_update_v1",
        "emr4_context_fabric.cf_guard_audit_v1",
        "emr4_context_fabric.cf_fence_audit_v1",
        "emr4_context_fabric.cf_guard_event_v1",
        "emr4_context_fabric.cf_fence_event_v1",
        "emr4_context_fabric.cf_guard_alias_v1",
        "emr4_context_fabric.cf_fence_alias_v1",
        "emr4_context_fabric.cf_guard_stream_head_v1",
        "emr4_context_fabric.cf_fence_stream_head_v1",
        "emr4_context_fabric.cf_guard_outbox_v1",
        "emr4_context_fabric.cf_fence_outbox_v1",
    }
)


def _first_keyword(statement: str) -> str:
    stripped = statement.lstrip()
    return stripped.split()[0].upper() if stripped else ""


def _statement_issues(
    statement: str, statements: list[str], effective: dict[str, Any]
) -> list[RecognitionIssue]:
    issues: list[RecognitionIssue] = []
    upper = statement.upper()
    first = _first_keyword(statement)

    if first in ("SELECT", "INSERT", "UPDATE", "DELETE"):
        issues.append(RecognitionIssue("top_level_dml", "top-level DML statement"))
    if first in ("INSERT", "UPDATE", "DELETE") and "public." in statement:
        issues.append(RecognitionIssue("application_dml", "application table DML"))
    if first in (
        "BEGIN",
        "COMMIT",
        "ROLLBACK",
        "SAVEPOINT",
        "RELEASE",
        "TRUNCATE",
        "COPY",
    ):
        issues.append(
            RecognitionIssue("transaction_control", "top-level transaction control")
        )
    if first == "DO":
        issues.append(RecognitionIssue("anonymous_block", "top-level DO block"))
    if first == "SET":
        issues.append(RecognitionIssue("session_setting", "top-level SET statement"))
    if first.startswith("\\"):
        issues.append(RecognitionIssue("psql_meta", "psql meta-command"))
    if upper.startswith("CREATE EXTENSION"):
        issues.append(RecognitionIssue("extension", "CREATE EXTENSION forbidden"))
    if upper.startswith(
        (
            "CREATE SERVER",
            "CREATE FOREIGN",
            "CREATE USER MAPPING",
            "CREATE PUBLICATION",
            "CREATE SUBSCRIPTION",
        )
    ):
        issues.append(RecognitionIssue("network_surface", "external surface statement"))
    if upper.startswith(("CREATE PROCEDURE", "CREATE AGGREGATE", "CREATE OPERATOR")):
        issues.append(
            RecognitionIssue("helper_overload", "forbidden helper/overload surface")
        )
    for match in re.finditer(r"ERRCODE\s*=\s*'([A-Z0-9]{5})'", statement):
        sqlstate = match.group(1)
        if sqlstate not in REGISTERED_SQLSTATES:
            issues.append(
                RecognitionIssue("wrong_sqlstate", "unregistered SQLSTATE " + sqlstate)
            )
    for match in re.finditer(r"ERRCODE\s*=\s*'CF004'", statement):
        if "required_row_missing_or_ambiguous" not in statement:
            issues.append(
                RecognitionIssue(
                    "wrong_sqlstate", "CF004 missing canonical reason message"
                )
            )

    if first == "DROP":
        issues.append(RecognitionIssue("drop_statement", "DROP statement forbidden"))
    if first == "ALTER" and upper.startswith("ALTER ROLE"):
        issues.append(RecognitionIssue("role_alter", "ALTER ROLE forbidden"))

    for token in FORBIDDEN_BODY_TOKENS:
        if token in upper:
            if token == "SECURITY INVOKER":
                issues.append(
                    RecognitionIssue("security_invoker", "SECURITY INVOKER forbidden")
                )
            elif token == "ON CONFLICT DO NOTHING":
                issues.append(
                    RecognitionIssue(
                        "on_conflict_do_nothing", "ON CONFLICT DO NOTHING forbidden"
                    )
                )
            elif token == "WHEN OTHERS":
                issues.append(
                    RecognitionIssue("when_others", "broad exception handler forbidden")
                )
            elif token in (
                "pg_read_file",
                "pg_write_file",
                "pg_ls_dir",
                "pg_notify",
                "dblink",
            ):
                issues.append(
                    RecognitionIssue("file_network", "file/network primitive forbidden")
                )
            elif token == "CREATE PROCEDURE":
                issues.append(
                    RecognitionIssue("helper_overload", "CREATE PROCEDURE forbidden")
                )
            elif token in ("COPY ", "LISTEN ", "NOTIFY "):
                issues.append(
                    RecognitionIssue("file_network", "copy/listen/notify forbidden")
                )
            else:
                issues.append(
                    RecognitionIssue("forbidden_token", "forbidden token " + token)
                )

    # PostgreSQL grammar constructs are not pg_catalog objects.
    if "pg_catalog.ARRAY" in statement:
        issues.append(
            RecognitionIssue("pg_catalog_array", "pg_catalog.ARRAY grammar misuse")
        )
    if "pg_catalog.ROW" in statement:
        issues.append(
            RecognitionIssue("pg_catalog_row", "pg_catalog.ROW grammar misuse")
        )
    if "pg_catalog.coalesce(" in statement.lower():
        issues.append(
            RecognitionIssue(
                "pg_catalog_coalesce",
                "COALESCE special form cannot be schema-qualified",
            )
        )
    if re.search(r"\b(?:OLD|NEW)\s*\.\s*\"?xmin\"?", statement, re.IGNORECASE):
        issues.append(
            RecognitionIssue(
                "trigger_row_xmin",
                "trigger row images cannot expose PostgreSQL system xmin",
            )
        )
    if re.search(r"\([a-z][a-z0-9_]*\)\s*\.\s*\"?xmin\"?", statement, re.IGNORECASE):
        issues.append(
            RecognitionIssue(
                "anonymous_record_xmin",
                "anonymous PL/pgSQL record xmin must use direct record-field access",
            )
        )
    if statement.count("pg_catalog.array_length(") != statement.count(
        "COALESCE(pg_catalog.array_length("
    ):
        issues.append(
            RecognitionIssue("nullable_count", "bare array_length count lowering")
        )
    # Isolation must be an actual read-only current_setting assertion.
    if re.search(r"--\s*assert_isolation\b", statement):
        issues.append(
            RecognitionIssue(
                "comment_only_isolation", "comment-only isolation assertion"
            )
        )
    # Bounded source delete must use a key CTE, never DELETE ORDER BY/LIMIT.
    if re.search(
        r"\bDELETE\s+FROM\b[^;]*\bORDER\s+BY\b", statement, flags=re.IGNORECASE
    ):
        issues.append(
            RecognitionIssue("delete_order_limit", "DELETE ... ORDER BY invalid")
        )
    if re.search(r"\bDELETE\s+FROM\b[^;]*\bLIMIT\b", statement, flags=re.IGNORECASE):
        issues.append(RecognitionIssue("delete_limit", "DELETE ... LIMIT invalid"))
    # Anonymous-record set aggregation is not a typed complete set.
    if re.search(r"array_agg\(\s*sub\b", statement, flags=re.IGNORECASE):
        issues.append(
            RecognitionIssue("anonymous_record_set", "anonymous-record set aggregation")
        )
    # Every exact read/write must use strict INTO, never a bare INTO.  The
    # complete-set aggregation is the sole non-strict INTO; it always continues
    # with a newline and the outer FROM (never a same-line FROM target).
    if re.search(
        r"\b(?:SELECT|UPDATE)\b[^;]*\bINTO\s+(?!STRICT\b)"
        r"[a-zA-Z_][a-zA-Z0-9_]*+(?!\s*\n\s*FROM\b)",
        statement,
        flags=re.IGNORECASE,
    ) and not re.search(
        r"SELECT\s+pg_catalog\.count\(\*\)\s+INTO\b", statement, flags=re.IGNORECASE
    ):
        issues.append(
            RecognitionIssue("non_strict_exact", "non-strict exact read/write")
        )
    # Role identifiers are cluster principals, never schema-qualified tokens.
    if re.search(
        r"\bOWNER\s+TO\s+[a-zA-Z_][a-zA-Z0-9_]*\.[a-zA-Z_][a-zA-Z0-9_]*", statement
    ):
        issues.append(
            RecognitionIssue("schema_qualified_owner", "schema-qualified owner role")
        )
    # UTC digest canonical text must carry a literal terminal Z.
    for match in re.finditer(r"HH24:MI:SS\.US", statement):
        if statement[match.end() : match.end() + 3] != '"Z"':
            issues.append(
                RecognitionIssue("digest_utc_z", "UTC digest text missing terminal Z")
            )

    # CREATE FUNCTION must be security definer with fixed search path.
    if upper.startswith("CREATE FUNCTION"):
        if "SECURITY DEFINER" not in upper:
            issues.append(
                RecognitionIssue("security_definer", "function not SECURITY DEFINER")
            )
        if "SECURITY INVOKER" in upper:
            issues.append(
                RecognitionIssue("security_invoker", "SECURITY INVOKER forbidden")
            )
        search_path_match = re.search(r"SET search_path\s*=\s*([^;]+)", statement)
        if search_path_match:
            path = search_path_match.group(1).strip()
            if path.replace(" ", "") != "pg_catalog,emr4_context_fabric":
                issues.append(RecognitionIssue("search_path", "search-path widening"))
        if "pg_catalog, emr4_context_fabric" not in statement:
            issues.append(RecognitionIssue("search_path", "missing fixed search path"))

    if upper.startswith("CREATE TABLE") or upper.startswith("ALTER TABLE"):
        target = statement.split()[2]
        if not (
            target.startswith("emr4_context_fabric.") or target.startswith("public.")
        ):
            issues.append(
                RecognitionIssue("unqualified_identifier", "unqualified table target")
            )
        if upper.startswith("CREATE TABLE") and target.startswith("public."):
            issues.append(RecognitionIssue("application_ddl", "application table DDL"))
        if target.startswith("public.") and upper.startswith("ALTER TABLE"):
            issues.append(
                RecognitionIssue("application_ddl", "application table ALTER")
            )

    if upper.startswith("CREATE POLICY"):
        parts = statement.split()
        if len(parts) >= 5:
            target = parts[4]
            if not target.startswith("emr4_context_fabric."):
                issues.append(
                    RecognitionIssue(
                        "unqualified_identifier", "unqualified policy target"
                    )
                )
        else:
            issues.append(
                RecognitionIssue("malformed_policy", "malformed CREATE POLICY")
            )

    if upper.startswith(("CREATE TRIGGER", "CREATE CONSTRAINT TRIGGER")):
        if " ON " in upper:
            on = statement.upper().split(" ON ")[1].split()[0]
            if not (on.startswith("EMR4_CONTEXT_FABRIC.") or on.startswith("PUBLIC.")):
                issues.append(
                    RecognitionIssue(
                        "unqualified_identifier", "unqualified trigger target"
                    )
                )
        if upper.startswith("CREATE CONSTRAINT TRIGGER"):
            if " AFTER " not in upper or " FOR EACH ROW" not in upper:
                issues.append(
                    RecognitionIssue(
                        "constraint_trigger_shape",
                        "constraint trigger must be AFTER FOR EACH ROW",
                    )
                )
            if " DEFERRABLE INITIALLY DEFERRED" not in upper:
                issues.append(
                    RecognitionIssue(
                        "constraint_trigger_shape",
                        "deferred constraint trigger clauses missing or reordered",
                    )
                )
        elif "DEFERRABLE" in upper or "INITIALLY DEFERRED" in upper:
            issues.append(
                RecognitionIssue(
                    "ordinary_trigger_deferrable",
                    "ordinary trigger carries deferrability",
                )
            )

    if upper.startswith(("GRANT ", "REVOKE ")):
        if " ON SCHEMA " in upper:
            target = statement.split(" ON SCHEMA ")[1].split()[0]
            if target != "emr4_context_fabric":
                issues.append(
                    RecognitionIssue(
                        "unqualified_identifier", "unqualified schema privilege target"
                    )
                )
        elif " ON TABLE " in upper:
            on = statement.split(" ON TABLE ")[1].split()[0]
            if not (on.startswith("emr4_context_fabric.") or on.startswith("public.")):
                issues.append(
                    RecognitionIssue(
                        "unqualified_identifier", "unqualified privilege target"
                    )
                )
            if upper.startswith("GRANT ") and on.startswith("public."):
                grant_part = upper.split(" ON TABLE ")[0]
                privileges = grant_part[len("GRANT ") :].strip().split()[0]
                if privileges != "SELECT":
                    issues.append(
                        RecognitionIssue("application_grant", "application table grant")
                    )
        elif " ON FUNCTION " in upper:
            on = statement.split(" ON FUNCTION ")[1].split()[0].split("(")[0]
            if not (on.startswith("emr4_context_fabric.") or on.startswith("public.")):
                issues.append(
                    RecognitionIssue(
                        "unqualified_identifier",
                        "unqualified function privilege target",
                    )
                )
            if upper.startswith("GRANT ") and on in TRIGGER_FUNCTION_IDS:
                issues.append(
                    RecognitionIssue("trigger_grant", "trigger function execute grant")
                )
        if " TRIGGER " in upper and "GRANT " in upper:
            issues.append(
                RecognitionIssue("trigger_grant", "trigger grant in runtime phase")
            )

    if upper.startswith("CREATE FUNCTION"):
        # Ensure function id is an accepted id (no helper/overload).
        name_match = re.match(r"CREATE FUNCTION\s+([a-zA-Z0-9_\.]+)", statement)
        if name_match:
            fn_name = name_match.group(1).lower()
            if fn_name not in ACCEPTED_FUNCTION_IDS:
                issues.append(
                    RecognitionIssue("helper_overload", "unknown function " + fn_name)
                )

    return issues


def recognize_inert_sql(
    sql_text: str,
    manifest: dict[str, Any] | None = None,
    effective: dict[str, Any] | None = None,
) -> RecognitionReport:
    """Independently tokenize the emitted bytes and validate the closed subset."""
    issues: list[RecognitionIssue] = []
    issues.extend(_check_balanced(sql_text))
    statements = _extract_top_level_statements(sql_text)
    phase_markers = [
        line for line in sql_text.splitlines() if line.startswith("-- PHASE ")
    ]
    end_markers = [
        line for line in sql_text.splitlines() if line.startswith("-- END PHASE ")
    ]
    if len(phase_markers) != 6:
        issues.append(RecognitionIssue("phase_marker", "expected 6 phase markers"))
    if len(end_markers) != 6:
        issues.append(RecognitionIssue("phase_marker", "expected 6 end-phase markers"))
    if not sql_text.startswith("-- " + HEADER_LINE):
        issues.append(RecognitionIssue("header", "missing fixed header"))
    revoke_count = sum(
        1 for stmt in statements if stmt.lstrip().upper().startswith("REVOKE")
    )
    if revoke_count < 43:
        issues.append(
            RecognitionIssue("missing_revoke", "expected at least 43 revoke statements")
        )
    if re.search(r"C:[\\/]|\.\.\\|\.\./", sql_text):
        issues.append(RecognitionIssue("path_escape", "output-path escape"))
    constraint_names: set[str] = set()
    for stmt in statements:
        match = re.search(r"ADD CONSTRAINT\s+([a-zA-Z0-9_]+)", stmt)
        if match:
            constraint_names.add(match.group(1))
        match = re.search(r"CREATE UNIQUE INDEX\s+([a-zA-Z0-9_]+)", stmt)
        if match:
            constraint_names.add(match.group(1))
    for stmt in statements:
        for match in re.finditer(r"cf_constraint_name = '([^']+)'", stmt):
            if match.group(1) not in constraint_names:
                issues.append(
                    RecognitionIssue(
                        "wrong_constraint", "unrecognized conflict constraint name"
                    )
                )
    targeted_conflicts = list(
        re.finditer(
            r"ON\s+CONFLICT\s+ON\s+CONSTRAINT\s+([a-zA-Z0-9_]+)\s+DO\s+NOTHING",
            sql_text,
            flags=re.IGNORECASE,
        )
    )
    if len(re.findall(r"\bON\s+CONFLICT\b", sql_text, flags=re.IGNORECASE)) != len(
        targeted_conflicts
    ):
        issues.append(
            RecognitionIssue(
                "on_conflict_do_nothing",
                "every ON CONFLICT must name one exact rendered constraint",
            )
        )
    for match in targeted_conflicts:
        if match.group(1) not in constraint_names:
            issues.append(
                RecognitionIssue(
                    "wrong_constraint", "unrecognized conflict constraint name"
                )
            )
    for stmt in statements:
        issues.extend(_statement_issues(stmt, statements, effective or {}))
    alter_owner_count = sum(
        1
        for stmt in statements
        if stmt.lstrip().upper().startswith("ALTER FUNCTION")
        and "OWNER TO" in stmt.upper()
    )
    expected_functions = 24  # 9 entry points + 14 trigger functions + 1 support
    if alter_owner_count != expected_functions:
        issues.append(
            RecognitionIssue(
                "missing_owner",
                "expected %d function owner statements, saw %d"
                % (expected_functions, alter_owner_count),
            )
        )
    support_index = next(
        (
            index
            for index, stmt in enumerate(statements)
            if stmt.lstrip().startswith(
                "CREATE FUNCTION emr4_context_fabric.session_binding_allows_v1"
            )
        ),
        None,
    )
    policy_indexes = [
        index
        for index, stmt in enumerate(statements)
        if stmt.lstrip().upper().startswith("CREATE POLICY")
    ]
    if (
        support_index is None
        or not policy_indexes
        or support_index >= min(policy_indexes)
    ):
        issues.append(
            RecognitionIssue(
                "dependency_order", "support helper must precede every RLS policy"
            )
        )
    composite_rows = (
        effective.get("effective_structural", {})
        .get("type_catalogue", {})
        .get("composites", [])
    )
    if isinstance(composite_rows, list) and composite_rows:
        try:
            expected_composites = [
                row["name"] for row in _ordered_composites(composite_rows)
            ]
        except (KeyError, TypeError, ValueError):
            expected_composites = []
        actual_composites: list[str] = []
        for statement in statements:
            match = re.match(
                r"\s*CREATE TYPE emr4_context_fabric\.([a-zA-Z0-9_]+) AS \(",
                statement,
            )
            if match:
                actual_composites.append(match.group(1))
        if actual_composites != expected_composites:
            issues.append(
                RecognitionIssue(
                    "composite_dependency_order",
                    "composite CREATE order must be stable and dependency-safe",
                )
            )
    ordinary_triggers = sum(
        1 for stmt in statements if stmt.lstrip().upper().startswith("CREATE TRIGGER")
    )
    constraint_triggers = sum(
        1
        for stmt in statements
        if stmt.lstrip().upper().startswith("CREATE CONSTRAINT TRIGGER")
    )
    if ordinary_triggers != 7 or constraint_triggers != 7:
        issues.append(
            RecognitionIssue(
                "trigger_population",
                "expected seven immediate and seven constraint triggers",
            )
        )
    type_owner_count = sum(
        1
        for stmt in statements
        if stmt.lstrip().upper().startswith(("ALTER DOMAIN", "ALTER TYPE"))
        and "OWNER TO CONTEXT_SCHEMA_OWNER" in stmt.upper()
    )
    relation_owner_count = sum(
        1
        for stmt in statements
        if stmt.lstrip().upper().startswith("ALTER TABLE EMR4_CONTEXT_FABRIC.")
        and "OWNER TO CONTEXT_SCHEMA_OWNER" in stmt.upper()
    )
    if type_owner_count != 32 or relation_owner_count != 18:
        issues.append(
            RecognitionIssue(
                "object_owner",
                "exact fabric type/relation owner population mismatch",
            )
        )
    if (
        "CREATE SCHEMA emr4_context_fabric AUTHORIZATION context_schema_owner;"
        not in sql_text
    ):
        issues.append(
            RecognitionIssue("schema_owner", "exact schema authorization missing")
        )
    if manifest is not None:
        actual_hash = "sha256:" + sha256_hex(sql_text.encode("utf-8"))
        if manifest.get("sql_sha256") != actual_hash:
            issues.append(RecognitionIssue("hash_mismatch", "artifact sha256 mismatch"))
        if manifest.get("sql_byte_count") != len(sql_text.encode("utf-8")):
            issues.append(RecognitionIssue("byte_count", "byte count mismatch"))
        if manifest.get("statement_count") != len(statements):
            issues.append(
                RecognitionIssue("statement_count", "statement count mismatch")
            )
        if manifest.get("phase_spans") != _phase_line_spans(sql_text):
            issues.append(RecognitionIssue("phase_span", "phase span mismatch"))
    return RecognitionReport(len(issues) == 0, issues)


# ---------------------------------------------------------------------------
# Canonical artifact writing and fixed-path CLI
# ---------------------------------------------------------------------------


def write_artifacts(result: dict[str, Any] | None = None) -> dict[str, Any]:
    """Write the four canonical inert artifacts under the fixed output dir."""
    if result is None:
        result = render_inert()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    contract = build_lowering_contract(result["effective"], result["loaded"])
    schema = build_lowering_schema()
    _write_utf8_lf(SQL_INERT_PATH, result["sql_text"])
    _write_utf8_lf(
        MANIFEST_PATH, json.dumps(result["manifest"], indent=2, sort_keys=True)
    )
    _write_utf8_lf(
        LOWERING_CONTRACT_PATH, json.dumps(contract, indent=2, sort_keys=True)
    )
    _write_utf8_lf(LOWERING_SCHEMA_PATH, json.dumps(schema, indent=2, sort_keys=True))
    return {
        "sql_inert": str(SQL_INERT_PATH),
        "render_manifest": str(MANIFEST_PATH),
        "lowering_contract": str(LOWERING_CONTRACT_PATH),
        "lowering_schema": str(LOWERING_SCHEMA_PATH),
    }


def check_artifacts() -> dict[str, Any]:
    """Verify the canonical files exist, match a fresh render and recognize."""
    result = render_inert()
    issues: list[str] = []
    if not SQL_INERT_PATH.exists():
        issues.append("missing " + str(SQL_INERT_PATH))
    if not MANIFEST_PATH.exists():
        issues.append("missing " + str(MANIFEST_PATH))
    if not LOWERING_CONTRACT_PATH.exists():
        issues.append("missing " + str(LOWERING_CONTRACT_PATH))
    if not LOWERING_SCHEMA_PATH.exists():
        issues.append("missing " + str(LOWERING_SCHEMA_PATH))
    if issues:
        return {"valid": False, "issues": issues}
    canonical_sql = SQL_INERT_PATH.read_text(encoding="utf-8")
    if canonical_sql != result["sql_text"]:
        issues.append("sql artifact differs from fresh render")
    manifest = _read_json(MANIFEST_PATH)
    if manifest != result["manifest"]:
        issues.append("manifest differs from fresh render")
    if _read_json(LOWERING_CONTRACT_PATH) != build_lowering_contract(
        result["effective"], result["loaded"]
    ):
        issues.append("lowering contract differs from fresh render")
    if _read_json(LOWERING_SCHEMA_PATH) != build_lowering_schema():
        issues.append("lowering schema differs from fresh render")
    report = recognize_inert_sql(canonical_sql, manifest, result["effective"])
    if not report.valid:
        issues.append("recognizer rejected canonical artifact")
    return {"valid": len(issues) == 0, "issues": issues}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Provider-free unmounted durability inert DDL rehearsal"
    )
    parser.add_argument(
        "command",
        choices=("check", "regenerate"),
        help="check canonical inert files or regenerate them",
    )
    args = parser.parse_args()
    if args.command == "regenerate":
        result = render_inert()
        written = write_artifacts(result)
        print("regenerated:")
        for key, path in written.items():
            print("  " + key + ": " + path)
        return 0
    outcome = check_artifacts()
    if outcome["valid"]:
        print("check: ok")
        return 0
    print("check: failed")
    for issue in outcome["issues"]:
        print("  - " + issue)
    return 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
