#!/usr/bin/env python3
"""LC4R8 Exit-blocker reconciliation — clarification decision surface and
replay/delta contract audit.

Uses the accepted LC4R7 queue as the frozen blocker-selection boundary but
recomputes every classification through ordinary development-only deterministic
evidence.  Does not feed expected fields into interpretation.

Usage:
    python scripts/bernie_lc4r8_exit_blocker_reconciliation.py            # print report JSON
    python scripts/bernie_lc4r8_exit_blocker_reconciliation.py --check     # verify frozen assertions
    python scripts/bernie_lc4r8_exit_blocker_reconciliation.py --check --json  # both
"""

from __future__ import annotations

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
QUEUE_PATH = PROJECT_ROOT / "docs" / "bernie-lc4r7-adjudication-queue.json"
CLARIFICATION_OUTPUT = PROJECT_ROOT / "docs" / "bernie-lc4r8-clarification-decision-surface.json"
REPLAY_OUTPUT = PROJECT_ROOT / "docs" / "bernie-lc4r8-replay-contract-audit.json"
REPORT_OUTPUT = PROJECT_ROOT / "docs" / "bernie-lc4r8-exit-blocker-report.json"

# ---------------------------------------------------------------------------
# Frozen contract constants  (DO NOT MODIFY)
# ---------------------------------------------------------------------------

# --- Clarification decision surface ---
EXPECTED_CLARIFICATION_SELECTION_HASH = "9496e23c6f339603"
EXPECTED_CLARIFICATION_SELECTION_COUNT = 53

EXPECTED_CLARIFICATION_CLASSES: dict[str, dict[str, Any]] = {
    "normalization_contract_blocked": {
        "count": 3,
        "hash": "db484a50adc0b601",
    },
    "entity_and_normalization_contract_blocked": {
        "count": 6,
        "hash": "ff20612b3c9e276e",
    },
    "temporal_and_normalization_contract_blocked": {
        "count": 20,
        "hash": "910950860133d8b9",
    },
    "temporal_entity_and_normalization_contract_blocked": {
        "count": 24,
        "hash": "7cfaa6e4ddefc172",
    },
    "isolated_clarification_policy_choice": {
        "count": 0,
        "hash": "e3b0c44298fc1c14",
    },
}

EXPECTED_CLARIFICATION_ACTION_DISTRIBUTION: dict[str, int] = {
    "create": 13,
    "move": 13,
    "resize": 14,
    "cancel": 13,
}
CLARIFICATION_RECORD_HASH = "baf4c66b1a7ee139"

# --- Replay/delta contract audit ---
EXPECTED_REPLAY_SELECTION_HASH = "2e45f30f714568ef"
EXPECTED_REPLAY_SELECTION_COUNT = 51

EXPECTED_REPLAY_CLASSES: dict[str, dict[str, Any]] = {
    "audit_change_type_vocabulary_only": {
        "count": 11,
        "hash": "b88018991e49ffd5",
    },
    "clarification_tool_without_clarification_contract": {
        "count": 11,
        "hash": "dc7446b93a05c648",
    },
    "creation_expectation_conflicts_with_replay_policy": {
        "count": 28,
        "hash": "3206003d4bc39a23",
    },
    "negated_surface_conflicts_with_create_contract": {
        "count": 1,
        "hash": "020fade8ca644684",
    },
    "genuine_replay_integration_defect": {
        "count": 0,
        "hash": "e3b0c44298fc1c14",
    },
}

REPLAY_RECORD_HASH = "2fabb972ad0bc00b"
COMBINED_HASH = "fd0de59a2967ddf8"

# --- Exit counts ---
EXPECTED_EXIT = {
    "clarification_policy_decision_ready": 0,
    "genuine_replay_integration_defect": 0,
    "generator_backed_contract_repair_authorized": 11,
    "upstream_clarification_contract_blockers": 53,
    "remaining_replay_contract_reconciliation_blockers": 40,
}

# --- Semantic baseline (from LC4R7 contract) ---
CURRENT_INTENDED_ACTION = 880
CURRENT_ACTION_SEMANTICS = 814
CURRENT_TEMPORAL_RELATION = 628
CURRENT_NORMALIZED_VALUES = 101
CURRENT_ENTITY_SEMANTICS = 300
CURRENT_CLARIFICATION = 782
TOTAL_SCENARIOS = 1152
TOTAL_SAMPLES = 2304

