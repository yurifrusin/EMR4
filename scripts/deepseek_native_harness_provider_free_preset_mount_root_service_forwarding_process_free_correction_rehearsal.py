"""Derive the native preset root-service-forwarding correction without JavaScript."""

from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Any
from zoneinfo import ZoneInfo

import jsonschema

if str(Path(__file__).resolve().parents[1]) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from orchestration_harness.git_object_resolution import resolve_commit_source
from orchestration_harness.git_refs_snapshot import build_git_refs_snapshot
from scripts import (
    deepseek_native_harness_provider_free_preset_mount_composition_unclassified_source_reconciliation_rehearsal as predecessor,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
OPERATION_ID = (
    "deepseek-native-harness-provider-free-preset-mount-root-service-forwarding-"
    "process-free-correction-rehearsal"
)
OPERATION_ROOT = REPO_ROOT / "orchestration" / "continuity" / OPERATION_ID
PLAN_PATH = REPO_ROOT / "docs" / f"{OPERATION_ID}-plan.md"
THREAT_PATH = REPO_ROOT / "docs" / "security" / f"{OPERATION_ID}-threat-model-delta.md"
CONTRACT_PATH = OPERATION_ROOT / "contract.json"
CONTRACT_SCHEMA_PATH = OPERATION_ROOT / "contract.schema.json"
EVIDENCE_SCHEMA_PATH = OPERATION_ROOT / "evidence.schema.json"
EVIDENCE_PATH = OPERATION_ROOT / "process-free-correction-evidence.json"
REPORT_PATH = OPERATION_ROOT / "process-free-correction-report.md"
FOCUSED_TEST_PATH = (
    REPO_ROOT
    / "tests"
    / "test_deepseek_native_harness_provider_free_preset_mount_root_service_forwarding_process_free_correction_rehearsal.py"
)
ACCEPTED_RECONCILIATION_CONTRACT_PATH = predecessor.CONTRACT_PATH
ACCEPTED_RECONCILIATION_EVIDENCE_PATH = predecessor.EVIDENCE_PATH
EXPECTED_PROTECTED_COMMIT = "2e34bdad732fdab32fbf778280b3d3c70d66d602"
PROTECTED_REFS = (
    "refs/heads/master",
    "refs/remotes/origin/master",
    "refs/heads/handoff/current",
    "refs/remotes/origin/handoff/current",
)
FULL_OID = re.compile(r"(?<![0-9a-f])[0-9a-f]{40}(?![0-9a-f])")
SCHEMA_VERSION = (
    "ariadne.native_harness_preset_mount_root_service_forwarding_process_free_"
    "correction_evidence.v1"
)
CONTRACT_VERSION = (
    "ariadne.native_harness_preset_mount_root_service_forwarding_process_free_"
    "correction_contract.v1"
)
CLOSED_RESULTS = [
    "root_service_forwarding_correction_admitted",
    "prospective_source_derivation_rejected",
    "source_binding_rejected",
]
ADMITTED_RESULT = "root_service_forwarding_correction_admitted"


class ProspectiveCorrectionError(RuntimeError):
    """A closed source, contract or prospective correction coordinate failed."""


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def _canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def _git(*args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(REPO_ROOT), *args],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=15,
    )
    if completed.returncode != 0:
        raise ProspectiveCorrectionError("git_resolution_failed")
    return completed.stdout.strip()


def _source_entry(payload: bytes) -> dict[str, Any]:
    return {"bytes": len(payload), "sha256": sha256_bytes(payload)}


def accepted_source_inventory() -> tuple[dict[str, bytes], dict[str, dict[str, Any]]]:
    payloads, _ = predecessor.source_inventory()
    selected = {
        "accepted_generated_runner": payloads["generated_runner"],
        "accepted_generated_guard": payloads["generated_guard"],
        "accepted_preset_mount_bridge": payloads["preset_mount_bridge"],
        "accepted_preset_mount_sanitizer": payloads["preset_mount_sanitizer"],
        "installed_agent_presets": payloads["installed_agent_presets"],
    }
    return selected, {
        name: _source_entry(payload) for name, payload in selected.items()
    }


def predecessor_bindings() -> dict[str, str]:
    paths = {
        "frozen_plan_sha256": PLAN_PATH,
        "threat_model_sha256": THREAT_PATH,
        "accepted_source_reconciliation_contract_sha256": (
            ACCEPTED_RECONCILIATION_CONTRACT_PATH
        ),
        "accepted_source_reconciliation_evidence_sha256": (
            ACCEPTED_RECONCILIATION_EVIDENCE_PATH
        ),
    }
    return {name: sha256_file(path) for name, path in paths.items()}


