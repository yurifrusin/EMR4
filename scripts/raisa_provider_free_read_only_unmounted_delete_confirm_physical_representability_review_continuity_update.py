"""Advance Continuity and Compass for delete-confirm physical representability."""

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

NODE_ID = (
    "raisa-provider-free-read-only-unmounted-delete-confirm-physical-"
    "representability-review"
)
PARENT = (
    "raisa-provider-free-unmounted-delete-confirm-conditional-command-kernel-"
    "architecture-admission"
)
OPERATION_ID = "raisa-reception-one-delete-confirm-physical-representability-review"
SOURCE_HEAD = "bc066a1b639c5c57cc72f2697c063c5842511840"
UPDATED_AT = "2026-08-15T04:44:52Z"
CURRENT_HORIZON = "reception-one-delete-confirm-physical-representability"
NEXT_HORIZON = "reception-one-delete-confirm-physical-design-architecture"

PLAN = (
    "docs/raisa-provider-free-read-only-unmounted-delete-confirm-physical-"
    "representability-review-plan.md"
)
THREAT = (
    "docs/security/raisa-provider-free-read-only-unmounted-delete-confirm-"
    "physical-representability-review-threat-model-delta.md"
)
REVIEW = (
    "docs/raisa-provider-free-read-only-unmounted-delete-confirm-physical-"
    "representability-review.md"
)
CONTINUITY_DIR = (
    "orchestration/continuity/raisa-provider-free-read-only-unmounted-delete-"
    "confirm-physical-representability-review"
)
CONTRACT = f"{CONTINUITY_DIR}/review-contract.json"
EVIDENCE_SCHEMA = f"{CONTINUITY_DIR}/provider-free-review-evidence.schema.json"
EVIDENCE = f"{CONTINUITY_DIR}/provider-free-review-evidence.json"
VALIDATOR = (
    "scripts/raisa_provider_free_read_only_unmounted_delete_confirm_physical_"
    "representability_review.py"
)
REVIEW_TEST = (
    "tests/test_raisa_provider_free_read_only_unmounted_delete_confirm_"
    "physical_representability_review.py"
)
PLAN_TEST = (
    "tests/test_raisa_provider_free_read_only_unmounted_delete_confirm_"
    "physical_representability_review_plan.py"
)
PREFLIGHT = (
    "orchestration/agent_inbox/codex/raisa-delete-confirm-physical-"
    "representability-gemini-worktree-preflight.json"
)
MANIFEST_ADMISSION = (
    "orchestration/agent_inbox/codex/raisa-delete-confirm-physical-"
    "representability-gemini-command-manifest-admission.json"
)
GEMINI = (
    "orchestration/agent_inbox/antigravity/raisa-delete-confirm-physical-"
    "representability-gemini-review-receipt.json"
)
REGISTER_286 = "docs/ariadne-agent-error-correction-register-revision-286.md"
REGISTER_287 = "docs/ariadne-agent-error-correction-register-revision-287.md"
REGISTER_288 = "docs/ariadne-agent-error-correction-register-revision-288.md"
REGISTER_289 = "docs/ariadne-agent-error-correction-register-revision-289.md"
CLOSEOUT = (
    "docs/raisa-provider-free-read-only-unmounted-delete-confirm-physical-"
    "representability-review-closeout.md"
)
ACCEPTANCE = (
    "orchestration/agent_inbox/codex/raisa-delete-confirm-physical-"
    "representability-review-sol-acceptance.md"
)
MAILBOX = (
    "orchestration/human_inbox/yuri/2026-08-15--delete-confirm-physical-"
    "representability-review.md"
)
UPDATER = (
    "scripts/raisa_provider_free_read_only_unmounted_delete_confirm_physical_"
    "representability_review_continuity_update.py"
)
CONTINUITY_TEST = (
    "tests/test_raisa_provider_free_read_only_unmounted_delete_confirm_"
    "physical_representability_review_continuity.py"
)


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def _evidence() -> list[str]:
    return [
        PLAN,
        THREAT,
        REVIEW,
        CONTRACT,
        EVIDENCE_SCHEMA,
        EVIDENCE,
        VALIDATOR,
        REVIEW_TEST,
        PLAN_TEST,
        PREFLIGHT,
        MANIFEST_ADMISSION,
        GEMINI,
        REGISTER_286,
        REGISTER_287,
        REGISTER_288,
        REGISTER_289,
        CLOSEOUT,
        ACCEPTANCE,
        MAILBOX,
    ]


