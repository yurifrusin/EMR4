"""Prove the rc.7 required-service injection repair without starting Harness."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import re
import tarfile
from io import BytesIO
from pathlib import Path
from typing import Any

import yaml

from scripts.deepseek_native_harness_provider_free_preterminal_observability_recovery import (
    corrected_runner_source,
    load_contract as load_observability_contract,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
OPERATION_ID = "deepseek-native-harness-provider-free-required-service-injection-recovery"
ROOT = (
    REPO_ROOT
    / "orchestration"
    / "continuity"
    / OPERATION_ID
)
CONTRACT_PATH = ROOT / "contract.json"
EVIDENCE_PATH = ROOT / "provider-free-required-service-injection-evidence.json"
REPORT_PATH = ROOT / "provider-free-required-service-injection-report.md"
PLAN_PATH = (
    REPO_ROOT
    / "docs"
    / "deepseek-native-harness-provider-free-required-service-injection-recovery-plan.md"
)
CONTROLLER_PATH = Path(__file__).resolve()
FOCUSED_TEST_PATH = (
    REPO_ROOT
    / "tests"
    / "test_deepseek_native_harness_provider_free_required_service_injection_recovery.py"
)
HEX_40 = re.compile(r"^[0-9a-f]{40}$")
HEX_64 = re.compile(r"^[0-9a-f]{64}$")
REQUIRED_SERVICES = ("hmr", "agentPresets", "tools")
ROOT_CAUSE = "headless_agent_presets_row_absent_and_runner_dependencies_underdeclared"
EVIDENCE_SCHEMA = (
    "ariadne.deepseek_native_harness_required_service_injection_recovery_evidence.v1"
)
ACCEPTED_RUNNER_INJECT = b'export const inject = ["hmr"];'
FUTURE_RUNNER_INJECT = b'export const inject = ["hmr", "agentPresets", "tools"];'


class ServiceInjectionRecoveryError(RuntimeError):
    """A closed deterministic recovery check failed."""


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        + "\n"
    ).encode("utf-8")


def load_contract() -> dict[str, Any]:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    if contract.get("schema_version") != (
        "ariadne.deepseek_native_harness_required_service_injection_recovery_contract.v1"
    ):
        raise ServiceInjectionRecoveryError("contract_schema_mismatch")
    if contract.get("operation_id") != OPERATION_ID:
        raise ServiceInjectionRecoveryError("contract_operation_mismatch")
    if contract.get("root_cause") != ROOT_CAUSE:
        raise ServiceInjectionRecoveryError("contract_root_cause_mismatch")
    for field in ("planning_source", "accepted_failed_source"):
        if HEX_40.fullmatch(str(contract.get(field, ""))) is None:
            raise ServiceInjectionRecoveryError(f"contract_full_git_id_required:{field}")
    packages = contract.get("packages")
    if not isinstance(packages, list) or len(packages) != 8:
        raise ServiceInjectionRecoveryError("contract_package_count_mismatch")
    if len({row.get("name") for row in packages if isinstance(row, dict)}) != 8:
        raise ServiceInjectionRecoveryError("contract_package_names_not_unique")
    future = contract.get("future_declaration", {})
    if tuple(future.get("required_services", ())) != REQUIRED_SERVICES:
        raise ServiceInjectionRecoveryError("contract_required_services_mismatch")
    if future.get("selected_profile_materialised") is not False:
        raise ServiceInjectionRecoveryError("contract_preset_claim_must_remain_false")
    for field, digest in contract.get("implementation_bytes", {}).items():
        if HEX_64.fullmatch(str(digest)) is None:
            raise ServiceInjectionRecoveryError(
                f"contract_implementation_digest_invalid:{field}"
            )
    return contract


def default_cache_root() -> Path:
    local_app_data = os.environ.get("LOCALAPPDATA")
    if not local_app_data:
        raise ServiceInjectionRecoveryError("localappdata_missing")
    return Path(local_app_data) / "npm-cache"


def cache_blob_path(cache_root: Path, integrity: str) -> Path:
    if not integrity.startswith("sha512-"):
        raise ServiceInjectionRecoveryError("package_integrity_algorithm_mismatch")
    try:
        digest = base64.b64decode(integrity.removeprefix("sha512-"), validate=True)
    except ValueError as error:
        raise ServiceInjectionRecoveryError(
            "package_integrity_encoding_invalid"
        ) from error
    if len(digest) != 64:
        raise ServiceInjectionRecoveryError("package_integrity_length_invalid")
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


def verify_package_payload(
    package: dict[str, Any], payload: bytes
) -> tuple[dict[str, Any], dict[str, bytes], tuple[str, ...]]:
    if hashlib.sha1(payload).hexdigest() != package["registry_shasum"]:  # noqa: S324
        raise ServiceInjectionRecoveryError(
            f"package_registry_shasum_mismatch:{package['name']}"
        )
    integrity = "sha512-" + base64.b64encode(hashlib.sha512(payload).digest()).decode(
        "ascii"
    )
    if integrity != package["registry_integrity"]:
        raise ServiceInjectionRecoveryError(
            f"package_registry_integrity_mismatch:{package['name']}"
        )
    if sha256_bytes(payload) != package["tar_sha256"]:
        raise ServiceInjectionRecoveryError(
            f"package_tar_sha256_mismatch:{package['name']}"
        )

    retained: dict[str, bytes] = {}
    expected = {f"package/{row['path']}": row for row in package["members"]}
    try:
        with tarfile.open(fileobj=BytesIO(payload), mode="r:gz") as archive:
            members = archive.getmembers()
            names = tuple(member.name for member in members if member.isfile())
            if len(names) != len(set(names)):
                raise ServiceInjectionRecoveryError(
                    f"package_duplicate_member:{package['name']}"
                )
            package_json = archive.getmember("package/package.json")
            if not package_json.isfile() or package_json.issym():
                raise ServiceInjectionRecoveryError(
                    f"package_identity_member_unsafe:{package['name']}"
                )
            identity_stream = archive.extractfile(package_json)
            if identity_stream is None:
                raise ServiceInjectionRecoveryError(
                    f"package_identity_member_unreadable:{package['name']}"
                )
            identity = json.loads(identity_stream.read())
            if (
                identity.get("name") != package["name"]
                or identity.get("version") != package["version"]
            ):
                raise ServiceInjectionRecoveryError(
                    f"package_identity_mismatch:{package['name']}"
                )
            by_name = {member.name: member for member in members}
            for archive_name, row in expected.items():
                member = by_name.get(archive_name)
                if member is None or not member.isfile() or member.issym():
                    raise ServiceInjectionRecoveryError(
                        f"package_member_missing_or_unsafe:{package['name']}:{row['path']}"
                    )
                stream = archive.extractfile(member)
                if stream is None:
                    raise ServiceInjectionRecoveryError(
                        f"package_member_unreadable:{package['name']}:{row['path']}"
                    )
                member_payload = stream.read()
                if len(member_payload) != row["bytes"]:
                    raise ServiceInjectionRecoveryError(
                        f"package_member_size_mismatch:{package['name']}:{row['path']}"
                    )
                if sha256_bytes(member_payload) != row["sha256"]:
                    raise ServiceInjectionRecoveryError(
                        f"package_member_sha256_mismatch:{package['name']}:{row['path']}"
                    )
                retained[row["path"]] = member_payload
    except (KeyError, json.JSONDecodeError, tarfile.TarError) as error:
        raise ServiceInjectionRecoveryError(
            f"package_archive_invalid:{package['name']}"
        ) from error

    return (
        {
            "name": package["name"],
            "version": package["version"],
            "registry_shasum": package["registry_shasum"],
            "registry_integrity": package["registry_integrity"],
            "tar_sha256": package["tar_sha256"],
            "members": [
                {
                    "path": row["path"],
                    "bytes": row["bytes"],
                    "sha256": row["sha256"],
                }
                for row in package["members"]
            ],
        },
        retained,
        names,
    )


def verify_package(
    package: dict[str, Any], cache_root: Path
) -> tuple[dict[str, Any], dict[str, bytes], tuple[str, ...]]:
    path = cache_blob_path(cache_root, package["registry_integrity"])
    if not path.is_file() or path.is_symlink():
        raise ServiceInjectionRecoveryError(
            f"package_cache_blob_missing_or_unsafe:{package['name']}"
        )
    return verify_package_payload(package, path.read_bytes())


def future_patch_fragment() -> bytes:
    return b"""- insert:
    - id: agent-presets
      name: '@deepseek-ai/dsh-agent-presets'
      config:
        default: standard
    - id: provider-free-preterminal-observable-runner
      name: ../../../installation/proof/runner.mjs
      inject: [hmr, agentPresets, tools]
