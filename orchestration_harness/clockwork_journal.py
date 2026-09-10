from dataclasses import dataclass as _dataclass
from enum import Enum as _Enum, unique as _unique
import hashlib as _hashlib
import json as _json
from orchestration_harness.clockwork_state import (
    ClockworkCommand as _ClockworkCommand,
    ClockworkEvent as _ClockworkEvent,
    ClockworkState as _ClockworkState,
    InvalidTransition as _InvalidTransition,
    TransitionResult as _TransitionResult,
    canonical_bytes as _canonical_bytes,
    transition as _transition,
)

JOURNAL_ENTRY_SCHEMA_VERSION = "ariadne.clockwork_journal_entry.v1"
REPLAY_SCHEMA_VERSION = "ariadne.clockwork_replay.v1"
GENESIS_PREVIOUS_DIGEST = "sha256:" + "0" * 64


@_unique
class JournalRejection(_Enum):
    WRONG_SCHEMA = "wrong_schema"
    FOREIGN_TYPE = "foreign_type"
    INVALID_SEQUENCE = "invalid_sequence"
    SEQUENCE_GAP = "sequence_gap"
    DUPLICATE_SEQUENCE = "duplicate_sequence"
    REORDERED_ENTRY = "reordered_entry"
    PREVIOUS_DIGEST_MISMATCH = "previous_digest_mismatch"
    MALFORMED_DIGEST = "malformed_digest"
    ENTRY_BYTES_TAMPERED = "entry_bytes_tampered"
    STORED_RESULT_MISMATCH = "stored_result_mismatch"
    UNRECOGNISED_INVALID_TRANSITION_CODE = "unrecognised_invalid_transition_code"
    INVALID_TRANSITION_REPRESENTED_AS_SUCCESS = (
        "invalid_transition_represented_as_success"
    )
    VALID_TRANSITION_REPRESENTED_AS_INVALID = "valid_transition_represented_as_invalid"
    MUTABLE_INPUT_COLLECTION = "mutable_input_collection"


@_dataclass(frozen=True, slots=True)
class JournalEntry:
    schema_version: str
    sequence: int
    previous_digest: str
    event: _ClockworkEvent
    command: _ClockworkCommand
    stored_result: _TransitionResult
    digest: str


@_dataclass(frozen=True, slots=True)
class ReplayResult:
    schema_version: str
    state: _ClockworkState
    next_sequence: int
    previous_digest: str
    validated_journal: tuple[JournalEntry, ...]
    rejection: JournalRejection | None


def _is_digest(value: object) -> bool:
    return (
        type(value) is str
        and len(value) == 71
        and value.startswith("sha256:")
        and all(character in "0123456789abcdef" for character in value[7:])
    )


def _closed_result(
    state: _ClockworkState,
    next_sequence: int,
    previous_digest: str,
    validated_journal: tuple[JournalEntry, ...],
    rejection: JournalRejection | None,
) -> ReplayResult:
    return ReplayResult(
        REPLAY_SCHEMA_VERSION,
        state,
        next_sequence,
        previous_digest,
        validated_journal,
        rejection,
    )


