"""Advance Continuity and Compass for selected-appointment duration composition."""

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
NODE_ID = "raisa-reception-one-selected-appointment-duration-composition"
PARENT = "raisa-reception-one-selected-appointment-time-reschedule-composition"
SOURCE_HEAD = "f397a3706f3b870b8436eb3993bd90c6c0c742a8"
UPDATED_AT = "2026-08-14T01:55:58Z"
PLAN = "docs/raisa-reception-one-selected-appointment-duration-composition-plan.md"
THREAT = "docs/security/raisa-reception-one-selected-appointment-duration-composition-threat-model-delta.md"
EVIDENCE_ROOT = "orchestration/continuity/raisa-reception-one-selected-appointment-duration-composition"
EVIDENCE_SCHEMA = f"{EVIDENCE_ROOT}/selected-appointment-duration-evidence.schema.json"
EVIDENCE = f"{EVIDENCE_ROOT}/selected-appointment-duration-evidence.json"
BROWSER = "review/test_reception_one_duration_action.py"
STATIC_TEST = "tests/test_reception_one_duration_composition.py"
EVIDENCE_TEST = "tests/test_raisa_reception_one_selected_appointment_duration_composition_evidence.py"
RECOVERY = "docs/raisa-reception-one-duration-deepseek-test-integration-recovery.md"
DEEPSEEK = "orchestration/agent_inbox/deepseek/raisa-reception-one-duration-test-worker-receipt.json"
GEMINI = "orchestration/agent_inbox/antigravity/raisa-reception-one-duration-composition-gemini-review-receipt.json"
PARALLEL_CONTROL = "docs/ariadne-mandatory-parallelism-efficacy-control.md"
CLOSEOUT = "docs/raisa-reception-one-selected-appointment-duration-composition-closeout.md"
ACCEPTANCE = "orchestration/agent_inbox/codex/raisa-reception-one-selected-appointment-duration-composition-sol-acceptance.md"
MAILBOX = "orchestration/human_inbox/yuri/2026-08-14--reception-one-selected-appointment-duration-composition.md"
PRE_VERIFIER = "orchestration/agent_inbox/codex/raisa-reception-one-duration-composition-pre-verifier-receipt.json"
UPDATER = "scripts/raisa_reception_one_selected_appointment_duration_composition_continuity_update.py"
CONTINUITY_TEST = "tests/test_raisa_reception_one_selected_appointment_duration_composition_continuity.py"


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _evidence() -> list[str]:
    return [
        PLAN,
        THREAT,
        EVIDENCE_SCHEMA,
        EVIDENCE,
        BROWSER,
        STATIC_TEST,
        EVIDENCE_TEST,
        RECOVERY,
        DEEPSEEK,
        GEMINI,
        PARALLEL_CONTROL,
        CLOSEOUT,
        ACCEPTANCE,
        MAILBOX,
        PRE_VERIFIER,
    ]


def _node() -> dict[str, Any]:
    return {
        "id": NODE_ID,
        "title": "Provider-free Reception One selected-appointment duration composition",
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
                "Consumer-only authored-synthetic composition over the existing appointment update proposal/confirm family.",
                "The bridge validates one duration delta, fixes start delta at zero, retains the same practitioner and performs no network call.",
                "Backend current-authority, source-truth, safety, idempotency, audit and atomic-commit ownership are unchanged.",
            ],
        },
        "decisions": [{
            "id": "accept-reception-one-selected-appointment-duration-composition",
            "source": ACCEPTANCE,
            "status": "accepted",
            "summary": "Accept one selected current appointment duration-only change through the existing update interaction with fresh reconciliation.",
        }],
        "claim_scope": [
            "One selected current Reception One appointment can propose a bounded whole-15-minute duration delta with unchanged date, start and practitioner.",
            "Twelve paired traces cover safe, cancelled, blocked, stale, failed and committed outcomes with eight equal fresh-truth fields.",
            "DeepSeek and native subagents found material risks; Gemini returned one fresh unchanged-candidate veto pass over 68 tests.",
            "No raw fallback, unexpected mutation, backend/API/database/product-provider/deployment or protected-ref activity occurred.",
        ],
        "contract_evidence": [
            {
                "contract_id": "combined-patient-practitioner-time-duration-intent",
                "status": "satisfied",
                "evidence": [PLAN, EVIDENCE, BROWSER, CLOSEOUT],
                "note": "Duration-only interaction preserves appointment identity, patient linkage, date, start and practitioner through the existing command path.",
            },
            {
                "contract_id": "committed-reschedule-availability-reconciliation",
                "status": "satisfied",
                "evidence": [PLAN, EVIDENCE, BROWSER, CLOSEOUT],
                "note": "Every terminal outcome fresh-reads current truth before a duration or derived end is presented as committed.",
            },
        ],
        "evidence": {
            "plans": [PLAN, THREAT],
            "findings": [EVIDENCE_SCHEMA, EVIDENCE, RECOVERY, PARALLEL_CONTROL],
            "closeouts": [CLOSEOUT, MAILBOX],
            "acceptances": [ACCEPTANCE],
            "receipts": [DEEPSEEK, GEMINI, PRE_VERIFIER],
            "tests": [BROWSER, STATIC_TEST, EVIDENCE_TEST, CONTINUITY_TEST],
            "artifacts": [UPDATER],
        },
        "unresolved_gates": [
            "The next planned descendant is same-date, same-start, same-duration practitioner-only reassignment through the existing update interaction.",
            "Cross-day movement, full appointment editing and another command or event family remain closed.",
            "Product data, watcher/runtime, product providers, deployment, production and release remain closed.",
        ],
    }


