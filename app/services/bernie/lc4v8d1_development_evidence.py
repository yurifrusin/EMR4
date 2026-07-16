"""LC4V8D1 fresh projection diagnostic runner.

Loads the 24-case Sol-authored development fixture, validates it fail-closed,
calls ordinary non-intercepted extract_semantics then explicit Option A
resolve_policy, projects the typed PolicyResolution to exactly 14 JSON-safe
fields, independently derives semantic policy invariants from the runtime
result, scores four layers separately, and applies the frozen classification
precedence:

    1. authoring_invalid     — fixture validation failure only
    2. normalization_gap     — time-form fragment/canonical/span absent or wrong
    3. parser_gap            — extraction intended_action/temporal mismatch
    4. policy_behavior_gap   — derived semantic policy invariants mismatch
    5. policy_projection_gap — exact canonical projection mismatch
    6. pass                  — every layer matches
"""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any, Mapping

from app.services.bernie.lc4v4d3_policy_resolution import (
    PolicyResolution,
    resolve_policy,
)
from app.services.bernie.semantic_extraction import extract_semantics

# ---------------------------------------------------------------------------
# Constants — must match the authorship test exactly
# ---------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parents[3]
FIXTURE_PATH = (
    ROOT
    / "tests"
    / "fixtures"
    / "bernie_lc4v8d1_development"
    / "probes.json"
)
EXPECTED_RAW_HASH = (
    "sha256:ebcfe4bbbd9c89dff00f1ff30643f2b9dc21f5cfba5febf62fd22e041f76269c"
)
REFERENCE_DATE = "2026-07-16"
SCHEMA_VERSION = "bernie.lc4v8d1.probes.v1"
EVIDENCE_SCHEMA_VERSION = "bernie.lc4v8d1.evidence.v1"
PROVENANCE_VALUE = (
    "fresh_sol_authored_synthetic_gold_development_only_from_public_v8_aggregates"
)
TOTAL_EXPECTED = 24
EXPECTED_FAMILY_COUNTS = {
    "canonical_policy_actions": 6,
    "policy_boundaries": 6,
    "time_surface_forms": 6,
    "time_relation_composition": 6,
}

TOP_LEVEL_KEYS = {"schema_version", "reference_date", "provenance", "cases"}
CASE_KEYS = {
    "probe_id",
    "family",
    "language_form",
    "utterances",
    "diary_state",
    "diary_appointments",
    "expected",
}
EXPECTED_KEYS = {
    "intended_action",
    "temporal_relation",
    "earliest_time",
    "latest_time",
    "normalization_time_forms",
    "policy_semantics",
    "policy_resolution",
}
TIME_FORM_KEYS = {"turn_index", "fragment", "canonical"}
POLICY_SEMANTIC_KEYS = {"resolution", "mutation_allowed", "safe"}
POLICY_RESOLUTION_KEYS = {
    "requires_clarification",
    "clarification_choices",
    "resolved_patient",
    "resolved_practitioner",
    "resolved_practitioner_id",
    "selected_tools",
    "authority",
    "diary_relation",
    "conflicting_fields",
    "downstream_outcome",
    "appointment_delta_count",
    "audit_delta_count",
    "simulated_write",
    "entity_semantics_unchanged",
}

# 14 JSON-safe projection field names (in contract order)
PROJECTION_FIELDS = (
    "requires_clarification",
    "clarification_choices",
    "resolved_patient",
    "resolved_practitioner",
    "resolved_practitioner_id",
    "selected_tools",
    "authority",
    "diary_relation",
    "conflicting_fields",
    "downstream_outcome",
    "appointment_delta_count",
    "audit_delta_count",
    "simulated_write",
    "entity_semantics_unchanged",
)

KNOWN_INTENDED_ACTIONS = frozenset({
    "create", "move", "resize", "cancel", "status_change", "explain_schedule",
})
TEMPORAL_RELATIONS = frozenset({
    "unspecified", "exact", "interval", "not_before", "not_after", "approximate",
})
MUTATION_TOOL_NAMES = frozenset({
    "create_booking", "update_appointment", "change_appointment_status",
})

CLASSIFICATIONS = (
    "pass",
    "authoring_invalid",
    "normalization_gap",
    "parser_gap",
    "policy_behavior_gap",
    "policy_projection_gap",
)

