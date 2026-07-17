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

from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any

from app.services.bernie.corpus_tier import compute_scenario_hash
from app.services.bernie.scale_corpus import DevelopmentOnlyLoader
from app.services.bernie.scenario_spec import ReceptionScenarioSpec

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

_AUTHORITY_ALL_FALSE: dict[str, bool] = {
    "provider_write": False,
    "diary_write": False,
    "confirmation": False,
    "override_authority": False,
}

_ACTION_OUTCOMES: dict[str, str] = {
    "create": "appointment_created",
    "move": "appointment_moved",
    "resize": "appointment_resized",
    "cancel": "appointment_cancelled",
    "status_change": "appointment_status_changed",
    "explain_schedule": "schedule_explained",
}

_ACTION_TOOLS: dict[str, list[str]] = {
    "create": ["search_patients", "find_slots", "create_booking"],
    "move": ["search_patients", "update_appointment"],
    "resize": ["search_patients", "update_appointment"],
    "cancel": ["search_patients", "update_appointment"],
    "status_change": ["search_patients", "change_appointment_status"],
    "explain_schedule": ["search_patients", "find_slots"],
}

_EXECUTABLE_NON_CREATE_STATES = {
    "empty",
    "exact_duplicate",
    "overlap",
    "same_day_distinct",
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
    """Select coherent provenance bases independently of their dialogue form.

    Source dialogue is never copied. Each base must already have exact entity
    semantics and a coherent successful action-specific policy/replay shape.
    V2 then freezes its own dialogue-form meaning over that base. A small pool
    may be reused deterministically; seed identity and form contracts remain
    unique.
    """

    pools: dict[str, list[ReceptionScenarioSpec]] = {}
    for action in ACTIONS_V2:
        eligible = sorted(
            (
                scenario
                for scenario in corpus.all_variants()
                if _source_is_eligible(scenario, action)
            ),
            key=lambda scenario: scenario.scenario_id,
        )
        if not eligible:
            raise RuntimeError(f"No coherent development source for {action}")
        pools[action] = eligible

    result: dict[tuple[str, str], list[ReceptionScenarioSpec]] = {}
    for action in ACTIONS_V2:
        pool = pools[action]
        for form_index, form_v2 in enumerate(FORMS_V2):
            offset = form_index * 2
            result[(action, form_v2)] = [
                pool[offset % len(pool)],
                pool[(offset + 1) % len(pool)],
            ]
    return result


def _source_is_eligible(
    scenario: ReceptionScenarioSpec, action: str
) -> bool:
    patient_is_coherent = (
        scenario.patient_semantics == "omitted"
        if action == "explain_schedule"
        else scenario.patient_semantics == "exact"
    )
    deltas_are_coherent = (
        not scenario.expected_appointment_deltas
        and not scenario.expected_audit_deltas
        if action == "explain_schedule"
        else bool(scenario.expected_appointment_deltas)
        and bool(scenario.expected_audit_deltas)
    )
    return bool(
        scenario.intended_action == action
        and scenario.action_semantics == "intended"
        # Non-clarification create cells model executable requests. Approximate
        # create targets are intentionally fail-closed by the product.
        and (action != "create" or scenario.temporal_relation == "exact")
        and (
            action in {"create", "explain_schedule"}
            or scenario.diary_state in _EXECUTABLE_NON_CREATE_STATES
        )
        and scenario.entity_state == "exact"
        and patient_is_coherent
        and scenario.practitioner_semantics == "exact"
        and scenario.expected_clarification is None
        and scenario.expected_outcome_kind == _ACTION_OUTCOMES[action]
        and scenario.expected_tool_sequence == _ACTION_TOOLS[action]
        and deltas_are_coherent
    )


# ---------------------------------------------------------------------------
# Semantic contract builder
# ---------------------------------------------------------------------------


def _build_semantic_contract(
    scenario: ReceptionScenarioSpec,
    *,
    form_v2: str,
    cell_variant: int,
) -> dict[str, Any]:
    """Build the independent coherent oracle for one v2 dialogue form."""
    action = scenario.intended_action
    is_clarification = form_v2 == "clarification"
    is_reversal = form_v2 == "reversal"
    is_schedule = action == "explain_schedule"

    earliest_time = scenario.earliest_time
    latest_time = scenario.latest_time
    if (
        scenario.temporal_relation == "approximate"
        and earliest_time is not None
        and latest_time is not None
    ):
        lower_minutes = int(earliest_time[:2]) * 60 + int(earliest_time[3:])
        upper_minutes = int(latest_time[:2]) * 60 + int(latest_time[3:])
        midpoint = (lower_minutes + upper_minutes) // 2
        lower = max(0, midpoint - 30)
        upper = min(23 * 60 + 59, midpoint + 30)
        earliest_time = f"{lower // 60:02d}:{lower % 60:02d}"
        latest_time = f"{upper // 60:02d}:{upper % 60:02d}"

    # Freeze only values the generated dialogue will actually surface. Source
    # scenarios provide provenance and temporal facts, not a replay oracle.
    normalized_values = {
        "appointment_date": scenario.normalized_values["appointment_date"],
    }
    if earliest_time is not None:
        normalized_values["earliest_time"] = earliest_time
    if latest_time is not None:
        normalized_values["latest_time"] = latest_time
    if action in {"create", "resize"}:
        normalized_values["duration_minutes"] = scenario.duration_minutes or 15

    if is_clarification:
        outcome = "clarification_required"
    elif is_reversal:
        outcome = None
    else:
        outcome = scenario.expected_outcome_kind

    if is_clarification:
        tools = ["request_clarification"]
    elif is_reversal:
        tools = [] if is_schedule else ["search_patients"]
    elif is_schedule:
        tools = ["find_slots"]
    else:
        tools = list(_ACTION_TOOLS[action])

    apt_deltas: list[dict[str, Any]] = []
    audit_deltas: list[dict[str, Any]] = []
    if not is_clarification and not is_reversal and not is_schedule:
        change_type = {
            "create": "created",
            "move": "moved",
            "resize": "resized",
            "cancel": "cancelled",
            "status_change": "status_changed",
        }[action]
        apt_deltas = [{
            "appointment_id": "apt-001",
            "change_type": change_type,
            "patient_id": "p-001",
            "practitioner_id": "pr-001",
            "date": normalized_values["appointment_date"],
            "start_time": normalized_values.get("earliest_time", ""),
            "duration_minutes": normalized_values.get("duration_minutes", 15),
        }]
        audit_deltas = [{
            "change_type": change_type,
            "appointment_id": "apt-001",
            "count": 1,
        }]

    patient_semantics = scenario.patient_semantics
    practitioner_semantics = scenario.practitioner_semantics
    entity_state = scenario.entity_state
    if is_clarification:
        entity_state = "ambiguous"
        if cell_variant == 1 and not is_schedule:
            patient_semantics = "ambiguous"
            practitioner_semantics = "exact"
            clar_question = (
                "Please clarify: which patient is this appointment for?"
            )
            clar_choices = [
                "Margaret Thompson",
                "Robert Johnson",
            ]
        else:
            patient_semantics = "omitted" if is_schedule else "exact"
            practitioner_semantics = "ambiguous"
            clar_question = (
                "Please clarify: which practitioner should the appointment "
                "be booked with?"
            )
            clar_choices = [
                "Dr Shera",
                "Dr Patel",
            ]
    else:
        clar_question = None
        clar_choices = []

    if form_v2 == "correction":
        practitioner_semantics = "corrected"
        entity_state = "corrected"
    elif is_reversal:
        entity_state = "negated"

    contract: dict[str, Any] = {
        "reference_date": scenario.reference_date.isoformat(),
        "clinic_clock": scenario.clinic_clock.isoformat(),
        "intended_action": scenario.intended_action,
        "action_semantics": "ambiguous" if is_clarification else "intended",
        "temporal_relation": scenario.temporal_relation,
        "earliest_time": earliest_time,
        "latest_time": latest_time,
        "normalized_values": normalized_values,
        "duration_minutes": scenario.duration_minutes if action in {"create", "resize"} else None,
        "patient_semantics": patient_semantics,
        "practitioner_semantics": practitioner_semantics,
        "location_semantics": scenario.location_semantics,
        "appointment_type_semantics": scenario.appointment_type_semantics,
        "duration_semantics": "exact" if action in {"create", "resize"} else "omitted",
        "diary_state": scenario.diary_state,
        "entity_state": entity_state,
        "initial_diary_state": deepcopy(scenario.initial_diary_state),
        "expected_outcome_kind": outcome,
        "expected_tool_sequence": tools,
        "expected_appointment_deltas": apt_deltas,
        "expected_audit_deltas": audit_deltas,
        "forbidden_outcomes": list(scenario.forbidden_outcomes),
        "forbidden_tool_calls": list(scenario.forbidden_tool_calls),
        "expected_clarification": clar_question,
        "clarification_choices": clar_choices,
        "action_withdrawn": is_reversal,
    }
    return contract


def _build_dialogue_form_contract(
    scenario: ReceptionScenarioSpec,
    *,
    form_v2: str,
    cell_variant: int,
) -> dict[str, Any]:
    """Freeze the evidence that candidate dialogue must surface locally."""
    action = scenario.intended_action
    is_schedule = action == "explain_schedule"
    ambiguity_target: str | None = None
    correction_target: str | None = None
    prior_value: str | None = None
    final_value: str | None = None

    requirements: dict[str, list[str]] = {
        "one_shot": ["complete_request_in_single_turn"],
        "clarification": [
            "explicit_action",
            "explicit_unresolved_ambiguity",
            "clarification_remains_unresolved",
        ],
        "correction": [
            "initial_practitioner_value",
            "explicit_replacement_cue",
            "final_practitioner_value",
        ],
        "reversal": [
            "initial_complete_request",
            "explicit_whole_action_withdrawal",
        ],
        "ellipsis": ["antecedent_in_prior_turn", "locally_recoverable_ellipsis"],
        "anaphora": ["antecedent_in_prior_turn", "locally_resolved_anaphora"],
        "repeated_request": ["complete_request", "same_request_repeated_once"],
        "session_restart": [
            "explicit_prior_request_abandonment",
            "complete_fresh_request",
        ],
    }
    if form_v2 == "clarification":
        ambiguity_target = (
            "patient" if cell_variant == 1 and not is_schedule else "practitioner"
        )
        requirements[form_v2].append(f"explicit_{ambiguity_target}_ambiguity")
    elif form_v2 == "correction":
        correction_target = "practitioner"
        prior_value = "Dr Patel"
        final_value = "Dr Shera"

    return {
        "dialogue_form": form_v2,
        "minimum_turns": 1 if form_v2 == "one_shot" else 2,
        "surface_requirements": requirements[form_v2],
        "ambiguity_target": ambiguity_target,
        "correction_target": correction_target,
        "prior_value": prior_value,
        "final_value": final_value,
        "local_recovery_required": form_v2 in {"ellipsis", "anaphora"},
        "whole_action_withdrawn": form_v2 == "reversal",
        "authority_grant": dict(_AUTHORITY_ALL_FALSE),
        "source_bindings": {
            "source_scenario_id": scenario.scenario_id,
            "source_scenario_hash": compute_scenario_hash(scenario),
        },
        "cell_variant": cell_variant,
    }


def _required_evidence_keys(
    scenario: ReceptionScenarioSpec, form_v2: str
) -> list[str]:
    keys = {"intended_action", "appointment_date", "practitioner"}
    if scenario.intended_action != "explain_schedule":
        keys.add("patient")
    if scenario.temporal_relation != "unspecified":
        keys.add("temporal_relation")
    if scenario.intended_action in {"create", "resize"}:
        keys.add("duration_minutes")
    if scenario.intended_action == "status_change":
        keys.add("status")
    if form_v2 != "one_shot":
        keys.add("dialogue_transition")
    return sorted(keys)


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
        "required_evidence_keys": _required_evidence_keys(scenario, form_v2),
        "dialogue_form_contract": dialogue_form_contract,
    }

    seed_hash = _sha256(anchor_without_hash)
    anchor_without_hash["seed_hash"] = seed_hash

    return anchor_without_hash


