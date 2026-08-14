"""Advance Continuity and Compass for the combined update kernel rehearsal."""

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
NODE_ID = "raisa-reception-one-same-update-family-multi-change-kernel-rehearsal"
PARENT = "raisa-reception-one-multi-change-request-atomicity-orientation"
SOURCE_HEAD = "3dd5f3b39ed98a2d562685d1d1567a359930c693"
UPDATED_AT = "2026-08-14T14:46:56Z"
PLAN = (
    "docs/raisa-reception-one-same-update-family-multi-change-kernel-rehearsal-plan.md"
)
THREAT = "docs/security/raisa-reception-one-same-update-family-multi-change-kernel-rehearsal-threat-model-delta.md"
TEST = (
    "tests/test_raisa_reception_one_same_update_family_multi_change_kernel_rehearsal.py"
)
PREFLIGHT = "orchestration/agent_inbox/codex/raisa-reception-one-same-update-family-multi-change-kernel-rehearsal-gemini-worktree-preflight.json"
PACKET = "orchestration/agent_inbox/codex/raisa-reception-one-same-update-family-multi-change-kernel-rehearsal-gemini-review-packet.md"
PREDISPATCH = "orchestration/agent_inbox/codex/raisa-reception-one-same-update-family-multi-change-kernel-rehearsal-gemini-predispatch-receipt.json"
PRE_ACCEPTANCE = "orchestration/agent_inbox/codex/raisa-reception-one-same-update-family-multi-change-kernel-rehearsal-pre-verifier-acceptance-receipt.json"
GEMINI = "orchestration/agent_inbox/antigravity/raisa-reception-one-same-update-family-multi-change-kernel-rehearsal-gemini-review-receipt.json"
REGISTER_REVISIONS = [
    "docs/ariadne-agent-error-correction-register-revision-270.md",
    "docs/ariadne-agent-error-correction-register-revision-271.md",
    "docs/ariadne-agent-error-correction-register-revision-272.md",
]
CLOSEOUT = "docs/raisa-reception-one-same-update-family-multi-change-kernel-rehearsal-closeout.md"
ACCEPTANCE = "orchestration/agent_inbox/codex/raisa-reception-one-same-update-family-multi-change-kernel-rehearsal-sol-acceptance.md"
MAILBOX = "orchestration/human_inbox/yuri/2026-08-15--reception-one-same-update-family-multi-change-kernel-rehearsal.md"
UPDATER = "scripts/raisa_reception_one_same_update_family_multi_change_kernel_rehearsal_continuity_update.py"
CONTINUITY_TEST = "tests/test_raisa_reception_one_same_update_family_multi_change_kernel_rehearsal_continuity.py"


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def _evidence() -> list[str]:
    return [
        PLAN,
        THREAT,
        TEST,
        PREFLIGHT,
        PACKET,
        PREDISPATCH,
        PRE_ACCEPTANCE,
        GEMINI,
        *REGISTER_REVISIONS,
        CLOSEOUT,
        ACCEPTANCE,
        MAILBOX,
    ]


def _node() -> dict[str, Any]:
    return {
        "id": NODE_ID,
        "title": "Provider-free Reception One same-update-family multi-change kernel rehearsal",
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
                "The existing update proposal/confirm kernel accepts practitioner, local time and duration as one closed command, never three client writes.",
                "Current appointment truth, target conflict and practitioner state are rechecked before one explicit confirmation can commit.",
                "Status remains a distinct command family and no model, adapter or channel receives confirmation or write authority.",
            ],
        },
        "decisions": [
            {
                "id": "accept-reception-one-same-update-family-multi-change-kernel-rehearsal",
                "source": ACCEPTANCE,
                "status": "accepted",
                "summary": "Accept M1-M7 as proof of one atomic practitioner/time/duration update with denial, replay and rollback safety.",
            }
        ],
        "claim_scope": [
            "One combined practitioner, local time and duration proposal is non-mutating and one confirmation commits all three fields with one correlated audit and idempotency result.",
            "Stale appointment truth, a new target conflict and target-practitioner inactivation deny the entire candidate without retained effects.",
            "Fresh-session exact replay is mutation-free, different-body key reuse conflicts, and post-flush pre-commit failure rolls every effect back before clean retry.",
            "Gemini passed 412 exact tests at unchanged clean source and the evidence label is provider_free_live_local_backend_postgresql_authored_synthetic.",
        ],
        "contract_evidence": [
            {
                "contract_id": "committed-reschedule-availability-reconciliation",
                "status": "satisfied",
                "evidence": [PLAN, THREAT, TEST, CLOSEOUT],
                "note": "Combined update confirmation revalidates current truth, target availability and practitioner state before one commit.",
            },
            {
                "contract_id": "combined-patient-practitioner-time-duration-intent",
                "status": "satisfied",
                "evidence": [TEST, GEMINI, ACCEPTANCE],
                "note": "One appointment outcome, audit and idempotency result remain correlated across success, replay and rollback/retry.",
            },
        ],
        "evidence": {
            "plans": [PLAN, THREAT],
            "findings": [*REGISTER_REVISIONS],
            "closeouts": [CLOSEOUT, MAILBOX],
            "acceptances": [ACCEPTANCE],
            "receipts": [PREFLIGHT, PACKET, PREDISPATCH, PRE_ACCEPTANCE, GEMINI],
            "tests": [TEST, CONTINUITY_TEST],
            "artifacts": [UPDATER],
        },
        "unresolved_gates": [
            "Compose the proven practitioner/time/duration command into one progressive Reception One editor with one review and explicit confirmation.",
            "No browser/editor evidence, conversational execution, patient-channel delegation or cross-family atomic command is yet proven.",
            "Product data, providers, watcher runtime, deployment, production and release remain closed.",
        ],
    }


