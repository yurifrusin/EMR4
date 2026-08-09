"""Reproduce behavior failure 022 and release only allowlisted coordinates."""

from __future__ import annotations

import hashlib
import json
from typing import Any

from scripts import (
    raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal as behavior,
)
from scripts import (
    raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal as parent,
)


ALLOWED_FUNCTIONS = frozenset(
    {
        "cf_fence_stream_head_v1",
        "register_observer_generation_v1",
    }
)


class CapturingRunner:
    """Delegate every call while retaining only the exact BTR-E01 result in memory."""

    def __init__(self, target_sql: bytes) -> None:
        self._target_sql = target_sql
        self.target_result: parent.ProcessResult | None = None

    def __call__(
        self,
        argv: list[str],
        stdin: bytes | None,
        timeout: float,
        cap: int,
    ) -> parent.ProcessResult:
        result = parent._subprocess_runner(argv, stdin, timeout, cap)  # noqa: SLF001
        if stdin == self._target_sql:
            if self.target_result is not None:
                raise RuntimeError("duplicate_target_scenario_execution")
            self.target_result = result
        return result


def diagnose() -> dict[str, Any]:
    contract, _, _, _ = behavior._validate_contract()  # noqa: SLF001
    target_sql = behavior.render_scenario_sql(contract, "BTR-E01")
    runner = CapturingRunner(target_sql)
    evidence = behavior.run_rehearsal(runner=runner)
    failure = evidence.get("environment", {}).get("failure", {})
    cleanup = evidence.get("cleanup", {})
    if not (
        evidence.get("result") == "rehearsal_failed"
        and failure.get("scenario_id") == "BTR-E01"
        and failure.get("sqlstate") == "CF105"
        and evidence.get("scenario_reconciliation", {}).get("observed") == 0
        and cleanup.get("status") == "cleanup_verified"
        and cleanup.get("absence_verified") is True
    ):
        raise RuntimeError("failure_022_not_reproduced_exactly")
    if runner.target_result is None:
        raise RuntimeError("target_scenario_result_missing")

    raw = runner.target_result.stdout + b"\n" + runner.target_result.stderr
    matches = sorted(
        {
            (function_raw.decode("ascii"), int(line_raw.decode("ascii")))
            for function_raw, line_raw in behavior.PSQL_PLPGSQL_CONTEXT_LINE.findall(
                raw
            )
            if function_raw.decode("ascii") in ALLOWED_FUNCTIONS
        }
    )
    if not matches:
        raise RuntimeError("allowlisted_plpgsql_coordinate_missing")
    return {
        "schema_version": "emr4.raisa-context-fabric-durability-failure-022-diagnosis.v1",
        "status": "diagnosis_reproduced_cleanup_verified",
        "parent_failure": {
            "run_sequence": 22,
            "internal_attempt_id": "c9288fb197ed96d136f6022b",
            "evidence_sha256": "sha256:6ae6ef74c6a44c8f022f54f54bbc31d6a867a6f9953b7ee52ca34e68bf71f224",
        },
        "diagnosis_runtime": {
            "internal_attempt_id": evidence["attempt_id"],
            "raw_diagnostic_sha256": "sha256:" + hashlib.sha256(raw).hexdigest(),
            "raw_error_persisted": False,
            "container_id": cleanup["container_id"],
            "cleanup_absence_verified": True,
        },
        "failure": {
            "scenario_id": "BTR-E01",
            "sqlstate": "CF105",
            "coordinates": [
                {
                    "function_id": f"emr4_context_fabric.{function_name}",
                    "function_line": function_line,
                }
                for function_name, function_line in matches
            ],
        },
        "authority_boundary": "provider_free_authored_synthetic_disposable_postgresql_diagnosis_only_no_product_provider_command_deployment_or_protected_ref_authority",
    }


def main() -> int:
    print(json.dumps(diagnose(), sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