# ---------------------------------------------------------------------------
# Manifest builder
# ---------------------------------------------------------------------------

def _strip_seed_hashes(anchor: dict[str, Any]) -> dict[str, Any]:
    """Return a deep copy of anchor with the top-level seed hash removed."""
    cleaned = deepcopy(anchor)
    cleaned.pop("seed_hash", None)
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

    corpus = DevelopmentOnlyLoader().load_all()
    source_lookup = {
        scenario.scenario_id: scenario
        for scenario in corpus.all_variants()
    }
    if manifest.get("source_corpus_hash") != corpus.corpus_hash:
        errors.append("source_corpus_hash does not match ordinary development")

    # Action and form balance tracking
    action_counts: dict[str, int] = {a: 0 for a in ACTIONS_V2}
    form_counts: dict[str, int] = {f: 0 for f in FORMS_V2}
    cell_counts: dict[tuple[str, str], int] = {}

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
        source_id = anchor.get("source_scenario_id")
        source = source_lookup.get(source_id)
        if source is None:
            errors.append(f"unknown ordinary-development source: {seed_id}")
        else:
            expected_source_hash = compute_scenario_hash(source)
            if anchor.get("source_scenario_hash") != expected_source_hash:
                errors.append(f"source scenario hash mismatch: {seed_id}")
            if source_bindings != {
                "source_scenario_id": source_id,
                "source_scenario_hash": expected_source_hash,
            }:
                errors.append(f"source binding mismatch: {seed_id}")

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
        if intended_action in action_counts and df_form in form_counts:
            cell = (intended_action, df_form)
            cell_counts[cell] = cell_counts.get(cell, 0) + 1

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

        if source is not None:
            if not _source_is_eligible(source, str(action)):
                errors.append(f"source is not a coherent provenance base: {seed_id}")
            if action != source.intended_action:
                errors.append(f"source action mismatch: {seed_id}")

        expected_required = (
            _required_evidence_keys(source, str(df_form))
            if source is not None and df_form in FORMS_V2
            else []
        )
        if anchor.get("required_evidence_keys") != expected_required:
            errors.append(f"required evidence mismatch: {seed_id}")

        cell_variant = dfc.get("cell_variant")
        if cell_variant not in {1, 2}:
            errors.append(f"cell_variant must be 1 or 2: {seed_id}")
        elif source is not None and df_form in FORMS_V2:
            expected_semantic = _build_semantic_contract(
                source,
                form_v2=str(df_form),
                cell_variant=cell_variant,
            )
            if sc != expected_semantic:
                errors.append(f"semantic contract mismatch: {seed_id}")
            expected_form_contract = _build_dialogue_form_contract(
                source,
                form_v2=str(df_form),
                cell_variant=cell_variant,
            )
            if dfc != expected_form_contract:
                errors.append(f"dialogue form contract mismatch: {seed_id}")

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
            ambiguity_target = dfc.get("ambiguity_target")
            if is_schedule:
                if (
                    ambiguity_target != "practitioner"
                    or sc.get("patient_semantics") != "omitted"
                    or sc.get("practitioner_semantics") != "ambiguous"
                ):
                    errors.append(
                        f"schedule clarification must surface practitioner ambiguity: {seed_id}"
                    )
            elif cell_variant == 1:
                if (
                    ambiguity_target != "patient"
                    or sc.get("patient_semantics") != "ambiguous"
                    or sc.get("practitioner_semantics") != "exact"
                ):
                    errors.append(
                        f"clarification variant 1 must surface patient ambiguity: {seed_id}"
                    )
            elif (
                ambiguity_target != "practitioner"
                or sc.get("patient_semantics") != "exact"
                or sc.get("practitioner_semantics") != "ambiguous"
            ):
                errors.append(
                    f"clarification variant 2 must surface practitioner ambiguity: {seed_id}"
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
            expected_tools = [] if is_schedule else ["search_patients"]
            if tools != expected_tools:
                errors.append(
                    f"reversal tool expectation mismatch for {seed_id}: "
                    f"expected {expected_tools}, got {tools}"
                )
            if sc.get("entity_state") != "negated":
                errors.append(f"reversal entity state must be negated: {seed_id}")
            if dfc.get("whole_action_withdrawn") is not True:
                errors.append(f"reversal form contract must withdraw action: {seed_id}")

        # Correction check
        if df_form == "correction":
            if not tools:
                errors.append(
                    "correction requires non-empty tool "
                    f"sequence: {seed_id}"
                )
            if outcome is None:
                errors.append(
                    f"correction requires non-null outcome: {seed_id}"
                )
            if (
                sc.get("practitioner_semantics") != "corrected"
                or sc.get("entity_state") != "corrected"
                or dfc.get("correction_target") != "practitioner"
                or not dfc.get("prior_value")
                or not dfc.get("final_value")
            ):
                errors.append(
                    f"correction must freeze explicit practitioner replacement: {seed_id}"
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

    for action in ACTIONS_V2:
        for form in FORMS_V2:
            if cell_counts.get((action, form), 0) != 2:
                errors.append(
                    f"cell ({action}, {form}) must contain exactly 2 anchors"
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
    errors = validate_v2_anchor_manifest(manifest)
    if manifest != build_v2_anchor_manifest():
        errors.append("committed v2 anchor manifest does not regenerate exactly")
    return errors


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
