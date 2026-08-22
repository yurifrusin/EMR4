from __future__ import annotations

import copy
import json
from pathlib import Path
import subprocess

import jsonschema
import pytest

from scripts import (
    deepseek_native_harness_provider_free_guard_bridge_import_closure_recovery_rehearsal as subject,
)


def _completed(
    *, returncode: int = 0, stdout: bytes | None = None, stderr: bytes = b""
) -> subprocess.CompletedProcess[bytes]:
    if stdout is None:
        stdout = (
            json.dumps(
                subject.predecessor.exact_fixture_outcome(), separators=(",", ":")
            )
            + "\n"
        ).encode("utf-8")
    return subprocess.CompletedProcess(
        args=["node", "fixture"],
        returncode=returncode,
        stdout=stdout,
        stderr=stderr,
    )


def test_plan_freezes_causal_correction_and_direct_convergence() -> None:
    plan = subject.PLAN_PATH.read_text(encoding="utf-8")
    threat = subject.THREAT_PATH.read_text(encoding="utf-8")
    flattened_plan = " ".join(plan.splitlines())
    for token in (
        "not accepted as the exclusive process cause",
        "literal leading `+` patch",
        "derive every static relative module specifier",
        "exactly eight disposable files",
        "exactly one distinct Node process",
        "advances directly to the complete package-unloaded runner",
        "No new intermediate tranche",
    ):
        assert token in flattened_plan
    assert "previous absent-target diagnosis is overstated" in threat
    assert "stage only explicit tranche paths" in threat


def test_accepted_module_identities_are_unchanged() -> None:
    _, inventory = subject.accepted_graph_sources()
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


def test_fixture_correction_is_exact_and_patch_markers_are_absent() -> None:
    source, reading = subject.fixture_correction()
    decoded = source.decode("utf-8")
    assert reading == {
        "predecessor_fixture_source": {
            "bytes": 3724,
            "sha256": "7dee0e3a029fcef0ca4fff439572478ab38f9655124e95b39566455bd1a83788",
        },
        "corrected_fixture_source": {
            "bytes": 3621,
            "sha256": "4d97131aa65d699e5775e90482562219f85d1ab42abd38c99dd69c284e4e359c",
        },
        "leading_patch_marker_count_removed": 103,
        "leading_patch_marker_absent_after_correction": True,
        "carriage_return_absent": True,
    }
    assert all(not line.startswith("+") for line in decoded.splitlines())
    assert "\r" not in decoded
    assert decoded.startswith("import {\n  PresetMountSanitizedTerminalError,")
    assert decoded.endswith('process.stdout.write(JSON.stringify(output) + "\\n");\n')


def test_fixture_marker_drift_fails_closed(monkeypatch) -> None:
    original = subject.predecessor.fixture_source()
    monkeypatch.setattr(subject.predecessor, "fixture_source", lambda: b"+" + original)
    with pytest.raises(subject.ImportClosureError, match="fixture_patch_marker"):
        subject.fixture_correction()


def test_static_specifier_extraction_is_exact() -> None:
    modules = subject.executable_module_sources()
    assert subject._static_specifiers(modules[subject.FIXTURE_FILENAME]) == [
        f"./{subject.GUARD_FILENAME}"
    ]
    assert subject._static_specifiers(modules[subject.GUARD_FILENAME]) == [
        "@deepseek-ai/dsh-scope",
        "@deepseek-ai/dsh-agent-presets",
        f"./{subject.BRIDGE_TARGET_FILENAME}",
    ]
    assert subject._static_specifiers(modules[subject.BRIDGE_TARGET_FILENAME]) == [
        f"./{subject.SANITIZER_FILENAME}"
    ]
    assert subject._static_specifiers(modules[subject.SANITIZER_FILENAME]) == []


