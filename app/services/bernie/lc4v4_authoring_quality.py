"""Independent, content-blind authoring-quality gate for LC4V4.

The gate validates authored semantic facts and rendered evidence before a
certification corpus may be sealed.  It deliberately does not import or call
the production interpreter, replay, scorer, providers, routes, storage, or any
holdout implementation.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict, dataclass
from typing import Any, Literal, Mapping, Sequence


AUTHORING_RECEIPT_SCHEMA = "lc4v4.authoring_quality_receipt.v1"
REQUIRED_RECEIPT_CATEGORIES = frozenset({
    "turn_index_population",
    "rendered_text_composition",
    "canonical_core_preservation",
    "language_form_vocabulary",
    "authority_token_duplicate",
    "authority_span_range",
    "authority_token_inside_core",
    "authority_token_value",
    "source_span_value",
    "authority_span_overlap",
    "required_authority_evidence",
    "entity_relation_evidence",
    "policy_derivation",
    "scenario_population",
    "scenario_identity",
    "distinct_coverage_cells",
    "category_completeness",
})
REQUIRED_CATEGORY_MIN_TOTALS: dict[str, int] = {
    "turn_index_population": 288,
    "rendered_text_composition": 360,
    "canonical_core_preservation": 360,
    "language_form_vocabulary": 360,
    "authority_token_duplicate": 288,
    "authority_span_range": 288,
    "authority_token_inside_core": 288,
    "authority_token_value": 288,
    "source_span_value": 288,
    "authority_span_overlap": 288,
    "required_authority_evidence": 288,
    "entity_relation_evidence": 1440,
    "policy_derivation": 3744,
    "scenario_population": 1,
    "scenario_identity": 1,
    "distinct_coverage_cells": 1,
    "category_completeness": 7,
}

EntityRelation = Literal[
    "exact", "corrected", "omitted", "ambiguous", "negated", "mismatched"
]


@dataclass(frozen=True)
class AuthorityToken:
    """One authority-bearing token at exact coordinates in a rendered turn."""

    field_name: str
    canonical_text: str
    case_sensitive: bool
    turn_index: int
    source_start: int
    source_end: int
    source_text: str


@dataclass(frozen=True)
class RenderedTurn:
    """A rendered turn with independent canonical and rendered core values."""

    turn_index: int
    prefix: str
    canonical_core: str
    rendered_core: str
    suffix: str
    rendered_text: str
    language_form: str


@dataclass(frozen=True)
class CanonicalFactBundle:
    """Adjudicated semantic facts, never a production-parser observation."""

    scenario_id: str
    intended_action: str
    action_semantics: str
    temporal_relation: str
    normalized_values: dict[str, Any]
    entity_relations: dict[str, EntityRelation]
    requires_clarification: bool
    clarification_choices: tuple[str, ...]
    action_negated: bool
    diary_state: str


@dataclass(frozen=True)
class ExpectedScenarioContract:
    """Expected contract independently derived from canonical facts."""

    intended_action: str
    action_semantics: str
    temporal_relation: str
    normalized_values: dict[str, Any]
    entity_relations: dict[str, EntityRelation]
    requires_clarification: bool
    clarification_choices: tuple[str, ...]
    expected_tool_sequence: tuple[str, ...]
    expected_outcome_kind: str | None
    expected_authority: str
    expected_appointment_deltas: tuple[dict[str, Any], ...]
    expected_audit_deltas: tuple[dict[str, Any], ...]
    diary_state: str


@dataclass(frozen=True)
class AuthoringQualityFinding:
    """Internal pre-receipt finding. Detail is never emitted in the receipt."""

    category: str
    passed: bool
    detail: str = ""


@dataclass(frozen=True)
class AuthoringQualityReceipt:
    """Aggregate-only, hash-bound authoring-quality receipt."""

    schema_version: str
    total_checks: int
    passed_checks: int
    failed_checks: int
    total_surfaces_validated: int
    surfaces_passed: int
    surfaces_failed: int
    distinct_coverage_cells: int
    category_totals: dict[str, dict[str, int]]
    all_passed: bool
    receipt_hash: str


_ACTIONS = {
    "create", "move", "resize", "cancel", "status_change", "explain_schedule"
}
_DIARY_STATES = {
    "empty", "exact_duplicate", "overlap", "same_day_distinct", "terminal",
    "stale", "concurrent", "roster_absent", "break", "no_slots",
    "elapsed_window",
}
_ENTITY_RELATIONS = {
    "exact", "corrected", "omitted", "ambiguous", "negated", "mismatched"
}
_TEMPORAL_RELATIONS = {
    "exact", "not_before", "not_after", "interval", "approximate", "unspecified"
}
_DIALOGUE_FORMS = {
    "one_shot", "clarification", "correction", "reversal", "ellipsis",
    "anaphora", "repeated", "session_restart",
}
_LANGUAGE_FORMS = {
    "plain", "paraphrase", "filler", "abbreviation", "typo", "speech_like",
    "punctuation_variant", "adversarial",
}
_ENTITY_FIELDS = {
    "patient", "practitioner", "location", "appointment_type", "duration"
}

LATTICE_VOCABULARIES: dict[str, set[str]] = {
    "intended_action": _ACTIONS,
    "diary_state": _DIARY_STATES,
    "entity_state": _ENTITY_RELATIONS,
    "temporal_relation": _TEMPORAL_RELATIONS,
    "dialogue_form": _DIALOGUE_FORMS,
    "language_form": _LANGUAGE_FORMS,
    "trajectory_type": {"single_turn", "trajectory"},
}


def _patient_resolved(facts: CanonicalFactBundle) -> bool:
    return facts.entity_relations.get("patient") in {"exact", "corrected"}


def _has_time_bounds(facts: CanonicalFactBundle) -> bool:
    return bool(
        facts.normalized_values.get("earliest_time") is not None
        or facts.normalized_values.get("latest_time") is not None
    )


def _derive_outcome(facts: CanonicalFactBundle) -> str | None:
    if facts.action_negated:
        return None
    if facts.action_semantics == "prohibited":
        return "instruction_refused"
    if facts.requires_clarification or facts.action_semantics == "ambiguous":
        return "clarification_required"
    if facts.intended_action == "explain_schedule":
        return "schedule_explained"
    if facts.intended_action == "create":
        if facts.diary_state in {"empty", "same_day_distinct", "terminal"}:
            return "appointment_created"
        if facts.diary_state == "exact_duplicate":
            return "existing_booking_found"
        if facts.diary_state == "overlap":
            return "candidate_selection_required"
        return None
    if facts.diary_state in {
        "terminal", "stale", "concurrent", "no_slots", "roster_absent",
        "break", "elapsed_window",
    }:
        return None
    return {
        "move": "appointment_moved",
        "resize": "appointment_resized",
        "cancel": "appointment_cancelled",
        "status_change": "appointment_status_changed",
    }.get(facts.intended_action)


def _derive_tools(facts: CanonicalFactBundle) -> tuple[str, ...]:
    patient = _patient_resolved(facts)
    if facts.action_negated:
        return ("search_patients",) if patient else ()
    if facts.action_semantics == "prohibited":
        tools: list[str] = ["search_patients"] if patient else []
        if facts.intended_action == "create" and _has_time_bounds(facts):
            tools.extend(["find_slots", "create_booking"])
        tools.append("refuse_instruction")
        return tuple(tools)
    if facts.requires_clarification or facts.action_semantics == "ambiguous":
        return ("request_clarification",)
    tools = ["search_patients"] if patient else []
    action_tool = {
        "create": ("find_slots", "create_booking"),
        "move": ("update_appointment",),
        "resize": ("update_appointment",),
        "cancel": ("update_appointment",),
        "status_change": ("change_appointment_status",),
        "explain_schedule": ("find_slots",),
    }.get(facts.intended_action, ())
    tools.extend(action_tool)
    return tuple(tools)


def _derive_authority(facts: CanonicalFactBundle) -> str:
    if facts.action_semantics == "prohibited":
        return "refuse"
    if facts.requires_clarification or facts.action_semantics == "ambiguous":
        return "clarify"
    return "read"


def _derive_deltas(
    facts: CanonicalFactBundle, outcome: str | None,
) -> tuple[tuple[dict[str, Any], ...], tuple[dict[str, Any], ...]]:
    change_type = {
        "appointment_created": "created",
        "existing_booking_found": "created",
        "appointment_moved": "moved",
        "appointment_resized": "resized",
        "appointment_cancelled": "cancelled",
        "appointment_status_changed": "status_changed",
    }.get(outcome)
    if change_type is None or facts.action_negated:
        return (), ()
    values = facts.normalized_values
    appointment = {
        "appointment_id": "apt-001",
        "change_type": change_type,
        "patient_id": "p-001",
        "practitioner_id": "pr-001",
        "date": values.get("appointment_date", ""),
        "start_time": values.get("earliest_time", ""),
        "duration_minutes": values.get("duration_minutes", 15),
    }
    audit = {
        "change_type": change_type,
        "appointment_id": "apt-001",
        "count": 1,
    }
    return (appointment,), (audit,)


def derive_expected_contract(facts: CanonicalFactBundle) -> ExpectedScenarioContract:
    """Derive the complete expected contract from canonical facts only."""
    if facts.intended_action not in _ACTIONS:
        raise ValueError("unknown canonical action")
    if facts.diary_state not in _DIARY_STATES:
        raise ValueError("unknown canonical diary state")
    if facts.temporal_relation not in _TEMPORAL_RELATIONS:
        raise ValueError("unknown canonical temporal relation")
    if set(facts.entity_relations) != _ENTITY_FIELDS:
        raise ValueError("canonical entity relation population drift")
    if not set(facts.entity_relations.values()) <= _ENTITY_RELATIONS:
        raise ValueError("unknown canonical entity relation")
    outcome = _derive_outcome(facts)
    appointment, audit = _derive_deltas(facts, outcome)
    return ExpectedScenarioContract(
        intended_action=facts.intended_action,
        action_semantics=facts.action_semantics,
        temporal_relation=facts.temporal_relation,
        normalized_values=dict(facts.normalized_values),
        entity_relations=dict(facts.entity_relations),
        requires_clarification=facts.requires_clarification,
        clarification_choices=tuple(facts.clarification_choices),
        expected_tool_sequence=_derive_tools(facts),
        expected_outcome_kind=outcome,
        expected_authority=_derive_authority(facts),
        expected_appointment_deltas=appointment,
        expected_audit_deltas=audit,
        diary_state=facts.diary_state,
    )


def _finding(category: str, passed: bool, detail: str = "") -> AuthoringQualityFinding:
    return AuthoringQualityFinding(category=category, passed=passed, detail=detail)


def validate_rendered_surface(
    turns: Sequence[RenderedTurn],
    tokens: Sequence[AuthorityToken],
    *,
    required_field_counts: Mapping[str, tuple[int, int]] | None = None,
) -> list[AuthoringQualityFinding]:
    """Validate independent rendering, core preservation, and source evidence."""
    findings: list[AuthoringQualityFinding] = []
    required_field_counts = required_field_counts or {}
    turn_map = {turn.turn_index: turn for turn in turns}
    findings.append(_finding(
        "turn_index_population",
        len(turn_map) == len(turns) and set(turn_map) == set(range(len(turns))),
        "turn indexes must be unique and contiguous",
    ))
    for turn in turns:
        findings.append(_finding(
            "rendered_text_composition",
            turn.rendered_text == turn.prefix + turn.rendered_core + turn.suffix,
            "rendered text must equal prefix + rendered core + suffix",
        ))
        findings.append(_finding(
            "canonical_core_preservation",
            turn.rendered_core == turn.canonical_core,
            "style rendering must preserve the canonical core byte-for-byte",
        ))
        findings.append(_finding(
            "language_form_vocabulary",
            turn.language_form in _LANGUAGE_FORMS,
            "unknown language form",
        ))

    field_tokens: dict[str, list[AuthorityToken]] = {}
    turn_tokens: dict[int, list[AuthorityToken]] = {}
    seen_token_identity: set[tuple[Any, ...]] = set()
    for token in tokens:
        field_tokens.setdefault(token.field_name, []).append(token)
        turn_tokens.setdefault(token.turn_index, []).append(token)
        identity = (
            token.field_name, token.turn_index, token.source_start,
            token.source_end, token.canonical_text,
        )
        duplicate = identity in seen_token_identity
        seen_token_identity.add(identity)
        findings.append(_finding("authority_token_duplicate", not duplicate, "duplicate token"))
        turn = turn_map.get(token.turn_index)
        if turn is None:
            findings.append(_finding("authority_turn_missing", False, "token references missing turn"))
            continue
        valid_range = (
            0 <= token.source_start < token.source_end <= len(turn.rendered_text)
        )
        findings.append(_finding("authority_span_range", valid_range, "invalid token coordinates"))
        if not valid_range:
            continue
        core_start = len(turn.prefix)
        core_end = core_start + len(turn.rendered_core)
        findings.append(_finding(
            "authority_token_inside_core",
            core_start <= token.source_start and token.source_end <= core_end,
            "authority token must remain inside the preserved core",
        ))
        actual = turn.rendered_text[token.source_start:token.source_end]
        matches = (
            actual == token.canonical_text
            if token.case_sensitive
            else actual.casefold() == token.canonical_text.casefold()
        )
        findings.append(_finding("authority_token_value", matches, "authority token mismatch"))
        findings.append(_finding(
            "source_span_value", actual == token.source_text, "source span text mismatch"
        ))

    for turn_index, positioned in turn_tokens.items():
        ordered = sorted(positioned, key=lambda item: (item.source_start, item.source_end))
        overlap = any(
            current.source_start < previous.source_end
            for previous, current in zip(ordered, ordered[1:])
        )
        findings.append(_finding(
            "authority_span_overlap", not overlap, f"overlap in turn {turn_index}"
        ))

    for field_name, (minimum, maximum) in required_field_counts.items():
        count = len(field_tokens.get(field_name, []))
        findings.append(_finding(
            "required_authority_evidence",
            minimum <= count <= maximum,
            f"field {field_name} count outside frozen bounds",
        ))
    return findings


def validate_entity_relation_evidence(
    entity_relations: Mapping[str, EntityRelation],
    tokens: Sequence[AuthorityToken],
) -> list[AuthoringQualityFinding]:
    """Require evidence shapes appropriate to each explicit entity relation."""
    findings: list[AuthoringQualityFinding] = []
    if set(entity_relations) != _ENTITY_FIELDS:
        return [_finding("entity_relation_population", False, "entity field population drift")]
    by_field: dict[str, list[AuthorityToken]] = {}
    for token in tokens:
        by_field.setdefault(token.field_name, []).append(token)
    for field_name, relation in entity_relations.items():
        evidence = by_field.get(field_name, [])
        if relation == "omitted":
            passed = not evidence
        elif relation == "exact":
            passed = len(evidence) == 1 and evidence[0].case_sensitive
        elif relation == "corrected":
            passed = (
                len(evidence) >= 2
                and all(token.case_sensitive for token in evidence)
                and len({token.canonical_text for token in evidence}) >= 2
            )
        else:
            # Ambiguous, negated, and mismatched are explicit relations and
            # therefore require surface relation evidence, not silent absence.
            passed = len(evidence) >= 1
        findings.append(_finding(
            "entity_relation_evidence", passed, f"invalid evidence for {field_name}:{relation}"
        ))
    return findings


def validate_expected_contract_derivation(
    facts: CanonicalFactBundle,
    expected: ExpectedScenarioContract,
) -> list[AuthoringQualityFinding]:
    """Compare every expected field with a fresh independent derivation."""
    derived = derive_expected_contract(facts)
    expected_map = asdict(expected)
    derived_map = asdict(derived)
    return [
        _finding(
            "policy_derivation",
            expected_map[field_name] == derived_map[field_name],
            f"derived field drift: {field_name}",
        )
        for field_name in sorted(derived_map)
    ]


def validate_lattice_coverage(
    cells: Sequence[Mapping[str, str]],
    *,
    expected_scenarios: int = 288,
    minimum_distinct_cells: int = 240,
) -> list[AuthoringQualityFinding]:
    """Validate population, category completeness, IDs, and distinct cells."""
    findings: list[AuthoringQualityFinding] = []
    findings.append(_finding(
        "scenario_population", len(cells) == expected_scenarios, "scenario population drift"
    ))
    ids = [cell.get("scenario_id", "") for cell in cells]
    findings.append(_finding(
        "scenario_identity", all(ids) and len(ids) == len(set(ids)), "duplicate or empty IDs"
    ))
    dimensions = tuple(name for name in LATTICE_VOCABULARIES if name != "trajectory_type")
    distinct = {
        tuple(cell.get(dimension, "") for dimension in dimensions)
        for cell in cells
    }
    findings.append(_finding(
        "distinct_coverage_cells",
        len(distinct) >= minimum_distinct_cells,
        "insufficient distinct lattice coverage",
    ))
    for dimension, vocabulary in LATTICE_VOCABULARIES.items():
        observed = {cell.get(dimension, "") for cell in cells}
        findings.append(_finding(
            "category_completeness",
            observed == vocabulary,
            f"category drift: {dimension}",
        ))
    return findings


def _normalize_json_value(value: Any) -> Any:
    if isinstance(value, str):
        return value.replace("\r\n", "\n").replace("\r", "\n")
    if isinstance(value, dict):
        return {key: _normalize_json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_normalize_json_value(item) for item in value]
    return value


def canonical_json_bytes(value: Any) -> bytes:
    """Return sorted, compact UTF-8 JSON bytes with platform-neutral LF."""
    if hasattr(value, "__dataclass_fields__"):
        value = asdict(value)
    text = json.dumps(
        _normalize_json_value(value),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )
    return (text + "\n").encode("utf-8")


def stable_hash(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_json_bytes(value)).hexdigest()


_SAFE_CATEGORY_RE = re.compile(r"^[a-z][a-z0-9_]{0,63}$")


def _receipt_payload(receipt: AuthoringQualityReceipt) -> dict[str, Any]:
    payload = asdict(receipt)
    payload.pop("receipt_hash", None)
    return payload


def build_authoring_receipt(
    findings: Sequence[AuthoringQualityFinding],
    *,
    total_surfaces: int,
    surfaces_passed: int,
    surfaces_failed: int,
    distinct_coverage_cells: int,
) -> AuthoringQualityReceipt:
    """Collapse internal findings into category totals with no case details."""
    if surfaces_passed + surfaces_failed != total_surfaces:
        raise ValueError("surface receipt totals do not reconcile")
    categories: dict[str, dict[str, int]] = {}
    for finding in findings:
        if not _SAFE_CATEGORY_RE.fullmatch(finding.category):
            raise ValueError("unsafe authoring receipt category")
        bucket = categories.setdefault(finding.category, {"passed": 0, "failed": 0, "total": 0})
        bucket["total"] += 1
        bucket["passed" if finding.passed else "failed"] += 1
    passed = sum(1 for finding in findings if finding.passed)
    failed = len(findings) - passed
    partial = AuthoringQualityReceipt(
        schema_version=AUTHORING_RECEIPT_SCHEMA,
        total_checks=len(findings),
        passed_checks=passed,
        failed_checks=failed,
        total_surfaces_validated=total_surfaces,
        surfaces_passed=surfaces_passed,
        surfaces_failed=surfaces_failed,
        distinct_coverage_cells=distinct_coverage_cells,
        category_totals=dict(sorted(categories.items())),
        all_passed=(failed == 0 and surfaces_failed == 0),
        receipt_hash="",
    )
    return AuthoringQualityReceipt(
        **_receipt_payload(partial),
        receipt_hash=stable_hash(_receipt_payload(partial)),
    )


def authoring_receipt_to_dict(receipt: AuthoringQualityReceipt) -> dict[str, Any]:
    return asdict(receipt)


def validate_authoring_receipt(
    value: Mapping[str, Any],
    *,
    expected_surfaces: int = 288,
    minimum_coverage: int = 240,
) -> dict[str, Any]:
    """Fail closed unless an aggregate receipt proves a complete clean gate."""
    expected_keys = set(AuthoringQualityReceipt.__dataclass_fields__)
    if set(value) != expected_keys:
        raise ValueError("authoring receipt schema drift")
    receipt = AuthoringQualityReceipt(**dict(value))
    if receipt.schema_version != AUTHORING_RECEIPT_SCHEMA:
        raise ValueError("authoring receipt version drift")
    if receipt.total_surfaces_validated != expected_surfaces:
        raise ValueError("authoring receipt surface population drift")
    if receipt.surfaces_passed != expected_surfaces or receipt.surfaces_failed != 0:
        raise ValueError("authoring receipt contains failed surfaces")
    if receipt.distinct_coverage_cells < minimum_coverage:
        raise ValueError("authoring receipt coverage below threshold")
    if (
        receipt.total_checks <= 0
        or receipt.passed_checks != receipt.total_checks
        or receipt.failed_checks != 0
        or not receipt.all_passed
    ):
        raise ValueError("authoring receipt did not pass completely")
    if not receipt.category_totals:
        raise ValueError("authoring receipt categories missing")
    if not REQUIRED_RECEIPT_CATEGORIES <= set(receipt.category_totals):
        raise ValueError("authoring receipt required categories missing")
    for category, totals in receipt.category_totals.items():
        if not _SAFE_CATEGORY_RE.fullmatch(category):
            raise ValueError("unsafe authoring receipt category")
        if set(totals) != {"passed", "failed", "total"}:
            raise ValueError("authoring receipt category schema drift")
        if totals["passed"] + totals["failed"] != totals["total"] or totals["failed"]:
            raise ValueError("authoring receipt category contains failure")
        if not all(type(totals[key]) is int and totals[key] >= 0 for key in totals):
            raise ValueError("authoring receipt category totals must be non-negative integers")
    for category, minimum in REQUIRED_CATEGORY_MIN_TOTALS.items():
        if receipt.category_totals[category]["total"] < minimum:
            raise ValueError(f"authoring receipt category under-count: {category}")
    payload = dict(value)
    claimed = payload.pop("receipt_hash")
    if claimed != stable_hash(payload):
        raise ValueError("authoring receipt hash mismatch")
    return dict(value)


def validate_lc4v4_authoring_quality_isolation() -> None:
    """Prove the quality gate has no application/runtime dependency."""
    import ast
    import pathlib

    tree = ast.parse(pathlib.Path(__file__).read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module and node.module.startswith("app"):
            raise RuntimeError(f"authoring quality imports application module: {node.module}")
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith("app"):
                    raise RuntimeError(f"authoring quality imports application module: {alias.name}")


__all__ = [
    "AUTHORING_RECEIPT_SCHEMA", "REQUIRED_RECEIPT_CATEGORIES",
    "REQUIRED_CATEGORY_MIN_TOTALS", "AuthorityToken", "AuthoringQualityFinding",
    "AuthoringQualityReceipt", "CanonicalFactBundle", "EntityRelation",
    "ExpectedScenarioContract", "LATTICE_VOCABULARIES", "RenderedTurn",
    "authoring_receipt_to_dict", "build_authoring_receipt",
    "canonical_json_bytes", "derive_expected_contract", "stable_hash",
    "validate_authoring_receipt", "validate_entity_relation_evidence",
    "validate_expected_contract_derivation", "validate_lattice_coverage",
    "validate_lc4v4_authoring_quality_isolation", "validate_rendered_surface",
]
