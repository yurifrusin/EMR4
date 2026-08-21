from __future__ import annotations

from dataclasses import replace
import json

import pytest

from scripts import (
    deepseek_native_harness_provider_free_repaired_sentinel_preactivation_source_coordinate_diagnosis
    as subject,
)


def test_exact_static_diagnosis_names_unique_coordinate() -> None:
    contract = subject.load_contract()
    evidence = subject.analyze_static_inputs(
        contract, subject.repository_inputs(contract)
    )

    assert evidence["result"] == "pass"
    assert evidence["verdict"] == "unique_supported_coordinate"
    assert evidence["lexical_analysis"]["source_coordinate_count"] == 1
    assert evidence["lexical_analysis"]["first_fatal_coordinate"]["context"] == (
        "regular_expression_literal"
    )
    assert evidence["lexical_analysis"]["first_fatal_coordinate"]["control"] == "CR"
    assert evidence["passing_control"]["lexical_violation_count"] == 0
    assert all(value == 0 for value in evidence["zero_activity"].values())


def test_failed_author_is_extracted_without_import_or_execution() -> None:
    contract = subject.load_contract()
    inputs = subject.repository_inputs(contract)
    module = subject.extract_static_module(
        inputs.components["failed_sentinel_author"], "sentinel_source"
    )

    assert module["sha256"] == (
        json.loads(inputs.components["failed_boot_terminal"])["profile"][
            "sentinel_sha256"
        ]
    )
    assert module["return_line"] == module["function_line"] + 1


def test_raw_literal_repair_removes_the_lexical_coordinate() -> None:
    contract = subject.load_contract()
    source = subject.repository_inputs(contract).components["failed_sentinel_author"]
    repaired = source.replace(b"return b'''import {", b"return br'''import {", 1)

    module = subject.extract_static_module(repaired, "sentinel_source")

    assert subject.lexical_line_terminator_violations(module["bytes"]) == []


def test_duplicate_sentinel_function_fails_closed() -> None:
    contract = subject.load_contract()
    source = subject.repository_inputs(contract).components["failed_sentinel_author"]
    duplicate = source + b"\n\ndef sentinel_source():\n    return b'x'\n"

    with pytest.raises(subject.DiagnosisError, match="duplicate_static_function"):
        subject.extract_static_module(duplicate, "sentinel_source")


def test_absent_violation_cannot_be_called_unique() -> None:
    payload = b'''export function apply() {\n  const rows = "ok\\n";\n}\n'''

    assert subject.lexical_line_terminator_violations(payload) == []


def test_multiple_literal_contexts_remain_enumerated() -> None:
    payload = b'const a = "bad\n"; const b = "also\r";\n'
    violations = subject.lexical_line_terminator_violations(payload)

    assert [(row["context"], row["control"]) for row in violations] == [
        ("quoted_string_literal", "LF"),
        ("quoted_string_literal", "CR"),
    ]


def test_terminal_digest_drift_returns_insufficient_coordinate() -> None:
    contract = subject.load_contract()
    inputs = subject.repository_inputs(contract)
    terminal = json.loads(inputs.components["failed_boot_terminal"])
    terminal["launch"]["exit_code_after_controller_termination"] = 2
    components = dict(inputs.components)
    components["failed_boot_terminal"] = subject._canonical_json(terminal)

    evidence = subject.analyze_static_inputs(
        contract, replace(inputs, components=components)
    )

    assert evidence["result"] == "failed_closed"
    assert evidence["verdict"] == "insufficient_source_coordinate"
    assert evidence["narrowest_supported_coordinate"] is None


def test_contract_forbids_all_executable_harness_activity() -> None:
    method = subject.load_contract()["method"]

    assert method["execute_failed_author"] is False
    assert method["import_failed_author"] is False
    assert method["node_process_limit"] == 0
    assert method["harness_process_limit"] == 0
    assert method["provider_request_limit"] == 0
    assert method["raw_stream_reconstruction"] is False
