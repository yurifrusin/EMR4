"""Fixed output adapter for one check-in relay-free recovery attempt 004."""

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
    "raisa-provider-free-check-in-relay-free-recovery-attempt-004"
)
ENVELOPE_SCHEMA_PATH = TOPIC / "attempt-004-execution-envelope.schema.json"
ENVELOPE_PATH = TOPIC / "attempt-004-execution-envelope.json"
ATTESTATION_PATH = TOPIC / "transaction-attestation.json"
EVIDENCE_PATH = TOPIC / "rehearsal-evidence.json"
FAILURE_PATH = TOPIC / "rehearsal-failure-evidence.json"
TERMINAL_PATHS = (ENVELOPE_PATH, ATTESTATION_PATH, EVIDENCE_PATH, FAILURE_PATH)

GIT_SOURCES = {
    "plan_source": "7bbc0eb6466811c323006ddb6bcc80a3a6fcb679",
    "attempt_003_execution_source": "19e4414fec067fcbb6af12818e432953432878be",
    "attempt_003_evidence_source": "d2c6f7e465b1bcf2f8cf458a8fbd5721631db422",
    "call_site_repair_source": "95d456a1e3861ae463cf3643f347fa666c75fa48",
    "call_site_reviewed_candidate": "8bda88069daeb314998341fc961b9aa061d496e5",
    "no_database_source": "958ae762e7c6a065b5926f47eb1a2b63115212c7",
    "native_hmr_source": "5ff79d68f6df25d8bebdba78a6d504afb64de2ab",
    "relay_free_transport_source": "4f0f54c2b0861828f9994444201b8da1bd54be00",
    "runtime_role_source": "6a2832575e9b4df5c40a13984db7281e79814a94",
}

BASE_TOPIC = ROOT / (
    "orchestration/continuity/"
    "raisa-provider-free-disposable-postgresql-default-off-check-in-relay-free-"
    "rollback-unknown-commit-recovery-rehearsal"
)
PREDECESSOR_002_TOPIC = ROOT / (
    "orchestration/continuity/"
    "raisa-provider-free-check-in-relay-free-recovery-attempt-002"
)
PREDECESSOR_003_TOPIC = ROOT / (
    "orchestration/continuity/"
    "raisa-provider-free-check-in-relay-free-recovery-attempt-003"
)
CREATED_STATE_TOPIC = ROOT / (
    "orchestration/continuity/"
    "raisa-provider-free-docker-created-state-profile-conformance-repair"
)
NO_DATABASE_TOPIC = ROOT / (
    "orchestration/continuity/"
    "ariadne-provider-free-no-database-manifest-runner-admission-repair"
)
NATIVE_HMR_TOPIC = ROOT / (
    "orchestration/continuity/"
    "deepseek-native-harness-provider-free-stock-headless-to-custom-runner-"
    "hmr-boot-proof"
)

HASH_BINDINGS = {
    "corrected_harness_sha256": (
        Path(accepted.__file__),
        "eda68427b87db48064bcfb82762d55c51b600cf2ba5d4724a0faae24d8a3db5b",
    ),
    "contract_sha256": (
        BASE_TOPIC / "contract.json",
        "bed2a89a3814ba9e9ac006d0fdb0c68d204fec53d8c21b6128190605b6ad9ec2",
    ),
    "transaction_attestation_schema_sha256": (
        BASE_TOPIC / "transaction-attestation.schema.json",
        "d2c186b0d30419e0459d93d92af1f84907125becdeb75c7e1890dce597d3e72c",
    ),
    "created_state_evidence_sha256": (
        CREATED_STATE_TOPIC / "created-state-representation-evidence.json",
        "9f721e0d0e11f5570c2ebe95f8e62d4f1f0e7b2af27f704e4108e2f1792fb98b",
    ),
    "repair_attestation_sha256": (
        CREATED_STATE_TOPIC / "repair-attestation.json",
        "49c5a3673d388fc84b2f046a993a8f4c747f9887252ef4cdd2dfcc59e9a11410",
    ),
    "predecessor_001_failure_sha256": (
        BASE_TOPIC / "rehearsal-failure-evidence.json",
        "5c38080aa27615ea1efad166d14a61605596130058498ea03c8b631bbeae3be2",
    ),
    "predecessor_001_cleanup_sha256": (
        BASE_TOPIC / "attempt-001-cleanup-recovery.json",
        "a8920b0a294b43c8f67d0348bc6087b84921f8f8788ccd3f969913d95861c06a",
    ),
    "predecessor_002_failure_sha256": (
        PREDECESSOR_002_TOPIC / "rehearsal-failure-evidence.json",
        "7efb9853beee9723dbb01fac1f03c4392216bfcc15e9f490f4cb0baae08920ff",
    ),
    "predecessor_002_envelope_sha256": (
        PREDECESSOR_002_TOPIC / "attempt-002-execution-envelope.json",
        "6418ecf2e2356b6c875a70106136cdc65d6e545ead5fceeb2c793db45ebe2e40",
    ),
    "predecessor_003_failure_sha256": (
        PREDECESSOR_003_TOPIC / "rehearsal-failure-evidence.json",
        "e8bf62e86fd3dbcfbcd7a0d68628e0d736b06617f4ef1a023a9a8928344fe96b",
    ),
    "predecessor_003_envelope_sha256": (
        PREDECESSOR_003_TOPIC / "attempt-003-execution-envelope.json",
        "91e12b3268283fc3be48df583f7a0650a5a30bdaee40b1f74297d8185af91c75",
    ),
    "predecessor_003_cleanup_sha256": (
        PREDECESSOR_003_TOPIC / "attempt-003-cleanup-recovery.json",
        "048cd946166fabb8b2ce3400e31c85ee2fe410e6a3c07d5d26cbc79141250b71",
    ),
    "no_database_evidence_sha256": (
        NO_DATABASE_TOPIC / "provider-free-no-database-admission-evidence.json",
        "9770af5d6d8e4282456e2ddd43ce6359c5dbff13b974c7d37a887fab331476d8",
    ),
    "native_hmr_evidence_sha256": (
        NATIVE_HMR_TOPIC / "provider-free-native-harness-hmr-boot-evidence.json",
        "68d4168649d80268fdb81ba3582bed261e7944fc0f19d24aee5933270882afcc",
    ),
}

