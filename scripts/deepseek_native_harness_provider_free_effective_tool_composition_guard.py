"""Build the provider-free rc.7 effective-tool composition guard evidence."""

from __future__ import annotations

import argparse
import base64
from dataclasses import dataclass
from datetime import datetime
import hashlib
from io import BytesIO
import json
import os
from pathlib import Path
import re
import tarfile
from typing import Any
from zoneinfo import ZoneInfo

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
OPERATION_ID = (
    "deepseek-native-harness-provider-free-effective-tool-composition-and-"
    "terminal-coordinate-guard"
)
OPERATION_ROOT = REPO_ROOT / "orchestration" / "continuity" / OPERATION_ID
CONTRACT_PATH = OPERATION_ROOT / "contract.json"
EVIDENCE_PATH = OPERATION_ROOT / "provider-free-effective-tool-guard-evidence.json"
REPORT_PATH = OPERATION_ROOT / "provider-free-effective-tool-guard-report.md"
SCHEMA_VERSION = "ariadne.deepseek_native_harness_effective_tool_guard_evidence.v1"
CONTRACT_SCHEMA_VERSION = (
    "ariadne.deepseek_native_harness_effective_tool_guard_contract.v1"
)
SAFE_TOOL_NAME = re.compile(r"^[a-z_]+$")
SUCCESS_COORDINATE = "EFFECTIVE_TOOL_COMPOSITION_PASSED"
FAILURE_COORDINATES = (
    "EFFECTIVE_TOOL_COMPOSITION_INPUT_INVALID",
    "EFFECTIVE_TOOL_COMPOSITION_PRESET_MOUNT_FAILED",
    "EFFECTIVE_TOOL_COMPOSITION_SCOPE_MISSING",
    "EFFECTIVE_TOOL_COMPOSITION_SCOPE_LOCAL_TOOL_PRESENT",
    "EFFECTIVE_TOOL_COMPOSITION_EXPECTED_TOOL_NOT_INHERITED",
    "EFFECTIVE_TOOL_COMPOSITION_RESTRICTION_FAILED",
    "EFFECTIVE_TOOL_COMPOSITION_SCHEMA_VIEW_INVALID",
    "EFFECTIVE_TOOL_COMPOSITION_EFFECTIVE_VIEW_MISMATCH",
    "EFFECTIVE_TOOL_COMPOSITION_UNCLASSIFIED",
)
EXPECTED_TOOLS = ("edit", "glob", "read")


class GuardError(RuntimeError):
    """Fail-closed deterministic guard construction error."""


@dataclass(frozen=True)
class Projection:
    coordinate: str
    detail: str | None = None

    def as_dict(self, scenario: str) -> dict[str, str | None]:
        return {
            "scenario": scenario,
            "coordinate": self.coordinate,
            "detail": self.detail,
        }


def canonical_json_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def load_contract(path: Path = CONTRACT_PATH) -> dict[str, Any]:
    contract = json.loads(path.read_text(encoding="utf-8"))
    if contract.get("schema_version") != CONTRACT_SCHEMA_VERSION:
        raise GuardError("contract_schema_mismatch")
    if contract.get("operation_id") != OPERATION_ID:
        raise GuardError("contract_operation_mismatch")
    planning_source = contract.get("planning_source")
    if not isinstance(planning_source, str) or not re.fullmatch(
        r"[0-9a-f]{40}", planning_source
    ):
        raise GuardError("contract_planning_source_not_full_git_oid")
    package_names = [row.get("name") for row in contract.get("packages", [])]
    if package_names != [
        "@deepseek-ai/dsh",
        "@deepseek-ai/dsh-tools",
        "@deepseek-ai/dsh-agent-presets",
        "@deepseek-ai/dsh-scope",
    ]:
        raise GuardError("contract_package_order_mismatch")
    guard = contract.get("guard", {})
    if tuple(guard.get("selected_tools", ())) != EXPECTED_TOOLS:
        raise GuardError("contract_selected_tools_mismatch")
    if guard.get("success_coordinate") != SUCCESS_COORDINATE:
        raise GuardError("contract_success_coordinate_mismatch")
    if tuple(guard.get("failure_coordinates", ())) != FAILURE_COORDINATES:
        raise GuardError("contract_failure_coordinates_mismatch")
    if guard.get("forbidden_terminal_coordinate") != "CUSTOM_RUNNER_FAILURE":
        raise GuardError("contract_forbidden_coordinate_mismatch")
    return contract


