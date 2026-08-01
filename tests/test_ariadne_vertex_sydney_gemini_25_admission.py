from __future__ import annotations

import ast
import json
from pathlib import Path

import jsonschema

from scripts import ariadne_vertex_sydney_gemini_25_admission as admission


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_policy_and_documentary_gate_pass_exact_sydney_model() -> None:
    policy = load(admission.POLICY_PATH)
    schema = load(admission.SCHEMA_PATH)
    source = load(admission.SOURCE_PATH)
    jsonschema.validate(policy, schema)
    assert admission.validate(policy, schema, source) == []
    assert policy["subject"] == admission.EXPECTED_SUBJECT
    assert policy["decision"]["admitted"] is True


def test_data_and_geography_boundaries_remain_closed() -> None:
    policy = load(admission.POLICY_PATH)
    assert policy["data_classes"]["authored_synthetic"]["admitted"] is True
    assert policy["data_classes"]["product_derived"]["admitted"] is False
    assert (
        policy["data_classes"]["patient_or_health_information"]["admitted"]
        is False
    )
    assert policy["geography"]["container_effect"].startswith(
        "constrains_local_capabilities"
    )
    assert "in_memory_cache_disabled" in policy["required_admission_checks"]
    assert "another_model" in policy["rejected_routes"]


def test_current_model_observation_is_bounded() -> None:
    source = load(admission.SOURCE_PATH)
    card = next(
        item
        for item in source["sources"]
        if item["id"] == "gemini_2_5_flash_model_card"
    )["observations"]
    assert card["model_id"] == "gemini-2.5-flash"
    assert card["model_availability_australia_southeast1"] is True
    assert card["ml_processing_australia_southeast1"] is True
    assert card["structured_output_supported"] is True
    assert card["retirement_on"] == "2026-10-16"
    assert source["unverified_provider_controls"] == {
        "provider_training_control": "not_verified",
        "provider_abuse_monitoring_retention": "not_verified",
    }
    assert set(source["explicit_exclusions"].values()) == {False}


def test_training_and_abuse_retention_are_not_overclaimed() -> None:
    policy = load(admission.POLICY_PATH)
    assert "not independently verified" in policy["provider_controls"]["training"]
    assert "not independently verified" in (
        policy["provider_controls"]["abuse_monitoring_retention"]
    )
    prohibited = set(policy["claim_boundary"]["prohibited_claims"])
    assert "provider training controls were verified" in prohibited
    assert "provider abuse-monitoring retention was verified" in prohibited


def test_evidence_opens_only_provider_blocked_tranche() -> None:
    evidence = admission.build_evidence(
        load(admission.POLICY_PATH),
        load(admission.SCHEMA_PATH),
        load(admission.SOURCE_PATH),
    )
    assert evidence["policy_valid"] is True
    assert evidence["next_tranche_opened"] is True
    assert evidence["next_action"] == "open_provider_blocked_contract_tranche_only"
    assert evidence["call_accounting"]["occupied_calls_consumed"] == 0
    assert set(evidence["external_actions"].values()) == {False}


def test_validator_has_no_cloud_network_subprocess_or_environment_surface() -> None:
    tree = ast.parse(Path(admission.__file__).read_text(encoding="utf-8"))
    imports = {
        alias.name.split(".", 1)[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    imports |= {
        (node.module or "").split(".", 1)[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
    }
    assert not imports & {
        "google",
        "http",
        "os",
        "requests",
        "socket",
        "subprocess",
        "urllib",
    }


def test_committed_evidence_is_exact() -> None:
    assert admission.check_committed()["policy_valid"] is True
