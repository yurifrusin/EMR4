"""Fixed fail-closed adapter for check-in relay-free recovery attempt 007."""

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
    "raisa-provider-free-check-in-relay-free-recovery-attempt-007"
)
ENVELOPE_SCHEMA_PATH = TOPIC / "attempt-007-execution-envelope.schema.json"
ENVELOPE_PATH = TOPIC / "attempt-007-execution-envelope.json"
ATTESTATION_PATH = TOPIC / "transaction-attestation.json"
EVIDENCE_PATH = TOPIC / "rehearsal-evidence.json"
FAILURE_PATH = TOPIC / "rehearsal-failure-evidence.json"
TERMINAL_PATHS = (ENVELOPE_PATH, ATTESTATION_PATH, EVIDENCE_PATH, FAILURE_PATH)

GIT_SOURCES = {
    "plan_source": "e3da4d993c8daec9973aed59ca4052e8a8429747",
    "attempt_006_execution_source": "a9567be36c82bc6d2eebc2488b48cd8bfb9f8d23",
    "attempt_006_closeout_source": "53760513c42a380904136eb4ef2f5ffda397e820",
    "start_option_repair_implementation_source": (
        "022d780726c74cb285d5b626cd004821b4e5ff47"
    ),
    "start_option_repair_reviewed_source": (
        "8814d4b5d62885f8f8eca4cf02fe5a49ccdc013b"
    ),
    "start_option_repair_closeout_source": "f30b82ea0b80bdef2fa8d63549ba78d39d14e24d",
    "protected_source": "2e34bdad732fdab32fbf778280b3d3c70d66d602",
}

BASE_TOPIC = ROOT / (
    "orchestration/continuity/"
    "raisa-provider-free-disposable-postgresql-default-off-check-in-relay-free-"
    "rollback-unknown-commit-recovery-rehearsal"
)
ATTEMPT_006_TOPIC = ROOT / (
    "orchestration/continuity/"
    "raisa-provider-free-check-in-relay-free-recovery-attempt-006"
)
START_ARGV_REPAIR_TOPIC = ROOT / (
    "orchestration/continuity/"
    "raisa-provider-free-check-in-server-start-argv-sig-proxy-removal-"
    "conformance-repair"
)

HASH_BINDINGS = {
    "repaired_harness_sha256": (
        Path(accepted.__file__),
        "1b7ec51cfd97fa6a54398ab0587acf79d3b0b8d34fa5609a2bad2abe17e91c16",
    ),
    "contract_sha256": (
        BASE_TOPIC / "contract.json",
        "bed2a89a3814ba9e9ac006d0fdb0c68d204fec53d8c21b6128190605b6ad9ec2",
    ),
    "transaction_attestation_schema_sha256": (
        BASE_TOPIC / "transaction-attestation.schema.json",
        "d2c186b0d30419e0459d93d92af1f84907125becdeb75c7e1890dce597d3e72c",
    ),
    "attempt_006_failure_sha256": (
        ATTEMPT_006_TOPIC / "rehearsal-failure-evidence.json",
        "3c7049b318fffb28aa70e8b4346f1ed857b7cf34e1780eec21373935f6c88efd",
    ),
    "attempt_006_envelope_sha256": (
        ATTEMPT_006_TOPIC / "attempt-006-execution-envelope.json",
        "52470c6c6245f0988dd4f580e68f7a0e21ce5b8636e60119091c089d603bde1c",
    ),
    "start_option_repair_attestation_sha256": (
        START_ARGV_REPAIR_TOPIC / "repair-attestation.json",
        "73d5773d3662509ec2cdb8d8f109651b77ef79be42f5b641f07e36d7ca8bcf91",
    ),
    "start_option_repair_contract_sha256": (
        START_ARGV_REPAIR_TOPIC / "contract.json",
        "de9106afdd69db62eaaf6888ba780e65596838c162f2f1db5cc2703b893bf8d7",
    ),
    "start_option_repair_report_sha256": (
        START_ARGV_REPAIR_TOPIC / "repair-report.md",
        "35afc06958477556f9d0689a99fad26babb8e15fb268d90b1cb983321ee9fee4",
    ),
}

PASS_RESULT = "raisa_provider_free_check_in_relay_free_recovery_attempt_007_pass"


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
        raise accepted.RehearsalFailure("attempt_007_static", "git_binding_failed")
    return completed.stdout.strip()