def _node() -> dict[str, Any]:
    evidence = _evidence()
    return {
        "id": NODE_ID,
        "title": (
            "Provider-free read-only unmounted delete-confirm physical "
            "representability review"
        ),
        "kind": "foundation",
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
                "The accepted result is provider-free, read-only and unmounted.",
                "Appointment truth is represented; five surrounding domains require bounded additive design.",
                "The current mounted route and compatibility paths are not the accepted kernel.",
            ],
        },
        "decisions": [
            {
                "id": "accept-delete-confirm-physical-representability-review",
                "source": ACCEPTANCE,
                "status": "accepted",
                "summary": (
                    "Accept exact physical representability without implementation "
                    "admission and proceed only to unmounted physical design."
                ),
            }
        ],
        "claim_scope": [
            "Thirteen exact hashes and twenty-six line-bound observations support six closed verdicts.",
            "Appointment practice ownership, status, waiting area, exact reasons and positive monotonic version are already represented.",
            "Practice authority, private receipt, audit correlation, atomic ordering and fresh readback are representable with additive change.",
            "The current mounted route remains unadmitted.",
            "All fifty-two hostile mutations fail closed and implementation remains not admitted.",
            "Gemini passed five exact commands at unchanged clean reviewed source.",
        ],
        "contract_evidence": [
            {
                "contract_id": "combined-patient-practitioner-time-duration-intent",
                "status": "satisfied",
                "evidence": [GEMINI, CLOSEOUT],
                "note": (
                    "The cancellation kernel has an exact physical mapping or bounded "
                    "additive gap in every domain without mounting a command."
                ),
            }
        ],
        "evidence": {
            "plans": [PLAN, THREAT],
            "findings": [REVIEW, REGISTER_286, REGISTER_287, REGISTER_288, REGISTER_289],
            "closeouts": [CLOSEOUT, MAILBOX],
            "acceptances": [ACCEPTANCE],
            "receipts": [PREFLIGHT, MANIFEST_ADMISSION, GEMINI],
            "tests": [REVIEW_TEST, PLAN_TEST, CONTINUITY_TEST],
            "artifacts": [CONTRACT, EVIDENCE_SCHEMA, EVIDENCE, VALIDATOR, UPDATER],
        },
        "unresolved_gates": [
            "No additive column, constraint, migration, service or route design is selected yet.",
            "Real PostgreSQL parse, catalogue, locking, concurrency, rollback and restart behavior remain unproved.",
            "Mounted delete-confirm route convergence and Reception One cancellation composition remain closed.",
            "Product data, external adapters, providers, deployment, production, release, Pages and protected refs remain closed.",
        ],
    }


def _update_graph() -> dict[str, Any]:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] != 296:
        raise SystemExit("Expected graph revision 296")
    if any(item["id"] == NODE_ID for item in graph["nodes"]):
        raise SystemExit("Representability node already exists")
    if not any(item["id"] == PARENT for item in graph["nodes"]):
        raise SystemExit("Representability parent missing")
    graph["nodes"].append(_node())
    graph["graph_revision"] = 297
    graph["updated_at"] = UPDATED_AT
    _write(GRAPH, graph)
    return graph


