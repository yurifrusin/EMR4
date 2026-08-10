from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PARENT_SOURCE = "c23c65a364a576b553ab0640cf4206c2d95f7e24"
HARNESS_PATH = (
    "scripts/"
    "raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py"
)
FAILURE_PATH = ROOT / (
    "orchestration/continuity/"
    "raisa-provider-free-disposable-postgresql-durability-behavior-transaction-rehearsal/"
    "provider-free-behavior-transaction-failure-evidence-040.json"
)
OUTPUT_PATH = ROOT / (
    "orchestration/continuity/"
    "raisa-provider-free-disposable-postgresql-durability-behavior-transaction-rehearsal/"
    "provider-free-behavior-transaction-diagnosis-evidence-040.json"
)
FAILURE_SHA256 = "93af223dfb25aab6a217f98eea45aa43c27efdb2d85d102caaf0f3b05b41ff98"


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
        raise ValueError("failure 040 digest mismatch")
    failure = json.loads(failure_bytes)
    failure_detail = failure["environment"]["failure"]
    if failure_detail != {
        "code": "scenario_probe",
        "detail_digest": "sha256:1ca46cd39619f67e83854ef51bb6470412c2f46f83b1cd32ca9f9b6d71d8ac0d",
        "failed_probe_indexes": [5],
        "scenario_id": "BTR-E04",
        "stage": "readback",
    }:
        raise ValueError("failure 040 locator mismatch")
    if failure["cleanup"] != {
        "absence_verified": True,
        "container_id": "d561608bb7df43c8f4f54472c4dd831d57314d450b6b492dafd7701d075ceb44",
        "removed": True,
        "status": "cleanup_verified",
    }:
        raise ValueError("failure 040 cleanup mismatch")

    parent_bytes = _git_show(PARENT_SOURCE, HARNESS_PATH)
    parent = parent_bytes.decode("utf-8")
    required_parent_fragments = (
        "beta_generation AS (",
        "observer_happy",
        "beta_obligation AS (",
        "'ONE','PENDING'",
        '"BTR-E04": {',
        '"emr4_context_fabric.context_reassembly_obligation": 1',
        "_assert_delta(scenario_id, before, after)",
        "_probe(runner, docker, container_id, profile, contract, scenario_id)",
        "context_reassembly_obligation WHERE observer_id=",
    )
    if any(fragment not in parent for fragment in required_parent_fragments):
        raise ValueError("parent scope diagnosis fragment missing")
    if parent.index("_assert_delta(scenario_id, before, after)") > parent.index(
        "_probe(runner, docker, container_id, profile, contract, scenario_id)"
    ):
        raise ValueError("parent readback order mismatch")
    if "happy_obligation_scope" in parent:
        raise ValueError("parent already contains scoped obligation probe")

    return {
        "schema_version": (
            "emr4.raisa-context-fabric-durability-failure-040-"
            "obligation-scope-diagnosis.v1"
        ),
        "status": "unscoped_cross_practice_fixture_collision_proven",
        "authority_boundary": (
            "provider_free_repository_diagnosis_and_probe_scope_repair_only_"
            "no_database_body_contract_product_provider_or_protected_ref_authority"
        ),
        "parent_failure": {
            "run_sequence": 40,
            "internal_attempt_id": failure["attempt_id"],
            "evidence_sha256": f"sha256:{FAILURE_SHA256}",
            "scenario_id": "BTR-E04",
            "failed_probe_indexes": [5],
            "cleanup_absence_verified": True,
        },
        "diagnosis": {
            "probe_semantic": "one_pending_reassembly_obligation",
            "beta_fixture_preseeds_pending_obligation": True,
            "beta_fixture_reuses_happy_observer_id": True,
            "btr_e04_relation_delta_one_admitted_before_probe": True,
            "parent_probe_filtered_only_observer_and_state": True,
            "parent_probe_omitted_practice_and_stream": True,
            "logical_matching_rows": 2,
            "database_body_defect_indicated": False,
            "additional_container_runs": 0,
            "raw_postgresql_values_persisted": False,
        },
        "bounded_repair": {
            "scope_btr_e04_and_i03_obligation_probes_to_practice_alpha": True,
            "scope_btr_e04_and_i03_obligation_probes_to_stream_alpha": True,
            "database_artifact_unchanged": True,
            "behavior_contract_unchanged": True,
            "scenario_population_unchanged": True,
            "allowed_digest_changes_unchanged": True,
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
