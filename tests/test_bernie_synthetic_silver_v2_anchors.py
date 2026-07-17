"""Focused tests for v2 dialogue-free anchor builder and coherence validator.

Tests cover exact 96/192 target math, action/form/cell balance, unique IDs
and hashes, deterministic regeneration, no dialogue/descriptions in anchors,
exact source binding, access flags, coherence invariants, contradiction-class
rejection, correction and local-recovery form contracts, and import isolation.
"""

from __future__ import annotations

import ast
import json
from collections import Counter
from pathlib import Path

from app.services.bernie.synthetic_noise_v2 import (
    ACTIONS_V2,
    ANCHOR_COUNT_V2,
    DEFAULT_SEED_PATH_V2,
    FORMS_V2,
    build_v2_anchor_manifest,
    check_v2_anchor_manifest,
    validate_v2_anchor_manifest,
)
from app.services.bernie.corpus_tier import compute_scenario_hash
from app.services.bernie.scale_corpus import DevelopmentOnlyLoader

# ==========================================================================
# Structure, balance, determinism
# ==========================================================================


def test_anchor_count_is_96() -> None:
    manifest = build_v2_anchor_manifest()
    assert manifest["anchor_count"] == ANCHOR_COUNT_V2 == 96
    assert len(manifest["anchors"]) == 96


def test_candidate_count_is_192() -> None:
    manifest = build_v2_anchor_manifest()
    # Two candidates per anchor = 192
    assert manifest["anchor_count"] * 2 == 192


def test_action_balance() -> None:
    manifest = build_v2_anchor_manifest()
    action_counts = Counter(
        a["semantic_contract"]["intended_action"]
        for a in manifest["anchors"]
    )
    assert len(action_counts) == 6
    for action in ACTIONS_V2:
        assert action_counts[action] == 16, (
            f"Action {action!r} has {action_counts[action]} anchors, "
            f"expected 16"
        )


def test_form_balance() -> None:
    manifest = build_v2_anchor_manifest()
    form_counts = Counter(
        a["dialogue_form_contract"]["dialogue_form"]
        for a in manifest["anchors"]
    )
    assert len(form_counts) == 8
    for form in FORMS_V2:
        assert form_counts[form] == 12, (
            f"Form {form!r} has {form_counts[form]} anchors, expected 12"
        )


def test_every_action_form_cell_has_exactly_two_anchors() -> None:
    manifest = build_v2_anchor_manifest()
    cells: dict[tuple[str, str], int] = {}
    for a in manifest["anchors"]:
        key = (
            a["semantic_contract"]["intended_action"],
            a["dialogue_form_contract"]["dialogue_form"],
        )
        cells[key] = cells.get(key, 0) + 1
    for action in ACTIONS_V2:
        for form in FORMS_V2:
            assert cells.get((action, form)) == 2, (
                f"Cell ({action}, {form}) has "
                f"{cells.get((action, form))} anchors, expected 2"
            )


def test_unique_seed_ids() -> None:
    manifest = build_v2_anchor_manifest()
    ids = [a["seed_id"] for a in manifest["anchors"]]
    assert len(ids) == len(set(ids))


def test_unique_seed_hashes() -> None:
    manifest = build_v2_anchor_manifest()
    hashes = [a["seed_hash"] for a in manifest["anchors"]]
    assert len(hashes) == len(set(hashes))


def test_deterministic_regeneration() -> None:
    first = build_v2_anchor_manifest()
    second = build_v2_anchor_manifest()
    assert first == second


def test_committed_fixture_matches_regeneration() -> None:
    manifest = build_v2_anchor_manifest()
    committed = json.loads(
        DEFAULT_SEED_PATH_V2.read_text(encoding="utf-8")
    )
    assert committed == manifest


def test_validate_committed_fixture() -> None:
    errors = check_v2_anchor_manifest()
    assert errors == [], f"Fixture check failed: {errors}"


# ==========================================================================
# No dialogue, descriptions, or source spans in anchors
# ==========================================================================


def test_no_source_dialogue_in_anchors() -> None:
    manifest = build_v2_anchor_manifest()
    serialized = json.dumps(manifest["anchors"], sort_keys=True)
    assert '"dialogue_turns"' not in serialized
    assert '"utterance"' not in serialized
    assert '"description"' not in serialized


