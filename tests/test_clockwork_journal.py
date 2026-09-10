from dataclasses import replace as _replace
from orchestration_harness.clockwork_journal import (
    GENESIS_PREVIOUS_DIGEST,
    JOURNAL_ENTRY_SCHEMA_VERSION,  # noqa: F401
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
    assert (
        first.digest
        == "sha256:58cb7d6ba45ce9071c26c587977e3b676e90d2c491227d1b2a64b19d2fa11d9c"
    )
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
    third_result = append_entry(
        (first, second), ClockworkEvent.STOP, ClockworkCommand.ADVANCE
    )
    assert third_result.rejection is None
    third = third_result.validated_journal[-1]
    gap = _redigest(_replace(second, sequence=3))
    duplicate = _redigest(_replace(second, sequence=1))
    reordered = _redigest(_replace(third, sequence=1))
    assert replay((first, gap)).rejection is JournalRejection.SEQUENCE_GAP
    assert replay((first, duplicate)).rejection is JournalRejection.DUPLICATE_SEQUENCE
    assert (
        replay((first, second, reordered)).rejection is JournalRejection.REORDERED_ENTRY
    )


def test_wrong_schema_foreign_types_and_malformed_digests_are_rejected():
    first = _base_journal()[0]
    assert (
        replay((_replace(first, schema_version="wrong"),)).rejection
        is JournalRejection.WRONG_SCHEMA
    )
    assert (
        replay((_ExplosiveForeignEntry(),)).rejection is JournalRejection.FOREIGN_TYPE
    )
    _assert_fixed_serializer_errors(_ExplosiveForeignEntry())
    assert (
        replay((_replace(first, sequence=True),)).rejection
        is JournalRejection.INVALID_SEQUENCE
    )
    assert (
        replay((_replace(first, sequence=0),)).rejection
        is JournalRejection.INVALID_SEQUENCE
    )
    assert (
        replay((_replace(first, sequence="1"),)).rejection
        is JournalRejection.INVALID_SEQUENCE
    )
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
    assert (
        replay((wrong_previous,)).rejection is JournalRejection.PREVIOUS_DIGEST_MISMATCH
    )
    assert replay((field_tamper,)).rejection is JournalRejection.ENTRY_BYTES_TAMPERED
    assert (
        replay((first, _replace(second, digest="sha256:" + "f" * 64))).rejection
        is JournalRejection.ENTRY_BYTES_TAMPERED
    )


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
    assert (
        replay((stored_mismatch,)).rejection is JournalRejection.STORED_RESULT_MISMATCH
    )
    assert (
        replay((first, invalid_as_success)).rejection
        is JournalRejection.INVALID_TRANSITION_REPRESENTED_AS_SUCCESS
    )
    assert (
        replay((valid_as_invalid,)).rejection
        is JournalRejection.VALID_TRANSITION_REPRESENTED_AS_INVALID
    )
    assert (
        replay((first, unknown_invalid_code)).rejection
        is JournalRejection.UNRECOGNISED_INVALID_TRANSITION_CODE
    )
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