def _update_compass(graph: dict[str, Any]) -> None:
    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    if compass["map_revision"] != 278 or compass["source_graph_revision"] != 296:
        raise SystemExit("Expected Compass 278 bound to Continuity 296")
    if not any(item["id"] == CURRENT_HORIZON for item in compass["decision_horizon"]):
        raise SystemExit("Current representability horizon missing")

    compass["journey"].append(
        {
            "node_id": NODE_ID,
            "lineage_parent": PARENT,
            "strategic_role": (
                "Prove the abstract cancellation kernel fits exact physical/API "
                "structures before selecting implementation"
            ),
            "outcome": (
                "Appointment truth is already represented and five surrounding "
                "domains have bounded additive paths; the current route remains unadmitted."
            ),
            "evidence": _evidence(),
        }
    )
    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": "Hold cancellation at the declarative physical-design gate",
        "why_now": (
            "Representability passes without weakening the kernel; exact additive "
            "structures and ordering must now be selected before any DDL or route work."
        ),
        "outcome": (
            "Proceed to provider-free unmounted physical-design architecture only."
        ),
        "unlocks": [
            "An exact declarative practice-authority fence and delete-confirm private receipt design.",
            "A later inert DDL lowering and disposable PostgreSQL rehearsal if design passes.",
            "A stable command seam for Reception One and future separately gated adapters.",
        ],
        "does_not_solve": [
            "No schema, migration, service, route or client is changed.",
            "No PostgreSQL locking, concurrency, rollback or restart behavior is proved.",
            "No external adapter, product data, provider, production or release authority is opened.",
        ],
        "evidence": _evidence(),
    }
    compass["decision_horizon"] = [
        item for item in compass["decision_horizon"] if item["id"] != CURRENT_HORIZON
    ]
    compass["decision_horizon"].insert(
        0,
        {
            "id": NEXT_HORIZON,
            "title": "Reception One delete-confirm physical-design architecture",
            "status": "active",
            "strategic_question": (
                "What is the smallest declarative additive design that realizes "
                "all five representability gaps without mounting the command?"
            ),
            "why_it_matters": (
                "The exact authority fence, receipt, audit and transaction order must "
                "be frozen before inert DDL or disposable PostgreSQL behavior work."
            ),
            "prerequisites": [
                "Use the exact six representability verdicts and twenty-six observations.",
                "Remain provider-free, authored-synthetic, declarative and unmounted.",
                "Preserve current-authority non-disclosure, exact lock order, reasons, version advance, atomic artifacts and separate readback.",
            ],
            "boundary_changes": [],
            "evidence": [REVIEW, EVIDENCE, GEMINI, CLOSEOUT, ACCEPTANCE],
        },
    )
    for item in compass["decision_horizon"]:
        if item["id"] == "reception-one-appointment-cancellation-direction":
            item["strategic_question"] = (
                "Cancellation is selected and physically representable; how should "
                "its exact design cross the remaining database and product gates?"
            )
            item["prerequisites"] = [
                "Complete the provider-free unmounted physical-design architecture.",
                "Keep inert DDL, disposable PostgreSQL behavior, mounted route convergence and Reception One composition as later distinct gates.",
            ]
            for path in (REVIEW, GEMINI, CLOSEOUT, ACCEPTANCE, MAILBOX):
                if path not in item["evidence"]:
                    item["evidence"].append(path)

    compass["orientation_statement"] = (
        "EMR4 is at Continuity 297 / Compass 279. Delete-confirm physical "
        "representability passes; unmounted physical design is next before DDL, "
        "database behavior, route or Reception One composition."
    )
    limit = (
        "The delete-confirm representability result selects no physical design and "
        "proves no DDL, PostgreSQL behavior, mounted route or client behavior."
    )
    if limit not in compass["map_limits"]:
        compass["map_limits"].insert(0, limit)
    compass["source_graph_revision"] = 297
    compass["map_revision"] = 279
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)

    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    COMPASS_REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")


def _update_handover() -> None:
    text = HANDOVER.read_text(encoding="utf-8")
    relation_old = (
        "The task branch `codex/ariadne-bernie-davida-parallel-seam` must "
        "preserve the accepted provider-free unmounted delete-confirm"
    )
    relation_new = (
        "The task branch `codex/ariadne-bernie-davida-parallel-seam` must "
        "preserve the accepted provider-free read-only unmounted delete-confirm "
        "physical representability review at exact source `"
        + SOURCE_HEAD
        + "`, the accepted provider-free unmounted delete-confirm"
    )
    if relation_old not in text:
        raise SystemExit("Required Git relation anchor missing")
    text = text.replace(relation_old, relation_new, 1)

    rows = text.splitlines()
    compact_track = (
        "| Active product track | Reception One's typed backend authority-kernel seam "
        "now covers proposal/confirmation, status and multi-field rescheduling, while "
        "appointment cancellation has passed readiness, abstract kernel and exact physical "
        "representability at `bc066a1b639c5c57cc72f2697c063c5842511840`. Appointment truth "
        "is already represented; five surrounding cancellation domains need bounded additive "
        "design, and the current mounted/compatibility routes remain unadmitted. Reception One "
        "is the first-party reference client; Clinician One follows the same stricter clinical "
        "seam, and My Health Record remains a future regulated integration adapter. EMR4's "
        "higher-order direction is a provider-agnostic, provider-qualified general-practice "
        "medical-management intelligence harness; no present accreditation, safety, external "
        "adapter, provider, production or release claim is made. |"
    )
    acceptance_row = (
        "| Provider-free read-only unmounted delete-confirm physical representability review acceptance | "
        f"`{PLAN}`, `{REVIEW}`, `{THREAT}`, `{CONTINUITY_DIR}/`, `{VALIDATOR}`, "
        f"`{REVIEW_TEST}`, `{PLAN_TEST}`, `{GEMINI}`, `{REGISTER_289}`, `{CLOSEOUT}`, "
        f"`{ACCEPTANCE}`, `{MAILBOX}`, `{UPDATER}`, and `{CONTINUITY_TEST}` |"
    )
    result_row = (
        "| Current result | At Continuity 297 / Compass 279, "
        "`raisa_provider_free_read_only_unmounted_delete_confirm_physical_representability_review_pass` "
        f"is accepted at exact reviewed source `{SOURCE_HEAD}`. Thirteen hashes, twenty-six "
        "observations, six verdicts and fifty-two hostile rejections pass. Appointment truth "
        "is already represented; practice authority, private receipt, audit correlation, atomic "
        "ordering and separate readback are additive. Implementation remains not admitted; "
        "Gemini passed five exact commands at unchanged clean source. |"
    )
    next_row = (
        "| Next implementation | The provider-free unmounted delete-confirm physical-design "
        "architecture is next. Freeze the smallest declarative additive authority fence, private "
        "receipt, audit correlation, exact transaction order, reason/version semantics and "
        "separate readback. No application/DDL execution, database, route, UI, product data, "
        "provider, deployment, release, Pages or protected-ref change is authorised. Preserve "
        "`docs/branding/` and all unrelated untracked files; stage explicit paths only. |"
    )
    updated: list[str] = []
    inserted = False
    for row in rows:
        if row.startswith("| Active product track |"):
            updated.append(compact_track)
        elif row.startswith("| Current result |"):
            if not inserted:
                updated.append(acceptance_row)
                inserted = True
            updated.append(result_row)
        elif row.startswith("| Next implementation |"):
            updated.append(next_row)
        else:
            updated.append(row)
    if not inserted:
        raise SystemExit("Current result row missing")
    HANDOVER.write_text("\n".join(updated) + "\n", encoding="utf-8")


