"""Advance Continuity and Compass for the selected-action-console composition."""

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
NODE_ID = "raisa-reception-one-selected-action-console-progressive-disclosure-composition"
PARENT = "raisa-reception-one-selected-action-console-consolidation-orientation"
SOURCE_HEAD = "1d9e58fd2624f87b8b3def538297054999e7bef3"
UPDATED_AT = "2026-08-14T08:40:01Z"
PLAN = "docs/raisa-reception-one-selected-action-console-progressive-disclosure-composition-plan.md"
THREAT = "docs/security/raisa-reception-one-selected-action-console-progressive-disclosure-composition-threat-model-delta.md"
ROOT_EVIDENCE = "orchestration/continuity/raisa-reception-one-selected-action-console-progressive-disclosure-composition"
EVIDENCE_SCHEMA = f"{ROOT_EVIDENCE}/selected-action-console-composition-evidence.schema.json"
EVIDENCE = f"{ROOT_EVIDENCE}/selected-action-console-composition-evidence.json"
NATIVE = "orchestration/agent_inbox/codex/raisa-reception-one-selected-action-console-progressive-disclosure-composition-native-analysis.md"
RECOVERY = "orchestration/agent_inbox/codex/raisa-reception-one-selected-action-console-progressive-disclosure-composition-sol-test-recovery.md"
POSTCOMPACTION = "orchestration/agent_inbox/codex/raisa-reception-one-selected-action-console-progressive-disclosure-composition-closeout-postcompaction-2-receipt.json"
PRE_VERIFIER = "orchestration/agent_inbox/codex/raisa-reception-one-selected-action-console-progressive-disclosure-composition-pre-verifier-acceptance-receipt.json"
PREFLIGHT = "orchestration/agent_inbox/codex/raisa-reception-one-selected-action-console-progressive-disclosure-composition-review-worktree-preflight.json"
PACKET = "orchestration/agent_inbox/codex/raisa-reception-one-selected-action-console-progressive-disclosure-composition-gemini-review-packet.md"
GEMINI = "orchestration/agent_inbox/antigravity/raisa-reception-one-selected-action-console-progressive-disclosure-composition-gemini-review-receipt.json"
NEW_BROWSER_TEST = "review/test_reception_one_selected_action_console.py"
EVIDENCE_TEST = "tests/test_raisa_reception_one_selected_action_console_progressive_disclosure_composition_evidence.py"
PARITY_TEST = "review/test_two_projection_truth_parity.py"
CLOSEOUT = "docs/raisa-reception-one-selected-action-console-progressive-disclosure-composition-closeout.md"
ACCEPTANCE = "orchestration/agent_inbox/codex/raisa-reception-one-selected-action-console-progressive-disclosure-composition-sol-acceptance.md"
MAILBOX = "orchestration/human_inbox/yuri/2026-08-14--reception-one-selected-action-console-progressive-disclosure.md"
UPDATER = "scripts/raisa_reception_one_selected_action_console_progressive_disclosure_composition_continuity_update.py"
CONTINUITY_TEST = "tests/test_raisa_reception_one_selected_action_console_progressive_disclosure_composition_continuity.py"


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _evidence() -> list[str]:
    return [
        PLAN,
        THREAT,
        EVIDENCE_SCHEMA,
        EVIDENCE,
        NATIVE,
        RECOVERY,
        POSTCOMPACTION,
        PRE_VERIFIER,
        PREFLIGHT,
        PACKET,
        GEMINI,
        NEW_BROWSER_TEST,
        EVIDENCE_TEST,
        PARITY_TEST,
        "docs/diary/diary.html",
        "docs/diary/meta-grid.css",
        "docs/diary/meta-grid.js",
        CLOSEOUT,
        ACCEPTANCE,
        MAILBOX,
    ]


