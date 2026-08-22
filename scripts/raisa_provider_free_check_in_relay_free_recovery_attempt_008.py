"""Fixed fail-closed adapter for check-in relay-free recovery attempt 008."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import subprocess
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from jsonschema import Draft202012Validator

from scripts import (
    raisa_provider_free_disposable_postgresql_default_off_check_in_relay_free_rollback_unknown_commit_recovery_rehearsal as accepted,
)


ROOT = Path(__file__).resolve().parents[1]
TOPIC = ROOT / (
    "orchestration/continuity/"
    "raisa-provider-free-check-in-relay-free-recovery-attempt-008"
)
ENVELOPE_SCHEMA_PATH = TOPIC / "attempt-008-execution-envelope.schema.json"
ENVELOPE_PATH = TOPIC / "attempt-008-execution-envelope.json"
ATTESTATION_PATH = TOPIC / "transaction-attestation.json"
EVIDENCE_PATH = TOPIC / "rehearsal-evidence.json"
FAILURE_PATH = TOPIC / "rehearsal-failure-evidence.json"
TERMINAL_PATHS = (ENVELOPE_PATH, ATTESTATION_PATH, EVIDENCE_PATH, FAILURE_PATH)

GIT_SOURCES = {
    "plan_source": "337ac16c8871dfedee455eeb13d1195aa5dbfc44",
    "attempt_007_terminal_source": "6657ee5061265d732096e9987f327d82feed800c",
    "diagnosis_closeout_source": "5d93380060f31bab21bddc9ffdd5580754eb4fc6",
    "repair_implementation_source": "8a82a8184cc66efbe31769eda88e299887f798bc",
    "repair_closeout_source": "a33a4ccc7619fcae5cdd45a48a2312ab0c0384a4",
    "verification_closeout_source": "d01ef2f3afe16ccdb9a8f2077d5e76688397adb6",
    "plan_admissibility_source": "bcdd7fc25f745ade62cb145ead73c4a1ad6f4e83",
    "protected_source": "2e34bdad732fdab32fbf778280b3d3c70d66d602",
}

BASE_TOPIC = ROOT / (
    "orchestration/continuity/"
    "raisa-provider-free-disposable-postgresql-default-off-check-in-relay-free-"
    "rollback-unknown-commit-recovery-rehearsal"
)
ATTEMPT_007_TOPIC = ROOT / (
    "orchestration/continuity/"
    "raisa-provider-free-check-in-relay-free-recovery-attempt-007"
)
REPAIR_TOPIC = ROOT / (
    "orchestration/continuity/"
    "raisa-provider-free-check-in-prospective-success-redaction-and-typed-"
    "cleanup-projection-conformance-repair"
)
VERIFICATION_TOPIC = ROOT / (
    "orchestration/continuity/"
    "ariadne-provider-free-verification-envelope-phase-and-runner-admission-"
    "repair"
)
DECISION_TOPIC = ROOT / (
    "orchestration/continuity/"
    "raisa-provider-free-read-only-check-in-attempt-008-plan-admissibility-"
    "decision"
)

HASH_BINDINGS = {
    "repaired_base_harness_sha256": (
        Path(accepted.__file__),
        "c4372d443206c2a39351667b6d599c6911d575059955e6c615358d379355ae78",
    ),
    "base_contract_sha256": (
        BASE_TOPIC / "contract.json",
        "bcad86a4607c12ef5a3f98394b6e65e03c7ff8be8b3d83de2ba39884ea63bbda",
    ),
    "transaction_attestation_schema_sha256": (
        BASE_TOPIC / "transaction-attestation.schema.json",
        "d2c186b0d30419e0459d93d92af1f84907125becdeb75c7e1890dce597d3e72c",
    ),
    "attempt_007_failure_sha256": (
        ATTEMPT_007_TOPIC / "rehearsal-failure-evidence.json",
        "86e5e1342eb54e062e35d73390ebceb141d097d03e180e4fe3c0ed64b465f422",
    ),
    "attempt_007_envelope_sha256": (
        ATTEMPT_007_TOPIC / "attempt-007-execution-envelope.json",
        "3338c58054dea96b3845827dacfe184889ee328e5a4463966464b560d0a2c2c5",
    ),
    "repair_contract_sha256": (
        REPAIR_TOPIC / "repair-contract.json",
        "662e055f9011aa5574127503b46dd3ca9c6c3113ce6dad3b6e3ca35728930658",
    ),
    "repair_evidence_sha256": (
        REPAIR_TOPIC / "repair-evidence.json",
        "47f422e7b8ad072c9f4912fe6269cfc85f44eb75808419182c75e19d41157eaa",
    ),
    "verification_envelope_evidence_sha256": (
        VERIFICATION_TOPIC / "evidence.json",
        "47e6fd567e773c69fd7867e30a56f69e0d9346f1f6216fd37aebbdbaec96aa0d",
    ),
    "plan_admissibility_evidence_sha256": (
        DECISION_TOPIC / "decision-evidence.json",
        "88a6763d325b9cf8801503daec12f6b53e21cb047419d47d904e0450fb5598dd",
    ),
}

PASS_RESULT = "raisa_provider_free_check_in_relay_free_recovery_attempt_008_pass"
HARD_CONDITIONS = tuple(f"P{number:02d}" for number in range(6, 15))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_json(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise accepted.RehearsalFailure("attempt_008_static", "bound_json_invalid")
    return value


def _git(*arguments: str) -> str:
    completed = subprocess.run(
        ["git", *arguments],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="strict",
    )
    if completed.returncode != 0:
        raise accepted.RehearsalFailure(
            "attempt_008_static", "git_binding_failed"
        )
    return completed.stdout.strip()


def _source_head() -> str:
    head = _git("rev-parse", "--verify", "HEAD^{commit}")
    if accepted.HEX40.fullmatch(head) is None:
        raise accepted.RehearsalFailure(
            "attempt_008_static", "source_head_invalid"
        )
    for source in GIT_SOURCES.values():
        if accepted.HEX40.fullmatch(source) is None:
            raise accepted.RehearsalFailure(
                "attempt_008_static", "source_binding_not_full_commit"
            )
        if _git("cat-file", "-t", source) != "commit":
            raise accepted.RehearsalFailure(
                "attempt_008_static", "source_binding_not_commit"
            )
        relation = subprocess.run(
            ["git", "merge-base", "--is-ancestor", source, head],
            cwd=ROOT,
            check=False,
            capture_output=True,
        )
        if relation.returncode != 0:
            raise accepted.RehearsalFailure(
                "attempt_008_static", "source_binding_not_ancestor"
            )
    return head


def _assert_terminal_namespace_empty(
    paths: tuple[Path, ...] = TERMINAL_PATHS,
) -> None:
    if any(path.exists() for path in paths):
        raise accepted.RehearsalFailure(
            "attempt_008_execution", "terminal_artifact_already_exists"
        )


@contextmanager
def _attempt_008_terminal_bindings() -> Iterator[None]:
    originals = (
        accepted.ATTESTATION_PATH,
        accepted.EVIDENCE_PATH,
        accepted.FAILURE_PATH,
    )
    accepted.ATTESTATION_PATH = ATTESTATION_PATH
    accepted.EVIDENCE_PATH = EVIDENCE_PATH
    accepted.FAILURE_PATH = FAILURE_PATH
    try:
        yield
    finally:
        (
            accepted.ATTESTATION_PATH,
            accepted.EVIDENCE_PATH,
            accepted.FAILURE_PATH,
        ) = originals


def _bindings_are_historical() -> bool:
    return (
        accepted.ATTESTATION_PATH == accepted.TOPIC / "transaction-attestation.json"
        and accepted.EVIDENCE_PATH == accepted.TOPIC / "rehearsal-evidence.json"
        and accepted.FAILURE_PATH == accepted.TOPIC / "rehearsal-failure-evidence.json"
    )


def _validate_accepted_controls() -> None:
    repair = _load_json(REPAIR_TOPIC / "repair-evidence.json")
    projection = repair.get("prospective_projection")
    terminal = repair.get("typed_terminal")
    if not isinstance(projection, dict) or not isinstance(terminal, dict):
        raise accepted.RehearsalFailure(
            "attempt_008_static", "repair_evidence_shape_invalid"
        )
    if projection != {
        "before_docker_capable_call": True,
        "hostile_attempted": 66,
        "hostile_rejected": 66,
        "path_count": 67,
        "redaction_status": "passed",
        "runtime_path_count": 67,
        "schema_status": "passed",
    }:
        raise accepted.RehearsalFailure(
            "attempt_008_static", "prospective_projection_control_invalid"
        )
    required_terminal = {
        "frozen_dataclass": True,
        "late_failure_escape_count": 0,
        "redaction_failure_cleanup": "cleanup_verified",
        "schema_failure_cleanup": "cleanup_verified",
        "success_cleanup": "cleanup_verified",
        "success_release_after_late_failure_count": 0,
        "wrapper_cleanup_projection": "cleanup_verified",
    }
    if any(terminal.get(key) != value for key, value in required_terminal.items()):
        raise accepted.RehearsalFailure(
            "attempt_008_static", "typed_terminal_control_invalid"
        )

    verification = _load_json(VERIFICATION_TOPIC / "evidence.json")
    if (
        verification.get("database_authority") != "closed"
        or verification.get("hostile_rejection_count") != 8
        or verification.get("subprocess_launch_count") != 0
        or verification.get("phase_partition", {}).get(
            "cross_phase_execution_count"
        )
        != 0
    ):
        raise accepted.RehearsalFailure(
            "attempt_008_static", "verification_envelope_control_invalid"
        )

    decision = _load_json(DECISION_TOPIC / "decision-evidence.json")
    if (
        decision.get("verdict") != "admissible_for_separate_plan_freeze"
        or decision.get("attempt_008", {}).get("ready_to_execute") is not False
        or decision.get("counts")
        != {
            "blocking_count": 0,
            "plan_required_count": 6,
            "preexecution_required_count": 3,
            "prerequisite_count": 14,
            "satisfied_count": 5,
        }
    ):
        raise accepted.RehearsalFailure(
            "attempt_008_static", "plan_admissibility_control_invalid"
        )


def _validate_envelope(value: dict[str, object]) -> None:
    schema = json.loads(ENVELOPE_SCHEMA_PATH.read_text(encoding="utf-8"))
    if list(Draft202012Validator(schema).iter_errors(value)):
        raise accepted.RehearsalFailure(
            "attempt_008_evidence", "execution_envelope_schema_invalid"
        )


def _example_envelope(source_head: str) -> dict[str, object]:
    return {
        "schema_version": (
            "emr4.check-in-relay-free-recovery-attempt-008.execution-envelope.v1"
        ),
        "result": "failed_closed",
        "attempt_id": "attempt-008",
        "source_head": source_head,
        **GIT_SOURCES,
        **{key: digest for key, (_, digest) in HASH_BINDINGS.items()},
        "hard_condition_ids": list(HARD_CONDITIONS),
        "prospective_projection_path_count": 67,
        "prospective_projection_hostile_rejection_count": 66,
        "occupied_execution_count": 1,
        "automatic_retry_count": 0,
        "resume_count": 0,
        "fallback_count": 0,
        "ambiguous_success_released": False,
        "ordinary_admission_release_count": 0,
        "product_record_count": 0,
        "terminal_artifact_kind": "rehearsal_failure_evidence",
        "terminal_artifact_sha256": "0" * 64,
        "transaction_attestation_sha256": None,
        "base_result": "failed_closed",
        "cleanup_status": "not_started",
        "finalized_cleanup_projection_preserved": False,
        "terminal_binding_restored": True,
    }


def static_check(*, require_empty_namespace: bool = True) -> dict[str, object]:
    source_head = _source_head()
    terminal_namespace_empty = not any(path.exists() for path in TERMINAL_PATHS)
    for code, (path, expected) in HASH_BINDINGS.items():
        if _sha256(path) != expected:
            raise accepted.RehearsalFailure(
                "attempt_008_static", f"{code}_mismatch"
            )
    if not _bindings_are_historical():
        raise accepted.RehearsalFailure(
            "attempt_008_static", "accepted_terminal_binding_not_historical"
        )
    if require_empty_namespace:
        _assert_terminal_namespace_empty()
    _validate_accepted_controls()
    base = accepted.static_check()
    example = _example_envelope(source_head)
    accepted._assert_redacted(example, forbidden_values=())
    _validate_envelope(example)
    return {
        "schema_version": "emr4.check-in-relay-free-recovery-attempt-008.static.v1",
        "status": "passed",
        "source_head": source_head,
        **GIT_SOURCES,
        **{key: digest for key, (_, digest) in HASH_BINDINGS.items()},
        "hard_condition_ids": list(HARD_CONDITIONS),
        "base_static_status": base["status"],
        "contract_mutations": base["contract_mutations"],
        "manifest_mutations": base["manifest_mutations"],
        "classifier_mutations": base["classifier_mutations"],
        "state_mutations": base["state_mutations"],
        "prospective_projection": base["prospective_projection"],
        "terminal_namespace_empty": terminal_namespace_empty,
    }


def _sanitized_failure(
    error: accepted.RehearsalFailure,
    cleanup: dict[str, object] | None = None,
) -> dict[str, object]:
    return accepted._failure_evidence(
        error,
        ["attempt_008_wrapper_failed_closed"],
        copy.deepcopy(cleanup or {"status": "not_started"}),
    )


def _write_failure_if_absent(
    error: accepted.RehearsalFailure,
    cleanup: dict[str, object] | None = None,
) -> dict[str, object]:
    if FAILURE_PATH.exists():
        return _load_json(FAILURE_PATH)
    failure = _sanitized_failure(error, cleanup)
    accepted._assert_redacted(failure, forbidden_values=())
    accepted._write_json(FAILURE_PATH, failure)
    return failure


def _build_execution_envelope(
    *,
    source_head: str,
    evidence: dict[str, object],
    terminal_path: Path,
    terminal_kind: str,
) -> dict[str, object]:
    base_result = str(evidence.get("result", "failed_closed"))
    passed = base_result == accepted.PASS_RESULT
    cleanup = evidence.get("cleanup", {})
    cleanup_status = (
        str(cleanup.get("status", "not_started"))
        if isinstance(cleanup, dict)
        else "not_started"
    )
    envelope: dict[str, object] = {
        **_example_envelope(source_head),
        "result": PASS_RESULT if passed else "failed_closed",
        "terminal_artifact_kind": terminal_kind,
        "terminal_artifact_sha256": _sha256(terminal_path),
        "transaction_attestation_sha256": (
            _sha256(ATTESTATION_PATH) if ATTESTATION_PATH.exists() else None
        ),
        "base_result": base_result,
        "cleanup_status": cleanup_status,
        "ordinary_admission_release_count": int(
            evidence.get("ordinary_admission_release_count", 0)
        ),
        "product_record_count": int(evidence.get("product_record_count", 0)),
        "finalized_cleanup_projection_preserved": cleanup_status
        in {"cleanup_verified", "cleanup_incomplete"},
        "terminal_binding_restored": _bindings_are_historical(),
    }
    accepted._assert_redacted(envelope, forbidden_values=())
    _validate_envelope(envelope)
    return envelope


def run_attempt() -> dict[str, object]:
    static = static_check()
    evidence: dict[str, object]
    try:
        with _attempt_008_terminal_bindings():
            evidence, _ = accepted.run_rehearsal()
    except accepted.RehearsalFailure as error:
        evidence = _write_failure_if_absent(error)
    except Exception:
        evidence = _write_failure_if_absent(
            accepted.RehearsalFailure(
                "attempt_008_execution", "unexpected_controller_failure"
            )
        )
    if not _bindings_are_historical():
        raise accepted.RehearsalFailure(
            "attempt_008_evidence", "terminal_binding_not_restored"
        )
    if EVIDENCE_PATH.exists():
        terminal_path = EVIDENCE_PATH
        terminal_kind = "rehearsal_evidence"
    elif FAILURE_PATH.exists():
        terminal_path = FAILURE_PATH
        terminal_kind = "rehearsal_failure_evidence"
    else:
        evidence = _write_failure_if_absent(
            accepted.RehearsalFailure(
                "attempt_008_evidence", "terminal_artifact_missing"
            )
        )
        terminal_path = FAILURE_PATH
        terminal_kind = "rehearsal_failure_evidence"
    envelope = _build_execution_envelope(
        source_head=str(static["source_head"]),
        evidence=evidence,
        terminal_path=terminal_path,
        terminal_kind=terminal_kind,
    )
    accepted._write_json(ENVELOPE_PATH, envelope)
    return envelope


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--execute", action="store_true")
    arguments = parser.parse_args(argv)
    try:
        result = static_check() if arguments.check else run_attempt()
    except accepted.RehearsalFailure as error:
        print(
            json.dumps(
                {"result": "failed_closed", "stage": error.stage, "code": error.code}
            )
        )
        return 1
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if arguments.check or result.get("result") == PASS_RESULT else 1


if __name__ == "__main__":
    raise SystemExit(main())
