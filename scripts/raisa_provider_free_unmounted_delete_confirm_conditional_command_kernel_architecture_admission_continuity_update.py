"""Advance Continuity and Compass for the unmounted delete-confirm kernel."""

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
    "raisa-provider-free-unmounted-delete-confirm-conditional-command-kernel-"
    "architecture-admission"
)
OPERATION_ID = (
    "raisa-reception-one-delete-confirm-conditional-command-kernel-"
    "architecture-admission"
)
PARENT = "raisa-reception-one-cancellation-command-path-readiness-review"
SOURCE_HEAD = "356b28a1750e7a7b379406e864f2a3501606938a"
UPDATED_AT = "2026-08-15T02:56:41Z"
CANCELLATION_DECISION_ID = "reception-one-appointment-cancellation-direction"
KERNEL_HORIZON_ID = "reception-one-delete-confirm-conditional-command-kernel"
NEXT_HORIZON_ID = "reception-one-delete-confirm-physical-representability"

PLAN = (
    "docs/raisa-provider-free-unmounted-delete-confirm-conditional-command-"
    "kernel-architecture-admission-rehearsal-plan.md"
)
ARCHITECTURE = (
    "docs/raisa-provider-free-unmounted-delete-confirm-conditional-command-"
    "kernel-architecture-admission.md"
)
THREAT = (
    "docs/security/raisa-provider-free-unmounted-delete-confirm-conditional-"
    "command-kernel-architecture-admission-threat-model-delta.md"
)
CONTRACT = (
    "orchestration/continuity/raisa-provider-free-unmounted-delete-confirm-"
    "conditional-command-kernel-architecture-admission/contract.json"
)
CONTRACT_SCHEMA = (
    "orchestration/continuity/raisa-provider-free-unmounted-delete-confirm-"
    "conditional-command-kernel-architecture-admission/contract.schema.json"
)
EVIDENCE = (
    "orchestration/continuity/raisa-provider-free-unmounted-delete-confirm-"
    "conditional-command-kernel-architecture-admission/provider-free-acceptance-evidence.json"
)
SIMULATOR = (
    "scripts/raisa_provider_free_unmounted_delete_confirm_conditional_command_"
    "kernel_architecture_admission.py"
)
PROTOCOL_TEST = (
    "tests/test_raisa_provider_free_unmounted_delete_confirm_conditional_"
    "command_kernel_architecture_admission.py"
)
PLAN_TEST = (
    "tests/test_raisa_provider_free_unmounted_delete_confirm_conditional_"
    "command_kernel_architecture_admission_plan.py"
)
RECOVERY = (
    "orchestration/agent_inbox/codex/raisa-delete-confirm-kernel-deepseek-"
    "rejection-and-sol-recovery.md"
)
POSTCOMPACTION = (
    "orchestration/agent_inbox/codex/raisa-reception-one-delete-confirm-"
    "conditional-command-kernel-architecture-admission-postcompaction-"
    "closeout-receipt.json"
)
PREFLIGHT = (
    "orchestration/agent_inbox/codex/raisa-delete-confirm-kernel-gemini-review-"
    "worktree-preflight.json"
)
PACKET = (
    "orchestration/agent_inbox/codex/raisa-delete-confirm-kernel-sol-recovery-"
    "gemini-review-packet.md"
)
PRE_ACCEPTANCE = (
    "orchestration/agent_inbox/codex/raisa-reception-one-delete-confirm-"
    "conditional-command-kernel-architecture-admission-pre-verifier-"
    "acceptance-receipt.json"
)
GEMINI = (
    "orchestration/agent_inbox/antigravity/raisa-delete-confirm-kernel-sol-"
    "recovery-gemini-review-receipt.json"
)
REGISTER = "docs/ariadne-agent-error-correction-register-revision-285.md"
DIRECTION = "docs/raisa-authority-kernel-reference-client-adapter-seam.md"
CLOSEOUT = (
    "docs/raisa-provider-free-unmounted-delete-confirm-conditional-command-"
    "kernel-architecture-admission-rehearsal-closeout.md"
)
ACCEPTANCE = (
    "orchestration/agent_inbox/codex/raisa-delete-confirm-conditional-command-"
    "kernel-architecture-admission-sol-acceptance.md"
)
MAILBOX = (
    "orchestration/human_inbox/yuri/2026-08-15--delete-confirm-conditional-"
    "command-kernel-architecture-admission.md"
)
UPDATER = (
    "scripts/raisa_provider_free_unmounted_delete_confirm_conditional_command_"
    "kernel_architecture_admission_continuity_update.py"
)
CONTINUITY_TEST = (
    "tests/test_raisa_provider_free_unmounted_delete_confirm_conditional_"
    "command_kernel_architecture_admission_continuity.py"
)


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def _evidence() -> list[str]:
    return [
        PLAN,
        ARCHITECTURE,
        THREAT,
        CONTRACT,
        CONTRACT_SCHEMA,
        EVIDENCE,
        SIMULATOR,
        PROTOCOL_TEST,
        PLAN_TEST,
        RECOVERY,
        POSTCOMPACTION,
        PREFLIGHT,
        PACKET,
        PRE_ACCEPTANCE,
        GEMINI,
        REGISTER,
        DIRECTION,
        CLOSEOUT,
        ACCEPTANCE,
        MAILBOX,
    ]


