import ast
import copy
import json
import hashlib
import inspect
import shutil
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Callable

import pytest
import yaml

import orchestration_harness.programme_admission as pa
import orchestration_harness.pinned_programme_gatekeeper as pg
from orchestration_harness.programme_admission import (
    ENTRYPOINTS,
    GitPathChange,
    ProgrammeAdmissionError,
    ProgrammeDecision,
    evaluate_committed_scope,
    evaluate_programme_operation_admission,
    evaluate_programme_admission,
    git_change_inventory,
    load_programme_policy,
)
from scripts.ariadne_orchestrator_preflight import build_receipt
from scripts.raisa_ariadne_recovery_preflight import PreflightError, build_task_manifest
from orchestration_harness.settings_fingerprint import settings_fingerprint


ROOT = Path(__file__).resolve().parents[1]
RUNTIME_STATE = ROOT / "tests/fixtures/ariadne_harness/orchestrator_runtime_state.json"


def _valid_g1b1_runtime_source() -> str:
    return """from dataclasses import dataclass as _dataclass
from enum import Enum as _Enum, unique as _unique
import json as _json

STATE_SCHEMA_VERSION = "ariadne.clockwork_state.v1"
EVENT_SCHEMA_VERSION = "ariadne.clockwork_event.v1"
COMMAND_SCHEMA_VERSION = "ariadne.clockwork_command.v1"


@_unique
class ClockworkState(_Enum):
    IDLE = "idle"
    ACTIVE = "active"


@_unique
class ClockworkEvent(_Enum):
    START = "start"
    STOP = "stop"


@_unique
class ClockworkCommand(_Enum):
    ADVANCE = "advance"
    HOLD = "hold"


@_dataclass(frozen=True, slots=True)
class InvalidTransition:
    code: str


@_dataclass(frozen=True, slots=True)
class TransitionResult:
    state: ClockworkState
    command: ClockworkCommand
    invalid: InvalidTransition | None = None


def transition(
    state: ClockworkState,
    event: ClockworkEvent,
    command: ClockworkCommand,
) -> TransitionResult:
    if state is ClockworkState.IDLE and event is ClockworkEvent.START:
        return TransitionResult(ClockworkState.ACTIVE, command, None)
    return TransitionResult(state, command, InvalidTransition("invalid_transition"))


def canonical_bytes(value: TransitionResult) -> bytes:
    if not (type(value) is TransitionResult):
        raise TypeError("invalid_clockwork_transition_result")
    if not (type(value.state) is ClockworkState):
        raise TypeError("invalid_clockwork_transition_result")
    if not (type(value.command) is ClockworkCommand):
        raise TypeError("invalid_clockwork_transition_result")
    if not (value.invalid is None or type(value.invalid) is InvalidTransition):
        raise TypeError("invalid_clockwork_transition_result")
    if not (value.invalid is None or type(value.invalid.code) is str):
        raise TypeError("invalid_clockwork_transition_result")
    payload = {
        "command_schema_version": COMMAND_SCHEMA_VERSION,
        "event_schema_version": EVENT_SCHEMA_VERSION,
        "invalid": value.invalid.code if value.invalid is not None else None,
        "state": value.state.value,
        "state_schema_version": STATE_SCHEMA_VERSION,
        "command": value.command.value,
    }
    return _json.dumps(
        payload,
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
"""


def _valid_g1b1_test_source() -> str:
    return """from orchestration_harness.clockwork_state import (
    COMMAND_SCHEMA_VERSION,
    EVENT_SCHEMA_VERSION,
    STATE_SCHEMA_VERSION,
    ClockworkCommand,
    ClockworkEvent,
    ClockworkState,
    InvalidTransition,
    TransitionResult,
    canonical_bytes,
    transition,
)


def test_same_input_gives_byte_identical_output():
    first_result = transition(ClockworkState.IDLE, ClockworkEvent.START, ClockworkCommand.ADVANCE)
    second_result = transition(ClockworkState.IDLE, ClockworkEvent.START, ClockworkCommand.ADVANCE)
    first_payload = canonical_bytes(first_result)
    second_payload = canonical_bytes(second_result)
    assert first_payload == second_payload


def test_canonical_key_order_and_unicode_policy():
    result = TransitionResult(ClockworkState.ACTIVE, ClockworkCommand.HOLD, None)
    payload = canonical_bytes(result)
    assert payload == b'{"command":"hold","command_schema_version":"ariadne.clockwork_command.v1","event_schema_version":"ariadne.clockwork_event.v1","invalid":null,"state":"active","state_schema_version":"ariadne.clockwork_state.v1"}'


def test_no_ambient_locale_time_or_environment_dependency():
    first_result = transition(ClockworkState.IDLE, ClockworkEvent.START, ClockworkCommand.HOLD)
    second_result = transition(ClockworkState.IDLE, ClockworkEvent.START, ClockworkCommand.HOLD)
    first_payload = canonical_bytes(first_result)
    second_payload = canonical_bytes(second_result)
    assert first_payload == second_payload


def test_closed_invalid_transition_behavior():
    result = transition(ClockworkState.ACTIVE, ClockworkEvent.START, ClockworkCommand.HOLD)
    expected = InvalidTransition("invalid_transition")
    assert result.invalid == expected


def test_transition_does_not_mutate_inputs():
    state = ClockworkState.IDLE
    event = ClockworkEvent.START
    command = ClockworkCommand.ADVANCE
    transition(state, event, command)
    assert state is ClockworkState.IDLE
    assert event is ClockworkEvent.START
    assert command is ClockworkCommand.ADVANCE


def test_serialized_form_includes_schema_versions():
    result = transition(ClockworkState.IDLE, ClockworkEvent.START, ClockworkCommand.ADVANCE)
    payload = canonical_bytes(result)
    assert b"ariadne.clockwork_state.v1" in payload
    assert b"ariadne.clockwork_event.v1" in payload
    assert b"ariadne.clockwork_command.v1" in payload
"""


def _valid_g1b2_runtime_source() -> str:
    return """from dataclasses import dataclass as _dataclass
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
    INVALID_TRANSITION_REPRESENTED_AS_SUCCESS = "invalid_transition_represented_as_success"
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
            return _closed_result(state, next_sequence, previous_digest, validated_journal, JournalRejection.FOREIGN_TYPE)
        if type(entry.schema_version) is not str:
            return _closed_result(state, next_sequence, previous_digest, validated_journal, JournalRejection.FOREIGN_TYPE)
        if entry.schema_version != JOURNAL_ENTRY_SCHEMA_VERSION:
            return _closed_result(state, next_sequence, previous_digest, validated_journal, JournalRejection.WRONG_SCHEMA)
        if type(entry.sequence) is not int or entry.sequence <= 0:
            return _closed_result(state, next_sequence, previous_digest, validated_journal, JournalRejection.INVALID_SEQUENCE)
        if entry.sequence > next_sequence:
            return _closed_result(state, next_sequence, previous_digest, validated_journal, JournalRejection.SEQUENCE_GAP)
        if entry.sequence < next_sequence:
            rejection = (
                JournalRejection.DUPLICATE_SEQUENCE
                if entry.sequence == next_sequence - 1
                else JournalRejection.REORDERED_ENTRY
            )
            return _closed_result(state, next_sequence, previous_digest, validated_journal, rejection)
        if type(entry.previous_digest) is not str or type(entry.digest) is not str:
            return _closed_result(state, next_sequence, previous_digest, validated_journal, JournalRejection.FOREIGN_TYPE)
        if not _is_digest(entry.previous_digest) or not _is_digest(entry.digest):
            return _closed_result(state, next_sequence, previous_digest, validated_journal, JournalRejection.MALFORMED_DIGEST)
        if entry.previous_digest != previous_digest:
            return _closed_result(state, next_sequence, previous_digest, validated_journal, JournalRejection.PREVIOUS_DIGEST_MISMATCH)
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
            return _closed_result(state, next_sequence, previous_digest, validated_journal, JournalRejection.FOREIGN_TYPE)
        if (
            entry.stored_result.invalid is not None
            and type(entry.stored_result.invalid.code) is not str
        ):
            return _closed_result(state, next_sequence, previous_digest, validated_journal, JournalRejection.FOREIGN_TYPE)
        if (
            entry.stored_result.invalid is not None
            and entry.stored_result.invalid.code != "invalid_transition"
        ):
            return _closed_result(state, next_sequence, previous_digest, validated_journal, JournalRejection.UNRECOGNISED_INVALID_TRANSITION_CODE)
        if entry.digest != entry_digest(entry):
            return _closed_result(state, next_sequence, previous_digest, validated_journal, JournalRejection.ENTRY_BYTES_TAMPERED)
        derived = _transition(state, entry.event, entry.command)
        if derived.invalid is not None and entry.stored_result.invalid is None:
            return _closed_result(state, next_sequence, previous_digest, validated_journal, JournalRejection.INVALID_TRANSITION_REPRESENTED_AS_SUCCESS)
        if derived.invalid is None and entry.stored_result.invalid is not None:
            return _closed_result(state, next_sequence, previous_digest, validated_journal, JournalRejection.VALID_TRANSITION_REPRESENTED_AS_INVALID)
        if _canonical_bytes(derived) != _canonical_bytes(entry.stored_result):
            return _closed_result(state, next_sequence, previous_digest, validated_journal, JournalRejection.STORED_RESULT_MISMATCH)
        state = derived.state
        next_sequence += 1
        previous_digest = entry.digest
        validated_journal += (entry,)
    return _closed_result(state, next_sequence, previous_digest, validated_journal, None)
"""


def _rejected_g1b2_runtime_source() -> str:
    source = _valid_g1b2_runtime_source()
    corrections = (
        """    if not (
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
""",
        """        if type(entry.schema_version) is not str:
            return _closed_result(state, next_sequence, previous_digest, validated_journal, JournalRejection.FOREIGN_TYPE)
""",
        """        if type(entry.previous_digest) is not str or type(entry.digest) is not str:
            return _closed_result(state, next_sequence, previous_digest, validated_journal, JournalRejection.FOREIGN_TYPE)
""",
        """        if (
            entry.stored_result.invalid is not None
            and type(entry.stored_result.invalid.code) is not str
        ):
            return _closed_result(state, next_sequence, previous_digest, validated_journal, JournalRejection.FOREIGN_TYPE)
""",
    )
    for correction in corrections:
        assert source.count(correction) == 1
        source = source.replace(correction, "", 1)
    return source


def _valid_g1b2_test_source() -> str:
    return """from dataclasses import replace as _replace
from orchestration_harness.clockwork_journal import (
    GENESIS_PREVIOUS_DIGEST,
    JOURNAL_ENTRY_SCHEMA_VERSION,
    JournalEntry,
    JournalRejection,
    ReplayResult,
    append_entry,
    canonical_entry_bytes,
    entry_digest,
    replay,
)
from orchestration_harness.clockwork_state import (
    ClockworkCommand,
    ClockworkEvent,
    ClockworkState,
    InvalidTransition,
    TransitionResult,
)


class _ExplosiveForeignEntry:
    @property
    def schema_version(self):
        raise AssertionError("foreign_entry_was_inspected")


_PROTOCOL_EVENTS: list[str] = []


class _ProtocolSentinel:
    def _fail(self, protocol: str):
        _PROTOCOL_EVENTS.append(protocol)
        raise AssertionError(f"sentinel_protocol_dispatched:{protocol}")

    def __eq__(self, _other):
        return self._fail("__eq__")

    def __ne__(self, _other):
        return self._fail("__ne__")

    def __lt__(self, _other):
        return self._fail("__lt__")

    def __le__(self, _other):
        return self._fail("__le__")

    def __gt__(self, _other):
        return self._fail("__gt__")

    def __ge__(self, _other):
        return self._fail("__ge__")

    def __len__(self):
        return self._fail("__len__")

    def startswith(self, _prefix):
        return self._fail("startswith")

    def __iter__(self):
        return self._fail("__iter__")

    def __getitem__(self, _key):
        return self._fail("__getitem__")

    def __str__(self):
        return self._fail("__str__")

    def __format__(self, _format_spec):
        return self._fail("__format__")

    def __call__(self, *_args, **_kwargs):
        return self._fail("__call__")

    @property
    def value(self):
        return self._fail("value")

    @property
    def state(self):
        return self._fail("state")

    @property
    def command(self):
        return self._fail("command")

    @property
    def invalid(self):
        return self._fail("invalid")

    @property
    def code(self):
        return self._fail("code")


def _base_journal() -> tuple[JournalEntry, ...]:
    first = append_entry((), ClockworkEvent.START, ClockworkCommand.ADVANCE)
    assert first.rejection is None
    second = append_entry(
        first.validated_journal,
        ClockworkEvent.STOP,
        ClockworkCommand.HOLD,
    )
    assert second.rejection is None
    return second.validated_journal


def _redigest(entry: JournalEntry) -> JournalEntry:
    draft = _replace(entry, digest="")
    return _replace(draft, digest=entry_digest(draft))


def _assert_fixed_serializer_errors(entry):
    for serializer in (canonical_entry_bytes, entry_digest):
        try:
            serializer(entry)
        except TypeError as error:
            assert type(error) is TypeError
            assert error.args == ("invalid_clockwork_journal_entry",)
        else:
            raise AssertionError("fixed_journal_type_error_not_raised")


def _assert_field_protocol_closed(entry: JournalEntry, rejection: JournalRejection):
    _PROTOCOL_EVENTS.clear()
    result = replay((entry,))
    assert type(result) is ReplayResult
    assert result.rejection is rejection
    assert _PROTOCOL_EVENTS == []
    _assert_fixed_serializer_errors(entry)
    assert _PROTOCOL_EVENTS == []


def test_genesis_and_digest_chain_are_deterministic():
    first_result = append_entry((), ClockworkEvent.START, ClockworkCommand.ADVANCE)
    assert first_result.rejection is None
    first = first_result.validated_journal[0]
    expected = (
        b'{"command":"advance","event":"start","previous_digest":"sha256:'
        b'0000000000000000000000000000000000000000000000000000000000000000",'
        b'"schema_version":"ariadne.clockwork_journal_entry.v1","sequence":1,'
        b'"stored_result":{"command":"advance","command_schema_version":'
        b'"ariadne.clockwork_command.v1","event_schema_version":'
        b'"ariadne.clockwork_event.v1","invalid":null,"state":"active",'
        b'"state_schema_version":"ariadne.clockwork_state.v1"}}'
    )
    assert first.sequence == 1
    assert first.previous_digest == GENESIS_PREVIOUS_DIGEST
    assert canonical_entry_bytes(first) == expected
    assert canonical_entry_bytes(first) == canonical_entry_bytes(first)
    assert entry_digest(first) == first.digest
    assert first.digest == "sha256:58cb7d6ba45ce9071c26c587977e3b676e90d2c491227d1b2a64b19d2fa11d9c"
    repeated = append_entry((), ClockworkEvent.START, ClockworkCommand.ADVANCE)
    assert repeated == first_result
    original = first_result.validated_journal
    appended = append_entry(original, ClockworkEvent.STOP, ClockworkCommand.HOLD)
    assert original == (first,)
    assert original[0] is first
    assert appended.validated_journal[1].sequence == 2
    assert appended.validated_journal[1].previous_digest == first.digest


def test_replay_rederives_each_result():
    journal = _base_journal()
    result = replay(journal)
    assert result.rejection is None
    assert result.state is ClockworkState.ACTIVE
    assert result.next_sequence == 3
    assert result.previous_digest == journal[-1].digest
    assert result.validated_journal == journal


def test_tamper_gap_duplicate_and_reorder_are_rejected():
    first, second = _base_journal()
    third_result = append_entry((first, second), ClockworkEvent.STOP, ClockworkCommand.ADVANCE)
    assert third_result.rejection is None
    third = third_result.validated_journal[-1]
    gap = _redigest(_replace(second, sequence=3))
    duplicate = _redigest(_replace(second, sequence=1))
    reordered = _redigest(_replace(third, sequence=1))
    assert replay((first, gap)).rejection is JournalRejection.SEQUENCE_GAP
    assert replay((first, duplicate)).rejection is JournalRejection.DUPLICATE_SEQUENCE
    assert replay((first, second, reordered)).rejection is JournalRejection.REORDERED_ENTRY


def test_wrong_schema_foreign_types_and_malformed_digests_are_rejected():
    first = _base_journal()[0]
    assert replay((_replace(first, schema_version="wrong"),)).rejection is JournalRejection.WRONG_SCHEMA
    assert replay((_ExplosiveForeignEntry(),)).rejection is JournalRejection.FOREIGN_TYPE
    _assert_fixed_serializer_errors(_ExplosiveForeignEntry())
    assert replay((_replace(first, sequence=True),)).rejection is JournalRejection.INVALID_SEQUENCE
    assert replay((_replace(first, sequence=0),)).rejection is JournalRejection.INVALID_SEQUENCE
    assert replay((_replace(first, sequence="1"),)).rejection is JournalRejection.INVALID_SEQUENCE
    assert replay([first]).rejection is JournalRejection.MUTABLE_INPUT_COLLECTION
    sentinel = _ProtocolSentinel()
    field_matrix = (
        (_replace(first, schema_version=sentinel), JournalRejection.FOREIGN_TYPE),
        (_replace(first, sequence=sentinel), JournalRejection.INVALID_SEQUENCE),
        (_replace(first, previous_digest=sentinel), JournalRejection.FOREIGN_TYPE),
        (_replace(first, event=sentinel), JournalRejection.FOREIGN_TYPE),
        (_replace(first, command=sentinel), JournalRejection.FOREIGN_TYPE),
        (_replace(first, stored_result=sentinel), JournalRejection.FOREIGN_TYPE),
        (
            _replace(
                first,
                stored_result=TransitionResult(
                    sentinel,
                    first.stored_result.command,
                    first.stored_result.invalid,
                ),
            ),
            JournalRejection.FOREIGN_TYPE,
        ),
        (
            _replace(
                first,
                stored_result=TransitionResult(
                    first.stored_result.state,
                    sentinel,
                    first.stored_result.invalid,
                ),
            ),
            JournalRejection.FOREIGN_TYPE,
        ),
        (
            _replace(
                first,
                stored_result=TransitionResult(
                    first.stored_result.state,
                    first.stored_result.command,
                    sentinel,
                ),
            ),
            JournalRejection.FOREIGN_TYPE,
        ),
        (
            _replace(
                first,
                stored_result=TransitionResult(
                    first.stored_result.state,
                    first.stored_result.command,
                    InvalidTransition(sentinel),
                ),
            ),
            JournalRejection.FOREIGN_TYPE,
        ),
        (_replace(first, digest=sentinel), JournalRejection.FOREIGN_TYPE),
    )
    for entry, rejection in field_matrix:
        _assert_field_protocol_closed(entry, rejection)


def test_malformed_chain_tamper_and_previous_digest_are_rejected():
    first, second = _base_journal()
    malformed_digest = _replace(first, digest="sha256:not-a-digest")
    malformed_previous = _replace(first, previous_digest="not-a-digest")
    wrong_previous = _replace(first, previous_digest="sha256:" + "1" * 64)
    field_tamper = _replace(first, event=ClockworkEvent.STOP)
    assert replay((malformed_digest,)).rejection is JournalRejection.MALFORMED_DIGEST
    assert replay((malformed_previous,)).rejection is JournalRejection.MALFORMED_DIGEST
    assert replay((wrong_previous,)).rejection is JournalRejection.PREVIOUS_DIGEST_MISMATCH
    assert replay((field_tamper,)).rejection is JournalRejection.ENTRY_BYTES_TAMPERED
    assert replay((first, _replace(second, digest="sha256:" + "f" * 64))).rejection is JournalRejection.ENTRY_BYTES_TAMPERED


def test_result_representation_mismatches_and_all_rejections_are_reachable():
    first, second = _base_journal()
    stored_mismatch = _redigest(
        _replace(
            first,
            stored_result=TransitionResult(
                ClockworkState.ACTIVE,
                ClockworkCommand.HOLD,
                None,
            ),
        )
    )
    invalid_as_success = _redigest(
        _replace(
            second,
            stored_result=TransitionResult(
                ClockworkState.ACTIVE,
                ClockworkCommand.HOLD,
                None,
            ),
        )
    )
    valid_as_invalid = _redigest(
        _replace(
            first,
            stored_result=TransitionResult(
                ClockworkState.ACTIVE,
                ClockworkCommand.ADVANCE,
                InvalidTransition("invalid_transition"),
            ),
        )
    )
    unknown_invalid_code = _redigest(
        _replace(
            second,
            stored_result=TransitionResult(
                ClockworkState.ACTIVE,
                ClockworkCommand.HOLD,
                InvalidTransition("foreign_code"),
            ),
        )
    )
    assert replay((stored_mismatch,)).rejection is JournalRejection.STORED_RESULT_MISMATCH
    assert replay((first, invalid_as_success)).rejection is JournalRejection.INVALID_TRANSITION_REPRESENTED_AS_SUCCESS
    assert replay((valid_as_invalid,)).rejection is JournalRejection.VALID_TRANSITION_REPRESENTED_AS_INVALID
    assert replay((first, unknown_invalid_code)).rejection is JournalRejection.UNRECOGNISED_INVALID_TRANSITION_CODE
    assert {member.value for member in JournalRejection} == {
        "wrong_schema",
        "foreign_type",
        "invalid_sequence",
        "sequence_gap",
        "duplicate_sequence",
        "reordered_entry",
        "previous_digest_mismatch",
        "malformed_digest",
        "entry_bytes_tampered",
        "stored_result_mismatch",
        "unrecognised_invalid_transition_code",
        "invalid_transition_represented_as_success",
        "valid_transition_represented_as_invalid",
        "mutable_input_collection",
    }
"""


def _replace_g1b1_test_function(source: str, name: str, body: str) -> str:
    start = source.index(f"def {name}():")
    next_function = source.find("\n\ndef ", start + 1)
    end = len(source) if next_function < 0 else next_function
    return source[:start] + f"def {name}():\n{body}" + source[end:]


def _parent_valid_g1b1_runtime_source() -> str:
    prefix = _valid_g1b1_runtime_source().split("def canonical_bytes", 1)[0]
    return (
        prefix
        + """def canonical_bytes(value: object) -> bytes:
    payload = {
        "command_schema_version": COMMAND_SCHEMA_VERSION,
        "event_schema_version": EVENT_SCHEMA_VERSION,
        "invalid": value.invalid.code if value.invalid is not None else None,
        "state": value.state.value,
        "state_schema_version": STATE_SCHEMA_VERSION,
        "command": value.command.value,
    }
    return _json.dumps(
        payload,
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
"""
    )


def _insert_before_parent_payload(source: str, statement: str) -> str:
    marker = "    payload = {\n"
    return source.replace(marker, statement + marker, 1)


def _parent_broad_call_model_would_admit(source: str) -> bool:
    module = compile(
        source.encode("utf-8"),
        "<parent-g1b1-model>",
        mode="exec",
        flags=ast.PyCF_ONLY_AST | ast.PyCF_TYPE_COMMENTS,
        dont_inherit=True,
    )
    assert isinstance(module, ast.Module)
    bindings = {"_json": "json"}
    local_functions = {
        node.name for node in module.body if isinstance(node, ast.FunctionDef)
    }
    local_classes = {
        node.name for node in module.body if isinstance(node, ast.ClassDef)
    }
    parent_pure_builtins = {
        "all",
        "any",
        "bool",
        "bytes",
        "dict",
        "enumerate",
        "float",
        "frozenset",
        "int",
        "isinstance",
        "len",
        "list",
        "max",
        "min",
        "range",
        "reversed",
        "set",
        "sorted",
        "str",
        "sum",
        "tuple",
        "zip",
    }

    def resolved_name(node: ast.AST) -> str | None:
        if isinstance(node, ast.Name):
            return bindings.get(node.id, node.id)
        if isinstance(node, ast.Attribute):
            base = resolved_name(node.value)
            return f"{base}.{node.attr}" if base else None
        return None

    for node in ast.walk(module):
        if isinstance(node, ast.Name) and node.id in pa._G1B1_DYNAMIC_EXECUTION_NAMES:
            return False
        if not isinstance(node, ast.Call):
            continue
        resolved = resolved_name(node.func)
        if resolved == "json.dumps":
            continue
        if isinstance(node.func, ast.Name) and node.func.id == "_dataclass":
            continue
        if (
            isinstance(node.func, ast.Attribute)
            and node.func.attr == "encode"
            and len(node.args) == 1
            and isinstance(node.args[0], ast.Constant)
            and node.args[0].value == "utf-8"
        ):
            continue
        if isinstance(node.func, ast.Name) and (
            node.func.id in parent_pure_builtins
            or node.func.id in local_functions
            or node.func.id in local_classes
        ):
            continue
        return False
    return True


class _G1B1SentinelField:
    value = "sentinel"


class _G1B1DispatchSentinel:
    def __init__(self) -> None:
        self.events: list[str] = []
        self.invalid = None
        self.state = _G1B1SentinelField()
        self.command = _G1B1SentinelField()

    def _record(self, event: str) -> None:
        object.__getattribute__(self, "events").append(event)

    def __getattribute__(self, name: str) -> object:
        if name == "dispatch":
            object.__getattribute__(self, "_record")("getattribute")
            return "sentinel"
        return object.__getattribute__(self, name)

    def __format__(self, _format_spec: str) -> str:
        self._record("format")
        return "sentinel"

    def __str__(self) -> str:
        self._record("str")
        return "sentinel"

    def __iter__(self):
        self._record("iter")
        return iter(())

    def __getitem__(self, _key: object) -> str:
        self._record("getitem")
        return "sentinel"

    def __lt__(self, _other: object) -> bool:
        self._record("compare")
        return False

    def __add__(self, _other: object) -> int:
        self._record("arithmetic")
        return 1

    def __call__(self) -> None:
        self._record("call")

    def encode(self, _encoding: str) -> bytes:
        self._record("encode")
        return b"sentinel"

    def dumps(self, *_args: object, **_kwargs: object) -> str:
        self._record("dumps")
        return "sentinel"


