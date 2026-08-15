"""Advance Continuity and Compass for the cancellation readiness review."""

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
COMPASS_REPORT = ROOT / "docs/ariadne-compass-current.md"
HANDOVER = ROOT / "AGENTS.md"
MASTER_PLAN = ROOT / "implementation_plan.md"
LATCH = ROOT / "orchestration/continuity/ariadne-active-operation-latch/current.json"

NODE_ID = "raisa-reception-one-cancellation-command-path-readiness-review"
PARENT = "raisa-post-combined-editor-compass-baton-orientation"
SOURCE_HEAD = "bb36e19c774eb1bc4ace8cafc6ae2b5c35bc8735"
UPDATED_AT = "2026-08-15T01:33:02Z"
DECISION_ID = "reception-one-appointment-cancellation-direction"
NEXT_HORIZON_ID = "reception-one-delete-confirm-conditional-command-kernel"

PLAN = "docs/raisa-reception-one-cancellation-command-path-readiness-review-plan.md"
REPORT = "docs/raisa-reception-one-cancellation-command-path-readiness-review.md"
THREAT = "docs/security/raisa-reception-one-cancellation-command-path-readiness-review-threat-model-delta.md"
PREPLANNING = "orchestration/agent_inbox/codex/raisa-reception-one-cancellation-command-path-readiness-review-preplanning-receipt.json"
PREFLIGHT = "orchestration/agent_inbox/codex/raisa-reception-one-cancellation-command-path-readiness-review-gemini-worktree-preflight.json"
PACKET = "orchestration/agent_inbox/codex/raisa-reception-one-cancellation-command-path-readiness-review-gemini-review-packet.md"
PRE_ACCEPTANCE = "orchestration/agent_inbox/codex/raisa-reception-one-cancellation-command-path-readiness-review-pre-verifier-acceptance-receipt.json"
GEMINI = "orchestration/agent_inbox/antigravity/raisa-reception-one-cancellation-command-path-readiness-review-gemini-review-receipt.json"
TEST = "tests/test_raisa_reception_one_cancellation_command_path_readiness_review.py"
CLOSEOUT = "docs/raisa-reception-one-cancellation-command-path-readiness-review-closeout.md"
ACCEPTANCE = "orchestration/agent_inbox/codex/raisa-reception-one-cancellation-command-path-readiness-review-sol-acceptance.md"
MAILBOX = "orchestration/human_inbox/yuri/2026-08-15--reception-one-cancellation-command-path-readiness-review.md"
UPDATER = "scripts/raisa_reception_one_cancellation_command_path_readiness_review_continuity_update.py"
CONTINUITY_TEST = "tests/test_raisa_reception_one_cancellation_command_path_readiness_review_continuity.py"


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def _evidence() -> list[str]:
    return [
        PLAN,
        REPORT,
        THREAT,
        PREPLANNING,
        PREFLIGHT,
        PACKET,
        PRE_ACCEPTANCE,
        GEMINI,
        TEST,
        CLOSEOUT,
        ACCEPTANCE,
        MAILBOX,
    ]