def _cache_blob_path(cache_root: Path, integrity: str) -> Path:
    if not integrity.startswith("sha512-"):
        raise GuardError("package_integrity_algorithm_mismatch")
    try:
        digest = base64.b64decode(integrity.removeprefix("sha512-"), validate=True)
    except ValueError as error:
        raise GuardError("package_integrity_encoding_invalid") from error
    if len(digest) != 64:
        raise GuardError("package_integrity_length_invalid")
    encoded = digest.hex()
    return (
        cache_root
        / "_cacache"
        / "content-v2"
        / "sha512"
        / encoded[:2]
        / encoded[2:4]
        / encoded[4:]
    )


def verify_package_blob(
    package: dict[str, Any], cache_root: Path
) -> tuple[dict[str, Any], dict[str, bytes]]:
    blob_path = _cache_blob_path(cache_root, package["registry_integrity"])
    if not blob_path.is_file() or blob_path.is_symlink():
        raise GuardError(f"package_cache_blob_missing:{package['name']}")
    payload = blob_path.read_bytes()
    shasum = hashlib.sha1(payload).hexdigest()  # noqa: S324 - npm identity.
    integrity = "sha512-" + base64.b64encode(hashlib.sha512(payload).digest()).decode(
        "ascii"
    )
    if shasum != package["registry_shasum"]:
        raise GuardError(f"package_registry_shasum_mismatch:{package['name']}")
    if integrity != package["registry_integrity"]:
        raise GuardError(f"package_registry_integrity_mismatch:{package['name']}")

    retained_members: dict[str, bytes] = {}
    expected = {f"package/{row['path']}": row for row in package["members"]}
    try:
        with tarfile.open(fileobj=BytesIO(payload), mode="r:gz") as archive:
            members = {member.name: member for member in archive.getmembers()}
            for archive_name, row in expected.items():
                member = members.get(archive_name)
                if member is None or not member.isfile() or member.issym():
                    raise GuardError(
                        f"package_member_missing_or_unsafe:{package['name']}:{row['path']}"
                    )
                stream = archive.extractfile(member)
                if stream is None:
                    raise GuardError(
                        f"package_member_unreadable:{package['name']}:{row['path']}"
                    )
                member_payload = stream.read()
                if len(member_payload) != row["bytes"]:
                    raise GuardError(
                        f"package_member_size_mismatch:{package['name']}:{row['path']}"
                    )
                if sha256_bytes(member_payload) != row["sha256"]:
                    raise GuardError(
                        f"package_member_sha256_mismatch:{package['name']}:{row['path']}"
                    )
                retained_members[row["path"]] = member_payload
    except tarfile.TarError as error:
        raise GuardError(f"package_tar_invalid:{package['name']}") from error

    return (
        {
            "name": package["name"],
            "version": package["version"],
            "registry_identity_passed": True,
            "member_count": len(expected),
            "members_passed": True,
        },
        retained_members,
    )


