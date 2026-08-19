from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess

import pytest
import yaml

from scripts.deepseek_native_harness_provider_free_hmr_boot_proof import (
    CONTRACT_PATH,
    EXPECTED_EVENTS,
    ProofError,
    _verify_installed_source,
    build_child_environment,
    build_patch_pair,
    custom_runner_source,
    load_contract,
    network_guard_source,
    parse_events,
    sentinel_source,
    validate_patch_pair,
    validate_terminal_events,
    verify_tarball,
)


def test_contract_freezes_exact_rc7_identity_and_one_nonretrying_boot() -> None:
    contract = load_contract()

    assert contract["package"] == {
        "name": "@deepseek-ai/dsh",
        "version": "0.1.0-rc.7",
        "bin": "lib/bin.js",
        "tarball_sha1": "8a69013c06179d7af437de92fb4a9a2e1fd7d410",
        "tarball_integrity": "sha512-ZceDCJ8FAywih+USW/OMk9jEhunlvJBGEz4kqrhau23hPzbciOazZrywH0nBRsaalSeAJ1JGBmjtw4OSjToStw==",
    }
    assert contract["launch"]["node_flag"] == "--expose-internals"
    assert contract["launch"]["profile_args"] == ["--profile", "headless"]
    assert contract["launch"]["native_boot_process_count"] == 1
    assert contract["terminal"]["automatic_retry"] is False


def test_contract_schema_and_plan_keep_occupied_and_product_authority_closed() -> None:
    schema = json.loads(CONTRACT_PATH.with_name("contract.schema.json").read_text(encoding="utf-8"))
    plan = (
        Path("docs/deepseek-native-harness-provider-free-stock-headless-to-custom-runner-hmr-boot-proof-plan.md")
        .read_text(encoding="utf-8")
    )

    assert schema["properties"]["planning_source"]["const"] == load_contract()["planning_source"]
    for phrase in (
        "no occupied DeepSeek attempt",
        "no EMR4 product/config/API/client/waiting-area change",
        "Attempt-004 remains closed",
        "There is no automatic second native boot",
    ):
        assert phrase in plan


def test_wrong_tarball_rejects_before_materialisation(tmp_path: Path) -> None:
    tarball = tmp_path / "wrong.tgz"
    tarball.write_bytes(b"not the pinned package")

    with pytest.raises(ProofError, match="package_tarball_sha1_mismatch"):
        verify_tarball(tarball, load_contract())


def test_installed_source_check_accepts_exact_documented_headless_marker(tmp_path: Path) -> None:
    scope = tmp_path / "node_modules" / "@deepseek-ai"
    package = scope / "dsh"
    (package / "lib").mkdir(parents=True)
    (scope / "dsh-headless").mkdir()
    (scope / "cordis-plugin-hmr" / "lib").mkdir(parents=True)
    (package / "package.json").write_text(
        json.dumps(
            {
                "name": "@deepseek-ai/dsh",
                "version": "0.1.0-rc.7",
                "bin": {"dsh": "lib/bin.js"},
            }
        ),
        encoding="utf-8",
    )
    (package / "lib" / "bin.js").write_text(
        'option("--profile <name>"); // dsh --profile headless', encoding="utf-8"
    )
    (scope / "dsh-headless" / "cordis.patch.yml").write_text(
        "- id: hmr\n  disabled: true\n- id: headless-runner\n", encoding="utf-8"
    )
    (scope / "cordis-plugin-hmr" / "lib" / "index.js").write_text(
        'throw new Error("--expose-internals is required for HMR service");\n'
        "async registerConfig() {}\n",
        encoding="utf-8",
    )
    (package / "lib" / "profile-boot-exact.js").write_text(
        "config: { root: [] };\nawait watchUserPatches(ctx);\nawait watchUserPatches(ctx);\n",
        encoding="utf-8",
    )

    projection = _verify_installed_source(package, load_contract())

    assert all(projection["checks"].values())


