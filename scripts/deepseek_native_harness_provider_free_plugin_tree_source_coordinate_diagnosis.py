#!/usr/bin/env python3
"""Provider-free static diagnosis for the rc.7 plugin-tree startup terminal."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
OPERATION_ID = (
    "deepseek-native-harness-provider-free-plugin-tree-failed-to-load-"
    "source-coordinate-diagnosis"
)
CONTINUITY_ROOT = (
    REPO_ROOT
    / "orchestration"
    / "continuity"
    / OPERATION_ID
)
TERMINAL_PATH = (
    REPO_ROOT
    / "orchestration"
    / "continuity"
    / "raisa-authored-synthetic-check-in-native-harness-bounded-worker-"
    "monitored-development-rehearsal"
    / "attempt-004"
    / "pre-hmr-startup-terminal.json"
)
PROFILE_SOURCE_PATH = (
    REPO_ROOT
    / "scripts"
    / "raisa_authored_synthetic_check_in_native_harness_bounded_worker_"
    "monitored_development_rehearsal.py"
)
PREDECESSOR_SOURCE_PATH = (
    REPO_ROOT
    / "scripts"
    / "deepseek_native_harness_provider_free_complete_composition_native_"
    "boot_recovery.py"
)
PREDECESSOR_EVIDENCE_PATH = (
    REPO_ROOT
    / "orchestration"
    / "continuity"
    / "deepseek-native-harness-provider-free-complete-composition-native-boot-"
    "recovery"
    / "provider-free-complete-composition-native-boot-evidence.json"
)
PRESET_PATH = (
    REPO_ROOT
    / "orchestration"
    / "continuity"
    / "deepseek-native-harness-provider-free-emr4-bounded-worker-preset-"
    "materialisation-recovery"
    / "materialised-home"
    / ".agent-presets"
    / "emr4-bounded-worker"
    / "agent.cordis.yml"
)

EXPECTED_TERMINAL_SHA256 = (
    "cc77466d1e30a371478b700cc08cb23d91b86e0161dadaf8c8ad23883fea3dcb"
)
EXPECTED_PACKAGE_SHA256 = (
    "7a9f356ad1e27c7013b44619bc675b8cb877f995cd0951ab3dfeb10d4edcc361"
)
EXPECTED_PRESET_SHA256 = (
    "3de182eb702e6f2b397941c73393b87f65acb9b401565f966059d2bd46f649d1"
)
EXPECTED_PREDECESSOR_EVIDENCE_SHA256 = (
    "9ba784b0726addb5644ac3786def410aed56e5bf9da3e23ec21d8e10f6ba1ea0"
)

ABSOLUTE_PROOF_MODULE = re.compile(
    r'name:\s+\{quoted\(proof / "(?P<module>[^"]+\.mjs)"\)\}'
)


class DiagnosisError(RuntimeError):
    """Fail-closed deterministic diagnosis error."""


@dataclass(frozen=True)
class StaticInputs:
    package_json: bytes
    terminal: bytes
    profile_source: bytes
    predecessor_source: bytes
    predecessor_evidence: bytes
    preset: bytes
    app_boot: bytes
    loader_entry: bytes
    loader_tree: bytes


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def canonical_json_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode(
        "utf-8"
    )


def read_bytes(path: Path) -> bytes:
    try:
        return path.read_bytes()
    except OSError as exc:
        raise DiagnosisError(f"required_static_source_unavailable:{path.name}") from exc


def package_sources(package_root: Path) -> StaticInputs:
    package_root = package_root.resolve()
    scoped_root = package_root.parent
    return StaticInputs(
        package_json=read_bytes(package_root / "package.json"),
        terminal=read_bytes(TERMINAL_PATH),
        profile_source=read_bytes(PROFILE_SOURCE_PATH),
        predecessor_source=read_bytes(PREDECESSOR_SOURCE_PATH),
        predecessor_evidence=read_bytes(PREDECESSOR_EVIDENCE_PATH),
        preset=read_bytes(PRESET_PATH),
        app_boot=read_bytes(scoped_root / "dsh-app-boot" / "lib" / "index.js"),
        loader_entry=read_bytes(
            scoped_root / "cordis-plugin-loader" / "src" / "config" / "entry.ts"
        ),
        loader_tree=read_bytes(
            scoped_root / "cordis-plugin-loader" / "src" / "config" / "tree.ts"
        ),
    )


def _terminal_matches(terminal: dict[str, Any], digest: str) -> bool:
    diagnostic = terminal.get("structured_diagnostic", {})
    chain = diagnostic.get("cause_chain", [])
    return bool(
        digest == EXPECTED_TERMINAL_SHA256
        and terminal.get("schema_version")
        == "ariadne.native_harness_pre_hmr_startup_terminal.v2"
        and terminal.get("cause") == "structured_entrypoint_import_rejected"
        and terminal.get("hmr_event_count") == 0
        and diagnostic.get("phase") == "entrypoint_import_rejected"
        and len(chain) == 4
        and chain[0].get("message_coordinate") == "plugin_tree_failed_to_load"
        and chain[-1].get("code_coordinate") == "unrecognized"
        and not diagnostic.get("cause_chain_cycle_detected")
        and not diagnostic.get("cause_chain_truncated")
        and diagnostic.get("raw_error_message_retained") is False
        and diagnostic.get("raw_paths_retained") is False
        and diagnostic.get("raw_stack_retained") is False
    )


def _source_chain_matches(texts: dict[str, str]) -> bool:
    app_boot = texts["app_boot"]
    loader_entry = texts["loader_entry"]
    loader_tree = texts["loader_tree"]
    return all(
        (
            'bareModuleBaseUrl === void 0 ? Include' in app_boot,
            'stage = "plugin tree failed to load"' in app_boot,
            'throw new Error(`${binName}: ${stage}: ${detail}${stack}`, { cause });'
            in app_boot,
            "throw updateError('import', this.options, error)" in loader_entry,
            "throw updateError('apply', this.options, error)" in loader_entry,
            "else if (name.startsWith('.'))" in loader_tree,
            "return await import(/* @vite-ignore */name)" in loader_tree,
        )
    )


def analyze_static_inputs(inputs: StaticInputs) -> dict[str, Any]:
    digests = {
        "package_manifest": sha256_bytes(inputs.package_json),
        "attempt_004_structured_terminal": sha256_bytes(inputs.terminal),
        "current_profile_author": sha256_bytes(inputs.profile_source),
        "accepted_relative_specifier_predecessor": sha256_bytes(
            inputs.predecessor_source
        ),
        "accepted_relative_specifier_predecessor_evidence": sha256_bytes(
            inputs.predecessor_evidence
        ),
        "accepted_bounded_worker_preset": sha256_bytes(inputs.preset),
        "rc7_app_boot": sha256_bytes(inputs.app_boot),
        "rc7_loader_entry": sha256_bytes(inputs.loader_entry),
        "rc7_loader_tree": sha256_bytes(inputs.loader_tree),
    }
    try:
        package = json.loads(inputs.package_json)
        terminal = json.loads(inputs.terminal)
        predecessor_evidence = json.loads(inputs.predecessor_evidence)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise DiagnosisError("static_json_input_invalid") from exc

    texts = {
        "profile": inputs.profile_source.decode("utf-8"),
        "predecessor": inputs.predecessor_source.decode("utf-8"),
        "app_boot": inputs.app_boot.decode("utf-8"),
        "loader_entry": inputs.loader_entry.decode("utf-8"),
        "loader_tree": inputs.loader_tree.decode("utf-8"),
    }
    package_ok = bool(
        package.get("name") == "@deepseek-ai/dsh"
        and package.get("version") == "0.1.0-rc.7"
        and digests["package_manifest"] == EXPECTED_PACKAGE_SHA256
    )
    terminal_ok = _terminal_matches(
        terminal, digests["attempt_004_structured_terminal"]
    )
    preset_ok = digests["accepted_bounded_worker_preset"] == EXPECTED_PRESET_SHA256
    chain_ok = _source_chain_matches(texts)

    function_body = texts["profile"].split("def profile_patch", 1)[-1].split(
        "def validate_profile_patch", 1
    )[0]
    initial_body, marker, changed_body = function_body.partition("    if changed:")
    initial_absolute_modules = ABSOLUTE_PROOF_MODULE.findall(initial_body)
    changed_absolute_modules = ABSOLUTE_PROOF_MODULE.findall(changed_body)
    predecessor_relative = all(
        anchor in texts["predecessor"]
        for anchor in (
            "name: ../../../installation/proof/sentinel.mjs",
            "name: ../../../installation/proof/runner.mjs",
        )
    )
    predecessor_passed = bool(
        digests["accepted_relative_specifier_predecessor_evidence"]
        == EXPECTED_PREDECESSOR_EVIDENCE_SHA256
        and predecessor_evidence.get("result") == "pass"
        and predecessor_evidence.get("launch", {}).get("exit_code") == 0
        and predecessor_evidence.get("readiness", {}).get("exact_expected_order")
        is True
        and predecessor_evidence.get("provider_boundary", {}).get(
            "provider_request_count"
        )
        == 0
        and predecessor_evidence.get("package", {}).get("name")
        == "@deepseek-ai/dsh"
        and predecessor_evidence.get("package", {}).get("version") == "0.1.0-rc.7"
    )

    bindings_ok = package_ok and terminal_ok and preset_ok and chain_ok and bool(marker)
    match_count = len(initial_absolute_modules) if bindings_ok else 0
    unique = bool(
        bindings_ok
        and match_count == 1
        and initial_absolute_modules == ["sentinel.mjs"]
        and changed_absolute_modules == ["runner.mjs"]
        and predecessor_relative
        and predecessor_passed
    )

    if not bindings_ok:
        verdict = "source_binding_failed"
        status = "failed_closed"
        owner = "insufficient_source_coordinate"
        coordinate = None
        repair_justified = False
        rationale = (
            "One or more exact rc.7 package, terminal, preset or wrapper-source "
            "bindings failed; no deeper coordinate is admitted."
        )
    elif unique:
        verdict = "unique_supported_coordinate"
        status = "passed"
        owner = "profile_input"
        coordinate = (
            "profile_patch.initial.synthetic-worker-hmr-sentinel.name:"
            "absolute_windows_path_not_normalized_to_relative_or_file_url_"
            "before_loader_import"
        )
        repair_justified = True
        rationale = (
            "The initial patch has exactly one custom module import and authors "
            "it as an absolute Windows filesystem specifier. The rc.7 root Include "
            "uses the unnormalised Include path, whose loader reserves relative "
            "handling for dot-prefixed names and otherwise imports the supplied "
            "specifier. The resulting root-apply/import/underlying-error wrappers "
            "plus the boot wrapper match the four-node terminal. The accepted "
            "provider-free predecessor proves the same sentinel and later runner "
            "with profile-relative specifiers. A separate repair may replace only "
            "this two-row specifier family before any new boot proof."
        )
    else:
        verdict = "insufficient_source_coordinate"
        status = "failed_closed"
        owner = "insufficient_source_coordinate"
        coordinate = None
        repair_justified = False
        rationale = (
            "The admitted source does not expose exactly one initial absolute "
            "custom-module branch plus its changed-patch counterpart and accepted "
            "relative-specifier control."
        )

    candidates: list[dict[str, Any]] = []
    if bindings_ok:
        for index, module in enumerate(initial_absolute_modules):
            candidates.append(
                {
                    "candidate_id": f"initial_absolute_custom_module_{index + 1}",
                    "module_coordinate": module,
                    "profile_phase": "initial_pre_hmr",
                    "specifier_form": "absolute_windows_filesystem_path",
                    "loader_route": "non_relative_specifier_import",
                    "wrapper_shape": [
                        "boot_plugin_tree_wrapper",
                        "root_include_apply_wrapper",
                        "loader_entry_import_wrapper",
                        "underlying_import_error_closed_code",
                    ],
                    "terminal_shape_match": len(initial_absolute_modules) == 1,
                }
            )

    return {
        "schema_version": (
            "ariadne.native_harness_plugin_tree_source_diagnosis_evidence.v1"
        ),
        "operation_id": OPERATION_ID,
        "status": status,
        "verdict": verdict,
        "package": {
            "name": package.get("name", ""),
            "version": package.get("version", ""),
            "package_json_sha256": digests["package_manifest"],
            "source_root_coordinate": "preexisting_local_rc7_materialization",
        },
        "inputs": [
            {"coordinate": name, "sha256": digest}
            for name, digest in sorted(digests.items())
        ],
        "candidate_branches": candidates,
        "match_count": match_count,
        "narrowest_supported_coordinate": coordinate,
        "owner_classification": owner,
        "repair_justified": repair_justified,
        "repair_rationale": rationale,
        "zero_activity": {
            "node_process_count": 0,
            "harness_process_count": 0,
            "broker_process_count": 0,
            "worker_process_count": 0,
            "model_request_count": 0,
            "provider_request_count": 0,
            "network_request_count": 0,
        },
        "claim_boundary": (
            "Static source evidence narrows the attempt-004 startup branch and "
            "justifies at most a separate provider-free two-row specifier repair. "
            "It does not prove a repaired boot, reach DeepSeek, authorize an "
            "occupied retry or open product, data, deployment or protected refs."
        ),
    }


def report_markdown(evidence: dict[str, Any]) -> str:
    timestamp = datetime.now().astimezone().isoformat()
    coordinate = evidence["narrowest_supported_coordinate"] or "none"
    return f"""# DeepSeek native Harness plugin-tree source-coordinate diagnosis

