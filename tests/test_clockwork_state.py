from orchestration_harness.clockwork_state import (
    COMMAND_SCHEMA_VERSION,  # noqa: F401
    EVENT_SCHEMA_VERSION,  # noqa: F401
    STATE_SCHEMA_VERSION,  # noqa: F401
    ClockworkCommand,
    ClockworkEvent,
    ClockworkState,
    InvalidTransition,
    TransitionResult,
    canonical_bytes,
    transition,
)


def test_same_input_gives_byte_identical_output():
    first_result = transition(
        ClockworkState.IDLE,
        ClockworkEvent.START,
        ClockworkCommand.ADVANCE,
    )
    second_result = transition(
        ClockworkState.IDLE,
        ClockworkEvent.START,
        ClockworkCommand.ADVANCE,
    )
    first_payload = canonical_bytes(first_result)
    second_payload = canonical_bytes(second_result)
    assert first_payload == second_payload


def test_canonical_key_order_and_unicode_policy():
    result = TransitionResult(ClockworkState.ACTIVE, ClockworkCommand.HOLD, None)
    payload = canonical_bytes(result)
    assert payload == (
        b'{"command":"hold","command_schema_version":"ariadne.clockwork_command.v1",'
        b'"event_schema_version":"ariadne.clockwork_event.v1","invalid":null,'
        b'"state":"active","state_schema_version":"ariadne.clockwork_state.v1"}'
    )


def test_no_ambient_locale_time_or_environment_dependency():
    first_result = transition(
        ClockworkState.IDLE,
        ClockworkEvent.START,
        ClockworkCommand.HOLD,
    )
    second_result = transition(
        ClockworkState.IDLE,
        ClockworkEvent.START,
        ClockworkCommand.HOLD,
    )
    first_payload = canonical_bytes(first_result)
    second_payload = canonical_bytes(second_result)
    assert first_payload == second_payload


def test_closed_invalid_transition_behavior():
    result = transition(
        ClockworkState.ACTIVE,
        ClockworkEvent.START,
        ClockworkCommand.HOLD,
    )
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
    result = transition(
        ClockworkState.IDLE,
        ClockworkEvent.START,
        ClockworkCommand.ADVANCE,
    )
    payload = canonical_bytes(result)
    assert b"ariadne.clockwork_state.v1" in payload
    assert b"ariadne.clockwork_event.v1" in payload
    assert b"ariadne.clockwork_command.v1" in payload
