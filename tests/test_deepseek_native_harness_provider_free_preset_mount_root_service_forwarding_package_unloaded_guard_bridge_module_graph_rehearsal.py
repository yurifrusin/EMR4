from __future__ import annotations

import json
from pathlib import Path
import subprocess

import jsonschema
import pytest

from scripts import (
    deepseek_native_harness_provider_free_preset_mount_root_service_forwarding_package_unloaded_guard_bridge_module_graph_rehearsal as subject,
)


def _completed(
    value: object, *, returncode: int = 0, stderr: bytes = b""
) -> subprocess.CompletedProcess[bytes]:
    return subprocess.CompletedProcess(
        args=["node", "fixture.mjs"],
        returncode=returncode,
        stdout=(json.dumps(value, separators=(",", ":")) + "\n").encode(),
        stderr=stderr,
    )


def test_plan_freezes_convergence_and_closed_boundary() -> None:
    plan = subject.PLAN_PATH.read_text(encoding="utf-8")
    threat = subject.THREAT_PATH.read_text(encoding="utf-8")
    for value in (plan, threat):
        assert "Date: 2026-08-22" in value
        assert "Timestamp: 2026-08-22T10:08:50.8671885+10:00" in value
        assert "installed package" in value
        assert "native Harness" in value
        assert "DeepSeek worker" in value
        assert "protected-ref" in value or "protected ref" in value
    assert "Convergence and anti-orbit rule" in plan
    assert "complete package-unloaded\nrunner" in plan
    assert "useful Raisa development work" in plan
    assert "specific new failure mode" in plan


def test_exact_accepted_source_inventory_and_semantics() -> None:
    sources, inventory = subject.accepted_graph_sources()
    assert inventory == {
        "derived_guard": {
            "bytes": 4501,
            "sha256": "76029da0f9c030651fd10c0df16f4e75e86b2269d7560af7f94c74680f8598b9",
        },
        "derived_bridge": {
            "bytes": 1661,
            "sha256": "3a49b28174eeefd77d7efe0a00498901ac6636b637ed9dfe60aba46980df1d0b",
        },
        "accepted_sanitizer": {
            "bytes": 2439,
            "sha256": "12552925a600dc951afc30b9a738746499c7e2f4cefc9962bc05fb06780f158f",
        },
    }
    guard = sources["derived_guard"].decode()
    bridge = sources["derived_bridge"].decode()
    assert (
        guard.count(
            "assertEffectiveToolComposition(agentCtx, presetService, presetId, requiredTools)"
        )
        == 1
    )
    assert guard.count("    presetService,") == 1
    assert "agentCtx.agentPresets" not in guard
    assert guard.count("scopeOf(agentCtx)") == 1
    assert guard.count("agentCtx.tools.restrict") == 1
    assert guard.count("agentCtx.tools.schemas") == 1
    assert "const mount = presetService.mount;" in bridge
    assert "await mount.call(presetService, agentCtx, presetId);" in bridge


def test_local_stubs_are_minimal_and_provider_free() -> None:
    stubs = subject.package_stub_sources()
    assert tuple(stubs) == (
        subject.SCOPE_STUB_MANIFEST,
        subject.SCOPE_STUB_SOURCE,
        subject.PRESETS_STUB_MANIFEST,
        subject.PRESETS_STUB_SOURCE,
    )
    scope = stubs[subject.SCOPE_STUB_SOURCE].decode()
    presets = stubs[subject.PRESETS_STUB_SOURCE].decode()
    assert scope.count("export function scopeOf") == 1
    assert scope.count("__emr4FixtureScope") == 1
    assert presets.count("export class PresetMountError") == 1
    combined = "\n".join(payload.decode() for payload in stubs.values())
    for token in ("process.env", "node:fs", "node:child_process", "fetch(", "require("):
        assert token not in combined


def test_fixture_is_closed_and_runs_exact_three_cases() -> None:
    source = subject.fixture_source().decode()
    assert source.count(f'from "./{subject.GUARD_FILENAME}"') == 1
    assert source.count("await successCase()") == 1
    assert source.count('await failureCase("missing_service", null)') == 1
    assert source.count('await failureCase("missing_mount", Object.freeze({}))') == 1
    assert source.count("process.stdout.write") == 1
    assert "sanitizeEffectiveToolTerminal" not in source
    for token in (
        "process.env",
        "node:fs",
        "node:child_process",
        ".message",
        ".stack",
        ".cause",
    ):
        assert token not in source


def test_materialization_is_exact_and_runner_absent() -> None:
    sources = subject.materialized_sources()
    assert tuple(sources) == subject.MATERIALIZED_RELATIVE_PATHS
    assert len(sources) == 8
    assert all("derived-runner" not in path for path in sources)
    assert all("generated-runner" not in path for path in sources)
    assert all(payload for payload in sources.values())