def _update_handover_and_plan() -> None:
    handover = HANDOVER.read_text(encoding="utf-8")
    relation_old = "The task branch `codex/ariadne-bernie-davida-parallel-seam` must preserve the accepted Reception One selected-appointment time-reschedule composition"
    relation_new = "The task branch `codex/ariadne-bernie-davida-parallel-seam` must preserve the accepted Reception One selected-appointment duration composition at exact source `f397a3706f3b870b8436eb3993bd90c6c0c742a8`, the accepted Reception One selected-appointment time-reschedule composition"
    if relation_new not in handover:
        if relation_old not in handover:
            raise SystemExit("Required Git relation anchor missing")
        handover = handover.replace(relation_old, relation_new, 1)

    row = "| Reception One selected-appointment duration composition acceptance | `docs/raisa-reception-one-selected-appointment-duration-composition-plan.md`, `docs/security/raisa-reception-one-selected-appointment-duration-composition-threat-model-delta.md`, `docs/diary/diary.js`, `docs/diary/meta-grid.js`, `docs/diary/meta-grid.css`, `review/test_reception_one_duration_action.py`, `tests/test_reception_one_duration_composition.py`, `orchestration/continuity/raisa-reception-one-selected-appointment-duration-composition/`, `docs/raisa-reception-one-duration-deepseek-test-integration-recovery.md`, `orchestration/agent_inbox/deepseek/raisa-reception-one-duration-test-worker-receipt.json`, `orchestration/agent_inbox/antigravity/raisa-reception-one-duration-composition-gemini-review-receipt.json`, `docs/ariadne-mandatory-parallelism-efficacy-control.md`, `docs/raisa-reception-one-selected-appointment-duration-composition-closeout.md`, `orchestration/agent_inbox/codex/raisa-reception-one-selected-appointment-duration-composition-sol-acceptance.md`, `orchestration/human_inbox/yuri/2026-08-14--reception-one-selected-appointment-duration-composition.md`, `scripts/raisa_reception_one_selected_appointment_duration_composition_continuity_update.py`, and `tests/test_raisa_reception_one_selected_appointment_duration_composition_continuity.py` |"
    if row not in handover:
        anchor = next(line for line in handover.splitlines() if line.startswith("| Reception One selected-appointment time-reschedule composition acceptance |"))
        handover = handover.replace(anchor, anchor + "\n" + row, 1)

    lines = handover.splitlines()
    replacements = {
        "Current result": "| Current result | At Continuity 287 / Compass 269, `raisa_reception_one_selected_appointment_duration_composition_pass` is accepted at exact reviewed source `f397a3706f3b870b8436eb3993bd90c6c0c742a8`. One selected current appointment can propose a bounded whole-15-minute duration delta through the existing update proposal/confirm path with unchanged date, start and practitioner. Twelve paired traces agree on eight fresh-truth fields across six outcomes; raw and unexpected mutation routes are zero. DeepSeek and native-subagent work exposed material risks, and one fresh Gemini veto passed 68 tests at an unchanged clean candidate. |",
        "Next implementation": "| Next implementation | Continue under standing authority with the narrowest remaining `handleMoveResize` field: a provider-free selected-appointment practitioner-only reassignment through the same existing update proposal/confirm path. Freeze date, start time, duration and every unrelated field; limit targets to existing active practitioners; preserve visible confirmation, fresh authoritative reconciliation, paired conventional-grid/Reception One outcomes and zero raw or second command path. First perform the mandatory DeepSeek/Gemini/native-subagent parallelism-efficacy assessment. No backend/API/OpenAPI/GraphQL/database/event/watcher expansion, cross-day move, full edit, product/patient data, provider/ADC, credentials/IAM/network, deployment, production, release, Pages or protected-ref movement is inferred. Preserve `docs/branding/` and all unrelated untracked files; use explicit-path staging only. |",
    }
    for label, replacement in replacements.items():
        prefix = f"| {label} |"
        indices = [index for index, line in enumerate(lines) if line.startswith(prefix)]
        if len(indices) != 1:
            raise SystemExit(f"Expected one handover row for {label}")
        lines[indices[0]] = replacement

    track_index = next(index for index, line in enumerate(lines) if line.startswith("| Active product track |"))
    old = "its first time-only Reception One composition now passes through the same canonical update proposal/confirm path with fresh reconciliation and no second command path. A duration-only descendant is next."
    new = "Its time-only and duration-only Reception One compositions now pass through the same canonical update proposal/confirm path with fresh reconciliation and no second command path. Practitioner-only reassignment is the next narrow descendant."
    if old in lines[track_index]:
        lines[track_index] = lines[track_index].replace(old, new, 1)
    elif new not in lines[track_index]:
        raise SystemExit("Active product track duration anchor missing")
    HANDOVER.write_text("\n".join(lines) + "\n", encoding="utf-8")

    plan = MASTER_PLAN.read_text(encoding="utf-8")
    old_plan = """`d803d1d85267af31ee5b6a08b0ecfefb6ad3e04a`, through the same update
proposal/confirm path with fresh reconciliation and no second command path. A
duration-only composition is the next narrow descendant. No watcher runtime, existing database/"""
    new_plan = """`d803d1d85267af31ee5b6a08b0ecfefb6ad3e04a`, through the same update
proposal/confirm path with fresh reconciliation and no second command path. Its
duration-only descendant now also passes at exact reviewed source
`f397a3706f3b870b8436eb3993bd90c6c0c742a8`, preserving date, start and
practitioner through the identical command path. Same-date, same-start,
same-duration practitioner-only reassignment is the next narrow descendant.
No watcher runtime, existing database/"""
    if old_plan in plan:
        plan = plan.replace(old_plan, new_plan, 1)
    elif new_plan not in plan:
        raise SystemExit("Master-plan duration anchor missing")
    MASTER_PLAN.write_text(plan, encoding="utf-8")


