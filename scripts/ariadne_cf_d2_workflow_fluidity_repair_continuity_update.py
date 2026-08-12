"""Advance Continuity and Compass for the accepted CF-D2 workflow repair."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import ariadne_compass


GRAPH = ROOT / "orchestration/continuity/emr4-continuity-graph.json"
COMPASS = ROOT / "orchestration/continuity/emr4-compass.json"
REPORT = ROOT / "docs/ariadne-compass-current.md"
NODE_ID = "ariadne-cf-d2-workflow-incident-diagnosis-and-fluidity-repair"
PARENT = "raisa-provider-free-disposable-postgresql-durability-concurrency-rehearsal"
SOURCE_HEAD = "018099dd6c5f0502121360732feb602252eb34cc"
UPDATED_AT = "2026-08-12T00:00:00Z"
PLAN = "docs/ariadne-cf-d2-workflow-incident-diagnosis-and-fluidity-repair-plan.md"
DIAGNOSIS = "docs/ariadne-cf-d2-workflow-incident-diagnosis.md"
POLICY = "orchestration/harness_settings/evidence_led_workflow.yaml"
GATE = "scripts/ariadne_evidence_gate.py"
CLOSEOUT = (
    "docs/ariadne-cf-d2-workflow-incident-diagnosis-and-fluidity-repair-closeout.md"
)
ACCEPTANCE = (
    "orchestration/agent_inbox/codex/"
    "ariadne-cf-d2-workflow-fluidity-repair-sol-acceptance.md"
)
REVIEW = (
    "orchestration/agent_inbox/antigravity/"
    "ariadne-cf-d2-workflow-fluidity-final-review-v2-receipt.json"
)
MAILBOX = (
    "orchestration/human_inbox/yuri/"
    "2026-08-12--cf-d2-workflow-incident-diagnosis-and-fluidity-repair.md"
)
TEST = "tests/test_ariadne_cf_d2_workflow_fluidity_repair_continuity.py"
UPDATER = "scripts/ariadne_cf_d2_workflow_fluidity_repair_continuity_update.py"


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def _evidence() -> list[str]:
    return [PLAN, DIAGNOSIS, POLICY, GATE, CLOSEOUT, ACCEPTANCE, REVIEW, MAILBOX]


def _node() -> dict[str, Any]:
    return {
        "id": NODE_ID,
        "title": "Ariadne CF-D2 workflow incident diagnosis and fluidity repair",
        "kind": "maintenance",
        "status": "accepted",
        "created_at": UPDATED_AT,
        "updated_at": UPDATED_AT,
        "coordinates": {
            "git_ref": "codex/ariadne-bernie-davida-parallel-seam",
            "source_head": SOURCE_HEAD,
            "thread_id": None,
            "worktree_role": "task",
        },
        "relationships": [{"node_id": PARENT, "relation": "builds_on"}],
        "authority": {
            "authorized_openings": [],
            "notes": [
                "This is a repository-only workflow maintenance result; it does not accept or reopen CF-D2.",
                "Hard authority, data, effect, stop, cleanup, claim and protected-ref controls remain fail closed.",
                "Adaptive flow may improvise inside a frozen boundary only while each retry creates discriminating evidence.",
            ],
        },
        "decisions": [
            {
                "id": "accept-cf-d2-workflow-incident-diagnosis-and-fluidity-repair",
                "source": CLOSEOUT,
                "status": "accepted",
                "summary": "Accept the evidence-led workflow repair while leaving CF-D2 stopped and unproved.",
            }
        ],
        "claim_scope": [
            "Workflow ceremony amplified genuine CF-D2 complexity by permitting corrections without distinct observations for all viable causes.",
            "The repaired diagnostic gate rejects nondiscriminating retries and unsupported exclusive-cause claims.",
            "The repaired verifier gate binds exact structured argv and admits pass only when every individual exit code is zero.",
            "Receipt events and exact Git candidate identities are discoverable machine outputs rather than memory tasks.",
            "CF-D2, crash/restart and unknown-commit recovery remain unproved.",
        ],
        "contract_evidence": [],
        "evidence": {
            "plans": [PLAN],
            "findings": [DIAGNOSIS],
            "closeouts": [CLOSEOUT, MAILBOX],
            "acceptances": [ACCEPTANCE],
            "receipts": [REVIEW],
            "tests": [
                "tests/test_ariadne_evidence_gate.py",
                "tests/test_ariadne_antigravity.py",
                "tests/test_ariadne_orchestrator_preflight.py",
                "tests/test_ariadne_verifier_execution_policy.py",
                "tests/test_ariadne_agent_error_register.py",
                TEST,
            ],
            "artifacts": [POLICY, GATE, UPDATER],
        },
        "unresolved_gates": [
            "CF-D2 attempt 003 and every further runtime probe remain ineligible without a new observability-first authority decision.",
            "Key rotation and retention/purge remain dependency-blocked because CF-D2 did not pass.",
            "No dependency-satisfied automatic programme tranche remains; Yuri must select the next independent direction.",
            "Operational database/source access, real/product/patient/clinical data, provider tools, commands, deployment, Pages and protected refs remain closed.",
        ],
    }


def main() -> int:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 243 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 244
        graph["updated_at"] = UPDATED_AT
    elif graph["graph_revision"] == 244 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
    else:
        raise SystemExit("Unexpected workflow-repair Continuity predecessor")
    _write(GRAPH, graph)

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Repair diagnostic flow after stopped CF-D2 without weakening hard safety boundaries",
        "outcome": "Evidence-led gates now require discriminating observations and exact command results; CF-D2 remains unproved and the next programme direction requires Yuri's choice.",
        "evidence": _evidence(),
    }
    if (
        compass["map_revision"] == 225
        and compass["source_graph_revision"] == 243
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 226
        and compass["source_graph_revision"] == 244
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected workflow-repair Compass predecessor")

    for horizon in compass["programme_support_horizon"]:
        if horizon["id"] == "raisa-practice-context-fabric":
            horizon["status"] = "blocked"
            horizon["prerequisites"] = [
                "CF-D2 restart and unknown-commit recovery remains unproved and closed.",
                "Yuri must choose an independent programme direction or explicitly authorize a new observability-first CF-D2 architecture.",
                "Key rotation and retention/purge remain dependency-blocked.",
            ]
            for item in journey["evidence"]:
                if item not in horizon["evidence"]:
                    horizon["evidence"].append(item)
            break
    else:
        raise SystemExit("Practice Context Fabric horizon item missing")

    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": "Evidence-led workflow repair accepted; independent programme fork required",
        "why_now": "CF-D2 exhausted its bounded diagnostic path without discriminating the remaining anchor assertions, and Yuri requested a workflow incident diagnosis before choosing another direction.",
        "outcome": "Hard safety gates remain intact while adaptive work now stops before nondiscriminating corrections or retries.",
        "unlocks": [
            "Choose a separately valuable product or architecture direction without carrying CF-D2 ceremony into it.",
            "If explicitly authorized later, design an observability-first CF-D2 architecture whose outcomes distinguish every viable assertion before runtime.",
        ],
        "does_not_solve": [
            "The unresolved CF-D2 anchor-internal cause, crash/restart or unknown-commit recovery.",
            "Key rotation, retention/purge, long-lived persistence or operational database wiring.",
            "Patient/product/clinical data, provider tools, commands, deployment, Pages or protected-ref movement.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 244 / Compass 226. The CF-D2 workflow incident "
        "diagnosis and evidence-led fluidity repair pass, while CF-D2 itself "
        "remains stopped and unproved. No automatic durability tranche is "
        "dependency-satisfied; Yuri must select the next independent programme direction."
    )
    limit = "The workflow repair proves discriminating diagnostic and exact review admission controls; it does not prove the unresolved CF-D2 database behavior."
    if limit not in compass["map_limits"]:
        compass["map_limits"].insert(0, limit)
    compass["source_graph_revision"] = 244
    compass["map_revision"] = 226
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)

    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
