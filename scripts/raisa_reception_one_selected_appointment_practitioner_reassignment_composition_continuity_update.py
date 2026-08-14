"""Advance Continuity and Compass for selected-appointment practitioner reassignment."""

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
NODE_ID = "raisa-reception-one-selected-appointment-practitioner-reassignment-composition"
PARENT = "raisa-reception-one-selected-appointment-duration-composition"
SOURCE_HEAD = "f085fc98ead21a3e7929ee9adbda81abfc7542c9"
UPDATED_AT = "2026-08-14T03:38:04Z"
PLAN = "docs/raisa-reception-one-selected-appointment-practitioner-reassignment-composition-plan.md"
THREAT = "docs/security/raisa-reception-one-selected-appointment-practitioner-reassignment-composition-threat-model-delta.md"
EVIDENCE_ROOT = "orchestration/continuity/raisa-reception-one-selected-appointment-practitioner-reassignment-composition"
EVIDENCE_SCHEMA = f"{EVIDENCE_ROOT}/selected-appointment-practitioner-reassignment-evidence.schema.json"
EVIDENCE = f"{EVIDENCE_ROOT}/selected-appointment-practitioner-reassignment-evidence.json"
BROWSER = "review/test_reception_one_practitioner_reassignment_action.py"
STATIC_TEST = "tests/test_reception_one_practitioner_reassignment_composition.py"
EVIDENCE_TEST = "tests/test_raisa_reception_one_selected_appointment_practitioner_reassignment_composition_evidence.py"
DEEPSEEK = "orchestration/agent_inbox/codex/raisa-reception-one-practitioner-reassignment-deepseek-worker-output.json"
GEMINI = "orchestration/agent_inbox/antigravity/raisa-reception-one-practitioner-reassignment-gemini-review-receipt.json"
PARALLEL_CONTROL = "docs/ariadne-mandatory-parallelism-efficacy-control.md"
CLOSEOUT = "docs/raisa-reception-one-selected-appointment-practitioner-reassignment-composition-closeout.md"
ACCEPTANCE = "orchestration/agent_inbox/codex/raisa-reception-one-selected-appointment-practitioner-reassignment-composition-sol-acceptance.md"
MAILBOX = "orchestration/human_inbox/yuri/2026-08-14--reception-one-selected-appointment-practitioner-reassignment.md"
PRE_VERIFIER = "orchestration/agent_inbox/codex/raisa-reception-one-practitioner-reassignment-pre-verifier-acceptance-receipt.json"
UPDATER = "scripts/raisa_reception_one_selected_appointment_practitioner_reassignment_composition_continuity_update.py"
CONTINUITY_TEST = "tests/test_raisa_reception_one_selected_appointment_practitioner_reassignment_composition_continuity.py"


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _evidence() -> list[str]:
    return [PLAN, THREAT, EVIDENCE_SCHEMA, EVIDENCE, BROWSER, STATIC_TEST,
            EVIDENCE_TEST, DEEPSEEK, GEMINI, PARALLEL_CONTROL, CLOSEOUT,
            ACCEPTANCE, MAILBOX, PRE_VERIFIER]


def _node() -> dict[str, Any]:
    return {
        "id": NODE_ID,
        "title": "Provider-free Reception One selected-appointment practitioner reassignment composition",
        "kind": "implementation",
        "status": "accepted",
        "created_at": UPDATED_AT,
        "updated_at": UPDATED_AT,
        "coordinates": {"git_ref": "codex/ariadne-bernie-davida-parallel-seam", "source_head": SOURCE_HEAD, "thread_id": None, "worktree_role": "task"},
        "relationships": [{"node_id": PARENT, "relation": "implements"}],
        "authority": {
            "authorized_openings": [],
            "notes": [
                "Authored-synthetic composition over the existing appointment update proposal/confirm family.",
                "The bridge admits one fresh unique active-directory target, freezes it, fixes both deltas at zero and delegates once without network access.",
                "The existing proposal and confirm-time re-proposal own changed-target activity, current authority, source truth, idempotency, audit and atomic commit.",
            ],
        },
        "decisions": [{"id": "accept-reception-one-selected-appointment-practitioner-reassignment", "source": ACCEPTANCE, "status": "accepted", "summary": "Accept one selected current appointment practitioner-only reassignment through the existing update interaction with current active-target truth and fresh reconciliation."}],
        "claim_scope": [
            "One selected current appointment can move to one distinct active practitioner with unchanged date, start and duration.",
            "Twelve paired traces cover safe, cancelled, blocked, stale, failed and committed outcomes with eight equal fresh-truth fields and no raw fallback.",
            "DeepSeek supplied useful but uneconomical test breadth, native review drove material repairs and Gemini passed 80 tests at an unchanged clean candidate.",
            "No new command route, product/provider call, real product data, deployment or protected-ref activity occurred.",
        ],
        "contract_evidence": [
            {"contract_id": "combined-patient-practitioner-time-duration-intent", "status": "satisfied", "evidence": [PLAN, EVIDENCE, BROWSER, CLOSEOUT], "note": "Practitioner-only interaction preserves appointment identity, patient linkage, date, start and duration through the existing command path."},
            {"contract_id": "committed-reschedule-availability-reconciliation", "status": "satisfied", "evidence": [PLAN, EVIDENCE, BROWSER, CLOSEOUT], "note": "Every terminal outcome fresh-reads current truth before a practitioner is presented as committed."},
        ],
        "evidence": {
            "plans": [PLAN, THREAT], "findings": [EVIDENCE_SCHEMA, EVIDENCE, PARALLEL_CONTROL],
            "closeouts": [CLOSEOUT, MAILBOX], "acceptances": [ACCEPTANCE],
            "receipts": [DEEPSEEK, GEMINI, PRE_VERIFIER],
            "tests": [BROWSER, STATIC_TEST, EVIDENCE_TEST, CONTINUITY_TEST], "artifacts": [UPDATER],
        },
        "unresolved_gates": [
            "The next planned descendant is a read-only selected-action-console consolidation orientation before another appointment field is added.",
            "Cross-day movement, full editing and another command or event family remain closed.",
            "Product data, watcher/runtime, providers, deployment, production and release remain closed.",
        ],
    }