def canonical_entry_bytes(entry: JournalEntry) -> bytes:
    if type(entry) is not JournalEntry:
        raise TypeError("invalid_clockwork_journal_entry")
    if not (
        type(entry.schema_version) is str
        and type(entry.sequence) is int
        and type(entry.previous_digest) is str
        and type(entry.event) is _ClockworkEvent
        and type(entry.command) is _ClockworkCommand
        and type(entry.stored_result) is _TransitionResult
        and type(entry.stored_result.state) is _ClockworkState
        and type(entry.stored_result.command) is _ClockworkCommand
        and (
            entry.stored_result.invalid is None
            or type(entry.stored_result.invalid) is _InvalidTransition
        )
        and (
            entry.stored_result.invalid is None
            or type(entry.stored_result.invalid.code) is str
        )
        and type(entry.digest) is str
    ):
        raise TypeError("invalid_clockwork_journal_entry")
    stored_result = _json.loads(_canonical_bytes(entry.stored_result).decode("utf-8"))
    return _json.dumps(
        {
            "command": entry.command.value,
            "event": entry.event.value,
            "previous_digest": entry.previous_digest,
            "schema_version": entry.schema_version,
            "sequence": entry.sequence,
            "stored_result": stored_result,
        },
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def entry_digest(entry: JournalEntry) -> str:
    return "sha256:" + _hashlib.sha256(canonical_entry_bytes(entry)).hexdigest()


def append_entry(
    journal: tuple[JournalEntry, ...],
    event: _ClockworkEvent,
    command: _ClockworkCommand,
) -> ReplayResult:
    base = replay(journal)
    if base.rejection is not None:
        return base
    if type(event) is not _ClockworkEvent or type(command) is not _ClockworkCommand:
        return _closed_result(
            base.state,
            base.next_sequence,
            base.previous_digest,
            base.validated_journal,
            JournalRejection.FOREIGN_TYPE,
        )
    result = _transition(base.state, event, command)
    draft = JournalEntry(
        JOURNAL_ENTRY_SCHEMA_VERSION,
        base.next_sequence,
        base.previous_digest,
        event,
        command,
        result,
        "",
    )
    entry = JournalEntry(
        draft.schema_version,
        draft.sequence,
        draft.previous_digest,
        draft.event,
        draft.command,
        draft.stored_result,
        entry_digest(draft),
    )
    return replay(journal + (entry,))


def replay(journal: tuple[JournalEntry, ...]) -> ReplayResult:
    if type(journal) is not tuple:
        rejection = (
            JournalRejection.MUTABLE_INPUT_COLLECTION
            if type(journal) is list
            else JournalRejection.FOREIGN_TYPE
        )
        return _closed_result(
            _ClockworkState.IDLE,
            1,
            GENESIS_PREVIOUS_DIGEST,
            (),
            rejection,
        )
    state = _ClockworkState.IDLE
    next_sequence = 1
    previous_digest = GENESIS_PREVIOUS_DIGEST
    validated_journal: tuple[JournalEntry, ...] = ()
    for entry in journal:
        if type(entry) is not JournalEntry:
            return _closed_result(
                state,
                next_sequence,
                previous_digest,
                validated_journal,
                JournalRejection.FOREIGN_TYPE,
            )
        if type(entry.schema_version) is not str:
            return _closed_result(
                state,
                next_sequence,
                previous_digest,
                validated_journal,
                JournalRejection.FOREIGN_TYPE,
            )
        if entry.schema_version != JOURNAL_ENTRY_SCHEMA_VERSION:
            return _closed_result(
                state,
                next_sequence,
                previous_digest,
                validated_journal,
                JournalRejection.WRONG_SCHEMA,
            )
        if type(entry.sequence) is not int or entry.sequence <= 0:
            return _closed_result(
                state,
                next_sequence,
                previous_digest,
                validated_journal,
                JournalRejection.INVALID_SEQUENCE,
            )
        if entry.sequence > next_sequence:
            return _closed_result(
                state,
                next_sequence,
                previous_digest,
                validated_journal,
                JournalRejection.SEQUENCE_GAP,
            )
        if entry.sequence < next_sequence:
            rejection = (
                JournalRejection.DUPLICATE_SEQUENCE
                if entry.sequence == next_sequence - 1
                else JournalRejection.REORDERED_ENTRY
            )
            return _closed_result(
                state, next_sequence, previous_digest, validated_journal, rejection
            )
        if type(entry.previous_digest) is not str or type(entry.digest) is not str:
            return _closed_result(
                state,
                next_sequence,
                previous_digest,
                validated_journal,
                JournalRejection.FOREIGN_TYPE,
            )
        if not _is_digest(entry.previous_digest) or not _is_digest(entry.digest):
            return _closed_result(
                state,
                next_sequence,
                previous_digest,
                validated_journal,
                JournalRejection.MALFORMED_DIGEST,
            )
        if entry.previous_digest != previous_digest:
            return _closed_result(
                state,
                next_sequence,
                previous_digest,
                validated_journal,
                JournalRejection.PREVIOUS_DIGEST_MISMATCH,
            )
        if (
            type(entry.event) is not _ClockworkEvent
            or type(entry.command) is not _ClockworkCommand
            or type(entry.stored_result) is not _TransitionResult
            or type(entry.stored_result.state) is not _ClockworkState
            or type(entry.stored_result.command) is not _ClockworkCommand
            or not (
                entry.stored_result.invalid is None
                or type(entry.stored_result.invalid) is _InvalidTransition
            )
        ):
            return _closed_result(
                state,
                next_sequence,
                previous_digest,
                validated_journal,
                JournalRejection.FOREIGN_TYPE,
            )
        if (
            entry.stored_result.invalid is not None
            and type(entry.stored_result.invalid.code) is not str
        ):
            return _closed_result(
                state,
                next_sequence,
                previous_digest,
                validated_journal,
                JournalRejection.FOREIGN_TYPE,
            )
        if (
            entry.stored_result.invalid is not None
            and entry.stored_result.invalid.code != "invalid_transition"
        ):
            return _closed_result(
                state,
                next_sequence,
                previous_digest,
                validated_journal,
                JournalRejection.UNRECOGNISED_INVALID_TRANSITION_CODE,
            )
        if entry.digest != entry_digest(entry):
            return _closed_result(
                state,
                next_sequence,
                previous_digest,
                validated_journal,
                JournalRejection.ENTRY_BYTES_TAMPERED,
            )
        derived = _transition(state, entry.event, entry.command)
        if derived.invalid is not None and entry.stored_result.invalid is None:
            return _closed_result(
                state,
                next_sequence,
                previous_digest,
                validated_journal,
                JournalRejection.INVALID_TRANSITION_REPRESENTED_AS_SUCCESS,
            )
        if derived.invalid is None and entry.stored_result.invalid is not None:
            return _closed_result(
                state,
                next_sequence,
                previous_digest,
                validated_journal,
                JournalRejection.VALID_TRANSITION_REPRESENTED_AS_INVALID,
            )
        if _canonical_bytes(derived) != _canonical_bytes(entry.stored_result):
            return _closed_result(
                state,
                next_sequence,
                previous_digest,
                validated_journal,
                JournalRejection.STORED_RESULT_MISMATCH,
            )
        state = derived.state
        next_sequence += 1
        previous_digest = entry.digest
        validated_journal += (entry,)
    return _closed_result(
        state, next_sequence, previous_digest, validated_journal, None
    )
