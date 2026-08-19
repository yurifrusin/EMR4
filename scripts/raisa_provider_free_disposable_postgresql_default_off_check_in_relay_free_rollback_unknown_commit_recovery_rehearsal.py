"""Run the bounded relay-free check-in rollback/unknown-response rehearsal."""

from __future__ import annotations

import argparse
import ast
import copy
import hashlib
import json
import re
import secrets
import shutil
import subprocess
import time
import uuid
from pathlib import Path
from typing import Any, NoReturn

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
TOPIC = ROOT / (
    "orchestration/continuity/raisa-provider-free-disposable-postgresql-default-"
    "off-check-in-relay-free-rollback-unknown-commit-recovery-rehearsal"
)
CONTRACT_PATH = TOPIC / "contract.json"
CONTRACT_SCHEMA_PATH = TOPIC / "contract.schema.json"
MANIFEST_SCHEMA_PATH = TOPIC / "transaction-manifest.schema.json"
ATTESTATION_SCHEMA_PATH = TOPIC / "transaction-attestation.schema.json"
EVIDENCE_SCHEMA_PATH = TOPIC / "evidence.schema.json"
ATTESTATION_PATH = TOPIC / "transaction-attestation.json"
EVIDENCE_PATH = TOPIC / "rehearsal-evidence.json"
FAILURE_PATH = TOPIC / "rehearsal-failure-evidence.json"

PLAN_SOURCE = "eb568174debd6dba2a32d1dea94be7f6b9fd3ddc"
RELAY_FREE_SOURCE = "4f0f54c2b0861828f9994444201b8da1bd54be00"
RUNTIME_ROLE_SOURCE = "6a2832575e9b4df5c40a13984db7281e79814a94"
PROTECTED_SOURCE = "2e34bdad732fdab32fbf778280b3d3c70d66d602"
PASS_RESULT = (
    "raisa_provider_free_disposable_postgresql_default_off_check_in_relay_free_"
    "rollback_unknown_commit_recovery_rehearsal_pass"
)
EVIDENCE_LABEL = (
    "authored_synthetic_provider_free_disposable_postgresql_check_in_relay_free_"
    "rollback_unknown_terminal_response_recovery"
)
PACKET_KEYS = ("effect", "receipt", "audit")
HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
CONTAINER_ID = re.compile(r"^[0-9a-f]{64}$")
ROLE_ID = re.compile(r"^emr4_checkin_rfr_[0-9a-f]{16}$")
APP_ID = re.compile(r"^emr4_checkin_rfr_[0-9a-f]{16}$")

FORBIDDEN_EVIDENCE_KEYS = {
    "password",
    "secret",
    "credential",
    "dsn",
    "environment_value",
    "argv",
    "command_text",
    "raw_sql",
    "query_text",
    "stdout",
    "stderr",
    "exception",
    "backend_pid",
    "container_id",
    "container_name",
    "network_id",
    "network_name",
    "owner_nonce",
    "local_path",
    "patient",
    "appointment",
    "clinical",
}


class RehearsalFailure(RuntimeError):
    def __init__(self, stage: str, code: str, detail: str | None = None) -> None:
        self.stage = stage
        self.code = code
        self.detail = detail
        super().__init__(f"{stage}:{code}")


def _fail(stage: str, code: str, detail: str | None = None) -> NoReturn:
    raise RehearsalFailure(stage, code, detail)


def _canonical_source_bytes(path: Path) -> bytes:
    raw = path.read_bytes()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as caught:
        raise RehearsalFailure("source", "invalid_utf8", path.as_posix()) from caught
    normalized = text.replace("\r\n", "\n")
    if "\r" in normalized:
        _fail("source", "bare_carriage_return", path.as_posix())
    return normalized.encode("utf-8")


def _sha256(value: bytes | str) -> str:
    data = value.encode("utf-8") if isinstance(value, str) else value
    return hashlib.sha256(data).hexdigest()


