"""Identify only the failed conjunct behind behavior failure 022."""

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


FUNCTION_START = b"CREATE FUNCTION emr4_context_fabric.cf_fence_stream_head_v1()"
FUNCTION_END = (
    b"ALTER FUNCTION emr4_context_fabric.cf_fence_stream_head_v1() "
    b"OWNER TO context_schema_owner;"
)
ORIGINAL_RAISE = (
    b"RAISE EXCEPTION USING ERRCODE = 'CF105', "
    b"MESSAGE = 'stream_head_invalid_or_exhausted';"
)
DIAGNOSTIC_RAISE = (
    b"RAISE EXCEPTION USING ERRCODE = 'CF105', MESSAGE = "
    b"pg_catalog.format('stream_head_diagnostic:%s:%s:%s', "
    b"COALESCE((final_head.last_position = 0::pg_catalog.int8)"
    b"::pg_catalog.text, 'null'::pg_catalog.text), "
    b"COALESCE((final_head.stream_epoch = 1::pg_catalog.int8)"
    b"::pg_catalog.text, 'null'::pg_catalog.text), "
    b"COALESCE((final_head.xmin = ((((pg_catalog.pg_current_xact_id()"
    b"::pg_catalog.text)::pg_catalog.int8 & 4294967295)::pg_catalog.text)"
    b"::pg_catalog.xid))::pg_catalog.text, 'null'::pg_catalog.text));"
)
DIAGNOSTIC_PATTERN = re.compile(
    rb"stream_head_diagnostic:(true|false|null):(true|false|null):(true|false|null)"
)


def diagnostic_function_sql(artifact: bytes) -> bytes:
    """Extract the accepted function and alter only its failure message in memory."""
    if artifact.count(FUNCTION_START) != 1 or artifact.count(FUNCTION_END) != 1:
        raise RuntimeError("diagnostic_function_boundary_not_unique")
    start = artifact.index(FUNCTION_START)
    end = artifact.index(FUNCTION_END, start) + len(FUNCTION_END)
    function = artifact[start:end]
    if function.count(ORIGINAL_RAISE) != 1:
        raise RuntimeError("diagnostic_raise_not_unique_within_function")
    function = function.replace(
        FUNCTION_START,
        b"CREATE OR REPLACE FUNCTION emr4_context_fabric.cf_fence_stream_head_v1()",
        1,
    ).replace(ORIGINAL_RAISE, DIAGNOSTIC_RAISE, 1)
    if b"pg_catalog.coalesce" in function or function.count(b"COALESCE(") != 3:
        raise RuntimeError("diagnostic_coalesce_special_form_invalid")
    return function + b"\n"


class ConjunctDiagnosticRunner:
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
    runner = ConjunctDiagnosticRunner(target_sql, diagnostic_sql)
    evidence = behavior.run_rehearsal(runner=runner)
    failure = evidence.get("environment", {}).get("failure", {})
    cleanup = evidence.get("cleanup", {})
    if not (
        runner.installed
        and evidence.get("result") == "rehearsal_failed"
        and failure.get("scenario_id") == "BTR-E01"
        and failure.get("sqlstate") == "CF105"
        and evidence.get("scenario_reconciliation", {}).get("observed") == 0
        and cleanup.get("status") == "cleanup_verified"
        and cleanup.get("absence_verified") is True
    ):
        raise RuntimeError("failure_022_conjunct_diagnosis_not_closed")
    if runner.target_result is None:
        raise RuntimeError("target_scenario_result_missing")

    raw = runner.target_result.stdout + b"\n" + runner.target_result.stderr
    matches = DIAGNOSTIC_PATTERN.findall(raw)
    if len(matches) != 1:
        raise RuntimeError("single_conjunct_diagnostic_missing")
    last_position, stream_epoch, xmin = (value.decode("ascii") for value in matches[0])
    return {
        "schema_version": "emr4.raisa-context-fabric-durability-failure-022-conjunct-diagnosis.v1",
        "status": "conjunct_diagnosis_complete_cleanup_verified",
        "parent_failure": {
            "run_sequence": 22,
            "internal_attempt_id": "c9288fb197ed96d136f6022b",
            "evidence_sha256": "sha256:6ae6ef74c6a44c8f022f54f54bbc31d6a867a6f9953b7ee52ca34e68bf71f224",
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
        "conjuncts": {
            "last_position_equals_zero": last_position,
            "stream_epoch_equals_one": stream_epoch,
            "xmin_equals_current_transaction": xmin,
        },
        "authority_boundary": "provider_free_authored_synthetic_disposable_postgresql_diagnosis_only_no_product_provider_command_deployment_or_protected_ref_authority",
    }


def main() -> int:
    print(json.dumps(diagnose(), sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
