from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess

import jsonschema
import pytest
import yaml

from scripts.deepseek_native_harness_provider_free_effective_tool_composition_native_boot_proof import (
    CONTRACT_PATH,
    EXPECTED_EVENTS,
    NativeCompositionProofError,
    REPO_ROOT,
    build_patch_pair,
    build_preset_source,
    deterministic_check,
    load_contract,
    parse_events,
    parse_terminal,
    runner_source,
    sentinel_source,
    validate_events,
    validate_patch_pair,
    validate_predecessors,
    validate_runner_source,
)
from scripts.deepseek_native_harness_provider_free_effective_tool_composition_guard import (
    build_guard_source,
)


def test_contract_and_schema_freeze_one_nonretrying_native_boot() -> None:
    contract = load_contract()
    schema = json.loads(CONTRACT_PATH.with_name("contract.schema.json").read_text(encoding="utf-8"))

    jsonschema.validate(contract, schema)
    assert contract["launch"] == {
        "node_flag": "--expose-internals",
        "profile_args": ["--profile", "headless"],
        "native_boot_process_count": 1,
        "online_package_fallback": False,
        "package_lifecycle_scripts": False,
        "attempt_id": "native-composition-attempt-001",
        "automatic_retry": False,
    }
    assert contract["terminal"]["effective_tool_names"] == ["edit", "glob", "read"]


def test_predecessors_are_full_git_objects_with_exact_bytes() -> None:
    projection = validate_predecessors(load_contract())

    assert all(len(value) == 40 for value in projection["accepted_sources"].values())
    assert projection["guard"]["sha256"] == (
        "6678ed31bdcd30a5018689b72ad509c182854bf5d63862f59b397acc8de40894"
    )


def test_plan_and_threat_delta_keep_closed_surfaces_and_semantic_clockwork_fix() -> None:
    plan = Path(
        "docs/deepseek-native-harness-provider-free-effective-tool-composition-native-boot-proof-plan.md"
    ).read_text(encoding="utf-8")
    threat = Path(
        "docs/security/deepseek-native-harness-provider-free-effective-tool-composition-native-boot-proof-threat-model-delta.md"
    ).read_text(encoding="utf-8")

    for phrase in (
        "exactly one offline",
        "automatic or manual second native",
        "no agent, session, turn, broker request, model request",
        "no production, deployment, release, Pages",
        "current_position.outcome",
    ):
        assert phrase in plan
    assert "future target as current evidence" in threat


def test_preset_has_exactly_two_filesystem_rows() -> None:
    contract = load_contract()
    payload = build_preset_source(contract)

    assert yaml.safe_load(payload) == contract["preset"]["rows"]
    assert payload.count(b"- id:") == 2
    assert b"sampleOverCapGlobResults: false" in payload


def test_patch_adds_only_guard_runner_after_readiness(tmp_path: Path) -> None:
    profile = tmp_path / "home" / "profiles" / "headless"
    modules = tmp_path / "installation" / "proof"
    initial, changed = build_patch_pair(
        profile,
        tmp_path / "events.jsonl",
        tmp_path / "terminal.json",
        modules / "sentinel.mjs",
        modules / "runner.mjs",
    )

    validate_patch_pair(initial, changed)
    assert b"provider-free-effective-tool-proof-runner" not in initial
    assert changed.count(b"provider-free-effective-tool-proof-runner") == 1
    assert b"inject: [hmr, agentPresets, tools]" in changed


def test_patch_rejects_runner_in_initial_layer(tmp_path: Path) -> None:
    profile = tmp_path / "home" / "profiles" / "headless"
    modules = tmp_path / "installation" / "proof"
    _, changed = build_patch_pair(
        profile,
        tmp_path / "events.jsonl",
        tmp_path / "terminal.json",
        modules / "sentinel.mjs",
        modules / "runner.mjs",
    )

    with pytest.raises(NativeCompositionProofError, match="initial_patch_runner_present"):
        validate_patch_pair(changed, changed)


def test_runner_has_one_guard_scope_terminal_disposal_exit_chain() -> None:
    projection = validate_runner_source(runner_source())

    assert projection["create_scope_count"] == 1
    assert projection["guard_call_count"] == 1
    assert projection["exclusive_terminal_count"] == 1
    assert projection["scope_dispose_count"] == 1
    assert projection["exit_request_count"] == 1


def test_sentinel_attributes_readiness_to_exact_hmr_watches() -> None:
    source = sentinel_source().decode()

    assert 'const hmr = ctx.get("hmr")' in source
    assert "hmr.configs instanceof Map" in source
    assert 'emit("stock_headless_hmr_ready")' in source
    assert "config.watchedPaths" in source


def _write_mock_scope_package(root: Path) -> None:
    package = root / "node_modules" / "@deepseek-ai" / "dsh-scope"
    package.mkdir(parents=True)
    (package / "package.json").write_text(
        json.dumps({"name": "@deepseek-ai/dsh-scope", "version": "0.1.0-rc.7", "type": "module"}),
        encoding="utf-8",
    )
    (package / "index.js").write_text(
        "export const createScope = (ctx, key) => ctx.__scopeFactory(key);\n"
        "export const scopeOf = (ctx) => ctx.__scopeKey;\n",
        encoding="utf-8",
    )


