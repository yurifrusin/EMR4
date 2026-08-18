"""Advance Continuity and Compass for default-off check-in route convergence."""

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
NODE_ID = (
    "raisa-provider-free-default-off-canonical-check-in-route-adapter-"
    "convergence-rehearsal"
)
PARENT = (
    "raisa-provider-free-unmounted-canonical-check-in-product-adapter-"
    "extraction-rehearsal"
)
SOURCE_HEAD = "c82c3a741053a9c8da260aa62e1a968af22bb54e"
UPDATED_AT = "2026-08-18T03:39:45Z"
PLAN = (
    "docs/raisa-provider-free-default-off-canonical-check-in-route-adapter-"
    "convergence-rehearsal-plan.md"
)
THREAT = (
    "docs/security/raisa-provider-free-default-off-canonical-check-in-route-"
    "adapter-convergence-rehearsal-threat-model-delta.md"
)
ROUTER = "app/routers/appointments.py"
ADAPTER = "app/services/appointment_check_in_product_adapter.py"
TEST = (
    "tests/test_raisa_provider_free_default_off_canonical_check_in_route_"
    "adapter_convergence.py"
)
ADAPTER_TEST = (
    "tests/test_raisa_provider_free_unmounted_canonical_check_in_product_"
    "adapter.py"
)
CLOSEOUT = (
    "docs/raisa-provider-free-default-off-canonical-check-in-route-adapter-"
    "convergence-rehearsal-closeout.md"
)
ACCEPTANCE = (
    "orchestration/agent_inbox/codex/raisa-default-off-check-in-route-adapter-"
    "sol-acceptance.md"
)
MAILBOX = (
    "orchestration/human_inbox/yuri/2026-08-18--default-off-canonical-check-"
    "in-route-adapter-convergence-rehearsal.md"
)
PACKET = (
    "orchestration/agent_inbox/codex/raisa-default-off-check-in-route-adapter-"
    "gemini37-review-packet.md"
)
MANIFEST = (
    "orchestration/agent_inbox/codex/raisa-default-off-check-in-route-adapter-"
    "gemini37-command-manifest.json"
)
PREFLIGHT = (
    "orchestration/agent_inbox/codex/raisa-default-off-check-in-route-adapter-"
    "gemini37-review-worktree-preflight.json"
)
ORCHESTRATOR_RECEIPT = (
    "orchestration/agent_inbox/codex/raisa-default-off-check-in-route-adapter-"
    "pre-verifier-acceptance-receipt.json"
)
REVIEW = (
    "orchestration/agent_inbox/antigravity/raisa-default-off-check-in-route-"
    "adapter-gemini37-review-receipt.json"
)
DETERMINISTIC = (
    "orchestration/agent_inbox/codex/raisa-default-off-check-in-route-adapter-"
    "deterministic-admission.json"
)
RECOVERY = (
    "orchestration/agent_inbox/codex/raisa-default-off-check-in-route-adapter-"
    "sol-recovery-result.md"
)
REGISTER_REVISION = "docs/ariadne-agent-error-correction-register-revision-382.md"
UPDATER = (
    "scripts/raisa_provider_free_default_off_canonical_check_in_route_adapter_"
    "convergence_rehearsal_continuity_update.py"
)
CONTINUITY_TEST = (
    "tests/test_raisa_provider_free_default_off_canonical_check_in_route_"
    "adapter_convergence_rehearsal_continuity.py"
)


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def _evidence() -> list[str]:
    return [
        PLAN,
        THREAT,
        ROUTER,
        ADAPTER,
        TEST,
        ADAPTER_TEST,
        DETERMINISTIC,
        RECOVERY,
        PACKET,
        MANIFEST,
        PREFLIGHT,
        ORCHESTRATOR_RECEIPT,
        REVIEW,
        REGISTER_REVISION,
        CLOSEOUT,
        ACCEPTANCE,
        MAILBOX,
    ]


