"""Classify the undefined PostgreSQL symbol behind behavior failure 024."""

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


UNDEFINED_FUNCTION_PATTERN = re.compile(
    rb"(?m)^(?:psql:[^\r\n]{1,160}:\s*)?ERROR:\s+42883:\s+function\s+"
    rb"([a-z][a-z0-9_.]*)\([^\r\n]{0,500}\)\s+does not exist(?:\s+at character [0-9]+)?\s*$"
)
UNDEFINED_OPERATOR_PATTERN = re.compile(
    rb"(?m)^(?:psql:[^\r\n]{1,160}:\s*)?ERROR:\s+42883:\s+operator does not exist:\s+"
    rb"([^\r\n]{1,160})\s*$"
)

SAFE_FUNCTION_SYMBOLS = {
    "pg_catalog.sha256": "pg_catalog.sha256",
    "sha256": "pg_catalog.sha256",
    "pg_catalog.make_interval": "pg_catalog.make_interval",
    "make_interval": "pg_catalog.make_interval",
    "pg_catalog.to_char": "pg_catalog.to_char",
    "to_char": "pg_catalog.to_char",
    "pg_catalog.jsonb_build_object": "pg_catalog.jsonb_build_object",
    "jsonb_build_object": "pg_catalog.jsonb_build_object",
    "emr4_context_fabric.project_update_confirm_reschedule_v1": (
        "emr4_context_fabric.project_update_confirm_reschedule_v1"
    ),
}
SAFE_OPERATOR_SIGNATURES = {
    "integer * interval": "pg_catalog.int4_times_interval",
    "interval * integer": "pg_catalog.interval_times_int4",
    "bigint * interval": "pg_catalog.int8_times_interval",
    "interval * bigint": "pg_catalog.interval_times_int8",
}

RESOLUTION_PROBE_SQL = b"""SELECT pg_catalog.json_build_object(
'pg_catalog.sha256',pg_catalog.to_regprocedure('pg_catalog.sha256(bytea)') IS NOT NULL,
'emr4_context_fabric.project_update_confirm_reschedule_v1',pg_catalog.to_regprocedure('emr4_context_fabric.project_update_confirm_reschedule_v1(uuid)') IS NOT NULL,
'pg_catalog.make_interval',pg_catalog.to_regprocedure('pg_catalog.make_interval(integer,integer,integer,integer,integer,integer,double precision)') IS NOT NULL,
'pg_catalog.to_char_timestamptz',pg_catalog.to_regprocedure('pg_catalog.to_char(timestamp with time zone,text)') IS NOT NULL,
'pg_catalog.int4_times_interval',pg_catalog.to_regoperator('pg_catalog.*(integer,interval)') IS NOT NULL,
'pg_catalog.timestamptz_plus_interval',pg_catalog.to_regoperator('pg_catalog.+(timestamp with time zone,interval)') IS NOT NULL
)::pg_catalog.text;
"""
REQUIRED_RESOLUTION_SYMBOLS = frozenset(
    {
        "pg_catalog.sha256",
        "emr4_context_fabric.project_update_confirm_reschedule_v1",
        "pg_catalog.make_interval",
        "pg_catalog.to_char_timestamptz",
        "pg_catalog.int4_times_interval",
        "pg_catalog.timestamptz_plus_interval",
    }
)


def classify_undefined_symbol(raw: bytes) -> str:
    """Return one closed symbol identifier without releasing raw error text."""
    function_matches = {
        value.decode("ascii") for value in UNDEFINED_FUNCTION_PATTERN.findall(raw)
    }
    operator_matches = {
        value.decode("ascii") for value in UNDEFINED_OPERATOR_PATTERN.findall(raw)
    }
    admitted: set[str] = set()
    for value in function_matches:
        if value in SAFE_FUNCTION_SYMBOLS:
            admitted.add(SAFE_FUNCTION_SYMBOLS[value])
    for value in operator_matches:
        if value in SAFE_OPERATOR_SIGNATURES:
            admitted.add(SAFE_OPERATOR_SIGNATURES[value])
    if len(admitted) != 1:
        raise RuntimeError("single_allowlisted_undefined_symbol_missing")
    return next(iter(admitted))


