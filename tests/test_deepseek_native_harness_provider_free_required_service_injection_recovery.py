from __future__ import annotations

import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from scripts import (
    deepseek_native_harness_provider_free_required_service_injection_recovery as recovery,
)


def test_contract_and_schemas_are_exact() -> None:
    contract = recovery.load_contract()
    contract_schema = json.loads(
        (recovery.ROOT / "contract.schema.json").read_text(encoding="utf-8")
    )
    evidence_schema = json.loads(
        (recovery.ROOT / "evidence.schema.json").read_text(encoding="utf-8")
    )
    Draft202012Validator(contract_schema).validate(contract)
    Draft202012Validator.check_schema(evidence_schema)
    assert contract["planning_source"] == "3e9c004e09b09c228937276f520d39e4b2c3d36b"
    assert contract["accepted_failed_source"] == (
        "8155a941a28b3d22a7dbb4132c4b0ada8558482e"
    )
    assert contract["future_declaration"]["required_services"] == [
        "hmr",
        "agentPresets",
        "tools",
    ]
    assert contract["future_declaration"]["selected_profile_materialised"] is False


def test_all_exact_cache_packages_and_members_pass() -> None:
    contract = recovery.load_contract()
    cache_root = recovery.default_cache_root()
    projections = []
    for package in contract["packages"]:
        projection, retained, names = recovery.verify_package(package, cache_root)
        projections.append(projection)
        assert set(retained) == {row["path"] for row in package["members"]}
        assert "package/package.json" in names
    assert [row["name"] for row in projections] == [
        "@deepseek-ai/dsh",
        "@deepseek-ai/dsh-base",
        "@deepseek-ai/dsh-headless",
        "@deepseek-ai/dsh-web-app",
        "@deepseek-ai/dsh-agent-presets",
        "@deepseek-ai/dsh-tools",
        "@deepseek-ai/cordis",
        "@deepseek-ai/cordis-plugin-loader",
    ]


def test_corrupt_cache_payload_fails_closed() -> None:
    package = recovery.load_contract()["packages"][0]
    payload = recovery.cache_blob_path(
        recovery.default_cache_root(), package["registry_integrity"]
    ).read_bytes()
    with pytest.raises(
        recovery.ServiceInjectionRecoveryError,
        match="package_registry_shasum_mismatch",
    ):
        recovery.verify_package_payload(package, payload[:-1] + bytes([payload[-1] ^ 1]))


def test_source_semantics_identify_exact_missing_row_and_activation_rule() -> None:
    contract = recovery.load_contract()
    sources: dict[tuple[str, str], bytes] = {}
    dsh_names: tuple[str, ...] = ()
    for package in contract["packages"]:
        _, retained, names = recovery.verify_package(
            package, recovery.default_cache_root()
        )
        if package["name"] == "@deepseek-ai/dsh":
            dsh_names = names
        for path, payload in retained.items():
            sources[(package["name"], path)] = payload
    reading = recovery.inspect_source_semantics(sources, dsh_names)
    assert all(reading["checks"].values())
    assert reading["base_headless_service_reading"] == {
        "tools_provider_row_present": True,
        "agent_presets_provider_row_present": False,
        "runner_declared_dependencies": ["hmr"],
    }
    assert reading["official_agent_presets_row"] == {
        "id": "agent-presets",
        "name": "@deepseek-ai/dsh-agent-presets",
        "default": "standard",
    }
    assert reading["shipped_preset_ids"] == ["code", "cordis", "minimal", "standard"]


def test_future_patch_is_exact_and_hostile_variants_reject() -> None:
    payload = recovery.future_patch_fragment()
    projection = recovery.validate_future_patch(payload)
    assert projection["required_services"] == ["hmr", "agentPresets", "tools"]
    assert projection["inserted_row_ids"] == [
        "agent-presets",
        "provider-free-preterminal-observable-runner",
    ]
    hostile = [
        payload.replace(b"agentPresets, ", b""),
        payload.replace(b"hmr, agentPresets, tools", b"agentPresets, hmr, tools"),
        payload.replace(b"hmr, agentPresets, tools", b"hmr, agentPresets, tools, fs"),
        payload.replace(b"default: standard", b"default: emr4-bounded-worker"),
        payload.replace(b"- id: agent-presets\n", b""),
        payload.replace(b"@deepseek-ai/dsh-agent-presets", b"@deepseek-ai/dsh-tools"),
    ]
    for candidate in hostile:
        with pytest.raises(recovery.ServiceInjectionRecoveryError):
            recovery.validate_future_patch(candidate)