Date: {timestamp[:10]}
Timestamp: {timestamp} (Australia/Brisbane)

## Result

- Verdict: `{evidence['verdict']}`
- Owner classification: `{evidence['owner_classification']}`
- Matching source branches: `{evidence['match_count']}`
- Narrowest supported coordinate: `{coordinate}`
- Separate provider-free repair justified: `{str(evidence['repair_justified']).lower()}`

## Reading

{evidence['repair_rationale']}

The diagnosis used only the exact local rc.7 package source, accepted profile
authors, preset and immutable sanitized attempt-004 terminal. Node, Harness,
broker, worker, model, provider and network counts are all zero. No raw terminal
message, code, stack, path or stream was reconstructed.

## Claim boundary

{evidence['claim_boundary']}
"""


def run(package_root: Path, output_root: Path = CONTINUITY_ROOT) -> dict[str, Any]:
    evidence = analyze_static_inputs(package_sources(package_root))
    output_root.mkdir(parents=True, exist_ok=True)
    (output_root / "diagnosis-evidence.json").write_bytes(
        canonical_json_bytes(evidence)
    )
    (output_root / "diagnosis-report.md").write_text(
        report_markdown(evidence), encoding="utf-8", newline="\n"
    )
    return evidence


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package-root", required=True, type=Path)
    parser.add_argument("--output-root", type=Path, default=CONTINUITY_ROOT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        evidence = run(args.package_root, args.output_root)
    except DiagnosisError as exc:
        raise SystemExit(str(exc)) from exc
    print(evidence["verdict"])
    return 0 if evidence["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