def _policy_sandbox(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    subprocess.run(
        ["git", "init"], cwd=root, check=True, capture_output=True, text=True
    )
    object_store = subprocess.run(
        ["git", "rev-parse", "--path-format=absolute", "--git-path", "objects"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    alternates = root / ".git/objects/info/alternates"
    alternates.parent.mkdir(parents=True, exist_ok=True)
    alternates.write_bytes((object_store + "\n").encode("utf-8"))
    _git(root, "read-tree", "91f1e6e645424a448bdcdfa2adabb86d31fb5f0b")
    _git(root, "config", "core.longpaths", "true")
    _git(root, "config", "user.email", "tests@example.invalid")
    _git(root, "config", "user.name", "Programme Policy Tests")
    _git(root, "symbolic-ref", "HEAD", "refs/heads/policy-sandbox")
    _git(root, "read-tree", "--empty")
    (root / "orchestration/programme").mkdir(parents=True, exist_ok=True)
    (root / "orchestration/continuity/ariadne-active-operation-latch").mkdir(
        parents=True, exist_ok=True
    )
    shutil.copytree(
        ROOT / "orchestration/harness_settings",
        root / "orchestration/harness_settings",
        dirs_exist_ok=True,
    )
    for relative in (
        pa.STATE_PATH,
        pa.GATES_PATH,
        pa.RISK_PATH,
        pa.INVENTORY_PATH,
        pa.G1A_SCOPE_PATH,
        pa.G1A_ACCEPTED_SURFACE_PATH,
        pa.G1B_CLOCKWORK_SCOPE_PATH,
        pa.G1B1_ACCEPTED_SURFACE_PATH,
        pa.G1B2_JOURNAL_REPLAY_SCOPE_PATH,
        pa.LATCH_PATH,
        pa.AGENTS_PATH,
        Path(pa.OWNER_DISPOSITION_PATH),
        Path(pa.G1A3_R1_REVIEW_PATH),
    ):
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / relative, target)
    for relative_text in (
        pa.G0_G08_ALLOWED_PATHS
        | pa.G1A_ALLOWED_PATHS
        | pa.G1A2_ALLOWED_PATHS
        | pa.G1A3_ALLOWED_PATHS
        | set(pa.G1A_ACCEPTED_SOURCE_BLOBS)
        | set(pa.CLOCKWORK_INVENTORY_BLOBS)
        | set(pa.G1A_ACCEPTED_EVIDENCE)
        | pa.G1B1_ALLOWED_PATHS
    ):
        source = ROOT / relative_text
        if not source.is_file():
            continue
        target = root / relative_text
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    for authority_root in (
        pa.TRANSITION_REVIEW_ROOT,
        pa.TRANSITION_ARTIFACT_ROOT,
        pa.SUBGATE_REVIEW_ROOT,
        pa.SUBGATE_IMPLEMENTATION_REVIEW_ROOT,
        pa.G1A3_TRANSITION_REVIEW_ROOT,
        pa.SUBGATE_TRANSITION_ARTIFACT_ROOT,
    ):
        source_root = ROOT / authority_root
        if source_root.is_dir():
            shutil.copytree(source_root, root / authority_root, dirs_exist_ok=True)
    shutil.copytree(
        ROOT / "orchestration_harness",
        root / "orchestration_harness",
        dirs_exist_ok=True,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
    )
    _git(root, "add", "-A")
    tree = _git(root, "write-tree")
    commit = _git(
        root,
        "commit-tree",
        tree,
        "-p",
        "4ce17198fad677aed1fe45be4e3bf2b18c713b3b",
        "-m",
        "authored-synthetic policy sandbox",
    )
    _git(root, "update-ref", "refs/heads/policy-sandbox", commit)
    return root


def _manifest() -> dict:
    policy = load_programme_policy(ROOT)
    reviewed = policy.state["gate_transition"]["reviewed_commit"]
    activation = _git(ROOT, "rev-list", "--reverse", f"{reviewed}..HEAD").splitlines()[
        0
    ]
    return {
        "schema_version": pa.TASK_MANIFEST_VERSION,
        "task_id": "closed-g1a1-candidate-probe",
        "task_class": pa.G1A_TASK_CLASS,
        "programme_gate": "G1A.1",
        "objective": "Prove the accepted G1A.1 implementation cannot be reopened.",
        "base_commit": activation,
        "candidate_or_current_head": _git(ROOT, "rev-parse", "HEAD"),
        "allowed_path_roots": sorted(pa.G1A_ALLOWED_PATHS),
        "intended_side_effect_classes": sorted(pa.G1A_ALLOWED_EFFECTS),
        "forbidden_side_effect_classes": sorted(pa.G1A_FORBIDDEN_EFFECTS),
        "state_digest": policy.state_digest,
        "policy_digest": policy.policy_digest,
    }


def test_canonical_orchestrator_cannot_dispatch_with_current_fingerprint(
    tmp_path: Path,
) -> None:
    runtime = json.loads(RUNTIME_STATE.read_text(encoding="utf-8"))
    runtime["active_operation"]["checkpoint"]["settings_fingerprint"] = (
        settings_fingerprint(ROOT / "orchestration/harness_settings")
    )
    runtime_path = tmp_path / "orchestrator-runtime-state.json"
    _write_json(runtime_path, runtime)
    receipt = build_receipt(runtime_state_path=runtime_path)

    assert receipt["status"] == "passed"
    assert receipt["worker_dispatch_permitted"] is False
    assert receipt["admission_usable"] is False
    assert receipt["programme_admission"]["admitted"] is False


def test_mislabeled_product_task_cannot_enter_g0_5() -> None:
    manifest = _manifest()
    manifest["task_class"] = "product_feature"

    decision = evaluate_programme_admission(
        repo_root=ROOT, manifest=manifest, entrypoint="task_selection"
    )

    assert decision.admitted is False
    assert decision.reason_codes == ["task_class_not_admitted"]


@pytest.mark.parametrize("entrypoint", sorted(ENTRYPOINTS))
def test_missing_manifest_blocks_every_gated_entrypoint(entrypoint: str) -> None:
    decision = evaluate_programme_admission(
        repo_root=ROOT, manifest=None, entrypoint=entrypoint
    )

    assert decision.admitted is False
    assert decision.reason_codes == ["task_manifest_missing"]


@pytest.mark.parametrize("field", ["state_digest", "policy_digest"])
def test_review_pending_profile_precedes_manifest_digest_evaluation(field: str) -> None:
    manifest = _manifest()
    manifest[field] = "sha256:" + "0" * 64

    decision = evaluate_programme_admission(
        repo_root=ROOT, manifest=manifest, entrypoint="task_selection"
    )

    assert decision.admitted is False
    assert decision.reason_codes == ["task_class_not_admitted"]


@pytest.mark.parametrize("failure", ["missing", "malformed", "contradictory"])
def test_missing_malformed_or_contradictory_policy_fails_closed(
    tmp_path: Path, failure: str
) -> None:
    root = _policy_sandbox(tmp_path)
    if failure == "missing":
        (root / pa.STATE_PATH).unlink()
    elif failure == "malformed":
        (root / pa.STATE_PATH).write_text("{", encoding="utf-8")
    else:
        gates_path = root / pa.GATES_PATH
        gates = yaml.safe_load(gates_path.read_text(encoding="utf-8"))
        gates["programme"]["current_gate_status"] = "passed"
        _write_yaml(gates_path, gates)
    _git(root, "add", "-A")

    with pytest.raises(ProgrammeAdmissionError):
        load_programme_policy(root)


def test_duplicate_yaml_key_is_rejected(tmp_path: Path) -> None:
    root = _policy_sandbox(tmp_path)
    path = root / pa.GATES_PATH
    path.write_bytes(
        ('schema_version: "duplicate"\n' + path.read_text(encoding="utf-8")).encode(
            "utf-8"
        )
    )
    _git(root, "add", "--", pa.GATES_PATH.as_posix())

    with pytest.raises(ProgrammeAdmissionError, match="yaml_duplicate_key"):
        load_programme_policy(root)


@pytest.mark.parametrize(
    "variable", ["GIT_DIR", "GIT_INDEX_FILE", "GIT_CONFIG_PARAMETERS"]
)
def test_programme_policy_rejects_git_redirection_environment(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, variable: str
) -> None:
    root = _policy_sandbox(tmp_path)
    monkeypatch.setenv(variable, "synthetic-redirection")

    with pytest.raises(
        ProgrammeAdmissionError, match="trusted_git_environment_forbidden"
    ):
        load_programme_policy(root)


def test_duplicate_json_key_is_rejected(tmp_path: Path) -> None:
    root = _policy_sandbox(tmp_path)
    path = root / pa.STATE_PATH
    path.write_bytes(
        path.read_text(encoding="utf-8")
        .replace("{\n", '{\n  "schema_version": "duplicate",\n', 1)
        .encode("utf-8")
    )
    _git(root, "add", "--", pa.STATE_PATH.as_posix())

    with pytest.raises(ProgrammeAdmissionError, match="json_duplicate_key"):
        load_programme_policy(root)


def test_unknown_policy_field_is_rejected(tmp_path: Path) -> None:
    root = _policy_sandbox(tmp_path)
    path = root / pa.STATE_PATH
    state = json.loads(path.read_text(encoding="utf-8"))
    state["permissive_unknown"] = True
    path.write_bytes(json.dumps(state).encode("utf-8"))
    _git(root, "add", "--", pa.STATE_PATH.as_posix())

    with pytest.raises(ProgrammeAdmissionError, match="programme_state_schema_invalid"):
        load_programme_policy(root)


def test_state_and_gate_disagreement_is_rejected(tmp_path: Path) -> None:
    root = _policy_sandbox(tmp_path)
    path = root / pa.GATES_PATH
    gates = yaml.safe_load(path.read_text(encoding="utf-8"))
    gates["programme"]["next_eligible_tranche"] = "G1A.1"
    _write_yaml(path, gates)
    _git(root, "add", "--", pa.GATES_PATH.as_posix())

    with pytest.raises(
        ProgrammeAdmissionError, match="programme_state_gate_disagreement"
    ):
        load_programme_policy(root)


def test_duplicate_risk_id_is_rejected(tmp_path: Path) -> None:
    root = _policy_sandbox(tmp_path)
    path = root / pa.RISK_PATH
    path.write_bytes(
        path.read_text(encoding="utf-8")
        .replace('- id: "R-002"', '- id: "R-001"', 1)
        .encode("utf-8")
    )
    _git(root, "add", "--", pa.RISK_PATH.as_posix())

    with pytest.raises(ProgrammeAdmissionError, match="risk_id_duplicate"):
        load_programme_policy(root)


def test_g1a_parser_inventory_and_allowlist_are_exact(tmp_path: Path) -> None:
    root = _policy_sandbox(tmp_path)
    path = root / pa.G1A_SCOPE_PATH
    scope = yaml.safe_load(path.read_text(encoding="utf-8"))
    scope["subgates"]["G1A.1"]["verdict_parsers"][0]["disposition"] = (
        "leave_duplicate_parser"
    )
    _write_yaml(path, scope)

    with pytest.raises(ProgrammeAdmissionError, match="g1a_1_parser_inventory_invalid"):
        load_programme_policy(root)


def test_g1a_1_excludes_provider_and_integration_mutators() -> None:
    policy = load_programme_policy(ROOT)
    g1a_1_paths = set(policy.g1a_scope["subgates"]["G1A.1"]["allowed_paths"])

    assert "scripts/ariadne_antigravity.py" not in g1a_1_paths
    assert "scripts/agent_worktrees.py" not in g1a_1_paths
    assert policy.g1a_scope["transition_opens_only"] == "G1A.1"
    assert policy.g1a_scope["subgates"]["G1A.2"]["status"] == (
        "external_review_passed_frozen"
    )
    assert set(policy.g1a_scope["subgates"]["G1A.3"]["allowed_paths"]) == (
        pa.G1A3_R1_ALLOWED_PATHS
    )


def test_owner_disposition_is_exact_digest_bound_and_not_external_pass() -> None:
    policy = load_programme_policy(ROOT)
    authority = policy.state["g1a_subgate_authority"]
    entry = authority["owner_disposition_history"][0]
    record_path = ROOT / entry["record_path"]
    record = pa.strict_json_object(record_path)

    assert entry["record_sha256"] == pa._sha256_bytes(record_path.read_bytes())
    assert record["decision"] == "ACCEPT_WITH_RESIDUAL_RISK"
    assert record["subject_commit"] == "91f1e6e645424a448bdcdfa2adabb86d31fb5f0b"
    assert record["subject_tree"] == "24b92d586061901e7574d511105b21ea66d97f7e"
    assert record["g1a2_transition_enablement_authorized"] is True
    assert record["g1a2_state_transition_authorized"] is False
    assert record["g1a2_implementation_authorized"] is False
    assert record["provider_invocation_authorized"] is False
    assert authority["external_review_history"][0]["verdict"] == "PASS"
    assert authority["decisive_transition_enablement_review_id"] == (
        "g1a2-e0-review-dab684e-independent-20260828-pass"
    )
    assert record["residual_risks"] == [
        {
            "id": "G1A1-PARSER-MIXED-TAB-001",
            "classification": "parser_robustness_backlog",
            "description": "Mixed space-plus-tab indentation remains an unclosed free-form source-text marker edge case.",
            "accepted_for_progression": True,
            "must_be_reconsidered_before": "future high-trust free-form text integration authority",
        }
    ]


def test_current_closeout_candidate_is_review_pending_and_admits_no_task() -> None:
    policy = load_programme_policy(ROOT)
    g1b1 = policy.state["g1b"]["subgates"]["G1B.1"]
    g1b2 = policy.state["g1b"]["subgates"]["G1B.2"]

    assert policy.state["current_gate"] == "G1B.1"
    assert policy.state["active_correction"] == pa.G1B1_CLOSEOUT_CORRECTION
    assert policy.overlay["active_profile"] == pa.G1B1_CLOSEOUT_REVIEW_PENDING_PROFILE
    assert policy.state["task_selection"]["allowed_task_kinds"] == []
    assert policy.state["task_selection"]["next_eligible_now"] is False
    assert policy.state["task_selection"]["next_eligible_tranche"] == "G1B.2"
    assert g1b1 == {
        "status": "implementation_external_review_passed_closeout_review_pending",
        "implementation_status": "external_review_passed",
        "implementation_started": True,
        "implementation_complete": True,
        "closeout_status": "review_pending",
        "closed": False,
        "accepted_surface_path": pa.G1B1_ACCEPTED_SURFACE_PATH.as_posix(),
    }
    assert g1b2["status"] == "closed_pending_state_transition"
    assert g1b2["state_transition_status"] == "not_started"
    assert g1b2["state_transition"] is None
    assert g1b2["implementation_authorized"] is False
    assert g1b2["implementation_started"] is False
    assert policy.state["g1b"]["decisive_implementation_review_id"] == (
        pa.G1B1_REVIEW_ID
    )
    assert policy.state["g1b"]["status"] == "g1b1_closeout_review_pending"
    assert policy.state["g1b"]["next_action"] == (
        "external_G1B1_closeout_G1B2_transition_enablement_review_only"
    )
    provider = evaluate_programme_admission(
        repo_root=ROOT, manifest={}, entrypoint="provider_invocation"
    )
    assert provider.admitted is False
    assert provider.reason_codes == ["provider_invocation_closed_in_active_profile"]
    local_operation = evaluate_programme_operation_admission(
        repo_root=ROOT,
        manifest={},
        entrypoint="task_branch_commit",
        phase="development",
    )
    assert local_operation.admitted is False
    assert local_operation.reason_codes == ["pinned_gatekeeper_required"]
    with pytest.raises(
        PreflightError, match="no implementation task is currently eligible"
    ):
        build_task_manifest(ROOT)


def test_g1a2_implementation_pass_is_exact_and_ledger_separated() -> None:
    policy = load_programme_policy(ROOT)
    authority = policy.state["g1a_subgate_authority"]
    entry = authority["implementation_review_history"][0]
    path = ROOT / entry["review_record_path"]

    assert hashlib.sha256(path.read_bytes()).hexdigest() == (
        "bd29a64c591e0cddd9cc47cc2ae4408f63c36acc3e663bd431bc369ee7385fcb"
    )
    assert entry["review_record_sha256"] == (
        "sha256:bd29a64c591e0cddd9cc47cc2ae4408f63c36acc3e663bd431bc369ee7385fcb"
    )
    assert authority["implementation_review_record_root"] == (
        pa.SUBGATE_IMPLEMENTATION_REVIEW_ROOT
    )
    assert authority["external_subgate_review_record_root"] == pa.SUBGATE_REVIEW_ROOT
    assert (
        authority["implementation_review_record_root"]
        != (authority["external_subgate_review_record_root"])
    )
    assert entry["reviewed_commit"] == ("37e2d6f51ebbdb281771f922a5f460fd23e2571b")
    assert entry["reviewed_tree"] == "798a2eda11438fe05da2528298006775774ccfc4"
    assert entry["reviewed_parent"] == ("474d79e0ef918dc8e7fef6780ea34c5c105fe236")


def test_enablement_candidate_preserves_accepted_implementation_blobs() -> None:
    assert (
        _git(ROOT, "rev-parse", "HEAD:scripts/ariadne_antigravity.py")
        == (pa.G1A_ACCEPTED_SOURCE_BLOBS["scripts/ariadne_antigravity.py"])
    )
    assert (
        _git(ROOT, "rev-parse", "HEAD:scripts/agent_worktrees.py")
        == (pa.G1A_ACCEPTED_SOURCE_BLOBS["scripts/agent_worktrees.py"])
    )


def test_g1a3_r1_pass_is_byte_exact_digest_bound_and_append_only() -> None:
    policy = load_programme_policy(ROOT)
    path = ROOT / pa.G1A3_R1_REVIEW_PATH
    history = policy.state["g1a_subgate_authority"]["g1a3_r1_review_history"]
    assert len(history) == 1
    assert (
        policy.state["g1a_subgate_authority"]["decisive_g1a3_r1_review_id"]
        == pa.G1A3_R1_REVIEW_ID
    )
    assert pa._sha256_bytes(path.read_bytes()) == pa.G1A3_R1_REVIEW_SHA256
    assert _git(ROOT, "hash-object", "--", pa.G1A3_R1_REVIEW_PATH) == (
        "7ffbd6870eb24124252d9b1fa1d3a9e882f8b682"
    )
    assert history[0]["review_record_sha256"] == pa.G1A3_R1_REVIEW_SHA256
    assert history[0]["reviewed_commit"] == ("23aa3ab19aec6cee9246e7dd3a88f61ada39bd7a")
    assert history[0]["reviewed_tree"] == ("e06fbf5c5f46b7a637a1d2987ce34c8f37990283")
    assert history[0]["reviewed_parent"] == ("29b07cc8c70dd5813d59d99fb2be113a88dd55e2")


@pytest.mark.parametrize(
    "case",
    [
        "missing",
        "modified_bytes",
        "wrong_commit",
        "wrong_tree",
        "wrong_parent",
        "negative",
        "findings",
        "contradictory_authority",
    ],
)
def test_g1a3_r1_review_corruption_fails_closed(tmp_path: Path, case: str) -> None:
    root = _policy_sandbox(tmp_path)
    state_path = root / pa.STATE_PATH
    state = json.loads(state_path.read_text(encoding="utf-8"))
    entry = state["g1a_subgate_authority"]["g1a3_r1_review_history"][0]
    review_path = root / entry["review_record_path"]
    if case == "missing":
        review_path.unlink()
        _git(root, "add", "-A")
    elif case == "modified_bytes":
        review_path.write_bytes(review_path.read_bytes() + b" ")
        _git(root, "add", "--", entry["review_record_path"])
    else:
        record = json.loads(review_path.read_text(encoding="utf-8"))
        if case == "wrong_commit":
            record["reviewed_commit"] = entry["reviewed_commit"] = "0" * 40
        elif case == "wrong_tree":
            record["reviewed_tree"] = entry["reviewed_tree"] = "0" * 40
        elif case == "wrong_parent":
            record["reviewed_parent"] = entry["reviewed_parent"] = "0" * 40
        elif case == "negative":
            record["verdict"] = entry["verdict"] = "REVISION_REQUIRED"
        elif case == "findings":
            record["blocking_finding_count"] = entry["blocking_finding_count"] = 1
        else:
            record["g1b_state_transition_authorized"] = True
            entry["g1b_state_transition_authorized"] = True
        _write_json(review_path, record)
        entry["review_record_sha256"] = pa._sha256_bytes(review_path.read_bytes())
        _write_json(state_path, state)
    with pytest.raises(ProgrammeAdmissionError):
        load_programme_policy(root)


def test_g1a_accepted_surface_matches_every_frozen_object() -> None:
    policy = load_programme_policy(ROOT)
    surface = policy.g1a_accepted_surface
    runtime = {row["path"]: row["git_blob"] for row in surface["runtime_sources"]}
    evidence = {
        row["path"]: (
            row["schema_version"],
            row["record_id"],
            row["physical_sha256"],
            row["git_blob"],
        )
        for row in surface["authority_evidence"]
    }
    assert runtime == pa.G1A_ACCEPTED_SOURCE_BLOBS
    assert evidence == pa.G1A_ACCEPTED_EVIDENCE
    assert surface["runtime_execution_authorized"] is False
    assert surface["future_transition_input_only"] is True
    assert surface["residual_risks"][0]["status"] == "accepted_not_fixed"


def test_g1b_clockwork_scope_covers_sources_writers_tests_and_fixtures() -> None:
    policy = load_programme_policy(ROOT)
    scope = policy.g1b_clockwork_scope
    items = {row["path"]: row for row in scope["items"]}
    assert {path: row["git_blob"] for path, row in items.items()} == (
        pa.CLOCKWORK_INVENTORY_BLOBS
    )
    assert {
        "orchestration_harness/governance_clockwork.py",
        "orchestration_harness/governance_clockwork_tick.py",
        "orchestration_harness/governance_live_adoption.py",
        "orchestration_harness/governance_migration.py",
        "orchestration_harness/shadow_clockwork.py",
        "orchestration_harness/transactional_closeout.py",
        "scripts/ariadne_governance_clockwork_tick.py",
        "scripts/ariadne_governance_clockwork_closeout.py",
    }.issubset(items)
    current_core = set(policy.state["harness_inventory"]["clockwork_core"])
    assert current_core == pa.CLOCKWORK_CORE_MINIMUM_PATHS
    assert current_core.issubset(items)
    closure = scope["inventory_closure"]
    assert set(closure["minimum_clockwork_core_paths"]) == current_core
    assert set(closure["direct_cli_paths"]) == pa.CLOCKWORK_DIRECT_CLI_PATHS
    assert set(closure["direct_test_paths"]) == pa.CLOCKWORK_DIRECT_TEST_PATHS
    assert set(closure["direct_fixture_paths"]) == pa.CLOCKWORK_DIRECT_FIXTURE_PATHS
    for path in (
        pa.CLOCKWORK_DIRECT_CLI_PATHS
        | pa.CLOCKWORK_DIRECT_TEST_PATHS
        | pa.CLOCKWORK_DIRECT_FIXTURE_PATHS
    ):
        assert items[path]["git_blob"] == pa.CLOCKWORK_INVENTORY_BLOBS[path]
    controls = scope["authority_surface_controls"]
    assert set(controls) == {
        "orchestration_harness/governance_live_adoption.py",
        "orchestration_harness/governance_migration.py",
    }
    for path, control in controls.items():
        assert "persistent_state_writer" in control["roles"]
        assert "adapter_migration_boundary" in control["roles"]
        assert set(control["writers"]) == set(items[path]["writers"])
        assert control["atomicity_or_commit_point"]
        assert control["lease_or_cas_behavior"]
        assert control["replay_or_recovery_behavior"]
        assert control["portable_extraction_disposition"]
    assert any(row["writers"] for row in items.values())
    assert all(
        "pytest_collection" in row["entrypoints"]
        for path, row in items.items()
        if path.startswith("tests/")
    )
    assert scope["known_historical_fixture_failures"]["count"] == 7
    assert (
        set(scope["portable_ariadne_extraction_boundary"]["future_kernel_paths"])
        == pa.G1B1_ALLOWED_PATHS
    )
    assert scope["runtime_mutation_authorized"] is False
    assert scope["implementation_authorized"] is False


@pytest.mark.parametrize(
    "case",
    ["missing", "rewritten", "negative", "stale", "wrong_tree", "findings"],
)
def test_g1a2_implementation_review_failures_hard_stop(
    tmp_path: Path, case: str
) -> None:
    root = _policy_sandbox(tmp_path)
    state_path = root / pa.STATE_PATH
    state = json.loads(state_path.read_text(encoding="utf-8"))
    entry = state["g1a_subgate_authority"]["implementation_review_history"][0]
    record_path = root / entry["review_record_path"]
    if case == "missing":
        record_path.unlink()
        _git(root, "add", "-A")
    elif case == "rewritten":
        record_path.write_bytes(record_path.read_bytes() + b" ")
        _git(root, "add", "--", entry["review_record_path"])
    else:
        record = json.loads(record_path.read_text(encoding="utf-8"))
        if case == "negative":
            record["verdict"] = entry["verdict"] = "REVISION_REQUIRED"
        elif case == "stale":
            record["reviewed_commit"] = entry["reviewed_commit"] = "0" * 40
        elif case == "wrong_tree":
            record["reviewed_tree"] = entry["reviewed_tree"] = "0" * 40
        else:
            record["blocking_finding_count"] = entry["blocking_finding_count"] = 1
        _write_json(record_path, record)
        entry["review_record_sha256"] = pa._sha256_bytes(record_path.read_bytes())
        _write_json(state_path, state)

    with pytest.raises(ProgrammeAdmissionError):
        load_programme_policy(root)


@pytest.mark.parametrize("case", ["missing", "rewritten", "contradictory"])
def test_owner_disposition_missing_rewritten_or_contradictory_fails_closed(
    tmp_path: Path, case: str
) -> None:
    root = _policy_sandbox(tmp_path)
    record_path = root / pa.OWNER_DISPOSITION_PATH
    if case == "missing":
        record_path.unlink()
        _git(root, "add", "-A")
    elif case == "rewritten":
        record = json.loads(record_path.read_text(encoding="utf-8"))
        record["residual_risks"][0]["description"] += " rewritten"
        _write_json(record_path, record)
    else:
        state_path = root / pa.STATE_PATH
        state = json.loads(state_path.read_text(encoding="utf-8"))
        state["g1a_subgate_authority"]["subgates"]["G1A.2"][
            "implementation_authorized"
        ] = True
        _write_json(state_path, state)

    with pytest.raises(ProgrammeAdmissionError):
        load_programme_policy(root)


def test_owner_disposition_duplicate_key_is_rejected(tmp_path: Path) -> None:
    root = _policy_sandbox(tmp_path)
    record_path = root / pa.OWNER_DISPOSITION_PATH
    record_path.write_bytes(
        record_path.read_text(encoding="utf-8")
        .replace(
            "{\n",
            '{\n  "schema_version": "duplicate-owner-schema",\n',
            1,
        )
        .encode("utf-8")
    )
    state_path = root / pa.STATE_PATH
    state = json.loads(state_path.read_text(encoding="utf-8"))
    state["g1a_subgate_authority"]["owner_disposition_history"][0]["record_sha256"] = (
        pa._sha256_bytes(record_path.read_bytes())
    )
    _write_json(state_path, state)
    _git(root, "add", "--", pa.OWNER_DISPOSITION_PATH, pa.STATE_PATH.as_posix())

    with pytest.raises(ProgrammeAdmissionError, match="json_duplicate_key"):
        load_programme_policy(root)


def _install_historical_g1a2_antigravity_source(root: Path) -> Path:
    """Bind G1A.2 contract regressions to their accepted implementation source."""
    path = root / "scripts/ariadne_antigravity.py"
    path.write_bytes(
        pa._git_object_bytes(
            ROOT,
            "37e2d6f51ebbdb281771f922a5f460fd23e2571b:scripts/ariadne_antigravity.py",
        )
    )
    return path


def test_g1a_2_adapter_only_mutation_preserves_provider_contract(
    tmp_path: Path,
) -> None:
    root = _policy_sandbox(tmp_path)
    path = _install_historical_g1a2_antigravity_source(root)
    source = path.read_text(encoding="utf-8")
    path.write_text(
        source.replace(
            "    return next(iter(unique.values()))\n",
            "    return dict(next(iter(unique.values())))\n",
            1,
        ),
        encoding="utf-8",
    )

    assert pa.g1a2_provider_contract_reasons(root) == []


def test_g1a_2_nonadapter_provider_mutation_is_rejected(tmp_path: Path) -> None:
    root = _policy_sandbox(tmp_path)
    path = _install_historical_g1a2_antigravity_source(root)
    source = path.read_text(encoding="utf-8")
    path.write_text(
        source.replace(
            "    require_programme_admission(\n",
            "    provider_contract_drift = None\n    require_programme_admission(\n",
            1,
        ),
        encoding="utf-8",
    )

    reasons = pa.g1a2_provider_contract_reasons(root)
    assert "g1a_2_nonadapter_provider_code_changed" in reasons
    assert "g1a_2_protected_provider_symbol_changed" in reasons


@pytest.mark.parametrize(
    "symbol",
    [
        "WorktreeState",
        "_git",
        "inspect_worktree",
        "build_command",
        "admit_orchestrator_receipt",
        "_atomic_receipt_write",
        "_output_evidence",
        "run_worker",
        "main",
    ],
)
def test_every_protected_antigravity_symbol_is_immutable(
    tmp_path: Path, symbol: str
) -> None:
    root = _policy_sandbox(tmp_path)
    path = _install_historical_g1a2_antigravity_source(root)
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    node = next(
        item
        for item in tree.body
        if isinstance(item, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
        and item.name == symbol
    )
    lines = source.splitlines(keepends=True)
    lines.insert(node.body[0].lineno - 1, "    synthetic_contract_drift = None\n")
    path.write_text("".join(lines), encoding="utf-8")

    reasons = pa.g1a2_provider_contract_reasons(root)

    assert "g1a_2_nonadapter_provider_code_changed" in reasons
    assert "g1a_2_protected_provider_symbol_changed" in reasons


def test_g1a3_record_integration_is_the_only_mutable_production_symbol(
    tmp_path: Path,
) -> None:
    root = _policy_sandbox(tmp_path)
    path = root / "scripts/agent_worktrees.py"
    source = path.read_text(encoding="utf-8")
    target = (
        "def record_integration(args: argparse.Namespace) -> None:\n"
        '    _require_command_admission(args, entrypoint="integration")\n'
    )
    updated = source.replace(
        target,
        target + "    synthetic_bounded_consumer_mutation = True\n",
        1,
    )
    assert updated != source
    path.write_text(updated, encoding="utf-8")

    assert pa.g1a3_integration_contract_reasons(root) == []


def _run_worker_admission_source() -> str:
    return (
        "    require_programme_admission(\n"
        "        repo_root=REPO_ROOT,\n"
        "        manifest_path=programme_task_manifest,\n"
        '        entrypoint="provider_invocation",\n'
        "    )\n"
    )


def test_g1a3_review_producer_baseline_is_runtime_faithful_body_only() -> None:
    scope = yaml.safe_load((ROOT / pa.G1A_SCOPE_PATH).read_text(encoding="utf-8"))
    overlay = yaml.safe_load((ROOT / pa.OVERLAY_PATH).read_text(encoding="utf-8"))
    g1a3 = scope["subgates"]["G1A.3"]
    contract = g1a3["immutable_review_producer_contract"]
    payload = pa._git_object_bytes(
        ROOT, f"{contract['source_commit']}:{contract['path']}"
    )

    assert g1a3["antigravity_allowed_mutation_symbols"] == ["run_worker"]
    assert contract["source_blob"] == ("ff1c95d9a24fddcba1df3ee6dc10a21b71b89049")
    assert contract["hash_semantics"] == (pa.G1A3_REVIEW_PRODUCER_HASH_SEMANTICS)
    assert contract["runtime_source_parsing_contract"] == (
        pa.G1A3_RUNTIME_SOURCE_PARSING_CONTRACT
    )
    assert contract["first_executable_statement_contract"] == (
        pa.G1A3_RUN_WORKER_FIRST_ADMISSION_CONTRACT
    )
    assert contract["protected_ast_sha256"] == (
        "sha256:cb4f0845acfa52e71ac80b7f4a333873b11af518726236d62700427d7e647141"
    )
    assert (
        pa._protected_module_ast_hash_with_only_allowed_function_bodies_replaced_by_pass(
            payload, {"run_worker"}
        )
        == contract["protected_ast_sha256"]
    )
    assert pa._run_worker_admission_is_first(payload) is True
    assert overlay["profiles"][pa.G1A3_R1_ACTIVE_PROFILE]["source_contract"] == {
        "antigravity_allowed_mutation": "run_worker_body_only",
        "antigravity_runtime_source_parsing_contract": pa.G1A3_RUNTIME_SOURCE_PARSING_CONTRACT,
        "run_worker_first_admission_contract": pa.G1A3_RUN_WORKER_FIRST_ADMISSION_CONTRACT,
        "integration_allowed_mutation": "record_integration_body_only",
        "record_integration_first_admission_contract": pa.G1A3_RECORD_INTEGRATION_FIRST_ADMISSION_CONTRACT,
    }
    assert pa.g1a3_review_producer_contract_reasons(ROOT) == []


def test_g1a3_run_worker_body_change_after_admission_is_admitted(
    tmp_path: Path,
) -> None:
    root = _policy_sandbox(tmp_path)
    path = root / "scripts/ariadne_antigravity.py"
    source = path.read_text(encoding="utf-8")
    admission = _run_worker_admission_source()
    updated = source.replace(
        admission,
        admission + "    complete_review_binding_enabled = True\n",
        1,
    )
    assert updated != source
    path.write_text(updated, encoding="utf-8")

    assert pa.g1a3_review_producer_contract_reasons(root) == []


@pytest.mark.parametrize(
    ("symbol", "needle"),
    [
        ("WorktreeState", "class WorktreeState:\n"),
        ("inspect_worktree", "def inspect_worktree("),
    ],
)
def test_g1a3_worktree_state_and_inspector_are_fully_immutable(
    tmp_path: Path, symbol: str, needle: str
) -> None:
    root = _policy_sandbox(tmp_path)
    path = root / "scripts/ariadne_antigravity.py"
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    node = next(item for item in tree.body if getattr(item, "name", None) == symbol)
    lines = source.splitlines(keepends=True)
    lines.insert(node.body[0].lineno - 1, "    synthetic_contract_drift = None\n")
    path.write_text("".join(lines), encoding="utf-8")

    reasons = pa.g1a3_review_producer_contract_reasons(root)
    assert "g1a_3_non_review_binding_code_changed" in reasons
    assert "g1a_3_protected_review_producer_symbol_changed" in reasons


@pytest.mark.parametrize(
    ("needle", "replacement"),
    [
        ("class WorktreeState:\n", "class ReboundWorktreeState:\n"),
        (
            "def inspect_worktree(cwd: Path, *, require_clean: bool) -> WorktreeState:\n",
            "def inspect_worktree(cwd: object, *, require_clean: bool) -> WorktreeState:\n",
        ),
    ],
    ids=["worktree-state-definition", "inspect-worktree-definition"],
)
def test_g1a3_worktree_state_and_inspector_definition_changes_are_rejected(
    tmp_path: Path, needle: str, replacement: str
) -> None:
    root = _policy_sandbox(tmp_path)
    path = root / "scripts/ariadne_antigravity.py"
    source = path.read_text(encoding="utf-8")
    updated = source.replace(needle, replacement, 1)
    assert updated != source
    path.write_text(updated, encoding="utf-8")

    reasons = pa.g1a3_review_producer_contract_reasons(root)
    assert "g1a_3_non_review_binding_code_changed" in reasons
    assert "g1a_3_protected_review_producer_symbol_changed" in reasons


@pytest.mark.parametrize(
    "replacement",
    [
        "@staticmethod\ndef run_worker(\n",
        "def run_worker(\n    marker: object = None,\n    *,\n",
        "def run_worker(\n    *,\n    packet_path: Path = Path('changed'),\n",
        "def run_worker(\n    *,\n    packet_path: object,\n",
        "def run_worker(\n    *,\n    renamed_packet_path: Path,\n",
        "def run_worker(\n    *,\n    packet_path: Path,\n    extra_parameter: object,\n",
        "RETURN_ANNOTATION",
        "async def run_worker(\n",
    ],
    ids=[
        "decorator",
        "positional-default",
        "keyword-only-default",
        "annotation",
        "parameter-name",
        "parameter-shape",
        "signature-baseline-control",
        "async-function",
    ],
)
def test_g1a3_run_worker_definition_metadata_is_immutable(
    tmp_path: Path, replacement: str
) -> None:
    root = _policy_sandbox(tmp_path)
    path = root / "scripts/ariadne_antigravity.py"
    source = path.read_text(encoding="utf-8")
    if replacement == "RETURN_ANNOTATION":
        updated = source.replace(") -> dict:\n", ") -> object:\n", 1)
    elif replacement.startswith("def run_worker(\n    *,\n    packet_path: Path,\n"):
        updated = source.replace(
            "def run_worker(\n    *,\n    packet_path: Path,\n",
            replacement,
            1,
        )
    else:
        updated = source.replace("def run_worker(\n", replacement, 1)
    assert updated != source
    path.write_text(updated, encoding="utf-8")

    assert pa.g1a3_review_producer_contract_reasons(root)


@pytest.mark.parametrize("surface", ["default", "decorator"])
@pytest.mark.parametrize("effect", ["filesystem", "git_subprocess"])
def test_g1a3_import_time_review_producer_effects_are_rejected_before_import(
    tmp_path: Path, surface: str, effect: str
) -> None:
    root = _policy_sandbox(tmp_path)
    path = root / "scripts/ariadne_antigravity.py"
    source = path.read_text(encoding="utf-8")
    probe = tmp_path / f"{surface}-{effect}-probe"
    if effect == "filesystem":
        expression = f"Path({str(probe)!r}).write_text('executed', encoding='utf-8')"
    else:
        expression = (
            f"__import__('subprocess').run(['git', 'init', {str(probe)!r}], check=True)"
        )
    if surface == "default":
        replacement = f"def run_worker(\n    marker: object = {expression},\n    *,\n"
        updated = source.replace("def run_worker(\n    *,\n", replacement, 1)
    else:
        decorator = f"@(lambda function: ({expression} and function))\n"
        updated = source.replace(
            "def run_worker(\n", decorator + "def run_worker(\n", 1
        )
    assert updated != source
    path.write_text(updated, encoding="utf-8")

    assert not probe.exists()
    assert pa.g1a3_review_producer_contract_reasons(root)
    assert not probe.exists()


@pytest.mark.parametrize("mutation", ["missing", "moved", "wrapped", "changed"])
def test_g1a3_run_worker_admission_call_must_remain_exactly_first(
    tmp_path: Path, mutation: str
) -> None:
    root = _policy_sandbox(tmp_path)
    path = root / "scripts/ariadne_antigravity.py"
    source = path.read_text(encoding="utf-8")
    admission = _run_worker_admission_source()
    if mutation == "missing":
        updated = source.replace(admission, "", 1)
    elif mutation == "moved":
        updated = source.replace(
            admission, "    before_admission = True\n" + admission, 1
        )
    elif mutation == "wrapped":
        updated = source.replace(
            admission,
            "    if True:\n"
            + "".join("    " + line for line in admission.splitlines(keepends=True)),
            1,
        )
    else:
        updated = source.replace(
            '        entrypoint="provider_invocation",\n',
            '        entrypoint="worker_dispatch",\n',
            1,
        )
    assert updated != source
    path.write_text(updated, encoding="utf-8")

    reasons = pa.g1a3_review_producer_contract_reasons(root)
    assert "g1a_3_run_worker_admission_not_first" in reasons


@pytest.mark.parametrize("mutation", ["missing", "moved", "wrapped", "changed"])
def test_g1a3_record_integration_admission_call_must_remain_exactly_first(
    tmp_path: Path, mutation: str
) -> None:
    root = _policy_sandbox(tmp_path)
    path = root / "scripts/agent_worktrees.py"
    source = path.read_text(encoding="utf-8")
    header = "def record_integration(args: argparse.Namespace) -> None:\n"
    admission = '    _require_command_admission(args, entrypoint="integration")\n'
    needle = header + admission
    if mutation == "missing":
        updated = source.replace(needle, header, 1)
    elif mutation == "moved":
        updated = source.replace(
            needle, header + "    before_admission = True\n" + admission, 1
        )
    elif mutation == "wrapped":
        updated = source.replace(needle, header + "    if True:\n    " + admission, 1)
    else:
        updated = source.replace(
            needle,
            header
            + '    _require_command_admission(args, entrypoint="worker_dispatch")\n',
            1,
        )
    assert updated != source
    path.write_text(updated, encoding="utf-8")

    reasons = pa.g1a3_integration_contract_reasons(root)
    assert "g1a_3_record_integration_admission_not_first" in reasons


def test_g1a2_hash_semantics_and_digest_remain_unchanged() -> None:
    scope = yaml.safe_load((ROOT / pa.G1A_SCOPE_PATH).read_text(encoding="utf-8"))
    g1a2 = scope["subgates"]["G1A.2"]
    contract = g1a2["immutable_provider_contract"]
    payload = pa._git_object_bytes(
        ROOT, f"{contract['source_commit']}:{contract['path']}"
    )

    assert contract["hash_semantics"] == (
        "sha256_of_ast_dump_with_allowed_mutation_symbols_replaced_by_pass"
    )
    assert contract["protected_ast_sha256"] == (
        "sha256:30e1e223a18ec9ac7b88fa8f338550abad1a5613feb985574af0299eb533edbc"
    )
    assert (
        pa._protected_module_ast_hash(payload, set(g1a2["allowed_mutation_symbols"]))
        == contract["protected_ast_sha256"]
    )


def test_g1a3_baseline_blob_satisfies_body_only_contract() -> None:
    scope = yaml.safe_load((ROOT / pa.G1A_SCOPE_PATH).read_text(encoding="utf-8"))
    g1a3 = scope["subgates"]["G1A.3"]
    contract = g1a3["immutable_integration_consumer_contract"]
    payload = pa._git_object_bytes(
        ROOT, f"{contract['source_commit']}:{contract['path']}"
    )

    assert contract["source_blob"] == ("f15d13f60c2c93edef0559b7b30b536b334bb884")
    assert (
        pa._run_git(
            ROOT,
            "rev-parse",
            f"{contract['source_commit']}:{contract['path']}",
        )
        == contract["source_blob"]
    )
    assert contract["hash_semantics"] == (
        "sha256_of_ast_dump_with_only_allowed_function_bodies_replaced_by_pass"
    )
    assert contract["runtime_source_parsing_contract"] == (
        pa.G1A3_RUNTIME_SOURCE_PARSING_CONTRACT
    )
    assert contract["first_executable_statement_contract"] == (
        pa.G1A3_RECORD_INTEGRATION_FIRST_ADMISSION_CONTRACT
    )
    assert contract["protected_ast_sha256"] == (
        "sha256:e016601c0c6f577ae51beecc0fb47e8ec28b235458b5e2cc6031e4a5babb57f6"
    )
    assert (
        pa._protected_module_ast_hash_with_only_allowed_function_bodies_replaced_by_pass(
            payload, set(g1a3["integration_allowed_mutation_symbols"])
        )
        == contract["protected_ast_sha256"]
    )
    assert pa._record_integration_admission_is_first(payload) is True


@pytest.mark.parametrize("prefix", [b"", b"# coding: utf-8\n"])
def test_g1a3_runtime_source_parser_admits_utf8_baseline_and_cookie(
    tmp_path: Path, prefix: bytes
) -> None:
    root = _policy_sandbox(tmp_path)
    path = root / "scripts/agent_worktrees.py"
    path.write_bytes(prefix + path.read_bytes())

    assert pa.g1a3_integration_contract_reasons(root) == []


@pytest.mark.parametrize(
    "encoded_expression",
    [
        b'__import__("pathlib").Path("g1a3-source-probe").write_text("executed")',
        b'__import__("subprocess").run(["git", "status"], check=False)',
    ],
    ids=["filesystem-write", "subprocess-git"],
)
def test_g1a3_utf7_encoded_top_level_effect_is_rejected_before_import(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    encoded_expression: bytes,
) -> None:
    monkeypatch.chdir(tmp_path)
    future = b"from __future__ import annotations\n"
    baseline = (
        b"# coding: utf-7\n"
        + future
        + b"\ndef record_integration(value):\n    return value\n"
    )
    encoded_line = b"# +AAo-" + encoded_expression + b"+AAo-#\n"
    payload = baseline.replace(future, future + encoded_line, 1)
    assert payload != baseline

    monitored_tree = pa._runtime_faithful_python_module_ast(payload)
    runtime_tree = compile(
        payload,
        "synthetic-agent-worktrees.py",
        "exec",
        flags=ast.PyCF_ONLY_AST | ast.PyCF_TYPE_COMMENTS,
        dont_inherit=True,
    )
    forced_utf8_tree = ast.parse(payload.decode("utf-8"), type_comments=True)

    assert isinstance(runtime_tree, ast.Module)
    assert ast.dump(monitored_tree, include_attributes=False) == ast.dump(
        runtime_tree, include_attributes=False
    )
    assert len(runtime_tree.body) == len(forced_utf8_tree.body) + 1
    assert (
        pa._protected_module_ast_hash_with_only_allowed_function_bodies_replaced_by_pass(
            payload, {"record_integration"}
        )
        != pa._protected_module_ast_hash_with_only_allowed_function_bodies_replaced_by_pass(
            baseline, {"record_integration"}
        )
    )
    root = _policy_sandbox(tmp_path)
    (root / "scripts/agent_worktrees.py").write_bytes(payload)
    assert "g1a_3_nonconsumer_code_changed" in pa.g1a3_integration_contract_reasons(
        root
    )
    assert not Path("g1a3-source-probe").exists()


@pytest.mark.parametrize(
    "payload_prefix",
    [
        b"# coding: emr4-unknown-codec\n",
        b"\xef\xbb\xbf# coding: latin-1\n",
    ],
    ids=["unknown-encoding", "utf8-bom-cookie-conflict"],
)
def test_g1a3_unknown_encoding_and_bom_cookie_conflict_fail_closed(
    tmp_path: Path, payload_prefix: bytes
) -> None:
    root = _policy_sandbox(tmp_path)
    path = root / "scripts/agent_worktrees.py"
    payload = payload_prefix + path.read_bytes()
    path.write_bytes(payload)

    with pytest.raises(
        pa.ProgrammeAdmissionError,
        match="g1a_3_integration_contract_source_invalid",
    ):
        pa._runtime_faithful_python_module_ast(payload)
    assert pa.g1a3_integration_contract_reasons(root) == [
        "g1a_3_allowed_function_body_contract_invalid"
    ]


@pytest.mark.parametrize(
    ("replacement", "expected_reason"),
    [
        (
            "@staticmethod\n"
            "def record_integration(args: argparse.Namespace) -> None:\n",
            "g1a_3_nonconsumer_code_changed",
        ),
        (
            "def record_integration(\n"
            "    args: argparse.Namespace = None,\n"
            ") -> None:\n",
            "g1a_3_nonconsumer_code_changed",
        ),
        (
            "def record_integration(\n"
            "    args: argparse.Namespace, *, marker: object = None\n"
            ") -> None:\n",
            "g1a_3_nonconsumer_code_changed",
        ),
        (
            "def record_integration(args: object) -> None:\n",
            "g1a_3_nonconsumer_code_changed",
        ),
        (
            "def record_integration(\n"
            "    args: argparse.Namespace, extra: object\n"
            ") -> None:\n",
            "g1a_3_nonconsumer_code_changed",
        ),
        (
            "def record_integration(args: argparse.Namespace) -> int:\n",
            "g1a_3_nonconsumer_code_changed",
        ),
        (
            "async def record_integration(args: argparse.Namespace) -> None:\n",
            "g1a_3_allowed_function_body_contract_invalid",
        ),
    ],
    ids=[
        "decorator",
        "positional-default",
        "keyword-only-default",
        "annotation",
        "parameter-shape",
        "return-annotation",
        "async-function",
    ],
)
def test_g1a3_record_integration_definition_metadata_is_immutable(
    tmp_path: Path, replacement: str, expected_reason: str
) -> None:
    root = _policy_sandbox(tmp_path)
    path = root / "scripts/agent_worktrees.py"
    source = path.read_text(encoding="utf-8")
    updated = source.replace(
        "def record_integration(args: argparse.Namespace) -> None:\n",
        replacement,
        1,
    )
    assert updated != source
    path.write_text(updated, encoding="utf-8")

    assert expected_reason in pa.g1a3_integration_contract_reasons(root)


@pytest.mark.parametrize("default_kind", ["positional", "keyword-only"])
def test_g1a3_import_time_append_log_default_is_rejected_before_import(
    tmp_path: Path, default_kind: str
) -> None:
    root = _policy_sandbox(tmp_path)
    path = root / "scripts/agent_worktrees.py"
    source = path.read_text(encoding="utf-8")
    effect_root = tmp_path / "import-time-effect"
    expression = (
        "append_integration_log(agent='synthetic', task='synthetic', "
        "branch='synthetic', review='import-time', "
        "integration_commit='synthetic', result='integrated', follow_up='', "
        f"repo_root=Path({str(effect_root)!r}))"
    )
    if default_kind == "positional":
        replacement = (
            "def record_integration(\n"
            f"    args: argparse.Namespace = {expression},\n"
            ") -> None:\n"
        )
    else:
        replacement = (
            "def record_integration(\n"
            "    args: argparse.Namespace, *,\n"
            f"    marker: object = {expression},\n"
            ") -> None:\n"
        )
    path.write_text(
        source.replace(
            "def record_integration(args: argparse.Namespace) -> None:\n",
            replacement,
            1,
        ),
        encoding="utf-8",
    )

    assert not (effect_root / "orchestration/integration_log.md").exists()
    assert "g1a_3_nonconsumer_code_changed" in (
        pa.g1a3_integration_contract_reasons(root)
    )
    assert not (effect_root / "orchestration/integration_log.md").exists()


@pytest.mark.parametrize(
    "expression",
    [
        'run_git(["status"])',
        'subprocess.run(["git", "status"], check=False)',
    ],
    ids=["run-git", "subprocess"],
)
def test_g1a3_import_time_process_default_is_rejected_before_import(
    tmp_path: Path, expression: str
) -> None:
    root = _policy_sandbox(tmp_path)
    path = root / "scripts/agent_worktrees.py"
    source = path.read_text(encoding="utf-8")
    replacement = (
        "def record_integration(\n"
        f"    args: argparse.Namespace = {expression},\n"
        ") -> None:\n"
    )
    path.write_text(
        source.replace(
            "def record_integration(args: argparse.Namespace) -> None:\n",
            replacement,
            1,
        ),
        encoding="utf-8",
    )

    assert "g1a_3_nonconsumer_code_changed" in (
        pa.g1a3_integration_contract_reasons(root)
    )


@pytest.mark.parametrize("mutation", ["missing", "duplicate", "malformed"])
def test_g1a3_missing_duplicate_or_malformed_allowed_function_fails_closed(
    tmp_path: Path, mutation: str
) -> None:
    root = _policy_sandbox(tmp_path)
    path = root / "scripts/agent_worktrees.py"
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    node = next(
        item
        for item in tree.body
        if isinstance(item, ast.FunctionDef) and item.name == "record_integration"
    )
    segment = ast.get_source_segment(source, node)
    assert segment is not None
    if mutation == "duplicate":
        updated = f"{source.rstrip()}\n\n{segment}\n"
        path.write_text(updated, encoding="utf-8")
    elif mutation == "missing":
        lines = source.splitlines(keepends=True)
        del lines[node.lineno - 1 : node.end_lineno]
        path.write_text("".join(lines), encoding="utf-8")
    else:
        path.write_bytes(
            source.replace(
                "def record_integration(args: argparse.Namespace) -> None:\n",
                "def record_integration(:\n",
                1,
            ).encode("utf-8")
        )

    assert pa.g1a3_integration_contract_reasons(root) == [
        "g1a_3_allowed_function_body_contract_invalid"
    ]


def test_g1a3_body_only_hash_preserves_type_comment_metadata() -> None:
    baseline = b"def record_integration(value):\n    return value\n"
    body_changed = b"def record_integration(value):\n    return None\n"
    type_comment_changed = (
        b"def record_integration(value):  # type: (int) -> int\n    return value\n"
    )
    allowed = {"record_integration"}

    assert (
        pa._protected_module_ast_hash_with_only_allowed_function_bodies_replaced_by_pass(
            baseline, allowed
        )
        == pa._protected_module_ast_hash_with_only_allowed_function_bodies_replaced_by_pass(
            body_changed, allowed
        )
    )
    assert (
        pa._protected_module_ast_hash_with_only_allowed_function_bodies_replaced_by_pass(
            baseline, allowed
        )
        != pa._protected_module_ast_hash_with_only_allowed_function_bodies_replaced_by_pass(
            type_comment_changed, allowed
        )
    )


@pytest.mark.skipif(
    sys.version_info < (3, 12), reason="PEP 695 syntax needs Python 3.12"
)
def test_g1a3_body_only_hash_preserves_type_parameters_when_supported() -> None:
    baseline = b"def record_integration[T](value: T) -> T:\n    return value\n"
    changed = b"def record_integration[U](value: U) -> U:\n    return value\n"
    allowed = {"record_integration"}

    assert (
        pa._protected_module_ast_hash_with_only_allowed_function_bodies_replaced_by_pass(
            baseline, allowed
        )
        != pa._protected_module_ast_hash_with_only_allowed_function_bodies_replaced_by_pass(
            changed, allowed
        )
    )


@pytest.mark.parametrize(
    "symbol",
    [
        "_require_command_admission",
        "append_integration_log",
        "build_parser",
        "main",
        "run_git",
        "push_handoff_refs",
        "handoff",
        "sync",
        "realign",
        "submit",
        "dispatch",
        "ensure_integration_log",
        "integration_log_records",
    ],
)
def test_every_protected_g1a3_integration_symbol_is_immutable(
    tmp_path: Path, symbol: str
) -> None:
    root = _policy_sandbox(tmp_path)
    path = root / "scripts/agent_worktrees.py"
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    node = next(
        item
        for item in tree.body
        if isinstance(item, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
        and item.name == symbol
    )
    lines = source.splitlines(keepends=True)
    lines.insert(node.body[0].lineno - 1, "    synthetic_contract_drift = None\n")
    path.write_text("".join(lines), encoding="utf-8")

    reasons = pa.g1a3_integration_contract_reasons(root)

    assert "g1a_3_nonconsumer_code_changed" in reasons
    assert "g1a_3_protected_integration_symbol_changed" in reasons


def _scope_git_stub(
    manifest: dict,
    *,
    commit_count: int = 1,
    changed: str = "AGENTS.md",
    remote: str | None = "base",
):
    head = manifest["candidate_or_current_head"]
    branch = "codex/raisa-ariadne-recovery-g0"

    def run(_root: Path, *args: str) -> str:
        if args == ("branch", "--show-current"):
            return branch
        if args == ("rev-parse", "HEAD"):
            return head
        if args == ("rev-parse", f"origin/{branch}"):
            return manifest["base_commit"]
        if args[:2] == ("rev-list", "--count"):
            return str(commit_count)
        if args[:2] == ("rev-list", "--reverse"):
            return manifest["base_commit"]
        if args[:2] == ("diff", "--name-only"):
            return changed if "..HEAD" in args[-1] else ""
        if args == ("diff", "--cached", "--name-only"):
            return ""
        if args == ("status", "--porcelain", "--untracked-files=no"):
            return ""
        if args == ("write-tree",):
            return head
        if args == (
            "rev-parse",
            "--path-format=absolute",
            "--git-common-dir",
        ):
            return str((ROOT / ".git").resolve())
        if args[:2] == ("ls-remote", "--refs"):
            observed = manifest["base_commit"] if remote == "base" else remote
            return "" if observed is None else f"{observed}\trefs/heads/{branch}"
        raise AssertionError(args)

    return run


def _admitted(policy: pa.ProgrammePolicy) -> ProgrammeDecision:
    return ProgrammeDecision(
        pa.DECISION_VERSION,
        True,
        [],
        "recovery",
        "G0",
        pa.ADMITTED_TASK_CLASS,
        policy.state_digest,
        policy.policy_digest,
    )


def _changes(
    path: str = "AGENTS.md",
) -> tuple[list[GitPathChange], list[GitPathChange], list[GitPathChange]]:
    rows = [GitPathChange("M", path, "100644", "100644")]
    return rows, rows, []


def test_committed_product_path_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    policy = load_programme_policy(ROOT)
    manifest = _manifest()
    monkeypatch.setattr(pa, "load_programme_policy", lambda _root: policy)
    monkeypatch.setattr(
        pa, "evaluate_programme_admission", lambda **_kwargs: _admitted(policy)
    )
    monkeypatch.setattr(
        pa,
        "_validate_manifest",
        lambda value, **_kwargs: (value, value["allowed_path_roots"]),
    )
    monkeypatch.setattr(pa, "g1a2_provider_contract_reasons", lambda _root: [])
    monkeypatch.setattr(pa, "_is_ancestor", lambda *_args: True)
    monkeypatch.setattr(
        pa, "_run_git", _scope_git_stub(manifest, changed="app/main.py")
    )
    monkeypatch.setattr(
        pa,
        "_scope_change_inventories",
        lambda *_args, **_kwargs: _changes("app/main.py"),
    )

    decision = evaluate_committed_scope(
        repo_root=ROOT, manifest=manifest, phase="pre-push"
    )

    assert decision.admitted is False
    assert "scope_path_outside_policy" in decision.reason_codes


def test_later_commit_after_candidate_is_rejected(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    policy = load_programme_policy(ROOT)
    manifest = _manifest()
    monkeypatch.setattr(pa, "load_programme_policy", lambda _root: policy)
    monkeypatch.setattr(
        pa, "evaluate_programme_admission", lambda **_kwargs: _admitted(policy)
    )
    monkeypatch.setattr(
        pa,
        "_validate_manifest",
        lambda value, **_kwargs: (value, value["allowed_path_roots"]),
    )
    monkeypatch.setattr(pa, "g1a2_provider_contract_reasons", lambda _root: [])
    monkeypatch.setattr(pa, "_is_ancestor", lambda *_args: True)
    monkeypatch.setattr(pa, "_run_git", _scope_git_stub(manifest, commit_count=2))
    monkeypatch.setattr(
        pa, "_scope_change_inventories", lambda *_args, **_kwargs: _changes()
    )

    decision = evaluate_committed_scope(
        repo_root=ROOT, manifest=manifest, phase="pre-push"
    )

    assert decision.admitted is False
    assert "scope_candidate_commit_count_invalid" in decision.reason_codes


@pytest.mark.parametrize("remote", [None, "0" * 40])
def test_post_push_missing_or_mismatched_origin_is_rejected(
    monkeypatch: pytest.MonkeyPatch, remote: str | None
) -> None:
    policy = load_programme_policy(ROOT)
    manifest = _manifest()
    monkeypatch.setattr(pa, "load_programme_policy", lambda _root: policy)
    monkeypatch.setattr(
        pa, "evaluate_programme_admission", lambda **_kwargs: _admitted(policy)
    )
    monkeypatch.setattr(
        pa,
        "_validate_manifest",
        lambda value, **_kwargs: (value, value["allowed_path_roots"]),
    )
    monkeypatch.setattr(pa, "g1a2_provider_contract_reasons", lambda _root: [])
    monkeypatch.setattr(pa, "_is_ancestor", lambda *_args: True)
    monkeypatch.setattr(pa, "_run_git", _scope_git_stub(manifest, remote=remote))
    monkeypatch.setattr(
        pa, "_scope_change_inventories", lambda *_args, **_kwargs: _changes()
    )

    decision = evaluate_committed_scope(
        repo_root=ROOT, manifest=manifest, phase="post-push"
    )

    assert decision.admitted is False
    assert any(
        reason.startswith("scope_fresh_origin")
        or reason == "scope_origin_head_mismatch"
        for reason in decision.reason_codes
    )


def test_review_pending_latch_cannot_resume_implementation(tmp_path: Path) -> None:
    root = _policy_sandbox(tmp_path)
    path = root / pa.LATCH_PATH
    latch = json.loads(path.read_text(encoding="utf-8"))
    latch["status"] = "in_progress"
    _write_json(path, latch)

    with pytest.raises(
        ProgrammeAdmissionError,
        match="g1b1_closeout_review_pending_latch_invalid",
    ):
        load_programme_policy(root)


def test_current_replacement_operation_identity_is_exact_across_control_surfaces() -> (
    None
):
    expected = pa.G1B1_CLOSEOUT_TASK_GENERATION
    state = json.loads((ROOT / pa.STATE_PATH).read_text(encoding="utf-8"))
    latch = json.loads((ROOT / pa.LATCH_PATH).read_text(encoding="utf-8"))
    agents = (ROOT / pa.AGENTS_PATH).read_text(encoding="utf-8")
    narrative = (ROOT / "docs/programme/raisa-ariadne-recovery-programme.md").read_text(
        encoding="utf-8"
    )
    g1b_plan = (ROOT / "docs/architecture/ariadne-g1b-state-machine-plan.md").read_text(
        encoding="utf-8"
    )

    assert state["active_profile"] == pa.G1B1_CLOSEOUT_REVIEW_PENDING_PROFILE
    assert state["authority"]["directive_sha256"] == (pa.G1B1_CLOSEOUT_DIRECTIVE_SHA256)
    assert state["g1b"]["next_action"] == (
        "external_G1B1_closeout_G1B2_transition_enablement_review_only"
    )
    assert latch["operation_id"] == expected
    assert latch["active_tranche"] == pa.G1B1_CLOSEOUT_TRANCHE
    assert latch["objective"] == pa.G1B1_CLOSEOUT_OBJECTIVE
    assert latch["authority_source"] == pa.G1B1_CLOSEOUT_AUTHORITY
    assert latch["checkpoint"]["completed_stage"] == pa.G1B1_CLOSEOUT_COMPLETED_STAGE
    assert latch["checkpoint"]["next_executable_stage"] == pa.G1B1_CLOSEOUT_NEXT_STAGE
    assert f"Task generation `{expected}`" in agents
    assert expected in narrative
    assert expected in g1b_plan


@pytest.mark.parametrize(
    ("case", "expected_reason"),
    [
        ("state_next_action", "g1b_state_invalid"),
        (
            "latch_operation_id",
            "g1b1_closeout_review_pending_latch_invalid",
        ),
        (
            "latch_active_tranche",
            "g1b1_closeout_review_pending_latch_invalid",
        ),
        ("latch_objective", "g1b1_closeout_review_pending_latch_invalid"),
        (
            "latch_authority_source",
            "g1b1_closeout_review_pending_latch_invalid",
        ),
        (
            "latch_completed_stage",
            "g1b1_closeout_review_pending_latch_invalid",
        ),
        (
            "latch_next_stage",
            "g1b1_closeout_review_pending_latch_invalid",
        ),
        ("agents_task_generation", "agents_recovery_operation_identity_invalid"),
    ],
)
def test_current_replacement_operation_identity_drift_matrix_fails_closed(
    tmp_path: Path, case: str, expected_reason: str
) -> None:
    root = _policy_sandbox(tmp_path)
    stale = "g1a-closeout-g1b-enablement-stale-operation"
    if case == "state_next_action":
        path = root / pa.STATE_PATH
        state = json.loads(path.read_text(encoding="utf-8"))
        state["g1b"]["next_action"] = stale
        _write_json(path, state)
    elif case.startswith("latch_"):
        path = root / pa.LATCH_PATH
        latch = json.loads(path.read_text(encoding="utf-8"))
        key_by_case = {
            "latch_operation_id": ("operation_id",),
            "latch_active_tranche": ("active_tranche",),
            "latch_objective": ("objective",),
            "latch_authority_source": ("authority_source",),
            "latch_completed_stage": ("checkpoint", "completed_stage"),
            "latch_next_stage": ("checkpoint", "next_executable_stage"),
        }
        keys = key_by_case[case]
        target = latch
        for key in keys[:-1]:
            target = target[key]
        target[keys[-1]] = stale
        _write_json(path, latch)
    else:
        path = root / pa.AGENTS_PATH
        text = path.read_text(encoding="utf-8").replace(
            pa.G1B1_CLOSEOUT_TASK_GENERATION,
            stale,
        )
        path.write_bytes(text.encode("utf-8"))
        _git(root, "add", "--", pa.AGENTS_PATH.as_posix())

    with pytest.raises(ProgrammeAdmissionError, match=expected_reason):
        load_programme_policy(root)


def test_agents_emergency_header_has_machine_precedence(tmp_path: Path) -> None:
    root = _policy_sandbox(tmp_path)
    path = root / pa.AGENTS_PATH
    text = path.read_text(encoding="utf-8")
    path.write_bytes(text.split("# EMR4 Centaur", 1)[1].encode("utf-8"))
    _git(root, "add", "--", pa.AGENTS_PATH.as_posix())

    with pytest.raises(
        ProgrammeAdmissionError, match="agents_recovery_precedence_missing"
    ):
        load_programme_policy(root)


@pytest.mark.parametrize("entrypoint", sorted(pa.ENTRYPOINTS_CLOSED_IN_G0))
def test_forbidden_side_effect_entrypoints_remain_closed(entrypoint: str) -> None:
    decision = evaluate_programme_admission(
        repo_root=ROOT, manifest=_manifest(), entrypoint=entrypoint
    )

    assert decision.admitted is False
    assert decision.reason_codes == [f"{entrypoint}_closed_in_active_profile"]


def test_machine_state_claims_only_exact_g1a2_implementation_acceptance() -> None:
    policy = load_programme_policy(ROOT)

    authority = policy.state["g1a_subgate_authority"]
    decisive_id = authority["decisive_implementation_review_id"]
    decisive = authority["implementation_review_history"][0]
    assert decisive["review_id"] == decisive_id
    assert decisive["reviewed_commit"] == ("37e2d6f51ebbdb281771f922a5f460fd23e2571b")
    assert decisive["reviewed_tree"] == "798a2eda11438fe05da2528298006775774ccfc4"
    assert decisive["reviewed_parent"] == ("474d79e0ef918dc8e7fef6780ea34c5c105fe236")
    assert decisive["verdict"] == "PASS"
    assert decisive["blocking_finding_count"] == 0
    assert authority["decisive_g1a3_transition_enablement_review_id"] == (
        "g1a3-e0-review-e5cb887-independent-20260829-pass"
    )
    assert authority["g1a3_transition_enablement_review_history"] == [
        {
            "review_id": "g1a3-e0-review-e5cb887-independent-20260829-pass",
            "review_record_path": "orchestration/programme/subgate-transition-enablement-reviews/g1a3-e0-review-e5cb887-independent-20260829-pass.json",
            "reviewed_commit": "e5cb887090ea1cafdce30e4e1d787940f5622104",
            "reviewed_tree": "848d1a3602a1f6c1cc17edc9e3e3c54e16fc3152",
            "reviewed_parent": "37e2d6f51ebbdb281771f922a5f460fd23e2571b",
            "verdict": "PASS",
            "blocking_finding_count": 0,
            "reviewer_surface": "external_chatgpt_repository_review",
            "g1a3_state_transition_authorized": True,
            "g1a3_implementation_authorized": False,
            "provider_invocation_authorized": False,
            "integration_authorized": False,
            "review_record_sha256": "sha256:8c695d7694b5f41b3f9cba20efdef576d2b27f655cce8d12174edf7f3dfda9fc",
        }
    ]


def test_production_review_history_uses_real_resolving_commit_trees() -> None:
    policy = load_programme_policy(ROOT)
    state = policy.state
    expected = [
        (
            state["g0_1_correction"]["authorized_parent_commit"],
            state["g0_1_correction"]["reviewed_g0_tree"],
        ),
        (
            state["g0_2_correction"]["authorized_parent_commit"],
            state["g0_2_correction"]["reviewed_g0_1_tree"],
        ),
        (
            state["g0_3_correction"]["authorized_parent_commit"],
            "bbeddb0e467c57970024d14cddf72156bed86947",
        ),
        (
            state["g0_4_correction"]["authorized_parent_commit"],
            "9da62d169d564c86afdd087ec03da270e4989d91",
        ),
        (
            state["g0_5_correction"]["authorized_parent_commit"],
            "e061800df0ae7c5daba6b2db13e8aa774f3eaff9",
        ),
        (
            state["g0_6_correction"]["authorized_parent_commit"],
            "ef84162bbc6ef24241678d14e0183b876af3a1e3",
        ),
        (
            state["g0_7_correction"]["authorized_parent_commit"],
            "a23cc914dddd1e17121f7b04083ee1c08338549a",
        ),
        (
            state["g0_8_correction"]["authorized_parent_commit"],
            "00c1af2f47ceee88c10507809f69058c24c6bd85",
        ),
    ]
    for commit, tree in expected:
        assert _git(ROOT, "rev-parse", f"{commit}^{{tree}}") == tree
        assert _git(ROOT, "rev-parse", f"{tree}^{{tree}}") == tree
    assert len(state["g0_acceptance"]["external_review_history"]) == 9


def test_false_g0_2_tree_binding_is_rejected_and_unresolved() -> None:
    false_tree = "bbeddb0e129f5787d7852913d72e3409ae65b1d8"
    completed = subprocess.run(
        ["git", "cat-file", "-e", f"{false_tree}^{{tree}}"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode != 0


@pytest.mark.parametrize(
    ("section", "field"),
    [
        ("g0_1_correction", "reviewed_g0_tree"),
        ("g0_2_correction", "reviewed_g0_1_tree"),
        ("g0_3_correction", "reviewed_g0_2_tree"),
        ("g0_4_correction", "reviewed_g0_3_tree"),
        ("g0_5_correction", "reviewed_g0_4_tree"),
        ("g0_6_correction", "reviewed_g0_5_tree"),
        ("g0_7_correction", "reviewed_g0_6_tree"),
        ("g0_8_correction", "reviewed_g0_7_tree"),
    ],
)
def test_retained_review_history_cannot_rewrite_tree_bindings(
    tmp_path: Path, section: str, field: str
) -> None:
    root = _policy_sandbox(tmp_path)
    path = root / pa.STATE_PATH
    state = json.loads(path.read_text(encoding="utf-8"))
    state[section][field] = "0" * 40
    _write_json(path, state)
    with pytest.raises(
        ProgrammeAdmissionError,
        match="review.*binding_invalid|decisive_external_review_binding_invalid",
    ):
        load_programme_policy(root)


def test_retained_review_record_bytes_are_immutable(tmp_path: Path) -> None:
    root = _policy_sandbox(tmp_path)
    state = json.loads((root / pa.STATE_PATH).read_text(encoding="utf-8"))
    retained = state["g0_acceptance"]["external_review_history"][0]
    path = root / retained["review_record_path"]
    path.write_bytes(path.read_bytes() + b" ")
    _stage_written_repository_path(path)

    with pytest.raises(ProgrammeAdmissionError, match="review_record_digest_mismatch"):
        load_programme_policy(root)


@pytest.mark.parametrize("case", ["delete", "reorder", "digest", "rewrite_and_rebind"])
def test_retained_review_ledger_cannot_be_deleted_reordered_or_rebound(
    tmp_path: Path, case: str
) -> None:
    root = _policy_sandbox(tmp_path)
    path = root / pa.STATE_PATH
    state = json.loads(path.read_text(encoding="utf-8"))
    history = state["g0_acceptance"]["external_review_history"]
    if case == "delete":
        del history[1]
    elif case == "reorder":
        history[0], history[1] = history[1], history[0]
    elif case == "digest":
        history[0]["review_record_sha256"] = "sha256:" + "0" * 64
    else:
        record_path = root / history[0]["review_record_path"]
        record = json.loads(record_path.read_text(encoding="utf-8"))
        record["reviewer_surface"] = "rewritten_external_review"
        history[0]["reviewer_surface"] = "rewritten_external_review"
        _write_json(record_path, record)
        history[0]["review_record_sha256"] = (
            "sha256:" + hashlib.sha256(record_path.read_bytes()).hexdigest()
        )
    _write_json(path, state)

    with pytest.raises(
        ProgrammeAdmissionError,
        match="retained_external_review_history_invalid|review_record_digest_mismatch",
    ):
        load_programme_policy(root)


def test_gated_executable_sources_require_programme_admission() -> None:
    sources = {
        "scripts/ariadne_antigravity.py": "provider_invocation",
        "scripts/ariadne_deepseek_claude.py": "provider_invocation",
        "scripts/drive_agent_headless.py": "provider_invocation",
        "scripts/ariadne_governance_clockwork_tick.py": "clockwork_tick_mutation",
        "scripts/ariadne_governance_clockwork_closeout.py": "clockwork_closeout_mutation",
        "scripts/agent_worktrees.py": "worker_dispatch",
    }
    for relative, entrypoint in sources.items():
        source = (ROOT / relative).read_text(encoding="utf-8")
        assert "require_programme_admission(" in source
        assert f'"{entrypoint}"' in source


def _git(root: Path, *args: str, input_text: str | None = None) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=root,
        input=input_text,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return completed.stdout.strip()


def _new_inventory_repo(tmp_path: Path) -> tuple[Path, str]:
    root = tmp_path / "inventory-repo"
    root.mkdir()
    _git(root, "init", "-b", "inventory")
    _git(root, "config", "user.email", "tests@example.invalid")
    _git(root, "config", "user.name", "G0.2 Tests")
    _git(root, "config", "core.autocrlf", "false")
    (root / "app").mkdir()
    (root / "orchestration/programme").mkdir(parents=True)
    (root / "app/product.txt").write_text("product\n", encoding="utf-8")
    (root / "orchestration/programme/current-state.json").write_text(
        "{}\n", encoding="utf-8"
    )
    _git(root, "add", "-A")
    _git(root, "commit", "-m", "seed")
    return root, _git(root, "rev-parse", "HEAD")


def test_raw_inventory_exposes_unauthorised_source_of_pure_rename(
    tmp_path: Path,
) -> None:
    root, base = _new_inventory_repo(tmp_path)
    _git(
        root,
        "mv",
        "app/product.txt",
        "orchestration/programme/review.json",
    )

    changes = git_change_inventory(root, f"{base}..HEAD") + git_change_inventory(
        root, "--cached"
    )

    assert {(row.status, row.path) for row in changes} >= {
        ("D", "app/product.txt"),
        ("A", "orchestration/programme/review.json"),
    }
    assert {row.path for row in changes} - {"orchestration/programme/review.json"}


def test_raw_inventory_exposes_both_sides_of_modified_rename(tmp_path: Path) -> None:
    root, _base = _new_inventory_repo(tmp_path)
    _git(
        root,
        "mv",
        "app/product.txt",
        "orchestration/programme/review.json",
    )
    with (root / "orchestration/programme/review.json").open(
        "a", encoding="utf-8"
    ) as stream:
        stream.write("modified\n")
    _git(root, "add", "-A")

    changes = git_change_inventory(root, "--cached")

    assert {(row.status, row.path) for row in changes} == {
        ("D", "app/product.txt"),
        ("A", "orchestration/programme/review.json"),
    }


def test_raw_inventory_exposes_unauthorised_deletion(tmp_path: Path) -> None:
    root, _base = _new_inventory_repo(tmp_path)
    _git(root, "rm", "app/product.txt")

    changes = git_change_inventory(root, "--cached")

    assert [(row.status, row.path) for row in changes] == [("D", "app/product.txt")]


def test_raw_inventory_rejects_symlink_substitution(tmp_path: Path) -> None:
    root, _base = _new_inventory_repo(tmp_path)
    blob = _git(root, "hash-object", "-w", "--stdin", input_text="target\n")
    _git(
        root,
        "update-index",
        "--cacheinfo",
        f"120000,{blob},orchestration/programme/current-state.json",
    )

    changes = git_change_inventory(root, "--cached")

    assert "scope_symlink_mode_forbidden" in pa._change_inventory_reasons(changes)


def test_raw_inventory_rejects_gitlink_substitution(tmp_path: Path) -> None:
    root, base = _new_inventory_repo(tmp_path)
    _git(
        root,
        "update-index",
        "--cacheinfo",
        f"160000,{base},orchestration/programme/current-state.json",
    )

    changes = git_change_inventory(root, "--cached")

    assert "scope_gitlink_mode_forbidden" in pa._change_inventory_reasons(changes)


def test_raw_inventory_preserves_windows_relevant_path_case_change(
    tmp_path: Path,
) -> None:
    root, _base = _new_inventory_repo(tmp_path)
    path = root / "orchestration/programme/Policy.json"
    path.write_text("{}\n", encoding="utf-8")
    _git(root, "add", "orchestration/programme/Policy.json")
    _git(root, "commit", "-m", "add case source")
    _git(
        root,
        "mv",
        "orchestration/programme/Policy.json",
        "orchestration/programme/case-hop.json",
    )
    _git(
        root,
        "mv",
        "orchestration/programme/case-hop.json",
        "orchestration/programme/policy.json",
    )

    changes = git_change_inventory(root, "--cached")

    assert {row.path for row in changes} == {
        "orchestration/programme/Policy.json",
        "orchestration/programme/policy.json",
    }


def test_raw_inventory_allows_ordinary_regular_file_modification(
    tmp_path: Path,
) -> None:
    root, _base = _new_inventory_repo(tmp_path)
    (root / "orchestration/programme/current-state.json").write_text(
        '{"changed": true}\n', encoding="utf-8"
    )

    changes = git_change_inventory(root)

    assert [(row.status, row.path, row.old_mode, row.new_mode) for row in changes] == [
        (
            "M",
            "orchestration/programme/current-state.json",
            "100644",
            "100644",
        )
    ]
    assert pa._change_inventory_reasons(changes) == []


def test_untracked_inventory_observes_regular_file_and_rejects_import_hooks(
    tmp_path: Path,
) -> None:
    root, _base = _new_inventory_repo(tmp_path)
    allowed = root / "orchestration_harness/verdict.py"
    allowed.parent.mkdir(parents=True)
    allowed.write_text("# new verdict\n", encoding="utf-8")
    hook = root / "sitecustomize.py"
    hook.write_text("raise RuntimeError\n", encoding="utf-8")

    inventory = pa.git_untracked_inventory(root)
    assert {(row.status, row.path) for row in inventory} == {
        ("?", "orchestration_harness/verdict.py"),
        ("?", "sitecustomize.py"),
    }
    assert "scope_import_hook_forbidden" in pa._change_inventory_reasons(inventory)


def test_untracked_inventory_rejects_symlink_or_reparse_component(
    tmp_path: Path,
) -> None:
    root, _base = _new_inventory_repo(tmp_path)
    target = tmp_path / "junction-target"
    target.mkdir()
    (target / "outside.py").write_text("outside\n", encoding="utf-8")
    link = root / "orchestration_harness"
    try:
        link.symlink_to(target, target_is_directory=True)
    except OSError:
        completed = subprocess.run(
            ["cmd.exe", "/d", "/c", "mklink", "/J", str(link), str(target)],
            check=False,
            capture_output=True,
            text=True,
        )
        if completed.returncode != 0:
            pytest.skip(f"reparse creation unavailable: {completed.stderr}")

    with pytest.raises(ProgrammeAdmissionError, match="untracked_reparse_forbidden"):
        pa.git_untracked_inventory(root)


@pytest.mark.parametrize(
    "relative_path",
    [
        ".env",
        ".env.local",
        "sitecustomize.py",
        "usercustomize.py",
        "bootstrap.pth",
        "module.pyc",
        "__pycache__/module.pyc",
        ".pytest_cache/v/cache/nodeids",
        ".venv/Lib/site-packages/runtime.py",
        "credentials.json",
    ],
)
def test_complete_inventory_observes_repository_ignored_execution_material(
    tmp_path: Path, relative_path: str
) -> None:
    root, _base = _new_inventory_repo(tmp_path)
    ignore = root / ".gitignore"
    ignore.write_text("*\n", encoding="utf-8")
    _git(root, "add", "-f", ".gitignore")
    _git(root, "commit", "-m", "ignore fixture")
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("synthetic\n", encoding="utf-8")

    inventory = pa.git_all_file_inventory(root)

    assert [(row.status, row.path) for row in inventory] == [("!", relative_path)]


@pytest.mark.parametrize("exclude_surface", ["info", "configured_global"])
def test_complete_inventory_cannot_be_blinded_by_non_repository_excludes(
    tmp_path: Path, exclude_surface: str
) -> None:
    root, _base = _new_inventory_repo(tmp_path)
    hidden = root / "hidden-runtime.py"
    hidden.write_text("synthetic\n", encoding="utf-8")
    if exclude_surface == "info":
        (root / ".git/info/exclude").write_text("hidden-runtime.py\n", encoding="utf-8")
    else:
        excludes = tmp_path / "global-excludes"
        excludes.write_text("hidden-runtime.py\n", encoding="utf-8")
        _git(root, "config", "core.excludesFile", str(excludes))

    inventory = pa.git_all_file_inventory(root)

    assert [(row.status, row.path) for row in inventory] == [("!", "hidden-runtime.py")]


@pytest.mark.parametrize(
    ("tracked", "alias"),
    [
        ("orchestration_harness/verdict.py", "orchestration_harness/Verdict.py"),
        ("tests/caf\u00e9.py", "tests/cafe\u0301.py"),
    ],
)
def test_complete_inventory_rejects_case_and_unicode_protected_path_aliases(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, tracked: str, alias: str
) -> None:
    root = tmp_path / "alias-repo"
    root.mkdir()

    def inventory(_root: Path, *args: str) -> bytes:
        if "--cached" in args:
            return tracked.encode("utf-8") + b"\0"
        if "--ignored" in args:
            return b""
        return alias.encode("utf-8") + b"\0"

    monkeypatch.setattr(pa, "_run_git_bytes", inventory)
    with pytest.raises(ProgrammeAdmissionError, match="protected_path_alias_forbidden"):
        pa.git_all_file_inventory(root)


def _remote_identity_repo(tmp_path: Path) -> tuple[Path, Path, dict]:
    root = tmp_path / "remote-repo"
    bare = tmp_path / "bound-origin.git"
    root.mkdir()
    bare.mkdir()
    _git(root, "init", "-b", "remote-test")
    _git(bare, "init", "--bare")
    _git(root, "remote", "add", "origin", str(bare))
    return root, bare, pa.build_synthetic_remote_identity_policy(bare)


def test_production_remote_identity_policy_matches_verified_repository() -> None:
    policy = load_programme_policy(ROOT).overlay["remote_identity_policy"]

    observed = pa.observe_remote_identity(ROOT, policy)

    assert observed["expected_repository_identity"] == "github.com/yurifrusin/emr4"
    assert observed["normalized_fetch_url"] == "https://github.com/yurifrusin/emr4"
    assert observed["normalized_push_url"] == observed["normalized_fetch_url"]
    assert observed["explicit_push_url_count"] == 0


def test_synthetic_bound_bare_remote_identity_passes(tmp_path: Path) -> None:
    root, _bare, policy = _remote_identity_repo(tmp_path)

    observed = pa.observe_remote_identity(root, policy)

    assert observed == policy


def test_production_policy_rejects_local_fake_bare_origin(tmp_path: Path) -> None:
    root, _bare, _synthetic = _remote_identity_repo(tmp_path)
    production = load_programme_policy(ROOT).overlay["remote_identity_policy"]

    with pytest.raises(ProgrammeAdmissionError, match="remote_identity"):
        pa.observe_remote_identity(root, production)


@pytest.mark.parametrize(
    "mutation",
    [
        "changed_fetch",
        "multiple_fetch",
        "changed_push",
        "multiple_push",
        "instead_of",
        "push_instead_of",
        "valid_fetch_redirected_push",
    ],
)
def test_remote_identity_rejects_url_and_rewrite_adversaries(
    tmp_path: Path, mutation: str
) -> None:
    root, _bare, policy = _remote_identity_repo(tmp_path)
    fake = tmp_path / "fake-origin.git"
    fake.mkdir()
    _git(fake, "init", "--bare")
    if mutation == "changed_fetch":
        _git(root, "remote", "set-url", "origin", str(fake))
    elif mutation == "multiple_fetch":
        _git(root, "config", "--add", "remote.origin.url", str(fake))
    elif mutation in {"changed_push", "valid_fetch_redirected_push"}:
        _git(root, "remote", "set-url", "--push", "origin", str(fake))
    elif mutation == "multiple_push":
        _git(root, "config", "--add", "remote.origin.pushurl", str(fake))
        _git(root, "config", "--add", "remote.origin.pushurl", str(_bare))
    elif mutation == "instead_of":
        _git(root, "config", f"url.{fake.as_posix()}.insteadOf", _bare.as_posix())
    else:
        _git(
            root,
            "config",
            f"url.{fake.as_posix()}.pushInsteadOf",
            _bare.as_posix(),
        )

    with pytest.raises(ProgrammeAdmissionError, match="remote_identity"):
        pa.observe_remote_identity(root, policy)


@pytest.mark.parametrize("mutation", ["client_hook", "core_hooks_path"])
def test_git_administrative_identity_rejects_unmodelled_hook_execution(
    tmp_path: Path, mutation: str
) -> None:
    root, _bare, _policy = _remote_identity_repo(tmp_path)
    if mutation == "client_hook":
        hooks = (
            Path(
                _git(
                    root,
                    "rev-parse",
                    "--path-format=absolute",
                    "--git-common-dir",
                )
            )
            / "hooks"
        )
        hooks.mkdir(parents=True, exist_ok=True)
        (hooks / "pre-push").write_text("synthetic\n", encoding="utf-8")
    else:
        custom_hooks = tmp_path / "custom-hooks"
        custom_hooks.mkdir()
        _git(root, "config", "core.hooksPath", str(custom_hooks))

    with pytest.raises(ProgrammeAdmissionError, match="git_administrative"):
        pa.observe_git_administrative_identity(root)


def _write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes((json.dumps(value, indent=2) + "\n").encode("utf-8"))
    _stage_written_repository_path(path)


def _write_yaml(path: Path, value: dict) -> None:
    path.write_bytes(yaml.safe_dump(value, sort_keys=False).encode("utf-8"))
    _stage_written_repository_path(path)


def _stage_written_repository_path(path: Path) -> None:
    completed = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=path.parent,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        return
    root = Path(completed.stdout.strip()).resolve()
    try:
        relative = path.resolve().relative_to(root).as_posix()
    except ValueError:
        return
    _git(root, "add", "--", relative)


def _build_transition_repository(tmp_path: Path) -> tuple[Path, dict]:
    root = _policy_sandbox(tmp_path)
    synthetic_base = _git(root, "rev-parse", "HEAD")
    branch = "codex/raisa-ariadne-recovery-g0"
    _git(root, "branch", "-m", branch)
    _git(root, "config", "user.email", "tests@example.invalid")
    _git(root, "config", "user.name", "G0.5 Tests")
    _git(root, "config", "core.autocrlf", "false")
    _git(
        root,
        "branch",
        "master",
        "2e34bdad732fdab32fbf778280b3d3c70d66d602",
    )
    _git(
        root,
        "branch",
        "handoff/current",
        "2e34bdad732fdab32fbf778280b3d3c70d66d602",
    )
    _git(
        root,
        "branch",
        "safety/ariadne-clockwork-pre-g0-20260825",
        "03e6860394c39086ec1ffb3f2457acc5f7c8b5f9",
    )

    origin = tmp_path / "origin.git"
    origin.mkdir()
    _git(origin, "init", "--bare")
    _git(root, "remote", "add", "origin", str(origin))

    state_path = root / pa.STATE_PATH
    state = json.loads(state_path.read_text(encoding="utf-8"))
    state["recovery_baton"]["base_sha"] = synthetic_base
    state["g0_8_correction"]["status"] = "review_pending"
    state["g0_8_correction"]["external_review_status"] = "pending"
    state["g0_8_correction"]["next_action"] = "external_G0_review_only"
    _write_json(state_path, state)

    gates_path = root / pa.GATES_PATH
    gates = yaml.safe_load(gates_path.read_text(encoding="utf-8"))
    next(row for row in gates["gates"] if row["id"] == "G0.8")["status"] = (
        "review_pending"
    )
    _write_yaml(gates_path, gates)

    overlay_path = root / pa.OVERLAY_PATH
    overlay = yaml.safe_load(overlay_path.read_text(encoding="utf-8"))
    overlay["scope_policy"]["frozen_recovery_base"] = synthetic_base
    overlay["remote_identity_policy"] = pa.build_synthetic_remote_identity_policy(
        origin
    )
    _write_yaml(overlay_path, overlay)
    inventory_path = root / pa.INVENTORY_PATH
    inventory = yaml.safe_load(inventory_path.read_text(encoding="utf-8"))
    inventory["authoritative_refs"]["recovery_base"] = synthetic_base
    _write_yaml(inventory_path, inventory)
    from orchestration_harness.settings_fingerprint import settings_fingerprint

    latch_path = root / pa.LATCH_PATH
    latch = json.loads(latch_path.read_text(encoding="utf-8"))
    latch["checkpoint"]["settings_fingerprint"] = settings_fingerprint(
        root / "orchestration/harness_settings"
    )
    _write_json(latch_path, latch)
    _git(root, "add", "-A")
    _git(root, "commit", "-m", "G0.5 reviewed candidate")
    reviewed = _git(root, "rev-parse", "HEAD")
    reviewed_tree = _git(root, "rev-parse", f"{reviewed}^{{tree}}")

    protected = "2e34bdad732fdab32fbf778280b3d3c70d66d602"
    _git(root, "push", "origin", f"{protected}:refs/heads/master")
    _git(root, "push", "origin", f"{protected}:refs/heads/handoff/current")
    _git(root, "push", "-u", "origin", branch)
    _git(root, "fetch", "origin")

    load_programme_policy(root)
    before_state_digest = pa._sha256_bytes(
        pa._git_object_bytes(root, f"{reviewed}:{pa.STATE_PATH.as_posix()}")
    )
    before_policy_digest = pa._digest_paths_at(
        root,
        reviewed,
        (
            pa.GATES_PATH,
            pa.RISK_PATH,
            pa.INVENTORY_PATH,
            pa.G1A_SCOPE_PATH,
            pa.OVERLAY_PATH,
            pa.PROJECT_PATH,
            pa.CONTINUATION_PATH,
            pa.LATCH_PATH,
            pa.AGENTS_PATH,
        ),
    )
    transition_id = "g0-to-g1a-synthetic-pass"
    reviewer_surface = "external_native_review"
    review_path = root / pa.TRANSITION_REVIEW_ROOT / f"{transition_id}.json"
    artifact_path = root / pa.TRANSITION_ARTIFACT_ROOT / f"{transition_id}.json"
    record = {
        "schema_version": "raisa-ariadne.external-g0-review.v2",
        "review_id": transition_id,
        "recorded_at": "2026-08-25T20:00:26+10:00",
        "reviewed_commit": reviewed,
        "reviewed_tree": reviewed_tree,
        "verdict": "PASS",
        "blocking_finding_count": 0,
        "reviewer_surface": reviewer_surface,
        "g1a_authorized": True,
        "source_artifact_sha256": "1" * 64,
    }
    _write_json(review_path, record)
    review_digest = "sha256:" + hashlib.sha256(review_path.read_bytes()).hexdigest()

    agents_path = root / pa.AGENTS_PATH
    agents_text = agents_path.read_text(encoding="utf-8")
    agents_path.write_bytes(
        agents_text.replace(
            "Gate G0.8 is the only authorised correction; G1A is\nclosed.",
            "The reviewed G0 to G1A.1 transition is complete; Gate G1A.1 is active\nfor its bounded pure-verdict task only.",
            1,
        ).encode("utf-8")
    )
    _git(root, "add", "--", pa.AGENTS_PATH.as_posix())

    state = json.loads(state_path.read_text(encoding="utf-8"))
    state["observed_at"] = "2026-08-25T22:20:00+10:00"
    state["current_gate"] = "G1A.1"
    state["current_gate_status"] = "active"
    state["active_correction"] = "G1A.1"
    state["active_profile"] = pa.G1A_ACTIVE_PROFILE
    state["task_selection"]["allowed_task_kinds"] = [pa.G1A_TASK_CLASS]
    state["task_selection"]["next_eligible_tranche"] = "G1A.1"
    state["task_selection"]["next_tranche_admission_requires_state_transition"] = False
    state["task_selection"]["next_eligibility_condition"] = (
        "bounded_G1A_1_profile_active_next_tranche_not_started"
    )
    state["g0_acceptance"]["status"] = "passed"
    state["g0_acceptance"]["decisive_review_id"] = transition_id
    state["g0_acceptance"]["external_review_history"].append(
        {
            "review_id": transition_id,
            "review_record_path": review_path.relative_to(root).as_posix(),
            "reviewed_commit": reviewed,
            "reviewed_tree": reviewed_tree,
            "verdict": "PASS",
            "blocking_finding_count": 0,
            "reviewer_surface": reviewer_surface,
            "g1a_authorized": True,
            "review_record_sha256": review_digest,
        }
    )
    state["g0_acceptance"]["next_action"] = "begin_bounded_G1A_1_only"
    state["g0_8_correction"]["status"] = "external_review_passed"
    state["g0_8_correction"]["external_review_status"] = "pass"
    state["g0_8_correction"]["g1a_authorized"] = True
    state["g0_8_correction"]["next_action"] = "bounded_G1A_1_profile_active"
    state["gate_transition"] = {
        "status": "complete",
        "transition_id": transition_id,
        "from_gate": "G0",
        "to_gate": "G1A.1",
        "reviewed_commit": reviewed,
        "reviewed_tree": reviewed_tree,
        "external_review_status": "pass",
        "blocking_finding_count": 0,
        "reviewer_surface": reviewer_surface,
        "g1a_authorized": True,
        "next_action": "G1A_1_only",
    }
    _write_json(state_path, state)

    gates = yaml.safe_load(gates_path.read_text(encoding="utf-8"))
    gates["programme"]["prepared_at"] = "2026-08-25T22:20:00+10:00"
    gates["programme"]["current_gate"] = "G1A.1"
    gates["programme"]["current_gate_status"] = "active"
    gates["programme"]["next_eligible_tranche"] = "G1A.1"
    statuses = {
        "G0": "passed",
        "G0.1": "superseded_revision_required",
        "G0.4": "superseded_revision_required",
        "G0.5": "superseded_revision_required",
        "G0.6": "superseded_revision_required",
        "G0.7": "superseded_revision_required",
        "G0.8": "external_review_passed",
        "G1A": "active_subgate_G1A_1",
        "G1A.1": "active",
    }
    for row in gates["gates"]:
        if row["id"] in statuses:
            row["status"] = statuses[row["id"]]
    _write_yaml(gates_path, gates)

    review_relative = review_path.relative_to(root).as_posix()
    artifact_relative = artifact_path.relative_to(root).as_posix()
    transition_paths = sorted(
        pa.TRANSITION_FIXED_ALLOWED_PATHS | {review_relative, artifact_relative}
    )
    overlay = yaml.safe_load(overlay_path.read_text(encoding="utf-8"))
    overlay["active_profile"] = pa.G1A_ACTIVE_PROFILE
    _write_yaml(overlay_path, overlay)
    latch = json.loads(latch_path.read_text(encoding="utf-8"))
    latch["authority_source"] = (
        "Yuri's external Gate G0 PASS and typed G0 transition activate bounded G1A.1 only."
    )
    latch["checkpoint"]["settings_fingerprint"] = settings_fingerprint(
        root / "orchestration/harness_settings"
    )
    _write_json(latch_path, latch)

    manifest = {
        "schema_version": pa.TRANSITION_MANIFEST_VERSION,
        "transition_id": transition_id,
        "from_gate": "G0",
        "to_gate": "G1A.1",
        "reviewed_commit": reviewed,
        "reviewed_tree": reviewed_tree,
        "transition_parent": reviewed,
        "external_review_verdict": "PASS",
        "external_review_record_sha256": review_digest,
        "blocking_finding_count": 0,
        "reviewer_surface": reviewer_surface,
        "state_digest_before": before_state_digest,
        "policy_digest_before": before_policy_digest,
        "allowed_transition_paths": transition_paths,
        "forbidden_effect_classes": sorted(pa.TRANSITION_FORBIDDEN_EFFECTS),
    }
    after_policy = load_programme_policy(root)
    pointer_map = pa._transition_semantic_pointer_map(root, reviewed)
    manifest_digest = (
        "sha256:"
        + hashlib.sha256(
            json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
    )
    artifact = {
        "schema_version": "raisa-ariadne.g0-to-g1a-transition.v1",
        "transition_id": transition_id,
        "recorded_at": "2026-08-25T22:20:00+10:00",
        "transition_manifest": manifest,
        "transition_manifest_sha256": manifest_digest,
        "reviewed_commit": reviewed,
        "reviewed_tree": reviewed_tree,
        "external_review_record_sha256": review_digest,
        "state_digest_before": before_state_digest,
        "state_digest_after": after_policy.state_digest,
        "policy_digest_before": before_policy_digest,
        "policy_digest_after": after_policy.policy_digest,
        "changed_semantic_pointers": pointer_map,
        "scope_result": {"admitted": True, "phase": "development"},
        "target_cleanliness_contract": {
            "schema_version": "ariadne.g1a_target_cleanliness_contract.v2",
            "preserved_legacy_worktree": "C:/Users/sarashera/emr4",
            "separate_clean_target_required": True,
            "activation_untracked_count_required": 0,
            "development_allowed_untracked_paths": sorted(
                pa.G1A_ALLOWED_UNTRACKED_PATHS
            ),
            "pre_push_untracked_count_required": 0,
            "post_push_untracked_count_required": 0,
            "inventory_includes_ignored": True,
            "protected_path_aliases_forbidden": True,
            "remote_identity_sha256": overlay["remote_identity_policy"][
                "remote_identity_sha256"
            ],
        },
    }
    _write_json(artifact_path, artifact)
    _git(root, "add", "--sparse", *transition_paths)
    _git(root, "commit", "-m", "operational G0 to G1A transition")
    return root, manifest


def _copy_indexed_candidate(root: Path) -> None:
    tracked = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    ).stdout.split(b"\0")
    for encoded in tracked:
        if not encoded:
            continue
        relative = encoded.decode("utf-8")
        source = ROOT / relative
        destination = root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)


def _materialize_exact_commit_bytes(root: Path, commit: str) -> None:
    """Replace checkout-filtered bytes with the exact blobs named by a commit."""
    inventory_payload = subprocess.run(
        ["git", "ls-tree", "-r", "-z", commit],
        cwd=root,
        check=True,
        capture_output=True,
    ).stdout
    inventory: list[tuple[str, str]] = []
    for raw_entry in inventory_payload.split(b"\0"):
        if not raw_entry:
            continue
        header, raw_path = raw_entry.split(b"\t", 1)
        _mode, object_type, object_id = header.decode("ascii").split(" ")
        assert object_type == "blob"
        inventory.append((raw_path.decode("utf-8"), object_id))
    batch = subprocess.run(
        ["git", "cat-file", "--batch"],
        cwd=root,
        input="".join(f"{object_id}\n" for _, object_id in inventory).encode("ascii"),
        check=True,
        capture_output=True,
    ).stdout
    offset = 0
    for relative, object_id in inventory:
        header_end = batch.index(b"\n", offset)
        returned_id, object_type, raw_size = (
            batch[offset:header_end].decode("ascii").split(" ")
        )
        size = int(raw_size)
        payload_start = header_end + 1
        payload_end = payload_start + size
        assert returned_id == object_id
        assert object_type == "blob"
        assert batch[payload_end : payload_end + 1] == b"\n"
        (root / relative).write_bytes(batch[payload_start:payload_end])
        offset = payload_end + 1
    assert offset == len(batch)
    _git(root, "add", "--all")
    assert _git(root, "write-tree") == _git(root, "rev-parse", f"{commit}^{{tree}}")


def _build_subgate_transition_repository(
    tmp_path: Path,
) -> tuple[Path, Path, dict, str]:
    """Build a real staged G1A.1 -> G1A.2 transition over this candidate."""
    root = tmp_path / "g1a2-target"
    root.mkdir()
    _git(root, "init", "-b", "codex/raisa-ariadne-recovery-g0")
    object_store = _git(
        ROOT, "rev-parse", "--path-format=absolute", "--git-path", "objects"
    )
    alternates = root / ".git/objects/info/alternates"
    alternates.parent.mkdir(parents=True, exist_ok=True)
    alternates.write_bytes((object_store + "\n").encode("utf-8"))
    _git(root, "config", "user.email", "tests@example.invalid")
    _git(root, "config", "user.name", "G1A.2 Transition Tests")
    _git(root, "config", "core.autocrlf", "false")
    _git(root, "config", "core.longpaths", "true")
    _copy_indexed_candidate(root)

    origin = tmp_path / "g1a2-origin.git"
    origin.mkdir()
    _git(origin, "init", "--bare")
    _git(root, "remote", "add", "origin", str(origin))
    overlay_path = root / pa.OVERLAY_PATH
    overlay = yaml.safe_load(overlay_path.read_text(encoding="utf-8"))
    overlay["remote_identity_policy"] = pa.build_synthetic_remote_identity_policy(
        origin
    )
    _write_yaml(overlay_path, overlay)
    from orchestration_harness.settings_fingerprint import settings_fingerprint

    latch_path = root / pa.LATCH_PATH
    latch = json.loads(latch_path.read_text(encoding="utf-8"))
    latch["checkpoint"]["settings_fingerprint"] = settings_fingerprint(
        root / "orchestration/harness_settings"
    )
    _write_json(latch_path, latch)
    _git(root, "add", "-A")
    enablement_tree = _git(root, "write-tree")
    enablement = _git(
        root,
        "commit-tree",
        enablement_tree,
        "-p",
        "91f1e6e645424a448bdcdfa2adabb86d31fb5f0b",
        "-m",
        "synthetic G1A.2 transition enablement candidate",
    )
    _git(
        root,
        "update-ref",
        "refs/heads/codex/raisa-ariadne-recovery-g0",
        enablement,
    )
    protected = "2e34bdad732fdab32fbf778280b3d3c70d66d602"
    _git(root, "branch", "master", protected)
    _git(root, "branch", "handoff/current", protected)
    _git(
        root,
        "branch",
        "safety/ariadne-clockwork-pre-g0-20260825",
        "03e6860394c39086ec1ffb3f2457acc5f7c8b5f9",
    )
    _git(root, "push", "origin", f"{protected}:refs/heads/master")
    _git(root, "push", "origin", f"{protected}:refs/heads/handoff/current")
    _git(
        root,
        "push",
        "-u",
        "origin",
        f"{enablement}:refs/heads/codex/raisa-ariadne-recovery-g0",
    )
    _git(root, "fetch", "origin")
    load_programme_policy(root)

    gatekeeper = tmp_path / "g1a2-pinned-gatekeeper"
    _git(root, "worktree", "add", "--detach", str(gatekeeper), enablement)
    before_state_digest = pa._sha256_bytes(
        pa._git_object_bytes(root, f"{enablement}:{pa.STATE_PATH.as_posix()}")
    )
    before_policy_digest = pa._digest_paths_at(
        root,
        enablement,
        (
            pa.GATES_PATH,
            pa.RISK_PATH,
            pa.INVENTORY_PATH,
            pa.G1A_SCOPE_PATH,
            pa.OVERLAY_PATH,
            pa.PROJECT_PATH,
            pa.CONTINUATION_PATH,
            pa.LATCH_PATH,
            pa.AGENTS_PATH,
        ),
    )
    transition_id = "g1a1-to-g1a2-synthetic-pass"
    reviewer_surface = "external_native_review"
    review_path = root / pa.SUBGATE_REVIEW_ROOT / f"{transition_id}.json"
    artifact_path = root / pa.SUBGATE_TRANSITION_ARTIFACT_ROOT / f"{transition_id}.json"
    review = {
        "schema_version": "ariadne.external_subgate_review.v1",
        "review_id": transition_id,
        "recorded_at": "2026-08-28T12:00:00+10:00",
        "review_subject": "G1A.2_transition_enablement",
        "reviewed_commit": enablement,
        "reviewed_tree": enablement_tree,
        "verdict": "PASS",
        "blocking_finding_count": 0,
        "reviewer_surface": reviewer_surface,
        "g1a2_state_transition_authorized": True,
        "g1a2_implementation_authorized": False,
        "provider_invocation_authorized": False,
        "source_artifact_sha256": "1" * 64,
    }
    _write_json(review_path, review)
    review_digest = pa._sha256_bytes(review_path.read_bytes())

    state_path = root / pa.STATE_PATH
    state = json.loads(state_path.read_text(encoding="utf-8"))
    state["observed_at"] = "2026-08-28T12:05:00+10:00"
    state["current_gate"] = "G1A.2"
    state["active_correction"] = "G1A.2"
    state["active_profile"] = pa.G1A2_ACTIVE_PROFILE
    selection = state["task_selection"]
    selection["allowed_task_kinds"] = [pa.G1A2_TASK_CLASS]
    selection["next_eligible_now"] = True
    selection["next_tranche_admission_requires_state_transition"] = False
    selection["next_eligibility_condition"] = (
        "bounded_G1A_2_profile_active_next_tranche_not_started"
    )
    authority = state["g1a_subgate_authority"]
    authority["decisive_transition_enablement_review_id"] = transition_id
    authority["external_review_history"] = [
        {
            "review_id": transition_id,
            "review_record_path": review_path.relative_to(root).as_posix(),
            "reviewed_commit": enablement,
            "reviewed_tree": enablement_tree,
            "verdict": "PASS",
            "blocking_finding_count": 0,
            "reviewer_surface": reviewer_surface,
            "g1a2_state_transition_authorized": True,
            "g1a2_implementation_authorized": False,
            "provider_invocation_authorized": False,
            "review_record_sha256": review_digest,
        }
    ]
    g1a2 = authority["subgates"]["G1A.2"]
    g1a2["transition_enablement_status"] = "external_review_passed"
    g1a2["state_transition_status"] = "complete"
    g1a2["state_transition"] = {
        "status": "complete",
        "transition_id": transition_id,
        "from_gate": "G1A.1",
        "to_gate": "G1A.2",
        "owner_disposition_id": pa.OWNER_DISPOSITION_ID,
        "external_review_id": transition_id,
        "enablement_controller_commit": enablement,
        "enablement_controller_tree": enablement_tree,
        "external_review_status": "pass",
        "blocking_finding_count": 0,
        "reviewer_surface": reviewer_surface,
        "next_action": "G1A_2_adapter_only",
    }
    g1a2["implementation_authorized"] = True
    g1a2["next_action"] = "begin_bounded_G1A_2_adapter_implementation"
    _write_json(state_path, state)

    gates_path = root / pa.GATES_PATH
    gates = yaml.safe_load(gates_path.read_text(encoding="utf-8"))
    gates["programme"]["prepared_at"] = "2026-08-28T12:05:00+10:00"
    gates["programme"]["current_gate"] = "G1A.2"
    by_id = {row["id"]: row for row in gates["gates"]}
    by_id["G1A"]["status"] = "active_subgate_G1A_2"
    by_id["G1A.1"]["next_gate"] = "G1A.2"
    by_id["G1A.2"]["status"] = "active"
    _write_yaml(gates_path, gates)

    overlay = yaml.safe_load(overlay_path.read_text(encoding="utf-8"))
    overlay["active_profile"] = pa.G1A2_ACTIVE_PROFILE
    overlay["subgate_transition_policy"]["transition_status"] = "complete"
    _write_yaml(overlay_path, overlay)

    agents_path = root / pa.AGENTS_PATH
    agents = agents_path.read_text(encoding="utf-8")
    old_header = (
        "Gate G1A.1 is owner-accepted with residual risk; G1A.2\n"
        "transition enablement is review-pending and its state transition, implementation and provider invocation remain closed."
    )
    new_header = (
        "Gate G1A.2 is active only for its bounded verdict adapter; provider invocation\n"
        "remains closed. G1A.3 integration and every protected ref remain closed."
    )
    assert old_header in agents
    agents_path.write_bytes(agents.replace(old_header, new_header, 1).encode("utf-8"))
    _git(root, "add", "--", pa.AGENTS_PATH.as_posix())

    latch = json.loads(latch_path.read_text(encoding="utf-8"))
    latch["operation_id"] = "g1a2-antigravity-verdict-adapter"
    latch["active_tranche"] = "G1A.2 bounded Antigravity verdict adapter"
    latch["objective"] = (
        "Implement only the structured verdict adapter inside the three reviewed Antigravity symbols without invoking a provider."
    )
    latch["status"] = "in_progress"
    latch["source_head"] = enablement
    latch["authority_source"] = (
        "External G1A.2 transition-enablement PASS plus Yuri Frusin owner disposition"
    )
    latch["checkpoint"]["completed_stage"] = (
        "Externally accepted state-only G1A.1 to G1A.2 transition complete."
    )
    latch["checkpoint"]["next_executable_stage"] = (
        "Implement the bounded G1A.2 Antigravity verdict adapter without provider invocation."
    )
    latch["resume_after_compaction"] = True
    latch["terminal_response"] = {
        "permitted": False,
        "reason": "unfinished_authorized_operation",
    }
    latch["protected_boundaries"][3] = "G1A.2_state_transition_complete_and_frozen"
    latch["protected_boundaries"][4] = (
        "G1A.2_implementation_bounded_authorized_not_started"
    )
    latch["checkpoint"]["settings_fingerprint"] = settings_fingerprint(
        root / "orchestration/harness_settings"
    )
    _write_json(latch_path, latch)

    review_relative = review_path.relative_to(root).as_posix()
    artifact_relative = artifact_path.relative_to(root).as_posix()
    transition_paths = sorted(
        pa.SUBGATE_TRANSITION_FIXED_ALLOWED_PATHS | {review_relative, artifact_relative}
    )
    owner_digest = state["g1a_subgate_authority"]["owner_disposition_history"][0][
        "record_sha256"
    ]
    manifest = {
        "schema_version": pa.SUBGATE_TRANSITION_MANIFEST_VERSION,
        "transition_id": transition_id,
        "from_gate": "G1A.1",
        "to_gate": "G1A.2",
        "owner_disposition_id": pa.OWNER_DISPOSITION_ID,
        "owner_disposition_record_sha256": owner_digest,
        "enablement_controller_commit": enablement,
        "enablement_controller_tree": enablement_tree,
        "transition_parent": enablement,
        "external_review_verdict": "PASS",
        "external_review_record_sha256": review_digest,
        "blocking_finding_count": 0,
        "reviewer_surface": reviewer_surface,
        "state_digest_before": before_state_digest,
        "policy_digest_before": before_policy_digest,
        "allowed_transition_paths": transition_paths,
        "forbidden_effect_classes": sorted(pa.TRANSITION_FORBIDDEN_EFFECTS),
    }
    after_policy = load_programme_policy(root)
    pointer_map = pa._subgate_transition_semantic_pointer_map(root, enablement)
    manifest_digest = pa._sha256_bytes(
        json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode("utf-8")
    )
    scope = after_policy.g1a_scope["subgates"]["G1A.2"]
    contract = scope["immutable_provider_contract"]
    artifact = {
        "schema_version": "ariadne.g1a1-to-g1a2-transition.v1",
        "transition_id": transition_id,
        "recorded_at": "2026-08-28T12:05:00+10:00",
        "transition_manifest": manifest,
        "transition_manifest_sha256": manifest_digest,
        "owner_disposition_record_sha256": owner_digest,
        "external_review_record_sha256": review_digest,
        "enablement_controller_commit": enablement,
        "enablement_controller_tree": enablement_tree,
        "state_digest_before": before_state_digest,
        "state_digest_after": after_policy.state_digest,
        "policy_digest_before": before_policy_digest,
        "policy_digest_after": after_policy.policy_digest,
        "changed_semantic_pointers": pointer_map,
        "scope_result": {"admitted": True, "phase": "development"},
        "g1a2_profile_contract": {
            "active_profile": pa.G1A2_ACTIVE_PROFILE,
            "task_class": pa.G1A2_TASK_CLASS,
            "allowed_paths": sorted(pa.G1A2_ALLOWED_PATHS),
            "allowed_effects": sorted(pa.G1A2_ALLOWED_EFFECTS),
            "provider_invocation_authorized": False,
            "allowed_mutation_symbols": sorted(scope["allowed_mutation_symbols"]),
            "protected_ast_sha256": contract["protected_ast_sha256"],
        },
    }
    _write_json(artifact_path, artifact)
    _git(root, "add", "--", *transition_paths)
    return root, gatekeeper, manifest, enablement


def _build_g1a3_transition_repository(
    tmp_path: Path,
) -> tuple[Path, Path, dict, str]:
    """Build a real staged G1A.2 -> G1A.3 transition over this candidate."""
    root = tmp_path / "g1a3-target"
    root.mkdir()
    _git(root, "init", "-b", "codex/raisa-ariadne-recovery-g0")
    object_store = _git(
        ROOT, "rev-parse", "--path-format=absolute", "--git-path", "objects"
    )
    alternates = root / ".git/objects/info/alternates"
    alternates.parent.mkdir(parents=True, exist_ok=True)
    alternates.write_bytes((object_store + "\n").encode("utf-8"))
    _git(root, "config", "user.email", "tests@example.invalid")
    _git(root, "config", "user.name", "G1A.3 Transition Tests")
    _git(root, "config", "core.autocrlf", "false")
    _git(root, "config", "core.longpaths", "true")
    _copy_indexed_candidate(root)
    historical_enablement = "e5cb887090ea1cafdce30e4e1d787940f5622104"
    for relative in (pa.STATE_PATH, pa.GATES_PATH, pa.LATCH_PATH, pa.AGENTS_PATH):
        (root / relative).write_bytes(
            pa._git_object_bytes(ROOT, f"{historical_enablement}:{relative.as_posix()}")
        )
    for relative in (
        "scripts/ariadne_antigravity.py",
        "scripts/agent_worktrees.py",
    ):
        (root / relative).write_bytes(
            pa._git_object_bytes(ROOT, f"{historical_enablement}:{relative}")
        )

    origin = tmp_path / "g1a3-origin.git"
    origin.mkdir()
    _git(origin, "init", "--bare")
    _git(root, "remote", "add", "origin", str(origin))
    overlay_path = root / pa.OVERLAY_PATH
    overlay = yaml.safe_load(overlay_path.read_text(encoding="utf-8"))
    overlay["active_profile"] = pa.G1A3_ENABLEMENT_PENDING_PROFILE
    overlay["g1a3_transition_policy"]["transition_status"] = "review_pending"
    overlay["g1a3_r0_transition_policy"]["transition_status"] = "not_started"
    overlay["g1a_to_g1b1_transition_policy"]["transition_status"] = "review_pending"
    overlay["g1b1_to_g1b2_transition_policy"]["transition_status"] = "review_pending"
    overlay["remote_identity_policy"] = pa.build_synthetic_remote_identity_policy(
        origin
    )
    _write_yaml(overlay_path, overlay)
    latch_path = root / pa.LATCH_PATH
    latch = json.loads(latch_path.read_text(encoding="utf-8"))
    latch["checkpoint"]["settings_fingerprint"] = settings_fingerprint(
        root / "orchestration/harness_settings"
    )
    _write_json(latch_path, latch)
    _git(root, "add", "-A")
    enablement_tree = _git(root, "write-tree")
    implementation = "37e2d6f51ebbdb281771f922a5f460fd23e2571b"
    enablement = _git(
        root,
        "commit-tree",
        enablement_tree,
        "-p",
        implementation,
        "-m",
        "synthetic G1A.3 transition enablement candidate",
    )
    branch_ref = "refs/heads/codex/raisa-ariadne-recovery-g0"
    _git(root, "update-ref", branch_ref, enablement)
    protected = "2e34bdad732fdab32fbf778280b3d3c70d66d602"
    _git(root, "branch", "master", protected)
    _git(root, "branch", "handoff/current", protected)
    _git(
        root,
        "branch",
        "safety/ariadne-clockwork-pre-g0-20260825",
        "03e6860394c39086ec1ffb3f2457acc5f7c8b5f9",
    )
    _git(root, "push", "origin", f"{protected}:refs/heads/master")
    _git(root, "push", "origin", f"{protected}:refs/heads/handoff/current")
    _git(root, "push", "-u", "origin", f"{enablement}:{branch_ref}")
    _git(root, "fetch", "origin")
    load_programme_policy(root)

    gatekeeper = tmp_path / "g1a3-pinned-gatekeeper"
    _git(root, "worktree", "add", "--detach", str(gatekeeper), enablement)
    _materialize_exact_commit_bytes(gatekeeper, enablement)
    before_state_digest = pa._sha256_bytes(
        pa._git_object_bytes(root, f"{enablement}:{pa.STATE_PATH.as_posix()}")
    )
    before_policy_digest = pa._digest_paths_at(
        root,
        enablement,
        (
            pa.GATES_PATH,
            pa.RISK_PATH,
            pa.INVENTORY_PATH,
            pa.G1A_SCOPE_PATH,
            pa.OVERLAY_PATH,
            pa.PROJECT_PATH,
            pa.CONTINUATION_PATH,
            pa.LATCH_PATH,
            pa.AGENTS_PATH,
        ),
    )
    transition_id = "g1a2-to-g1a3-synthetic-pass"
    review_id = "g1a3-e0-synthetic-pass"
    reviewer_surface = "external_native_review"
    review_path = root / pa.G1A3_TRANSITION_REVIEW_ROOT / f"{review_id}.json"
    artifact_path = root / pa.SUBGATE_TRANSITION_ARTIFACT_ROOT / f"{transition_id}.json"
    review = {
        "schema_version": "ariadne.external_g1a3_transition_enablement_review.v1",
        "review_id": review_id,
        "recorded_at": "2026-08-28T23:00:00+10:00",
        "review_subject": "G1A.3_transition_enablement",
        "reviewed_commit": enablement,
        "reviewed_tree": enablement_tree,
        "reviewed_parent": implementation,
        "verdict": "PASS",
        "blocking_finding_count": 0,
        "reviewer_surface": reviewer_surface,
        "g1a3_state_transition_authorized": True,
        "g1a3_implementation_authorized": False,
        "provider_invocation_authorized": False,
        "integration_authorized": False,
        "source_artifact_sha256": "2" * 64,
    }
    _write_json(review_path, review)
    review_digest = pa._sha256_bytes(review_path.read_bytes())

    state_path = root / pa.STATE_PATH
    state = json.loads(state_path.read_text(encoding="utf-8"))
    state["observed_at"] = "2026-08-28T23:05:00+10:00"
    state["current_gate"] = "G1A.3"
    state["active_correction"] = "G1A.3"
    state["active_profile"] = pa.G1A3_ACTIVE_PROFILE
    selection = state["task_selection"]
    selection["allowed_task_kinds"] = [pa.G1A3_TASK_CLASS]
    selection["next_eligible_now"] = True
    selection["next_tranche_admission_requires_state_transition"] = False
    selection["next_eligibility_condition"] = (
        "bounded_G1A_3_profile_active_next_tranche_not_started"
    )
    authority = state["g1a_subgate_authority"]
    authority["decisive_g1a3_transition_enablement_review_id"] = review_id
    authority["g1a3_transition_enablement_review_history"] = [
        {
            "review_id": review_id,
            "review_record_path": review_path.relative_to(root).as_posix(),
            "reviewed_commit": enablement,
            "reviewed_tree": enablement_tree,
            "reviewed_parent": implementation,
            "verdict": "PASS",
            "blocking_finding_count": 0,
            "reviewer_surface": reviewer_surface,
            "g1a3_state_transition_authorized": True,
            "g1a3_implementation_authorized": False,
            "provider_invocation_authorized": False,
            "integration_authorized": False,
            "review_record_sha256": review_digest,
        }
    ]
    g1a3 = authority["subgates"]["G1A.3"]
    g1a3["status"] = "active"
    g1a3["transition_enablement_status"] = "external_review_passed"
    g1a3["state_transition_status"] = "complete"
    g1a3["state_transition"] = {
        "status": "complete",
        "transition_id": transition_id,
        "from_gate": "G1A.2",
        "to_gate": "G1A.3",
        "g1a2_implementation_review_id": authority["decisive_implementation_review_id"],
        "external_review_id": review_id,
        "enablement_controller_commit": enablement,
        "enablement_controller_tree": enablement_tree,
        "external_review_status": "pass",
        "blocking_finding_count": 0,
        "reviewer_surface": reviewer_surface,
        "next_action": "G1A_3_integration_consumer_only",
    }
    g1a3["implementation_authorized"] = True
    g1a3["next_action"] = "begin_bounded_G1A3_integration_consumer_implementation"
    _write_json(state_path, state)

    gates_path = root / pa.GATES_PATH
    gates = yaml.safe_load(gates_path.read_text(encoding="utf-8"))
    gates["programme"]["prepared_at"] = "2026-08-28T23:05:00+10:00"
    gates["programme"]["current_gate"] = "G1A.3"
    by_id = {row["id"]: row for row in gates["gates"]}
    by_id["G1A"]["status"] = "active_subgate_G1A_3"
    by_id["G1A.3"]["status"] = "active"
    _write_yaml(gates_path, gates)

    overlay = yaml.safe_load(overlay_path.read_text(encoding="utf-8"))
    overlay["active_profile"] = pa.G1A3_ACTIVE_PROFILE
    overlay["g1a3_transition_policy"]["transition_status"] = "complete"
    _write_yaml(overlay_path, overlay)

    agents_path = root / pa.AGENTS_PATH
    agents = agents_path.read_text(encoding="utf-8")
    old_header = (
        "Gate G1A.2 implementation is externally accepted. G1A.3 transition enablement\n"
        "is review-pending as a runtime-faithful source-byte/body-only-AST replacement; its state transition,\n"
        "implementation, integration entrypoint, provider invocation and every protected ref\n"
        "remain closed."
    )
    new_header = (
        "Gate G1A.3 is active only for its bounded integration-authority consumer;\n"
        "integration execution, provider invocation and every protected ref remain closed."
    )
    assert old_header in agents
    agents_path.write_bytes(agents.replace(old_header, new_header, 1).encode("utf-8"))
    _git(root, "add", "--", pa.AGENTS_PATH.as_posix())

    latch = json.loads(latch_path.read_text(encoding="utf-8"))
    latch["operation_id"] = "g1a3-integration-consumer-mutation"
    latch["active_tranche"] = "G1A.3 bounded integration-authority consumer"
    latch["objective"] = (
        "Implement only record_integration as the canonical immutable worker-receipt authority consumer without executing integration."
    )
    latch["status"] = "in_progress"
    latch["source_head"] = enablement
    latch["authority_source"] = (
        "External G1A.3 transition-enablement PASS plus exact G1A.2 implementation PASS"
    )
    latch["checkpoint"]["completed_stage"] = (
        "Externally accepted state-only G1A.2 to G1A.3 transition complete."
    )
    latch["checkpoint"]["next_executable_stage"] = (
        "Implement the bounded G1A.3 integration-authority consumer without executing integration."
    )
    latch["resume_after_compaction"] = True
    latch["terminal_response"] = {
        "permitted": False,
        "reason": "unfinished_authorized_operation",
    }
    latch["protected_boundaries"][7] = (
        "G1A.3_state_transition_complete_implementation_bounded_not_started"
    )
    latch["checkpoint"]["settings_fingerprint"] = settings_fingerprint(
        root / "orchestration/harness_settings"
    )
    _write_json(latch_path, latch)

    review_relative = review_path.relative_to(root).as_posix()
    artifact_relative = artifact_path.relative_to(root).as_posix()
    transition_paths = sorted(
        pa.G1A3_TRANSITION_FIXED_ALLOWED_PATHS | {review_relative, artifact_relative}
    )
    implementation_entry = authority["implementation_review_history"][0]
    manifest = {
        "schema_version": pa.G1A3_TRANSITION_MANIFEST_VERSION,
        "transition_id": transition_id,
        "from_gate": "G1A.2",
        "to_gate": "G1A.3",
        "g1a2_implementation_review_id": implementation_entry["review_id"],
        "g1a2_implementation_review_record_sha256": implementation_entry[
            "review_record_sha256"
        ],
        "g1a2_implementation_commit": implementation_entry["reviewed_commit"],
        "g1a2_implementation_tree": implementation_entry["reviewed_tree"],
        "enablement_review_id": review_id,
        "enablement_controller_commit": enablement,
        "enablement_controller_tree": enablement_tree,
        "transition_parent": enablement,
        "external_review_verdict": "PASS",
        "external_review_record_sha256": review_digest,
        "blocking_finding_count": 0,
        "reviewer_surface": reviewer_surface,
        "state_digest_before": before_state_digest,
        "policy_digest_before": before_policy_digest,
        "allowed_transition_paths": transition_paths,
        "forbidden_effect_classes": sorted(pa.TRANSITION_FORBIDDEN_EFFECTS),
    }
    after_policy = load_programme_policy(root)
    pointer_map = pa._g1a3_transition_semantic_pointer_map(root, enablement)
    manifest_digest = pa._sha256_bytes(
        json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode("utf-8")
    )
    scope = after_policy.g1a_scope["subgates"]["G1A.3"]
    contract = scope["immutable_integration_consumer_contract"]
    artifact = {
        "schema_version": "ariadne.g1a2-to-g1a3-transition.v1",
        "transition_id": transition_id,
        "recorded_at": "2026-08-28T23:05:00+10:00",
        "transition_manifest": manifest,
        "transition_manifest_sha256": manifest_digest,
        "g1a2_implementation_review_record_sha256": implementation_entry[
            "review_record_sha256"
        ],
        "external_review_record_sha256": review_digest,
        "enablement_controller_commit": enablement,
        "enablement_controller_tree": enablement_tree,
        "state_digest_before": before_state_digest,
        "state_digest_after": after_policy.state_digest,
        "policy_digest_before": before_policy_digest,
        "policy_digest_after": after_policy.policy_digest,
        "changed_semantic_pointers": pointer_map,
        "scope_result": {"admitted": True, "phase": "development"},
        "g1a3_profile_contract": {
            "active_profile": pa.G1A3_ACTIVE_PROFILE,
            "task_class": pa.G1A3_TASK_CLASS,
            "allowed_paths": sorted(pa.G1A3_ALLOWED_PATHS),
            "allowed_effects": sorted(pa.G1A3_ALLOWED_EFFECTS),
            "integration_entrypoint_closed": True,
            "provider_invocation_authorized": False,
            "allowed_mutation_symbols": ["record_integration"],
            "hash_semantics": contract["hash_semantics"],
            "runtime_source_parsing_contract": contract[
                "runtime_source_parsing_contract"
            ],
            "protected_ast_sha256": contract["protected_ast_sha256"],
            "source_blob": contract["source_blob"],
        },
    }
    _write_json(artifact_path, artifact)
    _git(root, "add", "--", *transition_paths)
    return root, gatekeeper, manifest, enablement


def _build_g1a3_r0_transition_repository(
    tmp_path: Path,
) -> tuple[Path, Path, dict, str]:
    """Build one real staged external-PASS R0 -> R1 transition."""
    root = tmp_path / "g1a3-r1-target"
    root.mkdir()
    _git(root, "init", "-b", "codex/raisa-ariadne-recovery-g0")
    object_store = _git(
        ROOT, "rev-parse", "--path-format=absolute", "--git-path", "objects"
    )
    alternates = root / ".git/objects/info/alternates"
    alternates.parent.mkdir(parents=True, exist_ok=True)
    alternates.write_bytes((object_store + "\n").encode("utf-8"))
    _git(root, "config", "user.email", "tests@example.invalid")
    _git(root, "config", "user.name", "G1A.3-R0 Transition Tests")
    _git(root, "config", "core.autocrlf", "false")
    _git(root, "config", "core.longpaths", "true")
    _copy_indexed_candidate(root)
    historical_r0 = "ccbe0d6a36218903fc6582a0b348bd0b0199794b"
    for relative in (pa.STATE_PATH, pa.GATES_PATH, pa.LATCH_PATH, pa.AGENTS_PATH):
        (root / relative).write_bytes(
            pa._git_object_bytes(ROOT, f"{historical_r0}:{relative.as_posix()}")
        )
    for relative in (
        "scripts/ariadne_antigravity.py",
        "scripts/agent_worktrees.py",
    ):
        (root / relative).write_bytes(
            pa._git_object_bytes(ROOT, f"{historical_r0}:{relative}")
        )

    origin = tmp_path / "g1a3-r1-origin.git"
    origin.mkdir()
    _git(origin, "init", "--bare")
    _git(root, "remote", "add", "origin", str(origin))
    overlay_path = root / pa.OVERLAY_PATH
    overlay = yaml.safe_load(overlay_path.read_text(encoding="utf-8"))
    overlay["active_profile"] = pa.G1A3_R0_REVIEW_PENDING_PROFILE
    overlay["g1a3_r0_transition_policy"]["transition_status"] = "not_started"
    overlay["g1a_to_g1b1_transition_policy"]["transition_status"] = "review_pending"
    overlay["g1b1_to_g1b2_transition_policy"]["transition_status"] = "review_pending"
    overlay["remote_identity_policy"] = pa.build_synthetic_remote_identity_policy(
        origin
    )
    _write_yaml(overlay_path, overlay)
    latch_path = root / pa.LATCH_PATH
    latch = json.loads(latch_path.read_text(encoding="utf-8"))
    latch["checkpoint"]["settings_fingerprint"] = settings_fingerprint(
        root / "orchestration/harness_settings"
    )
    _write_json(latch_path, latch)
    _git(root, "add", "-A")
    r0_tree = _git(root, "write-tree")
    r0_parent = "5a298856be05ce08e50dd7ab4501b7e16a3d0843"
    r0_candidate = _git(
        root,
        "commit-tree",
        r0_tree,
        "-p",
        r0_parent,
        "-m",
        "synthetic G1A.3-R0 candidate",
    )
    branch_ref = "refs/heads/codex/raisa-ariadne-recovery-g0"
    _git(root, "update-ref", branch_ref, r0_candidate)
    protected = "2e34bdad732fdab32fbf778280b3d3c70d66d602"
    _git(root, "branch", "master", protected)
    _git(root, "branch", "handoff/current", protected)
    _git(root, "push", "origin", f"{protected}:refs/heads/master")
    _git(root, "push", "origin", f"{protected}:refs/heads/handoff/current")
    _git(root, "push", "-u", "origin", f"{r0_candidate}:{branch_ref}")
    _git(root, "fetch", "origin")
    load_programme_policy(root)

    gatekeeper = tmp_path / "g1a3-r0-pinned-gatekeeper"
    gatekeeper.mkdir()
    _git(gatekeeper, "init")
    gatekeeper_alternates = gatekeeper / ".git/objects/info/alternates"
    gatekeeper_alternates.parent.mkdir(parents=True, exist_ok=True)
    target_object_store = _git(
        root, "rev-parse", "--path-format=absolute", "--git-path", "objects"
    )
    gatekeeper_alternates.write_bytes((target_object_store + "\n").encode("utf-8"))
    _git(gatekeeper, "config", "core.autocrlf", "false")
    _git(gatekeeper, "config", "core.longpaths", "true")
    _git(
        gatekeeper,
        "-c",
        "core.autocrlf=false",
        "checkout",
        "--detach",
        r0_candidate,
    )
    raw_inventory = subprocess.run(
        ["git", "ls-tree", "-r", "-z", r0_candidate],
        cwd=gatekeeper,
        check=True,
        capture_output=True,
    ).stdout
    inventory: list[tuple[str, str]] = []
    for raw_entry in raw_inventory.split(b"\0"):
        if not raw_entry:
            continue
        header, raw_path = raw_entry.split(b"\t", 1)
        _mode, object_type, object_id = header.decode("ascii").split(" ")
        assert object_type == "blob"
        inventory.append((raw_path.decode("utf-8"), object_id))
    batch = subprocess.run(
        ["git", "cat-file", "--batch"],
        cwd=gatekeeper,
        input="".join(f"{object_id}\n" for _, object_id in inventory).encode("ascii"),
        check=True,
        capture_output=True,
    ).stdout
    offset = 0
    for relative, object_id in inventory:
        header_end = batch.index(b"\n", offset)
        returned_id, object_type, raw_size = (
            batch[offset:header_end].decode("ascii").split(" ")
        )
        size = int(raw_size)
        payload_start = header_end + 1
        payload_end = payload_start + size
        assert returned_id == object_id
        assert object_type == "blob"
        assert batch[payload_end : payload_end + 1] == b"\n"
        (gatekeeper / relative).write_bytes(batch[payload_start:payload_end])
        offset = payload_end + 1
    assert offset == len(batch)
    attributes_path = Path(
        _git(
            gatekeeper,
            "rev-parse",
            "--path-format=absolute",
            "--git-path",
            "info/attributes",
        )
    )
    attributes_path.parent.mkdir(parents=True, exist_ok=True)
    attributes_path.write_text("* -text\n", encoding="utf-8")
    _git(gatekeeper, "add", "--all")
    assert _git(gatekeeper, "write-tree") == r0_tree
    assert _git(gatekeeper, "status", "--porcelain", "--untracked-files=no") == ""
    before_state_digest = pa._sha256_bytes(
        pa._git_object_bytes(root, f"{r0_candidate}:{pa.STATE_PATH.as_posix()}")
    )
    policy_paths = (
        pa.GATES_PATH,
        pa.RISK_PATH,
        pa.INVENTORY_PATH,
        pa.G1A_SCOPE_PATH,
        pa.OVERLAY_PATH,
        pa.PROJECT_PATH,
        pa.CONTINUATION_PATH,
        pa.LATCH_PATH,
        pa.AGENTS_PATH,
    )
    before_policy_digest = pa._digest_paths_at(root, r0_candidate, policy_paths)
    transition_id = "g1a3-r0-to-r1-synthetic-pass"
    review_id = "g1a3-r0-review-synthetic-pass"
    reviewer_surface = "external_native_review"
    review_path = root / pa.SUBGATE_IMPLEMENTATION_REVIEW_ROOT / f"{review_id}.json"
    artifact_path = root / pa.SUBGATE_TRANSITION_ARTIFACT_ROOT / f"{transition_id}.json"
    review = {
        "schema_version": "ariadne.external_g1a3_r0_review.v1",
        "review_id": review_id,
        "recorded_at": "2026-08-30T01:00:00+10:00",
        "review_subject": "G1A.3-R0_complete_review_byte_binding_control_plane",
        "reviewed_commit": r0_candidate,
        "reviewed_tree": r0_tree,
        "reviewed_parent": r0_parent,
        "verdict": "PASS",
        "blocking_finding_count": 0,
        "reviewer_surface": reviewer_surface,
        "g1a3_r1_state_transition_authorized": True,
        "g1a3_r1_implementation_authorized": False,
        "provider_invocation_authorized": False,
        "integration_authorized": False,
        "protected_ref_movement_authorized": False,
        "source_artifact_sha256": "3" * 64,
    }
    _write_json(review_path, review)
    review_digest = pa._sha256_bytes(review_path.read_bytes())

    state_path = root / pa.STATE_PATH
    state = json.loads(state_path.read_text(encoding="utf-8"))
    state["observed_at"] = "2026-08-30T01:05:00+10:00"
    state["current_gate_status"] = "active"
    state["active_correction"] = pa.G1A3_R1_CORRECTION
    state["active_profile"] = pa.G1A3_R1_ACTIVE_PROFILE
    selection = state["task_selection"]
    selection["allowed_task_kinds"] = [pa.G1A3_R1_TASK_CLASS]
    selection["next_eligible_now"] = True
    selection["next_tranche_admission_requires_state_transition"] = False
    selection["next_eligibility_condition"] = (
        "bounded_G1A_3_R1_profile_active_next_tranche_not_started"
    )
    authority = state["g1a_subgate_authority"]
    authority["decisive_g1a3_r0_review_id"] = review_id
    authority["g1a3_r0_review_history"] = [
        {
            "review_id": review_id,
            "review_record_path": review_path.relative_to(root).as_posix(),
            "reviewed_commit": r0_candidate,
            "reviewed_tree": r0_tree,
            "reviewed_parent": r0_parent,
            "verdict": "PASS",
            "blocking_finding_count": 0,
            "reviewer_surface": reviewer_surface,
            "g1a3_r1_state_transition_authorized": True,
            "g1a3_r1_implementation_authorized": False,
            "provider_invocation_authorized": False,
            "integration_authorized": False,
            "protected_ref_movement_authorized": False,
            "review_record_sha256": review_digest,
        }
    ]
    g1a3 = authority["subgates"]["G1A.3"]
    g1a3["status"] = "active_review_binding"
    g1a3["r0_status"] = "external_review_passed"
    g1a3["r1_state_transition_status"] = "complete"
    g1a3["r1_state_transition"] = {
        "status": "complete",
        "transition_id": transition_id,
        "from_profile": pa.G1A3_R0_REVIEW_PENDING_PROFILE,
        "to_profile": pa.G1A3_R1_ACTIVE_PROFILE,
        "r0_external_review_id": review_id,
        "r0_controller_commit": r0_candidate,
        "r0_controller_tree": r0_tree,
        "external_review_status": "pass",
        "blocking_finding_count": 0,
        "reviewer_surface": reviewer_surface,
        "next_action": "G1A_3_R1_review_binding_only",
    }
    g1a3["implementation_authorized"] = True
    g1a3["next_action"] = "begin_bounded_G1A3_R1_review_binding_implementation"
    _write_json(state_path, state)

    gates_path = root / pa.GATES_PATH
    gates = yaml.safe_load(gates_path.read_text(encoding="utf-8"))
    gates["programme"]["prepared_at"] = "2026-08-30T01:05:00+10:00"
    gates["programme"]["current_gate_status"] = "active"
    by_id = {row["id"]: row for row in gates["gates"]}
    by_id["G1A"]["status"] = "active_subgate_G1A_3_R1"
    by_id["G1A.3"]["status"] = "active_review_binding"
    _write_yaml(gates_path, gates)

    overlay = yaml.safe_load(overlay_path.read_text(encoding="utf-8"))
    overlay["active_profile"] = pa.G1A3_R1_ACTIVE_PROFILE
    overlay["g1a3_r0_transition_policy"]["transition_status"] = "complete"
    _write_yaml(overlay_path, overlay)

    agents_path = root / pa.AGENTS_PATH
    agents = agents_path.read_text(encoding="utf-8")
    agents = agents.replace(
        "Gate G1A.3-R0 is review-pending with no eligible implementation task;\n"
        "integration execution, provider invocation, G1B and every protected ref remain closed.",
        "Gate G1A.3-R1 is active only for complete review-byte binding;\n"
        "integration execution, provider invocation, G1B and every protected ref remain closed.",
        1,
    )
    agents_path.write_bytes(agents.encode("utf-8"))
    _git(root, "add", "--", pa.AGENTS_PATH.as_posix())

    latch = json.loads(latch_path.read_text(encoding="utf-8"))
    latch["operation_id"] = "g1a3-r1-review-byte-binding"
    latch["active_tranche"] = "G1A.3-R1 complete review-byte binding"
    latch["objective"] = "Implement only the exact four-path reviewed binding seam."
    latch["status"] = "in_progress"
    latch["source_head"] = r0_candidate
    latch["authority_source"] = "External G1A.3-R0 PASS"
    latch["checkpoint"]["completed_stage"] = "External R0 PASS bound."
    latch["checkpoint"]["next_executable_stage"] = (
        "Implement exact R1 binding without provider or integration execution."
    )
    latch["resume_after_compaction"] = True
    latch["terminal_response"] = {
        "permitted": False,
        "reason": "unfinished_authorized_operation",
    }
    latch["checkpoint"]["settings_fingerprint"] = settings_fingerprint(
        root / "orchestration/harness_settings"
    )
    _write_json(latch_path, latch)

    review_relative = review_path.relative_to(root).as_posix()
    artifact_relative = artifact_path.relative_to(root).as_posix()
    transition_paths = sorted(
        pa.G1A3_R0_TRANSITION_FIXED_ALLOWED_PATHS | {review_relative, artifact_relative}
    )
    manifest = {
        "schema_version": pa.G1A3_R0_TRANSITION_MANIFEST_VERSION,
        "transition_id": transition_id,
        "from_profile": pa.G1A3_R0_REVIEW_PENDING_PROFILE,
        "to_profile": pa.G1A3_R1_ACTIVE_PROFILE,
        "r0_candidate_commit": r0_candidate,
        "r0_candidate_tree": r0_tree,
        "r0_external_review_id": review_id,
        "r0_external_review_record_sha256": review_digest,
        "rejected_g1a3_review_id": pa.G1A3_R0_REVIEW_ID,
        "rejected_g1a3_review_record_sha256": pa.G1A3_R0_REVIEW_SHA256,
        "transition_parent": r0_candidate,
        "external_review_verdict": "PASS",
        "blocking_finding_count": 0,
        "reviewer_surface": reviewer_surface,
        "state_digest_before": before_state_digest,
        "policy_digest_before": before_policy_digest,
        "allowed_transition_paths": transition_paths,
        "forbidden_effect_classes": sorted(pa.TRANSITION_FORBIDDEN_EFFECTS),
    }
    after_policy = load_programme_policy(root)
    artifact = {
        "schema_version": "ariadne.g1a3-r0-to-r1-transition.v1",
        "transition_id": transition_id,
        "recorded_at": "2026-08-30T01:05:00+10:00",
        "transition_manifest": manifest,
        "transition_manifest_sha256": pa._sha256_bytes(
            json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode()
        ),
        "r0_external_review_record_sha256": review_digest,
        "rejected_g1a3_review_record_sha256": pa.G1A3_R0_REVIEW_SHA256,
        "r0_controller_commit": r0_candidate,
        "r0_controller_tree": r0_tree,
        "state_digest_before": before_state_digest,
        "state_digest_after": after_policy.state_digest,
        "policy_digest_before": before_policy_digest,
        "policy_digest_after": after_policy.policy_digest,
        "scope_result": {"admitted": True, "phase": "development"},
        "r1_profile_contract": {
            "active_profile": pa.G1A3_R1_ACTIVE_PROFILE,
            "task_class": pa.G1A3_R1_TASK_CLASS,
            "allowed_paths": sorted(pa.G1A3_R1_ALLOWED_PATHS),
            "allowed_effects": sorted(pa.G1A3_R1_ALLOWED_EFFECTS),
            "provider_invocation_authorized": False,
            "integration_execution_authorized": False,
            "antigravity_allowed_mutation": "run_worker_body_only",
            "antigravity_runtime_source_parsing_contract": pa.G1A3_RUNTIME_SOURCE_PARSING_CONTRACT,
            "run_worker_first_admission_contract": pa.G1A3_RUN_WORKER_FIRST_ADMISSION_CONTRACT,
            "integration_allowed_mutation": "record_integration_body_only",
            "record_integration_first_admission_contract": pa.G1A3_RECORD_INTEGRATION_FIRST_ADMISSION_CONTRACT,
        },
    }
    _write_json(artifact_path, artifact)
    _git(root, "add", "--", *transition_paths)
    return root, gatekeeper, manifest, r0_candidate


def _build_g1a_to_g1b1_transition_repository(
    tmp_path: Path,
) -> tuple[Path, Path, dict, str, str]:
    """Build the separately reviewed seven-path transition in a bare-origin fixture."""
    root = tmp_path / "g1b1-transition-target"
    root.mkdir()
    _git(root, "init", "-b", "codex/raisa-ariadne-recovery-g0")
    object_store = _git(
        ROOT, "rev-parse", "--path-format=absolute", "--git-path", "objects"
    )
    alternates = root / ".git/objects/info/alternates"
    alternates.parent.mkdir(parents=True, exist_ok=True)
    alternates.write_bytes((object_store + "\n").encode("utf-8"))
    _git(root, "config", "user.email", "tests@example.invalid")
    _git(root, "config", "user.name", "G1B.1 Transition Tests")
    _git(root, "config", "core.autocrlf", "false")
    _git(root, "config", "core.longpaths", "true")
    _copy_indexed_candidate(root)
    historical_closeout = "00534520ed387c5766281de932e91ad74f7071f1"
    for relative in (pa.STATE_PATH, pa.GATES_PATH, pa.LATCH_PATH, pa.AGENTS_PATH):
        (root / relative).write_bytes(
            pa._git_object_bytes(ROOT, f"{historical_closeout}:{relative.as_posix()}")
        )
    for relative in pa.G1B1_ALLOWED_PATHS:
        (root / relative).unlink()

    origin = tmp_path / "g1b1-origin.git"
    origin.mkdir()
    _git(origin, "init", "--bare")
    _git(root, "remote", "add", "origin", str(origin))
    overlay_path = root / pa.OVERLAY_PATH
    overlay = yaml.safe_load(overlay_path.read_text(encoding="utf-8"))
    overlay["active_profile"] = pa.G1A_CLOSEOUT_REVIEW_PENDING_PROFILE
    overlay["g1a_to_g1b1_transition_policy"]["transition_status"] = "review_pending"
    overlay["g1b1_to_g1b2_transition_policy"]["transition_status"] = "review_pending"
    overlay["remote_identity_policy"] = pa.build_synthetic_remote_identity_policy(
        origin
    )
    _write_yaml(overlay_path, overlay)
    latch_path = root / pa.LATCH_PATH
    latch = json.loads(latch_path.read_text(encoding="utf-8"))
    latch["checkpoint"]["settings_fingerprint"] = settings_fingerprint(
        root / "orchestration/harness_settings"
    )
    _write_json(latch_path, latch)
    _git(root, "add", "-A")
    enablement_tree = _git(root, "write-tree")
    enablement = _git(
        root,
        "commit-tree",
        enablement_tree,
        "-p",
        "23aa3ab19aec6cee9246e7dd3a88f61ada39bd7a",
        "-m",
        "synthetic externally reviewable G1A closeout controller",
    )
    branch_ref = "refs/heads/codex/raisa-ariadne-recovery-g0"
    _git(root, "update-ref", branch_ref, enablement)
    protected = "2e34bdad732fdab32fbf778280b3d3c70d66d602"
    _git(root, "branch", "master", protected)
    _git(root, "branch", "handoff/current", protected)
    _git(
        root,
        "branch",
        "safety/ariadne-clockwork-pre-g0-20260825",
        "03e6860394c39086ec1ffb3f2457acc5f7c8b5f9",
    )
    _git(root, "push", "origin", f"{protected}:refs/heads/master")
    _git(root, "push", "origin", f"{protected}:refs/heads/handoff/current")
    _git(root, "push", "-u", "origin", f"{enablement}:{branch_ref}")
    _git(root, "fetch", "origin")
    before_policy = load_programme_policy(root)

    gatekeeper = tmp_path / "g1b1-pinned-gatekeeper"
    _git(root, "worktree", "add", "--detach", str(gatekeeper), enablement)
    _materialize_exact_commit_bytes(gatekeeper, enablement)

    transition_id = "g1a-to-g1b1-synthetic-pass"
    review_id = "g1a-closeout-g1b-enablement-synthetic-pass"
    reviewer_surface = "external_native_review"
    review_path = root / pa.G1A_CLOSEOUT_REVIEW_ROOT / f"{review_id}.json"
    artifact_path = (
        root / pa.G1A_TO_G1B1_TRANSITION_ARTIFACT_ROOT / f"{transition_id}.json"
    )
    review = {
        "schema_version": "ariadne.external_g1a_closeout_g1b_enablement_review.v1",
        "review_id": review_id,
        "recorded_at": "2026-09-01T00:05:00+10:00",
        "review_subject": "G1A_closeout_and_G1B_transition_enablement_controller",
        "reviewed_commit": enablement,
        "reviewed_tree": enablement_tree,
        "reviewed_parent": "23aa3ab19aec6cee9246e7dd3a88f61ada39bd7a",
        "verdict": "PASS",
        "blocking_finding_count": 0,
        "reviewer_surface": reviewer_surface,
        "g1a_closeout_authorized": True,
        "g1b_state_transition_authorized": True,
        "g1b_implementation_authorized": False,
        "provider_invocation_authorized": False,
        "integration_execution_authorized": False,
        "protected_ref_movement_authorized": False,
        "source_artifact_sha256": "3" * 64,
    }
    _write_json(review_path, review)
    review_digest = pa._sha256_bytes(review_path.read_bytes())

    state_path = root / pa.STATE_PATH
    state = json.loads(state_path.read_text(encoding="utf-8"))
    state["observed_at"] = "2026-09-01T00:10:00+10:00"
    state["current_gate"] = "G1B.1"
    state["active_correction"] = "G1B.1"
    state["active_profile"] = pa.G1B1_ACTIVE_PROFILE
    state["g1a_closeout"].update(
        {
            "status": "accepted",
            "external_review_status": "pass",
            "g1a_closed": True,
            "next_action": "begin_bounded_G1B1_pure_state_event_kernel",
        }
    )
    state["g1b"].update(
        {
            "status": "active_G1B1",
            "transition_enablement_status": "external_review_passed",
            "state_transition_status": "complete",
            "state_transition": {
                "status": "complete",
                "transition_id": transition_id,
                "from_profile": pa.G1A_CLOSEOUT_REVIEW_PENDING_PROFILE,
                "to_profile": pa.G1B1_ACTIVE_PROFILE,
                "enablement_review_id": review_id,
                "enablement_candidate_commit": enablement,
                "enablement_candidate_tree": enablement_tree,
                "external_review_status": "pass",
                "blocking_finding_count": 0,
                "reviewer_surface": reviewer_surface,
                "next_action": "begin_bounded_G1B1_pure_state_event_kernel",
            },
        }
    )
    state["task_selection"].update(
        {
            "allowed_task_kinds": [pa.G1B1_TASK_CLASS],
            "next_eligible_now": True,
            "next_tranche_admission_requires_state_transition": False,
            "next_eligibility_condition": "bounded_G1B1_profile_active_next_tranche_not_started",
        }
    )
    _write_json(state_path, state)

    gates_path = root / pa.GATES_PATH
    gates = yaml.safe_load(gates_path.read_text(encoding="utf-8"))
    gates["programme"]["prepared_at"] = "2026-09-01T00:10:00+10:00"
    gates["programme"]["current_gate"] = "G1B.1"
    by_id = {row["id"]: row for row in gates["gates"]}
    by_id["G1A"]["status"] = "passed"
    by_id["G1B"]["status"] = "active_subgate_G1B_1"
    by_id["G1B.1"]["status"] = "active"
    _write_yaml(gates_path, gates)

    overlay = yaml.safe_load(overlay_path.read_text(encoding="utf-8"))
    overlay["active_profile"] = pa.G1B1_ACTIVE_PROFILE
    overlay["g1a_to_g1b1_transition_policy"]["transition_status"] = "complete"
    _write_yaml(overlay_path, overlay)

    agents_path = root / pa.AGENTS_PATH
    agents = agents_path.read_text(encoding="utf-8")
    old_header = "Gate G1A.3 implementation is externally accepted. G1A closeout and G1B transition enablement are review-pending; G1B remains closed."
    new_header = "Gate G1B.1 is active only for the bounded pure state/event kernel; G1A is closed and all runtime entrypoints remain closed."
    assert old_header in agents
    agents_path.write_bytes(agents.replace(old_header, new_header, 1).encode("utf-8"))

    latch = json.loads(latch_path.read_text(encoding="utf-8"))
    latch["operation_id"] = "g1b1-pure-state-event-kernel"
    latch["active_tranche"] = "G1B.1 bounded pure state/event kernel"
    latch["objective"] = (
        "Implement only the pure deterministic G1B.1 state/event kernel."
    )
    latch["status"] = "in_progress"
    latch["source_head"] = enablement
    latch["authority_source"] = (
        "External G1A closeout and G1B transition-enablement PASS"
    )
    latch["checkpoint"]["completed_stage"] = (
        "Externally accepted state-only G1A to G1B.1 transition complete."
    )
    latch["checkpoint"]["next_executable_stage"] = (
        "Implement the bounded G1B.1 pure state/event kernel only."
    )
    latch["resume_after_compaction"] = True
    latch["terminal_response"] = {
        "permitted": False,
        "reason": "unfinished_authorized_operation",
    }
    latch["protected_boundaries"][10] = "G1B1_state_transition_complete"
    latch["protected_boundaries"][11] = "G1B1_pure_kernel_only"
    latch["protected_boundaries"][12] = "all_runtime_entrypoints_closed"
    latch["checkpoint"]["settings_fingerprint"] = settings_fingerprint(
        root / "orchestration/harness_settings"
    )
    _write_json(latch_path, latch)

    accepted_payload = (root / pa.G1A_ACCEPTED_SURFACE_PATH).read_bytes()
    clockwork_payload = (root / pa.G1B_CLOCKWORK_SCOPE_PATH).read_bytes()
    review_relative = review_path.relative_to(root).as_posix()
    artifact_relative = artifact_path.relative_to(root).as_posix()
    transition_paths = sorted(
        pa.G1A_TO_G1B1_TRANSITION_FIXED_ALLOWED_PATHS
        | {review_relative, artifact_relative}
    )
    manifest = {
        "schema_version": pa.G1A_TO_G1B1_TRANSITION_MANIFEST_VERSION,
        "transition_id": transition_id,
        "from_profile": pa.G1A_CLOSEOUT_REVIEW_PENDING_PROFILE,
        "to_profile": pa.G1B1_ACTIVE_PROFILE,
        "g1a3_r1_review_id": pa.G1A3_R1_REVIEW_ID,
        "g1a3_r1_review_record_sha256": pa.G1A3_R1_REVIEW_SHA256,
        "enablement_review_id": review_id,
        "enablement_candidate_commit": enablement,
        "enablement_candidate_tree": enablement_tree,
        "enablement_candidate_parent": "23aa3ab19aec6cee9246e7dd3a88f61ada39bd7a",
        "transition_parent": enablement,
        "external_review_verdict": "PASS",
        "external_review_record_sha256": review_digest,
        "blocking_finding_count": 0,
        "reviewer_surface": reviewer_surface,
        "state_digest_before": before_policy.state_digest,
        "policy_digest_before": before_policy.policy_digest,
        "accepted_surface_sha256": pa._sha256_bytes(accepted_payload),
        "accepted_surface_git_blob": _git(
            root, "rev-parse", f"{enablement}:{pa.G1A_ACCEPTED_SURFACE_PATH.as_posix()}"
        ),
        "clockwork_scope_sha256": pa._sha256_bytes(clockwork_payload),
        "clockwork_scope_git_blob": _git(
            root, "rev-parse", f"{enablement}:{pa.G1B_CLOCKWORK_SCOPE_PATH.as_posix()}"
        ),
        "allowed_transition_paths": transition_paths,
        "required_semantic_pointer_delta": pa.G1A_TO_G1B1_TRANSITION_SEMANTIC_POINTERS,
        "protected_refs_before": {
            "refs/heads/master": protected,
            "refs/heads/handoff/current": protected,
            "refs/remotes/origin/master": protected,
            "refs/remotes/origin/handoff/current": protected,
        },
        "forbidden_effect_classes": sorted(pa.G1A_TO_G1B1_FORBIDDEN_EFFECTS),
    }
    _git(
        root,
        "add",
        "--",
        *(path for path in transition_paths if path != artifact_relative),
    )
    after_policy = load_programme_policy(root)
    semantic = pa._g1a_to_g1b1_transition_semantic_pointer_map(root, enablement)
    artifact = {
        "schema_version": "ariadne.g1a-to-g1b1-transition.v1",
        "transition_id": transition_id,
        "recorded_at": "2026-09-01T00:10:00+10:00",
        "transition_manifest": manifest,
        "transition_manifest_sha256": pa._sha256_bytes(
            json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode()
        ),
        "g1a3_r1_review_record_sha256": pa.G1A3_R1_REVIEW_SHA256,
        "external_review_record_sha256": review_digest,
        "enablement_candidate_commit": enablement,
        "enablement_candidate_tree": enablement_tree,
        "enablement_candidate_parent": "23aa3ab19aec6cee9246e7dd3a88f61ada39bd7a",
        "accepted_surface_sha256": manifest["accepted_surface_sha256"],
        "accepted_surface_git_blob": manifest["accepted_surface_git_blob"],
        "clockwork_scope_sha256": manifest["clockwork_scope_sha256"],
        "clockwork_scope_git_blob": manifest["clockwork_scope_git_blob"],
        "state_digest_before": before_policy.state_digest,
        "state_digest_after": after_policy.state_digest,
        "policy_digest_before": before_policy.policy_digest,
        "policy_digest_after": after_policy.policy_digest,
        "changed_semantic_pointers": semantic,
        "scope_result": "passed",
        "g1b1_profile_contract": {
            "active_profile": pa.G1B1_ACTIVE_PROFILE,
            "task_class": pa.G1B1_TASK_CLASS,
            "allowed_paths": sorted(pa.G1B1_ALLOWED_PATHS),
            "allowed_effects": sorted(pa.G1B1_ALLOWED_EFFECTS),
            "forbidden_effects": sorted(pa.G1B1_FORBIDDEN_EFFECTS),
            "runtime_entrypoints_closed": True,
        },
    }
    _write_json(artifact_path, artifact)
    _git(root, "add", "--", *transition_paths)
    _git(root, "commit", "--no-verify", "-m", "synthetic G1A to G1B.1 transition")
    transition = _git(root, "rev-parse", "HEAD")
    assert _git(root, "rev-list", "--parents", "-n", "1", transition) == (
        f"{transition} {enablement}"
    )
    return root, gatekeeper, manifest, enablement, transition


def _build_g1b1_to_g1b2_transition_repository(
    tmp_path: Path,
) -> tuple[Path, Path, dict, str, str]:
    """Build a direct-child closeout controller and separate state-only transition."""
    root = tmp_path / "g1b2-transition-target"
    root.mkdir()
    _git(root, "init", "-b", "codex/raisa-ariadne-recovery-g0")
    object_store = _git(
        ROOT, "rev-parse", "--path-format=absolute", "--git-path", "objects"
    )
    alternates = root / ".git/objects/info/alternates"
    alternates.parent.mkdir(parents=True, exist_ok=True)
    alternates.write_bytes((object_store + "\n").encode("utf-8"))
    _git(root, "config", "user.email", "tests@example.invalid")
    _git(root, "config", "user.name", "G1B.2 Transition Tests")
    _git(root, "config", "core.autocrlf", "false")
    _git(root, "config", "core.longpaths", "true")
    _copy_indexed_candidate(root)

    origin = tmp_path / "g1b2-origin.git"
    origin.mkdir()
    _git(origin, "init", "--bare")
    _git(root, "remote", "add", "origin", str(origin))
    overlay_path = root / pa.OVERLAY_PATH
    overlay = yaml.safe_load(overlay_path.read_text(encoding="utf-8"))
    overlay["remote_identity_policy"] = pa.build_synthetic_remote_identity_policy(
        origin
    )
    _write_yaml(overlay_path, overlay)
    latch_path = root / pa.LATCH_PATH
    latch = json.loads(latch_path.read_text(encoding="utf-8"))
    latch["checkpoint"]["settings_fingerprint"] = settings_fingerprint(
        root / "orchestration/harness_settings"
    )
    _write_json(latch_path, latch)
    _git(root, "add", "-A")
    controller_tree = _git(root, "write-tree")
    accepted_g1b1 = "faaf2d2b4e72c823b79d9da9aed49f0182125748"
    controller = _git(
        root,
        "commit-tree",
        controller_tree,
        "-p",
        accepted_g1b1,
        "-m",
        "synthetic externally reviewable G1B.1 closeout controller",
    )
    branch_ref = "refs/heads/codex/raisa-ariadne-recovery-g0"
    _git(root, "update-ref", branch_ref, controller)
    protected = "2e34bdad732fdab32fbf778280b3d3c70d66d602"
    _git(root, "branch", "master", protected)
    _git(root, "branch", "handoff/current", protected)
    _git(
        root,
        "branch",
        "safety/ariadne-clockwork-pre-g0-20260825",
        "03e6860394c39086ec1ffb3f2457acc5f7c8b5f9",
    )
    _git(root, "push", "origin", f"{protected}:refs/heads/master")
    _git(root, "push", "origin", f"{protected}:refs/heads/handoff/current")
    _git(root, "push", "-u", "origin", f"{controller}:{branch_ref}")
    _git(root, "fetch", "origin")
    before_policy = load_programme_policy(root)
    assert before_policy.state["active_profile"] == (
        pa.G1B1_CLOSEOUT_REVIEW_PENDING_PROFILE
    )
    assert before_policy.allowed_paths == ()

    gatekeeper = tmp_path / "g1b2-pinned-gatekeeper"
    _git(root, "worktree", "add", "--detach", str(gatekeeper), controller)
    _materialize_exact_commit_bytes(gatekeeper, controller)

    transition_id = "g1b1-to-g1b2-synthetic-pass"
    review_id = "g1b1-closeout-g1b2-synthetic-pass"
    reviewer_surface = "external_native_review"
    review_relative = (
        "orchestration/programme/subgate-transition-enablement-reviews/"
        f"{review_id}.json"
    )
    artifact_relative = f"{pa.SUBGATE_TRANSITION_ARTIFACT_ROOT}/{transition_id}.json"
    review_path = root / review_relative
    artifact_path = root / artifact_relative
    review = {
        "schema_version": "ariadne.external_g1b1_closeout_g1b2_enablement_review.v1",
        "review_id": review_id,
        "recorded_at": "2026-09-03T11:00:00+10:00",
        "review_subject": "G1B1_closeout_and_G1B2_transition_enablement_controller",
        "reviewed_commit": controller,
        "reviewed_tree": controller_tree,
        "reviewed_parent": accepted_g1b1,
        "verdict": "PASS",
        "blocking_finding_count": 0,
        "reviewer_surface": reviewer_surface,
        "g1b1_closeout_authorized": True,
        "g1b2_state_transition_authorized": True,
        "g1b2_implementation_authorized": False,
        "provider_invocation_authorized": False,
        "integration_execution_authorized": False,
        "existing_clockwork_runtime_mutation_authorized": False,
        "g1c_authorized": False,
        "protected_ref_movement_authorized": False,
        "source_artifact_sha256": "4" * 64,
    }
    _write_json(review_path, review)
    review_digest = pa._sha256_bytes(review_path.read_bytes())

    state_path = root / pa.STATE_PATH
    state = json.loads(state_path.read_text(encoding="utf-8"))
    state["observed_at"] = "2026-09-03T11:05:00+10:00"
    state["current_gate"] = "G1B.2"
    state["active_correction"] = "G1B.2"
    state["active_profile"] = pa.G1B2_ACTIVE_PROFILE
    state["g1b"]["status"] = "active_G1B2"
    state["g1b"]["next_action"] = "begin_bounded_G1B2_pure_journal_replay_kernel"
    state["g1b"]["subgates"]["G1B.1"].update(
        {
            "status": "passed",
            "closeout_status": "accepted",
            "closed": True,
        }
    )
    transition_record = {
        "status": "complete",
        "transition_id": transition_id,
        "from_profile": pa.G1B1_CLOSEOUT_REVIEW_PENDING_PROFILE,
        "to_profile": pa.G1B2_ACTIVE_PROFILE,
        "enablement_review_id": review_id,
        "enablement_candidate_commit": controller,
        "enablement_candidate_tree": controller_tree,
        "external_review_status": "pass",
        "blocking_finding_count": 0,
        "reviewer_surface": reviewer_surface,
        "next_action": "begin_bounded_G1B2_pure_journal_replay_kernel",
    }
    state["g1b"]["subgates"]["G1B.2"].update(
        {
            "status": "active",
            "state_transition_status": "complete",
            "state_transition": transition_record,
            "implementation_authorized": True,
        }
    )
    state["task_selection"].update(
        {
            "allowed_task_kinds": [pa.G1B2_TASK_CLASS],
            "next_eligible_now": True,
            "next_tranche_admission_requires_state_transition": False,
            "next_eligibility_condition": (
                "bounded_G1B2_profile_active_next_tranche_not_started"
            ),
        }
    )
    _write_json(state_path, state)

    gates_path = root / pa.GATES_PATH
    gates = yaml.safe_load(gates_path.read_text(encoding="utf-8"))
    gates["programme"]["prepared_at"] = "2026-09-03T11:05:00+10:00"
    gates["programme"]["current_gate"] = "G1B.2"
    by_id = {row["id"]: row for row in gates["gates"]}
    by_id["G1B"]["status"] = "active_subgate_G1B_2"
    by_id["G1B.1"]["status"] = "passed"
    by_id["G1B.2"]["status"] = "active"
    _write_yaml(gates_path, gates)

    overlay = yaml.safe_load(overlay_path.read_text(encoding="utf-8"))
    overlay["active_profile"] = pa.G1B2_ACTIVE_PROFILE
    overlay["g1b1_to_g1b2_transition_policy"]["transition_status"] = "complete"
    _write_yaml(overlay_path, overlay)

    agents_path = root / pa.AGENTS_PATH
    agents = agents_path.read_text(encoding="utf-8")
    marker = "# EMR4 Centaur — Live Agent Handover"
    assert marker in agents
    body = agents.split(marker, 1)[1]
    agents_path.write_bytes(
        (
            "# EMERGENCY RAISA/ARIADNE RECOVERY PRECEDENCE\n\n"
            "Gate G1B.2 is active only for the pure versioned journal and "
            "deterministic replay kernel; G1C remains closed.\n\n"
            "Missing, malformed, stale, or contradictory programme state is a "
            "hard stop.\n\n" + marker + body
        ).encode("utf-8")
    )

    latch = json.loads(latch_path.read_text(encoding="utf-8"))
    latch.update(
        {
            "operation_id": "g1b2-pure-journal-replay-kernel",
            "active_tranche": "G1B.2 pure journal and deterministic replay kernel",
            "objective": (
                "Implement only the predeclared pure G1B.2 journal/replay kernel."
            ),
            "status": "in_progress",
            "source_head": controller,
            "authority_source": (
                "External G1B.1 closeout and G1B.2 transition-enablement PASS"
            ),
            "resume_after_compaction": True,
        }
    )
    latch["checkpoint"]["completed_stage"] = (
        "G1B.1 closeout accepted and state-only G1B.1-to-G1B.2 transition complete."
    )
    latch["checkpoint"]["next_executable_stage"] = (
        "Bounded G1B.2 pure journal/replay implementation only."
    )
    latch["checkpoint"]["settings_fingerprint"] = settings_fingerprint(
        root / "orchestration/harness_settings"
    )
    latch["terminal_response"].update(
        {"permitted": False, "reason": "unfinished_authorized_operation"}
    )
    _write_json(latch_path, latch)

    transition_paths = sorted(
        pa.G1B1_TO_G1B2_TRANSITION_FIXED_ALLOWED_PATHS
        | {review_relative, artifact_relative}
    )
    accepted_payload = pa._git_object_bytes(
        root, f"{controller}:{pa.G1B1_ACCEPTED_SURFACE_PATH.as_posix()}"
    )
    manifest = {
        "schema_version": pa.G1B1_TO_G1B2_TRANSITION_MANIFEST_VERSION,
        "transition_id": transition_id,
        "from_profile": pa.G1B1_CLOSEOUT_REVIEW_PENDING_PROFILE,
        "to_profile": pa.G1B2_ACTIVE_PROFILE,
        "g1b1_implementation_review_id": pa.G1B1_REVIEW_ID,
        "g1b1_implementation_review_record_sha256": pa.G1B1_REVIEW_SHA256,
        "enablement_review_id": review_id,
        "enablement_candidate_commit": controller,
        "enablement_candidate_tree": controller_tree,
        "enablement_candidate_parent": accepted_g1b1,
        "transition_parent": controller,
        "external_review_verdict": "PASS",
        "external_review_record_sha256": review_digest,
        "blocking_finding_count": 0,
        "reviewer_surface": reviewer_surface,
        "state_digest_before": before_policy.state_digest,
        "policy_digest_before": before_policy.policy_digest,
        "accepted_surface_sha256": pa._sha256_bytes(accepted_payload),
        "accepted_runtime_git_blob": "5a8600b043773c3187b3770d9c40614ced76a370",
        "accepted_test_git_blob": "94b9cd01d33adc47da324d61855e79c9c940e9ef",
        "allowed_transition_paths": transition_paths,
        "required_semantic_pointer_delta": (
            pa.G1B1_TO_G1B2_TRANSITION_SEMANTIC_POINTERS
        ),
        "protected_refs_before": {
            "refs/heads/master": protected,
            "refs/heads/handoff/current": protected,
            "refs/remotes/origin/master": protected,
            "refs/remotes/origin/handoff/current": protected,
        },
        "forbidden_effect_classes": sorted(pa.G1B1_TO_G1B2_FORBIDDEN_EFFECTS),
    }
    _git(
        root,
        "add",
        "--",
        *(path for path in transition_paths if path != artifact_relative),
    )
    after_policy = load_programme_policy(root)
    semantic = pa._g1b1_to_g1b2_transition_semantic_pointer_map(root, controller)
    assert semantic == pa.G1B1_TO_G1B2_TRANSITION_SEMANTIC_POINTERS
    artifact = {
        "schema_version": "ariadne.g1b1-to-g1b2-transition.v1",
        "transition_id": transition_id,
        "recorded_at": "2026-09-03T11:05:00+10:00",
        "transition_manifest": manifest,
        "transition_manifest_sha256": pa._sha256_bytes(
            json.dumps(
                manifest,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ),
        "g1b1_implementation_review_record_sha256": pa.G1B1_REVIEW_SHA256,
        "external_review_record_sha256": review_digest,
        "enablement_candidate_commit": controller,
        "enablement_candidate_tree": controller_tree,
        "enablement_candidate_parent": accepted_g1b1,
        "accepted_surface_sha256": manifest["accepted_surface_sha256"],
        "accepted_runtime_git_blob": manifest["accepted_runtime_git_blob"],
        "accepted_test_git_blob": manifest["accepted_test_git_blob"],
        "state_digest_before": before_policy.state_digest,
        "state_digest_after": after_policy.state_digest,
        "policy_digest_before": before_policy.policy_digest,
        "policy_digest_after": after_policy.policy_digest,
        "changed_semantic_pointers": semantic,
        "scope_result": "passed",
        "g1b2_profile_contract": {
            "active_profile": pa.G1B2_ACTIVE_PROFILE,
            "task_class": pa.G1B2_TASK_CLASS,
            "allowed_paths": sorted(pa.G1B2_ALLOWED_PATHS),
            "allowed_effects": sorted(pa.G1B2_ALLOWED_EFFECTS),
            "forbidden_effects": sorted(pa.G1B2_FORBIDDEN_EFFECTS),
            "runtime_entrypoints_closed": True,
        },
    }
    _write_json(artifact_path, artifact)
    _git(root, "add", "--", *transition_paths)
    staged_tree = _git(root, "write-tree")
    assert _git(root, "rev-parse", "HEAD") == controller
    assert staged_tree != controller_tree
    return root, gatekeeper, manifest, controller, staged_tree


def test_synthetic_g1b1_closeout_to_g1b2_state_transition_is_separate_and_pinned(
    tmp_path: Path,
) -> None:
    root, gatekeeper, manifest, controller, staged_tree = (
        _build_g1b1_to_g1b2_transition_repository(tmp_path)
    )
    development = pg.evaluate_pinned_programme_operation(
        gatekeeper_root=gatekeeper,
        target_repo_root=root,
        manifest=manifest,
        entrypoint="task_branch_commit",
        phase="development",
    )
    assert development.admitted is True, development.reason_codes
    assert development.gatekeeper_commit == controller
    assert development.target_head == controller
    assert development.target_index_tree == staged_tree
    assert '"commit", "--no-verify"' not in inspect.getsource(
        _build_g1b1_to_g1b2_transition_repository
    )
    receipt_directory = tmp_path / "g1b2-operation-receipts"
    receipt_directory.mkdir()
    commit_receipt = pg.execute_exact_index_commit(
        gatekeeper_root=gatekeeper,
        target_repo_root=root,
        manifest=manifest,
        message="synthetic G1B.1 to G1B.2 transition",
        receipt_directory=receipt_directory,
    )
    transition = commit_receipt["result_sha"]
    assert commit_receipt["result_tree"] == staged_tree
    assert _git(root, "rev-list", "--parents", "-n", "1", transition) == (
        f"{transition} {controller}"
    )
    pre_push = pg.evaluate_pinned_programme_operation(
        gatekeeper_root=gatekeeper,
        target_repo_root=root,
        manifest=manifest,
        entrypoint="task_branch_push",
        phase="pre-push",
    )
    assert pre_push.admitted is True, pre_push.reason_codes
    push_receipt = pg.execute_exact_sha_push(
        gatekeeper_root=gatekeeper,
        target_repo_root=root,
        manifest=manifest,
        receipt_directory=receipt_directory,
    )
    assert push_receipt["result_sha"] == transition
    assert push_receipt["post_push_readback_sha"] == transition
    post_push = pg.evaluate_pinned_programme_operation(
        gatekeeper_root=gatekeeper,
        target_repo_root=root,
        manifest=manifest,
        entrypoint="task_branch_push",
        phase="post-push",
    )
    assert post_push.admitted is True, post_push.reason_codes
    task_manifest = build_task_manifest(root)
    assert task_manifest["task_class"] == pa.G1B2_TASK_CLASS
    assert set(task_manifest["allowed_path_roots"]) == pa.G1B2_ALLOWED_PATHS
    assert not (root / pa.G1B2_RUNTIME_PATH).exists()
    assert not (root / pa.G1B2_TEST_PATH).exists()
    candidate_local = evaluate_programme_operation_admission(
        repo_root=root,
        manifest=manifest,
        entrypoint="task_branch_push",
        phase="pre-push",
    )
    assert candidate_local.admitted is False
    assert candidate_local.reason_codes == ["pinned_gatekeeper_required"]
    for entrypoint in ("provider_invocation", "integration"):
        denied = evaluate_programme_admission(
            repo_root=root,
            manifest=task_manifest,
            entrypoint=entrypoint,
        )
        assert denied.admitted is False
    for forbidden_effect in (
        "existing_clockwork_mutation",
        "g1c_work",
        "protected_ref_movement",
    ):
        forged_effect = copy.deepcopy(task_manifest)
        forged_effect["intended_side_effect_classes"].append(forbidden_effect)
        denied = evaluate_programme_admission(
            repo_root=root,
            manifest=forged_effect,
            entrypoint="recovery_preflight",
        )
        assert denied.admitted is False
        assert denied.reason_codes == ["task_manifest_effects_not_admitted"]
    for forged_paths, expected_reason in (
        (
            [pa.G1B2_RUNTIME_PATH.as_posix()],
            "g1b2_task_manifest_paths_not_exact",
        ),
        (
            [*task_manifest["allowed_path_roots"], "app/main.py"],
            "task_manifest_path_outside_policy",
        ),
    ):
        forged_scope = copy.deepcopy(task_manifest)
        forged_scope["allowed_path_roots"] = forged_paths
        denied = evaluate_programme_admission(
            repo_root=root,
            manifest=forged_scope,
            entrypoint="recovery_preflight",
        )
        assert denied.admitted is False
        assert denied.reason_codes == [expected_reason]


def test_historical_r0_candidate_is_bound_to_explicit_commit_and_review() -> None:
    historical_commit = "ccbe0d6a36218903fc6582a0b348bd0b0199794b"
    state = pa._strict_json_payload(
        pa._git_object_bytes(ROOT, f"{historical_commit}:{pa.STATE_PATH.as_posix()}"),
        "historical_r0_state_invalid",
    )
    review = pa._git_object_bytes(ROOT, f"{historical_commit}:{pa.G1A3_R0_REVIEW_PATH}")

    assert state["active_profile"] == pa.G1A3_R0_REVIEW_PENDING_PROFILE
    assert state["task_selection"]["allowed_task_kinds"] == []
    assert state["task_selection"]["next_eligible_now"] is False
    assert pa._sha256_bytes(review) == (pa.G1A3_R0_REVIEW_SHA256)
    assert (
        state["g1a_subgate_authority"]["subgates"]["G1A.3"][
            "provider_invocation_authorized"
        ]
        is False
    )
    assert (
        state["g1a_subgate_authority"]["subgates"]["G1A.3"][
            "integration_execution_authorized"
        ]
        is False
    )


def test_synthetic_external_r0_pass_admits_only_state_transition(
    tmp_path: Path,
) -> None:
    root, _gatekeeper, manifest, _r0 = _build_g1a3_r0_transition_repository(tmp_path)
    decision = evaluate_committed_scope(
        repo_root=root, manifest=manifest, phase="development"
    )
    assert decision.admitted is True, decision.reason_codes
    for entrypoint in ("provider_invocation", "integration"):
        denied = evaluate_programme_admission(
            repo_root=root, manifest=manifest, entrypoint=entrypoint
        )
        assert denied.admitted is False


@pytest.fixture(scope="module")
def staged_g1a_to_g1b1_transition(
    tmp_path_factory: pytest.TempPathFactory,
) -> tuple[Path, Path, dict, str, str]:
    return _build_g1a_to_g1b1_transition_repository(
        tmp_path_factory.mktemp("staged-g1a-to-g1b1-transition")
    )


def test_synthetic_external_closeout_pass_admits_exact_state_transition(
    staged_g1a_to_g1b1_transition: tuple[Path, Path, dict, str, str],
) -> None:
    root, _gatekeeper, manifest, enablement, transition = staged_g1a_to_g1b1_transition
    decision = evaluate_committed_scope(
        repo_root=root, manifest=manifest, phase="development"
    )
    assert decision.admitted is True, decision.reason_codes
    assert decision.candidate_commit_count == 1
    assert decision.authorized_parent_commit == enablement
    assert decision.head == transition
    assert set(
        _git(root, "diff", "--name-only", f"{enablement}..{transition}").splitlines()
    ) == set(manifest["allowed_transition_paths"])
    policy = load_programme_policy(root)
    assert policy.state["current_gate"] == "G1B.1"
    assert policy.state["g1a_closeout"]["g1a_closed"] is True
    assert policy.state["g1b"]["implementation_started"] is False
    assert policy.state["task_selection"]["allowed_task_kinds"] == [pa.G1B1_TASK_CLASS]
    for entrypoint in (
        "provider_invocation",
        "integration",
        "clockwork_tick_mutation",
        "clockwork_closeout_mutation",
        "protected_ref_operation",
        "deployment",
    ):
        denied = evaluate_programme_admission(
            repo_root=root,
            manifest=manifest,
            entrypoint=entrypoint,
        )
        assert denied.admitted is False


@pytest.mark.parametrize(
    "field",
    [
        "transition_parent",
        "enablement_candidate_tree",
        "external_review_record_sha256",
        "accepted_surface_sha256",
        "accepted_surface_git_blob",
        "clockwork_scope_sha256",
        "clockwork_scope_git_blob",
        "state_digest_before",
        "policy_digest_before",
        "protected_refs_before",
        "required_semantic_pointer_delta",
    ],
)
def test_g1a_to_g1b1_transition_rejects_wrong_authority_binding(
    staged_g1a_to_g1b1_transition: tuple[Path, Path, dict, str, str],
    field: str,
) -> None:
    root, _gatekeeper, source, _enablement, _transition = staged_g1a_to_g1b1_transition
    manifest = copy.deepcopy(source)
    if field == "protected_refs_before":
        manifest[field]["refs/heads/master"] = "0" * 40
    elif field == "required_semantic_pointer_delta":
        manifest[field][pa.STATE_PATH.as_posix()] = ["/observed_at"]
    elif field.endswith("sha256") or "digest" in field:
        manifest[field] = "sha256:" + "0" * 64
    else:
        manifest[field] = "0" * 40
    decision = evaluate_committed_scope(
        repo_root=root, manifest=manifest, phase="development"
    )
    assert decision.admitted is False
    assert decision.reason_codes


def test_g1a_to_g1b1_transition_missing_or_forged_review_fails_closed(
    staged_g1a_to_g1b1_transition: tuple[Path, Path, dict, str, str],
) -> None:
    root, _gatekeeper, manifest, _enablement, _transition = (
        staged_g1a_to_g1b1_transition
    )
    path = (
        root / pa.G1A_CLOSEOUT_REVIEW_ROOT / f"{manifest['enablement_review_id']}.json"
    )
    accepted = path.read_bytes()
    try:
        path.unlink()
        missing = evaluate_committed_scope(
            repo_root=root, manifest=manifest, phase="development"
        )
        assert missing.admitted is False
        assert missing.reason_codes == ["trusted_git_path_missing"]
        path.write_bytes(accepted + b" ")
        forged = evaluate_committed_scope(
            repo_root=root, manifest=manifest, phase="development"
        )
        assert forged.admitted is False
        assert forged.reason_codes == ["trusted_git_physical_bytes_mismatch"]
    finally:
        path.write_bytes(accepted)


@pytest.fixture(scope="module")
def staged_subgate_transition(
    tmp_path_factory: pytest.TempPathFactory,
) -> tuple[Path, dict]:
    root, _gatekeeper, manifest, _enablement = _build_g1a3_transition_repository(
        tmp_path_factory.mktemp("staged-subgate-transition")
    )
    return root, manifest


def test_valid_synthetic_g1a2_to_g1a3_state_transition_is_admitted(
    staged_subgate_transition: tuple[Path, dict],
) -> None:
    root, manifest = staged_subgate_transition

    decision = evaluate_committed_scope(
        repo_root=root, manifest=manifest, phase="development"
    )

    assert decision.admitted is True
    assert decision.reason_codes == []
    assert decision.candidate_commit_count == 0
    assert set(manifest["allowed_transition_paths"]) == (
        pa.G1A3_TRANSITION_FIXED_ALLOWED_PATHS
        | {
            f"{pa.G1A3_TRANSITION_REVIEW_ROOT}/{manifest['enablement_review_id']}.json",
            f"{pa.SUBGATE_TRANSITION_ARTIFACT_ROOT}/{manifest['transition_id']}.json",
        }
    )


@pytest.mark.parametrize(
    "case",
    ["negative", "stale_commit", "wrong_tree", "nonzero_findings"],
)
def test_subgate_transition_rejects_nonpassing_or_stale_review_binding(
    staged_subgate_transition: tuple[Path, dict], case: str
) -> None:
    root, source_manifest = staged_subgate_transition
    manifest = copy.deepcopy(source_manifest)
    if case == "negative":
        manifest["external_review_verdict"] = "REVISION_REQUIRED"
    elif case == "stale_commit":
        manifest["enablement_controller_commit"] = "0" * 40
        manifest["transition_parent"] = "0" * 40
    elif case == "wrong_tree":
        manifest["enablement_controller_tree"] = "0" * 40
    else:
        manifest["blocking_finding_count"] = 1

    decision = evaluate_programme_admission(
        repo_root=root, manifest=manifest, entrypoint="recovery_preflight"
    )

    assert decision.admitted is False


def test_subgate_transition_rejects_semantic_pointer_widening(
    staged_subgate_transition: tuple[Path, dict], monkeypatch: pytest.MonkeyPatch
) -> None:
    root, manifest = staged_subgate_transition
    actual = pa._g1a3_transition_semantic_pointer_map(
        root, manifest["enablement_controller_commit"]
    )
    widened = copy.deepcopy(actual)
    widened[pa.STATE_PATH.as_posix()].append("/global_checks/global_gate")
    monkeypatch.setattr(
        pa, "_g1a3_transition_semantic_pointer_map", lambda *_args: widened
    )

    decision = evaluate_committed_scope(
        repo_root=root, manifest=manifest, phase="development"
    )

    assert decision.admitted is False
    assert "g1a3_transition_semantic_pointer_delta_not_exact" in (decision.reason_codes)


def _write_g1b1_contract_candidate(
    root: Path, *, runtime_source: str | None = None, test_source: str | None = None
) -> tuple[Path, Path]:
    runtime = root / pa.G1B1_RUNTIME_PATH
    tests = root / pa.G1B1_TEST_PATH
    runtime.parent.mkdir(parents=True, exist_ok=True)
    tests.parent.mkdir(parents=True, exist_ok=True)
    runtime.write_text(
        runtime_source if runtime_source is not None else _valid_g1b1_runtime_source(),
        encoding="utf-8",
    )
    tests.write_text(
        test_source if test_source is not None else _valid_g1b1_test_source(),
        encoding="utf-8",
    )
    return runtime, tests


def test_g1b1_closed_two_file_contract_accepts_legitimate_pure_kernel(
    tmp_path: Path,
) -> None:
    _write_g1b1_contract_candidate(tmp_path)

    assert pa.g1b1_kernel_contract_reasons(tmp_path) == []


def test_g1b1_pass_and_accepted_surface_are_exact_and_g1b2_is_not_implemented() -> None:
    policy = load_programme_policy(ROOT)
    surface = policy.g1b1_accepted_surface
    review_path = ROOT / pa.G1B1_REVIEW_PATH

    assert hashlib.sha256(review_path.read_bytes()).hexdigest() == (
        "098950cb7763b1483ee67124c13086af847ee8ba1dedcfc752f77ef06988278a"
    )
    assert surface["source"] == {
        "commit": "faaf2d2b4e72c823b79d9da9aed49f0182125748",
        "tree": "a27d0f1e05df2c8f64c070b318a5c1c3cf30f870",
        "sole_parent": "a6703be708d99d148296562d30fe4d5ae011f869",
    }
    assert surface["kernel"]["runtime"]["git_blob"] == (
        "5a8600b043773c3187b3770d9c40614ced76a370"
    )
    assert surface["kernel"]["tests"]["git_blob"] == (
        "94b9cd01d33adc47da324d61855e79c9c940e9ef"
    )
    assert pa.g1b1_kernel_contract_reasons(ROOT) == []
    assert not (ROOT / pa.G1B2_RUNTIME_PATH).exists()
    assert not (ROOT / pa.G1B2_TEST_PATH).exists()


def test_g1b2_predeclared_contract_accepts_only_the_two_synthetic_future_files(
    tmp_path: Path,
) -> None:
    root = tmp_path / "g1b2-contract"
    runtime = root / pa.G1B2_RUNTIME_PATH
    tests = root / pa.G1B2_TEST_PATH
    runtime.parent.mkdir(parents=True)
    tests.parent.mkdir(parents=True)
    runtime.write_bytes(_valid_g1b2_runtime_source().encode("utf-8"))
    tests.write_bytes(_valid_g1b2_test_source().encode("utf-8"))

    assert pa.g1b2_journal_contract_reasons(root) == []
    accepted_kernel = ROOT / pa.G1B1_RUNTIME_PATH
    synthetic_kernel = root / pa.G1B1_RUNTIME_PATH
    synthetic_kernel.parent.mkdir(parents=True, exist_ok=True)
    synthetic_kernel.write_bytes(accepted_kernel.read_bytes())
    completed = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", pa.G1B2_TEST_PATH.as_posix()],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert "6 passed" in completed.stdout


def test_g1b2_rejected_runtime_is_exact_negative_evidence_and_new_tests_close_it(
    tmp_path: Path,
) -> None:
    root = tmp_path / "g1b2-rejected-field-protocol-baseline"
    runtime = root / pa.G1B2_RUNTIME_PATH
    tests = root / pa.G1B2_TEST_PATH
    runtime.parent.mkdir(parents=True)
    tests.parent.mkdir(parents=True)
    accepted_kernel = ROOT / pa.G1B1_RUNTIME_PATH
    synthetic_kernel = root / pa.G1B1_RUNTIME_PATH
    synthetic_kernel.parent.mkdir(parents=True, exist_ok=True)
    synthetic_kernel.write_bytes(accepted_kernel.read_bytes())
    rejected_source = _rejected_g1b2_runtime_source()
    runtime.write_bytes(rejected_source.encode("utf-8"))
    tests.write_bytes(_valid_g1b2_test_source().encode("utf-8"))

    rejected_module = compile(
        rejected_source.encode("utf-8"),
        "rejected-g1b2-runtime.py",
        "exec",
        ast.PyCF_ONLY_AST | ast.PyCF_TYPE_COMMENTS,
        dont_inherit=True,
    )
    assert pa._g1b2_ast_sha256(rejected_module) == (pa.G1B2_REJECTED_RUNTIME_AST_SHA256)
    assert pa.g1b2_journal_contract_reasons(root) == ["g1b2_runtime_ast_not_exact"]
    rejected = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", pa.G1B2_TEST_PATH.as_posix()],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    assert rejected.returncode != 0
    assert "sentinel_protocol_dispatched" in rejected.stdout + rejected.stderr

    runtime.write_bytes(_valid_g1b2_runtime_source().encode("utf-8"))
    corrected = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", pa.G1B2_TEST_PATH.as_posix()],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    assert corrected.returncode == 0, corrected.stdout + corrected.stderr
    assert "6 passed" in corrected.stdout


@pytest.mark.parametrize(
    ("mutation", "expected_reason"),
    [
        (
            lambda source: source.replace("import hashlib", "import os"),
            "g1b2_runtime_ast_not_exact",
        ),
        (
            lambda source: source.replace(
                '    ENTRY_BYTES_TAMPERED = "entry_bytes_tampered"\n', ""
            ),
            "g1b2_runtime_ast_not_exact",
        ),
        (
            lambda source: source.replace(
                "    if type(entry) is not JournalEntry:\n",
                '    open("journal")\n    if type(entry) is not JournalEntry:\n',
                1,
            ),
            "g1b2_runtime_ast_not_exact",
        ),
    ],
)
def test_g1b2_source_contract_rejects_scope_purity_and_vocabulary_drift(
    tmp_path: Path, mutation: Callable[[str], str], expected_reason: str
) -> None:
    root = tmp_path / "g1b2-contract-adversary"
    runtime = root / pa.G1B2_RUNTIME_PATH
    tests = root / pa.G1B2_TEST_PATH
    runtime.parent.mkdir(parents=True)
    tests.parent.mkdir(parents=True)
    runtime.write_bytes(mutation(_valid_g1b2_runtime_source()).encode("utf-8"))
    tests.write_bytes(_valid_g1b2_test_source().encode("utf-8"))

    assert expected_reason in pa.g1b2_journal_contract_reasons(root)


def _rejected_broad_runtime_semantics_would_accept(source: str) -> bool:
    module = compile(
        source.encode("utf-8"),
        "rejected-broad-runtime.py",
        "exec",
        ast.PyCF_ONLY_AST | ast.PyCF_TYPE_COMMENTS,
        dont_inherit=True,
    )
    public = {
        node.name
        for node in module.body
        if isinstance(node, (ast.ClassDef, ast.FunctionDef))
        and not node.name.startswith("_")
    }
    public.update(
        target.id
        for node in module.body
        if isinstance(node, ast.Assign)
        for target in node.targets
        if isinstance(target, ast.Name) and target.id.isupper()
    )
    calls = {
        node.func.id
        for node in ast.walk(module)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    return public == set(pa.G1B2_PUBLIC_API) and {
        "_transition",
        "_canonical_bytes",
        "type",
    }.issubset(calls)


def _rejected_assertion_only_test_predicate(source: str) -> bool:
    module = compile(
        source.encode("utf-8"),
        "rejected-broad-tests.py",
        "exec",
        ast.PyCF_ONLY_AST | ast.PyCF_TYPE_COMMENTS,
        dont_inherit=True,
    )
    functions = [node for node in module.body if isinstance(node, ast.FunctionDef)]
    return {node.name for node in functions} == set(pa.G1B2_REQUIRED_TESTS) and all(
        any(isinstance(item, ast.Assert) for item in ast.walk(function))
        for function in functions
    )


def test_g1b2_exact_ast_rejects_callback_semantic_substitution_before_execution(
    tmp_path: Path,
) -> None:
    root = tmp_path / "g1b2-callback-adversary"
    runtime = root / pa.G1B2_RUNTIME_PATH
    tests = root / pa.G1B2_TEST_PATH
    runtime.parent.mkdir(parents=True)
    tests.parent.mkdir(parents=True)
    callback_source = _valid_g1b2_runtime_source().replace(
        "    if type(journal) is not tuple:\n",
        "    if journal and callable(journal[0]):\n"
        "        return journal[0]()\n"
        "    if type(journal) is not tuple:\n",
        1,
    )
    runtime.write_bytes(callback_source.encode("utf-8"))
    tests.write_bytes(_valid_g1b2_test_source().encode("utf-8"))

    assert _rejected_broad_runtime_semantics_would_accept(callback_source) is True
    assert pa.g1b2_journal_contract_reasons(root) == ["g1b2_runtime_ast_not_exact"]


def test_g1b2_exact_ast_rejects_noop_assertion_bodies_before_import(
    tmp_path: Path,
) -> None:
    root = tmp_path / "g1b2-noop-test-adversary"
    runtime = root / pa.G1B2_RUNTIME_PATH
    tests = root / pa.G1B2_TEST_PATH
    runtime.parent.mkdir(parents=True)
    tests.parent.mkdir(parents=True)
    noop_tests = "\n\n".join(
        f"def {name}():\n    assert {{'{name}'}}"
        for name in sorted(pa.G1B2_REQUIRED_TESTS)
    )
    runtime.write_bytes(_valid_g1b2_runtime_source().encode("utf-8"))
    tests.write_bytes(noop_tests.encode("utf-8"))

    assert _rejected_assertion_only_test_predicate(noop_tests) is True
    assert pa.g1b2_journal_contract_reasons(root) == ["g1b2_test_ast_not_exact"]


@pytest.mark.parametrize(
    "case",
    [
        "single_if_without_default_return",
        "if_elif_with_missing_final_path",
    ],
)
def test_g1b1_transition_totality_rejection_matrix(tmp_path: Path, case: str) -> None:
    source = _valid_g1b1_runtime_source()
    if case == "single_if_without_default_return":
        source = source.replace(
            '    return TransitionResult(state, command, InvalidTransition("invalid_transition"))\n',
            "",
            1,
        )
    else:
        start = source.index("def transition(")
        end = source.index("\n\ndef canonical_bytes", start)
        source = (
            source[:start]
            + """def transition(
    state: ClockworkState,
    event: ClockworkEvent,
    command: ClockworkCommand,
) -> TransitionResult:
    if state is ClockworkState.IDLE and event is ClockworkEvent.START:
        return TransitionResult(ClockworkState.ACTIVE, command, None)
    elif state is ClockworkState.ACTIVE:
        return TransitionResult(state, command, InvalidTransition("invalid_transition"))
"""
            + source[end:]
        )
    _write_g1b1_contract_candidate(tmp_path, runtime_source=source)

    reasons = pa.g1b1_kernel_contract_reasons(tmp_path)

    assert "g1b1_transition_not_total" in reasons


@pytest.mark.parametrize(
    ("case", "function_name", "replacement_body"),
    [
        (
            "same_input_payload_self_equality",
            "test_same_input_gives_byte_identical_output",
            "    result = transition(ClockworkState.IDLE, ClockworkEvent.START, ClockworkCommand.ADVANCE)\n"
            "    payload = canonical_bytes(result)\n"
            "    assert payload == payload\n",
        ),
        (
            "key_order_payload_self_equality",
            "test_canonical_key_order_and_unicode_policy",
            "    result = TransitionResult(ClockworkState.ACTIVE, ClockworkCommand.HOLD, None)\n"
            "    payload = canonical_bytes(result)\n"
            "    assert payload == payload\n",
        ),
        (
            "ambient_payload_self_equality",
            "test_no_ambient_locale_time_or_environment_dependency",
            "    result = transition(ClockworkState.IDLE, ClockworkEvent.START, ClockworkCommand.HOLD)\n"
            "    payload = canonical_bytes(result)\n"
            "    assert payload == payload\n",
        ),
        (
            "schema_versions_payload_self_equality",
            "test_serialized_form_includes_schema_versions",
            "    result = transition(ClockworkState.IDLE, ClockworkEvent.START, ClockworkCommand.ADVANCE)\n"
            "    payload = canonical_bytes(result)\n"
            "    assert payload == payload\n",
        ),
        (
            "wrong_invalid_code_inside_identical_tuples",
            "test_closed_invalid_transition_behavior",
            "    result = transition(ClockworkState.ACTIVE, ClockworkEvent.START, ClockworkCommand.HOLD)\n"
            '    expected = InvalidTransition("wrong")\n'
            "    assert (result.invalid, expected) == (result.invalid, expected)\n",
        ),
        (
            "identical_list_wrapper_equality",
            "test_same_input_gives_byte_identical_output",
            "    first_result = transition(ClockworkState.IDLE, ClockworkEvent.START, ClockworkCommand.ADVANCE)\n"
            "    second_result = transition(ClockworkState.IDLE, ClockworkEvent.START, ClockworkCommand.ADVANCE)\n"
            "    first_payload = canonical_bytes(first_result)\n"
            "    second_payload = canonical_bytes(second_result)\n"
            "    assert [first_payload, second_payload] == [first_payload, second_payload]\n",
        ),
        (
            "required_call_present_but_assertion_unrelated",
            "test_same_input_gives_byte_identical_output",
            "    result = transition(ClockworkState.IDLE, ClockworkEvent.START, ClockworkCommand.ADVANCE)\n"
            "    payload = canonical_bytes(result)\n"
            '    assert b"left" == b"right"\n',
        ),
    ],
)
def test_g1b1_required_tests_reject_derived_tautology_matrix(
    tmp_path: Path,
    case: str,
    function_name: str,
    replacement_body: str,
) -> None:
    del case
    source = _replace_g1b1_test_function(
        _valid_g1b1_test_source(), function_name, replacement_body
    )
    _write_g1b1_contract_candidate(tmp_path, test_source=source)

    reasons = pa.g1b1_kernel_contract_reasons(tmp_path)

    assert "g1b1_test_function_grammar_invalid" in reasons
    assert "g1b1_determinism_test_contract_incomplete" in reasons


@pytest.mark.parametrize(
    ("case", "runtime_mutation", "test_mutation", "expected_reason"),
    [
        (
            "runtime_module_open",
            lambda source: source + '\nopen("outside", "w")\n',
            None,
            "g1b1_dynamic_execution_forbidden",
        ),
        (
            "runtime_transition_open",
            lambda source: source.replace(
                "    if state is ClockworkState.IDLE",
                '    open("outside", "w")\n    if state is ClockworkState.IDLE',
                1,
            ),
            None,
            "g1b1_dynamic_execution_forbidden",
        ),
        (
            "test_open",
            None,
            lambda source: source.replace(
                "    result = transition(",
                '    open("outside", "w")\n    result = transition(',
                1,
            ),
            "g1b1_dynamic_execution_forbidden",
        ),
        (
            "dynamic_import",
            lambda source: source + '\ndef _bad():\n    return __import__("os")\n',
            None,
            "g1b1_dynamic_execution_forbidden",
        ),
        (
            "eval_exec_compile",
            lambda source: (
                source
                + '\ndef _bad(value):\n    eval(value)\n    exec(value)\n    return compile(value, "x", "exec")\n'
            ),
            None,
            "g1b1_dynamic_execution_forbidden",
        ),
        (
            "getattr_recovery",
            lambda source: (
                source + '\ndef _bad(value):\n    return getattr(value, "open")\n'
            ),
            None,
            "g1b1_dynamic_execution_forbidden",
        ),
        (
            "reflective_dunder",
            lambda source: (
                source + "\ndef _bad(value):\n    return value.__subclasses__\n"
            ),
            None,
            "g1b1_reflection_forbidden",
        ),
        (
            "top_level_call",
            lambda source: source + "\n_PRIVATE = dict()\n",
            None,
            "g1b1_module_level_effect_forbidden",
        ),
        (
            "top_level_comprehension",
            lambda source: source + "\n_PRIVATE = [item for item in ()]\n",
            None,
            "g1b1_module_level_effect_forbidden",
        ),
        (
            "effectful_decorator",
            lambda source: (
                source + '\n@open("outside", "w")\ndef _bad():\n    return None\n'
            ),
            None,
            "g1b1_definition_time_effect_forbidden",
        ),
        (
            "effectful_default",
            lambda source: (
                source + '\ndef _bad(value=open("outside", "w")):\n    return value\n'
            ),
            None,
            "g1b1_definition_time_effect_forbidden",
        ),
        (
            "effectful_annotation",
            lambda source: (
                source + '\ndef _bad(value: open("outside", "w")):\n    return value\n'
            ),
            None,
            "g1b1_definition_time_effect_forbidden",
        ),
        (
            "unknown_call",
            lambda source: source + "\ndef _bad():\n    return mystery()\n",
            None,
            "g1b1_unknown_call_target",
        ),
        (
            "extra_public_symbol",
            lambda source: source + "\nEXTRA_PUBLIC = 1\n",
            None,
            "g1b1_exact_public_api_mismatch",
        ),
        (
            "wrong_schema_constant",
            lambda source: source.replace(
                'STATE_SCHEMA_VERSION = "ariadne.clockwork_state.v1"',
                'STATE_SCHEMA_VERSION = "wrong"',
            ),
            None,
            "g1b1_schema_constant_invalid",
        ),
        (
            "wrong_transition_signature",
            lambda source: source.replace(
                "    command: ClockworkCommand,\n) -> TransitionResult:",
                ") -> TransitionResult:",
                1,
            ),
            None,
            "g1b1_transition_signature_invalid",
        ),
        (
            "wrong_canonical_signature",
            lambda source: source.replace(
                "def canonical_bytes(value: TransitionResult) -> bytes:",
                "def canonical_bytes(value) -> bytes:",
            ),
            None,
            "g1b1_canonical_bytes_signature_invalid",
        ),
        (
            "noncanonical_serialization",
            lambda source: source.replace("sort_keys=True", "sort_keys=False"),
            None,
            "g1b1_nondeterministic_serialization_forbidden",
        ),
        (
            "test_import_outside_allowlist",
            None,
            lambda source: "import os as _os\n" + source,
            "g1b1_test_import_not_allowlisted",
        ),
        (
            "test_file_is_parsed",
            None,
            lambda source: source + "\ndef _bad(value):\n    return value.mystery()\n",
            "g1b1_unknown_call_target",
        ),
    ],
    ids=lambda value: value if isinstance(value, str) else None,
)
def test_g1b1_purity_effect_adversarial_matrix(
    tmp_path: Path,
    case: str,
    runtime_mutation: Callable[[str], str] | None,
    test_mutation: Callable[[str], str] | None,
    expected_reason: str,
) -> None:
    del case
    runtime_source = _valid_g1b1_runtime_source()
    test_source = _valid_g1b1_test_source()
    if runtime_mutation is not None:
        runtime_source = runtime_mutation(runtime_source)
    if test_mutation is not None:
        test_source = test_mutation(test_source)
    _write_g1b1_contract_candidate(
        tmp_path, runtime_source=runtime_source, test_source=test_source
    )

    reasons = pa.g1b1_kernel_contract_reasons(tmp_path)

    assert expected_reason in reasons


@pytest.mark.parametrize(
    "module_name",
    [
        "asyncio",
        "builtins",
        "cffi",
        "concurrent.futures",
        "ctypes",
        "datetime",
        "httpx",
        "importlib",
        "marshal",
        "multiprocessing",
        "os",
        "pathlib",
        "pickle",
        "psycopg",
        "random",
        "requests",
        "runpy",
        "secrets",
        "shelve",
        "socket",
        "sqlite3",
        "subprocess",
        "sys",
        "threading",
        "time",
        "urllib.request",
        "uuid",
    ],
)
def test_g1b1_runtime_import_allowlist_rejects_effect_capability_families(
    tmp_path: Path, module_name: str
) -> None:
    source = f"import {module_name} as _forbidden\n" + _valid_g1b1_runtime_source()
    _write_g1b1_contract_candidate(tmp_path, runtime_source=source)

    reasons = pa.g1b1_kernel_contract_reasons(tmp_path)

    assert "g1b1_runtime_import_not_allowlisted" in reasons


@pytest.mark.parametrize(
    ("target", "payload", "expected_reason"),
    [
        ("runtime", b"\xef\xbb\xbf# coding: latin-1\n", "g1b1_runtime_source_invalid"),
        ("runtime", b"# coding: unknown-codec\n", "g1b1_runtime_source_invalid"),
        ("tests", b"\xef\xbb\xbf# coding: latin-1\n", "g1b1_test_source_invalid"),
        ("tests", b"# coding: unknown-codec\n", "g1b1_test_source_invalid"),
    ],
)
def test_g1b1_runtime_faithful_byte_parser_fails_closed(
    tmp_path: Path, target: str, payload: bytes, expected_reason: str
) -> None:
    runtime, tests = _write_g1b1_contract_candidate(tmp_path)
    (runtime if target == "runtime" else tests).write_bytes(payload)

    assert pa.g1b1_kernel_contract_reasons(tmp_path) == [expected_reason]


def test_g1b1_determinism_test_contract_is_mandatory(tmp_path: Path) -> None:
    source = _valid_g1b1_test_source().replace(
        "test_serialized_form_includes_schema_versions",
        "test_serialized_form_omits_schema_versions",
    )
    _write_g1b1_contract_candidate(tmp_path, test_source=source)

    assert "g1b1_determinism_test_contract_incomplete" in (
        pa.g1b1_kernel_contract_reasons(tmp_path)
    )


@pytest.mark.parametrize(
    ("case", "expected_event"),
    [
        ("import_alias_shadow", "dumps"),
        ("approved_target_shadow", "call"),
        ("arbitrary_encode_receiver", "encode"),
        ("custom___getattribute__", "getattribute"),
        ("custom___format__", "format"),
        ("custom___str__", "str"),
        ("custom___iter___list", "iter"),
        ("custom___iter___tuple", "iter"),
        ("custom___iter___dict", "iter"),
        ("custom___iter___sorted", "iter"),
        ("custom___getitem__", "getitem"),
        ("custom___call__", "call"),
        ("unvalidated_iteration", "iter"),
        ("unvalidated_comparison", "compare"),
        ("unvalidated_arithmetic", "arithmetic"),
    ],
)
def test_g1b1_parent_dispatch_bypasses_are_rejected_before_harmless_execution(
    tmp_path: Path, case: str, expected_event: str
) -> None:
    source = _parent_valid_g1b1_runtime_source()
    statement_by_case = {
        "import_alias_shadow": "    _json = value\n",
        "approved_target_shadow": "    _invoke = value\n    _invoke()\n",
        "arbitrary_encode_receiver": '    value.encode("utf-8")\n',
        "custom___getattribute__": "    observed = value.dispatch\n",
        "custom___format__": '    observed = f"{value}"\n',
        "custom___str__": "    observed = str(value)\n",
        "custom___iter___list": "    observed = list(value)\n",
        "custom___iter___tuple": "    observed = tuple(value)\n",
        "custom___iter___dict": "    observed = dict(value)\n",
        "custom___iter___sorted": "    observed = sorted(value)\n",
        "custom___getitem__": "    observed = value[0]\n",
        "custom___call__": "    _invoke = value\n    _invoke()\n",
        "unvalidated_iteration": "    for observed in value:\n        pass\n",
        "unvalidated_comparison": "    observed = value < 1\n",
        "unvalidated_arithmetic": "    observed = value + 1\n",
    }
    source = _insert_before_parent_payload(source, statement_by_case[case])
    if case in {"approved_target_shadow", "custom___call__"}:
        source += "\n\ndef _invoke():\n    return None\n"

    assert _parent_broad_call_model_would_admit(source) is True
    _write_g1b1_contract_candidate(tmp_path, runtime_source=source)
    reasons = pa.g1b1_kernel_contract_reasons(tmp_path)

    assert reasons
    assert (
        "g1b1_lexical_binding_shadowed" in reasons
        or "g1b1_protocol_dispatch_forbidden" in reasons
        or "g1b1_canonical_bytes_grammar_invalid" in reasons
        or "g1b1_canonical_bytes_signature_invalid" in reasons
    )

    namespace: dict[str, object] = {}
    exec(  # noqa: S102 - exact harmless sentinel proof required by the contract
        compile(source, "<synthetic-g1b1-dispatch>", "exec"), namespace
    )
    sentinel = _G1B1DispatchSentinel()
    namespace["canonical_bytes"](sentinel)
    assert expected_event in sentinel.events


@pytest.mark.parametrize(
    "case",
    [
        "module___all__",
        "module___getattr__",
        "extra_private_helper",
        "extra_private_class",
        "api_name_rebinding",
        "approved_builtin_rebinding",
        "parameter_call_target_shadowing",
        "comprehension_call_target_shadowing",
        "arbitrary_receiver_method",
        "required_test_pass_only",
        "required_test_assert_true_only",
        "required_test_constant_tautology",
        "test_local_call_target_shadowing",
    ],
)
def test_g1b1_exact_closed_grammar_rejects_remaining_adversarial_matrix(
    tmp_path: Path, case: str
) -> None:
    runtime_source = _valid_g1b1_runtime_source()
    test_source = _valid_g1b1_test_source()
    if case == "module___all__":
        runtime_source += "\n__all__ = ()\n"
    elif case == "module___getattr__":
        runtime_source += "\ndef __getattr__(name):\n    return name\n"
    elif case == "extra_private_helper":
        runtime_source += "\ndef _helper():\n    return None\n"
    elif case == "extra_private_class":
        runtime_source += "\nclass _Helper:\n    pass\n"
    elif case == "api_name_rebinding":
        runtime_source = runtime_source.replace(
            "    payload = {\n",
            "    TransitionResult = value\n    TransitionResult()\n    payload = {\n",
            1,
        )
    elif case == "approved_builtin_rebinding":
        runtime_source = runtime_source.replace(
            "    payload = {\n",
            "    str = value\n    str()\n    payload = {\n",
            1,
        )
    elif case == "parameter_call_target_shadowing":
        runtime_source += "\ndef _helper(transition):\n    return transition()\n"
    elif case == "comprehension_call_target_shadowing":
        runtime_source = runtime_source.replace(
            "    payload = {\n",
            "    observed = [transition for transition in ()]\n    payload = {\n",
            1,
        )
    elif case == "arbitrary_receiver_method":
        runtime_source = runtime_source.replace(
            "    payload = {\n",
            "    value.mystery()\n    payload = {\n",
            1,
        )
    elif case in {
        "required_test_pass_only",
        "required_test_assert_true_only",
        "required_test_constant_tautology",
    }:
        start = test_source.index("def test_same_input_gives_byte_identical_output")
        end = test_source.index("\n\ndef test_canonical_key_order", start)
        body = {
            "required_test_pass_only": "    pass\n",
            "required_test_assert_true_only": "    assert True\n",
            "required_test_constant_tautology": (
                "    result = transition(ClockworkState.IDLE, ClockworkEvent.START, "
                "ClockworkCommand.ADVANCE)\n"
                "    payload = canonical_bytes(result)\n"
                "    assert 1 == 1\n"
            ),
        }[case]
        test_source = (
            test_source[:start]
            + "def test_same_input_gives_byte_identical_output():\n"
            + body
            + test_source[end:]
        )
    elif case == "test_local_call_target_shadowing":
        test_source = test_source.replace(
            "def test_same_input_gives_byte_identical_output():\n",
            "def test_same_input_gives_byte_identical_output():\n"
            "    transition = ClockworkState.IDLE\n",
            1,
        )

    _write_g1b1_contract_candidate(
        tmp_path, runtime_source=runtime_source, test_source=test_source
    )
    reasons = pa.g1b1_kernel_contract_reasons(tmp_path)

    assert reasons
    if case in {
        "required_test_pass_only",
        "required_test_assert_true_only",
        "required_test_constant_tautology",
    }:
        assert "g1b1_determinism_test_contract_incomplete" in reasons
    if "shadowing" in case or "rebinding" in case:
        assert "g1b1_lexical_binding_shadowed" in reasons


def test_candidate_local_controller_cannot_accept_subgate_transition(
    staged_subgate_transition: tuple[Path, dict],
) -> None:
    root, manifest = staged_subgate_transition

    decision = evaluate_programme_operation_admission(
        repo_root=root,
        manifest=manifest,
        entrypoint="task_branch_commit",
        phase="development",
    )

    assert decision.admitted is False
    assert decision.reason_codes == ["pinned_gatekeeper_required"]


def test_superseded_g0_transition_regressions_are_bound_to_historical_source() -> None:
    """Do not reinterpret the G0 controller suite against the G1A closeout state."""
    historical = "7cae4e88e2f3951e51dcaf1378e52187e191a33d"
    assert (
        _git(
            ROOT,
            "rev-parse",
            f"{historical}:tests/test_programme_admission.py",
        )
        == "a3d76a1bb739a122b8ef0d0891550650283183ca"
    )
    assert (
        _git(
            ROOT,
            "rev-parse",
            f"{historical}:orchestration_harness/programme_admission.py",
        )
        == "124c205d5d05f35bc658c8a6fc5a0996ab562be0"
    )


def test_commit_and_push_require_one_combined_admission_and_scope_decision() -> None:
    manifest = _manifest()
    manifest["allowed_path_roots"] = [pa.STATE_PATH.as_posix()]
    direct = evaluate_programme_admission(
        repo_root=ROOT, manifest=manifest, entrypoint="task_branch_commit"
    )
    combined = evaluate_programme_operation_admission(
        repo_root=ROOT,
        manifest=manifest,
        entrypoint="task_branch_commit",
        phase="development",
    )
    assert direct.admitted is False
    assert direct.reason_codes == ["task_class_not_admitted"]
    assert combined.admitted is False
    assert combined.reason_codes == ["pinned_gatekeeper_required"]


def test_direct_antigravity_runner_rechecks_admission_before_forged_receipt(
    tmp_path: Path,
) -> None:
    from scripts import ariadne_antigravity

    packet = tmp_path / "packet.md"
    packet.write_text("forged launch", encoding="utf-8")
    forged = tmp_path / "historical-receipt.json"
    forged.write_text(
        json.dumps(
            {
                "schema_version": "ariadne.orchestrator_receipt.v1",
                "status": "passed",
                "worker_dispatch_permitted": True,
                "rehydration_sources": sorted(ariadne_antigravity.REHYDRATION_SOURCES),
            }
        ),
        encoding="utf-8",
    )
    output = tmp_path / "provider-output.json"

    with pytest.raises(ProgrammeAdmissionError, match="task_manifest_missing"):
        ariadne_antigravity.run_worker(
            packet_path=packet,
            cwd=ROOT,
            output_path=output,
            orchestrator_receipt_path=forged,
            model=ariadne_antigravity.DEFAULT_MODEL,
            os_sandbox=False,
        )

    assert not output.exists()


def test_direct_deepseek_runner_rechecks_admission_before_subprocess(
    tmp_path: Path,
) -> None:
    from scripts import ariadne_deepseek_claude

    packet = tmp_path / "packet.md"
    packet.write_text("forged launch", encoding="utf-8")
    output = tmp_path / "provider-output.json"

    with pytest.raises(ProgrammeAdmissionError, match="task_manifest_missing"):
        ariadne_deepseek_claude.run_worker(
            packet_path=packet,
            cwd=ROOT,
            output_path=output,
            model="deepseek-v4-flash",
            effort="high",
        )

    assert not output.exists()


def test_direct_clockwork_closeout_rechecks_admission_before_read_or_write(
    tmp_path: Path,
) -> None:
    from scripts import ariadne_governance_clockwork_closeout as closeout

    with pytest.raises(ProgrammeAdmissionError, match="task_manifest_missing"):
        closeout.run_bound_closeout(
            ROOT,
            intent_raw=tmp_path / "missing.json",
            mode="publish",
        )


def test_agent_worktree_mutator_rechecks_admission_before_mutation() -> None:
    from scripts import agent_worktrees

    args = SimpleNamespace(programme_task_manifest=None)

    with pytest.raises(ProgrammeAdmissionError, match="task_manifest_missing"):
        agent_worktrees.setup(args)


def test_nested_closeout_forwards_programme_manifest(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from scripts import ariadne_governance_clockwork_closeout as closeout

    intent = tmp_path / "closeout-intent.json"
    intent.write_text(
        json.dumps({"schema_version": closeout.SEMANTIC_TICK_INTENT_VERSION}),
        encoding="utf-8",
    )
    manifest = tmp_path / "transition-manifest.json"
    manifest.write_text("{}", encoding="utf-8")
    calls: list[list[str]] = []
    monkeypatch.setattr(closeout, "require_programme_admission", lambda **_kwargs: None)
    monkeypatch.setattr(closeout, "validate_contract", lambda value: value)
    monkeypatch.setattr(
        closeout,
        "admit_tick_intent",
        lambda *_args: {"command_manifest": {"commands": []}},
    )
    monkeypatch.setattr(
        closeout, "resolve_full_head", lambda *_args, **_kwargs: "1" * 40
    )
    monkeypatch.setattr(
        closeout,
        "resolve_repository_interpreter",
        lambda *_args, **_kwargs: (Path(sys.executable), Path(sys.executable)),
    )
    monkeypatch.setattr(closeout, "_git_paths", lambda *_args, **_kwargs: set())
    monkeypatch.setattr(closeout, "_publication_surface", lambda *_args, **_kwargs: {})

    def stop_after_capture(command, **_kwargs):
        calls.append(command)
        raise RuntimeError("captured nested tick")

    monkeypatch.setattr(closeout, "_run_text", stop_after_capture)

    with pytest.raises(RuntimeError, match="captured nested tick"):
        closeout.run_bound_closeout(
            tmp_path,
            intent_raw=Path("closeout-intent.json"),
            mode="publish",
            programme_task_manifest=manifest,
        )

    assert calls
    assert "--programme-task-manifest" in calls[0]
    assert calls[0][calls[0].index("--programme-task-manifest") + 1] == str(
        manifest.resolve()
    )


@pytest.mark.parametrize(
    "arguments",
    [
        [
            "scripts/ariadne_antigravity.py",
            "--packet",
            "missing",
            "--cwd",
            ".",
            "--output",
            "missing",
            "--orchestrator-receipt",
            "missing",
        ],
        [
            "scripts/ariadne_deepseek_claude.py",
            "--packet",
            "missing",
            "--cwd",
            ".",
            "--output",
            "missing",
        ],
        ["scripts/drive_agent_headless.py", "--cwd", ".", "--prompt", "none"],
        [
            "scripts/ariadne_governance_clockwork_tick.py",
            "--publish",
            "--intent",
            "missing",
        ],
        [
            "scripts/ariadne_governance_clockwork_closeout.py",
            "--publish",
            "--intent",
            "missing",
        ],
        [
            "scripts/agent_worktrees.py",
            "dispatch",
            "--agent",
            "claude",
            "--title",
            "x",
            "--mission",
            "x",
            "--in-scope",
            "x",
            "--out-of-scope",
            "x",
            "--verification",
            "x",
            "--merge-criteria",
            "x",
        ],
        ["scripts/agent_worktrees.py", "submit"],
        ["scripts/agent_worktrees.py", "handoff"],
    ],
)
def test_gated_cli_entrypoints_reject_missing_manifest_before_effects(
    arguments: list[str],
) -> None:
    completed = subprocess.run(
        [sys.executable, *arguments],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert completed.returncode == 2
    assert "task_manifest_missing" in (completed.stdout + completed.stderr).lower()
