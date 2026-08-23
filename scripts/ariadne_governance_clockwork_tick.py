"""Check, publish or roll back one generic live governance clockwork tick."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from orchestration_harness.governance_clockwork_tick import (
    BLOCKED_INTENT_VERSION,
    CHECKPOINT_INTENT_VERSION,
    SEMANTIC_TICK_INTENT_VERSION,
    SEMANTIC_VERIFICATION_PROFILE,
    USER_DECISION_INTENT_VERSION,
    ClockworkTickRejection,
    admit_tick_intent,
    build_checkpoint_tick_generation,
    build_user_decision_tick_generation,
    build_tick_generation,
    build_blocked_tick_generation,
    materialize_semantic_evidence_headers,
    publish_tick_generation,
    rollback_tick_generation,
    validate_blocked_tick_intent,
    validate_checkpoint_tick_intent,
    validate_tick_live_state,
    validate_user_decision_tick_intent,
)
from orchestration_harness.governance_live_adoption import validate_contract
from orchestration_harness import transactional_closeout as tc


CONTRACT = ROOT / "orchestration/continuity/ariadne-provider-free-clockwork-live-canonical-adoption-retirement/contract.json"
TRANSACTION_FACTS_VERSION = "ariadne.governance_command_transaction_facts.v1"
SEMANTIC_VERIFICATION_FACTS_VERSION = (
    "ariadne.governance_semantic_verification_facts.v1"
)


class SemanticVerificationRejection(ClockworkTickRejection):
    """A closed semantic verification command failed before preparation."""

    def __init__(self, facts: dict[str, Any]):
        super().__init__("tick_semantic_verification")
        self.facts = facts


def _load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"object_required:{path}")
    return value


def _intent_path(raw: Path) -> Path:
    path = (ROOT / raw).resolve() if not raw.is_absolute() else raw.resolve()
    try:
        path.relative_to(ROOT.resolve())
    except ValueError as error:
        raise ValueError("intent_path_escape") from error
    if not path.is_file() or path.name not in {
        "closeout-intent.json",
        "checkpoint-intent.json",
    }:
        raise ValueError("closed_tick_intent_required")
    return path


def _transaction_facts(
    *,
    disposition: str,
    preparations: int,
    preparation_rejections: int,
    publication_attempts: int,
    published_generations: int,
    rollback_attempts: int,
    byte_exact_rollbacks: int,
    idempotent_readbacks: int,
    base_lease_sequence: int,
    prospective_lease_sequence: int | None,
    result_lease_sequence: int,
    base_generation_id: str,
    prepared_generation_id: str | None,
    result_generation_id: str,
) -> dict[str, Any]:
    return {
        "schema_version": TRANSACTION_FACTS_VERSION,
        "command_disposition": disposition,
        "invocations": 1,
        "preparations": preparations,
        "preparation_rejections": preparation_rejections,
        "publication_attempts": publication_attempts,
        "published_generations": published_generations,
        "rollback_attempts": rollback_attempts,
        "byte_exact_rollbacks": byte_exact_rollbacks,
        "idempotent_readbacks": idempotent_readbacks,
        "base_lease_sequence": base_lease_sequence,
        "prospective_lease_sequence": prospective_lease_sequence,
        "result_lease_sequence": result_lease_sequence,
        "committed_lease_advance": result_lease_sequence - base_lease_sequence,
        "base_generation_id": base_generation_id,
        "prepared_generation_id": prepared_generation_id,
        "result_generation_id": result_generation_id,
    }


def _prepared_transaction_facts(
    prepared: dict[str, Any], *, published: bool
) -> dict[str, Any]:
    base = prepared["base_pointer"]
    target = prepared["pointer"]
    generation_id = prepared["generation_manifest"]["generation_id"]
    return _transaction_facts(
        disposition="publication_committed" if published else "dry_preparation",
        preparations=1,
        preparation_rejections=0,
        publication_attempts=int(published),
        published_generations=int(published),
        rollback_attempts=0,
        byte_exact_rollbacks=0,
        idempotent_readbacks=0,
        base_lease_sequence=base["lease_sequence"],
        prospective_lease_sequence=target["lease_sequence"],
        result_lease_sequence=(
            target["lease_sequence"] if published else base["lease_sequence"]
        ),
        base_generation_id=base["selected_generation_id"],
        prepared_generation_id=generation_id,
        result_generation_id=(
            generation_id if published else base["selected_generation_id"]
        ),
    )


def _idempotent_transaction_facts(state: dict[str, Any]) -> dict[str, Any]:
    return _transaction_facts(
        disposition="idempotent_readback",
        preparations=0,
        preparation_rejections=0,
        publication_attempts=0,
        published_generations=0,
        rollback_attempts=0,
        byte_exact_rollbacks=0,
        idempotent_readbacks=1,
        base_lease_sequence=state["lease_sequence"],
        prospective_lease_sequence=None,
        result_lease_sequence=state["lease_sequence"],
        base_generation_id=state["generation_id"],
        prepared_generation_id=None,
        result_generation_id=state["generation_id"],
    )


def _rollback_transaction_facts(result: dict[str, Any]) -> dict[str, Any]:
    result_lease = result["lease_sequence"]
    return _transaction_facts(
        disposition="byte_exact_rollback",
        preparations=0,
        preparation_rejections=0,
        publication_attempts=0,
        published_generations=0,
        rollback_attempts=1,
        byte_exact_rollbacks=int(result["byte_exact"] is True),
        idempotent_readbacks=0,
        base_lease_sequence=result_lease - 1,
        prospective_lease_sequence=result_lease,
        result_lease_sequence=result_lease,
        base_generation_id=result["rolled_back_from_generation_id"],
        prepared_generation_id=None,
        result_generation_id=result["selected_generation_id"],
    )


def _command_result(
    result: dict[str, Any],
    transaction_facts: dict[str, Any],
    verification_facts: dict[str, Any] | None = None,
) -> dict[str, Any]:
    output = {
        **result,
        "transaction_facts": transaction_facts,
        "caller_authored_derived_fields": 0,
        "live_publication_count": transaction_facts["published_generations"],
        "bespoke_updater_executions": 0,
    }
    if verification_facts is not None:
        output["verification_facts"] = verification_facts
    return output


def _is_semantic_intent(intent: dict[str, Any]) -> bool:
    return intent.get("schema_version") == SEMANTIC_TICK_INTENT_VERSION


def _semantic_validation_facts(command_count: int, *, disposition: str) -> dict[str, Any]:
    return {
        "schema_version": SEMANTIC_VERIFICATION_FACTS_VERSION,
        "profile": SEMANTIC_VERIFICATION_PROFILE,
        "disposition": disposition,
        "command_count": command_count,
        "executed_command_count": 0,
        "passed_command_count": 0,
        "tracked_drift": 0,
        "commands": [],
    }


def _tracked_status(repo_root: Path) -> str:
    result = subprocess.run(
        ["git", "status", "--porcelain=v1", "--untracked-files=no"],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if result.returncode != 0:
        raise RuntimeError("semantic_verification_git_status_failed")
    return result.stdout


def _run_semantic_verification(
    repo_root: Path,
    command_manifest: dict[str, Any],
    *,
    command_runner: Any | None = None,
    tracked_reader: Any | None = None,
    interpreter: Path | None = None,
) -> dict[str, Any]:
    runner = command_runner or subprocess.run
    read_tracked = tracked_reader or _tracked_status
    commands = command_manifest["commands"]
    facts = _semantic_validation_facts(
        len(commands), disposition="verification_rejected"
    )
    try:
        starting_status = read_tracked(repo_root)
    except (OSError, RuntimeError) as error:
        facts["reason"] = "tracked_status_unavailable"
        raise SemanticVerificationRejection(facts) from error
    if starting_status:
        facts["reason"] = "tracked_worktree_not_clean"
        facts["tracked_drift"] = 1
        raise SemanticVerificationRejection(facts)

    executable = (interpreter or (repo_root / ".venv/Scripts/python.exe")).resolve()
    if not executable.is_file() or executable != Path(sys.executable).resolve():
        facts["reason"] = "active_interpreter_mismatch"
        raise SemanticVerificationRejection(facts)

    for command in commands:
        try:
            completed = runner(
                [str(executable), *command["arguments"]],
                cwd=repo_root,
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=600,
            )
        except (OSError, subprocess.SubprocessError) as error:
            facts["reason"] = "command_start_or_timeout"
            facts["failed_command_id"] = command["command_id"]
            raise SemanticVerificationRejection(facts) from error
        reading = {
            "command_id": command["command_id"],
            "exit_code": completed.returncode,
            "stdout_sha256": hashlib.sha256(
                completed.stdout.encode("utf-8")
            ).hexdigest(),
            "stderr_sha256": hashlib.sha256(
                completed.stderr.encode("utf-8")
            ).hexdigest(),
        }
        facts["commands"].append(reading)
        facts["executed_command_count"] += 1
        if completed.returncode != 0:
            facts["reason"] = "command_failed"
            facts["failed_command_id"] = command["command_id"]
            raise SemanticVerificationRejection(facts)
        facts["passed_command_count"] += 1
        try:
            current_status = read_tracked(repo_root)
        except (OSError, RuntimeError) as error:
            facts["reason"] = "tracked_status_unavailable"
            raise SemanticVerificationRejection(facts) from error
        if current_status != starting_status:
            facts["reason"] = "tracked_worktree_drift"
            facts["tracked_drift"] = 1
            facts["failed_command_id"] = command["command_id"]
            raise SemanticVerificationRejection(facts)
    facts["disposition"] = "verification_passed"
    return facts


def _prospective_rejection_result(
    error: ClockworkTickRejection,
) -> dict[str, Any]:
    prefix = "tick_prospective_current_node_evidence:"
    message = str(error)
    if not message.startswith(prefix):
        raise error
    state = validate_tick_live_state(ROOT, validate_contract(_load(CONTRACT)))
    transaction_facts = _transaction_facts(
        disposition="prospective_evidence_rejected",
        preparations=1,
        preparation_rejections=1,
        publication_attempts=0,
        published_generations=0,
        rollback_attempts=0,
        byte_exact_rollbacks=0,
        idempotent_readbacks=0,
        base_lease_sequence=state["lease_sequence"],
        prospective_lease_sequence=None,
        result_lease_sequence=state["lease_sequence"],
        base_generation_id=state["generation_id"],
        prepared_generation_id=None,
        result_generation_id=state["generation_id"],
    )
    errors = message.removeprefix(prefix).split(",")
    return _command_result(
        {
            "schema_version": (
                "ariadne.governance_prospective_evidence_rejection.v1"
            ),
            "status": "revision_required",
            "reason": "tick_prospective_current_node_evidence",
            "errors": errors,
            "error_count": len(errors),
            "source_commit": state["source_commit"],
            "generation_id": state["generation_id"],
            "previous_generation_id": state["previous_generation_id"],
            "lease_sequence": state["lease_sequence"],
        },
        transaction_facts,
    )


def _semantic_verification_rejection_result(
    error: SemanticVerificationRejection,
) -> dict[str, Any]:
    state = validate_tick_live_state(ROOT, validate_contract(_load(CONTRACT)))
    transaction_facts = _transaction_facts(
        disposition="semantic_verification_rejected",
        preparations=0,
        preparation_rejections=1,
        publication_attempts=0,
        published_generations=0,
        rollback_attempts=0,
        byte_exact_rollbacks=0,
        idempotent_readbacks=0,
        base_lease_sequence=state["lease_sequence"],
        prospective_lease_sequence=None,
        result_lease_sequence=state["lease_sequence"],
        base_generation_id=state["generation_id"],
        prepared_generation_id=None,
        result_generation_id=state["generation_id"],
    )
    return _command_result(
        {
            "schema_version": "ariadne.governance_semantic_verification_rejection.v1",
            "status": "revision_required",
            "reason": "tick_semantic_verification",
            "source_commit": state["source_commit"],
            "generation_id": state["generation_id"],
            "previous_generation_id": state["previous_generation_id"],
            "lease_sequence": state["lease_sequence"],
        },
        transaction_facts,
        error.facts,
    )


def _semantic_materialization_rejection_result(
    error: ClockworkTickRejection,
) -> dict[str, Any]:
    message = str(error)
    prefix = "tick_semantic_evidence_materialization:"
    errors = message.removeprefix(prefix).split(",") if message.startswith(prefix) else [message]
    return {
        "schema_version": "ariadne.governance_semantic_evidence_rejection.v1",
        "status": "revision_required",
        "reason": "tick_semantic_evidence_materialization",
        "errors": errors,
        "error_count": len(errors),
        "canonical_writes": 0,
        "pointer_movement": 0,
    }


def _write_outputs(topic: Path, result: dict, *, prefix: str = "clockwork-tick") -> None:
    evidence = topic / f"{prefix}-evidence.json"
    report = topic / f"{prefix}-report.md"
    evidence.write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    verification = result.get("verification_facts")
    verification_text = (
        "\n\nVerification profile: "
        f"`{verification['profile']}`\n\n"
        f"Executed verification commands: {verification['executed_command_count']}\n\n"
        f"Passed verification commands: {verification['passed_command_count']}"
        if isinstance(verification, dict)
        else ""
    )
    report.write_text(
        "# Governance clockwork tick\n\n"
        f"Status: **{result['status']}**\n\n"
        f"Operation: `{result.get('operation_id', 'not-published')}`\n\n"
        f"Source: `{result['source_commit']}`\n\n"
        f"Generation: `{result['generation_id']}`\n\n"
        f"Previous generation: `{result['previous_generation_id']}`\n\n"
        f"Lease sequence: {result['lease_sequence']}\n\n"
        f"Command disposition: `{result['transaction_facts']['command_disposition']}`\n\n"
        f"Published generations: {result['transaction_facts']['published_generations']}\n\n"
        f"Byte-exact rollbacks: {result['transaction_facts']['byte_exact_rollbacks']}"
        f"{verification_text}\n",
        encoding="utf-8",
        newline="\n",
    )


def _output_prefix(intent: dict) -> str:
    return (
        "clockwork-checkpoint-tick"
        if intent.get("schema_version") == CHECKPOINT_INTENT_VERSION
        else "clockwork-tick"
    )


def _write_idempotent_readback(
    topic: Path,
    result: dict,
    *,
    prefix: str,
) -> Path:
    publication_evidence = topic / f"{prefix}-evidence.json"
    publication_report = topic / f"{prefix}-report.md"
    errors: list[str] = []
    try:
        evidence_bytes = publication_evidence.read_bytes()
        publication = json.loads(evidence_bytes.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        evidence_bytes = b""
        publication = None
        errors.append("publication_evidence_missing_or_unreadable")
    try:
        report_bytes = publication_report.read_bytes()
        report_text = report_bytes.decode("utf-8")
    except (OSError, UnicodeDecodeError):
        report_bytes = b""
        report_text = ""
        errors.append("publication_report_missing_or_unreadable")

    operation_id = result.get("operation_id")
    expected_publication = {
        "status": "passed",
        "operation_id": operation_id,
        "source_commit": result.get("source_commit"),
        "generation_id": result.get("generation_id"),
    }
    if isinstance(publication, dict):
        for key, expected in expected_publication.items():
            if publication.get(key) != expected:
                errors.append(f"publication_evidence_{key}_mismatch")
        transaction = publication.get("transaction_facts")
        if not isinstance(transaction, dict):
            errors.append("publication_transaction_facts_missing")
        else:
            if transaction.get("command_disposition") != "publication_committed":
                errors.append("publication_disposition_mismatch")
            if transaction.get("published_generations") != 1:
                errors.append("publication_count_mismatch")
    elif "publication_evidence_missing_or_unreadable" not in errors:
        errors.append("publication_evidence_object_required")

    report_bindings = (
        f"Operation: `{operation_id if operation_id is not None else 'not-published'}`",
        f"Source: `{result.get('source_commit')}`",
        f"Generation: `{result.get('generation_id')}`",
        "Command disposition: `publication_committed`",
    )
    for binding in report_bindings:
        if binding not in report_text:
            errors.append("publication_report_binding_mismatch")
            break

    facts = result.get("transaction_facts")
    if (
        not isinstance(facts, dict)
        or facts.get("command_disposition") != "idempotent_readback"
    ):
        errors.append("idempotent_readback_facts_required")

    if errors:
        raise ClockworkTickRejection(
            "tick_publication_evidence_preservation:" + ",".join(errors)
        )

    readback = topic / f"{prefix}-idempotent-readback.json"
    temporary = readback.with_name(f".{readback.name}.tmp")
    payload = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    try:
        temporary.write_text(
            payload,
            encoding="utf-8",
            newline="\n",
        )
        if (
            publication_evidence.read_bytes() != evidence_bytes
            or publication_report.read_bytes() != report_bytes
        ):
            raise ClockworkTickRejection(
                "tick_publication_evidence_preservation:publication_pair_changed"
            )
        temporary.replace(readback)
    finally:
        temporary.unlink(missing_ok=True)
    return readback


def _intent_identity(
    repo_root: Path, intent: dict, contract: dict
) -> tuple[str | None, str, str]:
    version = intent.get("schema_version")
    if version == BLOCKED_INTENT_VERSION:
        admitted = validate_blocked_tick_intent(intent, contract)
        return admitted["operation_id"], "blocked_transition", tc.sha256(admitted)
    if version == CHECKPOINT_INTENT_VERSION:
        admitted = validate_checkpoint_tick_intent(intent, contract)
        return admitted["operation_id"], "checkpoint_transition", tc.sha256(admitted)
    if version == USER_DECISION_INTENT_VERSION:
        admitted = validate_user_decision_tick_intent(intent, contract)
        return (
            admitted["next_operation"]["operation_id"],
            "user_decision_transition",
            tc.sha256(admitted),
        )
    admitted = admit_tick_intent(repo_root, intent, contract)
    return (
        admitted["transaction_manifest"]["operation_id"],
        "clean_closeout",
        tc.sha256(admitted["transaction_manifest"]),
    )


def _is_exact_published_intent(
    transaction: dict,
    *,
    operation_id: str | None,
    event_kind: str,
    intent_sha256: str,
) -> bool:
    if (
        transaction.get("operation_id") != operation_id
        or transaction.get("event_kind") != event_kind
    ):
        return False
    return any(
        isinstance(event, dict)
        and isinstance(event.get("payload"), dict)
        and (
            event["payload"].get("intent_sha256") == intent_sha256
            or event["payload"].get("manifest_sha256") == intent_sha256
        )
        for event in transaction.get("journal", [])
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--publish", action="store_true")
    mode.add_argument("--rollback", action="store_true")
    mode.add_argument("--prepare-evidence", action="store_true")
    parser.add_argument("--intent", type=Path)
    arguments = parser.parse_args(argv)
    contract = validate_contract(_load(CONTRACT))
    if arguments.rollback:
        if arguments.intent is not None:
            parser.error("--rollback does not accept --intent")
        rollback = rollback_tick_generation(ROOT, contract, writer_id="clockwork")
        result = _command_result(rollback, _rollback_transaction_facts(rollback))
    else:
        if arguments.intent is None:
            parser.error("--check, --publish and --prepare-evidence require --intent")
        intent_path = _intent_path(arguments.intent)
        intent = _load(intent_path)
        if arguments.prepare_evidence:
            if not _is_semantic_intent(intent):
                parser.error("--prepare-evidence requires a semantic closeout intent")
            result = materialize_semantic_evidence_headers(ROOT, intent, contract)
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return 0
        transaction = _load(ROOT / contract["clockwork_root"] / "transaction.json")
        operation_id, event_kind, intent_sha256 = _intent_identity(
            ROOT, intent, contract
        )
        semantic = _is_semantic_intent(intent)
        verification_facts: dict[str, Any] | None = None
        admitted_semantic: dict[str, Any] | None = None
        if semantic:
            admitted_semantic = admit_tick_intent(ROOT, intent, contract)
            verification_facts = _semantic_validation_facts(
                len(admitted_semantic["command_manifest"]["commands"]),
                disposition="validated_not_executed",
            )
        if _is_exact_published_intent(
            transaction,
            operation_id=operation_id,
            event_kind=event_kind,
            intent_sha256=intent_sha256,
        ):
            state = validate_tick_live_state(ROOT, contract)
            if verification_facts is not None:
                verification_facts["disposition"] = "idempotent_not_reexecuted"
            result = _command_result(
                state,
                _idempotent_transaction_facts(state),
                verification_facts,
            )
            if arguments.publish:
                _write_idempotent_readback(
                    intent_path.parent,
                    result,
                    prefix=_output_prefix(intent),
                )
        else:
            if semantic and arguments.publish:
                if admitted_semantic is None:
                    raise RuntimeError("semantic_intent_not_admitted")
                verification_facts = _run_semantic_verification(
                    ROOT, admitted_semantic["command_manifest"]
                )
            if intent.get("schema_version") == BLOCKED_INTENT_VERSION:
                prepared = build_blocked_tick_generation(ROOT, contract, intent)
            elif intent.get("schema_version") == CHECKPOINT_INTENT_VERSION:
                prepared = build_checkpoint_tick_generation(ROOT, contract, intent)
            elif intent.get("schema_version") == USER_DECISION_INTENT_VERSION:
                prepared = build_user_decision_tick_generation(
                    ROOT, contract, intent
                )
            else:
                prepared = build_tick_generation(ROOT, contract, intent)
            if arguments.check:
                result = _command_result(
                    {
                        "schema_version": "ariadne.governance_live_tick_dry_run.v1",
                        "status": "passed",
                        "source_commit": prepared["source_commit"],
                        "generation_id": prepared["generation_manifest"]["generation_id"],
                        "bundle_sha256": prepared["generation_manifest"]["bundle_sha256"],
                        "previous_generation_id": prepared["pointer"]["previous_generation_id"],
                        "lease_sequence": prepared["pointer"]["lease_sequence"],
                    },
                    _prepared_transaction_facts(prepared, published=False),
                    verification_facts,
                )
            else:
                published = publish_tick_generation(
                    ROOT, prepared, writer_id="clockwork"
                )
                result = _command_result(
                    published,
                    _prepared_transaction_facts(prepared, published=True),
                    verification_facts,
                )
                _write_outputs(
                    intent_path.parent,
                    result,
                    prefix=_output_prefix(intent),
                )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


def cli(argv: list[str] | None = None) -> int:
    try:
        return main(argv)
    except SemanticVerificationRejection as error:
        result = _semantic_verification_rejection_result(error)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 1
    except ClockworkTickRejection as error:
        message = str(error)
        if message.startswith("tick_prospective_current_node_evidence:"):
            result = _prospective_rejection_result(error)
        elif message.startswith("tick_semantic"):
            result = _semantic_materialization_rejection_result(error)
        elif message.startswith("tick_publication_evidence_preservation:"):
            errors = message.split(":", 1)[1].split(",")
            result = {
                "schema_version": "ariadne.governance_idempotent_readback_rejection.v1",
                "status": "revision_required",
                "reason": "tick_publication_evidence_preservation",
                "errors": errors,
                "error_count": len(errors),
                "readback_writes": 0,
                "canonical_writes": 0,
                "pointer_movement": 0,
            }
        else:
            raise
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(cli())
