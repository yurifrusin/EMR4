"""Advance Continuity and Compass for the post-combined-editor orientation."""

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
LATCH = ROOT / "orchestration/continuity/ariadne-active-operation-latch/current.json"
NODE_ID = "raisa-post-combined-editor-compass-baton-orientation"
PARENT = "raisa-reception-one-same-update-family-multi-change-editor-composition"
SOURCE_HEAD = "2ca3a111d2ee9277571ea3c905f22ce78c8e9745"
UPDATED_AT = "2026-08-14T20:42:00Z"
DECISION_ID = "reception-one-appointment-cancellation-direction"
PLAN = "docs/raisa-post-combined-editor-compass-baton-orientation-plan.md"
ORIENTATION = "docs/raisa-post-combined-editor-compass-baton-orientation.md"
THREAT = "docs/security/raisa-post-combined-editor-compass-baton-orientation-threat-model-delta.md"
PREFLIGHT = "orchestration/agent_inbox/codex/raisa-post-combined-editor-compass-baton-orientation-gemini-worktree-preflight.json"
PACKET = "orchestration/agent_inbox/codex/raisa-post-combined-editor-compass-baton-orientation-gemini-review-packet.md"
PRE_ACCEPTANCE = "orchestration/agent_inbox/codex/raisa-post-combined-editor-compass-baton-orientation-pre-verifier-acceptance-receipt.json"
GEMINI = "orchestration/agent_inbox/antigravity/raisa-post-combined-editor-compass-baton-orientation-gemini-review-receipt.json"
INCIDENT = "orchestration/agent_inbox/codex/raisa-post-combined-editor-compass-baton-orientation-pre-verifier-receipt-incident.json"
REGISTER_REVISION = "docs/ariadne-agent-error-correction-register-revision-281.md"
TESTS = [
    "tests/test_raisa_post_combined_editor_compass_baton_orientation_plan.py",
    "tests/test_raisa_post_combined_editor_compass_baton_orientation.py",
]
CLOSEOUT = "docs/raisa-post-combined-editor-compass-baton-orientation-closeout.md"
ACCEPTANCE = "orchestration/agent_inbox/codex/raisa-post-combined-editor-compass-baton-orientation-sol-acceptance.md"
MAILBOX = "orchestration/human_inbox/yuri/2026-08-15--post-combined-editor-programme-orientation.md"
UPDATER = (
    "scripts/raisa_post_combined_editor_compass_baton_orientation_continuity_update.py"
)
CONTINUITY_TEST = (
    "tests/test_raisa_post_combined_editor_compass_baton_orientation_continuity.py"
)


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def _evidence() -> list[str]:
    return [
        PLAN,
        ORIENTATION,
        THREAT,
        PREFLIGHT,
        PACKET,
        PRE_ACCEPTANCE,
        GEMINI,
        INCIDENT,
        REGISTER_REVISION,
        *TESTS,
        CLOSEOUT,
        ACCEPTANCE,
        MAILBOX,
    ]


