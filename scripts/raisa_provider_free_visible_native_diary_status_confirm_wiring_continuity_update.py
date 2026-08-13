"""Advance Continuity and Compass for visible Diary status-confirm wiring."""

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
NODE_ID = "raisa-provider-free-visible-native-diary-status-confirm-wiring"
PARENT = "raisa-channel-neutral-patient-interaction-foundation"
SOURCE_HEAD = "bed49be3d78d79207857b3d3a044cebd334112dc"
UPDATED_AT = "2026-08-13T05:42:33Z"
PLAN = "docs/raisa-provider-free-visible-native-diary-status-confirm-wiring-plan.md"
THREAT = (
    "docs/security/"
    "raisa-provider-free-visible-native-diary-status-confirm-wiring-threat-model-delta.md"
)
CLOSEOUT = "docs/raisa-provider-free-visible-native-diary-status-confirm-wiring-closeout.md"
ACCEPTANCE = (
    "orchestration/agent_inbox/codex/"
    "raisa-provider-free-visible-native-diary-status-confirm-wiring-sol-acceptance.md"
)
MAILBOX = (
    "orchestration/human_inbox/yuri/"
    "2026-08-13--visible-native-diary-status-confirm-wiring.md"
)
BASE = (
    "orchestration/continuity/"
    "raisa-provider-free-visible-native-diary-status-confirm-wiring/"
)
EVIDENCE = BASE + "visible-status-confirm-evidence.json"
EVIDENCE_SCHEMA = BASE + "visible-status-confirm-evidence.schema.json"
JS = "docs/diary/diary.js"
CSS = "docs/diary/diary.css"
HTML = "docs/diary/diary.html"
BROWSER_TEST = "review/test_diary_smoke.py"
TEST = "tests/test_raisa_provider_free_visible_native_diary_status_confirm_wiring.py"
SECURITY_TEST = "tests/test_diary_security_hardening.py"
CONTINUITY_TEST = (
    "tests/test_raisa_provider_free_visible_native_diary_status_confirm_wiring_continuity.py"
)
UPDATER = (
    "scripts/raisa_provider_free_visible_native_diary_status_confirm_wiring_continuity_update.py"
)
RECEIPTS = [
    "orchestration/agent_inbox/codex/raisa-provider-free-visible-native-diary-status-confirm-wiring-preplanning-receipt.json",
    "orchestration/agent_inbox/codex/raisa-provider-free-visible-native-diary-status-confirm-wiring-preacceptance-receipt.json",
]


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def _evidence() -> list[str]:
    return [
        PLAN,
        THREAT,
        HTML,
        CSS,
        JS,
        EVIDENCE,
        EVIDENCE_SCHEMA,
        BROWSER_TEST,
        TEST,
        SECURITY_TEST,
        CLOSEOUT,
        ACCEPTANCE,
        MAILBOX,
        *RECEIPTS,
    ]


def _node() -> dict[str, Any]:
    return {
        "id": NODE_ID,
        "title": "Provider-free visible native Diary status-confirm wiring",
        "kind": "implementation",
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
                "The existing backend status-confirm command remains the sole write authority.",
                "No route, raw fallback, database/source, product data, patient channel, provider, deployment or protected-ref authority was opened.",
            ],
        },
        "decisions": [
            {
                "id": "accept-visible-native-diary-status-confirm-wiring",
                "source": ACCEPTANCE,
                "status": "accepted",
                "summary": "Accept truthful responsive staff status proposal/confirm interaction over the existing backend command.",
            }
        ],
        "claim_scope": [
            "Safe routine status changes remain dialog-free; warning and terminal changes require explicit labelled confirmation.",
            "Blocked, cancelled, stale and rejected changes restore prior truth, clear busy state and expose no raw fallback.",
            "Desktop, tablet, phone, keyboard, focus and interruption behavior pass with zero console warnings or errors.",
            "Four route-intercepted status cases, 144 full Diary tests, 81 focused tests and the 193-test canonical fast profile pass.",
        ],
        "contract_evidence": [
            {
                "contract_id": "combined-patient-practitioner-time-duration-intent",
                "status": "satisfied",
                "evidence": [PLAN, EVIDENCE, BROWSER_TEST, CLOSEOUT],
                "note": "The status-only interaction preserves the accepted appointment identity, practitioner, time and duration projection while proposing and confirming only one status field.",
            },
            {
                "contract_id": "committed-reschedule-availability-reconciliation",
                "status": "satisfied",
                "evidence": [PLAN, EVIDENCE, BROWSER_TEST, CLOSEOUT],
                "note": "Successful status confirmation reloads authoritative Diary truth; late, duplicate or absent event cues remain non-authoritative and CF-D2 stays separately closed.",
            },
        ],
        "evidence": {
            "plans": [PLAN, THREAT],
            "findings": [EVIDENCE],
            "closeouts": [CLOSEOUT, MAILBOX],
            "acceptances": [ACCEPTANCE],
            "receipts": RECEIPTS,
            "tests": [BROWSER_TEST, TEST, SECURITY_TEST, CONTINUITY_TEST],
            "artifacts": [HTML, CSS, JS, EVIDENCE_SCHEMA, UPDATER],
        },
        "unresolved_gates": [
            "The rendered smoke client and intercepted browser cases are not live-backend evidence; backend proof remains inherited from its accepted source.",
            "CF-D2 restart, unknown-commit and durable event/cue delivery remain unproved and reopen only through a fresh observability-first plan.",
            "Other commands, external patient clients, real identity, patient/product data, providers, deployment, production, release, Pages and protected refs remain closed.",
        ],
    }


