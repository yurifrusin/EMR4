"""
Bernie scenario corpus loader.

Loads YAML scenario fixtures from tests/fixtures/bernie_scenarios/ and
returns typed Scenario dataclasses for the replay harness.

Authorship boundary:
  - Harness demo fixtures (harness_demo_*.yaml): owned by Claude/harness
  - Corpus scenario files: owned by Antigravity (Sprint R1-B)
  - Fixture integrity: owned by DeepSeek (Sprint R1-C)
"""

from __future__ import annotations

import re
from datetime import date, time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

import yaml

KNOWN_ACTIONS = frozenset({
    "normalize",
    "search",
    "select",
    "supervise",
    "confirm",
    "interpret",
    "external_appointment",
})

EXTERNAL_OPERATIONS = frozenset({"create", "set_status"})
EXTERNAL_MAX_DURATION_MINUTES = 480
EXTERNAL_PATIENT_REFS = frozenset(
    {"{patient_id}", "fixture_patient", "Margaret Thompson"}
)
EXTERNAL_PRACTITIONER_REFS = frozenset(
    {"{practitioner_id}", "fixture_practitioner", "Dr Shera"}
)
EXTERNAL_APPOINTMENT_STATUSES = frozenset(
    {
        "Booked",
        "Confirmed",
        "Arrived",
        "InConsult",
        "Completed",
        "Cancelled",
        "NoShow",
        "DNA",
    }
)

EXTERNAL_CREATE_ALLOWED = frozenset({
    "operation", "patient", "practitioner", "date", "time",
    "duration_minutes", "status", "reason", "id",
})

EXTERNAL_SET_STATUS_ALLOWED = frozenset({
    "operation", "appointment_id", "status",
})
KNOWN_FORBIDDEN_OUTCOMES = frozenset({
    "provider_called",
    "appointment_written",
    "audit_written",
})

# Canonical corpus directory (Antigravity and Claude demo fixtures)
CORPUS_DIR = Path(__file__).parent.parent / "fixtures" / "bernie_scenarios"


class NonExecutableScenario(ValueError):
    """Raised when a YAML scenario is corpus memory, not a replay fixture."""


@dataclass
class TurnExpect:
    status: int = 200
    fields: dict[str, Any] = field(default_factory=dict)
    appointment_delta: Optional[int] = None
    audit_delta: Optional[int] = None


@dataclass
class ScenarioTurn:
    action: str
    input: dict[str, Any] = field(default_factory=dict)
    expect: TurnExpect = field(default_factory=TurnExpect)


@dataclass
class ScenarioXFail:
    reason: str


@dataclass
class ScenarioExpected:
    appointment_written: bool = False
    audit_written: bool = False


@dataclass
class Scenario:
    id: str
    category: str
    reference_date: str
    initial_state: dict[str, Any]
    turns: list[ScenarioTurn]
    expected: ScenarioExpected = field(default_factory=ScenarioExpected)
    preserved_fields: list[str] = field(default_factory=list)
    forbidden_outcomes: list[str] = field(default_factory=list)
    xfail: Optional[ScenarioXFail] = None
    source_file: Optional[Path] = None


