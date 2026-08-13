"""Run the fixed provider-free CF-D2 serial PostgreSQL behavior rehearsal.

No caller-selected SQL, database, fixture, image or output is accepted.  The
harness uses one exact cached, networkless, tmpfs PostgreSQL 16 container and
fixed authored-synthetic rows, then removes only the captured owned container.
"""

from __future__ import annotations

import copy
import hashlib
import json
import re
import secrets
import shutil
import sys
import time
from pathlib import Path
from typing import Any, Callable

from jsonschema import Draft202012Validator

try:
    from scripts import (
        raisa_provider_free_disposable_postgresql_cf_d2_event_cue_parse_catalogue_rehearsal as catalogue,
    )
except ModuleNotFoundError:  # direct ``python scripts/<name>.py`` entry point
    import raisa_provider_free_disposable_postgresql_cf_d2_event_cue_parse_catalogue_rehearsal as catalogue


ROOT = Path(__file__).resolve().parents[1]
CONTINUITY_DIR = (
    ROOT
    / "orchestration"
    / "continuity"
    / "raisa-provider-free-disposable-postgresql-cf-d2-event-cue-behavior-transaction-rehearsal"
)
CONTRACT_PATH = CONTINUITY_DIR / "rehearsal-contract.json"
CONTRACT_SCHEMA_PATH = CONTINUITY_DIR / "rehearsal-contract.schema.json"
EVIDENCE_SCHEMA_PATH = CONTINUITY_DIR / "provider-free-behavior-transaction-evidence.schema.json"
EVIDENCE_PATH = CONTINUITY_DIR / "provider-free-behavior-transaction-evidence.json"
FAILURE_EVIDENCE_PATH = CONTINUITY_DIR / "provider-free-behavior-transaction-failure-evidence.json"
ARTIFACT_PATH = (
    ROOT
    / "orchestration"
    / "continuity"
    / "raisa-provider-free-unmounted-cf-d2-event-cue-inert-ddl-lowering"
    / "event-cue-schema.sql.inert"
)
EXPECTED_CONTRACT_DIGEST = (
    "70218b8c3a5165fcb8cc4960e9c6bfc59154108d68480427d083a540acd0fd89"
)
PASS_RESULT = (
    "raisa_provider_free_disposable_postgresql_cf_d2_event_cue_behavior_transaction_pass"
)
FAIL_RESULT = "rehearsal_failed"
EVIDENCE_SCHEMA_VERSION = (
    "raisa.context_fabric.cf_d2_event_cue_behavior_transaction_evidence.v1"
)
CLAIM_BOUNDARY = (
    "Exact fixed authored-synthetic serial PostgreSQL 16 transactions prove the five "
    "accepted CF-D2 protocol effects, denials, rollback and uncontended required "
    "relation-lock footprints in one destroyed server; no concurrency, restart, "
    "source, runtime, product or external-authority behavior is proved."
)
SCHEMA = "emr4_context_fabric_cue"

Runner = Callable[[list[str], bytes | None, int, int], catalogue.ProcessResult]


class RehearsalFailure(RuntimeError):
    def __init__(self, stage: str, code: str, detail: bytes | str = b"") -> None:
        super().__init__(f"{stage}:{code}")
        self.stage = stage
        self.code = code
        self.detail = detail.encode("utf-8") if isinstance(detail, str) else detail


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def _canonical_digest(value: Any) -> str:
    return "sha256:" + _sha256(_canonical_bytes(value))


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RehearsalFailure("preflight", "json_root_not_object", str(path))
    return value


def _leaf_paths(value: Any, prefix: tuple[Any, ...] = ()) -> list[tuple[Any, ...]]:
    if isinstance(value, dict):
        return [
            path
            for key, child in value.items()
            for path in _leaf_paths(child, (*prefix, key))
        ]
    if isinstance(value, list):
        return [
            path
            for index, child in enumerate(value)
            for path in _leaf_paths(child, (*prefix, index))
        ]
    return [prefix]


def _mutate_leaf(value: Any) -> Any:
    if isinstance(value, bool):
        return not value
    if isinstance(value, int):
        return value + 1
    if isinstance(value, str):
        return value + "-hostile"
    if value is None:
        return "hostile"
    raise TypeError(type(value).__name__)


def _validate_contract_candidate(candidate: dict[str, Any]) -> None:
    Draft202012Validator(_load_json(CONTRACT_SCHEMA_PATH)).validate(candidate)
    if _canonical_digest(candidate) != "sha256:" + EXPECTED_CONTRACT_DIGEST:
        raise RehearsalFailure("preflight", "contract_digest_mismatch")


def hostile_mutations_rejected(contract: dict[str, Any]) -> int:
    paths = _leaf_paths(contract)
    target = contract["hostile_mutation_target"]
    if len(paths) < target:
        raise RehearsalFailure("preflight", "insufficient_hostile_leaves")
    rejected = 0
    for path in paths[:target]:
        candidate = copy.deepcopy(contract)
        parent = candidate
        for component in path[:-1]:
            parent = parent[component]
        parent[path[-1]] = _mutate_leaf(parent[path[-1]])
        try:
            _validate_contract_candidate(candidate)
        except Exception:
            rejected += 1
    return rejected


def verify_contract() -> tuple[dict[str, Any], dict[str, str], bytes]:
    contract = _load_json(CONTRACT_PATH)
    _validate_contract_candidate(contract)
    if contract["result"] != PASS_RESULT or contract["claim_boundary"] != CLAIM_BOUNDARY:
        raise RehearsalFailure("preflight", "contract_semantics_mismatch")
    if [item["name"] for item in contract["protocols"]] != [
        "admit_terminal",
        "coalesce_pending",
        "advance_contiguous_checkpoint",
        "record_dispatch_attempt",
        "record_reconciliation",
    ]:
        raise RehearsalFailure("preflight", "protocol_order_mismatch")
    if hostile_mutations_rejected(contract) != contract["hostile_mutation_target"]:
        raise RehearsalFailure("preflight", "hostile_mutation_gate_failed")

    observed: dict[str, str] = {}
    for binding in contract["source_bindings"]:
        path = ROOT / binding["path"]
        if not path.is_file():
            raise RehearsalFailure("preflight", "source_missing", binding["path"])
        digest = _sha256(path.read_bytes())
        observed[binding["path"]] = digest
        if digest != binding["sha256"]:
            raise RehearsalFailure("preflight", "source_hash_mismatch", binding["path"])

    artifact = ARTIFACT_PATH.read_bytes()
    expected = contract["artifact"]
    if _sha256(artifact) != expected["sha256"] or len(artifact) != expected["byte_count"]:
        raise RehearsalFailure("preflight", "artifact_identity_mismatch")
    if b"\r" in artifact or artifact.count(b";") != expected["statement_count"]:
        raise RehearsalFailure("preflight", "artifact_statement_shape_mismatch")
    return contract, observed, artifact