def _node() -> dict[str, Any]:
    return {
        "id": NODE_ID,
        "title": (
            "Provider-free unmounted delete-confirm conditional-command kernel "
            "architecture and admission"
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
                "The accepted result is authored-synthetic, provider-free and unmounted.",
                "One future dedicated delete-confirm command owns current authority, locked truth, confirmation, idempotency, audit, receipt and readback semantics.",
                "Reception One remains a future reference client; no route, database or UI authority is opened.",
            ],
        },
        "decisions": [
            {
                "id": "accept-delete-confirm-kernel-architecture-admission",
                "source": ACCEPTANCE,
                "status": "accepted",
                "summary": (
                    "Accept the closed abstract cancellation transaction contract and "
                    "proceed only to provider-free physical representability review."
                ),
            }
        ],
        "claim_scope": [
            "Exact practice, appointment and idempotency lock order plus two current-authority checks are frozen.",
            "One valid explicit human confirmation and exact 24-field signed evidence are required for a first effect.",
            "Cancellation, audit and completed receipt publish atomically; rollback and response-loss replay are fail closed.",
            "46 decisions, 15 schedules and 67 hostile mutations pass with zero runtime authority.",
            "Gemini passed all 15 independent challenges at unchanged clean exact candidate source.",
            "Reception One is recorded as the first-party reference client around one backend authority kernel; external adapters remain closed.",
            "EMR4's higher-order direction is a provider-agnostic, provider-qualified general-practice medical-management intelligence harness without a present accreditation or safety claim.",
        ],
        "contract_evidence": [
            {
                "contract_id": "combined-patient-practitioner-time-duration-intent",
                "status": "satisfied",
                "evidence": [GEMINI, CLOSEOUT],
                "note": (
                    "The destructive cancellation command contract is now explicit "
                    "without mounting any product surface."
                ),
            }
        ],
        "evidence": {
            "plans": [PLAN, ARCHITECTURE, THREAT],
            "findings": [RECOVERY, DIRECTION],
            "closeouts": [CLOSEOUT, MAILBOX],
            "acceptances": [ACCEPTANCE],
            "receipts": [
                POSTCOMPACTION,
                PREFLIGHT,
                PACKET,
                PRE_ACCEPTANCE,
                GEMINI,
            ],
            "tests": [PROTOCOL_TEST, PLAN_TEST, CONTINUITY_TEST],
            "artifacts": [
                CONTRACT,
                CONTRACT_SCHEMA,
                EVIDENCE,
                SIMULATOR,
                REGISTER,
                UPDATER,
            ],
        },
        "unresolved_gates": [
            "The abstract practice authority fence has no accepted physical PostgreSQL mapping yet.",
            "Real locking, isolation, concurrency and mounted delete-confirm route convergence remain unproved and closed.",
            "Reception One cancellation composition and every external adapter remain closed.",
            "Product data, providers, deployment, production, release, Pages and protected refs remain closed.",
        ],
    }