def test_patch_transition_adds_only_hmr_bound_custom_runner(tmp_path: Path) -> None:
    profile = tmp_path / "home" / "profiles" / "headless"
    profile.mkdir(parents=True)
    initial, changed = build_patch_pair(profile, tmp_path / "events.jsonl")
    validate_patch_pair(initial, changed)
    initial_rows = yaml.safe_load(initial)
    changed_rows = yaml.safe_load(changed)

    assert "provider-free-hmr-custom-runner" not in initial.decode()
    assert changed_rows[:-1] == initial_rows[:-1]
    assert [row["id"] for row in initial_rows[:3]] == [
        "headless-runner",
        "code-runtime",
        "session-telemetry-otel",
    ]
    assert all(row["disabled"] is True for row in initial_rows[:3])
    assert changed_rows[-1]["insert"][-1]["inject"] == ["hmr"]


def test_patch_transition_rejects_custom_runner_in_initial_layer(tmp_path: Path) -> None:
    profile = tmp_path / "home" / "profiles" / "headless"
    profile.mkdir(parents=True)
    initial, changed = build_patch_pair(profile, tmp_path / "events.jsonl")

    with pytest.raises(ProofError, match="initial_patch_custom_runner_present"):
        validate_patch_pair(changed, changed)


def test_plugins_attribute_readiness_to_real_hmr_registry_and_exit_owner() -> None:
    sentinel = sentinel_source().decode()
    runner = custom_runner_source().decode()

    assert 'const hmr = ctx.get("hmr")' in sentinel
    assert "hmr.configs instanceof Map" in sentinel
    assert 'emit("stock_headless_hmr_ready")' in sentinel
    assert 'export const inject = ["hmr"]' in runner
    assert 'const exit = ctx.get("appExit")' in runner
    assert 'emit("custom_runner_reached")' in runner
    assert 'emit("app_exit_requested")' in runner
    assert "exit(0)" in runner


def test_generated_plugins_execute_exact_lifecycle_against_mock_hmr(tmp_path: Path) -> None:
    node = shutil.which("node")
    assert node is not None
    sentinel_path = tmp_path / "sentinel.mjs"
    runner_path = tmp_path / "custom-runner.mjs"
    event_path = tmp_path / "events.jsonl"
    profile_patch = tmp_path / "home" / "profiles" / "headless" / "cordis.patch.yml"
    home_patch = tmp_path / "home" / "cordis.patch.yml"
    sentinel_path.write_bytes(sentinel_source())
    runner_path.write_bytes(custom_runner_source())
    driver = tmp_path / "driver.mjs"
    driver.write_text(
        """import * as sentinel from './sentinel.mjs';
import * as runner from './custom-runner.mjs';
const config = JSON.parse(process.argv[2]);
let exitCode;
const cleanups = [];
const hmr = { configs: new Map(config.watchedPaths.map((value) => [value, {}])) };
const ctx = {
  get(name) { if (name === 'hmr') return hmr; if (name === 'appExit') return (code) => { exitCode = code; }; },
  effect(factory) { cleanups.push(factory()); }
};
sentinel.apply(ctx, config);
await new Promise((resolve) => setTimeout(resolve, 50));
runner.apply(ctx, config);
for (const cleanup of cleanups) cleanup();
if (exitCode !== 0) process.exit(2);
""",
        encoding="utf-8",
    )
    config = {"eventPath": str(event_path), "watchedPaths": [str(profile_patch), str(home_patch)]}

    result = subprocess.run(
        [node, str(driver), json.dumps(config)],
        cwd=tmp_path,
        capture_output=True,
        check=False,
        timeout=5,
    )

    assert result.returncode == 0, result.stderr.decode(errors="replace")
    validate_terminal_events(parse_events(event_path))


def test_network_guard_denies_all_frozen_node_primitives() -> None:
    guard = network_guard_source().decode()

    for primitive in (
        "net.Socket.connect",
        "net.connect",
        "tls.connect",
        "http.request",
        "https.request",
        "dns.promises.",
        "dgram.createSocket",
        "fetch",
        "WebSocket",
    ):
        assert primitive in guard


