"""Advance Continuity and Compass for the pure route-adapter rehearsal."""

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
NODE_ID = (
    "raisa-provider-free-unmounted-pure-route-adapter-differential-rehearsal"
)
PARENT = "raisa-provider-free-unmounted-legacy-route-convergence-kernel-interface"
SOURCE_HEAD = "beb4e65cddf72437948d72e08dd18c2ea4f0c609"
UPDATED_AT = "2026-08-12T00:00:00Z"
PLAN = (
    "docs/raisa-provider-free-unmounted-pure-route-adapter-"
    "differential-rehearsal-plan.md"
)
DESIGN = (
    "docs/raisa-provider-free-unmounted-pure-route-adapter-"
    "differential-rehearsal-design.md"
)
THREAT = (
    "docs/security/raisa-provider-free-unmounted-pure-route-adapter-"
    "differential-rehearsal-threat-model-delta.md"
)
PACKET_DIR = (
    "orchestration/continuity/"
    "raisa-provider-free-unmounted-pure-route-adapter-differential-rehearsal/"
)
CONTRACT = PACKET_DIR + "contract.json"
SCHEMA = PACKET_DIR + "contract.schema.json"
CLOSEOUT = (
    "docs/raisa-provider-free-unmounted-pure-route-adapter-"
    "differential-rehearsal-closeout.md"
)
ACCEPTANCE = (
    "orchestration/agent_inbox/codex/"
    "raisa-pure-route-adapter-differential-rehearsal-sol-acceptance.md"
)
PREPLANNING_RECEIPT = (
    "orchestration/agent_inbox/codex/"
    "raisa-pure-route-adapter-differential-rehearsal-preplanning-receipt.json"
)
PRECOMMIT_RECEIPT = (
    "orchestration/agent_inbox/codex/"
    "raisa-pure-route-adapter-differential-rehearsal-candidate-precommit-receipt.json"
)
MAILBOX = (
    "orchestration/human_inbox/yuri/"
    "2026-08-12--pure-route-adapter-differential-rehearsal.md"
)
TEST = (
    "tests/test_raisa_provider_free_unmounted_pure_route_adapter_"
    "differential_rehearsal_continuity.py"
)
UPDATER = (
    "scripts/raisa_provider_free_unmounted_pure_route_adapter_"
    "differential_rehearsal_continuity_update.py"
)


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def _evidence() -> list[str]:
    return [
        PLAN,
        DESIGN,
        THREAT,
        CONTRACT,
        SCHEMA,
        CLOSEOUT,
        ACCEPTANCE,
        PREPLANNING_RECEIPT,
        PRECOMMIT_RECEIPT,
        MAILBOX,
    ]


def _node() -> dict[str, Any]:
    return {
        "id": NODE_ID,
        "title": "Provider-free unmounted pure route-adapter differential rehearsal",
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
                "This is a provider-free unmounted authored-synthetic pure adapter rehearsal.",
                "It imports or changes no application route and executes no kernel command.",
                "A complete hypothetical raw envelope grants no current route eligibility.",
            ],
        },
        "decisions": [
            {
                "id": "accept-pure-route-adapter-differential-rehearsal",
                "source": CLOSEOUT,
                "status": "accepted",
                "summary": "Accept exact pure mapping equivalence and current-raw missing-control rejection without runtime wiring.",
            }
        ],
        "claim_scope": [
            "Exactly nine adapters, four synthetic intents and thirteen scenarios are covered.",
            "Nine complete candidates map all eighteen fields and four current raw profiles reject with three exact gap codes.",
            "Four differential groups match on all seventeen semantic fields; only route_adapter_id differs.",
            "All forty-five hostile mutations fail closed.",
            "All candidates remain inert and runtime-ineligible.",
        ],
        "contract_evidence": [],
        "evidence": {
            "plans": [PLAN],
            "findings": [DESIGN, THREAT],
            "closeouts": [CLOSEOUT, MAILBOX],
            "acceptances": [ACCEPTANCE],
            "receipts": [PREPLANNING_RECEIPT, PRECOMMIT_RECEIPT],
            "tests": [
                "tests/test_raisa_provider_free_unmounted_pure_route_adapter_differential_rehearsal.py",
                TEST,
            ],
            "artifacts": [CONTRACT, SCHEMA, UPDATER],
        },
        "unresolved_gates": [
            "No application route adapter, default-off shadow observer or client behavior is wired.",
            "No production precondition token, database fence, idempotency/audit persistence or RLS behavior is proved.",
            "Database/source/watcher/event access, patient/product data, provider, commands, deployment, Pages and protected refs remain closed.",
        ],
    }


def main() -> int:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 247 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 248
        graph["updated_at"] = UPDATED_AT
    elif graph["graph_revision"] == 248 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
    else:
        raise SystemExit("Unexpected pure route-adapter Continuity predecessor")
    _write(GRAPH, graph)

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Prove route-specific envelopes preserve one conditional-command meaning",
        "outcome": "Pure differential rehearsal passes; a default-off non-enforcing shadow-comparison architecture is next.",
        "evidence": _evidence(),
    }
    if (
        compass["map_revision"] == 229
        and compass["source_graph_revision"] == 247
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 230
        and compass["source_graph_revision"] == 248
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected pure route-adapter Compass predecessor")

    for horizon in compass["programme_support_horizon"]:
        if horizon["id"] == "raisa-practice-context-fabric":
            horizon["status"] = "active"
            horizon["prerequisites"] = [
                "Freeze a provider-free unmounted default-off non-enforcing shadow-comparison architecture.",
                "Prove any future observer cannot gate, mutate or alter a route response before runtime wiring is considered.",
                "Then prove ordinary and fallback client proposal/confirm parity before raw-route convergence.",
                "Select and prove a database-owned create schedule fence before create convergence.",
                "Retain Durable Event and Cue Delivery as a later observability-first extension.",
            ]
            for item in journey["evidence"]:
                if item not in horizon["evidence"]:
                    horizon["evidence"].append(item)
            break
    else:
        raise SystemExit("Practice Context Fabric horizon item missing")

    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": "Pure route mapping proved; inert shadow-comparison boundary next",
        "why_now": "The common kernel and pure adapters now agree, so the next safe question is how to observe differences without influencing live behavior.",
        "outcome": "Nine complete candidates map, four current raw profiles fail with three exact gaps, and all 45 hostile mutations are contained.",
        "unlocks": [
            "Define a default-off non-enforcing route-local comparison record with minimized authored-synthetic fields.",
            "Prove the observer cannot gate a request, mutate a response, invoke the kernel or affect a write.",
        ],
        "does_not_solve": [
            "Application route wiring, HTTP compatibility, database fencing, persistent idempotency/audit or client migration.",
            "Durable cue delivery, CF-D2, patient/product data, providers, commands, deployment, Pages or protected refs.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 248 / Compass 230. The provider-free unmounted "
        "pure route-adapter rehearsal maps nine complete candidates, rejects four "
        "current raw profiles with three exact gaps and contains all 45 hostile "
        "mutations. The next safe tranche is the default-off non-enforcing "
        "shadow-comparison architecture."
    )
    limit = (
        "The pure route-adapter result is authored-synthetic and inert; complete "
        "mapping does not grant current raw-route or runtime eligibility."
    )
    if limit not in compass["map_limits"]:
        compass["map_limits"].insert(0, limit)
    compass["source_graph_revision"] = 248
    compass["map_revision"] = 230
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)

    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
