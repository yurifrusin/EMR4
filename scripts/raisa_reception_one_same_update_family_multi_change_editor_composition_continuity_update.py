"""Advance Continuity and Compass for the combined Reception One editor."""

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
NODE_ID = "raisa-reception-one-same-update-family-multi-change-editor-composition"
PARENT = "raisa-reception-one-same-update-family-multi-change-kernel-rehearsal"
SOURCE_HEAD = "daed421954d65c159871585559f45caa32d95aee"
UPDATED_AT = "2026-08-14T18:08:00Z"
PLAN = "docs/raisa-reception-one-same-update-family-multi-change-editor-composition-plan.md"
THREAT = "docs/security/raisa-reception-one-same-update-family-multi-change-editor-composition-threat-model-delta.md"
PRODUCT = [
    "docs/diary/diary.html",
    "docs/diary/diary.js",
    "docs/diary/meta-grid.css",
    "docs/diary/meta-grid.js",
]
UI_TESTS = [
    "review/test_reception_one_selected_action_console.py",
    "review/test_reception_one_time_reschedule_action.py",
    "review/test_reception_one_duration_action.py",
    "review/test_reception_one_practitioner_reassignment_action.py",
    "review/test_reception_one_same_update_family_multi_change_editor_composition.py",
    "review/test_two_projection_truth_parity.py",
]
DEEPSEEK = [
    "orchestration/agent_inbox/codex/raisa-reception-one-same-update-family-multi-change-editor-composition-deepseek-packet.md",
    "orchestration/agent_inbox/codex/raisa-reception-one-same-update-family-multi-change-editor-composition-deepseek-predispatch-receipt.json",
    "orchestration/agent_inbox/codex/raisa-reception-one-same-update-family-multi-change-editor-composition-deepseek-result.json",
]
PREFLIGHT = "orchestration/agent_inbox/codex/raisa-reception-one-same-update-family-multi-change-editor-composition-gemini-worktree-preflight.json"
PACKET = "orchestration/agent_inbox/codex/raisa-reception-one-same-update-family-multi-change-editor-composition-gemini-review-packet.md"
PREDISPATCH = "orchestration/agent_inbox/codex/raisa-reception-one-same-update-family-multi-change-editor-composition-gemini-predispatch-receipt.json"
PRE_ACCEPTANCE = "orchestration/agent_inbox/codex/raisa-reception-one-same-update-family-multi-change-editor-composition-pre-verifier-acceptance-receipt.json"
GEMINI = "orchestration/agent_inbox/antigravity/raisa-reception-one-same-update-family-multi-change-editor-composition-gemini-review-receipt.json"
REGISTER_REVISIONS = [
    "docs/ariadne-agent-error-correction-register-revision-273.md",
    "docs/ariadne-agent-error-correction-register-revision-274.md",
    "docs/ariadne-agent-error-correction-register-revision-275.md",
    "docs/ariadne-agent-error-correction-register-revision-276.md",
    "docs/ariadne-agent-error-correction-register-revision-277.md",
    "docs/ariadne-agent-error-correction-register-revision-278.md",
    "docs/ariadne-agent-error-correction-register-revision-279.md",
    "docs/ariadne-agent-error-correction-register-revision-280.md",
]
CLOSEOUT = "docs/raisa-reception-one-same-update-family-multi-change-editor-composition-closeout.md"
ACCEPTANCE = "orchestration/agent_inbox/codex/raisa-reception-one-same-update-family-multi-change-editor-composition-sol-acceptance.md"
MAILBOX = "orchestration/human_inbox/yuri/2026-08-15--reception-one-same-update-family-multi-change-editor-composition.md"
UPDATER = "scripts/raisa_reception_one_same_update_family_multi_change_editor_composition_continuity_update.py"
CONTINUITY_TEST = "tests/test_raisa_reception_one_same_update_family_multi_change_editor_composition_continuity.py"


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def _evidence() -> list[str]:
    return [
        PLAN,
        THREAT,
        *PRODUCT,
        *UI_TESTS,
        *DEEPSEEK,
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
        "title": "Provider-free Reception One same-update-family multi-change editor composition",
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
                "Time, duration and practitioner are three views over one local provisional draft, not three commands or current truth.",
                "One review enters one existing update-family proposal and every admissible proposal requires one visible explicit human confirmation.",
                "Status remains distinct; no model, adapter, channel or patient representative receives mutation or confirmation authority.",
            ],
        },
        "decisions": [
            {
                "id": "accept-reception-one-same-update-family-multi-change-editor-composition",
                "source": ACCEPTANCE,
                "status": "accepted",
                "summary": "Accept the shared provisional editor, single existing update proposal, forced explicit confirmation and fresh terminal reconciliation.",
            }
        ],
        "claim_scope": [
            "Same-family switching preserves one multi-field draft with zero requests; collapse, status crossing, reselection and interruption discard the entire draft.",
            "One combined review sends the three effective values through one bridge and exactly one existing handleMoveResize call.",
            "Fresh practitioner admission, interval validation, forced confirmation and fresh exact reconciliation prevent partial or optimistic truth promotion.",
            "Gemini passed 173 exact tests at unchanged clean source and the evidence label is route_intercepted_browser_authored_synthetic.",
        ],
        "contract_evidence": [
            {
                "contract_id": "combined-patient-practitioner-time-duration-intent",
                "status": "satisfied",
                "evidence": [PLAN, *UI_TESTS, GEMINI, CLOSEOUT],
                "note": "The visible client composes practitioner, time and duration into one existing atomic update command.",
            },
            {
                "contract_id": "committed-reschedule-availability-reconciliation",
                "status": "satisfied",
                "evidence": [THREAT, *UI_TESTS, GEMINI, CLOSEOUT, ACCEPTANCE],
                "note": "Only explicit confirmation may write and every terminal path rereads current appointment/projection truth.",
            },
        ],
        "evidence": {
            "plans": [PLAN, THREAT],
            "findings": [*REGISTER_REVISIONS],
            "closeouts": [CLOSEOUT, MAILBOX],
            "acceptances": [ACCEPTANCE],
            "receipts": [
                *DEEPSEEK,
                PREFLIGHT,
                PACKET,
                PREDISPATCH,
                PRE_ACCEPTANCE,
                GEMINI,
            ],
            "tests": [*UI_TESTS, CONTINUITY_TEST],
            "artifacts": [*PRODUCT, UPDATER],
        },
        "unresolved_gates": [
            "A read-only post-editor Compass orientation must select the narrowest dependency-satisfied next product tranche.",
            "Conversational execution, patient-channel delegation and live revocation enforcement remain unproved and closed.",
            "Other command/event families, product data, providers, watcher/database runtime, deployment, production and release require separate authority.",
        ],
    }


