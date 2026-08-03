"""Cross-file guarantees for deterministic-first three-lane verification."""

from pathlib import Path

import yaml


SETTINGS = Path("orchestration/harness_settings")


def _yaml(name: str) -> dict:
    return yaml.safe_load((SETTINGS / name).read_text(encoding="utf-8"))


def test_external_model_review_follows_every_deterministic_gate() -> None:
    policy = _yaml("verifier_execution_policy.yaml")
    order = policy["execution_order"]
    model_review = order.index("independent_model_review_when_triggered")

    assert policy["schema_version"] == "ariadne.verifier_execution_policy.v1"
    assert policy["deterministic_gate"]["required_before_external_model_dispatch"]
    assert policy["deterministic_gate"]["fail_closed_action"] == (
        "no_external_model_call"
    )
    for gate in [
        "five_source_rehydration_receipt",
        "exact_authority_and_scope_packet",
        "exact_non_protected_candidate_binding",
        "settings_fingerprint_match",
        "focused_tests",
        "static_and_filesystem_checks",
        "clean_candidate_precondition",
        "risk_trigger_decision",
    ]:
        assert order.index(gate) < model_review
    assert order[model_review + 1 :] == [
        "exact_single_decision_admission",
        "clean_unchanged_candidate_postcondition",
    ]


def test_three_lane_models_reasoning_and_ownership_are_exact() -> None:
    policy = _yaml("verifier_execution_policy.yaml")
    lanes = policy["lane_profile"]

    assert lanes["sol"]["routine_reasoning"] == "high"
    assert lanes["sol"]["material_reasoning"] == "extra_high"
    assert "architecture" in lanes["sol"]["owns"]
    assert "acceptance" in lanes["sol"]["owns"]

    assert lanes["deepseek_flash"]["model"] == "deepseek-v4-flash"
    assert lanes["deepseek_flash"]["reasoning"] == "high"
    assert lanes["deepseek_flash"]["transport"] == "claude_code_bare"
    assert "acceptance" in lanes["deepseek_flash"]["may_not"]

    assert lanes["gemini_flash"]["model"] == "gemini-3.6-flash-high"
    assert lanes["gemini_flash"]["reasoning"] == "high"
    assert lanes["gemini_flash"]["transport"] == "antigravity_fresh_project"
    assert "implementation" in lanes["gemini_flash"]["may_not"]
    assert "self_acceptance" in lanes["gemini_flash"]["may_not"]
    assert policy["external_verifier"]["environment_boundary"] == {
        "exact_existing_interpreter_required": True,
        "package_or_environment_bootstrap": "forbidden",
        "missing_dependency_action": "stop_and_report",
    }


def test_lane_policy_is_cross_referenced_and_dispatch_is_optional() -> None:
    verifier = _yaml("verifier_execution_policy.yaml")
    sprint = _yaml("sprint_worker_policy.yaml")
    operating = _yaml("operating_model.yaml")
    pool = _yaml("worker_pool.yaml")

    assert sprint["verifier_execution_policy"] == "verifier_execution_policy.yaml"
    assert sprint["independent_verifier"]["dispatch_only_after_deterministic_pass"]
    assert operating["verifier"]["execution_policy_file"] == (
        "verifier_execution_policy.yaml"
    )
    assert operating["verifier"]["external_dispatch_only_after_deterministic_pass"]
    assert verifier["dispatch_economy"]["dispatch_is_optional"]
    assert sprint["worker_mix"]["deepseek_flash"]["minimum_instances"] == 0

    workers = {item["resource_id"]: item for item in pool["workers"]}
    assert workers["openai-primary-orchestrator"]["default_reasoning"] == "high"
    assert workers["deepseek-flash-workers"]["default_reasoning"] == "high"
    gemini = workers["antigravity-gemini-flash-3-6-high-verifier"]
    assert gemini["default_model"] == "gemini-3.6-flash-high"
    assert gemini["default_reasoning"] == "high"
    assert "implementer" not in gemini["capabilities"]


def test_postgresql_tests_stay_serial_and_only_independent_checks_parallelize() -> None:
    policy = _yaml("verifier_execution_policy.yaml")["test_execution"]
    sprint = _yaml("sprint_worker_policy.yaml")["test_execution"]

    assert policy["repository_conftest_pytest"] == "serial"
    assert policy["shared_postgresql_schema"] == "serial"
    assert sprint["shared_postgresql_schema"]["concurrency"] == "serial"
    assert policy["required_pytest_launcher"] == (
        "../../scripts/ariadne_serial_pytest.py"
    )
    assert sprint["shared_postgresql_schema"]["required_launcher"] == (
        "../../scripts/ariadne_serial_pytest.py"
    )
    assert sprint["shared_postgresql_schema"]["instruction_only_serialization"] is False
    assert policy["conftest_enforcement"] == "../../tests/conftest.py"
    assert policy["direct_pytest_bypass"] == "serialized_by_repository_conftest"
    assert sprint["shared_postgresql_schema"]["conftest_enforcement"] == (
        "../../tests/conftest.py"
    )
    assert sprint["shared_postgresql_schema"]["direct_pytest_bypass"] == (
        "serialized_by_repository_conftest"
    )
    assert policy["parallel_allowed_only_for"] == [
        "import_free_static_checks",
        "filesystem_only_checks",
        "isolated_browser_checks_without_shared_mutable_runtime",
    ]