def implementation_bindings() -> dict[str, str]:
    paths = {
        "controller_sha256": Path(__file__).resolve(),
        "focused_test_sha256": FOCUSED_TEST_PATH,
        "contract_schema_sha256": CONTRACT_SCHEMA_PATH,
        "evidence_schema_sha256": EVIDENCE_SCHEMA_PATH,
    }
    return {name: sha256_file(path) for name, path in paths.items()}


def machine_git_bindings() -> dict[str, Any]:
    snapshot = build_git_refs_snapshot(
        repo_root=REPO_ROOT,
        expected_protected_commit=EXPECTED_PROTECTED_COMMIT,
        protected_refs=PROTECTED_REFS,
    )
    if (
        snapshot["status"] != "passed"
        or snapshot["tracked_worktree_clean"] is not True
        or snapshot["branch_origin_aligned"] is not True
        or snapshot["protected_refs_aligned"] is not True
    ):
        raise ProspectiveCorrectionError("source_binding_rejected")
    relative_plan = PLAN_PATH.relative_to(REPO_ROOT).as_posix()
    plan_observed = _git("log", "-1", "--format=%H", "--", relative_plan)
    plan_resolution = resolve_commit_source(
        repo_root=REPO_ROOT, source_head=plan_observed
    )
    candidate_resolution = resolve_commit_source(
        repo_root=REPO_ROOT, source_head=snapshot["head"]
    )
    if (
        plan_resolution["status"] != "passed"
        or candidate_resolution["status"] != "passed"
        or FULL_OID.fullmatch(plan_resolution["resolved_commit"]) is None
        or FULL_OID.fullmatch(candidate_resolution["resolved_commit"]) is None
    ):
        raise ProspectiveCorrectionError("source_binding_rejected")
    return {
        "policy": "machine_resolved_only",
        "caller_authored_object_id_count": 0,
        "planning_source_commit": plan_resolution["resolved_commit"],
        "candidate_source_commit": candidate_resolution["resolved_commit"],
        "planning_source_is_ancestor_of_candidate": (
            _git(
                "merge-base",
                "--is-ancestor",
                plan_resolution["resolved_commit"],
                candidate_resolution["resolved_commit"],
            )
            == ""
        ),
        "branch": snapshot["branch"],
        "branch_origin_aligned": snapshot["branch_origin_aligned"],
        "protected_refs_aligned": snapshot["protected_refs_aligned"],
        "tracked_worktree_clean": snapshot["tracked_worktree_clean"],
        "docs_branding_preserved": snapshot["preserved_untracked_paths"][
            "docs/branding"
        ],
    }


def load_contract(path: Path = CONTRACT_PATH) -> dict[str, Any]:
    contract = json.loads(path.read_bytes())
    schema = json.loads(CONTRACT_SCHEMA_PATH.read_bytes())
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(schema).validate(contract)
    if FULL_OID.search(json.dumps(contract, sort_keys=True)) is not None:
        raise ProspectiveCorrectionError("caller_authored_git_object_id_rejected")
    if (
        contract["schema_version"] != CONTRACT_VERSION
        or contract["operation_id"] != OPERATION_ID
        or contract["git_binding_policy"]
        != {
            "mode": "machine_resolved_only",
            "plan_path": PLAN_PATH.relative_to(REPO_ROOT).as_posix(),
            "caller_authored_object_id_count": 0,
        }
        or contract["closed_results"] != CLOSED_RESULTS
    ):
        raise ProspectiveCorrectionError("contract_identity_rejected")
    _, observed_inventory = accepted_source_inventory()
    if observed_inventory != contract["accepted_source_inventory"]:
        raise ProspectiveCorrectionError("source_binding_rejected")
    if predecessor_bindings() != contract["predecessor_bindings"]:
        raise ProspectiveCorrectionError("predecessor_binding_rejected")
    if implementation_bindings() != contract["implementation_bindings"]:
        raise ProspectiveCorrectionError("implementation_binding_rejected")
    expected_correction = {
        "result": ADMITTED_RESULT,
        "old_runner_call": (
            "assertEffectiveToolComposition(agentCtx, PRESET_ID, TOOLS)"
        ),
        "new_runner_call": (
            "assertEffectiveToolComposition(agentCtx, presets, PRESET_ID, TOOLS)"
        ),
        "old_guard_mount_binding": (
            "mount: agentCtx.agentPresets.mount.bind(agentCtx.agentPresets)"
        ),
        "new_guard_service_argument": "presetService,",
        "bridge_call": (
            "await mount.call(presetService, agentCtx, presetId);"
        ),
        "invalid_service_terminal": "PRESET_MOUNT_UNCLASSIFIED",
    }
    if contract["correction"] != expected_correction:
        raise ProspectiveCorrectionError("correction_contract_rejected")
    expected_claim = {
        "prospective_source_correction_only": True,
        "javascript_executed": False,
        "native_harness_executed": False,
        "worker_model_provider_executed": False,
        "native_retry_authorized": False,
        "product_authority": False,
    }
    if contract["claim_boundary"] != expected_claim:
        raise ProspectiveCorrectionError("claim_boundary_rejected")
    return contract