def test_exact_outcome_has_ordered_success_and_short_circuits() -> None:
    outcome = subject.exact_fixture_outcome()
    assert [row["case_id"] for row in outcome["cases"]] == [
        "success",
        "missing_service",
        "missing_mount",
    ]
    success = outcome["cases"][0]
    assert success["guard_result"] == {
        "coordinate": "EFFECTIVE_TOOL_COMPOSITION_PASSED",
        "presetId": "emr4-bounded-worker",
        "effectiveToolNames": ["edit", "glob", "read"],
        "effectiveToolCount": 3,
    }
    for row in outcome["cases"][1:]:
        assert row["typed_terminal_caught"] is True
        assert row["terminal"] == subject.exact_mount_terminal()
        assert row["scope_lookup_count"] == 0
        assert row["view_call_count"] == 0
        assert row["restrict_call_count"] == 0
        assert row["schema_call_count"] == 0


def test_minimum_environment_is_exact_and_rejects_expansion() -> None:
    source = {
        key: f"value-{index}"
        for index, key in enumerate(subject.WINDOWS_ENVIRONMENT_KEYS)
    }
    source["PATH"] = "forbidden"
    source["NODE_OPTIONS"] = "forbidden"
    assert subject.minimum_windows_environment(source) == {
        key: source[key] for key in subject.WINDOWS_ENVIRONMENT_KEYS
    }
    missing = dict(source)
    del missing["TEMP"]
    with pytest.raises(
        subject.ModuleGraphError, match="module_graph_preflight_rejected"
    ):
        subject.minimum_windows_environment(missing)