def _validate_external_appointment_input(
    inp: dict[str, Any], scenario_id: str, idx: int,
) -> None:
    """Validate external_appointment turn input fields."""
    if not isinstance(inp, dict):
        raise ValueError(
            f"Scenario {scenario_id!r} turn {idx}: "
            "external_appointment input must be a mapping"
        )
    operation = inp.get("operation")
    if not operation or operation not in EXTERNAL_OPERATIONS:
        raise ValueError(
            f"Scenario {scenario_id!r} turn {idx}: "
            f"external_appointment 'operation' must be one of "
            f"{sorted(EXTERNAL_OPERATIONS)}; got {operation!r}"
        )

    unknown = set(inp) - (
        EXTERNAL_CREATE_ALLOWED if operation == "create"
        else EXTERNAL_SET_STATUS_ALLOWED
    )
    if unknown:
        raise ValueError(
            f"Scenario {scenario_id!r} turn {idx}: "
            f"external_appointment({operation}) has unsupported "
            f"fields {sorted(unknown)}"
        )

    if operation == "create":
        for required in ("date", "time"):
            if not inp.get(required):
                raise ValueError(
                    f"Scenario {scenario_id!r} turn {idx}: "
                    f"external_appointment(create) '{required}' is required"
                )
        duration = inp.get("duration_minutes", 15)
        if (
            not isinstance(duration, int)
            or isinstance(duration, bool)
            or not 1 <= duration <= EXTERNAL_MAX_DURATION_MINUTES
        ):
            raise ValueError(
                f"Scenario {scenario_id!r} turn {idx}: "
                "external_appointment(create) duration_minutes must be an "
                f"integer from 1 to {EXTERNAL_MAX_DURATION_MINUTES}"
            )
        patient_ref = str(inp.get("patient") or "{patient_id}")
        if patient_ref not in EXTERNAL_PATIENT_REFS:
            raise ValueError(
                f"Scenario {scenario_id!r} turn {idx}: "
                "external_appointment(create) patient must reference the fixture patient"
            )
        practitioner_ref = str(inp.get("practitioner") or "{practitioner_id}")
        if practitioner_ref not in EXTERNAL_PRACTITIONER_REFS:
            raise ValueError(
                f"Scenario {scenario_id!r} turn {idx}: "
                "external_appointment(create) practitioner must reference "
                "the fixture practitioner"
            )
        try:
            date.fromisoformat(str(inp["date"]))
        except (TypeError, ValueError):
            raise ValueError(
                f"Scenario {scenario_id!r} turn {idx}: "
                "external_appointment(create) date must be YYYY-MM-DD"
            ) from None
        try:
            time.fromisoformat(str(inp["time"]))
        except (TypeError, ValueError):
            raise ValueError(
                f"Scenario {scenario_id!r} turn {idx}: "
                "external_appointment(create) time must be a valid local time"
            ) from None
        alias = str(inp.get("id") or "external")
        if not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_-]*", alias):
            raise ValueError(
                f"Scenario {scenario_id!r} turn {idx}: "
                "external_appointment(create) id must be a local alias"
            )
        reason = inp.get("reason")
        if reason is not None and (not isinstance(reason, str) or len(reason) > 500):
            raise ValueError(
                f"Scenario {scenario_id!r} turn {idx}: "
                "external_appointment(create) reason must be at most 500 characters"
            )
    elif operation == "set_status":
        if not inp.get("appointment_id"):
            raise ValueError(
                f"Scenario {scenario_id!r} turn {idx}: "
                "external_appointment(set_status) 'appointment_id' is required"
            )
        if not inp.get("status"):
            raise ValueError(
                f"Scenario {scenario_id!r} turn {idx}: "
                "external_appointment(set_status) 'status' is required"
            )

    status = inp.get("status", "Booked")
    if status not in EXTERNAL_APPOINTMENT_STATUSES:
        raise ValueError(
            f"Scenario {scenario_id!r} turn {idx}: external_appointment status "
            f"must be one of {sorted(EXTERNAL_APPOINTMENT_STATUSES)}"
        )
    appointment_alias = inp.get("appointment_id")
    if appointment_alias is not None and not re.fullmatch(
        r"[a-zA-Z0-9][a-zA-Z0-9_-]*", str(appointment_alias)
    ):
        raise ValueError(
            f"Scenario {scenario_id!r} turn {idx}: "
            "external_appointment appointment_id must be a local alias"
        )