def test_import_closure_is_exact_and_all_targets_are_bound() -> None:
    closure = subject.import_closure()
    assert closure["relative_edge_count"] == 3
    assert closure["bare_edge_count"] == 2
    assert closure["all_resolved_targets_materialized"] is True
    assert [
        (row["importer"], row["specifier"], row["resolved_target"])
        for row in closure["relative_edges"]
    ] == list(subject.EXPECTED_RELATIVE_EDGES)
    assert [
        (
            row["importer"],
            row["specifier"],
            row["resolved_manifest"],
            row["resolved_source"],
        )
        for row in closure["bare_edges"]
    ] == list(subject.EXPECTED_BARE_EDGES)


def test_materialization_uses_import_owned_bridge_target_only() -> None:
    sources = subject.materialized_sources()
    assert tuple(sources) == subject.MATERIALIZED_RELATIVE_PATHS
    assert len(sources) == 8
    assert subject.PREDECESSOR_BRIDGE_FILENAME not in sources
    accepted, _ = subject.accepted_graph_sources()
    assert sources[subject.BRIDGE_TARGET_FILENAME] == accepted["derived_bridge"]


def test_missing_relative_target_fails_before_process() -> None:
    modules = subject.executable_module_sources()
    modules.pop(subject.BRIDGE_TARGET_FILENAME)
    with pytest.raises(subject.ImportClosureError, match="relative_import_target"):
        subject.import_closure(modules=modules)


@pytest.mark.parametrize(
    "coordinate, expected",
    [
        ('\nimport x from "../escape.mjs";\n', "relative_import_target"),
        ('\nimport x from "/absolute.mjs";\n', "specifier_coordinate"),
        ('\nimport x from "file:///tmp/x.mjs";\n', "specifier_coordinate"),
        ('\nimport x from ".\\backslash.mjs";\n', "specifier_coordinate"),
        ('\nimport x from "unknown-package";\n', "bare_import_specifier"),
        ('\nconst x = import("./later.mjs");\n', "source_coordinate"),
        ('\nconst x = require("./later.cjs");\n', "source_coordinate"),
    ],
)
def test_hostile_import_coordinates_fail_closed(
    coordinate: str, expected: str
) -> None:
    modules = subject.executable_module_sources()
    modules[subject.SANITIZER_FILENAME] += coordinate.encode("utf-8")
    with pytest.raises(subject.ImportClosureError, match=expected):
        subject.import_closure(modules=modules)


def test_extra_valid_relative_edge_fails_exact_edge_set() -> None:
    modules = subject.executable_module_sources()
    modules["extra.mjs"] = b"export const extra = true;\n"
    modules[subject.SANITIZER_FILENAME] += b'\nimport "./extra.mjs";\n'
    with pytest.raises(subject.ImportClosureError, match="edge_set"):
        subject.import_closure(modules=modules)


def test_missing_local_stub_fails_closed() -> None:
    stubs = subject.package_stub_sources()
    stubs.pop(subject.SCOPE_STUB_SOURCE)
    with pytest.raises(subject.ImportClosureError, match="bare_import_target"):
        subject.import_closure(stubs=stubs)


def test_minimum_environment_is_exact_and_rejects_missing_value() -> None:
    source = {
        "SystemRoot": "system",
        "WINDIR": "windows",
        "ComSpec": "shell",
        "TEMP": "temp",
        "TMP": "tmp",
        "PATH": "forbidden",
        "NODE_OPTIONS": "forbidden",
    }
    assert subject.minimum_windows_environment(source) == {
        key: source[key] for key in subject.WINDOWS_ENVIRONMENT_KEYS
    }
    source["TEMP"] = ""
    with pytest.raises(subject.ImportClosureError, match="preflight_rejected"):
        subject.minimum_windows_environment(source)


