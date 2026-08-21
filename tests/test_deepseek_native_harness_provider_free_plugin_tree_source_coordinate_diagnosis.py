from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import jsonschema
import pytest

from scripts import (
    deepseek_native_harness_provider_free_plugin_tree_source_coordinate_diagnosis
    as diagnosis,
)


def terminal() -> bytes:
    return json.dumps(
        {
            "schema_version": "ariadne.native_harness_pre_hmr_startup_terminal.v2",
            "cause": "structured_entrypoint_import_rejected",
            "hmr_event_count": 0,
            "structured_diagnostic": {
                "phase": "entrypoint_import_rejected",
                "cause_chain": [
                    {"message_coordinate": "plugin_tree_failed_to_load"},
                    {},
                    {},
                    {"code_coordinate": "unrecognized"},
                ],
                "cause_chain_cycle_detected": False,
                "cause_chain_truncated": False,
                "raw_error_message_retained": False,
                "raw_paths_retained": False,
                "raw_stack_retained": False,
            },
        },
        sort_keys=True,
        separators=(",", ":"),
    ).encode()


def inputs() -> diagnosis.StaticInputs:
    package_json = json.dumps(
        {"name": "@deepseek-ai/dsh", "version": "0.1.0-rc.7"},
        sort_keys=True,
        separators=(",", ":"),
    ).encode()
    profile = b'''def profile_patch():
    rows = f"""- insert:
    - id: synthetic-worker-hmr-sentinel
      name: {quoted(proof / "sentinel.mjs")}
"""
    if changed:
        rows += f"""    - id: synthetic-one-request-worker-runner
      name: {quoted(proof / "runner.mjs")}
"""
def validate_profile_patch():
    pass
'''
    predecessor = b'''name: ../../../installation/proof/sentinel.mjs
name: ../../../installation/proof/runner.mjs
'''
    predecessor_evidence = json.dumps(
        {
            "result": "pass",
            "launch": {"exit_code": 0},
            "readiness": {"exact_expected_order": True},
            "provider_boundary": {"provider_request_count": 0},
            "package": {"name": "@deepseek-ai/dsh", "version": "0.1.0-rc.7"},
        },
        sort_keys=True,
        separators=(",", ":"),
    ).encode()
    app_boot = b'''const Root = bareModuleBaseUrl === void 0 ? Include : HostInclude;
stage = "plugin tree failed to load";
throw new Error(`${binName}: ${stage}: ${detail}${stack}`, { cause });
'''
    loader_entry = b'''throw updateError('import', this.options, error)
throw updateError('apply', this.options, error)
'''
    loader_tree = b'''else if (name.startsWith('.')) {
return await import(/* @vite-ignore */name)
'''
    return diagnosis.StaticInputs(
        package_json=package_json,
        terminal=terminal(),
        profile_source=profile,
        predecessor_source=predecessor,
        predecessor_evidence=predecessor_evidence,
        preset=b"preset",
        app_boot=app_boot,
        loader_entry=loader_entry,
        loader_tree=loader_tree,
    )


@pytest.fixture(autouse=True)
def fixture_digests(monkeypatch: pytest.MonkeyPatch) -> None:
    value = inputs()
    monkeypatch.setattr(
        diagnosis, "EXPECTED_PACKAGE_SHA256", diagnosis.sha256_bytes(value.package_json)
    )
    monkeypatch.setattr(
        diagnosis, "EXPECTED_TERMINAL_SHA256", diagnosis.sha256_bytes(value.terminal)
    )
    monkeypatch.setattr(
        diagnosis, "EXPECTED_PRESET_SHA256", diagnosis.sha256_bytes(value.preset)
    )
    monkeypatch.setattr(
        diagnosis,
        "EXPECTED_PREDECESSOR_EVIDENCE_SHA256",
        diagnosis.sha256_bytes(value.predecessor_evidence),
    )


def test_unique_initial_absolute_specifier_is_narrowed_without_raw_reconstruction() -> None:
    evidence = diagnosis.analyze_static_inputs(inputs())
    assert evidence["status"] == "passed"
    assert evidence["verdict"] == "unique_supported_coordinate"
    assert evidence["match_count"] == 1
    assert evidence["repair_justified"] is True
    assert evidence["owner_classification"] == "profile_input"
    assert all(value == 0 for value in evidence["zero_activity"].values())
    assert "ERR_" not in json.dumps(evidence)