def test_contains_source_utterances_false() -> None:
    manifest = build_v2_anchor_manifest()
    assert manifest["contains_source_utterances"] is False
    for a in manifest["anchors"]:
        assert a["contains_source_utterances"] is False


# ==========================================================================
# Source binding and hash
# ==========================================================================


def test_every_anchor_has_source_scenario_id_and_hash() -> None:
    manifest = build_v2_anchor_manifest()
    sources = {
        scenario.scenario_id: scenario
        for scenario in DevelopmentOnlyLoader().load_all().all_variants()
    }
    for a in manifest["anchors"]:
        dfc = a["dialogue_form_contract"]
        sb = dfc["source_bindings"]
        assert sb["source_scenario_id"], (
            f"Missing scenario_id in {a['seed_id']}"
        )
        assert sb["source_scenario_hash"], (
            f"Missing scenario_hash in {a['seed_id']}"
        )
        assert sb["source_scenario_hash"].startswith("sha256:")
        source = sources[sb["source_scenario_id"]]
        assert sb["source_scenario_hash"] == compute_scenario_hash(source)
        assert source.intended_action == a["semantic_contract"]["intended_action"]


def test_anchor_source_hash_matches_dialogue_form_contract() -> None:
    manifest = build_v2_anchor_manifest()
    for a in manifest["anchors"]:
        top_hash = a["source_scenario_hash"]
        dfc_hash = a["dialogue_form_contract"]["source_bindings"][
            "source_scenario_hash"
        ]
        assert top_hash == dfc_hash, (
            f"Hash mismatch in {a['seed_id']}: "
            f"{top_hash} != {dfc_hash}"
        )


# ==========================================================================
# Authority and access flags
# ==========================================================================


def test_all_authority_grants_false() -> None:
    manifest = build_v2_anchor_manifest()
    for a in manifest["anchors"]:
        auth = a["authority_grant"]
        assert auth == {
            "provider_write": False,
            "diary_write": False,
            "confirmation": False,
            "override_authority": False,
        }, (
            f"Authority grant not all false in {a['seed_id']}: {auth}"
        )
        # Also check in dialogue_form_contract
        dfc_auth = a["dialogue_form_contract"]["authority_grant"]
        assert dfc_auth == auth


def test_all_access_flags_false() -> None:
    manifest = build_v2_anchor_manifest()
    for flag in (
        "contains_source_utterances",
        "protected_holdout_access",
        "historical_diary_access",
        "external_corpus_access",
    ):
        assert manifest[flag] is False, (
            f"Manifest {flag} should be false"
        )


# ==========================================================================
# Coherence invariants -- mutation
# ==========================================================================


def test_mutation_anchors_have_tools_outcome_deltas() -> None:
    """Standard mutation anchors must have tools, outcome, and deltas."""
    manifest = build_v2_anchor_manifest()
    mutation_forms = {
        "one_shot",
        "correction",
        "ellipsis",
        "anaphora",
        "repeated_request",
        "session_restart",
    }
    for a in manifest["anchors"]:
        form = a["dialogue_form_contract"]["dialogue_form"]
        if form not in mutation_forms:
            continue
        sc = a["semantic_contract"]
        assert sc["expected_tool_sequence"], (
            f"{a['seed_id']} ({form}) has empty tool sequence"
        )
        assert sc["expected_outcome_kind"] is not None, (
            f"{a['seed_id']} ({form}) has null outcome"
        )
        action = sc["intended_action"]
        if action != "explain_schedule":
            assert sc["expected_appointment_deltas"], (
                f"{a['seed_id']} ({form}) has empty appointment deltas"
            )
            assert sc["expected_audit_deltas"], (
                f"{a['seed_id']} ({form}) has empty audit deltas"
            )


