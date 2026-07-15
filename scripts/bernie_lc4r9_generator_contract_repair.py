#!/usr/bin/env python3
"""LC4R9 Generator-backed contract repair — helper script.

Validates the generator allowlist, pre/post audit vocabulary, non-selected
scenario drift (by exact pre-repair reconstruction), hash cascade (recomputed),
composed evaluator result, semantic/safety/variance baselines, and exit evidence.

Usage:
    python scripts/bernie_lc4r9_generator_contract_repair.py            # print report JSON
    python scripts/bernie_lc4r9_generator_contract_repair.py --check     # verify frozen assertions
"""

from __future__ import annotations

import copy
import hashlib
import json
import pathlib
import sys
from typing import Any

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

HERE = pathlib.Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parent
FIXTURE_DIR = PROJECT_ROOT / "tests" / "fixtures" / "bernie_lc4_development"
DOCS_DIR = PROJECT_ROOT / "docs"
REPORT_OUTPUT = DOCS_DIR / "bernie-lc4r9-generator-contract-repair.json"
CLARIFICATION_SURFACE = DOCS_DIR / "bernie-lc4r8-clarification-decision-surface.json"
REPLAY_AUDIT = DOCS_DIR / "bernie-lc4r8-replay-contract-audit.json"

# ---------------------------------------------------------------------------
# Frozen contract constants  (DO NOT MODIFY)
# ---------------------------------------------------------------------------

ALLOWLIST_SELECTION_HASH = "b88018991e49ffd5"
ALLOWLIST_COUNT = 11

ALLOWLIST_SCENARIO_IDS: list[str] = [
    "lc4_dw1_dev_var_001_01",
    "lc4_dw1_dev_var_001_02",
    "lc4_dw1_dev_var_001_03",
    "lc4_dw1_dev_var_001_05",
    "lc4_dw1_dev_var_001_06",
    "lc4_dw1_dev_var_001_07",
    "lc4_dw1_dev_var_001_08",
    "lc4_dw1_dev_var_001_09",
    "lc4_dw1_dev_var_012_03",
    "lc4_dw1_dev_var_012_05",
    "lc4_dw1_dev_var_012_07",
]

PRE_REPAIR_DELTA_HASH = (
    "14e3648ae8a98598bbc091ce16bf29f31fd5b2fdb92fe7d817ae86fb21837c69"
)

# Expected audit deltas after repair
EXPECTED_AUDIT_DELTA = {"change_type": "created", "appointment_id": "apt-001", "count": 1}
# Pre-repair vocabulary (what the old code generated)
PRE_REPAIR_AUDIT_DELTA = {"change_type": "create_requested", "appointment_id": "apt-001", "count": 1}

# The pre-repair fixture hashes (from committed state before repair)
PRE_REPAIR_GROUP_001_HASH = "sha256:0874f6887020df0ae9abe0ca75a9ee60bc9eb0d55094701fbf5a48788cd71e5d"
PRE_REPAIR_GROUP_012_HASH = "sha256:76a4a27c6d217dcfd0fa4a96ea42b1416201b31fdb87af39c4bb32040f7fb9b6"
PRE_REPAIR_CORPUS_HASH = "sha256:aa2d946b60694eab96846ed77e885273c807e127f8998981a8cf8ff20ebae647"

# Semantic/safety/variance baseline (unchanged by this repair)
EXPECTED_SEMANTIC_COUNTS = (880, 814, 628, 101, 300, 782)
EXPECTED_SAFETY_PER_REPEAT = (1152, 1152)
EXPECTED_VARIANCE_SAMPLES = 2304
EXPECTED_EXIT_COUNTS = {
    "generator_repair_authorized": 0,
    "clarification_blockers": 53,
    "replay_contract_reconciliation_blockers": 40,
}
EXPECTED_CLARIFICATION_SELECTION_HASH = "9496e23c6f339603"
EXPECTED_REPLAY_SELECTION_HASH = "2e45f30f714568ef"
EXPECTED_REMAINING_REPLAY_HASH = "defe4c59877753e9"
POST_REPAIR_GROUP_001_HASH = "sha256:b1e33767b127856e25095c907b14a40a6f88e6522af0cc1841e9baa3bdeff6d7"
POST_REPAIR_GROUP_012_HASH = "sha256:90d321501e51df4e1b91aa94997e3470b3d26c2678ca61045ad8c6c63abdc5c0"
POST_REPAIR_CORPUS_HASH = "sha256:f11e98f9bc61b962da0e816fbb918d7f722d3f82c57dfde18a5e323c1b24e9e1"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _stable_hash(content: str) -> str:
    return "sha256:" + hashlib.sha256(content.encode("utf-8")).hexdigest()