# Known practitioner map (from authorship test)
KNOWN_PRACTITIONERS = {
    "Dr Shera": "pr-001",
    "Dr Taylor": "pr-002",
    "Dr Patel": "pr-003",
    "Dr Chen": "pr-004",
    "Dr Smith": "pr-005",
    "Dr Singh": "pr-006",
}

# ---------------------------------------------------------------------------
# Fixture loading and validation
# ---------------------------------------------------------------------------


def load_fixture() -> dict[str, Any]:
    """Load the V8D1 development fixture from disk."""
    payload = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("LC4V8D1 fixture must be a JSON object")
    return payload


def validate_fixture(fixture: Any) -> tuple[str, ...]:
    """Fail-closed structural validation without executing product code.

    Mirrors every structural and cross-field invariant enforced by the
    authorship test.  Returns a tuple of error messages (empty means valid).
    """
    errors: list[str] = []

    if not isinstance(fixture, Mapping):
        return ("fixture must be an object",)

    # Top-level keys
    if set(fixture) != TOP_LEVEL_KEYS:
        errors.append("top-level field population is not exact")
    if fixture.get("schema_version") != SCHEMA_VERSION:
        errors.append("schema_version is not exact")
    if fixture.get("reference_date") != REFERENCE_DATE:
        errors.append("reference_date is not exact")
    if fixture.get("provenance") != PROVENANCE_VALUE:
        errors.append("provenance is not exact")

    cases = fixture.get("cases")
    if not isinstance(cases, list):
        return tuple(errors + ["cases must be a list"])
    if len(cases) != TOTAL_EXPECTED:
        errors.append(f"case population must equal {TOTAL_EXPECTED}")

    ids: list[str] = []
    families: Counter[str] = Counter()

    for index, case in enumerate(cases):
        label = f"case[{index}]"
        if not isinstance(case, Mapping):
            errors.append(f"{label} must be an object")
            continue

        # Case keys
        if set(case) != CASE_KEYS:
            errors.append(f"{label} field population is not exact")

        probe_id = case.get("probe_id")
        if not isinstance(probe_id, str) or not probe_id.startswith("v8d1-"):
            errors.append(f"{label} probe_id must be non-empty and start with v8d1-")
        else:
            ids.append(probe_id)

        family = case.get("family")
        if not isinstance(family, str):
            errors.append(f"{label} family must be a string")
        else:
            families[family] += 1

        language_form = case.get("language_form")
        if not isinstance(language_form, str) or not language_form:
            errors.append(f"{label} language_form must be a non-empty string")

        utterances = case.get("utterances")
        if not isinstance(utterances, list) or not utterances or any(
            not isinstance(u, str) or not u.strip() for u in utterances
        ):
            errors.append(f"{label} utterances must be non-empty strings")
        valid_utterances = utterances if isinstance(utterances, list) else []

        diary_state = case.get("diary_state")
        if diary_state not in {"empty", "field_conflict"}:
            errors.append(f"{label} diary_state must be empty or field_conflict")

        diary_appts = case.get("diary_appointments")
        if not isinstance(diary_appts, list):
            errors.append(f"{label} diary_appointments must be a list")

        expected = case.get("expected")
        if not isinstance(expected, Mapping) or set(expected) != EXPECTED_KEYS:
            errors.append(f"{label} expected field population is not exact")
        else:
            # intended_action
            if expected.get("intended_action") not in KNOWN_INTENDED_ACTIONS:
                errors.append(f"{label} intended_action is invalid")

            # temporal_relation
            if expected.get("temporal_relation") not in TEMPORAL_RELATIONS:
                errors.append(f"{label} temporal_relation is invalid")

            # earliest_time / latest_time
            for bound in ("earliest_time", "latest_time"):
                value = expected.get(bound)
                if value is not None and not re.fullmatch(
                    r"(?:[01]\d|2[0-3]):[0-5]\d", value
                ):
                    errors.append(f"{label} {bound} must be HH:MM or null")

            # normalization_time_forms
            ntf = expected.get("normalization_time_forms", [])
            if not isinstance(ntf, list):
                errors.append(f"{label} normalization_time_forms must be a list")
            else:
                seen_forms: set[tuple[int, str]] = set()
                for ntf_idx, ntf_item in enumerate(ntf):
                    if (
                        not isinstance(ntf_item, Mapping)
                        or set(ntf_item) != TIME_FORM_KEYS
                    ):
                        errors.append(
                            f"{label} normalization_time_forms[{ntf_idx}]"
                            f" schema is invalid"
                        )
                        continue
                    turn_index = ntf_item.get("turn_index")
                    fragment = ntf_item.get("fragment")
                    canonical = ntf_item.get("canonical")
                    if (
                        isinstance(turn_index, bool)
                        or not isinstance(turn_index, int)
                        or turn_index < 0
                        or turn_index >= len(valid_utterances)
                    ):
                        errors.append(
                            f"{label} normalization_time_forms[{ntf_idx}]"
                            f" turn_index is invalid"
                        )
                    if not isinstance(fragment, str) or not fragment:
                        errors.append(
                            f"{label} normalization_time_forms[{ntf_idx}]"
                            f" fragment is invalid"
                        )
                    if (
                        not isinstance(canonical, str)
                        or not re.fullmatch(
                            r"(?:[01]\d|2[0-3]):[0-5]\d", canonical
                        )
                    ):
                        errors.append(
                            f"{label} normalization_time_forms[{ntf_idx}]"
                            f" canonical is invalid"
                        )
                    if isinstance(turn_index, int) and isinstance(fragment, str):
                        identity = (turn_index, fragment)
                        if identity in seen_forms:
                            errors.append(
                                f"{label} normalization time forms must be unique"
                            )
                        seen_forms.add(identity)

            relation = expected.get("temporal_relation")
            earliest = expected.get("earliest_time")
            latest = expected.get("latest_time")
            valid_bounds = {
                "unspecified": earliest is None and latest is None,
                "exact": earliest is not None and earliest == latest,
                "interval": earliest is not None and latest is not None,
                "not_before": earliest is not None and latest is None,
                "not_after": earliest is None and latest is not None,
                "approximate": earliest is not None and latest is not None,
            }
            if relation in valid_bounds and not valid_bounds[relation]:
                errors.append(f"{label} temporal relation and bounds contradict")

            # policy_semantics
            ps = expected.get("policy_semantics")
            if not isinstance(ps, Mapping) or set(ps) != POLICY_SEMANTIC_KEYS:
                errors.append(f"{label} policy_semantics field population is not exact")
            else:
                if ps.get("resolution") not in {
                    "propose_mutation", "proceed_read", "clarify",
                    "refuse", "no_action",
                }:
                    errors.append(f"{label} policy_semantics.resolution is invalid")
                if not isinstance(ps.get("mutation_allowed"), bool):
                    errors.append(
                        f"{label} policy_semantics.mutation_allowed must be bool"
                    )
                if ps.get("safe") is not True:
                    errors.append(f"{label} policy_semantics.safe must be True")

            # policy_resolution
            pr = expected.get("policy_resolution")
            if not isinstance(pr, Mapping) or set(pr) != POLICY_RESOLUTION_KEYS:
                errors.append(
                    f"{label} policy_resolution field population is not exact"
                )
            else:
                if not isinstance(pr.get("requires_clarification"), bool):
                    errors.append(
                        f"{label} policy_resolution.requires_clarification"
                        f" must be bool"
                    )
                for list_field in ("clarification_choices", "selected_tools",
                                   "conflicting_fields"):
                    val = pr.get(list_field)
                    if not isinstance(val, list) or any(
                        not isinstance(item, str) for item in val
                    ):
                        errors.append(
                            f"{label} policy_resolution.{list_field}"
                            f" must be a string list"
                        )
                if pr.get("authority") not in {"read", "clarify", "refuse"}:
                    errors.append(
                        f"{label} policy_resolution.authority is invalid"
                    )
                if pr.get("diary_relation") not in {
                    "no_conflict", "exact_duplicate", "field_conflict",
                }:
                    errors.append(
                        f"{label} policy_resolution.diary_relation is invalid"
                    )
                for int_field in ("appointment_delta_count", "audit_delta_count"):
                    value = pr.get(int_field)
                    if not isinstance(value, int) or isinstance(value, bool):
                        errors.append(
                            f"{label} policy_resolution.{int_field}"
                            f" must be int"
                        )
                    elif value < 0:
                        errors.append(
                            f"{label} policy_resolution.{int_field}"
                            f" must be >= 0"
                        )
                for bool_field in ("simulated_write", "entity_semantics_unchanged"):
                    if not isinstance(pr.get(bool_field), bool):
                        errors.append(
                            f"{label} policy_resolution.{bool_field} must be bool"
                        )
                if pr.get("entity_semantics_unchanged") is not True:
                    errors.append(
                        f"{label} policy_resolution.entity_semantics_unchanged"
                        " must be True"
                    )
                for nullable_field in (
                    "resolved_patient",
                    "resolved_practitioner",
                    "resolved_practitioner_id",
                    "downstream_outcome",
                ):
                    value = pr.get(nullable_field)
                    if value is not None and not isinstance(value, str):
                        errors.append(
                            f"{label} policy_resolution.{nullable_field}"
                            " must be string or null"
                        )

                # Cross-field practitioner consistency
                practitioner = pr.get("resolved_practitioner")
                practitioner_id = pr.get("resolved_practitioner_id")
                if practitioner in KNOWN_PRACTITIONERS:
                    if practitioner_id != KNOWN_PRACTITIONERS[practitioner]:
                        errors.append(
                            f"{label} practitioner ID mismatch for"
                            f" {practitioner}"
                        )
                elif practitioner is None or practitioner == "Dr Rowan":
                    if practitioner_id is not None:
                        errors.append(
                            f"{label} expected null practitioner_id for"
                            f" {practitioner}"
                        )
                else:
                    errors.append(
                        f"{label} unadjudicated practitioner: {practitioner}"
                    )

                if isinstance(ps, Mapping) and set(ps) == POLICY_SEMANTIC_KEYS:
                    resolution = ps.get("resolution")
                    mutation_allowed = ps.get("mutation_allowed")
                    tools = pr.get("selected_tools")
                    tools = tools if isinstance(tools, list) else []
                    has_mutation_tool = bool(MUTATION_TOOL_NAMES.intersection(tools))
                    apt_count = pr.get("appointment_delta_count")
                    audit_count = pr.get("audit_delta_count")
                    no_mutation_evidence = (
                        not has_mutation_tool
                        and apt_count == 0
                        and audit_count == 0
                        and pr.get("simulated_write") is False
                    )
                    if resolution == "propose_mutation":
                        consistent = (
                            mutation_allowed is True
                            and pr.get("requires_clarification") is False
                            and pr.get("authority") == "read"
                            and has_mutation_tool
                            and apt_count == 1
                            and audit_count == 1
                            and pr.get("simulated_write") is True
                            and pr.get("downstream_outcome") is not None
                        )
                    elif resolution == "proceed_read":
                        consistent = (
                            mutation_allowed is False
                            and pr.get("requires_clarification") is False
                            and pr.get("authority") == "read"
                            and no_mutation_evidence
                        )
                    elif resolution == "clarify":
                        consistent = (
                            mutation_allowed is False
                            and pr.get("requires_clarification") is True
                            and pr.get("authority") == "clarify"
                            and tools == ["request_clarification"]
                            and pr.get("downstream_outcome")
                            == "clarification_required"
                            and no_mutation_evidence
                        )
                    elif resolution == "refuse":
                        consistent = (
                            mutation_allowed is False
                            and pr.get("requires_clarification") is False
                            and pr.get("authority") == "refuse"
                            and tools == ["refuse_instruction"]
                            and pr.get("downstream_outcome") == "instruction_refused"
                            and no_mutation_evidence
                        )
                    elif resolution == "no_action":
                        consistent = (
                            mutation_allowed is False
                            and pr.get("requires_clarification") is False
                            and pr.get("authority") == "read"
                            and pr.get("downstream_outcome") is None
                            and no_mutation_evidence
                        )
                    else:
                        consistent = False
                    if not consistent:
                        errors.append(
                            f"{label} policy semantics and projection contradict"
                        )

        if diary_state == "empty" and diary_appts != []:
            errors.append(f"{label} empty diary_state requires no appointments")
        if diary_state == "field_conflict":
            if not isinstance(diary_appts, list) or len(diary_appts) != 1:
                errors.append(f"{label} field_conflict requires one appointment")
            if isinstance(expected, Mapping):
                policy_resolution = expected.get("policy_resolution")
                if isinstance(policy_resolution, Mapping) and (
                    policy_resolution.get("diary_relation") != "field_conflict"
                    or not policy_resolution.get("conflicting_fields")
                ):
                    errors.append(f"{label} field_conflict Gold is incomplete")

    # Uniqueness
    if len(ids) != len(set(ids)):
        errors.append("probe IDs must be unique")

    # Family counts
    if dict(families) != EXPECTED_FAMILY_COUNTS:
        errors.append("family population is not exact")

    return tuple(dict.fromkeys(errors))


