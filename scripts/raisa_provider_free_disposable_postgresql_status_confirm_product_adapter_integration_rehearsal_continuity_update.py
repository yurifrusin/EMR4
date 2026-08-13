"""Apply the accepted product-adapter/PostgreSQL integration continuity update."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
GRAPH_PATH = ROOT / "orchestration/continuity/emr4-continuity-graph.json"
COMPASS_PATH = ROOT / "orchestration/continuity/emr4-compass.json"
COMPASS_DOC_PATH = ROOT / "docs/ariadne-compass-current.md"
AGENTS_PATH = ROOT / "AGENTS.md"
NODE_ID = (
    "raisa-provider-free-disposable-postgresql-status-confirm-"
    "product-adapter-integration-rehearsal"
)
SOURCE_HEAD = "553d38c37af86ceefc7b4315b8eaa171d405ab95"
UPDATED_AT = "2026-08-13T01:39:55Z"
RESULT = (
    "raisa_provider_free_disposable_postgresql_status_confirm_"
    "product_adapter_integration_rehearsal_pass"
)

EVIDENCE = [
    "docs/raisa-provider-free-disposable-postgresql-status-confirm-product-adapter-integration-rehearsal-plan.md",
    "docs/security/raisa-provider-free-disposable-postgresql-status-confirm-product-adapter-integration-rehearsal-threat-model-delta.md",
    "app/services/appointment_status_product_adapter.py",
    "orchestration/continuity/raisa-provider-free-disposable-postgresql-status-confirm-product-adapter-integration-rehearsal/rehearsal-contract.json",
    "orchestration/continuity/raisa-provider-free-disposable-postgresql-status-confirm-product-adapter-integration-rehearsal/rehearsal-contract.schema.json",
    "orchestration/continuity/raisa-provider-free-disposable-postgresql-status-confirm-product-adapter-integration-rehearsal/provider-free-product-adapter-postgresql-evidence.schema.json",
    "orchestration/continuity/raisa-provider-free-disposable-postgresql-status-confirm-product-adapter-integration-rehearsal/provider-free-product-adapter-postgresql-evidence.json",
    "scripts/raisa_provider_free_disposable_postgresql_status_confirm_product_adapter_integration_rehearsal.py",
    "tests/test_raisa_provider_free_disposable_postgresql_status_confirm_product_adapter_integration_rehearsal.py",
    "tests/test_raisa_provider_free_disposable_postgresql_status_confirm_product_adapter_integration_rehearsal_plan.py",
    "docs/raisa-provider-free-disposable-postgresql-status-confirm-product-adapter-integration-rehearsal-closeout.md",
    "orchestration/agent_inbox/codex/raisa-status-confirm-product-adapter-postgresql-integration-sol-acceptance.md",
    "orchestration/human_inbox/yuri/2026-08-13--status-confirm-product-adapter-postgresql-integration.md",
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def update(
    graph: dict[str, Any], compass: dict[str, Any]
) -> tuple[dict[str, Any], dict[str, Any]]:
    if graph["graph_revision"] != 271 or compass["map_revision"] != 253:
        raise ValueError("unexpected continuity baseline")
    if any(node["id"] == NODE_ID for node in graph["nodes"]):
        raise ValueError("product-adapter PostgreSQL node already exists")
    graph["graph_revision"] = 272
    graph["updated_at"] = UPDATED_AT
    graph["nodes"].append(
        {
            "id": NODE_ID,
            "title": "Disposable PostgreSQL status-confirm product-adapter integration",
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
            "relationships": [
                {
                    "node_id": "raisa-provider-free-unmounted-status-confirm-product-adapter-rehearsal",
                    "relation": "builds_on",
                }
            ],
            "authority": {
                "authorized_openings": [
                    "owned disposable authored-synthetic PostgreSQL read/write and exact cleanup"
                ],
                "notes": [
                    "No route, product data, provider, deployment or protected-ref authority.",
                    "The disposable application role is non-superuser, non-BYPASSRLS and forced through five tenant policies.",
                ],
            },
            "decisions": [
                {
                    "id": "accept-status-confirm-product-adapter-postgresql-integration",
                    "source": EVIDENCE[11],
                    "status": "accepted",
                    "summary": "Accept exact adapter/physical PostgreSQL integration and proceed to provider-free route convergence.",
                }
            ],
            "claim_scope": [
                "Twelve serial authored-synthetic scenarios pass under forced five-table RLS.",
                "Atomic mutation/audit/receipt, adjacent version, byte-identical replay, rollback and pooled tenant-setting cleanup pass.",
                "All 104 hostile mutations, 112 focused current-lineage tests and the 193-test canonical fast profile pass.",
            ],
            "contract_evidence": [EVIDENCE[3]],
            "evidence": {
                "plans": EVIDENCE[:2],
                "findings": [],
                "closeouts": [EVIDENCE[10], EVIDENCE[12]],
                "acceptances": [EVIDENCE[11]],
                "receipts": [],
                "tests": EVIDENCE[8:10],
                "artifacts": EVIDENCE[2:8],
            },
            "unresolved_gates": [
                "The existing HTTP route still uses its legacy local write path.",
                "Opaque proposal-version carriage and exact stored-byte HTTP delivery remain unproved.",
                "Diary UI consumption remains closed until route convergence passes.",
            ],
        }
    )

    compass["map_revision"] = 254
    compass["source_graph_revision"] = 272
    compass["updated_at"] = UPDATED_AT
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 272 / Compass 254. The status-confirm product adapter "
        "passes real disposable PostgreSQL/RLS integration; HTTP route convergence remains closed."
    )
    compass["journey"].append(
        {
            "node_id": NODE_ID,
            "lineage_parent": "raisa-provider-free-unmounted-status-confirm-product-adapter-rehearsal",
            "strategic_role": "Join the accepted application adapter to the accepted physical database seam",
            "outcome": "Exact atomic commit, replay, rollback, RLS and tenant-setting lifecycle pass on disposable PostgreSQL 16.",
            "evidence": EVIDENCE,
        }
    )
    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": "The backend status-confirm path is ready for HTTP route convergence",
        "why_now": "Application and database behavior now pass together; the remaining backend gap is the existing route-local implementation and transport binding.",
        "outcome": "Twelve PostgreSQL integration scenarios pass with exact cleanup and no product data.",
        "unlocks": [
            "Freeze one provider-free authored-synthetic status-confirm HTTP route-convergence tranche."
        ],
        "does_not_solve": [
            "HTTP dependency wiring, opaque proposal-version carriage or exact stored-byte response delivery.",
            "Diary UI consumption or other command families.",
            "Product/patient data, concurrency, restart, deployment, production or release.",
        ],
        "evidence": EVIDENCE,
    }
    for item in compass["programme_support_horizon"]:
        if item["id"] == "raisa-practice-context-fabric":
            item["prerequisites"] = [
                "Preserve the accepted physical, composition, product-adapter and PostgreSQL integration proofs.",
                "Converge the existing authenticated status-confirm route with opaque version binding and stored-byte replay.",
                "Keep product data, providers, deployment and protected integration separately gated.",
            ]
            for path in EVIDENCE:
                if path not in item["evidence"]:
                    item["evidence"].append(path)
            break
    else:
        raise ValueError("Context Fabric horizon missing")
    compass["map_limits"].append(
        "The accepted PostgreSQL product-adapter integration is serial, disposable, authored-synthetic and off-route; HTTP and UI behavior remain unproved."
    )
    return graph, compass


def update_agents(text: str) -> str:
    required_marker = (
        "must preserve the accepted unmounted status-confirm product adapter at exact source "
        "`b728b903c99fa35f231df04ba68263533261121a`"
    )
    if required_marker not in text:
        raise ValueError("required Git relation baseline missing")
    text = text.replace(
        required_marker,
        "must preserve the accepted disposable PostgreSQL status-confirm product-adapter integration at exact source "
        f"`{SOURCE_HEAD}`, the accepted unmounted status-confirm product adapter at exact source "
        "`b728b903c99fa35f231df04ba68263533261121a`",
        1,
    )
    old_track = (
        "The Context Fabric/status-confirm line now has an accepted physical seam, unmounted composition and product adapter; real PostgreSQL adapter integration and route wiring remain closed."
    )
    new_track = (
        "The Context Fabric/status-confirm line now passes through physical seam, composition, product adapter and disposable PostgreSQL/RLS integration; HTTP route convergence remains closed."
    )
    if old_track not in text:
        raise ValueError("active product-track baseline missing")
    text = text.replace(old_track, new_track, 1)
    lines = text.splitlines()
    current_indexes = [i for i, line in enumerate(lines) if line.startswith("| Current result |")]
    next_indexes = [i for i, line in enumerate(lines) if line.startswith("| Next implementation |")]
    if len(current_indexes) != 1 or len(next_indexes) != 1:
        raise ValueError("current result/next rows are not unique")
    acceptance = (
        "| Disposable PostgreSQL status-confirm product-adapter integration acceptance | "
        "Plan/threat delta, adapter, closed contract/schemas/evidence, rehearsal/tests, timestamped closeout, "
        "Sol/Yuri summaries and continuity updater/test under the matching named paths. |"
    )
    lines.insert(current_indexes[0], acceptance)
    current_index = current_indexes[0] + 1
    next_index = next_indexes[0] + 1
    lines[current_index] = (
        f"| Current result | At Continuity 272 / Compass 254, `{RESULT}` is accepted at exact source "
        f"`{SOURCE_HEAD}`. Twelve serial PostgreSQL-16 scenarios pass under a restricted application role and "
        "forced five-table RLS: atomic mutation/audit/v1 receipt, adjacent version, byte-identical replay, both "
        "authority checks, stale/tampered/default-denial stops, rollback and pooled transaction-local tenant-context "
        "cleanup. All 104 hostile mutations, 112 current-lineage focused tests and the 193-test canonical fast profile "
        "pass with exact container/network cleanup. The current HTTP route remains on its legacy local implementation. |"
    )
    lines[next_index] = (
        f"| Next implementation | Freeze one provider-free authored-synthetic status-confirm HTTP route-convergence "
        f"tranche over exact source `{SOURCE_HEAD}`. Replace the existing `/appointments/proposals/status-confirm` "
        "route-local write path with the accepted product adapter, carry the opaque proposal-version binding without "
        "client authority, preserve status-only admission, decide the canonical alias and prove exact stored-byte HTTP "
        "replay against owned disposable PostgreSQL. Route/schema/dependency/API-contract edits and local synthetic "
        "calls are authorised; patient/clinical or operational product data, other command families, provider/ADC, "
        "credential/IAM/network, deployment, production, release, Pages and protected-ref movement remain closed. "
        "Diary UI wiring follows after this route tranche. Preserve `docs/branding/` and all unrelated untracked files; "
        "use explicit-path staging only. |"
    )
    return "\n".join(lines) + "\n"


def compact_agents(text: str) -> str:
    lines = text.splitlines()
    matches = [i for i, line in enumerate(lines) if line.startswith("| Active product track |")]
    if len(matches) != 1:
        raise ValueError("active product-track row is not unique")
    lines[matches[0]] = (
        "| Active product track | Yuri accepted the provider-free supervised appointment foundation, backend-owned "
        "intent-projected Diary and tablet-first `RECEPTION ONE™` projection-console UX. Core read/proposal, native "
        "Diary, cue/reconciliation and Stage 3A/3B readiness proofs pass; the voluntary reception-staff cohort remains "
        "unscheduled. Status-confirm now passes physical, composition, application-adapter and disposable PostgreSQL/RLS "
        "integration; HTTP convergence is next, then visible Diary wiring. Naming/artwork, voice, other event/command "
        "families, real product data, providers, deployment, production, release, Pages and protected refs remain closed. |"
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    graph, compass = update(read_json(GRAPH_PATH), read_json(COMPASS_PATH))
    write_json(GRAPH_PATH, graph)
    write_json(COMPASS_PATH, compass)
    old = (
        "> EMR4 is at Continuity 271 / Compass 253. The unmounted status-confirm product "
        "adapter passes. Disposable PostgreSQL integration and route wiring remain closed."
    )
    new = (
        "> EMR4 is at Continuity 272 / Compass 254. The status-confirm product adapter passes "
        "disposable PostgreSQL/RLS integration. HTTP route convergence remains closed."
    )
    compass_text = COMPASS_DOC_PATH.read_text(encoding="utf-8")
    if old not in compass_text:
        raise ValueError("Compass orientation baseline missing")
    COMPASS_DOC_PATH.write_text(compass_text.replace(old, new, 1), encoding="utf-8")
    updated_agents = update_agents(AGENTS_PATH.read_text(encoding="utf-8"))
    AGENTS_PATH.write_text(compact_agents(updated_agents), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