def _canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def _selection_hash(scenario_ids: list[str]) -> str:
    return hashlib.sha256(
        "\n".join(sorted(scenario_ids)).encode("utf-8")
    ).hexdigest()[:16]


def _load_fixture(path: pathlib.Path) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def committed_report_matches(report: dict[str, Any], path: pathlib.Path = REPORT_OUTPUT) -> bool:
    """Return false, rather than raising, for a missing, malformed, or drifted artifact."""
    try:
        frozen = _load_fixture(path)
    except (FileNotFoundError, json.JSONDecodeError, OSError, TypeError, ValueError):
        return False
    return frozen == report


def compute_variant_hash(variant_data: dict[str, Any]) -> str:
    """Deterministic hash of a single canonical variant payload (strips variant_hash)."""
    payload = {k: v for k, v in variant_data.items() if k != "variant_hash"}
    canonical = _canonical_json(payload)
    return _stable_hash(canonical)


def compute_group_hash_from_data(group_data: dict[str, Any]) -> str:
    """Deterministic hash of a group's semantic profile AND all variant hashes."""
    canonical = _canonical_json(group_data)
    return _stable_hash(canonical)


def compute_corpus_hash(group_hashes: list[str]) -> str:
    """Deterministic corpus hash from chained group hashes."""
    corpus_hash_input = _canonical_json(group_hashes)
    return _stable_hash(corpus_hash_input)


# ---------------------------------------------------------------------------
# Core checks
# ---------------------------------------------------------------------------


def check_allowlist_invariants() -> dict[str, Any]:
    """Verify the allowlist hash, count, and surface-only constraint."""
    result: dict[str, Any] = {
        "check": "allowlist_invariants",
        "passed": False,
        "details": {},
    }

    computed_count = len(ALLOWLIST_SCENARIO_IDS)
    computed_hash = hashlib.sha256(
        "\n".join(sorted(ALLOWLIST_SCENARIO_IDS)).encode("utf-8")
    ).hexdigest()[:16]

    count_ok = computed_count == ALLOWLIST_COUNT
    hash_ok = computed_hash == ALLOWLIST_SELECTION_HASH

    # All must be surface variants
    surface_ok = all(sid.startswith("lc4_dw1_dev_var") for sid in ALLOWLIST_SCENARIO_IDS)

    result["details"] = {
        "count": {"expected": ALLOWLIST_COUNT, "got": computed_count, "match": count_ok},
        "hash": {"expected": ALLOWLIST_SELECTION_HASH, "got": computed_hash, "match": hash_ok},
        "surface_only": surface_ok,
    }
    result["passed"] = count_ok and hash_ok and surface_ok
    return result


def check_vocabulary_change() -> dict[str, Any]:
    """Verify the 11 selected scenarios now have 'created' audit vocabulary."""
    result: dict[str, Any] = {
        "check": "vocabulary_change",
        "passed": False,
        "details": {},
    }

    overridden: list[str] = []
    missing: list[str] = []
    source = "app/services/bernie/scale_corpus.py (generator allowlist)"

    # Load from files to verify committed state
    for sid in sorted(ALLOWLIST_SCENARIO_IDS):
        parts = sid.split("_")
        group_idx = int(parts[4])
        group_file = FIXTURE_DIR / f"lc4_dw1_dev_group_{group_idx:03d}.json"
        if not group_file.exists():
            missing.append(sid)
            continue
        gdata = _load_fixture(group_file)
        found = False
        for vdata in gdata.get("surface_variants", []):
            if vdata.get("scenario_id") == sid:
                found = True
                aud_deltas = vdata.get("expected_audit_deltas", [])
                if aud_deltas and aud_deltas[0].get("change_type") == "created":
                    overridden.append(sid)
                else:
                    missing.append(sid)
                break
        if not found:
            missing.append(sid)

    result["details"] = {
        "source": source,
        "expected_count": ALLOWLIST_COUNT,
        "overridden_count": len(overridden),
        "overridden_ids": overridden,
        "missing_ids": missing,
    }
    result["passed"] = len(overridden) == ALLOWLIST_COUNT and len(missing) == 0
    return result