def _replace_once(source: str, old: str, new: str) -> str:
    if source.count(old) != 1:
        raise ProspectiveCorrectionError("prospective_source_derivation_rejected")
    return source.replace(old, new)


def derive_runner_source(source: bytes) -> bytes:
    text = source.decode("utf-8")
    text = _replace_once(
        text,
        "assertEffectiveToolComposition(agentCtx, PRESET_ID, TOOLS)",
        "assertEffectiveToolComposition(agentCtx, presets, PRESET_ID, TOOLS)",
    )
    return text.encode("utf-8")


def derive_guard_source(source: bytes) -> bytes:
    text = source.decode("utf-8")
    old_signature = (
        "export async function assertEffectiveToolComposition(agentCtx, presetId, "
        "selectedTools)"
    )
    new_signature = (
        "export async function assertEffectiveToolComposition(agentCtx, "
        "presetService, presetId, requiredTools)"
    )
    text = _replace_once(text, old_signature, new_signature)
    if text.count("selectedTools") != 2:
        raise ProspectiveCorrectionError("prospective_source_derivation_rejected")
    text = text.replace("selectedTools", "requiredTools")
    text = _replace_once(
        text,
        "    mount: agentCtx.agentPresets.mount.bind(agentCtx.agentPresets),",
        "    presetService,",
    )
    return text.encode("utf-8")


def derive_bridge_source(source: bytes) -> bytes:
    text = source.decode("utf-8")
    text = _replace_once(text, "  mount,\n", "  presetService,\n")
    text = _replace_once(text, '    typeof mount !== "function" ||\n', "")
    text = _replace_once(
        text,
        "  try {\n    await mount(agentCtx, presetId);",
        "  try {\n"
        "    if (\n"
        "      presetService === null ||\n"
        "      (typeof presetService !== \"object\" &&\n"
        "        typeof presetService !== \"function\")\n"
        "    ) {\n"
        '      throw new Error("PRESET_MOUNT_ROOT_SERVICE_INVALID");\n'
        "    }\n"
        "    const mount = presetService.mount;\n"
        '    if (typeof mount !== "function") {\n'
        '      throw new Error("PRESET_MOUNT_HANDLE_INVALID");\n'
        "    }\n"
        "    await mount.call(presetService, agentCtx, presetId);",
    )
    return text.encode("utf-8")


def derive_sources(payloads: dict[str, bytes]) -> dict[str, bytes]:
    return {
        "derived_runner": derive_runner_source(payloads["accepted_generated_runner"]),
        "derived_guard": derive_guard_source(payloads["accepted_generated_guard"]),
        "derived_bridge": derive_bridge_source(
            payloads["accepted_preset_mount_bridge"]
        ),
    }


def _once(source: str, token: str) -> bool:
    return source.count(token) == 1


