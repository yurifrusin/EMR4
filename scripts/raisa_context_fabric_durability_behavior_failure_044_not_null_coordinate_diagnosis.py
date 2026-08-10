from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PARENT_SOURCE = "70545fd2012ec8f92ff9d89658e455e8ff3c5b07"
HARNESS_PATH = (
    "scripts/"
    "raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py"
)
INERT_SQL_PATH = (
    "orchestration/continuity/"
    "raisa-provider-free-unmounted-durability-inert-ddl-rehearsal/"
    "durability-schema.sql.inert"
)
FAILURE_PATH = ROOT / (
    "orchestration/continuity/"
    "raisa-provider-free-disposable-postgresql-durability-behavior-transaction-rehearsal/"
    "provider-free-behavior-transaction-failure-evidence-044.json"
)
OUTPUT_PATH = ROOT / (
    "orchestration/continuity/"
    "raisa-provider-free-disposable-postgresql-durability-behavior-transaction-rehearsal/"
    "provider-free-behavior-transaction-diagnosis-evidence-044.json"
)
FAILURE_SHA256 = "0bacbe855a818c4dbb6bfa5c95ffbdb4fd5a91ac9ace431153669d17cb277345"
EXPECTED_NOT_NULL_COLUMNS = [
    "practice_id",
    "source_contract_id",
    "stream_id",
    "stream_epoch",
    "observer_id",
    "observer_generation",
    "source_position",
    "entry_kind",
    "observer_binding_revision",
    "key_id",
    "source_membership_digest",
    "admission_digest",
    "admitted_at",
]


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _git_show(source: str, path: str) -> bytes:
    completed = subprocess.run(
        ["git", "show", f"{source}:{path}"],
        cwd=ROOT,
        check=False,
        capture_output=True,
    )
    if completed.returncode != 0 or completed.stderr:
        raise RuntimeError(f"parent source unavailable: {path}")
    return completed.stdout


def build_evidence() -> dict[str, Any]:
    failure_bytes = FAILURE_PATH.read_bytes()
    if _sha256(failure_bytes) != FAILURE_SHA256:
        raise ValueError("failure 044 digest mismatch")
    failure = json.loads(failure_bytes)
    failure_detail = failure["environment"]["failure"]
    expected_detail = {
        "code": "unexpected_rejection",
        "detail_digest": (
            "sha256:c80c12f384c74aa94b32d5ad2e4ca557827a53d2f4a9586ca6ac953d55d40f48"
        ),
        "scenario_id": "BTR-I02",
        "sqlstate": "23502",
        "stage": "scenario",
    }
    if failure_detail != expected_detail:
        raise ValueError("failure 044 shape mismatch")
    bounded_detail = {"scenario_id": "BTR-I02", "sqlstate": "23502"}
    bounded_digest = hashlib.sha256(
        json.dumps(bounded_detail, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    if bounded_digest != failure_detail["detail_digest"][7:]:
        raise ValueError("failure 044 bounded detail digest mismatch")
    if not all(
        failure["cleanup"].get(key) is expected
        for key, expected in (("absence_verified", True), ("removed", True))
    ):
        raise ValueError("failure 044 cleanup mismatch")

    harness_bytes = _git_show(PARENT_SOURCE, HARNESS_PATH)
    harness = harness_bytes.decode("utf-8")
    if "PSQL_NOT_NULL_LINE = re.compile(" not in harness:
        raise ValueError("safe not-null header parser absent")
    if "def _safe_bootstrap_failure_metadata(" not in harness:
        raise ValueError("bootstrap not-null projection absent")
    if "def _safe_scenario_failure_metadata(" in harness:
        raise ValueError("parent already projects scenario not-null coordinate")
    unexpected_branch = harness.index("if expected_sqlstate is None:")
    mismatch_branch = harness.index(
        'raise BehaviorFailure("scenario", "sqlstate_mismatch"', unexpected_branch
    )
    unexpected_source = harness[unexpected_branch:mismatch_branch]
    if "_safe_bootstrap_failure_metadata" in unexpected_source:
        raise ValueError("parent scenario branch unexpectedly projects coordinate")

    inert_bytes = _git_show(PARENT_SOURCE, INERT_SQL_PATH)
    inert = inert_bytes.decode("utf-8")
    table_start = inert.index(
        "CREATE TABLE emr4_context_fabric.context_proofread_observation_admission ("
    )
    table_end = inert.index("\n);", table_start)
    table_block = inert[table_start:table_end]
    observed_not_null_columns = re.findall(
        r"^    ([a-z][a-z0-9_]*) [^\r\n]+ NOT NULL,$", table_block, re.MULTILINE
    )
    observed_not_null_columns.extend(
        re.findall(
            r"^    ([a-z][a-z0-9_]*) [^\r\n]+ NOT NULL$", table_block, re.MULTILINE
        )
    )
    if observed_not_null_columns != EXPECTED_NOT_NULL_COLUMNS:
        raise ValueError("admission not-null column set drift")

    return {
        "schema_version": (
            "emr4.raisa-context-fabric-durability-failure-044-"
            "not-null-coordinate-diagnosis.v1"
        ),
        "status": "scenario_not_null_coordinate_telemetry_gap_proven",
        "authority_boundary": (
            "provider_free_repository_diagnosis_and_bounded_failure_telemetry_only_"
            "no_database_body_product_provider_deployment_or_protected_ref_authority"
        ),
        "parent_failure": {
            "run_sequence": 44,
            "internal_attempt_id": failure["attempt_id"],
            "evidence_sha256": f"sha256:{FAILURE_SHA256}",
            "scenario_id": "BTR-I02",
            "failure_code": "unexpected_rejection",
            "observed_sqlstate": "23502",
            "cleanup_absence_verified": True,
        },
        "diagnosis": {
            "postgresql_failure_class_is_not_null_violation": True,
            "safe_not_null_header_parser_already_exists": True,
            "parent_parser_is_used_only_for_bootstrap_failures": True,
            "scenario_failure_coordinate_projection_exists": False,
            "persisted_relation_or_column_exists": False,
            "admission_not_null_candidate_columns": EXPECTED_NOT_NULL_COLUMNS,
            "actual_null_column_determined": False,
            "database_body_defect_claimed": False,
            "additional_container_runs": 0,
            "raw_postgresql_error_persisted": False,
        },
        "bounded_repair": {
            "reuse_existing_header_and_diagnostic_parsers": True,
            "scenario_relation_allowlist": [
                "emr4_context_fabric.context_proofread_observation_admission"
            ],
            "scenario_column_allowlist": EXPECTED_NOT_NULL_COLUMNS,
            "persist_only_sqlstate_coordinate_status_relation_and_column": True,
            "unlisted_relation_or_column_fails_closed": True,
            "raw_stderr_remains_digest_only": True,
            "database_body_contract_unchanged": True,
            "inert_sql_and_parse_evidence_unchanged": True,
            "behavior_contract_and_scenarios_unchanged": True,
            "fresh_exact_head_veto_before_new_attempt": True,
        },
        "parent_sources": {
            "commit": PARENT_SOURCE,
            "harness_sha256": f"sha256:{_sha256(harness_bytes)}",
            "inert_sql_sha256": f"sha256:{_sha256(inert_bytes)}",
        },
    }


def write_json_lf(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH)
    args = parser.parse_args()
    evidence = build_evidence()
    write_json_lf(args.output, evidence)
    print(json.dumps(evidence, separators=(",", ":"), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
