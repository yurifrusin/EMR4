"""Advance Continuity and Compass for the post-CF-D2 orientation."""

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
NODE_ID = "raisa-post-cf-d2-compass-baton-orientation"
PARENT = (
    "raisa-provider-free-disposable-postgresql-cf-d2-event-cue-behavior-transaction-rehearsal"
)
SOURCE_HEAD = "edba8f57380a48fd98decc332608349f2d9012e6"
UPDATED_AT = "2026-08-13T11:25:00Z"
PLAN = "docs/raisa-post-cf-d2-compass-baton-orientation-plan.md"
FINDING = "docs/raisa-post-cf-d2-compass-baton-orientation.md"
TEST = "tests/test_raisa_post_cf_d2_compass_baton_orientation.py"
UPDATER = "scripts/raisa_post_cf_d2_compass_baton_orientation_continuity_update.py"
CONTINUITY_TEST = "tests/test_raisa_post_cf_d2_compass_baton_orientation_continuity.py"
CLOSEOUT = "docs/raisa-post-cf-d2-compass-baton-orientation-closeout.md"
ACCEPTANCE = (
    "orchestration/agent_inbox/codex/"
    "raisa-post-cf-d2-compass-baton-orientation-sol-acceptance.md"
)
MAILBOX = (
    "orchestration/human_inbox/yuri/"
    "2026-08-13--post-cf-d2-compass-baton-orientation.md"
)
RECEIPTS = [
    "orchestration/agent_inbox/codex/raisa-post-cf-d2-compass-baton-orientation-preplanning-receipt.json",
    "orchestration/agent_inbox/codex/raisa-post-cf-d2-compass-baton-orientation-candidate-precommit-receipt.json",
    "orchestration/agent_inbox/codex/raisa-post-cf-d2-compass-baton-orientation-preacceptance-receipt.json",
]


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def _evidence() -> list[str]:
    return [
        PLAN,
        FINDING,
        TEST,
        CLOSEOUT,
        ACCEPTANCE,
        MAILBOX,
        *RECEIPTS,
    ]


def _node() -> dict[str, Any]:
    return {
        "id": NODE_ID,
        "title": "Read-only post-CF-D2 Compass and baton orientation",
        "kind": "review",
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
                "Repository-local read-only product/programme orientation; no product behavior or runtime changed.",
                "The selected successor reuses the accepted status proposal/confirm family and adds no command authority.",
                "CF-D2 remains an optional acceleration layer; source truth and command-time authority remain the correctness kernel.",
            ],
        },
        "decisions": [
            {
                "id": "select-reception-one-selected-appointment-status-action-composition",
                "source": ACCEPTANCE,
                "status": "accepted",
                "summary": "Select one provider-free visible Reception One composition over the existing status interaction as the narrowest dependency-satisfied successor.",
            }
        ],
        "claim_scope": [
            "Exact source inspection proves Reception One appointment status is read-only and its bridge has no status action.",
            "The ordinary Diary already owns the accepted visible status proposal/confirm interaction and raw fallback remains absent.",
            "Stage 3B participants, patient channels, another event or command family and operational CF-D2 runtime remain separately closed.",
            "Four orientation assertions, 91 focused tests and the 193-test canonical fast profile pass.",
        ],
        "contract_evidence": [],
        "evidence": {
            "plans": [PLAN],
            "findings": [FINDING],
            "closeouts": [CLOSEOUT, MAILBOX],
            "acceptances": [ACCEPTANCE],
            "receipts": RECEIPTS,
            "tests": [TEST, CONTINUITY_TEST],
            "artifacts": [UPDATER],
        },
        "unresolved_gates": [
            "The selected status-action composition remains unimplemented until its own freshly rehydrated plan and evidence pass.",
            "Representative staff execution still requires Yuri's cohort nomination and reopening.",
            "External patient channels, other events/commands, watcher/runtime, product data, providers, deployment, production and release remain closed.",
        ],
    }


def main() -> int:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 281 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 282
        graph["updated_at"] = UPDATED_AT
    elif graph["graph_revision"] == 282 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
    else:
        raise SystemExit("Unexpected post-CF-D2 orientation Continuity predecessor")
    _write(GRAPH, graph)

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Reorient from the completed CF-D2 serial foundation to the narrowest already-supported visible Reception One improvement",
        "outcome": "The provider-free Reception One selected-appointment status-action composition is selected without opening new command or runtime authority.",
        "evidence": _evidence(),
    }
    if (
        compass["map_revision"] == 263
        and compass["source_graph_revision"] == 281
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 264
        and compass["source_graph_revision"] == 282
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected post-CF-D2 orientation Compass predecessor")

    for horizon in compass["programme_support_horizon"]:
        if horizon["id"] == "raisa-practice-context-fabric":
            horizon["status"] = "active"
            horizon["prerequisites"] = [
                "Preserve source-owned truth and command-time current-authority checks as the correctness kernel.",
                "Preserve the accepted CF-D2 observability, admission, representation, inert-DDL, parse/catalogue and serial behavior evidence.",
                "Treat event/cue durability as an optional later acceleration layer; visible product work does not wait for watcher runtime.",
                "Keep concurrency, restart, watcher/source access, persistence/runtime, product data and operational retention separately closed.",
            ]
            for item in journey["evidence"]:
                if item not in horizon["evidence"]:
                    horizon["evidence"].append(item)
            break
    else:
        raise SystemExit("Practice Context Fabric horizon item missing")

    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": "The completed durability foundation is reconciled with the next visible Reception One product step",
        "why_now": "Reception One already shows selected appointment status and the ordinary Diary already owns the accepted status command interaction, leaving one small composition seam.",
        "outcome": "The provider-free selected-appointment status-action composition is frozen as the next dependency-satisfied tranche.",
        "unlocks": [
            "Freeze and execute the provider-free Reception One selected-appointment status-action composition.",
            "Reuse the existing status vocabulary, proposal/confirm interaction and fresh Diary reload without a second command path.",
            "Return to visible product work while retaining CF-D2 as a separately closed future acceleration extension.",
        ],
        "does_not_solve": [
            "The selected visible status composition is not yet implemented or rendered.",
            "Representative staff execution, first patient channel and another Diary event family still require their recorded user decisions.",
            "Watcher/runtime, product data, providers, new commands, deployment, production and release remain closed.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 282 / Compass 264. The post-CF-D2 read-only "
        "orientation selects a provider-free Reception One selected-appointment "
        "status-action composition as the next visible tranche. It reuses the "
        "accepted status proposal/confirm family; CF-D2 remains a separately "
        "closed optional acceleration layer."
    )
    limit = (
        "The post-CF-D2 orientation selects but does not implement the Reception One status-action composition; it opens no product, runtime, data, provider or command authority."
    )
    if limit not in compass["map_limits"]:
        compass["map_limits"].insert(0, limit)
    compass["source_graph_revision"] = 282
    compass["map_revision"] = 264
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)

    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
