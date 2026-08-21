from __future__ import annotations

import hashlib
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
    raisa_provider_free_check_in_native_harness_preset_mount_effective_tool_projection_rehearsal
    as projection,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
OPERATION_ID = (
    "raisa-authored-synthetic-native-harness-bounded-worker-attempt-004-"
    "readiness-and-preexecution-decision"
)
OCCUPIED_OPERATION_ID = (
    "raisa-authored-synthetic-check-in-native-harness-bounded-worker-attempt-004"
)
ATTEMPT_ID = "deepseek-native-synthetic-window-worker-004"
WORK_ORDER_ID = "wo-synthetic-native-window-worker-004"
LEASE_ID = "lease-synthetic-native-window-worker-004"
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
ATTEMPT_EVIDENCE_ROOT = PARENT_ROOT / "attempt-004"
CONVERGENCE_CONTRACT_PATH = (
    REPO_ROOT
    / "orchestration"
    / "continuity"
    / "raisa-provider-free-authored-synthetic-native-harness-structured-"
    "diagnostic-bounded-worker-controller-convergence-rehearsal"
    / "contract.json"
)
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
    "broker_sha256": REPO_ROOT / "scripts" / "ariadne_deepseek_native_harness_broker.mjs",
    "work_order_schema_sha256": REPO_ROOT
    / "orchestration"
    / "continuity"
    / "ariadne-provider-free-no-database-manifest-runner-admission-repair"
    / "work-order-v2.schema.json",
}
FUTURE_LEAVES = (
    "occupied-preexecution-checkpoint.json",
    "occupied-attempt-preparation.json",
    "work-order-v2.json",
    "worker-authority.json",
    "forbidden-surfaces.json",
    "command-manifest.json",
    "provider-free-no-database-admission.json",
    "occupied-attempt-consumed.json",
    "occupied-terminal.json",
    "occupied-terminal.schema.json",
    "occupied-report.md",
    "pre-hmr-startup-terminal.json",
)


class ReadinessError(RuntimeError):
    """A deterministic attempt-004 readiness invariant failed closed."""


def canonical_json(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        + "\n"
    ).encode("utf-8")


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
    jsonschema.Draft202012Validator(load_json(CONTRACT_SCHEMA_PATH)).validate(contract)
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


def validate_git_and_latch(contract: dict[str, Any]) -> dict[str, Any]:
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
    full_values = [
        value for key, value in refs.items() if key not in {"branch"}
    ]
    if any(len(value) != 40 for value in full_values):
        raise ReadinessError("full_git_object_required")
    if refs["branch"] != "codex/ariadne-bernie-davida-parallel-seam":
        raise ReadinessError("task_branch_mismatch")
    if refs["head"] != refs["origin_task"]:
        raise ReadinessError("task_origin_not_aligned")
    protected = contract["protected_ref_source"]
    if any(refs[key] != protected for key in (
        "master", "origin_master", "handoff_current", "origin_handoff_current"
    )):
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
    required_boundary = (
        "no_ordinary_practice_enablement_feature_flag_allowlist_or_command_mounting"
    )
    if required_boundary not in latch.get("protected_boundaries", []):
        raise ReadinessError("ordinary_practice_boundary_missing")
    return refs


def validate_consumed_history() -> list[dict[str, str]]:
    convergence = load_json(CONVERGENCE_CONTRACT_PATH)
    immutable = convergence.get("immutable_artifacts")
    if not isinstance(immutable, list) or len(immutable) != 7:
        raise ReadinessError("immutable_inventory_invalid")
    observed: list[dict[str, str]] = []
    for row in immutable:
        path = REPO_ROOT / row["path"]
        digest = file_sha256(path)
        if digest != row["sha256"]:
            raise ReadinessError("consumed_history_digest_mismatch")
        observed.append({"path": row["path"], "sha256": digest})
    consumed_paths = (
        PARENT_ROOT / "occupied-attempt-consumed.json",
        PARENT_ROOT / "attempt-002" / "occupied-attempt-consumed.json",
        PARENT_ROOT / "attempt-003" / "occupied-attempt-consumed.json",
    )
    expected_ids = [
        "deepseek-native-synthetic-window-worker-001",
        "deepseek-native-synthetic-window-worker-002",
        "deepseek-native-synthetic-window-worker-003",
    ]
    for path, expected_id in zip(consumed_paths, expected_ids, strict=True):
        value = load_json(path)
        if (
            value.get("state") != "consumed"
            or value.get("resume_permitted") is not False
            or value.get("automatic_retry_count") != 0
            or value.get("attempt_id") != expected_id
        ):
            raise ReadinessError("earlier_attempt_not_irrevocably_consumed")
    return observed