PASS_RESULT = "raisa_provider_free_check_in_relay_free_recovery_attempt_004_pass"


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
        raise accepted.RehearsalFailure("attempt_004_static", "git_binding_failed")
    return completed.stdout.strip()


def _source_head() -> str:
    head = _git("rev-parse", "HEAD")
    if accepted.HEX40.fullmatch(head) is None:
        raise accepted.RehearsalFailure("attempt_004_static", "source_head_invalid")
    for source in GIT_SOURCES.values():
        if accepted.HEX40.fullmatch(source) is None:
            raise accepted.RehearsalFailure(
                "attempt_004_static", "source_binding_not_full_commit"
            )
        if _git("cat-file", "-t", source) != "commit":
            raise accepted.RehearsalFailure(
                "attempt_004_static", "source_binding_not_commit"
            )
        relation = subprocess.run(
            ["git", "merge-base", "--is-ancestor", source, head],
            cwd=ROOT,
            check=False,
            capture_output=True,
        )
        if relation.returncode != 0:
            raise accepted.RehearsalFailure(
                "attempt_004_static", "source_binding_not_ancestor"
            )
    return head


def _assert_terminal_namespace_empty(
    paths: tuple[Path, ...] = TERMINAL_PATHS,
) -> None:
    if any(path.exists() for path in paths):
        raise accepted.RehearsalFailure(
            "attempt_004_execution", "terminal_artifact_already_exists"
        )


@contextmanager
def _attempt_004_terminal_bindings() -> Iterator[None]:
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
    errors = list(Draft202012Validator(schema).iter_errors(value))
    if errors:
        raise accepted.RehearsalFailure(
            "attempt_004_evidence", "execution_envelope_schema_invalid"
        )


def _example_envelope(source_head: str) -> dict[str, object]:
    return {
        "schema_version": (
            "emr4.check-in-relay-free-recovery-attempt-004.execution-envelope.v1"
        ),
        "result": "failed_closed",
        "attempt_id": "attempt-004",
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
            raise accepted.RehearsalFailure(
                "attempt_004_static", f"{code}_mismatch"
            )
    if not _bindings_are_historical():
        raise accepted.RehearsalFailure(
            "attempt_004_static", "accepted_terminal_binding_not_historical"
        )
    if require_empty_namespace:
        _assert_terminal_namespace_empty()
    base = accepted.static_check()
    _validate_envelope(_example_envelope(source_head))
    return {
        "schema_version": "emr4.check-in-relay-free-recovery-attempt-004.static.v1",
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
        ["attempt_004_wrapper_failed_closed"],
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
        with _attempt_004_terminal_bindings():
            evidence, _ = accepted.run_rehearsal()
    except accepted.RehearsalFailure as error:
        evidence = _write_failure_if_absent(error)
    except Exception:
        evidence = _write_failure_if_absent(
            accepted.RehearsalFailure(
                "attempt_004_execution", "unexpected_controller_failure"
            )
        )
    if not _bindings_are_historical():
        raise accepted.RehearsalFailure(
            "attempt_004_evidence", "terminal_binding_not_restored"
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
                "attempt_004_evidence", "terminal_artifact_missing"
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