def _update_handover_and_plan() -> None:
    handover = HANDOVER.read_text(encoding="utf-8")
    relation_old = "The task branch `codex/ariadne-bernie-davida-parallel-seam` must preserve the accepted Reception One selected-appointment duration composition"
    relation_new = "The task branch `codex/ariadne-bernie-davida-parallel-seam` must preserve the accepted Reception One selected-appointment practitioner reassignment composition at exact source `f085fc98ead21a3e7929ee9adbda81abfc7542c9`, the accepted Reception One selected-appointment duration composition"
    if relation_new not in handover:
        if relation_old not in handover:
            raise SystemExit("Required Git relation anchor missing")
        handover = handover.replace(relation_old, relation_new, 1)

    row = "| Reception One selected-appointment practitioner reassignment composition acceptance | `docs/raisa-reception-one-selected-appointment-practitioner-reassignment-composition-plan.md`, `docs/security/raisa-reception-one-selected-appointment-practitioner-reassignment-composition-threat-model-delta.md`, `docs/diary/diary.js`, `docs/diary/meta-grid.js`, `docs/diary/meta-grid.css`, `app/routers/appointments.py`, `review/test_reception_one_practitioner_reassignment_action.py`, `tests/test_reception_one_practitioner_reassignment_composition.py`, `tests/test_appointment_update_proposal.py`, `orchestration/continuity/raisa-reception-one-selected-appointment-practitioner-reassignment-composition/`, `orchestration/agent_inbox/codex/raisa-reception-one-practitioner-reassignment-deepseek-worker-output.json`, `orchestration/agent_inbox/antigravity/raisa-reception-one-practitioner-reassignment-gemini-review-receipt.json`, `docs/ariadne-mandatory-parallelism-efficacy-control.md`, `docs/raisa-reception-one-selected-appointment-practitioner-reassignment-composition-closeout.md`, `orchestration/agent_inbox/codex/raisa-reception-one-selected-appointment-practitioner-reassignment-composition-sol-acceptance.md`, `orchestration/human_inbox/yuri/2026-08-14--reception-one-selected-appointment-practitioner-reassignment.md`, `scripts/raisa_reception_one_selected_appointment_practitioner_reassignment_composition_continuity_update.py`, and `tests/test_raisa_reception_one_selected_appointment_practitioner_reassignment_composition_continuity.py` |"
    if row not in handover:
        anchor = next(line for line in handover.splitlines() if line.startswith("| Current result |"))
        handover = handover.replace(anchor, row + "\n" + anchor, 1)

    lines = handover.splitlines()
    replacements = {
        "Current result": "| Current result | At Continuity 288 / Compass 270, `raisa_reception_one_selected_appointment_practitioner_reassignment_composition_pass` is accepted at exact reviewed source `f085fc98ead21a3e7929ee9adbda81abfc7542c9`. One selected current appointment can move to one distinct current active practitioner through the existing update proposal/confirm path with unchanged date, start and duration. Twelve paired traces agree on eight fresh-truth fields; the backend blocks target deactivation again at confirmation; raw and unexpected mutation routes are zero. DeepSeek, native and Gemini lanes were all explicitly assessed, with one fresh Gemini veto passing 80 tests at an unchanged clean candidate. |",
        "Next implementation": "| Next implementation | Continue under standing authority with a provider-free read-only Reception One selected-action-console consolidation orientation. The four proven selected-appointment actions now risk vertical middleware-style UI accumulation; select the narrowest progressive-disclosure or intent-led composition that preserves status, time, duration and practitioner truth/command contracts before adding another field. Perform the mandatory DeepSeek/Gemini/native-subagent parallelism-efficacy assessment. No product edit, new command/field, backend/API/OpenAPI/GraphQL/database/event/watcher expansion, product/patient data, provider/ADC, credentials/IAM/network, deployment, production, release, Pages or protected-ref movement is inferred. Preserve `docs/branding/` and all unrelated untracked files; use explicit-path staging only. |",
    }
    for label, replacement in replacements.items():
        prefix = f"| {label} |"
        indices = [i for i, line in enumerate(lines) if line.startswith(prefix)]
        if len(indices) != 1:
            raise SystemExit(f"Expected one handover row for {label}")
        lines[indices[0]] = replacement

    track_index = next(i for i, line in enumerate(lines) if line.startswith("| Active product track |"))
    old = "Its time-only and duration-only Reception One compositions now pass through the same canonical update proposal/confirm path with fresh reconciliation and no second command path. Practitioner-only reassignment is the next narrow descendant."
    new = "Its time-only, duration-only and practitioner-only Reception One compositions now pass through the same canonical update proposal/confirm path with fresh reconciliation and no second command path. A read-only compact selected-action-console orientation is next before another field is added."
    if old in lines[track_index]:
        lines[track_index] = lines[track_index].replace(old, new, 1)
    elif new not in lines[track_index]:
        raise SystemExit("Active product track practitioner anchor missing")
    HANDOVER.write_text("\n".join(lines) + "\n", encoding="utf-8")

    plan = MASTER_PLAN.read_text(encoding="utf-8")
    old_plan = """`f397a3706f3b870b8436eb3993bd90c6c0c742a8`, preserving date, start and
practitioner through the identical command path. Same-date, same-start,
same-duration practitioner-only reassignment is the next narrow descendant.
No watcher runtime, existing database/"""
    new_plan = """`f397a3706f3b870b8436eb3993bd90c6c0c742a8`, preserving date, start and
practitioner through the identical command path. Its practitioner-only
descendant now also passes at exact reviewed source
`f085fc98ead21a3e7929ee9adbda81abfc7542c9`, preserving date, start and
duration while requiring one current active target at proposal and confirm.
Before another field is added, a read-only compact selected-action-console
orientation is the next narrow descendant so proven controls do not accrete as
vertical middleware-style UI.
No watcher runtime, existing database/"""
    if old_plan in plan:
        plan = plan.replace(old_plan, new_plan, 1)
    elif new_plan not in plan:
        raise SystemExit("Master-plan practitioner anchor missing")
    MASTER_PLAN.write_text(plan, encoding="utf-8")