def _parse_turn(raw: dict, idx: int, scenario_id: str) -> ScenarioTurn:
    action = raw.get("action")
    if action is None:
        raise NonExecutableScenario(
            f"Scenario {scenario_id!r} turn {idx}: no executable action"
        )
    if action not in KNOWN_ACTIONS:
        raise ValueError(
            f"Scenario {scenario_id!r} turn {idx}: "
            f"unknown action {action!r}; expected one of {sorted(KNOWN_ACTIONS)}"
        )

    if action == "external_appointment":
        _validate_external_appointment_input(raw.get("input") or {}, scenario_id, idx)

    inp = raw.get("input") or {}
    raw_expect = raw.get("expect") or {}
    for delta_name in ("appointment_delta", "audit_delta"):
        delta = raw_expect.get(delta_name)
        if delta is not None and (not isinstance(delta, int) or isinstance(delta, bool)):
            raise ValueError(
                f"Scenario {scenario_id!r} turn {idx}: "
                f"expect.{delta_name} must be an integer"
            )
    expect = TurnExpect(
        status=int(raw_expect.get("status", 200)),
        fields=raw_expect.get("fields") or {},
        appointment_delta=raw_expect.get("appointment_delta"),
        audit_delta=raw_expect.get("audit_delta"),
    )
    return ScenarioTurn(action=action, input=inp, expect=expect)


def _validate_executable_initial_state(raw: Any, scenario_id: str) -> dict[str, Any]:
    if raw is None:
        return {}
    if not isinstance(raw, dict):
        raise ValueError(f"Scenario {scenario_id!r}: initial_state must be a mapping")

    seeded = raw.get("seeded_appointments") or []
    if not isinstance(seeded, list):
        raise ValueError(
            f"Scenario {scenario_id!r}: initial_state.seeded_appointments must be a list"
        )

    allowed = {
        "id",
        "patient",
        "practitioner",
        "date",
        "time",
        "duration_minutes",
        "status",
        "reason",
    }
    aliases: set[str] = set()
    for index, seed in enumerate(seeded):
        if not isinstance(seed, dict):
            raise ValueError(
                f"Scenario {scenario_id!r}: seeded_appointments[{index}] "
                "must be a mapping"
            )
        unknown = set(seed) - allowed
        if unknown:
            raise ValueError(
                f"Scenario {scenario_id!r}: seeded_appointments[{index}] "
                f"has unsupported fields {sorted(unknown)}"
            )
        for required in ("date", "time"):
            if not seed.get(required):
                raise ValueError(
                    f"Scenario {scenario_id!r}: seeded_appointments[{index}]."
                    f"{required} is required"
                )
        alias = str(seed.get("id") or f"seed-{index}")
        if not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_-]*", alias):
            raise ValueError(
                f"Scenario {scenario_id!r}: seeded appointment id {alias!r} is invalid"
            )
        if alias in aliases:
            raise ValueError(
                f"Scenario {scenario_id!r}: duplicate seeded appointment id {alias!r}"
            )
        aliases.add(alias)

        duration = seed.get("duration_minutes", 15)
        if (
            not isinstance(duration, int)
            or isinstance(duration, bool)
            or not 1 <= duration <= EXTERNAL_MAX_DURATION_MINUTES
        ):
            raise ValueError(
                f"Scenario {scenario_id!r}: seeded_appointments[{index}]."
                f"duration_minutes must be an integer from 1 to {EXTERNAL_MAX_DURATION_MINUTES}"
            )
        patient_ref = str(seed.get("patient") or "{patient_id}")
        if patient_ref not in EXTERNAL_PATIENT_REFS:
            raise ValueError(
                f"Scenario {scenario_id!r}: seeded_appointments[{index}].patient "
                "must reference the fixture patient"
            )
        practitioner_ref = str(seed.get("practitioner") or "{practitioner_id}")
        if practitioner_ref not in EXTERNAL_PRACTITIONER_REFS:
            raise ValueError(
                f"Scenario {scenario_id!r}: seeded_appointments[{index}].practitioner "
                "must reference the fixture practitioner"
            )
        status = seed.get("status", "Booked")
        if status not in EXTERNAL_APPOINTMENT_STATUSES:
            raise ValueError(
                f"Scenario {scenario_id!r}: seeded_appointments[{index}].status "
                f"must be one of {sorted(EXTERNAL_APPOINTMENT_STATUSES)}"
            )
        try:
            date.fromisoformat(str(seed["date"]))
            time.fromisoformat(str(seed["time"]))
        except (TypeError, ValueError):
            raise ValueError(
                f"Scenario {scenario_id!r}: seeded_appointments[{index}] "
                "date/time must be valid local values"
            ) from None
        reason = seed.get("reason")
        if reason is not None and (not isinstance(reason, str) or len(reason) > 500):
            raise ValueError(
                f"Scenario {scenario_id!r}: seeded_appointments[{index}].reason "
                "must be at most 500 characters"
            )

    simulated_time = raw.get("simulated_clinic_time")
    if simulated_time is not None and not re.fullmatch(
        r"\d{2}:\d{2}(?::\d{2})?", str(simulated_time)
    ):
        raise ValueError(
            f"Scenario {scenario_id!r}: simulated_clinic_time must be HH:MM or HH:MM:SS"
        )
    return raw