def source_semantics(
    accepted: dict[str, bytes], derived: dict[str, bytes]
) -> dict[str, bool]:
    runner = derived["derived_runner"].decode("utf-8")
    guard = derived["derived_guard"].decode("utf-8")
    bridge = derived["derived_bridge"].decode("utf-8")
    sanitizer = accepted["accepted_preset_mount_sanitizer"].decode("utf-8")
    installed_presets = accepted["installed_agent_presets"].decode("utf-8")
    runner_inject = (
        'export const inject = ["hmr", "headlessStartup", "agents", "sessions", '
        '"agentPresets"];'
    )
    runner_resolution = 'const presets = ctx.get("agentPresets");'
    runner_call = (
        "assertEffectiveToolComposition(agentCtx, presets, PRESET_ID, TOOLS)"
    )
    guard_signature = (
        "export async function assertEffectiveToolComposition(agentCtx, "
        "presetService, presetId, requiredTools)"
    )
    bridge_call = "await mountWithSanitizedTerminal({"
    try_index = bridge.index("  try {")
    service_check_index = bridge.index("      presetService === null", try_index)
    handle_read_index = bridge.index("    const mount = presetService.mount;", try_index)
    handle_check_index = bridge.index('    if (typeof mount !== "function")', try_index)
    mount_call_index = bridge.index(
        "    await mount.call(presetService, agentCtx, presetId);", try_index
    )
    catch_index = bridge.index("  } catch (error) {", try_index)
    forbidden_release_tokens = (
        "detail: error.message",
        "safeGuardDetail = error.message",
        "stack: error.stack",
        "cause: error.cause",
        "process.env",
        "prompt:",
        "response:",
        "credential:",
    )
    checks = {
        "runner_root_dependency_once": _once(runner, runner_inject),
        "runner_root_service_resolution_once": _once(runner, runner_resolution),
        "runner_explicit_forwarding_call_once": _once(runner, runner_call),
        "runner_old_three_argument_call_absent": (
            "assertEffectiveToolComposition(agentCtx, PRESET_ID, TOOLS)"
            not in runner
        ),
        "runner_resolution_precedes_forwarding": (
            runner.index(runner_resolution) < runner.index(runner_call)
        ),
        "guard_explicit_service_signature_once": _once(guard, guard_signature),
        "guard_selected_tools_name_retired": "selectedTools" not in guard,
        "guard_passes_service_to_bridge_once": _once(guard, "    presetService,"),
        "guard_private_service_dereference_absent": (
            "agentCtx.agentPresets" not in guard
        ),
        "guard_bridge_call_precedes_service_argument": (
            guard.index(bridge_call)
            < guard.index("    presetService,", guard.index(bridge_call))
        ),
        "bridge_accepts_service_not_mount": (
            _once(bridge, "  presetService,\n") and "  mount,\n" not in bridge
        ),
        "bridge_stable_input_validation_precedes_try": (
            bridge.index("  if (\n") < try_index
            and 'typeof PresetMountError !== "function"' in bridge[:try_index]
        ),
        "bridge_service_validation_inside_try": (
            try_index < service_check_index < catch_index
        ),
        "bridge_mount_read_inside_try": (
            service_check_index < handle_read_index < catch_index
        ),
        "bridge_mount_validation_inside_try": (
            handle_read_index < handle_check_index < catch_index
        ),
        "bridge_bound_call_inside_try": (
            handle_check_index < mount_call_index < catch_index
        ),
        "bridge_catch_sanitizes_once": _once(
            bridge, "sanitizePresetMountError(error, PresetMountError)"
        ),
        "bridge_invalid_service_and_handle_are_caught": (
            bridge.index('throw new Error("PRESET_MOUNT_ROOT_SERVICE_INVALID")')
            < catch_index
            and bridge.index('throw new Error("PRESET_MOUNT_HANDLE_INVALID")')
            < catch_index
        ),
        "bridge_success_projection_preserved": _once(
            bridge, "Object.freeze({ passed: true, terminal: null })"
        ),
        "guard_sanitized_terminal_handoff_preserved": all(
            token in guard
            for token in (
                "PresetMountSanitizedTerminalError",
                "throw new PresetMountSanitizedTerminalError(mountReading.terminal)",
            )
        ),
        "sanitizer_unclassified_terminal_preserved": all(
            token in sanitizer
            for token in (
                'unclassified: "PRESET_MOUNT_UNCLASSIFIED"',
                "return terminal(CODES.unclassified);",
            )
        ),
        "installed_service_exposes_mount": all(
            token in installed_presets
            for token in (
                "var AgentPresets = class extends Service",
                "async mount(agentCtx, id)",
            )
        ),
        "derived_sources_release_no_raw_detail": not any(
            token in runner + guard + bridge for token in forbidden_release_tokens
        ),
    }
    return checks