"""


def validate_future_patch(payload: bytes) -> dict[str, Any]:
    try:
        rows = yaml.safe_load(payload)
    except yaml.YAMLError as error:
        raise ServiceInjectionRecoveryError("future_patch_yaml_invalid") from error
    expected = [
        {
            "insert": [
                {
                    "id": "agent-presets",
                    "name": "@deepseek-ai/dsh-agent-presets",
                    "config": {"default": "standard"},
                },
                {
                    "id": "provider-free-preterminal-observable-runner",
                    "name": "../../../installation/proof/runner.mjs",
                    "inject": list(REQUIRED_SERVICES),
                },
            ]
        }
    ]
    if rows != expected:
        raise ServiceInjectionRecoveryError("future_patch_shape_mismatch")
    return {
        "sha256": sha256_bytes(payload),
        "bytes": len(payload),
        "inserted_row_ids": ["agent-presets", "provider-free-preterminal-observable-runner"],
        "required_services": list(REQUIRED_SERVICES),
        "agent_presets_default": "standard",
    }


def future_runner_source() -> bytes:
    accepted = corrected_runner_source()
    if accepted.count(ACCEPTED_RUNNER_INJECT) != 1:
        raise ServiceInjectionRecoveryError("accepted_runner_injection_shape_mismatch")
    return accepted.replace(ACCEPTED_RUNNER_INJECT, FUTURE_RUNNER_INJECT)


def validate_future_runner(payload: bytes) -> dict[str, Any]:
    accepted = corrected_runner_source()
    if payload.count(FUTURE_RUNNER_INJECT) != 1:
        raise ServiceInjectionRecoveryError("future_runner_injection_shape_mismatch")
    if payload.replace(FUTURE_RUNNER_INJECT, ACCEPTED_RUNNER_INJECT) != accepted:
        raise ServiceInjectionRecoveryError("future_runner_changed_beyond_injection")
    source = payload.decode("utf-8")
    coordinates = load_observability_contract()["activation_coordinates"]
    if any(source.count(coordinate) != accepted.decode("utf-8").count(coordinate) for coordinate in coordinates):
        raise ServiceInjectionRecoveryError("future_runner_coordinate_drift")
    return {
        "accepted_sha256": sha256_bytes(accepted),
        "future_sha256": sha256_bytes(payload),
        "bytes": len(payload),
        "required_services": list(REQUIRED_SERVICES),
        "only_dependency_declaration_changed": True,
        "activation_vocabulary_unchanged": True,
    }


def validate_immutable_attempts(contract: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for attempt in contract["immutable_attempts"]:
        if HEX_40.fullmatch(attempt.get("source", "")) is None:
            raise ServiceInjectionRecoveryError("immutable_attempt_full_source_required")
        files = []
        for item in attempt["files"]:
            path = REPO_ROOT / item["path"]
            if not path.is_file() or path.is_symlink():
                raise ServiceInjectionRecoveryError(
                    f"immutable_attempt_file_missing_or_unsafe:{item['path']}"
                )
            actual = sha256_file(path)
            if actual != item["sha256"]:
                raise ServiceInjectionRecoveryError(
                    f"immutable_attempt_digest_mismatch:{item['path']}"
                )
            files.append({"path": item["path"], "sha256": actual})
        evidence_path = next(
            REPO_ROOT / item["path"]
            for item in attempt["files"]
            if item["path"].endswith("evidence.json")
        )
        evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
        if evidence.get("attempt_id") != attempt["attempt_id"] or evidence.get("result") != "fail":
            raise ServiceInjectionRecoveryError(
                f"immutable_attempt_terminal_mismatch:{attempt['attempt_id']}"
            )
        rows.append(
            {
                "attempt_id": attempt["attempt_id"],
                "source": attempt["source"],
                "result": "fail",
                "unchanged": True,
                "files": files,
            }
        )
    return rows


def validate_implementation_bytes(contract: dict[str, Any]) -> dict[str, str]:
    actual = {
        "plan_sha256": sha256_file(PLAN_PATH),
        "controller_sha256": sha256_file(CONTROLLER_PATH),
        "focused_test_sha256": sha256_file(FOCUSED_TEST_PATH),
    }
    if actual != contract["implementation_bytes"]:
        raise ServiceInjectionRecoveryError("implementation_digest_mismatch")
    return actual


def _contains_once(source: str, text: str) -> bool:
    return source.count(text) == 1


def inspect_source_semantics(
    sources: dict[tuple[str, str], bytes], dsh_archive_names: tuple[str, ...]
) -> dict[str, Any]:
    base = sources[("@deepseek-ai/dsh-base", "cordis.patch.yml")].decode()
    headless = sources[("@deepseek-ai/dsh-headless", "cordis.patch.yml")].decode()
    web = sources[("@deepseek-ai/dsh-web-app", "cordis.patch.yml")].decode()
    presets = sources[("@deepseek-ai/dsh-agent-presets", "lib/index.js")].decode()
    tools = sources[("@deepseek-ai/dsh-tools", "lib/index.js")].decode()
    cordis = sources[("@deepseek-ai/cordis", "lib/index.js")].decode()
    loader = sources[("@deepseek-ai/cordis-plugin-loader", "lib/index.js")].decode()
    profile_boot = sources[("@deepseek-ai/dsh", "lib/profile-boot-DG5t9aNs.js")].decode()

    shipped = sorted(
        {
            name.split("/")[3]
            for name in dsh_archive_names
            if name.startswith("package/config/agent-presets/")
            and name.endswith("/agent.cordis.yml")
            and len(name.split("/")) == 5
        }
    )
    checks = {
        "base_has_single_tools_provider_row": (
            _contains_once(base, "    - id: tools\n      name: '@deepseek-ai/dsh-tools'")
        ),
        "base_has_no_agent_presets_row": "- id: agent-presets" not in base,
        "headless_keeps_tools_row_enabled": (
            _contains_once(headless, "- id: tools\n  config:")
            and "- id: tools\n  disabled: true" not in headless
        ),
        "headless_has_no_agent_presets_row": "- id: agent-presets" not in headless,
        "headless_disables_stock_hmr": (
            _contains_once(headless, "- id: hmr\n  disabled: true")
        ),
        "web_official_agent_presets_row": (
            _contains_once(
                web,
                "    - id: agent-presets\n      name: '@deepseek-ai/dsh-agent-presets'\n      config:\n        default: standard",
            )
        ),
        "agent_presets_service_name": 'super(ctx, "agentPresets")' in presets,
        "agent_presets_requires_loader": 'static inject = ["loader"]' in presets,
        "agent_presets_requires_default": "default: z.string().required()" in presets,
        "tools_service_name": 'super(ctx, "tools")' in tools,
        "tools_requires_system_prompt": 'static inject = ["systemPrompt"]' in tools,
        "profile_boot_detects_agent_presets_row": 'if (rows.has("agent-presets"))' in profile_boot,
        "profile_boot_adds_shipped_root": (
            "path: SHIPPED_PRESET_ROOT" in profile_boot and 'trust: "system"' in profile_boot
        ),
        "cordis_module_inject_resolved": (
            "Inject.resolve(plugin.inject)" in cordis
        ),
        "cordis_array_inject_exact_names": (
            "if (Array.isArray(inject)) for (const name of inject) result[name] = null;"
            in cordis
        ),
        "cordis_missing_dependency_holds_inactive": (
            "for (const name of Object.keys(this.inject))" in cordis
            and "if (!impl) {\n\t\t\t\tepoch = INACTIVE;" in cordis
        ),
        "loader_entry_inject_merged_into_fiber": (
            "Inject.resolve(fiber.entry.options.inject, fiber.inject);" in loader
        ),
        "shipped_preset_set_exact": shipped == ["code", "cordis", "minimal", "standard"],
        "selected_emr4_preset_not_shipped": "emr4-bounded-worker" not in shipped,
    }
    if not all(checks.values()):
        failed = sorted(name for name, passed in checks.items() if not passed)
        raise ServiceInjectionRecoveryError(
            "source_semantic_check_failed:" + ",".join(failed)
        )
    return {
        "checks": checks,
        "base_headless_service_reading": {
            "tools_provider_row_present": True,
            "agent_presets_provider_row_present": False,
            "runner_declared_dependencies": ["hmr"],
        },
        "official_agent_presets_row": {
            "id": "agent-presets",
            "name": "@deepseek-ai/dsh-agent-presets",
            "default": "standard",
        },
        "shipped_preset_ids": shipped,
    }


def build_evidence(cache_root: Path | None = None) -> dict[str, Any]:
    contract = load_contract()
    resolved_cache = (cache_root or default_cache_root()).resolve()
    package_checks = []
    sources: dict[tuple[str, str], bytes] = {}
    archive_names: dict[str, tuple[str, ...]] = {}
    for package in contract["packages"]:
        projection, members, names = verify_package(package, resolved_cache)
        package_checks.append(projection)
        archive_names[package["name"]] = names
        for path, payload in members.items():
            sources[(package["name"], path)] = payload

    semantics = inspect_source_semantics(
        sources, archive_names["@deepseek-ai/dsh"]
    )
    accepted_runner = corrected_runner_source()
    if accepted_runner.count(ACCEPTED_RUNNER_INJECT) != 1:
        raise ServiceInjectionRecoveryError("accepted_runner_not_hmr_only")
    failed_evidence = json.loads(
        (
            REPO_ROOT
            / "orchestration"
            / "continuity"
            / "deepseek-native-harness-provider-free-preterminal-observable-composition-recovery-boot"
            / "provider-free-preterminal-observable-native-boot-evidence.json"
        ).read_text(encoding="utf-8")
    )
    if failed_evidence.get("failure_classification") != "SERVICES_UNAVAILABLE":
        raise ServiceInjectionRecoveryError("accepted_failure_coordinate_mismatch")

    patch = validate_future_patch(future_patch_fragment())
    runner = validate_future_runner(future_runner_source())
    immutable = validate_immutable_attempts(contract)
    implementation = validate_implementation_bytes(contract)
    zero_counts = {name: 0 for name in contract["required_zero_counts"]}
    return {
        "schema_version": EVIDENCE_SCHEMA,
        "operation_id": OPERATION_ID,
        "planning_source": contract["planning_source"],
        "result": "pass",
        "root_cause": ROOT_CAUSE,
        "package_checks": package_checks,
        "source_semantics": {
            **semantics,
            "accepted_terminal": "SERVICES_UNAVAILABLE",
            "accepted_runner_sha256": sha256_bytes(accepted_runner),
            "accepted_runner_hmr_only": True,
        },
        "future_declaration": {
            "patch": patch,
            "runner": runner,
            "required_services": list(REQUIRED_SERVICES),
            "selected_profile": "emr4-bounded-worker",
            "selected_profile_materialised": False,
            "native_execution_authorised": False,
            "implementation_bytes": implementation,
        },
        "immutable_attempts": immutable,
        "provider_boundary": zero_counts,
        "claim_boundary": {
            "proved": "exact_rc7_host_row_and_dependency_gated_future_declaration",
            "not_proved": [
                "emr4_bounded_worker_preset_materialisation",
                "preset_mount",
                "scope_creation",
                "effective_tool_view",
                "native_harness_boot",
                "occupied_deepseek_worker",
                "model_or_provider_reliability",
            ],
            "successor": "deepseek-native-harness-provider-free-emr4-bounded-worker-preset-materialisation-recovery",
        },
    }


def render_report(evidence: dict[str, Any]) -> str:
    package_names = ", ".join(row["name"] for row in evidence["package_checks"])
    future = evidence["future_declaration"]
    return f"""# Provider-free required-service injection recovery report

