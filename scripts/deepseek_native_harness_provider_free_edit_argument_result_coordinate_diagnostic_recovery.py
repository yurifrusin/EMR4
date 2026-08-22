"""Exercise the real native-Harness edit stack provider-free."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
from typing import Any

import jsonschema

from orchestration_harness import git_object_resolution
from orchestration_harness import native_edit_argument_result_coordinate as coordinate
from scripts import (
    raisa_provider_free_check_in_native_harness_preset_mount_effective_tool_projection_rehearsal
    as accepted_projection,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
OPERATION_ID = (
    "deepseek-native-harness-provider-free-edit-argument-result-coordinate-"
    "diagnostic-recovery"
)
OPERATION_ROOT = REPO_ROOT / "orchestration" / "continuity" / OPERATION_ID
CONTRACT_PATH = OPERATION_ROOT / "contract.json"
CONTRACT_SCHEMA_PATH = OPERATION_ROOT / "contract.schema.json"
COORDINATE_SCHEMA_PATH = OPERATION_ROOT / "coordinate.schema.json"
EVIDENCE_SCHEMA_PATH = OPERATION_ROOT / "evidence.schema.json"
FAILURE_SCHEMA_PATH = OPERATION_ROOT / "failure-terminal.schema.json"
EVIDENCE_PATH = OPERATION_ROOT / "deterministic-evidence.json"
REPORT_PATH = OPERATION_ROOT / "deterministic-report.md"
FAILURE_PATH = OPERATION_ROOT / "failure-terminal.json"
DISPOSABLE_PARENT = Path("C:/Users/sarashera/EMR4-worktrees")
DISPOSABLE_ROOT = DISPOSABLE_PARENT / "deepseek-edit-argument-coordinate-fixture-001"

CONTRACT_SCHEMA_VERSION = (
    "ariadne.native_harness_edit_argument_result_diagnostic_contract.v1"
)
EVIDENCE_SCHEMA_VERSION = (
    "ariadne.native_harness_edit_argument_result_diagnostic_evidence.v1"
)
FIXTURE_SCHEMA_VERSION = (
    "ariadne.native_harness_real_edit_argument_result_fixture.v1"
)
FAILURE_SCHEMA_VERSION = (
    "ariadne.native_harness_edit_argument_result_diagnostic_failure.v1"
)

PACKAGE_DIRECTORIES = {
    "dsh_tools": "dsh-tools",
    "dsh_tool_fs": "dsh-tool-fs",
    "dsh_fs": "dsh-fs",
    "dsh_fs_local": "dsh-fs-local",
}

VARIANT_IDS = (
    "unique_match_success",
    "replace_all_success",
    "schema_missing_required",
    "blank_file_path",
    "empty_old_string",
    "equal_old_new",
    "missing_target",
    "literal_not_found",
    "literal_ambiguous",
)

FAILURE_CODES = frozenset(
    {
        "contract_rejected",
        "package_source_rejected",
        "accepted_runner_rejected",
        "consumed_attempt_drift",
        "fixture_root_rejected",
        "fixture_source_rejected",
        "fixture_process_failed",
        "fixture_output_rejected",
        "fixture_cleanup_failed",
        "evidence_rejected",
        "output_conflict",
        "unexpected_provider_free_failure",
    }
)


class EditArgumentDiagnosticError(RuntimeError):
    """A provider-free edit diagnostic invariant failed closed."""

    def __init__(self, code: str) -> None:
        if code not in FAILURE_CODES:
            code = "unexpected_provider_free_failure"
        self.code = code
        super().__init__(code)


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_bytes())
    if not isinstance(value, dict):
        raise ValueError("json_root_invalid")
    return value


def _file_observation(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"present": False, "bytes": None, "sha256": None}
    payload = path.read_bytes()
    return {
        "present": True,
        "bytes": len(payload),
        "sha256": sha256_bytes(payload),
    }


def _expected_state(variant_id: str) -> tuple[dict[str, Any], dict[str, Any]]:
    ordinary = b"header\nneedle\nfooter\n"
    multiple = b"needle\nmiddle\nneedle\n"
    if variant_id == "unique_match_success":
        before = ordinary
        after = b"header\nreplacement\nfooter\n"
    elif variant_id == "replace_all_success":
        before = multiple
        after = b"replacement\nmiddle\nreplacement\n"
    elif variant_id == "missing_target":
        return (
            {"present": False, "bytes": None, "sha256": None},
            {"present": False, "bytes": None, "sha256": None},
        )
    elif variant_id == "literal_ambiguous":
        before = after = multiple
    else:
        before = after = ordinary
    return (
        {
            "present": True,
            "bytes": len(before),
            "sha256": sha256_bytes(before),
        },
        {
            "present": True,
            "bytes": len(after),
            "sha256": sha256_bytes(after),
        },
    )


def _binding(path: Path, expected: dict[str, Any], code: str) -> dict[str, Any]:
    try:
        payload = path.read_bytes()
    except OSError as error:
        raise EditArgumentDiagnosticError(code) from error
    observed = {"bytes": len(payload), "sha256": sha256_bytes(payload)}
    if observed != {
        "bytes": expected["bytes"],
        "sha256": expected["sha256"],
    }:
        raise EditArgumentDiagnosticError(code)
    return observed


def validate_contract(path: Path = CONTRACT_PATH) -> dict[str, Any]:
    try:
        value = load_json(path)
        jsonschema.Draft202012Validator(load_json(CONTRACT_SCHEMA_PATH)).validate(value)
        if value["schema_version"] != CONTRACT_SCHEMA_VERSION:
            raise ValueError("contract_schema_mismatch")
        if value["operation_id"] != OPERATION_ID:
            raise ValueError("contract_operation_mismatch")
        documents = value["documentation_bindings"]
        if sha256_file(
            REPO_ROOT
            / "docs"
            / "deepseek-native-harness-provider-free-edit-argument-result-"
            "coordinate-diagnostic-recovery-plan.md"
        ) != documents["plan_sha256"]:
            raise ValueError("plan_binding_mismatch")
        if sha256_file(
            REPO_ROOT
            / "docs"
            / "security"
            / "deepseek-native-harness-provider-free-edit-argument-result-"
            "coordinate-diagnostic-recovery-threat-model-delta.md"
        ) != documents["threat_model_sha256"]:
            raise ValueError("threat_binding_mismatch")
        if value["coordinates"] != list(coordinate.COORDINATES):
            raise ValueError("coordinate_inventory_mismatch")
        variants = value["variants"]
        if tuple(row["variant_id"] for row in variants) != VARIANT_IDS:
            raise ValueError("variant_inventory_mismatch")
        for row in variants:
            success = row["expected_coordinate"].startswith("edit_success_")
            observation = {
                "result_kind": "success" if success else "error",
                "structured_error_code": row["structured_error_code"],
                "success_class": row["success_class"],
                "target_changed": success,
            }
            released = coordinate.classify_observation(observation)
            if released["coordinate"] != row["expected_coordinate"]:
                raise ValueError("variant_coordinate_mismatch")
            before, after = _expected_state(row["variant_id"])
            if (
                before["present"] != row["target_present_before"]
                or after["present"] != row["target_present_after"]
            ):
                raise ValueError("variant_presence_mismatch")
        limits = value["process_limits"]
        if limits["node_fixture_process_count"] != 1:
            raise ValueError("fixture_process_limit_invalid")
        if any(
            count != 0
            for name, count in limits.items()
            if name != "node_fixture_process_count"
        ):
            raise ValueError("provider_free_process_limits_invalid")
    except (
        OSError,
        ValueError,
        json.JSONDecodeError,
        jsonschema.ValidationError,
        coordinate.NativeEditCoordinateError,
    ) as error:
        raise EditArgumentDiagnosticError("contract_rejected") from error
    return value


def validate_package_source(contract: dict[str, Any]) -> dict[str, Any]:
    try:
        accepted_projection.validate_materialization_source(
            accepted_projection.load_contract()
        )
        packages_root = (
            accepted_projection.MATERIALIZATION_SOURCE_ROOT.resolve(strict=True)
            / "node_modules"
            / "@deepseek-ai"
        )
        results: dict[str, Any] = {}
        sources: dict[str, str] = {}
        for key, directory in PACKAGE_DIRECTORIES.items():
            package_root = packages_root / directory
            package_contract = contract["accepted_packages"][key]
            package = load_json(package_root / "package.json")
            if (
                package.get("name") != package_contract["name"]
                or package.get("version") != package_contract["version"]
            ):
                raise EditArgumentDiagnosticError("package_source_rejected")
            files = {
                relative: _binding(
                    package_root / relative,
                    expected,
                    "package_source_rejected",
                )
                for relative, expected in package_contract["files"].items()
            }
            results[key] = {
                "name": package["name"],
                "version": package["version"],
                "files": files,
            }
            sources[key] = (package_root / "lib/index.js").read_text(
                encoding="utf-8"
            )
        checks = {
            "tool_args_code_is_invalid_args": (
                '"INVALID_ARGS"' in sources["dsh_tools"]
                and "var ToolArgsError = class extends HarnessError" in sources["dsh_tools"]
            ),
            "tool_definition_validates_before_user_execute": (
                "const violations = validate(args);" in sources["dsh_tools"]
                and "return userExecute(args, exec);" in sources["dsh_tools"]
            ),
            "tool_result_routes_only_harness_error_codes": (
                "return error instanceof HarnessError ? {" in sources["dsh_tools"]
                and "code: error.code" in sources["dsh_tools"]
            ),
            "real_edit_name_exact": 'name: "edit"' in sources["dsh_tool_fs"],
            "real_edit_blank_path_constraint": (
                'throw new Error("file_path must be a non-empty string")'
                in sources["dsh_tool_fs"]
            ),
            "real_edit_empty_old_constraint": (
                'throw new Error("old_string must be a non-empty string")'
                in sources["dsh_tool_fs"]
            ),
            "real_edit_equal_pair_constraint": (
                'throw new Error("old_string and new_string must differ")'
                in sources["dsh_tool_fs"]
            ),
            "real_edit_calls_fs_edit_text": (
                "outcome = await ctx.fs.editText(target" in sources["dsh_tool_fs"]
            ),
            "fs_error_extends_harness_error": (
                "var FsError = class extends HarnessError" in sources["dsh_fs"]
            ),
            "missing_target_is_stale_version": (
                '"FS_STALE_VERSION"' in sources["dsh_fs_local"]
            ),
            "missing_literal_is_edit_not_found": (
                '"FS_EDIT_NOT_FOUND"' in sources["dsh_fs_local"]
            ),
            "ambiguous_literal_is_ambiguous_edit": (
                '"FS_AMBIGUOUS_EDIT"' in sources["dsh_fs_local"]
            ),
            "bare_local_fs_reports_no_sandbox_mode": (
                "var LocalFileSystem = class extends FileSystem"
                in sources["dsh_fs_local"]
                and "get sandboxMode() {}" in sources["dsh_fs"]
            ),
        }
        if not all(checks.values()):
            raise EditArgumentDiagnosticError("package_source_rejected")
    except EditArgumentDiagnosticError:
        raise
    except (OSError, ValueError, json.JSONDecodeError) as error:
        raise EditArgumentDiagnosticError("package_source_rejected") from error
    return {
        **results,
        "third_party_source_text_retained": False,
        "source_checks": checks,
        "packages_root": packages_root,
    }


def validate_accepted_runner_and_attempts(
    contract: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    runner = contract["accepted_future_runner"]
    try:
        resolution = git_object_resolution.resolve_commit_source(
            repo_root=REPO_ROOT,
            source_head=runner["source_commit"],
        )
        observed_runner = _binding(
            REPO_ROOT / runner["path"], runner, "accepted_runner_rejected"
        )
        attempt_results = {
            key: _binding(REPO_ROOT / value["path"], value, "consumed_attempt_drift")
            for key, value in contract["consumed_attempt_bindings"].items()
        }
        attempt_001 = load_json(
            REPO_ROOT
            / contract["consumed_attempt_bindings"]["attempt_001_rejection"]["path"]
        )
        attempt_002 = load_json(
            REPO_ROOT
            / contract["consumed_attempt_bindings"]["attempt_002_terminal"]["path"]
        )
        consumed = load_json(
            REPO_ROOT
            / contract["consumed_attempt_bindings"]["attempt_002_consumed"]["path"]
        )
        if (
            attempt_001.get("disposition")
            != "immutable_preexecution_rejection_fresh_attempt_identity_required"
            or attempt_001.get("provider_request_count") != 0
            or attempt_002.get("runner", {}).get("tool_lifecycle", {}).get("coordinate")
            != "edit_error_accept_not_concluded"
            or attempt_002.get("candidate", {}).get("admitted") is not False
            or consumed.get("state") != "consumed"
            or consumed.get("resume_permitted") is not False
        ):
            raise EditArgumentDiagnosticError("consumed_attempt_drift")
    except EditArgumentDiagnosticError:
        raise
    except (
        OSError,
        ValueError,
        json.JSONDecodeError,
        git_object_resolution.GitObjectResolutionError,
    ) as error:
        raise EditArgumentDiagnosticError("accepted_runner_rejected") from error
    return (
        {
            **observed_runner,
            "source_commit": resolution["resolved_commit"],
            "source_commit_resolved": True,
            "source_is_ancestor_of_head": resolution["source_is_ancestor_of_head"],
        },
        attempt_results,
    )


def provider_free_check() -> dict[str, Any]:
    contract = validate_contract()
    package = validate_package_source(contract)
    runner, attempts = validate_accepted_runner_and_attempts(contract)
    packages_root = package.pop("packages_root")
    source_checks = package.pop("source_checks")
    return {
        "schema_version": "ariadne.native_harness_edit_argument_result_preflight.v1",
        "status": "passed",
        "operation_id": OPERATION_ID,
        "contract_sha256": sha256_file(CONTRACT_PATH),
        "package_source": package,
        "source_checks": source_checks,
        "accepted_future_runner": runner,
        "consumed_attempt_bindings": attempts,
        "packages_root": packages_root,
    }


def _fixture_source(variants: list[dict[str, Any]], packages_root: Path) -> bytes:
    rows = [
        {"variant_id": row["variant_id"], "success_class": row["success_class"]}
        for row in variants
    ]
    encoded = json.dumps(rows, sort_keys=True, separators=(",", ":"))
    cordis_url = (packages_root / "cordis" / "lib" / "index.js").as_uri()
    tools_url = (packages_root / "dsh-tools" / "lib" / "index.js").as_uri()
    tool_fs_url = (packages_root / "dsh-tool-fs" / "lib" / "index.js").as_uri()
    fs_local_url = (packages_root / "dsh-fs-local" / "lib" / "index.js").as_uri()
    return f'''import {{ createHash }} from "node:crypto";
import {{ existsSync, mkdirSync, readFileSync, rmSync, writeFileSync }} from "node:fs";
import {{ join }} from "node:path";
import {{ Context }} from "{cordis_url}";
import {{ ToolRuntime }} from "{tools_url}";
import {{ apply as applyToolFs }} from "{tool_fs_url}";
import {{ LocalFileSystem }} from "{fs_local_url}";
const variants = {encoded};
const fixtureRoot = process.cwd();
const workspace = join(fixtureRoot, "workspace");
function digest(value) {{ return createHash("sha256").update(value).digest("hex"); }}
function state(path) {{
  if (!existsSync(path)) return {{ present: false, bytes: null, sha256: null }};
  const value = readFileSync(path);
  return {{ present: true, bytes: value.length, sha256: digest(value) }};
}}
function spec(row, target) {{
  const ordinary = "header\\nneedle\\nfooter\\n";
  const multiple = "needle\\nmiddle\\nneedle\\n";
  switch (row.variant_id) {{
    case "unique_match_success": return {{ initial: ordinary, args: {{ file_path: target, old_string: "needle", new_string: "replacement" }} }};
    case "replace_all_success": return {{ initial: multiple, args: {{ file_path: target, old_string: "needle", new_string: "replacement", replace_all: true }} }};
    case "schema_missing_required": return {{ initial: ordinary, args: {{ file_path: target, old_string: "needle" }} }};
    case "blank_file_path": return {{ initial: ordinary, args: {{ file_path: "   ", old_string: "needle", new_string: "replacement" }} }};
    case "empty_old_string": return {{ initial: ordinary, args: {{ file_path: target, old_string: "", new_string: "replacement" }} }};
    case "equal_old_new": return {{ initial: ordinary, args: {{ file_path: target, old_string: "needle", new_string: "needle" }} }};
    case "missing_target": return {{ initial: null, args: {{ file_path: target, old_string: "needle", new_string: "replacement" }} }};
    case "literal_not_found": return {{ initial: ordinary, args: {{ file_path: target, old_string: "absent", new_string: "replacement" }} }};
    case "literal_ambiguous": return {{ initial: multiple, args: {{ file_path: target, old_string: "needle", new_string: "replacement" }} }};
    default: throw new Error("VARIANT_INVALID");
  }}
}}
const ctx = new Context();
ctx.provide("systemPrompt", {{ tools() {{ return () => {{}}; }}, section() {{ return () => {{}}; }} }});
const tools = new ToolRuntime(ctx);
new LocalFileSystem(ctx, {{ cwd: fixtureRoot, diffBasisMaxBytes: 10485760 }});
applyToolFs(ctx, {{ readLimit: 2000, readMaxLineLength: 2000, readMaxBytes: 51200, readStreamMinSize: 10485760 }});
const edit = tools.get("edit");
if (!edit || edit.description !== "Edit an existing UTF-8 text file by replacing literal text.") throw new Error("REAL_EDIT_NOT_MOUNTED");
const released = [];
for (const row of variants) {{
  rmSync(workspace, {{ recursive: true, force: true }});
  mkdirSync(workspace, {{ recursive: true }});
  const target = join(workspace, `${{row.variant_id}}.txt`);
  const value = spec(row, target);
  if (value.initial !== null) writeFileSync(target, value.initial, "utf8");
  const before = state(target);
  const result = await tools.execute({{ callId: `fixture-${{row.variant_id}}`, name: "edit", arguments: value.args, signal: new AbortController().signal }});
  const after = state(target);
  const targetChanged = before.present !== after.present || before.bytes !== after.bytes || before.sha256 !== after.sha256;
  const resultKind = result.isError === true ? "error" : "success";
  const code = result.isError === true && typeof result.error?.info?.code === "string" ? result.error.info.code : null;
  released.push({{ variant_id: row.variant_id, result_kind: resultKind, structured_error_code: code, success_class: resultKind === "success" ? row.success_class : null, target_changed: targetChanged, before, after }});
}}
await ctx.fiber.dispose();
process.stdout.write(JSON.stringify({{ schema_version: "{FIXTURE_SCHEMA_VERSION}", actual_dsh_tools_runtime_imported: true, actual_dsh_tool_fs_edit_imported: true, actual_dsh_fs_local_imported: true, synthetic_edit_registration_count: 0, tool_runtime_execution_count: released.length, cordis_disposed: true, rows: released }}) + "\\n");
'''.encode("utf-8")


def _remove_exact_root(root: Path) -> bool:
    parent = DISPOSABLE_PARENT.resolve(strict=True)
    try:
        resolved = root.resolve()
    except OSError:
        return False
    if resolved.parent != parent or resolved == parent or resolved.is_symlink():
        return False
    if resolved.exists():
        shutil.rmtree(resolved)
    return not resolved.exists()


def _fixture_environment(root: Path, node: Path) -> dict[str, str]:
    temp = root / "tmp"
    temp.mkdir()
    environment = {"PATH": str(node.parent), "TEMP": str(temp), "TMP": str(temp)}
    for key in ("SystemRoot", "WINDIR", "ComSpec", "PATHEXT"):
        if key in os.environ:
            environment[key] = os.environ[key]
    return environment


def run_node_fixture(
    contract: dict[str, Any], packages_root: Path
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    node_name = shutil.which("node")
    if node_name is None:
        raise EditArgumentDiagnosticError("fixture_process_failed")
    node = Path(node_name).resolve(strict=True)
    parent = DISPOSABLE_PARENT.resolve(strict=True)
    root = DISPOSABLE_ROOT.resolve()
    if root.parent != parent or root.exists():
        raise EditArgumentDiagnosticError("fixture_root_rejected")
    source = _fixture_source(contract["variants"], packages_root)
    decoded = source.decode("utf-8")
    if (
        "tools.register(" in decoded
        or decoded.count("new ToolRuntime(ctx)") != 1
        or decoded.count("applyToolFs(ctx,") != 1
        or decoded.count("new LocalFileSystem(ctx,") != 1
    ):
        raise EditArgumentDiagnosticError("fixture_source_rejected")
    cleanup_passed = False
    completed: subprocess.CompletedProcess[bytes] | None = None
    try:
        root.mkdir()
        fixture_path = root / "fixture.mjs"
        fixture_path.write_bytes(source)
        completed = subprocess.run(
            [str(node), str(fixture_path)],
            cwd=root,
            env=_fixture_environment(root, node),
            capture_output=True,
            check=False,
            timeout=30,
        )
        if completed.returncode != 0 or completed.stderr:
            raise EditArgumentDiagnosticError("fixture_process_failed")
        output = json.loads(completed.stdout)
        if not isinstance(output, dict) or set(output) != {
            "schema_version",
            "actual_dsh_tools_runtime_imported",
            "actual_dsh_tool_fs_edit_imported",
            "actual_dsh_fs_local_imported",
            "synthetic_edit_registration_count",
            "tool_runtime_execution_count",
            "cordis_disposed",
            "rows",
        }:
            raise EditArgumentDiagnosticError("fixture_output_rejected")
        if (
            output["schema_version"] != FIXTURE_SCHEMA_VERSION
            or output["actual_dsh_tools_runtime_imported"] is not True
            or output["actual_dsh_tool_fs_edit_imported"] is not True
            or output["actual_dsh_fs_local_imported"] is not True
            or output["synthetic_edit_registration_count"] != 0
            or output["tool_runtime_execution_count"] != len(VARIANT_IDS)
            or output["cordis_disposed"] is not True
        ):
            raise EditArgumentDiagnosticError("fixture_output_rejected")
        rows = output["rows"]
        if not isinstance(rows, list) or len(rows) != len(VARIANT_IDS):
            raise EditArgumentDiagnosticError("fixture_output_rejected")
        released_rows = []
        for expected, row in zip(contract["variants"], rows, strict=True):
            if not isinstance(row, dict) or set(row) != {
                "variant_id",
                "result_kind",
                "structured_error_code",
                "success_class",
                "target_changed",
                "before",
                "after",
            }:
                raise EditArgumentDiagnosticError("fixture_output_rejected")
            if row["variant_id"] != expected["variant_id"]:
                raise EditArgumentDiagnosticError("fixture_output_rejected")
            expected_before, expected_after = _expected_state(row["variant_id"])
            if row["before"] != expected_before or row["after"] != expected_after:
                raise EditArgumentDiagnosticError("fixture_output_rejected")
            observation = {
                "result_kind": row["result_kind"],
                "structured_error_code": row["structured_error_code"],
                "success_class": row["success_class"],
                "target_changed": row["target_changed"],
            }
            released = coordinate.classify_observation(observation)
            coordinate.validate_coordinate(released)
            jsonschema.Draft202012Validator(
                load_json(COORDINATE_SCHEMA_PATH)
            ).validate(released)
            if (
                released["coordinate"] != expected["expected_coordinate"]
                or released["structured_error_code"]
                != expected["structured_error_code"]
            ):
                raise EditArgumentDiagnosticError("fixture_output_rejected")
            released_rows.append(
                {"variant_id": row["variant_id"], **released, "before": row["before"], "after": row["after"]}
            )
    except EditArgumentDiagnosticError:
        raise
    except (
        OSError,
        ValueError,
        json.JSONDecodeError,
        jsonschema.ValidationError,
        subprocess.SubprocessError,
        coordinate.NativeEditCoordinateError,
    ) as error:
        raise EditArgumentDiagnosticError("fixture_output_rejected") from error
    finally:
        cleanup_passed = _remove_exact_root(root)
    if not cleanup_passed or root.exists():
        raise EditArgumentDiagnosticError("fixture_cleanup_failed")
    assert completed is not None
    return released_rows, {
        "node_fixture_process_count": 1,
        "actual_dsh_tools_runtime_imported": True,
        "actual_dsh_tool_fs_edit_imported": True,
        "actual_dsh_fs_local_imported": True,
        "synthetic_edit_registration_count": 0,
        "tool_runtime_execution_count": len(VARIANT_IDS),
        "cordis_disposed": True,
        "exit_code": completed.returncode,
        "stdout_bytes": len(completed.stdout),
        "stdout_sha256": sha256_bytes(completed.stdout),
        "stderr_bytes": len(completed.stderr),
        "stderr_sha256": sha256_bytes(completed.stderr),
        "owned_process_absent": True,
        "disposable_root_absent": True,
    }


def _write_exact(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != payload:
            raise EditArgumentDiagnosticError("output_conflict")
        return
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(payload)


def _render_report(evidence: dict[str, Any]) -> str:
    rows = "\n".join(
        f"- `{row['variant_id']}` -> `{row['coordinate']}`"
        for row in evidence["variants"]
    )
    return f"""# Provider-free real edit argument/result coordinate report