def test_generated_runner_reaches_exact_terminal_against_mock_services(tmp_path: Path) -> None:
    node = shutil.which("node")
    assert node is not None
    _write_mock_scope_package(tmp_path)
    proof = tmp_path / "proof"
    proof.mkdir()
    (proof / "runner.mjs").write_bytes(runner_source())
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
  get(name) { if (name === 'hmr') return hmr; if (name === 'appExit') return (code) => { exitCode = code; }; },
  __scopeFactory(key) { return { ctx: { __scopeKey: key, tools, agentPresets }, async dispose() { disposed = true; } }; }
};
await runner.apply(ctx, config);
if (exitCode !== 0 || !disposed) process.exit(2);
""",
        encoding="utf-8",
    )
    events = tmp_path / "events.jsonl"
    terminal = tmp_path / "terminal.json"
    watched = [
        str(tmp_path / "home" / "profiles" / "headless" / "cordis.patch.yml"),
        str(tmp_path / "home" / "cordis.patch.yml"),
    ]
    events.write_text(
        "".join(
            json.dumps({"schema_version": "ariadne.deepseek_native_harness_effective_tool_native_boot_event.v1", "sequence": index, "event": event}) + "\n"
            for index, event in enumerate(EXPECTED_EVENTS[:2], start=1)
        ),
        encoding="utf-8",
    )
    config = {"eventPath": str(events), "terminalPath": str(terminal), "watchedPaths": watched}

    completed = subprocess.run(
        [node, str(driver), json.dumps(config)],
        cwd=tmp_path,
        capture_output=True,
        check=False,
        timeout=5,
    )

    assert completed.returncode == 0, completed.stderr.decode(errors="replace")
    validate_events(parse_events(events))
    assert parse_terminal(terminal) == {
        "schema_version": "ariadne.deepseek_native_harness_effective_tool_native_boot_terminal.v1",
        "stage": "pre_provider_tool_composition",
        "code": "EFFECTIVE_TOOL_COMPOSITION_PASSED",
        "detail": None,
        "effective_tool_names": ["edit", "glob", "read"],
        "effective_tool_count": 3,
    }


def test_terminal_parser_rejects_unknown_text_and_duplicate_lines(tmp_path: Path) -> None:
    terminal = tmp_path / "terminal.json"
    unsafe = {
        "schema_version": "ariadne.deepseek_native_harness_effective_tool_native_boot_terminal.v1",
        "stage": "pre_provider_tool_composition",
        "code": "C:/secret/path",
        "detail": None,
        "effective_tool_names": [],
        "effective_tool_count": 0,
    }
    terminal.write_text(json.dumps(unsafe) + "\n", encoding="utf-8")
    with pytest.raises(NativeCompositionProofError, match="terminal_code_invalid"):
        parse_terminal(terminal)
    terminal.write_text(json.dumps(unsafe) + "\n" + json.dumps(unsafe) + "\n", encoding="utf-8")
    with pytest.raises(NativeCompositionProofError, match="terminal_record_count_invalid"):
        parse_terminal(terminal)


def test_event_ledger_rejects_reordering_and_duplicates(tmp_path: Path) -> None:
    ledger = tmp_path / "events.jsonl"
    wrong = [EXPECTED_EVENTS[0], EXPECTED_EVENTS[2]]
    ledger.write_text(
        "".join(
            json.dumps({"schema_version": "ariadne.deepseek_native_harness_effective_tool_native_boot_event.v1", "sequence": index, "event": event}) + "\n"
            for index, event in enumerate(wrong, start=1)
        ),
        encoding="utf-8",
    )

    with pytest.raises(NativeCompositionProofError, match="event_sequence_mismatch"):
        validate_events(parse_events(ledger))


def test_deterministic_check_uses_cache_only_and_starts_no_native_process() -> None:
    cache_root = REPO_ROOT.parent / "AppData" / "Local" / "npm-cache"
    projection = deterministic_check(cache_root)

    assert projection["package_count"] == 4
    assert projection["cache_blob_sha256"] == (
        "2f8f0b763d611ac536f7a9411ee43c0afc067c1b8732c3102c04dbe398bcacc5"
    )


def test_evidence_schema_accepts_closed_minimum_shape() -> None:
    schema = json.loads(CONTRACT_PATH.with_name("evidence.schema.json").read_text(encoding="utf-8"))
    payload = {
        "schema_version": "ariadne.deepseek_native_harness_effective_tool_native_boot_evidence.v1",
        "operation_id": "deepseek-native-harness-provider-free-effective-tool-composition-native-boot-proof",
        "planning_source": load_contract()["planning_source"],
        "attempt_id": "native-composition-attempt-001",
        "result": "pass",
        "failure_classification": None,
        "package": {},
        "source_contract": {},
        "launch": {},
        "composition": {},
        "lifecycle": {},
        "terminal": None,
        "provider_boundary": {},
        "cleanup": {},
    }

    jsonschema.validate(payload, schema)