def test_future_runner_changes_only_exact_dependency_declaration() -> None:
    payload = recovery.future_runner_source()
    projection = recovery.validate_future_runner(payload)
    assert projection["required_services"] == ["hmr", "agentPresets", "tools"]
    assert projection["only_dependency_declaration_changed"] is True
    assert projection["activation_vocabulary_unchanged"] is True
    assert recovery.FUTURE_RUNNER_INJECT in payload
    assert recovery.ACCEPTED_RUNNER_INJECT not in payload


def test_future_runner_hostile_variants_reject() -> None:
    payload = recovery.future_runner_source()
    hostile = [
        payload.replace(b", \"agentPresets\"", b""),
        payload.replace(
            b'"hmr", "agentPresets", "tools"',
            b'"agentPresets", "hmr", "tools"',
        ),
        payload.replace(b'"tools"]', b'"tools", "fs"]', 1),
        payload.replace(b"BOOTSTRAP_APPLY_ENTERED", b"BOOTSTRAP_CHANGED", 1),
    ]
    for candidate in hostile:
        with pytest.raises(recovery.ServiceInjectionRecoveryError):
            recovery.validate_future_runner(candidate)


def test_immutable_attempts_remain_exact_failed_results() -> None:
    rows = recovery.validate_immutable_attempts(recovery.load_contract())
    assert [row["attempt_id"] for row in rows] == [
        "native-composition-attempt-001",
        "preterminal-observable-composition-recovery-boot-attempt-001",
    ]
    assert all(row["result"] == "fail" and row["unchanged"] for row in rows)


def test_complete_evidence_passes_schema_and_keeps_all_execution_counts_zero() -> None:
    evidence = recovery.build_evidence()
    schema = json.loads(
        (recovery.ROOT / "evidence.schema.json").read_text(encoding="utf-8")
    )
    Draft202012Validator(schema).validate(evidence)
    assert evidence["result"] == "pass"
    assert evidence["root_cause"] == recovery.ROOT_CAUSE
    assert all(value == 0 for value in evidence["provider_boundary"].values())
    assert evidence["future_declaration"]["selected_profile_materialised"] is False
    assert evidence["future_declaration"]["native_execution_authorised"] is False
    assert "emr4_bounded_worker_preset_materialisation" in evidence["claim_boundary"][
        "not_proved"
    ]


def test_published_evidence_and_report_equal_deterministic_projection() -> None:
    expected = recovery.build_evidence()
    actual = json.loads(recovery.EVIDENCE_PATH.read_text(encoding="utf-8"))
    schema = json.loads(
        (recovery.ROOT / "evidence.schema.json").read_text(encoding="utf-8")
    )
    Draft202012Validator(schema).validate(actual)
    assert actual == expected
    assert recovery.REPORT_PATH.read_text(encoding="utf-8") == recovery.render_report(
        expected
    )


def test_controller_has_no_process_or_network_execution_surface() -> None:
    source = Path(recovery.__file__).read_text(encoding="utf-8")
    forbidden = (
        "import subprocess",
        "from subprocess",
        "import socket",
        "from socket",
        "import requests",
        "from requests",
        "import urllib",
        "from urllib",
        "Popen(",
        "subprocess.run(",
    )
    assert not any(token in source for token in forbidden)


def test_report_is_sanitized_and_names_claim_ceiling() -> None:
    report = recovery.render_report(recovery.build_evidence())
    normalized = " ".join(report.split())
    assert "Result: **pass**" in report
    assert recovery.ROOT_CAUSE in report
    assert "emr4-bounded-worker" in report
    assert "does not materialise it" in normalized
    assert "all zero" in report


def test_check_mode_is_idempotent_and_does_not_publish(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    before = (recovery.EVIDENCE_PATH.exists(), recovery.REPORT_PATH.exists())
    monkeypatch.setattr("sys.argv", ["service-injection-recovery", "--check"])
    assert recovery.main() == 0
    first = json.loads(capsys.readouterr().out)
    assert recovery.main() == 0
    second = json.loads(capsys.readouterr().out)
    assert first == second
    assert first["status"] == "passed"
    assert first["native_harness_processes"] == 0
    assert (recovery.EVIDENCE_PATH.exists(), recovery.REPORT_PATH.exists()) == before
