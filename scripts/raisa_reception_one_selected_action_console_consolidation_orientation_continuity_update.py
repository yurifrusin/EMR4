"""Advance Continuity and Compass for the selected-action-console orientation."""

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
HANDOVER = ROOT / "AGENTS.md"
MASTER_PLAN = ROOT / "implementation_plan.md"
NODE_ID = "raisa-reception-one-selected-action-console-consolidation-orientation"
PARENT = "raisa-reception-one-selected-appointment-practitioner-reassignment-composition"
SOURCE_HEAD = "2d602cfd822235977676bfe9ee8d8dc0a14714fe"
UPDATED_AT = "2026-08-14T04:29:56Z"
PLAN = "docs/raisa-reception-one-selected-action-console-consolidation-orientation-plan.md"
ARCHITECTURE = "docs/raisa-reception-one-selected-action-console-consolidation-architecture.md"
THREAT = "docs/security/raisa-reception-one-selected-action-console-consolidation-orientation-threat-model-delta.md"
ROOT_EVIDENCE = "orchestration/continuity/raisa-reception-one-selected-action-console-consolidation-orientation"
CONTRACT_SCHEMA = f"{ROOT_EVIDENCE}/selected-action-console-orientation-contract.schema.json"
CONTRACT = f"{ROOT_EVIDENCE}/selected-action-console-orientation-contract.json"
NATIVE = "orchestration/agent_inbox/codex/raisa-reception-one-selected-action-console-consolidation-orientation-native-analysis.md"
PREPLANNING = "orchestration/agent_inbox/codex/raisa-reception-one-selected-action-console-consolidation-orientation-preplanning-receipt.json"
PRECOMMIT = "orchestration/agent_inbox/codex/raisa-reception-one-selected-action-console-consolidation-orientation-candidate-precommit-receipt.json"
PREFLIGHT = "orchestration/agent_inbox/codex/raisa-reception-one-selected-action-console-consolidation-orientation-review-worktree-preflight.json"
PACKET = "orchestration/agent_inbox/codex/raisa-reception-one-selected-action-console-consolidation-orientation-gemini-review-packet.md"
MANIFEST = "orchestration/agent_inbox/codex/raisa-reception-one-selected-action-console-consolidation-orientation-gemini-command-manifest.json"
PRE_VERIFIER = "orchestration/agent_inbox/codex/raisa-reception-one-selected-action-console-consolidation-orientation-pre-verifier-acceptance-receipt.json"
GEMINI = "orchestration/agent_inbox/antigravity/raisa-reception-one-selected-action-console-consolidation-orientation-gemini-review-receipt.json"
TEST = "tests/test_raisa_reception_one_selected_action_console_consolidation_orientation.py"
CLOSEOUT = "docs/raisa-reception-one-selected-action-console-consolidation-orientation-closeout.md"
ACCEPTANCE = "orchestration/agent_inbox/codex/raisa-reception-one-selected-action-console-consolidation-orientation-sol-acceptance.md"
MAILBOX = "orchestration/human_inbox/yuri/2026-08-14--reception-one-selected-action-console-orientation.md"
UPDATER = "scripts/raisa_reception_one_selected_action_console_consolidation_orientation_continuity_update.py"
CONTINUITY_TEST = "tests/test_raisa_reception_one_selected_action_console_consolidation_orientation_continuity.py"


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _evidence() -> list[str]:
    return [
        PLAN, ARCHITECTURE, THREAT, CONTRACT_SCHEMA, CONTRACT, NATIVE,
        PREPLANNING, PRECOMMIT, PREFLIGHT, PACKET, MANIFEST, PRE_VERIFIER,
        GEMINI, TEST, CLOSEOUT, ACCEPTANCE, MAILBOX,
    ]


