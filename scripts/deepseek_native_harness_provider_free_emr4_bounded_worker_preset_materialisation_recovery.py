"""Materialise and prove the bounded rc.7 worker preset without starting Harness."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
from typing import Any

import yaml

from scripts.deepseek_native_harness_provider_free_required_service_injection_recovery import (
    ServiceInjectionRecoveryError,
    verify_package,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
OPERATION_ID = (
    "deepseek-native-harness-provider-free-emr4-bounded-worker-preset-"
    "materialisation-recovery"
)
ROOT = REPO_ROOT / "orchestration" / "continuity" / OPERATION_ID
CONTRACT_PATH = ROOT / "contract.json"
CONTRACT_SCHEMA_PATH = ROOT / "contract.schema.json"
EVIDENCE_SCHEMA_PATH = ROOT / "evidence.schema.json"
EVIDENCE_PATH = ROOT / "provider-free-emr4-bounded-worker-preset-evidence.json"
REPORT_PATH = ROOT / "provider-free-emr4-bounded-worker-preset-report.md"
MATERIALISED_PATH = (
    ROOT
    / "materialised-home"
    / ".agent-presets"
    / "emr4-bounded-worker"
    / "agent.cordis.yml"
)
PLAN_PATH = (
    REPO_ROOT
    / "docs"
    / "deepseek-native-harness-provider-free-emr4-bounded-worker-preset-"
    "materialisation-recovery-plan.md"
)
CONTROLLER_PATH = Path(__file__).resolve()
FOCUSED_TEST_PATH = (
    REPO_ROOT
    / "tests"
    / "test_deepseek_native_harness_provider_free_emr4_bounded_worker_preset_"
    "materialisation_recovery.py"
)
REQUIRED_SERVICE_ROOT = (
    REPO_ROOT
    / "orchestration"
    / "continuity"
    / "deepseek-native-harness-provider-free-required-service-injection-recovery"
)
GUARD_ROOT = (
    REPO_ROOT
    / "orchestration"
    / "continuity"
    / "deepseek-native-harness-provider-free-effective-tool-composition-and-"
    "terminal-coordinate-guard"
)
CONTRACT_SCHEMA = (
    "ariadne.deepseek_native_harness_emr4_bounded_worker_preset_contract.v1"
)
EVIDENCE_SCHEMA = (
    "ariadne.deepseek_native_harness_emr4_bounded_worker_preset_evidence.v1"
)
HEX_40 = re.compile(r"^[0-9a-f]{40}$")
HEX_64 = re.compile(r"^[0-9a-f]{64}$")
PRESET_ID = "emr4-bounded-worker"
PRESET_RELATIVE_PATH = (
    ".agent-presets/emr4-bounded-worker/agent.cordis.yml"
)
SELECTED_TOOLS = ("edit", "glob", "read")
UNCONDITIONAL_TOOLS = ("edit", "glob", "grep", "read", "write")
CONDITIONAL_TOOLS = ("read_image",)
PRESET_BYTES = b"""- id: tool-fs
  name: '@deepseek-ai/dsh-tool-fs'
- id: tool-fs-search
  name: '@deepseek-ai/dsh-tool-fs-search'
  config:
    sampleOverCapGlobResults: false
