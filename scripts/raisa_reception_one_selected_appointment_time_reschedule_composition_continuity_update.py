"""Advance Continuity and Compass for selected-appointment time rescheduling."""

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
NODE_ID = "raisa-reception-one-selected-appointment-time-reschedule-composition"
PARENT = "raisa-provider-free-two-projection-truth-parity-conformance-rehearsal"
SOURCE_HEAD = "d803d1d85267af31ee5b6a08b0ecfefb6ad3e04a"
UPDATED_AT = "2026-08-13T23:50:00Z"
PLAN = "docs/raisa-reception-one-selected-appointment-time-reschedule-composition-plan.md"
THREAT = "docs/security/raisa-reception-one-selected-appointment-time-reschedule-composition-threat-model-delta.md"
EVIDENCE_ROOT = "orchestration/continuity/raisa-reception-one-selected-appointment-time-reschedule-composition"
EVIDENCE_SCHEMA = f"{EVIDENCE_ROOT}/selected-appointment-time-reschedule-evidence.schema.json"
EVIDENCE = f"{EVIDENCE_ROOT}/selected-appointment-time-reschedule-evidence.json"
BROWSER = "review/test_reception_one_time_reschedule_action.py"
STATIC_TEST = "tests/test_reception_one_time_reschedule_composition.py"
EVIDENCE_TEST = "tests/test_raisa_reception_one_selected_appointment_time_reschedule_composition_evidence.py"
RECOVERY = "docs/raisa-reception-one-time-reschedule-deepseek-test-integration-recovery.md"
DEEPSEEK = "orchestration/agent_inbox/deepseek/raisa-reception-one-time-reschedule-test-worker-receipt.json"
GEMINI = "orchestration/agent_inbox/antigravity/raisa-reception-one-time-reschedule-gemini-review-receipt.json"
PARALLEL_CONTROL = "docs/ariadne-mandatory-parallelism-efficacy-control.md"
CLOSEOUT = "docs/raisa-reception-one-selected-appointment-time-reschedule-composition-closeout.md"
ACCEPTANCE = "orchestration/agent_inbox/codex/raisa-reception-one-selected-appointment-time-reschedule-composition-sol-acceptance.md"
MAILBOX = "orchestration/human_inbox/yuri/2026-08-14--reception-one-selected-appointment-time-reschedule-composition.md"
REHYDRATION_RECEIPT = "orchestration/agent_inbox/codex/raisa-reception-one-time-reschedule-postgemini-postcompaction-receipt.json"
UPDATER = "scripts/raisa_reception_one_selected_appointment_time_reschedule_composition_continuity_update.py"
CONTINUITY_TEST = "tests/test_raisa_reception_one_selected_appointment_time_reschedule_composition_continuity.py"


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


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
        REHYDRATION_RECEIPT,
    ]


def _node() -> dict[str, Any]:
    return {
        "id": NODE_ID,
        "title": "Provider-free Reception One selected-appointment time-reschedule composition",
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
                "Consumer-only authored-synthetic composition over the existing update proposal/confirm command family.",
                "The bridge validates a same-day time, fixes duration delta at zero, retains the same practitioner and performs no network call.",
                "Backend current-authority, source-truth, safety, idempotency, audit and atomic-commit ownership are unchanged.",
            ],
        },
        "decisions": [
            {
                "id": "accept-reception-one-selected-appointment-time-reschedule-composition",
                "source": ACCEPTANCE,
                "status": "accepted",
                "summary": "Accept one selected current appointment same-day time change through the existing update interaction with fresh reconciliation.",
            }
        ],
        "claim_scope": [
            "One selected current Reception One appointment can propose one 15-minute-aligned same-day start time with unchanged practitioner and duration.",
            "Twelve paired traces cover safe, cancelled, blocked, stale, failed and committed outcomes with eight equal fresh-truth fields.",
            "DeepSeek supplied one recovered test artifact and Gemini returned one fresh unchanged-candidate veto pass over 51 tests.",
            "No raw fallback, unexpected mutation, backend/API/database/provider/product-data/deployment or protected-ref activity occurred.",
        ],
        "contract_evidence": [
            {
                "contract_id": "combined-patient-practitioner-time-duration-intent",
                "status": "satisfied",
                "evidence": [PLAN, EVIDENCE, BROWSER, CLOSEOUT],
                "note": "The time-only interaction preserves appointment identity, patient linkage, practitioner and duration while changing only start/end coordinates through the existing command path.",
            },
            {
                "contract_id": "committed-reschedule-availability-reconciliation",
                "status": "satisfied",
                "evidence": [PLAN, EVIDENCE, BROWSER, CLOSEOUT],
                "note": "Every terminal outcome fresh-reads current truth; a committed card receives its coordinate only from the exact fresh appointment response.",
            },
        ],
        "evidence": {
            "plans": [PLAN, THREAT],
            "findings": [EVIDENCE_SCHEMA, EVIDENCE, RECOVERY, PARALLEL_CONTROL],
            "closeouts": [CLOSEOUT, MAILBOX],
            "acceptances": [ACCEPTANCE],
            "receipts": [DEEPSEEK, GEMINI, REHYDRATION_RECEIPT],
            "tests": [BROWSER, STATIC_TEST, EVIDENCE_TEST, CONTINUITY_TEST],
            "artifacts": [UPDATER],
        },
        "unresolved_gates": [
            "The next planned descendant is a same-start, same-date, same-practitioner duration-only composition through the existing update interaction.",
            "Cross-day and cross-practitioner rescheduling, full edit and another command or event family remain closed.",
            "Product data, watcher/runtime, providers, deployment, production and release remain closed.",
        ],
    }


