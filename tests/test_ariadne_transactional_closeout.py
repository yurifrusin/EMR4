from __future__ import annotations

import copy
import json
from pathlib import Path
import subprocess
import sys

import pytest
from jsonschema import Draft202012Validator

from orchestration_harness import transactional_closeout as tc
from orchestration_harness.provider_free_no_database_admission import canonical_sha256
from scripts.ariadne_evidence_gate import (
    COMMAND_MANIFEST_SCHEMA_VERSION,
    command_manifest_sha256,
)
from scripts.ariadne_validation_runner import validate_execution_manifest_with_admission


ROOT = Path(__file__).resolve().parents[1]
BASE = "orchestration/continuity/ariadne-transactional-closeout-control-plane-consolidation-efficacy-rehearsal"
SOURCE = "f21072405a4d5877ec03e2cd1aefc7fa74d379e9"
ACCEPTED_CANDIDATE = "f6cbd33fd3322754e06ac6dafa1503f5200e0803"
CANDIDATE_PATHS = [
    "orchestration_harness/transactional_closeout.py",
    f"{BASE}/control-plane.schema.json",
    "tests/test_ariadne_transactional_closeout.py",
    "scripts/ariadne_deepseek_native_harness_broker.mjs",
    "tests/test_ariadne_deepseek_native_harness_broker.py",
]


def _load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def _manifest(graph: dict) -> dict:
    parent = graph["nodes"][-1]["id"]
    evidence = [
        "docs/ariadne-transactional-closeout-control-plane-consolidation-efficacy-rehearsal-plan.md",
        "docs/security/ariadne-transactional-closeout-control-plane-consolidation-efficacy-rehearsal-threat-model-delta.md",
        "orchestration_harness/transactional_closeout.py",
        "tests/test_ariadne_transactional_closeout.py",
        f"{BASE}/control-plane.schema.json",
        f"{BASE}/historical-shadow-fixtures.json",
        "orchestration/agent_inbox/codex/raisa-ordinary-practice-check-in-admission-readiness-review-sol-acceptance.md",
    ]
    return {
        "schema_version": tc.SCHEMA_VERSION,
        "operation_id": "ariadne-transactional-closeout-control-plane-consolidation-efficacy-rehearsal",
        "title": "Ariadne transactional closeout control-plane consolidation efficacy rehearsal",
        "source_anchor": "current_head",
        "recorded_at": "2026-08-18T14:31:10.3800847Z",
        "node": {
            "id": "ariadne-transactional-closeout-control-plane-consolidation-efficacy-rehearsal-shadow",
            "title": "Transactional closeout control-plane consolidation efficacy rehearsal shadow",
            "kind": "maintenance",
            "relationships": [{"node_id": parent, "relation": "builds_on"}],
            "authority": {"authorized_openings": [], "notes": ["Shadow-only provider-free workflow evidence; no live control is replaced."]},
            "decisions": [{"id": "accept-shadow-clockwork-candidate", "source": evidence[6], "status": "accepted", "summary": "Prepare one prevalidated hash-chained closeout reading without live publication."}],
            "claim_scope": ["One machine-observed source commit binds every prospective projection.", "No canonical authority file changes during the rehearsal."],
            "contract_evidence": [],
            "evidence": {"plans": evidence[:2], "findings": [evidence[5]], "closeouts": [], "acceptances": [evidence[6]], "receipts": [], "tests": [evidence[3]], "artifacts": [evidence[2], evidence[4]]},
            "unresolved_gates": ["Live canonical replacement and occupied native-Harness work remain closed."],
        },
        "journey": {"strategic_role": "Replace copied closeout facts with one typed reading", "outcome": "A hash-chained shadow generation and broker WorkOrder share causal time.", "evidence": evidence},
        "current_position": {
            "strategic_role": "Continue to default-off ordinary-practice admission-control architecture",
            "why_now": "The shadow control plane is measured before any live adoption.",
            "outcome": "Use the accepted preparer while Sol retains existing application authority.",
            "unlocks": ["Prepare the deferred default-off architecture tranche."],
            "does_not_solve": ["No practice, product, provider, deployment or protected ref is opened."],
            "evidence": evidence,
            "orientation_statement": "EMR4 has a provider-free shadow clockwork candidate; live controls remain exact and the deferred default-off product architecture is next.",
        },
        "next_operation": {
            "operation_id": "raisa-provider-free-default-off-ordinary-practice-canonical-check-in-admission-control-architecture",
            "active_tranche": "Provider-free default-off ordinary-practice canonical check-in admission-control architecture",
            "objective": "Freeze a still-disabled ordinary-practice admission state machine and its fail-closed operational controls.",
            "authority_source": "Accepted not-ready review and Yuri standing uninterrupted-development authority.",
            "next_stage": "freeze_the_narrowest_default_off_admission_control_architecture_plan",
        },
        "incidents": [],
        "broker": {"enabled": True, "posture": "provider_free_shadow"},
    }