def _update_handover_and_plan() -> None:
    handover = HANDOVER.read_text(encoding="utf-8")
    relation_old = "The task branch `codex/ariadne-bernie-davida-parallel-seam` must preserve the accepted Reception One same-update-family multi-change kernel rehearsal"
    relation_new = "The task branch `codex/ariadne-bernie-davida-parallel-seam` must preserve the accepted Reception One same-update-family multi-change editor composition at exact source `daed421954d65c159871585559f45caa32d95aee`, the accepted Reception One same-update-family multi-change kernel rehearsal"
    if relation_new not in handover:
        if relation_old not in handover:
            raise SystemExit("Required Git relation anchor missing")
        handover = handover.replace(relation_old, relation_new, 1)

    row = "| Reception One same-update-family multi-change editor composition acceptance | `docs/raisa-reception-one-same-update-family-multi-change-editor-composition-plan.md`, `docs/security/raisa-reception-one-same-update-family-multi-change-editor-composition-threat-model-delta.md`, `docs/diary/diary.html`, `docs/diary/diary.js`, `docs/diary/meta-grid.css`, `docs/diary/meta-grid.js`, `review/test_reception_one_same_update_family_multi_change_editor_composition.py`, `orchestration/agent_inbox/antigravity/raisa-reception-one-same-update-family-multi-change-editor-composition-gemini-review-receipt.json`, `docs/ariadne-agent-error-correction-register-revision-280.md`, `docs/raisa-reception-one-same-update-family-multi-change-editor-composition-closeout.md`, `orchestration/agent_inbox/codex/raisa-reception-one-same-update-family-multi-change-editor-composition-sol-acceptance.md`, `orchestration/human_inbox/yuri/2026-08-15--reception-one-same-update-family-multi-change-editor-composition.md`, `scripts/raisa_reception_one_same_update_family_multi_change_editor_composition_continuity_update.py`, and `tests/test_raisa_reception_one_same_update_family_multi_change_editor_composition_continuity.py` |"
    if row not in handover:
        row_prefix = (
            "| Reception One same-update-family multi-change editor composition "
            "acceptance |"
        )
        existing_rows = [
            line for line in handover.splitlines() if line.startswith(row_prefix)
        ]
        if len(existing_rows) == 1:
            handover = handover.replace(existing_rows[0], row, 1)
        elif existing_rows:
            raise SystemExit("Duplicate combined editor acceptance rows")
        else:
            anchor = next(
                line
                for line in handover.splitlines()
                if line.startswith("| Current result |")
            )
            handover = handover.replace(anchor, row + "\n" + anchor, 1)

    lines = handover.splitlines()
    replacements = {
        "Current result": "| Current result | At Continuity 293 / Compass 275, `raisa_reception_one_same_update_family_multi_change_editor_composition_pass` is accepted at exact reviewed source `daed421954d65c159871585559f45caa32d95aee`. Reception One now composes practitioner, local time and duration as one provisional draft, one existing update proposal and one explicit confirmation with fresh practitioner admission and terminal truth reconciliation. Status remains distinct. Gemini passed the exact 173-test packet at an unchanged clean candidate. |",
        "Next implementation": "| Next implementation | Continue under standing authority with the provider-free read-only `raisa_post_combined_editor_compass_baton_orientation`. Reconcile the accepted Reception One command families, Context Fabric/event-cue horizon, patient-channel foundation and remaining Yuri-owned gates, then freeze the narrowest dependency-satisfied next tranche. It grants no new model/provider, external channel, command/event family, product/patient data, database/watcher runtime, deployment, production, release, Pages or protected-ref authority. Preserve `docs/branding/` and unrelated untracked files; use explicit-path staging only. |",
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
    old_registers = [
        "revisions 2-277 including current `docs/ariadne-agent-error-correction-register-revision-277.md`",
        "revisions 2-278 including current `docs/ariadne-agent-error-correction-register-revision-278.md`",
        "revisions 2-279 including current `docs/ariadne-agent-error-correction-register-revision-279.md`",
    ]
    new_register = "revisions 2-280 including current `docs/ariadne-agent-error-correction-register-revision-280.md`"
    matched_register = next(
        (value for value in old_registers if value in lines[register_index]), None
    )
    if matched_register is not None:
        lines[register_index] = lines[register_index].replace(
            matched_register, new_register, 1
        )
    elif new_register not in lines[register_index]:
        raise SystemExit("Agent-error register handover anchor missing")

    track_index = next(
        i for i, line in enumerate(lines) if line.startswith("| Active product track |")
    )
    old_track = "The same-update-family multi-change kernel rehearsal now passes: practitioner, local time and duration travel through one existing proposal/confirm transaction with current-truth, conflict, practitioner-state, idempotency, audit and rollback/retry proof. A provider-free progressive combined editor composition is next; status remains distinct and conversational activation stays closed."
    new_track = "The same-update-family multi-change kernel and visible combined editor now pass: practitioner, local time and duration share one provisional Reception One draft, one existing proposal/confirm transaction, forced explicit human confirmation and fresh terminal reconciliation. Status remains distinct; conversational and patient-channel activation stay closed. A provider-free read-only post-editor Compass orientation is next."
    if old_track in lines[track_index]:
        lines[track_index] = lines[track_index].replace(old_track, new_track, 1)
    elif new_track not in lines[track_index]:
        raise SystemExit("Active product track editor anchor missing")
    HANDOVER.write_text("\n".join(lines) + "\n", encoding="utf-8")

    plan = MASTER_PLAN.read_text(encoding="utf-8")
    old_plan = """The provider-free same-update-family multi-change kernel rehearsal now passes
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
    new_plan = """The provider-free same-update-family multi-change kernel and visible editor now
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
    if old_plan in plan:
        plan = plan.replace(old_plan, new_plan, 1)
    elif new_plan not in plan:
        raise SystemExit("Master-plan combined editor anchor missing")
    MASTER_PLAN.write_text(plan, encoding="utf-8")


def _complete_latch() -> None:
    latch = json.loads(LATCH.read_text(encoding="utf-8"))
    if latch.get("operation_id") != NODE_ID:
        raise SystemExit("Unexpected active-operation latch")
    latch["status"] = "complete"
    latch["source_head"] = SOURCE_HEAD
    latch["checkpoint"] = {
        "completed_stage": "Accepted at Continuity 293 / Compass 275 after deterministic and independent exact-candidate verification",
        "next_executable_stage": None,
        "retry_counters": {"implementation": 0, "review": 0, "verification": 1},
        "settings_fingerprint": latch["checkpoint"]["settings_fingerprint"],
    }
    latch["user_attention"] = {"required": False, "reason": None}
    latch["resume_after_compaction"] = False
    latch["terminal_response"] = {
        "permitted": True,
        "reason": "accepted_operation_complete",
    }
    _write(LATCH, latch)


def main() -> int:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 292 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 293
        graph["updated_at"] = UPDATED_AT
    elif graph["graph_revision"] == 293 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
    else:
        raise SystemExit("Unexpected combined editor Continuity predecessor")
    _write(GRAPH, graph)

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Expose the proved multi-field update kernel through one safe Reception One provisional editor",
        "outcome": "Practitioner, time and duration now converge on one existing proposal and one explicit confirmation with fresh reconciliation.",
        "evidence": _evidence(),
    }
    if (
        compass["map_revision"] == 274
        and compass["source_graph_revision"] == 292
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 275
        and compass["source_graph_revision"] == 293
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected combined editor Compass predecessor")

    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": "Join the Reception One semantic console to one backend-owned multi-field truth transaction",
        "why_now": "The atomic update kernel passed and could safely support a visible shared draft without adding command authority.",
        "outcome": "Reception One now composes doctor, time and duration provisionally, pauses at explicit confirmation and rereads truth after every terminal outcome.",
        "unlocks": [
            "Run a read-only post-editor programme orientation across the accepted command, context and channel foundations.",
            "Select and freeze the narrowest dependency-satisfied next product tranche without presuming a new authority opening.",
        ],
        "does_not_solve": [
            "No conversational execution, patient-channel delegation or live revocation enforcement is proven.",
            "No additional command or event family is opened by this acceptance.",
            "Product data, providers, watcher/database runtime, deployment, production and release remain closed.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 293 / Compass 275. The provider-free combined Reception One editor passes; a read-only post-editor Compass orientation is next."
    )
    limit = "The combined editor evidence is authored-synthetic and route-intercepted; it does not prove a live backend, conversational or patient-channel authority, delegation revocation, or production operation."
    if limit not in compass["map_limits"]:
        compass["map_limits"].insert(0, limit)
    compass["source_graph_revision"] = 293
    compass["map_revision"] = 275
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
