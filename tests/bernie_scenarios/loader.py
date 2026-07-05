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
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

import yaml

KNOWN_ACTIONS = frozenset({"normalize", "search", "select", "confirm"})
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
    inp = raw.get("input") or {}
    raw_expect = raw.get("expect") or {}
    expect = TurnExpect(
        status=int(raw_expect.get("status", 200)),
        fields=raw_expect.get("fields") or {},
    )
    return ScenarioTurn(action=action, input=inp, expect=expect)


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

    initial_state = raw.get("initial_state") or {}

    raw_turns = raw.get("turns")
    if not isinstance(raw_turns, list) or not raw_turns:
        raise ValueError(f"{path}: 'turns' must be a non-empty list")
    turns = [_parse_turn(t, i, _id) for i, t in enumerate(raw_turns)]

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