def _fixture_latch(live_latch: dict, operation_id: str) -> dict:
    latch = copy.deepcopy(live_latch)
    latch["checkpoint"]["next_executable_stage"] = "run_immutable_shadow_fixture"
    latch.update(
        operation_id=operation_id, status="in_progress", resume_after_compaction=True,
        user_attention={"required": False, "reason": None},
        terminal_response={"permitted": False, "reason": "unfinished_authorized_operation"},
    )
    return latch


@pytest.fixture
def state() -> tuple[dict, dict, dict, dict]:
    graph = _load("orchestration/continuity/emr4-continuity-graph.json")
    manifest = _manifest(graph)
    live_latch = _load(
        "orchestration/continuity/ariadne-active-operation-latch/current.json"
    )
    return (
        graph,
        _load("orchestration/continuity/emr4-compass.json"),
        _fixture_latch(live_latch, manifest["operation_id"]),
        manifest,
    )


def test_plan_freezes_clockwork_efficacy_and_closed_surfaces() -> None:
    plan = (ROOT / "docs/ariadne-transactional-closeout-control-plane-consolidation-efficacy-rehearsal-plan.md").read_text(encoding="utf-8")
    threat = (ROOT / "docs/security/ariadne-transactional-closeout-control-plane-consolidation-efficacy-rehearsal-threat-model-delta.md").read_text(encoding="utf-8")
    for text in (plan, threat):
        assert "Date: 2026-08-19" in text
        assert "+10:00 (Australia/Brisbane)" in text
    for marker in ("source_anchor: current_head", "at least 50 percent fewer", "fewer than 1,002 physical lines", "provider-free", "No ordinary-practice enablement"):
        assert marker in plan
    assert all(f"TCP-{index:03d}" in threat for index in range(1, 13))


def test_historical_shadow_set_is_exact_legacy_baseline() -> None:
    result = tc.verify_historical_fixtures(
        _load(f"{BASE}/historical-shadow-fixtures.json"), repo_root=ROOT,
        graph=_load("orchestration/continuity/emr4-continuity-graph.json"),
        compass=_load("orchestration/continuity/emr4-compass.json"),
    )
    assert _load(f"{BASE}/historical-shadow-fixtures.json")["baseline_source"] == SOURCE
    assert result == {"status": "passed", "fixtures": [
        {"node_id": "raisa-provider-free-default-off-canonical-check-in-route-adapter-convergence-rehearsal", "status": "passed", "legacy_lines": 351},
        {"node_id": "ariadne-post-native-harness-successor-resolution-repair", "status": "passed", "legacy_lines": 325},
        {"node_id": "raisa-provider-free-read-only-ordinary-practice-canonical-check-in-admission-readiness-review", "status": "passed", "legacy_lines": 326},
    ], "legacy_files": 6, "legacy_lines": 1002}