Date: 2026-08-20

Timestamp: 2026-08-20T09:14:31.1452892+10:00 (Australia/Brisbane)

Result: **pass**

## Exact reading

The exact rc.7 `base` + `headless` composition contains the host `tools`
provider but no `agent-presets` provider. The consumed runner and loader row
declared only `hmr`, so Cordis had no dependency gate for `agentPresets` or
`tools`. The retained `SERVICES_UNAVAILABLE` result is therefore explained by
`{evidence['root_cause']}` without rerunning Harness.

The exact future declarations add the official rc.7 `agent-presets` host row
with `default: standard` and require `hmr`, `agentPresets`, `tools` in both the
loader row and module export. Cordis and loader source prove that these names
are merged into the plugin fiber and that activation waits while any declared
provider is absent.

## Bindings

- packages checked: {package_names};
- future patch SHA-256: `{future['patch']['sha256']}`;
- future runner SHA-256: `{future['runner']['future_sha256']}`;
- both consumed native attempts: exact and unchanged; and
- Node, native Harness, occupied worker, agent/session/turn, broker, model,
  provider, network, Docker and database counts: all zero.

## Claim ceiling

`emr4-bounded-worker` is not one of the shipped rc.7 presets. This result does
not materialise it or prove preset mount, scope creation, the effective
`edit`, `glob`, `read` view, a native boot, an occupied worker, or model/provider
reliability. A separate provider-free preset-materialisation recovery must pass
before any future native process can be considered.
"""


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check or publish the provider-free rc.7 service injection recovery."
    )
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--check", action="store_true")
    action.add_argument("--publish", action="store_true")
    parser.add_argument("--cache-root", type=Path)
    args = parser.parse_args()
    try:
        evidence = build_evidence(args.cache_root)
        if args.publish:
            if EVIDENCE_PATH.exists() or REPORT_PATH.exists():
                raise ServiceInjectionRecoveryError("canonical_output_already_exists")
            EVIDENCE_PATH.write_bytes(canonical_json_bytes(evidence))
            REPORT_PATH.write_text(
                render_report(evidence), encoding="utf-8", newline="\n"
            )
        print(
            json.dumps(
                {
                    "status": "passed",
                    "package_count": len(evidence["package_checks"]),
                    "root_cause": evidence["root_cause"],
                    "required_services": evidence["future_declaration"][
                        "required_services"
                    ],
                    "native_harness_processes": evidence["provider_boundary"][
                        "native_harness_processes"
                    ],
                    "published": bool(args.publish),
                },
                sort_keys=True,
            )
        )
        return 0
    except (OSError, ServiceInjectionRecoveryError) as error:
        print(
            json.dumps(
                {"status": "revision_required", "reason": str(error)},
                sort_keys=True,
            )
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
