from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PARENT_SOURCE = "656da9851f113c7ab639fc7634307c7be4a32cd6"
BEHAVIOR_CONTRACT_PATH = (
    "orchestration/continuity/"
    "raisa-provider-free-disposable-postgresql-durability-behavior-transaction-rehearsal/"
    "behavior-transaction-rehearsal-contract.json"
)
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
    "provider-free-behavior-transaction-failure-evidence-043.json"
)
OUTPUT_PATH = ROOT / (
    "orchestration/continuity/"
    "raisa-provider-free-disposable-postgresql-durability-behavior-transaction-rehearsal/"
    "provider-free-behavior-transaction-diagnosis-evidence-043.json"
)
FAILURE_SHA256 = "00805d8b31ba445523a9a3e82581e07a4232873164ba49961ae5913f15617801"


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
        raise ValueError("failure 043 digest mismatch")
    failure = json.loads(failure_bytes)
    failure_detail = failure["environment"]["failure"]
    if failure_detail != {
        "code": "sqlstate_mismatch",
        "detail_digest": "sha256:8228d6cfa854202a230297ee9f6f58a46b8a1f5ff2a8a001620087b484f2f785",
        "sqlstate": "CF201",
        "stage": "scenario",
    }:
        raise ValueError("failure 043 shape mismatch")
    if hashlib.sha256(b"CF201").hexdigest() != failure_detail["detail_digest"][7:]:
        raise ValueError("failure 043 expected SQLSTATE digest mismatch")
    if not all(
        failure["cleanup"].get(key) is expected
        for key, expected in (("absence_verified", True), ("removed", True))
    ):
        raise ValueError("failure 043 cleanup mismatch")

    contract_bytes = _git_show(PARENT_SOURCE, BEHAVIOR_CONTRACT_PATH)
    contract = json.loads(contract_bytes)
    expected_rejection_scenarios = [
        row for row in contract["scenarios"] if row["expected_sqlstate"] is not None
    ]
    first_cf201 = next(
        row
        for row in expected_rejection_scenarios
        if row["expected_sqlstate"] == "CF201"
    )
    if first_cf201 != {
        "id": "BTR-E06",
        "category": "ENTRY_POINT",
        "principal": "context_observer",
        "action": "admit_valid_generation_missing_source_position",
        "transaction_shape": "one_read_committed_transaction",
        "expected_outcome": "ROLLBACK_EXPECTED_SQLSTATE",
        "expected_failure_id": "F_ADMISSION_SOURCE",
        "expected_sqlstate": "CF201",
        "readback": ["admission_counts_unchanged", "all_fabric_counts_unchanged"],
        "forbidden_effects": [
            "primary_admission",
            "conflict_admission",
            "source_synthesis",
        ],
    }:
        raise ValueError("BTR-E06 parent contract mismatch")

    harness_bytes = _git_show(PARENT_SOURCE, HARNESS_PATH)
    harness = harness_bytes.decode("utf-8")
    if (
        'raise BehaviorFailure("scenario", "sqlstate_mismatch", expected_sqlstate)'
        not in harness
    ):
        raise ValueError("parent mismatch evidence behavior changed")

    inert_bytes = _git_show(PARENT_SOURCE, INERT_SQL_PATH)
    inert = inert_bytes.decode("utf-8")
    source_select = inert.index(
        "INTO STRICT source FROM "
        "emr4_context_fabric.diary_context_observation_outbox_v1"
    )
    admission_end = inert.index(
        "\nCREATE FUNCTION emr4_context_fabric.apply_durability_transition_v1",
        source_select,
    )
    admission_tail = inert[source_select:admission_end]
    no_data = admission_tail.index("WHEN NO_DATA_FOUND THEN")
    cardinality_failure = admission_tail.index(
        "ERRCODE = 'CF004', MESSAGE = 'required_row_missing_or_ambiguous'",
        no_data,
    )
    digest_failure = admission_tail.index(
        "ERRCODE = 'CF201', MESSAGE = 'admission_source_mismatch'",
        cardinality_failure,
    )
    if not no_data < cardinality_failure < digest_failure:
        raise ValueError("rendered admission rejection order mismatch")

    return {
        "schema_version": (
            "emr4.raisa-context-fabric-durability-failure-043-"
            "missing-source-sqlstate-diagnosis.v1"
        ),
        "status": "behavior_expectation_to_rendered_missing_source_sqlstate_mismatch_proven",
        "authority_boundary": (
            "provider_free_repository_diagnosis_and_behavior_evidence_repair_only_"
            "no_database_body_product_provider_deployment_or_protected_ref_authority"
        ),
        "parent_failure": {
            "run_sequence": 43,
            "internal_attempt_id": failure["attempt_id"],
            "evidence_sha256": f"sha256:{FAILURE_SHA256}",
            "scenario_id": "BTR-E06",
            "failure_code": "sqlstate_mismatch",
            "expected_sqlstate": "CF201",
            "cleanup_absence_verified": True,
        },
        "diagnosis": {
            "scenario_recovered_as_first_expected_cf201_case": True,
            "scenario_action_is_missing_exact_outbox_position": True,
            "rendered_exact_source_select_maps_no_data_found_to_cf004": True,
            "rendered_cf201_is_later_packet_to_present_source_digest_assertion": True,
            "deterministic_observed_sqlstate_for_missing_row": "CF004",
            "actual_sqlstate_not_persisted_by_parent_harness": True,
            "behavior_contract_expected_failure_mismatch": True,
            "database_body_defect_indicated": False,
            "additional_container_runs": 0,
            "raw_postgresql_error_persisted": False,
        },
        "bounded_repair": {
            "btr_e06_expected_failure_id": "F_CARDINALITY",
            "btr_e06_expected_sqlstate": "CF004",
            "persist_scenario_and_expected_observed_sqlstates_on_future_mismatch": True,
            "database_body_contract_unchanged": True,
            "inert_sql_and_parse_evidence_unchanged": True,
            "scenario_population_and_order_unchanged": True,
            "fresh_exact_head_veto_before_characterization": True,
            "next_run_must_be_single_owned_disposable_attempt": True,
        },
        "parent_sources": {
            "commit": PARENT_SOURCE,
            "behavior_contract_sha256": f"sha256:{_sha256(contract_bytes)}",
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
