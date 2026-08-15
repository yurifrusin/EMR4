"""Pure deterministic continuity and refinement safeguards for Ariadne.

This module implements the frozen provider-free harness contract described in
``docs/ariadne-provider-free-continuity-journal-and-refinement-promotion-plan.md``.

It is deliberately standard-library only: it imports no application, Alembic,
database, network, cloud, provider or product module, and it never executes a
command or edits repository/product state. Every function is a pure validation
or decision function over explicit JSON-shaped values.
"""

from __future__ import annotations

import hashlib
import json
import re
from typing import Any

JOURNAL_SCHEMA_VERSION = "ariadne.operation_journal.v1"
GATE_ATTEMPT_SCHEMA_VERSION = "ariadne.gate_attempt.v1"
REFINEMENT_PROPOSAL_SCHEMA_VERSION = "ariadne.refinement_proposal.v1"
REFINEMENT_PROMOTION_SCHEMA_VERSION = "ariadne.refinement_promotion.v1"
DECISION_SCHEMA_VERSION = "ariadne.continuity_refinement_decision.v1"

JOURNAL_STATES = {"received", "running", "completed", "failed", "uncertain", "revoked"}
GATE_RESULTS = {"deterministic_pass", "deterministic_failure", "uncertain"}
REFINEMENT_KINDS = {
    "prompt_note",
    "memory_note",
    "skill_description",
    "subagent_spec",
    "policy_note",
}
REFINEMENT_SCOPES = {"local", "global"}
PROMOTION_DECISIONS = {"promote", "reject", "rollback"}
SOL_PROMOTION_AUTHORITY = "sol"
CURSOR_REJECT_REASONS = {
    "stale_generation",
    "future_generation",
    "missing_sequence",
    "out_of_range",
}
GATE_REASONS = {
    "no_exact_prior_attempt",
    "exact_prior_pass",
    "exact_prior_failure",
    "exact_prior_uncertain",
}

_IDENTIFIER = re.compile(r"^[a-z][a-z0-9._-]{0,127}$")
_GIT_OBJECT_ID = re.compile(r"^[0-9a-f]{40}$")
_SHA256_DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")
_CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