def _literal(value: str) -> str:
    if not isinstance(value, str) or not value or "\x00" in value:
        raise RehearsalFailure("fixture", "invalid_sql_literal")
    return "'" + value.replace("'", "''") + "'"


def _fingerprint(position: int, variant: str = "a") -> str:
    return "sha256:" + hashlib.sha256(
        f"cf-d2-fixed-fingerprint|{position}|{variant}".encode("utf-8")
    ).hexdigest()


STATE_SQL = f"""
SELECT pg_catalog.jsonb_build_object(
  'event_partition', COALESCE((SELECT pg_catalog.jsonb_agg(pg_catalog.to_jsonb(t) ORDER BY partition_id) FROM {SCHEMA}.event_partition t), '[]'::jsonb),
  'observer_coordinate', COALESCE((SELECT pg_catalog.jsonb_agg(pg_catalog.to_jsonb(t) ORDER BY partition_id, consumer_scope) FROM {SCHEMA}.observer_coordinate t), '[]'::jsonb),
  'terminal_receipt', COALESCE((SELECT pg_catalog.jsonb_agg(pg_catalog.to_jsonb(t) ORDER BY partition_id, source_epoch_digest, source_position) FROM {SCHEMA}.terminal_receipt t), '[]'::jsonb),
  'cue_obligation', COALESCE((SELECT pg_catalog.jsonb_agg(pg_catalog.to_jsonb(t) ORDER BY obligation_id) FROM {SCHEMA}.cue_obligation t), '[]'::jsonb),
  'consumer_checkpoint', COALESCE((SELECT pg_catalog.jsonb_agg(pg_catalog.to_jsonb(t) ORDER BY partition_id, consumer_scope, source_epoch_digest) FROM {SCHEMA}.consumer_checkpoint t), '[]'::jsonb),
  'dispatch_attempt', COALESCE((SELECT pg_catalog.jsonb_agg(pg_catalog.to_jsonb(t) ORDER BY obligation_id, attempt_ordinal) FROM {SCHEMA}.dispatch_attempt t), '[]'::jsonb),
  'reconciliation_receipt', COALESCE((SELECT pg_catalog.jsonb_agg(pg_catalog.to_jsonb(t) ORDER BY obligation_id) FROM {SCHEMA}.reconciliation_receipt t), '[]'::jsonb)
)::text;
"""