def test_one_reading_derives_full_source_all_projections_and_broker_gear(
    state: tuple[dict, dict, dict, dict],
) -> None:
    graph, compass, latch, manifest = state
    assert "source_head" not in json.dumps(manifest)
    bundle = tc.prepare_transaction(manifest, repo_root=ROOT, graph=graph, compass=compass, active_latch=latch, allow_legacy_work_order_v1=True)
    assert bundle["source_commit"] == bundle["git_snapshot"]["head"]
    assert bundle["projections"]["graph"]["graph_revision"] == graph["graph_revision"] + 1
    assert bundle["projections"]["compass"]["map_revision"] == compass["map_revision"] + 1
    assert bundle["projections"]["latch"]["operation_id"] == manifest["next_operation"]["operation_id"]
    assert bundle["work_order"]["source_commit"] == bundle["source_commit"]
    assert bundle["work_order"]["allowed_tool_names"] == ["edit", "glob", "read"]
    assert bundle["work_order"]["previous_event_sha256"] == bundle["journal"][-1]["event_sha256"]
    assert bundle["work_order_sha256"] == tc.sha256(bundle["work_order"])
    schema = _load(f"{BASE}/control-plane.schema.json")
    Draft202012Validator.check_schema(schema)
    Draft202012Validator({**schema, "$ref": "#/$defs/manifest"}).validate(manifest)
    Draft202012Validator({**schema, "$ref": "#/$defs/work_order"}).validate(bundle["work_order"])
    tc.validate_bundle(bundle, repo_root=ROOT)


def test_command_bound_work_order_v2_derives_no_database_digests(
    state: tuple[dict, dict, dict, dict], tmp_path: Path,
) -> None:
    graph, compass, latch, manifest = state
    with pytest.raises(ValueError, match="command_bound_work_order_required"):
        tc.prepare_transaction(
            manifest,
            repo_root=ROOT,
            graph=graph,
            compass=compass,
            active_latch=latch,
        )
    commands = {
        "schema_version": COMMAND_MANIFEST_SCHEMA_VERSION,
        "commands": [
            {
                "id": "PF",
                "argv": [
                    sys.executable,
                    "-m",
                    "scripts.ariadne_provider_free_pytest",
                    "--repo-root",
                    str(ROOT),
                    "tests/test_ariadne_provider_free_pytest.py",
                ],
            }
        ],
    }
    admitted, admission = validate_execution_manifest_with_admission(
        commands, repo_root=ROOT, require_provider_free=True
    )
    bundle = tc.prepare_transaction(
        manifest,
        repo_root=ROOT,
        graph=graph,
        compass=compass,
        active_latch=latch,
        broker_command_manifest=commands,
    )

    order = bundle["work_order"]
    assert order["schema_version"] == tc.WORK_ORDER_COMMAND_BOUND_VERSION
    assert order["command_manifest_sha256"] == "sha256:" + command_manifest_sha256(
        admitted
    )
    assert admission is not None
    assert bundle["broker_command_manifest"] == admitted
    assert bundle["provider_free_no_database_admission"] == admission
    assert order["provider_free_no_database_admission_sha256"] == canonical_sha256(
        admission
    )
    work_order_schema = _load(
        "orchestration/continuity/ariadne-provider-free-no-database-manifest-runner-admission-repair/work-order-v2.schema.json"
    )
    Draft202012Validator.check_schema(work_order_schema)
    Draft202012Validator(work_order_schema).validate(order)
    tc.validate_bundle(bundle, repo_root=ROOT)
    published = tc.publish_shadow(
        bundle, repo_root=ROOT, target=tmp_path / "v2-command-bound-shadow"
    )
    assert {
        "command-manifest.json",
        "provider-free-no-database-admission.json",
        "work-order.json",
        "work-order.sha256",
    }.issubset(path.name for path in published.iterdir())

    drifted = copy.deepcopy(bundle)
    drifted["work_order"]["provider_free_no_database_admission_sha256"] = (
        "sha256:" + "0" * 64
    )
    drifted["work_order_sha256"] = tc.sha256(drifted["work_order"])
    with pytest.raises(ValueError, match="work_order_base_binding_invalid"):
        # The digest is schema-valid but no longer the engine-derived base that
        # anchors the final journal event.
        tc.validate_bundle(drifted, repo_root=ROOT)

    artifact_drift = copy.deepcopy(bundle)
    artifact_drift["provider_free_no_database_admission"]["status"] = (
        "revision_required"
    )
    with pytest.raises(ValueError, match="provider_free_admission_identity_invalid"):
        tc.validate_bundle(artifact_drift, repo_root=ROOT)