def deterministic_check() -> dict[str, Any]:
    contract = load_contract()
    accepted_evidence = json.loads(ACCEPTED_RECONCILIATION_EVIDENCE_PATH.read_bytes())
    if (
        accepted_evidence.get("result")
        != "root_preset_service_not_forwarded_before_bridge"
        or accepted_evidence.get("claim_boundary", {}).get(
            "prospective_correction_applied"
        )
        is not False
    ):
        raise ProspectiveCorrectionError("accepted_source_reconciliation_rejected")
    accepted, accepted_inventory = accepted_source_inventory()
    derived = derive_sources(accepted)
    derived_inventory = {
        name: _source_entry(payload) for name, payload in derived.items()
    }
    checks = source_semantics(accepted, derived)
    failed = sorted(name for name, passed in checks.items() if not passed)
    result = ADMITTED_RESULT if not failed else "prospective_source_derivation_rejected"
    return {
        "schema_version": SCHEMA_VERSION,
        "operation_id": OPERATION_ID,
        "git_binding": machine_git_bindings(),
        "result": result,
        "failed_source_coordinates": failed,
        "accepted_source_inventory": accepted_inventory,
        "derived_source_inventory": derived_inventory,
        "source_semantics": checks,
        "correction_projection": {
            "root_service_admitted_by_runner": True,
            "root_service_forwarded_explicitly": result == ADMITTED_RESULT,
            "guard_private_service_dereference_count": guard_private_count(derived),
            "mount_handle_validation_inside_bridge": result == ADMITTED_RESULT,
            "invalid_service_terminal": "PRESET_MOUNT_UNCLASSIFIED",
            "javascript_materialized_or_executed": False,
        },
        "claim_boundary": {
            "prospective_source_correction_admitted": result == ADMITTED_RESULT,
            "javascript_executed": False,
            "native_harness_executed": False,
            "worker_model_provider_executed": False,
            "native_runtime_path_proved": False,
            "native_retry_authorized": False,
            "product_authority": False,
        },
        "process_boundary": {
            "node_process_count": 0,
            "native_harness_process_count": 0,
            "worker_process_count": 0,
            "model_request_count": 0,
            "provider_request_count": 0,
            "network_attempt_count": 0,
            "target_creation_count": 0,
            "target_use_count": 0,
            "retry_count": 0,
            "resume_count": 0,
        },
        "contract": contract,
    }


def guard_private_count(derived: dict[str, bytes]) -> int:
    return derived["derived_guard"].decode("utf-8").count("agentCtx.agentPresets")


def _evidence_projection(reading: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in reading.items() if key != "contract"}


def render_report(evidence: dict[str, Any], timestamp: str) -> str:
    failed = evidence["failed_source_coordinates"]
    failed_text = "none" if not failed else ", ".join(failed)
    return f"""# Native Harness root-service-forwarding process-free correction report

Date: 2026-08-22

Timestamp: {timestamp} (Australia/Brisbane)

Result: **{evidence['result']}**

The prospective runner passes its already admitted root preset service into an
explicit guard parameter. The prospective guard no longer reads
`agentCtx.agentPresets`; it passes only the service object into the typed
bridge. The bridge alone validates the service, reads and validates its mount
handle and invokes that handle with the service as receiver. All of those
operations occur inside the bridge's sanitizing `try` boundary.

Failed source coordinates: `{failed_text}`.

The caller-authored contract contains no Git object identity. Its plan and
candidate sources were resolved by the repository resolver as full commits at
evidence time.

This is a prospective source correction only. JavaScript was not materialized
or executed, and no Node, native Harness, worker, model or provider process,
request, retry or resume occurred. A separately frozen isolated Node fixture is
required before any native process can be considered.
"""


def execute() -> dict[str, Any]:
    if EVIDENCE_PATH.exists() or REPORT_PATH.exists():
        raise ProspectiveCorrectionError("immutable_output_exists")
    evidence = _evidence_projection(deterministic_check())
    schema = json.loads(EVIDENCE_SCHEMA_PATH.read_bytes())
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(schema).validate(evidence)
    if evidence["result"] != ADMITTED_RESULT:
        raise ProspectiveCorrectionError("prospective_source_derivation_rejected")
    timestamp = datetime.now(ZoneInfo("Australia/Brisbane")).isoformat()
    EVIDENCE_PATH.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE_PATH.write_bytes(_canonical(evidence))
    REPORT_PATH.write_text(render_report(evidence, timestamp), encoding="utf-8")
    return evidence


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    reading = execute() if args.execute else _evidence_projection(deterministic_check())
    print(json.dumps(reading, sort_keys=True, separators=(",", ":")))
    return 0 if reading["result"] == ADMITTED_RESULT else 1


if __name__ == "__main__":
    raise SystemExit(main())