def main() -> int:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 286 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 287
        graph["updated_at"] = UPDATED_AT
    elif graph["graph_revision"] == 287 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
    else:
        raise SystemExit("Unexpected duration Continuity predecessor")
    _write(GRAPH, graph)

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Apply projection-neutral kernel truth to a second update/reschedule field",
        "outcome": "One selected appointment can change duration through the canonical update path with fresh truth in both projections.",
        "evidence": _evidence(),
    }
    if compass["map_revision"] == 268 and compass["source_graph_revision"] == 286 and compass["current_position"]["node_id"] == PARENT:
        compass["journey"].append(journey)
    elif compass["map_revision"] == 269 and compass["source_graph_revision"] == 287 and compass["current_position"]["node_id"] == NODE_ID:
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected duration Compass predecessor")

    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": "The update/reschedule family now has time and duration compositions in Reception One",
        "why_now": "Duration was the next independent handleMoveResize field after same-day time rescheduling.",
        "outcome": "Duration-only adjustment passes through one backend-owned command path; practitioner-only reassignment is next.",
        "unlocks": [
            "Compose same-date, same-start, same-duration practitioner-only reassignment through the identical update interaction.",
            "Continue evaluating both projections by fresh kernel truth rather than renderer imitation.",
        ],
        "does_not_solve": [
            "Cross-day movement and full appointment editing remain closed.",
            "No new backend command, event family or watcher runtime is authorised.",
            "Product data, product providers, deployment, production and release remain closed.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 287 / Compass 269. Reception One time and duration "
        "changes pass through the canonical appointment-update path; practitioner-only "
        "reassignment is the next narrow descendant."
    )
    limit = "The selected-duration composition is authored-synthetic client evidence and cannot become a second scheduler, command path or live-product claim."
    if limit not in compass["map_limits"]:
        compass["map_limits"].insert(0, limit)
    compass["source_graph_revision"] = 287
    compass["map_revision"] = 269
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