def test_observed_bookkeeping_defects_fail_before_publication(
    state: tuple[dict, dict, dict, dict], tmp_path: Path,
) -> None:
    graph, compass, latch, manifest = state
    derived = copy.deepcopy(manifest)
    derived["source_head"] = "1234567"
    asymmetric = copy.deepcopy(manifest)
    asymmetric["incidents"] = [{"incident_id": "aer-1", "source_id": "source-1", "peers": ["aer-2"]}, {"incident_id": "aer-2", "source_id": "source-2", "peers": []}]
    cutoff = copy.deepcopy(manifest)
    cutoff["source_cutoff"] = "stale-source"
    population = copy.deepcopy(manifest)
    population["incident_population"] = 566
    boundary = copy.deepcopy(manifest)
    boundary["next_operation"]["protected_boundaries"] = ["paraphrased boundary"]
    for candidate in (derived, asymmetric, cutoff, population, boundary):
        with pytest.raises(ValueError):
            tc.validate_manifest(candidate)
    stale = copy.deepcopy(latch)
    stale["operation_id"] = "different-operation"
    with pytest.raises(ValueError, match="active_operation_mismatch"):
        tc.prepare_transaction(manifest, repo_root=ROOT, graph=graph, compass=compass, active_latch=stale, allow_legacy_work_order_v1=True)
    missing_evidence = copy.deepcopy(manifest)
    missing_evidence["node"]["evidence"]["receipts"].append("docs/nonexistent-new-clockwork-evidence.md")
    with pytest.raises(ValueError, match="prospective_projection_invalid"):
        tc.prepare_transaction(missing_evidence, repo_root=ROOT, graph=graph, compass=compass, active_latch=latch, allow_legacy_work_order_v1=True)
    bundle = tc.prepare_transaction(manifest, repo_root=ROOT, graph=graph, compass=compass, active_latch=latch, allow_legacy_work_order_v1=True)
    live = [ROOT / "orchestration/continuity/emr4-continuity-graph.json", ROOT / "orchestration/continuity/emr4-compass.json", ROOT / "orchestration/continuity/ariadne-active-operation-latch/current.json"]
    before = [path.read_bytes() for path in live]
    for step in range(1, 9):
        target = tmp_path / f"failed-{step}"
        with pytest.raises(RuntimeError, match="injected_shadow_write_failure"):
            tc.publish_shadow(bundle, repo_root=ROOT, target=target, fail_after_write=step)
        assert not target.exists()
    assert before == [path.read_bytes() for path in live]
    with pytest.raises(ValueError, match="shadow_target_forbidden"):
        tc.publish_shadow(bundle, repo_root=ROOT, target=ROOT / ".git/forbidden-shadow")
    published = tc.publish_shadow(bundle, repo_root=ROOT, target=tmp_path / "published")
    assert len(list(published.iterdir())) == 8


