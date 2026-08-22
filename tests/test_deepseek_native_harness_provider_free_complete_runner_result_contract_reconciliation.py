from __future__ import annotations

import copy
import json

import jsonschema
import pytest

from scripts import (
    deepseek_native_harness_provider_free_complete_runner_result_contract_reconciliation
    as controller,
)


def _parent() -> tuple[dict[str, object], dict[str, object], str]:
    envelope = controller._load_object(controller.PARENT_ENVELOPE_PATH)
    failure = controller._load_object(controller.PARENT_FAILURE_PATH)
    return envelope, failure, str(envelope["candidate_source"])


def _git_binding(candidate: str) -> dict[str, object]:
    return {
        "policy": "machine_resolved_only",
        "caller_authored_object_id_count": 0,
        "consumed_candidate_source": candidate,
        "reconciliation_source": "b" * 40,
        "consumed_candidate_is_ancestor_of_reconciliation": True,
        "branch": "codex/ariadne-bernie-davida-parallel-seam",
        "branch_origin_aligned": True,
        "protected_refs_aligned": True,
        "tracked_worktree_clean": True,
        "docs_branding_preserved": True,
    }


def test_addendum_forbids_retry_and_advances_to_occupied_worker() -> None:
    text = controller.ADDENDUM_PATH.read_text(encoding="utf-8")
    assert "must not be retried" in text
    assert "process-free reconciliation" in text
    assert "advance directly to the\nbounded occupied useful Raisa worker" in text


def test_declared_fixture_wire_exactly_matches_consumed_envelope() -> None:
    envelope, _, _ = _parent()
    wire = controller.fixture_wire_bytes()
    assert len(wire) == envelope["stdout_bytes"] == controller.EXPECTED_STDOUT_BYTES
    assert controller.sha256_bytes(wire) == envelope["stdout_sha256"] == controller.EXPECTED_STDOUT_SHA256


def test_generic_sorted_serializer_is_exact_demonstrated_controller_defect() -> None:
    declared = controller.fixture_wire_bytes()
    sorted_wire = controller.parent.canonical_bytes(controller.parent.exact_fixture_result())
    assert len(declared) == len(sorted_wire) == controller.EXPECTED_STDOUT_BYTES
    assert controller.sha256_bytes(declared) != controller.sha256_bytes(sorted_wire)
    assert list(controller.parent.exact_fixture_result()) == [
        "schema_version",
        "result",
        "app_exit_code",
    ]


def test_expected_sidecar_wire_exactly_matches_consumed_envelope() -> None:
    envelope, _, candidate = _parent()
    wire = controller.sidecar_wire_bytes(candidate)
    assert len(wire) == envelope["sidecar_bytes"] == controller.EXPECTED_SIDECAR_BYTES
    assert controller.sha256_bytes(wire) == envelope["sidecar_sha256"] == controller.EXPECTED_SIDECAR_SHA256


def test_consumed_attempt_reconciles_without_raw_content() -> None:
    envelope, failure, candidate = _parent()
    result = controller.validate_consumed_attempt(envelope, failure, candidate)
    assert result["controller_defect"] == {
        "coordinate": "fixture_wire_key_order_comparison",
        "observed_wire_matches_declared_fixture_order": True,
        "generic_sorted_serializer_was_incorrect": True,
        "runner_process_failed": False,
    }
    assert result["fixture_wire"]["content_retained_from_process"] is False
    assert result["sidecar_wire"]["content_retained_from_process"] is False


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("numeric_exit_code", 2),
        ("stdout_bytes", 128),
        ("stdout_sha256", "0" * 64),
        ("stderr_bytes", 1),
        ("sidecar_bytes", 1566),
        ("sidecar_sha256", "0" * 64),
        ("fixture_root_absent", False),
        ("node_process_count", 2),
        ("installed_package_import_count", 1),
        ("native_harness_process_count", 1),
        ("worker_model_provider_process_count", 1),
        ("further_process_authorized", True),
    ],
)
def test_reconciliation_rejects_any_immutable_envelope_drift(field: str, value: object) -> None:
    envelope, failure, candidate = _parent()
    changed = copy.deepcopy(envelope)
    changed[field] = value
    with pytest.raises(controller.ReconciliationError):
        controller.validate_consumed_attempt(changed, failure, candidate)


def test_reconciliation_rejects_failure_terminal_drift() -> None:
    envelope, failure, candidate = _parent()
    changed = copy.deepcopy(failure)
    changed["terminal"]["code"] = "different"
    with pytest.raises(controller.ReconciliationError):
        controller.validate_consumed_attempt(envelope, changed, candidate)


def test_reconciliation_evidence_is_process_free_and_narrow() -> None:
    envelope, failure, candidate = _parent()
    reconciliation = controller.validate_consumed_attempt(envelope, failure, candidate)
    evidence = controller.build_evidence(
        git_binding=_git_binding(candidate), reconciliation=reconciliation
    )
    assert evidence["result"] == controller.ADMITTED_RESULT
    assert evidence["immutable_parent_result"] == "complete_runner_result_rejected"
    assert evidence["process_boundary"]["consumed_node_process_count"] == 1
    assert evidence["process_boundary"]["reconciliation_process_count"] == 0
    assert evidence["process_boundary"]["retry_count"] == 0
    assert evidence["claim_boundary"]["native_harness_proved"] is False
    assert evidence["claim_boundary"]["retry_authorized"] is False


def test_schema_is_valid_and_rejects_extra_top_level_field() -> None:
    schema = json.loads(controller.EVIDENCE_SCHEMA_PATH.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator.check_schema(schema)
    envelope, failure, candidate = _parent()
    evidence = controller.build_evidence(
        git_binding=_git_binding(candidate),
        reconciliation=controller.validate_consumed_attempt(envelope, failure, candidate),
    )
    evidence["extra"] = True
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(schema).validate(evidence)


def test_reconciliation_source_contains_no_node_or_worker_launch() -> None:
    source = controller.Path(controller.__file__).read_text(encoding="utf-8")
    assert "resolved_node_executable" not in source
    assert "--execute" not in source
    assert "Popen(" not in source
    assert "create_subprocess" not in source