def _node() -> dict[str, Any]:
    inherited_contracts = [
        {
            "contract_id": "combined-patient-practitioner-time-duration-intent",
            "status": "satisfied",
            "evidence": [
                "docs/raisa-ordinary-diary-cancellation-canonical-consumer-convergence-composition-plan.md",
                "orchestration/continuity/raisa-ordinary-diary-cancellation-canonical-consumer-convergence-composition/ordinary-diary-cancellation-canonical-consumer-convergence-composition-evidence.json",
                "tests/test_raisa_ordinary_diary_cancellation_canonical_consumer_convergence_composition.py",
                "docs/raisa-ordinary-diary-cancellation-canonical-consumer-convergence-composition-closeout.md",
            ],
            "note": "The accepted first-party intent contract remains inherited; this default-off backend route convergence changes no client intent.",
        },
        {
            "contract_id": "committed-reschedule-availability-reconciliation",
            "status": "satisfied",
            "evidence": [
                "orchestration/continuity/raisa-ordinary-diary-cancellation-canonical-consumer-convergence-composition/ordinary-diary-cancellation-canonical-consumer-convergence-composition-evidence.json",
                "review/test_ordinary_diary_cancellation_convergence.py",
                "docs/raisa-ordinary-diary-cancellation-canonical-consumer-convergence-composition-closeout.md",
            ],
            "note": "The accepted fresh-read reconciliation contract remains inherited; no client projection changed.",
        },
    ]
    return {
        "id": NODE_ID,
        "title": "Provider-free default-off canonical check-in route-adapter convergence rehearsal",
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
                "Existing A5.1 remains default-off and exact authored-synthetic practice allowlisted.",
                "The route delegates once to the accepted check-in adapter with no fallback write path.",
                "Generic-status Arrived, action grammar, clients and waiting-area movement remain closed.",
            ],
        },
        "decisions": [
            {
                "id": "accept-default-off-canonical-check-in-route-adapter-convergence",
                "source": ACCEPTANCE,
                "status": "accepted",
                "summary": "Accept one default-off A5.1 delegation to the canonical check-in adapter without ordinary product admission.",
            }
        ],
        "claim_scope": [
            "Gate-before-lookup denial and the exact A5.1 authored-synthetic allowlist remain unchanged.",
            "One route binder composes locked current authority, check-in effect, audit, event, completion, commit/rollback and readback.",
            "Same-key classification retains route compatibility while newly claimed invalid envelopes roll back.",
            "103 focused, 35 database-backed and 85 API-Spine/plan checks plus the final Gemini 3.7 veto pass.",
        ],
        "contract_evidence": inherited_contracts,
        "evidence": {
            "plans": [
                PLAN,
                "docs/raisa-ordinary-diary-cancellation-canonical-consumer-convergence-composition-plan.md",
            ],
            "findings": [
                THREAT,
                DETERMINISTIC,
                REGISTER_REVISION,
                "orchestration/continuity/raisa-ordinary-diary-cancellation-canonical-consumer-convergence-composition/ordinary-diary-cancellation-canonical-consumer-convergence-composition-evidence.json",
            ],
            "closeouts": [
                CLOSEOUT,
                MAILBOX,
                "docs/raisa-ordinary-diary-cancellation-canonical-consumer-convergence-composition-closeout.md",
            ],
            "acceptances": [ACCEPTANCE],
            "receipts": [ORCHESTRATOR_RECEIPT, PREFLIGHT, REVIEW],
            "tests": [
                TEST,
                ADAPTER_TEST,
                CONTINUITY_TEST,
                "tests/test_raisa_ordinary_diary_cancellation_canonical_consumer_convergence_composition.py",
                "review/test_ordinary_diary_cancellation_convergence.py",
            ],
            "artifacts": [ROUTER, ADAPTER, PACKET, MANIFEST, RECOVERY, UPDATER],
        },
        "unresolved_gates": [
            "Ordinary-practice admission remains closed.",
            "Generic-status Arrived, action grammar and atomic two-client cutover remain closed.",
            "Real product data, providers, deployment, production and protected integration remain closed.",
        ],
    }


def main() -> int:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 316 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 317
    elif graph["graph_revision"] == 317 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
    else:
        raise SystemExit("Unexpected default-off check-in route Continuity predecessor")
    graph["updated_at"] = UPDATED_AT
    _write(GRAPH, graph)

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Converge default-off A5.1 onto the accepted check-in adapter",
        "outcome": "The closed route has one canonical check-in write path without ordinary-practice admission.",
        "evidence": _evidence(),
    }
    if (
        compass["map_revision"] == 298
        and compass["source_graph_revision"] == 316
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 299
        and compass["source_graph_revision"] == 317
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected default-off check-in route Compass predecessor")
    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": "Default-off A5.1 now delegates to one canonical check-in authority seam",
        "why_now": "The accepted unmounted adapter could replace duplicated route-local composition without opening product admission.",
        "outcome": "Run Yuri's tiny isolated native DeepSeek Harness traceability rehearsal, then resume product planning without changing A5.1 admission.",
        "unlocks": [
            "Measure whether the native DeepSeek harness improves terminal and trace evidence over Claude Code transport.",
            "Plan later check-in product admission and atomic client convergence as separate fail-closed gates.",
        ],
        "does_not_solve": [
            "No ordinary practice, generic-status Arrived, action grammar or client is enabled.",
            "Product/patient data, providers, deployment, production and protected integration remain closed.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 317 / Compass 299. Default-off A5.1 delegates to "
        "the canonical check-in adapter; the immediate authorised successor is a "
        "tiny isolated native DeepSeek Harness traceability rehearsal."
    )
    limit = (
        "Default-off check-in route convergence opens no ordinary practice, client, "
        "product data, provider, deployment, production or protected integration authority."
    )
    if limit not in compass["map_limits"]:
        compass["map_limits"].insert(0, limit)
    compass["source_graph_revision"] = 317
    compass["map_revision"] = 299
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)
    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