"""
EXPECTED_ROWS: list[dict[str, Any]] = [
    {"id": "tool-fs", "name": "@deepseek-ai/dsh-tool-fs"},
    {
        "id": "tool-fs-search",
        "name": "@deepseek-ai/dsh-tool-fs-search",
        "config": {"sampleOverCapGlobResults": False},
    },
]


class PresetMaterialisationError(RuntimeError):
    """A closed deterministic preset-materialisation check failed."""


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        + "\n"
    ).encode("utf-8")


def load_contract(path: Path = CONTRACT_PATH) -> dict[str, Any]:
    contract = json.loads(path.read_text(encoding="utf-8"))
    if contract.get("schema_version") != CONTRACT_SCHEMA:
        raise PresetMaterialisationError("contract_schema_mismatch")
    if contract.get("operation_id") != OPERATION_ID:
        raise PresetMaterialisationError("contract_operation_mismatch")
    for field in ("planning_source",):
        if HEX_40.fullmatch(str(contract.get(field, ""))) is None:
            raise PresetMaterialisationError(f"contract_full_git_id_required:{field}")
    accepted = contract.get("accepted_sources", {})
    if set(accepted) != {"effective_tool_guard", "required_service_recovery"}:
        raise PresetMaterialisationError("contract_accepted_source_keys_mismatch")
    for field, value in accepted.items():
        if HEX_40.fullmatch(str(value)) is None:
            raise PresetMaterialisationError(
                f"contract_full_git_id_required:accepted_sources.{field}"
            )
    predecessor_packages = contract.get("predecessor_package_names")
    if predecessor_packages != [
        "@deepseek-ai/dsh-base",
        "@deepseek-ai/dsh-headless",
        "@deepseek-ai/dsh-agent-presets",
        "@deepseek-ai/dsh-tools",
    ]:
        raise PresetMaterialisationError("predecessor_package_names_mismatch")
    packages = contract.get("packages")
    if not isinstance(packages, list) or [row.get("name") for row in packages] != [
        "@deepseek-ai/dsh-tool-fs",
        "@deepseek-ai/dsh-tool-fs-search",
    ]:
        raise PresetMaterialisationError("new_package_order_mismatch")
    preset = contract.get("preset", {})
    if preset != {
        "id": PRESET_ID,
        "install_relative_path": PRESET_RELATIVE_PATH,
        "materialised_repository_path": MATERIALISED_PATH.relative_to(
            REPO_ROOT
        ).as_posix(),
        "rows": EXPECTED_ROWS,
        "selected_tools": list(SELECTED_TOOLS),
        "unconditional_inherited_tools": list(UNCONDITIONAL_TOOLS),
        "conditional_inherited_tools": list(CONDITIONAL_TOOLS),
    }:
        raise PresetMaterialisationError("contract_preset_mismatch")
    for field, digest in contract.get("implementation_bytes", {}).items():
        if HEX_64.fullmatch(str(digest)) is None:
            raise PresetMaterialisationError(
                f"contract_implementation_digest_invalid:{field}"
            )
    expected_zero = [
        "agent_sessions",
        "broker_requests",
        "database_invocations",
        "docker_invocations",
        "model_requests",
        "native_harness_processes",
        "network_attempts",
        "node_processes",
        "occupied_workers",
        "provider_requests",
        "turns",
    ]
    if contract.get("required_zero_counts") != expected_zero:
        raise PresetMaterialisationError("required_zero_counts_mismatch")
    return contract


def default_cache_root() -> Path:
    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        return Path(local_app_data) / "npm-cache"
    for parent in REPO_ROOT.parents:
        candidate = parent / "AppData" / "Local" / "npm-cache"
        if candidate.is_dir() and not candidate.is_symlink():
            return candidate
    raise PresetMaterialisationError("localappdata_and_repo_owner_cache_missing")


def _validate_file_bindings(rows: list[dict[str, Any]]) -> list[dict[str, str]]:
    actual_rows: list[dict[str, str]] = []
    for row in rows:
        relative = row.get("path")
        digest = row.get("sha256")
        if not isinstance(relative, str) or HEX_64.fullmatch(str(digest)) is None:
            raise PresetMaterialisationError("predecessor_file_binding_invalid")
        path = REPO_ROOT / relative
        if not path.is_file() or path.is_symlink():
            raise PresetMaterialisationError(
                f"predecessor_file_missing_or_unsafe:{relative}"
            )
        actual = sha256_file(path)
        if actual != digest:
            raise PresetMaterialisationError(
                f"predecessor_file_digest_mismatch:{relative}"
            )
        actual_rows.append({"path": relative, "sha256": actual})
    return actual_rows


def _validate_immutable_attempts(
    required_evidence: dict[str, Any],
) -> list[dict[str, Any]]:
    attempts = required_evidence.get("immutable_attempts")
    if not isinstance(attempts, list) or len(attempts) != 2:
        raise PresetMaterialisationError("immutable_attempt_count_mismatch")
    result: list[dict[str, Any]] = []
    for attempt in attempts:
        if (
            HEX_40.fullmatch(str(attempt.get("source", ""))) is None
            or attempt.get("result") != "fail"
            or attempt.get("unchanged") is not True
        ):
            raise PresetMaterialisationError("immutable_attempt_binding_invalid")
        files = _validate_file_bindings(attempt.get("files", []))
        evidence_item = next(
            (item for item in attempt["files"] if item["path"].endswith("evidence.json")),
            None,
        )
        if evidence_item is None:
            raise PresetMaterialisationError("immutable_attempt_evidence_missing")
        retained = json.loads(
            (REPO_ROOT / evidence_item["path"]).read_text(encoding="utf-8")
        )
        if (
            retained.get("attempt_id") != attempt.get("attempt_id")
            or retained.get("result") != "fail"
        ):
            raise PresetMaterialisationError("immutable_attempt_terminal_mismatch")
        result.append(
            {
                "attempt_id": attempt["attempt_id"],
                "source": attempt["source"],
                "result": "fail",
                "unchanged": True,
                "files": files,
            }
        )
    return result


def validate_predecessors(contract: dict[str, Any]) -> dict[str, Any]:
    files = _validate_file_bindings(contract["predecessor_files"])
    required_contract = json.loads(
        (REQUIRED_SERVICE_ROOT / "contract.json").read_text(encoding="utf-8")
    )
    required_evidence = json.loads(
        (
            REQUIRED_SERVICE_ROOT
            / "provider-free-required-service-injection-evidence.json"
        ).read_text(encoding="utf-8")
    )
    guard_contract = json.loads(
        (GUARD_ROOT / "contract.json").read_text(encoding="utf-8")
    )
    guard_evidence = json.loads(
        (GUARD_ROOT / "provider-free-effective-tool-guard-evidence.json").read_text(
            encoding="utf-8"
        )
    )
    if required_evidence.get("result") != "pass":
        raise PresetMaterialisationError("required_service_predecessor_not_passed")
    future = required_evidence.get("future_declaration", {})
    if (
        future.get("selected_profile") != PRESET_ID
        or future.get("selected_profile_materialised") is not False
        or required_evidence.get("claim_boundary", {}).get("successor") != OPERATION_ID
    ):
        raise PresetMaterialisationError("required_service_successor_binding_mismatch")
    if guard_evidence.get("result") != "passed_provider_free_deterministic_guard":
        raise PresetMaterialisationError("effective_tool_guard_not_passed")
    guard = guard_contract.get("guard", {})
    if (
        guard.get("preset_id") != PRESET_ID
        or guard.get("selected_tools") != list(SELECTED_TOOLS)
        or guard_evidence.get("profile_check", {}).get("selected_profile")
        != PRESET_ID
        or guard_evidence.get("profile_check", {}).get("selected_tools")
        != list(SELECTED_TOOLS)
    ):
        raise PresetMaterialisationError("effective_tool_guard_binding_mismatch")
    immutable = _validate_immutable_attempts(required_evidence)
    by_name = {row["name"]: row for row in required_contract["packages"]}
    names = contract["predecessor_package_names"]
    if any(name not in by_name for name in names):
        raise PresetMaterialisationError("predecessor_package_spec_missing")
    return {
        "files": files,
        "package_specs": [by_name[name] for name in names],
        "immutable_attempts": immutable,
        "required_service_result": "pass",
        "effective_tool_guard_result": "pass",
        "guard_source_semantics": guard_evidence["source_semantic_checks"],
    }


def _contains_once(source: str, token: str) -> bool:
    return source.count(token) == 1


def inspect_source_semantics(
    sources: dict[tuple[str, str], bytes],
) -> dict[str, Any]:
    base = sources[("@deepseek-ai/dsh-base", "cordis.patch.yml")].decode()
    headless = sources[("@deepseek-ai/dsh-headless", "cordis.patch.yml")].decode()
    presets = sources[("@deepseek-ai/dsh-agent-presets", "lib/index.js")].decode()
    tools = sources[("@deepseek-ai/dsh-tools", "lib/index.js")].decode()
    tool_fs = sources[("@deepseek-ai/dsh-tool-fs", "lib/index.js")].decode()
    tool_search = sources[
        ("@deepseek-ai/dsh-tool-fs-search", "lib/index.js")
    ].decode()
    checks = {
        "preset_id_grammar_exact": (
            "const PRESET_ID = /^[a-z0-9][a-z0-9-]*$/;" in presets
        ),
        "preset_user_root_exact": (
            'const USER_PRESET_DIR = ".agent-presets";' in presets
            and "dshHomePath(USER_PRESET_DIR)" in presets
            and "includeUserRoot: z.boolean().default(true)" in presets
        ),
        "preset_composition_filename_exact": (
            'const COMPOSITION_FILE = "agent.cordis.yml";' in presets
        ),
        "preset_top_level_rows_required": (
            '"the composition must be a top-level list of plugin rows"' in presets
        ),
        "preset_invalid_composition_broken": (
            "const broken = await isFile(path) ? await compositionProblem(path)"
            in presets
        ),
        "preset_first_root_wins": (
            "if (byId.has(preset.id)) continue;" in presets
        ),
        "preset_mount_resolves_before_standing": (
            "const preset = await this.resolveMountable(id);\n"
            "\t\tconst standing = await this.ensureStanding(preset);" in presets
        ),
        "preset_mount_binds_standing_parent": (
            "this.bindings.set(agentKey, bindScopeParent(agentKey, standing.key));"
            in presets
        ),
        "base_required_provider_rows_present": all(
            token in base
            for token in (
                "    - id: subprocess\n      name: '@deepseek-ai/dsh-subprocess-local'",
                "    - id: tools\n      name: '@deepseek-ai/dsh-tools'",
                "    - id: system-prompt\n      name: '@deepseek-ai/dsh-system-prompt'",
                "    - id: fs-sandbox\n      name: '@deepseek-ai/dsh-fs-sandbox'",
            )
        ),
        "headless_does_not_disable_required_provider_rows": all(
            f"- id: {row}\n  disabled: true" not in headless
            for row in ("subprocess", "tools", "system-prompt", "fs-sandbox")
        ),
        "tools_service_and_restriction_source_exact": (
            'super(ctx, "tools")' in tools
            and "restrictableNames" in tools
            and "tools.restrict() names unknown global tool" in tools
        ),
        "tool_fs_plugin_name_exact": 'const name = "tool-fs";' in tool_fs,
        "tool_fs_inject_exact": (
            'const inject = [\n\t"tools",\n\t"fs",\n\t"systemPrompt"\n];'
            in tool_fs
        ),
        "tool_fs_mandatory_registrations_exact": all(
            _contains_once(tool_fs, f'name: "{name}"')
            for name in ("read", "write", "edit")
        ),
        "tool_fs_conditional_read_image_exact": (
            _contains_once(tool_fs, 'name: "read_image"')
            and 'ctx.inject(["attachments"], (imageCtx) =>' in tool_fs
            and "applyReadImageTool(imageCtx);" in tool_fs
        ),
        "tool_search_plugin_name_exact": (
            'const name = "tool-fs-search";' in tool_search
        ),
        "tool_search_inject_exact": (
            'const inject = [\n\t"tools",\n\t"systemPrompt",\n\t"subprocess"\n];'
            in tool_search
        ),
        "tool_search_requires_sampling_boolean": (
            "sampleOverCapGlobResults: z.boolean().required()" in tool_search
        ),
        "tool_search_registrations_exact": all(
            _contains_once(tool_search, f'name: "{name}"')
            for name in ("glob", "grep")
        ),
    }
    if not all(checks.values()):
        failed = sorted(name for name, passed in checks.items() if not passed)
        raise PresetMaterialisationError(
            "source_semantic_check_failed:" + ",".join(failed)
        )
    return {
        "checks": checks,
        "mandatory_selected_sources": {
            "edit": "@deepseek-ai/dsh-tool-fs",
            "glob": "@deepseek-ai/dsh-tool-fs-search",
            "read": "@deepseek-ai/dsh-tool-fs",
        },
        "unconditional_inherited_tools": list(UNCONDITIONAL_TOOLS),
        "conditional_inherited_tools": list(CONDITIONAL_TOOLS),
        "preset_is_authority_boundary": False,
        "accepted_guard_remains_mandatory": True,
        "outer_broker_allowlist_remains_mandatory": True,
    }


def validate_preset_relative_path(value: str) -> str:
    path = PurePosixPath(value)
    if (
        value != PRESET_RELATIVE_PATH
        or path.is_absolute()
        or ".." in path.parts
        or path.parts
        != (".agent-presets", PRESET_ID, "agent.cordis.yml")
        or re.fullmatch(r"[a-z0-9][a-z0-9-]*", path.parts[1]) is None
    ):
        raise PresetMaterialisationError("preset_relative_path_invalid")
    return value


def validate_preset_bytes(payload: bytes) -> dict[str, Any]:
    if payload != PRESET_BYTES:
        raise PresetMaterialisationError("preset_bytes_mismatch")
    if payload.startswith(b"\xef\xbb\xbf") or b"\r" in payload:
        raise PresetMaterialisationError("preset_encoding_or_newline_invalid")
    if any(token in payload for token in (b"!!", b"&", b"*", b"${")):
        raise PresetMaterialisationError("preset_dynamic_yaml_forbidden")
    try:
        rows = yaml.safe_load(payload)
    except yaml.YAMLError as error:
        raise PresetMaterialisationError("preset_yaml_invalid") from error
    if rows != EXPECTED_ROWS:
        raise PresetMaterialisationError("preset_rows_mismatch")
    if [list(row) for row in rows] != [["id", "name"], ["id", "name", "config"]]:
        raise PresetMaterialisationError("preset_key_order_mismatch")
    return {
        "id": PRESET_ID,
        "install_relative_path": validate_preset_relative_path(PRESET_RELATIVE_PATH),
        "repository_path": MATERIALISED_PATH.relative_to(REPO_ROOT).as_posix(),
        "bytes": len(payload),
        "sha256": sha256_bytes(payload),
        "row_ids": [row["id"] for row in rows],
        "row_count": len(rows),
        "sample_over_cap_glob_results": rows[1]["config"][
            "sampleOverCapGlobResults"
        ],
    }


def project_effective_tools(
    inherited: list[str],
    selected: list[str] | None = None,
    local: list[str] | None = None,
) -> list[str]:
    chosen = selected if selected is not None else list(SELECTED_TOOLS)
    own = local if local is not None else []
    if chosen != list(SELECTED_TOOLS) or len(chosen) != len(set(chosen)):
        raise PresetMaterialisationError("selected_tools_invalid")
    if own:
        raise PresetMaterialisationError("scope_local_tools_forbidden")
    if any(not isinstance(name, str) or re.fullmatch(r"[a-z_]+", name) is None for name in inherited):
        raise PresetMaterialisationError("inherited_tool_name_invalid")
    if not set(SELECTED_TOOLS).issubset(inherited):
        raise PresetMaterialisationError("selected_tool_not_inherited")
    return list(SELECTED_TOOLS)


def hostile_variant_results() -> list[dict[str, Any]]:
    variants: list[tuple[str, bytes]] = [
        ("missing_fs_row", PRESET_BYTES.split(b"- id: tool-fs-search", 1)[1]),
        ("missing_search_row", PRESET_BYTES.split(b"- id: tool-fs-search", 1)[0]),
        (
            "duplicate_fs_row",
            PRESET_BYTES.replace(b"- id: tool-fs-search", b"- id: tool-fs"),
        ),
        (
            "reordered_rows",
            b"""- id: tool-fs-search
  name: '@deepseek-ai/dsh-tool-fs-search'
  config:
    sampleOverCapGlobResults: false