def _update_handover_and_plan() -> None:
    handover = HANDOVER.read_text(encoding="utf-8")
    relation_old = "The task branch `codex/ariadne-bernie-davida-parallel-seam` must preserve the accepted two-projection truth-parity conformance rehearsal"
    relation_new = "The task branch `codex/ariadne-bernie-davida-parallel-seam` must preserve the accepted Reception One selected-appointment time-reschedule composition at exact source `d803d1d85267af31ee5b6a08b0ecfefb6ad3e04a`, the accepted two-projection truth-parity conformance rehearsal"
    if relation_new not in handover:
        if relation_old not in handover:
            raise SystemExit("Required Git relation anchor missing")
        handover = handover.replace(relation_old, relation_new, 1)

    row = "| Reception One selected-appointment time-reschedule composition acceptance | `docs/raisa-reception-one-selected-appointment-time-reschedule-composition-plan.md`, `docs/security/raisa-reception-one-selected-appointment-time-reschedule-composition-threat-model-delta.md`, `docs/diary/diary.js`, `docs/diary/meta-grid.js`, `docs/diary/meta-grid.css`, `review/test_reception_one_time_reschedule_action.py`, `tests/test_reception_one_time_reschedule_composition.py`, `orchestration/continuity/raisa-reception-one-selected-appointment-time-reschedule-composition/`, `docs/raisa-reception-one-time-reschedule-deepseek-test-integration-recovery.md`, `orchestration/agent_inbox/deepseek/raisa-reception-one-time-reschedule-test-worker-receipt.json`, `orchestration/agent_inbox/antigravity/raisa-reception-one-time-reschedule-gemini-review-receipt.json`, `docs/ariadne-mandatory-parallelism-efficacy-control.md`, `docs/raisa-reception-one-selected-appointment-time-reschedule-composition-closeout.md`, `orchestration/agent_inbox/codex/raisa-reception-one-selected-appointment-time-reschedule-composition-sol-acceptance.md`, `orchestration/human_inbox/yuri/2026-08-14--reception-one-selected-appointment-time-reschedule-composition.md`, `scripts/raisa_reception_one_selected_appointment_time_reschedule_composition_continuity_update.py`, and `tests/test_raisa_reception_one_selected_appointment_time_reschedule_composition_continuity.py` |"
    if row not in handover:
        anchor = next(
            line
            for line in handover.splitlines()
            if line.startswith("| Two-projection truth-parity conformance acceptance |")
        )
        handover = handover.replace(anchor, anchor + "\n" + row, 1)

    lines = handover.splitlines()
    replacements = {
        "Ariadne agent error and correction register acceptance": "| Ariadne agent error and correction register acceptance | `docs/ariadne-agent-error-correction-register-plan.md`, revisions 2-267 including current `docs/ariadne-agent-error-correction-register-revision-267.md`, `orchestration/continuity/ariadne-agent-error-register/agent-error-register.schema.json`, `orchestration/continuity/ariadne-agent-error-register/agent-error-register.json`, `orchestration/continuity/ariadne-agent-error-register/pattern-report.json`, `scripts/ariadne_agent_error_register.py`, `scripts/ariadne_serial_pytest.py`, `scripts/ariadne_verifier_worktree_preflight.py`, `orchestration/harness_settings/verifier_execution_policy.yaml`, `tests/test_ariadne_agent_error_register.py`, `tests/test_ariadne_serial_pytest.py`, `tests/test_ariadne_verifier_execution_policy.py`, `tests/test_ariadne_verifier_worktree_preflight.py`, `scripts/compact_agents_acceptance_index.py`, `docs/handover-ledgers/current-baton-acceptance-index.manifest.json`, `tests/test_agents_acceptance_index.py`, `docs/ariadne-agent-error-correction-register-closeout.md`, and `orchestration/agent_inbox/codex/ariadne-agent-error-register-sol-acceptance.md` |",
        "Current result": "| Current result | At Continuity 286 / Compass 268, `raisa_reception_one_selected_appointment_time_reschedule_composition_pass` is accepted at exact reviewed source `d803d1d85267af31ee5b6a08b0ecfefb6ad3e04a`. One selected current appointment can propose a 15-minute-aligned same-day time through the existing update proposal/confirm path with unchanged date, practitioner and duration. Twelve paired conventional-grid/Reception One traces agree on eight fresh-truth fields across six outcomes; raw and unexpected mutation routes are zero. DeepSeek's recovered test packet exposed and closed a fresh-coordinate race, and one fresh Gemini veto passed at an unchanged clean candidate. |",
        "Next implementation": "| Next implementation | Continue under standing authority with the narrowest dependency-satisfied descendant in the selected appointment update/rescheduling family: a provider-free selected-appointment duration-only composition through the same existing `handleMoveResize` update proposal/confirm path. Freeze date, start time, practitioner and every unrelated field; require visible confirmation where the backend does, fresh authoritative reconciliation, paired conventional-grid/Reception One outcomes and zero raw or second command path. First perform the mandatory DeepSeek/Gemini/native-subagent parallelism-efficacy assessment. No backend/API/OpenAPI/GraphQL/database/event/watcher expansion, cross-day or cross-practitioner move, full edit, product/patient data, provider/ADC, credentials/IAM/network, deployment, production, release, Pages or protected-ref movement is inferred. Preserve `docs/branding/` and all unrelated untracked files; use explicit-path staging only. |",
    }
    for label, replacement in replacements.items():
        prefix = f"| {label} |"
        indices = [index for index, line in enumerate(lines) if line.startswith(prefix)]
        if len(indices) != 1:
            raise SystemExit(f"Expected one handover row for {label}")
        lines[indices[0]] = replacement

    track_prefix = "| Active product track |"
    track_index = next(index for index, line in enumerate(lines) if line.startswith(track_prefix))
    old_track = lines[track_index]
    marker = "The two-projection truth-parity rehearsal now protects six paired status outcomes without changing product code; the next functional direction is a genuine Yuri-owned fork."
    replacement = "The two-projection truth-parity rehearsal protects six paired status outcomes. Yuri selected the existing update/reschedule family; its first time-only Reception One composition now passes through the same canonical update proposal/confirm path with fresh reconciliation and no second command path. A duration-only descendant is next."
    if marker in old_track:
        lines[track_index] = old_track.replace(marker, replacement, 1)
    elif replacement not in old_track:
        raise SystemExit("Active product track anchor missing")
    HANDOVER.write_text("\n".join(lines) + "\n", encoding="utf-8")

    plan = MASTER_PLAN.read_text(encoding="utf-8")
    old = """traces protect six paired status outcomes without changing product code. The
next functional direction is a genuine Yuri-owned fork; no command, cohort,
patient channel, event family or watcher runtime is inferred."""
    new = """traces protect six paired status outcomes without changing product code. Yuri
then selected the existing appointment update/reschedule family. Its first
same-day, same-practitioner, duration-fixed Reception One time composition
passes at exact reviewed source
`d803d1d85267af31ee5b6a08b0ecfefb6ad3e04a`, through the same update
proposal/confirm path with fresh reconciliation and no second command path. A
duration-only composition is the next narrow descendant."""
    if old in plan:
        plan = plan.replace(old, new, 1)
    elif new not in plan:
        raise SystemExit("Master-plan time-reschedule anchor missing")
    MASTER_PLAN.write_text(plan, encoding="utf-8")