def load_scenario_yaml(path: Path) -> Scenario:
    """Load and validate a single YAML scenario file."""
    with path.open("r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)
    if not isinstance(raw, dict):
        raise ValueError(f"{path}: expected a YAML mapping at top level")

    _id = raw.get("id")
    if not _id or not isinstance(_id, str):
        raise ValueError(f"{path}: 'id' is required and must be a non-empty string")
    if not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_-]*", _id):
        raise ValueError(
            f"{path}: 'id' must start with alphanumeric and use only "
            f"alphanumerics, hyphens, or underscores; got {_id!r}"
        )

    category = raw.get("category")
    if not category or not isinstance(category, str):
        raise ValueError(f"{path}: 'category' is required; got {category!r}")

    reference_date = raw.get("reference_date")
    if not reference_date:
        raise ValueError(f"{path}: 'reference_date' is required")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(reference_date)):
        raise ValueError(
            f"{path}: 'reference_date' must be YYYY-MM-DD; got {reference_date!r}"
        )

    raw_turns = raw.get("turns")
    if not isinstance(raw_turns, list) or not raw_turns:
        raise ValueError(f"{path}: 'turns' must be a non-empty list")
    turns = [_parse_turn(t, i, _id) for i, t in enumerate(raw_turns)]
    initial_state = _validate_executable_initial_state(raw.get("initial_state"), _id)

    raw_expected = raw.get("expected") or {}
    expected = ScenarioExpected(
        appointment_written=bool(raw_expected.get("appointment_written", False)),
        audit_written=bool(raw_expected.get("audit_written", False)),
    )

    preserved_fields = list(raw.get("preserved_fields") or [])

    raw_forbidden = list(raw.get("forbidden_outcomes") or [])
    for outcome in raw_forbidden:
        if outcome not in KNOWN_FORBIDDEN_OUTCOMES:
            raise ValueError(
                f"{path}: unknown forbidden_outcome {outcome!r}; "
                f"expected one of {sorted(KNOWN_FORBIDDEN_OUTCOMES)}"
            )

    raw_xfail = raw.get("xfail")
    xfail = None
    if raw_xfail is not None:
        reason = (raw_xfail.get("reason") or "").strip()
        if not reason:
            raise ValueError(f"{path}: 'xfail.reason' is required when 'xfail' is set")
        xfail = ScenarioXFail(reason=reason)

    return Scenario(
        id=_id,
        category=category,
        reference_date=str(reference_date),
        initial_state=initial_state,
        turns=turns,
        expected=expected,
        preserved_fields=preserved_fields,
        forbidden_outcomes=raw_forbidden,
        xfail=xfail,
        source_file=path,
    )


def discover_scenarios(dirs: list[Path] | None = None) -> list[Scenario]:
    """Discover all YAML scenario files from the given directories.

    Tolerates missing directories so corpus and harness lanes integrate
    independently. Raises ValueError on duplicate scenario ids.
    """
    if dirs is None:
        dirs = [CORPUS_DIR]
    scenarios: list[Scenario] = []
    seen_ids: set[str] = set()
    for d in dirs:
        if not d.is_dir():
            continue
        for path in sorted(d.glob("*.yaml")):
            try:
                s = load_scenario_yaml(path)
            except NonExecutableScenario:
                continue
            if s.id in seen_ids:
                raise ValueError(
                    f"Duplicate scenario id {s.id!r}: found again in {path}"
                )
            seen_ids.add(s.id)
            scenarios.append(s)
    return scenarios
