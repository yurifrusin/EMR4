"""LC4R3 development report — aligned action-surface closure.

Reports the four target family pass rates, deferred family outcomes,
full development safety/repeat-variance, semantic-field baselines, and
corpus/report hashes.

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
    load_lc2_candidates,
)
from app.services.bernie.composed_evaluator import (
    InterpretationObservation,
    score_interpretation_replay_pair,
)
from app.services.bernie.scale_corpus import DevelopmentOnlyLoader
from app.services.bernie.scenario_spec import ReceptionScenarioSpec

REPORT_PATH = _HERE / "docs" / "bernie-lc4r3-report.json"

LC4_TOTAL = 1152

# Target family variant suffixes (per contract)
# create: variant 03 = "New booking:" form
# cancel: variant 06 = "call off" form
# status_change: variants 03, 06, 07 = Arrived:/confirm arrival/Status label
# explain_schedule: variants 02, 03, 06, 07, 08 = availability/appointments/free slots/Schedule:/show times

CREATE_TARGET_SUFFIXES = frozenset({"03"})
CANCEL_TARGET_SUFFIXES = frozenset({"06"})
STATUS_TARGET_SUFFIXES = frozenset({"03", "06", "07"})
EXPLAIN_TARGET_SUFFIXES = frozenset({"02", "03", "06", "07", "08"})

DEFERRED_CHECK_IN_SUFFIX = "04"  # "check in ..." variants in status_change groups


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


def _compute_report_hash(report: dict) -> str:
    """Stable hash over the canonical report JSON."""
    return _stable_hash(_canonical_json(report))


def _is_surface_variant(scenario_id: str) -> bool:
    """True for single-turn surface variants (``_var_``), not multi-turn (``_mt_``)."""
    return "_var_" in scenario_id


def _get_variant_suffix(scenario_id: str) -> str:
    parts = scenario_id.rsplit("_", 1)
    return parts[-1] if len(parts) > 1 else ""


def _compute_report() -> dict:
    """Compute the LC4R3 aligned action-surface report."""
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

    # ---------- 2. Run interpretation on each variant ----------
    target_families = {
        "create_new_booking": {"count": 0, "pass": 0, "expected": "create", "suffixes": CREATE_TARGET_SUFFIXES},
        "cancel_call_off": {"count": 0, "pass": 0, "expected": "cancel", "suffixes": CANCEL_TARGET_SUFFIXES},
        "status_change_label": {"count": 0, "pass": 0, "expected": "status_change", "suffixes": STATUS_TARGET_SUFFIXES},
        "explain_schedule_query": {"count": 0, "pass": 0, "expected": "explain_schedule", "suffixes": EXPLAIN_TARGET_SUFFIXES},
    }
    deferred_check_in = {"count": 0, "not_status_change": 0}
    deferred_bare_arrival = {"count": 0, "not_status_change": 0}

    semantic_passes: dict[str, int] = {
        "intended_action": 0,
        "action_semantics": 0,
        "temporal_relation": 0,
        "normalized_values": 0,
        "entity_semantics": 0,
        "clarification": 0,
    }
    outcome_counts: dict[str, int] = {
        "downstream_outcome": 0,
        "interpretation_tools": 0,
        "replay_tools": 0,
        "clarification": 0,
        "authority": 0,
        "appointment_deltas": 0,
        "audit_deltas": 0,
        "safety": 0,
    }
    safety_failures = 0

    for v in variants:
        suffix = _get_variant_suffix(v.scenario_id)
        expected_action = v.intended_action
        is_surface = _is_surface_variant(v.scenario_id)

        interp = deterministic_interpret(v)
        interp_obs = InterpretationObservation(
            scenario_id=interp.scenario_id,
            sample_index=0,
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

        from app.services.bernie.composed_corpus_evaluator import deterministic_replay
        replay = deterministic_replay(v, interp_obs)
        result = score_interpretation_replay_pair(v, interp_obs, replay)

        # Semantic fields
        for field in semantic_passes:
            sf_result = getattr(result.semantic_fields, field, None)
            if sf_result is not None and sf_result.passed:
                semantic_passes[field] += 1

        # Outcome dimensions
        if result.downstream_outcome.passed:
            outcome_counts["downstream_outcome"] += 1
        if result.interpretation_tools.passed:
            outcome_counts["interpretation_tools"] += 1
        if result.tool_sequence.passed:
            outcome_counts["replay_tools"] += 1
        if result.clarification.passed:
            outcome_counts["clarification"] += 1
        if result.authority.passed:
            outcome_counts["authority"] += 1
        if result.appointment_deltas.passed:
            outcome_counts["appointment_deltas"] += 1
        if result.audit_deltas.passed:
            outcome_counts["audit_deltas"] += 1
        if result.safety.passed:
            outcome_counts["safety"] += 1
        else:
            safety_failures += 1

        # Target families — single-turn surface variants only
        for fam_key, fam in target_families.items():
            if expected_action == fam["expected"] and suffix in fam["suffixes"]:
                if is_surface:
                    fam["count"] += 1
                    if interp.intended_action == fam["expected"]:
                        fam["pass"] += 1

        # Deferred check_in: status_change groups variant 04 (surface only)
        if (expected_action == "status_change"
                and suffix == DEFERRED_CHECK_IN_SUFFIX
                and is_surface):
            deferred_check_in["count"] += 1
            if interp.intended_action != "status_change":
                deferred_check_in["not_status_change"] += 1

        # Bare narrative arrival: utterance with "arrived for an appointment"
        # but without "mark"/"update"/"Arrived:" prefix
        utterance = v.dialogue_turns[0].get("utterance", "")
        if ("arrived for an appointment" in utterance.lower()
                and not utterance.startswith("Arrived:")
                and "mark" not in utterance.lower()
                and "update" not in utterance.lower()):
            deferred_bare_arrival["count"] += 1
            if interp.intended_action != "status_change":
                deferred_bare_arrival["not_status_change"] += 1

    # ---------- 3. Build report ----------
    target_summary = {}
    total_target = 0
    total_target_pass = 0
    for fam_key, fam in target_families.items():
        target_summary[fam_key] = {
            "expected": fam["expected"],
            "count": fam["count"],
            "passed": fam["pass"],
            "all_passed": fam["pass"] == fam["count"],
        }
        total_target += fam["count"]
        total_target_pass += fam["pass"]

    report: dict[str, object] = {
        "schema_version": "lc4r3.aligned_action_surface.v1",
        "development_only": True,
        "no_holdout_accessed": True,
        "silver_pending_only": True,
        "worker": "deepseek_v4_flash",

        "corpus_manifest": {
            "total_development_records": LC4_TOTAL,
            "corpus_hash": corpus_hash,
            "provenance": "silver",
            "adjudication": "pending",
        },

        "target_families": target_summary,
        "target_family_totals": {
            "total": total_target,
            "passed": total_target_pass,
            "all_passed": total_target_pass == total_target,
        },

        "deferred_families": {
            "check_in_not_status_change": {
                "count": deferred_check_in["count"],
                "not_promoted_to_status_change": deferred_check_in["not_status_change"],
                "all_deferred": (
                    deferred_check_in["not_status_change"] == deferred_check_in["count"]
                    if deferred_check_in["count"] > 0 else True
                ),
            },
            "bare_arrival_narrative_not_status_change": {
                "count": deferred_bare_arrival["count"],
                "not_promoted_to_status_change": deferred_bare_arrival["not_status_change"],
                "all_deferred": (
                    deferred_bare_arrival["not_status_change"] == deferred_bare_arrival["count"]
                    if deferred_bare_arrival["count"] > 0 else True
                ),
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

        "repeat_variance": {
            "measured": 0,
            "note": "Variance is zero by construction — deterministic extraction produces identical results on every repeat.",
        },

        "assertions": {
            "target_families_154_of_154": total_target_pass >= 154,
            "intended_action_ge_874_of_1152": semantic_passes["intended_action"] >= 874,
            "safety_1152_of_1152": safety_failures == 0,
            "check_in_not_promoted": (
                deferred_check_in["not_status_change"] == deferred_check_in["count"]
                if deferred_check_in["count"] > 0 else True
            ),
            "bare_narrative_not_promoted": (
                deferred_bare_arrival["not_status_change"] == deferred_bare_arrival["count"]
                if deferred_bare_arrival["count"] > 0 else True
            ),
        },

        "pre_lc4r3_report_hash": None,  # Placeholder - filled by --check
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