def validate_components(contract: dict[str, Any]) -> dict[str, Any]:
    expected = contract["components"]
    observed = {name: file_sha256(path) for name, path in COMPONENT_PATHS.items()}
    preset = projection.native_predecessor.build_preset_source(
        projection.native_predecessor.load_contract()
    )
    target = (
        ATTEMPT_ROOT / "workspace" / accepted_controller.SYNTHETIC_PATH
    ).resolve().as_posix()
    observed.update(
        {
            "preset_sha256": sha256_bytes(preset),
            "task_sha256": sha256_bytes(
                accepted_controller.task_text(target).encode("utf-8")
            ),
            "baseline_source_sha256": sha256_bytes(
                accepted_controller.BASELINE_SOURCE.encode("utf-8")
            ),
            "expected_source_sha256": sha256_bytes(
                accepted_controller.EXPECTED_SOURCE.encode("utf-8")
            ),
        }
    )
    if observed != expected:
        raise ReadinessError("component_digest_mismatch")
    materialization = projection.validate_materialization_source(projection.load_contract())
    package_root = (
        projection.MATERIALIZATION_SOURCE_ROOT
        / "node_modules"
        / "@deepseek-ai"
        / "dsh"
    )
    package = load_json(package_root / "package.json")
    if package.get("name") != "@deepseek-ai/dsh" or package.get("version") != "0.1.0-rc.7":
        raise ReadinessError("native_harness_package_identity_mismatch")
    return {
        **observed,
        "package_name": package["name"],
        "package_version": package["version"],
        "materialization_source": materialization["root"],
        "materialization_process_count": materialization["materialization_process_count"],
    }


def validate_clockwork(contract: dict[str, Any]) -> dict[str, Any]:
    expected = contract["clockwork_reading"]
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
    if observed != expected or pointer.get("writer") != "clockwork":
        raise ReadinessError("clockwork_reading_mismatch")
    return observed


def validate_fresh_identity() -> dict[str, Any]:
    config = attempt_configuration()
    prior_values = {
        "deepseek-native-synthetic-window-worker-001",
        "deepseek-native-synthetic-window-worker-002",
        "deepseek-native-synthetic-window-worker-003",
        "wo-synthetic-native-window-worker-001",
        "wo-synthetic-native-window-worker-002",
        "wo-synthetic-native-window-worker-003",
        "lease-synthetic-native-window-worker-001",
        "lease-synthetic-native-window-worker-002",
        "lease-synthetic-native-window-worker-003",
    }
    if {ATTEMPT_ID, WORK_ORDER_ID, LEASE_ID} & prior_values:
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
    with tempfile.TemporaryDirectory(prefix="emr4-attempt-004-readiness-") as raw:
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
        invalid = converged_controller.select_pre_hmr_terminal(**common)
        value = diagnostic.build_diagnostic_from_fixture(
            {"name": "Error", "message": "redacted"}, **identity
        )
        sidecar.write_bytes(diagnostic.diagnostic_bytes(value))
        valid = converged_controller.select_pre_hmr_terminal(**common)
        lifecycle = converged_controller.validate_lifecycle_envelope(
            converged_controller.lifecycle_envelope_source()
        )
    result = {
        "absent": absent["failure_coordinate"],
        "invalid": invalid["failure_coordinate"],
        "valid_schema": valid["terminal"]["schema_version"],
        "valid_structured_accepted": valid["structured_accepted"],
        "lifecycle_checks": lifecycle["checks"],
        "fixture_root_removed": not root.exists(),
    }
    if result != {
        "absent": "structured_diagnostic_absent",
        "invalid": "structured_diagnostic_invalid",
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
    }:
        raise ReadinessError("terminal_projection_mismatch")
    return result


def deterministic_evidence() -> dict[str, Any]:
    contract = load_contract()
    refs = validate_git_and_latch(contract)
    consumed = validate_consumed_history()
    components = validate_components(contract)
    clockwork = validate_clockwork(contract)
    fresh = validate_fresh_identity()
    terminal = validate_terminal_projection()
    limits = contract["limits"]
    if any(limits[key] != 0 for key in (
        "automatic_retries", "resumes", "fallbacks", "second_workers"
    )):
        raise ReadinessError("retry_boundary_open")
    return {
        "schema_version": "ariadne.synthetic_native_worker_attempt_004_readiness_evidence.v1",
        "operation_id": OPERATION_ID,
        "result": "pass",
        "decision": contract["decision"]["pass_coordinate"],
        "evaluated_source": refs["head"],
        "git_refs": refs,
        "consumed_history": consumed,
        "components": components,
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
    jsonschema.Draft202012Validator(load_json(EVIDENCE_SCHEMA_PATH)).validate(value)
    contract = load_contract()
    if value["decision"] != contract["decision"]["pass_coordinate"]:
        raise ReadinessError("stored_decision_mismatch")
    if value["clockwork_reading"] != contract["clockwork_reading"]:
        raise ReadinessError("stored_clockwork_reading_mismatch")
    if value["occupied_attempt_authorized"] is not False:
        raise ReadinessError("occupied_authority_widened")
    report = REPORT_PATH.read_text(encoding="utf-8")
    for token in (
        "Timestamp: 2026-08-21T",
        contract["decision"]["pass_coordinate"],
        "occupied attempt remains unauthorised",
        contract["ordinary_practice_boundary"],
    ):
        if token not in report:
            raise ReadinessError("readiness_report_binding_missing")
    return value


if __name__ == "__main__":
    print(json.dumps(deterministic_evidence(), sort_keys=True, indent=2))
