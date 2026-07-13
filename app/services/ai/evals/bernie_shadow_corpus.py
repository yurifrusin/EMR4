"""Strict loader for authored-synthetic T1/T2 Bernie shadow cases."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Collection

from app.services.ai.evals.bernie_shadow_eval import ExpectedDecision, ShadowCase


SCHEMA_VERSION = "bernie.shadow_corpus.v1"
_TOP_LEVEL_KEYS = frozenset({"schema_version", "source", "cases"})
_CASE_KEYS = frozenset(
    {"id", "source_scenario_id", "instruction", "expected", "allowed_tools"}
)
_EXPECTED_KEYS = frozenset(
    {"authorship", "intent", "entities", "date_time", "requires_clarification", "tool_name"}
)
_ENTITY_KEYS = frozenset({"patient_ref", "practitioner_ref", "appointment_ref"})
_DATE_TIME_KEYS = frozenset(
    {"date", "date_from", "date_to", "day_offset", "earliest_time", "latest_time", "duration_minutes", "time_band"}
)
_ALLOWED_TOOLS = frozenset({"search_available_slots", "explain_schedule"})


def _require_exact_keys(value: dict[str, Any], allowed: frozenset[str], label: str) -> None:
    unknown = set(value) - allowed
    if unknown:
        raise ValueError(f"{label} contains unsupported fields: {sorted(unknown)}")


def _parse_pairs(
    raw: Any,
    *,
    allowed_keys: frozenset[str],
    label: str,
    require_synthetic_values: bool,
) -> tuple[tuple[str, str], ...]:
    if not isinstance(raw, dict):
        raise ValueError(f"{label} must be an object")
    unknown = set(raw) - allowed_keys
    if unknown:
        raise ValueError(f"{label} contains unsupported fields: {sorted(unknown)}")

    pairs: list[tuple[str, str]] = []
    for key, value in raw.items():
        if not isinstance(value, (str, int)) or isinstance(value, bool):
            raise ValueError(f"{label}.{key} must be a string or integer")
        text = str(value).strip()
        if not text:
            raise ValueError(f"{label}.{key} must be non-empty")
        if require_synthetic_values and not text.startswith("synthetic-"):
            raise ValueError(f"{label}.{key} must use a synthetic- alias")
        pairs.append((key, text))
    return tuple(pairs)


def load_shadow_corpus(
    path: str | Path,
    *,
    known_source_ids: Collection[str],
) -> tuple[ShadowCase, ...]:
    """Load a strictly allowlisted authored projection of known T1/T2 cases."""

    corpus_path = Path(path)
    try:
        raw = json.loads(corpus_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Unable to load shadow corpus: {exc}") from exc
    if not isinstance(raw, dict):
        raise ValueError("shadow corpus root must be an object")
    _require_exact_keys(raw, _TOP_LEVEL_KEYS, "shadow corpus")
    if raw.get("schema_version") != SCHEMA_VERSION:
        raise ValueError(f"schema_version must be {SCHEMA_VERSION}")
    if raw.get("source") != "authored_synthetic":
        raise ValueError("shadow corpus source must be authored_synthetic")

    raw_cases = raw.get("cases")
    if not isinstance(raw_cases, list) or not raw_cases:
        raise ValueError("shadow corpus cases must be a non-empty array")

    known = set(known_source_ids)
    seen_ids: set[str] = set()
    cases: list[ShadowCase] = []
    for index, raw_case in enumerate(raw_cases):
        label = f"cases[{index}]"
        if not isinstance(raw_case, dict):
            raise ValueError(f"{label} must be an object")
        _require_exact_keys(raw_case, _CASE_KEYS, label)

        case_id = raw_case.get("id")
        source_id = raw_case.get("source_scenario_id")
        instruction = raw_case.get("instruction")
        if not isinstance(case_id, str) or not case_id.strip():
            raise ValueError(f"{label}.id must be a non-empty string")
        if case_id in seen_ids:
            raise ValueError(f"duplicate shadow case id: {case_id}")
        seen_ids.add(case_id)
        if not isinstance(source_id, str) or source_id not in known:
            raise ValueError(f"{label}.source_scenario_id is not a known T1/T2 case")
        if not isinstance(instruction, str) or not instruction.strip():
            raise ValueError(f"{label}.instruction must be a non-empty string")

        expected = raw_case.get("expected")
        if not isinstance(expected, dict):
            raise ValueError(f"{label}.expected must be an object")
        _require_exact_keys(expected, _EXPECTED_KEYS, f"{label}.expected")
        if expected.get("authorship") != "manual":
            raise ValueError(f"{label}.expected.authorship must be manual")

        allowed_tools = raw_case.get("allowed_tools")
        if not isinstance(allowed_tools, list) or not all(
            isinstance(tool, str) and tool in _ALLOWED_TOOLS for tool in allowed_tools
        ):
            raise ValueError(f"{label}.allowed_tools contains an unsupported tool")
        if len(allowed_tools) != len(set(allowed_tools)):
            raise ValueError(f"{label}.allowed_tools contains duplicates")

        intent = expected.get("intent")
        tool_name = expected.get("tool_name")
        clarification = expected.get("requires_clarification")
        if intent is not None and not isinstance(intent, str):
            raise ValueError(f"{label}.expected.intent must be a string or null")
        if tool_name is not None and not isinstance(tool_name, str):
            raise ValueError(f"{label}.expected.tool_name must be a string or null")
        if not isinstance(clarification, bool):
            raise ValueError(f"{label}.expected.requires_clarification must be boolean")

        decision = ExpectedDecision(
            intent=intent,
            entities=_parse_pairs(
                expected.get("entities"),
                allowed_keys=_ENTITY_KEYS,
                label=f"{label}.expected.entities",
                require_synthetic_values=True,
            ),
            date_time=_parse_pairs(
                expected.get("date_time"),
                allowed_keys=_DATE_TIME_KEYS,
                label=f"{label}.expected.date_time",
                require_synthetic_values=False,
            ),
            requires_clarification=clarification,
            tool_name=tool_name,
        )
        cases.append(
            ShadowCase(
                case_id=case_id,
                source=f"authored_synthetic:t1_t2:{source_id}",
                instruction=instruction,
                expected=decision,
                allowed_tools=tuple(allowed_tools),
            )
        )
    return tuple(cases)


__all__ = ["SCHEMA_VERSION", "load_shadow_corpus"]