def _node() -> dict[str, Any]:
    return {
        "id": NODE_ID,
        "title": "Provider-free post-combined-editor Compass and baton orientation",
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
                "The programme is at a genuine Yuri-owned fork; standing continuation authority does not select a new command, channel, event or runtime family.",
                "A future patient-channel or assistant delegation is narrow, expiring and revocable for future acts, including an uncommitted confirmation.",
                "An already committed appointment remains source truth until a separately authorised cancellation or rescheduling command changes it.",
            ],
        },
        "decisions": [
            {
                "id": "accept-post-combined-editor-orientation",
                "source": ACCEPTANCE,
                "status": "accepted",
                "summary": "Accept cancellation as the recommended direction while pausing before its read-only readiness review until Yuri chooses it.",
            }
        ],
        "claim_scope": [
            "Reception One's exact current reach is one status command family and one update family spanning practitioner, local time and duration.",
            "Cancellation is presentation-only in Reception One and has an ordinary Diary delete-to-status compatibility seam requiring a read-only readiness review before reuse.",
            "Context Fabric events remain acceleration hints; source-owned current truth and command-time authority checks remain the correctness kernel.",
            "Gemini passed 115 exact tests and ten challenges at unchanged clean source; evidence is repository_static_authored_synthetic.",
        ],
        "contract_evidence": [
            {
                "contract_id": "combined-patient-practitioner-time-duration-intent",
                "status": "satisfied",
                "evidence": [ORIENTATION, GEMINI, CLOSEOUT],
                "note": "The accepted status and multi-field update reach is reconciled without granting another command family.",
            },
        ],
        "evidence": {
            "plans": [PLAN, THREAT],
            "findings": [ORIENTATION, INCIDENT, REGISTER_REVISION],
            "closeouts": [CLOSEOUT, MAILBOX],
            "acceptances": [ACCEPTANCE],
            "receipts": [PREFLIGHT, PACKET, PRE_ACCEPTANCE, GEMINI],
            "tests": [*TESTS, CONTINUITY_TEST],
            "artifacts": [UPDATER],
        },
        "unresolved_gates": [
            "Yuri must choose whether to begin the recommended cancellation direction before any cancellation-family convergence or UI exposure.",
            "Patient channels, identity, live delegation and revocation enforcement, Stage 3B and another event family remain separate choices or actions.",
            "Operational durability, source/database access, providers, product data, deployment, production and release remain closed.",
        ],
    }