def test_all_schemas_are_draft_202012_valid() -> None:
    for path in (
        subject.CONTRACT_SCHEMA_PATH,
        subject.PROCESS_ENVELOPE_SCHEMA_PATH,
        subject.EVIDENCE_SCHEMA_PATH,
        subject.FAILURE_TERMINAL_SCHEMA_PATH,
    ):
        schema = json.loads(path.read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator.check_schema(schema)


def test_contract_is_exact_machine_only_and_schema_valid() -> None:
    contract = subject.load_contract()
    assert contract == subject.contract_value()
    assert subject.FULL_OID.search(json.dumps(contract, sort_keys=True)) is None
    assert contract["git_binding_policy"]["caller_authored_object_id_count"] == 0
    assert (
        contract["accepted_source_inventory"]["derived_guard"]["sha256"]
        == "76029da0f9c030651fd10c0df16f4e75e86b2269d7560af7f94c74680f8598b9"
    )
    assert contract["materialized_relative_paths"] == list(
        subject.MATERIALIZED_RELATIVE_PATHS
    )
    assert contract["expected_result"] == subject.exact_fixture_outcome()


def test_contract_rejects_any_drift(tmp_path: Path) -> None:
    contract = subject.contract_value()
    contract["case_ids"] = ["success", "missing_mount", "missing_service"]
    path = tmp_path / "contract.json"
    path.write_bytes(subject.canonical_bytes(contract))
    with pytest.raises(subject.ModuleGraphError):
        subject.load_contract(path)


def test_process_envelope_is_content_free_and_exact() -> None:
    envelope = subject.build_process_envelope(
        candidate_source="0" * 40,
        returncode=0,
        stdout=b'{"safe":true}\n',
        stderr=b"",
        fixture_root_absent=True,
    )
    serialized = json.dumps(envelope, sort_keys=True)
    assert "safe" not in serialized
    assert envelope["stdout_bytes"] == 14
    assert envelope["materialized_file_count"] == 8
    assert envelope["local_stub_package_count"] == 2
    assert envelope["installed_package_import_count"] == 0
    assert envelope["environment"] == subject.environment_projection()


def test_exact_result_is_admitted() -> None:
    value = subject.exact_fixture_outcome()
    assert (
        subject.validate_fixture_result(
            completed=_completed(value), contract=subject.load_contract()
        )
        == value
    )


@pytest.mark.parametrize(
    "mutation",
    [
        lambda value: value.update({"result": "descriptive-pass"}),
        lambda value: value["cases"].reverse(),
        lambda value: value["cases"][0].update({"scope_lookup_count": 2}),
        lambda value: value["cases"][1]["terminal"].update({"detail": "raw"}),
        lambda value: value["cases"][2].update({"schema_call_count": 1}),
    ],
)
def test_result_drift_is_rejected(mutation) -> None:
    value = json.loads(json.dumps(subject.exact_fixture_outcome()))
    mutation(value)
    with pytest.raises(subject.ModuleGraphError, match="module_graph_result_rejected"):
        subject.validate_fixture_result(
            completed=_completed(value), contract=subject.load_contract()
        )


def test_key_order_and_raw_stderr_are_rejected() -> None:
    value = subject.exact_fixture_outcome()
    reordered = {
        "result": value["result"],
        "schema_version": value["schema_version"],
        "cases": value["cases"],
    }
    with pytest.raises(subject.ModuleGraphError, match="module_graph_result_rejected"):
        subject.validate_fixture_result(
            completed=_completed(reordered), contract=subject.load_contract()
        )
    with pytest.raises(subject.ModuleGraphError, match="module_graph_process_terminal"):
        subject.validate_fixture_result(
            completed=_completed(value, stderr=b"raw"), contract=subject.load_contract()
        )


def test_run_graph_invokes_one_process_with_exact_local_graph(
    monkeypatch, tmp_path: Path
) -> None:
    calls: list[dict[str, object]] = []
    expected = subject.exact_fixture_outcome()

    def fake_run(args, **kwargs):
        root = Path(kwargs["cwd"])
        observed = sorted(
            path.relative_to(root).as_posix()
            for path in root.rglob("*")
            if path.is_file()
        )
        assert observed == sorted(subject.MATERIALIZED_RELATIVE_PATHS)
        assert Path(args[1]).resolve() == (root / subject.FIXTURE_FILENAME).resolve()
        assert kwargs["env"] == {key: "x" for key in subject.WINDOWS_ENVIRONMENT_KEYS}
        assert kwargs["text"] is False
        calls.append({"args": args, "kwargs": kwargs})
        return _completed(expected)

    monkeypatch.setattr(subject.subprocess, "run", fake_run)
    envelope_path = tmp_path / "envelope.json"
    completed, envelope = subject.run_graph_once(
        node=Path("C:/synthetic/node.exe"),
        environment={key: "x" for key in subject.WINDOWS_ENVIRONMENT_KEYS},
        sources=subject.materialized_sources(),
        candidate_source="0" * 40,
        envelope_path=envelope_path,
    )
    assert len(calls) == 1
    assert completed.returncode == 0
    assert envelope_path.exists()
    assert json.loads(envelope_path.read_text()) == envelope
    assert envelope["fixture_root_absent"] is True


def test_timeout_still_records_content_free_envelope(
    monkeypatch, tmp_path: Path
) -> None:
    def fake_run(args, **kwargs):
        raise subprocess.TimeoutExpired(
            args, kwargs["timeout"], output=b"partial", stderr=b"closed"
        )

    monkeypatch.setattr(subject.subprocess, "run", fake_run)
    envelope_path = tmp_path / "timeout-envelope.json"
    completed, envelope = subject.run_graph_once(
        node=Path("C:/synthetic/node.exe"),
        environment={key: "x" for key in subject.WINDOWS_ENVIRONMENT_KEYS},
        sources=subject.materialized_sources(),
        candidate_source="0" * 40,
        envelope_path=envelope_path,
    )
    assert completed.returncode == -1
    persisted = envelope_path.read_text(encoding="utf-8")
    assert "partial" not in persisted
    assert "closed" not in persisted
    assert envelope["stdout_bytes"] == 7
    assert envelope["stderr_bytes"] == 6


def test_failure_terminal_is_closed_and_schema_valid() -> None:
    terminal = subject.build_failure_terminal(
        candidate_source="0" * 40,
        result="module_graph_result_rejected",
        code="module_graph_result_rejected",
        envelope_sha256="0" * 64,
    )
    assert terminal["terminal"] == {
        "stage": "package_unloaded_module_graph",
        "code": "module_graph_result_rejected",
        "detail": None,
    }
    assert "message" not in json.dumps(terminal)


def test_evidence_is_closed_and_schema_valid() -> None:
    contract = subject.load_contract()
    envelope = subject.build_process_envelope(
        candidate_source="0" * 40,
        returncode=0,
        stdout=b"safe\n",
        stderr=b"",
        fixture_root_absent=True,
    )
    git_binding = {
        "policy": "machine_resolved_only",
        "caller_authored_object_id_count": 0,
        "planning_source_commit": "0" * 40,
        "candidate_source_commit": "1" * 40,
        "planning_source_is_ancestor_of_candidate": True,
        "branch": "codex/ariadne-bernie-davida-parallel-seam",
        "branch_origin_aligned": True,
        "protected_refs_aligned": True,
        "tracked_worktree_clean": True,
        "docs_branding_preserved": True,
    }
    stubs = subject.package_stub_sources()
    evidence = subject.build_evidence(
        contract=contract,
        git_binding=git_binding,
        source_inventory=contract["accepted_source_inventory"],
        stub_inventory={
            path: subject.source_entry(payload) for path, payload in stubs.items()
        },
        fixture_inventory=subject.source_entry(subject.fixture_source()),
        outcome=subject.exact_fixture_outcome(),
        process_envelope=envelope,
    )
    assert evidence["process_envelope_recorded_before_interpretation"] is True
    assert evidence["process_boundary"]["node_process_count"] == 1
    assert all(
        evidence["process_boundary"][name] == 0 for name in subject.ZERO_COUNTERS
    )
    assert (
        evidence["claim_boundary"]["package_unloaded_guard_bridge_graph_proved"] is True
    )
    assert evidence["claim_boundary"]["derived_runner_proved"] is False


def test_execute_requires_fresh_output_paths(monkeypatch, tmp_path: Path) -> None:
    existing = tmp_path / "existing.json"
    existing.write_text("{}", encoding="utf-8")
    monkeypatch.setattr(subject, "OUTPUT_PATHS", (existing,))
    with pytest.raises(
        subject.ModuleGraphError, match="module_graph_preflight_rejected"
    ):
        subject._ensure_fresh_outputs()