- id: tool-fs
  name: '@deepseek-ai/dsh-tool-fs'
""",
        ),
        ("renamed_plugin", PRESET_BYTES.replace(b"dsh-tool-fs'", b"dsh-tool-x'", 1)),
        ("surplus_row", PRESET_BYTES + b"- id: shell\n  name: shell\n"),
        ("group_row", PRESET_BYTES.replace(b"  name:", b"  group: true\n  name:", 1)),
        ("unexpected_config", PRESET_BYTES.replace(b"- id: tool-fs\n", b"- id: tool-fs\n  config: {}\n", 1)),
        ("sampling_missing", PRESET_BYTES.replace(b"    sampleOverCapGlobResults: false\n", b"")),
        ("sampling_true", PRESET_BYTES.replace(b"false", b"true")),
        ("sampling_string", PRESET_BYTES.replace(b"false", b"'false'")),
        ("dynamic_tag", PRESET_BYTES.replace(b"false", b"!!js false")),
        ("alias", PRESET_BYTES + b"- &x {id: x, name: x}\n- *x\n"),
        ("crlf", PRESET_BYTES.replace(b"\n", b"\r\n")),
        ("bom", b"\xef\xbb\xbf" + PRESET_BYTES),
    ]
    results: list[dict[str, Any]] = []
    for name, payload in variants:
        try:
            validate_preset_bytes(payload)
        except PresetMaterialisationError:
            results.append({"scenario": name, "result": "rejected"})
        else:
            raise PresetMaterialisationError(f"hostile_variant_accepted:{name}")
    path_variants = [
        "../emr4-bounded-worker/agent.cordis.yml",
        ".agent-presets/../agent.cordis.yml",
        ".agent-presets/emr4_bounded_worker/agent.cordis.yml",
        ".agent-presets/EMR4-bounded-worker/agent.cordis.yml",
        ".agent-presets/emr4-bounded-worker/agent.yml",
        "/.agent-presets/emr4-bounded-worker/agent.cordis.yml",
    ]
    for index, value in enumerate(path_variants, start=1):
        try:
            validate_preset_relative_path(value)
        except PresetMaterialisationError:
            results.append({"scenario": f"hostile_path_{index:02d}", "result": "rejected"})
        else:
            raise PresetMaterialisationError(f"hostile_path_accepted:{value}")
    return results


def validate_implementation_bytes(contract: dict[str, Any]) -> dict[str, str]:
    actual = {
        "controller_sha256": sha256_file(CONTROLLER_PATH),
        "focused_test_sha256": sha256_file(FOCUSED_TEST_PATH),
        "plan_sha256": sha256_file(PLAN_PATH),
    }
    if actual != contract["implementation_bytes"]:
        raise PresetMaterialisationError("implementation_digest_mismatch")
    return actual


def build_evidence(cache_root: Path | None = None) -> dict[str, Any]:
    contract = load_contract()
    predecessor = validate_predecessors(contract)
    resolved_cache = (cache_root or default_cache_root()).resolve()
    if not resolved_cache.is_dir() or resolved_cache.is_symlink():
        raise PresetMaterialisationError("cache_root_missing_or_unsafe")
    package_specs = [*predecessor["package_specs"], *contract["packages"]]
    package_checks: list[dict[str, Any]] = []
    sources: dict[tuple[str, str], bytes] = {}
    try:
        for package in package_specs:
            projection, members, _ = verify_package(package, resolved_cache)
            package_checks.append(projection)
            for member_path, payload in members.items():
                sources[(package["name"], member_path)] = payload
    except ServiceInjectionRecoveryError as error:
        raise PresetMaterialisationError(str(error)) from error
    semantics = inspect_source_semantics(sources)
    preset = validate_preset_bytes(PRESET_BYTES)
    minimal = project_effective_tools(list(UNCONDITIONAL_TOOLS))
    attachments = project_effective_tools(
        [*UNCONDITIONAL_TOOLS, *CONDITIONAL_TOOLS]
    )
    hostile = hostile_variant_results()
    zero_counts = {name: 0 for name in contract["required_zero_counts"]}
    return {
        "schema_version": EVIDENCE_SCHEMA,
        "operation_id": OPERATION_ID,
        "planning_source": contract["planning_source"],
        "result": "pass",
        "predecessor_bindings": {
            "accepted_sources": contract["accepted_sources"],
            "files": predecessor["files"],
            "required_service_result": predecessor["required_service_result"],
            "effective_tool_guard_result": predecessor[
                "effective_tool_guard_result"
            ],
            "immutable_attempts": predecessor["immutable_attempts"],
        },
        "package_checks": package_checks,
        "source_semantics": semantics,
        "materialised_preset": preset,
        "effective_projection": {
            "selected_tools": list(SELECTED_TOOLS),
            "minimal_inherited_tools": list(UNCONDITIONAL_TOOLS),
            "minimal_effective_tools": minimal,
            "attachment_present_inherited_tools": [
                *UNCONDITIONAL_TOOLS,
                *CONDITIONAL_TOOLS,
            ],
            "attachment_present_effective_tools": attachments,
            "guard_applied_after_mount": True,
            "guard_source_semantics": predecessor["guard_source_semantics"],
            "outer_broker_allowlist_still_required": True,
        },
        "hostile_variants": hostile,
        "provider_boundary": zero_counts,
        "implementation_bytes": validate_implementation_bytes(contract),
        "claim_boundary": {
            "proved": "exact_rc7_materialised_preset_and_deterministic_post_mount_edit_glob_read_projection",
            "not_proved": [
                "native_preset_discovery",
                "native_preset_mount",
                "combined_service_activation",
                "native_scope_creation",
                "native_effective_schema_view",
                "future_native_harness_boot",
                "occupied_deepseek_worker",
                "model_or_provider_reliability",
            ],
            "future_native_execution_authorised": False,
        },
    }


def render_report(evidence: dict[str, Any]) -> str:
    package_names = ", ".join(row["name"] for row in evidence["package_checks"])
    preset = evidence["materialised_preset"]
    hostile_count = len(evidence["hostile_variants"])
    return f"""# Provider-free emr4-bounded-worker preset materialisation report

