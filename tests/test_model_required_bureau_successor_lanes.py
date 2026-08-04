from __future__ import annotations

from copy import deepcopy

import pytest
from jsonschema import Draft202012Validator, FormatChecker

from scripts.model_required_bureau_successor_lanes_acceptance import (
    CONTRACT,
    CONTRACT_SCHEMA,
    EXPECTED_HEAD,
    EXPECTED_RESULT,
    SCHEMA_EXAMPLES,
    build_evidence,
    language_decision,
    load_json,
    proofread_diagnosis,
)


def errors(schema_path, value):
    return list(Draft202012Validator(load_json(schema_path), format_checker=FormatChecker()).iter_errors(value))


def test_successor_lane_acceptance_passes_with_zero_side_effects():
    evidence = build_evidence()
    assert evidence["passed"] is True
    assert evidence["result"] == EXPECTED_RESULT
    assert evidence["source_head"] == EXPECTED_HEAD
    assert set(evidence["authority_and_side_effects"].values()) == {0}


def test_contract_and_examples_are_closed_draft_2020_12_schemas():
    contract = load_json(CONTRACT)
    assert not errors(CONTRACT_SCHEMA, contract)
    for schema_path, example_path in SCHEMA_EXAMPLES.values():
        schema = load_json(schema_path)
        Draft202012Validator.check_schema(schema)
        assert schema["additionalProperties"] is False
        assert not errors(schema_path, load_json(example_path))


def test_rayleen_reuses_shared_diary_action_grammar_and_never_confirms():
    rayleen = load_json(CONTRACT)["rayleen"]
    assert rayleen["action_grammar_reuse"] == {
        "check_in_proposal":"diary.check_in",
        "status_proposal":"diary.status_change",
        "waiting_area_move_proposal":"diary.waiting_area_move",
    }
    delegated = next(case for case in rayleen["cases"] if case["authority_shape"] == "direct_confirmation")
    assert language_decision("rayleen", delegated) == "refuse"


@pytest.mark.parametrize("domain", ["rayleen", "davida"])
def test_all_authored_language_cases_have_their_separate_policy_decision(domain):
    lane = load_json(CONTRACT)[domain]
    for case in lane["cases"]:
        assert language_decision(domain, case) == case["expected_decision"]


def test_provider_free_language_cases_do_not_claim_intelligent_end_to_end_path():
    contract = load_json(CONTRACT)
    assert contract["rayleen"]["provider_free_end_to_end_claim"] is False
    assert contract["davida"]["provider_free_end_to_end_claim"] is False


def test_waiting_room_context_is_minimized_labelled_and_data_only():
    frame = load_json(SCHEMA_EXAMPLES["waiting_room"][1])
    assert frame["reader"] == "authorized_reception_surface"
    assert {"contact_details", "national_identifiers", "clinical_text", "appointment_notes", "unrestricted_history"} <= set(frame["excluded_field_classes"])
    for fact in frame["backend_facts"]:
        assert fact["patient_display_token"].startswith("synthetic:")
        assert fact["label"]["integrity_principals"] == ["backend_truth"]
        assert fact["label"]["authority_ceiling"] == "data_only"


@pytest.mark.parametrize("field", ["phone", "date_of_birth", "medicare_number", "clinical_note", "command"])
def test_waiting_room_context_rejects_excess_or_authority_fields(field):
    frame = load_json(SCHEMA_EXAMPLES["waiting_room"][1])
    frame["backend_facts"][0][field] = "forbidden"
    assert errors(SCHEMA_EXAMPLES["waiting_room"][0], frame)


def test_c1_vocabulary_is_frozen_and_opens_only_schema_level_d1_d2():
    contract = load_json(CONTRACT)
    assert contract["controlled_recovery"]["c1_vocabulary_frozen"] is True
    assert contract["controlled_recovery"]["actuator_authorized"] is False
    assert len(contract["controlled_recovery"]["observation_kinds"]) == 11
    assert contract["update_supply_chain"]["activation_authorized"] is False


@pytest.mark.parametrize("field", ["credential", "raw_log", "patient_data", "sql", "shell"])
def test_technical_anatomy_rejects_forbidden_observation_fields(field):
    frame = load_json(SCHEMA_EXAMPLES["technical_anatomy"][1])
    frame["observations"][0][field] = "forbidden"
    assert errors(SCHEMA_EXAMPLES["technical_anatomy"][0], frame)


def test_diagnosis_proofreader_admits_only_bound_evidence_and_known_runbook():
    anatomy = load_json(SCHEMA_EXAMPLES["technical_anatomy"][1])
    candidate = load_json(SCHEMA_EXAMPLES["technical_diagnosis"][1])
    assert proofread_diagnosis(anatomy, candidate) is None
    candidate = deepcopy(candidate)
    candidate["hypotheses"][0]["evidence_links"] = ["unknown"]
    assert proofread_diagnosis(anatomy, candidate) == "UNKNOWN_EVIDENCE"


@pytest.mark.parametrize("field", ["shell", "sql", "command", "success", "actuator"])
def test_diagnosis_schema_rejects_executable_or_success_fields(field):
    candidate = load_json(SCHEMA_EXAMPLES["technical_diagnosis"][1])
    candidate[field] = "do it"
    assert errors(SCHEMA_EXAMPLES["technical_diagnosis"][0], candidate)


def test_update_classes_have_distinct_future_command_families_and_no_generic_command():
    update = load_json(CONTRACT)["update_supply_chain"]
    mapping = {item["id"]: item["future_command_family"] for item in update["classes"]}
    assert len(mapping) == len(set(mapping.values())) == 4
    assert update["generic_update_command"] is False


@pytest.mark.parametrize("update_class,wrong_family", [
    ("application_dependency_build", "database_migration_promotion"),
    ("database_schema_migration", "reference_dataset_activation"),
    ("reference_dataset", "policy_content_activation"),
    ("operational_clinical_policy", "application_build_promotion"),
])
def test_update_schema_rejects_cross_class_command_family(update_class, wrong_family):
    value = load_json(SCHEMA_EXAMPLES["update_provenance_delta"][1])
    value["update_class"] = update_class
    value["future_command_family"] = wrong_family
    assert errors(SCHEMA_EXAMPLES["update_provenance_delta"][0], value)


def test_api_spine_and_access_ai_remain_closed():
    spine = load_json(CONTRACT)["api_spine"]
    assert spine == {
        "read_context":"graphql_or_existing_authorized_read_only",
        "commands":"rest_openapi_single_purpose_separately_closed",
        "events":"committed_hints_require_fresh_authorized_read",
        "manifests":"declarative_inputs_typed_code_enforced",
        "access_ai_gate":"closed",
    }
