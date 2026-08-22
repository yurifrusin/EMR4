"""Control one useful authored-synthetic edit through the corrected guard graph."""

from __future__ import annotations

import argparse
from contextlib import contextmanager
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Any, Iterator

import jsonschema

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts import (
    raisa_authored_synthetic_check_in_native_harness_bounded_worker_attempt_004
    as accepted_attempt,
)
from scripts import (
    raisa_authored_synthetic_check_in_native_harness_bounded_worker_monitored_development_rehearsal
    as accepted_controller,
)
from scripts import (
    deepseek_native_harness_provider_free_integrated_runner_accepted_guard_graph_materialization_recovery
    as accepted_graph,
)


OPERATION_ID = (
    "raisa-authored-synthetic-native-harness-corrected-guard-graph-first-"
    "useful-development-recovery-rehearsal"
)
ATTEMPT_ID = "deepseek-native-corrected-guard-window-worker-001"
WORK_ORDER_ID = "wo-deepseek-native-corrected-guard-window-worker-001"
LEASE_ID = "lease-deepseek-native-corrected-guard-window-worker-001"
OPERATION_ROOT = REPO_ROOT / "orchestration" / "continuity" / OPERATION_ID
ATTEMPT_ROOT = Path(f"C:/Users/sarashera/EMR4-worktrees/{ATTEMPT_ID}")
PLAN_PATH = REPO_ROOT / "docs" / f"{OPERATION_ID}-plan.md"
THREAT_PATH = REPO_ROOT / "docs" / "security" / f"{OPERATION_ID}-threat-model-delta.md"
CONTRACT_PATH = OPERATION_ROOT / "contract.json"
CONTRACT_SCHEMA_PATH = OPERATION_ROOT / "contract.schema.json"
TERMINAL_SCHEMA_PATH = OPERATION_ROOT / "occupied-terminal.schema.json"
PROVIDER_FREE_EVIDENCE_PATH = OPERATION_ROOT / "provider-free-evidence.json"
PROVIDER_FREE_REPORT_PATH = OPERATION_ROOT / "provider-free-report.md"
FOCUSED_TEST_PATH = (
    REPO_ROOT
    / "tests"
    / "test_raisa_authored_synthetic_native_harness_corrected_guard_graph_first_"
    "useful_development_recovery_rehearsal.py"
)
PLANNING_SOURCE = "97c73ea454489d40dcf6e3cb0a024fc9e023a03d"
ACCEPTED_GRAPH_SOURCE = "822d487afcf6657027bc66c8d6d9635677e73096"
ACCEPTED_BOOT_SOURCE = "f0f8e59ebd70da5167edf907c9ece26049cdcf1c"
ACCEPTED_RUNNER_SHA256 = (
    "017394e3f86a3efdf5eba0745c254a8b561615fb6ab923978b81bb5941e8e3f4"
)
ACCEPTED_RUNNER_BYTES = 14210
ACCEPTED_RUNNER_TARGET = (
    "C:/Users/sarashera/EMR4-worktrees/"
    "deepseek-native-integrated-window-worker-001/workspace/"
    "synthetic_window_coalescer.py"
)
ACCEPTED_GRAPH_INVENTORY = {
    "guard": {
        "bytes": 4501,
        "sha256": "76029da0f9c030651fd10c0df16f4e75e86b2269d7560af7f94c74680f8598b9",
    },
    "bridge": {
        "bytes": 1661,
        "sha256": "3a49b28174eeefd77d7efe0a00498901ac6636b637ed9dfe60aba46980df1d0b",
    },
    "sanitizer": {
        "bytes": 2439,
        "sha256": "12552925a600dc951afc30b9a738746499c7e2f4cefc9962bc05fb06780f158f",
    },
}
GRAPH_FILENAMES = {
    "guard": "effective-tool-guard.mjs",
    "bridge": "preset-mount-sanitizer-runner-bridge.mjs",
    "sanitizer": (
        "deepseek_native_harness_provider_free_"
        "preset_mount_safe_subcoordinate_sanitizer.mjs"
    ),
}
_ACCEPTED_GRAPH_CACHE: dict[str, bytes] | None = None
FULL_OID = re.compile(r"^[0-9a-f]{40}$")

