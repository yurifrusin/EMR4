"""Classify the remaining PostgreSQL symbol behind behavior failure 025."""

from __future__ import annotations

import hashlib
import json
import re
from typing import Any

from scripts import (
    raisa_context_fabric_durability_behavior_failure_024_undefined_symbol_diagnosis as prior,
)
from scripts import (
    raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal as behavior,
)


PARENT_ATTEMPT_ID = "be5d718776ad1353669e37dd"
PARENT_EVIDENCE_SHA256 = (
    "sha256:b963933df05c418456fdc1e101a7254a617ba743a4cb4b03888caf0aac547ba2"
)
EXPECTED_REPAIRED_ABSENCE = "pg_catalog.int4_times_interval"
CALL_NAME = re.compile(rb"(?<![a-zA-Z0-9_])([a-z][a-z0-9_.]*)\s*\(")
SAFE_TYPE_OPERATOR = re.compile(
    r"^[a-z][a-z0-9_ ]*(?:\[\])?\s+[=<>+\-*/@#~!^%&|?]{1,4}\s+"
    r"[a-z][a-z0-9_ ]*(?:\[\])?$"
)


def classify_repository_bounded_symbol(
    raw: bytes, *, target_sql: bytes, artifact: bytes
) -> str:
    try:
        return prior.classify_undefined_symbol(raw)
    except RuntimeError:
        pass

    admitted_calls = {
        value.decode("ascii")
        for value in CALL_NAME.findall(target_sql + b"\n" + artifact)
    }
    function_matches = {
        value.decode("ascii") for value in prior.UNDEFINED_FUNCTION_PATTERN.findall(raw)
    }
    function_matches = {
        value
        for value in function_matches
        if value in admitted_calls
        or any(call.endswith("." + value) for call in admitted_calls)
    }
    operator_matches = {
        " ".join(value.decode("ascii").lower().split())
        for value in prior.UNDEFINED_OPERATOR_PATTERN.findall(raw)
    }
    operator_matches = {
        value for value in operator_matches if SAFE_TYPE_OPERATOR.fullmatch(value)
    }
    classified = {
        *("repository_function::" + value for value in function_matches),
        *("postgresql_operator::" + value for value in operator_matches),
    }
    if len(classified) != 1:
        raise RuntimeError("single_repository_bounded_symbol_missing")
    return next(iter(classified))


def diagnose() -> dict[str, Any]:
    contract, _, _, artifact = behavior._validate_contract()  # noqa: SLF001
    target_sql = behavior.render_scenario_sql(contract, "BTR-E02")
    runner = prior.UndefinedSymbolDiagnosticRunner(target_sql)
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
        raise RuntimeError("failure_025_undefined_symbol_diagnosis_not_closed")
    if runner.target_result is None or runner.resolution is None:
        raise RuntimeError("target_scenario_result_missing")

    resolution = dict(runner.resolution)
    if resolution.pop(EXPECTED_REPAIRED_ABSENCE, None) is not False:
        raise RuntimeError("repaired_predecessor_signature_unexpectedly_resolved")
    if not all(resolution.values()):
        raise RuntimeError("required_symbol_resolution_changed")

    raw = runner.target_result.stdout + b"\n" + runner.target_result.stderr
    raw_symbol = classify_repository_bounded_symbol(
        raw, target_sql=target_sql, artifact=artifact
    )
    if raw_symbol == EXPECTED_REPAIRED_ABSENCE:
        raise RuntimeError("repaired_predecessor_signature_still_executed")
    return {
        "schema_version": "emr4.raisa-context-fabric-durability-failure-025-undefined-symbol-diagnosis.v1",
        "status": "undefined_symbol_diagnosis_complete_cleanup_verified",
        "parent_failure": {
            "run_sequence": 25,
            "internal_attempt_id": PARENT_ATTEMPT_ID,
            "evidence_sha256": PARENT_EVIDENCE_SHA256,
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
            "required_resolution": resolution,
            "known_absent_but_not_executed": EXPECTED_REPAIRED_ABSENCE,
            "raw_message_symbol_id": raw_symbol,
        },
        "authority_boundary": "provider_free_authored_synthetic_disposable_postgresql_diagnosis_only_no_product_provider_command_deployment_or_protected_ref_authority",
    }


def main() -> int:
    print(json.dumps(diagnose(), sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
