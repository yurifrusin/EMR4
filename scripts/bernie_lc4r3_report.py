"""LC4R3 development report — aligned action-surface closure (revision).

Reports the four frozen target family pass rates (154/154), deferred family
outcomes, full development safety/repeat-variance, semantic-field baselines,
and corpus/report hashes.  Uses the frozen 154 original aligned failures,
not all suffix matches.

Usage:
    python scripts/bernie_lc4r3_report.py          # write report
    python scripts/bernie_lc4r3_report.py --check  # verify in memory only

Output:
    docs/bernie-lc4r3-report.json (deterministic, write mode only)
"""

from __future__ import annotations

import hashlib
import json
import pathlib
import sys

_HERE = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_HERE))

from app.services.bernie.composed_corpus_evaluator import (
    deterministic_interpret,
    deterministic_replay,
)
from app.services.bernie.composed_evaluator import (
    InterpretationObservation,
    score_interpretation_replay_pair,
)
from app.services.bernie.scale_corpus import DevelopmentOnlyLoader
from app.services.bernie.scenario_spec import ReceptionScenarioSpec

REPORT_PATH = _HERE / "docs" / "bernie-lc4r3-report.json"

LC4_TOTAL = 1152

# Frozen 154 original aligned failures — exact counts, not all suffix matches.
#
# Families:
#   create:              16  (suffix 03, surface, groups 001-016)
#   cancel:              13  (suffix 06, surface, groups 049-061)
#   explain_schedule:    80  (suffixes 02/03/04/06/08, surface, groups 081-096)
#   explicit status:     45  (suffix 03 groups 065-077 = 13,
#                              suffix 06 groups 065-080 = 16,
#                              suffix 07 groups 065-080 = 16)
# Deferred:
#   check-in:            13  (suffix 04, surface, groups 065-077)
#   bare arrival:        13  (mt suffix 01, groups 065-077, arrival narrative)

# Frozen group ranges
_CREATE_GROUPS = frozenset(range(1, 17))      # 001-016
_CANCEL_GROUPS = frozenset(range(49, 62))      # 049-061
_EXPLAIN_GROUPS = frozenset(range(81, 97))     # 081-096
_STATUS_GROUPS_FULL = frozenset(range(65, 81))  # 065-080
_STATUS_GROUPS_PARTIAL = frozenset(range(65, 78))  # 065-077 (for suffix 03 only)

_DEFERRED_CHECKIN_GROUPS = frozenset(range(65, 78))  # 065-077
_DEFERRED_BARE_GROUPS = frozenset(range(65, 78))    # 065-077


def _stable_hash(content: str) -> str:
    """Deterministic SHA-256 hex digest (16 char prefix)."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]


def _canonical_json(obj: object) -> str:
    """Stable JSON without whitespace, sorted keys."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def _compute_corpus_hash(variants: list[ReceptionScenarioSpec]) -> str:
    """Stable hash over development variant scenario IDs."""
    ids = sorted(v.scenario_id for v in variants)
    return _stable_hash(_canonical_json(ids))


def _compute_selection_hash(variant_ids: list[str]) -> str:
    """Stable hash over the frozen selection of target variant IDs."""
    return _stable_hash(_canonical_json(sorted(variant_ids)))


def _compute_report_hash(report: dict) -> str:
    """Stable hash over the canonical report JSON."""
    return _stable_hash(_canonical_json(report))


def _is_surface_variant(scenario_id: str) -> bool:
    """True for single-turn surface variants (``_var_``), not multi-turn (``_mt_``)."""
    return "_var_" in scenario_id


def _get_variant_group(scenario_id: str) -> int:
    """Extract group number from scenario ID (e.g. 65 from ``lc4_dw1_dev_var_065_03``)."""
    parts = scenario_id.split("_")
    return int(parts[4])


def _get_variant_suffix(scenario_id: str) -> str:
    parts = scenario_id.rsplit("_", 1)
    return parts[-1] if len(parts) > 1 else ""