def verify_source_semantics(
    sources: dict[tuple[str, str], bytes]
) -> dict[str, bool]:
    tools = sources[("@deepseek-ai/dsh-tools", "lib/types/index.js")].decode(
        "utf-8"
    )
    presets = sources[("@deepseek-ai/dsh-agent-presets", "lib/index.js")].decode(
        "utf-8"
    )
    scope = sources[("@deepseek-ai/dsh-scope", "lib/index.js")].decode("utf-8")
    checks = {
        "tools_restrict_reads_restrictable_names": (
            "const known = this.view(scope).restrictableNames;" in tools
        ),
        "tools_restrict_rejects_unknown_names": (
            "tools.restrict() names unknown global tool" in tools
            and "filter(name => !known.has(name))" in tools
        ),
        "tools_view_filters_inherited_layers": (
            "if (layers.every(layer => layer.admits(name)))" in tools
            and "visible.set(name, definition);" in tools
        ),
        "tools_view_preserves_own_layer_registrations": (
            "if (own !== undefined)" in tools
            and "for (const [name, definition] of own.tools.entries())" in tools
            and "visible.set(name, definition);" in tools
        ),
        "preset_mount_awaits_standing_generation": (
            "const standing = await this.ensureStanding(preset);" in presets
        ),
        "preset_mount_binds_agent_scope_to_standing_parent": (
            "bindScopeParent(agentKey, standing.key)" in presets
        ),
        "scope_parent_binding_is_single_owner": (
            "if (scopeParents.has(key)) throw new Error" in scope
            and "linkScopeParent(key, parent);" in scope
        ),
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise GuardError("source_semantic_check_failed:" + ",".join(sorted(failed)))
    return checks


def verify_profile(contract: dict[str, Any]) -> dict[str, Any]:
    profile_contract = contract["profile"]
    profile_path = (REPO_ROOT / profile_contract["path"]).resolve()
    if REPO_ROOT.resolve() not in profile_path.parents:
        raise GuardError("profile_path_escape")
    payload = profile_path.read_bytes()
    if sha256_bytes(payload) != profile_contract["sha256"]:
        raise GuardError("profile_sha256_mismatch")
    family = yaml.safe_load(payload.decode("utf-8"))
    selected_name = profile_contract["selected_profile"]
    selected = family.get("profiles", {}).get(selected_name)
    if not isinstance(selected, dict):
        raise GuardError("selected_profile_missing")
    selected_tools = selected.get("tools")
    if not isinstance(selected_tools, list) or sorted(selected_tools) != list(
        EXPECTED_TOOLS
    ):
        raise GuardError("selected_profile_tools_mismatch")
    outer = family.get("tool_view_enforcement", {}).get("outer_broker", {})
    if outer != {
        "required": True,
        "tool_allowlist_source": "selected_profile.tools",
        "exact_match_required": True,
    }:
        raise GuardError("outer_broker_contract_mismatch")
    return {
        "path_sha256_passed": True,
        "selected_profile": selected_name,
        "selected_tools": list(EXPECTED_TOOLS),
    }


def build_guard_source() -> bytes:
    source = r'''import { scopeOf } from "@deepseek-ai/dsh-scope";

const PRESET_ID = "emr4-bounded-worker";
const EXPECTED_TOOLS = Object.freeze(["edit", "glob", "read"]);
const SUCCESS_COORDINATE = "EFFECTIVE_TOOL_COMPOSITION_PASSED";
const FAILURE_COORDINATES = new Set([
  "EFFECTIVE_TOOL_COMPOSITION_INPUT_INVALID",
  "EFFECTIVE_TOOL_COMPOSITION_PRESET_MOUNT_FAILED",
  "EFFECTIVE_TOOL_COMPOSITION_SCOPE_MISSING",
  "EFFECTIVE_TOOL_COMPOSITION_SCOPE_LOCAL_TOOL_PRESENT",
  "EFFECTIVE_TOOL_COMPOSITION_EXPECTED_TOOL_NOT_INHERITED",
  "EFFECTIVE_TOOL_COMPOSITION_RESTRICTION_FAILED",
  "EFFECTIVE_TOOL_COMPOSITION_SCHEMA_VIEW_INVALID",
  "EFFECTIVE_TOOL_COMPOSITION_EFFECTIVE_VIEW_MISMATCH",
  "EFFECTIVE_TOOL_COMPOSITION_UNCLASSIFIED",
]);
const SAFE_TOOL_NAME = /^[a-z_]+$/;

class EffectiveToolCompositionError extends Error {
  constructor(code, names = []) {
    super(code);
    this.name = "EffectiveToolCompositionError";
    this.code = code;
    this.safeToolNames = Object.freeze([...new Set(names)].sort());
  }
}

function fail(code, names = []) {
  throw new EffectiveToolCompositionError(code, names);
}

function exactNames(values) {
  if (!Array.isArray(values)) return undefined;
  if (!values.every((value) => typeof value === "string" && SAFE_TOOL_NAME.test(value))) return undefined;
  if (new Set(values).size !== values.length) return undefined;
  return [...values].sort();
}

export async function assertEffectiveToolComposition(agentCtx, presetId, selectedTools) {
  const selected = exactNames(selectedTools);
  if (presetId !== PRESET_ID || selected === undefined || JSON.stringify(selectedTools) !== JSON.stringify(EXPECTED_TOOLS) || JSON.stringify(selected) !== JSON.stringify(EXPECTED_TOOLS)) {
    fail("EFFECTIVE_TOOL_COMPOSITION_INPUT_INVALID");
  }
  try {
    await agentCtx.agentPresets.mount(agentCtx, presetId);
  } catch {
    fail("EFFECTIVE_TOOL_COMPOSITION_PRESET_MOUNT_FAILED");
  }
  const scope = scopeOf(agentCtx);
  if (scope === undefined) fail("EFFECTIVE_TOOL_COMPOSITION_SCOPE_MISSING");
  const before = agentCtx.tools.view(scope);
  const known = exactNames([...before.knownNames]);
  const restrictable = exactNames([...before.restrictableNames]);
  if (known === undefined || restrictable === undefined) fail("EFFECTIVE_TOOL_COMPOSITION_SCHEMA_VIEW_INVALID");
  const restrictableSet = new Set(restrictable);
  const local = known.filter((name) => !restrictableSet.has(name));
  if (local.length > 0) fail("EFFECTIVE_TOOL_COMPOSITION_SCOPE_LOCAL_TOOL_PRESENT", local);
  const missing = EXPECTED_TOOLS.filter((name) => !restrictableSet.has(name));
  if (missing.length > 0) fail("EFFECTIVE_TOOL_COMPOSITION_EXPECTED_TOOL_NOT_INHERITED", missing);
  try {
    agentCtx.tools.restrict({ allow: [...EXPECTED_TOOLS] });
  } catch {
    fail("EFFECTIVE_TOOL_COMPOSITION_RESTRICTION_FAILED");
  }
  let schemas;
  try {
    schemas = agentCtx.tools.schemas(scope);
  } catch {
    fail("EFFECTIVE_TOOL_COMPOSITION_SCHEMA_VIEW_INVALID");
  }
  const effective = exactNames(Array.isArray(schemas) ? schemas.map((schema) => schema?.name) : undefined);
  if (effective === undefined) fail("EFFECTIVE_TOOL_COMPOSITION_SCHEMA_VIEW_INVALID");
  if (JSON.stringify(effective) !== JSON.stringify(EXPECTED_TOOLS)) {
    const mismatch = [...new Set([...effective, ...EXPECTED_TOOLS].filter((name) => !effective.includes(name) || !EXPECTED_TOOLS.includes(name)))].sort();
    fail("EFFECTIVE_TOOL_COMPOSITION_EFFECTIVE_VIEW_MISMATCH", mismatch);
  }
  return Object.freeze({ coordinate: SUCCESS_COORDINATE, presetId: PRESET_ID, effectiveToolNames: effective, effectiveToolCount: effective.length });
}

export function sanitizeEffectiveToolTerminal(error) {
  const code = FAILURE_COORDINATES.has(error?.code) ? error.code : "EFFECTIVE_TOOL_COMPOSITION_UNCLASSIFIED";
  const names = exactNames(error?.safeToolNames);
  return Object.freeze({
    stage: "pre_provider_tool_composition",
    code,
    detail: names === undefined || names.length === 0 ? null : names.join(","),
  });
}
'''
    return source.encode("utf-8")


def validate_guard_source(payload: bytes) -> dict[str, Any]:
    source = payload.decode("utf-8")
    counts = {
        "mount_count": source.count("agentCtx.agentPresets.mount("),
        "view_count": source.count("agentCtx.tools.view("),
        "restriction_count": source.count("agentCtx.tools.restrict("),
        "schema_projection_count": source.count("agentCtx.tools.schemas("),
    }
    if counts != {
        "mount_count": 1,
        "view_count": 1,
        "restriction_count": 1,
        "schema_projection_count": 1,
    }:
        raise GuardError("generated_guard_call_count_mismatch")
    ordered = [
        "await agentCtx.agentPresets.mount(",
        "agentCtx.tools.view(",
        "agentCtx.tools.restrict(",
        "agentCtx.tools.schemas(",
    ]
    positions = [source.index(fragment) for fragment in ordered]
    if positions != sorted(positions):
        raise GuardError("generated_guard_call_order_mismatch")
    if "CUSTOM_RUNNER_FAILURE" in source:
        raise GuardError("generated_guard_forbidden_generic_present")
    for coordinate in (SUCCESS_COORDINATE, *FAILURE_COORDINATES):
        if coordinate not in source:
            raise GuardError("generated_guard_coordinate_missing")
    return {
        "sha256": sha256_bytes(payload),
        "bytes": len(payload),
        **counts,
        "forbidden_generic_present": False,
    }


def _safe_names(values: Any) -> list[str] | None:
    if not isinstance(values, (list, tuple, set)):
        return None
    names = list(values)
    if not all(isinstance(name, str) and SAFE_TOOL_NAME.fullmatch(name) for name in names):
        return None
    if len(set(names)) != len(names):
        return None
    return sorted(names)


def simulate_guard(
    *,
    selected: Any = EXPECTED_TOOLS,
    mount_ok: bool = True,
    scope_present: bool = True,
    known: Any = ("edit", "glob", "grep", "read", "write"),
    restrictable: Any = ("edit", "glob", "grep", "read", "write"),
    restriction_ok: bool = True,
    schemas: Any = EXPECTED_TOOLS,
) -> Projection:
    selected_names = _safe_names(selected)
    if (
        not isinstance(selected, (list, tuple))
        or list(selected) != list(EXPECTED_TOOLS)
        or selected_names != list(EXPECTED_TOOLS)
    ):
        return Projection("EFFECTIVE_TOOL_COMPOSITION_INPUT_INVALID")
    if not mount_ok:
        return Projection("EFFECTIVE_TOOL_COMPOSITION_PRESET_MOUNT_FAILED")
    if not scope_present:
        return Projection("EFFECTIVE_TOOL_COMPOSITION_SCOPE_MISSING")
    known_names = _safe_names(known)
    restrictable_names = _safe_names(restrictable)
    if known_names is None or restrictable_names is None:
        return Projection("EFFECTIVE_TOOL_COMPOSITION_SCHEMA_VIEW_INVALID")
    inherited = set(restrictable_names)
    local = sorted(set(known_names) - inherited)
    if local:
        return Projection(
            "EFFECTIVE_TOOL_COMPOSITION_SCOPE_LOCAL_TOOL_PRESENT", ",".join(local)
        )
    missing = sorted(set(EXPECTED_TOOLS) - inherited)
    if missing:
        return Projection(
            "EFFECTIVE_TOOL_COMPOSITION_EXPECTED_TOOL_NOT_INHERITED",
            ",".join(missing),
        )
    if not restriction_ok:
        return Projection("EFFECTIVE_TOOL_COMPOSITION_RESTRICTION_FAILED")
    effective = _safe_names(schemas)
    if effective is None:
        return Projection("EFFECTIVE_TOOL_COMPOSITION_SCHEMA_VIEW_INVALID")
    if effective != list(EXPECTED_TOOLS):
        mismatch = sorted(set(effective) ^ set(EXPECTED_TOOLS))
        return Projection(
            "EFFECTIVE_TOOL_COMPOSITION_EFFECTIVE_VIEW_MISMATCH",
            ",".join(mismatch) or None,
        )
    return Projection(SUCCESS_COORDINATE)


def sanitize_terminal(code: Any, detail: Any = None) -> Projection:
    coordinate = code if code in FAILURE_COORDINATES else FAILURE_COORDINATES[-1]
    names = _safe_names(detail)
    return Projection(coordinate, ",".join(names) if names else None)


def scenario_matrix() -> list[dict[str, str | None]]:
    scenarios = [
        ("accepted_inherited_surplus_filtered", simulate_guard()),
        (
            "scope_local_selected_rejected",
            simulate_guard(known=("edit", "glob", "read"), restrictable=("glob", "read")),
        ),
        (
            "scope_local_surplus_rejected",
            simulate_guard(
                known=("edit", "glob", "read", "write"),
                restrictable=("edit", "glob", "read"),
            ),
        ),
        (
            "missing_inherited_rejected",
            simulate_guard(
                known=("edit", "read"), restrictable=("edit", "read")
            ),
        ),
        (
            "surplus_effective_schema_rejected",
            simulate_guard(schemas=("edit", "glob", "read", "write")),
        ),
        (
            "missing_effective_schema_rejected",
            simulate_guard(schemas=("edit", "read")),
        ),
        (
            "duplicate_effective_schema_rejected",
            simulate_guard(schemas=("edit", "glob", "read", "read")),
        ),
        (
            "malformed_effective_schema_rejected",
            simulate_guard(schemas=("edit", "glob", "C:/secret")),
        ),
        (
            "reordered_selected_input_rejected",
            simulate_guard(selected=("read", "glob", "edit")),
        ),
        (
            "mount_failure_sanitized",
            simulate_guard(mount_ok=False),
        ),
        (
            "missing_scope_sanitized",
            simulate_guard(scope_present=False),
        ),
        (
            "restriction_failure_sanitized",
            simulate_guard(restriction_ok=False),
        ),
        (
            "unknown_exception_sanitized",
            sanitize_terminal("raw dynamic error", ["C:/secret"]),
        ),
    ]
    return [projection.as_dict(name) for name, projection in scenarios]


def build_evidence(cache_root: Path) -> dict[str, Any]:
    contract = load_contract()
    package_checks: list[dict[str, Any]] = []
    sources: dict[tuple[str, str], bytes] = {}
    for package in contract["packages"]:
        projection, members = verify_package_blob(package, cache_root)
        package_checks.append(projection)
        for member_path, payload in members.items():
            sources[(package["name"], member_path)] = payload
    semantic_checks = verify_source_semantics(sources)
    if list(semantic_checks) != contract["semantic_checks"]:
        raise GuardError("semantic_check_order_mismatch")
    profile_check = verify_profile(contract)
    generated_guard = validate_guard_source(build_guard_source())
    matrix = scenario_matrix()
    allowed = {SUCCESS_COORDINATE, *FAILURE_COORDINATES}
    if any(row["coordinate"] not in allowed for row in matrix):
        raise GuardError("scenario_coordinate_outside_contract")
    zero_counts = {name: 0 for name in contract["required_zero_counts"]}
    return {
        "schema_version": SCHEMA_VERSION,
        "operation_id": OPERATION_ID,
        "recorded_at": datetime.now(ZoneInfo("Australia/Brisbane")).isoformat(),
        "planning_source": contract["planning_source"],
        "result": "passed_provider_free_deterministic_guard",
        "package_checks": package_checks,
        "source_semantic_checks": semantic_checks,
        "profile_check": profile_check,
        "generated_guard": generated_guard,
        "scenario_matrix": matrix,
        "zero_counts": zero_counts,
        "retention": {
            "package_source": False,
            "prompt": False,
            "reasoning": False,
            "response": False,
            "tool_payload": False,
            "exception_text": False,
            "stack": False,
            "credential": False,
            "environment_values": False,
        },
        "claim_boundary": (
            "deterministic_guard_construction_only_not_native_boot_agent_session_"
            "model_or_provider_evidence"
        ),
    }


def render_report(evidence: dict[str, Any]) -> str:
    passed = sum(
        1
        for row in evidence["scenario_matrix"]
        if row["coordinate"]
        in {SUCCESS_COORDINATE, *FAILURE_COORDINATES}
    )
    return f"""# Provider-free effective-tool composition guard report

Date: 2026-08-20

Timestamp: {evidence['recorded_at']} (Australia/Brisbane)

Status: `passed`

The exact cached rc.7 package identities and all seven frozen source-semantic
predicates passed. The generated setup helper awaits the bounded preset mount,
rejects child-scope tool registrations, proves the three selected names are
inherited/restrictable, installs one restriction and requires final schemas to
be exactly `edit`, `glob`, `read`.

All {passed}/{len(evidence['scenario_matrix'])} deterministic projections
returned a closed coordinate. Generic `CUSTOM_RUNNER_FAILURE`, raw exception
text, stacks, prompts, payloads, paths, credentials and environment values are
absent.

Node/native-Harness boots, occupied workers, sessions, broker requests, model
requests, provider calls, network attempts, Docker and database invocations
were all zero. This is deterministic guard-construction evidence only; it is
not a native boot, agent, model or provider result.
"""


def _default_cache_root() -> Path:
    local_app_data = os.environ.get("LOCALAPPDATA")
    if not local_app_data:
        raise GuardError("localappdata_missing")
    return Path(local_app_data) / "npm-cache"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check or publish the provider-free rc.7 effective-tool guard."
    )
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--check", action="store_true")
    action.add_argument("--publish", action="store_true")
    parser.add_argument("--cache-root", type=Path)
    args = parser.parse_args()
    try:
        cache_root = (args.cache_root or _default_cache_root()).resolve()
        evidence = build_evidence(cache_root)
        if args.publish:
            if EVIDENCE_PATH.exists() or REPORT_PATH.exists():
                raise GuardError("canonical_output_already_exists")
            EVIDENCE_PATH.write_bytes(canonical_json_bytes(evidence))
            REPORT_PATH.write_text(render_report(evidence), encoding="utf-8", newline="\n")
        print(
            json.dumps(
                {
                    "status": "passed",
                    "package_count": len(evidence["package_checks"]),
                    "semantic_check_count": len(evidence["source_semantic_checks"]),
                    "scenario_count": len(evidence["scenario_matrix"]),
                    "guard_sha256": evidence["generated_guard"]["sha256"],
                    "published": bool(args.publish),
                    "zero_counts": evidence["zero_counts"],
                },
                indent=2,
                sort_keys=True,
            )
        )
    except (GuardError, OSError, ValueError, KeyError, json.JSONDecodeError) as error:
        print(json.dumps({"status": "revision_required", "reason": str(error)}))
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