def _node() -> dict[str, Any]:
    return {
        "id": NODE_ID,
        "title": "Reception One cancellation command-path readiness review",
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
                "Yuri selected appointment cancellation; the review itself changes no product or runtime source.",
                "The dedicated delete family retains explicit human confirmation, signed evidence, idempotency, audit and fresh readback.",
                "Reception One composition waits for a provider-free unmounted locked-truth/current-authority kernel architecture and admission rehearsal.",
            ],
        },
        "decisions": [
            {
                "id": "accept-cancellation-command-path-readiness-review",
                "source": ACCEPTANCE,
                "status": "accepted",
                "summary": "Accept the dedicated delete family as the convergence base, but require an unmounted conditional-command kernel prerequisite before UI reuse.",
            }
        ],
        "claim_scope": [
            "The current delete confirm path has explicit confirmation, signed actor/practice/command/current-state evidence, freshness, reason preservation, idempotency, audit and result readback.",
            "It does not lock the appointment or explicitly recheck current actor authority inside its mutation transaction; current differently-keyed coverage is serial.",
            "The native Diary 404 fallback crosses into status confirmation and omits free-text cancellation reason while retaining explicit and signed confirmation.",
            "OpenAPI/runtime delete proposal and confirmation path/payload shapes are not exact; evidence is repository_static_authored_synthetic.",
            "Gemini passed 188 exact tests and ten challenges at unchanged clean source.",
        ],
        "contract_evidence": [
            {
                "contract_id": "combined-patient-practitioner-time-duration-intent",
                "status": "satisfied",
                "evidence": [REPORT, GEMINI, CLOSEOUT],
                "note": "The exact existing cancellation routes and missing conditional-command safeguards are frozen before any Reception One exposure.",
            }
        ],
        "evidence": {
            "plans": [PLAN, THREAT],
            "findings": [REPORT],
            "closeouts": [CLOSEOUT, MAILBOX],
            "acceptances": [ACCEPTANCE],
            "receipts": [PREPLANNING, PREFLIGHT, PACKET, PRE_ACCEPTANCE, GEMINI],
            "tests": [TEST, CONTINUITY_TEST],
            "artifacts": [UPDATER],
        },
        "unresolved_gates": [
            "Mounted delete route, database and native client convergence remain unproved and closed.",
            "Reception One cancellation UI remains closed until the kernel and later product-integration gates pass.",
            "Raw compatibility delete remains mounted and must not become a new product-client path.",
            "Patient channels, product data, providers, deployment, production and release remain closed.",
        ],
    }


def _update_handover_and_plan() -> None:
    handover = HANDOVER.read_text(encoding="utf-8")
    relation_old = "The task branch `codex/ariadne-bernie-davida-parallel-seam` must preserve the accepted post-combined-editor programme orientation"
    relation_new = "The task branch `codex/ariadne-bernie-davida-parallel-seam` must preserve the accepted Reception One cancellation command-path readiness review at exact source `bb36e19c774eb1bc4ace8cafc6ae2b5c35bc8735`, the accepted post-combined-editor programme orientation"
    if relation_new not in handover:
        if relation_old not in handover:
            raise SystemExit("Required Git relation anchor missing")
        handover = handover.replace(relation_old, relation_new, 1)

    row = "| Reception One cancellation command-path readiness review acceptance | `docs/raisa-reception-one-cancellation-command-path-readiness-review-plan.md`, `docs/raisa-reception-one-cancellation-command-path-readiness-review.md`, `docs/security/raisa-reception-one-cancellation-command-path-readiness-review-threat-model-delta.md`, `orchestration/agent_inbox/antigravity/raisa-reception-one-cancellation-command-path-readiness-review-gemini-review-receipt.json`, `docs/raisa-reception-one-cancellation-command-path-readiness-review-closeout.md`, `orchestration/agent_inbox/codex/raisa-reception-one-cancellation-command-path-readiness-review-sol-acceptance.md`, `orchestration/human_inbox/yuri/2026-08-15--reception-one-cancellation-command-path-readiness-review.md`, `scripts/raisa_reception_one_cancellation_command_path_readiness_review_continuity_update.py`, and `tests/test_raisa_reception_one_cancellation_command_path_readiness_review_continuity.py` |"
    if row not in handover:
        anchor = next(
            line for line in handover.splitlines() if line.startswith("| Current result |")
        )
        handover = handover.replace(anchor, row + "\n" + anchor, 1)

    lines = handover.splitlines()
    replacements = {
        "Current result": "| Current result | At Continuity 295 / Compass 277, `raisa_reception_one_cancellation_command_path_readiness_review_pass` is accepted at exact reviewed source `bb36e19c774eb1bc4ace8cafc6ae2b5c35bc8735`. The dedicated cancellation family already has explicit confirmation, signed evidence, freshness, reason preservation, idempotency, audit and readback, but lacks a locked appointment read and explicit in-transaction current-authority recheck. The native Diary's 404 status fallback omits free-text cancellation reason. Seven focused checks, 188 cancellation/API tests, the 196-test canonical fast profile and Gemini's ten exact challenges pass. |",
        "Next implementation": "| Next implementation | The provider-free unmounted delete-confirm conditional-command kernel architecture and admission rehearsal is the next dependency-satisfied tranche. Freeze a typed locked-truth/current-authority/idempotency/audit transaction contract against authored-synthetic scenarios only. No mounted route, OpenAPI, database, product client, UI exposure, provider, patient/product data, deployment, production, release, Pages or protected-ref change is authorised. Patient-channel identity/delegation, check-in/waiting-area, Stage 3B, another event family and operational durability remain retained but inactive. Preserve `docs/branding/` and unrelated untracked files; use explicit-path staging only. |",
    }
    for label, replacement in replacements.items():
        prefix = f"| {label} |"
        indices = [i for i, line in enumerate(lines) if line.startswith(prefix)]
        if len(indices) != 1:
            raise SystemExit(f"Expected one handover row for {label}")
        lines[indices[0]] = replacement

    track_index = next(
        i for i, line in enumerate(lines) if line.startswith("| Active product track |")
    )
    old_track = "The post-editor orientation now records a genuine Yuri-owned fork. Appointment cancellation is recommended, beginning only with a read-only command-path readiness review after Yuri chooses it; patient-channel delegation, check-in, Stage 3B, another event family and operational durability remain retained at their exact gates."
    new_track = "Yuri selected appointment cancellation. Its repository-static command-path readiness review now passes: the dedicated delete family is the convergence base, but a provider-free unmounted locked-truth/current-authority kernel architecture must precede any mounted route or Reception One UI composition. The native Diary's delete-to-status fallback is not inherited by Reception One. Patient-channel delegation, check-in, Stage 3B, another event family and operational durability remain retained at their exact gates."
    if old_track in lines[track_index]:
        lines[track_index] = lines[track_index].replace(old_track, new_track, 1)
    elif new_track not in lines[track_index]:
        raise SystemExit("Active product track cancellation anchor missing")
    HANDOVER.write_text("\n".join(lines) + "\n", encoding="utf-8")

    plan = MASTER_PLAN.read_text(encoding="utf-8")
    old_plan = """The provider-free same-update-family multi-change kernel and visible editor pass
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
    new_plan = """The provider-free same-update-family multi-change kernel and visible editor pass
