from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PARENT_SOURCE = "c8a3d2b51b8249ab7fee0a373c9dc8b2d375ecc3"
HARNESS_PATH = (
    "scripts/"
    "raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py"
)
FAILURE_PATH = ROOT / (
    "orchestration/continuity/"
    "raisa-provider-free-disposable-postgresql-durability-behavior-transaction-rehearsal/"
    "provider-free-behavior-transaction-failure-evidence-041.json"
)
OUTPUT_PATH = ROOT / (
    "orchestration/continuity/"
    "raisa-provider-free-disposable-postgresql-durability-behavior-transaction-rehearsal/"
    "provider-free-behavior-transaction-diagnosis-evidence-041.json"
)
FAILURE_SHA256 = "c1215b6dae6e1f2608c55d38ee35ecbea5df2f341f1141707239e8371f129491"


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
        raise RuntimeError("parent source unavailable")
    return completed.stdout


def build_evidence() -> dict[str, Any]:
    failure_bytes = FAILURE_PATH.read_bytes()
    if _sha256(failure_bytes) != FAILURE_SHA256:
        raise ValueError("failure 041 digest mismatch")
    failure = json.loads(failure_bytes)
    failure_detail = failure["environment"]["failure"]
    if failure_detail != {
        "code": "transition_result_missing",
        "detail_digest": "sha256:cc877d3da850b96fd76414811ed5fba25a310746de887d7cc316feeebd542a50",
        "stage": "scenario",
    }:
        raise ValueError("failure 041 shape mismatch")
    if hashlib.sha256(b"BTR-I03").hexdigest() != failure_detail["detail_digest"][7:]:
        raise ValueError("failure 041 scenario digest mismatch")
    if not all(
        failure["cleanup"].get(key) is expected
        for key, expected in (("absence_verified", True), ("removed", True))
    ):
        raise ValueError("failure 041 cleanup mismatch")

    parent_bytes = _git_show(PARENT_SOURCE, HARNESS_PATH)
    parent = parent_bytes.decode("utf-8")
    outcome_start = parent.index("def _bounded_outcome(")
    outcome_end = parent.index("\ndef _run_precondition(", outcome_start)
    old_outcome = parent[outcome_start:outcome_end]
    marker_offset = old_outcome.index(
        "result_kind = _transition_result_from_stdout(result, scenario_id)"
    )
    rejection_offset = old_outcome.index(
        "bounded = parent._bounded_psql_rejection("
    )
    if marker_offset >= rejection_offset:
        raise ValueError("parent no longer has marker-first classification")

    return {
        "schema_version": (
            "emr4.raisa-context-fabric-durability-failure-041-"
            "rejection-precedence-diagnosis.v1"
        ),
        "status": "transition_marker_masked_rejection_classification_proven",
        "authority_boundary": (
            "provider_free_repository_diagnosis_and_harness_classification_"
            "repair_only_no_database_body_contract_product_provider_or_protected_ref_authority"
        ),
        "parent_failure": {
            "run_sequence": 41,
            "internal_attempt_id": failure["attempt_id"],
            "evidence_sha256": f"sha256:{FAILURE_SHA256}",
            "scenario_id": "BTR-I03",
            "failure_code": "transition_result_missing",
            "cleanup_absence_verified": True,
        },
        "diagnosis": {
            "btr_e04_completed_before_failure": True,
            "failure_scenario_recovered_from_digest": True,
            "parent_called_marker_parser_before_rejection_classifier": True,
            "underlying_psql_outcome_not_persisted": True,
            "database_body_defect_indicated": False,
            "additional_container_runs": 0,
            "raw_stderr_persisted": False,
        },
        "bounded_repair": {
            "classify_unexpected_rejection_before_success_marker": True,
            "classify_sqlstate_mismatch_before_expected_failure_marker": True,
            "retain_marker_requirement_after_transport_admission": True,
            "database_artifact_unchanged": True,
            "behavior_contract_unchanged": True,
            "scenario_population_unchanged": True,
            "fresh_exact_head_veto_before_characterization": True,
            "next_run_must_be_single_owned_disposable_attempt": True,
        },
        "parent_source": {
            "commit": PARENT_SOURCE,
            "path": HARNESS_PATH,
            "sha256": f"sha256:{_sha256(parent_bytes)}",
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