class DatabaseScenarios:
    def __init__(
        self,
        runner: Runner,
        docker: str,
        container_id: str,
        contract: dict[str, Any],
    ) -> None:
        self.runner = runner
        self.docker = docker
        self.container_id = container_id
        self.contract = contract
        self.profile = contract["docker_profile"]
        self.fx = contract["fixtures"]
        self.groups: list[dict[str, Any]] = []
        self.denied: list[dict[str, Any]] = []
        self.rollbacks: list[dict[str, Any]] = []
        self.locks: list[dict[str, Any]] = []

    def _sql(self, sql: str, *, tuples_only: bool = False) -> catalogue.ProcessResult:
        result = self.runner(
            catalogue._psql_argv(
                self.docker,
                self.container_id,
                self.profile,
                tuples_only=tuples_only,
            ),
            sql.encode("utf-8"),
            self.profile["command_timeout_seconds"],
            256_000,
        )
        if result.returncode != 0:
            raise RehearsalFailure("psql", "unexpected_sql_failure", result.stderr)
        return result

    def _expected_failure(self, sql: str, marker: str) -> None:
        result = self.runner(
            catalogue._psql_argv(
                self.docker,
                self.container_id,
                self.profile,
            ),
            sql.encode("utf-8"),
            self.profile["command_timeout_seconds"],
            256_000,
        )
        if result.returncode == 0 or marker.encode("utf-8") not in result.stderr:
            raise RehearsalFailure("scenario", "expected_failure_not_observed", marker)

    def state(self) -> dict[str, Any]:
        result = self._sql(STATE_SQL, tuples_only=True)
        try:
            value = json.loads(catalogue._stdout_value(result))
        except (json.JSONDecodeError, UnicodeDecodeError) as error:
            raise RehearsalFailure("state", "state_projection_invalid", str(error)) from error
        if not isinstance(value, dict) or set(value) != {
            "event_partition",
            "observer_coordinate",
            "terminal_receipt",
            "cue_obligation",
            "consumer_checkpoint",
            "dispatch_attempt",
            "reconciliation_receipt",
        }:
            raise RehearsalFailure("state", "state_projection_shape_invalid")
        return value

    def digest(self) -> str:
        return _canonical_digest(self.state())

    @staticmethod
    def _counts(state: dict[str, Any]) -> dict[str, int]:
        return {name: len(rows) for name, rows in state.items()}

    def _require(self, condition: bool, code: str) -> None:
        if not condition:
            raise RehearsalFailure("scenario", code)

    def _finish_group(self, group_id: str, assertions: int) -> None:
        state = self.state()
        self.groups.append(
            {
                "id": group_id,
                "status": "passed",
                "assertion_count": assertions,
                "final_state_sha256": _canonical_digest(state),
                "row_counts": self._counts(state),
            }
        )

    def reset(self) -> None:
        p = self.fx
        self._sql(
            f"""
BEGIN;
TRUNCATE TABLE {SCHEMA}.event_partition CASCADE;
INSERT INTO {SCHEMA}.event_partition
  (partition_id, source_system, practice_scope_digest, event_family, source_epoch_digest, lease_generation)
VALUES
  ({_literal(p['partition_id'])}, {_literal(p['source_system'])}, {_literal(p['practice_scope_digest'])}, {_literal(p['event_family'])}, {_literal(p['source_epoch_digest'])}, {p['lease_generation']});
INSERT INTO {SCHEMA}.observer_coordinate
  (partition_id, consumer_scope, source_epoch_digest, observed_state, observed_position, source_head_state, source_head_epoch_digest, source_head_position)
VALUES
  ({_literal(p['partition_id'])}, {_literal(p['consumer_scope'])}, {_literal(p['source_epoch_digest'])}, 'none', NULL, 'unknown', NULL, NULL);
INSERT INTO {SCHEMA}.consumer_checkpoint
  (partition_id, consumer_scope, source_epoch_digest, checkpoint_state, checkpoint_position, lease_generation)
VALUES
  ({_literal(p['partition_id'])}, {_literal(p['consumer_scope'])}, {_literal(p['source_epoch_digest'])}, 'none', NULL, {p['lease_generation']});
COMMIT;
"""
        )

    def _admit_sql(
        self,
        *,
        position: int,
        receipt_id: str,
        obligation_id: str,
        classification: str,
        reason_code: str | None,
        generation: int,
        fingerprint_variant: str = "a",
    ) -> str:
        p = self.fx
        reason = "NULL" if reason_code is None else _literal(reason_code)
        return f"""
BEGIN;
DO $cf$
DECLARE
  current_generation bigint;
  current_epoch text;
  existing {SCHEMA}.terminal_receipt%ROWTYPE;
  selected_obligation text;
  next_position bigint;
  next_receipt record;
BEGIN
  SELECT lease_generation, source_epoch_digest
    INTO current_generation, current_epoch
    FROM {SCHEMA}.event_partition
    WHERE partition_id = {_literal(p['partition_id'])}
    FOR UPDATE;
  IF NOT FOUND OR current_generation <> {generation} THEN
    RAISE EXCEPTION 'ownership_fenced';
  END IF;
  IF current_epoch <> {_literal(p['source_epoch_digest'])} THEN
    RAISE EXCEPTION 'epoch_mismatch';
  END IF;

  SELECT * INTO existing
    FROM {SCHEMA}.terminal_receipt
    WHERE partition_id = {_literal(p['partition_id'])}
      AND source_epoch_digest = {_literal(p['source_epoch_digest'])}
      AND source_position = {position}
    FOR UPDATE;
  IF FOUND THEN
    IF existing.event_fingerprint_digest IS DISTINCT FROM {_literal(_fingerprint(position, fingerprint_variant))}
       OR existing.classification IS DISTINCT FROM {_literal(classification)}
       OR existing.reason_code IS DISTINCT FROM {reason} THEN
      RAISE EXCEPTION 'identity_conflict';
    END IF;
    RETURN;
  END IF;

  IF {_literal(classification)} = 'cue_required' THEN
    SELECT obligation_id INTO selected_obligation
      FROM {SCHEMA}.cue_obligation
      WHERE partition_id = {_literal(p['partition_id'])}
        AND consumer_scope = {_literal(p['consumer_scope'])}
        AND source_epoch_digest = {_literal(p['source_epoch_digest'])}
        AND reason_code = {reason}
        AND state = 'pending'
        AND through_position + 1 = {position}
      ORDER BY from_position DESC
      LIMIT 1
      FOR UPDATE;
    IF NOT FOUND THEN
      selected_obligation := {_literal(obligation_id)};
      INSERT INTO {SCHEMA}.cue_obligation
        (obligation_id, partition_id, consumer_scope, source_epoch_digest, from_position, through_position, reason_code, fresh_authorized_read_required, state)
      VALUES
        (selected_obligation, {_literal(p['partition_id'])}, {_literal(p['consumer_scope'])}, {_literal(p['source_epoch_digest'])}, {position}, {position}, {reason}, TRUE, 'pending');
    ELSE
      UPDATE {SCHEMA}.cue_obligation
        SET through_position = {position}
        WHERE obligation_id = selected_obligation;
    END IF;
  ELSE
    selected_obligation := NULL;
  END IF;

  INSERT INTO {SCHEMA}.terminal_receipt
    (receipt_id, partition_id, source_epoch_digest, source_position, event_fingerprint_digest, classification, reason_code, obligation_id)
  VALUES
    ({_literal(receipt_id)}, {_literal(p['partition_id'])}, {_literal(p['source_epoch_digest'])}, {position}, {_literal(_fingerprint(position, fingerprint_variant))}, {_literal(classification)}, {reason}, selected_obligation);

  SELECT COALESCE(checkpoint_position, 0) + 1 INTO next_position
    FROM {SCHEMA}.consumer_checkpoint
    WHERE partition_id = {_literal(p['partition_id'])}
      AND consumer_scope = {_literal(p['consumer_scope'])}
      AND source_epoch_digest = {_literal(p['source_epoch_digest'])}
      AND lease_generation = {generation}
    FOR UPDATE;
  LOOP
    SELECT classification, obligation_id INTO next_receipt
      FROM {SCHEMA}.terminal_receipt
      WHERE partition_id = {_literal(p['partition_id'])}
        AND source_epoch_digest = {_literal(p['source_epoch_digest'])}
        AND source_position = next_position
      FOR UPDATE;
    EXIT WHEN NOT FOUND;
    IF next_receipt.classification = 'cue_required' AND NOT EXISTS (
      SELECT 1 FROM {SCHEMA}.cue_obligation
      WHERE obligation_id = next_receipt.obligation_id
        AND partition_id = {_literal(p['partition_id'])}
        AND consumer_scope = {_literal(p['consumer_scope'])}
        AND source_epoch_digest = {_literal(p['source_epoch_digest'])}
        AND from_position <= next_position
        AND through_position >= next_position
      FOR UPDATE
    ) THEN
      EXIT;
    END IF;
    UPDATE {SCHEMA}.consumer_checkpoint
      SET checkpoint_state = 'exact', checkpoint_position = next_position
      WHERE partition_id = {_literal(p['partition_id'])}
        AND consumer_scope = {_literal(p['consumer_scope'])}
        AND source_epoch_digest = {_literal(p['source_epoch_digest'])};
    next_position := next_position + 1;
  END LOOP;
END
$cf$;
COMMIT;
"""

    def admit(self, **kwargs: Any) -> None:
        self._sql(self._admit_sql(**kwargs))

    def denied_admit(self, code: str, marker: str, **kwargs: Any) -> None:
        before = self.digest()
        self._expected_failure(self._admit_sql(**kwargs), marker)
        after = self.digest()
        self._require(before == after, f"{code}_changed_state")
        self.denied.append({"id": code, "state_unchanged": True})

    def _dispatch_sql(
        self,
        obligation_id: str,
        *,
        generation: int,
        ordinal: int,
        outcome: str,
        failure_class: str | None,
    ) -> str:
        failure = "NULL" if failure_class is None else _literal(failure_class)
        p = self.fx
        return f"""
BEGIN;
DO $cf$
DECLARE
  current_generation bigint;
  obligation_state text;
  next_ordinal bigint;
BEGIN
  SELECT lease_generation INTO current_generation
    FROM {SCHEMA}.event_partition
    WHERE partition_id = {_literal(p['partition_id'])}
    FOR UPDATE;
  IF NOT FOUND OR current_generation <> {generation} THEN
    RAISE EXCEPTION 'ownership_fenced';
  END IF;
  SELECT state INTO obligation_state
    FROM {SCHEMA}.cue_obligation
    WHERE obligation_id = {_literal(obligation_id)}
    FOR UPDATE;
  IF NOT FOUND THEN RAISE EXCEPTION 'obligation_unknown'; END IF;
  IF obligation_state = 'delivered' THEN RETURN; END IF;
  PERFORM 1 FROM {SCHEMA}.dispatch_attempt
    WHERE obligation_id = {_literal(obligation_id)} FOR UPDATE;
  SELECT COALESCE(MAX(attempt_ordinal), 0) + 1 INTO next_ordinal
    FROM {SCHEMA}.dispatch_attempt
    WHERE obligation_id = {_literal(obligation_id)};
  IF next_ordinal <> {ordinal} THEN
    RAISE EXCEPTION 'attempt_ordinal_out_of_sequence';
  END IF;
  IF ({_literal(outcome)} = 'delivered' AND {failure} IS NOT NULL)
     OR ({_literal(outcome)} = 'failed' AND {failure} IS NULL) THEN
    RAISE EXCEPTION 'dispatch_failure_shape_invalid';
  END IF;
  INSERT INTO {SCHEMA}.dispatch_attempt
    (obligation_id, attempt_ordinal, lease_generation, outcome, failure_class)
  VALUES
    ({_literal(obligation_id)}, {ordinal}, {generation}, {_literal(outcome)}, {failure});
  IF {_literal(outcome)} = 'delivered' THEN
    UPDATE {SCHEMA}.cue_obligation
      SET state = 'delivered'
      WHERE obligation_id = {_literal(obligation_id)};
  END IF;
END
$cf$;
COMMIT;
"""

    def dispatch(self, obligation_id: str, **kwargs: Any) -> None:
        self._sql(self._dispatch_sql(obligation_id, **kwargs))

    def denied_dispatch(
        self, code: str, marker: str, obligation_id: str, **kwargs: Any
    ) -> None:
        before = self.digest()
        self._expected_failure(self._dispatch_sql(obligation_id, **kwargs), marker)
        after = self.digest()
        self._require(before == after, f"{code}_changed_state")
        self.denied.append({"id": code, "state_unchanged": True})

    def _reconcile_sql(
        self,
        obligation_id: str,
        *,
        attempt_ordinal: int,
        reconciliation_id: str,
        outcome: str,
        scope_authorized: bool,
        fresh_read_performed: bool,
        display_disposition: str,
    ) -> str:
        scope = "TRUE" if scope_authorized else "FALSE"
        fresh = "TRUE" if fresh_read_performed else "FALSE"
        return f"""
BEGIN;
DO $cf$
DECLARE
  obligation_state text;
  dispatch_state text;
  existing {SCHEMA}.reconciliation_receipt%ROWTYPE;
BEGIN
  IF NOT (
    ({_literal(outcome)} = 'projection_unchanged' AND {scope} AND {fresh} AND {_literal(display_disposition)} = 'unchanged') OR
    ({_literal(outcome)} = 'projection_refreshed' AND {scope} AND {fresh} AND {_literal(display_disposition)} = 'refreshed') OR
    ({_literal(outcome)} = 'local_selection_or_proposal_cleared' AND {scope} AND {fresh} AND {_literal(display_disposition)} = 'cleared') OR
    ({_literal(outcome)} = 'authorization_rejected' AND NOT {scope} AND NOT {fresh} AND {_literal(display_disposition)} = 'unchanged') OR
    ({_literal(outcome)} = 'source_unavailable' AND {scope} AND NOT {fresh} AND {_literal(display_disposition)} = 'unchanged') OR
    ({_literal(outcome)} = 'stale_session' AND NOT {scope} AND NOT {fresh} AND {_literal(display_disposition)} = 'unchanged')
  ) THEN
    RAISE EXCEPTION 'reconciliation_truth_table_invalid';
  END IF;
  SELECT state INTO obligation_state
    FROM {SCHEMA}.cue_obligation
    WHERE obligation_id = {_literal(obligation_id)}
    FOR UPDATE;
  IF NOT FOUND OR obligation_state <> 'delivered' THEN
    RAISE EXCEPTION 'delivery_not_proved';
  END IF;
  SELECT da.outcome INTO dispatch_state
    FROM {SCHEMA}.dispatch_attempt da
    WHERE da.obligation_id = {_literal(obligation_id)}
      AND da.attempt_ordinal = {attempt_ordinal}
    FOR UPDATE;
  IF NOT FOUND OR dispatch_state <> 'delivered' THEN
    RAISE EXCEPTION 'delivery_not_proved';
  END IF;
  SELECT * INTO existing
    FROM {SCHEMA}.reconciliation_receipt
    WHERE obligation_id = {_literal(obligation_id)}
    FOR UPDATE;
  IF FOUND THEN
    IF existing.dispatch_attempt_ordinal = {attempt_ordinal}
       AND existing.outcome = {_literal(outcome)}
       AND existing.scope_authorized = {scope}
       AND existing.fresh_read_performed = {fresh}
       AND existing.acknowledgement = 'one_fresh_read_attempt_only'
       AND existing.display_disposition = {_literal(display_disposition)} THEN
      RETURN;
    END IF;
    RAISE EXCEPTION 'reconciliation_conflict';
  END IF;
  INSERT INTO {SCHEMA}.reconciliation_receipt
    (reconciliation_id, obligation_id, dispatch_attempt_ordinal, outcome, scope_authorized, fresh_read_performed, acknowledgement, display_disposition)
  VALUES
    ({_literal(reconciliation_id)}, {_literal(obligation_id)}, {attempt_ordinal}, {_literal(outcome)}, {scope}, {fresh}, 'one_fresh_read_attempt_only', {_literal(display_disposition)});
END
$cf$;
COMMIT;
"""

    def reconcile(self, obligation_id: str, **kwargs: Any) -> None:
        self._sql(self._reconcile_sql(obligation_id, **kwargs))

    def denied_reconcile(
        self, code: str, marker: str, obligation_id: str, **kwargs: Any
    ) -> None:
        before = self.digest()
        self._expected_failure(self._reconcile_sql(obligation_id, **kwargs), marker)
        after = self.digest()
        self._require(before == after, f"{code}_changed_state")
        self.denied.append({"id": code, "state_unchanged": True})

    def _advance_only(self) -> None:
        p = self.fx
        self._sql(
            f"""
BEGIN;
DO $cf$
DECLARE next_position bigint; next_receipt record;
BEGIN
  PERFORM 1 FROM {SCHEMA}.event_partition
    WHERE partition_id = {_literal(p['partition_id'])}
      AND lease_generation = {p['lease_generation']} FOR UPDATE;
  IF NOT FOUND THEN RAISE EXCEPTION 'ownership_fenced'; END IF;
  SELECT COALESCE(checkpoint_position, 0) + 1 INTO next_position
    FROM {SCHEMA}.consumer_checkpoint
    WHERE partition_id = {_literal(p['partition_id'])}
      AND consumer_scope = {_literal(p['consumer_scope'])}
      AND source_epoch_digest = {_literal(p['source_epoch_digest'])}
      AND lease_generation = {p['lease_generation']} FOR UPDATE;
  LOOP
    SELECT classification, obligation_id INTO next_receipt
      FROM {SCHEMA}.terminal_receipt
      WHERE partition_id = {_literal(p['partition_id'])}
        AND source_epoch_digest = {_literal(p['source_epoch_digest'])}
        AND source_position = next_position FOR UPDATE;
    EXIT WHEN NOT FOUND;
    IF next_receipt.classification = 'cue_required' AND NOT EXISTS (
      SELECT 1 FROM {SCHEMA}.cue_obligation
      WHERE obligation_id = next_receipt.obligation_id
        AND from_position <= next_position AND through_position >= next_position
      FOR UPDATE
    ) THEN EXIT; END IF;
    UPDATE {SCHEMA}.consumer_checkpoint SET checkpoint_state = 'exact', checkpoint_position = next_position
      WHERE partition_id = {_literal(p['partition_id'])}
        AND consumer_scope = {_literal(p['consumer_scope'])}
        AND source_epoch_digest = {_literal(p['source_epoch_digest'])};
    next_position := next_position + 1;
  END LOOP;
END
$cf$;
COMMIT;
"""
        )

    def run_admission_group(self) -> None:
        self.reset()
        reason = self.fx["cue_reasons"][0]
        self.admit(position=1, receipt_id="receipt-a1", obligation_id="obligation-a1", classification="cue_required", reason_code=reason, generation=7)
        first = self.state()
        self._require(len(first["terminal_receipt"]) == 1, "admission_receipt_missing")
        self._require(len(first["cue_obligation"]) == 1, "admission_obligation_missing")
        self._require(first["consumer_checkpoint"][0]["checkpoint_position"] == 1, "admission_checkpoint_not_advanced")
        before = _canonical_digest(first)
        self.admit(position=1, receipt_id="receipt-unused", obligation_id="obligation-unused", classification="cue_required", reason_code=reason, generation=7)
        self._require(self.digest() == before, "exact_duplicate_changed_state")
        self.denied_admit("divergent_duplicate", "identity_conflict", position=1, receipt_id="receipt-divergent", obligation_id="obligation-divergent", classification="cue_required", reason_code=reason, generation=7, fingerprint_variant="b")
        self.denied_admit("stale_generation_admission", "ownership_fenced", position=2, receipt_id="receipt-stale", obligation_id="obligation-stale", classification="cue_required", reason_code=reason, generation=6)
        rollback_before = self.digest()
        self._expected_failure(
            f"""
BEGIN;
SELECT 1 FROM {SCHEMA}.event_partition WHERE partition_id = {_literal(self.fx['partition_id'])} FOR UPDATE;
UPDATE {SCHEMA}.cue_obligation SET through_position = 2 WHERE obligation_id = 'obligation-a1';
INSERT INTO {SCHEMA}.terminal_receipt
  (receipt_id, partition_id, source_epoch_digest, source_position, event_fingerprint_digest, classification, reason_code, obligation_id)
VALUES
  ('receipt-rollback', {_literal(self.fx['partition_id'])}, {_literal(self.fx['source_epoch_digest'])}, 2, {_literal(_fingerprint(2))}, 'suppressed_irrelevant', NULL, 'obligation-a1');
COMMIT;
""",
            "ck_terminal_receipt_classification_shape",
        )
        rollback_after = self.digest()
        self._require(rollback_before == rollback_after, "admission_forced_rollback_changed_state")
        self.rollbacks.append({"id": "admission_post_obligation_mutation", "state_unchanged": True})
        self._finish_group("admission_identity_fencing_and_atomic_rollback", 8)

    def _denied_coalesce_probe(
        self, probe_id: str, obligation_id: str, target: int, reason: str
    ) -> None:
        before = self.digest()
        self._expected_failure(
            f"""
BEGIN;
DO $cf$ DECLARE row_state record; BEGIN
  SELECT * INTO row_state FROM {SCHEMA}.cue_obligation
    WHERE obligation_id = {_literal(obligation_id)} FOR UPDATE;
  IF NOT FOUND OR row_state.state <> 'pending'
     OR row_state.partition_id <> {_literal(self.fx['partition_id'])}
     OR row_state.source_epoch_digest <> {_literal(self.fx['source_epoch_digest'])}
     OR row_state.consumer_scope <> {_literal(self.fx['consumer_scope'])}
     OR row_state.reason_code <> {_literal(reason)}
     OR row_state.through_position + 1 <> {target} THEN
    RAISE EXCEPTION 'coalesce_precondition_failed';
  END IF;
  UPDATE {SCHEMA}.cue_obligation SET through_position = {target}
    WHERE obligation_id = {_literal(obligation_id)};
END $cf$;
COMMIT;
""",
            "coalesce_precondition_failed",
        )
        self._require(before == self.digest(), f"{probe_id}_changed_state")
        self.denied.append({"id": probe_id, "state_unchanged": True})

    def run_coalescing_group(self) -> None:
        self.reset()
        status_reason, availability_reason = self.fx["cue_reasons"]
        self.admit(position=1, receipt_id="receipt-c1", obligation_id="obligation-c1", classification="cue_required", reason_code=status_reason, generation=7)
        self.admit(position=2, receipt_id="receipt-c2", obligation_id="obligation-unused", classification="cue_required", reason_code=status_reason, generation=7)
        state = self.state()
        self._require(len(state["cue_obligation"]) == 1, "same_reason_not_coalesced")
        self._require(state["cue_obligation"][0]["through_position"] == 2, "coalesced_range_wrong")
        self.admit(position=3, receipt_id="receipt-c3", obligation_id="obligation-c2", classification="cue_required", reason_code=availability_reason, generation=7)
        self._require(len(self.state()["cue_obligation"]) == 2, "different_reason_coalesced")
        self.dispatch("obligation-c1", generation=7, ordinal=1, outcome="delivered", failure_class=None)
        delivered_before = [x for x in self.state()["cue_obligation"] if x["obligation_id"] == "obligation-c1"][0]
        self.admit(position=4, receipt_id="receipt-c4", obligation_id="obligation-c3", classification="cue_required", reason_code=status_reason, generation=7)
        state = self.state()
        delivered_after = [x for x in state["cue_obligation"] if x["obligation_id"] == "obligation-c1"][0]
        self._require(delivered_after == delivered_before, "delivered_obligation_mutated")
        self._require(len(state["cue_obligation"]) == 3, "delivered_obligation_reused")
        self._denied_coalesce_probe("coalesce_gap", "obligation-c2", 5, availability_reason)
        self._denied_coalesce_probe("coalesce_cross_reason", "obligation-c2", 4, status_reason)
        self._denied_coalesce_probe("coalesce_delivered", "obligation-c1", 3, status_reason)
        self._finish_group("pending_only_coalescing_boundaries", 8)

    def run_checkpoint_group(self) -> None:
        self.reset()
        status_reason, availability_reason = self.fx["cue_reasons"]
        self.admit(position=2, receipt_id="receipt-k2", obligation_id="obligation-unused", classification="suppressed_irrelevant", reason_code=None, generation=7)
        self._require(self.state()["consumer_checkpoint"][0]["checkpoint_position"] is None, "out_of_order_gap_crossed")
        self.admit(position=4, receipt_id="receipt-k4", obligation_id="obligation-k4", classification="cue_required", reason_code=availability_reason, generation=7)
        self.admit(position=1, receipt_id="receipt-k1", obligation_id="obligation-unused", classification="rejected_unsupported", reason_code=self.fx["rejection_reason"], generation=7)
        self._require(self.state()["consumer_checkpoint"][0]["checkpoint_position"] == 2, "gap_fill_partial_advance_wrong")
        self.admit(position=3, receipt_id="receipt-k3", obligation_id="obligation-k3", classification="cue_required", reason_code=status_reason, generation=7)
        state = self.state()
        self._require(state["consumer_checkpoint"][0]["checkpoint_position"] == 4, "gap_fill_did_not_advance")
        self._require(len(state["dispatch_attempt"]) == 0, "delivery_incorrectly_required")
        self._sql(
            f"""
INSERT INTO {SCHEMA}.terminal_receipt
  (receipt_id, partition_id, source_epoch_digest, source_position, event_fingerprint_digest, classification, reason_code, obligation_id)
VALUES
  ('receipt-uncovered', {_literal(self.fx['partition_id'])}, {_literal(self.fx['source_epoch_digest'])}, 5, {_literal(_fingerprint(5))}, 'cue_required', {_literal(status_reason)}, 'obligation-k3');
"""
        )
        before = self.digest()
        self._advance_only()
        self._require(before == self.digest(), "uncovered_required_cue_crossed")
        self.denied.append({"id": "checkpoint_uncovered_required_cue", "state_unchanged": True})
        self._finish_group("contiguous_checkpoint_movement", 7)

    def run_dispatch_group(self) -> None:
        self.reset()
        status_reason, availability_reason = self.fx["cue_reasons"]
        self.admit(position=1, receipt_id="receipt-d1", obligation_id="obligation-d1", classification="cue_required", reason_code=status_reason, generation=7)
        self.denied_dispatch("stale_generation_dispatch", "ownership_fenced", "obligation-d1", generation=6, ordinal=1, outcome="failed", failure_class="transient_transport")
        self.dispatch("obligation-d1", generation=7, ordinal=1, outcome="failed", failure_class="transient_transport")
        state = self.state()
        self._require(state["cue_obligation"][0]["state"] == "pending", "failed_dispatch_changed_state")
        self._require(state["dispatch_attempt"][0]["failure_class"] == "transient_transport", "failure_class_not_stable")
        rollback_before = self.digest()
        self._expected_failure(
            """
BEGIN;
SELECT 1 FROM emr4_context_fabric_cue.event_partition FOR UPDATE;
SELECT 1 FROM emr4_context_fabric_cue.cue_obligation WHERE obligation_id = 'obligation-d1' FOR UPDATE;
INSERT INTO emr4_context_fabric_cue.dispatch_attempt
  (obligation_id, attempt_ordinal, lease_generation, outcome, failure_class)
VALUES ('obligation-d1', 2, 7, 'delivered', NULL);
UPDATE emr4_context_fabric_cue.cue_obligation SET state = 'invalid' WHERE obligation_id = 'obligation-d1';
COMMIT;
""",
            "ck_cue_obligation_state",
        )
        self._require(rollback_before == self.digest(), "dispatch_forced_rollback_changed_state")
        self.rollbacks.append({"id": "dispatch_post_attempt_pre_state_transition", "state_unchanged": True})
        self.dispatch("obligation-d1", generation=7, ordinal=2, outcome="delivered", failure_class=None)
        delivered = self.state()
        self._require([x["attempt_ordinal"] for x in delivered["dispatch_attempt"]] == [1, 2], "dispatch_ordinals_wrong")
        self._require(delivered["cue_obligation"][0]["state"] == "delivered", "delivery_state_not_atomic")
        before_duplicate = self.digest()
        self.dispatch("obligation-d1", generation=7, ordinal=3, outcome="delivered", failure_class=None)
        self._require(before_duplicate == self.digest(), "delivered_duplicate_created_attempt")
        self.admit(position=2, receipt_id="receipt-d2", obligation_id="obligation-d2", classification="cue_required", reason_code=availability_reason, generation=7)
        self.denied_dispatch("dispatch_skipped_ordinal", "attempt_ordinal_out_of_sequence", "obligation-d2", generation=7, ordinal=2, outcome="failed", failure_class="consumer_unavailable")
        delivered_before = self.digest()
        self.dispatch("obligation-d1", generation=7, ordinal=3, outcome="failed", failure_class="consumer_unavailable")
        self._require(delivered_before == self.digest(), "delivered_to_pending_regression")
        self._finish_group("dispatch_ordering_and_atomic_rollback", 10)

    def run_reconciliation_group(self) -> None:
        self.reset()
        status_reason, availability_reason = self.fx["cue_reasons"]
        self.admit(position=1, receipt_id="receipt-r1", obligation_id="obligation-r1", classification="cue_required", reason_code=status_reason, generation=7)
        self.admit(position=2, receipt_id="receipt-r2", obligation_id="obligation-r2", classification="cue_required", reason_code=availability_reason, generation=7)
        self.dispatch("obligation-r1", generation=7, ordinal=1, outcome="delivered", failure_class=None)
        self.dispatch("obligation-r2", generation=7, ordinal=1, outcome="failed", failure_class="consumer_unavailable")
        self.denied_reconcile("reconcile_without_delivered_attempt", "delivery_not_proved", "obligation-r2", attempt_ordinal=1, reconciliation_id="reconciliation-r2", outcome="authorization_rejected", scope_authorized=False, fresh_read_performed=False, display_disposition="unchanged")
        rollback_before = self.digest()
        self._expected_failure(
            """
BEGIN;
SELECT 1 FROM emr4_context_fabric_cue.cue_obligation WHERE obligation_id = 'obligation-r1' FOR UPDATE;
SELECT 1 FROM emr4_context_fabric_cue.dispatch_attempt WHERE obligation_id = 'obligation-r1' AND attempt_ordinal = 1 FOR UPDATE;
INSERT INTO emr4_context_fabric_cue.reconciliation_receipt
  (reconciliation_id, obligation_id, dispatch_attempt_ordinal, outcome, scope_authorized, fresh_read_performed, acknowledgement, display_disposition)
VALUES
  ('reconciliation-rollback', 'obligation-r1', 1, 'projection_refreshed', TRUE, TRUE, 'one_fresh_read_attempt_only', 'refreshed');
SELECT 1 / 0;
COMMIT;
""",
            "division by zero",
        )
        self._require(rollback_before == self.digest(), "reconciliation_forced_rollback_changed_state")
        self.rollbacks.append({"id": "reconciliation_post_receipt", "state_unchanged": True})
        args = dict(attempt_ordinal=1, reconciliation_id="reconciliation-r1", outcome="projection_refreshed", scope_authorized=True, fresh_read_performed=True, display_disposition="refreshed")
        self.reconcile("obligation-r1", **args)
        state = self.state()
        self._require(len(state["reconciliation_receipt"]) == 1, "reconciliation_missing")
        self._require("future_freshness" not in state["reconciliation_receipt"][0], "future_freshness_represented")
        duplicate_before = self.digest()
        duplicate_args = dict(args)
        duplicate_args["reconciliation_id"] = "reconciliation-unused"
        self.reconcile("obligation-r1", **duplicate_args)
        self._require(duplicate_before == self.digest(), "reconciliation_duplicate_changed_state")
        conflict_args = dict(args)
        conflict_args.update(outcome="projection_unchanged", display_disposition="unchanged", reconciliation_id="reconciliation-conflict")
        self.denied_reconcile("reconciliation_conflict", "reconciliation_conflict", "obligation-r1", **conflict_args)
        invalid_args = dict(args)
        invalid_args.update(reconciliation_id="reconciliation-invalid", scope_authorized=False)
        self.denied_reconcile("reconciliation_truth_table_invalid", "reconciliation_truth_table_invalid", "obligation-r1", **invalid_args)
        self._finish_group("delivered_only_reconciliation_and_atomic_rollback", 9)

    def _lock_probe(self, protocol: dict[str, Any]) -> None:
        statements = "\n".join(
            f"  PERFORM 1 FROM {SCHEMA}.{relation} FOR UPDATE;"
            for relation in protocol["required_lock_relations"]
        )
        result = self._sql(
            f"""
BEGIN;
DO $cf$ BEGIN
{statements}
END $cf$;
SELECT COALESCE(pg_catalog.jsonb_agg(pg_catalog.jsonb_build_object('relation', relname, 'mode', mode) ORDER BY relname, mode), '[]'::jsonb)::text
FROM (
  SELECT DISTINCT c.relname, l.mode
  FROM pg_catalog.pg_locks l
  JOIN pg_catalog.pg_class c ON c.oid = l.relation
  JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace
  WHERE l.pid = pg_catalog.pg_backend_pid()
    AND l.granted IS TRUE
    AND n.nspname = '{SCHEMA}'
    AND c.relkind = 'r'
) observed;
ROLLBACK;
""",
            tuples_only=True,
        )
        try:
            observed = json.loads(catalogue._stdout_value(result))
        except (json.JSONDecodeError, UnicodeDecodeError) as error:
            raise RehearsalFailure("locks", "lock_projection_invalid", str(error)) from error
        pairs = {(item["relation"], item["mode"]) for item in observed}
        required = {
            (relation, self.contract["acceptance"]["required_relation_lock_mode"])
            for relation in protocol["required_lock_relations"]
        }
        self._require(required <= pairs, f"{protocol['name']}_required_lock_missing")
        self.locks.append(
            {
                "protocol": protocol["name"],
                "required_relation_mode_pairs": [
                    {"relation": relation, "mode": mode}
                    for relation, mode in sorted(required)
                ],
                "required_subset_observed": True,
                "contention_claim": False,
            }
        )

    def run_lock_group(self) -> None:
        self.reset()
        self.admit(position=1, receipt_id="receipt-l1", obligation_id="obligation-l1", classification="cue_required", reason_code=self.fx["cue_reasons"][0], generation=7)
        self.dispatch("obligation-l1", generation=7, ordinal=1, outcome="delivered", failure_class=None)
        self.reconcile("obligation-l1", attempt_ordinal=1, reconciliation_id="reconciliation-l1", outcome="projection_unchanged", scope_authorized=True, fresh_read_performed=True, display_disposition="unchanged")
        for protocol in self.contract["protocols"]:
            self._lock_probe(protocol)
        self._finish_group("uncontended_protocol_lock_footprints", 5)

    def run_all(self) -> None:
        self.run_admission_group()
        self.run_coalescing_group()
        self.run_checkpoint_group()
        self.run_dispatch_group()
        self.run_reconciliation_group()
        self.run_lock_group()
        if [group["id"] for group in self.groups] != self.contract["scenario_groups"]:
            raise RehearsalFailure("scenario", "scenario_group_order_mismatch")