at exact reviewed editor source
`daed421954d65c159871585559f45caa32d95aee`. The subsequent programme
orientation passes at `2ca3a111d2ee9277571ea3c905f22ce78c8e9745`, Yuri selected
appointment cancellation, and its repository-static command-path readiness
review passes at exact reviewed source
`bb36e19c774eb1bc4ace8cafc6ae2b5c35bc8735`. The dedicated delete family is
the convergence base, but its confirm transaction lacks a locked appointment
read and explicit in-transaction current-authority recheck; the native Diary's
404 status fallback also omits free-text cancellation reason. The next narrow
descendant is a provider-free unmounted delete-confirm conditional-command
kernel architecture and admission rehearsal before any mounted route,
PostgreSQL or Reception One UI change. Patient-channel delegation, check-in,
Stage 3B, another event family and operational durability remain retained at
their exact gates. No watcher runtime, product data, external patient client,
provider, deployment, production or release is opened."""
    if old_plan in plan:
        plan = plan.replace(old_plan, new_plan, 1)
    elif new_plan not in plan:
        raise SystemExit("Master-plan cancellation-readiness anchor missing")
    MASTER_PLAN.write_text(plan, encoding="utf-8")


def _complete_latch() -> None:
    latch = json.loads(LATCH.read_text(encoding="utf-8"))
    if latch.get("operation_id") != NODE_ID:
        raise SystemExit("Unexpected active-operation latch")
    latch["status"] = "complete"
    latch["source_head"] = SOURCE_HEAD
    latch["checkpoint"] = {
        "completed_stage": "Accepted at Continuity 295 / Compass 277 after deterministic and independent exact-candidate verification",
        "next_executable_stage": None,
        "retry_counters": {"planning": 0, "review": 1, "verification": 0},
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
    if graph["graph_revision"] == 294 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 295
        graph["updated_at"] = UPDATED_AT
    elif graph["graph_revision"] == 295 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
    else:
        raise SystemExit("Unexpected cancellation readiness Continuity predecessor")
    _write(GRAPH, graph)

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Map the existing cancellation family and freeze its smallest assurance prerequisite",
        "outcome": "The dedicated delete family is the convergence base; an unmounted locked-truth/current-authority kernel architecture must precede Reception One composition.",
        "evidence": _evidence(),
    }
    if (
        compass["map_revision"] == 276
        and compass["source_graph_revision"] == 294
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 277
        and compass["source_graph_revision"] == 295
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected cancellation readiness Compass predecessor")

    cancellation_horizon = next(
        item for item in compass["decision_horizon"] if item["id"] == DECISION_ID
    )
    cancellation_horizon.update(
        {
            "status": "active",
            "strategic_question": "Yuri selected Reception One appointment cancellation; its command-path readiness review now passes.",
            "why_it_matters": "The existing delete family is retained as the convergence base while its exact locked-truth/current-authority prerequisite is made explicit before UI exposure.",
            "prerequisites": [
                "Complete the provider-free unmounted delete-confirm conditional-command kernel architecture and admission rehearsal.",
                "Keep mounted route, PostgreSQL and UI integration as later gates.",
            ],
            "boundary_changes": [],
            "evidence": [REPORT, GEMINI, CLOSEOUT, ACCEPTANCE, MAILBOX],
        }
    )
    compass["user_owned_decisions"] = [
        item for item in compass["user_owned_decisions"] if item["id"] != DECISION_ID
    ]

    next_horizon = {
        "id": NEXT_HORIZON_ID,
        "title": "Reception One delete-confirm conditional-command kernel",
        "status": "active",
        "strategic_question": "How should the dedicated cancellation family lock current truth and recheck current actor authority atomically before later runtime convergence?",
        "why_it_matters": "Cancellation is destructive; UI composition should inherit one backend-owned transaction with current truth, current authority, confirmation, idempotency, audit and readback.",
        "prerequisites": [
            "Provider-free authored-synthetic unmounted architecture only.",
            "No mounted route, database, product client or UI source change.",
            "Preserve explicit human confirmation and the existing signed delete evidence semantics.",
        ],
        "boundary_changes": [],
        "evidence": [REPORT, THREAT, CLOSEOUT, ACCEPTANCE],
    }
    existing = next(
        (i for i, item in enumerate(compass["decision_horizon"]) if item["id"] == NEXT_HORIZON_ID),
        None,
    )
    if existing is None:
        compass["decision_horizon"].insert(0, next_horizon)
    else:
        compass["decision_horizon"][existing] = next_horizon

    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": "Convert Yuri's cancellation choice into one exact backend-assurance sequence",
        "why_now": "The read-only review found a strong existing family and two exact convergence blockers before destructive UI exposure.",
        "outcome": "Proceed to an unmounted locked-truth/current-authority kernel architecture; do not yet change product or runtime source.",
        "unlocks": [
            "A typed admission contract for the future dedicated cancellation transaction.",
            "Later disposable PostgreSQL and mounted route convergence gates if the architecture passes.",
            "Reception One cancellation composition only after backend convergence evidence.",
        ],
        "does_not_solve": [
            "No current delete route, raw compatibility route or native fallback changed.",
            "No concurrent PostgreSQL cancellation behavior is proved.",
            "No cancellation UI, patient channel, provider, production or release authority is opened.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 295 / Compass 277. Cancellation is selected and its command path is mapped; an unmounted locked-truth/current-authority kernel architecture is next before Reception One exposure."
    )
    limit = "The cancellation readiness result is repository-static; it proves no locked concurrent database transaction, current-authority revocation behavior, mounted route convergence or UI behavior."
    if limit not in compass["map_limits"]:
        compass["map_limits"].insert(0, limit)
    compass["source_graph_revision"] = 295
    compass["map_revision"] = 277
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)

    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    COMPASS_REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")
    _update_handover_and_plan()
    _complete_latch()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