PATH_BINDINGS = {
    "CHECKPOINT_PATH": OPERATION_ROOT / "occupied-preexecution-checkpoint.json",
    "PREPARATION_PATH": OPERATION_ROOT / "occupied-attempt-preparation.json",
    "WORK_ORDER_PATH": OPERATION_ROOT / "work-order-v2.json",
    "AUTHORITY_PATH": OPERATION_ROOT / "worker-authority.json",
    "FORBIDDEN_PATH": OPERATION_ROOT / "forbidden-surfaces.json",
    "COMMAND_MANIFEST_PATH": OPERATION_ROOT / "command-manifest.json",
    "NO_DATABASE_ADMISSION_PATH": OPERATION_ROOT
    / "provider-free-no-database-admission.json",
    "CONSUMED_PATH": OPERATION_ROOT / "occupied-attempt-consumed.json",
    "TERMINAL_PATH": OPERATION_ROOT / "occupied-terminal.json",
    "TERMINAL_SCHEMA_PATH": TERMINAL_SCHEMA_PATH,
    "NATIVE_REPORT_PATH": OPERATION_ROOT / "occupied-report.md",
    "PRE_HMR_TERMINAL_PATH": OPERATION_ROOT / "pre-hmr-startup-terminal.json",
}


class IntegratedDevelopmentError(RuntimeError):
    """A frozen useful-development invariant failed closed."""


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_bytes())
    if not isinstance(value, dict):
        raise IntegratedDevelopmentError(f"json_root_invalid:{path.name}")
    return value


def git(*args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(REPO_ROOT), *args],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=20,
    )
    if completed.returncode != 0:
        raise IntegratedDevelopmentError("git_resolution_failed")
    return completed.stdout.strip()


def is_ancestor(object_id: str) -> bool:
    return (
        FULL_OID.fullmatch(object_id) is not None
        and subprocess.run(
            ["git", "-C", str(REPO_ROOT), "merge-base", "--is-ancestor", object_id, "HEAD"],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=20,
        ).returncode
        == 0
    )


def accepted_graph_sources() -> dict[str, bytes]:
    global _ACCEPTED_GRAPH_CACHE
    if _ACCEPTED_GRAPH_CACHE is not None:
        return dict(_ACCEPTED_GRAPH_CACHE)
    sources = accepted_graph.accepted_sources(accepted_graph.load_contract())
    if set(sources) != {"runner", "guard", "bridge", "sanitizer"}:
        raise IntegratedDevelopmentError("accepted_graph_inventory_invalid")
    runner = sources["runner"]
    if (
        len(runner) != ACCEPTED_RUNNER_BYTES
        or sha256_bytes(runner) != ACCEPTED_RUNNER_SHA256
    ):
        raise IntegratedDevelopmentError("accepted_runner_binding_invalid")
    for name, expected in ACCEPTED_GRAPH_INVENTORY.items():
        payload = sources[name]
        if (
            len(payload) != expected["bytes"]
            or sha256_bytes(payload) != expected["sha256"]
        ):
            raise IntegratedDevelopmentError(f"accepted_{name}_binding_invalid")
    _ACCEPTED_GRAPH_CACHE = dict(sources)
    return dict(sources)


def integrated_runner_source(target_path: str) -> bytes:
    source = accepted_graph_sources()["runner"].decode("utf-8")
    original_target = f"const TARGET_PATH = {json.dumps(ACCEPTED_RUNNER_TARGET)};"
    if source.count(original_target) != 1:
        raise IntegratedDevelopmentError("accepted_target_literal_invalid")
    derived_literal = f"const TARGET_PATH = {json.dumps(target_path)};"
    derived = source.replace(original_target, derived_literal)
    if derived.count(derived_literal) != 1:
        raise IntegratedDevelopmentError("derived_target_literal_invalid")
    if derived.replace(derived_literal, original_target) != source:
        raise IntegratedDevelopmentError("runner_reverse_binding_invalid")
    return derived.encode("utf-8")


