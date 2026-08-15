"""Standard-library-only deterministic risk-weighted Ariadne workflow core.

This module is deliberately pure. It reads only Python objects supplied by
callers, executes no command, opens no database, contacts no provider and never
mutates Git, AGENTS, Continuity, Compass, the latch or any protected ref. It
implements the frozen contract in ``docs/ariadne-risk-weighted-workflow-reform-plan.md``
and ``docs/security/ariadne-risk-weighted-workflow-reform-threat-model-delta.md``:

* validates the exact typed tranche profile and result structures;
* derives the highest applicable risk tier (callers cannot lower it);
* computes the required baseline, deterministic gates and final vetoes;
* validates semantic versus volatile bindings;
* returns the union change-triggered rerun decision;
* verifies named-threat coverage, incident grouping and safe tail deferral;
* admits a result only when its tier-required evidence is complete.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

PROFILE_SCHEMA_VERSION = "ariadne.risk_weighted_tranche_profile.v1"
RESULT_SCHEMA_VERSION = "ariadne.risk_weighted_tranche_result.v1"
DIGEST_PATTERN = "sha256:[0-9a-f]{64}"

TIER_0_METADATA = "tier_0_metadata"
TIER_1_PROVIDER_FREE_SOURCE = "tier_1_provider_free_source"
TIER_2_AUTHORITY_RUNTIME = "tier_2_authority_runtime"
TIER_3_OCCUPIED_PROTECTED = "tier_3_occupied_protected"
TIER_ORDER = (
    TIER_0_METADATA,
    TIER_1_PROVIDER_FREE_SOURCE,
    TIER_2_AUTHORITY_RUNTIME,
    TIER_3_OCCUPIED_PROTECTED,
)

ALL_TIER_NAMES = frozenset(TIER_ORDER)

# Closed change families from the frozen rerun matrix.
CHANGE_FAMILIES = frozenset(
    {
        "product",
        "harness",
        "policy",
        "schema",
        "migration",
        "semantic_test",
        "verifier_command_manifest",
        "documentation_or_closeout_prose",
        "continuity_compass_baton_metadata",
        "receipt_runtime_state",
        "agent_error_register",
    }
)
SEMANTIC_FAMILIES = frozenset(
    {
        "product",
        "harness",
        "policy",
        "schema",
        "migration",
        "semantic_test",
    }
)

# Exact rerun requirements per post-freeze change family (union for mixed).
RERUN_BY_FAMILY: dict[str, tuple[str, ...]] = {
    "product": (
        "focused_semantic_gates",
        "canonical_final_profile",
        "invalidate_earlier_verifier_result",
    ),
    "harness": (
        "focused_semantic_gates",
        "canonical_final_profile",
        "invalidate_earlier_verifier_result",
    ),
    "policy": (
        "focused_semantic_gates",
        "canonical_final_profile",
        "invalidate_earlier_verifier_result",
    ),
    "schema": (
        "focused_semantic_gates",
        "canonical_final_profile",
        "invalidate_earlier_verifier_result",
    ),
    "migration": (
        "focused_semantic_gates",
        "canonical_final_profile",
        "invalidate_earlier_verifier_result",
    ),
    "semantic_test": (
        "focused_semantic_gates",
        "canonical_final_profile",
        "invalidate_earlier_verifier_result",
    ),
    "verifier_command_manifest": (
        "manifest_validation",
        "verifier_worktree_path_preflight",
    ),
    "documentation_or_closeout_prose": ("document_metadata_link_whitespace",),
    "continuity_compass_baton_metadata": ("continuity_compass_baton",),
    "receipt_runtime_state": ("receipt_preflight",),
    "agent_error_register": ("register_schema_pattern",),
}

ALL_RERUN_ITEMS = frozenset({item for items in RERUN_BY_FAMILY.values() for item in items})
# A rerun item may be satisfied by a deterministic gate with the same category.
RERUN_ITEM_TO_GATE_CATEGORY: dict[str, str] = {
    "focused_semantic_gates": "focused_semantic_gates",
    "canonical_final_profile": "canonical_final_profile",
    "manifest_validation": "manifest_validation",
    "verifier_worktree_path_preflight": "verifier_worktree_path_preflight",
    "document_metadata_link_whitespace": "document_metadata_link_whitespace",
    "continuity_compass_baton": "continuity_compass_baton",
    "receipt_preflight": "receipt_preflight",
    "register_schema_pattern": "register_schema_pattern",
}
GATE_CATEGORIES = frozenset(RERUN_ITEM_TO_GATE_CATEGORY.values())
# invalidate_earlier_verifier_result has no gate category; it is a bookkeeping
# rerun requirement that forces earlier verifier results to be ignored.

TIER1_SIGNALS = frozenset({"provider_free_source_edit"})
TIER2_SIGNALS = frozenset(
    {
        "workflow_policy_change",
        "database_runtime",
        "authority_or_security_contract",
        "executable_tool",
        "network_capability",
        "operational_product_derived_data",
        "migration_representation",
        "migration_execution",
        "product_command_or_write",
    }
)
TIER3_SIGNALS = frozenset(
    {
        "patient_or_clinical_data",
        "occupied_provider_call",
        "credentials_or_iam",
        "deployment_production_release_pages",
        "protected_ref_movement",
    }
)
ALL_SIGNALS = frozenset(
    {"docs_only", "unmounted"} | TIER1_SIGNALS | TIER2_SIGNALS | TIER3_SIGNALS
)

SEMANTIC_KINDS = frozenset({"source", "contract", "policy", "schema", "semantic_test"})
VOLATILE_KINDS = frozenset(
    {
        "receipt",
        "timestamp",
        "latch_snapshot",
        "generated_closeout",
        "mailbox_message",
        "baton_prose",
    }
)

REVIEW_TRIGGER_KEYS = frozenset(
    {
        "new_authority_or_security_boundary",
        "prior_substantive_rejection",
        "ambiguous_hard_boundary",
        "explicit_risk_trigger",
    }
)

PARALLELISM_LANE_KEYS = frozenset({"deepseek_lane", "gemini_lane", "native_lane"})

HARD_DEFECT_FLAGS = frozenset(
    {
        "safety_relevant",
        "authority_relevant",
        "integrity_relevant",
        "privacy_relevant",
        "atomicity_relevant",
        "protected_evidence_relevant",
        "irreversible_effect_relevant",
    }
)


def _object(value: object, *, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a JSON object")
    return value


def _exact_keys(value: dict[str, Any], expected: set[str], *, label: str) -> None:
    if set(value) != expected:
        raise ValueError(
            f"{label} keys must be exact: expected={sorted(expected)!r} "
            f"observed={sorted(value)!r}"
        )


def _require_keys(value: dict[str, Any], required: set[str], *, label: str) -> None:
    missing = required - set(value)
    if missing:
        raise ValueError(f"{label} is missing required keys: {sorted(missing)!r}")


def _enum(value: object, allowed: frozenset[str] | set[str], *, label: str) -> None:
    if value not in allowed:
        raise ValueError(f"{label} is not admitted: {value!r}")


def _bool(value: object, *, label: str) -> bool:
    if not isinstance(value, bool):
        raise ValueError(f"{label} must be a boolean")
    return value


def _digest(value: object, *, label: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{label} must be a sha256 digest string")
    if not len(value) == len("sha256:") + 64 or not value.startswith("sha256:"):
        raise ValueError(f"{label} must be a sha256 digest")
    if any(char not in "0123456789abcdef" for char in value[len("sha256:"):]):
        raise ValueError(f"{label} must be a lowercase sha256 digest")
    return value


def _nonempty_string(value: object, *, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a non-empty string")
    return value


_HEX40 = frozenset("0123456789abcdef")


def _hex40(value: object, *, label: str) -> str:
    if not isinstance(value, str) or len(value) != 40:
        raise ValueError(f"{label} must be a 40-character lowercase source id")
    if any(char not in _HEX40 for char in value):
        raise ValueError(f"{label} must contain only lowercase hex characters")
    return value


def _list_of(value: object, *, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise ValueError(f"{label} must be an array")
    return value


def _string_list(
    value: object,
    *,
    label: str,
    minimum: int = 0,
    maximum: int = 256,
) -> list[str]:
    entries = _list_of(value, label=label)
    if not minimum <= len(entries) <= maximum:
        raise ValueError(f"{label} must contain {minimum}..{maximum} entries")
    normalized: list[str] = []
    observed: set[str] = set()
    for index, raw in enumerate(entries):
        item = _nonempty_string(raw, label=f"{label}[{index}]")
        if item in observed:
            raise ValueError(f"{label}[{index}] duplicates {item!r}")
        observed.add(item)
        normalized.append(item)
    return normalized


def _canonical_bytes(value: object) -> bytes:
    return (
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    ).encode("utf-8")


def profile_sha256(profile: dict[str, Any]) -> str:
    """Return the canonical SHA-256 digest of an admitted profile object."""
    validate_profile(profile)
    return "sha256:" + hashlib.sha256(_canonical_bytes(profile)).hexdigest()


def canonical_pass_fingerprint(profile: dict[str, Any]) -> str:
    """Bind the stable inputs that permit reuse of one canonical pass.

    Volatile receipts, timestamps, closeout paths and baton prose are
    intentionally excluded. Any semantic source, binding, focused-gate,
    baseline, threat or toolchain drift changes this digest.
    """
    normalized = validate_profile(profile)
    stable_inputs = {
        "baseline": normalized["baseline"],
        "change_families": normalized["change_families"],
        "change_signals": normalized["change_signals"],
        "semantic_bindings": normalized["semantic_bindings"],
        "semantic_freeze": normalized["semantic_freeze"],
        "threat_ids": normalized["threat_ids"],
    }
    return "sha256:" + hashlib.sha256(_canonical_bytes(stable_inputs)).hexdigest()


def _validate_change_signals(value: dict[str, Any]) -> dict[str, bool]:
    _exact_keys(value, set(ALL_SIGNALS), label="change_signals")
    return {key: _bool(value[key], label=f"change_signals.{key}") for key in value}


def _validate_change_families(value: object, *, label: str) -> list[str]:
    families = _list_of(value, label=label)
    if not 1 <= len(families) <= 16:
        raise ValueError(f"{label} must contain 1..16 families")
    normalized: list[str] = []
    for index, family in enumerate(families):
        if not isinstance(family, str) or family not in CHANGE_FAMILIES:
            raise ValueError(f"{label}[{index}] is not an admitted change family")
        if family in normalized:
            raise ValueError(f"{label}[{index}] duplicates family {family!r}")
        normalized.append(family)
    return normalized


def _validate_binding_list(value: object, kinds: frozenset[str], *, label: str) -> list[dict[str, str]]:
    entries = _list_of(value, label=label)
    if len(entries) > 256:
        raise ValueError(f"{label} must contain at most 256 entries")
    normalized: list[dict[str, str]] = []
    observed_paths: set[str] = set()
    for index, entry in enumerate(entries):
        item = _object(entry, label=f"{label}[{index}]")
        _exact_keys(item, {"path", "kind"}, label=f"{label}[{index}]")
        path = _nonempty_string(item["path"], label=f"{label}[{index}].path")
        if path in observed_paths:
            raise ValueError(f"{label}[{index}] duplicates path {path!r}")
        observed_paths.add(path)
        kind = item["kind"]
        if not isinstance(kind, str) or kind not in kinds:
            raise ValueError(f"{label}[{index}].kind is not admitted: {kind!r}")
        normalized.append({"path": path, "kind": kind})
    return normalized


def _derive_tier(
    signals: dict[str, bool],
    families: set[str],
    review_triggers: dict[str, bool],
) -> str:
    """Derive the highest applicable tier; callers cannot choose or lower it."""
    if any(signals.get(key) for key in TIER3_SIGNALS):
        return TIER_3_OCCUPIED_PROTECTED
    if any(signals.get(key) for key in TIER2_SIGNALS):
        return TIER_2_AUTHORITY_RUNTIME
    if review_triggers["new_authority_or_security_boundary"]:
        return TIER_2_AUTHORITY_RUNTIME
    if "migration" in families:
        return TIER_2_AUTHORITY_RUNTIME
    if any(signals.get(key) for key in TIER1_SIGNALS) or bool(families & SEMANTIC_FAMILIES):
        return TIER_1_PROVIDER_FREE_SOURCE
    if any(review_triggers.values()):
        return TIER_1_PROVIDER_FREE_SOURCE
    return TIER_0_METADATA


def _check_contradictions(signals: dict[str, bool], families: set[str]) -> None:
    docs_only = signals.get("docs_only", False)
    unmounted = signals.get("unmounted", False)
    any_scope_signal = any(
        signals.get(key) for key in set(ALL_SIGNALS) - {"docs_only", "unmounted"}
    )
    if docs_only and (any_scope_signal or bool(families & SEMANTIC_FAMILIES)):
        raise ValueError(
            "docs_only contradicts executable/product/policy/authority/provider scope"
        )
    tier2_or_3 = any(signals.get(key) for key in (TIER2_SIGNALS | TIER3_SIGNALS))
    if unmounted and (tier2_or_3 or "migration" in families):
        raise ValueError(
            "unmounted contradicts database/authority/provider/migration scope"
        )


def _validate_baseline(
    value: object, *, label: str
) -> dict[str, Any]:
    baseline = _object(value, label=label)
    _require_keys(
        baseline,
        {"fingerprint_sha256", "result", "known_failure_ids", "captured_before_first_edit"},
        label=label,
    )
    if set(baseline) - {
        "fingerprint_sha256",
        "result",
        "known_failure_ids",
        "captured_before_first_edit",
    }:
        raise ValueError(f"{label} has unexpected keys")
    _digest(baseline["fingerprint_sha256"], label=f"{label}.fingerprint_sha256")
    _enum(
        baseline["result"],
        {"passed", "passed_with_known_failures", "not_required"},
        label=f"{label}.result",
    )
    normalized_known = _string_list(
        baseline["known_failure_ids"], label=f"{label}.known_failure_ids"
    )
    _bool(baseline["captured_before_first_edit"], label=f"{label}.captured_before_first_edit")
    return {
        "fingerprint_sha256": baseline["fingerprint_sha256"],
        "result": baseline["result"],
        "known_failure_ids": normalized_known,
        "captured_before_first_edit": baseline["captured_before_first_edit"],
    }


def _validate_semantic_freeze(value: object, *, label: str) -> dict[str, Any]:
    freeze = _object(value, label=label)
    _require_keys(
        freeze,
        {
            "source_head",
            "source_tree",
            "semantic_bindings_sha256",
            "toolchain_sha256",
            "focused_gate_results",
        },
        label=label,
    )
    if set(freeze) - {
        "source_head",
        "source_tree",
        "semantic_bindings_sha256",
        "toolchain_sha256",
        "focused_gate_results",
    }:
        raise ValueError(f"{label} has unexpected keys")
    _hex40(freeze["source_head"], label=f"{label}.source_head")
    _hex40(freeze["source_tree"], label=f"{label}.source_tree")
    _digest(freeze["semantic_bindings_sha256"], label=f"{label}.semantic_bindings_sha256")
    _digest(freeze["toolchain_sha256"], label=f"{label}.toolchain_sha256")
    focused = _object(freeze["focused_gate_results"], label=f"{label}.focused_gate_results")
    for key, result in focused.items():
        _nonempty_string(key, label=f"{label}.focused_gate_results key")
        _enum(result, {"passed", "revision_required", "uncertain"}, label=f"{label}.focused_gate_results.{key}")
    return {
        "source_head": freeze["source_head"],
        "source_tree": freeze["source_tree"],
        "semantic_bindings_sha256": freeze["semantic_bindings_sha256"],
        "toolchain_sha256": freeze["toolchain_sha256"],
        "focused_gate_results": dict(focused),
    }


def validate_profile(value: object) -> dict[str, Any]:
    """Validate a typed tranche profile and return a normalized copy.

    Raises ``ValueError`` on any structural, contradictory or caller-lowered
    classification. The returned profile includes ``derived_tier``,
    ``required_baseline``, ``required_final_vetoes`` and the computed rerun
    requirements so downstream admission cannot recompute differently.
    """
    profile = _object(value, label="tranche profile")
    _require_keys(
        profile,
        {
            "schema_version",
            "tranche_id",
            "source_head",
            "source_tree",
            "declared_tier",
            "change_signals",
            "change_families",
            "semantic_bindings",
            "volatile_bindings",
            "baseline",
            "semantic_freeze",
            "post_freeze_change_families",
            "configured_continuation_events",
            "threat_ids",
            "mutation_count",
            "review_triggers",
            "parallelism_plan",
            "capability",
            "closed_surfaces",
            "place_in_raisa",
            "next_tranche",
            "attention_status",
        },
        label="tranche profile",
    )
    if set(profile) - {
        "schema_version",
        "tranche_id",
        "source_head",
        "source_tree",
        "declared_tier",
        "change_signals",
        "change_families",
        "semantic_bindings",
        "volatile_bindings",
        "baseline",
        "semantic_freeze",
        "post_freeze_change_families",
        "configured_continuation_events",
        "threat_ids",
        "mutation_count",
        "review_triggers",
        "parallelism_plan",
        "capability",
        "closed_surfaces",
        "place_in_raisa",
        "next_tranche",
        "attention_status",
    }:
        raise ValueError("tranche profile has unexpected keys")
    if profile["schema_version"] != PROFILE_SCHEMA_VERSION:
        raise ValueError("tranche profile schema version is not admitted")
    tranche_id = _nonempty_string(profile["tranche_id"], label="tranche_id")
    source_head = _hex40(profile["source_head"], label="source_head")
    source_tree = _hex40(profile["source_tree"], label="source_tree")
    _enum(profile["declared_tier"], ALL_TIER_NAMES, label="declared_tier")

    signals = _validate_change_signals(profile["change_signals"])
    families = set(_validate_change_families(profile["change_families"], label="change_families"))
    review_triggers = _object(profile["review_triggers"], label="review_triggers")
    _exact_keys(review_triggers, REVIEW_TRIGGER_KEYS, label="review_triggers")
    normalized_triggers = {
        key: _bool(review_triggers[key], label=f"review_triggers.{key}")
        for key in review_triggers
    }
    _check_contradictions(signals, families)
    if signals["docs_only"] and normalized_triggers["new_authority_or_security_boundary"]:
        raise ValueError("docs_only contradicts a new authority or security boundary")
    derived_tier = _derive_tier(signals, families, normalized_triggers)
    if profile["declared_tier"] != derived_tier:
        raise ValueError(
            "declared tier cannot be caller-chosen or lowered: "
            f"declared={profile['declared_tier']!r} derived={derived_tier!r}"
        )

    semantic_bindings = _validate_binding_list(
        profile["semantic_bindings"], SEMANTIC_KINDS, label="semantic_bindings"
    )
    volatile_bindings = _validate_binding_list(
        profile["volatile_bindings"], VOLATILE_KINDS, label="volatile_bindings"
    )
    _validate_disjoint_bindings(semantic_bindings, volatile_bindings)
    if signals["docs_only"] and semantic_bindings:
        raise ValueError("docs_only profiles cannot carry semantic bindings")

    baseline = _validate_baseline(profile["baseline"], label="baseline")
    freeze = _validate_semantic_freeze(profile["semantic_freeze"], label="semantic_freeze")

    required_baseline = derived_tier != TIER_0_METADATA
    if required_baseline:
        if baseline["result"] == "not_required":
            raise ValueError("tier 1-3 profiles require a captured canonical baseline")
        if not baseline["captured_before_first_edit"]:
            raise ValueError("baseline must be captured before the first semantic edit")
    else:
        if baseline["result"] not in {"passed", "not_required"}:
            raise ValueError("tier 0 baseline must be passed or not_required")

    if derived_tier != TIER_0_METADATA and not freeze["focused_gate_results"]:
        raise ValueError("tier 1-3 semantic freeze requires focused gate results")

    post_freeze = _validate_change_families_optional(
        profile["post_freeze_change_families"], label="post_freeze_change_families"
    )
    rerun = compute_rerun({"post_freeze_change_families": post_freeze})

    configured_events = _string_list(
        profile["configured_continuation_events"],
        label="configured_continuation_events",
        minimum=1,
    )

    threat_ids = _list_of(profile["threat_ids"], label="threat_ids")
    if not threat_ids:
        raise ValueError("threat_ids must name at least one required threat")
    normalized_threats: list[str] = []
    for index, threat_id in enumerate(threat_ids):
        if (
            not isinstance(threat_id, str)
            or len(threat_id) != 7
            or not threat_id.startswith("RWW-")
            or not threat_id[4:].isdigit()
        ):
            raise ValueError(f"threat_ids[{index}] must be an RWW-\\d{{3}} id")
        if threat_id in normalized_threats:
            raise ValueError(f"threat_ids[{index}] duplicates {threat_id!r}")
        normalized_threats.append(threat_id)

    mutation_count = profile["mutation_count"]
    if isinstance(mutation_count, bool) or not isinstance(mutation_count, int) or mutation_count < 0:
        raise ValueError("mutation_count must be a nonnegative integer")

    parallelism_plan = _object(profile["parallelism_plan"], label="parallelism_plan")
    _exact_keys(parallelism_plan, PARALLELISM_LANE_KEYS, label="parallelism_plan")
    _validate_parallelism_lanes(parallelism_plan, label="parallelism_plan")

    capability = _nonempty_string(profile["capability"], label="capability")
    closed_surfaces = _string_list(
        profile["closed_surfaces"], label="closed_surfaces", minimum=1
    )
    place_in_raisa = _nonempty_string(profile["place_in_raisa"], label="place_in_raisa")
    next_tranche = _nonempty_string(profile["next_tranche"], label="next_tranche")
    _enum(profile["attention_status"], {"green", "amber", "red"}, label="attention_status")

    required_final_vetoes = _required_final_vetoes(derived_tier, normalized_triggers)

    normalized = {
        "schema_version": PROFILE_SCHEMA_VERSION,
        "tranche_id": tranche_id,
        "source_head": source_head,
        "source_tree": source_tree,
        "declared_tier": profile["declared_tier"],
        "derived_tier": derived_tier,
        "change_signals": signals,
        "change_families": sorted(families),
        "semantic_bindings": semantic_bindings,
        "volatile_bindings": volatile_bindings,
        "baseline": baseline,
        "semantic_freeze": freeze,
        "post_freeze_change_families": sorted(post_freeze),
        "configured_continuation_events": configured_events,
        "threat_ids": normalized_threats,
        "mutation_count": mutation_count,
        "review_triggers": normalized_triggers,
        "parallelism_plan": dict(parallelism_plan),
        "capability": capability,
        "closed_surfaces": list(closed_surfaces),
        "place_in_raisa": place_in_raisa,
        "next_tranche": next_tranche,
        "attention_status": profile["attention_status"],
        "required_baseline": required_baseline,
        "required_final_vetoes": required_final_vetoes,
        "rerun_requirements": rerun,
    }
    return normalized


def _validate_change_families_optional(value: object, *, label: str) -> list[str]:
    families = _list_of(value, label=label)
    if len(families) > 16:
        raise ValueError(f"{label} must contain at most 16 families")
    normalized: list[str] = []
    for index, family in enumerate(families):
        if not isinstance(family, str) or family not in CHANGE_FAMILIES:
            raise ValueError(f"{label}[{index}] is not an admitted change family")
        if family in normalized:
            raise ValueError(f"{label}[{index}] duplicates family {family!r}")
        normalized.append(family)
    return normalized


def _validate_disjoint_bindings(
    semantic: list[dict[str, str]], volatile: list[dict[str, str]]
) -> None:
    semantic_paths = {entry["path"] for entry in semantic}
    volatile_paths = {entry["path"] for entry in volatile}
    overlap = semantic_paths & volatile_paths
    if overlap:
        raise ValueError(
            "semantic and volatile bindings must be disjoint; duplicated or "
            f"reclassified paths: {sorted(overlap)!r}"
        )


def _validate_parallelism_lanes(value: dict[str, Any], *, label: str) -> None:
    _enum(
        value.get("deepseek_lane"),
        {"bounded_mechanical_implementation", "declined"},
        label=f"{label}.deepseek_lane",
    )
    _enum(value.get("gemini_lane"), {"single_final_veto", "declined"}, label=f"{label}.gemini_lane")
    _enum(value.get("native_lane"), {"declined", "explicit_review_lane"}, label=f"{label}.native_lane")


def _required_final_vetoes(tier: str, review_triggers: dict[str, bool]) -> int:
    if tier == TIER_0_METADATA:
        return 0
    if tier == TIER_1_PROVIDER_FREE_SOURCE:
        return 1 if any(review_triggers.values()) else 0
    # Tier 2 and Tier 3 always require exactly one final independent veto.
    return 1


def classify_tier(profile: dict[str, Any]) -> str:
    """Derive the highest applicable tier from an admitted profile."""
    normalized = validate_profile(profile)
    return normalized["derived_tier"]


def compute_rerun(profile: dict[str, Any]) -> list[str]:
    """Return the union change-triggered rerun requirement list.

    The input may be a raw profile or the normalized profile produced by
    ``validate_profile``. Unknown change families fail closed; mixed families
    take the union.
    """
    raw_families = profile.get("post_freeze_change_families")
    if raw_families is None:
        raise ValueError("post_freeze_change_families is required")
    families = set(_validate_change_families_optional(raw_families, label="post_freeze_change_families"))
    union: list[str] = []
    for family in sorted(families):
        for item in RERUN_BY_FAMILY[family]:
            if item not in union:
                union.append(item)
    return union


def validate_threat_coverage(profile: dict[str, Any], result: dict[str, Any]) -> None:
    """Every required threat ID must be covered by at least one passing gate."""
    required = set(profile.get("threat_ids", []))
    if not required:
        raise ValueError("profile must name required threat IDs")
    gates = _list_of(result.get("deterministic_gates"), label="deterministic_gates")
    covered: set[str] = set()
    for gate in gates:
        if gate.get("result") == "passed":
            covered.update(gate.get("covers", []))
    missing = required - covered
    if missing:
        raise ValueError(f"threat IDs lack passing gate coverage: {sorted(missing)!r}")


def validate_incident_grouping(result: dict[str, Any]) -> None:
    """Distinct origins must remain distinct incident records.

    Two incidents that share the exact origin/category/role/resource/signature
    tuple are one causal incident and must not be emitted as separate records.
    """
    incidents = _list_of(result.get("incidents"), label="incidents")
    seen: set[tuple[str, str, str, str, str]] = set()
    for index, incident in enumerate(incidents):
        key = (
            incident["origin"],
            incident["category"],
            incident["role"],
            incident["resource"],
            incident["signature"],
        )
        if key in seen:
            raise ValueError(
                "incident grouping collapses one causal origin into multiple "
                f"records at incidents[{index}]"
            )
        seen.add(key)


def validate_tail_deferral(result: dict[str, Any]) -> None:
    """A tail item may be deferred only when no hard-control flag is set."""
    items = _list_of(result.get("deferred_tail"), label="deferred_tail")
    for index, item in enumerate(items):
        if any(item.get(flag) for flag in HARD_DEFECT_FLAGS):
            raise ValueError(
                f"deferred_tail[{index}] carries a safety/authority/integrity/"
                "privacy/atomicity/protected-evidence/irreversible-effect flag"
            )
        owner = item.get("owner")
        boundary = item.get("next_review_boundary")
        if not isinstance(owner, str) or not owner.strip():
            raise ValueError(f"deferred_tail[{index}] requires an owner")
        if not isinstance(boundary, str) or not boundary.strip():
            raise ValueError(f"deferred_tail[{index}] requires a next review boundary")


def _validate_review(value: object, *, label: str) -> dict[str, Any]:
    review = _object(value, label=label)
    _exact_keys(review, {"required_final_vetoes", "final_vetoes"}, label=label)
    required_vetoes = review["required_final_vetoes"]
    if isinstance(required_vetoes, bool) or not isinstance(required_vetoes, int):
        raise ValueError(f"{label}.required_final_vetoes must be an integer")
    if required_vetoes < 0 or required_vetoes > 1:
        raise ValueError(f"{label}.required_final_vetoes must be 0 or 1")
    final_vetoes = _list_of(review["final_vetoes"], label=f"{label}.final_vetoes")
    if len(final_vetoes) > 1:
        raise ValueError(f"{label}.final_vetoes must contain at most one veto")
    normalized: list[dict[str, Any]] = []
    for index, veto in enumerate(final_vetoes):
        item = _object(veto, label=f"{label}.final_vetoes[{index}]")
        _exact_keys(item, {"veto_id", "reviewer_lane", "decision"}, label=f"{label}.final_vetoes[{index}]")
        _nonempty_string(item["veto_id"], label=f"{label}.final_vetoes[{index}].veto_id")
        _enum(
            item["reviewer_lane"],
            {"gemini_single_final_veto", "native_explicit_review_lane"},
            label=f"{label}.final_vetoes[{index}].reviewer_lane",
        )
        _enum(item["decision"], {"pass", "revision_required"}, label=f"{label}.final_vetoes[{index}].decision")
        normalized.append(
            {
                "veto_id": item["veto_id"],
                "reviewer_lane": item["reviewer_lane"],
                "decision": item["decision"],
            }
        )
    return {"required_final_vetoes": required_vetoes, "final_vetoes": normalized}


def _validate_parallelism_result(value: object, *, label: str) -> dict[str, Any]:
    parallelism = _object(value, label=label)
    _exact_keys(parallelism, {"planned", "actual", "planned_vs_actual"}, label=label)
    planned = _object(parallelism["planned"], label=f"{label}.planned")
    actual = _object(parallelism["actual"], label=f"{label}.actual")
    _exact_keys(planned, PARALLELISM_LANE_KEYS, label=f"{label}.planned")
    _exact_keys(actual, PARALLELISM_LANE_KEYS, label=f"{label}.actual")
    _validate_parallelism_lanes(planned, label=f"{label}.planned")
    _validate_parallelism_lanes(actual, label=f"{label}.actual")
    _enum(
        parallelism["planned_vs_actual"],
        {"exact", "deviation_recorded"},
        label=f"{label}.planned_vs_actual",
    )
    return {
        "planned": dict(planned),
        "actual": dict(actual),
        "planned_vs_actual": parallelism["planned_vs_actual"],
    }


def _validate_continuation_receipts(value: object, *, label: str) -> list[dict[str, str]]:
    receipts = _list_of(value, label=label)
    normalized: list[dict[str, str]] = []
    observed: set[str] = set()
    for index, receipt in enumerate(receipts):
        item = _object(receipt, label=f"{label}[{index}]")
        _exact_keys(item, {"event", "receipt_sha256"}, label=f"{label}[{index}]")
        event = _nonempty_string(item["event"], label=f"{label}[{index}].event")
        if event in observed:
            raise ValueError(f"{label}[{index}] duplicates event {event!r}")
        observed.add(event)
        normalized.append(
            {
                "event": event,
                "receipt_sha256": _digest(item["receipt_sha256"], label=f"{label}[{index}].receipt_sha256"),
            }
        )
    return normalized


def _validate_incidents(value: object, *, label: str) -> list[dict[str, Any]]:
    incidents = _list_of(value, label=label)
    normalized: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for index, incident in enumerate(incidents):
        item = _object(incident, label=f"{label}[{index}]")
        _exact_keys(
            item,
            {
                "id",
                "origin",
                "category",
                "role",
                "resource",
                "signature",
                "recorded_before_correction",
            },
            label=f"{label}[{index}]",
        )
        incident_id = _nonempty_string(item["id"], label=f"{label}[{index}].id")
        if incident_id in seen_ids:
            raise ValueError(f"{label}[{index}] duplicates id {incident_id!r}")
        seen_ids.add(incident_id)
        normalized.append(
            {
                "id": incident_id,
                "origin": _nonempty_string(item["origin"], label=f"{label}[{index}].origin"),
                "category": _nonempty_string(item["category"], label=f"{label}[{index}].category"),
                "role": _nonempty_string(item["role"], label=f"{label}[{index}].role"),
                "resource": _nonempty_string(item["resource"], label=f"{label}[{index}].resource"),
                "signature": _nonempty_string(item["signature"], label=f"{label}[{index}].signature"),
                "recorded_before_correction": _bool(
                    item["recorded_before_correction"],
                    label=f"{label}[{index}].recorded_before_correction",
                ),
            }
        )
    return normalized


def _validate_deferred_tail(value: object, *, label: str) -> list[dict[str, Any]]:
    items = _list_of(value, label=label)
    normalized: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for index, item in enumerate(items):
        entry = _object(item, label=f"{label}[{index}]")
        _exact_keys(
            entry,
            {
                "id",
                "title",
                "safety_relevant",
                "authority_relevant",
                "integrity_relevant",
                "privacy_relevant",
                "atomicity_relevant",
                "protected_evidence_relevant",
                "irreversible_effect_relevant",
                "owner",
                "next_review_boundary",
            },
            label=f"{label}[{index}]",
        )
        item_id = _nonempty_string(entry["id"], label=f"{label}[{index}].id")
        if item_id in seen_ids:
            raise ValueError(f"{label}[{index}] duplicates id {item_id!r}")
        seen_ids.add(item_id)
        _nonempty_string(entry["title"], label=f"{label}[{index}].title")
        flags = {
            flag: _bool(entry[flag], label=f"{label}[{index}].{flag}")
            for flag in HARD_DEFECT_FLAGS
        }
        owner = _nonempty_string(entry["owner"], label=f"{label}[{index}].owner")
        boundary = _nonempty_string(
            entry["next_review_boundary"], label=f"{label}[{index}].next_review_boundary"
        )
        normalized.append(
            {
                "id": item_id,
                "title": entry["title"],
                **flags,
                "owner": owner,
                "next_review_boundary": boundary,
            }
        )
    return normalized


def validate_result(value: object) -> dict[str, Any]:
    """Validate a typed tranche result structure and return a normalized copy."""
    result = _object(value, label="tranche result")
    _require_keys(
        result,
        {
            "schema_version",
            "tranche_id",
            "profile_sha256",
            "classified_tier",
            "decision",
            "baseline",
            "semantic_freeze",
            "deterministic_gates",
            "required_rerun",
            "review",
            "canonical_pass_reuse",
            "continuation_receipts",
            "incidents",
            "deferred_tail",
            "parallelism",
            "capability",
            "technical_result",
            "closed_surfaces",
            "issues",
            "place_in_raisa",
            "next_tranche",
            "attention_status",
        },
        label="tranche result",
    )
    if set(result) - {
        "schema_version",
        "tranche_id",
        "profile_sha256",
        "classified_tier",
        "decision",
        "baseline",
        "semantic_freeze",
        "deterministic_gates",
        "required_rerun",
        "review",
        "canonical_pass_reuse",
        "continuation_receipts",
        "incidents",
        "deferred_tail",
        "parallelism",
        "capability",
        "technical_result",
        "closed_surfaces",
        "issues",
        "place_in_raisa",
        "next_tranche",
        "attention_status",
    }:
        raise ValueError("tranche result has unexpected keys")
    if result["schema_version"] != RESULT_SCHEMA_VERSION:
        raise ValueError("tranche result schema version is not admitted")
    tranche_id = _nonempty_string(result["tranche_id"], label="tranche_id")
    _digest(result["profile_sha256"], label="profile_sha256")
    _enum(result["classified_tier"], ALL_TIER_NAMES, label="classified_tier")
    _enum(result["decision"], {"pass", "revision_required"}, label="decision")
    baseline = _validate_baseline(result["baseline"], label="baseline")
    freeze = _validate_semantic_freeze(result["semantic_freeze"], label="semantic_freeze")

    gates = _list_of(result["deterministic_gates"], label="deterministic_gates")
    normalized_gates: list[dict[str, Any]] = []
    seen_gate_ids: set[str] = set()
    for index, gate in enumerate(gates):
        item = _object(gate, label=f"deterministic_gates[{index}]")
        _exact_keys(item, {"id", "category", "result", "covers"}, label=f"deterministic_gates[{index}]")
        gate_id = _nonempty_string(item["id"], label=f"deterministic_gates[{index}].id")
        if gate_id in seen_gate_ids:
            raise ValueError(f"deterministic_gates[{index}] duplicates id {gate_id!r}")
        seen_gate_ids.add(gate_id)
        _enum(item["category"], GATE_CATEGORIES, label=f"deterministic_gates[{index}].category")
        _enum(item["result"], {"passed", "revision_required", "uncertain"}, label=f"deterministic_gates[{index}].result")
        covers = _list_of(item["covers"], label=f"deterministic_gates[{index}].covers")
        normalized_covers: list[str] = []
        for threat_id in covers:
            if (
                not isinstance(threat_id, str)
                or len(threat_id) != 7
                or not threat_id.startswith("RWW-")
                or not threat_id[4:].isdigit()
            ):
                raise ValueError(f"deterministic_gates[{index}].covers has invalid threat id")
            if threat_id in normalized_covers:
                raise ValueError(
                    f"deterministic_gates[{index}].covers duplicates {threat_id!r}"
                )
            normalized_covers.append(threat_id)
        normalized_gates.append(
            {"id": gate_id, "category": item["category"], "result": item["result"], "covers": normalized_covers}
        )

    required_rerun = _list_of(result["required_rerun"], label="required_rerun")
    normalized_rerun: list[str] = []
    for index, item in enumerate(required_rerun):
        if not isinstance(item, str) or item not in ALL_RERUN_ITEMS:
            raise ValueError(f"required_rerun[{index}] is not an admitted rerun item")
        if item in normalized_rerun:
            raise ValueError(f"required_rerun[{index}] duplicates {item!r}")
        normalized_rerun.append(item)

    review = _validate_review(result["review"], label="review")
    canonical_reuse = _object(result["canonical_pass_reuse"], label="canonical_pass_reuse")
    _exact_keys(canonical_reuse, {"reused", "fingerprint_sha256", "exact"}, label="canonical_pass_reuse")
    _bool(canonical_reuse["reused"], label="canonical_pass_reuse.reused")
    _digest(canonical_reuse["fingerprint_sha256"], label="canonical_pass_reuse.fingerprint_sha256")
    _bool(canonical_reuse["exact"], label="canonical_pass_reuse.exact")
    continuation_receipts = _validate_continuation_receipts(
        result["continuation_receipts"], label="continuation_receipts"
    )
    incidents = _validate_incidents(result["incidents"], label="incidents")
    deferred_tail = _validate_deferred_tail(result["deferred_tail"], label="deferred_tail")
    parallelism = _validate_parallelism_result(result["parallelism"], label="parallelism")
    capability = _nonempty_string(result["capability"], label="capability")
    technical_result = _nonempty_string(result["technical_result"], label="technical_result")
    closed_surfaces = _string_list(
        result["closed_surfaces"], label="closed_surfaces", minimum=1
    )
    issues = _string_list(result["issues"], label="issues")
    place_in_raisa = _nonempty_string(result["place_in_raisa"], label="place_in_raisa")
    next_tranche = _nonempty_string(result["next_tranche"], label="next_tranche")
    _enum(result["attention_status"], {"green", "amber", "red"}, label="attention_status")

    normalized = {
        "schema_version": RESULT_SCHEMA_VERSION,
        "tranche_id": tranche_id,
        "profile_sha256": result["profile_sha256"],
        "classified_tier": result["classified_tier"],
        "decision": result["decision"],
        "baseline": baseline,
        "semantic_freeze": freeze,
        "deterministic_gates": normalized_gates,
        "required_rerun": normalized_rerun,
        "review": review,
        "canonical_pass_reuse": {
            "reused": canonical_reuse["reused"],
            "fingerprint_sha256": canonical_reuse["fingerprint_sha256"],
            "exact": canonical_reuse["exact"],
        },
        "continuation_receipts": continuation_receipts,
        "incidents": incidents,
        "deferred_tail": deferred_tail,
        "parallelism": parallelism,
        "capability": capability,
        "technical_result": technical_result,
        "closed_surfaces": list(closed_surfaces),
        "issues": list(issues),
        "place_in_raisa": place_in_raisa,
        "next_tranche": next_tranche,
        "attention_status": result["attention_status"],
    }
    return normalized


def admit_result(profile_value: object, result_value: object) -> dict[str, Any]:
    """Admit a tranche result only when its tier-required evidence is complete.

    Returns a deterministic decision envelope with ``decision`` equal to
    ``pass`` or ``revision_required`` and a ``reasons`` list. A pass result must
    bind the exact profile digest, classified tier, baseline, semantic freeze,
    rerun requirements, review vetoes, threat coverage, incidents, tail and
    parallelism plan. Omission, contradiction and excess reviewer claims fail
    closed.
    """
    profile = validate_profile(profile_value)
    result = validate_result(result_value)
    reasons: list[str] = []

    # Exact profile digest binding (RWW-016). Hash the raw supplied profile so
    # the digest is stable and independent of any normalized field additions.
    expected_digest = profile_sha256(profile_value)
    if result["profile_sha256"] != expected_digest:
        reasons.append("profile_sha256_mismatch")

    if result["classified_tier"] != profile["derived_tier"]:
        reasons.append("classified_tier_mismatch")
    if result["tranche_id"] != profile["tranche_id"]:
        reasons.append("tranche_id_mismatch")

    # Baseline evidence.
    if profile["required_baseline"]:
        if result["baseline"]["result"] not in {"passed", "passed_with_known_failures"}:
            reasons.append("baseline_evidence_missing")
        if result["baseline"]["fingerprint_sha256"] != profile["baseline"]["fingerprint_sha256"]:
            reasons.append("baseline_fingerprint_mismatch")
        if set(result["baseline"]["known_failure_ids"]) != set(profile["baseline"]["known_failure_ids"]):
            reasons.append("baseline_known_failure_ids_mismatch")
        if result["baseline"]["captured_before_first_edit"] != profile["baseline"]["captured_before_first_edit"]:
            reasons.append("baseline_capture_order_mismatch")
    else:
        if result["baseline"]["result"] not in {"passed", "not_required"}:
            reasons.append("baseline_evidence_exceeds_tier_0")

    if result["semantic_freeze"] != profile["semantic_freeze"]:
        reasons.append("semantic_freeze_mismatch")
    for gate_id, gate_result in profile["semantic_freeze"]["focused_gate_results"].items():
        if gate_result != "passed":
            reasons.append(f"semantic_freeze_gate_not_passed_{gate_id}")

    # The reuse fingerprint is derived rather than accepted as a caller claim.
    # It binds stable source/evidence/input/toolchain state while excluding the
    # volatile closeout surfaces that the reform deliberately decouples.
    expected_reuse_fingerprint = canonical_pass_fingerprint(profile_value)
    if result["canonical_pass_reuse"]["fingerprint_sha256"] != expected_reuse_fingerprint:
        reasons.append("canonical_pass_fingerprint_mismatch")
    if result["canonical_pass_reuse"]["reused"] and not result["canonical_pass_reuse"]["exact"]:
        reasons.append("stale_canonical_pass_reuse")

    # Rerun requirements must match the union computed from the profile.
    expected_rerun = profile["rerun_requirements"]
    if set(result["required_rerun"]) != set(expected_rerun):
        reasons.append("required_rerun_mismatch")

    # Every rerun-required gate category must be present as a passing gate.
    gate_categories = {gate["category"] for gate in result["deterministic_gates"]}
    for item in expected_rerun:
        category = RERUN_ITEM_TO_GATE_CATEGORY.get(item)
        if category is None:
            continue
        if category not in gate_categories:
            reasons.append(f"missing_gate_category_{category}")
        else:
            category_gates = [
                gate for gate in result["deterministic_gates"] if gate["category"] == category
            ]
            if all(gate["result"] != "passed" for gate in category_gates):
                reasons.append(f"gate_category_not_passed_{category}")

    # A canonical final profile is mandatory for tier 1-3.
    if profile["required_baseline"] and "canonical_final_profile" not in gate_categories:
        reasons.append("missing_canonical_final_profile")

    # Deterministic gates cannot remain failed or uncertain for a pass.
    for gate in result["deterministic_gates"]:
        if gate["result"] == "revision_required":
            reasons.append(f"gate_revision_required_{gate['id']}")
        if gate["result"] == "uncertain":
            reasons.append(f"gate_uncertain_{gate['id']}")

    # Named-threat coverage (RWW-009).
    try:
        validate_threat_coverage(profile, result)
    except ValueError as error:
        reasons.append(str(error))

    # Review economy (RWW-007, RWW-008, RWW-016).
    required_vetoes = profile["required_final_vetoes"]
    if result["review"]["required_final_vetoes"] != required_vetoes:
        reasons.append("review_requirement_mismatch")
    final_vetoes = result["review"]["final_vetoes"]
    if len(final_vetoes) > required_vetoes:
        reasons.append("excess_reviewer_claim")
    if len(final_vetoes) < required_vetoes:
        reasons.append("review_veto_omission")
    if required_vetoes == 1:
        if len(final_vetoes) == 1 and final_vetoes[0]["decision"] != "pass":
            reasons.append("final_veto_not_pass")

    # Incidents (RWW-010, RWW-011).
    try:
        validate_incident_grouping(result)
    except ValueError as error:
        reasons.append(str(error))
    for incident in result["incidents"]:
        if incident["recorded_before_correction"] is False:
            reasons.append("incident_not_recorded_before_correction")

    # Safe tail deferral (RWW-012).
    try:
        validate_tail_deferral(result)
    except ValueError as error:
        reasons.append(str(error))

    # Parallelism must be explicit (RWW-018).
    if result["parallelism"]["planned"] != profile["parallelism_plan"]:
        reasons.append("parallelism_plan_mismatch")
    if result["parallelism"]["actual"] != result["parallelism"]["planned"]:
        reasons.append("parallelism_actual_mismatch")
    if result["parallelism"]["planned_vs_actual"] == "deviation_recorded":
        reasons.append("parallelism_deviation_recorded")

    # The result packet cannot silently rewrite the accepted scope or handoff.
    if result["capability"] != profile["capability"]:
        reasons.append("capability_mismatch")
    if result["closed_surfaces"] != profile["closed_surfaces"]:
        reasons.append("closed_surfaces_mismatch")
    if result["place_in_raisa"] != profile["place_in_raisa"]:
        reasons.append("place_in_raisa_mismatch")
    if result["next_tranche"] != profile["next_tranche"]:
        reasons.append("next_tranche_mismatch")
    if result["attention_status"] != profile["attention_status"]:
        reasons.append("attention_status_mismatch")

    # Continuation events must each have a fresh five-source receipt (RWW-017).
    expected_events = set(profile["configured_continuation_events"])
    receipt_events = {receipt["event"] for receipt in result["continuation_receipts"]}
    missing_events = expected_events - receipt_events
    if missing_events:
        reasons.append(f"missing_continuation_receipts_{sorted(missing_events)!r}")

    evidence_decision = "pass" if not reasons else "revision_required"
    if result["decision"] != evidence_decision:
        reasons.append("decision_does_not_match_evidence")
    decision = "pass" if not reasons else "revision_required"

    return {
        "schema_version": RESULT_SCHEMA_VERSION,
        "tranche_id": result["tranche_id"],
        "decision": decision,
        "classified_tier": result["classified_tier"],
        "profile_sha256": expected_digest,
        "reasons": reasons,
    }
