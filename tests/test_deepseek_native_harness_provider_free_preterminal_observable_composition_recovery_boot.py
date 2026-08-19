from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess

import jsonschema
import pytest
import yaml

from scripts.deepseek_native_harness_provider_free_effective_tool_composition_guard import (
    build_guard_source,
)
from scripts.deepseek_native_harness_provider_free_hmr_boot_proof import (
    DISPOSABLE_PARENT,
)
from scripts.deepseek_native_harness_provider_free_preterminal_observability_recovery import (
    corrected_runner_source,
)
from scripts.deepseek_native_harness_provider_free_preterminal_observable_composition_recovery_boot import (
    CONTRACT_PATH,
    RecoveryBootError,
    build_patch_pair,
    deterministic_check,
    load_contract,
    parse_activation,
    parse_readiness,
    parse_terminal,
    validate_activation,
    validate_controller_source,
    validate_patch_pair,
    validate_predecessors,
    validate_readiness,
    validate_readiness_prefix,
)


def test_contract_and_schema_freeze_distinct_one_process_attempt() -> None:
    contract = load_contract()
    schema = json.loads(
        CONTRACT_PATH.with_name("contract.schema.json").read_text(encoding="utf-8")
    )

    jsonschema.validate(contract, schema)
    assert contract["attempt"] == {
        "attempt_id": "preterminal-observable-composition-recovery-boot-attempt-001",
        "native_process_count": 1,
        "automatic_retry": False,
        "manual_retry": False,
        "resume": False,
    }
    assert (
        contract["attempt"]["attempt_id"]
        != contract["immutable_predecessor_attempt"]["attempt_id"]
    )
    assert contract["terminal"]["effective_tool_names"] == ["edit", "glob", "read"]


def test_predecessors_are_full_git_objects_with_exact_accepted_bytes() -> None:
    projection = validate_predecessors(load_contract())

    assert all(len(value) == 40 for value in projection["accepted_sources"].values())
    assert projection["immutable_predecessor_unchanged"] is True
    assert (
        projection["implementation_sha256"] == load_contract()["implementation_bytes"]
    )
    assert projection["generated_sha256"]["generated_corrected_runner_sha256"] == (
        "230d5a2d41f3768260fb908bd1d7e162cdd102cb32867cfa3d4a69e9fe376a5e"
    )


def test_plan_and_threat_delta_keep_single_run_and_closed_surfaces() -> None:
    plan = Path(
        "docs/deepseek-native-harness-provider-free-preterminal-observable-composition-"
        "recovery-boot-plan.md"
    ).read_text(encoding="utf-8")
    threat = Path(
        "docs/security/deepseek-native-harness-provider-free-preterminal-observable-"
        "composition-recovery-boot-threat-model-delta.md"
    ).read_text(encoding="utf-8")

    for phrase in (
        "exactly one new",
        "There is no\nautomatic or manual second native process",
        "Elapsed time must be assigned in a `finally` path",
        "no agent/session/\nturn, broker/model/provider call",
        "no production, deployment, release",
    ):
        assert phrase in plan
    assert "Starting more than one process" in threat
    assert "No prompt" in threat


def test_patch_uses_separate_readiness_and_activation_writers(tmp_path: Path) -> None:
    profile = tmp_path / "home" / "profiles" / "headless"
    modules = tmp_path / "installation" / "proof"
    initial, changed = build_patch_pair(
        profile,
        tmp_path / "readiness.jsonl",
        tmp_path / "activation.jsonl",
        tmp_path / "terminal.json",
        modules / "sentinel.mjs",
        modules / "runner.mjs",
    )

    validate_patch_pair(initial, changed)
    initial_rows = yaml.safe_load(initial)
    changed_rows = yaml.safe_load(changed)
    initial_inserted = initial_rows[-1]["insert"]
    changed_inserted = changed_rows[-1]["insert"]
    assert len(initial_inserted) == 1
    assert len(changed_inserted) == 2
    assert "eventPath" in initial_inserted[0]["config"]
    assert "activationPath" not in initial_inserted[0]["config"]
    assert "activationPath" in changed_inserted[1]["config"]
    assert "eventPath" not in changed_inserted[1]["config"]