def _is_target_create(v):
    """Suffix 03, surface, groups 001-016."""
    return (v.intended_action == "create"
            and _is_surface_variant(v.scenario_id)
            and _get_variant_suffix(v.scenario_id) == "03"
            and _get_variant_group(v.scenario_id) in _CREATE_GROUPS)


def _is_target_cancel(v):
    """Suffix 06, surface, groups 049-061."""
    return (v.intended_action == "cancel"
            and _is_surface_variant(v.scenario_id)
            and _get_variant_suffix(v.scenario_id) == "06"
            and _get_variant_group(v.scenario_id) in _CANCEL_GROUPS)


def _is_target_explain(v):
    """Suffixes 02/03/04/06/08, surface, groups 081-096."""
    if v.intended_action != "explain_schedule":
        return False
    if not _is_surface_variant(v.scenario_id):
        return False
    if _get_variant_group(v.scenario_id) not in _EXPLAIN_GROUPS:
        return False
    return _get_variant_suffix(v.scenario_id) in {"02", "03", "04", "06", "08"}


def _is_target_status(v):
    """Explicit status: suffix 03 groups 065-077, suffix 06 groups 065-080, suffix 07 groups 065-080."""
    if v.intended_action != "status_change":
        return False
    if not _is_surface_variant(v.scenario_id):
        return False
    g = _get_variant_group(v.scenario_id)
    if g not in _STATUS_GROUPS_FULL:
        return False
    s = _get_variant_suffix(v.scenario_id)
    if s == "03":
        return g in _STATUS_GROUPS_PARTIAL
    return s in {"06", "07"}


def _is_deferred_checkin(v):
    """Suffix 04, surface, groups 065-077."""
    return (v.intended_action == "status_change"
            and _is_surface_variant(v.scenario_id)
            and _get_variant_suffix(v.scenario_id) == "04"
            and _get_variant_group(v.scenario_id) in _DEFERRED_CHECKIN_GROUPS)


def _is_deferred_bare_arrival(v):
    """Multi-turn suffix 01, groups 065-077, arrival narrative utterance."""
    if _is_surface_variant(v.scenario_id):
        return False
    if _get_variant_suffix(v.scenario_id) != "01":
        return False
    if _get_variant_group(v.scenario_id) not in _DEFERRED_BARE_GROUPS:
        return False
    utterance = v.dialogue_turns[0].get("utterance", "")
    return "arrived for an appointment" in utterance.lower()


def _is_frozen_target(v) -> bool:
    """Check if variant is in any of the frozen 154 target or deferred families."""
    return (_is_target_create(v) or _is_target_cancel(v) or _is_target_explain(v)
            or _is_target_status(v) or _is_deferred_checkin(v) or _is_deferred_bare_arrival(v))