def _update_handover_and_plan() -> None:
    handover = HANDOVER.read_text(encoding="utf-8")
    relation_old = "The task branch `codex/ariadne-bernie-davida-parallel-seam` must preserve the accepted Reception One same-update-family multi-change editor composition"
    relation_new = "The task branch `codex/ariadne-bernie-davida-parallel-seam` must preserve the accepted post-combined-editor programme orientation at exact source `2ca3a111d2ee9277571ea3c905f22ce78c8e9745`, the accepted Reception One same-update-family multi-change editor composition"
    if relation_new not in handover:
        if relation_old not in handover:
            raise SystemExit("Required Git relation anchor missing")
        handover = handover.replace(relation_old, relation_new, 1)

    row = "| Post-combined-editor Compass and baton orientation acceptance | `docs/raisa-post-combined-editor-compass-baton-orientation-plan.md`, `docs/raisa-post-combined-editor-compass-baton-orientation.md`, `docs/security/raisa-post-combined-editor-compass-baton-orientation-threat-model-delta.md`, `orchestration/agent_inbox/antigravity/raisa-post-combined-editor-compass-baton-orientation-gemini-review-receipt.json`, `docs/ariadne-agent-error-correction-register-revision-281.md`, `docs/raisa-post-combined-editor-compass-baton-orientation-closeout.md`, `orchestration/agent_inbox/codex/raisa-post-combined-editor-compass-baton-orientation-sol-acceptance.md`, `orchestration/human_inbox/yuri/2026-08-15--post-combined-editor-programme-orientation.md`, `scripts/raisa_post_combined_editor_compass_baton_orientation_continuity_update.py`, and `tests/test_raisa_post_combined_editor_compass_baton_orientation_continuity.py` |"
    if row not in handover:
        anchor = next(
            line
            for line in handover.splitlines()
            if line.startswith("| Current result |")
        )
        handover = handover.replace(anchor, row + "\n" + anchor, 1)

    lines = handover.splitlines()
    replacements = {
        "Current result": "| Current result | At Continuity 294 / Compass 276, `raisa_post_combined_editor_compass_baton_orientation_pass` is accepted at exact reviewed source `2ca3a111d2ee9277571ea3c905f22ce78c8e9745`. Reception One's existing status and multi-field update families are complete, and the programme is at a genuine Yuri-owned programme fork. Appointment cancellation is recommended, beginning only with a provider-free read-only command-path readiness review. Gemini passed the exact 115-test packet and ten challenges at an unchanged clean candidate. |",
        "Next implementation": "| Next implementation | Paused pending Yuri's programme choice. Recommended: select Reception One appointment cancellation, then begin the provider-free read-only cancellation command-path readiness review. No cancellation implementation, UI exposure or command-family convergence is authorised until Yuri selects this direction. Patient-channel identity/delegation, check-in/waiting-area, Stage 3B, another event family and operational durability remain retained alternatives at their exact gates. Preserve `docs/branding/` and unrelated untracked files; use explicit-path staging only. |",
    }
    for label, replacement in replacements.items():
        prefix = f"| {label} |"
        indices = [i for i, line in enumerate(lines) if line.startswith(prefix)]
        if len(indices) != 1:
            raise SystemExit(f"Expected one handover row for {label}")
        lines[indices[0]] = replacement

    register_index = next(
        i
        for i, line in enumerate(lines)
        if line.startswith("| Ariadne agent error and correction register acceptance |")
    )
    old_register = "revisions 2-280 including current `docs/ariadne-agent-error-correction-register-revision-280.md`"
    new_register = "revisions 2-281 including current `docs/ariadne-agent-error-correction-register-revision-281.md`"
    if old_register in lines[register_index]:
        lines[register_index] = lines[register_index].replace(
            old_register, new_register, 1
        )
    elif new_register not in lines[register_index]:
        raise SystemExit("Agent-error register handover anchor missing")

    track_index = next(
        i for i, line in enumerate(lines) if line.startswith("| Active product track |")
    )
    old_track = "A provider-free read-only post-editor Compass orientation is next."
    new_track = "The post-editor orientation now records a genuine Yuri-owned fork. Appointment cancellation is recommended, beginning only with a read-only command-path readiness review after Yuri chooses it; patient-channel delegation, check-in, Stage 3B, another event family and operational durability remain retained at their exact gates."
    if old_track in lines[track_index]:
        lines[track_index] = lines[track_index].replace(old_track, new_track, 1)
    elif new_track not in lines[track_index]:
        raise SystemExit("Active product track orientation anchor missing")
    HANDOVER.write_text("\n".join(lines) + "\n", encoding="utf-8")

    plan = MASTER_PLAN.read_text(encoding="utf-8")
    old_plan = """The provider-free same-update-family multi-change kernel and visible editor now
pass at exact reviewed editor source
`daed421954d65c159871585559f45caa32d95aee`. Practitioner, local time and
duration share one provisional Reception One draft, one existing update
proposal and one explicit confirmation. Same-family switching is request-free;
collapse, status crossing, reselection and interruption discard the draft.
Fresh practitioner admission and exact terminal reconciliation prevent partial
or optimistic truth promotion. Status remains separate and conversational
activation stays closed. The next narrow descendant is a provider-free,
read-only post-editor Compass orientation before another product family is
opened. No watcher runtime, product data, external patient client, new command
family, provider, deployment, production or release is opened."""
    new_plan = """The provider-free same-update-family multi-change kernel and visible editor pass
at exact reviewed editor source
`daed421954d65c159871585559f45caa32d95aee`. The subsequent read-only programme
orientation passes at exact reviewed source
`2ca3a111d2ee9277571ea3c905f22ce78c8e9745`. It finds a genuine Yuri-owned
fork: appointment cancellation is recommended, but Yuri's programme choice is
required before the provider-free read-only cancellation command-path readiness
review begins. That review must classify the ordinary Diary delete-to-status
compatibility seam before any destructive Reception One UI or command-family
convergence. Patient-channel delegation, check-in, Stage 3B, another event
family and operational durability remain retained at their exact gates. No
watcher runtime, product data, external patient client, new command family,
provider, deployment, production or release is opened."""
    if old_plan in plan:
        plan = plan.replace(old_plan, new_plan, 1)
    elif new_plan not in plan:
        raise SystemExit("Master-plan post-editor orientation anchor missing")
    MASTER_PLAN.write_text(plan, encoding="utf-8")


def _complete_latch() -> None:
    latch = json.loads(LATCH.read_text(encoding="utf-8"))
    if latch.get("operation_id") != NODE_ID:
        raise SystemExit("Unexpected active-operation latch")
    latch["status"] = "blocked"
    latch["source_head"] = SOURCE_HEAD
    latch["checkpoint"] = {
        "completed_stage": "Accepted at Continuity 294 / Compass 276 after deterministic and independent exact-candidate verification",
        "next_executable_stage": None,
        "retry_counters": {"planning": 1, "review": 1, "verification": 0},
        "settings_fingerprint": latch["checkpoint"]["settings_fingerprint"],
    }
    latch["user_attention"] = {
        "required": True,
        "reason": "Yuri must choose whether to pursue the recommended appointment-cancellation direction before its read-only readiness review begins.",
    }
    latch["resume_after_compaction"] = False
    latch["terminal_response"] = {
        "permitted": True,
        "reason": "genuine_user_attention_fork",
    }
    _write(LATCH, latch)


