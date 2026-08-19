"""Fixed output adapter for one check-in relay-free recovery attempt 002."""

from __future__ import annotations

import argparse
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
    "raisa-provider-free-check-in-relay-free-recovery-attempt-002"
)
ENVELOPE_SCHEMA_PATH = TOPIC / "attempt-002-execution-envelope.schema.json"
ENVELOPE_PATH = TOPIC / "attempt-002-execution-envelope.json"
ATTESTATION_PATH = TOPIC / "transaction-attestation.json"
EVIDENCE_PATH = TOPIC / "rehearsal-evidence.json"
FAILURE_PATH = TOPIC / "rehearsal-failure-evidence.json"
TERMINAL_PATHS = (ENVELOPE_PATH, ATTESTATION_PATH, EVIDENCE_PATH, FAILURE_PATH)

PLAN_SOURCE = "85342f5e203c854090320481bef6a88e63ca565a"
LIFECYCLE_ADMISSION_REPAIR_SOURCE = "fc772085a02d7db790b938fb845ef4546156d31e"
ACCEPTED_HARNESS_SHA256 = (
    "5c60e6e4b0d554b3c323a932e8aa5a96943705e30a4d09afb2d6b8794a1503f4"
)
PREDECESSOR_FAILURE_PATH = accepted.TOPIC / "rehearsal-failure-evidence.json"
PREDECESSOR_FAILURE_SHA256 = (
    "5c38080aa27615ea1efad166d14a61605596130058498ea03c8b631bbeae3be2"
)
PREDECESSOR_CLEANUP_PATH = accepted.TOPIC / "attempt-001-cleanup-recovery.json"
PREDECESSOR_CLEANUP_SHA256 = (
    "a8920b0a294b43c8f67d0348bc6087b84921f8f8788ccd3f969913d95861c06a"
)
PASS_RESULT = "raisa_provider_free_check_in_relay_free_recovery_attempt_002_pass"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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
        raise accepted.RehearsalFailure("attempt_002_static", "git_binding_failed")
    return completed.stdout.strip()


def _source_head() -> str:
    head = _git("rev-parse", "HEAD")
    if accepted.HEX40.fullmatch(head) is None:
        raise accepted.RehearsalFailure("attempt_002_static", "source_head_invalid")
    for source in (PLAN_SOURCE, LIFECYCLE_ADMISSION_REPAIR_SOURCE):
        if _git("cat-file", "-t", source) != "commit":
            raise accepted.RehearsalFailure(
                "attempt_002_static", "source_binding_not_commit"
            )
        relation = subprocess.run(
            ["git", "merge-base", "--is-ancestor", source, head],
            cwd=ROOT,
            check=False,
            capture_output=True,
        )
        if relation.returncode != 0:
            raise accepted.RehearsalFailure(
                "attempt_002_static", "source_binding_not_ancestor"
            )
    return head


def _assert_terminal_namespace_empty(
    paths: tuple[Path, ...] = TERMINAL_PATHS,
) -> None:
    if any(path.exists() for path in paths):
        raise accepted.RehearsalFailure(
            "attempt_002_execution", "terminal_artifact_already_exists"
        )


@contextmanager
def _attempt_002_terminal_bindings() -> Iterator[None]:
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


def _validate_envelope(value: dict[str, object]) -> None:
    errors = list(
        Draft202012Validator(json.loads(ENVELOPE_SCHEMA_PATH.read_text("utf-8"))).iter_errors(
            value
        )
    )
    if errors:
        raise accepted.RehearsalFailure(
            "attempt_002_evidence", "execution_envelope_schema_invalid"
        )


def _example_envelope(source_head: str) -> dict[str, object]:
    return {
        "schema_version": (
            "emr4.check-in-relay-free-recovery-attempt-002.execution-envelope.v1"
        ),
        "result": "failed_closed",
        "attempt_id": "attempt-002",
        "source_head": source_head,
        "plan_source": PLAN_SOURCE,
        "lifecycle_admission_repair_source": LIFECYCLE_ADMISSION_REPAIR_SOURCE,
        "accepted_harness_sha256": ACCEPTED_HARNESS_SHA256,
        "predecessor_failure_sha256": PREDECESSOR_FAILURE_SHA256,
        "predecessor_cleanup_sha256": PREDECESSOR_CLEANUP_SHA256,
        "occupied_execution_count": 1,
        "automatic_retry_count": 0,
        "ambiguous_success_released": False,
        "ordinary_admission_release_count": 0,
        "product_record_count": 0,
        "terminal_artifact_kind": "rehearsal_failure_evidence",
        "terminal_artifact_sha256": "0" * 64,
        "transaction_attestation_sha256": None,
        "base_result": "failed_closed",
        "cleanup_status": "not_started",
        "terminal_binding_restored": True,
    }