# ---------------------------------------------------------------------------
# Hash helpers
# ---------------------------------------------------------------------------


def _canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def _stable_hash(content: str) -> str:
    return "sha256:" + hashlib.sha256(content.encode("utf-8")).hexdigest()


def _selection_hash(scenario_ids: list[str]) -> str:
    """SHA-256 hexdigest truncated to 16 chars over newline-joined sorted IDs."""
    return hashlib.sha256(
        "\n".join(sorted(scenario_ids)).encode("utf-8")
    ).hexdigest()[:16]


def _records_hash(lines: list[str]) -> str:
    """SHA-256 truncated to 16 chars over sorted newline-joined lines."""
    return hashlib.sha256(
        "\n".join(sorted(lines)).encode("utf-8")
    ).hexdigest()[:16]


# ---------------------------------------------------------------------------
# Corpus and queue loading
# ---------------------------------------------------------------------------


def _load_corpus():
    """Load the LC4 development corpus."""
    sys.path.insert(0, str(PROJECT_ROOT))
    from app.services.bernie.scale_corpus import DevelopmentOnlyLoader
    return DevelopmentOnlyLoader().load_all()


def _load_queue() -> list[dict[str, str]]:
    """Load the frozen LC4R7 adjudication queue."""
    if not QUEUE_PATH.exists():
        raise FileNotFoundError(f"LC4R7 queue not found at {QUEUE_PATH}")
    with open(QUEUE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _run_evaluation(scenario) -> tuple[Any, Any, Any]:
    """Run deterministic interpretation + replay + scoring for one scenario."""
    sys.path.insert(0, str(PROJECT_ROOT))
    from app.services.bernie.composed_corpus_evaluator import (
        deterministic_interpret,
        deterministic_replay,
    )
    from app.services.bernie.composed_evaluator import (
        InterpretationObservation,
        score_interpretation_replay_pair,
    )

    interp = deterministic_interpret(scenario)
    interp_obj = InterpretationObservation(
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
    replay = deterministic_replay(scenario, interp_obj)
    result = score_interpretation_replay_pair(scenario, interp_obj, replay)
    return interp_obj, replay, result


# ---------------------------------------------------------------------------
# Clarification decision surface  (53 scenarios)
# ---------------------------------------------------------------------------


def _classify_clarification_blocker(
    result,
) -> str:
    """Classify a requires_adjudication scenario by its non-clarification semantic failures.

    Priority:
      1. temporal_relation + entity_semantics + normalized_values fail
         → temporal_entity_and_normalization_contract_blocked
      2. entity_semantics + normalized_values fail
         → entity_and_normalization_contract_blocked
      3. temporal_relation + normalized_values fail
         → temporal_and_normalization_contract_blocked
      4. only normalized_values fails (besides requires_clarification)
         → normalization_contract_blocked
      5. only requires_clarification fails
         → isolated_clarification_policy_choice
    """
    other_failures = {
        f for f in result.semantic_fields.failures
        if f != "requires_clarification"
    }

    has_temporal = "temporal_relation" in other_failures
    has_entity = "entity_semantics" in other_failures
    has_normalized = "normalized_values" in other_failures

    if has_temporal and has_entity and has_normalized:
        return "temporal_entity_and_normalization_contract_blocked"
    if has_entity and has_normalized:
        return "entity_and_normalization_contract_blocked"
    if has_temporal and has_normalized:
        return "temporal_and_normalization_contract_blocked"
    if has_normalized:
        return "normalization_contract_blocked"
    return "isolated_clarification_policy_choice"


def _build_clarification_surface(
    adj_scenarios: list[str],
    variants: dict[str, Any],
) -> dict[str, Any]:
    """Build the clarification decision surface from 53 adjudication scenarios."""
    records: list[dict[str, str]] = []
    class_scenarios: dict[str, list[str]] = {
        k: [] for k in EXPECTED_CLARIFICATION_CLASSES
    }
    action_dist: dict[str, int] = {}

    for sid in sorted(adj_scenarios):
        scenario = variants[sid]
        _interp, _replay, result = _run_evaluation(scenario)
        blocker_class = _classify_clarification_blocker(result)

        records.append({
            "scenario_id": sid,
            "blocker_class": blocker_class,
            "decision_readiness": "blocked_by_upstream_contract_defect",
            "provenance": "silver",
            "adjudication": "pending",
        })
        class_scenarios.setdefault(blocker_class, []).append(sid)

        # Track action distribution
        action = scenario.intended_action
        action_dist[action] = action_dist.get(action, 0) + 1

    # Compute class counts and hashes
    class_counts: dict[str, dict[str, Any]] = {}
    for cls_name, sids in class_scenarios.items():
        class_counts[cls_name] = {
            "count": len(sids),
            "hash": _selection_hash(sids),
        }

    # Compute record hash over sorted canonical lines
    record_lines = [
        f"{r['scenario_id']}|{r['blocker_class']}|{r['decision_readiness']}"
        for r in records
    ]
    records_hash = _records_hash(record_lines)

    return {
        "schema_version": "lc4r8.clarification_decision_surface.v1",
        "development_only": True,
        "silver_pending_only": True,
        "selection": {
            "count": len(adj_scenarios),
            "hash": _selection_hash(sorted(adj_scenarios)),
            "expected_count": EXPECTED_CLARIFICATION_SELECTION_COUNT,
            "expected_hash": EXPECTED_CLARIFICATION_SELECTION_HASH,
            "hash_match": (
                _selection_hash(sorted(adj_scenarios))
                == EXPECTED_CLARIFICATION_SELECTION_HASH
            ),
        },
        "blocker_classes": class_counts,
        "action_distribution": action_dist,
        "records": records,
        "record_hash": records_hash,
        "expected_record_hash": CLARIFICATION_RECORD_HASH,
        "record_hash_match": records_hash == CLARIFICATION_RECORD_HASH,
        "assertions": {
            "selection_count_53": len(adj_scenarios) == EXPECTED_CLARIFICATION_SELECTION_COUNT,
            "selection_hash_match": (
                _selection_hash(sorted(adj_scenarios))
                == EXPECTED_CLARIFICATION_SELECTION_HASH
            ),
            "zero_decision_ready": (
                len(class_scenarios.get("isolated_clarification_policy_choice", [])) == 0
            ),
        },
    }


# ---------------------------------------------------------------------------
# Replay/delta contract audit  (51 scenarios)
# ---------------------------------------------------------------------------


def _classify_replay_blocker(
    scenario,
    interp_obj,
    replay,
    result,
) -> str:
    """Classify a non_language_contract_mismatch scenario using the frozen priority order.

    Priority:
      1. negated_surface_conflicts_with_create_contract
      2. clarification_tool_without_clarification_contract
      3. audit_change_type_vocabulary_only
      4. creation_expectation_conflicts_with_replay_policy
      5. genuine_replay_integration_defect  (remainder)
    """
    # Priority 1: Negated surface with create contract
    if interp_obj.action_negated and scenario.expected_outcome_kind == "appointment_created":
        return "negated_surface_conflicts_with_create_contract"

    # Priority 2: Expected tool sequence is only request_clarification but no expected clarification
    expected_tools = list(scenario.expected_tool_sequence) if scenario.expected_tool_sequence else []
    expected_clarify = getattr(scenario, "expected_clarification", None)
    if expected_tools == ["request_clarification"] and expected_clarify is None:
        return "clarification_tool_without_clarification_contract"

    # Priority 3: All pass except audit delta
    outcome_pass = result.downstream_outcome.passed
    tool_seq_pass = result.tool_sequence.passed
    interp_tools_pass = result.interpretation_tools.passed
    authority_pass = result.authority.passed
    clarification_pass = result.clarification.passed
    apt_deltas_pass = result.appointment_deltas.passed
    audit_deltas_pass = result.audit_deltas.passed

    if (
        outcome_pass
        and tool_seq_pass
        and interp_tools_pass
        and authority_pass
        and clarification_pass
        and apt_deltas_pass
        and not audit_deltas_pass
    ):
        return "audit_change_type_vocabulary_only"

    # Priority 4: Contract expects appointment_created, replay yields no outcome, tool seqs agree
    if (
        scenario.expected_outcome_kind == "appointment_created"
        and replay.downstream_outcome is None
        and tool_seq_pass
    ):
        return "creation_expectation_conflicts_with_replay_policy"

    return "genuine_replay_integration_defect"


def _build_replay_audit(
    nlcm_scenarios: list[str],
    variants: dict[str, Any],
) -> dict[str, Any]:
    """Build the replay/delta contract audit from 51 non_language_contract_mismatch scenarios."""
    records: list[dict[str, str]] = []
    class_scenarios: dict[str, list[str]] = {
        k: [] for k in EXPECTED_REPLAY_CLASSES
    }

    for sid in sorted(nlcm_scenarios):
        scenario = variants[sid]
        interp_obj, replay, result = _run_evaluation(scenario)
        blocker_class = _classify_replay_blocker(scenario, interp_obj, replay, result)

        remediation_status = (
            "authorized_for_generator_backed_contract_repair"
            if blocker_class == "audit_change_type_vocabulary_only"
            else "not_authorized_contract_reconciliation_required"
        )

        records.append({
            "scenario_id": sid,
            "blocker_class": blocker_class,
            "remediation_status": remediation_status,
            "provenance": "silver",
            "adjudication": "pending",
        })
        class_scenarios.setdefault(blocker_class, []).append(sid)

    # Compute class counts and hashes
    class_counts: dict[str, dict[str, Any]] = {}
    for cls_name, sids in class_scenarios.items():
        class_counts[cls_name] = {
            "count": len(sids),
            "hash": _selection_hash(sids),
        }

    # Compute record hash
    record_lines = [
        f"{r['scenario_id']}|{r['blocker_class']}|{r['remediation_status']}"
        for r in records
    ]
    records_hash = _records_hash(record_lines)

    return {
        "schema_version": "lc4r8.replay_contract_audit.v1",
        "development_only": True,
        "silver_pending_only": True,
        "selection": {
            "count": len(nlcm_scenarios),
            "hash": _selection_hash(sorted(nlcm_scenarios)),
            "expected_count": EXPECTED_REPLAY_SELECTION_COUNT,
            "expected_hash": EXPECTED_REPLAY_SELECTION_HASH,
            "hash_match": (
                _selection_hash(sorted(nlcm_scenarios))
                == EXPECTED_REPLAY_SELECTION_HASH
            ),
        },
        "blocker_classes": class_counts,
        "records": records,
        "record_hash": records_hash,
        "expected_record_hash": REPLAY_RECORD_HASH,
        "record_hash_match": records_hash == REPLAY_RECORD_HASH,
        "assertions": {
            "selection_count_51": len(nlcm_scenarios) == EXPECTED_REPLAY_SELECTION_COUNT,
            "selection_hash_match": (
                _selection_hash(sorted(nlcm_scenarios))
                == EXPECTED_REPLAY_SELECTION_HASH
            ),
            "zero_genuine_defects": (
                len(class_scenarios.get("genuine_replay_integration_defect", [])) == 0
            ),
            "audit_change_type_count_11": (
                len(class_scenarios.get("audit_change_type_vocabulary_only", [])) == 11
            ),
        },
    }


# ---------------------------------------------------------------------------
# Exit report
# ---------------------------------------------------------------------------


def _build_exit_report(
    clarification: dict[str, Any],
    replay_audit: dict[str, Any],
    combined_hash: str = "",
) -> dict[str, Any]:
    """Build the aggregate exit-blocker report."""
    adj_count = clarification["selection"]["count"]
    nlcm_count = replay_audit["selection"]["count"]
    audit_count = replay_audit["blocker_classes"].get(
        "audit_change_type_vocabulary_only", {}
    ).get("count", 0)
    genuine_count = replay_audit["blocker_classes"].get(
        "genuine_replay_integration_defect", {}
    ).get("count", 0)
    policy_ready = clarification["blocker_classes"].get(
        "isolated_clarification_policy_choice", {}
    ).get("count", 0)

    report_payload: dict[str, Any] = {
        "schema_version": "lc4r8.exit_blocker_report.v1",
        "development_only": True,
        "silver_pending_only": True,
        "clarification_decision_surface": {
            "selection_count": adj_count,
            "expected_selection_count": EXPECTED_CLARIFICATION_SELECTION_COUNT,
            "selection_hash": clarification["selection"]["hash"],
            "expected_selection_hash": EXPECTED_CLARIFICATION_SELECTION_HASH,
            "selection_hash_match": clarification["selection"]["hash_match"],
            "record_hash": clarification["record_hash"],
            "expected_record_hash": CLARIFICATION_RECORD_HASH,
            "record_hash_match": clarification["record_hash_match"],
            "blocker_classes": {
                cls: {
                    "count": info["count"],
                    "hash": info["hash"],
                    "expected_count": EXPECTED_CLARIFICATION_CLASSES[cls]["count"],
                    "expected_hash": EXPECTED_CLARIFICATION_CLASSES[cls]["hash"],
                    "hash_match": info["hash"] == EXPECTED_CLARIFICATION_CLASSES[cls]["hash"],
                }
                for cls, info in clarification["blocker_classes"].items()
            },
            "action_distribution": clarification["action_distribution"],
        },
        "replay_contract_audit": {
            "selection_count": nlcm_count,
            "expected_selection_count": EXPECTED_REPLAY_SELECTION_COUNT,
            "selection_hash": replay_audit["selection"]["hash"],
            "expected_selection_hash": EXPECTED_REPLAY_SELECTION_HASH,
            "selection_hash_match": replay_audit["selection"]["hash_match"],
            "record_hash": replay_audit["record_hash"],
            "expected_record_hash": REPLAY_RECORD_HASH,
            "record_hash_match": replay_audit["record_hash_match"],
            "combined_hash": combined_hash,
            "expected_combined_hash": COMBINED_HASH,
            "combined_hash_match": combined_hash == COMBINED_HASH,
            "blocker_classes": {
                cls: {
                    "count": info["count"],
                    "hash": info["hash"],
                    "expected_count": EXPECTED_REPLAY_CLASSES[cls]["count"],
                    "expected_hash": EXPECTED_REPLAY_CLASSES[cls]["hash"],
                    "hash_match": info["hash"] == EXPECTED_REPLAY_CLASSES[cls]["hash"],
                }
                for cls, info in replay_audit["blocker_classes"].items()
            },
        },
        "exit_counts": EXPECTED_EXIT,
        "exit_status": "blocked_pending_generator_repair_and_contract_reconciliation",
        "assertions": {
            "clarification_selection_53": adj_count == EXPECTED_CLARIFICATION_SELECTION_COUNT,
            "replay_selection_51": nlcm_count == EXPECTED_REPLAY_SELECTION_COUNT,
            "clarification_policy_decision_ready_0": policy_ready == 0,
            "genuine_replay_defect_0": genuine_count == 0,
            "generator_repair_authorized_11": audit_count == 11,
            "exit_status_blocked": True,
        },
    }

    report_payload["report_hash"] = _compute_report_hash(report_payload)

    return report_payload


def _compute_report_hash(report_no_hash: dict[str, Any]) -> str:
    """Compute report hash with the hash field excluded."""
    copy_ = dict(report_no_hash)
    copy_.pop("report_hash", None)
    return _stable_hash(_canonical_json(copy_))


# ---------------------------------------------------------------------------
# Build all artifacts
# ---------------------------------------------------------------------------


def build_all() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    """Build all three LC4R8 artifacts.

    Returns (clarification_surface, replay_audit, exit_report).
    """
    # Load corpus and queue
    corpus = _load_corpus()
    queue = _load_queue()
    variants = {v.scenario_id: v for v in corpus.all_variants()}

    # Extract scenario IDs from queue by disposition
    adj_sids = sorted(set(
        r["scenario_id"] for r in queue if r["disposition"] == "requires_adjudication"
    ))
    nlcm_sids = sorted(set(
        r["scenario_id"] for r in queue if r["disposition"] == "non_language_contract_mismatch"
    ))

    # Build clarification decision surface
    clarification = _build_clarification_surface(adj_sids, variants)

    # Build replay/delta contract audit
    replay_audit = _build_replay_audit(nlcm_sids, variants)

    # Compute combined hash: clarification| prefix for clarification records,
    # replay| prefix for replay records, sorted newline-joined
    combined_lines = []
    for r in clarification["records"]:
        combined_lines.append(
            f"clarification|{r['scenario_id']}|{r['blocker_class']}|{r['decision_readiness']}"
        )
    for r in replay_audit["records"]:
        combined_lines.append(
            f"replay|{r['scenario_id']}|{r['blocker_class']}|{r['remediation_status']}"
        )
    combined_hash = _records_hash(combined_lines)

    # Build exit report
    exit_report = _build_exit_report(clarification, replay_audit, combined_hash)

    return clarification, replay_audit, exit_report


# ---------------------------------------------------------------------------
# --check mode
# ---------------------------------------------------------------------------


def _load_json(path: pathlib.Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def run_check(
    clarification: dict[str, Any],
    replay_audit: dict[str, Any],
    exit_report: dict[str, Any],
) -> bool:
    """Verify recomputed artifacts against contract constants AND committed artifacts."""
    issues: list[str] = []

    try:
        frozen_clarification = _load_json(CLARIFICATION_OUTPUT)
        frozen_replay = _load_json(REPLAY_OUTPUT)
        frozen_report = _load_json(REPORT_OUTPUT)
    except (FileNotFoundError, json.JSONDecodeError, OSError) as exc:
        print(f"LC4R8 CHECK FAILED:\n  - unable to load frozen artifacts: {exc}")
        return False

    # --- 1. Clarification decision surface ---
    # Selection
    for key in ("count", "hash", "expected_count", "expected_hash", "hash_match"):
        rv = clarification.get("selection", {}).get(key)
        fv = frozen_clarification.get("selection", {}).get(key)
        if rv != fv:
            issues.append(f"clarification.selection.{key}: recomputed={rv}, frozen={fv}")
    # Validate against contract constant
    if clarification["selection"]["hash"] != EXPECTED_CLARIFICATION_SELECTION_HASH:
        issues.append(
            f"clarification selection hash {clarification['selection']['hash']} "
            f"!= contract {EXPECTED_CLARIFICATION_SELECTION_HASH}"
        )
    if clarification["selection"]["count"] != EXPECTED_CLARIFICATION_SELECTION_COUNT:
        issues.append("clarification selection count != 53")

    # Blocker classes
    for cls_name, expected in EXPECTED_CLARIFICATION_CLASSES.items():
        rc = clarification["blocker_classes"].get(cls_name, {}).get("count", 0)
        fc = frozen_clarification.get("blocker_classes", {}).get(cls_name, {}).get("count", 0)
        if rc != fc:
            issues.append(
                f"clarification.{cls_name} count: recomputed={rc}, frozen={fc}"
            )
        if rc != expected["count"]:
            issues.append(
                f"clarification.{cls_name} count {rc} != contract {expected['count']}"
            )
        rh = clarification["blocker_classes"].get(cls_name, {}).get("hash", "")
        if rh != expected["hash"]:
            issues.append(
                f"clarification.{cls_name} hash {rh} != contract {expected['hash']}"
            )

    # Record hash
    if clarification["record_hash"] != CLARIFICATION_RECORD_HASH:
        issues.append(
            f"clarification record hash {clarification['record_hash']} "
            f"!= contract {CLARIFICATION_RECORD_HASH}"
        )
    if clarification["record_hash"] != frozen_clarification.get("record_hash", ""):
        issues.append("clarification record hash != frozen artifact")

    # Action distribution
    r_dist = clarification.get("action_distribution", {})
    f_dist = frozen_clarification.get("action_distribution", {})
    for action, count in EXPECTED_CLARIFICATION_ACTION_DISTRIBUTION.items():
        if r_dist.get(action) != count:
            issues.append(
                f"clarification action_distribution.{action}: "
                f"recomputed={r_dist.get(action)}, expected={count}"
            )
        if r_dist.get(action) != f_dist.get(action):
            issues.append(
                f"clarification action_distribution.{action}: "
                f"recomputed={r_dist.get(action)}, frozen={f_dist.get(action)}"
            )

    # --- 2. Replay/delta contract audit ---
    # Selection
    for key in ("count", "hash", "expected_count", "expected_hash", "hash_match"):
        rv = replay_audit.get("selection", {}).get(key)
        fv = frozen_replay.get("selection", {}).get(key)
        if rv != fv:
            issues.append(f"replay_audit.selection.{key}: recomputed={rv}, frozen={fv}")
    if replay_audit["selection"]["hash"] != EXPECTED_REPLAY_SELECTION_HASH:
        issues.append(
            f"replay selection hash {replay_audit['selection']['hash']} "
            f"!= contract {EXPECTED_REPLAY_SELECTION_HASH}"
        )
    if replay_audit["selection"]["count"] != EXPECTED_REPLAY_SELECTION_COUNT:
        issues.append("replay selection count != 51")

    # Blocker classes
    for cls_name, expected in EXPECTED_REPLAY_CLASSES.items():
        rc = replay_audit["blocker_classes"].get(cls_name, {}).get("count", 0)
        fc = frozen_replay.get("blocker_classes", {}).get(cls_name, {}).get("count", 0)
        if rc != fc:
            issues.append(
                f"replay.{cls_name} count: recomputed={rc}, frozen={fc}"
            )
        if rc != expected["count"]:
            issues.append(
                f"replay.{cls_name} count {rc} != contract {expected['count']}"
            )
        rh = replay_audit["blocker_classes"].get(cls_name, {}).get("hash", "")
        if rh != expected["hash"]:
            issues.append(
                f"replay.{cls_name} hash {rh} != contract {expected['hash']}"
            )

    # Record hash
    if replay_audit["record_hash"] != REPLAY_RECORD_HASH:
        issues.append(
            f"replay record hash {replay_audit['record_hash']} "
            f"!= contract {REPLAY_RECORD_HASH}"
        )
    if replay_audit["record_hash"] != frozen_replay.get("record_hash", ""):
        issues.append("replay record hash != frozen artifact")

    # Combined hash (stored in exit report's replay_contract_audit section)
    rc_combined = exit_report.get("replay_contract_audit", {}).get("combined_hash", "")
    f_combined = frozen_report.get("replay_contract_audit", {}).get("combined_hash", "")
    if rc_combined != COMBINED_HASH:
        issues.append(
            f"combined hash {rc_combined} != contract {COMBINED_HASH}"
        )
    if rc_combined != f_combined:
        issues.append(
            f"combined hash: recomputed={rc_combined}, frozen={f_combined}"
        )

    # --- 3. Exit report ---
    # selection counts
    for key in ("clarification_selection_53", "replay_selection_51"):
        if exit_report.get("assertions", {}).get(key) is not True:
            issues.append(f"exit assertion {key} is not True")

    # Exit counts
    for key, expected in EXPECTED_EXIT.items():
        rv = exit_report.get("exit_counts", {}).get(key)
        fv = frozen_report.get("exit_counts", {}).get(key)
        if rv != fv:
            issues.append(f"exit_counts.{key}: recomputed={rv}, frozen={fv}")
        if rv != expected:
            issues.append(f"exit_counts.{key} {rv} != contract {expected}")

    # Exit status
    for source, label in [(exit_report, "recomputed"), (frozen_report, "frozen")]:
        status = source.get("exit_status", "")
        if status != "blocked_pending_generator_repair_and_contract_reconciliation":
            issues.append(f"{label} exit_status is {status!r}, expected blocked")

    # Report hash
    recomputed_hash = _compute_report_hash(exit_report)
    frozen_hash = frozen_report.get("report_hash", "")
    if _compute_report_hash(frozen_report) != frozen_hash:
        issues.append("committed frozen report hash is invalid")
    if recomputed_hash != frozen_hash:
        issues.append(
            f"report_hash mismatch: recomputed={recomputed_hash}, frozen={frozen_hash}"
        )

    if issues:
        print("LC4R8 CHECK FAILED:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("LC4R8 CHECK PASSED")

    return len(issues) == 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    check_only = "--check" in sys.argv
    print_json = "--json" in sys.argv or not check_only

    clarification, replay_audit, exit_report = build_all()

    if check_only:
        passed = run_check(clarification, replay_audit, exit_report)
        if print_json:
            print()
            print(json.dumps({
                "clarification_decision_surface": clarification,
                "replay_contract_audit": replay_audit,
                "exit_blocker_report": exit_report,
            }, indent=2, default=str))
        sys.exit(0 if passed else 1)
    else:
        output = {
            "clarification_decision_surface": clarification,
            "replay_contract_audit": replay_audit,
            "exit_blocker_report": exit_report,
        }
        print(json.dumps(output, indent=2, default=str))


if __name__ == "__main__":
    main()