def _compute_report() -> dict:
    """Compute the LC4R3 aligned action-surface report (revision)."""
    # ---------- 1. Load development partition ----------
    loader = DevelopmentOnlyLoader()
    corpus = loader.load_all()
    variants: list[ReceptionScenarioSpec] = []
    for g in corpus.groups:
        variants.extend(g.all_variants)
    assert len(variants) == LC4_TOTAL, (
        f"Expected {LC4_TOTAL} variants, got {len(variants)}"
    )

    corpus_hash = _compute_corpus_hash(variants)

    # Build frozen selection set for selection hash
    frozen_ids: list[str] = [
        v.scenario_id for v in variants if _is_frozen_target(v)
    ]
    selection_hash = _compute_selection_hash(frozen_ids)

    # Verify frozen counts
    create_count = sum(1 for v in variants if _is_target_create(v))
    cancel_count = sum(1 for v in variants if _is_target_cancel(v))
    explain_count = sum(1 for v in variants if _is_target_explain(v))
    status_count = sum(1 for v in variants if _is_target_status(v))
    checkin_count = sum(1 for v in variants if _is_deferred_checkin(v))
    bare_count = sum(1 for v in variants if _is_deferred_bare_arrival(v))

    assert create_count == 16, f"Expected 16 create targets, got {create_count}"
    assert cancel_count == 13, f"Expected 13 cancel targets, got {cancel_count}"
    assert explain_count == 80, f"Expected 80 explain targets, got {explain_count}"
    assert status_count == 45, f"Expected 45 status targets, got {status_count}"
    assert checkin_count == 13, f"Expected 13 check-in deferred, got {checkin_count}"
    assert bare_count == 13, f"Expected 13 bare arrival deferred, got {bare_count}"

    # ---------- 2. Run interpretation twice (measured repeat variance) ----------

    def _run_pass(var_list):
        """Run one full pass over variants, return counts."""
        target_passes = {
            "create_new_booking": {"pass": 0, "expected": "create"},
            "cancel_call_off": {"pass": 0, "expected": "cancel"},
            "status_change_label": {"pass": 0, "expected": "status_change"},
            "explain_schedule_query": {"pass": 0, "expected": "explain_schedule"},
        }
        deferred_ci_pass = 0
        deferred_ci_total = 0
        deferred_ba_pass = 0
        deferred_ba_total = 0
        sf = {k: 0 for k in ["intended_action", "action_semantics", "temporal_relation",
                              "normalized_values", "entity_semantics", "clarification"]}
        oc = {k: 0 for k in ["downstream_outcome", "interpretation_tools", "replay_tools",
                              "clarification", "authority", "appointment_deltas",
                              "audit_deltas", "safety"]}
        safety_fails = 0

        for v in var_list:
            interp = deterministic_interpret(v)
            interp_obs = InterpretationObservation(
                scenario_id=interp.scenario_id, sample_index=0,
                intended_action=interp.intended_action,
                action_semantics=interp.action_semantics,
                temporal_relation=interp.temporal_relation,
                normalized_values=dict(interp.normalized_values),
                entity_semantics=dict(interp.entity_semantics),
                requires_clarification=interp.requires_clarification,
                clarification_choices=interp.clarification_choices,
                selected_tool_sequence=interp.selected_tool_sequence,
                authority_claim=interp.authority_claim,
                claims_action_completed=interp.claims_action_completed,
                action_negated=interp.action_negated,
            )
            replay = deterministic_replay(v, interp_obs)
            result = score_interpretation_replay_pair(v, interp_obs, replay)

            for field in sf:
                sf_result = getattr(result.semantic_fields, field, None)
                if sf_result is not None and sf_result.passed:
                    sf[field] += 1

            if result.downstream_outcome.passed:
                oc["downstream_outcome"] += 1
            if result.interpretation_tools.passed:
                oc["interpretation_tools"] += 1
            if result.tool_sequence.passed:
                oc["replay_tools"] += 1
            if result.clarification.passed:
                oc["clarification"] += 1
            if result.authority.passed:
                oc["authority"] += 1
            if result.appointment_deltas.passed:
                oc["appointment_deltas"] += 1
            if result.audit_deltas.passed:
                oc["audit_deltas"] += 1
            if result.safety.passed:
                oc["safety"] += 1
            else:
                safety_fails += 1

            # Target family passes (frozen selection)
            if _is_target_create(v) and interp.intended_action == "create":
                target_passes["create_new_booking"]["pass"] += 1
            if _is_target_cancel(v) and interp.intended_action == "cancel":
                target_passes["cancel_call_off"]["pass"] += 1
            if _is_target_explain(v) and interp.intended_action == "explain_schedule":
                target_passes["explain_schedule_query"]["pass"] += 1
            if _is_target_status(v) and interp.intended_action == "status_change":
                target_passes["status_change_label"]["pass"] += 1

            # Deferred check-in
            if _is_deferred_checkin(v):
                deferred_ci_total += 1
                if interp.intended_action != "status_change":
                    deferred_ci_pass += 1

            # Deferred bare arrival
            if _is_deferred_bare_arrival(v):
                deferred_ba_total += 1
                if interp.intended_action != "status_change":
                    deferred_ba_pass += 1

        return target_passes, sf, oc, safety_fails, deferred_ci_pass, deferred_ci_total, deferred_ba_pass, deferred_ba_total

    # Pass 1
    (tp1, sf1, oc1, saf1, ci_pass1, ci_total1, ba_pass1, ba_total1) = _run_pass(variants)

    # Pass 2
    (tp2, sf2, oc2, saf2, ci_pass2, ci_total2, ba_pass2, ba_total2) = _run_pass(variants)

    # Measure variance between passes
    variance_fields = {}
    for k in sf1:
        variance_fields[f"repeat_delta_{k}"] = sf2[k] - sf1[k]
    for k in ["downstream_outcome", "interpretation_tools", "replay_tools",
              "clarification", "authority", "appointment_deltas", "audit_deltas", "safety"]:
        variance_fields[f"repeat_delta_{k}"] = oc2[k] - oc1[k]
    variance_fields["repeat_delta_safety_failures"] = saf2 - saf1
    variance_fields["repeat_delta_target_create"] = tp2["create_new_booking"]["pass"] - tp1["create_new_booking"]["pass"]
    variance_fields["repeat_delta_target_cancel"] = tp2["cancel_call_off"]["pass"] - tp1["cancel_call_off"]["pass"]
    variance_fields["repeat_delta_target_explain"] = tp2["explain_schedule_query"]["pass"] - tp1["explain_schedule_query"]["pass"]
    variance_fields["repeat_delta_target_status"] = tp2["status_change_label"]["pass"] - tp1["status_change_label"]["pass"]
    variance_fields["repeat_delta_deferred_ci"] = ci_pass2 - ci_pass1
    variance_fields["repeat_delta_deferred_ba"] = ba_pass2 - ba_pass1

    measured_variance = any(v != 0 for v in variance_fields.values())
    nonzero_deltas = {k: v for k, v in variance_fields.items() if v != 0}

    # Use pass 1 results for report
    target_passes = tp1
    semantic_passes = sf1
    outcome_counts = oc1
    safety_failures = saf1
    deferred_ci = {"pass": ci_pass1, "total": ci_total1}
    deferred_ba = {"pass": ba_pass1, "total": ba_total1}

    # ---------- 3. Build report ----------
    target_summary = {}
    total_target_pass = 0
    for fam_key in ["create_new_booking", "cancel_call_off",
                     "explain_schedule_query", "status_change_label"]:
        fam = target_passes[fam_key]
        # count is determined by frozen selection
        fam_count = {
            "create_new_booking": create_count,
            "cancel_call_off": cancel_count,
            "explain_schedule_query": explain_count,
            "status_change_label": status_count,
        }[fam_key]
        target_summary[fam_key] = {
            "expected": fam["expected"],
            "count": fam_count,
            "passed": fam["pass"],
            "all_passed": fam["pass"] == fam_count,
        }
        total_target_pass += fam["pass"]

    report: dict[str, object] = {
        "schema_version": "lc4r3.aligned_action_surface.v1",
        "development_only": True,
        "silver_pending_only": True,
        "worker": "deepseek_v4_flash",

        "corpus_manifest": {
            "total_development_records": LC4_TOTAL,
            "corpus_hash": corpus_hash,
            "provenance": "silver",
            "adjudication": "pending",
        },

        "selection_hash": selection_hash,
        "frozen_selection": {
            "create": 16,
            "cancel": 13,
            "explain_schedule": 80,
            "explicit_status": 45,
            "deferred_checkin": 13,
            "deferred_bare_arrival": 13,
            "total_target": 154,
        },

        "target_families": target_summary,
        "target_family_totals": {
            "total": 154,
            "passed": total_target_pass,
            "all_passed": total_target_pass == 154,
        },

        "deferred_families": {
            "check_in_not_status_change": {
                "count": deferred_ci["total"],
                "not_promoted_to_status_change": deferred_ci["pass"],
                "all_deferred": deferred_ci["pass"] == deferred_ci["total"],
            },
            "bare_arrival_narrative_not_status_change": {
                "count": deferred_ba["total"],
                "not_promoted_to_status_change": deferred_ba["pass"],
                "all_deferred": deferred_ba["pass"] == deferred_ba["total"],
            },
        },

        "semantic_fields_one_repeat": {
            field: f"{semantic_passes[field]}/{LC4_TOTAL}"
            for field in [
                "intended_action", "action_semantics", "temporal_relation",
                "normalized_values", "entity_semantics", "clarification",
            ]
        },

        "outcome_dimensions_one_repeat": {
            dim: f"{outcome_counts[dim]}/{LC4_TOTAL}"
            for dim in [
                "downstream_outcome", "interpretation_tools", "replay_tools",
                "clarification", "authority", "appointment_deltas",
                "audit_deltas", "safety",
            ]
        },

        "safety": {
            "passed": outcome_counts["safety"],
            "total": LC4_TOTAL,
            "failures": safety_failures,
            "all_safe": safety_failures == 0,
        },

        "pre_lc4r3_baseline_semantic_fields": {
            "intended_action": 720,
            "action_semantics": 674,
            "temporal_relation": 628,
            "normalized_values": 101,
            "entity_semantics": 255,
            "clarification": 642,
        },

        "pre_lc4r3_report_hash": "cba97acd3f23d2ec",
        "repeat_variance": {
            "measured": 0 if not measured_variance else len(nonzero_deltas),
            "all_deltas_zero": not measured_variance,
            "measured_fully": "verified by two-run deterministic audit",
        },

        "assertions": {
            "target_families_exact_154_of_154": total_target_pass == 154,
            "intended_action_exact_ge_874_of_1152": semantic_passes["intended_action"] >= 874,
            "intended_action_exact_computed": semantic_passes["intended_action"],
            "safety_exact_1152_of_1152": safety_failures == 0,
            "deferred_checkin_exact_13_not_promoted": (
                deferred_ci["pass"] == 13 and deferred_ci["total"] == 13
            ),
            "deferred_bare_arrival_exact_13_not_promoted": (
                deferred_ba["pass"] == 13 and deferred_ba["total"] == 13
            ),
            "repeat_variance_measured_zero": not measured_variance,
            "create_exact_16": target_passes["create_new_booking"]["pass"] == 16,
            "cancel_exact_13": target_passes["cancel_call_off"]["pass"] == 13,
            "explain_exact_80": target_passes["explain_schedule_query"]["pass"] == 80,
            "status_change_exact_45": target_passes["status_change_label"]["pass"] == 45,
        },

        "report_hash": None,
    }

    report_hash = _compute_report_hash(report)
    report["report_hash"] = report_hash

    return report


def main() -> None:
    check_mode = "--check" in sys.argv

    report = _compute_report()
    report_json = json.dumps(report, indent=2, default=str, sort_keys=True) + "\n"

    if check_mode:
        if not REPORT_PATH.exists():
            print(f"Report file not found at {REPORT_PATH} — nothing to check.",
                  file=sys.stderr)
            sys.exit(1)
        existing = REPORT_PATH.read_text(encoding="utf-8")
        if existing != report_json:
            print("REPORT DRIFT DETECTED", file=sys.stderr)
            print("  Existing report differs from in-memory computation.",
                  file=sys.stderr)
            print("  Regenerate with: python scripts/bernie_lc4r3_report.py",
                  file=sys.stderr)
            sys.exit(1)
        print("LC4R3 report check passed — in-memory computation matches stored report.")
    else:
        REPORT_PATH.write_text(report_json, encoding="utf-8")
        print(f"LC4R3 report written to {REPORT_PATH}")


if __name__ == "__main__":
    main()
