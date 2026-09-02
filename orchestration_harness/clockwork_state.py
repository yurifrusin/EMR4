from dataclasses import dataclass as _dataclass
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