def test_successful_mutation_contracts_use_canonical_surfaced_delta_shapes() -> None:
    manifest = build_v2_anchor_manifest()
    change_types = {
        "create": "created",
        "move": "moved",
        "resize": "resized",
        "cancel": "cancelled",
        "status_change": "status_changed",
    }
    for anchor in manifest["anchors"]:
        form = anchor["dialogue_form_contract"]["dialogue_form"]
        sc = anchor["semantic_contract"]
        if form in {"clarification", "reversal"} or sc["intended_action"] == "explain_schedule":
            continue
        change_type = change_types[sc["intended_action"]]
        values = sc["normalized_values"]
        assert sc["expected_appointment_deltas"] == [{
            "appointment_id": "apt-001",
            "change_type": change_type,
            "patient_id": "p-001",
            "practitioner_id": "pr-001",
            "date": values["appointment_date"],
            "start_time": values.get("earliest_time", ""),
            "duration_minutes": values.get("duration_minutes", 15),
        }]
        assert sc["expected_audit_deltas"] == [{
            "change_type": change_type,
            "appointment_id": "apt-001",
            "count": 1,
        }]


# ==========================================================================
# Coherence invariants -- schedule explanation
# ==========================================================================


def test_schedule_explanation_has_no_deltas() -> None:
    manifest = build_v2_anchor_manifest()
    for a in manifest["anchors"]:
        sc = a["semantic_contract"]
        form = a["dialogue_form_contract"]["dialogue_form"]
        if sc["intended_action"] != "explain_schedule":
            continue
        if form in ("clarification", "reversal"):
            continue
        assert sc["expected_outcome_kind"] == "schedule_explained", (
            f"{a['seed_id']} outcome should be schedule_explained"
        )
        assert sc["expected_appointment_deltas"] == [], (
            f"{a['seed_id']} should have empty appointment deltas"
        )
        assert sc["expected_audit_deltas"] == [], (
            f"{a['seed_id']} should have empty audit deltas"
        )
        assert sc["expected_tool_sequence"] == ["find_slots"]


# ==========================================================================
# Coherence invariants -- clarification
# ==========================================================================


def test_clarification_anchors_have_question_and_choices() -> None:
    manifest = build_v2_anchor_manifest()
    for a in manifest["anchors"]:
        form = a["dialogue_form_contract"]["dialogue_form"]
        if form != "clarification":
            continue
        sc = a["semantic_contract"]
        assert sc["expected_clarification"] is not None, (
            f"{a['seed_id']} missing clarification question"
        )
        assert len(sc["clarification_choices"]) >= 2, (
            f"{a['seed_id']} needs at least 2 choices"
        )
        assert sc["expected_tool_sequence"] == ["request_clarification"], (
            f"{a['seed_id']} tool sequence must be [request_clarification]"
        )
        assert sc["expected_outcome_kind"] == "clarification_required", (
            f"{a['seed_id']} outcome must be clarification_required"
        )
        assert sc["expected_appointment_deltas"] == [], (
            f"{a['seed_id']} should have empty appointment deltas"
        )
        assert sc["expected_audit_deltas"] == [], (
            f"{a['seed_id']} should have empty audit deltas"
        )
        assert sc["action_withdrawn"] is False, (
            f"{a['seed_id']} clarification must not be withdrawn"
        )


def test_clarification_variant_1_is_patient_ambiguity() -> None:
    manifest = build_v2_anchor_manifest()
    for a in manifest["anchors"]:
        form = a["dialogue_form_contract"]["dialogue_form"]
        cv = a["dialogue_form_contract"]["cell_variant"]
        if form != "clarification" or cv != 1:
            continue
        sc = a["semantic_contract"]
        target = a["dialogue_form_contract"]["ambiguity_target"]
        q = sc["expected_clarification"]
        if sc["intended_action"] == "explain_schedule":
            assert target == "practitioner"
            assert sc["patient_semantics"] == "omitted"
            assert sc["practitioner_semantics"] == "ambiguous"
            assert "practitioner" in q.lower()
        else:
            assert target == "patient"
            assert sc["patient_semantics"] == "ambiguous"
            assert sc["practitioner_semantics"] == "exact"
            assert "patient" in q.lower()