def _node() -> dict[str, Any]:
    return {
        "id": NODE_ID,
        "title": "Provider-free Reception One selected-action-console progressive-disclosure composition",
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
        "relationships": [{"node_id": PARENT, "relation": "implements"}],
        "authority": {
            "authorized_openings": [],
            "notes": [
                "Presentation now exposes four native choices and zero-or-one existing editor without changing backend command authority.",
                "Palette activity is route-inert; idle drafts are discarded and busy, confirmation, interruption and reconciliation states fail closed.",
                "Status and update command families remain distinct; no generic dispatcher, automatic sequencing or compound-update claim exists.",
            ],
        },
        "decisions": [{
            "id": "accept-reception-one-selected-action-console-progressive-disclosure",
            "source": ACCEPTANCE,
            "status": "accepted",
            "summary": "Accept the compact four-button, zero-or-one-editor composition over the unchanged four appointment action paths.",
        }],
        "claim_scope": [
            "The current-truth summary, native action palette and shared editor are implemented in the existing Diary presentation layer.",
            "Collapse and idle switching issue zero routes and discard abandoned provisional drafts; busy reselection cannot erase an in-flight latch.",
            "The exact broader packet passes 167 tests, the canonical fast profile passes 196 tests, and Gemini passed the unchanged clean candidate.",
            "Browser command evidence is route_intercepted_browser; live backend/database behavior, compound updates and representative usability are not claimed.",
        ],
        "contract_evidence": [
            {
                "contract_id": "combined-patient-practitioner-time-duration-intent",
                "status": "satisfied",
                "evidence": [PLAN, EVIDENCE, NEW_BROWSER_TEST, CLOSEOUT],
                "note": "The console presents current status, time, duration and practitioner while keeping every action independently explicit and future intent non-executing.",
            },
            {
                "contract_id": "committed-reschedule-availability-reconciliation",
                "status": "satisfied",
                "evidence": [THREAT, EVIDENCE, PARITY_TEST, CLOSEOUT],
                "note": "Requested values never become truth; terminal display remains bound to exact fresh projection reconciliation.",
            },
        ],
        "evidence": {
            "plans": [PLAN, THREAT],
            "findings": [EVIDENCE_SCHEMA, EVIDENCE, NATIVE, RECOVERY],
            "closeouts": [CLOSEOUT, MAILBOX],
            "acceptances": [ACCEPTANCE],
            "receipts": [POSTCOMPACTION, PRE_VERIFIER, PREFLIGHT, PACKET, GEMINI],
            "tests": [NEW_BROWSER_TEST, EVIDENCE_TEST, PARITY_TEST, CONTINUITY_TEST],
            "artifacts": ["docs/diary/diary.html", "docs/diary/meta-grid.css", "docs/diary/meta-grid.js", UPDATER],
        },
        "unresolved_gates": [
            "Run a read-only multi-change request atomicity orientation before any combined appointment edit is represented or executed.",
            "Automatic sequential execution, a compound payload and a compound atomicity claim remain closed.",
            "Product data, watcher/runtime, providers, deployment, production and release remain closed.",
        ],
    }


def _update_handover_and_plan() -> None:
    handover = HANDOVER.read_text(encoding="utf-8")
    relation_old = "The task branch `codex/ariadne-bernie-davida-parallel-seam` must preserve the accepted Reception One selected-action-console consolidation orientation"
    relation_new = "The task branch `codex/ariadne-bernie-davida-parallel-seam` must preserve the accepted Reception One selected-action-console progressive-disclosure composition at exact source `1d9e58fd2624f87b8b3def538297054999e7bef3`, the accepted Reception One selected-action-console consolidation orientation"
    if relation_new not in handover:
        if relation_old not in handover:
            raise SystemExit("Required Git relation anchor missing")
        handover = handover.replace(relation_old, relation_new, 1)

    row = "| Reception One selected-action-console progressive-disclosure composition acceptance | `docs/raisa-reception-one-selected-action-console-progressive-disclosure-composition-plan.md`, `docs/security/raisa-reception-one-selected-action-console-progressive-disclosure-composition-threat-model-delta.md`, `docs/diary/meta-grid.js`, `docs/diary/meta-grid.css`, `docs/diary/diary.html`, `review/test_reception_one_selected_action_console.py`, `orchestration/continuity/raisa-reception-one-selected-action-console-progressive-disclosure-composition/`, `orchestration/agent_inbox/codex/raisa-reception-one-selected-action-console-progressive-disclosure-composition-native-analysis.md`, `orchestration/agent_inbox/antigravity/raisa-reception-one-selected-action-console-progressive-disclosure-composition-gemini-review-receipt.json`, `docs/raisa-reception-one-selected-action-console-progressive-disclosure-composition-closeout.md`, `orchestration/agent_inbox/codex/raisa-reception-one-selected-action-console-progressive-disclosure-composition-sol-acceptance.md`, `orchestration/human_inbox/yuri/2026-08-14--reception-one-selected-action-console-progressive-disclosure.md`, `scripts/raisa_reception_one_selected_action_console_progressive_disclosure_composition_continuity_update.py`, and `tests/test_raisa_reception_one_selected_action_console_progressive_disclosure_composition_continuity.py` |"
    if row not in handover:
        anchor = next(line for line in handover.splitlines() if line.startswith("| Current result |"))
        handover = handover.replace(anchor, row + "\n" + anchor, 1)

    lines = handover.splitlines()
    replacements = {
        "Current result": "| Current result | At Continuity 290 / Compass 272, `raisa_reception_one_selected_action_console_progressive_disclosure_composition_pass` is accepted at exact reviewed source `1d9e58fd2624f87b8b3def538297054999e7bef3`. Reception One now shows one current-truth summary, four native action choices and zero-or-one existing editor. Palette activity is route-inert, abandoned drafts are discarded, busy/interrupted/fresh-reconciliation states fail closed, all four command paths remain distinct and unchanged, and Gemini passed 167 tests at an unchanged clean candidate. |",
        "Next implementation": "| Next implementation | Continue under standing authority with the provider-free, read-only Reception One multi-change request atomicity orientation. Map the exact existing appointment update proposal/confirm contract and freeze how requests containing several changes are represented, reviewed, confirmed, made current and recovered. Automatic sequencing of single-field commands, a combined client dispatcher and any compound atomicity claim remain forbidden unless a separately proven kernel-owned command contract supports them. No product implementation, backend/API/OpenAPI/GraphQL/database/event/watcher expansion, product/patient data, provider/ADC, credentials/IAM/network, deployment, production, release, Pages or protected-ref movement is inferred. Preserve `docs/branding/` and unrelated untracked files; use explicit-path staging only. |",
    }
    for label, replacement in replacements.items():
        prefix = f"| {label} |"
        indices = [i for i, line in enumerate(lines) if line.startswith(prefix)]
        if len(indices) != 1:
            raise SystemExit(f"Expected one handover row for {label}")
        lines[indices[0]] = replacement

    track_index = next(i for i, line in enumerate(lines) if line.startswith("| Active product track |"))
    old = "The read-only selected-action-console orientation now selects a deterministic four-button palette with zero-or-one progressively disclosed existing editor; its presentation-only implementation is next before another field is added."
    new = "The selected-action-console progressive-disclosure composition now implements that architecture: one current-truth summary, four route-inert native choices and zero-or-one existing editor, with abandoned-draft disposal and exact busy/interruption/fresh-reconciliation protection. A read-only multi-change request atomicity orientation is next before any compound edit or another command field."
    if old in lines[track_index]:
        lines[track_index] = lines[track_index].replace(old, new, 1)
    elif new not in lines[track_index]:
        raise SystemExit("Active product track console anchor missing")
    HANDOVER.write_text("\n".join(lines) + "\n", encoding="utf-8")

    plan = MASTER_PLAN.read_text(encoding="utf-8")
    old_plan = """The read-only selected-action-console orientation now passes at exact reviewed
source `2d602cfd822235977676bfe9ee8d8dc0a14714fe`. It selects four native action
choices with no editor initially and at most one progressively disclosed
existing editor, while preserving distinct status and update command families.
Its presentation-only implementation is the next narrow descendant before
another field is added.
No watcher runtime, existing database/
source access, persistence, product data, external patient client, other
command, restart/unknown-commit claim, provider, deployment, production or
release is opened."""
    new_plan = """The selected-action-console progressive-disclosure composition now passes at
exact reviewed source `1d9e58fd2624f87b8b3def538297054999e7bef3`.
Reception One shows one current-truth summary, four route-inert native choices
and at most one existing field editor; abandoned drafts are discarded and
busy, confirmation, interruption and fresh-reconciliation states fail closed.
All four existing command paths remain distinct and unchanged. The next narrow
descendant is a provider-free read-only multi-change request atomicity
orientation before any compound edit or another command field is considered.
No watcher runtime, existing database/source access, persistence, product data,
external patient client, compound command, restart/unknown-commit claim,
provider, deployment, production or release is opened."""
    if old_plan in plan:
        plan = plan.replace(old_plan, new_plan, 1)
    elif new_plan not in plan:
        raise SystemExit("Master-plan console anchor missing")
    MASTER_PLAN.write_text(plan, encoding="utf-8")