Status: passed

Result: `{evidence['result']}`

The one local Node fixture mounted the exact accepted rc.7 `ToolRuntime`, real
`dsh-tool-fs` edit definition and bare `LocalFileSystem`. It made no Harness
worker, model, provider, broker, network, database or Docker request.

## Closed readings

{rows}

All successful variants produced their exact expected synthetic hash transition.
Every failed variant left its synthetic target state unchanged. No raw argument,
content, error, stack, prompt, response, reasoning, session, environment or
credential material was retained, and the exact disposable root was removed.

The consumed occupied error remains `edit_error_accept_not_concluded`; its lost
arguments cannot honestly be reconstructed. A future runner can now release the
narrower tested edit-result coordinate without parsing error prose.
"""


def execute() -> dict[str, Any]:
    preflight = provider_free_check()
    contract = validate_contract()
    rows, fixture = run_node_fixture(contract, preflight.pop("packages_root"))
    evidence = {
        "schema_version": EVIDENCE_SCHEMA_VERSION,
        "status": "passed",
        "result": "real_edit_argument_result_coordinate_diagnostic_pass",
        "operation_id": OPERATION_ID,
        "evidence_label": contract["evidence_label"],
        "contract_sha256": preflight["contract_sha256"],
        "package_source": preflight["package_source"],
        "source_checks": preflight["source_checks"],
        "accepted_future_runner": preflight["accepted_future_runner"],
        "consumed_attempt_bindings": preflight["consumed_attempt_bindings"],
        "variants": rows,
        "process_counts": dict(contract["process_limits"]),
        "fixture": fixture,
        "cleanup": {
            "owned_process_absent": True,
            "disposable_root_absent": True,
            "credentials_present_in_fixture_environment": False,
            "raw_arguments_content_error_stack_retained": False,
            "raw_prompt_response_reasoning_session_environment_retained": False,
        },
    }
    try:
        jsonschema.Draft202012Validator(load_json(EVIDENCE_SCHEMA_PATH)).validate(
            evidence
        )
    except (OSError, json.JSONDecodeError, jsonschema.ValidationError) as error:
        raise EditArgumentDiagnosticError("evidence_rejected") from error
    _write_exact(EVIDENCE_PATH, canonical_bytes(evidence))
    _write_exact(REPORT_PATH, _render_report(evidence).encode("utf-8"))
    return evidence


def write_failure_terminal(code: str) -> dict[str, Any]:
    value = {
        "schema_version": FAILURE_SCHEMA_VERSION,
        "status": "failed_closed",
        "operation_id": OPERATION_ID,
        "failure_coordinate": code
        if code in FAILURE_CODES
        else "unexpected_provider_free_failure",
        "native_harness_process_count": 0,
        "worker_process_count": 0,
        "model_request_count": 0,
        "provider_request_count": 0,
        "broker_process_count": 0,
        "network_attempt_count": 0,
        "database_attempt_count": 0,
        "docker_attempt_count": 0,
        "retry_count": 0,
        "resume_count": 0,
        "fallback_count": 0,
        "disposable_root_absent": not DISPOSABLE_ROOT.exists(),
        "raw_sensitive_material_retained": False,
    }
    try:
        jsonschema.Draft202012Validator(load_json(FAILURE_SCHEMA_PATH)).validate(value)
        _write_exact(FAILURE_PATH, canonical_bytes(value))
    except (
        OSError,
        json.JSONDecodeError,
        jsonschema.ValidationError,
        EditArgumentDiagnosticError,
    ):
        pass
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_mutually_exclusive_group(required=True)
    actions.add_argument("--check", action="store_true")
    actions.add_argument("--run", action="store_true")
    args = parser.parse_args()
    try:
        value = provider_free_check() if args.check else execute()
        print(json.dumps({"status": value["status"], "operation_id": OPERATION_ID}))
        return 0
    except EditArgumentDiagnosticError as error:
        terminal = write_failure_terminal(error.code)
        print(
            json.dumps(
                {"status": terminal["status"], "error": terminal["failure_coordinate"]}
            )
        )
        return 1
    except Exception:
        terminal = write_failure_terminal("unexpected_provider_free_failure")
        print(
            json.dumps(
                {"status": terminal["status"], "error": terminal["failure_coordinate"]}
            )
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