def _update_plan() -> None:
    text = MASTER_PLAN.read_text(encoding="utf-8")
    old = """The next narrow descendant is a provider-free unmounted physical
representability review before any mounted route, PostgreSQL behavior or
Reception One cancellation composition. Patient-channel delegation, check-in,
Stage 3B, another event family and operational durability remain retained at
their exact gates. No watcher runtime, product data, external patient client,
provider, deployment, production or release is opened."""
    new = """The provider-free read-only unmounted physical representability review now
passes at exact reviewed source
`bc066a1b639c5c57cc72f2697c063c5842511840`. Appointment truth is already
represented; the practice-authority fence, delete-confirm private receipt,
audit correlation, ordered atomic boundary and separately authorised readback
are each representable through bounded additive change. The current mounted
and compatibility routes remain unadmitted. The next narrow descendant is a
provider-free unmounted physical-design architecture before inert DDL,
PostgreSQL behavior, route convergence or Reception One cancellation
composition. Patient-channel delegation, check-in, Stage 3B, another event
family and operational durability remain retained at their exact gates. No
watcher runtime, product data, external patient client, provider, deployment,
production or release is opened."""
    if old not in text:
        raise SystemExit("Implementation-plan representability anchor missing")
    MASTER_PLAN.write_text(text.replace(old, new, 1), encoding="utf-8")


def _complete_latch() -> None:
    latch = json.loads(LATCH.read_text(encoding="utf-8"))
    if latch["operation_id"] != OPERATION_ID or latch["status"] != "in_progress":
        raise SystemExit("Active-operation latch mismatch")
    latch["status"] = "complete"
    latch["source_head"] = SOURCE_HEAD
    latch["checkpoint"] = {
        "completed_stage": (
            "Accepted physical representability review: thirteen hashes, twenty-six "
            "observations, six verdicts, fifty-two hostile rejections and independent "
            "Gemini pass at unchanged clean source"
        ),
        "next_executable_stage": None,
        "retry_counters": {"planning": 1, "implementation": 1, "review": 2, "verification": 1},
        "settings_fingerprint": (
            "sha256:0ec4410bad05929fd2e7d3649a70aeeab65bd86c9fa8c9ecc70a6b61f5306acc"
        ),
    }
    latch["resume_after_compaction"] = False
    latch["user_attention"] = {"required": False, "reason": None}
    latch["terminal_response"] = {
        "permitted": True,
        "reason": "operation_complete",
    }
    _write(LATCH, latch)


def main() -> int:
    graph = _update_graph()
    _update_compass(graph)
    _update_handover()
    _update_plan()
    _complete_latch()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
