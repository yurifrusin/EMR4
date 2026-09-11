"""Authored lifecycle fixtures; never loads the real repository policy or Git."""

import hashlib
from types import SimpleNamespace
from pathlib import Path
import orchestration_harness.programme_admission as pa
import scripts.raisa_ariadne_recovery_preflight as preflight


def make_preflight_fixture(tmp_path, monkeypatch, gate, phase):
    root = tmp_path / "authored-repository"
    root.mkdir(parents=True)
    parent, child, reviewed = "1" * 40, "2" * 40, "3" * 40
    head = parent if phase == "development" else child
    remote = child if phase == "post-push" else parent
    branch = "codex/synthetic-recovery"
    url = "https://example.invalid/authored/repository"
    current = gate in {"G1B.2", "G1A.3-R1"}
    r1 = gate == "G1A.3-R1"
    r0 = gate == "G1A.3-R0"
    programme_gate = "G1A.3" if r0 or r1 else gate
    task_class = pa.G1A3_R1_TASK_CLASS if r1 else pa.G1B2_TASK_CLASS
    paths = pa.G1A3_R1_ALLOWED_PATHS if r1 else pa.G1B2_ALLOWED_PATHS
    effects = pa.G1A3_R1_ALLOWED_EFFECTS if r1 else pa.G1B2_ALLOWED_EFFECTS
    forbidden = pa.G1A_FORBIDDEN_EFFECTS if r1 else pa.G1B2_FORBIDDEN_EFFECTS
    profile = (
        pa.G1A3_R1_ACTIVE_PROFILE
        if r1
        else pa.G1A3_R0_REVIEW_PENDING_PROFILE
        if r0
        else pa.G1B2_ACTIVE_PROFILE
        if current
        else pa.G1B1_CLOSEOUT_REVIEW_PENDING_PROFILE
    )
    rows = [f"{parent} refs/heads/authored-{i:03d}" for i in range(135)]
    digest = hashlib.sha256(("\n".join(rows) + "\n").encode()).hexdigest()

    def put(name, value):
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(value, encoding="utf-8")
        return path

    artifacts = {}
    for name in ("git_bundle", "pre_g0_untracked_archive"):
        path = put("preservation/" + name, "authored inert preservation bytes")
        artifacts[name] = {
            "path": str(path),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }
    for name in preflight.REQUIRED_WORKFLOWS:
        put(name, "# authored workflow marker\n")
    put(
        "alembic/versions/d4787e8e3629_phase_0_baseline.py",
        'revision = "authored_head"\ndown_revision = None\n'
        "# TRUNCATE TABLE prescriptions, mbs_claims, clinical_diagnoses, encounters, patients CASCADE\n",
    )
    put(
        "app/routers/consultation.py",
        '# os.path.join("static", "audio", audio_filename)\n',
    )
    put("app/main.py", '# app.mount("/static", StaticFiles(directory="static")\n')
    state = {
        "programme_mode": "recovery",
        "current_gate": programme_gate,
        "current_gate_status": "active",
        "active_profile": profile,
        "active_correction": gate if current or r0 else pa.G1B1_CLOSEOUT_CORRECTION,
        "feature_work_eligible": False,
        "product_work_eligible": False,
        "task_selection": {"allowed_task_kinds": [task_class] if current else []},
        "recovery_baton": {"branch": branch},
        "g1a_subgate_authority": {
            "subgates": {
                "G1A.3": {"r1_state_transition": {"r0_controller_commit": reviewed}}
            }
        },
        "g1b": {
            "implementation_review_history": [{"reviewed_commit": parent}],
            "subgates": {
                "G1B.2": {"state_transition": {"enablement_candidate_commit": reviewed}}
            },
        },
        "protected_refs": {
            "expected_sha": parent,
            "refs": ["refs/heads/master", "refs/heads/handoff/current"],
        },
        "clockwork_snapshot": {
            "local_safety_ref": "refs/heads/safety/authored",
            "frozen_sha": parent,
            **artifacts,
        },
        "repository_inventory": {
            "pre_g0_remote_branch_count": 135,
            "pre_g0_remote_branch_snapshot_sha256": digest,
        },
        "global_checks": {
            "global_gate": "red_repair_only",
            "feature_work_suspended": True,
            "pytest_collection": {"status": "red"},
            "alembic": {"head": "authored_head"},
            "python_security": {
                "status": "red",
                "task_branch_local_bandit": {
                    "status": "red_reviewed_baseline_mismatch"
                },
            },
        },
        "actions_performed": {
            "live_provider_calls": 0,
            "real_patient_data_accesses": 0,
            "protected_ref_movements": 0,
        },
    }
    active = {
        "admitted_task_classes": [task_class] if current else [],
        "programme_gate": programme_gate,
        "allowed_effects": sorted(effects) if current else [],
        "forbidden_effects": sorted(forbidden) if current else [],
        "closed_entrypoints": ["provider_invocation", "integration"],
    }
    policy = SimpleNamespace(
        state=state,
        overlay={
            "active_profile": profile,
            "profiles": {profile: active},
            "remote_identity_policy": {"normalized_push_url": url},
        },
        allowed_paths=tuple(sorted(paths)) if current else (),
        state_digest="a" * 64,
        policy_digest="b" * 64,
        risks={"risks": [{"id": name} for name in sorted(preflight.EXPECTED_RISKS)]},
    )
    observations = []

    def git(repo, *args):
        assert repo.resolve() == root.resolve()
        observations.append(args)
        if args == ("rev-parse", "HEAD"):
            return head
        if args == ("branch", "--show-current"):
            return branch
        if args in [
            ("rev-list", "--reverse", f"{reviewed}..{head}"),
            ("rev-list", "--reverse", f"{reviewed}..HEAD"),
        ]:
            return parent if head == parent else parent + "\n" + head
        if args == ("ls-remote", "--refs", url, f"refs/heads/{branch}"):
            return f"{remote}\trefs/heads/{branch}"
        if args == (
            "for-each-ref",
            "--format=%(objectname) %(refname)",
            "refs/remotes/origin",
        ):
            return "\n".join(
                row.replace("refs/heads/", "refs/remotes/origin/") for row in rows
            )
        if (
            len(args) == 2
            and args[0] == "rev-parse"
            and args[1]
            in (
                *state["protected_refs"]["refs"],
                state["clockwork_snapshot"]["local_safety_ref"],
            )
        ):
            return parent
        raise AssertionError(f"unexpected Git observation: {args}")

    def load(repo):
        assert repo.resolve() == root.resolve()
        return policy

    monkeypatch.setattr(preflight, "load_programme_policy", load)
    monkeypatch.setattr(pa, "load_programme_policy", load)
    monkeypatch.setattr(preflight, "_trusted_run_git", git)
    monkeypatch.setattr(pa, "_run_git", git)
    return SimpleNamespace(
        root=root,
        state=state,
        policy=policy,
        observations=observations,
        artifact=Path(artifacts["git_bundle"]["path"]),
    )
