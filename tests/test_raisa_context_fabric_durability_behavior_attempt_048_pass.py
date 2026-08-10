from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

import jsonschema


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_DIR = ROOT / (
    "orchestration/continuity/raisa-provider-free-disposable-postgresql-"
    "durability-behavior-transaction-rehearsal"
)
PASS_PATH = EVIDENCE_DIR / (
    "provider-free-behavior-transaction-evidence-admission-replay-recovery-pass.json"
)
SCHEMA_PATH = EVIDENCE_DIR / "provider-free-behavior-transaction-evidence.schema.json"
CONTRACT_PATH = EVIDENCE_DIR / "behavior-transaction-rehearsal-contract.json"


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_attempt_048_pass_is_sealed_schema_valid_and_complete() -> None:
    raw = PASS_PATH.read_bytes()
    evidence = json.loads(raw)
    contract = _read_json(CONTRACT_PATH)

    assert hashlib.sha256(raw).hexdigest() == (
        "26c6dec802e46dec055c1c42aecc97df9942180014fc9fa410f96e1305798200"
    )
    jsonschema.validate(evidence, _read_json(SCHEMA_PATH))
    assert evidence["result"] == (
        "raisa_provider_free_disposable_postgresql_"
        "durability_behavior_transaction_rehearsal_pass"
    )
    assert evidence["attempt_id"] == "3ef353ae4f6648e3c9d36404"
    assert evidence["scenario_reconciliation"] == {
        "expected": 20,
        "observed": 20,
        "passed": 20,
    }
    assert [row["scenario_id"] for row in evidence["scenarios"]] == contract[
        "scenario_order"
    ]
    assert all(row["passed"] is True for row in evidence["scenarios"])
    assert Counter(row["category"] for row in evidence["scenarios"]) == {
        "ENTRY_POINT": 6,
        "IDEMPOTENCY": 4,
        "RLS": 3,
        "TRIGGER": 4,
        "ROLLBACK": 3,
    }
    assert evidence["lifecycle"][-3:] == [
        "catalogue_reconciled_after_behavior",
        "cleanup_verified",
        "passed",
    ]


def test_attempt_048_pass_binds_exact_parents_and_repaired_scenarios() -> None:
    evidence = _read_json(PASS_PATH)
    scenarios = {row["scenario_id"]: row for row in evidence["scenarios"]}

    assert evidence["parent"] == {
        "artifact_sha256": (
            "sha256:dc475f71005a2b5a37de829e7f5e21be425dc970091e5b5567099cf2449142d7"
        ),
        "behavior_contract_sha256": (
            "sha256:43b25bd7509439f069643dcb0ae8e62e27002834fe9903d84e7478486b452615"
        ),
        "manifest_sha256": (
            "sha256:2013d4e7d13d10808c2e872ed8e689edc1639f7e97b1f96fa3559826130a7271"
        ),
        "prerequisite_sha256": (
            "sha256:313d283b4a53c08a34b65f7c932457010cc9317c87a3bfe6a1b9dc218ba220b7"
        ),
        "statement_count": 424,
    }
    assert scenarios["BTR-I02"]["transaction_shape"] == (
        "three_separate_read_committed_transactions_after_exact_position_two_projection"
    )
    assert scenarios["BTR-I02"]["readback_checks"] == {
        "one_conflict_admission": True,
        "one_primary_admission": True,
        "primary_unchanged": True,
        "same_conflict_identity_on_replay": True,
        "two_total_rows_for_locator": True,
    }
    assert scenarios["BTR-B03"]["observed_outcome"] == "ROLLBACK_INJECTED"
    assert scenarios["BTR-B03"]["observed_sqlstate"] == "P0001"
    assert scenarios["BTR-B03"]["transport"]["result_kind"] == "RECEIPT_APPLIED"
    assert scenarios["BTR-B03"]["readback_checks"] == {
        "audit_unchanged": True,
        "checkpoint_unchanged": True,
        "frames_unchanged": True,
        "lifecycle_unchanged": True,
        "obligations_unchanged": True,
        "primary_admission_retained": True,
        "receipt_absent": True,
        "watermarks_unchanged": True,
    }


def test_attempt_048_pass_proves_cleanup_and_retains_claim_boundary() -> None:
    evidence = _read_json(PASS_PATH)

    assert evidence["cleanup"] == {
        "absence_verified": True,
        "container_id": (
            "4bbb33f427d5b006aecc38e6a1901c61d5581a69ed825b24d6266948b26702a6"
        ),
        "removed": True,
        "status": "cleanup_verified",
    }
    assert evidence["environment"]["image"] == {
        "id": "sha256:64154d0babcb1741988719e703419af0382b19953706149f9872fbd0f438efa8",
        "pull_attempted": False,
        "reference": "postgres:16-bookworm",
    }
    assert evidence["environment"]["readiness"]["status"] == "stable"
    assert evidence["claim_boundary"] == (
        "selected_serial_entry_point_trigger_rls_idempotency_"
        "and_outer_rollback_behavior_only"
    )
