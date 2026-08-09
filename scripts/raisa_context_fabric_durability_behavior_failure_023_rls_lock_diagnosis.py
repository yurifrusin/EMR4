"""Identify the RLS lock-path outcome behind behavior failure 023."""

from __future__ import annotations

import hashlib
import json
import re
from typing import Any

from scripts import (
    raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal as behavior,
)
from scripts import (
    raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal as parent,
)


FUNCTION_START = (
    b"CREATE FUNCTION emr4_context_fabric.register_observer_generation_v1("
    b"registration emr4_context_fabric.generation_registration_v1)"
)
FUNCTION_END = (
    b"ALTER FUNCTION emr4_context_fabric.register_observer_generation_v1("
    b"registration emr4_context_fabric.generation_registration_v1) "
    b"OWNER TO context_schema_owner;"
)
LOCK_BLOCK_START = (
    b"    ELSE\n"
    b"        BEGIN\n"
    b"SELECT emr4_context_fabric.context_observation_stream_head.practice_id"
)
LOCK_BLOCK_END = (
    b"        END;\n"
    b"    END IF;\n"
    b"    SELECT COALESCE(pg_catalog.array_agg((ROW("
    b"emr4_context_fabric.context_observer_generation.practice_id"
)
ORIGINAL_NO_DATA_RAISE = (
    b"                RAISE EXCEPTION USING ERRCODE = 'CF004', "
    b"MESSAGE = 'required_row_missing_or_ambiguous';"
)
ORIGINAL_TOO_MANY_RAISE = ORIGINAL_NO_DATA_RAISE
DIAGNOSTIC_NO_DATA_RAISE = (
    b"                RAISE EXCEPTION USING ERRCODE = 'CF004', MESSAGE = "
    b"pg_catalog.format('stream_head_lock_diagnostic:%s:%s:no_data', "
    b"COALESCE(pg_catalog.array_length(head_set, 1), 0)::pg_catalog.text, "
    b"COALESCE(binding_allowed::pg_catalog.text, 'null'::pg_catalog.text));"
)
DIAGNOSTIC_TOO_MANY_RAISE = (
    b"                RAISE EXCEPTION USING ERRCODE = 'CF004', MESSAGE = "
    b"pg_catalog.format('stream_head_lock_diagnostic:%s:%s:too_many', "
    b"COALESCE(pg_catalog.array_length(head_set, 1), 0)::pg_catalog.text, "
    b"COALESCE(binding_allowed::pg_catalog.text, 'null'::pg_catalog.text));"
)
DIAGNOSTIC_PATTERN = re.compile(
    rb"stream_head_lock_diagnostic:([0-9]+):(true|false|null):(no_data|too_many)"
)


def diagnostic_function_sql(artifact: bytes) -> bytes:
    """Change only the two stream-head lock rejection messages in memory."""
    if artifact.count(FUNCTION_START) != 1 or artifact.count(FUNCTION_END) != 1:
        raise RuntimeError("diagnostic_function_boundary_not_unique")
    function_start = artifact.index(FUNCTION_START)
    function_end = artifact.index(FUNCTION_END, function_start) + len(FUNCTION_END)
    function = artifact[function_start:function_end]
    if function.count(LOCK_BLOCK_START) != 1 or function.count(LOCK_BLOCK_END) != 1:
        raise RuntimeError("stream_head_lock_block_boundary_not_unique")
    block_start = function.index(LOCK_BLOCK_START)
    block_end = function.index(LOCK_BLOCK_END, block_start)
    block = function[block_start:block_end]
    if block.count(ORIGINAL_NO_DATA_RAISE) != 2:
        raise RuntimeError("stream_head_lock_raise_population_not_exact")
    block = block.replace(ORIGINAL_NO_DATA_RAISE, DIAGNOSTIC_NO_DATA_RAISE, 1)
    block = block.replace(ORIGINAL_TOO_MANY_RAISE, DIAGNOSTIC_TOO_MANY_RAISE, 1)
    function = function[:block_start] + block + function[block_end:]
    function = function.replace(
        FUNCTION_START,
        b"CREATE OR REPLACE FUNCTION "
        + FUNCTION_START.removeprefix(b"CREATE FUNCTION "),
        1,
    )
    if function.count(b"stream_head_lock_diagnostic:") != 2:
        raise RuntimeError("stream_head_lock_diagnostic_population_not_exact")
    if b"pg_catalog.coalesce" in function:
        raise RuntimeError("diagnostic_coalesce_special_form_invalid")
    return function + b"\n"


