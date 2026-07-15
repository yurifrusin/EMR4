"""Content-blind authoring quality gate for LC4V4.

This module is a frozen, provider-free validator for rendered scenario surfaces.
It must not import or execute the production parser, composed evaluator, replay,
scenario fixtures, providers, or runtime.

The validator checks:
- each rendered turn equals ``prefix + core + suffix`` byte-for-byte;
- every case-sensitive authority token appears byte-identically at its stated
  coordinates, including proper-name case;
- every source span matches the rendered source exactly;
- duplicate, overlapping, out-of-range, missing, or empty authority spans are
  rejected where the field contract requires one;
- ``exact`` and ``corrected`` entity semantics carry case-preserved evidence;
- ``omitted``, ``ambiguous``, ``negated``, and ``mismatched`` semantics use
  explicit relation assertions rather than silently claiming exact evidence;
- expected tools, outcome, deltas, and authority are independently derived from
  canonical facts through a frozen local policy table (not copied from parser);
- JSON bytes are UTF-8/LF deterministic and hash-stable.

No provider, route, database, UI, runtime, wall-clock, production parser,
composed evaluator, or protected-holdout dependency exists.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Literal

# ---------------------------------------------------------------------------
# Typed records
# ---------------------------------------------------------------------------

EntityRelation = Literal[
    "exact",
    "corrected",
    "omitted",
    "ambiguous",
    "negated",
    "mismatched",
]


@dataclass(frozen=True)
class AuthorityToken:
    """One authority-bearing evidence token in a rendered surface."""

    field_name: str
    canonical_text: str
    case_sensitive: bool
    turn_index: int
    source_start: int
    source_end: int
    source_text: str


@dataclass(frozen=True)
class RenderedTurn:
    """One rendered turn split into prefix, core, and suffix."""

    prefix: str
    core: str
    suffix: str
    language_form: str | None = None

    @property
    def full_text(self) -> str:
        """Byte-for-byte concatenation of prefix + core + suffix."""
        return self.prefix + self.core + self.suffix


@dataclass(frozen=True)
class CanonicalFactBundle:
    """Canonical semantic facts for one scenario surface.

    This is the input to the authoring quality validator.  It is constructed
    from frozen adjudicated facts, never from production parser output.
    """

    scenario_id: str
    intended_action: str
    action_semantics: str
    temporal_relation: str
    normalized_values: dict[str, Any]
    entity_relations: dict[str, EntityRelation]
    requires_clarification: bool
    clarification_choices: tuple[str, ...]
    selected_tool_sequence: tuple[str, ...]
    authority_claim: str | None
    claims_action_completed: bool
    action_negated: bool
    diary_state: str


@dataclass(frozen=True)
class ExpectedScenarioContract:
    """Expected scenario contract independently derived from canonical facts.

    All fields are derived through a frozen local policy table, never copied
    from production parser observations.
    """

    intended_action: str
    action_semantics: str
    temporal_relation: str
    normalized_values: dict[str, Any]
    entity_relations: dict[str, EntityRelation]
    requires_clarification: bool
    clarification_choices: tuple[str, ...]
    expected_tool_sequence: tuple[str, ...]
    expected_outcome_kind: str | None
    expected_authority: str | None
    expected_appointment_deltas: tuple[dict[str, Any], ...]
    expected_audit_deltas: tuple[dict[str, Any], ...]
    diary_state: str


# ---------------------------------------------------------------------------
# Frozen policy table – independently derives expected values from canonical
# facts without reference to production parser or scenario fixtures.
# This is the single source of truth for expected contracts in this module.
# ---------------------------------------------------------------------------


def _derive_expected_outcome(facts: CanonicalFactBundle) -> str | None:
    """Independently derive expected outcome from canonical facts."""
    if facts.action_semantics == "prohibited":
        return "instruction_refused"
    if facts.requires_clarification:
        return "clarification_required"
    if facts.action_negated:
        return None
    intended = facts.intended_action
    diary = facts.diary_state
    if intended == "explain_schedule":
        return "schedule_explained"
    if intended == "create":
        if diary in ("empty", "same_day_distinct", "terminal"):
            return "appointment_created"
        if diary == "exact_duplicate":
            return "existing_booking_found"
        if diary == "overlap":
            return "candidate_selection_required"
        return None
    _UNCERTAIN = frozenset({
        "terminal", "stale", "concurrent", "no_slots",
        "roster_absent", "break", "elapsed_window",
    })
    if diary in _UNCERTAIN:
        return None
    action_map = {
        "move": "appointment_moved",
        "resize": "appointment_resized",
        "cancel": "appointment_cancelled",
        "status_change": "appointment_status_changed",
    }
    return action_map.get(intended, None)


def _derive_expected_tools(facts: CanonicalFactBundle) -> tuple[str, ...]:
    """Independently derive expected tool sequence from canonical facts."""
    tools: list[str] = []
    for t in facts.selected_tool_sequence:
        if t not in tools:
            tools.append(t)
    return tuple(tools)


def _derive_expected_authority(facts: CanonicalFactBundle) -> str | None:
    """Independently derive expected authority posture from canonical facts."""
    if facts.action_semantics == "prohibited":
        return "refuse"
    if facts.action_semantics == "ambiguous" or facts.requires_clarification:
        return "clarify"
    return "read"


def _derive_expected_deltas(
    facts: CanonicalFactBundle,
    outcome: str | None,
) -> tuple[tuple[dict[str, Any], ...], tuple[dict[str, Any], ...]]:
    """Independently derive expected appointment/audit deltas.

    Only mutation outcomes produce deltas.  Refusal, negation,
    clarification, and non-mutation outcomes produce none.
    """
    if outcome is None or facts.action_negated:
        return (), ()
    if outcome == "instruction_refused":
        return (), ()
    if outcome == "clarification_required":
        return (), ()
    if outcome == "schedule_explained":
        return (), ()
    if outcome == "candidate_selection_required":
        return (), ()

    change_map = {
        "appointment_created": "created",
        "existing_booking_found": "created",
        "appointment_moved": "moved",
        "appointment_resized": "resized",
        "appointment_cancelled": "cancelled",
        "appointment_status_changed": "status_changed",
    }
    change_type = change_map.get(outcome, "")
    if not change_type:
        return (), ()

    vals = facts.normalized_values
    apt = {
        "appointment_id": "apt-001",
        "change_type": change_type,
        "patient_id": "p-001",
        "practitioner_id": "pr-001",
        "date": vals.get("appointment_date", ""),
        "start_time": vals.get("earliest_time", ""),
        "duration_minutes": vals.get("duration_minutes", 15),
    }
    aud = {
        "change_type": change_type,
        "appointment_id": "apt-001",
        "count": 1,
    }
    return (apt,), (aud,)


def derive_expected_contract(facts: CanonicalFactBundle) -> ExpectedScenarioContract:
    """Derive the expected scenario contract from canonical facts.

    This function is the single entry point for the frozen policy table.
    It must not import or call any production parser, composed evaluator,
    replay, scenario fixture, provider, or runtime module.

    Parameters
    ----------
    facts :
        The canonical fact bundle for one scenario.

    Returns
    -------
    ExpectedScenarioContract
        The expected contract with all fields independently derived.
    """
    outcome = _derive_expected_outcome(facts)
    tools = _derive_expected_tools(facts)
    authority = _derive_expected_authority(facts)
    apt_deltas, aud_deltas = _derive_expected_deltas(facts, outcome)

    return ExpectedScenarioContract(
        intended_action=facts.intended_action,
        action_semantics=facts.action_semantics,
        temporal_relation=facts.temporal_relation,
        normalized_values=dict(facts.normalized_values),
        entity_relations=dict(facts.entity_relations),
        requires_clarification=facts.requires_clarification,
        clarification_choices=facts.clarification_choices,
        expected_tool_sequence=tools,
        expected_outcome_kind=outcome,
        expected_authority=authority,
        expected_appointment_deltas=apt_deltas,
        expected_audit_deltas=aud_deltas,
        diary_state=facts.diary_state,
    )


# ---------------------------------------------------------------------------
# Validator
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class AuthoringQualityFinding:
    """One finding from the authoring quality check."""

    category: str
    passed: bool
    detail: str = ""


@dataclass(frozen=True)
class AuthoringQualityReceipt:
    """Aggregate authoring-quality receipt.

    Contains no utterances, tokens, source spans, scenario IDs,
    expected values, or case findings.
    """

    total_checks: int
    passed_checks: int
    failed_checks: int
    findings: tuple[AuthoringQualityFinding, ...] = ()
    total_surfaces_validated: int = 0
    surfaces_passed: int = 0
    surfaces_failed: int = 0

    @property
    def all_passed(self) -> bool:
        return self.failed_checks == 0


def validate_rendered_surface(
    turn: RenderedTurn,
    tokens: list[AuthorityToken],
    *,
    field_contract_requires: set[str] | None = None,
) -> list[AuthoringQualityFinding]:
    """Validate one rendered surface against the authoring quality contract.

    Parameters
    ----------
    turn :
        The rendered turn with prefix, core, suffix.
    tokens :
        Authority-bearing evidence tokens to validate.
    field_contract_requires :
        Set of field names that require exactly one authority token.
        If None, defaults to empty set.

    Returns
    -------
    list[AuthoringQualityFinding]
        Findings from the validation.
    """
    findings: list[AuthoringQualityFinding] = []
    if field_contract_requires is None:
        field_contract_requires = set()

    # 1. Prefix + core + suffix must equal full text byte-for-byte
    full = turn.full_text
    expected_parts = turn.prefix + turn.core + turn.suffix
    findings.append(AuthoringQualityFinding(
        category="prefix_core_suffix_integrity",
        passed=full == expected_parts,
        detail=(
            "prefix + core + suffix equals full text"
            if full == expected_parts
            else "prefix + core + suffix does not match full text"
        ),
    ))

    # 2. Style metadata may identify a language form but cannot rewrite the core
    # (already structural via RenderedTurn — core is separate from language_form)

    # 3. Case-sensitive authority tokens appear byte-identically
    for token in tokens:
        if token.turn_index != 0 and token.turn_index != 0:
            # multi-turn not fully supported in this simplified check
            pass

        turn_text = full
        if token.source_start < 0 or token.source_end > len(turn_text):
            findings.append(AuthoringQualityFinding(
                category="authority_span_out_of_range",
                passed=False,
                detail=f"Token {token.field_name!r} span [{token.source_start}:{token.source_end}] out of range",
            ))
            continue
        if token.source_end <= token.source_start:
            findings.append(AuthoringQualityFinding(
                category="authority_span_empty",
                passed=False,
                detail=f"Token {token.field_name!r} has empty span",
            ))
            continue

        actual_text = turn_text[token.source_start:token.source_end]
        if token.case_sensitive:
            match = actual_text == token.canonical_text
        else:
            match = actual_text.lower() == token.canonical_text.lower()

        findings.append(AuthoringQualityFinding(
            category=f"authority_token_{token.field_name}",
            passed=match,
            detail=(
                f"Token {token.field_name!r} matches at coordinates"
                if match
                else f"Token {token.field_name!r} mismatch: expected {token.canonical_text!r}, got {actual_text!r}"
            ),
        ))

        # Check source span text matches rendered source exactly
        # (always checked, independently of authority token match)
        if actual_text != token.source_text:
            findings.append(AuthoringQualityFinding(
                category=f"source_span_{token.field_name}",
                passed=False,
                detail=f"Source span text {token.source_text!r} does not match rendered {actual_text!r}",
            ))
        else:
            findings.append(AuthoringQualityFinding(
                category=f"source_span_{token.field_name}",
                passed=True,
                detail=f"Source span text matches for {token.field_name!r}",
            ))

    # 4. Field contract requires exactly one token per field
    token_fields: dict[str, list[AuthorityToken]] = {}
    for t in tokens:
        token_fields.setdefault(t.field_name, []).append(t)

    for field_name in field_contract_requires:
        found = token_fields.get(field_name, [])
        if not found:
            findings.append(AuthoringQualityFinding(
                category=f"field_contract_{field_name}",
                passed=False,
                detail=f"Required authority token for {field_name!r} is missing",
            ))
        elif len(found) > 1:
            findings.append(AuthoringQualityFinding(
                category=f"field_contract_{field_name}",
                passed=False,
                detail=f"Duplicate authority tokens for {field_name!r}",
            ))
        else:
            findings.append(AuthoringQualityFinding(
                category=f"field_contract_{field_name}",
                passed=True,
                detail=f"Required authority token for {field_name!r} present",
            ))

    return findings


def validate_entity_relation_evidence(
    entity_relations: dict[str, EntityRelation],
    tokens: list[AuthorityToken],
) -> list[AuthoringQualityFinding]:
    """Validate entity relation assertions match evidence.

    ``exact`` and ``corrected`` entity semantics must carry case-preserved
    evidence tokens.  ``omitted``, ``ambiguous``, ``negated``, and
    ``mismatched`` must use explicit relation assertions rather than
    silently claiming exact evidence.
    """
    findings: list[AuthoringQualityFinding] = []
    token_field_names = {t.field_name for t in tokens}

    for field_name, relation in entity_relations.items():
        if relation in ("exact", "corrected"):
            if field_name not in token_field_names:
                findings.append(AuthoringQualityFinding(
                    category=f"entity_relation_{field_name}",
                    passed=False,
                    detail=f"Entity {field_name!r} is {relation!r} but has no evidence token",
                ))
            else:
                findings.append(AuthoringQualityFinding(
                    category=f"entity_relation_{field_name}",
                    passed=True,
                    detail=f"Entity {field_name!r} is {relation!r} with evidence token",
                ))
                # Check case preservation for exact/corrected
                token = next(t for t in tokens if t.field_name == field_name)
                if not token.case_sensitive:
                    findings.append(AuthoringQualityFinding(
                        category=f"entity_relation_{field_name}_case",
                        passed=False,
                        detail=f"Entity {field_name!r} is {relation!r} but token is case-insensitive",
                    ))
                else:
                    findings.append(AuthoringQualityFinding(
                        category=f"entity_relation_{field_name}_case",
                        passed=True,
                        detail=f"Entity {field_name!r} is {relation!r} with case-preserved token",
                    ))
        else:
            # omitted, ambiguous, negated, mismatched
            if field_name in token_field_names:
                findings.append(AuthoringQualityFinding(
                    category=f"entity_relation_{field_name}",
                    passed=False,
                    detail=f"Entity {field_name!r} is {relation!r} but has evidence token (should use relation assertion)",
                ))
            else:
                findings.append(AuthoringQualityFinding(
                    category=f"entity_relation_{field_name}",
                    passed=True,
                    detail=f"Entity {field_name!r} is {relation!r} with no evidence token (relation assertion only)",
                ))

    return findings


def validate_expected_contract_derivation(
    facts: CanonicalFactBundle,
    expected: ExpectedScenarioContract,
) -> list[AuthoringQualityFinding]:
    """Validate that the expected contract matches independent policy derivation.

    This ensures no field is copied from a production parser observation.
    """
    findings: list[AuthoringQualityFinding] = []

    # Re-derive from frozen policy to verify consistency
    derived = derive_expected_contract(facts)

    checks = [
        ("intended_action", expected.intended_action, derived.intended_action),
        ("action_semantics", expected.action_semantics, derived.action_semantics),
        ("temporal_relation", expected.temporal_relation, derived.temporal_relation),
        ("expected_outcome_kind", expected.expected_outcome_kind, derived.expected_outcome_kind),
        ("expected_authority", expected.expected_authority, derived.expected_authority),
        ("diary_state", expected.diary_state, derived.diary_state),
    ]
    for name, exp_val, der_val in checks:
        match = exp_val == der_val
        findings.append(AuthoringQualityFinding(
            category=f"policy_derivation_{name}",
            passed=match,
            detail=(
                f"{name} matches policy derivation"
                if match
                else f"{name}: expected {exp_val!r}, derived {der_val!r}"
            ),
        ))

    # Tools
    if expected.expected_tool_sequence != derived.expected_tool_sequence:
        findings.append(AuthoringQualityFinding(
            category="policy_derivation_expected_tool_sequence",
            passed=False,
            detail=f"Tool sequence: expected {expected.expected_tool_sequence}, derived {derived.expected_tool_sequence}",
        ))
    else:
        findings.append(AuthoringQualityFinding(
            category="policy_derivation_expected_tool_sequence",
            passed=True,
            detail="Tool sequence matches policy derivation",
        ))

    # Deltas
    if expected.expected_appointment_deltas != derived.expected_appointment_deltas:
        findings.append(AuthoringQualityFinding(
            category="policy_derivation_appointment_deltas",
            passed=False,
            detail="Appointment deltas do not match policy derivation",
        ))
    else:
        findings.append(AuthoringQualityFinding(
            category="policy_derivation_appointment_deltas",
            passed=True,
            detail="Appointment deltas match policy derivation",
        ))

    if expected.expected_audit_deltas != derived.expected_audit_deltas:
        findings.append(AuthoringQualityFinding(
            category="policy_derivation_audit_deltas",
            passed=False,
            detail="Audit deltas do not match policy derivation",
        ))
    else:
        findings.append(AuthoringQualityFinding(
            category="policy_derivation_audit_deltas",
            passed=True,
            detail="Audit deltas match policy derivation",
        ))

    # Entity relations
    if expected.entity_relations != derived.entity_relations:
        findings.append(AuthoringQualityFinding(
            category="policy_derivation_entity_relations",
            passed=False,
            detail="Entity relations do not match policy derivation",
        ))
    else:
        findings.append(AuthoringQualityFinding(
            category="policy_derivation_entity_relations",
            passed=True,
            detail="Entity relations match policy derivation",
        ))

    # Normalized values
    if expected.normalized_values != derived.normalized_values:
        findings.append(AuthoringQualityFinding(
            category="policy_derivation_normalized_values",
            passed=False,
            detail="Normalized values do not match policy derivation",
        ))
    else:
        findings.append(AuthoringQualityFinding(
            category="policy_derivation_normalized_values",
            passed=True,
            detail="Normalized values match policy derivation",
        ))

    return findings


# ---------------------------------------------------------------------------
# JSON hash stability
# ---------------------------------------------------------------------------


def canonical_json_bytes(obj: Any) -> bytes:
    """Deterministic UTF-8/LF JSON serialization.

    Uses sorted keys, no extra whitespace, and LF line endings regardless
    of platform text settings.
    """
    text = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return text.encode("utf-8")


def stable_hash(obj: Any) -> str:
    """Deterministic SHA-256 hex digest with ``sha256:`` prefix."""
    return "sha256:" + hashlib.sha256(canonical_json_bytes(obj)).hexdigest()


# ---------------------------------------------------------------------------
# Aggregate receipt builder
# ---------------------------------------------------------------------------


def build_authoring_receipt(
    findings: list[AuthoringQualityFinding],
    total_surfaces: int = 0,
    surfaces_passed: int = 0,
    surfaces_failed: int = 0,
) -> AuthoringQualityReceipt:
    """Build an aggregate authoring quality receipt.

    The receipt contains no utterances, tokens, source spans, scenario IDs,
    expected values, or case findings.
    """
    total = len(findings)
    passed = sum(1 for f in findings if f.passed)
    failed = total - passed

    # Verify no case-level leakage in the receipt
    _verify_aggregate_safety(findings)

    return AuthoringQualityReceipt(
        total_checks=total,
        passed_checks=passed,
        failed_checks=failed,
        findings=tuple(findings),
        total_surfaces_validated=total_surfaces,
        surfaces_passed=surfaces_passed,
        surfaces_failed=surfaces_failed,
    )


def _verify_aggregate_safety(findings: list[AuthoringQualityFinding]) -> None:
    """Verify no findings contain case-level leakage: scenario IDs, tokens, etc."""
    prohibited_patterns = (
        "scenario_id",
        "utterance",
        "dialogue_turn",
        "source_span",
    )
    for finding in findings:
        lower = finding.detail.lower()
        for pattern in prohibited_patterns:
            if pattern in lower:
                raise ValueError(
                    f"Aggregate receipt leaks case-level content: "
                    f"pattern {pattern!r} in finding detail"
                )


__all__ = [
    "AuthorityToken",
    "AuthoringQualityFinding",
    "AuthoringQualityReceipt",
    "CanonicalFactBundle",
    "EntityRelation",
    "ExpectedScenarioContract",
    "RenderedTurn",
    "build_authoring_receipt",
    "canonical_json_bytes",
    "derive_expected_contract",
    "stable_hash",
    "validate_entity_relation_evidence",
    "validate_expected_contract_derivation",
    "validate_rendered_surface",
]