def main() -> int:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 293 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 294
        graph["updated_at"] = UPDATED_AT
    elif graph["graph_revision"] == 294 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
    else:
        raise SystemExit("Unexpected post-editor orientation Continuity predecessor")
    _write(GRAPH, graph)

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Reconcile the completed Reception One command set and expose the next material programme choice",
        "outcome": "The programme is at a genuine Yuri-owned fork; cancellation is recommended and begins only with a read-only readiness review if selected.",
        "evidence": _evidence(),
    }
    if (
        compass["map_revision"] == 275
        and compass["source_graph_revision"] == 293
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 276
        and compass["source_graph_revision"] == 294
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected post-editor orientation Compass predecessor")

    horizon = {
        "id": DECISION_ID,
        "title": "Reception One appointment cancellation direction",
        "status": "candidate",
        "strategic_question": "Should Reception One pursue appointment cancellation next, beginning with a provider-free read-only cancellation command-path readiness review?",
        "why_it_matters": "Cancellation is a high-value selected-appointment action, but the ordinary Diary's delete-to-status fallback and Reception One's missing bridge must be classified before destructive behavior is exposed in a second renderer.",
        "prerequisites": [
            "Yuri selects appointment cancellation as the next programme direction.",
            "The first tranche remains provider-free and repository-read-only.",
            "No cancellation UI, command-family convergence or write is inferred from the review.",
        ],
        "boundary_changes": [],
        "evidence": [ORIENTATION, THREAT, CLOSEOUT, ACCEPTANCE, MAILBOX],
    }
    existing = next(
        (
            index
            for index, item in enumerate(compass["decision_horizon"])
            if item["id"] == DECISION_ID
        ),
        None,
    )
    if existing is None:
        compass["decision_horizon"].insert(0, horizon)
    else:
        compass["decision_horizon"][existing] = horizon

    user_decision = {
        "id": DECISION_ID,
        "question": horizon["strategic_question"],
        "required_before": "Yuri's choice is required before any cancellation family convergence or UI exposure; if selected, only the provider-free read-only readiness review starts.",
        "evidence": [ORIENTATION, CLOSEOUT, ACCEPTANCE, MAILBOX],
    }
    existing_decision = next(
        (
            index
            for index, item in enumerate(compass["user_owned_decisions"])
            if item["id"] == DECISION_ID
        ),
        None,
    )
    if existing_decision is None:
        compass["user_owned_decisions"].append(user_decision)
    else:
        compass["user_owned_decisions"][existing_decision] = user_decision

    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": "Pause honestly at the first post-console material programme choice",
        "why_now": "Reception One's accepted status and multi-field update families are complete, while every high-value successor changes meaning or authority.",
        "outcome": "Cancellation is recommended, but no implementation or readiness review begins until Yuri selects that direction.",
        "unlocks": [
            "If Yuri agrees, freeze the provider-free read-only cancellation command-path readiness review.",
            "Retain patient-channel delegation, check-in, Stage 3B, event-family and operational durability horizons without activating them.",
        ],
        "does_not_solve": [
            "No cancellation family, control, runtime or safety property is implemented or accepted.",
            "No live patient identity, delegation or revocation enforcement exists.",
            "Product data, providers, watcher/database runtime, deployment, production and release remain closed.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 294 / Compass 276. Reception One's first status and update console is complete; cancellation is recommended at a genuine Yuri-owned programme fork."
    )
    limit = "The post-editor orientation is repository-static evidence and opens no cancellation command, patient-channel delegation, live revocation, database/watcher runtime or production authority."
    if limit not in compass["map_limits"]:
        compass["map_limits"].insert(0, limit)
    compass["source_graph_revision"] = 294
    compass["map_revision"] = 276
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)

    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")
    _update_handover_and_plan()
    _complete_latch()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