def main() -> int:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 274 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 275
        graph["updated_at"] = UPDATED_AT
    elif graph["graph_revision"] == 275 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
    else:
        raise SystemExit("Unexpected visible status-confirm Continuity predecessor")
    _write(GRAPH, graph)

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Make the accepted status command truthful and usable in Reception One",
        "outcome": "Visible staff status-confirm behavior passes; its cue and reconciliation needs now bound the next observability-first durability plan.",
        "evidence": _evidence(),
    }
    if (
        compass["map_revision"] == 256
        and compass["source_graph_revision"] == 274
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 257
        and compass["source_graph_revision"] == 275
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected visible status-confirm Compass predecessor")

    for horizon in compass["programme_support_horizon"]:
        if horizon["id"] == "raisa-practice-context-fabric":
            horizon["status"] = "active"
            horizon["prerequisites"] = [
                "Preserve accepted conditional-command and status-confirm route correctness.",
                "Use the accepted visible staff status-confirm boundary to specify cue, lag and reconciliation evidence.",
                "Keep future patient channels behind the accepted identity, assurance, recovery, projection and confirmation foundation.",
                "Return to durable event/cue delivery only through a fresh provider-free observability-first CF-D2 plan; events remain acceleration hints, not command evidence.",
            ]
            for item in journey["evidence"]:
                if item not in horizon["evidence"]:
                    horizon["evidence"].append(item)
            break
    else:
        raise SystemExit("Practice Context Fabric horizon item missing")

    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": "First visible staff status command complete; observability-first cue planning next",
        "why_now": "The UI now identifies the exact checking, confirmation, non-change, commit and refresh states that durable event delivery may accelerate without owning correctness.",
        "outcome": "Reception One visibly preserves proposal versus current-truth semantics across safe, warning, blocked, stale, success and interruption paths.",
        "unlocks": [
            "Freeze the narrowest provider-free CF-D2 observability-first durable event/cue plan.",
            "Define the positions, lag, deduplication, reconciliation and operator evidence needed by this visible consumer without opening a watcher runtime.",
            "Keep correctness in command-time authority and source-truth checks even when cues are late, duplicated or absent.",
        ],
        "does_not_solve": [
            "Live product-data status operation, another command family or patient self-service.",
            "A database watcher, durable cue transport, restart or unknown-commit recovery.",
            "External identity/channel delivery, provider access, deployment, production or release.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 275 / Compass 257. The provider-free visible native "
        "Diary status-confirm wiring passes for staff over the existing backend-owned "
        "command, with responsive, keyboard, interruption and fail-closed evidence. "
        "The next safe gate is a fresh provider-free CF-D2 observability-first durable "
        "event/cue plan; no watcher runtime or product-data authority is open."
    )
    limit = (
        "Visible status-confirm evidence uses an authored-synthetic smoke client and route-intercepted browser responses; it is not live product-data or deployment evidence."
    )
    if limit not in compass["map_limits"]:
        compass["map_limits"].insert(0, limit)
    compass["source_graph_revision"] = 275
    compass["map_revision"] = 257
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)

    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