def test_clarification_variant_2_is_practitioner_ambiguity() -> None:
    manifest = build_v2_anchor_manifest()
    for a in manifest["anchors"]:
        form = a["dialogue_form_contract"]["dialogue_form"]
        cv = a["dialogue_form_contract"]["cell_variant"]
        if form != "clarification" or cv != 2:
            continue
        q = a["semantic_contract"]["expected_clarification"]
        assert a["dialogue_form_contract"]["ambiguity_target"] == "practitioner"
        assert a["semantic_contract"]["practitioner_semantics"] == "ambiguous"
        assert "practitioner" in q.lower(), (
            f"{a['seed_id']} variant 2 should mention practitioner: {q}"
        )


# ==========================================================================
# Coherence invariants -- reversal
# ==========================================================================


def test_reversal_anchors_withdrawn_no_outcome_no_deltas() -> None:
    manifest = build_v2_anchor_manifest()
    for a in manifest["anchors"]:
        form = a["dialogue_form_contract"]["dialogue_form"]
        if form != "reversal":
            continue
        sc = a["semantic_contract"]
        assert sc["action_withdrawn"] is True, (
            f"{a['seed_id']} reversal must have action_withdrawn=true"
        )
        assert sc["expected_outcome_kind"] is None, (
            f"{a['seed_id']} reversal must have null outcome"
        )
        assert sc["expected_appointment_deltas"] == [], (
            f"{a['seed_id']} reversal must have empty appointment deltas"
        )
        assert sc["expected_audit_deltas"] == [], (
            f"{a['seed_id']} reversal must have empty audit deltas"
        )


def test_reversal_tool_sequence() -> None:
    """Reversal tool list: search_patients when patient exact, else empty."""
    manifest = build_v2_anchor_manifest()
    for a in manifest["anchors"]:
        form = a["dialogue_form_contract"]["dialogue_form"]
        if form != "reversal":
            continue
        sc = a["semantic_contract"]
        tools = sc["expected_tool_sequence"]
        if sc["patient_semantics"] == "exact":
            assert tools == ["search_patients"], (
                f"{a['seed_id']} reversal should use [search_patients], "
                f"got {tools}"
            )
        else:
            assert tools == [], (
                f"{a['seed_id']} reversal should have empty tools, "
                f"got {tools}"
            )


# ==========================================================================
# Coherence invariants -- correction
# ==========================================================================


def test_correction_anchors_have_tools_and_outcome() -> None:
    manifest = build_v2_anchor_manifest()
    for a in manifest["anchors"]:
        form = a["dialogue_form_contract"]["dialogue_form"]
        if form != "correction":
            continue
        sc = a["semantic_contract"]
        assert sc["expected_tool_sequence"], (
            f"{a['seed_id']} correction needs tools"
        )
        assert sc["expected_outcome_kind"] is not None, (
            f"{a['seed_id']} correction needs non-null outcome"
        )
        dfc = a["dialogue_form_contract"]
        assert sc["practitioner_semantics"] == "corrected"
        assert sc["entity_state"] == "corrected"
        assert dfc["correction_target"] == "practitioner"
        assert dfc["prior_value"] == "Dr Patel"
        assert dfc["final_value"] == "Dr Shera"
        assert "explicit_replacement_cue" in dfc["surface_requirements"]


# ==========================================================================
# Coherence invariants -- ellipsis/anaphora/repeated/session_restart
# ==========================================================================


def test_local_recovery_forms_have_tools_outcome_deltas() -> None:
    manifest = build_v2_anchor_manifest()
    recovery_forms = {
        "ellipsis",
        "anaphora",
        "repeated_request",
        "session_restart",
    }
    for a in manifest["anchors"]:
        form = a["dialogue_form_contract"]["dialogue_form"]
        if form not in recovery_forms:
            continue
        sc = a["semantic_contract"]
        assert sc["expected_tool_sequence"], (
            f"{a['seed_id']} ({form}) needs tools"
        )
        assert sc["expected_outcome_kind"] is not None, (
            f"{a['seed_id']} ({form}) needs non-null outcome"
        )
        if sc["intended_action"] != "explain_schedule":
            assert sc["expected_appointment_deltas"], (
                f"{a['seed_id']} ({form}) needs appointment deltas"
            )
        dfc = a["dialogue_form_contract"]
        if form in {"ellipsis", "anaphora"}:
            assert dfc["local_recovery_required"] is True
            assert "antecedent_in_prior_turn" in dfc["surface_requirements"]