def test_all_schemas_are_draft_202012_valid() -> None:
    for path in (
        subject.CONTRACT_SCHEMA_PATH,
        subject.PROCESS_ENVELOPE_SCHEMA_PATH,
        subject.EVIDENCE_SCHEMA_PATH,
        subject.FAILURE_TERMINAL_SCHEMA_PATH,
    ):
        schema = json.loads(path.read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator.check_schema(schema)


def test_contract_is_machine_only_exact_and_schema_valid(tmp_path: Path) -> None:
    contract = subject.contract_value()
    subject._validate(
        subject.CONTRACT_SCHEMA_PATH, contract, "contract_schema_rejected"
    )
    assert subject.FULL_OID.search(json.dumps(contract, sort_keys=True)) is None
    assert contract["git_binding_policy"]["caller_authored_object_id_count"] == 0
    assert contract["fixture_correction"]["leading_patch_marker_count_removed"] == 103
    assert contract["import_closure"] == subject.import_closure()
    path = tmp_path / "contract.json"
    subject.write_contract(path)
    assert subject.load_contract(path) == contract


def test_contract_drift_is_rejected(tmp_path: Path) -> None:
    contract = subject.contract_value()
    contract["import_closure"]["relative_edges"].reverse()
    path = tmp_path / "contract.json"
    path.write_bytes(subject.canonical_bytes(contract))
    with pytest.raises(subject.ImportClosureError, match="contract_rejected"):
        subject.load_contract(path)


def test_process_envelope_is_content_free_and_exact() -> None:
    envelope = subject.build_process_envelope(
        candidate_source="a" * 40,
        returncode=0,
        stdout=b'{"synthetic":true}\n',
        stderr=b"",
        fixture_root_absent=True,
    )
    assert envelope["stdout_bytes"] == 19
    assert envelope["stream_content_retained"] is False
    assert envelope["raw_runtime_detail_retained"] is False
    assert envelope["materialized_file_count"] == 8
    assert envelope["node_process_count"] == 1
    assert envelope["further_process_authorized"] is False
    assert not any("synthetic" in str(value) for value in envelope.values())


def test_exact_fixture_result_is_admitted() -> None:
    contract = {"expected_result": subject.predecessor.exact_fixture_outcome()}
    assert subject.validate_fixture_result(
        completed=_completed(), contract=contract
    ) == contract["expected_result"]


@pytest.mark.parametrize("kind", ["value", "order", "stderr", "exit"])
def test_fixture_result_drift_is_rejected(kind: str) -> None:
    value = copy.deepcopy(subject.predecessor.exact_fixture_outcome())
    completed = _completed()
    expected = "import_closure_result_rejected"
    if kind == "value":
        value["cases"][0]["guard_result"]["effectiveToolCount"] = 4
        completed = _completed(stdout=subject.canonical_bytes(value))
    elif kind == "order":
        value = {
            "result": value["result"],
            "schema_version": value["schema_version"],
            "cases": value["cases"],
        }
        completed = _completed(stdout=json.dumps(value).encode() + b"\n")
    elif kind == "stderr":
        completed = _completed(stderr=b"content-not-retained")
        expected = "import_closure_process_terminal"
    else:
        completed = _completed(returncode=1)
        expected = "import_closure_process_terminal"
    with pytest.raises(subject.ImportClosureError, match=expected):
        subject.validate_fixture_result(
            completed=completed,
            contract={"expected_result": subject.predecessor.exact_fixture_outcome()},
        )


def test_run_graph_invokes_one_process_with_exact_closed_inventory(
    monkeypatch, tmp_path: Path
) -> None:
    calls: list[dict[str, object]] = []

    def fake_run(args, **kwargs):
        root = Path(kwargs["cwd"])
        observed = sorted(
            path.relative_to(root).as_posix()
            for path in root.rglob("*")
            if path.is_file()
        )
        assert observed == sorted(subject.MATERIALIZED_RELATIVE_PATHS)
        assert not (root / subject.PREDECESSOR_BRIDGE_FILENAME).exists()
        calls.append({"args": args, **kwargs})
        return _completed()

    monkeypatch.setattr(subject.subprocess, "run", fake_run)
    envelope_path = tmp_path / "envelope.json"
    completed, envelope = subject.run_graph_once(
        node=tmp_path / "node.exe",
        environment={key: key for key in subject.WINDOWS_ENVIRONMENT_KEYS},
        sources=subject.materialized_sources(),
        candidate_source="b" * 40,
        envelope_path=envelope_path,
    )
    assert completed.returncode == 0
    assert len(calls) == 1
    assert calls[0]["check"] is False
    assert calls[0]["capture_output"] is True
    assert calls[0]["text"] is False
    assert envelope["fixture_root_absent"] is True
    assert json.loads(envelope_path.read_text()) == envelope


def test_timeout_consumes_one_process_and_records_closed_envelope(
    monkeypatch, tmp_path: Path
) -> None:
    def fake_run(*args, **kwargs):
        raise subprocess.TimeoutExpired(cmd=args[0], timeout=30, output=b"x", stderr=b"y")

    monkeypatch.setattr(subject.subprocess, "run", fake_run)
    completed, envelope = subject.run_graph_once(
        node=tmp_path / "node.exe",
        environment={key: key for key in subject.WINDOWS_ENVIRONMENT_KEYS},
        sources=subject.materialized_sources(),
        candidate_source="c" * 40,
        envelope_path=tmp_path / "envelope.json",
    )
    assert completed.returncode == -1
    assert envelope["stdout_bytes"] == 1
    assert envelope["stderr_bytes"] == 1
    assert envelope["node_process_count"] == 1
    assert envelope["further_process_authorized"] is False


def test_failure_terminal_is_closed_and_schema_valid() -> None:
    terminal = subject.build_failure_terminal(
        candidate_source="d" * 40,
        result="import_closure_process_terminal",
        code="import_closure_process_terminal",
        envelope_sha256="e" * 64,
    )
    assert terminal["terminal"] == {
        "stage": "package_unloaded_import_closure_recovery",
        "code": "import_closure_process_terminal",
        "detail": None,
    }
    assert terminal["raw_runtime_detail_retained"] is False
    assert terminal["further_process_authorized"] is False


def test_evidence_is_closed_and_schema_valid() -> None:
    contract = subject.contract_value()
    envelope = subject.build_process_envelope(
        candidate_source="f" * 40,
        returncode=0,
        stdout=subject.canonical_bytes(subject.predecessor.exact_fixture_outcome()),
        stderr=b"",
        fixture_root_absent=True,
    )
    git_binding = {
        "policy": "machine_resolved_only",
        "caller_authored_object_id_count": 0,
        "planning_source_commit": "1" * 40,
        "candidate_source_commit": "2" * 40,
        "planning_source_is_ancestor_of_candidate": True,
        "branch": "codex/ariadne-bernie-davida-parallel-seam",
        "branch_origin_aligned": True,
        "protected_refs_aligned": True,
        "tracked_worktree_clean": True,
        "docs_branding_preserved": True,
    }
    evidence = subject.build_evidence(
        contract=contract,
        git_binding=git_binding,
        outcome=subject.predecessor.exact_fixture_outcome(),
        process_envelope=envelope,
    )
    assert evidence["result"] == subject.ADMITTED_RESULT
    assert evidence["import_closure"]["relative_edge_count"] == 3
    assert evidence["process_boundary"]["node_process_count"] == 1
    assert all(evidence["process_boundary"][name] == 0 for name in subject.ZERO_COUNTERS)
    assert evidence["claim_boundary"]["native_harness_proved"] is False


def test_execute_requires_fresh_outputs(monkeypatch, tmp_path: Path) -> None:
    existing = tmp_path / "already-present.json"
    existing.write_text("{}", encoding="utf-8")
    monkeypatch.setattr(subject, "OUTPUT_PATHS", (existing,))
    monkeypatch.setattr(subject, "load_contract", lambda: subject.contract_value())
    with pytest.raises(subject.ImportClosureError, match="preflight_rejected"):
        subject.execute()