# ---------------------------------------------------------------------------
# Hashing
# ---------------------------------------------------------------------------


def compute_fixture_hash(fixture: Mapping[str, Any]) -> str:
    """Deterministic SHA-256 of the fixture content (sorted JSON keys)."""
    encoded = json.dumps(
        fixture, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def compute_raw_fixture_hash() -> str:
    """Return the exact committed fixture-byte binding."""
    return "sha256:" + hashlib.sha256(FIXTURE_PATH.read_bytes()).hexdigest()


# ---------------------------------------------------------------------------
# Observation — runs extraction then policy, no expected values passed
# ---------------------------------------------------------------------------


def _observe(
    utterances: list[str],
    diary_state: str,
    diary_appointments: list[dict[str, Any]],
    reference_date: str,
) -> dict[str, Any]:
    """Produce a single deterministic observation with no Gold comparison."""
    extraction = extract_semantics(utterances, reference_date)
    policy = resolve_policy(
        utterances=utterances,
        entity_semantics=extraction.entity_semantics,
        requires_clarification=extraction.requires_clarification,
        clarification_choices=extraction.clarification_choices,
        intended_action=extraction.intended_action,
        action_semantics=extraction.action_semantics,
        authority_claim=extraction.authority_claim,
        selected_tool_sequence=extraction.selected_tool_sequence,
        normalized_values=extraction.normalized_values,
        temporal_relation=extraction.temporal_relation,
        earliest_time=extraction.earliest_time,
        latest_time=extraction.latest_time,
        action_negated=extraction.action_negated,
        diary_state=diary_state,
        diary_appointments=diary_appointments,
        reference_date=reference_date,
    )

    # Project the typed PolicyResolution to exactly 14 JSON-safe fields.
    # Ordered tuples become arrays; explicit nulls are preserved.
    projection = _project_policy(policy)

    return {
        "extraction": {
            "intended_action": extraction.intended_action,
            "temporal_relation": extraction.temporal_relation,
            "earliest_time": extraction.earliest_time,
            "latest_time": extraction.latest_time,
            "action_semantics": extraction.action_semantics,
            "action_negated": extraction.action_negated,
            "authority": extraction.authority_claim,
            "requires_clarification": extraction.requires_clarification,
            "clarification_choices": list(extraction.clarification_choices),
            "claims_action_completed": extraction.claims_action_completed,
            "normalization_turns": [
                {
                    "time_forms": dict(nu.time_forms),
                    "source_spans": {
                        k: list(v) if isinstance(v, tuple) else v
                        for k, v in nu.source_spans.items()
                    },
                }
                for nu in extraction.normalized_turns
            ],
        },
        "policy": projection,
    }


def _project_policy(policy: PolicyResolution) -> dict[str, Any]:
    """Project a typed PolicyResolution to the exact 14-field JSON form.

    This is the canonical lossless projection.  Tuples become arrays,
    explicit nulls are preserved, and every field is emitted.
    """
    return {
        "requires_clarification": policy.requires_clarification,
        "clarification_choices": list(policy.clarification_choices),
        "resolved_patient": policy.resolved_patient,
        "resolved_practitioner": policy.resolved_practitioner,
        "resolved_practitioner_id": policy.resolved_practitioner_id,
        "selected_tools": list(policy.selected_tools),
        "authority": policy.authority,
        "diary_relation": policy.diary_comparison.relation,
        "conflicting_fields": list(policy.diary_comparison.conflicting_fields),
        "downstream_outcome": policy.downstream_outcome,
        "appointment_delta_count": len(policy.appointment_deltas),
        "audit_delta_count": len(policy.audit_deltas),
        "simulated_write": policy.is_simulated_confirmed_write,
        "entity_semantics_unchanged": policy.utterance_entity_semantics_unchanged,
    }


# ---------------------------------------------------------------------------
# Derived semantic policy invariants
# ---------------------------------------------------------------------------


def _derive_policy_semantics(
    observation: dict[str, Any],
) -> dict[str, Any]:
    """Independently derive semantic policy invariants from the runtime result.

    Never compares to Gold.  Derives resolution, mutation_allowed, and safe
    from the observation alone.
    """
    extraction = observation["extraction"]
    policy = observation["policy"]
    authority = policy["authority"]
    requires_clarification = policy["requires_clarification"]
    has_mutation_tool = any(
        tool in MUTATION_TOOL_NAMES for tool in policy["selected_tools"]
    )
    has_appointment_delta = policy["appointment_delta_count"] > 0
    has_audit_delta = policy["audit_delta_count"] > 0
    simulated_write = policy["simulated_write"] is True
    has_any_mutation_evidence = (
        has_mutation_tool
        or has_appointment_delta
        or has_audit_delta
        or simulated_write
    )

    # Derive resolution from runtime behavior
    if extraction["action_semantics"] == "prohibited":
        resolution = "refuse"
    elif extraction["action_negated"]:
        resolution = "no_action"
    elif requires_clarification or authority == "clarify":
        resolution = "clarify"
    elif authority == "refuse":
        resolution = "refuse"
    elif extraction["intended_action"] == "explain_schedule":
        resolution = "proceed_read"
    elif extraction["intended_action"] is not None:
        resolution = "propose_mutation"
    else:
        resolution = "clarify"

    mutation_allowed = (
        resolution == "propose_mutation"
        and has_mutation_tool
        and has_appointment_delta
        and has_audit_delta
        and simulated_write
    )

    # Safety: no premature completion claim, valid authority, no mutation
    # tools for non-mutation resolutions
    safe: bool = (
        extraction.get("claims_action_completed") is False
        and authority in ("read", "clarify", "refuse")
    )
    if safe and resolution == "propose_mutation":
        safe = mutation_allowed
    elif safe:
        safe = not has_any_mutation_evidence

    return {
        "resolution": resolution,
        "mutation_allowed": mutation_allowed,
        "safe": safe,
    }


# ---------------------------------------------------------------------------
# Layer comparison functions
# ---------------------------------------------------------------------------


def _normalization_mismatches(
    expected: Mapping[str, Any],
    observation: dict[str, Any],
) -> tuple[str, ...]:
    """Check each expected normalisation time form has exact canonical + span."""
    expected_forms = expected.get("normalization_time_forms", [])
    if not expected_forms:
        return ()
    mismatches: list[str] = []
    normalization_turns = observation["extraction"]["normalization_turns"]
    for form in expected_forms:
        turn_idx = form["turn_index"]
        fragment = form["fragment"]
        canonical = form["canonical"]
        if turn_idx >= len(normalization_turns):
            mismatches.append(f"normalization_missing_turn:{turn_idx}")
            continue
        nu = normalization_turns[turn_idx]
        time_forms = nu["time_forms"]
        if fragment not in time_forms:
            mismatches.append(f"normalization_missing_fragment:{fragment}")
            continue
        if time_forms[fragment] != canonical:
            mismatches.append(f"normalization_canonical_mismatch:{fragment}")
        span_key = f"time:{fragment}"
        if span_key not in nu["source_spans"]:
            mismatches.append(f"normalization_missing_span:{fragment}")
    return tuple(mismatches)


def _extraction_mismatches(
    expected: Mapping[str, Any],
    observation: dict[str, Any],
) -> tuple[str, ...]:
    """Compare extraction action and temporal relation/bounds."""
    ext = observation["extraction"]
    mismatches: list[str] = []

    if ext["intended_action"] != expected["intended_action"]:
        mismatches.append("intended_action")
    if ext["temporal_relation"] != expected["temporal_relation"]:
        mismatches.append("temporal_relation")
    if ext["earliest_time"] != expected["earliest_time"]:
        mismatches.append("earliest_time")
    if ext["latest_time"] != expected["latest_time"]:
        mismatches.append("latest_time")
    if ext.get("claims_action_completed") is not False:
        mismatches.append("claims_action_completed")

    return tuple(mismatches)


def _policy_behavior_mismatches(
    expected: Mapping[str, Any],
    observation: dict[str, Any],
) -> tuple[str, ...]:
    """Compare derived semantic policy invariants against Gold.

    The derived invariants (resolution, mutation_allowed, safe) are compared
    to expected['policy_semantics'].  Returns the list of mismatched fields.
    """
    derived = observation["derived_semantics"]
    gold = expected.get("policy_semantics", {})
    mismatches: list[str] = []

    if derived["resolution"] != gold.get("resolution"):
        mismatches.append("resolution")
    if derived["mutation_allowed"] != gold.get("mutation_allowed"):
        mismatches.append("mutation_allowed")
    if derived["safe"] != gold.get("safe"):
        mismatches.append("safe")

    return tuple(mismatches)


def _policy_projection_mismatches(
    expected: Mapping[str, Any],
    observation: dict[str, Any],
) -> tuple[str, ...]:
    """Compare exact 14-field projection against Gold policy_resolution."""
    policy = observation["policy"]
    gold = expected.get("policy_resolution", {})
    mismatches: list[str] = []

    for field in PROJECTION_FIELDS:
        obs_val = policy.get(field)
        exp_val = gold.get(field)
        if obs_val != exp_val:
            mismatches.append(field)

    return tuple(mismatches)


def _safe(
    observation: dict[str, Any],
) -> bool:
    """Independently assess safety from the observation.

    Returns True when the runtime behavior is safe: no premature completion
    claim, valid authority, and appropriate tool selection for the derived
    resolution.
    """
    derived = observation["derived_semantics"]
    if derived["safe"] is not True:
        return False
    return derived["safe"] is True


# ---------------------------------------------------------------------------
# Main evidence procedure
# ---------------------------------------------------------------------------


def run_lc4v8d1_evidence(
    fixture: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Run the complete LC4V8D1 evidence procedure and return the report.

    Parameters
    ----------
    fixture :
        The fixture dict.  Loaded from disk when None.

    Returns
    -------
    dict
        The complete evidence report with per-case observations, aggregate
        counts, classifications, selection, and report hash.
    """
    raw_fixture_hash: str | None = None
    if fixture is None:
        raw_fixture_hash = compute_raw_fixture_hash()
        fixture = load_fixture()
        if raw_fixture_hash != EXPECTED_RAW_HASH:
            return _invalid_report(
                fixture,
                ("raw fixture hash is not exact",),
                raw_fixture_hash=raw_fixture_hash,
            )

    errors = validate_fixture(fixture)
    if errors:
        return _invalid_report(
            fixture,
            errors,
            raw_fixture_hash=raw_fixture_hash,
        )

    results: list[dict[str, Any]] = []
    classification_counts: dict[str, int] = {name: 0 for name in CLASSIFICATIONS}
    reference_date = fixture.get("reference_date", REFERENCE_DATE)

    for case in fixture["cases"]:
        probe_id = case["probe_id"]
        family = case["family"]
        utterances = case["utterances"]
        diary_state = case.get("diary_state", "empty")
        diary_appointments = case.get("diary_appointments", [])
        expected = case["expected"]

        # Run twice with no expected values downstream
        first = _observe(utterances, diary_state, diary_appointments, reference_date)
        second = _observe(utterances, diary_state, diary_appointments, reference_date)

        # Derive semantic policy invariants from runtime result only
        first["derived_semantics"] = _derive_policy_semantics(first)
        second["derived_semantics"] = _derive_policy_semantics(second)

        # Score each layer
        normalization_misms = _normalization_mismatches(expected, first)
        extraction_misms = _extraction_mismatches(expected, first)
        behavior_misms = _policy_behavior_mismatches(expected, first)
        projection_misms = _policy_projection_mismatches(expected, first)

        # Classify in precedence order
        if normalization_misms:
            classification = "normalization_gap"
        elif extraction_misms:
            classification = "parser_gap"
        elif behavior_misms:
            classification = "policy_behavior_gap"
        elif projection_misms:
            classification = "policy_projection_gap"
        else:
            classification = "pass"

        classification_counts[classification] += 1
        variance = first != second

        results.append({
            "probe_id": probe_id,
            "family": family,
            "classification": classification,
            "normalization_mismatches": normalization_misms,
            "extraction_mismatches": extraction_misms,
            "policy_behavior_mismatches": behavior_misms,
            "policy_projection_mismatches": projection_misms,
            "safe": _safe(first),
            "variance": variance,
            "observations": (first, second),
        })

    # Aggregate counts
    normalization_pass = sum(
        not item["normalization_mismatches"] for item in results
    )
    extraction_pass = sum(not item["extraction_mismatches"] for item in results)
    behavior_pass = sum(not item["policy_behavior_mismatches"] for item in results)
    projection_pass = sum(
        not item["policy_projection_mismatches"] for item in results
    )
    composed_pass = sum(
        not item["normalization_mismatches"]
        and not item["extraction_mismatches"]
        and not item["policy_behavior_mismatches"]
        and not item["policy_projection_mismatches"]
        for item in results
    )

    # Build non-pass selection
    non_pass = [item for item in results if item["classification"] != "pass"]
    selection_data = [
        {
            "probe_id": item["probe_id"],
            "classification": item["classification"],
            "normalization_mismatches": list(item["normalization_mismatches"]),
            "extraction_mismatches": list(item["extraction_mismatches"]),
            "policy_behavior_mismatches": list(item["policy_behavior_mismatches"]),
            "policy_projection_mismatches": list(item["policy_projection_mismatches"]),
        }
        for item in non_pass
    ]
    selection_encoded = json.dumps(
        selection_data,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    selection = {
        "non_pass_count": len(non_pass),
        "selection_hash": "sha256:" + hashlib.sha256(selection_encoded).hexdigest(),
    }

    report = {
        "schema_version": EVIDENCE_SCHEMA_VERSION,
        "fixture_hash": compute_fixture_hash(fixture),
        "fixture_raw_hash": raw_fixture_hash,
        "fixture_valid": True,
        "fixture_validation_errors": (),
        "aggregate": {
            "total": len(results),
            "normalization_pass": normalization_pass,
            "extraction_pass": extraction_pass,
            "policy_behavior_pass": behavior_pass,
            "policy_projection_pass": projection_pass,
            "composed_pass": composed_pass,
            "safe": sum(item["safe"] for item in results),
            "variance": sum(item["variance"] for item in results),
        },
        "classifications": classification_counts,
        "family_counts": dict(
            Counter(item["family"] for item in results)
        ),
        "selection": selection,
        "cases": tuple(results),
    }

    # Bind the complete final report hash (after selection insertion)
    report_encoded = json.dumps(
        report, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    report["report_hash"] = (
        "sha256:" + hashlib.sha256(report_encoded).hexdigest()
    )

    return report


def _invalid_report(
    fixture: Mapping[str, Any],
    errors: tuple[str, ...],
    *,
    raw_fixture_hash: str | None = None,
) -> dict[str, Any]:
    """Build a fail-closed report when fixture validation fails.

    Returns 24 authoring_invalid classifications with zero observations,
    no product code executed.
    """
    selection_data = [{"classification": "authoring_invalid", "count": TOTAL_EXPECTED}]
    selection_encoded = json.dumps(
        selection_data, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    report = {
        "schema_version": EVIDENCE_SCHEMA_VERSION,
        "fixture_hash": compute_fixture_hash(fixture),
        "fixture_raw_hash": raw_fixture_hash,
        "fixture_valid": False,
        "fixture_validation_errors": errors,
        "aggregate": {
            "total": 0,
            "normalization_pass": 0,
            "extraction_pass": 0,
            "policy_behavior_pass": 0,
            "policy_projection_pass": 0,
            "composed_pass": 0,
            "safe": 0,
            "variance": 0,
        },
        "classifications": {
            name: (TOTAL_EXPECTED if name == "authoring_invalid" else 0)
            for name in CLASSIFICATIONS
        },
        "family_counts": {},
        "selection": {
            "non_pass_count": TOTAL_EXPECTED,
            "selection_hash": "sha256:"
            + hashlib.sha256(selection_encoded).hexdigest(),
        },
        "cases": (),
    }
    report_encoded = json.dumps(
        report, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    report["report_hash"] = "sha256:" + hashlib.sha256(report_encoded).hexdigest()
    return report


__all__ = [
    "CLASSIFICATIONS",
    "EXPECTED_FAMILY_COUNTS",
    "FIXTURE_PATH",
    "PROJECTION_FIELDS",
    "REFERENCE_DATE",
    "SCHEMA_VERSION",
    "TOTAL_EXPECTED",
    "compute_fixture_hash",
    "compute_raw_fixture_hash",
    "load_fixture",
    "run_lc4v8d1_evidence",
    "validate_fixture",
]