# ==========================================================================
# Contradiction-class rejection tests
# ==========================================================================


def test_validator_rejects_missing_mutation_outcome() -> None:
    manifest = build_v2_anchor_manifest()
    for anchor in manifest["anchors"]:
        if anchor["dialogue_form_contract"]["dialogue_form"] == "one_shot":
            anchor["semantic_contract"]["expected_outcome_kind"] = None
            break
    errors = validate_v2_anchor_manifest(manifest)
    assert any("non-null" in e for e in errors), (
        f"Expected rejection of null outcome, got: {errors}"
    )


def test_validator_rejects_empty_clarification_choices() -> None:
    manifest = build_v2_anchor_manifest()
    for anchor in manifest["anchors"]:
        if anchor["dialogue_form_contract"]["dialogue_form"] == "clarification":
            anchor["semantic_contract"]["clarification_choices"] = []
            break
    errors = validate_v2_anchor_manifest(manifest)
    assert any("at least 2" in e for e in errors), (
        f"Expected rejection of empty choices, got: {errors}"
    )


def test_validator_rejects_clarification_without_ambiguous_entity() -> None:
    manifest = build_v2_anchor_manifest()
    for anchor in manifest["anchors"]:
        sc = anchor["semantic_contract"]
        if (
            anchor["dialogue_form_contract"]["dialogue_form"] == "clarification"
            and sc["intended_action"] != "explain_schedule"
        ):
            sc["patient_semantics"] = "exact"
            break
    errors = validate_v2_anchor_manifest(manifest)
    assert any("patient ambiguity" in error for error in errors)


def test_validator_rejects_correction_without_replacement_contract() -> None:
    manifest = build_v2_anchor_manifest()
    for anchor in manifest["anchors"]:
        if anchor["dialogue_form_contract"]["dialogue_form"] == "correction":
            anchor["dialogue_form_contract"]["prior_value"] = None
            break
    errors = validate_v2_anchor_manifest(manifest)
    assert any("explicit practitioner replacement" in error for error in errors)


def test_validator_rejects_clarification_with_wrong_tool() -> None:
    manifest = build_v2_anchor_manifest()
    for anchor in manifest["anchors"]:
        if anchor["dialogue_form_contract"]["dialogue_form"] == "clarification":
            anchor["semantic_contract"]["expected_tool_sequence"] = [
                "search_patients"
            ]
            break
    errors = validate_v2_anchor_manifest(manifest)
    assert any("request_clarification" in e for e in errors), (
        f"Expected rejection of wrong tool, got: {errors}"
    )


def test_validator_rejects_clarification_with_appointment_deltas() -> None:
    manifest = build_v2_anchor_manifest()
    for anchor in manifest["anchors"]:
        if anchor["dialogue_form_contract"]["dialogue_form"] == "clarification":
            anchor["semantic_contract"]["expected_appointment_deltas"] = [
                {"change_type": "created"}
            ]
            break
    errors = validate_v2_anchor_manifest(manifest)
    assert any("empty appointment" in e for e in errors), (
        f"Expected rejection of non-empty deltas, got: {errors}"
    )


def test_validator_rejects_reversal_with_outcome() -> None:
    manifest = build_v2_anchor_manifest()
    for anchor in manifest["anchors"]:
        if anchor["dialogue_form_contract"]["dialogue_form"] == "reversal":
            anchor["semantic_contract"]["expected_outcome_kind"] = (
                "appointment_cancelled"
            )
            break
    errors = validate_v2_anchor_manifest(manifest)
    assert any("null outcome" in e for e in errors), (
        f"Expected rejection of non-null outcome, got: {errors}"
    )


def test_validator_rejects_reversal_with_deltas() -> None:
    manifest = build_v2_anchor_manifest()
    for anchor in manifest["anchors"]:
        if anchor["dialogue_form_contract"]["dialogue_form"] == "reversal":
            anchor["semantic_contract"]["expected_appointment_deltas"] = [
                {"change_type": "cancelled"}
            ]
            break
    errors = validate_v2_anchor_manifest(manifest)
    assert any("empty appointment" in e for e in errors), (
        f"Expected rejection of non-empty deltas, got: {errors}"
    )