def main() -> int:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 289 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 290
        graph["updated_at"] = UPDATED_AT
    elif graph["graph_revision"] == 290 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
    else:
        raise SystemExit("Unexpected selected-action-console composition Continuity predecessor")
    _write(GRAPH, graph)

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Implement the compact action surface over four proven selected-appointment command paths",
        "outcome": "One current-truth summary and four route-inert choices now expose zero-or-one existing editor without merging command authority.",
        "evidence": _evidence(),
    }
    if compass["map_revision"] == 271 and compass["source_graph_revision"] == 289 and compass["current_position"]["node_id"] == PARENT:
        compass["journey"].append(journey)
    elif compass["map_revision"] == 272 and compass["source_graph_revision"] == 290 and compass["current_position"]["node_id"] == NODE_ID:
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected selected-action-console composition Compass predecessor")

    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": "Keep Reception One compact while preserving kernel-owned command meaning",
        "why_now": "The four independent actions were proven and their selected single-editor presentation architecture was accepted.",
        "outcome": "The compact console is implemented with route-inert palette activity, draft disposal and exact fresh reconciliation over unchanged command paths.",
        "unlocks": [
            "Orient the safe representation and atomicity of a request containing several appointment changes.",
            "Consider later intent-driven editor activation without granting language command authority.",
        ],
        "does_not_solve": [
            "No compound update transaction, automatic command sequencing or conversational execution is implemented.",
            "Representative usability and live backend/database behavior remain unproved by this tranche.",
            "Product data, providers, deployment, production and release remain closed.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = "EMR4 is at Continuity 290 / Compass 272. Reception One now has a compact four-choice, zero-or-one-editor action console; read-only multi-change atomicity orientation is next."
    limit = "The selected-action-console composition proves route-intercepted presentation behavior, not live backend/database execution, compound updates or representative usability."
    if limit not in compass["map_limits"]:
        compass["map_limits"].insert(0, limit)
    compass["source_graph_revision"] = 290
    compass["map_revision"] = 272
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