def _update_handover_and_plan() -> None:
    handover = HANDOVER.read_text(encoding="utf-8")
    relation_old = "The task branch `codex/ariadne-bernie-davida-parallel-seam` must preserve the accepted Reception One multi-change request atomicity orientation"
    relation_new = "The task branch `codex/ariadne-bernie-davida-parallel-seam` must preserve the accepted Reception One same-update-family multi-change kernel rehearsal at exact source `3dd5f3b39ed98a2d562685d1d1567a359930c693`, the accepted Reception One multi-change request atomicity orientation"
    if relation_new not in handover:
        if relation_old not in handover:
            raise SystemExit("Required Git relation anchor missing")
        handover = handover.replace(relation_old, relation_new, 1)

    row = "| Reception One same-update-family multi-change kernel rehearsal acceptance | `docs/raisa-reception-one-same-update-family-multi-change-kernel-rehearsal-plan.md`, `docs/security/raisa-reception-one-same-update-family-multi-change-kernel-rehearsal-threat-model-delta.md`, `tests/test_raisa_reception_one_same_update_family_multi_change_kernel_rehearsal.py`, `orchestration/agent_inbox/antigravity/raisa-reception-one-same-update-family-multi-change-kernel-rehearsal-gemini-review-receipt.json`, `docs/ariadne-agent-error-correction-register-revision-272.md`, `docs/raisa-reception-one-same-update-family-multi-change-kernel-rehearsal-closeout.md`, `orchestration/agent_inbox/codex/raisa-reception-one-same-update-family-multi-change-kernel-rehearsal-sol-acceptance.md`, `orchestration/human_inbox/yuri/2026-08-15--reception-one-same-update-family-multi-change-kernel-rehearsal.md`, `scripts/raisa_reception_one_same_update_family_multi_change_kernel_rehearsal_continuity_update.py`, and `tests/test_raisa_reception_one_same_update_family_multi_change_kernel_rehearsal_continuity.py` |"
    if row not in handover:
        anchor = next(
            line
            for line in handover.splitlines()
            if line.startswith("| Current result |")
        )
        handover = handover.replace(anchor, row + "\n" + anchor, 1)

    lines = handover.splitlines()
    replacements = {
        "Current result": "| Current result | At Continuity 292 / Compass 274, `raisa_reception_one_same_update_family_multi_change_kernel_rehearsal_pass` is accepted at exact reviewed source `3dd5f3b39ed98a2d562685d1d1567a359930c693`. The unchanged existing update proposal/confirm kernel passes all seven combined practitioner/time/duration scenarios: proposal non-mutation, one correlated commit, stale-truth denial, new-conflict denial, inactive-practitioner denial, exact replay/body conflict and transaction-wide rollback before clean retry. Gemini passed 412 exact tests at an unchanged clean candidate. No product source changed. |",
        "Next implementation": "| Next implementation | Continue under standing authority with the provider-free `raisa_reception_one_same_update_family_multi_change_editor_composition`. Compose practitioner, local time and duration into one progressive Reception One draft, one existing update-family proposal, one review and one explicit confirmation. Status remains distinct. Reuse the canonical route and fresh reconciliation; add no new backend command, conversational execution or external patient/channel authority. No product/patient data, provider/ADC, credentials/IAM/network, deployment, production, release, Pages or protected-ref movement is inferred. Preserve `docs/branding/` and unrelated untracked files; use explicit-path staging only. |",
    }
    for label, replacement in replacements.items():
        prefix = f"| {label} |"
        indices = [i for i, line in enumerate(lines) if line.startswith(prefix)]
        if len(indices) != 1:
            raise SystemExit(f"Expected one handover row for {label}")
        lines[indices[0]] = replacement

    register_prefix = "| Ariadne agent error and correction register acceptance |"
    register_index = next(
        i for i, line in enumerate(lines) if line.startswith(register_prefix)
    )
    old_register = "revisions 2-269 including current `docs/ariadne-agent-error-correction-register-revision-269.md`"
    new_register = "revisions 2-272 including current `docs/ariadne-agent-error-correction-register-revision-272.md`"
    if old_register in lines[register_index]:
        lines[register_index] = lines[register_index].replace(
            old_register, new_register, 1
        )
    elif new_register not in lines[register_index]:
        raise SystemExit("Agent-error register handover anchor missing")

    track_index = next(
        i for i, line in enumerate(lines) if line.startswith("| Active product track |")
    )
    old_track = "The multi-change request atomicity orientation now freezes typed inert candidates: time, duration and practitioner may share one update proposal and confirmation, while status remains separate and cross-family requests are non-executable. The same-update-family multi-change kernel rehearsal is next before any compound editor or conversational activation."
    new_track = "The same-update-family multi-change kernel rehearsal now passes: practitioner, local time and duration travel through one existing proposal/confirm transaction with current-truth, conflict, practitioner-state, idempotency, audit and rollback/retry proof. A provider-free progressive combined editor composition is next; status remains distinct and conversational activation stays closed."
    if old_track in lines[track_index]:
        lines[track_index] = lines[track_index].replace(old_track, new_track, 1)
    elif new_track not in lines[track_index]:
        raise SystemExit("Active product track kernel anchor missing")
    HANDOVER.write_text("\n".join(lines) + "\n", encoding="utf-8")

    plan = MASTER_PLAN.read_text(encoding="utf-8")
    old_plan = """The provider-free multi-change request atomicity orientation now passes at
exact reviewed source `fbb7ffb46e041bbfc193ff3a76b2f970c06dee58`.
Raisa and future adapters may emit only typed inert candidates. Time, duration
and practitioner may compose into one existing update-family proposal and one
explicit confirmation; status remains separate and cross-family requests stay
non-executable. The next narrow descendant is an authored-synthetic kernel
rehearsal of practitioner, time and duration together through the existing
update path, including stale truth, conflict, idempotency, audit and rollback.
No watcher runtime, existing product data, external patient client, new command
family, provider, deployment, production or release is opened."""
    new_plan = """The provider-free same-update-family multi-change kernel rehearsal now passes
at exact reviewed source `3dd5f3b39ed98a2d562685d1d1567a359930c693`.
The unchanged existing update proposal/confirm path handles practitioner, local
time and duration as one command with proposal non-mutation, current-truth and
target-state denials, one correlated audit/idempotency outcome, exact replay,
different-body conflict and transaction-wide rollback before clean retry. The
next narrow descendant is a provider-free progressive Reception One combined
editor composition over that exact command; status remains separate and
conversational activation stays closed. No watcher runtime, product data,
external patient client, new command family, provider, deployment, production
or release is opened."""
    if old_plan in plan:
        plan = plan.replace(old_plan, new_plan, 1)
    elif new_plan not in plan:
        raise SystemExit("Master-plan combined kernel anchor missing")
    MASTER_PLAN.write_text(plan, encoding="utf-8")