class UndefinedSymbolDiagnosticRunner:
    """Capture only the exact BTR-E02 result while preserving normal cleanup."""

    def __init__(self, target_sql: bytes) -> None:
        self._target_sql = target_sql
        self.target_result: parent.ProcessResult | None = None
        self.resolution: dict[str, bool] | None = None

    def __call__(
        self,
        argv: list[str],
        stdin: bytes | None,
        timeout: float,
        cap: int,
    ) -> parent.ProcessResult:
        if stdin == self._target_sql:
            if self.target_result is not None:
                raise RuntimeError("duplicate_target_scenario_execution")
            probe = parent._subprocess_runner(  # noqa: SLF001
                argv, RESOLUTION_PROBE_SQL, timeout, cap
            )
            if probe.returncode != 0:
                raise RuntimeError("resolution_probe_failed")
            lines = [line.strip() for line in probe.stdout.splitlines() if line.strip()]
            if len(lines) != 1:
                raise RuntimeError("resolution_probe_output_population")
            candidate = json.loads(lines[0])
            if (
                not isinstance(candidate, dict)
                or set(candidate) != REQUIRED_RESOLUTION_SYMBOLS
                or any(type(value) is not bool for value in candidate.values())
            ):
                raise RuntimeError("resolution_probe_output_shape")
            self.resolution = candidate
            self.target_result = parent._subprocess_runner(  # noqa: SLF001
                argv, stdin, timeout, cap
            )
            return self.target_result
        return parent._subprocess_runner(argv, stdin, timeout, cap)  # noqa: SLF001


def diagnose() -> dict[str, Any]:
    contract, _, _, _ = behavior._validate_contract()  # noqa: SLF001
    target_sql = behavior.render_scenario_sql(contract, "BTR-E02")
    runner = UndefinedSymbolDiagnosticRunner(target_sql)
    evidence = behavior.run_rehearsal(runner=runner)
    failure = evidence.get("environment", {}).get("failure", {})
    cleanup = evidence.get("cleanup", {})
    if not (
        evidence.get("result") == "rehearsal_failed"
        and failure.get("scenario_id") == "BTR-E02"
        and failure.get("sqlstate") == "42883"
        and evidence.get("scenario_reconciliation", {}).get("observed") == 0
        and cleanup.get("status") == "cleanup_verified"
        and cleanup.get("absence_verified") is True
    ):
        raise RuntimeError("failure_024_undefined_symbol_diagnosis_not_closed")
    if runner.target_result is None or runner.resolution is None:
        raise RuntimeError("target_scenario_result_missing")

    raw = runner.target_result.stdout + b"\n" + runner.target_result.stderr
    missing_symbols = sorted(
        name for name, available in runner.resolution.items() if not available
    )
    raw_symbol: str | None
    try:
        raw_symbol = classify_undefined_symbol(raw)
    except RuntimeError:
        raw_symbol = None
    return {
        "schema_version": "emr4.raisa-context-fabric-durability-failure-024-undefined-symbol-diagnosis.v1",
        "status": "undefined_symbol_diagnosis_complete_cleanup_verified",
        "parent_failure": {
            "run_sequence": 24,
            "internal_attempt_id": "556dc0541f0152f96bea4ba5",
            "evidence_sha256": "sha256:bc2efc6fffea47e8104324c822bd6c1afde28f746b05b2a5bff925dbbfe7f57b",
        },
        "diagnosis_runtime": {
            "internal_attempt_id": evidence["attempt_id"],
            "raw_diagnostic_sha256": "sha256:" + hashlib.sha256(raw).hexdigest(),
            "raw_error_persisted": False,
            "container_id": cleanup["container_id"],
            "cleanup_absence_verified": True,
        },
        "observation": {
            "scenario_id": "BTR-E02",
            "sqlstate": "42883",
            "resolution": runner.resolution,
            "missing_symbols": missing_symbols,
            "raw_message_symbol_id": raw_symbol,
        },
        "authority_boundary": "provider_free_authored_synthetic_disposable_postgresql_diagnosis_only_no_product_provider_command_deployment_or_protected_ref_authority",
    }


def main() -> int:
    print(json.dumps(diagnose(), sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
