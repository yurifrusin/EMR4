"""Advance Continuity and Compass for compatibility-consumer admission."""

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
NODE_ID = "raisa-provider-free-compatibility-consumer-kernel-convergence-admission-review"
PARENT = "raisa-provider-free-ordinary-fallback-diary-client-proposal-confirm-parity"
SOURCE_HEAD = "9c7444ecce69b51ca5cac80818e8997724a11f13"
UPDATED_AT = "2026-08-12T00:00:00Z"
PLAN = "docs/raisa-provider-free-compatibility-consumer-kernel-convergence-admission-review-plan.md"
FINDING = "docs/raisa-provider-free-compatibility-consumer-kernel-convergence-admission-review.md"
THREAT = "docs/security/raisa-provider-free-compatibility-consumer-kernel-convergence-admission-review-threat-model-delta.md"
CLOSEOUT = "docs/raisa-provider-free-compatibility-consumer-kernel-convergence-admission-review-closeout.md"
ACCEPTANCE = "orchestration/agent_inbox/codex/raisa-compatibility-consumer-kernel-convergence-admission-review-sol-acceptance.md"
PREPLANNING = "orchestration/agent_inbox/codex/raisa-provider-free-compatibility-consumer-kernel-convergence-admission-review-preplanning-receipt.json"
PRECOMMIT = "orchestration/agent_inbox/codex/raisa-provider-free-compatibility-consumer-kernel-convergence-admission-review-precommit-receipt.json"
MAILBOX = "orchestration/human_inbox/yuri/2026-08-12--compatibility-consumer-kernel-convergence-admission-review.md"
INVENTORY = "orchestration/continuity/raisa-provider-free-compatibility-consumer-kernel-convergence-admission-review/consumer-and-preservation-inventory.json"
TEST = "tests/test_raisa_provider_free_compatibility_consumer_kernel_convergence_admission_review_continuity.py"
UPDATER = "scripts/raisa_provider_free_compatibility_consumer_kernel_convergence_admission_review_continuity_update.py"


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def _evidence() -> list[str]:
    return [PLAN, FINDING, THREAT, INVENTORY, CLOSEOUT, ACCEPTANCE, PREPLANNING, PRECOMMIT, MAILBOX]


def _node() -> dict[str, Any]:
    return {
        "id": NODE_ID,
        "title": "Provider-free compatibility-consumer and kernel-convergence admission review",
        "kind": "foundation",
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
                "This is provider-free read-only/static admission evidence.",
                "All four raw compatibility routes remain mounted and unchanged.",
                "External consumers remain unknown and no retirement or header rollout is authorized.",
            ],
        },
        "decisions": [{
            "id": "accept-compatibility-consumer-kernel-convergence-admission-review",
            "source": CLOSEOUT,
            "status": "accepted",
            "summary": "Accept the exact consumer census, preservation matrix and status confirm-first direction.",
        }],
        "claim_scope": [
            "Zero committed product/runtime/import/recovery/migration/operational raw HTTP consumers are found.",
            "Exactly 126 conformance call expressions remain in 21 test/review files and four direct database fixture obligations are separate.",
            "External consumers remain unknown and all four routes stay mounted in default audit mode.",
            "Status confirm-first is selected without changing raw status or implementing a kernel.",
            "Seven tranche, 167 dependency, 184 current behavior and canonical 191 fast-profile tests pass.",
        ],
        "contract_evidence": [],
        "evidence": {
            "plans": [PLAN],
            "findings": [FINDING, THREAT],
            "closeouts": [CLOSEOUT, MAILBOX],
            "acceptances": [ACCEPTANCE],
            "receipts": [PREPLANNING, PRECOMMIT],
            "tests": [
                "tests/test_raisa_provider_free_compatibility_consumer_kernel_convergence_admission_review.py",
                TEST,
            ],
            "artifacts": [INVENTORY, UPDATER],
        },
        "unresolved_gates": [
            "Forty-five stale tests require a test-only temporal/idempotency readiness repair before status-kernel work.",
            "External consumer readiness, route retirement and header-mode rollout remain unproved.",
            "Kernel execution, raw convergence and create schedule fencing remain closed.",
            "Product data, providers, deployment, Pages and protected refs remain closed.",
        ],
    }


def main() -> int:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 253 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 254
        graph["updated_at"] = UPDATED_AT
    elif graph["graph_revision"] == 254 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
    else:
        raise SystemExit("Unexpected compatibility admission Continuity predecessor")
    _write(GRAPH, graph)

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Separate real compatibility obligations from unknown external consumers before convergence",
        "outcome": "Repository consumers are exactly classified; test-harness readiness repair is next before status-kernel protocol work.",
        "evidence": _evidence(),
    }
    if (
        compass["map_revision"] == 235
        and compass["source_graph_revision"] == 253
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 236
        and compass["source_graph_revision"] == 254
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected compatibility admission Compass predecessor")

    for horizon in compass["programme_support_horizon"]:
        if horizon["id"] == "raisa-practice-context-fabric":
            horizon["status"] = "active"
            horizon["prerequisites"] = [
                "Repair the 45 stale temporal/idempotency conformance tests without changing application behavior.",
                "Prove all 311 ordinary compatibility tests green.",
                "Rehearse the unmounted status transaction-kernel protocol before any runtime convergence.",
                "Keep raw status unchanged until precondition, confirmation and idempotency ingress is accepted.",
                "Select and prove a database-owned create schedule fence before create convergence.",
            ]
            for item in journey["evidence"]:
                if item not in horizon["evidence"]:
                    horizon["evidence"].append(item)
            break
    else:
        raise SystemExit("Practice Context Fabric horizon item missing")

    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": "Compatibility obligations classified; conformance readiness next",
        "why_now": "The native client is clean, and the remaining repository consumers can now be made trustworthy before status-kernel protocol work.",
        "outcome": "Zero committed system callers, 126 conformance calls, four direct fixtures and unknown external consumers are distinguished without changing a route.",
        "unlocks": [
            "Repair only stale test clocks and proposal idempotency headers.",
            "Then rehearse status transaction-kernel semantics in a provider-free unmounted protocol.",
        ],
        "does_not_solve": [
            "External-consumer readiness, route retirement, header-mode rollout or raw-route convergence.",
            "Kernel runtime, create schedule fencing, product data, deployment, Pages or protected refs.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 254 / Compass 236. The provider-free compatibility-consumer admission review "
        "finds zero committed system raw-route callers, preserves unknown external consumers, selects status confirm-first "
        "and names a 45-test temporal/idempotency harness repair as the next gate."
    )
    for limit in (
        "Zero committed compatibility consumers does not prove absence of external consumers.",
        "Forty-five stale tests are a harness repair obligation, not authority to weaken temporal or idempotency controls.",
    ):
        if limit not in compass["map_limits"]:
            compass["map_limits"].insert(0, limit)
    compass["source_graph_revision"] = 254
    compass["map_revision"] = 236
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)

    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
