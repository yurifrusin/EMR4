from __future__ import annotations

import copy

from scripts import (
    deepseek_native_harness_provider_free_repaired_sentinel_preactivation_source_coordinate_diagnosis
    as diagnosis,
)
from scripts import deepseek_native_harness_provider_free_sentinel_source_escape_repair as subject


def test_exact_source_only_repair_passes() -> None:
    evidence = subject.analyze_repair(subject.load_contract())

    assert evidence["result"] == "pass"
    assert evidence["repair"]["exact_delta"] is True
    assert evidence["repair"]["changed_byte_count"] == 1
    assert evidence["repair"]["literal_prefix"] == "br"
    assert evidence["repair"]["generated_spellings_present"] is True
    assert evidence["repair"]["lexical_violation_count"] == 0
    assert evidence["consumed_evidence"]["all_preserved"] is True
    assert all(value == 0 for value in evidence["zero_activity"].values())


def test_candidate_equals_planning_preimage_plus_exact_inserted_r() -> None:
    contract = subject.load_contract()
    target = contract["repair_target"]
    preimage = subject._git_show(contract["planning_source"], target["path"])
    candidate = (subject.REPO_ROOT / target["path"]).read_bytes()

    assert preimage.count(target["old_token"].encode()) == 1
    assert candidate == preimage.replace(
        target["old_token"].encode(), target["new_token"].encode(), 1
    )


def test_ordinary_bytes_literal_regression_fails_closed() -> None:
    contract = subject.load_contract()
    target = contract["repair_target"]
    preimage = subject._git_show(contract["planning_source"], target["path"])

    evidence = subject.analyze_repair(contract, target_payload=preimage)

    assert evidence["result"] == "failed_closed"
    assert evidence["repair"]["exact_delta"] is False
    assert evidence["repair"]["lexical_violation_count"] == 3


def test_any_second_source_edit_fails_closed() -> None:
    contract = subject.load_contract()
    target = contract["repair_target"]
    candidate = (subject.REPO_ROOT / target["path"]).read_bytes() + b"\n"

    evidence = subject.analyze_repair(contract, target_payload=candidate)

    assert evidence["result"] == "failed_closed"
    assert evidence["repair"]["exact_delta"] is False


def test_raw_line_terminator_in_generated_literal_is_detected() -> None:
    payload = b'const rows = value.split(/\r?\n/); const line = "bad\n";\n'
    violations = diagnosis.lexical_line_terminator_violations(payload)

    assert [(row["context"], row["control"]) for row in violations] == [
        ("regular_expression_literal", "CR"),
        ("regular_expression_literal", "LF"),
        ("quoted_string_literal", "LF"),
    ]


def test_binding_drift_fails_closed() -> None:
    contract = subject.load_contract()
    path = contract["diagnosis_bindings"][0]["path"]

    evidence = subject.analyze_repair(
        contract, binding_overrides={path: b"{}\n"}
    )

    assert evidence["result"] == "failed_closed"
    assert any(not row["matched"] for row in evidence["bindings"])


def test_consumed_attempt_drift_fails_closed() -> None:
    contract = subject.load_contract()
    path = (
        "orchestration/continuity/deepseek-native-harness-provider-free-repaired-"
        "sentinel-native-boot-proof/provider-free-repaired-sentinel-native-boot-terminal.json"
    )

    evidence = subject.analyze_repair(
        contract, consumed_overrides={path: b"{}\n"}
    )

    assert evidence["result"] == "failed_closed"
    assert evidence["consumed_evidence"]["all_preserved"] is False


def test_malformed_static_return_shape_fails_closed() -> None:
    contract = subject.load_contract()
    candidate = b"def sentinel_source():\n    value = b'x'\n    return value\n"

    evidence = subject.analyze_repair(contract, target_payload=candidate)

    assert evidence["result"] == "failed_closed"
    assert evidence["repair"]["literal_prefix"] == "other"


def test_contract_forbids_every_executable_surface() -> None:
    method = subject.load_contract()["method"]

    assert method["execute_or_import_repair_target"] is False
    assert method["maximum_modified_preexisting_files"] == 1
    for field in (
        "node_process_limit",
        "harness_process_limit",
        "broker_process_limit",
        "worker_process_limit",
        "model_request_limit",
        "provider_request_limit",
        "network_request_limit",
        "raw_stream_reconstruction_limit",
    ):
        assert method[field] == 0


def test_contract_digest_mutation_is_rejected_by_result() -> None:
    contract = copy.deepcopy(subject.load_contract())
    contract["repair_target"]["postimage_sha256"] = "f" * 64

    evidence = subject.analyze_repair(contract)

    assert evidence["result"] == "failed_closed"


def test_runner_writes_schema_valid_evidence_and_report(tmp_path) -> None:
    evidence = subject.run(tmp_path)

    assert evidence["result"] == "pass"
    assert (tmp_path / subject.EVIDENCE_PATH.name).is_file()
    report = (tmp_path / subject.REPORT_PATH.name).read_text(encoding="utf-8")
    assert "Exact one-byte source delta: `True`" in report
    assert "activity: `0 / 0 / 0 / 0 / 0 / 0 / 0`" in report
