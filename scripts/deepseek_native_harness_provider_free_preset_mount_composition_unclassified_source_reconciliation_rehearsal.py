"""Attribute the consumed native unclassified composition terminal from exact source."""

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

from scripts import (
    deepseek_native_harness_provider_free_preset_mount_sanitized_terminal_native_rehearsal as native,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
OPERATION_ID = (
    "deepseek-native-harness-provider-free-preset-mount-composition-unclassified-"
    "source-reconciliation-rehearsal"
)
OPERATION_ROOT = REPO_ROOT / "orchestration" / "continuity" / OPERATION_ID
PLAN_PATH = REPO_ROOT / "docs" / f"{OPERATION_ID}-plan.md"
THREAT_PATH = REPO_ROOT / "docs" / "security" / f"{OPERATION_ID}-threat-model-delta.md"
CONTRACT_PATH = OPERATION_ROOT / "contract.json"
CONTRACT_SCHEMA_PATH = OPERATION_ROOT / "contract.schema.json"
EVIDENCE_SCHEMA_PATH = OPERATION_ROOT / "evidence.schema.json"
EVIDENCE_PATH = OPERATION_ROOT / "source-reconciliation-evidence.json"
REPORT_PATH = OPERATION_ROOT / "source-reconciliation-report.md"
FOCUSED_TEST_PATH = (
    REPO_ROOT
    / "tests"
    / "test_deepseek_native_harness_provider_free_preset_mount_composition_unclassified_source_reconciliation_rehearsal.py"
)
PACKAGE_SEED_ROOT = Path(
    r"C:\Users\sarashera\.cache\emr4-native-harness\dsh-0.1.0-rc.7-package-seed"
)
PACKAGE_NAMESPACE_ROOT = PACKAGE_SEED_ROOT / "node_modules" / "@deepseek-ai"
BRIDGE_PATH = native.BRIDGE_PATH
SANITIZER_PATH = native.SANITIZER_PATH
ACCEPTED_NATIVE_CONTRACT_PATH = native.CONTRACT_PATH
ACCEPTED_TERMINAL_PATH = native.OPERATION_ROOT / "offline-admitted-terminal.json"
ACCEPTED_RECOVERY_PATH = native.OPERATION_ROOT / "offline-recovery-evidence.json"
PRIOR_RECONCILIATION_ROOT = (
    REPO_ROOT
    / "orchestration"
    / "continuity"
    / "deepseek-native-harness-provider-free-preset-mount-source-coordinate-reconciliation-rehearsal"
)
PRIOR_RECONCILIATION_CONTRACT_PATH = PRIOR_RECONCILIATION_ROOT / "contract.json"
PRIOR_RECONCILIATION_EVIDENCE_PATH = (
    PRIOR_RECONCILIATION_ROOT / "source-coordinate-reconciliation-evidence.json"
)
INSTALLED_SOURCE_PATHS = {
    "agent_loop": PACKAGE_NAMESPACE_ROOT / "dsh-agent-loop" / "lib" / "index.js",
    "scope": PACKAGE_NAMESPACE_ROOT / "dsh-scope" / "lib" / "index.js",
    "agent_presets": PACKAGE_NAMESPACE_ROOT / "dsh-agent-presets" / "lib" / "index.js",
}
FULL_OID = re.compile(r"^[0-9a-f]{40}$")
SCHEMA_VERSION = (
    "ariadne.native_harness_composition_unclassified_source_reconciliation_"
    "evidence.v1"
)
CLOSED_RESULTS = [
    "root_preset_service_not_forwarded_before_bridge",
    "source_evidence_insufficient",
    "source_binding_rejected",
]
ATTRIBUTION = "root_preset_service_not_forwarded_before_bridge"


class SourceReconciliationError(RuntimeError):
    """A closed source binding or semantic coordinate failed."""


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
        raise SourceReconciliationError("git_resolution_failed")
    return completed.stdout.strip()


def _source_entry(payload: bytes) -> dict[str, Any]:
    return {"bytes": len(payload), "sha256": sha256_bytes(payload)}


def source_inventory() -> tuple[dict[str, bytes], dict[str, dict[str, Any]]]:
    payloads = {
        "generated_runner": native.runner_source(),
        "generated_guard": native.guard_source(),
        "preset_mount_bridge": BRIDGE_PATH.read_bytes(),
        "preset_mount_sanitizer": SANITIZER_PATH.read_bytes(),
        **{
            f"installed_{name}": path.read_bytes()
            for name, path in INSTALLED_SOURCE_PATHS.items()
        },
    }
    return payloads, {name: _source_entry(payload) for name, payload in payloads.items()}


def predecessor_bindings() -> dict[str, str]:
    paths = {
        "frozen_plan_sha256": PLAN_PATH,
        "threat_model_sha256": THREAT_PATH,
        "accepted_native_contract_sha256": ACCEPTED_NATIVE_CONTRACT_PATH,
        "accepted_terminal_sha256": ACCEPTED_TERMINAL_PATH,
        "accepted_offline_recovery_sha256": ACCEPTED_RECOVERY_PATH,
        "prior_source_reconciliation_contract_sha256": (
            PRIOR_RECONCILIATION_CONTRACT_PATH
        ),
        "prior_source_reconciliation_evidence_sha256": (
            PRIOR_RECONCILIATION_EVIDENCE_PATH
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


def load_contract(path: Path = CONTRACT_PATH) -> dict[str, Any]:
    contract = json.loads(path.read_bytes())
    schema = json.loads(CONTRACT_SCHEMA_PATH.read_bytes())
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(schema).validate(contract)
    planning_source = contract["planning_source"]
    plan_relative = PLAN_PATH.relative_to(REPO_ROOT).as_posix()
    if (
        contract["schema_version"]
        != "ariadne.native_harness_composition_unclassified_source_reconciliation_contract.v1"
        or contract["operation_id"] != OPERATION_ID
        or FULL_OID.fullmatch(planning_source) is None
        or planning_source
        != _git("rev-parse", "--verify", f"{planning_source}^{{commit}}")
        or planning_source != _git("log", "-1", "--format=%H", "--", plan_relative)
    ):
        raise SourceReconciliationError("contract_identity_or_planning_source_invalid")
    if contract["closed_results"] != CLOSED_RESULTS:
        raise SourceReconciliationError("closed_result_vocabulary_invalid")
    if contract["attribution"] != {
        "result": ATTRIBUTION,
        "exact_runtime_exception_observed": False,
        "private_context_value_observed": False,
        "new_bridge_runtime_path_proved": False,
        "prospective_correction_applied": False,
    }:
        raise SourceReconciliationError("attribution_claim_boundary_invalid")
    _, observed_inventory = source_inventory()
    if observed_inventory != contract["source_inventory"]:
        raise SourceReconciliationError("source_binding_rejected")
    if predecessor_bindings() != contract["predecessor_bindings"]:
        raise SourceReconciliationError("predecessor_binding_rejected")
    if implementation_bindings() != contract["implementation_bindings"]:
        raise SourceReconciliationError("implementation_binding_rejected")
    return contract


def _once(source: str, token: str) -> bool:
    return source.count(token) == 1


def source_semantics(payloads: dict[str, bytes]) -> dict[str, bool]:
    runner = payloads["generated_runner"].decode("utf-8")
    guard = payloads["generated_guard"].decode("utf-8")
    bridge = payloads["preset_mount_bridge"].decode("utf-8")
    agent_loop = payloads["installed_agent_loop"].decode("utf-8")
    scope = payloads["installed_scope"].decode("utf-8")
    presets = payloads["installed_agent_presets"].decode("utf-8")
    runner_root_inject = (
        'export const inject = ["hmr", "headlessStartup", "agents", "sessions", '
        '"agentPresets"];'
    )
    runner_root_resolution = 'const presets = ctx.get("agentPresets");'
    runner_guard_call = "assertEffectiveToolComposition(agentCtx, PRESET_ID, TOOLS)"
    guard_signature = (
        "export async function assertEffectiveToolComposition(agentCtx, presetId, "
        "selectedTools)"
    )
    premature_mount_binding = (
        "mount: agentCtx.agentPresets.mount.bind(agentCtx.agentPresets)"
    )
    bridge_call = "await mountWithSanitizedTerminal({"
    bridge_try = "  try {\n    await mount(agentCtx, presetId);"
    broad_fallback = (
        "const code = FAILURE_COORDINATES.has(error?.code) ? error.code : "
        '"EFFECTIVE_TOOL_COMPOSITION_UNCLASSIFIED";'
    )
    inject_start = agent_loop.index("static inject = [")
    inject_end = agent_loop.index("];", inject_start)
    inject_block = agent_loop[inject_start:inject_end]
    checks = {
        "runner_declares_root_agent_presets_dependency_once": _once(
            runner, runner_root_inject
        ),
        "runner_resolves_root_agent_presets_once": _once(
            runner, runner_root_resolution
        ),
        "runner_guard_call_omits_root_presets_once": _once(runner, runner_guard_call)
        and "assertEffectiveToolComposition(agentCtx, presets," not in runner,
        "guard_signature_omits_root_presets_once": _once(guard, guard_signature),
        "guard_dereferences_private_agent_presets_once": _once(
            guard, premature_mount_binding
        ),
        "guard_dereference_is_bridge_argument_evaluation": (
            guard.index(bridge_call)
            < guard.index(premature_mount_binding)
            < guard.index("    PresetMountError,", guard.index(bridge_call))
        ),
        "bridge_sanitizing_try_starts_after_argument_validation": bridge.index(
            "if ("
        )
        < bridge.index(bridge_try),
        "broader_sanitizer_maps_uncoded_error_to_unclassified_once": _once(
            guard, broad_fallback
        ),
        "agent_loop_setup_receives_private_agent_context_once": _once(
            agent_loop, "setup?.(prepared.agent.ctx)"
        ),
        "agent_loop_private_context_derives_from_loop_runtime": all(
            _once(agent_loop, token)
            for token in (
                "this.runtime = { ctx };",
                "const loopCtx = this.runtime.ctx;",
                "new ReactLoopAgent(loopCtx, id, options, session)",
                "this.scope = createScope(loopCtx, this);",
            )
        ),
        "agent_loop_dependency_surface_excludes_agent_presets": (
            "agentPresets" not in inject_block
            and all(
                f'"{name}"' in inject_block
                for name in ("agents", "sessions", "llm", "tools", "systemPrompt")
            )
        ),
        "scope_inherits_minting_plugin_dependency_api": all(
            token in scope
            for token in (
                "The scoped context inherits the minting plugin's",
                "dependency API and owns every registration made through it.",
                "const fiber = ctx.plugin(scope);",
                "const scoped = fiber.ctx.extend({ [kScope]: key });",
            )
        ),
        "installed_preset_service_exposes_mount": all(
            token in presets
            for token in (
                "var AgentPresets = class extends Service",
                "async mount(agentCtx, id)",
            )
        ),
    }
    return checks


def deterministic_check() -> dict[str, Any]:
    contract = load_contract()
    admitted = json.loads(ACCEPTED_TERMINAL_PATH.read_bytes())
    recovery = json.loads(ACCEPTED_RECOVERY_PATH.read_bytes())
    prior = json.loads(PRIOR_RECONCILIATION_EVIDENCE_PATH.read_bytes())
    expected_terminal = {
        "error_class": None,
        "last_admitted_stage": "private_identity_admitted",
        "preset_mount_terminal": None,
        "result": "preset_composition_failure_attributed",
        "safe_guard_coordinate": "EFFECTIVE_TOOL_COMPOSITION_UNCLASSIFIED",
        "safe_guard_detail": None,
    }
    if admitted["terminal"] != expected_terminal:
        raise SourceReconciliationError("accepted_terminal_binding_rejected")
    if (
        recovery.get("result") != "recovered_finite_terminal"
        or recovery.get("new_bridge_runtime_path_proved") is not False
        or prior.get("result") != "pass"
        or prior.get("claim_boundary", {}).get("source_reachable_candidate_set_only")
        is not True
    ):
        raise SourceReconciliationError("accepted_evidence_semantics_rejected")
    payloads, inventory = source_inventory()
    checks = source_semantics(payloads)
    failed = sorted(name for name, passed in checks.items() if not passed)
    result = ATTRIBUTION if not failed else "source_evidence_insufficient"
    return {
        "schema_version": SCHEMA_VERSION,
        "operation_id": OPERATION_ID,
        "candidate_source": _git("rev-parse", "HEAD"),
        "result": result,
        "failed_source_coordinates": failed,
        "accepted_terminal": expected_terminal,
        "source_inventory": inventory,
        "source_semantics": checks,
        "attribution": {
            "root_preset_service_admitted_by_runner": True,
            "root_preset_service_forwarded_to_guard": False,
            "private_agent_context_dependency_surface_declares_agent_presets": False,
            "mount_handle_dereference_occurs_before_bridge_entry": True,
            "uncoded_escape_maps_to_observed_terminal": True,
            "prospective_correction_coordinate": (
                "forward_admitted_root_preset_service_into_guard_and_validate_"
                "mount_handle_inside_bridge"
            ),
        },
        "claim_boundary": {
            "deterministic_source_route_explained": result == ATTRIBUTION,
            "exact_runtime_exception_observed": False,
            "private_context_value_observed": False,
            "new_bridge_runtime_path_proved": False,
            "prospective_correction_applied": False,
            "native_retry_authorized": False,
            "worker_model_provider_process_authorized": False,
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


def _evidence_projection(reading: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in reading.items() if key != "contract"}


def render_report(evidence: dict[str, Any], timestamp: str) -> str:
    failed = evidence["failed_source_coordinates"]
    failed_text = "none" if not failed else ", ".join(failed)
    return f"""# Native Harness composition-unclassified source reconciliation report

Date: 2026-08-22

Timestamp: {timestamp} (Australia/Brisbane)

Result: **{evidence['result']}**

The exact generated runner admits the root `agentPresets` service but does not
forward that handle into the composition guard. The exact installed agent loop
supplies setup with a private context derived from a dependency surface that
does not declare `agentPresets`. The generated guard dereferences
`agentCtx.agentPresets.mount.bind(...)` before the preset-mount bridge enters
its sanitizing boundary. An uncoded escape therefore reaches the broader guard,
whose closed fallback is the observed
`EFFECTIVE_TOOL_COMPOSITION_UNCLASSIFIED` coordinate.

Failed source coordinates: `{failed_text}`.

The narrowest prospective correction is to forward the already admitted root
preset service explicitly into the guard and validate the mount handle inside
the bridge. No correction or retry occurred here. No raw exception or private
context value was recovered, and the new bridge runtime path remains unproved.

Node, native Harness, worker, model and provider processes started by this
reconciliation: **0**.
"""


def execute() -> dict[str, Any]:
    if EVIDENCE_PATH.exists() or REPORT_PATH.exists():
        raise SourceReconciliationError("immutable_output_exists")
    evidence = _evidence_projection(deterministic_check())
    schema = json.loads(EVIDENCE_SCHEMA_PATH.read_bytes())
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(schema).validate(evidence)
    if evidence["result"] != ATTRIBUTION:
        raise SourceReconciliationError("source_evidence_insufficient")
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