def test_second_initial_absolute_module_fails_closed_as_ambiguous() -> None:
    value = inputs()
    profile = value.profile_source.replace(
        b'    if changed:',
        b'    - id: another\n      name: {quoted(proof / "another.mjs")}\n    if changed:',
    )
    evidence = diagnosis.analyze_static_inputs(replace(value, profile_source=profile))
    assert evidence["verdict"] == "insufficient_source_coordinate"
    assert evidence["match_count"] == 2
    assert evidence["repair_justified"] is False


def test_missing_initial_absolute_module_fails_closed() -> None:
    value = inputs()
    profile = value.profile_source.replace(
        b'{quoted(proof / "sentinel.mjs")}',
        b'../../../installation/proof/sentinel.mjs',
    )
    evidence = diagnosis.analyze_static_inputs(replace(value, profile_source=profile))
    assert evidence["verdict"] == "insufficient_source_coordinate"
    assert evidence["match_count"] == 0


def test_terminal_shape_drift_rejects_source_binding() -> None:
    value = inputs()
    changed = json.loads(value.terminal)
    changed["structured_diagnostic"]["cause_chain"].pop()
    evidence = diagnosis.analyze_static_inputs(
        replace(value, terminal=json.dumps(changed).encode())
    )
    assert evidence["verdict"] == "source_binding_failed"
    assert evidence["repair_justified"] is False


def test_package_identity_drift_rejects_source_binding() -> None:
    value = inputs()
    evidence = diagnosis.analyze_static_inputs(
        replace(
            value,
            package_json=json.dumps(
                {"name": "@deepseek-ai/dsh", "version": "0.1.0-rc.6"}
            ).encode(),
        )
    )
    assert evidence["verdict"] == "source_binding_failed"
    schema = json.loads(
        (diagnosis.CONTINUITY_ROOT / "diagnosis-evidence.schema.json").read_text(
            encoding="utf-8"
        )
    )
    jsonschema.Draft202012Validator(schema).validate(evidence)


def test_runner_source_contains_no_process_or_network_entry_points() -> None:
    source = Path(diagnosis.__file__).read_text(encoding="utf-8")
    forbidden = (
        "subprocess",
        "Popen(",
        "requests.",
        "urllib.",
        "socket.",
        "http.client",
        "os.system",
    )
    assert all(token not in source for token in forbidden)


def test_frozen_plan_and_contract_keep_execution_and_product_boundaries_closed() -> None:
    plan = (
        diagnosis.REPO_ROOT
        / "docs"
        / "deepseek-native-harness-provider-free-plugin-tree-failed-to-load-"
        "source-coordinate-diagnosis-plan.md"
    ).read_text(encoding="utf-8")
    contract = json.loads(
        (diagnosis.CONTINUITY_ROOT / "contract.json").read_text(encoding="utf-8")
    )
    for token in (
        "provider-free static reading only",
        "no Harness, broker, worker, model, provider, network, retry, resume",
        "no product source, configuration, API, database, route, adapter",
        "no ordinary-practice enablement or generic-status `Arrived` change",
        "explicit-path staging only",
    ):
        assert token in plan
    assert contract["repair_implementation_authorized"] is False
    assert contract["occupied_retry_authorized"] is False


def test_real_contract_and_generated_evidence_are_schema_valid() -> None:
    contract_schema = json.loads(
        (diagnosis.CONTINUITY_ROOT / "contract.schema.json").read_text(
            encoding="utf-8"
        )
    )
    contract = json.loads(
        (diagnosis.CONTINUITY_ROOT / "contract.json").read_text(encoding="utf-8")
    )
    evidence_schema = json.loads(
        (diagnosis.CONTINUITY_ROOT / "diagnosis-evidence.schema.json").read_text(
            encoding="utf-8"
        )
    )
    evidence = json.loads(
        (diagnosis.CONTINUITY_ROOT / "diagnosis-evidence.json").read_text(
            encoding="utf-8"
        )
    )
    jsonschema.Draft202012Validator(contract_schema).validate(contract)
    jsonschema.Draft202012Validator(evidence_schema).validate(evidence)
