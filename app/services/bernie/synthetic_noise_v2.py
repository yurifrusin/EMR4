"""Development-only v2 dialogue-free anchor contracts for Bernie Silver.

V2 replaces the v1 coverage shape with a balanced 96-anchor/192-candidate
matrix across 6 actions and 8 dialogue forms.  Each anchor is dialogue-free,
stores a complete semantic/policy/replay contract, and is validated by a
fail-closed coherence validator before generation.

The module loads only ordinary LC4 development evidence.  It never accesses
a protected holdout, historical diary, appointment-call corpus, or external
dialogue corpus.  No source utterance, description, or source span is exported
into an anchor.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from app.services.bernie.corpus_tier import compute_scenario_hash
from app.services.bernie.scale_corpus import (
    DevelopmentOnlyLoader,
    ReceptionScenarioSpec,
)

# ---------------------------------------------------------------------------
# V2 schema and count constants
# ---------------------------------------------------------------------------

SEED_SCHEMA_VERSION_V2 = "emr4.bernie.synthetic_noise_seed.v2"
SEED_MANIFEST_SCHEMA_VERSION_V2 = (
    "emr4.bernie.synthetic_noise_seed_manifest.v2"
)
ANCHOR_COUNT_V2 = 96
DEFAULT_SEED_PATH_V2 = Path(
    "tests/fixtures/bernie_synthetic_noise/semantic_seeds_v2.json"
)

# The six action types in canonical order.
ACTIONS_V2: tuple[str, ...] = (
    "create",
    "move",
    "resize",
    "cancel",
    "status_change",
    "explain_schedule",
)

# The eight dialogue forms in canonical order.
FORMS_V2: tuple[str, ...] = (
    "one_shot",
    "clarification",
    "correction",
    "reversal",
    "ellipsis",
    "anaphora",
    "repeated_request",
    "session_restart",
)

# Map v2 form names to the v1 scenario dialogue_form literal for searching
# the existing development corpus.
_FORM_V1_MAP: dict[str, str] = {
    "one_shot": "one_shot",
    "clarification": "clarification",
    "correction": "correction",
    "reversal": "reversal",
    "ellipsis": "ellipsis",
    "anaphora": "anaphora",
    "repeated_request": "repeated",
    "session_restart": "session_restart",
}

_AUTHORITY_ALL_FALSE: dict[str, bool] = {
    "provider_write": False,
    "diary_write": False,
    "confirmation": False,
    "override_authority": False,
}


# ---------------------------------------------------------------------------
# Deterministic helpers
# ---------------------------------------------------------------------------


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def _sha256(value: Any) -> str:
    return "sha256:" + hashlib.sha256(
        _canonical_json(value).encode("utf-8")
    ).hexdigest()


# ---------------------------------------------------------------------------
# Source selection
# ---------------------------------------------------------------------------


def _select_anchor_sources(
    corpus: Any,
) -> dict[tuple[str, str], list[ReceptionScenarioSpec]]:
    """Select exactly 2 source scenarios per (action, form) cell.

    Returns a dict keyed by (action, form_v2) with a list of 2
    ReceptionScenarioSpec sources, sorted deterministically by scenario_id.
    """
    all_variants = corpus.all_variants()

    # Index variants by (v1_action, v1_dialogue_form)
    buckets: dict[tuple[str, str], list[ReceptionScenarioSpec]] = {}
    for v in all_variants:
        key = (v.intended_action, v.dialogue_form)
        buckets.setdefault(key, []).append(v)

    result: dict[tuple[str, str], list[ReceptionScenarioSpec]] = {}
    for action in ACTIONS_V2:
        for form_v2 in FORMS_V2:
            form_v1 = _FORM_V1_MAP[form_v2]
            candidates = sorted(
                buckets.get((action, form_v1), []),
                key=lambda s: s.scenario_id,
            )
            if len(candidates) < 2:
                raise RuntimeError(
                    f"Not enough source scenarios for ({action}, {form_v2}): "
                    f"found {len(candidates)}, need 2"
                )
            result[(action, form_v2)] = candidates[:2]

    return result


# ---------------------------------------------------------------------------
# Action-specific contract derivation helpers
# ---------------------------------------------------------------------------


def _action_tool_sequence(action: str) -> list[str]:
    if action == "create":
        return ["search_patients", "find_slots", "create_booking"]
    if action in ("move", "resize", "cancel"):
        return ["search_patients", "update_appointment"]
    if action == "status_change":
        return ["search_patients", "change_appointment_status"]
    if action == "explain_schedule":
        return ["search_patients", "find_slots"]
    return ["search_patients"]


def _action_outcome(action: str) -> str:
    outcomes = {
        "create": "appointment_created",
        "move": "appointment_moved",
        "resize": "appointment_resized",
        "cancel": "appointment_cancelled",
        "status_change": "appointment_status_changed",
        "explain_schedule": "schedule_explained",
    }
    return outcomes.get(action, "action_completed")


def _action_appointment_deltas(
    action: str,
    scenario: ReceptionScenarioSpec,
) -> list[dict[str, Any]]:
    """Derive action-specific appointment deltas from the source scenario.

    Uses the source scenario's normalized values for date, times, and
    duration so that the anchor's deltas are consistent with its
    provenance base.
    """
    if action == "explain_schedule":
        return []

    norm = scenario.normalized_values
    appointment_date = norm.get("appointment_date", "")
    start_time = norm.get("earliest_time", "15:00")
    duration_minutes = scenario.duration_minutes or 15

    patient_name = "Margaret Thompson"
    practitioner_name = "Dr Shera"

    # Infer patient/practitioner IDs from scenario semantics
    practitioner_id = "pr-001"
    if scenario.practitioner_semantics == "mismatched":
        practitioner_id = "pr-002"

    delta: dict[str, Any] = {
        "appointment_id": "apt-001",
        "patient_id": "p-001",
        "practitioner_id": practitioner_id,
        "patient_name": patient_name,
        "practitioner_name": practitioner_name,
    }

    if action == "create":
        delta["change_type"] = "created"
        delta["date"] = appointment_date
        delta["start_time"] = start_time
        delta["duration_minutes"] = duration_minutes
    elif action == "move":
        delta["change_type"] = "moved"
        delta["new_date"] = appointment_date
        delta["new_start_time"] = start_time
    elif action == "resize":
        delta["change_type"] = "resized"
        delta["new_duration_minutes"] = duration_minutes
    elif action == "cancel":
        delta["change_type"] = "cancelled"
        delta["date"] = appointment_date
        delta["start_time"] = start_time
    elif action == "status_change":
        delta["change_type"] = "status_changed"
        delta["new_status"] = "arrived"
        delta["date"] = appointment_date
        delta["start_time"] = start_time
    else:
        delta["change_type"] = "updated"

    return [delta]


def _action_audit_deltas(action: str) -> list[dict[str, Any]]:
    if action == "explain_schedule":
        return []
    return [
        {
            "change_type": f"{action}_requested",
            "appointment_id": "apt-001",
            "count": 1,
        }
    ]


def _forbidden_outcomes(action: str, diary_state: str) -> list[str]:
    if action == "create" and diary_state == "exact_duplicate":
        return ["second_appointment_created"]
    return []


def _forbidden_tool_calls() -> list[str]:
    return ["mutate_diary_direct", "override_confirmation"]


# ---------------------------------------------------------------------------
# Semantic contract builder
# ---------------------------------------------------------------------------


def _build_semantic_contract(
    scenario: ReceptionScenarioSpec,
    *,
    form_v2: str,
    cell_variant: int,
) -> dict[str, Any]:
    """Build a complete dialogue-free semantic contract for a v2 anchor.

    Copies entity, temporal, and diary semantics from the source scenario.
    Derives outcome, tools, and deltas from the v2 form and action to
    match the v2 coherence model.  No source utterance, description, or
    source span is exported.
    """
    action = scenario.intended_action
    is_clarification = form_v2 == "clarification"
    is_reversal = form_v2 == "reversal"
    is_schedule = action == "explain_schedule"

    # --- Outcome (derived per v2 form) ---
    if is_clarification:
        outcome = "clarification_required"
    elif is_reversal:
        outcome = None
    else:
        outcome = _action_outcome(action)

    # --- Tool sequence (derived per v2 form) ---
    if is_clarification:
        tools = ["request_clarification"]
    elif is_reversal:
        # Only search_patients when patient is surfaced, else empty
        if scenario.patient_semantics == "exact":
            tools = ["search_patients"]
        else:
            tools = []
    else:
        tools = _action_tool_sequence(action)

    # --- Appointment deltas ---
    if is_clarification or is_reversal:
        apt_deltas: list[dict[str, Any]] = []
    elif is_schedule:
        apt_deltas = []
    else:
        apt_deltas = _action_appointment_deltas(action, scenario)

    # --- Audit deltas ---
    if is_clarification or is_reversal:
        audit_deltas: list[dict[str, Any]] = []
    elif is_schedule:
        audit_deltas = []
    else:
        audit_deltas = _action_audit_deltas(action)

    # --- Clarification question/choices (fictional, form-derived) ---
    if is_clarification:
        if cell_variant == 1:
            # Patient ambiguity
            clar_question = (
                "Please clarify: which patient is this appointment for?"
            )
            clar_choices = [
                "Margaret Thompson",
                "Robert Johnson",
                "Sarah Williams",
            ]
        else:
            # Practitioner ambiguity
            clar_question = (
                "Please clarify: which practitioner should the appointment "
                "be booked with?"
            )
            clar_choices = [
                "Dr Shera",
                "Dr Patel",
                "Dr Chen",
            ]
    else:
        clar_question = None
        clar_choices = []

    # --- action_withdrawn ---
    action_withdrawn = is_reversal

    contract: dict[str, Any] = {
        "reference_date": scenario.reference_date.isoformat(),
        "clinic_clock": scenario.clinic_clock.isoformat(),
        "intended_action": scenario.intended_action,
        "action_semantics": scenario.action_semantics,
        "temporal_relation": scenario.temporal_relation,
        "earliest_time": scenario.earliest_time,
        "latest_time": scenario.latest_time,
        "normalized_values": dict(scenario.normalized_values),
        "duration_minutes": scenario.duration_minutes,
        "patient_semantics": scenario.patient_semantics,
        "practitioner_semantics": scenario.practitioner_semantics,
        "location_semantics": scenario.location_semantics,
        "appointment_type_semantics": scenario.appointment_type_semantics,
        "duration_semantics": scenario.duration_semantics,
        "diary_state": scenario.diary_state,
        "entity_state": scenario.entity_state,
        "initial_diary_state": dict(scenario.initial_diary_state),
        "expected_outcome_kind": outcome,
        "expected_tool_sequence": tools,
        "expected_appointment_deltas": apt_deltas,
        "expected_audit_deltas": audit_deltas,
        "forbidden_outcomes": _forbidden_outcomes(
            action, scenario.diary_state
        ),
        "forbidden_tool_calls": _forbidden_tool_calls(),
        "expected_clarification": clar_question,
        "clarification_choices": clar_choices,
        "action_withdrawn": action_withdrawn,
    }
    return contract


def _build_dialogue_form_contract(
    scenario: ReceptionScenarioSpec,
    *,
    form_v2: str,
    cell_variant: int,
) -> dict[str, Any]:
    """Build the dialogue-form contract for an anchor (without seed_hash).

    The caller adds seed_hash after computing it over the full anchor.
    """
    return {
        "dialogue_form": form_v2,
        "required_evidence_keys": sorted(scenario.source_spans),
        "authority_grant": dict(_AUTHORITY_ALL_FALSE),
        "source_bindings": {
            "source_scenario_id": scenario.scenario_id,
            "source_scenario_hash": compute_scenario_hash(scenario),
        },
        "cell_variant": cell_variant,
    }


def _map_form_to_v2(v1_form: str) -> str:
    """Map a v1 dialogue_form literal to the v2 form name."""
    reverse_map = {v: k for k, v in _FORM_V1_MAP.items()}
    return reverse_map.get(v1_form, v1_form)


# ---------------------------------------------------------------------------
# Anchor builder
# ---------------------------------------------------------------------------


def _build_anchor(
    scenario: ReceptionScenarioSpec,
    *,
    seed_id: str,
    form_v2: str,
    cell_variant: int,
) -> dict[str, Any]:
    """Build one dialogue-free v2 anchor from a source scenario.

    The semantic_contract is independently derived per the v2 coherence
    model, using the source scenario for entity/temporal/diary base data.
    """
    semantic_contract = _build_semantic_contract(
        scenario, form_v2=form_v2, cell_variant=cell_variant
    )

    dialogue_form_contract = _build_dialogue_form_contract(
        scenario,
        form_v2=form_v2,
        cell_variant=cell_variant,
    )

    # Build anchor WITHOUT seed_hash fields, so we can compute the hash
    # over the complete payload.
    anchor_without_hash = {
        "schema_version": SEED_SCHEMA_VERSION_V2,
        "seed_id": seed_id,
        "source_scenario_id": scenario.scenario_id,
        "source_scenario_hash": compute_scenario_hash(scenario),
        "semantic_contract": semantic_contract,
        "contains_source_utterances": False,
        "authority_grant": dict(_AUTHORITY_ALL_FALSE),
        "required_evidence_keys": sorted(scenario.source_spans),
        "dialogue_form_contract": dialogue_form_contract,
    }

    seed_hash = _sha256(anchor_without_hash)

    # Add seed_hash to both top-level and dialogue_form_contract
    anchor_without_hash["seed_hash"] = seed_hash
    anchor_without_hash["dialogue_form_contract"]["seed_hash"] = seed_hash

    return anchor_without_hash


# ---------------------------------------------------------------------------
# Manifest builder
# ---------------------------------------------------------------------------

import copy


def _strip_seed_hashes(anchor: dict[str, Any]) -> dict[str, Any]:
    """Return a deep copy of anchor with all seed_hash fields removed."""
    cleaned = copy.deepcopy(anchor)
    cleaned.pop("seed_hash", None)
    dfc = cleaned.get("dialogue_form_contract")
    if isinstance(dfc, dict):
        dfc.pop("seed_hash", None)
    return cleaned


def build_v2_anchor_manifest() -> dict[str, Any]:
    """Build the complete v2 anchor manifest with 96 dialogue-free anchors.

    Loads only DevelopmentOnlyLoader().load_all().  Selects exactly 2 source
    scenarios per action/form cell for 96 anchors total.
    """
    corpus = DevelopmentOnlyLoader().load_all()
    sources = _select_anchor_sources(corpus)

    anchors: list[dict[str, Any]] = []
    seed_index = 0

    for action in ACTIONS_V2:
        for form in FORMS_V2:
            cell_sources = sources[(action, form)]

            for cell_variant, scenario in enumerate(cell_sources, start=1):
                seed_index += 1
                seed_id = f"bernie_noise_seed_v2_{seed_index:03d}"
                anchor = _build_anchor(
                    scenario,
                    seed_id=seed_id,
                    form_v2=form,
                    cell_variant=cell_variant,
                )
                anchors.append(anchor)

    if len(anchors) != ANCHOR_COUNT_V2:
        raise RuntimeError(
            f"Expected {ANCHOR_COUNT_V2} anchors, got {len(anchors)}"
        )

    manifest_without_hash = {
        "schema_version": SEED_MANIFEST_SCHEMA_VERSION_V2,
        "corpus": "bernie-receptionist-to-assistant-synthetic-noise-v2",
        "tier": "silver",
        "adjudication": "pending",
        "source_corpus": "lc4-development",
        "source_corpus_hash": corpus.corpus_hash,
        "contains_source_utterances": False,
        "protected_holdout_access": False,
        "historical_diary_access": False,
        "external_corpus_access": False,
        "anchor_count": len(anchors),
        "anchors": anchors,
    }

    return {
        **manifest_without_hash,
        "manifest_hash": _sha256(manifest_without_hash),
    }


def write_v2_anchor_manifest(
    path: Path = DEFAULT_SEED_PATH_V2,
) -> dict[str, Any]:
    """Build and write the v2 anchor manifest to a JSON file."""
    manifest = build_v2_anchor_manifest()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return manifest


# ---------------------------------------------------------------------------
# Coherence validator
# ---------------------------------------------------------------------------


def validate_v2_anchor_manifest(manifest: dict[str, Any]) -> list[str]:
    """Validate the v2 anchor manifest and all anchor invariants.

    Returns a list of error messages (empty if valid).
    """
    errors: list[str] = []

    anchors = manifest.get("anchors")
    if not isinstance(anchors, list) or len(anchors) != ANCHOR_COUNT_V2:
        errors.append(
            f"anchor_count must be {ANCHOR_COUNT_V2}, got "
            f"{len(anchors) if isinstance(anchors, list) else type(anchors).__name__}"
        )
        return errors

    # Access flags on manifest
    for flag in (
        "contains_source_utterances",
        "protected_holdout_access",
        "historical_diary_access",
        "external_corpus_access",
    ):
        if manifest.get(flag) is not False:
            errors.append(f"manifest {flag} must be false")

    if manifest.get("anchor_count") != len(anchors):
        errors.append("anchor_count does not match anchors length")

    # Action and form balance tracking
    action_counts: dict[str, int] = {a: 0 for a in ACTIONS_V2}
    form_counts: dict[str, int] = {f: 0 for f in FORMS_V2}

    seen_ids: set[str] = set()
    seen_hashes: set[str] = set()

    for anchor in anchors:
        seed_id = anchor.get("seed_id")
        if not isinstance(seed_id, str) or seed_id in seen_ids:
            errors.append(f"duplicate or invalid seed_id: {seed_id!r}")
        else:
            seen_ids.add(seed_id)

        # Check seed_hash: compute from anchor minus all seed_hash fields
        supplied_hash = anchor.get("seed_hash")
        anchor_without_hash = _strip_seed_hashes(anchor)
        if supplied_hash != _sha256(anchor_without_hash):
            errors.append(f"seed hash mismatch: {seed_id}")

        # Check for duplicate hashes
        if supplied_hash in seen_hashes:
            errors.append(f"duplicate seed_hash: {seed_id}")
        else:
            seen_hashes.add(supplied_hash)

        # Forbidden fields (no source dialogue)
        forbidden_keys = {"dialogue_turns", "utterance", "description"}
        if forbidden_keys.intersection(anchor):
            errors.append(
                f"source dialogue field leaked into anchor: {seed_id}"
            )

        # Check source_bindings
        dfc = anchor.get("dialogue_form_contract", {})
        source_bindings = dfc.get("source_bindings", {})
        if not source_bindings.get("source_scenario_id"):
            errors.append(f"missing source_scenario_id in {seed_id}")
        if not source_bindings.get("source_scenario_hash"):
            errors.append(f"missing source_scenario_hash in {seed_id}")

        # Authority all false
        auth = anchor.get("authority_grant", {})
        if any(auth.values()):
            errors.append(f"authority_grant must be all false: {seed_id}")

        # contains_source_utterances must be false per anchor
        if anchor.get("contains_source_utterances") is not False:
            errors.append(
                f"contains_source_utterances must be false: {seed_id}"
            )

        # Semantic contract checks
        sc = anchor.get("semantic_contract", {})
        if not isinstance(sc, dict):
            errors.append(f"semantic_contract missing in {seed_id}")
            continue

        intended_action = sc.get("intended_action")
        if intended_action in action_counts:
            action_counts[intended_action] += 1

        # Check form balance from dialogue_form_contract
        df_form = dfc.get("dialogue_form")
        if df_form in form_counts:
            form_counts[df_form] += 1

        # ---- Coherence invariants ----
        action = sc.get("intended_action")
        tools = sc.get("expected_tool_sequence", [])
        outcome = sc.get("expected_outcome_kind")
        apt_deltas = sc.get("expected_appointment_deltas", [])
        audit_deltas = sc.get("expected_audit_deltas", [])
        clarification = sc.get("expected_clarification")
        choices = sc.get("clarification_choices", [])
        withdrawn = sc.get("action_withdrawn", False)

        is_schedule = action == "explain_schedule"
        is_clarification_form = df_form == "clarification"
        is_reversal_form = df_form == "reversal"

        # Check action_withdrawn matches form
        if is_reversal_form and not withdrawn:
            errors.append(
                f"reversal anchor must have action_withdrawn=true: {seed_id}"
            )
        if not is_reversal_form and withdrawn:
            errors.append(
                "non-reversal anchor must have "
                f"action_withdrawn=false: {seed_id}"
            )

        # Mutation check (non-schedule, non-clarification, non-reversal)
        if (
            not is_schedule
            and not is_clarification_form
            and not is_reversal_form
        ):
            if not tools:
                errors.append(
                    "successful mutation requires non-empty tool "
                    f"sequence: {seed_id}"
                )
            if outcome is None:
                errors.append(
                    "successful mutation requires non-null "
                    f"outcome: {seed_id}"
                )
            if action != "explain_schedule" and not apt_deltas:
                errors.append(
                    "mutation action requires non-empty appointment "
                    f"deltas: {seed_id}"
                )
            if action != "explain_schedule" and not audit_deltas:
                errors.append(
                    "mutation action requires non-empty audit "
                    f"deltas: {seed_id}"
                )

        # Schedule explanation check (not applicable for clarification or
        # reversal forms which have their own coherence model)
        if is_schedule and not is_clarification_form and not is_reversal_form:
            if not tools:
                errors.append(
                    "schedule explanation requires non-empty tool "
                    f"sequence: {seed_id}"
                )
            if outcome != "schedule_explained":
                errors.append(
                    "schedule explanation must have "
                    f"outcome=schedule_explained: {seed_id}"
                )
            if apt_deltas:
                errors.append(
                    "schedule explanation must have empty appointment "
                    f"deltas: {seed_id}"
                )
            if audit_deltas:
                errors.append(
                    "schedule explanation must have empty audit "
                    f"deltas: {seed_id}"
                )

        # Clarification check
        if is_clarification_form:
            if not clarification:
                errors.append(
                    "clarification requires non-null clarification "
                    f"question: {seed_id}"
                )
            if len(choices) < 2:
                errors.append(
                    "clarification requires at least 2 "
                    f"choices: {seed_id}"
                )
            if tools != ["request_clarification"]:
                errors.append(
                    "clarification must have sole tool "
                    f"request_clarification: {seed_id}"
                )
            if outcome != "clarification_required":
                errors.append(
                    "clarification must have outcome "
                    f"clarification_required: {seed_id}"
                )
            if apt_deltas:
                errors.append(
                    "clarification must have empty appointment "
                    f"deltas: {seed_id}"
                )
            if audit_deltas:
                errors.append(
                    "clarification must have empty audit "
                    f"deltas: {seed_id}"
                )
            if withdrawn:
                errors.append(
                    "clarification must have "
                    f"action_withdrawn=false: {seed_id}"
                )

        # Reversal check
        if is_reversal_form:
            if outcome is not None:
                errors.append(f"reversal must have null outcome: {seed_id}")
            if apt_deltas:
                errors.append(
                    "reversal must have empty appointment "
                    f"deltas: {seed_id}"
                )
            if audit_deltas:
                errors.append(
                    "reversal must have empty audit deltas: {seed_id}"
                )
            # Check tool expectation
            patient_sem = sc.get("patient_semantics")
            if patient_sem == "exact":
                expected_tools = ["search_patients"]
            else:
                expected_tools = []
            if tools != expected_tools:
                errors.append(
                    f"reversal tool expectation mismatch for {seed_id}: "
                    f"expected {expected_tools}, got {tools}"
                )

        # Correction check
        if df_form == "correction":
            if not tools:
                errors.append(
                    "correction requires non-empty tool "
                    f"sequence: {seed_id}"
                )
            if outcome is None:
                errors.append(
                    "correction requires non-null outcome: {seed_id}"
                )

        # Ellipsis/anaphora/repeated/session_restart
        if df_form in (
            "ellipsis",
            "anaphora",
            "repeated_request",
            "session_restart",
        ):
            if not tools:
                errors.append(
                    f"{df_form} requires non-empty tool "
                    f"sequence: {seed_id}"
                )
            if outcome is None:
                errors.append(
                    f"{df_form} requires non-null outcome: {seed_id}"
                )
            if action != "explain_schedule" and not apt_deltas:
                errors.append(
                    f"{df_form} requires non-empty appointment "
                    f"deltas: {seed_id}"
                )

    # Balance validation
    for action, count in action_counts.items():
        expected = 16  # 8 forms * 2 anchors
        if count != expected:
            errors.append(
                f"action {action!r} has {count} anchors, "
                f"expected {expected}"
            )

    for form, count in form_counts.items():
        expected = 12  # 6 actions * 2 anchors
        if count != expected:
            errors.append(
                f"form {form!r} has {count} anchors, expected {expected}"
            )

    # Manifest hash
    manifest_without_hash = {
        k: v for k, v in manifest.items() if k != "manifest_hash"
    }
    if manifest.get("manifest_hash") != _sha256(manifest_without_hash):
        errors.append("manifest hash mismatch")

    return errors


def check_v2_anchor_manifest(
    path: Path = DEFAULT_SEED_PATH_V2,
) -> list[str]:
    """Read the committed fixture and validate it.

    Returns a list of error messages (empty if valid).
    """
    if not path.is_file():
        return [f"Fixture file not found: {path}"]

    manifest = json.loads(path.read_text(encoding="utf-8"))
    return validate_v2_anchor_manifest(manifest)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

__all__ = [
    "SEED_SCHEMA_VERSION_V2",
    "SEED_MANIFEST_SCHEMA_VERSION_V2",
    "ANCHOR_COUNT_V2",
    "DEFAULT_SEED_PATH_V2",
    "ACTIONS_V2",
    "FORMS_V2",
    "build_v2_anchor_manifest",
    "write_v2_anchor_manifest",
    "validate_v2_anchor_manifest",
    "check_v2_anchor_manifest",
]