def check_hash_cascade() -> dict[str, Any]:
    """Recompute the current variant/group/corpus hash chain from fixture data.

    Fails closed on any drift between recomputed hashes and frozen post-repair
    identities stored in the manifest.
    """
    result: dict[str, Any] = {
        "check": "hash_cascade",
        "passed": False,
        "details": {},
    }

    manifest = _load_fixture(FIXTURE_DIR / "lc4_development_manifest.json")

    # Recompute variant hashes for every variant in every group
    errors: list[str] = []
    group_hash_results: list[dict[str, Any]] = []
    all_recomputed_group_hashes: list[str] = []

    for g_entry in manifest.get("groups", []):
        fname = g_entry["filename"]
        gdata = _load_fixture(FIXTURE_DIR / fname)

        # Recompute variant hashes
        variant_hash_errors: list[str] = []
        for vdata in gdata.get("surface_variants", []):
            sid = vdata.get("scenario_id", "?")
            stored = vdata.get("variant_hash", "")
            recomputed = compute_variant_hash(vdata)
            if stored != recomputed:
                variant_hash_errors.append(
                    f"{sid}: stored={stored}, recomputed={recomputed}"
                )
        for vdata in gdata.get("multi_turn_variants", []):
            sid = vdata.get("scenario_id", "?")
            stored = vdata.get("variant_hash", "")
            recomputed = compute_variant_hash(vdata)
            if stored != recomputed:
                variant_hash_errors.append(
                    f"{sid} (mt): stored={stored}, recomputed={recomputed}"
                )

        # Recompute group hash
        surface_hashes = [
            compute_variant_hash(vd) for vd in gdata.get("surface_variants", [])
        ]
        multi_turn_hashes = [
            compute_variant_hash(vd) for vd in gdata.get("multi_turn_variants", [])
        ]
        spec = gdata.get("spec", {})
        recomputed_group_data = {
            "group_id": gdata["group_id"],
            "spec": spec,
            "surface_count": len(surface_hashes),
            "multi_turn_count": len(multi_turn_hashes),
            "surface_variant_hashes": surface_hashes,
            "multi_turn_variant_hashes": multi_turn_hashes,
        }
        recomputed_group_hash = compute_group_hash_from_data(recomputed_group_data)
        stored_group_hash = g_entry.get("group_hash", "")

        group_hash_match = recomputed_group_hash == stored_group_hash
        if not group_hash_match:
            variant_hash_errors.append(
                f"group {gdata.get('group_id')}: stored={stored_group_hash}, "
                f"recomputed={recomputed_group_hash}"
            )

        all_recomputed_group_hashes.append(recomputed_group_hash)

        group_hash_results.append({
            "group_index": g_entry.get("group_index"),
            "group_id": gdata.get("group_id"),
            "stored_hash": stored_group_hash,
            "recomputed_hash": recomputed_group_hash,
            "match": group_hash_match,
            "variant_hash_errors": variant_hash_errors,
        })
        errors.extend(variant_hash_errors)

    # Recompute corpus hash from chained group hashes
    recomputed_corpus_hash = compute_corpus_hash(all_recomputed_group_hashes)
    stored_corpus_hash = manifest.get("corpus_hash", "")
    corpus_hash_match = recomputed_corpus_hash == stored_corpus_hash
    if not corpus_hash_match:
        errors.append(
            f"corpus hash: stored={stored_corpus_hash}, "
            f"recomputed={recomputed_corpus_hash}"
        )

    group_001_hash = next(
        (g["group_hash"] for g in manifest.get("groups", []) if g["group_index"] == 1),
        "NOT_FOUND",
    )
    group_012_hash = next(
        (g["group_hash"] for g in manifest.get("groups", []) if g["group_index"] == 12),
        "NOT_FOUND",
    )
    frozen_hashes_match = (
        group_001_hash == POST_REPAIR_GROUP_001_HASH
        and group_012_hash == POST_REPAIR_GROUP_012_HASH
        and stored_corpus_hash == POST_REPAIR_CORPUS_HASH
    )
    if not frozen_hashes_match:
        errors.append("post-repair group/corpus identities differ from frozen contract")

    result["details"] = {
        "group_001_hash": group_001_hash,
        "group_012_hash": group_012_hash,
        "corpus_hash": stored_corpus_hash,
        "frozen_hashes_match": frozen_hashes_match,
        "recomputed_corpus_hash": recomputed_corpus_hash,
        "corpus_hash_match": corpus_hash_match,
        "group_hashes": group_hash_results,
        "errors": errors,
    }
    result["passed"] = len(errors) == 0
    return result


