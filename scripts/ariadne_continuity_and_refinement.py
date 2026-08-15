"""Thin provider-free CLI for Ariadne continuity and refinement decisions.

The CLI reads only explicit supplied JSON files and prints (or writes to an
explicitly named output file) a typed decision result. It never appends a
journal, discovers files, executes a command, spawns a process, accesses the
network/database/provider, or modifies repository/product state.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from orchestration_harness.continuity_and_refinement import (
    assess_command_submission,
    assess_cursor,
    assess_gate,
    assess_promotion,
    assess_rejection,
    assess_rollback,
    validate_gate_attempt,
    validate_operation_journal,
    validate_refinement_promotion,
    validate_refinement_proposal,
)


def _load_json(path: Path, *, label: str) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ValueError(f"{label} must be valid JSON") from error


def _load_list(path: Path, *, label: str) -> list[Any]:
    value = _load_json(path, label=label)
    if not isinstance(value, list):
        raise ValueError(f"{label} must be a JSON array")
    return value


def _canonical_bytes(value: object) -> bytes:
    return (
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    ).encode("utf-8")


def _emit(payload: dict[str, Any], output: Path | None) -> int:
    if output is not None:
        output.write_bytes(_canonical_bytes(payload))
    else:
        sys.stdout.buffer.write(_canonical_bytes(payload))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate and decide Ariadne continuity and refinement safeguards."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_journal = subparsers.add_parser(
        "validate-journal", help="Validate an operation journal and print it."
    )
    validate_journal.add_argument("--journal", type=Path, required=True)
    validate_journal.add_argument("--output", type=Path)

    assess_submission = subparsers.add_parser(
        "assess-submission",
        help="Decide whether a command submission is new, replay, conflict or live.",
    )
    assess_submission.add_argument("--journal", type=Path, required=True)
    assess_submission.add_argument("--command-id", required=True)
    assess_submission.add_argument("--request-digest", required=True)
    assess_submission.add_argument("--output", type=Path)

    assess_cursor_cmd = subparsers.add_parser(
        "assess-cursor",
        help="Decide whether a (generation, sequence) cursor needs a snapshot.",
    )
    assess_cursor_cmd.add_argument("--journal", type=Path, required=True)
    assess_cursor_cmd.add_argument("--generation", type=int, required=True)
    assess_cursor_cmd.add_argument("--sequence", type=int, required=True)
    assess_cursor_cmd.add_argument("--output", type=Path)

    validate_gate = subparsers.add_parser(
        "validate-gate-attempt", help="Validate one gate attempt and print it."
    )
    validate_gate.add_argument("--attempt", type=Path, required=True)
    validate_gate.add_argument("--output", type=Path)

    assess_gate_cmd = subparsers.add_parser(
        "assess-gate",
        help="Decide whether to reuse, diagnose, resolve or run a deterministic gate.",
    )
    assess_gate_cmd.add_argument("--prior-attempts", type=Path, required=True)
    assess_gate_cmd.add_argument("--fingerprint", type=Path, required=True)
    assess_gate_cmd.add_argument("--output", type=Path)

    validate_proposal = subparsers.add_parser(
        "validate-proposal",
        help="Validate a quarantined refinement proposal and print it.",
    )
    validate_proposal.add_argument("--proposal", type=Path, required=True)
    validate_proposal.add_argument("--output", type=Path)

    assess_promotion_cmd = subparsers.add_parser(
        "assess-promotion", help="Assess promotion of one refinement proposal."
    )
    assess_promotion_cmd.add_argument("--proposal", type=Path, required=True)
    assess_promotion_cmd.add_argument("--validation-manifest-digest", required=True)
    assess_promotion_cmd.add_argument("--validation-result", required=True)
    assess_promotion_cmd.add_argument("--candidate-digest", required=True)
    assess_promotion_cmd.add_argument("--base-state-digest", required=True)
    assess_promotion_cmd.add_argument("--source-head", required=True)
    assess_promotion_cmd.add_argument("--promoter", required=True)
    assess_promotion_cmd.add_argument("--independent-reviewer")
    assess_promotion_cmd.add_argument("--prior-decisions", type=Path, required=True)
    assess_promotion_cmd.add_argument("--output", type=Path)

    assess_rejection_cmd = subparsers.add_parser(
        "assess-rejection", help="Emit a first-class terminal rejection decision."
    )
    assess_rejection_cmd.add_argument("--proposal", type=Path, required=True)
    assess_rejection_cmd.add_argument("--authority", required=True)
    assess_rejection_cmd.add_argument("--reason", required=True)
    assess_rejection_cmd.add_argument("--prior-decisions", type=Path, required=True)
    assess_rejection_cmd.add_argument("--output", type=Path)

    assess_rollback_cmd = subparsers.add_parser(
        "assess-rollback", help="Emit a first-class terminal rollback decision."
    )
    assess_rollback_cmd.add_argument("--promoted-record", type=Path, required=True)
    assess_rollback_cmd.add_argument("--decision-history", type=Path, required=True)
    assess_rollback_cmd.add_argument("--current-state-digest", required=True)
    assess_rollback_cmd.add_argument("--authority", required=True)
    assess_rollback_cmd.add_argument("--output", type=Path)

    validate_promotion = subparsers.add_parser(
        "validate-promotion", help="Validate a refinement promotion decision record."
    )
    validate_promotion.add_argument("--record", type=Path, required=True)
    validate_promotion.add_argument("--output", type=Path)

    return parser


def run(args: argparse.Namespace) -> int:
    command = args.command
    if command == "validate-journal":
        journal = _load_json(args.journal, label="journal")
        return _emit(validate_operation_journal(journal), args.output)
    if command == "assess-submission":
        journal = _load_json(args.journal, label="journal")
        return _emit(
            assess_command_submission(
                journal, command_id=args.command_id, request_digest=args.request_digest
            ),
            args.output,
        )
    if command == "assess-cursor":
        journal = _load_json(args.journal, label="journal")
        return _emit(
            assess_cursor(journal, generation=args.generation, sequence=args.sequence),
            args.output,
        )
    if command == "validate-gate-attempt":
        attempt = _load_json(args.attempt, label="gate attempt")
        return _emit(validate_gate_attempt(attempt), args.output)
    if command == "assess-gate":
        prior = _load_list(args.prior_attempts, label="prior attempts")
        fingerprint = _load_json(args.fingerprint, label="fingerprint")
        return _emit(
            assess_gate(prior_attempts=prior, fingerprint=fingerprint), args.output
        )
    if command == "validate-proposal":
        proposal = _load_json(args.proposal, label="proposal")
        return _emit(validate_refinement_proposal(proposal), args.output)
    if command == "assess-promotion":
        proposal = _load_json(args.proposal, label="proposal")
        prior_decisions = _load_list(args.prior_decisions, label="prior decisions")
        return _emit(
            assess_promotion(
                proposal,
                validation_manifest_digest=args.validation_manifest_digest,
                validation_result=args.validation_result,
                candidate_digest=args.candidate_digest,
                base_state_digest=args.base_state_digest,
                source_head=args.source_head,
                promoter=args.promoter,
                independent_reviewer=args.independent_reviewer,
                prior_decisions=prior_decisions,
            ),
            args.output,
        )
    if command == "assess-rejection":
        proposal = _load_json(args.proposal, label="proposal")
        prior_decisions = _load_list(args.prior_decisions, label="prior decisions")
        return _emit(
            assess_rejection(
                proposal,
                authority=args.authority,
                reason=args.reason,
                prior_decisions=prior_decisions,
            ),
            args.output,
        )
    if command == "assess-rollback":
        promoted_record = _load_json(args.promoted_record, label="promoted record")
        decision_history = _load_list(args.decision_history, label="decision history")
        return _emit(
            assess_rollback(
                promoted_record=promoted_record,
                decision_history=decision_history,
                current_state_digest=args.current_state_digest,
                authority=args.authority,
            ),
            args.output,
        )
    if command == "validate-promotion":
        record = _load_json(args.record, label="promotion record")
        return _emit(validate_refinement_promotion(record), args.output)
    raise ValueError(f"unknown command {command}")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return run(args)
    except (OSError, ValueError) as error:
        print(f"ariadne continuity and refinement failed: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