def static_check(*, require_empty_namespace: bool = True) -> dict[str, object]:
    source_head = _source_head()
    if _sha256(accepted.__file__ and Path(accepted.__file__)) != ACCEPTED_HARNESS_SHA256:
        raise accepted.RehearsalFailure(
            "attempt_002_static", "accepted_harness_digest_mismatch"
        )
    if _sha256(PREDECESSOR_FAILURE_PATH) != PREDECESSOR_FAILURE_SHA256:
        raise accepted.RehearsalFailure(
            "attempt_002_static", "predecessor_failure_digest_mismatch"
        )
    if _sha256(PREDECESSOR_CLEANUP_PATH) != PREDECESSOR_CLEANUP_SHA256:
        raise accepted.RehearsalFailure(
            "attempt_002_static", "predecessor_cleanup_digest_mismatch"
        )
    if not _bindings_are_historical():
        raise accepted.RehearsalFailure(
            "attempt_002_static", "accepted_terminal_binding_not_historical"
        )
    if require_empty_namespace:
        _assert_terminal_namespace_empty()
    base = accepted.static_check()
    _validate_envelope(_example_envelope(source_head))
    return {
        "schema_version": "emr4.check-in-relay-free-recovery-attempt-002.static.v1",
        "status": "passed",
        "source_head": source_head,
        "plan_source": PLAN_SOURCE,
        "lifecycle_admission_repair_source": LIFECYCLE_ADMISSION_REPAIR_SOURCE,
        "accepted_harness_sha256": ACCEPTED_HARNESS_SHA256,
        "predecessor_failure_sha256": PREDECESSOR_FAILURE_SHA256,
        "predecessor_cleanup_sha256": PREDECESSOR_CLEANUP_SHA256,
        "base_static_status": base["status"],
        "contract_mutations": base["contract_mutations"],
        "manifest_mutations": base["manifest_mutations"],
        "classifier_mutations": base["classifier_mutations"],
        "state_mutations": base["state_mutations"],
        "terminal_namespace_empty": True,
    }


def _sanitized_failure(error: accepted.RehearsalFailure) -> dict[str, object]:
    return accepted._failure_evidence(
        error,
        ["attempt_002_wrapper_failed_closed"],
        {"status": "not_started"},
    )


def _write_failure_if_absent(error: accepted.RehearsalFailure) -> dict[str, object]:
    if FAILURE_PATH.exists():
        return json.loads(FAILURE_PATH.read_text(encoding="utf-8"))
    failure = _sanitized_failure(error)
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
        "schema_version": (
            "emr4.check-in-relay-free-recovery-attempt-002.execution-envelope.v1"
        ),
        "result": PASS_RESULT if passed else "failed_closed",
        "attempt_id": "attempt-002",
        "source_head": source_head,
        "plan_source": PLAN_SOURCE,
        "lifecycle_admission_repair_source": LIFECYCLE_ADMISSION_REPAIR_SOURCE,
        "accepted_harness_sha256": ACCEPTED_HARNESS_SHA256,
        "predecessor_failure_sha256": PREDECESSOR_FAILURE_SHA256,
        "predecessor_cleanup_sha256": PREDECESSOR_CLEANUP_SHA256,
        "occupied_execution_count": 1,
        "automatic_retry_count": 0,
        "ambiguous_success_released": False,
        "ordinary_admission_release_count": int(
            evidence.get("ordinary_admission_release_count", 0)
        ),
        "product_record_count": int(evidence.get("product_record_count", 0)),
        "terminal_artifact_kind": terminal_kind,
        "terminal_artifact_sha256": _sha256(terminal_path),
        "transaction_attestation_sha256": (
            _sha256(ATTESTATION_PATH) if ATTESTATION_PATH.exists() else None
        ),
        "base_result": base_result,
        "cleanup_status": cleanup_status,
        "terminal_binding_restored": _bindings_are_historical(),
    }
    accepted._assert_redacted(envelope, forbidden_values=())
    _validate_envelope(envelope)
    return envelope


def run_attempt() -> dict[str, object]:
    static = static_check()
    evidence: dict[str, object]
    try:
        with _attempt_002_terminal_bindings():
            evidence, _ = accepted.run_rehearsal()
    except accepted.RehearsalFailure as error:
        evidence = _write_failure_if_absent(error)
    except Exception:
        evidence = _write_failure_if_absent(
            accepted.RehearsalFailure(
                "attempt_002_execution", "unexpected_controller_failure"
            )
        )
    if not _bindings_are_historical():
        raise accepted.RehearsalFailure(
            "attempt_002_evidence", "terminal_binding_not_restored"
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
                "attempt_002_evidence", "terminal_artifact_missing"
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