def _source_head() -> str:
    head = _git("rev-parse", "--verify", "HEAD^{commit}")
    if accepted.HEX40.fullmatch(head) is None:
        raise accepted.RehearsalFailure("attempt_007_static", "source_head_invalid")
    for source in GIT_SOURCES.values():
        if accepted.HEX40.fullmatch(source) is None:
            raise accepted.RehearsalFailure(
                "attempt_007_static", "source_binding_not_full_commit"
            )
        if _git("cat-file", "-t", source) != "commit":
            raise accepted.RehearsalFailure(
                "attempt_007_static", "source_binding_not_commit"
            )
        relation = subprocess.run(
            ["git", "merge-base", "--is-ancestor", source, head],
            cwd=ROOT,
            check=False,
            capture_output=True,
        )
        if relation.returncode != 0:
            raise accepted.RehearsalFailure(
                "attempt_007_static", "source_binding_not_ancestor"
            )
    return head


def _assert_terminal_namespace_empty(
    paths: tuple[Path, ...] = TERMINAL_PATHS,
) -> None:
    if any(path.exists() for path in paths):
        raise accepted.RehearsalFailure(
            "attempt_007_execution", "terminal_artifact_already_exists"
        )


@contextmanager
def _attempt_007_terminal_bindings() -> Iterator[None]:
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
    schema = json.loads(ENVELOPE_SCHEMA_PATH.read_text(encoding="utf-8"))
    if list(Draft202012Validator(schema).iter_errors(value)):
        raise accepted.RehearsalFailure(
            "attempt_007_evidence", "execution_envelope_schema_invalid"
        )


def _example_envelope(source_head: str) -> dict[str, object]:
    return {
        "schema_version": (
            "emr4.check-in-relay-free-recovery-attempt-007.execution-envelope.v1"
        ),
        "result": "failed_closed",
        "attempt_id": "attempt-007",
        "source_head": source_head,
        **GIT_SOURCES,
        **{key: digest for key, (_, digest) in HASH_BINDINGS.items()},
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
    terminal_namespace_empty = not any(path.exists() for path in TERMINAL_PATHS)
    for code, (path, expected) in HASH_BINDINGS.items():
        if _sha256(path) != expected:
            raise accepted.RehearsalFailure("attempt_007_static", f"{code}_mismatch")
    if not _bindings_are_historical():
        raise accepted.RehearsalFailure(
            "attempt_007_static", "accepted_terminal_binding_not_historical"
        )
    if require_empty_namespace:
        _assert_terminal_namespace_empty()
    base = accepted.static_check()
    _validate_envelope(_example_envelope(source_head))
    return {
        "schema_version": "emr4.check-in-relay-free-recovery-attempt-007.static.v1",
        "status": "passed",
        "source_head": source_head,
        **GIT_SOURCES,
        **{key: digest for key, (_, digest) in HASH_BINDINGS.items()},
        "base_static_status": base["status"],
        "contract_mutations": base["contract_mutations"],
        "manifest_mutations": base["manifest_mutations"],
        "classifier_mutations": base["classifier_mutations"],
        "state_mutations": base["state_mutations"],
        "terminal_namespace_empty": terminal_namespace_empty,
    }


def _sanitized_failure(error: accepted.RehearsalFailure) -> dict[str, object]:
    return accepted._failure_evidence(
        error,
        ["attempt_007_wrapper_failed_closed"],
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
        "terminal_binding_restored": _bindings_are_historical(),
    }
    accepted._assert_redacted(envelope, forbidden_values=())
    _validate_envelope(envelope)
    return envelope


def run_attempt() -> dict[str, object]:
    static = static_check()
    evidence: dict[str, object]
    try:
        with _attempt_007_terminal_bindings():
            evidence, _ = accepted.run_rehearsal()
    except accepted.RehearsalFailure as error:
        evidence = _write_failure_if_absent(error)
    except Exception:
        evidence = _write_failure_if_absent(
            accepted.RehearsalFailure(
                "attempt_007_execution", "unexpected_controller_failure"
            )
        )
    if not _bindings_are_historical():
        raise accepted.RehearsalFailure(
            "attempt_007_evidence", "terminal_binding_not_restored"
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
                "attempt_007_evidence", "terminal_artifact_missing"
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