def test_child_environment_scrubs_credentials_and_forces_provider_free_controls(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("DEEPSEEK_API_KEY", "forbidden")
    monkeypatch.setenv("HTTPS_PROXY", "forbidden")
    monkeypatch.setenv("EMR4_HARMLESS_MARKER", "kept")
    guard = tmp_path / "guard.mjs"
    guard.write_text("", encoding="utf-8")

    child, removed = build_child_environment(tmp_path / "home", guard, tmp_path / "network.jsonl")

    assert removed >= 2
    assert "DEEPSEEK_API_KEY" not in child
    assert "HTTPS_PROXY" not in child
    assert child["EMR4_HARMLESS_MARKER"] == "kept"
    assert child["DSH_TELEMETRY_DISABLED"] == "1"
    assert child["NPM_CONFIG_OFFLINE"] == "true"
    assert child["NODE_OPTIONS"].startswith("--import=file:")


def test_event_ledger_requires_exact_unique_order(tmp_path: Path) -> None:
    ledger = tmp_path / "events.jsonl"
    records = [
        {
            "schema_version": "ariadne.deepseek_native_harness_hmr_boot_event.v1",
            "sequence": index,
            "event": event,
        }
        for index, event in enumerate(EXPECTED_EVENTS, start=1)
    ]
    ledger.write_text("".join(json.dumps(record) + "\n" for record in records), encoding="utf-8")

    parsed = parse_events(ledger)
    validate_terminal_events(parsed)
    parsed[-1]["event"] = "custom_runner_reached"
    with pytest.raises(ProofError, match="event_sequence_mismatch"):
        validate_terminal_events(parsed)


def test_partial_or_malformed_event_ledger_rejects(tmp_path: Path) -> None:
    ledger = tmp_path / "events.jsonl"
    ledger.write_text('{"schema_version":"wrong"}', encoding="utf-8")

    with pytest.raises(ProofError, match="partial_line"):
        parse_events(ledger)


def test_retained_native_attempt_evidence_is_exact_and_clean() -> None:
    root = CONTRACT_PATH.parent
    evidence = json.loads(
        (root / "provider-free-native-harness-hmr-boot-evidence.json").read_text(
            encoding="utf-8"
        )
    )
    rejected = json.loads(
        (root / "prelaunch-source-predicate-rejection.json").read_text(encoding="utf-8")
    )

    assert evidence["attempt_id"] == "native-attempt-001"
    assert evidence["result"] == "pass"
    assert evidence["failure_classification"] is None
    assert evidence["package"]["name"] == "@deepseek-ai/dsh"
    assert evidence["package"]["version"] == "0.1.0-rc.7"
    assert evidence["package"]["sha1"] == load_contract()["package"]["tarball_sha1"]
    assert all(evidence["source_contract"]["checks"].values())
    assert evidence["launch"]["native_boot_process_count"] == 1
    assert evidence["launch"]["mutated_after_in_process_readiness"] is True
    assert evidence["launch"]["exit_code"] == 0
    assert evidence["lifecycle"]["events"] == EXPECTED_EVENTS
    assert evidence["lifecycle"]["exact_expected_order"] is True
    assert evidence["lifecycle"]["readiness_source"] == "in_process_sentinel_only"
    assert set(evidence["provider_boundary"].values()) >= {0}
    for key in (
        "network_attempt_count",
        "model_request_count",
        "broker_request_count",
        "provider_request_count",
        "agent_session_count",
    ):
        assert evidence["provider_boundary"][key] == 0
    assert evidence["cleanup"]["process_absent"] is True
    assert evidence["cleanup"]["disposable_root_absent"] is True
    assert rejected["result"] == "fail"
    assert rejected["launch"]["native_boot_process_count"] == 0
    assert rejected["cleanup"]["disposable_root_absent"] is True