def _json_bytes(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode(
        "utf-8"
    )


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        _fail("source", "json_root_not_object", path.as_posix())
    return value


def _git(*arguments: str) -> str:
    completed = subprocess.run(
        ["git", *arguments],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
        shell=False,
    )
    if completed.returncode != 0:
        _fail("git", "command_failed")
    return completed.stdout.strip()


def _leaf_paths(
    value: object, prefix: tuple[str | int, ...] = ()
) -> list[tuple[str | int, ...]]:
    if isinstance(value, dict):
        result: list[tuple[str | int, ...]] = []
        for key, child in value.items():
            result.extend(_leaf_paths(child, (*prefix, key)))
        return result
    if isinstance(value, list):
        result = []
        for index, child in enumerate(value):
            result.extend(_leaf_paths(child, (*prefix, index)))
        return result
    return [prefix]


def _value_at(value: object, path: tuple[str | int, ...]) -> object:
    current = value
    for part in path:
        current = current[part]  # type: ignore[index]
    return current


def _replace_leaf(
    candidate: object, path: tuple[str | int, ...], replacement: object
) -> None:
    current = candidate
    for part in path[:-1]:
        current = current[part]  # type: ignore[index]
    current[path[-1]] = replacement  # type: ignore[index]


def _mutated_values(value: object) -> tuple[object, object]:
    if isinstance(value, bool):
        return (not value, "hostile_boolean")
    if isinstance(value, int):
        return (value + 1, -1)
    if isinstance(value, str):
        if HEX40.fullmatch(value):
            return ("0" * 40, value[:-1] + ("0" if value[-1] != "0" else "1"))
        if HEX64.fullmatch(value):
            return ("0" * 64, value[:-1] + ("0" if value[-1] != "0" else "1"))
        return ("", value + "-mutation")
    return (None, "mutation")


def _assert_redacted(value: object, *, forbidden_values: tuple[str, ...]) -> None:
    def walk(item: object) -> None:
        if isinstance(item, dict):
            for key, child in item.items():
                lowered = str(key).lower()
                if lowered in FORBIDDEN_EVIDENCE_KEYS or any(
                    f"{part}_" in lowered or lowered.endswith(f"_{part}")
                    for part in FORBIDDEN_EVIDENCE_KEYS
                ):
                    _fail("redaction", "forbidden_field")
                walk(child)
        elif isinstance(item, list):
            for child in item:
                walk(child)
        elif isinstance(item, str):
            if any(secret and secret in item for secret in forbidden_values):
                _fail("redaction", "forbidden_value")

    walk(value)


def validate_contract(
    value: object, *, canonical: dict[str, Any] | None = None
) -> dict[str, Any]:
    schema = _load_json(CONTRACT_SCHEMA_PATH)
    errors = list(Draft202012Validator(schema).iter_errors(value))
    if errors or not isinstance(value, dict):
        _fail("contract", "schema_invalid")
    contract = copy.deepcopy(value)
    expected = {
        "plan_source": PLAN_SOURCE,
        "accepted_relay_free_transport_source": RELAY_FREE_SOURCE,
        "accepted_runtime_role_source": RUNTIME_ROLE_SOURCE,
        "protected_source": PROTECTED_SOURCE,
        "result": PASS_RESULT,
        "evidence_label": EVIDENCE_LABEL,
    }
    if any(contract.get(key) != expected_value for key, expected_value in expected.items()):
        _fail("contract", "authority_binding_mismatch")
    if any(contract["closed_boundaries"].values()):
        _fail("contract", "closed_boundary_open")
    if canonical is not None and contract != canonical:
        _fail("contract", "noncanonical")
    return contract


def hostile_contract_mutations_rejected(
    contract: dict[str, Any], threshold: int
) -> tuple[int, int]:
    attempted = 0
    rejected = 0
    for path in _leaf_paths(contract):
        current = _value_at(contract, path)
        for replacement in _mutated_values(current):
            candidate = copy.deepcopy(contract)
            _replace_leaf(candidate, path, replacement)
            attempted += 1
            try:
                validate_contract(candidate, canonical=contract)
            except RehearsalFailure:
                rejected += 1
    if attempted < threshold or attempted != rejected:
        _fail("contract", "hostile_mutation_escape")
    return attempted, rejected


def verify_contract() -> tuple[dict[str, Any], dict[str, str], tuple[int, int]]:
    contract = validate_contract(_load_json(CONTRACT_PATH))
    mutations = hostile_contract_mutations_rejected(
        contract, contract["hostile_thresholds"]["contract"]
    )
    hashes: dict[str, str] = {}
    for binding in contract["source_bindings"]:
        path = ROOT / binding["path"]
        if not path.is_file():
            _fail("source", "binding_missing", binding["path"])
        digest = _sha256(_canonical_source_bytes(path))
        hashes[binding["path"]] = digest
        if digest != binding["sha256"]:
            _fail("source", "binding_digest_mismatch", binding["path"])
    if len(hashes) != 15 or len(hashes) != len(contract["source_bindings"]):
        _fail("source", "binding_count_mismatch")
    if _git("cat-file", "-t", PLAN_SOURCE) != "commit":
        _fail("git", "plan_source_not_commit")
    current = _git("rev-parse", "HEAD")
    if HEX40.fullmatch(current) is None:
        _fail("git", "head_not_full_git")
    ancestry = subprocess.run(
        ["git", "merge-base", "--is-ancestor", PLAN_SOURCE, current],
        cwd=ROOT,
        check=False,
        capture_output=True,
        timeout=30,
        shell=False,
    )
    if ancestry.returncode != 0:
        _fail("git", "plan_source_not_ancestor")
    return contract, hashes, mutations


def build_manifest(contract: dict[str, Any], physical_role: str) -> dict[str, Any]:
    transaction = contract["transaction_profile"]
    return {
        "schema_version": transaction["manifest_schema_version"],
        "environment_identifier": transaction["environment_identifier"],
        "practice_scope_reference": transaction["practice_scope_reference"],
        "practice_id": transaction["practice_id"],
        "other_practice_id": transaction["other_practice_id"],
        "logical_role_id": contract["role_profile"]["logical_role_id"],
        "physical_role_identifier": physical_role,
        "authority_git_object": contract["accepted_runtime_role_source"],
        "commands": {
            "rollback": copy.deepcopy(transaction["rollback"]),
            "ambiguous_response": copy.deepcopy(transaction["ambiguous_response"]),
        },
        "automatic_retry_count": transaction["automatic_retry_count"],
        "ordinary_admission_release_count": transaction[
            "ordinary_admission_release_count"
        ],
        "product_record_count": transaction["product_record_count"],
    }


def validate_manifest(
    value: object, *, physical_role: str, canonical: dict[str, Any] | None = None
) -> dict[str, Any]:
    schema = _load_json(MANIFEST_SCHEMA_PATH)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = list(validator.iter_errors(value))
    if errors or not isinstance(value, dict):
        _fail("manifest", "schema_invalid")
    manifest = copy.deepcopy(value)
    if (
        manifest["physical_role_identifier"] != physical_role
        or manifest["authority_git_object"] != RUNTIME_ROLE_SOURCE
        or manifest["practice_id"] == manifest["other_practice_id"]
    ):
        _fail("manifest", "authority_or_tenant_binding_mismatch")
    commands = manifest["commands"]
    if commands["rollback"]["command_id"] == commands["ambiguous_response"][
        "command_id"
    ]:
        _fail("manifest", "command_identity_collision")
    if canonical is not None and manifest != canonical:
        _fail("manifest", "noncanonical")
    return manifest


def hostile_manifest_mutations_rejected(
    manifest: dict[str, Any], physical_role: str, threshold: int
) -> tuple[int, int]:
    attempted = 0
    rejected = 0
    for path in _leaf_paths(manifest):
        for replacement in _mutated_values(_value_at(manifest, path)):
            candidate = copy.deepcopy(manifest)
            _replace_leaf(candidate, path, replacement)
            attempted += 1
            try:
                validate_manifest(
                    candidate, physical_role=physical_role, canonical=manifest
                )
            except RehearsalFailure:
                rejected += 1
    while attempted < threshold:
        candidate = copy.deepcopy(manifest)
        candidate[f"hostile_{attempted}"] = attempted
        attempted += 1
        try:
            validate_manifest(candidate, physical_role=physical_role, canonical=manifest)
        except RehearsalFailure:
            rejected += 1
    if attempted != rejected:
        _fail("manifest", "hostile_mutation_escape")
    return attempted, rejected


def packet_counts(packet: dict[str, Any]) -> dict[str, int]:
    return {key: len(packet.get(key, [])) for key in PACKET_KEYS}


def _canonical_uuid(value: object) -> bool:
    try:
        return str(uuid.UUID(str(value))) == value
    except (ValueError, TypeError, AttributeError):
        return False


def classify_readback(packet: object, expected_request_sha256: str) -> str:
    denied = "unresolved_denied"
    if not isinstance(packet, dict) or set(packet) != set(PACKET_KEYS):
        return denied
    if any(not isinstance(packet[key], list) for key in PACKET_KEYS):
        return denied
    counts = packet_counts(packet)
    if counts == {"effect": 0, "receipt": 0, "audit": 0}:
        return "rolled_back_zero_effect"
    if counts != {"effect": 1, "receipt": 1, "audit": 1}:
        return denied
    effect = packet["effect"][0]
    receipt = packet["receipt"][0]
    audit = packet["audit"][0]
    expected_keys = {
        "effect": {
            "practice_id",
            "command_id",
            "effect_id",
            "idempotency_identity",
            "request_sha256",
            "effect_kind",
        },
        "receipt": {
            "practice_id",
            "command_id",
            "effect_id",
            "idempotency_identity",
            "request_sha256",
            "outcome",
        },
        "audit": {
            "practice_id",
            "command_id",
            "effect_id",
            "audit_id",
            "idempotency_identity",
            "request_sha256",
            "action",
        },
    }
    rows = {"effect": effect, "receipt": receipt, "audit": audit}
    if any(
        not isinstance(row, dict) or set(row) != expected_keys[name]
        for name, row in rows.items()
    ):
        return denied
    shared = (
        "practice_id",
        "command_id",
        "effect_id",
        "idempotency_identity",
        "request_sha256",
    )
    if any(effect[key] != receipt[key] or effect[key] != audit[key] for key in shared):
        return denied
    if not all(
        _canonical_uuid(effect[key])
        for key in ("practice_id", "command_id", "effect_id")
    ) or not _canonical_uuid(audit["audit_id"]):
        return denied
    if (
        effect["request_sha256"] != expected_request_sha256
        or HEX64.fullmatch(expected_request_sha256) is None
        or re.fullmatch(
            r"idem:authored-synthetic/[a-z0-9-]{8,80}",
            effect["idempotency_identity"],
        )
        is None
        or effect["effect_kind"] != "check_in"
        or receipt["outcome"] != "committed"
        or audit["action"] != "check_in_committed"
    ):
        return denied
    return "committed_exactly_once"


def _canonical_packet(manifest: dict[str, Any]) -> dict[str, Any]:
    command = manifest["commands"]["ambiguous_response"]
    shared = {
        "practice_id": manifest["practice_id"],
        "command_id": command["command_id"],
        "effect_id": command["effect_id"],
        "idempotency_identity": command["idempotency_identity"],
        "request_sha256": command["request_sha256"],
    }
    return {
        "effect": [{**shared, "effect_kind": "check_in"}],
        "receipt": [{**shared, "outcome": "committed"}],
        "audit": [
            {**shared, "audit_id": command["audit_id"], "action": "check_in_committed"}
        ],
    }


def hostile_classifier_packets_rejected(
    packet: dict[str, Any], expected_request_sha256: str, threshold: int
) -> tuple[int, int]:
    candidates: list[object] = []
    for member in PACKET_KEYS:
        duplicate = copy.deepcopy(packet)
        duplicate[member].append(copy.deepcopy(duplicate[member][0]))
        candidates.append(duplicate)
        missing = copy.deepcopy(packet)
        missing[member] = []
        candidates.append(missing)
    replacements = {
        "practice_id": "44444444-4444-4444-8444-444444444444",
        "command_id": "55555555-5555-4555-8555-555555555555",
        "effect_id": "66666666-6666-4666-8666-666666666666",
        "audit_id": "77777777-7777-4777-8777-777777777777",
        "idempotency_identity": "idem:authored-synthetic/hostile-mismatch-v1",
        "request_sha256": "0" * 64,
        "effect_kind": "status_change",
        "outcome": "unknown",
        "action": "other",
    }
    for member in PACKET_KEYS:
        for field in packet[member][0]:
            if field == "audit_id":
                continue
            candidate = copy.deepcopy(packet)
            candidate[member][0][field] = replacements[field]
            candidates.append(candidate)
    while len(candidates) < threshold:
        candidate = copy.deepcopy(packet)
        candidate[f"hostile_{len(candidates)}"] = len(candidates)
        candidates.append(candidate)
    rejected = sum(
        classify_readback(candidate, expected_request_sha256) == "unresolved_denied"
        for candidate in candidates
    )
    if rejected != len(candidates):
        _fail("classifier", "hostile_packet_escape")
    return len(candidates), rejected


def _closed_state(row: dict[str, Any], *, identity_match: bool) -> dict[str, Any]:
    state = row.get("State", {})
    restart_count = row.get("RestartCount")
    return {
        "identity_match": identity_match,
        "stopped": state.get("Running") is False,
        "exit_code": state.get("ExitCode"),
        "oom_killed": state.get("OOMKilled"),
        "state_error_empty": state.get("Error") == "",
        "restart_count": restart_count,
    }


def classify_caller_state(value: object, *, observer_passed: bool) -> str:
    expected = {
        "identity_match",
        "stopped",
        "exit_code",
        "oom_killed",
        "state_error_empty",
        "restart_count",
    }
    if not isinstance(value, dict) or set(value) != expected:
        return "unresolved_denied"
    if value == {
        "identity_match": True,
        "stopped": True,
        "exit_code": 42,
        "oom_killed": False,
        "state_error_empty": True,
        "restart_count": 0,
    } and observer_passed:
        return "connection_lost_without_complete_terminal_response"
    return "unresolved_denied"


def hostile_states_rejected(threshold: int) -> tuple[int, int]:
    canonical = {
        "identity_match": True,
        "stopped": True,
        "exit_code": 42,
        "oom_killed": False,
        "state_error_empty": True,
        "restart_count": 0,
    }
    candidates: list[tuple[object, bool]] = [(copy.deepcopy(canonical), False)]
    for path in _leaf_paths(canonical):
        for replacement in _mutated_values(_value_at(canonical, path)):
            candidate = copy.deepcopy(canonical)
            _replace_leaf(candidate, path, replacement)
            candidates.append((candidate, True))
    while len(candidates) < threshold:
        candidate = copy.deepcopy(canonical)
        candidate[f"hostile_{len(candidates)}"] = len(candidates)
        candidates.append((candidate, True))
    rejected = sum(
        classify_caller_state(value, observer_passed=observer)
        == "unresolved_denied"
        for value, observer in candidates
    )
    if rejected != len(candidates):
        _fail("outcome", "hostile_state_escape")
    return len(candidates), rejected


def static_check() -> dict[str, Any]:
    contract, hashes, contract_mutations = verify_contract()
    sample_role = "emr4_checkin_rfr_0123456789abcdef"
    manifest = build_manifest(contract, sample_role)
    validate_manifest(manifest, physical_role=sample_role, canonical=manifest)
    manifest_mutations = hostile_manifest_mutations_rejected(
        manifest,
        sample_role,
        contract["hostile_thresholds"]["manifest_and_evidence_state"],
    )
    packet = _canonical_packet(manifest)
    if classify_readback(
        packet, manifest["commands"]["ambiguous_response"]["request_sha256"]
    ) != "committed_exactly_once":
        _fail("classifier", "canonical_packet_denied")
    if classify_readback(
        {"effect": [], "receipt": [], "audit": []},
        manifest["commands"]["rollback"]["request_sha256"],
    ) != "rolled_back_zero_effect":
        _fail("classifier", "empty_packet_denied")
    classifier_mutations = hostile_classifier_packets_rejected(
        packet,
        manifest["commands"]["ambiguous_response"]["request_sha256"],
        contract["hostile_thresholds"]["classifier"],
    )
    state_mutations = hostile_states_rejected(
        contract["hostile_thresholds"]["manifest_and_evidence_state"]
    )
    verify_program_digests(contract, manifest, sample_role)
    source = Path(__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    banned_imports = {"socket", "multiprocessing", "queue"}
    imported = {
        alias.name.split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in node.names
    }
    forbidden_symbol = "Docker" + "ExecRelay"
    if imported & banned_imports or any(
        isinstance(node, ast.Name) and node.id == forbidden_symbol
        for node in ast.walk(tree)
    ):
        _fail("static", "forbidden_host_control_path")
    for schema_path in (
        CONTRACT_SCHEMA_PATH,
        MANIFEST_SCHEMA_PATH,
        ATTESTATION_SCHEMA_PATH,
        EVIDENCE_SCHEMA_PATH,
    ):
        Draft202012Validator.check_schema(_load_json(schema_path))
    return {
        "status": "passed",
        "source_head": _git("rev-parse", "HEAD"),
        "plan_source": PLAN_SOURCE,
        "source_binding_count": len(hashes),
        "contract_sha256": _sha256(_canonical_source_bytes(CONTRACT_PATH)),
        "manifest_sha256": _sha256(_json_bytes(manifest)),
        "contract_mutations": {
            "attempted": contract_mutations[0],
            "rejected": contract_mutations[1],
        },
        "manifest_mutations": {
            "attempted": manifest_mutations[0],
            "rejected": manifest_mutations[1],
        },
        "classifier_mutations": {
            "attempted": classifier_mutations[0],
            "rejected": classifier_mutations[1],
        },
        "state_mutations": {
            "attempted": state_mutations[0],
            "rejected": state_mutations[1],
        },
    }


def _insert_packet_sql(schema: str, practice_id: str, command: dict[str, str]) -> str:
    return f"""
INSERT INTO {schema}.command_effect
  (practice_id,command_id,effect_id,idempotency_identity,request_sha256,effect_kind)
VALUES
  ('{practice_id}','{command['command_id']}','{command['effect_id']}',
   '{command['idempotency_identity']}','{command['request_sha256']}','check_in');
INSERT INTO {schema}.command_receipt
  (practice_id,command_id,effect_id,idempotency_identity,request_sha256,outcome)
VALUES
  ('{practice_id}','{command['command_id']}','{command['effect_id']}',
   '{command['idempotency_identity']}','{command['request_sha256']}','committed');
INSERT INTO {schema}.command_audit
  (practice_id,command_id,effect_id,audit_id,idempotency_identity,request_sha256,action)
VALUES
  ('{practice_id}','{command['command_id']}','{command['effect_id']}',
   '{command['audit_id']}','{command['idempotency_identity']}',
   '{command['request_sha256']}','check_in_committed');
"""


def _setup_sql(contract: dict[str, Any], physical_role: str) -> str:
    if ROLE_ID.fullmatch(physical_role) is None:
        _fail("program", "physical_role_invalid")
    schema = contract["database_profile"]["schema"]
    admin = contract["server_profile"]["postgres_user"]
    database = contract["server_profile"]["postgres_database"]
    setting = contract["database_profile"]["policy_setting"]
    return f"""
REVOKE ALL ON SCHEMA public FROM PUBLIC;
CREATE SCHEMA {schema} AUTHORIZATION {admin};
CREATE TABLE {schema}.command_effect (
  practice_id uuid NOT NULL,
  command_id uuid NOT NULL,
  effect_id uuid NOT NULL,
  idempotency_identity text NOT NULL,
  request_sha256 varchar(64) NOT NULL,
  effect_kind text NOT NULL,
  CONSTRAINT command_effect_pk PRIMARY KEY (practice_id, command_id),
  CONSTRAINT command_effect_id_uq UNIQUE (practice_id, effect_id),
  CONSTRAINT command_effect_packet_uq UNIQUE
    (practice_id, command_id, effect_id, idempotency_identity, request_sha256),
  CONSTRAINT command_effect_idempotency_uq
    UNIQUE (practice_id, idempotency_identity),
  CONSTRAINT command_effect_idem_ck CHECK
    (idempotency_identity ~ '^idem:authored-synthetic/[a-z0-9-]{{8,80}}$'),
  CONSTRAINT command_effect_digest_ck CHECK (request_sha256 ~ '^[0-9a-f]{{64}}$'),
  CONSTRAINT command_effect_kind_ck CHECK (effect_kind = 'check_in')
);
CREATE TABLE {schema}.command_receipt (
  practice_id uuid NOT NULL,
  command_id uuid NOT NULL,
  effect_id uuid NOT NULL,
  idempotency_identity text NOT NULL,
  request_sha256 varchar(64) NOT NULL,
  outcome text NOT NULL,
  CONSTRAINT command_receipt_pk PRIMARY KEY (practice_id, command_id),
  CONSTRAINT command_receipt_idempotency_uq
    UNIQUE (practice_id, idempotency_identity),
  CONSTRAINT command_receipt_packet_uq UNIQUE
    (practice_id, command_id, effect_id, idempotency_identity, request_sha256),
  CONSTRAINT command_receipt_effect_fk FOREIGN KEY
    (practice_id, command_id, effect_id, idempotency_identity, request_sha256)
    REFERENCES {schema}.command_effect
    (practice_id, command_id, effect_id, idempotency_identity, request_sha256),
  CONSTRAINT command_receipt_idem_ck CHECK
    (idempotency_identity ~ '^idem:authored-synthetic/[a-z0-9-]{{8,80}}$'),
  CONSTRAINT command_receipt_digest_ck CHECK
    (request_sha256 ~ '^[0-9a-f]{{64}}$'),
  CONSTRAINT command_receipt_outcome_ck CHECK (outcome = 'committed')
);
CREATE TABLE {schema}.command_audit (
  practice_id uuid NOT NULL,
  command_id uuid NOT NULL,
  effect_id uuid NOT NULL,
  audit_id uuid NOT NULL,
  idempotency_identity text NOT NULL,
  request_sha256 varchar(64) NOT NULL,
  action text NOT NULL,
  CONSTRAINT command_audit_pk PRIMARY KEY (practice_id, audit_id),
  CONSTRAINT command_audit_command_uq UNIQUE (practice_id, command_id),
  CONSTRAINT command_audit_idempotency_uq UNIQUE
    (practice_id, idempotency_identity),
  CONSTRAINT command_audit_receipt_fk FOREIGN KEY
    (practice_id, command_id, effect_id, idempotency_identity, request_sha256)
    REFERENCES {schema}.command_receipt
    (practice_id, command_id, effect_id, idempotency_identity, request_sha256),
  CONSTRAINT command_audit_idem_ck CHECK
    (idempotency_identity ~ '^idem:authored-synthetic/[a-z0-9-]{{8,80}}$'),
  CONSTRAINT command_audit_digest_ck CHECK (request_sha256 ~ '^[0-9a-f]{{64}}$'),
  CONSTRAINT command_audit_action_ck CHECK (action = 'check_in_committed')
);
ALTER TABLE {schema}.command_effect ENABLE ROW LEVEL SECURITY;
ALTER TABLE {schema}.command_effect FORCE ROW LEVEL SECURITY;
ALTER TABLE {schema}.command_receipt ENABLE ROW LEVEL SECURITY;
ALTER TABLE {schema}.command_receipt FORCE ROW LEVEL SECURITY;
ALTER TABLE {schema}.command_audit ENABLE ROW LEVEL SECURITY;
ALTER TABLE {schema}.command_audit FORCE ROW LEVEL SECURITY;
CREATE POLICY command_effect_tenant ON {schema}.command_effect
  USING (practice_id = nullif(current_setting('{setting}', true), '')::uuid)
  WITH CHECK (practice_id = nullif(current_setting('{setting}', true), '')::uuid);
CREATE POLICY command_receipt_tenant ON {schema}.command_receipt
  USING (practice_id = nullif(current_setting('{setting}', true), '')::uuid)
  WITH CHECK (practice_id = nullif(current_setting('{setting}', true), '')::uuid);
CREATE POLICY command_audit_tenant ON {schema}.command_audit
  USING (practice_id = nullif(current_setting('{setting}', true), '')::uuid)
  WITH CHECK (practice_id = nullif(current_setting('{setting}', true), '')::uuid);
CREATE ROLE {physical_role} LOGIN PASSWORD :'runtime_password'
  NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOREPLICATION NOBYPASSRLS;
GRANT CONNECT ON DATABASE {database} TO {physical_role};
GRANT USAGE ON SCHEMA {schema} TO {physical_role};
GRANT SELECT, INSERT ON
  {schema}.command_effect,
  {schema}.command_receipt,
  {schema}.command_audit
TO {physical_role};
DO $emr4$
BEGIN
  IF (SELECT count(*) FROM pg_roles
      WHERE rolname='{physical_role}' AND rolcanlogin AND NOT rolsuper
        AND NOT rolcreatedb AND NOT rolcreaterole AND NOT rolinherit
        AND NOT rolreplication AND NOT rolbypassrls) <> 1 THEN
    RAISE EXCEPTION 'role posture mismatch';
  END IF;
  IF (SELECT count(*) FROM pg_auth_members m JOIN pg_roles r ON r.oid=m.member
      WHERE r.rolname='{physical_role}') <> 0 THEN
    RAISE EXCEPTION 'role membership mismatch';
  END IF;
  IF (SELECT
        (SELECT count(*) FROM pg_database d JOIN pg_roles r
          ON r.oid=d.datdba WHERE r.rolname='{physical_role}') +
        (SELECT count(*) FROM pg_namespace n JOIN pg_roles r
          ON r.oid=n.nspowner WHERE r.rolname='{physical_role}') +
        (SELECT count(*) FROM pg_class c JOIN pg_roles r
          ON r.oid=c.relowner WHERE r.rolname='{physical_role}') +
        (SELECT count(*) FROM pg_proc p JOIN pg_roles r
          ON r.oid=p.proowner WHERE r.rolname='{physical_role}')) <> 0 THEN
    RAISE EXCEPTION 'role ownership mismatch';
  END IF;
  IF (SELECT count(*) FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
      WHERE n.nspname='{schema}' AND c.relkind='r') <> 3 THEN
    RAISE EXCEPTION 'relation count mismatch';
  END IF;
  IF (SELECT count(*) FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
      JOIN pg_roles r ON r.oid=c.relowner
      WHERE n.nspname='{schema}' AND c.relkind='r' AND r.rolname='{admin}'
        AND c.relrowsecurity AND c.relforcerowsecurity) <> 3 THEN
    RAISE EXCEPTION 'relation ownership or RLS mismatch';
  END IF;
  IF (SELECT count(*) FROM pg_policy p JOIN pg_class c ON c.oid=p.polrelid
      JOIN pg_namespace n ON n.oid=c.relnamespace
      WHERE n.nspname='{schema}') <> 3 THEN
    RAISE EXCEPTION 'policy count mismatch';
  END IF;
  IF (SELECT count(*) FROM pg_constraint c JOIN pg_namespace n
      ON n.oid=c.connamespace WHERE n.nspname='{schema}') <> 21 THEN
    RAISE EXCEPTION 'constraint count mismatch';
  END IF;
  IF (SELECT count(*) FROM information_schema.table_privileges
      WHERE grantee='{physical_role}' AND table_schema='{schema}'
        AND privilege_type IN ('INSERT','SELECT')) <> 6 THEN
    RAISE EXCEPTION 'probe grant mismatch';
  END IF;
  IF (SELECT count(*) FROM information_schema.table_privileges
      WHERE grantee='{physical_role}' AND table_schema<>'{schema}') <> 0 THEN
    RAISE EXCEPTION 'product privilege mismatch';
  END IF;
  IF has_schema_privilege('{physical_role}', 'public', 'USAGE') THEN
    RAISE EXCEPTION 'public schema usage mismatch';
  END IF;
  IF NOT has_schema_privilege('{physical_role}', '{schema}', 'USAGE')
     OR NOT has_database_privilege('{physical_role}', '{database}', 'CONNECT') THEN
    RAISE EXCEPTION 'connect or schema grant mismatch';
  END IF;
END
$emr4$;
"""


def _rollback_sql(contract: dict[str, Any], manifest: dict[str, Any]) -> str:
    schema = contract["database_profile"]["schema"]
    practice = manifest["practice_id"]
    command = manifest["commands"]["rollback"]
    inserts = _insert_packet_sql(schema, practice, command)
    return f"""
BEGIN;
SET LOCAL app.current_practice_id = '{practice}';
{inserts}
DO $emr4$
BEGIN
  IF (SELECT count(*) FROM {schema}.command_effect
      WHERE command_id='{command['command_id']}') <> 1
     OR (SELECT count(*) FROM {schema}.command_receipt
      WHERE command_id='{command['command_id']}') <> 1
     OR (SELECT count(*) FROM {schema}.command_audit
      WHERE command_id='{command['command_id']}') <> 1 THEN
    RAISE EXCEPTION 'staged packet mismatch';
  END IF;
END
$emr4$;
ROLLBACK;
"""


def _rollback_readback_sql(
    contract: dict[str, Any], manifest: dict[str, Any]
) -> str:
    schema = contract["database_profile"]["schema"]
    practice = manifest["practice_id"]
    command = manifest["commands"]["rollback"]
    return f"""
BEGIN;
SET LOCAL app.current_practice_id = '{practice}';
DO $emr4$
BEGIN
  IF (SELECT count(*) FROM {schema}.command_effect
      WHERE command_id='{command['command_id']}'
         OR idempotency_identity='{command['idempotency_identity']}') <> 0
     OR (SELECT count(*) FROM {schema}.command_receipt
      WHERE command_id='{command['command_id']}'
         OR idempotency_identity='{command['idempotency_identity']}') <> 0
     OR (SELECT count(*) FROM {schema}.command_audit
      WHERE command_id='{command['command_id']}'
         OR idempotency_identity='{command['idempotency_identity']}') <> 0 THEN
    RAISE EXCEPTION 'rollback durable effect mismatch';
  END IF;
END
$emr4$;
COMMIT;
"""


def _ambiguous_sql(contract: dict[str, Any], manifest: dict[str, Any]) -> str:
    schema = contract["database_profile"]["schema"]
    practice = manifest["practice_id"]
    command = manifest["commands"]["ambiguous_response"]
    hold = contract["containment_profile"]["post_commit_hold_seconds"]
    inserts = _insert_packet_sql(schema, practice, command)
    return f"""
BEGIN;
SET LOCAL app.current_practice_id = '{practice}';
{inserts}
COMMIT;
SELECT pg_sleep({hold});
"""


def _observer_sql(
    contract: dict[str, Any], physical_role: str, application_name: str
) -> str:
    if ROLE_ID.fullmatch(physical_role) is None or APP_ID.fullmatch(application_name) is None:
        _fail("program", "observer_identity_invalid")
    database = contract["server_profile"]["postgres_database"]
    timeout = contract["containment_profile"]["observer_timeout_seconds"]
    return f"""
DO $emr4$
DECLARE
  target_pid integer;
  matches integer;
  deadline timestamptz := clock_timestamp() + interval '{timeout} seconds';
BEGIN
  LOOP
    SELECT count(*), min(pid) INTO matches, target_pid
    FROM pg_stat_activity
    WHERE application_name='{application_name}'
      AND usename='{physical_role}'
      AND datname='{database}'
      AND wait_event_type='Timeout'
      AND wait_event='PgSleep';
    IF matches > 1 THEN
      RAISE EXCEPTION 'ambiguous backend multiplicity';
    END IF;
    IF matches = 1 THEN
      IF NOT pg_terminate_backend(target_pid) THEN
        RAISE EXCEPTION 'backend termination denied';
      END IF;
      RETURN;
    END IF;
    IF clock_timestamp() >= deadline THEN
      RAISE EXCEPTION 'post-commit hold not observed';
    END IF;
    PERFORM pg_sleep(0.05);
  END LOOP;
END
$emr4$;
"""


def _authoritative_readback_sql(
    contract: dict[str, Any], manifest: dict[str, Any]
) -> str:
    schema = contract["database_profile"]["schema"]
    practice = manifest["practice_id"]
    other_practice = manifest["other_practice_id"]
    command = manifest["commands"]["ambiguous_response"]
    identity = command["idempotency_identity"]
    return f"""
BEGIN;
SET LOCAL app.current_practice_id = '{practice}';
DO $emr4$
BEGIN
  IF (SELECT count(*) FROM {schema}.command_effect
      WHERE command_id='{command['command_id']}' OR idempotency_identity='{identity}') <> 1
     OR (SELECT count(*) FROM {schema}.command_receipt
      WHERE command_id='{command['command_id']}' OR idempotency_identity='{identity}') <> 1
     OR (SELECT count(*) FROM {schema}.command_audit
      WHERE command_id='{command['command_id']}' OR idempotency_identity='{identity}') <> 1 THEN
    RAISE EXCEPTION 'packet cardinality mismatch';
  END IF;
  IF (SELECT count(*) FROM {schema}.command_effect
      WHERE practice_id='{practice}' AND command_id='{command['command_id']}'
        AND effect_id='{command['effect_id']}' AND idempotency_identity='{identity}'
        AND request_sha256='{command['request_sha256']}'
        AND effect_kind='check_in') <> 1
     OR (SELECT count(*) FROM {schema}.command_receipt
      WHERE practice_id='{practice}' AND command_id='{command['command_id']}'
        AND effect_id='{command['effect_id']}' AND idempotency_identity='{identity}'
        AND request_sha256='{command['request_sha256']}' AND outcome='committed') <> 1
     OR (SELECT count(*) FROM {schema}.command_audit
      WHERE practice_id='{practice}' AND command_id='{command['command_id']}'
        AND effect_id='{command['effect_id']}' AND audit_id='{command['audit_id']}'
        AND idempotency_identity='{identity}'
        AND request_sha256='{command['request_sha256']}'
        AND action='check_in_committed') <> 1 THEN
    RAISE EXCEPTION 'packet identity mismatch';
  END IF;
END
$emr4$;
COMMIT;
BEGIN;
SET LOCAL app.current_practice_id = '{other_practice}';
DO $emr4$
BEGIN
  IF (SELECT count(*) FROM {schema}.command_effect
      WHERE command_id='{command['command_id']}' OR idempotency_identity='{identity}') <> 0
     OR (SELECT count(*) FROM {schema}.command_receipt
      WHERE command_id='{command['command_id']}' OR idempotency_identity='{identity}') <> 0
     OR (SELECT count(*) FROM {schema}.command_audit
      WHERE command_id='{command['command_id']}' OR idempotency_identity='{identity}') <> 0 THEN
    RAISE EXCEPTION 'cross-practice visibility mismatch';
  END IF;
END
$emr4$;
COMMIT;
"""


def _role_cleanup_sql(contract: dict[str, Any], physical_role: str) -> str:
    if ROLE_ID.fullmatch(physical_role) is None:
        _fail("program", "cleanup_role_invalid")
    schema = contract["database_profile"]["schema"]
    return f"""
DROP SCHEMA IF EXISTS {schema} CASCADE;
DO $emr4$
BEGIN
  IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname='{physical_role}') THEN
    EXECUTE 'DROP OWNED BY {physical_role}';
    EXECUTE 'DROP ROLE {physical_role}';
  END IF;
  IF (SELECT count(*) FROM pg_roles WHERE rolname='{physical_role}') <> 0 THEN
    RAISE EXCEPTION 'role still present';
  END IF;
END
$emr4$;
"""


def _server_wrapper(contract: dict[str, Any]) -> str:
    server = contract["server_profile"]
    return f"""set -eu
IFS= read -r emr4_admin_password
case "$emr4_admin_password" in ""|*[!0-9a-f]*) exit 43 ;; esac
[ "${{#emr4_admin_password}}" -eq 64 ] || exit 43
export POSTGRES_PASSWORD="$emr4_admin_password"
export POSTGRES_USER="{server['postgres_user']}"
export POSTGRES_DB="{server['postgres_database']}"
export PGDATA="{server['pgdata']}"
export POSTGRES_INITDB_ARGS="--auth-host={server['host_auth']}"
unset emr4_admin_password
exec /usr/local/bin/docker-entrypoint.sh postgres -c listen_addresses='*'
"""


READINESS_WRAPPER = """set -eu
IFS= read -r emr4_password
case "$emr4_password" in ""|*[!0-9a-f]*) exit 43 ;; esac
[ "${#emr4_password}" -eq 64 ] || exit 43
export PGPASSWORD="$emr4_password"
emr4_attempt=0
while [ "$emr4_attempt" -lt 90 ]; do
  if psql -X --no-psqlrc --set=ON_ERROR_STOP=1 --host="$1" --port=5432 \
    --username="$2" --dbname="$3" --command='SELECT 1' >/dev/null 2>&1; then
    unset PGPASSWORD emr4_password
    exit 0
  fi
  emr4_attempt=$((emr4_attempt + 1))
  sleep 1
done
unset PGPASSWORD emr4_password
exit 43
"""

ACTION_WRAPPER = """set -eu
IFS= read -r emr4_password
case "$emr4_password" in ""|*[!0-9a-f]*) exit 43 ;; esac
[ "${#emr4_password}" -eq 64 ] || exit 43
export PGPASSWORD="$emr4_password"
export PGAPPNAME="$5"
set +e
psql -X --no-psqlrc --set=ON_ERROR_STOP=1 --host="$1" --port=5432 \
  --username="$2" --dbname="$3" --command="$4" >/dev/null 2>&1
emr4_status=$?
set -e
unset PGPASSWORD PGAPPNAME emr4_password
if [ "$6" = "loss" ]; then
  [ "$emr4_status" -ne 0 ] && exit 42
  exit 0
fi
[ "$emr4_status" -eq 0 ] && exit 0
exit 43
"""

SETUP_WRAPPER = """set -eu
IFS= read -r emr4_admin_password
IFS= read -r emr4_runtime_password
case "$emr4_admin_password" in ""|*[!0-9a-f]*) exit 43 ;; esac
case "$emr4_runtime_password" in ""|*[!0-9a-f]*) exit 43 ;; esac
[ "${#emr4_admin_password}" -eq 64 ] || exit 43
[ "${#emr4_runtime_password}" -eq 64 ] || exit 43
export PGPASSWORD="$emr4_admin_password"
export PGAPPNAME="$5"
set +e
printf "\\set runtime_password '%s'\n%s\n" "$emr4_runtime_password" "$4" | \
  psql -X --no-psqlrc --set=ON_ERROR_STOP=1 --host="$1" --port=5432 \
  --username="$2" --dbname="$3" >/dev/null 2>&1
emr4_status=$?
set -e
unset PGPASSWORD PGAPPNAME emr4_admin_password emr4_runtime_password
[ "$emr4_status" -eq 0 ] && exit 0
exit 43
"""


def verify_program_digests(
    contract: dict[str, Any], manifest: dict[str, Any], physical_role: str
) -> None:
    sample_application = "emr4_checkin_rfr_1111111111111111"
    programs = {
        "server_wrapper": _server_wrapper(contract),
        "readiness_wrapper": READINESS_WRAPPER,
        "action_wrapper": ACTION_WRAPPER,
        "setup_wrapper": SETUP_WRAPPER,
        "setup_sql": _setup_sql(contract, physical_role),
        "rollback_sql": _rollback_sql(contract, manifest),
        "rollback_readback_sql": _rollback_readback_sql(contract, manifest),
        "ambiguous_sql": _ambiguous_sql(contract, manifest),
        "observer_sql": _observer_sql(
            contract, physical_role, sample_application
        ),
        "authoritative_readback_sql": _authoritative_readback_sql(
            contract, manifest
        ),
        "role_cleanup_sql": _role_cleanup_sql(contract, physical_role),
    }
    observed = {name: _sha256(program) for name, program in programs.items()}
    if observed != contract["program_sha256"]:
        _fail("program", "digest_mismatch")


def _docker(
    executable: str,
    *arguments: str,
    check: bool = True,
    timeout: int = 30,
) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        [executable, *arguments],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        timeout=timeout,
        shell=False,
    )
    if check and completed.returncode != 0:
        _fail("docker", "command_failed")
    return completed


def _docker_json(executable: str, *arguments: str) -> list[dict[str, Any]]:
    completed = _docker(executable, *arguments)
    try:
        value = json.loads(completed.stdout)
    except json.JSONDecodeError as caught:
        raise RehearsalFailure("docker", "json_invalid") from caught
    if not isinstance(value, list) or any(not isinstance(row, dict) for row in value):
        _fail("docker", "json_shape_invalid")
    return value


def _docker_executable(contract: dict[str, Any]) -> str:
    configured = contract["containment_profile"]["executable"]
    executable = shutil.which(configured) or shutil.which("docker")
    if not executable:
        _fail("environment", "docker_unavailable")
    return executable


def _inspect_image(executable: str, contract: dict[str, Any]) -> str:
    profile = contract["containment_profile"]
    rows = _docker_json(executable, "image", "inspect", profile["image_reference"])
    if len(rows) != 1 or rows[0].get("Id") != profile["image_id"]:
        _fail("environment", "image_identity_mismatch")
    return str(rows[0]["Id"])


def _inspect_container(executable: str, container_id: str) -> dict[str, Any]:
    rows = _docker_json(executable, "container", "inspect", container_id)
    if len(rows) != 1:
        _fail("docker", "container_inspect_shape")
    return rows[0]


def _network_matches(
    row: dict[str, Any],
    *,
    network_id: str,
    network_name: str,
    nonce: str,
    contract: dict[str, Any],
) -> bool:
    profile = contract["containment_profile"]
    try:
        labels = row["Labels"]
        return bool(
            row["Id"] == network_id
            and row["Name"] == network_name
            and row["Internal"] is True
            and row["Driver"] == "bridge"
            and labels[profile["harness_label_key"]]
            == profile["harness_label_value"]
            and labels[profile["nonce_label_key"]] == nonce
        )
    except (KeyError, TypeError):
        return False


def _container_matches(
    row: dict[str, Any],
    *,
    container_id: str,
    container_name: str,
    network_name: str,
    network_id: str,
    nonce: str,
    contract: dict[str, Any],
    kind: str,
    forbidden_values: tuple[str, ...],
) -> bool:
    profile = contract["containment_profile"]
    try:
        config = row["Config"]
        host = row["HostConfig"]
        labels = config["Labels"]
        endpoint = row["NetworkSettings"]["Networks"][network_name]
        common = bool(
            row["Id"] == container_id
            and row["Name"] == "/" + container_name
            and row["Image"] == profile["image_id"]
            and config["Image"] == profile["image_reference"]
            and labels[profile["harness_label_key"]]
            == profile["harness_label_value"]
            and labels[profile["nonce_label_key"]] == nonce
            and endpoint["NetworkID"] == network_id
            and not host.get("PortBindings")
            and not host.get("Binds")
            and host["LogConfig"]["Type"] == "none"
            and host["RestartPolicy"]["Name"] == "no"
            and config["OpenStdin"] is True
        )
        serialized = json.dumps(
            {"Config": config, "HostConfig": host}, sort_keys=True
        )
        if any(secret and secret in serialized for secret in forbidden_values):
            return False
        if kind == "server":
            tmpfs = host["Tmpfs"][profile["server_tmpfs_destination"]]
            return bool(
                common
                and host["Memory"] == profile["server_memory_bytes"]
                and host["NanoCpus"] == profile["server_nano_cpus"]
                and host["PidsLimit"] == profile["server_pids_limit"]
                and set(tmpfs.split(","))
                == set(profile["server_tmpfs_options"].split(","))
            )
        tmpfs = host["Tmpfs"][profile["sidecar_tmpfs_destination"]]
        return bool(
            common
            and labels["emr4.action"] == kind
            and host["ReadonlyRootfs"] is True
            and host["Memory"] == profile["sidecar_memory_bytes"]
            and host["NanoCpus"] == profile["sidecar_nano_cpus"]
            and host["PidsLimit"] == profile["sidecar_pids_limit"]
            and host["CapDrop"] == ["ALL"]
            and "no-new-privileges" in host["SecurityOpt"]
            and set(tmpfs.split(","))
            == set(profile["sidecar_tmpfs_options"].split(","))
        )
    except (KeyError, TypeError, AttributeError):
        return False


def _create_network(
    executable: str, contract: dict[str, Any], nonce: str
) -> tuple[str, str]:
    profile = contract["containment_profile"]
    name = profile["network_name_prefix"] + secrets.token_hex(8)
    completed = _docker(
        executable,
        "network",
        "create",
        "--internal",
        "--driver",
        "bridge",
        "--label",
        f"{profile['harness_label_key']}={profile['harness_label_value']}",
        "--label",
        f"{profile['nonce_label_key']}={nonce}",
        name,
    )
    network_id = completed.stdout.strip()
    if CONTAINER_ID.fullmatch(network_id) is None:
        _fail("environment", "network_id_invalid")
    rows = _docker_json(executable, "network", "inspect", network_id)
    if len(rows) != 1 or not _network_matches(
        rows[0],
        network_id=network_id,
        network_name=name,
        nonce=nonce,
        contract=contract,
    ):
        _fail("environment", "network_profile_mismatch")
    return network_id, name


def _create_server(
    executable: str,
    contract: dict[str, Any],
    *,
    nonce: str,
    network_id: str,
    network_name: str,
    forbidden_values: tuple[str, ...],
) -> tuple[str, str]:
    profile = contract["containment_profile"]
    name = profile["server_name_prefix"] + secrets.token_hex(8)
    completed = _docker(
        executable,
        "create",
        "--pull",
        "never",
        "--interactive",
        "--name",
        name,
        "--label",
        f"{profile['harness_label_key']}={profile['harness_label_value']}",
        "--label",
        f"{profile['nonce_label_key']}={nonce}",
        "--network",
        network_id,
        "--network-alias",
        profile["server_alias"],
        "--log-driver",
        "none",
        "--tmpfs",
        f"{profile['server_tmpfs_destination']}:{profile['server_tmpfs_options']}",
        "--memory",
        str(profile["server_memory_bytes"]),
        "--cpus",
        "1",
        "--pids-limit",
        str(profile["server_pids_limit"]),
        "--restart",
        "no",
        "--security-opt",
        "no-new-privileges",
        "--entrypoint",
        "sh",
        profile["image_reference"],
        "-c",
        _server_wrapper(contract),
    )
    container_id = completed.stdout.strip()
    if CONTAINER_ID.fullmatch(container_id) is None:
        _fail("environment", "server_id_invalid")
    row = _inspect_container(executable, container_id)
    if not _container_matches(
        row,
        container_id=container_id,
        container_name=name,
        network_name=network_name,
        network_id=network_id,
        nonce=nonce,
        contract=contract,
        kind="server",
        forbidden_values=forbidden_values,
    ):
        _fail("environment", "server_profile_mismatch")
    return container_id, name


def _create_sidecar(
    executable: str,
    contract: dict[str, Any],
    *,
    nonce: str,
    network_id: str,
    network_name: str,
    action: str,
    wrapper: str,
    arguments: list[str],
    forbidden_values: tuple[str, ...],
) -> tuple[str, str]:
    profile = contract["containment_profile"]
    if action not in contract["action_classes"]:
        _fail("sidecar", "action_not_allowlisted")
    name = profile["sidecar_name_prefix"] + secrets.token_hex(8)
    completed = _docker(
        executable,
        "create",
        "--pull",
        "never",
        "--interactive",
        "--name",
        name,
        "--label",
        f"{profile['harness_label_key']}={profile['harness_label_value']}",
        "--label",
        f"{profile['nonce_label_key']}={nonce}",
        "--label",
        f"emr4.action={action}",
        "--network",
        network_id,
        "--log-driver",
        "none",
        "--read-only",
        "--tmpfs",
        f"{profile['sidecar_tmpfs_destination']}:{profile['sidecar_tmpfs_options']}",
        "--memory",
        str(profile["sidecar_memory_bytes"]),
        "--cpus",
        "0.25",
        "--pids-limit",
        str(profile["sidecar_pids_limit"]),
        "--restart",
        "no",
        "--security-opt",
        "no-new-privileges",
        "--cap-drop",
        "ALL",
        "--entrypoint",
        "sh",
        profile["image_reference"],
        "-c",
        wrapper,
        "sh",
        *arguments,
    )
    container_id = completed.stdout.strip()
    if CONTAINER_ID.fullmatch(container_id) is None:
        _fail("sidecar", "container_id_invalid")
    row = _inspect_container(executable, container_id)
    if not _container_matches(
        row,
        container_id=container_id,
        container_name=name,
        network_name=network_name,
        network_id=network_id,
        nonce=nonce,
        contract=contract,
        kind=action,
        forbidden_values=forbidden_values,
    ):
        _fail("sidecar", "container_profile_mismatch")
    return container_id, name


def _start_attached(
    executable: str, container_id: str, credential_lines: tuple[str, ...]
) -> subprocess.Popen[bytes]:
    attachment = subprocess.Popen(
        [
            executable,
            "start",
            "--attach",
            "--interactive",
            "--sig-proxy=false",
            container_id,
        ],
        cwd=ROOT,
        stdin=subprocess.PIPE,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        shell=False,
    )
    if attachment.stdin is None:
        _fail("credential", "attachment_stdin_missing")
    payload = "".join(f"{line}\n" for line in credential_lines).encode("ascii")
    attachment.stdin.write(payload)
    attachment.stdin.flush()
    attachment.stdin.close()
    return attachment


def _stop_attachment(attachment: subprocess.Popen[bytes] | None) -> bool:
    if attachment is None:
        return True
    if attachment.poll() is None:
        attachment.terminate()
        try:
            attachment.wait(timeout=5)
        except subprocess.TimeoutExpired:
            attachment.kill()
            attachment.wait(timeout=5)
    return attachment.poll() is not None


def _wait_closed(
    executable: str, container_id: str, timeout: int
) -> dict[str, Any]:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        row = _inspect_container(executable, container_id)
        if row.get("State", {}).get("Running") is False:
            return row
        time.sleep(0.05)
    _fail("outcome", "container_state_timeout")


def _evidence_state(closed: dict[str, Any]) -> dict[str, Any]:
    return {
        "stopped": closed["stopped"],
        "exit_code": closed["exit_code"],
        "oom_killed": closed["oom_killed"],
        "state_error_empty": closed["state_error_empty"],
        "restart_count": closed["restart_count"],
    }


def _remove_container(
    executable: str,
    contract: dict[str, Any],
    *,
    container_id: str,
    container_name: str,
    network_id: str,
    network_name: str,
    nonce: str,
    kind: str,
    forbidden_values: tuple[str, ...],
) -> bool:
    inspect = _docker(
        executable, "container", "inspect", container_id, check=False
    )
    if inspect.returncode != 0:
        return True
    row = _inspect_container(executable, container_id)
    if not _container_matches(
        row,
        container_id=container_id,
        container_name=container_name,
        network_name=network_name,
        network_id=network_id,
        nonce=nonce,
        contract=contract,
        kind=kind,
        forbidden_values=forbidden_values,
    ):
        return False
    _docker(executable, "rm", "--force", container_id)
    return (
        _docker(executable, "container", "inspect", container_id, check=False).returncode
        != 0
    )


def _run_sidecar(
    executable: str,
    contract: dict[str, Any],
    *,
    nonce: str,
    network_id: str,
    network_name: str,
    action: str,
    wrapper: str,
    arguments: list[str],
    credentials: tuple[str, ...],
    expected_exit: int,
    registry: dict[str, tuple[str, str]],
    forbidden_values: tuple[str, ...],
    timeout_seconds: int | None = None,
) -> dict[str, Any]:
    container_id, name = _create_sidecar(
        executable,
        contract,
        nonce=nonce,
        network_id=network_id,
        network_name=network_name,
        action=action,
        wrapper=wrapper,
        arguments=arguments,
        forbidden_values=forbidden_values,
    )
    registry[container_id] = (name, action)
    attachment: subprocess.Popen[bytes] | None = None
    try:
        attachment = _start_attached(executable, container_id, credentials)
        row = _wait_closed(
            executable,
            container_id,
            timeout_seconds
            or (
                contract["containment_profile"]["action_timeout_seconds"]
                + contract["containment_profile"]["observer_timeout_seconds"]
            ),
        )
        identity = _container_matches(
            row,
            container_id=container_id,
            container_name=name,
            network_name=network_name,
            network_id=network_id,
            nonce=nonce,
            contract=contract,
            kind=action,
            forbidden_values=forbidden_values,
        )
        closed = _closed_state(row, identity_match=identity)
    finally:
        if not _stop_attachment(attachment):
            _fail("cleanup", "attachment_absence_unverified")
    if closed != {
        "identity_match": True,
        "stopped": True,
        "exit_code": expected_exit,
        "oom_killed": False,
        "state_error_empty": True,
        "restart_count": 0,
    }:
        _fail(action, "terminal_state_mismatch")
    if not _remove_container(
        executable,
        contract,
        container_id=container_id,
        container_name=name,
        network_id=network_id,
        network_name=network_name,
        nonce=nonce,
        kind=action,
        forbidden_values=forbidden_values,
    ):
        _fail("cleanup", "sidecar_absence_unverified")
    registry.pop(container_id, None)
    return _evidence_state(closed)


def _action_arguments(
    contract: dict[str, Any],
    *,
    user: str,
    sql: str,
    application_name: str,
    mode: str = "normal",
) -> list[str]:
    if APP_ID.fullmatch(application_name) is None or mode not in {"normal", "loss"}:
        _fail("program", "action_argument_invalid")
    return [
        contract["containment_profile"]["server_alias"],
        user,
        contract["server_profile"]["postgres_database"],
        sql,
        application_name,
        mode,
    ]


def _remove_network(
    executable: str,
    contract: dict[str, Any],
    *,
    network_id: str,
    network_name: str,
    nonce: str,
) -> bool:
    inspect = _docker(executable, "network", "inspect", network_id, check=False)
    if inspect.returncode != 0:
        return True
    rows = _docker_json(executable, "network", "inspect", network_id)
    if len(rows) != 1 or not _network_matches(
        rows[0],
        network_id=network_id,
        network_name=network_name,
        nonce=nonce,
        contract=contract,
    ):
        return False
    _docker(executable, "network", "rm", network_id)
    return _docker(executable, "network", "inspect", network_id, check=False).returncode != 0


def _matching_owned_resources(
    executable: str, contract: dict[str, Any], nonce: str
) -> int:
    key = contract["containment_profile"]["nonce_label_key"]
    label = f"label={key}={nonce}"
    containers = _docker(
        executable, "container", "ls", "--all", "--quiet", "--filter", label
    ).stdout.splitlines()
    networks = _docker(
        executable, "network", "ls", "--quiet", "--filter", label
    ).stdout.splitlines()
    return len([row for row in containers + networks if row.strip()])


def _scenario(identifier: str, observed: str | int | bool) -> dict[str, Any]:
    return {"id": identifier, "status": "passed", "observed": observed}


def _failure_evidence(
    error: RehearsalFailure,
    lifecycle: list[str],
    cleanup: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": (
            "emr4.check-in-relay-free-rollback-unknown-response-rehearsal-"
            "failure.v1"
        ),
        "result": "failed_closed",
        "stage": error.stage,
        "code": error.code,
        "evidence_label": EVIDENCE_LABEL,
        "plan_source": PLAN_SOURCE,
        "lifecycle": lifecycle,
        "success_released": False,
        "retry_count": 0,
        "cleanup": cleanup,
    }


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_bytes(_json_bytes(value))