def main() -> int:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 285 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 286
        graph["updated_at"] = UPDATED_AT
    elif graph["graph_revision"] == 286 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
    else:
        raise SystemExit("Unexpected time-reschedule Continuity predecessor")
    _write(GRAPH, graph)

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Apply projection-neutral kernel truth to the first update/reschedule field",
        "outcome": "One selected appointment can change its same-day start time through the canonical update path with fresh truth in both projections.",
        "evidence": _evidence(),
    }
    if (
        compass["map_revision"] == 267
        and compass["source_graph_revision"] == 285
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 268
        and compass["source_graph_revision"] == 286
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected time-reschedule Compass predecessor")

    compass["decision_horizon"] = [
        item
        for item in compass["decision_horizon"]
        if item["id"] != "post-truth-parity-programme-direction"
    ]
    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": "The update/reschedule family now has its first focused Reception One composition",
        "why_now": "Yuri selected appointment update/rescheduling after truth parity, and time-only change was its narrowest useful field.",
        "outcome": "Same-day time rescheduling passes through one backend-owned command path; duration-only composition is next.",
        "unlocks": [
            "Compose duration-only adjustment through the identical update interaction.",
            "Continue evaluating both projections by fresh kernel truth rather than renderer imitation.",
        ],
        "does_not_solve": [
            "Cross-day, cross-practitioner and full appointment editing remain closed.",
            "No new backend command, event family or watcher runtime is authorised.",
            "Product data, providers, deployment, production and release remain closed.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 286 / Compass 268. Reception One same-day "
        "time rescheduling passes through the canonical appointment-update "
        "path; duration-only composition is the next narrow descendant."
    )
    limit = "The selected-time composition is authored-synthetic client evidence and cannot become a second scheduler, command path or live-product claim."
    if limit not in compass["map_limits"]:
        compass["map_limits"].insert(0, limit)
    compass["source_graph_revision"] = 286
    compass["map_revision"] = 268
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
