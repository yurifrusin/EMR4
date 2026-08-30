"""Read-only, strict Gate G0 correction/transition committed-scope preflight."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from orchestration_harness.programme_admission import (
    G0_G08_ALLOWED_PATHS,
    TASK_MANIFEST_VERSION,
    ProgrammeAdmissionError,
    admission_payload,
    evaluate_committed_scope,
    evaluate_programme_operation_admission,
    evaluate_programme_admission,
    git_change_inventory,
    load_programme_policy,
    strict_json_object,
    _run_git as _trusted_run_git,
)

ALLOWED_G0_TRACKED_PATHS = G0_G08_ALLOWED_PATHS
EXPECTED_RISKS = {
    *(f"R-{index:03d}" for index in range(1, 14)),
    *(f"A-{index:03d}" for index in range(1, 11)),
}
RECOVERY_REMOTE_REF = "refs/heads/codex/raisa-ariadne-recovery-g0"
REQUIRED_WORKFLOWS = (
    ".github/workflows/codeql.yml",
    ".github/workflows/node-security.yml",
    ".github/workflows/pages.yml",
    ".github/workflows/python-security.yml",
    ".github/workflows/ui-review.yml",
)


@dataclass(frozen=True)
class Check:
    check_id: str
    passed: bool
    summary: str
    evidence: Any = None


class PreflightError(RuntimeError):
    """An observable preflight input could not be read."""


def _run_git(repo_root: Path, *args: str) -> str:
    try:
        return _trusted_run_git(repo_root, *args)
    except ProgrammeAdmissionError as error:
        raise PreflightError("git observation failed") from error


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
    except OSError as error:
        raise PreflightError("preservation artifact unavailable") from error
    return digest.hexdigest()


def _normalised_remote_rows(repo_root: Path) -> list[str]:
    rows: list[str] = []
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
            raise PreflightError("unexpected origin ref")
        rows.append(f"{object_id} refs/heads/{ref[len(prefix) :]}")
    return sorted(rows)


def _rows_digest(rows: list[str]) -> str:
    return hashlib.sha256(("\n".join(rows) + "\n").encode("utf-8")).hexdigest()


def _remote_baseline_snapshot(repo_root: Path) -> tuple[int, str, bool, int]:
    rows = _normalised_remote_rows(repo_root)
    suffix = f" {RECOVERY_REMOTE_REF}"
    recovery_rows = [row for row in rows if row.endswith(suffix)]
    if len(recovery_rows) > 1:
        raise PreflightError("duplicate recovery branch rows")
    baseline = [row for row in rows if not row.endswith(suffix)]
    return len(baseline), _rows_digest(baseline), bool(recovery_rows), len(rows)


def _alembic_heads(repo_root: Path) -> list[str]:
    revisions: set[str] = set()
    parents: set[str] = set()
    for path in sorted((repo_root / "alembic/versions").glob("*.py")):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except (OSError, SyntaxError) as error:
            raise PreflightError("migration parse failed") from error
        revision: str | None = None
        down: str | tuple[str, ...] | None = None
        for node in tree.body:
            if not isinstance(node, (ast.Assign, ast.AnnAssign)):
                continue
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            name = next(
                (target.id for target in targets if isinstance(target, ast.Name)), None
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


def _changed_tracked_paths(repo_root: Path) -> set[str]:
    return {
        change.path
        for change in (
            *git_change_inventory(repo_root),
            *git_change_inventory(repo_root, "--cached"),
        )
    }


def _risk_ids(repo_root: Path) -> set[str]:
    policy = load_programme_policy(repo_root)
    return {row["id"] for row in policy.risks["risks"]}


def _verification_phase(repo_root: Path, state: dict[str, Any]) -> str:
    """Select the one phase matching development, pre-push, or post-push Git state."""
    root = repo_root.resolve()
    head = _run_git(root, "rev-parse", "HEAD")
    active_correction = state["active_correction"]
    if active_correction == "G0.8":
        parent = state["g0_8_correction"]["authorized_parent_commit"]
    elif active_correction == "G1A.1":
        reviewed = state["gate_transition"]["reviewed_commit"]
        rows = _run_git(
            root, "rev-list", "--reverse", f"{reviewed}..{head}"
        ).splitlines()
        parent = rows[0] if rows else None
    elif active_correction == "G1A.3":
        reviewed = state["g1a_subgate_authority"]["subgates"]["G1A.3"][
            "state_transition"
        ]["enablement_controller_commit"]
        rows = _run_git(
            root, "rev-list", "--reverse", f"{reviewed}..{head}"
        ).splitlines()
        parent = rows[0] if rows else None
    elif active_correction == "G1A.3-R1":
        reviewed = state["g1a_subgate_authority"]["subgates"]["G1A.3"][
            "r1_state_transition"
        ]["r0_controller_commit"]
        rows = _run_git(
            root, "rev-list", "--reverse", f"{reviewed}..{head}"
        ).splitlines()
        parent = rows[0] if rows else None
    elif active_correction == "G1A.3-R0":
        parent = state["g1a_subgate_authority"]["subgates"]["G1A.3"]["owner_exception"][
            "authorized_parent_commit"
        ]
    elif active_correction == "G1A.2":
        reviewed = state["g1a_subgate_authority"]["subgates"]["G1A.2"][
            "state_transition"
        ]["enablement_controller_commit"]
        rows = _run_git(
            root, "rev-list", "--reverse", f"{reviewed}..{head}"
        ).splitlines()
        parent = rows[0] if rows else None
    else:
        parent = None
    if not isinstance(parent, str):
        raise PreflightError("active correction binding unavailable")
    branch = _run_git(root, "branch", "--show-current")
    policy = load_programme_policy(root)
    try:
        from orchestration_harness.programme_admission import _fresh_remote_head

        origin = _fresh_remote_head(
            root,
            policy.overlay["remote_identity_policy"]["normalized_push_url"],
            branch,
        )
    except ProgrammeAdmissionError as error:
        raise PreflightError("fresh remote observation failed") from error
    if head == parent and origin == parent:
        return "development"
    if origin == parent and head != parent:
        return "pre-push"
    if origin == head and head != parent:
        return "post-push"
    raise PreflightError("Git lifecycle phase is contradictory")


def build_task_manifest(
    repo_root: Path = REPO_ROOT,
    *,
    intended_effects: Iterable[str] | None = None,
) -> dict[str, Any]:
    """Build the currently admitted typed task manifest without persisting a token."""
    root = repo_root.resolve()
    policy = load_programme_policy(root)
    active = policy.overlay["profiles"][policy.overlay["active_profile"]]
    if not policy.state["task_selection"]["allowed_task_kinds"]:
        raise PreflightError("no implementation task is currently eligible")
    if policy.state["active_correction"] == "G0.8":
        base_commit = policy.state["g0_8_correction"]["authorized_parent_commit"]
        task_id = "raisa-ariadne-g0-8-fsmonitor-closure"
        objective = "Close trusted Git fsmonitor configuration and index visibility plus complete the narrow pre-import source attestation only; stop before G1A implementation."
    elif policy.state["active_correction"] == "G1A.1":
        reviewed = policy.state["gate_transition"]["reviewed_commit"]
        rows = _run_git(root, "rev-list", "--reverse", f"{reviewed}..HEAD").splitlines()
        if not rows:
            raise PreflightError("G1A activation commit unavailable")
        base_commit = rows[0]
        task_id = "raisa-ariadne-g1a-1-pure-verdict-kernel"
        objective = "Repair the canonical verdict algebra and pure acceptance consumers inside the pre-reviewed G1A.1 scope only."
    elif policy.state["active_profile"] == "G1A.3_ACTIVE":
        reviewed = policy.state["g1a_subgate_authority"]["subgates"]["G1A.3"][
            "state_transition"
        ]["enablement_controller_commit"]
        rows = _run_git(root, "rev-list", "--reverse", f"{reviewed}..HEAD").splitlines()
        if not rows:
            raise PreflightError("G1A.3 activation commit unavailable")
        base_commit = rows[0]
        task_id = "raisa-ariadne-g1a-3-integration-authority-consumer"
        objective = "Implement only the canonical worker-receipt authority consumer inside record_integration without executing integration."
    elif policy.state["active_profile"] == "G1A.3-R1_REVIEW_BINDING_ACTIVE":
        reviewed = policy.state["g1a_subgate_authority"]["subgates"]["G1A.3"][
            "r1_state_transition"
        ]["r0_controller_commit"]
        rows = _run_git(root, "rev-list", "--reverse", f"{reviewed}..HEAD").splitlines()
        if not rows:
            raise PreflightError("G1A.3-R1 activation commit unavailable")
        base_commit = rows[0]
        task_id = "raisa-ariadne-g1a-3-r1-complete-review-byte-binding"
        objective = "Implement only complete review-byte binding inside the run_worker and record_integration bodies, preserving their exact admission-first calls and every other production AST surface, without provider or integration execution."
    else:
        reviewed = policy.state["g1a_subgate_authority"]["subgates"]["G1A.2"][
            "state_transition"
        ]["enablement_controller_commit"]
        rows = _run_git(root, "rev-list", "--reverse", f"{reviewed}..HEAD").splitlines()
        if not rows:
            raise PreflightError("G1A.2 activation commit unavailable")
        base_commit = rows[0]
        task_id = "raisa-ariadne-g1a-2-antigravity-verdict-adapter"
        objective = "Implement only the structured Antigravity verdict adapter inside the three pre-reviewed mutable symbols without provider invocation."
    return {
        "schema_version": TASK_MANIFEST_VERSION,
        "task_id": task_id,
        "task_class": active["admitted_task_classes"][0],
        "programme_gate": active["programme_gate"],
        "objective": objective,
        "base_commit": base_commit,
        "candidate_or_current_head": _run_git(root, "rev-parse", "HEAD"),
        "allowed_path_roots": sorted(policy.allowed_paths),
        "intended_side_effect_classes": list(
            active["allowed_effects"] if intended_effects is None else intended_effects
        ),
        "forbidden_side_effect_classes": sorted(active["forbidden_effects"]),
        "state_digest": policy.state_digest,
        "policy_digest": policy.policy_digest,
    }


def _preservation_checks(repo_root: Path, state: dict[str, Any]) -> list[Check]:
    checks: list[Check] = []
    expected = state["protected_refs"]["expected_sha"]
    refs = {
        ref: _run_git(repo_root, "rev-parse", ref)
        for ref in state["protected_refs"]["refs"]
    }
    checks.append(
        Check(
            "protected_refs",
            all(value == expected for value in refs.values()),
            "protected refs remain exact"
            if all(value == expected for value in refs.values())
            else "protected ref drift",
            refs,
        )
    )
    snapshot = state["clockwork_snapshot"]
    safety = _run_git(repo_root, "rev-parse", snapshot["local_safety_ref"])
    checks.append(
        Check(
            "clockwork_safety_ref",
            safety == snapshot["frozen_sha"],
            "safety ref preserves the frozen source"
            if safety == snapshot["frozen_sha"]
            else "safety ref drift",
            {"observed": safety, "expected": snapshot["frozen_sha"]},
        )
    )
    artifacts: dict[str, Any] = {}
    artifact_ok = True
    for key in ("git_bundle", "pre_g0_untracked_archive"):
        item = snapshot[key]
        observed = _sha256_file(Path(item["path"]))
        passed = observed == item["sha256"]
        artifact_ok = artifact_ok and passed
        artifacts[key] = {
            "observed": observed,
            "expected": item["sha256"],
            "passed": passed,
        }
    checks.append(
        Check(
            "local_preservation_artifacts",
            artifact_ok,
            "preservation artifacts match"
            if artifact_ok
            else "preservation artifact mismatch",
            artifacts,
        )
    )
    count, digest, recovery_present, current = _remote_baseline_snapshot(repo_root)
    inventory = state["repository_inventory"]
    remote_ok = (
        count == inventory["pre_g0_remote_branch_count"] == 135
        and digest == inventory["pre_g0_remote_branch_snapshot_sha256"]
        and current == 135 + int(recovery_present)
    )
    checks.append(
        Check(
            "remote_branch_inventory",
            remote_ok,
            "remote baseline remains exact" if remote_ok else "remote baseline drift",
            {
                "baseline_count": count,
                "baseline_digest": digest,
                "current_count": current,
            },
        )
    )
    return checks


def _static_checks(repo_root: Path, policy: Any) -> list[Check]:
    state = policy.state
    checks: list[Check] = []
    risk_ids = {row["id"] for row in policy.risks["risks"]}
    checks.append(
        Check(
            "strict_risk_inventory",
            risk_ids == EXPECTED_RISKS,
            "strict risk inventory is exact",
            sorted(risk_ids),
        )
    )
    workflows_missing = [
        path for path in REQUIRED_WORKFLOWS if not (repo_root / path).is_file()
    ]
    checks.append(
        Check(
            "workflow_inventory",
            not workflows_missing,
            "workflow inventory is present",
            workflows_missing,
        )
    )
    heads = _alembic_heads(repo_root)
    expected_head = state["global_checks"]["alembic"]["head"]
    checks.append(
        Check(
            "alembic_heads",
            heads == [expected_head],
            "Alembic graph remains one-headed",
            {"heads": heads, "expected": expected_head},
        )
    )
    global_checks = state["global_checks"]
    global_red = (
        global_checks["pytest_collection"]["status"] == "red"
        and global_checks["python_security"]["status"] == "red"
        and global_checks["python_security"]["task_branch_local_bandit"]["status"]
        == "red_reviewed_baseline_mismatch"
        and global_checks["global_gate"] == "red_repair_only"
        and global_checks["feature_work_suspended"] is True
    )
    checks.append(
        Check(
            "global_red_containment",
            global_red,
            "known global reds remain explicit and feature work remains suspended",
        )
    )
    migration = (
        repo_root / "alembic/versions/d4787e8e3629_phase_0_baseline.py"
    ).read_text(encoding="utf-8")
    destructive = (
        "TRUNCATE TABLE prescriptions, mbs_claims, clinical_diagnoses, encounters, patients CASCADE"
        in migration
    )
    checks.append(
        Check(
            "destructive_upgrade_evidence",
            destructive,
            "R-001 binds the actual destructive upgrade",
        )
    )
    consultation = (repo_root / "app/routers/consultation.py").read_text(
        encoding="utf-8"
    )
    main = (repo_root / "app/main.py").read_text(encoding="utf-8")
    static_audio = (
        'os.path.join("static", "audio", audio_filename)' in consultation
        and 'app.mount("/static", StaticFiles(directory="static")' in main
    )
    checks.append(
        Check(
            "public_static_audio_evidence",
            static_audio,
            "R-003 binds the actual upload and static mount",
        )
    )
    actions = state["actions_performed"]
    forbidden_zero = all(value in (0, False) for value in actions.values())
    checks.append(
        Check(
            "forbidden_action_accounting",
            forbidden_zero,
            "all forbidden-action counters remain zero",
            actions,
        )
    )
    return checks


def build_report(
    repo_root: Path = REPO_ROOT,
    task_manifest: object | None = None,
    phase: str = "development",
    entrypoint: str = "recovery_preflight",
) -> dict[str, Any]:
    """Build a deterministic report; no task label can substitute for a manifest."""
    root = repo_root.resolve()
    try:
        policy = load_programme_policy(root)
    except ProgrammeAdmissionError as error:
        return {
            "schema_version": "raisa-ariadne.recovery-preflight.v2",
            "status": "blocked",
            "read_only": True,
            "phase": phase,
            "feature_work_eligible": False,
            "failed_checks": ["programme_state_missing_or_invalid"],
            "reason_codes": [error.reason_code],
            "checks": [],
        }
    if entrypoint in {"task_branch_commit", "task_branch_push"}:
        operation = evaluate_programme_operation_admission(
            repo_root=root,
            manifest=task_manifest,
            entrypoint=entrypoint,
            phase=phase,
        )
        admission = operation
        scope = operation
    else:
        admission = evaluate_programme_admission(
            repo_root=root, manifest=task_manifest, entrypoint=entrypoint
        )
        scope = evaluate_committed_scope(
            repo_root=root, manifest=task_manifest, phase=phase
        )
    checks = [
        Check(
            "programme_admission",
            admission.admitted,
            "typed correction or state-only transition admitted"
            if admission.admitted
            else "typed programme admission denied",
            admission_payload(admission),
        ),
        Check(
            "committed_scope",
            scope.admitted,
            "Git scope and phase binding passed"
            if scope.admitted
            else "Git scope or phase binding denied",
            admission_payload(scope),
        ),
        *_preservation_checks(root, policy.state),
        *_static_checks(root, policy),
    ]
    failed = [check.check_id for check in checks if not check.passed]
    return {
        "schema_version": "raisa-ariadne.recovery-preflight.v2",
        "status": "passed" if not failed else "blocked",
        "read_only": True,
        "phase": phase,
        "programme_mode": policy.state["programme_mode"],
        "current_gate": policy.state["current_gate"],
        "current_gate_status": policy.state["current_gate_status"],
        "active_correction": policy.state["active_correction"],
        "requested_entrypoint": entrypoint,
        "feature_work_eligible": False,
        "g1a_authorized": bool(
            policy.state.get("gate_transition")
            and policy.state["gate_transition"].get("g1a_authorized") is True
        ),
        "global_gate": policy.state["global_checks"]["global_gate"],
        "failed_checks": failed,
        "checks": [asdict(check) for check in checks],
    }


def _render_human(report: dict[str, Any]) -> str:
    lines = [
        f"Raisa/Ariadne recovery preflight: {report['status'].upper()}",
        f"phase={report.get('phase')} mode={report.get('programme_mode')} gate={report.get('current_gate')} active_correction={report.get('active_correction')}",
        f"feature_work_eligible=false g1a_authorized={str(bool(report.get('g1a_authorized'))).lower()}",
    ]
    for check in report.get("checks", []):
        lines.append(
            f"[{'PASS' if check['passed'] else 'BLOCK'}] {check['check_id']}: {check['summary']}"
        )
    if report["failed_checks"]:
        lines.append("failed_checks=" + ",".join(report["failed_checks"]))
    return "\n".join(lines)


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--task-manifest", type=Path)
    parser.add_argument(
        "--phase",
        choices=("development", "pre-push", "post-push"),
        default="development",
    )
    parser.add_argument(
        "--entrypoint",
        choices=(
            "task_selection",
            "recovery_preflight",
            "task_branch_commit",
            "task_branch_push",
        ),
        default="recovery_preflight",
    )
    parser.add_argument("--format", choices=("human", "json"), default="human")
    args = parser.parse_args(list(argv) if argv is not None else None)
    try:
        manifest = (
            strict_json_object(args.task_manifest) if args.task_manifest else None
        )
        report = build_report(args.repo_root, manifest, args.phase, args.entrypoint)
    except (OSError, ProgrammeAdmissionError, PreflightError) as error:
        reason = (
            error.reason_code
            if isinstance(error, ProgrammeAdmissionError)
            else "programme_state_missing_or_invalid"
        )
        report = {
            "schema_version": "raisa-ariadne.recovery-preflight.v2",
            "status": "blocked",
            "read_only": True,
            "phase": args.phase,
            "feature_work_eligible": False,
            "failed_checks": ["programme_state_missing_or_invalid"],
            "reason_codes": [reason],
            "checks": [],
        }
    print(
        json.dumps(report, indent=2, sort_keys=True)
        if args.format == "json"
        else _render_human(report)
    )
    return 0 if report["status"] == "passed" else 2


if __name__ == "__main__":
    raise SystemExit(main())