def test_validator_rejects_reversal_with_wrong_tools() -> None:
    manifest = build_v2_anchor_manifest()
    for anchor in manifest["anchors"]:
        if anchor["dialogue_form_contract"]["dialogue_form"] == "reversal":
            sc = anchor["semantic_contract"]
            if sc["patient_semantics"] == "exact":
                sc["expected_tool_sequence"] = []
            else:
                sc["expected_tool_sequence"] = ["search_patients"]
            break
    errors = validate_v2_anchor_manifest(manifest)
    assert any("tool expectation" in e for e in errors), (
        f"Expected rejection of wrong tools, got: {errors}"
    )


def test_validator_rejects_schedule_explanation_with_deltas() -> None:
    manifest = build_v2_anchor_manifest()
    for anchor in manifest["anchors"]:
        sc = anchor["semantic_contract"]
        form = anchor["dialogue_form_contract"]["dialogue_form"]
        if (
            sc["intended_action"] == "explain_schedule"
            and form not in ("clarification", "reversal")
        ):
            sc["expected_appointment_deltas"] = [{"change_type": "created"}]
            break
    errors = validate_v2_anchor_manifest(manifest)
    assert any("empty appointment" in e for e in errors), (
        f"Expected rejection of non-empty deltas, got: {errors}"
    )


def test_validator_rejects_wrong_action_withdrawn() -> None:
    manifest = build_v2_anchor_manifest()
    for anchor in manifest["anchors"]:
        if anchor["dialogue_form_contract"]["dialogue_form"] != "reversal":
            anchor["semantic_contract"]["action_withdrawn"] = True
            break
    errors = validate_v2_anchor_manifest(manifest)
    assert any("action_withdrawn=false" in e for e in errors), (
        f"Expected rejection of wrong action_withdrawn, got: {errors}"
    )


def test_validator_rejects_seed_hash_mismatch() -> None:
    manifest = build_v2_anchor_manifest()
    manifest["anchors"][0]["seed_hash"] = "sha256:" + "0" * 64
    errors = validate_v2_anchor_manifest(manifest)
    assert any("seed hash mismatch" in e for e in errors), (
        f"Expected rejection of hash mismatch, got: {errors}"
    )


def test_validator_rejects_source_hash_mismatch() -> None:
    manifest = build_v2_anchor_manifest()
    manifest["anchors"][0]["source_scenario_hash"] = "sha256:" + "0" * 64
    errors = validate_v2_anchor_manifest(manifest)
    assert any("source scenario hash mismatch" in error for error in errors)


def test_validator_rejects_authority_grant() -> None:
    manifest = build_v2_anchor_manifest()
    manifest["anchors"][0]["authority_grant"]["diary_write"] = True
    errors = validate_v2_anchor_manifest(manifest)
    assert any("all false" in e for e in errors), (
        f"Expected rejection of authority grant, got: {errors}"
    )


def test_validator_rejects_source_utterance_leak() -> None:
    manifest = build_v2_anchor_manifest()
    manifest["anchors"][0]["utterance"] = "leaked source dialogue"
    errors = validate_v2_anchor_manifest(manifest)
    assert any("leaked" in e for e in errors), (
        f"Expected rejection of leaked dialogue, got: {errors}"
    )


# ==========================================================================
# Import isolation
# ==========================================================================


def test_no_product_interpreter_or_scorer_import() -> None:
    """Verify that the v2 module does not import product modules."""
    v2_path = Path("app/services/bernie/synthetic_noise_v2.py")
    tree = ast.parse(v2_path.read_text(encoding="utf-8"))
    imported_modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported_modules.add(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_modules.add(node.module)

    prohibited_fragments = {
        "semantic_extraction",
        "composed_corpus_evaluator",
        "composed_evaluator",
        "synthetic_noise_robustness",
    }
    violations = {
        module
        for module in imported_modules
        if any(fragment in module for fragment in prohibited_fragments)
    }
    assert not violations, f"V2 module imports product evaluator code: {violations}"