def check_composed_evaluator(corpus) -> dict[str, Any]:
    """Run the composed evaluator (interpretation + replay + scoring) on all scenarios.

    Uses the same ordinary development-only deterministic interpretation, replay,
    and composed score path used by LC4R8. Requires the complete composed result
    to pass for every selected scenario, not merely the expected audit-delta equality.
    """
    result: dict[str, Any] = {
        "check": "composed_evaluator",
        "passed": False,
        "details": {},
    }

    from app.services.bernie.scale_corpus import LC4R9_AUDIT_VOCABULARY_ALLOWLIST
    from app.services.bernie.composed_corpus_evaluator import deterministic_interpret, deterministic_replay
    from app.services.bernie.composed_evaluator import score_interpretation_replay_pair

    passed = 0
    failed: list[dict[str, Any]] = []

    # Run on all scenarios, but report only for allowlist ones
    for g in corpus.groups:
        for v in g.all_variants:
            if v.scenario_id not in LC4R9_AUDIT_VOCABULARY_ALLOWLIST:
                continue
            # Run deterministic interpretation
            interp = deterministic_interpret(v)
            # Run deterministic replay
            replay = deterministic_replay(v, interp)
            # Score the pair
            score = score_interpretation_replay_pair(v, interp, replay)
            if score.all_passed:
                passed += 1
            else:
                failed.append({
                    "scenario_id": v.scenario_id,
                    "failure_layers": list(score.failure_layers),
                    "semantic_fields_failures": score.semantic_fields.failures,
                    "outcome_passed": score.downstream_outcome.passed,
                    "tool_seq_passed": score.tool_sequence.passed,
                    "authority_passed": score.authority.passed,
                    "audit_deltas_passed": score.audit_deltas.passed,
                })

    result["details"] = {
        "selected_scenario_count": ALLOWLIST_COUNT,
        "composed_passed_count": passed,
        "composed_failed_count": len(failed),
        "composed_failed": failed,
    }
    result["passed"] = passed == ALLOWLIST_COUNT and len(failed) == 0
    return result