def _object(value: object, *, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a JSON object")
    return value


def _exact_keys(value: dict[str, Any], expected: set[str], *, label: str) -> None:
    if set(value) != expected:
        raise ValueError(
            f"{label} keys must be exact: expected={sorted(expected)!r} "
            f"observed={sorted(value)!r}"
        )


def _canonical_bytes(value: object) -> bytes:
    return (
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    ).encode("utf-8")


def sha256_digest(value: object) -> str:
    """Return the canonical lowercase ``sha256:...`` digest of a JSON value."""
    return "sha256:" + hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _text(value: object, *, label: str, maximum: int = 500) -> str:
    if (
        not isinstance(value, str)
        or not value.strip()
        or value != value.strip()
        or len(value) > maximum
        or "\r" in value
        or "\n" in value
        or _CONTROL_CHARS.search(value) is not None
    ):
        raise ValueError(f"{label} must be bounded non-empty single-line text")
    return value


def _body_text(value: object, *, label: str, maximum: int = 4000) -> str:
    if (
        not isinstance(value, str)
        or not value.strip()
        or value != value.strip()
        or len(value) > maximum
        or "\r" in value
        or _CONTROL_CHARS.search(value) is not None
    ):
        raise ValueError(f"{label} must be bounded non-empty text without CR/control")
    return value


def _identifier(value: object, *, label: str) -> str:
    if not isinstance(value, str) or _IDENTIFIER.fullmatch(value) is None:
        raise ValueError(f"{label} is not a valid lowercase identifier")
    return value


def _git_object_id(value: object, *, label: str) -> str:
    if not isinstance(value, str) or _GIT_OBJECT_ID.fullmatch(value) is None:
        raise ValueError(f"{label} must be a lowercase full Git object id")
    return value


def _sha256_digest(value: object, *, label: str) -> str:
    if not isinstance(value, str) or _SHA256_DIGEST.fullmatch(value) is None:
        raise ValueError(f"{label} must be a lowercase sha256 digest")
    return value


def _positive_int(value: object, *, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError(f"{label} must be a positive integer")
    return value


def _optional_reason(value: object, *, label: str, maximum: int = 500) -> str | None:
    if value is not None:
        return _text(value, label=label, maximum=maximum)
    return None


def _decision(decision: str, **extra: object) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "schema_version": DECISION_SCHEMA_VERSION,
        "decision": decision,
    }
    payload.update(extra)
    return payload


# ---------------------------------------------------------------------------
# Operation journal
# ---------------------------------------------------------------------------


def _command_states(events: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    by_command: dict[str, list[dict[str, Any]]] = {}
    for event in events:
        by_command.setdefault(event["command_id"], []).append(event)
    states: dict[str, dict[str, Any]] = {}
    for command_id, command_events in by_command.items():
        ordered = sorted(command_events, key=lambda e: (e["generation"], e["sequence"]))
        first = ordered[0]
        last = ordered[-1]
        states[command_id] = {
            "command_id": command_id,
            "request_digest": first["request_digest"],
            "state": last["state"],
            "result_digest": last["result_digest"],
            "generation": last["generation"],
        }
    return states


def _check_transition(
    command_id: str,
    from_state: str,
    to_state: str,
    *,
    from_generation: int,
    to_generation: int,
) -> None:
    if from_state == "received":
        if to_state in {"running", "completed", "failed", "revoked"}:
            return
        if to_state == "uncertain":
            if to_generation == from_generation + 1:
                return  # only generation recovery may mark a received command uncertain
            raise ValueError(
                f"command {command_id} received->uncertain requires generation recovery"
            )
        raise ValueError(
            f"command {command_id} illegal transition {from_state}->{to_state}"
        )
    if from_state == "running":
        if to_state in {"completed", "failed", "uncertain", "revoked"}:
            if to_generation != from_generation and not (
                to_state == "uncertain" and to_generation == from_generation + 1
            ):
                raise ValueError(
                    f"command {command_id} cross-generation transition is not exact recovery"
                )
            return
        raise ValueError(
            f"command {command_id} illegal transition {from_state}->{to_state}"
        )
    raise ValueError(
        f"command {command_id} illegal transition {from_state}->{to_state}"
    )


def _validate_sequence_contiguity(events: list[dict[str, Any]]) -> None:
    by_generation: dict[int, list[int]] = {}
    for event in events:
        by_generation.setdefault(event["generation"], []).append(event["sequence"])
    for generation, sequences in by_generation.items():
        if sorted(sequences) != list(range(1, len(sequences) + 1)):
            raise ValueError(
                f"generation {generation} sequences are not contiguous from one"
            )


def _validate_command_transitions(events: list[dict[str, Any]]) -> None:
    by_command: dict[str, list[dict[str, Any]]] = {}
    for event in events:
        by_command.setdefault(event["command_id"], []).append(event)
    for command_id, command_events in by_command.items():
        ordered = sorted(command_events, key=lambda e: (e["generation"], e["sequence"]))
        first = ordered[0]
        if first["state"] != "received":
            raise ValueError(f"command {command_id} first event must be received")
        for previous, current in zip(ordered, ordered[1:]):
            _check_transition(
                command_id,
                previous["state"],
                current["state"],
                from_generation=previous["generation"],
                to_generation=current["generation"],
            )
        if len({e["request_digest"] for e in ordered}) != 1:
            raise ValueError(f"command {command_id} request digest is not stable")


def validate_operation_journal(value: object) -> dict[str, Any]:
    """Validate and normalize an operation journal, or fail closed."""
    journal = _object(value, label="operation journal")
    _exact_keys(
        journal,
        {"schema_version", "operation_id", "generation", "events"},
        label="operation journal",
    )
    if journal["schema_version"] != JOURNAL_SCHEMA_VERSION:
        raise ValueError("operation journal schema version is not admitted")
    operation_id = _identifier(journal["operation_id"], label="operation_id")
    generation = _positive_int(journal["generation"], label="generation")
    raw_events = journal["events"]
    if not isinstance(raw_events, list) or not 1 <= len(raw_events) <= 4096:
        raise ValueError("operation journal must contain 1..4096 events")

    seen_event_ids: set[str] = set()
    normalized_events: list[dict[str, Any]] = []
    for index, raw_event in enumerate(raw_events):
        event = _object(raw_event, label=f"event[{index}]")
        _exact_keys(
            event,
            {
                "event_id",
                "generation",
                "sequence",
                "command_id",
                "request_digest",
                "state",
                "result_digest",
            },
            label=f"event[{index}]",
        )
        event_id = _identifier(event["event_id"], label=f"event[{index}].event_id")
        if event_id in seen_event_ids:
            raise ValueError(f"event[{index}] event_id is duplicated")
        seen_event_ids.add(event_id)
        event_generation = _positive_int(
            event["generation"], label=f"event[{index}].generation"
        )
        if event_generation > generation:
            raise ValueError(f"event[{index}] generation is in the future")
        sequence = _positive_int(event["sequence"], label=f"event[{index}].sequence")
        command_id = _identifier(
            event["command_id"], label=f"event[{index}].command_id"
        )
        request_digest = _sha256_digest(
            event["request_digest"], label=f"event[{index}].request_digest"
        )
        state = event["state"]
        if state not in JOURNAL_STATES:
            raise ValueError(f"event[{index}] state is not admitted")
        result_digest = event["result_digest"]
        if result_digest is not None:
            result_digest = _sha256_digest(
                result_digest, label=f"event[{index}].result_digest"
            )
        if state == "completed" and result_digest is None:
            raise ValueError(
                f"event[{index}] completed requires an exact result digest"
            )
        if state != "completed" and result_digest is not None:
            raise ValueError(
                f"event[{index}] non-completed states forbid a result digest"
            )
        normalized_events.append(
            {
                "event_id": event_id,
                "generation": event_generation,
                "sequence": sequence,
                "command_id": command_id,
                "request_digest": request_digest,
                "state": state,
                "result_digest": result_digest,
            }
        )

    coordinates = [
        (event["generation"], event["sequence"]) for event in normalized_events
    ]
    if coordinates != sorted(coordinates):
        raise ValueError("journal events must remain in append-only coordinate order")
    _validate_sequence_contiguity(normalized_events)
    _validate_command_transitions(normalized_events)
    for command in _command_states(normalized_events).values():
        if command["generation"] < generation and command["state"] in {
            "received",
            "running",
        }:
            raise ValueError(
                "unfinished command from a retired generation requires an uncertain recovery event"
            )
    return {
        "schema_version": JOURNAL_SCHEMA_VERSION,
        "operation_id": operation_id,
        "generation": generation,
        "events": normalized_events,
    }


def assess_command_submission(
    value: object, *, command_id: str, request_digest: str
) -> dict[str, Any]:
    """Decide whether a submitted command is new, a replay, a conflict or live."""
    journal = validate_operation_journal(value)
    command_id = _identifier(command_id, label="command_id")
    request_digest = _sha256_digest(request_digest, label="request_digest")
    states = _command_states(journal["events"])
    recorded = states.get(command_id)
    if recorded is None:
        return _decision(
            "new_command",
            command_id=command_id,
            request_digest=request_digest,
            recorded_result_digest=None,
            reasons=[],
        )
    if recorded["request_digest"] != request_digest:
        return _decision(
            "conflict",
            command_id=command_id,
            request_digest=request_digest,
            recorded_result_digest=None,
            reasons=["differing_request_under_same_command_id"],
        )
    if recorded["state"] == "completed":
        return _decision(
            "replay_completed",
            command_id=command_id,
            request_digest=request_digest,
            recorded_result_digest=recorded["result_digest"],
            reasons=[],
        )
    if recorded["state"] in {"received", "running"}:
        return _decision(
            "already_in_progress",
            command_id=command_id,
            request_digest=request_digest,
            recorded_result_digest=None,
            reasons=["live_command_in_progress"],
        )
    # failed, revoked and uncertain never auto-replay.
    return _decision(
        "requires_new_generation",
        command_id=command_id,
        request_digest=request_digest,
        recorded_result_digest=None,
        reasons=["non_completed_terminal_state_requires_new_generation"],
    )


def admit_command_event(
    value: object,
    *,
    event_id: str,
    command_id: str,
    request_digest: str,
    state: str,
    result_digest: str | None = None,
) -> dict[str, Any]:
    """Return a new journal with one appended command event, or fail closed."""
    journal = validate_operation_journal(value)
    event_id = _identifier(event_id, label="event_id")
    command_id = _identifier(command_id, label="command_id")
    request_digest = _sha256_digest(request_digest, label="request_digest")
    if state not in JOURNAL_STATES:
        raise ValueError("event state is not admitted")
    if result_digest is not None:
        result_digest = _sha256_digest(result_digest, label="result_digest")
    if state == "completed" and result_digest is None:
        raise ValueError("completed requires an exact result digest")
    if state != "completed" and result_digest is not None:
        raise ValueError("non-completed states forbid a result digest")

    states = _command_states(journal["events"])
    generation = journal["generation"]
    max_sequence = max(
        (e["sequence"] for e in journal["events"] if e["generation"] == generation),
        default=0,
    )

    if state == "received":
        if command_id in states:
            raise ValueError("a command can only be received once")
    else:
        if command_id not in states:
            raise ValueError("first event for a command must be received")
        previous = states[command_id]
        _check_transition(
            command_id,
            previous["state"],
            state,
            from_generation=previous["generation"],
            to_generation=generation,
        )

    new_event = {
        "event_id": event_id,
        "generation": generation,
        "sequence": max_sequence + 1,
        "command_id": command_id,
        "request_digest": request_digest,
        "state": state,
        "result_digest": result_digest,
    }
    return validate_operation_journal(
        {
            "schema_version": JOURNAL_SCHEMA_VERSION,
            "operation_id": journal["operation_id"],
            "generation": generation,
            "events": journal["events"] + [new_event],
        }
    )


def recover_generation(value: object) -> dict[str, Any]:
    """Advance the journal generation exactly once and mark unfinished work uncertain.

    Unfinished (``received`` or ``running``) commands receive one ``uncertain``
    event in the new generation; completed, failed, revoked and already-uncertain
    outcomes remain immutable. Nothing is executed or replayed.
    """
    journal = validate_operation_journal(value)
    new_generation = journal["generation"] + 1
    states = _command_states(journal["events"])
    unfinished = sorted(
        command_id
        for command_id, info in states.items()
        if info["state"] in {"received", "running"}
    )
    new_events = list(journal["events"])
    used_ids = {e["event_id"] for e in new_events}
    for index, command_id in enumerate(unfinished, start=1):
        event_id = f"evt-recovery-{new_generation}-{index}"
        salt = 0
        while event_id in used_ids:
            salt += 1
            event_id = f"evt-recovery-{new_generation}-{index}-{salt}"
        used_ids.add(event_id)
        new_events.append(
            {
                "event_id": event_id,
                "generation": new_generation,
                "sequence": index,
                "command_id": command_id,
                "request_digest": states[command_id]["request_digest"],
                "state": "uncertain",
                "result_digest": None,
            }
        )
    return validate_operation_journal(
        {
            "schema_version": JOURNAL_SCHEMA_VERSION,
            "operation_id": journal["operation_id"],
            "generation": new_generation,
            "events": new_events,
        }
    )


def assess_cursor(value: object, *, generation: int, sequence: int) -> dict[str, Any]:
    """Decide whether a ``(generation, sequence)`` cursor is usable or needs a snapshot."""
    journal = validate_operation_journal(value)
    if isinstance(generation, bool) or not isinstance(generation, int):
        raise ValueError("cursor generation must be an integer")
    if isinstance(sequence, bool) or not isinstance(sequence, int):
        raise ValueError("cursor sequence must be an integer")
    if generation < 1 or sequence < 1:
        return _decision(
            "snapshot_required",
            reason="out_of_range",
            generation=generation,
            sequence=sequence,
            reasons=["out_of_range_cursor_requires_snapshot"],
        )
    current = journal["generation"]
    if generation < current:
        return _decision(
            "snapshot_required",
            reason="stale_generation",
            generation=generation,
            sequence=sequence,
            reasons=["retired_generation_cursor_requires_snapshot"],
        )
    if generation > current:
        return _decision(
            "snapshot_required",
            reason="future_generation",
            generation=generation,
            sequence=sequence,
            reasons=["future_generation_cursor_requires_snapshot"],
        )
    present = {
        e["sequence"] for e in journal["events"] if e["generation"] == generation
    }
    if sequence not in present:
        if present and sequence > max(present):
            reason = "out_of_range"
        else:
            reason = "missing_sequence"
        return _decision(
            "snapshot_required",
            reason=reason,
            generation=generation,
            sequence=sequence,
            reasons=[f"{reason}_cursor_requires_snapshot"],
        )
    later = sorted(
        (
            e
            for e in journal["events"]
            if e["generation"] == generation and e["sequence"] > sequence
        ),
        key=lambda e: e["sequence"],
    )
    if later:
        return _decision(
            "events_available",
            reason="same_generation",
            generation=generation,
            sequence=sequence,
            later_events=later,
            reasons=[],
        )
    return _decision(
        "up_to_date",
        reason="same_generation",
        generation=generation,
        sequence=sequence,
        later_events=[],
        reasons=[],
    )


# ---------------------------------------------------------------------------
# Unchanged deterministic gate
# ---------------------------------------------------------------------------


def _validate_fingerprint(value: object) -> dict[str, Any]:
    fingerprint = _object(value, label="gate fingerprint")
    _exact_keys(
        fingerprint,
        {
            "gate_id",
            "candidate_source_head",
            "candidate_source_tree",
            "evidence_set_digest",
            "command_manifest_digest",
            "relevant_input_digest",
            "toolchain_digest",
        },
        label="gate fingerprint",
    )
    return {
        "gate_id": _identifier(fingerprint["gate_id"], label="gate_id"),
        "candidate_source_head": _git_object_id(
            fingerprint["candidate_source_head"], label="candidate_source_head"
        ),
        "candidate_source_tree": _git_object_id(
            fingerprint["candidate_source_tree"], label="candidate_source_tree"
        ),
        "evidence_set_digest": _sha256_digest(
            fingerprint["evidence_set_digest"], label="evidence_set_digest"
        ),
        "command_manifest_digest": _sha256_digest(
            fingerprint["command_manifest_digest"], label="command_manifest_digest"
        ),
        "relevant_input_digest": _sha256_digest(
            fingerprint["relevant_input_digest"], label="relevant_input_digest"
        ),
        "toolchain_digest": _sha256_digest(
            fingerprint["toolchain_digest"], label="toolchain_digest"
        ),
    }


def validate_gate_attempt(value: object) -> dict[str, Any]:
    """Validate and normalize one gate attempt, or fail closed."""
    attempt = _object(value, label="gate attempt")
    _exact_keys(
        attempt,
        {"schema_version", "attempt_id", "fingerprint", "result", "generation"},
        label="gate attempt",
    )
    if attempt["schema_version"] != GATE_ATTEMPT_SCHEMA_VERSION:
        raise ValueError("gate attempt schema version is not admitted")
    attempt_id = _identifier(attempt["attempt_id"], label="attempt_id")
    fingerprint = _validate_fingerprint(attempt["fingerprint"])
    result = attempt["result"]
    if result not in GATE_RESULTS:
        raise ValueError("gate result is not admitted")
    generation = _positive_int(attempt["generation"], label="generation")
    return {
        "schema_version": GATE_ATTEMPT_SCHEMA_VERSION,
        "attempt_id": attempt_id,
        "fingerprint": fingerprint,
        "result": result,
        "generation": generation,
    }


def assess_gate(*, prior_attempts: object, fingerprint: object) -> dict[str, Any]:
    """Decide whether to reuse, diagnose, resolve or run a deterministic gate."""
    current = _validate_fingerprint(fingerprint)
    if not isinstance(prior_attempts, list):
        raise ValueError("prior_attempts must be a list")
    normalized_prior = [validate_gate_attempt(attempt) for attempt in prior_attempts]
    attempt_ids = [attempt["attempt_id"] for attempt in normalized_prior]
    if len(set(attempt_ids)) != len(attempt_ids):
        raise ValueError("prior gate attempt ids must be unique")
    matching = [
        attempt for attempt in normalized_prior if attempt["fingerprint"] == current
    ]
    if not matching:
        return _decision(
            "run_gate",
            reason="no_exact_prior_attempt",
            gate_id=current["gate_id"],
            matched_attempt_id=None,
            reasons=[],
        )
    generations = [attempt["generation"] for attempt in matching]
    if len(set(generations)) != len(generations):
        raise ValueError("exact gate attempts have ambiguous duplicate generations")
    if len({attempt["result"] for attempt in matching}) != 1:
        raise ValueError("exact gate attempts contain conflicting terminal evidence")
    latest = max(matching, key=lambda attempt: attempt["generation"])
    if latest["result"] == "deterministic_pass":
        decision = "reuse_exact_pass"
        reason = "exact_prior_pass"
    elif latest["result"] == "deterministic_failure":
        decision = "diagnose_without_rerun"
        reason = "exact_prior_failure"
    else:
        decision = "resolve_uncertainty"
        reason = "exact_prior_uncertain"
    return _decision(
        decision,
        reason=reason,
        gate_id=current["gate_id"],
        matched_attempt_id=latest["attempt_id"],
        reasons=[],
    )


# ---------------------------------------------------------------------------
# Refinement proposal and promotion
# ---------------------------------------------------------------------------


def validate_refinement_proposal(value: object) -> dict[str, Any]:
    """Validate and normalize a quarantined refinement proposal, or fail closed."""
    proposal = _object(value, label="refinement proposal")
    _exact_keys(
        proposal,
        {
            "schema_version",
            "proposal_id",
            "kind",
            "scope",
            "title",
            "body",
            "base_state_digest",
            "candidate_digest",
            "source_evidence_digests",
            "source_head",
            "proposer",
            "validation_manifest_digest",
            "status",
            "generation",
        },
        label="refinement proposal",
    )
    if proposal["schema_version"] != REFINEMENT_PROPOSAL_SCHEMA_VERSION:
        raise ValueError("refinement proposal schema version is not admitted")
    proposal_id = _identifier(proposal["proposal_id"], label="proposal_id")
    kind = proposal["kind"]
    if kind not in REFINEMENT_KINDS:
        raise ValueError("refinement kind is not admitted")
    scope = proposal["scope"]
    if scope not in REFINEMENT_SCOPES:
        raise ValueError("refinement scope is not admitted")
    title = _text(proposal["title"], label="title", maximum=200)
    body = _body_text(proposal["body"], label="body")
    base_state_digest = _sha256_digest(
        proposal["base_state_digest"], label="base_state_digest"
    )
    candidate_digest = _sha256_digest(
        proposal["candidate_digest"], label="candidate_digest"
    )
    raw_evidence = proposal["source_evidence_digests"]
    if not isinstance(raw_evidence, list) or not 1 <= len(raw_evidence) <= 64:
        raise ValueError("source_evidence_digests must contain 1..64 digests")
    evidence = [
        _sha256_digest(digest, label="source_evidence_digest")
        for digest in raw_evidence
    ]
    if len(set(evidence)) != len(evidence):
        raise ValueError("source_evidence_digests must be unique")
    source_head = _git_object_id(proposal["source_head"], label="source_head")
    proposer = _text(proposal["proposer"], label="proposer", maximum=200)
    validation_manifest_digest = _sha256_digest(
        proposal["validation_manifest_digest"], label="validation_manifest_digest"
    )
    status = proposal["status"]
    if status != "quarantined":
        raise ValueError("new refinement proposals must begin quarantined")
    generation = _positive_int(proposal["generation"], label="generation")
    return {
        "schema_version": REFINEMENT_PROPOSAL_SCHEMA_VERSION,
        "proposal_id": proposal_id,
        "kind": kind,
        "scope": scope,
        "title": title,
        "body": body,
        "base_state_digest": base_state_digest,
        "candidate_digest": candidate_digest,
        "source_evidence_digests": evidence,
        "source_head": source_head,
        "proposer": proposer,
        "validation_manifest_digest": validation_manifest_digest,
        "status": status,
        "generation": generation,
    }


def validate_refinement_promotion(value: object) -> dict[str, Any]:
    """Validate and normalize a refinement promotion decision record."""
    record = _object(value, label="refinement promotion record")
    _exact_keys(
        record,
        {
            "schema_version",
            "promotion_id",
            "proposal_id",
            "proposal_digest",
            "decision",
            "generation",
            "scope",
            "candidate_digest",
            "base_state_digest",
            "source_head",
            "source_evidence_digests",
            "validation_manifest_digest",
            "validation_result",
            "proposer",
            "promoter",
            "independent_reviewer",
            "promoted_decision_id",
            "reasons",
        },
        label="refinement promotion record",
    )
    if record["schema_version"] != REFINEMENT_PROMOTION_SCHEMA_VERSION:
        raise ValueError("refinement promotion schema version is not admitted")
    promotion_id = _identifier(record["promotion_id"], label="promotion_id")
    proposal_id = _identifier(record["proposal_id"], label="proposal_id")
    proposal_digest = _sha256_digest(record["proposal_digest"], label="proposal_digest")
    decision = record["decision"]
    if decision not in PROMOTION_DECISIONS:
        raise ValueError("refinement promotion decision is not admitted")
    generation = _positive_int(record["generation"], label="generation")
    scope = record["scope"]
    if scope not in REFINEMENT_SCOPES:
        raise ValueError("refinement promotion scope is not admitted")
    candidate_digest = _sha256_digest(
        record["candidate_digest"], label="candidate_digest"
    )
    base_state_digest = _sha256_digest(
        record["base_state_digest"], label="base_state_digest"
    )
    source_head = _git_object_id(record["source_head"], label="source_head")
    raw_source_evidence = record["source_evidence_digests"]
    if (
        not isinstance(raw_source_evidence, list)
        or not 1 <= len(raw_source_evidence) <= 64
    ):
        raise ValueError("source_evidence_digests must contain 1..64 digests")
    source_evidence_digests = [
        _sha256_digest(digest, label="source_evidence_digest")
        for digest in raw_source_evidence
    ]
    if len(set(source_evidence_digests)) != len(source_evidence_digests):
        raise ValueError("source_evidence_digests must be unique")
    validation_manifest_digest = _sha256_digest(
        record["validation_manifest_digest"], label="validation_manifest_digest"
    )
    validation_result = record["validation_result"]
    if validation_result not in {"pass", "fail"}:
        raise ValueError("refinement promotion validation_result is not admitted")
    proposer = _text(record["proposer"], label="proposer", maximum=200)
    promoter = _text(record["promoter"], label="promoter", maximum=200)
    independent_reviewer = _optional_reason(
        record["independent_reviewer"], label="independent_reviewer", maximum=200
    )
    promoted_decision_id = record["promoted_decision_id"]
    if promoted_decision_id is not None:
        promoted_decision_id = _identifier(
            promoted_decision_id, label="promoted_decision_id"
        )
    raw_reasons = record["reasons"]
    if not isinstance(raw_reasons, list) or len(raw_reasons) > 64:
        raise ValueError("reasons must contain 0..64 entries")
    reasons = [_text(reason, label="reason", maximum=500) for reason in raw_reasons]
    if len(set(reasons)) != len(reasons):
        raise ValueError("reasons must be unique")

    if decision == "rollback":
        if promoted_decision_id is None:
            raise ValueError("rollback must name the exact promoted decision")
    else:
        if promoted_decision_id is not None:
            raise ValueError("promote/reject must not carry a promoted_decision_id")

    if decision == "promote":
        if validation_result != "pass":
            raise ValueError("promotion requires a deterministic validation pass")
        if reasons:
            raise ValueError("promotion must not carry rejection reasons")
        if promoter != SOL_PROMOTION_AUTHORITY:
            raise ValueError("promotion requires exact Sol authority")
        if promoter == proposer:
            raise ValueError("the proposer cannot promote its own proposal")
        if scope == "global":
            if independent_reviewer is None:
                raise ValueError("global promotion requires independent review")
            if independent_reviewer in {proposer, promoter}:
                raise ValueError(
                    "global promotion identities must be pairwise distinct"
                )
    elif decision == "reject":
        if not reasons:
            raise ValueError("rejection must carry at least one reason")
    else:
        if validation_result != "pass":
            raise ValueError("rollback validation result must be pass")
        if reasons:
            raise ValueError("rollback must not carry rejection reasons")
        if promoter != SOL_PROMOTION_AUTHORITY:
            raise ValueError("rollback requires exact Sol authority")
        if independent_reviewer is not None:
            raise ValueError("rollback must not claim an independent review")

    return {
        "schema_version": REFINEMENT_PROMOTION_SCHEMA_VERSION,
        "promotion_id": promotion_id,
        "proposal_id": proposal_id,
        "proposal_digest": proposal_digest,
        "decision": decision,
        "generation": generation,
        "scope": scope,
        "candidate_digest": candidate_digest,
        "base_state_digest": base_state_digest,
        "source_head": source_head,
        "source_evidence_digests": source_evidence_digests,
        "validation_manifest_digest": validation_manifest_digest,
        "validation_result": validation_result,
        "proposer": proposer,
        "promoter": promoter,
        "independent_reviewer": independent_reviewer,
        "promoted_decision_id": promoted_decision_id,
        "reasons": reasons,
    }


def _promotion_record(
    proposal: dict[str, Any],
    *,
    promotion_id: str,
    decision: str,
    promoter: str,
    independent_reviewer: str | None,
    promoted_decision_id: str | None = None,
    validation_result: str,
    reasons: list[str],
) -> dict[str, Any]:
    return {
        "schema_version": REFINEMENT_PROMOTION_SCHEMA_VERSION,
        "promotion_id": _identifier(promotion_id, label="promotion_id"),
        "proposal_id": proposal["proposal_id"],
        "proposal_digest": sha256_digest(proposal),
        "decision": decision,
        "generation": proposal["generation"],
        "scope": proposal["scope"],
        "candidate_digest": proposal["candidate_digest"],
        "base_state_digest": proposal["base_state_digest"],
        "source_head": proposal["source_head"],
        "source_evidence_digests": proposal["source_evidence_digests"],
        "validation_manifest_digest": proposal["validation_manifest_digest"],
        "validation_result": validation_result,
        "proposer": proposal["proposer"],
        "promoter": _text(promoter, label="promoter", maximum=200),
        "independent_reviewer": independent_reviewer,
        "promoted_decision_id": promoted_decision_id,
        "reasons": list(reasons),
    }


def assess_promotion(
    proposal_value: object,
    *,
    validation_manifest_digest: str,
    validation_result: str,
    candidate_digest: str,
    base_state_digest: str,
    source_head: str,
    promoter: str,
    independent_reviewer: str | None = None,
    prior_decisions: object,
) -> dict[str, Any]:
    """Assess promotion of one quarantined proposal and emit a typed decision record."""
    proposal = validate_refinement_proposal(proposal_value)
    validation_manifest_digest = _sha256_digest(
        validation_manifest_digest, label="validation_manifest_digest"
    )
    candidate_digest = _sha256_digest(candidate_digest, label="candidate_digest")
    base_state_digest = _sha256_digest(base_state_digest, label="base_state_digest")
    source_head = _git_object_id(source_head, label="source_head")
    history = _validate_decision_history(prior_decisions)
    if any(record["proposal_id"] == proposal["proposal_id"] for record in history):
        raise ValueError("proposal already has an immutable terminal decision")
    if history and proposal["generation"] != history[-1]["generation"] + 1:
        raise ValueError("proposal must use the next immutable decision generation")
    promotion_id = f"prom-{proposal['proposal_id']}"
    reasons: list[str] = []

    if validation_manifest_digest != proposal["validation_manifest_digest"]:
        reasons.append("validation_manifest_mismatch")
    if validation_result != "pass":
        reasons.append("validation_not_pass")
    if candidate_digest != proposal["candidate_digest"]:
        reasons.append("candidate_binding_mismatch")
    if base_state_digest != proposal["base_state_digest"]:
        reasons.append("base_state_binding_mismatch")
    if source_head != proposal["source_head"]:
        reasons.append("source_head_binding_mismatch")
    if not isinstance(promoter, str) or not promoter.strip():
        reasons.append("missing_promoter")
    else:
        if promoter == proposal["proposer"]:
            reasons.append("promoter_is_proposer")
        if promoter != SOL_PROMOTION_AUTHORITY:
            reasons.append("promoter_not_sol_authority")

    normalized_reviewer: str | None = None
    if independent_reviewer is not None:
        normalized_reviewer = _text(
            independent_reviewer, label="independent_reviewer", maximum=200
        )
    if proposal["scope"] == "global":
        if normalized_reviewer is None:
            reasons.append("missing_independent_reviewer")
        elif normalized_reviewer == proposal["proposer"]:
            reasons.append("reviewer_is_proposer")
        elif (
            isinstance(promoter, str)
            and promoter.strip()
            and normalized_reviewer == promoter
        ):
            reasons.append("reviewer_is_promoter")

    if reasons:
        decision = "reject"
    else:
        decision = "promote"
    return validate_refinement_promotion(
        _promotion_record(
            proposal,
            promotion_id=promotion_id,
            decision=decision,
            promoter=(
                promoter
                if isinstance(promoter, str) and promoter.strip()
                else "unknown"
            ),
            independent_reviewer=normalized_reviewer,
            validation_result="pass" if validation_result == "pass" else "fail",
            reasons=reasons,
        )
    )


def assess_rejection(
    proposal_value: object,
    *,
    authority: str,
    reason: str,
    prior_decisions: object,
) -> dict[str, Any]:
    """Emit a first-class terminal rejection decision record for a proposal."""
    proposal = validate_refinement_proposal(proposal_value)
    authority = _text(authority, label="authority", maximum=200)
    reason = _text(reason, label="reason", maximum=500)
    history = _validate_decision_history(prior_decisions)
    if any(record["proposal_id"] == proposal["proposal_id"] for record in history):
        raise ValueError("proposal already has an immutable terminal decision")
    if history and proposal["generation"] != history[-1]["generation"] + 1:
        raise ValueError("proposal must use the next immutable decision generation")
    return validate_refinement_promotion(
        _promotion_record(
            proposal,
            promotion_id=f"rej-{proposal['proposal_id']}",
            decision="reject",
            promoter=authority,
            independent_reviewer=None,
            validation_result="fail",
            reasons=[reason],
        )
    )


def assess_rollback(
    *,
    promoted_record: object,
    decision_history: object,
    current_state_digest: str,
    authority: str,
) -> dict[str, Any]:
    """Emit a first-class terminal rollback decision creating a new generation.

    Rollback names the exact promoted decision and its recorded base digest. It
    never infers or rewrites content, and it advances the immutable generation.
    """
    target = validate_refinement_promotion(promoted_record)
    if target["decision"] != "promote":
        raise ValueError("rollback target must be an exact promoted decision")
    history = _validate_decision_history(decision_history)
    matching = [
        record for record in history if record["promotion_id"] == target["promotion_id"]
    ]
    if matching != [target]:
        raise ValueError("rollback target must occur exactly once in decision history")
    if any(
        record["decision"] == "rollback"
        and record["promoted_decision_id"] == target["promotion_id"]
        for record in history
    ):
        raise ValueError("promoted decision has already been rolled back")
    if any(
        record["generation"] > target["generation"]
        and record["decision"] in {"promote", "rollback"}
        for record in history
    ):
        raise ValueError("intervening decision makes rollback target stale")
    current_state_digest = _sha256_digest(
        current_state_digest, label="current_state_digest"
    )
    if current_state_digest != target["candidate_digest"]:
        raise ValueError("current state does not match promoted candidate")
    authority = _text(authority, label="authority", maximum=200)
    if authority != SOL_PROMOTION_AUTHORITY:
        raise ValueError("rollback requires exact Sol authority")
    next_generation = max(record["generation"] for record in history) + 1
    return validate_refinement_promotion(
        {
            "schema_version": REFINEMENT_PROMOTION_SCHEMA_VERSION,
            "promotion_id": f"rb-{target['promotion_id']}",
            "proposal_id": target["proposal_id"],
            "proposal_digest": target["proposal_digest"],
            "decision": "rollback",
            "generation": next_generation,
            "scope": target["scope"],
            "candidate_digest": target["base_state_digest"],
            "base_state_digest": current_state_digest,
            "source_head": target["source_head"],
            "source_evidence_digests": target["source_evidence_digests"],
            "validation_manifest_digest": target["validation_manifest_digest"],
            "validation_result": "pass",
            "proposer": target["proposer"],
            "promoter": authority,
            "independent_reviewer": None,
            "promoted_decision_id": target["promotion_id"],
            "reasons": [],
        }
    )


def _validate_decision_history(value: object) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        raise ValueError("decision history must be a list")
    records = [validate_refinement_promotion(record) for record in value]
    promotion_ids = [record["promotion_id"] for record in records]
    if len(set(promotion_ids)) != len(promotion_ids):
        raise ValueError("decision history promotion ids must be unique")
    generations = [record["generation"] for record in records]
    if len(set(generations)) != len(generations):
        raise ValueError("decision history generations must be unique")
    if generations != sorted(generations):
        raise ValueError("decision history must remain in generation order")
    return records