def main() -> int:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 287 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 288
        graph["updated_at"] = UPDATED_AT
    elif graph["graph_revision"] == 288 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
    else:
        raise SystemExit("Unexpected practitioner Continuity predecessor")
    _write(GRAPH, graph)

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    journey = {"node_id": NODE_ID, "lineage_parent": PARENT, "strategic_role": "Complete the bounded handleMoveResize field family with practitioner-only composition", "outcome": "One selected appointment can move to one current active practitioner through the canonical update path with fresh truth in both projections.", "evidence": _evidence()}
    if compass["map_revision"] == 269 and compass["source_graph_revision"] == 287 and compass["current_position"]["node_id"] == PARENT:
        compass["journey"].append(journey)
    elif compass["map_revision"] == 270 and compass["source_graph_revision"] == 288 and compass["current_position"]["node_id"] == NODE_ID:
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected practitioner Compass predecessor")

    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": "Reception One now composes status and all three bounded handleMoveResize meanings over kernel truth",
        "why_now": "Practitioner reassignment was the final independent handleMoveResize field after same-day time and duration.",
        "outcome": "One active-target reassignment passes through the backend-owned command path; compact selected-action orientation is next.",
        "unlocks": ["Orient a compact progressive-disclosure or intent-led selected-action console without opening another field.", "Continue evaluating both projections by fresh kernel truth rather than renderer imitation."],
        "does_not_solve": ["Cross-day movement, full editing and another appointment field remain closed.", "No new command, event family or watcher runtime is authorised.", "Product data, providers, deployment, production and release remain closed."],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = "EMR4 is at Continuity 288 / Compass 270. Reception One status, time, duration and practitioner reassignment share kernel-owned truth; compact selected-action orientation is next."
    limit = "The selected-practitioner composition is authored-synthetic client and local command-test evidence and cannot become a second scheduler, new command path or live-product claim."
    if limit not in compass["map_limits"]:
        compass["map_limits"].insert(0, limit)
    compass["source_graph_revision"] = 288
    compass["map_revision"] = 270
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
