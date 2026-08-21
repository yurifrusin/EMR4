from __future__ import annotations

import hashlib
import inspect
import json
from pathlib import Path
import subprocess
import tempfile
from typing import Any

import jsonschema

from orchestration_harness import (
    bounded_worker_structured_diagnostic_controller as converged_controller,
)
from orchestration_harness import native_pre_hmr_diagnostic as diagnostic
from scripts import (
    raisa_authored_synthetic_check_in_native_harness_bounded_worker_monitored_development_rehearsal
    as accepted_controller,
)
from scripts import (
    raisa_authored_synthetic_native_harness_bounded_worker_attempt_004_readiness_and_preexecution_decision
    as attempt_004_readiness,
)
from scripts import (
    raisa_provider_free_check_in_native_harness_preset_mount_effective_tool_projection_rehearsal
    as projection,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
OPERATION_ID = (
    "raisa-authored-synthetic-check-in-native-harness-bounded-worker-attempt-005-"
    "readiness-and-preexecution-decision"
)
OCCUPIED_OPERATION_ID = (
    "raisa-authored-synthetic-check-in-native-harness-bounded-worker-attempt-005"
)
ATTEMPT_ID = "deepseek-native-synthetic-window-worker-005"
WORK_ORDER_ID = "wo-synthetic-native-window-worker-005"
LEASE_ID = "lease-synthetic-native-window-worker-005"
ATTEMPT_ROOT = Path(f"C:/Users/sarashera/EMR4-worktrees/{ATTEMPT_ID}")
CONTINUITY_ROOT = REPO_ROOT / "orchestration" / "continuity" / OPERATION_ID
CONTRACT_PATH = CONTINUITY_ROOT / "contract.json"
CONTRACT_SCHEMA_PATH = CONTINUITY_ROOT / "contract.schema.json"
EVIDENCE_PATH = CONTINUITY_ROOT / "deterministic-evidence.json"
EVIDENCE_SCHEMA_PATH = CONTINUITY_ROOT / "deterministic-evidence.schema.json"
REPORT_PATH = CONTINUITY_ROOT / "readiness-report.md"
LATCH_PATH = (
    REPO_ROOT
    / "orchestration"
    / "continuity"
    / "ariadne-active-operation-latch"
    / "current.json"
)
CLOCKWORK_ROOT = REPO_ROOT / "orchestration" / "continuity" / "ariadne-governance-clockwork"
PARENT_ROOT = (
    REPO_ROOT
    / "orchestration"
    / "continuity"
    / "raisa-authored-synthetic-check-in-native-harness-bounded-worker-"
    "monitored-development-rehearsal"
)
ATTEMPT_EVIDENCE_ROOT = PARENT_ROOT / "attempt-005"
COMPONENT_PATHS = {
    "converged_controller_sha256": REPO_ROOT
    / "orchestration_harness"
    / "bounded_worker_structured_diagnostic_controller.py",
    "structured_diagnostic_sha256": REPO_ROOT
    / "orchestration_harness"
    / "native_pre_hmr_diagnostic.py",
    "legacy_terminal_sha256": REPO_ROOT
    / "orchestration_harness"
    / "native_startup_terminal.py",
    "accepted_controller_sha256": REPO_ROOT
    / "scripts"
    / "raisa_authored_synthetic_check_in_native_harness_bounded_worker_"
    "monitored_development_rehearsal.py",
    "attempt_004_wrapper_sha256": REPO_ROOT
    / "scripts"
    / "raisa_authored_synthetic_check_in_native_harness_bounded_worker_"
    "attempt_004.py",
    "broker_sha256": REPO_ROOT / "scripts" / "ariadne_deepseek_native_harness_broker.mjs",
    "work_order_schema_sha256": REPO_ROOT
    / "orchestration"
    / "continuity"
    / "ariadne-provider-free-no-database-manifest-runner-admission-repair"
    / "work-order-v2.schema.json",
}
FUTURE_LEAVES = (
    "checkpoint-intent.json",
    "clockwork-checkpoint-tick-evidence.json",
    "clockwork-checkpoint-tick-report.md",
    "clockwork-tick-evidence.json",
    "clockwork-tick-report.md",
    "closeout-intent.json",
    "command-manifest.json",
    "diagnosis.md",
    "efficacy-reading.json",
    "forbidden-surfaces.json",
    "occupied-attempt-consumed.json",
    "occupied-attempt-preparation.json",
    "occupied-preexecution-checkpoint.json",
    "occupied-report.md",
    "occupied-terminal.json",
    "occupied-terminal.schema.json",
    "postterminal-command-manifest.json",
    "pre-hmr-startup-terminal.json",
    "provider-free-no-database-admission.json",
    "pushover-notification-receipt.json",
    "work-order-v2.json",
    "worker-authority.json",
)


class ReadinessError(RuntimeError):
    """A deterministic attempt-005 readiness invariant failed closed."""


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ReadinessError(f"json_object_required:{path.as_posix()}")
    return value


def git(*args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def load_contract() -> dict[str, Any]:
    contract = load_json(CONTRACT_PATH)
    schema = load_json(CONTRACT_SCHEMA_PATH)
    jsonschema.Draft202012Validator(schema).validate(contract)
    return contract


def attempt_configuration() -> dict[str, Any]:
    return {
        "operation_id": OCCUPIED_OPERATION_ID,
        "attempt_id": ATTEMPT_ID,
        "work_order_id": WORK_ORDER_ID,
        "lease_id": LEASE_ID,
        "attempt_root": ATTEMPT_ROOT,
        "evidence_root": ATTEMPT_EVIDENCE_ROOT,
        "paths": [ATTEMPT_EVIDENCE_ROOT / leaf for leaf in FUTURE_LEAVES],
    }


def validate_git_and_latch(contract: dict[str, Any]) -> dict[str, str]:
    refs = {
        "head": git("rev-parse", "HEAD"),
        "branch": git("branch", "--show-current"),
        "origin_task": git(
            "rev-parse", "origin/codex/ariadne-bernie-davida-parallel-seam"
        ),
        "master": git("rev-parse", "master"),
        "origin_master": git("rev-parse", "origin/master"),
        "handoff_current": git("rev-parse", "handoff/current"),
        "origin_handoff_current": git("rev-parse", "origin/handoff/current"),
    }
    full_values = [value for key, value in refs.items() if key != "branch"]
    if any(len(value) != 40 for value in full_values):
        raise ReadinessError("full_git_object_required")
    if refs["branch"] != "codex/ariadne-bernie-davida-parallel-seam":
        raise ReadinessError("task_branch_mismatch")
    if refs["head"] != refs["origin_task"]:
        raise ReadinessError("task_origin_not_aligned")
    protected = contract["protected_ref_source"]
    protected_names = (
        "master",
        "origin_master",
        "handoff_current",
        "origin_handoff_current",
    )
    if any(refs[name] != protected for name in protected_names):
        raise ReadinessError("protected_ref_mismatch")
    subprocess.run(
        ["git", "merge-base", "--is-ancestor", contract["planning_source"], refs["head"]],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
    )
    latch = load_json(LATCH_PATH)
    if (
        latch.get("operation_id") != OPERATION_ID
        or latch.get("status") != "in_progress"
        or latch.get("user_attention", {}).get("required") is not False
    ):
        raise ReadinessError("active_latch_mismatch")
    required = "no_ordinary_practice_enablement_feature_flag_allowlist_or_command_mounting"
    if required not in latch.get("protected_boundaries", []):
        raise ReadinessError("ordinary_practice_boundary_missing")
    return refs


def _lineage_by_role(contract: dict[str, Any]) -> dict[str, Path]:
    observed: dict[str, Path] = {}
    for row in contract["startup_lineage"]:
        if set(row) != {"role", "path", "sha256"}:
            raise ReadinessError("startup_lineage_shape_mismatch")
        role = row["role"]
        path = (REPO_ROOT / row["path"]).resolve()
        if role in observed or REPO_ROOT.resolve() not in path.parents:
            raise ReadinessError("startup_lineage_path_invalid")
        if not path.is_file() or file_sha256(path) != row["sha256"]:
            raise ReadinessError("startup_lineage_digest_mismatch")
        observed[role] = path
    if len(observed) != 15:
        raise ReadinessError("startup_lineage_count_mismatch")
    return observed


def _require_consumed(path: Path, attempt_id: str) -> None:
    value = load_json(path)
    if (
        value.get("state") != "consumed"
        or value.get("resume_permitted") is not False
        or value.get("automatic_retry_count") != 0
        or value.get("attempt_id") != attempt_id
    ):
        raise ReadinessError("lineage_attempt_not_irrevocably_consumed")


def validate_startup_lineage(
    contract: dict[str, Any],
) -> tuple[list[dict[str, str]], list[dict[str, str]], dict[str, Any]]:
    legacy = attempt_004_readiness.validate_consumed_history()
    roles = _lineage_by_role(contract)
    _require_consumed(
        roles["attempt_004_consumed"],
        "deepseek-native-synthetic-window-worker-004",
    )
    _require_consumed(
        roles["repaired_sentinel_consumed"],
        "repaired-sentinel-native-boot-attempt-001",
    )
    _require_consumed(
        roles["source_repaired_sentinel_consumed"],
        "source-repaired-sentinel-native-boot-attempt-001",
    )
    _require_consumed(
        roles["inert_task_readiness_consumed"],
        "inert-task-sentinel-readiness-native-boot-attempt-001",
    )

    attempt_004 = load_json(roles["attempt_004_terminal"])
    repaired = load_json(roles["repaired_sentinel_terminal"])
    source_repaired = load_json(roles["source_repaired_sentinel_terminal"])
    inert = load_json(roles["inert_task_readiness_terminal"])
    if (
        attempt_004.get("result") != "failed_closed"
        or set(attempt_004.get("broker", {}).values()) != {0}
        or attempt_004.get("automatic_retry_count") != 0
    ):
        raise ReadinessError("attempt_004_terminal_semantics_mismatch")
    if (
        repaired.get("result") != "failed_closed"
        or repaired.get("hmr_events") != []
        or repaired.get("launch", {}).get("retry_count") != 0
    ):
        raise ReadinessError("repaired_sentinel_terminal_semantics_mismatch")
    if (
        source_repaired.get("result") != "failed_closed"
        or source_repaired.get("hmr_events") != ["sentinel_activated"]
        or source_repaired.get("launch", {}).get("task_argument_count") != 0
    ):
        raise ReadinessError("source_repaired_terminal_semantics_mismatch")
    if (
        inert.get("result") != "pass"
        or inert.get("hmr_events")
        != ["sentinel_activated", "stock_headless_hmr_ready"]
        or inert.get("launch", {}).get("task_argument_count") != 1
        or inert.get("launch", {}).get("retry_count") != 0
        or set(inert.get("provider_boundary", {}).values()) - {0, 3}
    ):
        raise ReadinessError("inert_readiness_terminal_semantics_mismatch")

    plugin = load_json(roles["plugin_tree_diagnosis"])
    relative = load_json(roles["relative_specifier_repair"])
    preactivation = load_json(roles["sentinel_preactivation_diagnosis"])
    escape = load_json(roles["sentinel_source_escape_repair"])
    empty_task = load_json(roles["post_sentinel_empty_task_diagnosis"])
    semantics = {
        "attempt_004_coordinate": attempt_004.get("failure_coordinate"),
        "plugin_coordinate": plugin.get("narrowest_supported_coordinate"),
        "relative_specifier_repair_status": relative.get("status"),
        "repaired_sentinel_events": repaired.get("hmr_events"),
        "preactivation_coordinate": preactivation.get(
            "narrowest_supported_coordinate"
        ),
        "sentinel_escape_repair_result": escape.get("result"),
        "source_repaired_events": source_repaired.get("hmr_events"),
        "empty_task_coordinate": empty_task.get("narrowest_supported_coordinate"),
        "inert_readiness_events": inert.get("hmr_events"),
        "inert_readiness_task_argument_count": inert.get("launch", {}).get(
            "task_argument_count"
        ),
    }
    expected = {
        "attempt_004_coordinate": "native_harness_terminal_failure",
        "plugin_coordinate": (
            "profile_patch.initial.synthetic-worker-hmr-sentinel.name:"
            "absolute_windows_path_not_normalized_to_relative_or_file_url_before_"
            "loader_import"
        ),
        "relative_specifier_repair_status": "passed",
        "repaired_sentinel_events": [],
        "preactivation_coordinate": (
            "failed_sentinel_author.sentinel_source.return_bytes_literal:"
            "python_escape_translation_emits_raw_line_terminators_inside_javascript_"
            "regex_and_string_literals"
        ),
        "sentinel_escape_repair_result": "pass",
        "source_repaired_events": ["sentinel_activated"],
        "empty_task_coordinate": (
            "headless_startup.apply.missing_task_program_error_to_app_exit_one"
        ),
        "inert_readiness_events": [
            "sentinel_activated",
            "stock_headless_hmr_ready",
        ],
        "inert_readiness_task_argument_count": 1,
    }
    if semantics != expected:
        raise ReadinessError("startup_lineage_semantics_mismatch")
    lineage = [
        {"role": row["role"], "path": row["path"], "sha256": row["sha256"]}
        for row in contract["startup_lineage"]
    ]
    return legacy, lineage, semantics


def validate_components(contract: dict[str, Any]) -> dict[str, Any]:
    target = (ATTEMPT_ROOT / "workspace" / accepted_controller.SYNTHETIC_PATH).resolve()
    target_text = target.as_posix()
    initial = accepted_controller.profile_patch(ATTEMPT_ROOT, 43123, changed=False)
    changed = accepted_controller.profile_patch(ATTEMPT_ROOT, 43123, changed=True)
    runner = accepted_controller.runner_source(target_text)
    sentinel = accepted_controller.sentinel_source()
    accepted_controller.validate_runner_source(runner)
    accepted_controller.validate_profile_patch(initial, changed=False)
    accepted_controller.validate_profile_patch(changed, changed=True)
    source_semantics = accepted_controller.source_semantics()
    preset = projection.native_predecessor.build_preset_source(
        projection.native_predecessor.load_contract()
    )
    package_root = (
        projection.MATERIALIZATION_SOURCE_ROOT
        / "node_modules"
        / "@deepseek-ai"
        / "dsh"
    )
    package = load_json(package_root / "package.json")
    observed = {name: file_sha256(path) for name, path in COMPONENT_PATHS.items()}
    observed.update(
        {
            "runner_sha256": sha256_bytes(runner),
            "sentinel_sha256": sha256_bytes(sentinel),
            "initial_profile_sha256": sha256_bytes(initial),
            "changed_profile_sha256": sha256_bytes(changed),
            "preset_sha256": sha256_bytes(preset),
            "task_sha256": sha256_bytes(
                accepted_controller.task_text(target_text).encode("utf-8")
            ),
            "baseline_source_sha256": sha256_bytes(
                accepted_controller.BASELINE_SOURCE.encode("utf-8")
            ),
            "expected_source_sha256": sha256_bytes(
                accepted_controller.EXPECTED_SOURCE.encode("utf-8")
            ),
            "package_json_sha256": file_sha256(package_root / "package.json"),
        }
    )
    if observed != contract["components"]:
        raise ReadinessError("component_digest_mismatch")
    if package.get("name") != "@deepseek-ai/dsh" or package.get("version") != "0.1.0-rc.7":
        raise ReadinessError("native_harness_package_identity_mismatch")
    initial_text = initial.decode("utf-8")
    changed_text = changed.decode("utf-8")
    composition = {
        "initial_sentinel_rows": initial_text.count(
            "- id: synthetic-worker-hmr-sentinel"
        ),
        "initial_runner_rows": initial_text.count(
            "- id: synthetic-one-request-worker-runner"
        ),
        "changed_sentinel_rows": changed_text.count(
            "- id: synthetic-worker-hmr-sentinel"
        ),
        "changed_runner_rows": changed_text.count(
            "- id: synthetic-one-request-worker-runner"
        ),
        "relative_sentinel": "name: ../../../installation/proof/sentinel.mjs"
        in initial_text,
        "relative_runner": "name: ../../../installation/proof/runner.mjs"
        in changed_text,
        "default_headless_runner_disabled": (
            "- id: headless-runner\n  disabled: true" in initial_text
            and "- id: headless-runner\n  disabled: true" in changed_text
        ),
        "retry_plugin_disabled": (
            "- id: llm-retry\n  disabled: true" in initial_text
            and "- id: llm-retry\n  disabled: true" in changed_text
        ),
        "runner_source_checks_passed": True,
        "profile_source_checks_passed": True,
        "runtime_source_semantics_passed": all(source_semantics["checks"].values()),
    }
    expected_composition = {
        "initial_sentinel_rows": 1,
        "initial_runner_rows": 0,
        "changed_sentinel_rows": 1,
        "changed_runner_rows": 1,
        "relative_sentinel": True,
        "relative_runner": True,
        "default_headless_runner_disabled": True,
        "retry_plugin_disabled": True,
        "runner_source_checks_passed": True,
        "profile_source_checks_passed": True,
        "runtime_source_semantics_passed": True,
    }
    if composition != expected_composition:
        raise ReadinessError("profile_runner_composition_mismatch")
    materialization = projection.validate_materialization_source(
        projection.load_contract()
    )
    return {
        **observed,
        "package_name": package["name"],
        "package_version": package["version"],
        "materialization_source": materialization["root"],
        "materialization_process_count": materialization[
            "materialization_process_count"
        ],
        "composition": composition,
    }


def validate_clockwork(contract: dict[str, Any]) -> dict[str, Any]:
    pointer = load_json(CLOCKWORK_ROOT / "current.json")
    transaction = load_json(CLOCKWORK_ROOT / "transaction.json")
    journal = transaction.get("journal")
    if not isinstance(journal, list) or not journal:
        raise ReadinessError("clockwork_journal_missing")
    tip = journal[-1]
    observed = {
        "generation_id": pointer.get("selected_generation_id"),
        "lease_sequence": pointer.get("lease_sequence"),
        "transaction_id": transaction.get("transaction_id"),
        "journal_id": tip.get("journal_id"),
        "sequence": tip.get("sequence"),
        "previous_event_sha256": tip.get("event_sha256"),
        "read_only": True,
        "reusable_for_occupied_execution": False,
    }
    if observed != contract["clockwork_reading"] or pointer.get("writer") != "clockwork":
        raise ReadinessError("clockwork_reading_mismatch")
    return observed


def validate_fresh_identity() -> dict[str, Any]:
    config = attempt_configuration()
    prior = set()
    for number in range(1, 5):
        suffix = f"{number:03d}"
        prior.update(
            {
                f"deepseek-native-synthetic-window-worker-{suffix}",
                f"wo-synthetic-native-window-worker-{suffix}",
                f"lease-synthetic-native-window-worker-{suffix}",
            }
        )
    if {ATTEMPT_ID, WORK_ORDER_ID, LEASE_ID} & prior:
        raise ReadinessError("attempt_identity_collision")
    root = ATTEMPT_ROOT.resolve()
    parent = Path("C:/Users/sarashera/EMR4-worktrees").resolve()
    if root.parent != parent or root.exists():
        raise ReadinessError("attempt_root_not_fresh_exact_descendant")
    residue = [path.as_posix() for path in config["paths"] if path.exists()]
    if ATTEMPT_EVIDENCE_ROOT.exists() or residue:
        raise ReadinessError("attempt_output_residue")
    return {
        "operation_id": OCCUPIED_OPERATION_ID,
        "attempt_id": ATTEMPT_ID,
        "work_order_id": WORK_ORDER_ID,
        "lease_id": LEASE_ID,
        "attempt_root": root.as_posix(),
        "evidence_root": ATTEMPT_EVIDENCE_ROOT.relative_to(REPO_ROOT).as_posix(),
        "attempt_root_absent": True,
        "attempt_evidence_root_absent": True,
        "output_path_count": len(config["paths"]),
        "output_paths_absent": True,
    }


def validate_terminal_projection() -> dict[str, Any]:
    identity = {
        "operation_id": OCCUPIED_OPERATION_ID,
        "attempt_id": ATTEMPT_ID,
        "candidate_source": "1" * 40,
    }
    stream = {
        "byte_count": 0,
        "sha256": hashlib.sha256(b"").hexdigest(),
        "classification_bytes": b"",
        "limit_exceeded": False,
    }
    with tempfile.TemporaryDirectory(prefix="emr4-attempt-005-readiness-") as raw:
        root = Path(raw).resolve()
        sidecar = root / converged_controller.DIAGNOSTIC_LEAF
        common = {
            **identity,
            "native_process_started": True,
            "exit_code": 1,
            "controller_coordinate": "native_process_exited_nonzero",
            "hmr_events": [],
            "stdout": dict(stream),
            "stderr": dict(stream),
            "diagnostic_path": sidecar,
            "disposable_root": root,
        }
        absent = converged_controller.select_pre_hmr_terminal(**common)
        sidecar.write_bytes(b"not-json")
        malformed = converged_controller.select_pre_hmr_terminal(**common)
        wrong = diagnostic.build_diagnostic_from_fixture(
            {"name": "Error", "message": "redacted"},
            operation_id=OCCUPIED_OPERATION_ID,
            attempt_id="wrong-attempt",
            candidate_source=identity["candidate_source"],
        )
        sidecar.write_bytes(diagnostic.diagnostic_bytes(wrong))
        wrong_identity = converged_controller.select_pre_hmr_terminal(**common)
        valid_value = diagnostic.build_diagnostic_from_fixture(
            {"name": "Error", "message": "redacted"}, **identity
        )
        sidecar.write_bytes(diagnostic.diagnostic_bytes(valid_value))
        valid = converged_controller.select_pre_hmr_terminal(**common)
        lifecycle = converged_controller.validate_lifecycle_envelope(
            converged_controller.lifecycle_envelope_source()
        )
    result = {
        "absent": absent["failure_coordinate"],
        "malformed": malformed["failure_coordinate"],
        "wrong_identity": wrong_identity["failure_coordinate"],
        "valid_schema": valid["terminal"]["schema_version"],
        "valid_structured_accepted": valid["structured_accepted"],
        "lifecycle_checks": lifecycle["checks"],
        "fixture_root_removed": not root.exists(),
    }
    expected = {
        "absent": "structured_diagnostic_absent",
        "malformed": "structured_diagnostic_invalid",
        "wrong_identity": "structured_diagnostic_invalid",
        "valid_schema": "ariadne.native_harness_pre_hmr_startup_terminal.v2",
        "valid_structured_accepted": True,
        "lifecycle_checks": {
            "single_launch": True,
            "single_terminal_write": True,
            "exact_order": True,
            "cleanup_last": True,
            "no_retry": True,
        },
        "fixture_root_removed": True,
    }
    if result != expected:
        raise ReadinessError("terminal_projection_mismatch")
    return result


def validate_process_free_source() -> dict[str, bool]:
    source = inspect.getsource(inspect.getmodule(validate_process_free_source))
    popen_token = "subprocess." + "Popen"
    node_executable_token = "node" + ".exe"
    node_entrypoint_token = "lib/" + "bin.js"
    provider_endpoint_token = "api." + "deepseek.com"
    provider_credential_token = "DEEPSEEK" + "_API_KEY"
    subprocess_run_token = "subprocess." + "run("
    checks = {
        "no_popen": popen_token not in source,
        "no_node_launch": (
            node_executable_token not in source and node_entrypoint_token not in source
        ),
        "no_provider_endpoint": provider_endpoint_token not in source,
        "no_provider_credential": provider_credential_token not in source,
        "git_reader_only": source.count(subprocess_run_token) == 2,
    }
    if not all(checks.values()):
        raise ReadinessError("process_free_source_boundary_failed")
    return checks


def deterministic_evidence() -> dict[str, Any]:
    contract = load_contract()
    refs = validate_git_and_latch(contract)
    legacy, lineage, semantics = validate_startup_lineage(contract)
    components = validate_components(contract)
    clockwork = validate_clockwork(contract)
    fresh = validate_fresh_identity()
    terminal = validate_terminal_projection()
    process_source = validate_process_free_source()
    limits = contract["limits"]
    zero_limit_names = (
        "automatic_retries",
        "resumes",
        "fallbacks",
        "auxiliary_models",
        "second_workers",
    )
    if any(limits[name] != 0 for name in zero_limit_names):
        raise ReadinessError("retry_or_auxiliary_boundary_open")
    return {
        "schema_version": "ariadne.synthetic_native_worker_attempt_005_readiness_evidence.v1",
        "operation_id": OPERATION_ID,
        "result": "pass",
        "decision": contract["decision"]["pass_coordinate"],
        "evaluated_source": refs["head"],
        "git_refs": refs,
        "legacy_consumed_history": legacy,
        "startup_lineage": lineage,
        "startup_semantics": semantics,
        "components": {**components, "process_free_source_checks": process_source},
        "clockwork_reading": clockwork,
        "fresh_attempt": fresh,
        "terminal_projection": terminal,
        "limits": limits,
        "process_boundary": {
            "node": 0,
            "native_harness": 0,
            "broker": 0,
            "worker": 0,
            "session": 0,
            "prompt": 0,
            "tool": 0,
            "model": 0,
            "provider": 0,
            "network": 0,
        },
        "occupied_attempt_authorized": False,
        "readiness_clockwork_reusable_for_execution": False,
        "fresh_post_closeout_clockwork_reading_required": True,
        "ordinary_practice_boundary": contract["ordinary_practice_boundary"],
    }


def validate_artifacts() -> dict[str, Any]:
    value = load_json(EVIDENCE_PATH)
    schema = load_json(EVIDENCE_SCHEMA_PATH)
    jsonschema.Draft202012Validator(schema).validate(value)
    contract = load_contract()
    if value["decision"] != contract["decision"]["pass_coordinate"]:
        raise ReadinessError("stored_decision_mismatch")
    if value["clockwork_reading"] != contract["clockwork_reading"]:
        raise ReadinessError("stored_clockwork_reading_mismatch")
    if value["occupied_attempt_authorized"] is not False:
        raise ReadinessError("occupied_authority_widened")
    report = REPORT_PATH.read_text(encoding="utf-8")
    required = (
        "Timestamp: 2026-08-21T",
        contract["decision"]["pass_coordinate"],
        "occupied attempt remains unauthorised",
        contract["ordinary_practice_boundary"],
    )
    if any(token not in report for token in required):
        raise ReadinessError("readiness_report_binding_missing")
    return value


if __name__ == "__main__":
    print(json.dumps(deterministic_evidence(), sort_keys=True, indent=2))