def _node() -> dict[str, Any]:
    return {
        "id": NODE_ID,
        "title": "Provider-free Reception One selected-action-console consolidation orientation",
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
                "Read-only architecture selects a deterministic four-button palette with no editor initially and at most one existing field editor.",
                "Status and update proposal/confirm authorities remain distinct; the palette is presentation state only and issues no command.",
                "Idle switching discards unsubmitted drafts; busy, stale, interrupted and confirmation states forbid switching; terminal truth still requires exact fresh reconciliation.",
            ],
        },
        "decisions": [{
            "id": "accept-reception-one-selected-action-console-orientation",
            "source": ACCEPTANCE,
            "status": "accepted",
            "summary": "Accept a deterministic action palette with single-panel progressive disclosure as the next Reception One composition boundary.",
        }],
        "claim_scope": [
            "The orientation replaces four permanently visible editors with four discoverable choices and zero-or-one visible existing editor in the next implementation.",
            "Action choice remains zero-route presentation state; no generic dispatcher, compound edit or command-capable language intent is admitted.",
            "Two native analyses converged and one fresh Gemini veto passed 77 tests at an unchanged clean candidate.",
            "No product source, patient/product data, provider, deployment or protected-ref activity occurred.",
        ],
        "contract_evidence": [
            {
                "contract_id": "combined-patient-practitioner-time-duration-intent",
                "status": "satisfied",
                "evidence": [PLAN, ARCHITECTURE, CONTRACT, CLOSEOUT],
                "note": "The compact palette preserves distinct status, time, duration and practitioner meanings while future intent is limited to editor activation.",
            },
            {
                "contract_id": "committed-reschedule-availability-reconciliation",
                "status": "satisfied",
                "evidence": [ARCHITECTURE, THREAT, CONTRACT, CLOSEOUT],
                "note": "Current summary and terminal outcomes remain bound to exact fresh projection truth rather than hidden or requested drafts.",
            },
        ],
        "evidence": {
            "plans": [PLAN, ARCHITECTURE, THREAT],
            "findings": [CONTRACT_SCHEMA, CONTRACT, NATIVE],
            "closeouts": [CLOSEOUT, MAILBOX],
            "acceptances": [ACCEPTANCE],
            "receipts": [PREPLANNING, PRECOMMIT, PREFLIGHT, PACKET, MANIFEST, PRE_VERIFIER, GEMINI],
            "tests": [TEST, CONTINUITY_TEST],
            "artifacts": [UPDATER],
        },
        "unresolved_gates": [
            "Implement the bounded presentation-only progressive-disclosure console over the four existing action paths.",
            "Natural-language action activation, another field, full edit and compound commands remain closed.",
            "Product data, watcher/runtime, providers, deployment, production and release remain closed.",
        ],
    }


def _update_handover_and_plan() -> None:
    handover = HANDOVER.read_text(encoding="utf-8")
    relation_old = "The task branch `codex/ariadne-bernie-davida-parallel-seam` must preserve the accepted Reception One selected-appointment practitioner reassignment composition"
    relation_new = "The task branch `codex/ariadne-bernie-davida-parallel-seam` must preserve the accepted Reception One selected-action-console consolidation orientation at exact source `2d602cfd822235977676bfe9ee8d8dc0a14714fe`, the accepted Reception One selected-appointment practitioner reassignment composition"
    if relation_new not in handover:
        if relation_old not in handover:
            raise SystemExit("Required Git relation anchor missing")
        handover = handover.replace(relation_old, relation_new, 1)

    row = "| Reception One selected-action-console consolidation orientation acceptance | `docs/raisa-reception-one-selected-action-console-consolidation-orientation-plan.md`, `docs/raisa-reception-one-selected-action-console-consolidation-architecture.md`, `docs/security/raisa-reception-one-selected-action-console-consolidation-orientation-threat-model-delta.md`, `orchestration/continuity/raisa-reception-one-selected-action-console-consolidation-orientation/`, `orchestration/agent_inbox/codex/raisa-reception-one-selected-action-console-consolidation-orientation-native-analysis.md`, `orchestration/agent_inbox/antigravity/raisa-reception-one-selected-action-console-consolidation-orientation-gemini-review-receipt.json`, `docs/raisa-reception-one-selected-action-console-consolidation-orientation-closeout.md`, `orchestration/agent_inbox/codex/raisa-reception-one-selected-action-console-consolidation-orientation-sol-acceptance.md`, `orchestration/human_inbox/yuri/2026-08-14--reception-one-selected-action-console-orientation.md`, `scripts/raisa_reception_one_selected_action_console_consolidation_orientation_continuity_update.py`, and `tests/test_raisa_reception_one_selected_action_console_consolidation_orientation_continuity.py` |"
    if row not in handover:
        anchor = next(line for line in handover.splitlines() if line.startswith("| Current result |"))
        handover = handover.replace(anchor, row + "\n" + anchor, 1)

    lines = handover.splitlines()
    replacements = {
        "Current result": "| Current result | At Continuity 289 / Compass 271, `raisa_reception_one_selected_action_console_consolidation_orientation_pass` is accepted at exact reviewed source `2d602cfd822235977676bfe9ee8d8dc0a14714fe`. The selected architecture uses four native action choices and zero-or-one existing field editor, preserves distinct status/update command families, discards idle abandoned drafts and retains exact fresh reconciliation. Two native analyses converged and Gemini passed 77 tests at an unchanged clean candidate; no product source changed. |",
        "Next implementation": "| Next implementation | Continue under standing authority with the provider-free Reception One selected-action-console progressive-disclosure composition. Add only presentation state, a current-truth summary, four native action buttons and one shared editor region in the existing Diary client, while leaving all four renderers, executors, bridges, request payloads, route counts and confirmation flows semantically unchanged. Prove zero routes on palette activity, one-or-zero editor, abandoned-draft disposal, busy/interruption/fresh-reconciliation behavior, unchanged paired command traces, accessibility and desktop/tablet/phone containment. Perform the mandatory DeepSeek/Gemini/native-subagent assessment. No backend/API/OpenAPI/GraphQL/database/event/watcher expansion, product/patient data, provider/ADC, credentials/IAM/network, deployment, production, release, Pages or protected-ref movement is inferred. Preserve `docs/branding/` and unrelated untracked files; use explicit-path staging only. |",
    }
    for label, replacement in replacements.items():
        prefix = f"| {label} |"
        indices = [i for i, line in enumerate(lines) if line.startswith(prefix)]
        if len(indices) != 1:
            raise SystemExit(f"Expected one handover row for {label}")
        lines[indices[0]] = replacement

    track_index = next(i for i, line in enumerate(lines) if line.startswith("| Active product track |"))
    old = "A read-only compact selected-action-console orientation is next before another field is added."
    new = "The read-only selected-action-console orientation now selects a deterministic four-button palette with zero-or-one progressively disclosed existing editor; its presentation-only implementation is next before another field is added."
    if old in lines[track_index]:
        lines[track_index] = lines[track_index].replace(old, new, 1)
    elif new not in lines[track_index]:
        raise SystemExit("Active product track console anchor missing")
    HANDOVER.write_text("\n".join(lines) + "\n", encoding="utf-8")

    plan = MASTER_PLAN.read_text(encoding="utf-8")
    old_plan = """Before another field is added, a read-only compact selected-action-console
orientation is the next narrow descendant so proven controls do not accrete as
vertical middleware-style UI.
No watcher runtime, existing database/"""
    new_plan = """The read-only selected-action-console orientation now passes at exact reviewed
source `2d602cfd822235977676bfe9ee8d8dc0a14714fe`. It selects four native action
choices with no editor initially and at most one progressively disclosed
existing editor, while preserving distinct status and update command families.
Its presentation-only implementation is the next narrow descendant before
another field is added.
No watcher runtime, existing database/"""
    if old_plan in plan:
        plan = plan.replace(old_plan, new_plan, 1)
    elif new_plan not in plan:
        raise SystemExit("Master-plan console anchor missing")
    MASTER_PLAN.write_text(plan, encoding="utf-8")