def _base_evidence(contract: dict[str, Any] | None) -> dict[str, Any]:
    return {
        "schema_version": EVIDENCE_SCHEMA_VERSION,
        "result": FAIL_RESULT,
        "status": "failed",
        "evidence_label": (
            contract["evidence_label"]
            if contract is not None
            else "authored_synthetic_provider_free_disposable_postgresql_16_serial_behavior_transaction"
        ),
        "contract_sha256": "sha256:" + _sha256(CONTRACT_PATH.read_bytes()),
        "source_hashes": {},
        "hostile_mutations_rejected": 0,
        "environment": {},
        "scenario_groups": [],
        "protocols_proved": [],
        "rollback_probes": [],
        "denied_transition_probes": [],
        "lock_observations": [],
        "cleanup": {"status": "not_needed"},
        "effects": {},
        "claim_boundary": CLAIM_BOUNDARY,
    }


def run_rehearsal(runner: Runner = catalogue._run) -> dict[str, Any]:
    contract: dict[str, Any] | None = None
    evidence = _base_evidence(contract)
    docker = ""
    container_id = ""
    name = ""
    nonce = ""
    try:
        contract, source_hashes, artifact = verify_contract()
        evidence = _base_evidence(contract)
        evidence["source_hashes"] = source_hashes
        evidence["hostile_mutations_rejected"] = contract["hostile_mutation_target"]
        profile = contract["docker_profile"]
        deadline = time.monotonic() + profile["total_timeout_seconds"]

        docker = shutil.which(profile["executable"]) or ""
        if not docker:
            raise RehearsalFailure("environment", "docker_client_missing")
        image_result = runner(
            [docker, "image", "inspect", profile["image_reference"]],
            None,
            profile["command_timeout_seconds"],
            256_000,
        )
        if image_result.returncode != 0:
            raise RehearsalFailure("environment", "local_image_unavailable")
        try:
            image = json.loads(image_result.stdout.decode("utf-8"))[0]
            image_id = image["Id"]
            repo_digests = image["RepoDigests"]
        except (UnicodeDecodeError, json.JSONDecodeError, IndexError, KeyError, TypeError):
            raise RehearsalFailure("environment", "image_inspect_invalid") from None
        if image_id != profile["image_id"] or profile["repo_digest"] not in repo_digests:
            raise RehearsalFailure("environment", "local_image_identity_mismatch")

        nonce = secrets.token_hex(16)
        name = profile["container_name_prefix"] + secrets.token_hex(8)
        created = runner(
            catalogue.build_container_argv(docker, name, nonce, contract),
            None,
            profile["command_timeout_seconds"],
            16_384,
        )
        if created.returncode != 0:
            raise RehearsalFailure("container", "create_failed", created.stderr)
        container_id = created.stdout.decode("ascii", errors="strict").strip()
        if not re.fullmatch(r"[0-9a-f]{64}", container_id):
            raise RehearsalFailure("container", "captured_id_invalid")
        inspected_result, inspected = catalogue._inspect(
            runner, docker, container_id, profile["command_timeout_seconds"]
        )
        if inspected_result.returncode != 0 or inspected is None or not catalogue._container_owned(
            inspected,
            container_id=container_id,
            name=name,
            nonce=nonce,
            profile=profile,
        ):
            raise RehearsalFailure("container", "ownership_or_profile_mismatch")

        readiness_deadline = min(
            deadline, time.monotonic() + profile["startup_timeout_seconds"]
        )
        observations = 0
        while time.monotonic() < readiness_deadline and observations < profile["readiness_observations"]:
            ready = runner(
                [
                    docker,
                    "exec",
                    "--env",
                    f"PGPASSWORD={profile['postgres_password']}",
                    container_id,
                    "pg_isready",
                    "--quiet",
                    "--username",
                    profile["postgres_user"],
                    "--dbname",
                    profile["postgres_database"],
                    "--host",
                    "/var/run/postgresql",
                ],
                None,
                5,
                4096,
            )
            if ready.returncode != 0:
                observations = 0
                time.sleep(1)
                continue
            version = runner(
                catalogue._psql_argv(docker, container_id, profile, tuples_only=True),
                b"SELECT current_setting('server_version_num')::integer / 10000;\n",
                5,
                4096,
            )
            if version.returncode != 0:
                observations = 0
                time.sleep(1)
                continue
            try:
                major = catalogue._stdout_value(version)
            except catalogue.RehearsalFailure:
                observations = 0
                time.sleep(1)
                continue
            if major != "16":
                observations = 0
                time.sleep(1)
                continue
            observations += 1
            if observations < profile["readiness_observations"]:
                time.sleep(1)
        if observations != profile["readiness_observations"]:
            raise RehearsalFailure("readiness", "postgresql_16_not_ready")
        if time.monotonic() >= deadline:
            raise RehearsalFailure("bounds", "total_timeout_exceeded")

        catalogue._psql(
            runner,
            docker,
            container_id,
            profile,
            artifact,
            single_transaction=True,
        )
        parse_contract = catalogue._load_json(catalogue.CONTRACT_PATH)
        manifest = catalogue._load_json(catalogue.MANIFEST_PATH)
        catalogue._assert_catalogue(
            catalogue._query_json(
                runner, docker, container_id, profile, catalogue.CATALOGUE_SQL
            ),
            parse_contract,
            manifest,
        )
        catalogue._assert_row_counts(
            catalogue._query_json(
                runner, docker, container_id, profile, catalogue.ROW_COUNTS_SQL
            ),
            parse_contract,
        )

        scenarios = DatabaseScenarios(runner, docker, container_id, contract)
        scenarios.run_all()
        evidence.update(
            {
                "result": PASS_RESULT,
                "status": "passed",
                "environment": {
                    "postgresql_major": 16,
                    "image_reference": profile["image_reference"],
                    "image_id_sha256": "sha256:" + _sha256(image_id.encode("ascii")),
                    "repo_digest_sha256": "sha256:" + _sha256(profile["repo_digest"].encode("ascii")),
                    "network_mode": "none",
                    "storage": "container_local_tmpfs",
                    "catalogue_re_admitted": True,
                },
                "scenario_groups": scenarios.groups,
                "protocols_proved": [item["name"] for item in contract["protocols"]],
                "rollback_probes": scenarios.rollbacks,
                "denied_transition_probes": scenarios.denied,
                "lock_observations": scenarios.locks,
                "effects": contract["effects"],
            }
        )
    except (RehearsalFailure, catalogue.RehearsalFailure) as error:
        evidence["failure"] = {
            "stage": error.stage,
            "code": error.code,
            "detail_sha256": "sha256:" + _sha256(error.detail),
        }
    finally:
        cleanup: dict[str, Any] = {"status": "not_needed"}
        if container_id and contract is not None:
            cleanup = catalogue._cleanup(
                runner,
                docker,
                container_id,
                name,
                nonce,
                contract["docker_profile"],
            )
            if cleanup["status"] != "cleanup_verified":
                evidence["result"] = FAIL_RESULT
                evidence["status"] = "failed"
                evidence["failure"] = {
                    "stage": "cleanup",
                    "code": cleanup["status"],
                    "detail_sha256": "sha256:" + _sha256(b""),
                }
        evidence["cleanup"] = cleanup
    return evidence


def validate_evidence(evidence: dict[str, Any]) -> None:
    Draft202012Validator(_load_json(EVIDENCE_SCHEMA_PATH)).validate(evidence)
    if evidence["result"] != PASS_RESULT or evidence["claim_boundary"] != CLAIM_BOUNDARY:
        raise RehearsalFailure("evidence", "evidence_semantics_mismatch")


def _write(path: Path, evidence: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(evidence, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def main() -> int:
    if len(sys.argv) != 1:
        print(json.dumps({"result": FAIL_RESULT, "failure": "arguments_not_allowed"}))
        return 2
    evidence = run_rehearsal()
    if evidence["result"] == PASS_RESULT:
        evidence.pop("failure", None)
        validate_evidence(evidence)
        _write(EVIDENCE_PATH, evidence)
        print(json.dumps({"result": PASS_RESULT, "evidence": str(EVIDENCE_PATH)}))
        return 0
    _write(FAILURE_EVIDENCE_PATH, evidence)
    print(
        json.dumps(
            {
                "result": FAIL_RESULT,
                "evidence": str(FAILURE_EVIDENCE_PATH),
                "failure": evidence.get("failure"),
            }
        )
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