def test_event_and_broker_chains_reject_reorder_or_tamper(
    state: tuple[dict, dict, dict, dict],
) -> None:
    graph, compass, latch, manifest = state
    bundle = tc.prepare_transaction(manifest, repo_root=ROOT, graph=graph, compass=compass, active_latch=latch, allow_legacy_work_order_v1=True)
    tampered = copy.deepcopy(bundle["journal"])
    tampered[1]["payload"]["source_commit"] = "2" * 40
    with pytest.raises(ValueError, match="event_digest_invalid"):
        tc.validate_event_chain(tampered)
    identity_drift = copy.deepcopy(bundle["journal"])
    identity_drift[1]["transaction_id"] = "txn-different"
    identity_drift[1]["event_sha256"] = tc.sha256(
        {key: value for key, value in identity_drift[1].items() if key != "event_sha256"}
    )
    with pytest.raises(ValueError, match="event_identity_drift"):
        tc.validate_event_chain(identity_drift)
    rebound = copy.deepcopy(bundle)
    rebound["work_order"]["transaction_id"] = "txn-different"
    rebound["work_order_sha256"] = tc.sha256(rebound["work_order"])
    with pytest.raises(ValueError, match="work_order_base_binding_invalid"):
        tc.validate_bundle(rebound, repo_root=ROOT)
    order = bundle["work_order"]
    events = []
    previous = order["previous_event_sha256"]
    for sequence, event_type in enumerate(("broker-ready", "broker-request-rejected"), start=order["next_sequence"]):
        event = {"event": event_type, "work_order_id": order["work_order_id"], "transaction_id": order["transaction_id"], "operation_id": order["operation_id"], "source_commit": order["source_commit"], "authority_sha256": order["authority_sha256"], "clock_sequence": sequence, "previous_event_sha256": previous}
        event["event_sha256"] = tc.sha256(event)
        events.append(event)
        previous = event["event_sha256"]
    tc.validate_broker_events(order, events)
    events[1]["clock_sequence"] += 1
    with pytest.raises(ValueError, match="broker_event_clock_invalid"):
        tc.validate_broker_events(order, events)


def test_candidate_maintained_surface_is_below_frozen_legacy_baseline() -> None:
    result = subprocess.run(["git", "diff", "--numstat", SOURCE, ACCEPTED_CANDIDATE, "--", *CANDIDATE_PATHS], cwd=ROOT, check=True, capture_output=True, text=True, encoding="utf-8")
    tracked_delta = {path: int(added) + int(deleted) for added, deleted, path in (line.split("\t") for line in result.stdout.splitlines() if line)}
    changed_lines = 0
    for path in CANDIDATE_PATHS:
        tracked = subprocess.run(["git", "ls-files", "--error-unmatch", path], cwd=ROOT, capture_output=True, check=False).returncode == 0
        changed_lines += tracked_delta[path] if tracked else len((ROOT / path).read_text(encoding="utf-8").splitlines())
    assert len(CANDIDATE_PATHS) < 6
    assert changed_lines < 1002


def test_controlled_efficacy_gate_passes_without_hidden_engine_cost(
    state: tuple[dict, dict, dict, dict],
) -> None:
    graph, compass, latch, manifest = state
    result = tc.measure_efficacy(
        repo_root=ROOT, manifest=manifest, graph=graph, compass=compass,
        latch=latch, fixtures=_load(f"{BASE}/historical-shadow-fixtures.json"),
        candidate_paths=CANDIDATE_PATHS, candidate_source=ACCEPTED_CANDIDATE,
    )
    assert result["status"] == "passed"
    assert result["defects"]["escaped"] == []
    assert result["retries"]["reduction_percent"] >= 50
    assert result["surface"]["candidate_files"] == 5
    assert result["surface"]["candidate_lines"] < 1002
    assert result["timing"] == {"reproduced": False, "acceptance_relevant": False}
    stored = _load(f"{BASE}/provider-free-efficacy-evidence.json")
    assert stored["timing"]["iterations"] == 20
    assert stored["timing"]["acceptance_relevant"] is False
    for key in ("status", "commands", "manual_fields", "defects", "retries", "surface", "canonical_writes_before_validation", "hand_copied_git_object_ids"):
        assert stored[key] == result[key]
