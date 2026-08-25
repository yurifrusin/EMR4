"""Read-only fail-closed preflight for the Raisa/Ariadne recovery programme.

The command reads Git and repository files. It does not write files, refs,
databases, remotes, caches, provider state or deployment state.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable


REPO_ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = Path("orchestration/programme/current-state.json")
GATES_PATH = Path("orchestration/programme/gates.yaml")
RISK_PATH = Path("orchestration/programme/risk-register.yaml")
INVENTORY_PATH = Path("orchestration/programme/branch-pr-disposition.yaml")
RECOVERY_SETTINGS_PATH = Path(
    "orchestration/harness_settings/programme_recovery.yaml"
)
RECOVERY_REMOTE_REF = "refs/heads/codex/raisa-ariadne-recovery-g0"

ALLOWED_G0_TRACKED_PATHS = {
    "docs/programme/raisa-ariadne-recovery-programme.md",
    "docs/architecture/raisa-projection-native-north-star.md",
    "docs/architecture/ariadne-clockwork-correction.md",
    "orchestration/programme/gates.yaml",
    "orchestration/programme/current-state.json",
    "orchestration/programme/risk-register.yaml",
    "orchestration/programme/branch-pr-disposition.yaml",
    "orchestration/harness_settings/programme_recovery.yaml",
    "orchestration/harness_settings/project.yaml",
    "orchestration/harness_settings/autonomous_continuation.yaml",
    "scripts/raisa_ariadne_recovery_preflight.py",
    "tests/test_raisa_ariadne_recovery_preflight.py",
    "tests/test_ariadne_orchestrator_preflight.py",
    "tests/fixtures/ariadne_harness/orchestrator_runtime_state.json",
}

REQUIRED_G0_FILES = tuple(
    Path(value)
    for value in (
        "docs/programme/raisa-ariadne-recovery-programme.md",
        "docs/architecture/raisa-projection-native-north-star.md",
        "docs/architecture/ariadne-clockwork-correction.md",
        str(GATES_PATH),
        str(STATE_PATH),
        str(RISK_PATH),
        str(INVENTORY_PATH),
        str(RECOVERY_SETTINGS_PATH),
        "scripts/raisa_ariadne_recovery_preflight.py",
        "tests/test_raisa_ariadne_recovery_preflight.py",
    )
)

REQUIRED_WORKFLOWS = (
    ".github/workflows/codeql.yml",
    ".github/workflows/node-security.yml",
    ".github/workflows/pages.yml",
    ".github/workflows/python-security.yml",
    ".github/workflows/ui-review.yml",
)

EXPECTED_RISKS = {
    *(f"R-{index:03d}" for index in range(1, 14)),
    *(f"A-{index:03d}" for index in range(1, 11)),
}

TASK_KINDS = (
    "g0_recovery",
    "product_feature",
    "g1a",
    "integration",
    "provider_call",
    "deployment",
    "protected_ref_operation",
)


@dataclass(frozen=True)
class Check:
    check_id: str
    passed: bool
    summary: str
    evidence: Any = None


class PreflightError(RuntimeError):
    """An observable preflight input could not be read or validated."""


def _run_git(repo_root: Path, *args: str) -> str:
    try:
        completed = subprocess.run(  # noqa: S603
            ["git", *args],
            cwd=repo_root,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            shell=False,
            timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        raise PreflightError(f"git command unavailable: {' '.join(args)}") from error
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip()
        raise PreflightError(f"git {' '.join(args)} failed: {detail}")
    return completed.stdout


def _json_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise PreflightError(f"invalid or missing JSON state: {path}") from error
    if not isinstance(value, dict):
        raise PreflightError(f"JSON state must be an object: {path}")
    return value


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
    except OSError as error:
        raise PreflightError(f"preservation artifact unavailable: {path}") from error
    return digest.hexdigest()


def _normalised_remote_rows(repo_root: Path) -> list[str]:
    rows = []
    for line in _run_git(
        repo_root,
        "for-each-ref",
        "--format=%(objectname) %(refname)",
        "refs/remotes/origin",
    ).splitlines():
        object_id, ref = line.split(" ", 1)
        if ref == "refs/remotes/origin/HEAD":
            continue
        prefix = "refs/remotes/origin/"
        if not ref.startswith(prefix):
            raise PreflightError(f"unexpected origin ref: {ref}")
        rows.append(f"{object_id} refs/heads/{ref[len(prefix):]}")
    return sorted(rows)


def _rows_digest(rows: list[str]) -> str:
    payload = ("\n".join(rows) + "\n").encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _remote_snapshot(repo_root: Path) -> tuple[int, str]:
    rows = _normalised_remote_rows(repo_root)
    return len(rows), _rows_digest(rows)


def _remote_baseline_snapshot(repo_root: Path) -> tuple[int, str, bool, int]:
    """Return the pre-G0 baseline after excluding only the recovery branch."""
    rows = _normalised_remote_rows(repo_root)
    recovery_suffix = f" {RECOVERY_REMOTE_REF}"
    recovery_rows = [row for row in rows if row.endswith(recovery_suffix)]
    if len(recovery_rows) > 1:
        raise PreflightError("duplicate recovery branch rows in origin inventory")
    baseline = [row for row in rows if not row.endswith(recovery_suffix)]
    return len(baseline), _rows_digest(baseline), bool(recovery_rows), len(rows)


def _alembic_heads(repo_root: Path) -> list[str]:
    revisions: set[str] = set()
    parents: set[str] = set()
    versions = repo_root / "alembic" / "versions"
    for path in sorted(versions.glob("*.py")):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except (OSError, SyntaxError) as error:
            raise PreflightError(f"cannot statically parse migration: {path}") from error
        revision: str | None = None
        down: str | tuple[str, ...] | None = None
        for node in tree.body:
            if not isinstance(node, (ast.Assign, ast.AnnAssign)):
                continue
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            name = next(
                (target.id for target in targets if isinstance(target, ast.Name)),
                None,
            )
            if name not in {"revision", "down_revision"}:
                continue
            try:
                value = ast.literal_eval(node.value)
            except (ValueError, TypeError):
                continue
            if name == "revision" and isinstance(value, str):
                revision = value
            elif name == "down_revision" and (
                value is None
                or isinstance(value, str)
                or (
                    isinstance(value, tuple)
                    and all(isinstance(item, str) for item in value)
                )
            ):
                down = value
        if revision:
            revisions.add(revision)
            if isinstance(down, str):
                parents.add(down)
            elif isinstance(down, tuple):
                parents.update(down)
    return sorted(revisions - parents)


def _destructive_migration_markers(repo_root: Path) -> dict[str, int]:
    pattern = re.compile(
        r"\b(?:drop_table|drop_column|TRUNCATE|DELETE\s+FROM)\b",
        re.IGNORECASE,
    )
    files = 0
    matches = 0
    for path in sorted((repo_root / "alembic" / "versions").glob("*.py")):
        try:
            count = len(pattern.findall(path.read_text(encoding="utf-8")))
        except OSError as error:
            raise PreflightError(f"cannot read migration: {path}") from error
        if count:
            files += 1
            matches += count
    return {"files": files, "markers": matches}


def _settings_references(repo_root: Path) -> tuple[list[str], list[str]]:
    settings_dir = repo_root / "orchestration" / "harness_settings"
    pattern = re.compile(
        r"^\s*[A-Za-z0-9_-]*settings_file:\s*[\"']?([^\s#\"']+)",
        re.MULTILINE,
    )
    referenced: list[str] = []
    missing: list[str] = []
    for source in sorted(settings_dir.glob("*.yaml")):
        try:
            values = pattern.findall(source.read_text(encoding="utf-8"))
        except OSError as error:
            raise PreflightError(f"cannot read harness settings: {source}") from error
        for value in values:
            label = f"{source.name}:{value}"
            referenced.append(label)
            if not (settings_dir / value).is_file():
                missing.append(label)
    return referenced, missing


def _risk_ids(repo_root: Path) -> set[str]:
    try:
        text = (repo_root / RISK_PATH).read_text(encoding="utf-8")
    except OSError as error:
        raise PreflightError("risk register is unavailable") from error
    return set(re.findall(r"^\s+- id:\s*[\"']([RA]-\d{3})[\"']", text, re.MULTILINE))


def _changed_tracked_paths(repo_root: Path) -> set[str]:
    paths: set[str] = set()
    for args in (("diff", "--name-only"), ("diff", "--cached", "--name-only")):
        paths.update(
            value.strip().replace("\\", "/")
            for value in _run_git(repo_root, *args).splitlines()
            if value.strip()
        )
    return paths


def _check_programme_files(repo_root: Path) -> Check:
    missing = [str(path) for path in REQUIRED_G0_FILES if not (repo_root / path).is_file()]
    return Check(
        "required_g0_files",
        not missing,
        "all required G0 programme files exist" if not missing else "required G0 files are missing",
        {"missing": missing, "required_count": len(REQUIRED_G0_FILES)},
    )


def _build_checks(repo_root: Path, state: dict[str, Any], task_kind: str) -> list[Check]:
    checks: list[Check] = [_check_programme_files(repo_root)]

    state_shape_ok = (
        state.get("schema_version") == "raisa-ariadne.programme-state.v1"
        and state.get("machine_authoritative") is True
        and state.get("programme_mode") == "recovery"
        and state.get("current_gate") == "G0"
        and state.get("feature_work_eligible") is False
    )
    checks.append(
        Check(
            "machine_authoritative_state",
            state_shape_ok,
            "structured recovery state is authoritative and fail-closed"
            if state_shape_ok
            else "structured recovery state is missing, invalid or permissive",
        )
    )

    selection = state.get("task_selection", {})
    task_allowed = (
        task_kind == "g0_recovery"
        and selection.get("autonomous_selection_enabled") is False
        and selection.get("allowed_task_kinds") == ["g0_recovery"]
        and state.get("feature_work_eligible") is False
    )
    checks.append(
        Check(
            "task_admission",
            task_allowed,
            "task is admitted inside G0 recovery"
            if task_allowed
            else f"task kind {task_kind!r} is blocked by G0 recovery",
            {"requested": task_kind, "allowed": ["g0_recovery"]},
        )
    )

    baton = state.get("recovery_baton", {})
    branch = _run_git(repo_root, "branch", "--show-current").strip()
    head = _run_git(repo_root, "rev-parse", "HEAD").strip()
    base = baton.get("base_sha")
    ancestor = False
    if isinstance(base, str) and re.fullmatch(r"[0-9a-f]{40}", base):
        try:
            ancestor = (
                _run_git(repo_root, "merge-base", "--is-ancestor", base, head) == ""
            )
        except PreflightError:
            ancestor = False
    branch_ok = branch == baton.get("branch") and ancestor
    checks.append(
        Check(
            "recovery_baton",
            branch_ok,
            "recovery branch descends from the exact frozen clockwork base"
            if branch_ok
            else "recovery branch or frozen-base ancestry is invalid",
            {"branch": branch, "head": head, "base": base, "base_is_ancestor": ancestor},
        )
    )

    expected = state.get("protected_refs", {}).get("expected_sha")
    protected_observed: dict[str, str] = {}
    protected_ok = isinstance(expected, str)
    for ref in state.get("protected_refs", {}).get("refs", []):
        try:
            value = _run_git(repo_root, "rev-parse", ref).strip()
        except PreflightError:
            value = "missing"
        protected_observed[ref] = value
        protected_ok = protected_ok and value == expected
    checks.append(
        Check(
            "protected_refs",
            protected_ok,
            "all four protected local/tracking refs remain aligned"
            if protected_ok
            else "a protected local/tracking ref moved or is missing",
            protected_observed,
        )
    )

    snapshot = state.get("clockwork_snapshot", {})
    safety_ref = snapshot.get("local_safety_ref")
    frozen_sha = snapshot.get("frozen_sha")
    try:
        safety_sha = _run_git(repo_root, "rev-parse", str(safety_ref)).strip()
    except PreflightError:
        safety_sha = "missing"
    safety_ok = safety_sha == frozen_sha
    checks.append(
        Check(
            "clockwork_safety_ref",
            safety_ok,
            "named safety ref preserves the exact clockwork base"
            if safety_ok
            else "clockwork safety ref is missing or moved",
            {"ref": safety_ref, "observed_sha": safety_sha, "expected_sha": frozen_sha},
        )
    )

    artifact_evidence: dict[str, Any] = {}
    artifacts_ok = True
    for key in ("git_bundle", "pre_g0_untracked_archive"):
        descriptor = snapshot.get(key, {})
        path = Path(str(descriptor.get("path", "")))
        expected_digest = descriptor.get("sha256")
        try:
            observed_digest = _sha256_file(path)
        except PreflightError:
            observed_digest = "missing"
        ok = observed_digest == expected_digest
        artifacts_ok = artifacts_ok and ok
        artifact_evidence[key] = {
            "path": path.as_posix(),
            "expected_sha256": expected_digest,
            "observed_sha256": observed_digest,
            "passed": ok,
        }
    checks.append(
        Check(
            "local_preservation_artifacts",
            artifacts_ok,
            "tracked and untracked preservation artifacts match their digests"
            if artifacts_ok
            else "a local preservation artifact is missing or changed",
            artifact_evidence,
        )
    )

    (
        remote_baseline_count,
        remote_baseline_digest,
        recovery_remote_present,
        remote_current_count,
    ) = _remote_baseline_snapshot(repo_root)
    inventory = state.get("repository_inventory", {})
    remote_ok = (
        remote_baseline_count == inventory.get("pre_g0_remote_branch_count") == 135
        and remote_baseline_digest
        == inventory.get("pre_g0_remote_branch_snapshot_sha256")
        and remote_current_count in {135, 136}
        and remote_current_count == 135 + int(recovery_remote_present)
    )
    checks.append(
        Check(
            "remote_branch_inventory",
            remote_ok,
            "the 135-head baseline matches; only the recovery branch may be added"
            if remote_ok
            else "cached origin branches differ from the G0 baseline or contain an unauthorized addition",
            {
                "pre_g0_count": remote_baseline_count,
                "pre_g0_sha256": remote_baseline_digest,
                "recovery_remote_present": recovery_remote_present,
                "current_count": remote_current_count,
            },
        )
    )

    risks = _risk_ids(repo_root)
    risk_ok = risks == EXPECTED_RISKS
    checks.append(
        Check(
            "risk_inventory",
            risk_ok,
            "all 23 known stop-ship/controller risks have explicit entries"
            if risk_ok
            else "risk register IDs are incomplete or unexpected",
            {"observed": sorted(risks), "missing": sorted(EXPECTED_RISKS - risks)},
        )
    )

    referenced, missing = _settings_references(repo_root)
    checks.append(
        Check(
            "harness_policy_references",
            not missing,
            "all settings_file references resolve"
            if not missing
            else "one or more harness policy references are missing",
            {"reference_count": len(referenced), "missing": missing},
        )
    )

    project = (repo_root / "orchestration/harness_settings/project.yaml").read_text(
        encoding="utf-8"
    )
    continuation = (
        repo_root / "orchestration/harness_settings/autonomous_continuation.yaml"
    ).read_text(encoding="utf-8")
    overlay = (repo_root / RECOVERY_SETTINGS_PATH).read_text(encoding="utf-8")
    overlay_ok = all(
        token in project + continuation + overlay
        for token in (
            "programme_recovery.yaml",
            "higher_than_standing_continuation",
            "autonomous_task_selection: false",
            "missing_or_invalid_state: \"hard_stop\"",
        )
    )
    checks.append(
        Check(
            "recovery_overlay",
            overlay_ok,
            "emergency overlay outranks ordinary autonomous continuation and fails closed"
            if overlay_ok
            else "recovery overlay is missing or does not fail closed",
        )
    )

    changed = _changed_tracked_paths(repo_root)
    unexpected = sorted(changed - ALLOWED_G0_TRACKED_PATHS)
    checks.append(
        Check(
            "tracked_change_scope",
            not unexpected,
            "all tracked working changes are inside the explicit G0 allowlist"
            if not unexpected
            else "tracked changes exist outside Gate G0",
            {"changed": sorted(changed), "unexpected": unexpected},
        )
    )

    workflows_missing = [
        value for value in REQUIRED_WORKFLOWS if not (repo_root / value).is_file()
    ]
    checks.append(
        Check(
            "workflow_inventory",
            not workflows_missing,
            "all five repository workflows are present"
            if not workflows_missing
            else "repository workflow inventory is incomplete",
            {"missing": workflows_missing},
        )
    )

    heads = _alembic_heads(repo_root)
    expected_head = state.get("global_checks", {}).get("alembic", {}).get("head")
    checks.append(
        Check(
            "alembic_heads",
            heads == [expected_head],
            "Alembic graph has the one recorded head"
            if heads == [expected_head]
            else "Alembic graph is missing, divergent or contradictory",
            {"heads": heads, "expected": expected_head},
        )
    )

    globals_ = state.get("global_checks", {})
    containment_ok = (
        globals_.get("pytest_collection", {}).get("status") == "red"
        and globals_.get("python_security", {}).get("status") == "red"
        and globals_
        .get("python_security", {})
        .get("task_branch_local_bandit", {})
        .get("status")
        == "red_reviewed_baseline_mismatch"
        and globals_.get("global_gate") == "red_repair_only"
        and globals_.get("feature_work_suspended") is True
        and state.get("feature_work_eligible") is False
    )
    checks.append(
        Check(
            "global_red_containment",
            containment_ok,
            "known collection and dependency reds are explicit and suspend feature work"
            if containment_ok
            else "global red status is absent or fails to suspend feature work",
            {
                "pytest_collection": globals_.get("pytest_collection", {}).get("status"),
                "python_security": globals_.get("python_security", {}).get("status"),
                "task_branch_local_bandit": globals_
                .get("python_security", {})
                .get("task_branch_local_bandit", {})
                .get("status"),
                "global_gate": globals_.get("global_gate"),
            },
        )
    )

    markers = _destructive_migration_markers(repo_root)
    marker_contained = (
        markers["markers"] > 0
        and state.get("stop_ship_containment", {}).get("destructive_migration")
        == "recorded_R-001_no_migration_execution"
        and state.get("feature_work_eligible") is False
    )
    checks.append(
        Check(
            "destructive_marker_containment",
            marker_contained,
            "destructive migration markers are reported and execution remains forbidden"
            if marker_contained
            else "destructive migration markers are absent from structured containment",
            markers,
        )
    )

    actions = state.get("actions_performed", {})
    forbidden_zero = all(
        actions.get(key) in (0, False)
        for key in (
            "protected_ref_movements",
            "branches_deleted",
            "feature_branches_rebased",
            "prs_closed",
            "prs_merged",
            "pages_runs_triggered",
            "deployments",
            "live_provider_calls",
            "real_patient_data_accesses",
            "product_defects_fixed",
            "g1a_started",
        )
    )
    checks.append(
        Check(
            "forbidden_action_accounting",
            forbidden_zero,
            "all G0 forbidden-action counters remain zero"
            if forbidden_zero
            else "structured state records a forbidden G0 action",
            actions,
        )
    )
    return checks


def build_report(repo_root: Path = REPO_ROOT, task_kind: str = "g0_recovery") -> dict[str, Any]:
    """Build a deterministic, read-only recovery report."""
    root = repo_root.resolve()
    state = _json_object(root / STATE_PATH)
    checks = _build_checks(root, state, task_kind)
    failed = [check.check_id for check in checks if not check.passed]
    return {
        "schema_version": "raisa-ariadne.recovery-preflight.v1",
        "status": "passed" if not failed else "blocked",
        "read_only": True,
        "programme_mode": state.get("programme_mode"),
        "current_gate": state.get("current_gate"),
        "current_gate_status": state.get("current_gate_status"),
        "requested_task_kind": task_kind,
        "out_of_gate_work_blocked": task_kind != "g0_recovery",
        "feature_work_eligible": False,
        "global_gate": state.get("global_checks", {}).get("global_gate"),
        "failed_checks": failed,
        "checks": [asdict(check) for check in checks],
    }


def _render_human(report: dict[str, Any]) -> str:
    lines = [
        f"Raisa/Ariadne recovery preflight: {report['status'].upper()}",
        f"mode={report['programme_mode']} gate={report['current_gate']} task={report['requested_task_kind']}",
        f"global_gate={report['global_gate']} feature_work_eligible=false",
    ]
    for check in report["checks"]:
        marker = "PASS" if check["passed"] else "BLOCK"
        lines.append(f"[{marker}] {check['check_id']}: {check['summary']}")
    if report["failed_checks"]:
        lines.append("failed_checks=" + ",".join(report["failed_checks"]))
    return "\n".join(lines)


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--task-kind", choices=TASK_KINDS, default="g0_recovery")
    parser.add_argument("--format", choices=("human", "json"), default="human")
    args = parser.parse_args(list(argv) if argv is not None else None)
    try:
        report = build_report(args.repo_root, args.task_kind)
    except PreflightError as error:
        report = {
            "schema_version": "raisa-ariadne.recovery-preflight.v1",
            "status": "blocked",
            "read_only": True,
            "requested_task_kind": args.task_kind,
            "failed_checks": ["programme_state_missing_or_invalid"],
            "error": str(error),
        }
    if args.format == "json":
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(_render_human(report) if "checks" in report else json.dumps(report, indent=2))
    return 0 if report["status"] == "passed" else 2


if __name__ == "__main__":
    raise SystemExit(main())