def run_rehearsal() -> tuple[dict[str, Any], dict[str, Any] | None]:
    if EVIDENCE_PATH.exists() or ATTESTATION_PATH.exists() or FAILURE_PATH.exists():
        _fail("execution", "terminal_artifact_already_exists")
    static = static_check()
    contract = validate_contract(_load_json(CONTRACT_PATH))
    physical_role = "emr4_checkin_rfr_" + secrets.token_hex(8)
    application_names = {
        action: "emr4_checkin_rfr_" + secrets.token_hex(8)
        for action in contract["action_classes"]
    }
    if any(APP_ID.fullmatch(value) is None for value in application_names.values()):
        _fail("program", "application_identity_invalid")
    manifest = build_manifest(contract, physical_role)
    validate_manifest(manifest, physical_role=physical_role, canonical=manifest)
    manifest_mutations = hostile_manifest_mutations_rejected(
        manifest,
        physical_role,
        contract["hostile_thresholds"]["manifest_and_evidence_state"],
    )
    canonical_packet = _canonical_packet(manifest)
    classifier_mutations = hostile_classifier_packets_rejected(
        canonical_packet,
        manifest["commands"]["ambiguous_response"]["request_sha256"],
        contract["hostile_thresholds"]["classifier"],
    )
    state_mutations = hostile_states_rejected(
        contract["hostile_thresholds"]["manifest_and_evidence_state"]
    )
    executable = _docker_executable(contract)
    _inspect_image(executable, contract)
    nonce = secrets.token_hex(16)
    admin_password = secrets.token_hex(32)
    runtime_password = secrets.token_hex(32)
    forbidden_values = (admin_password, runtime_password, nonce)
    network_id: str | None = None
    network_name = ""
    server_id: str | None = None
    server_name = ""
    server_attachment: subprocess.Popen[bytes] | None = None
    registry: dict[str, tuple[str, str]] = {}
    role_created = False
    role_absent = True
    lifecycle = ["static_admission_passed"]
    cleanup: dict[str, Any] = {
        "role_absent_before_teardown": False,
        "attachments_absent": False,
        "sidecars_absent": False,
        "server_absent": False,
        "network_absent": False,
        "matching_owned_resources": -1,
        "status": "not_started",
    }
    error: RehearsalFailure | None = None
    result: dict[str, Any] | None = None
    attestation: dict[str, Any] | None = None
    started = time.monotonic()
    rollback_state: dict[str, Any] | None = None
    rollback_readback_state: dict[str, Any] | None = None
    observer_state: dict[str, Any] | None = None
    caller_state: dict[str, Any] | None = None
    readback_state: dict[str, Any] | None = None
    role_cleanup_state: dict[str, Any] | None = None
    sidecar_count = 0
    try:
        network_id, network_name = _create_network(executable, contract, nonce)
        lifecycle.append("captured_internal_network_verified")
        server_id, server_name = _create_server(
            executable,
            contract,
            nonce=nonce,
            network_id=network_id,
            network_name=network_name,
            forbidden_values=forbidden_values,
        )
        lifecycle.append("captured_server_created_without_secret_configuration")
        server_attachment = _start_attached(
            executable, server_id, (admin_password,)
        )
        lifecycle.append("server_credential_delivered_by_attached_stdin")
        readiness_state = _run_sidecar(
            executable,
            contract,
            nonce=nonce,
            network_id=network_id,
            network_name=network_name,
            action="readiness",
            wrapper=READINESS_WRAPPER,
            arguments=[
                contract["containment_profile"]["server_alias"],
                contract["server_profile"]["postgres_user"],
                contract["server_profile"]["postgres_database"],
            ],
            credentials=(admin_password,),
            expected_exit=0,
            registry=registry,
            forbidden_values=forbidden_values,
            timeout_seconds=contract["containment_profile"][
                "startup_timeout_seconds"
            ]
            + 5,
        )
        sidecar_count += 1
        if not _stop_attachment(server_attachment):
            _fail("cleanup", "server_attachment_absence_unverified")
        server_attachment = None
        server_row = _inspect_container(executable, server_id)
        if (
            server_row.get("State", {}).get("Running") is not True
            or not _container_matches(
                server_row,
                container_id=server_id,
                container_name=server_name,
                network_name=network_name,
                network_id=network_id,
                nonce=nonce,
                contract=contract,
                kind="server",
                forbidden_values=forbidden_values,
            )
        ):
            _fail("environment", "server_not_ready_or_identity_mismatch")
        lifecycle.append("relay_free_server_readiness_verified")
        role_created = True
        role_absent = False
        setup_state = _run_sidecar(
            executable,
            contract,
            nonce=nonce,
            network_id=network_id,
            network_name=network_name,
            action="setup_and_catalogue",
            wrapper=SETUP_WRAPPER,
            arguments=[
                contract["containment_profile"]["server_alias"],
                contract["server_profile"]["postgres_user"],
                contract["server_profile"]["postgres_database"],
                _setup_sql(contract, physical_role),
                application_names["setup_and_catalogue"],
            ],
            credentials=(admin_password, runtime_password),
            expected_exit=0,
            registry=registry,
            forbidden_values=forbidden_values,
        )
        sidecar_count += 1
        lifecycle.append("restricted_role_forced_rls_and_catalogue_verified")
        rollback_state = _run_sidecar(
            executable,
            contract,
            nonce=nonce,
            network_id=network_id,
            network_name=network_name,
            action="explicit_rollback",
            wrapper=ACTION_WRAPPER,
            arguments=_action_arguments(
                contract,
                user=physical_role,
                sql=_rollback_sql(contract, manifest),
                application_name=application_names["explicit_rollback"],
            ),
            credentials=(runtime_password,),
            expected_exit=0,
            registry=registry,
            forbidden_values=forbidden_values,
        )
        sidecar_count += 1
        lifecycle.append("explicit_rollback_staged_three_members")
        rollback_readback_state = _run_sidecar(
            executable,
            contract,
            nonce=nonce,
            network_id=network_id,
            network_name=network_name,
            action="rollback_readback",
            wrapper=ACTION_WRAPPER,
            arguments=_action_arguments(
                contract,
                user=physical_role,
                sql=_rollback_readback_sql(contract, manifest),
                application_name=application_names["rollback_readback"],
            ),
            credentials=(runtime_password,),
            expected_exit=0,
            registry=registry,
            forbidden_values=forbidden_values,
        )
        sidecar_count += 1
        lifecycle.append("fresh_restricted_rollback_zero_readback_verified")
        caller_id, caller_name = _create_sidecar(
            executable,
            contract,
            nonce=nonce,
            network_id=network_id,
            network_name=network_name,
            action="ambiguous_caller",
            wrapper=ACTION_WRAPPER,
            arguments=_action_arguments(
                contract,
                user=physical_role,
                sql=_ambiguous_sql(contract, manifest),
                application_name=application_names["ambiguous_caller"],
                mode="loss",
            ),
            forbidden_values=forbidden_values,
        )
        registry[caller_id] = (caller_name, "ambiguous_caller")
        caller_attachment = _start_attached(
            executable, caller_id, (runtime_password,)
        )
        sidecar_count += 1
        lifecycle.append("one_shot_ambiguous_caller_started_without_host_relay")
        try:
            observer_state = _run_sidecar(
                executable,
                contract,
                nonce=nonce,
                network_id=network_id,
                network_name=network_name,
                action="observer_terminator",
                wrapper=ACTION_WRAPPER,
                arguments=_action_arguments(
                    contract,
                    user=contract["server_profile"]["postgres_user"],
                    sql=_observer_sql(
                        contract,
                        physical_role,
                        application_names["ambiguous_caller"],
                    ),
                    application_name=application_names["observer_terminator"],
                ),
                credentials=(admin_password,),
                expected_exit=0,
                registry=registry,
                forbidden_values=forbidden_values,
            )
            sidecar_count += 1
            lifecycle.append("exact_post_commit_backend_observed_and_terminated")
            caller_row = _wait_closed(
                executable,
                caller_id,
                contract["containment_profile"]["action_timeout_seconds"],
            )
            caller_identity = _container_matches(
                caller_row,
                container_id=caller_id,
                container_name=caller_name,
                network_name=network_name,
                network_id=network_id,
                nonce=nonce,
                contract=contract,
                kind="ambiguous_caller",
                forbidden_values=forbidden_values,
            )
            caller_closed = _closed_state(
                caller_row, identity_match=caller_identity
            )
        finally:
            if not _stop_attachment(caller_attachment):
                _fail("cleanup", "caller_attachment_absence_unverified")
        classification = classify_caller_state(
            caller_closed, observer_passed=observer_state is not None
        )
        if classification != "connection_lost_without_complete_terminal_response":
            _fail("ambiguous_caller", "unknown_outcome_not_admitted")
        caller_state = _evidence_state(caller_closed)
        if not _remove_container(
            executable,
            contract,
            container_id=caller_id,
            container_name=caller_name,
            network_id=network_id,
            network_name=network_name,
            nonce=nonce,
            kind="ambiguous_caller",
            forbidden_values=forbidden_values,
        ):
            _fail("cleanup", "caller_absence_unverified")
        registry.pop(caller_id, None)
        lifecycle.append("caller_exit_42_released_no_success_and_no_retry")
        readback_state = _run_sidecar(
            executable,
            contract,
            nonce=nonce,
            network_id=network_id,
            network_name=network_name,
            action="authoritative_readback",
            wrapper=ACTION_WRAPPER,
            arguments=_action_arguments(
                contract,
                user=physical_role,
                sql=_authoritative_readback_sql(contract, manifest),
                application_name=application_names["authoritative_readback"],
            ),
            credentials=(runtime_password,),
            expected_exit=0,
            registry=registry,
            forbidden_values=forbidden_values,
        )
        sidecar_count += 1
        lifecycle.append("fresh_restricted_exactly_once_readback_verified")
        role_cleanup_state = _run_sidecar(
            executable,
            contract,
            nonce=nonce,
            network_id=network_id,
            network_name=network_name,
            action="role_cleanup",
            wrapper=ACTION_WRAPPER,
            arguments=_action_arguments(
                contract,
                user=contract["server_profile"]["postgres_user"],
                sql=_role_cleanup_sql(contract, physical_role),
                application_name=application_names["role_cleanup"],
            ),
            credentials=(admin_password,),
            expected_exit=0,
            registry=registry,
            forbidden_values=forbidden_values,
        )
        sidecar_count += 1
        role_created = False
        role_absent = True
        lifecycle.append("physical_role_absent_before_server_teardown")
        attestation = {
            "schema_version": (
                "emr4.check-in-relay-free-rollback-unknown-response-"
                "transaction-attestation.v1"
            ),
            "evidence_reference": (
                "evidence-ref:authored-synthetic/check-in-relay-free-rollback-"
                "unknown-response-transaction-attestation"
            ),
            "source_head": static["source_head"],
            "plan_source": PLAN_SOURCE,
            "contract_sha256": static["contract_sha256"],
            "manifest_sha256": _sha256(_json_bytes(manifest)),
            "role_catalogue": {
                "login": True,
                "superuser": False,
                "create_database": False,
                "create_role": False,
                "inherit": False,
                "replication": False,
                "bypass_rls": False,
                "memberships": 0,
                "owned_objects": 0,
                "product_privileges": 0,
            },
            "relation_catalogue": {
                "relation_count": 3,
                "admin_owned_count": 3,
                "rls_enabled_count": 3,
                "rls_forced_count": 3,
                "policy_count": 3,
                "constraint_count": 21,
                "grants_exact": True,
            },
            "explicit_rollback": {
                "action_state": rollback_state,
                "staged_counts": {"effect": 1, "receipt": 1, "audit": 1},
                "readback_state": rollback_readback_state,
                "readback_counts": {"effect": 0, "receipt": 0, "audit": 0},
                "classification": "rolled_back_zero_effect",
            },
            "ambiguous_response": {
                "observer_state": observer_state,
                "exact_backend_observed": True,
                "exact_backend_terminated": True,
                "caller_state": caller_state,
                "classification": (
                    "connection_lost_without_complete_terminal_response"
                ),
                "complete_terminal_response": False,
                "success_released": False,
                "retry_count": 0,
            },
            "authoritative_readback": {
                "state": readback_state,
                "counts": {"effect": 1, "receipt": 1, "audit": 1},
                "classification": "committed_exactly_once",
                "other_practice_visible_count": 0,
                "duplicate_effect_count": 0,
            },
            "hostile_classifier": {
                "attempted": classifier_mutations[0],
                "rejected": classifier_mutations[1],
                "escapes": 0,
            },
            "ordinary_admission_release_count": 0,
            "product_record_count": 0,
            "redaction": {
                "forbidden_fields": 0,
                "forbidden_values": 0,
                "status": "passed",
            },
        }
        _assert_redacted(attestation, forbidden_values=forbidden_values)
        errors = list(
            Draft202012Validator(_load_json(ATTESTATION_SCHEMA_PATH)).iter_errors(
                attestation
            )
        )
        if errors:
            _fail("evidence", "attestation_schema_invalid")
        lifecycle.append("closed_transaction_attestation_validated")
        result = {
            "schema_version": (
                "emr4.check-in-relay-free-rollback-unknown-response-rehearsal-"
                "evidence.v1"
            ),
            "result": PASS_RESULT,
            "evidence_label": EVIDENCE_LABEL,
            "source_head": static["source_head"],
            "plan_source": PLAN_SOURCE,
            "accepted_relay_free_transport_source": RELAY_FREE_SOURCE,
            "accepted_runtime_role_source": RUNTIME_ROLE_SOURCE,
            "protected_source": PROTECTED_SOURCE,
            "contract_sha256": static["contract_sha256"],
            "source_binding_count": static["source_binding_count"],
            "manifest_sha256": _sha256(_json_bytes(manifest)),
            "attestation_sha256": _sha256(_json_bytes(attestation)),
            "hostile_mutations": {
                "contract_attempted": static["contract_mutations"]["attempted"],
                "contract_rejected": static["contract_mutations"]["rejected"],
                "state_attempted": state_mutations[0],
                "state_rejected": state_mutations[1],
                "classifier_attempted": classifier_mutations[0],
                "classifier_rejected": classifier_mutations[1],
                "escapes": 0,
            },
            "scenarios": [
                _scenario("RFR-S01", static["source_binding_count"]),
                _scenario("RFR-S02", manifest_mutations[1]),
                _scenario("RFR-S03", "internal_network_no_host_transport"),
                _scenario("RFR-S04", setup_state["exit_code"]),
                _scenario("RFR-S05", "rolled_back_zero_effect"),
                _scenario("RFR-S06", "post_commit_hold_reached"),
                _scenario("RFR-S07", observer_state["exit_code"]),
                _scenario("RFR-S08", caller_state["exit_code"]),
                _scenario("RFR-S09", "committed_exactly_once"),
                _scenario("RFR-S10", classifier_mutations[1]),
                _scenario("RFR-S11", 0),
                _scenario("RFR-S12", role_cleanup_state["exit_code"]),
            ],
            "containment": {
                "image_reference": contract["containment_profile"][
                    "image_reference"
                ],
                "image_id_sha256": contract["containment_profile"]["image_id"],
                "pulls": 0,
                "internal_network": True,
                "published_ports": False,
                "bind_mounts": 0,
                "volumes": 0,
                "log_driver": "none",
                "server_count": 1,
                "sidecar_count": sidecar_count,
            },
            "transport": {
                "host_listener": False,
                "forwarder": False,
                "socket_copy_relay": False,
                "docker_exec_byte_bridge": False,
                "multiprocessing_process_or_queue": False,
                "input_channel": "post_inspection_attached_stdin",
                "outcome_channel": "exact_terminal_oci_state",
                "attachment_is_outcome_evidence": False,
                "complete_terminal_response": False,
                "success_released": False,
                "automatic_retries": 0,
            },
            "cleanup": cleanup,
            "elapsed_seconds": 0.0,
            "closed_boundaries": copy.deepcopy(contract["closed_boundaries"]),
        }
    except RehearsalFailure as caught:
        error = caught
    finally:
        if not _stop_attachment(server_attachment):
            error = RehearsalFailure("cleanup", "server_attachment_absence_unverified")
        if role_created and network_id and server_id:
            try:
                _run_sidecar(
                    executable,
                    contract,
                    nonce=nonce,
                    network_id=network_id,
                    network_name=network_name,
                    action="role_cleanup",
                    wrapper=ACTION_WRAPPER,
                    arguments=_action_arguments(
                        contract,
                        user=contract["server_profile"]["postgres_user"],
                        sql=_role_cleanup_sql(contract, physical_role),
                        application_name=application_names["role_cleanup"],
                    ),
                    credentials=(admin_password,),
                    expected_exit=0,
                    registry=registry,
                    forbidden_values=forbidden_values,
                )
                role_absent = True
                role_created = False
                lifecycle.append("failure_path_physical_role_absent")
            except RehearsalFailure:
                role_absent = False
                lifecycle.append("failure_path_role_cleanup_unverified")
        sidecars_absent = True
        if network_id:
            for captured_id, (captured_name, kind) in list(registry.items()):
                if not _remove_container(
                    executable,
                    contract,
                    container_id=captured_id,
                    container_name=captured_name,
                    network_id=network_id,
                    network_name=network_name,
                    nonce=nonce,
                    kind=kind,
                    forbidden_values=forbidden_values,
                ):
                    sidecars_absent = False
                else:
                    registry.pop(captured_id, None)
        if registry:
            sidecars_absent = False
        server_absent = server_id is None
        if server_id is not None and network_id is not None:
            server_absent = _remove_container(
                executable,
                contract,
                container_id=server_id,
                container_name=server_name,
                network_id=network_id,
                network_name=network_name,
                nonce=nonce,
                kind="server",
                forbidden_values=forbidden_values,
            )
        network_absent = network_id is None
        if network_id is not None:
            network_absent = _remove_network(
                executable,
                contract,
                network_id=network_id,
                network_name=network_name,
                nonce=nonce,
            )
        matching = _matching_owned_resources(executable, contract, nonce)
        cleanup = {
            "role_absent_before_teardown": role_absent,
            "attachments_absent": True,
            "sidecars_absent": sidecars_absent,
            "server_absent": server_absent,
            "network_absent": network_absent,
            "matching_owned_resources": matching,
            "status": (
                "cleanup_verified"
                if role_absent
                and sidecars_absent
                and server_absent
                and network_absent
                and matching == 0
                else "cleanup_incomplete"
            ),
        }
        if cleanup["status"] != "cleanup_verified":
            error = RehearsalFailure("cleanup", "exact_cleanup_unverified")
    elapsed = round(time.monotonic() - started, 6)
    if error is not None or result is None or attestation is None:
        failure = _failure_evidence(
            error or RehearsalFailure("execution", "result_missing"),
            lifecycle,
            cleanup,
        )
        _assert_redacted(failure, forbidden_values=forbidden_values)
        _write_json(FAILURE_PATH, failure)
        return failure, None
    result["cleanup"] = cleanup
    result["elapsed_seconds"] = elapsed
    _assert_redacted(result, forbidden_values=forbidden_values)
    evidence_errors = list(
        Draft202012Validator(_load_json(EVIDENCE_SCHEMA_PATH)).iter_errors(result)
    )
    if evidence_errors:
        failure = _failure_evidence(
            RehearsalFailure("evidence", "parent_schema_invalid"),
            lifecycle,
            cleanup,
        )
        _write_json(FAILURE_PATH, failure)
        return failure, None
    _write_json(ATTESTATION_PATH, attestation)
    _write_json(EVIDENCE_PATH, result)
    return result, attestation


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--execute", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.check:
            print(json.dumps(static_check(), indent=2))
            return 0
        evidence, _ = run_rehearsal()
        print(
            json.dumps(
                {
                    "result": evidence.get("result"),
                    "cleanup": evidence.get("cleanup", {}).get("status"),
                },
                indent=2,
            )
        )
        return 0 if evidence.get("result") == PASS_RESULT else 1
    except RehearsalFailure as caught:
        print(json.dumps({"result": "failed_closed", "stage": caught.stage, "code": caught.code}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