Date: 2026-08-20

Timestamp: 2026-08-20T10:30:02.1366272+10:00 (Australia/Brisbane)

Result: **pass**

## Exact materialisation

The exact rc.7-compatible payload is retained at
`{preset['repository_path']}` and is installation-ready only for future relative
destination `{preset['install_relative_path']}`. It contains exactly the
official `tool-fs` and `tool-fs-search` rows, with
`sampleOverCapGlobResults: false`.

The preset's raw inherited surface is deliberately broader than its admitted
model-facing surface. Exact source provides unconditional `edit`, `glob`,
`grep`, `read`, `write` and conditional `read_image`. The already accepted
post-mount guard reduces both admitted inheritance cases to exactly sorted
`edit`, `glob`, `read`; the outer broker allowlist remains separately required.

## Bindings

- exact local-cache packages checked: {package_names};
- payload bytes: {preset['bytes']};
- payload SHA-256: `{preset['sha256']}`;
- hostile preset/path variants rejected: {hostile_count};
- both consumed native attempts: exact and unchanged; and
- Node, native Harness, occupied worker, agent/session/turn, broker, model,
  provider, network, Docker and database counts: all zero.

## Claim ceiling

This result does not prove live discovery, mount, combined service activation,
scope creation, a native effective-schema view, another Harness boot, an
occupied DeepSeek worker or model/provider reliability. Any native successor
requires a separately frozen one-process plan and latch.
"""


def expected_outputs(evidence: dict[str, Any]) -> dict[Path, bytes]:
    return {
        MATERIALISED_PATH: PRESET_BYTES,
        EVIDENCE_PATH: canonical_json_bytes(evidence),
        REPORT_PATH: render_report(evidence).encode("utf-8"),
    }


def _require_safe_owned_output(path: Path) -> None:
    try:
        path.relative_to(ROOT)
    except ValueError as error:
        raise PresetMaterialisationError("output_outside_operation_root") from error
    if path.exists() and (not path.is_file() or path.is_symlink()):
        raise PresetMaterialisationError(
            f"output_existing_path_unsafe:{path.relative_to(REPO_ROOT).as_posix()}"
        )
    for parent in path.parents:
        if parent == ROOT.parent:
            break
        if parent.exists() and parent.is_symlink():
            raise PresetMaterialisationError(
                f"output_parent_symlink_forbidden:{parent.relative_to(REPO_ROOT).as_posix()}"
            )


def write_outputs(outputs: dict[Path, bytes]) -> None:
    for path, payload in outputs.items():
        _require_safe_owned_output(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)


def check_outputs(outputs: dict[Path, bytes]) -> None:
    for path, expected in outputs.items():
        _require_safe_owned_output(path)
        if not path.is_file():
            raise PresetMaterialisationError(
                f"output_missing:{path.relative_to(REPO_ROOT).as_posix()}"
            )
        if path.read_bytes() != expected:
            raise PresetMaterialisationError(
                f"output_drift:{path.relative_to(REPO_ROOT).as_posix()}"
            )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Write or check the provider-free rc.7 bounded worker preset."
    )
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--check", action="store_true")
    action.add_argument("--write", action="store_true")
    parser.add_argument("--cache-root", type=Path)
    args = parser.parse_args()
    try:
        evidence = build_evidence(args.cache_root)
        outputs = expected_outputs(evidence)
        if args.write:
            write_outputs(outputs)
        check_outputs(outputs)
        print(
            json.dumps(
                {
                    "status": "passed",
                    "package_count": len(evidence["package_checks"]),
                    "preset_sha256": evidence["materialised_preset"]["sha256"],
                    "effective_tools": evidence["effective_projection"][
                        "minimal_effective_tools"
                    ],
                    "hostile_variant_count": len(evidence["hostile_variants"]),
                    "native_harness_processes": evidence["provider_boundary"][
                        "native_harness_processes"
                    ],
                    "written": bool(args.write),
                },
                sort_keys=True,
            )
        )
        return 0
    except (OSError, PresetMaterialisationError) as error:
        print(
            json.dumps(
                {"status": "revision_required", "reason": str(error)},
                sort_keys=True,
            )
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