def validate_integrated_runner_source(payload: bytes) -> dict[str, Any]:
    synthetic_target = (
        ATTEMPT_ROOT / "workspace" / accepted_controller.SYNTHETIC_PATH
    ).resolve().as_posix()
    deterministic_target = "C:/synthetic-native-worker/synthetic_window_coalescer.py"
    allowed_payloads = {
        integrated_runner_source(synthetic_target),
        integrated_runner_source(deterministic_target),
    }
    if payload not in allowed_payloads:
        raise IntegratedDevelopmentError("derived_runner_not_exact_transformation")
    source = payload.decode("utf-8")
    checks = {
        "typed_argument_preflight": (
            source.count("export function preflightEditArguments(args)") == 1
            and source.count(
                "const argumentPreflight = preflightEditArguments(args);"
            )
            == 1
        ),
        "typed_argument_result": source.count("classifyEditArgumentResult({") == 1,
        "typed_lifecycle": source.count("classifyToolLifecycle({") == 1,
        "one_factory": source.count("await agents.create(") == 1,
        "one_followup": source.count("agent.followup(") == 1,
        "one_pre_execute": source.count('agentCtx.on("tools/pre-execute"') == 1,
        "one_post_execute": source.count('agentCtx.on("tools/post-execute"') == 1,
        "one_result": source.count('agentCtx.on("tools/result"') == 1,
        "one_conclusion": source.count("exec.concludeTurn()") == 1,
        "conclusion_before_dispatch": source.index("exec.concludeTurn()")
        < source.index("return next();", source.index("exec.concludeTurn()")),
        "exact_tools": 'Object.freeze(["edit", "glob", "read"])' in source,
        "exact_model": (
            'provider: "deepseek-official", model: "deepseek-v4-flash", '
            'reasoningEffort: "high"'
        )
        in source,
        "no_retry_fallback": "retry(" not in source and "fallback" not in source.lower(),
        "conclusion_success_reading": (
            source.count("conclusion_marked: toolLifecycleCoordinate") == 1
        ),
        "conclusion_failure_reading": source.count("conclusion_marked: false") == 1,
        "corrected_guard_import": (
            source.count('import("./effective-tool-guard.mjs")') == 1
        ),
    }
    if not all(checks.values()):
        failed = sorted(name for name, passed in checks.items() if not passed)
        raise IntegratedDevelopmentError("derived_runner_controls_invalid:" + ",".join(failed))
    return {"sha256": sha256_bytes(payload), "bytes": len(payload), "checks": checks}


def validate_corrected_graph_directory(proof: Path, target_path: str) -> dict[str, Any]:
    expected = accepted_graph_sources()
    readings: dict[str, Any] = {}
    paths = {
        "runner": proof / "runner.mjs",
        **{name: proof / filename for name, filename in GRAPH_FILENAMES.items()},
    }
    for name, path in paths.items():
        if not path.is_file():
            raise IntegratedDevelopmentError(f"materialized_{name}_absent")
        payload = path.read_bytes()
        required = integrated_runner_source(target_path) if name == "runner" else expected[name]
        if payload != required:
            raise IntegratedDevelopmentError(f"materialized_{name}_mismatch")
        readings[name] = {"sha256": sha256_bytes(payload), "bytes": len(payload)}
    guard_source = paths["guard"].read_text(encoding="utf-8")
    if (
        guard_source.count(f'from "./{GRAPH_FILENAMES["bridge"]}"') != 1
        or paths["bridge"].read_text(encoding="utf-8").count(
            f'from "./{GRAPH_FILENAMES["sanitizer"]}"'
        )
        != 1
    ):
        raise IntegratedDevelopmentError("materialized_graph_import_closure_invalid")
    return readings


def materialize_corrected_profile(
    root: Path, base_materializer: Any
) -> dict[str, str]:
    profile = base_materializer(root)
    proof = root / "installation" / "proof"
    sources = accepted_graph_sources()
    (proof / GRAPH_FILENAMES["bridge"]).write_bytes(sources["bridge"])
    (proof / GRAPH_FILENAMES["sanitizer"]).write_bytes(sources["sanitizer"])
    target = (root / "workspace" / accepted_controller.SYNTHETIC_PATH).resolve().as_posix()
    readings = validate_corrected_graph_directory(proof, target)
    profile.update(
        {
            "bridge_sha256": readings["bridge"]["sha256"],
            "sanitizer_sha256": readings["sanitizer"]["sha256"],
        }
    )
    return profile