def check_semantic_safety_baseline(corpus) -> dict[str, Any]:
    """Recompute semantic/safety/variance baselines through the evaluator.

    Uses two deterministic samples (num_repeats=2) for 2,304 total samples.
    Checks against the frozen expected counts:
      semantic: (880, 814, 628, 101, 300, 782)
      safety: (1152, 1152)
      variance: zero over 2304 samples
    """
    result: dict[str, Any] = {
        "check": "semantic_safety_baseline",
        "passed": False,
        "details": {},
    }

    from app.services.bernie.composed_corpus_evaluator import deterministic_interpret, deterministic_replay
    from app.services.bernie.composed_evaluator import score_interpretation_replay_pair

    num_repeats = 2
    total_expected = len(list(corpus.all_variants())) * num_repeats

    # Aggregate counts
    intended_action_pass = 0
    action_semantics_pass = 0
    temporal_relation_pass = 0
    normalized_values_pass = 0
    entity_semantics_pass = 0
    clarification_pass = 0
    downstream_outcome_pass = 0
    authority_pass = 0
    safety_pass = 0
    safety_by_repeat = [0 for _ in range(num_repeats)]
    audit_deltas_pass = 0

    scenario_fingerprints: dict[str, set[tuple]] = {}

    for v in corpus.all_variants():
        for sample_idx in range(num_repeats):
            interp = deterministic_interpret(v)
            replay = deterministic_replay(v, interp)
            score = score_interpretation_replay_pair(v, interp, replay)

            if score.semantic_fields.intended_action.passed:
                intended_action_pass += 1
            if score.semantic_fields.action_semantics.passed:
                action_semantics_pass += 1
            if score.semantic_fields.temporal_relation.passed:
                temporal_relation_pass += 1
            if score.semantic_fields.normalized_values.passed:
                normalized_values_pass += 1
            if score.semantic_fields.entity_semantics.passed:
                entity_semantics_pass += 1
            if score.semantic_fields.clarification.passed:
                clarification_pass += 1
            if score.downstream_outcome.passed:
                downstream_outcome_pass += 1
            if score.authority.passed:
                authority_pass += 1
            if score.safety.passed:
                safety_pass += 1
                safety_by_repeat[sample_idx] += 1
            if score.audit_deltas.passed:
                audit_deltas_pass += 1

            # Fingerprint for variance detection
            def _canonicalize_for_hash(val):
                if isinstance(val, dict):
                    return tuple(sorted((k, _canonicalize_for_hash(v)) for k, v in val.items()))
                if isinstance(val, (list, tuple)):
                    return tuple(_canonicalize_for_hash(v) for v in val)
                return val
            fp = (
                score.semantic_fields.intended_action.observed,
                score.semantic_fields.action_semantics.observed,
                score.semantic_fields.temporal_relation.observed,
                score.downstream_outcome.comparison.observed,
                score.authority.authority_claim,
                _canonicalize_for_hash(tuple(score.audit_deltas.observed)),
            )
            scenario_fingerprints.setdefault(v.scenario_id, set()).add(fp)

    # Variance: count scenarios with >1 fingerprint across repeats
    variant_scenario_count = sum(
        1 for fps in scenario_fingerprints.values() if len(fps) > 1
    )
    variant_sample_count = sum(
        num_repeats for sid, fps in scenario_fingerprints.items() if len(fps) > 1
    )

    semantic_counts = (
        intended_action_pass,
        action_semantics_pass,
        temporal_relation_pass,
        normalized_values_pass,
        entity_semantics_pass,
        clarification_pass,
    )

    semantic_ok = semantic_counts == tuple(c * num_repeats for c in EXPECTED_SEMANTIC_COUNTS)
    safety_ok = tuple(safety_by_repeat) == EXPECTED_SAFETY_PER_REPEAT
    variance_ok = (variant_scenario_count == 0 and variant_sample_count == 0
                   and total_expected == EXPECTED_VARIANCE_SAMPLES)

    result["details"] = {
        "total_samples": total_expected,
        "semantic_counts": {
            "intended_action_pass": intended_action_pass,
            "action_semantics_pass": action_semantics_pass,
            "temporal_relation_pass": temporal_relation_pass,
            "normalized_values_pass": normalized_values_pass,
            "entity_semantics_pass": entity_semantics_pass,
            "clarification_pass": clarification_pass,
            "expected": list(EXPECTED_SEMANTIC_COUNTS),
            "match": semantic_ok,
        },
        "safety": {
            "per_repeat_passed": safety_by_repeat,
            "expected_per_repeat_passed": list(EXPECTED_SAFETY_PER_REPEAT),
            "total_passed": safety_pass,
            "total_samples": total_expected,
            "match": safety_ok,
        },
        "variance": {
            "variant_scenario_count": variant_scenario_count,
            "variant_sample_count": variant_sample_count,
            "total_samples": total_expected,
            "expected_zero_variance": True,
            "expected_samples": EXPECTED_VARIANCE_SAMPLES,
            "match": variance_ok,
        },
    }
    result["passed"] = semantic_ok and safety_ok and variance_ok
    return result