def test_patch_rejects_runner_in_initial_layer(tmp_path: Path) -> None:
    profile = tmp_path / "home" / "profiles" / "headless"
    modules = tmp_path / "installation" / "proof"
    _, changed = build_patch_pair(
        profile,
        tmp_path / "readiness.jsonl",
        tmp_path / "activation.jsonl",
        tmp_path / "terminal.json",
        modules / "sentinel.mjs",
        modules / "runner.mjs",
    )

    with pytest.raises(RecoveryBootError, match="initial_patch_runner_present"):
        validate_patch_pair(changed, changed)


def test_controller_has_one_launch_and_finally_timing_before_cleanup() -> None:
    checks = validate_controller_source()

    assert all(checks.values())
    assert checks["single_popen"] is True
    assert checks["duration_in_finally"] is True
    assert checks["duration_before_termination"] is True


def _write_ledger(path: Path, schema: str, key: str, values: list[str]) -> None:
    path.write_text(
        "".join(
            json.dumps({"schema_version": schema, "sequence": index, key: value}) + "\n"
            for index, value in enumerate(values, start=1)
        ),
        encoding="utf-8",
    )


def test_ledger_parsers_reject_reordering_duplicates_and_partial_lines(
    tmp_path: Path,
) -> None:
    contract = load_contract()
    readiness = tmp_path / "readiness.jsonl"
    activation = tmp_path / "activation.jsonl"
    _write_ledger(
        readiness,
        contract["readiness"]["schema_version"],
        "event",
        list(reversed(contract["readiness"]["events"])),
    )
    records = parse_readiness(readiness, contract)
    with pytest.raises(RecoveryBootError, match="readiness_prefix_invalid"):
        validate_readiness_prefix(records, contract)

    duplicate = [
        contract["activation"]["coordinates"][0],
        contract["activation"]["coordinates"][0],
    ]
    _write_ledger(
        activation,
        contract["activation"]["schema_version"],
        "coordinate",
        duplicate,
    )
    with pytest.raises(RecoveryBootError, match="ledger_duplicate_value"):
        parse_activation(activation, contract)

    readiness.write_bytes(readiness.read_bytes().rstrip(b"\n"))
    with pytest.raises(RecoveryBootError, match="ledger_partial_line"):
        parse_readiness(readiness, contract)


def _write_mock_scope_package(root: Path) -> None:
    package = root / "node_modules" / "@deepseek-ai" / "dsh-scope"
    package.mkdir(parents=True)
    (package / "package.json").write_text(
        json.dumps(
            {
                "name": "@deepseek-ai/dsh-scope",
                "version": "0.1.0-rc.7",
                "type": "module",
            }
        ),
        encoding="utf-8",
    )
    (package / "index.js").write_text(
        "export const createScope = (ctx, key) => ctx.__scopeFactory(key);\n"
        "export const scopeOf = (ctx) => ctx.__scopeKey;\n",
        encoding="utf-8",
    )


def test_corrected_runner_reaches_exact_activation_and_terminal_against_mock_services(
    tmp_path: Path,
) -> None:
    node = shutil.which("node")
    assert node is not None
    contract = load_contract()
    _write_mock_scope_package(tmp_path)
    proof = tmp_path / "proof"
    proof.mkdir()
    (proof / "runner.mjs").write_bytes(corrected_runner_source())
    (proof / "effective-tool-guard.mjs").write_bytes(build_guard_source())
    driver = tmp_path / "driver.mjs"
    driver.write_text(
        """import * as runner from './proof/runner.mjs';
const config = JSON.parse(process.argv[2]);
let exitCode;
let disposed = false;
const tools = {
  view() { return { knownNames: new Set(['edit','glob','grep','read','write']), restrictableNames: new Set(['edit','glob','grep','read','write']) }; },
  restrict(value) { if (JSON.stringify(value) !== JSON.stringify({allow:['edit','glob','read']})) throw new Error('bad restriction'); },
  schemas() { return [{name:'edit'},{name:'glob'},{name:'read'}]; }
};
const agentPresets = { async mount(ctx, id) { if (id !== 'emr4-bounded-worker' || !ctx.__scopeKey) throw new Error('bad mount'); } };
const hmr = { configs: new Map(config.watchedPaths.map((value) => [value, {}])) };
const ctx = {
  get(name) { if (name === 'hmr') return hmr; if (name === 'appExit') return (code) => { exitCode = code; }; if (name === 'agentPresets') return agentPresets; if (name === 'tools') return tools; },
  __scopeFactory(key) { return { ctx: { __scopeKey: key, tools, agentPresets }, async dispose() { disposed = true; } }; }
};
await runner.apply(ctx, config);
if (exitCode !== 0 || !disposed) process.exit(2);
""",
        encoding="utf-8",
    )
    activation = tmp_path / "activation.jsonl"
    terminal = tmp_path / "terminal.json"
    watched = [
        str(tmp_path / "home" / "profiles" / "headless" / "cordis.patch.yml"),
        str(tmp_path / "home" / "cordis.patch.yml"),
    ]
    config = {
        "activationPath": str(activation),
        "terminalPath": str(terminal),
        "watchedPaths": watched,
    }

    completed = subprocess.run(
        [node, str(driver), json.dumps(config)],
        cwd=tmp_path,
        capture_output=True,
        check=False,
        timeout=5,
    )

    assert completed.returncode == 0, completed.stderr.decode(errors="replace")
    activation_records = parse_activation(activation, contract)
    validate_activation(activation_records, contract)
    assert parse_terminal(terminal, contract) == {
        "schema_version": contract["terminal"]["schema_version"],
        "stage": "preterminal_activation",
        "code": "EFFECTIVE_TOOL_COMPOSITION_PASSED",
        "detail": None,
        "effective_tool_names": ["edit", "glob", "read"],
        "effective_tool_count": 3,
    }