class RlsLockDiagnosticRunner:
    """Install an ephemeral diagnostic body immediately before exact BTR-E01."""

    def __init__(self, target_sql: bytes, diagnostic_sql: bytes) -> None:
        self._target_sql = target_sql
        self._diagnostic_sql = diagnostic_sql
        self.installed = False
        self.target_result: parent.ProcessResult | None = None

    def __call__(
        self,
        argv: list[str],
        stdin: bytes | None,
        timeout: float,
        cap: int,
    ) -> parent.ProcessResult:
        if stdin == self._target_sql:
            if self.installed or self.target_result is not None:
                raise RuntimeError("duplicate_target_scenario_execution")
            installed = parent._subprocess_runner(  # noqa: SLF001
                argv, self._diagnostic_sql, timeout, cap
            )
            if installed.returncode != 0:
                raise RuntimeError("ephemeral_diagnostic_function_rejected")
            self.installed = True
            self.target_result = parent._subprocess_runner(  # noqa: SLF001
                argv, stdin, timeout, cap
            )
            return self.target_result
        return parent._subprocess_runner(argv, stdin, timeout, cap)  # noqa: SLF001


def diagnose() -> dict[str, Any]:
    contract, _, _, artifact = behavior._validate_contract()  # noqa: SLF001
    target_sql = behavior.render_scenario_sql(contract, "BTR-E01")
    diagnostic_sql = diagnostic_function_sql(artifact)
    runner = RlsLockDiagnosticRunner(target_sql, diagnostic_sql)
    evidence = behavior.run_rehearsal(runner=runner)
    failure = evidence.get("environment", {}).get("failure", {})
    cleanup = evidence.get("cleanup", {})
    if not (
        runner.installed
        and evidence.get("result") == "rehearsal_failed"
        and failure.get("scenario_id") == "BTR-E01"
        and failure.get("sqlstate") == "CF004"
        and evidence.get("scenario_reconciliation", {}).get("observed") == 0
        and cleanup.get("status") == "cleanup_verified"
        and cleanup.get("absence_verified") is True
    ):
        raise RuntimeError("failure_023_rls_lock_diagnosis_not_closed")
    if runner.target_result is None:
        raise RuntimeError("target_scenario_result_missing")

    raw = runner.target_result.stdout + b"\n" + runner.target_result.stderr
    matches = DIAGNOSTIC_PATTERN.findall(raw)
    if len(matches) != 1:
        raise RuntimeError("single_rls_lock_diagnostic_missing")
    head_count, binding_allowed, lock_result = (
        value.decode("ascii") for value in matches[0]
    )
    return {
        "schema_version": "emr4.raisa-context-fabric-durability-failure-023-rls-lock-diagnosis.v1",
        "status": "rls_lock_diagnosis_complete_cleanup_verified",
        "parent_failure": {
            "run_sequence": 23,
            "internal_attempt_id": "67a7eab53961e8284fae1ac9",
            "evidence_sha256": "sha256:de359f9acc731b0127517b6dc14accb9bfe7e9b5ae63b35213cf5d6e160649ee",
        },
        "diagnosis_runtime": {
            "internal_attempt_id": evidence["attempt_id"],
            "ephemeral_function_sha256": "sha256:"
            + hashlib.sha256(diagnostic_sql).hexdigest(),
            "raw_diagnostic_sha256": "sha256:" + hashlib.sha256(raw).hexdigest(),
            "raw_error_persisted": False,
            "container_id": cleanup["container_id"],
            "cleanup_absence_verified": True,
        },
        "observations": {
            "plain_select_head_count": int(head_count),
            "lifecycle_binding_allowed": binding_allowed,
            "select_for_update_result": lock_result,
        },
        "authority_boundary": "provider_free_authored_synthetic_disposable_postgresql_diagnosis_only_no_product_provider_command_deployment_or_protected_ref_authority",
    }


def main() -> int:
    print(json.dumps(diagnose(), sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