def contract_value() -> dict[str, Any]:
    target = (ATTEMPT_ROOT / "workspace" / accepted_controller.SYNTHETIC_PATH).resolve().as_posix()
    return {
        "schema_version": "ariadne.native_harness_integrated_development_contract.v1",
        "operation_id": OPERATION_ID,
        "planning_source": PLANNING_SOURCE,
        "accepted_sources": {
            "corrected_guard_graph": ACCEPTED_GRAPH_SOURCE,
            "corrected_graph_stock_headless_boot": ACCEPTED_BOOT_SOURCE,
        },
        "identity": {
            "attempt_id": ATTEMPT_ID,
            "work_order_id": WORK_ORDER_ID,
            "lease_id": LEASE_ID,
            "target_path": target,
        },
        "runner": {
            "accepted_bytes": ACCEPTED_RUNNER_BYTES,
            "accepted_sha256": ACCEPTED_RUNNER_SHA256,
            "derived_bytes": len(integrated_runner_source(target)),
            "derived_sha256": sha256_bytes(integrated_runner_source(target)),
            "allowed_transformations": [
                "exact_target_literal_rebinding",
            ],
        },
        "graph_inventory": {
            name: {**value, "filename": GRAPH_FILENAMES[name]}
            for name, value in ACCEPTED_GRAPH_INVENTORY.items()
        },
        "work_package": {
            "path": accepted_controller.SYNTHETIC_PATH,
            "baseline_sha256": sha256_bytes(accepted_controller.BASELINE_SOURCE.encode()),
            "expected_sha256": sha256_bytes(accepted_controller.EXPECTED_SOURCE.encode()),
            "public_case_count": 4,
            "holdback_case_count": 3,
        },
        "documentation": {
            "plan_sha256": sha256_file(PLAN_PATH),
            "threat_model_sha256": sha256_file(THREAT_PATH),
        },
        "implementation": {
            "controller_sha256": sha256_file(Path(__file__).resolve()),
            "focused_test_sha256": sha256_file(FOCUSED_TEST_PATH),
            "contract_schema_sha256": sha256_file(CONTRACT_SCHEMA_PATH),
            "terminal_schema_sha256": sha256_file(TERMINAL_SCHEMA_PATH),
        },
        "ceilings": {
            "native_processes": 1,
            "sessions": 1,
            "turns": 1,
            "provider_requests": 1,
            "direct_literal_edits": 1,
            "retries": 0,
            "resumes": 0,
            "fallbacks": 0,
            "auxiliary_models": 0,
        },
    }


def write_contract() -> dict[str, Any]:
    if CONTRACT_PATH.exists():
        raise IntegratedDevelopmentError("contract_already_exists")
    value = contract_value()
    schema = load_json(CONTRACT_SCHEMA_PATH)
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(schema).validate(value)
    CONTRACT_PATH.write_bytes(canonical_bytes(value))
    return value


def load_contract() -> dict[str, Any]:
    value = load_json(CONTRACT_PATH)
    schema = load_json(CONTRACT_SCHEMA_PATH)
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(schema).validate(value)
    if value != contract_value():
        raise IntegratedDevelopmentError("contract_exact_binding_mismatch")
    if any(
        not is_ancestor(source)
        for source in [PLANNING_SOURCE, ACCEPTED_GRAPH_SOURCE, ACCEPTED_BOOT_SOURCE]
    ):
        raise IntegratedDevelopmentError("accepted_source_not_ancestor")
    if git("log", "-1", "--format=%H", "--", PLAN_PATH.relative_to(REPO_ROOT).as_posix()) != PLANNING_SOURCE:
        raise IntegratedDevelopmentError("planning_source_path_mismatch")
    return value


@contextmanager
def configured_accepted_attempt() -> Iterator[None]:
    # Resolve and validate the immutable graph before replacing the historical
    # guard builder from which that graph's ancestry is reconstructed.
    accepted_graph_sources()
    attempt_bindings: dict[str, Any] = {
        "OPERATION_ID": OPERATION_ID,
        "ATTEMPT_ID": ATTEMPT_ID,
        "WORK_ORDER_ID": WORK_ORDER_ID,
        "LEASE_ID": LEASE_ID,
        "EVIDENCE_ROOT": OPERATION_ROOT,
        "ATTEMPT_ROOT": ATTEMPT_ROOT,
        "TERMINAL_SCHEMA_PATH": TERMINAL_SCHEMA_PATH,
        "PATH_BINDINGS": PATH_BINDINGS,
    }
    attempt_prior = {name: getattr(accepted_attempt, name) for name in attempt_bindings}
    original_materializer = accepted_controller.materialize_profile
    controller_bindings: dict[str, Any] = {
        "runner_source": integrated_runner_source,
        "validate_runner_source": validate_integrated_runner_source,
        "materialize_profile": lambda root: materialize_corrected_profile(
            root, original_materializer
        ),
    }
    controller_prior = {
        name: getattr(accepted_controller, name) for name in controller_bindings
    }
    guard_prior = accepted_controller.guard.build_guard_source
    for name, value in attempt_bindings.items():
        setattr(accepted_attempt, name, value)
    for name, value in controller_bindings.items():
        setattr(accepted_controller, name, value)
    accepted_controller.guard.build_guard_source = lambda: accepted_graph_sources()[
        "guard"
    ]
    try:
        yield
    finally:
        accepted_controller.guard.build_guard_source = guard_prior
        for name, value in controller_prior.items():
            setattr(accepted_controller, name, value)
        for name, value in attempt_prior.items():
            setattr(accepted_attempt, name, value)