def check_exit_evidence(corpus) -> dict[str, Any]:
    """Recompute post-repair LC4R8 replay selection and exit counts.

    The 11 repaired scenarios must leave the generator-repair class (pass
    composed evaluation). The other 40 replay contract-reconciliation blockers
    must remain. The 53 clarification blockers must remain.
    Exit status: blocked_pending_contract_reconciliation.
    """
    result: dict[str, Any] = {
        "check": "exit_evidence",
        "passed": False,
        "details": {},
    }

    from app.services.bernie.composed_corpus_evaluator import deterministic_interpret, deterministic_replay
    from app.services.bernie.composed_evaluator import score_interpretation_replay_pair

    clarification_records = _load_fixture(CLARIFICATION_SURFACE).get("records", [])
    replay_records = _load_fixture(REPLAY_AUDIT).get("records", [])
    clarification_ids = [record["scenario_id"] for record in clarification_records]
    repair_ids = [
        record["scenario_id"] for record in replay_records
        if record.get("blocker_class") == "audit_change_type_vocabulary_only"
    ]
    remaining_replay_ids = [
        record["scenario_id"] for record in replay_records
        if record.get("blocker_class") != "audit_change_type_vocabulary_only"
    ]
    variants = {variant.scenario_id: variant for variant in corpus.all_variants()}
    selection_errors: list[str] = []
    if len(clarification_ids) != 53 or _selection_hash(clarification_ids) != EXPECTED_CLARIFICATION_SELECTION_HASH:
        selection_errors.append("LC4R8 clarification selection drift")
    if len(replay_records) != 51 or _selection_hash([record["scenario_id"] for record in replay_records]) != EXPECTED_REPLAY_SELECTION_HASH:
        selection_errors.append("LC4R8 replay selection drift")
    if len(repair_ids) != 11 or _selection_hash(repair_ids) != ALLOWLIST_SELECTION_HASH:
        selection_errors.append("LC4R8 generator-repair selection drift")
    if len(remaining_replay_ids) != 40 or _selection_hash(remaining_replay_ids) != EXPECTED_REMAINING_REPLAY_HASH:
        selection_errors.append("LC4R8 remaining replay selection drift")
    missing_ids = sorted(
        (set(clarification_ids) | set(repair_ids) | set(remaining_replay_ids))
        - set(variants)
    )
    if missing_ids:
        selection_errors.append(f"development scenarios missing: {missing_ids}")

    def _score(scenario_id: str):
        scenario = variants[scenario_id]
        interpretation = deterministic_interpret(scenario)
        replay = deterministic_replay(scenario, interpretation)
        return score_interpretation_replay_pair(scenario, interpretation, replay)

    repair_failures = [sid for sid in repair_ids if sid in variants and not _score(sid).all_passed]
    remaining_replay_passes = [
        sid for sid in remaining_replay_ids if sid in variants and _score(sid).all_passed
    ]
    clarification_unblocked = []
    for sid in clarification_ids:
        if sid not in variants:
            continue
        score = _score(sid)
        if "requires_clarification" not in score.semantic_fields.failures:
            clarification_unblocked.append(sid)

    generator_repair_remaining = len(repair_failures)
    clarification_blockers = len(clarification_ids) - len(clarification_unblocked)
    replay_blockers = len(remaining_replay_ids) - len(remaining_replay_passes)

    counts = {
        "generator_repair_authorized": generator_repair_remaining,
        "clarification_blockers": clarification_blockers,
        "replay_contract_reconciliation_blockers": replay_blockers,
    }
    counts_match = counts == EXPECTED_EXIT_COUNTS

    result["details"] = {
        "exit_counts": counts,
        "expected_counts": EXPECTED_EXIT_COUNTS,
        "counts_match": counts_match,
        "selection_hashes": {
            "clarification": _selection_hash(clarification_ids),
            "replay_all": _selection_hash([record["scenario_id"] for record in replay_records]),
            "repaired": _selection_hash(repair_ids),
            "remaining_replay": _selection_hash(remaining_replay_ids),
        },
        "repair_failures": repair_failures,
        "remaining_replay_unexpected_passes": remaining_replay_passes,
        "clarification_unblocked": clarification_unblocked,
        "selection_errors": selection_errors,
        "clarification_blocker_count": clarification_blockers,
        "replay_blocker_count": replay_blockers,
        "total_scenarios": len(list(corpus.all_variants())),
        "exit_status": "blocked_pending_contract_reconciliation",
    }
    result["passed"] = counts_match and not selection_errors
    return result