def main() -> int:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 291 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 292
        graph["updated_at"] = UPDATED_AT
    elif graph["graph_revision"] == 292 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
    else:
        raise SystemExit("Unexpected combined kernel Continuity predecessor")
    _write(GRAPH, graph)

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Prove the atomic backend kernel before exposing a combined Reception One editor",
        "outcome": "One practitioner/time/duration command now has denial, replay, audit, idempotency and rollback evidence without product-source change.",
        "evidence": _evidence(),
    }
    if (
        compass["map_revision"] == 273
        and compass["source_graph_revision"] == 291
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 274
        and compass["source_graph_revision"] == 292
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected combined kernel Compass predecessor")

    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": "Put compound Reception One interactions on one backend-owned truth transaction",
        "why_now": "The safe multi-change semantics were frozen and required exact kernel proof before visible compound composition.",
        "outcome": "The existing update command now proves all-or-none practitioner, time and duration behavior across success, denial, replay and rollback.",
        "unlocks": [
            "Compose practitioner, local time and duration into one progressive Reception One draft, review and explicit confirmation.",
            "Reuse the existing canonical route and fresh reconciliation without adding a backend command.",
        ],
        "does_not_solve": [
            "No browser/editor composition or conversational execution is yet proven.",
            "Status remains a distinct command family and cross-family atomicity remains closed.",
            "Patient channels, product data, providers, deployment, production and release remain closed.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 292 / Compass 274. The combined practitioner/time/duration update kernel passes; one provider-free progressive Reception One editor composition is next."
    )
    limit = "The combined update rehearsal is authored-synthetic local PostgreSQL evidence; it does not prove a browser editor, conversational activation, patient delegation or production operation."
    if limit not in compass["map_limits"]:
        compass["map_limits"].insert(0, limit)
    compass["source_graph_revision"] = 292
    compass["map_revision"] = 274
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