def provider_free_check() -> dict[str, Any]:
    contract = load_contract()
    if ATTEMPT_ROOT.exists():
        raise IntegratedDevelopmentError("disposable_attempt_root_must_be_absent")
    if any(PATH_BINDINGS[name].exists() for name in ("CONSUMED_PATH", "TERMINAL_PATH")):
        raise IntegratedDevelopmentError("occupied_identity_already_consumed")
    with configured_accepted_attempt():
        accepted = accepted_attempt.provider_free_check()
    target = contract["identity"]["target_path"]
    runner = validate_integrated_runner_source(integrated_runner_source(target))
    result = {
        "schema_version": "ariadne.native_harness_integrated_development_provider_free_evidence.v1",
        "operation_id": OPERATION_ID,
        "result": "passed",
        "contract_sha256": sha256_file(CONTRACT_PATH),
        "accepted_attempt_check": accepted,
        "runner": runner,
        "work_package": contract["work_package"],
        "boundary": {
            "native_process_count": 0,
            "session_count": 0,
            "turn_count": 0,
            "model_request_count": 0,
            "provider_request_count": 0,
            "retry_count": 0,
            "resume_count": 0,
            "fallback_count": 0,
            "auxiliary_model_count": 0,
            "database_or_docker_count": 0,
        },
    }
    return result


def publish_provider_free_check() -> dict[str, Any]:
    if PROVIDER_FREE_EVIDENCE_PATH.exists() or PROVIDER_FREE_REPORT_PATH.exists():
        raise IntegratedDevelopmentError("provider_free_output_already_exists")
    value = provider_free_check()
    PROVIDER_FREE_EVIDENCE_PATH.write_bytes(canonical_bytes(value))
    PROVIDER_FREE_REPORT_PATH.write_text(
        "# Integrated-runner useful-development provider-free report\n\n"
        f"- Result: `{value['result']}`\n"
        f"- Derived runner: `{value['runner']['sha256']}`\n"
        "- Work package: `synthetic_window_coalescer.py`\n"
        "- Public / holdback cases: `4 / 3`\n"
        "- Native/session/turn/model/provider/database/Docker counts: all `0`\n\n"
        "The exact integrated runner is rebound only to the synthetic target and "
        "retains its typed edit and lifecycle controls. No occupied authority was used.\n",
        encoding="utf-8",
        newline="\n",
    )
    return value


def prepare_attempt(review_receipt_path: Path) -> dict[str, Any]:
    provider_free_check()
    with configured_accepted_attempt():
        return accepted_attempt.prepare_attempt(review_receipt_path)


def execute_native() -> dict[str, Any]:
    load_contract()
    with configured_accepted_attempt():
        return accepted_attempt.execute_native()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--write-contract", action="store_true")
    action.add_argument("--check", action="store_true")
    action.add_argument("--publish-check", action="store_true")
    action.add_argument("--prepare-attempt", action="store_true")
    action.add_argument("--native", action="store_true")
    parser.add_argument("--review-receipt", type=Path)
    args = parser.parse_args()
    try:
        if args.write_contract:
            value = write_contract()
        elif args.check:
            value = provider_free_check()
        elif args.publish_check:
            value = publish_provider_free_check()
        elif args.prepare_attempt:
            if args.review_receipt is None:
                raise IntegratedDevelopmentError("review_receipt_required")
            value = prepare_attempt(args.review_receipt)
        else:
            if args.review_receipt is not None:
                raise IntegratedDevelopmentError("review_receipt_not_valid_for_native")
            value = execute_native()
        print(json.dumps({"status": value.get("result", value.get("status")), "operation_id": OPERATION_ID}))
        return 0
    except (
        IntegratedDevelopmentError,
        accepted_controller.RehearsalError,
        jsonschema.ValidationError,
        OSError,
        ValueError,
    ) as error:
        print(json.dumps({"status": "failed_closed", "error": str(error)}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