def check_non_selected_drift() -> dict[str, Any]:
    """Prove the exact corpus delta by reconstructing pre-repair state.

    Revert only the 11 selected audit deltas from 'created' back to
    'create_requested', recompute variant hashes for those variants,
    recompute group 001 and 012 hashes, and the corpus chain, and require
    the frozen pre-repair hashes from the contract.

    Also requires every other group hash/reference to be unchanged by
    this reconstruction.
    """
    result: dict[str, Any] = {
        "check": "non_selected_drift",
        "passed": False,
        "details": {},
    }

    manifest = _load_fixture(FIXTURE_DIR / "lc4_development_manifest.json")
    errors: list[str] = []
    pre_repair_group_001_hash = None
    pre_repair_group_012_hash = None

    all_recomputed_group_hashes: list[str] = []

    for g_entry in manifest.get("groups", []):
        fname = g_entry["filename"]
        gdata = _load_fixture(FIXTURE_DIR / fname)
        gidx = g_entry.get("group_index")

        # Deep-copy the group data so we can mutate it
        gdata_reconstructed = copy.deepcopy(gdata)

        # Revert only the 11 selected audit deltas in the copy
        for vdata in gdata_reconstructed.get("surface_variants", []):
            sid = vdata.get("scenario_id", "")
            if sid in ALLOWLIST_SCENARIO_IDS:
                # Revert audit delta from 'created' back to 'create_requested'
                for aud in vdata.get("expected_audit_deltas", []):
                    if aud.get("change_type") == "created":
                        aud["change_type"] = "create_requested"

        # Recompute variant hashes for the reconstructed data
        surface_hashes = [
            compute_variant_hash(vd) for vd in gdata_reconstructed.get("surface_variants", [])
        ]
        multi_turn_hashes = [
            compute_variant_hash(vd) for vd in gdata_reconstructed.get("multi_turn_variants", [])
        ]

        spec = gdata.get("spec", {})
        recomputed_group_data = {
            "group_id": gdata["group_id"],
            "spec": spec,
            "surface_count": len(surface_hashes),
            "multi_turn_count": len(multi_turn_hashes),
            "surface_variant_hashes": surface_hashes,
            "multi_turn_variant_hashes": multi_turn_hashes,
        }
        recomputed_group_hash = compute_group_hash_from_data(recomputed_group_data)
        all_recomputed_group_hashes.append(recomputed_group_hash)

        if gidx == 1:
            pre_repair_group_001_hash = recomputed_group_hash
            if recomputed_group_hash != PRE_REPAIR_GROUP_001_HASH:
                errors.append(
                    f"Group 001 pre-repair hash mismatch: "
                    f"expected {PRE_REPAIR_GROUP_001_HASH}, "
                    f"got {recomputed_group_hash}"
                )
        elif gidx == 12:
            pre_repair_group_012_hash = recomputed_group_hash
            if recomputed_group_hash != PRE_REPAIR_GROUP_012_HASH:
                errors.append(
                    f"Group 012 pre-repair hash mismatch: "
                    f"expected {PRE_REPAIR_GROUP_012_HASH}, "
                    f"got {recomputed_group_hash}"
                )
        else:
            # Every other group must be unchanged by reconstruction
            stored_hash = g_entry.get("group_hash", "")
            if recomputed_group_hash != stored_hash:
                errors.append(
                    f"Group {gidx} should be unchanged but hash changed: "
                    f"stored={stored_hash}, reconstructed={recomputed_group_hash}"
                )

    # Recompute corpus hash from reconstructed group hashes
    recomputed_corpus_hash = compute_corpus_hash(all_recomputed_group_hashes)
    if recomputed_corpus_hash != PRE_REPAIR_CORPUS_HASH:
        errors.append(
            f"Pre-repair corpus hash mismatch: "
            f"expected {PRE_REPAIR_CORPUS_HASH}, "
            f"got {recomputed_corpus_hash}"
        )

    result["details"] = {
        "pre_repair_reconstructed_group_001_hash": pre_repair_group_001_hash or "N/A",
        "expected_pre_repair_group_001_hash": PRE_REPAIR_GROUP_001_HASH,
        "pre_repair_reconstructed_group_012_hash": pre_repair_group_012_hash or "N/A",
        "expected_pre_repair_group_012_hash": PRE_REPAIR_GROUP_012_HASH,
        "pre_repair_reconstructed_corpus_hash": recomputed_corpus_hash,
        "expected_pre_repair_corpus_hash": PRE_REPAIR_CORPUS_HASH,
        "reconstruction_passed": len(errors) == 0,
        "errors": errors,
    }
    result["passed"] = len(errors) == 0
    return result


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def run_all(corpus) -> dict[str, Any]:
    """Run all checks and return a report dict."""
    checks = {
        "allowlist_invariants": check_allowlist_invariants(),
        "vocabulary_change": check_vocabulary_change(),
        "non_selected_drift": check_non_selected_drift(),
        "hash_cascade": check_hash_cascade(),
        "composed_evaluator": check_composed_evaluator(corpus),
        "semantic_safety_baseline": check_semantic_safety_baseline(corpus),
        "exit_evidence": check_exit_evidence(corpus),
    }

    all_passed = all(c["passed"] for c in checks.values())

    # Gather hash evidence
    manifest = _load_fixture(FIXTURE_DIR / "lc4_development_manifest.json")
    g001_hash = next((g["group_hash"] for g in manifest.get("groups", []) if g["group_index"] == 1), "?")
    g012_hash = next((g["group_hash"] for g in manifest.get("groups", []) if g["group_index"] == 12), "?")

    report: dict[str, Any] = {
        "schema": "lc4r9.generator_contract_repair.v1",
        "development_only": True,
        "silver_pending_only": True,
        "allowlist": {
            "count": ALLOWLIST_COUNT,
            "hash": ALLOWLIST_SELECTION_HASH,
            "ids": sorted(ALLOWLIST_SCENARIO_IDS),
        },
        "pre_repair_delta_hash": PRE_REPAIR_DELTA_HASH,
        "frozen_post_repair_hashes": {
            "group_001_hash": POST_REPAIR_GROUP_001_HASH,
            "group_012_hash": POST_REPAIR_GROUP_012_HASH,
            "corpus_hash": POST_REPAIR_CORPUS_HASH,
        },
        "frozen_pre_repair_hashes": {
            "group_001_hash": PRE_REPAIR_GROUP_001_HASH,
            "group_012_hash": PRE_REPAIR_GROUP_012_HASH,
            "corpus_hash": PRE_REPAIR_CORPUS_HASH,
        },
        "checks": checks,
        "all_passed": all_passed,
    }
    return report


def main() -> None:
    import sys as _sys
    _sys.path.insert(0, str(PROJECT_ROOT))

    from app.services.bernie.scale_corpus import (
        DevelopmentOnlyLoader,
        _validate_lc4r9_allowlist,
    )

    # Validate the source allowlist (fail-closed)
    _validate_lc4r9_allowlist()

    # Load the committed fixtures
    loader = DevelopmentOnlyLoader()
    corpus = loader.load_all()

    report = run_all(corpus)

    if "--write" in _sys.argv:
        DOCS_DIR.mkdir(parents=True, exist_ok=True)
        with open(REPORT_OUTPUT, "w", encoding="utf-8", newline="\n") as f:
            json.dump(report, f, indent=2)
            f.write("\n")

    print(json.dumps(report, indent=2))

    if "--check" in _sys.argv:
        artifact_matches = committed_report_matches(report)
        if report["all_passed"] and artifact_matches:
            print("\nLC4R9 CHECK PASSED")
            _sys.exit(0)
        else:
            if not artifact_matches:
                print("\nLC4R9 committed report differs from recomputed evidence")
            print("\nLC4R9 CHECK FAILED")
            _sys.exit(1)


if __name__ == "__main__":
    main()