def test_terminal_parser_rejects_unknown_text_and_duplicate_lines(
    tmp_path: Path,
) -> None:
    contract = load_contract()
    terminal = tmp_path / "terminal.json"
    unsafe = {
        "schema_version": contract["terminal"]["schema_version"],
        "stage": "preterminal_activation",
        "code": "C:/secret/path",
        "detail": None,
        "effective_tool_names": [],
        "effective_tool_count": 0,
    }
    terminal.write_text(json.dumps(unsafe) + "\n", encoding="utf-8")
    with pytest.raises(RecoveryBootError, match="terminal_code_invalid"):
        parse_terminal(terminal, contract)
    terminal.write_text(
        json.dumps(unsafe) + "\n" + json.dumps(unsafe) + "\n", encoding="utf-8"
    )
    with pytest.raises(RecoveryBootError, match="terminal_record_count_invalid"):
        parse_terminal(terminal, contract)


def test_deterministic_check_uses_cache_only_and_starts_no_native_process() -> None:
    cache_root = DISPOSABLE_PARENT.parent / "AppData" / "Local" / "npm-cache"
    projection = deterministic_check(cache_root)

    assert projection["package_count"] == 4
    assert projection["controller"]["single_popen"] is True
    assert projection["controller"]["no_retry_loop"] is True
    assert projection["cache_blob_sha256"] == (
        "2f8f0b763d611ac536f7a9411ee43c0afc067c1b8732c3102c04dbe398bcacc5"
    )


def test_success_sequences_are_exact_and_independently_validated(
    tmp_path: Path,
) -> None:
    contract = load_contract()
    readiness_path = tmp_path / "readiness.jsonl"
    activation_path = tmp_path / "activation.jsonl"
    _write_ledger(
        readiness_path,
        contract["readiness"]["schema_version"],
        "event",
        contract["readiness"]["events"],
    )
    _write_ledger(
        activation_path,
        contract["activation"]["schema_version"],
        "coordinate",
        contract["activation"]["success_sequence"],
    )

    validate_readiness(parse_readiness(readiness_path, contract), contract)
    validate_activation(parse_activation(activation_path, contract), contract)


def test_evidence_schema_accepts_closed_minimum_shape() -> None:
    schema = json.loads(
        CONTRACT_PATH.with_name("evidence.schema.json").read_text(encoding="utf-8")
    )
    payload = {
        "schema_version": "ariadne.deepseek_native_harness_preterminal_observable_composition_recovery_boot_evidence.v1",
        "operation_id": "deepseek-native-harness-provider-free-preterminal-observable-composition-recovery-boot",
        "planning_source": load_contract()["planning_source"],
        "attempt_id": "preterminal-observable-composition-recovery-boot-attempt-001",
        "result": "pass",
        "failure_classification": None,
        "package": {},
        "source_contract": {},
        "launch": {},
        "composition": {},
        "readiness": {},
        "activation": {},
        "terminal": {},
        "provider_boundary": {},
        "cleanup": {},
    }

    jsonschema.validate(payload, schema)