def main() -> int:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 288 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 289
        graph["updated_at"] = UPDATED_AT
    elif graph["graph_revision"] == 289 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
    else:
        raise SystemExit("Unexpected selected-action-console Continuity predecessor")
    _write(GRAPH, graph)

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Select a scalable presentation for the four proven selected-appointment actions",
        "outcome": "One deterministic palette will expose zero-or-one existing editor without merging command authority.",
        "evidence": _evidence(),
    }
    if compass["map_revision"] == 270 and compass["source_graph_revision"] == 288 and compass["current_position"]["node_id"] == PARENT:
        compass["journey"].append(journey)
    elif compass["map_revision"] == 271 and compass["source_graph_revision"] == 289 and compass["current_position"]["node_id"] == NODE_ID:
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected selected-action-console Compass predecessor")

    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": "Protect the minimum-app Reception One surface from one-panel-per-field accumulation",
        "why_now": "Four independently proven actions currently render as four full-width editors, making presentation consolidation dependency-satisfied before another field.",
        "outcome": "The accepted architecture keeps four discoverable choices and opens exactly one existing field editor at a time.",
        "unlocks": [
            "Implement a presentation-only progressive-disclosure console over the existing four command paths.",
            "Retain future intent compatibility without giving language command authority.",
        ],
        "does_not_solve": [
            "The compact console is not implemented yet and representative usability remains unproved.",
            "Another field, compound edits and language-driven action activation remain closed.",
            "Product data, providers, deployment, production and release remain closed.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = "EMR4 is at Continuity 289 / Compass 271. Reception One has a selected four-button, single-editor action-console architecture; its presentation-only implementation is next."
    limit = "The selected-action-console result is read-only architecture evidence; it does not implement UI behavior or merge status and update command authority."
    if limit not in compass["map_limits"]:
        compass["map_limits"].insert(0, limit)
    compass["source_graph_revision"] = 289
    compass["map_revision"] = 271
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)

    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")
    _update_handover_and_plan()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