def _update_handover_and_plan() -> None:
    handover = HANDOVER.read_text(encoding="utf-8")
    relation_old = (
        "The task branch `codex/ariadne-bernie-davida-parallel-seam` must "
        "preserve the accepted Reception One cancellation command-path readiness review"
    )
    relation_new = (
        "The task branch `codex/ariadne-bernie-davida-parallel-seam` must "
        "preserve the accepted provider-free unmounted delete-confirm conditional-command "
        "kernel architecture and admission at exact source "
        "`356b28a1750e7a7b379406e864f2a3501606938a`, the accepted Reception One "
        "cancellation command-path readiness review"
    )
    if relation_new not in handover:
        if relation_old not in handover:
            raise SystemExit("Required Git relation anchor missing")
        handover = handover.replace(relation_old, relation_new, 1)

    row = (
        "| Provider-free unmounted delete-confirm conditional-command kernel architecture and admission acceptance | "
        "`docs/raisa-provider-free-unmounted-delete-confirm-conditional-command-kernel-architecture-admission-rehearsal-plan.md`, "
        "`docs/raisa-provider-free-unmounted-delete-confirm-conditional-command-kernel-architecture-admission.md`, "
        "`docs/security/raisa-provider-free-unmounted-delete-confirm-conditional-command-kernel-architecture-admission-threat-model-delta.md`, "
        "`orchestration/continuity/raisa-provider-free-unmounted-delete-confirm-conditional-command-kernel-architecture-admission/`, "
        "`scripts/raisa_provider_free_unmounted_delete_confirm_conditional_command_kernel_architecture_admission.py`, "
        "`tests/test_raisa_provider_free_unmounted_delete_confirm_conditional_command_kernel_architecture_admission.py`, "
        "`tests/test_raisa_provider_free_unmounted_delete_confirm_conditional_command_kernel_architecture_admission_plan.py`, "
        "`orchestration/agent_inbox/antigravity/raisa-delete-confirm-kernel-sol-recovery-gemini-review-receipt.json`, "
        "`docs/ariadne-agent-error-correction-register-revision-285.md`, "
        "`docs/raisa-authority-kernel-reference-client-adapter-seam.md`, "
        "`docs/raisa-provider-free-unmounted-delete-confirm-conditional-command-kernel-architecture-admission-rehearsal-closeout.md`, "
        "`orchestration/agent_inbox/codex/raisa-delete-confirm-conditional-command-kernel-architecture-admission-sol-acceptance.md`, "
        "`orchestration/human_inbox/yuri/2026-08-15--delete-confirm-conditional-command-kernel-architecture-admission.md`, "
        "`scripts/raisa_provider_free_unmounted_delete_confirm_conditional_command_kernel_architecture_admission_continuity_update.py`, "
        "and `tests/test_raisa_provider_free_unmounted_delete_confirm_conditional_command_kernel_architecture_admission_continuity.py` |"
    )
    if row not in handover:
        anchor = next(
            line for line in handover.splitlines() if line.startswith("| Current result |")
        )
        handover = handover.replace(anchor, row + "\n" + anchor, 1)

    lines = handover.splitlines()
    replacements = {
        "Current result": (
            "| Current result | At Continuity 296 / Compass 278, "
            "`raisa_provider_free_unmounted_delete_confirm_conditional_command_kernel_architecture_admission_pass` "
            "is accepted at exact reviewed source `356b28a1750e7a7b379406e864f2a3501606938a`. "
            "The closed contract freezes exact practice/appointment/idempotency lock order, "
            "two current-authority checks, 24-field signed evidence, nullable reason preservation, "
            "atomic cancellation/audit/receipt completion, rollback, replay and separate readback. "
            "All 46 decisions, 15 schedules, 67 hostile mutations, focused and canonical checks "
            "and Gemini's 15 challenges pass. |"
        ),
        "Next implementation": (
            "| Next implementation | The provider-free unmounted delete-confirm physical "
            "representability review is the next dependency-satisfied tranche. Map the abstract "
            "practice authority fence, appointment and idempotency lock order, exact reasons, "
            "audit, receipt and readback obligations onto existing repository structures without "
            "mounting or executing the route. No OpenAPI/GraphQL, database mutation, product client, "
            "UI, provider, patient/product data, deployment, production, release, Pages or protected-ref "
            "change is authorised. External adapters remain future-closed. Preserve `docs/branding/` "
            "and unrelated untracked files; use explicit-path staging only. |"
        ),
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
    old_track = (
        "Yuri selected appointment cancellation. Its repository-static command-path readiness review now passes: "
        "the dedicated delete family is the convergence base, but a provider-free unmounted locked-truth/current-authority "
        "kernel architecture must precede any mounted route or Reception One UI composition. The native Diary's "
        "delete-to-status fallback is not inherited by Reception One."
    )
    new_track = (
        "Yuri selected appointment cancellation. Its readiness review and provider-free unmounted conditional-command "
        "kernel architecture/admission now pass at exact reviewed source `356b28a1750e7a7b379406e864f2a3501606938a`: "
        "the dedicated delete family must lock practice authority and appointment truth, recheck current authority twice, "
        "bind exact confirmation evidence and atomically publish cancellation, audit and receipt. The next gate is a "
        "provider-free unmounted physical representability review; the native Diary's delete-to-status fallback is not inherited by Reception One. "
        "Raisa's natural seam is now recorded: the backend is the typed authority kernel and Reception One is its first-party "
        "reference client, allowing later separately gated adapters without duplicating command authority or delaying the first native production horizon. "
        "The same principle applies to Clinician One at its stricter clinical authority, attestation and final-commit boundary. "
        "My Health Record is classified separately as a future regulated integration adapter whose existing Phase 10 gate remains closed. "
        "EMR4's higher-order direction is a provider-agnostic, provider-qualified general-practice medical-management intelligence harness; no present accreditation or safety claim is made."
    )
    if old_track in lines[track_index]:
        lines[track_index] = lines[track_index].replace(old_track, new_track, 1)
    elif (
        "The same principle applies to Clinician One at its stricter clinical authority, attestation and final-commit boundary."
        in lines[track_index]
        and "My Health Record is classified separately" not in lines[track_index]
    ):
        lines[track_index] = lines[track_index].replace(
            "The same principle applies to Clinician One at its stricter clinical authority, attestation and final-commit boundary.",
            "The same principle applies to Clinician One at its stricter clinical authority, attestation and final-commit boundary. My Health Record is classified separately as a future regulated integration adapter whose existing Phase 10 gate remains closed.",
            1,
        )
    if (
        "My Health Record is classified separately as a future regulated integration adapter whose existing Phase 10 gate remains closed."
        in lines[track_index]
        and "provider-qualified general-practice medical-management intelligence harness"
        not in lines[track_index]
    ):
        lines[track_index] = lines[track_index].replace(
            "My Health Record is classified separately as a future regulated integration adapter whose existing Phase 10 gate remains closed.",
            "My Health Record is classified separately as a future regulated integration adapter whose existing Phase 10 gate remains closed. EMR4's higher-order direction is a provider-agnostic, provider-qualified general-practice medical-management intelligence harness; no present accreditation or safety claim is made.",
            1,
        )
    elif new_track not in lines[track_index]:
        raise SystemExit("Active product track delete-confirm anchor missing")
    HANDOVER.write_text("\n".join(lines) + "\n", encoding="utf-8")

    plan = MASTER_PLAN.read_text(encoding="utf-8")
    old_plan = """The provider-free same-update-family multi-change kernel and visible editor pass
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
    new_plan = """The provider-free same-update-family multi-change kernel and visible editor pass
at exact reviewed editor source
`daed421954d65c159871585559f45caa32d95aee`. The subsequent programme
orientation passes at `2ca3a111d2ee9277571ea3c905f22ce78c8e9745`, Yuri selected
appointment cancellation, and its repository-static command-path readiness
review passes at `bb36e19c774eb1bc4ace8cafc6ae2b5c35bc8735`. The provider-free
unmounted delete-confirm conditional-command kernel architecture and admission
then passes at exact reviewed source
`356b28a1750e7a7b379406e864f2a3501606938a`, freezing exact lock order, two
current-authority checks, signed evidence, reason preservation, atomic
cancellation/audit/receipt completion, rollback, replay and separate readback.
The next narrow descendant is a provider-free unmounted physical
representability review before any mounted route, PostgreSQL behavior or
Reception One cancellation composition. Patient-channel delegation, check-in,
Stage 3B, another event family and operational durability remain retained at
their exact gates. No watcher runtime, product data, external patient client,
provider, deployment, production or release is opened.

The durable product seam is one Raisa authority kernel with replaceable
interaction adapters. Reception One is the first-party reference client; later
email, messaging, thin-web, voice or third-party assistants may render the same
versioned typed protocol only after separate identity, delegation, privacy and
conformance gates. This lets the first production horizon concentrate on the
core kernel and native Reception One client rather than waiting for every
possible channel, without granting any client independent command authority.
Clinician One follows the same principle with its Word/Office workspace as the
first-party clinical reference client; backend truth, permissions, document
versioning, clinician attestation, audit and final commit remain non-portable
authority boundaries.
My Health Record is a future regulated integration adapter: outbound material
must derive from explicitly authorised Raisa truth, inbound material remains
source-labelled external evidence, and all external effects stay behind
idempotent audited commands and the existing Phase 10 gate.
At the highest level, this creates a provider-agnostic but provider-qualified
general-practice medical-management intelligence meta-harness. Model providers
may supply bounded interpretation, synthesis and dialogue behind stable Bureau
contracts, while deterministic services retain evidence admission, truth,
authority, proofreading, human/clinician gates, commands, audit, receipts,
revocation and explicit degraded operation. “Provider-accredited” remains
reserved until a formal accreditation owner, criteria, lifecycle and regulatory
meaning are defined; this direction is not a present safety or certification
claim.
See `docs/raisa-authority-kernel-reference-client-adapter-seam.md`."""
    if old_plan in plan:
        plan = plan.replace(old_plan, new_plan, 1)
    elif new_plan not in plan:
        raise SystemExit("Master-plan delete-confirm anchor missing")
    MASTER_PLAN.write_text(plan, encoding="utf-8")


def _complete_latch() -> None:
    latch = json.loads(LATCH.read_text(encoding="utf-8"))
    if latch.get("operation_id") != OPERATION_ID:
        raise SystemExit("Unexpected active-operation latch")
    latch["status"] = "complete"
    latch["source_head"] = SOURCE_HEAD
    latch["checkpoint"] = {
        "completed_stage": (
            "Accepted at Continuity 296 / Compass 278 after deterministic Sol "
            "recovery and one fresh exact-candidate Gemini veto"
        ),
        "next_executable_stage": None,
        "retry_counters": {
            "planning": 0,
            "implementation": 1,
            "review": 0,
            "verification": 1,
        },
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
    if graph["graph_revision"] == 295 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 296
        graph["updated_at"] = UPDATED_AT
    elif graph["graph_revision"] == 296 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
    else:
        raise SystemExit("Unexpected delete-confirm kernel Continuity predecessor")
    _write(GRAPH, graph)

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": (
            "Freeze the destructive cancellation transaction before physical mapping"
        ),
        "outcome": (
            "The authored-synthetic kernel now owns current authority, locked truth, "
            "confirmation, idempotency, atomic audit/receipt and readback semantics."
        ),
        "evidence": _evidence(),
    }
    if (
        compass["map_revision"] == 277
        and compass["source_graph_revision"] == 295
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 278
        and compass["source_graph_revision"] == 296
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected delete-confirm kernel Compass predecessor")

    cancellation = next(
        item
        for item in compass["decision_horizon"]
        if item["id"] == CANCELLATION_DECISION_ID
    )
    cancellation.update(
        {
            "status": "active",
            "strategic_question": (
                "Cancellation is selected and its abstract conditional-command kernel passes; how should it cross the remaining physical and product gates?"
            ),
            "why_it_matters": (
                "The destructive action must retain one backend authority path from physical representation through Reception One composition."
            ),
            "prerequisites": [
                "Complete the provider-free unmounted physical representability review.",
                "Keep disposable PostgreSQL behavior, mounted route convergence and Reception One composition as later distinct gates.",
            ],
            "boundary_changes": [],
            "evidence": [ARCHITECTURE, GEMINI, CLOSEOUT, ACCEPTANCE, MAILBOX],
        }
    )

    compass["decision_horizon"] = [
        item
        for item in compass["decision_horizon"]
        if item["id"] != KERNEL_HORIZON_ID
    ]
    next_horizon = {
        "id": NEXT_HORIZON_ID,
        "title": "Reception One delete-confirm physical representability",
        "status": "active",
        "strategic_question": (
            "Can the abstract cancellation authority fence, lock order and atomic artifacts be represented exactly by existing repository structures?"
        ),
        "why_it_matters": (
            "Physical mapping must be honest before any database rehearsal, route convergence or destructive UI exposure."
        ),
        "prerequisites": [
            "Provider-free read-only repository inspection only.",
            "No mounted route, database mutation, product client or UI source change.",
            "Retain exact authority, evidence, reason, idempotency, audit, receipt and readback contracts.",
        ],
        "boundary_changes": [],
        "evidence": [PLAN, ARCHITECTURE, THREAT, CLOSEOUT, ACCEPTANCE],
    }
    existing = next(
        (
            i
            for i, item in enumerate(compass["decision_horizon"])
            if item["id"] == NEXT_HORIZON_ID
        ),
        None,
    )
    if existing is None:
        compass["decision_horizon"].insert(0, next_horizon)
    else:
        compass["decision_horizon"][existing] = next_horizon

    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": (
            "Hold cancellation at the authority-kernel seam before physical mapping"
        ),
        "why_now": (
            "The abstract transaction and independent veto pass; PostgreSQL representability is the next dependency."
        ),
        "outcome": (
            "Proceed to a read-only physical representability review without mounting or executing cancellation."
        ),
        "unlocks": [
            "An exact mapping or explicit gap list for practice authority fencing and lock order.",
            "A later inert physical design and disposable PostgreSQL rehearsal if representability passes.",
            "A stable authority seam for the native Reception One reference client and future separately gated adapters.",
        ],
        "does_not_solve": [
            "No PostgreSQL lock, isolation or concurrent behavior is proved.",
            "No route, OpenAPI, product client or cancellation UI is changed.",
            "No external adapter, patient identity/delegation, provider, production or release authority is opened.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 296 / Compass 278. The unmounted delete-confirm authority kernel passes; physical representability is next before database, route or Reception One cancellation composition."
    )
    limit = (
        "The delete-confirm kernel result is authored-synthetic and unmounted; it proves no PostgreSQL authority fence, real locking/concurrency, route behavior or client behavior."
    )
    if limit not in compass["map_limits"]:
        compass["map_limits"].insert(0, limit)
    compass["source_graph_revision"] = 296
    compass["map_revision"] = 278
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
