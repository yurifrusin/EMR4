"""Apply the accepted unmounted status-confirm product-adapter continuity update."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
GRAPH_PATH = ROOT / "orchestration/continuity/emr4-continuity-graph.json"
COMPASS_PATH = ROOT / "orchestration/continuity/emr4-compass.json"
COMPASS_DOC_PATH = ROOT / "docs/ariadne-compass-current.md"
AGENTS_PATH = ROOT / "AGENTS.md"
NODE_ID = "raisa-provider-free-unmounted-status-confirm-product-adapter-rehearsal"
SOURCE_HEAD = "b728b903c99fa35f231df04ba68263533261121a"
UPDATED_AT = "2026-08-13T00:44:05Z"
RESULT = "raisa_provider_free_unmounted_status_confirm_product_adapter_rehearsal_pass"

EVIDENCE = [
    "docs/raisa-provider-free-unmounted-status-confirm-product-adapter-rehearsal-plan.md",
    "docs/security/raisa-provider-free-unmounted-status-confirm-product-adapter-rehearsal-threat-model-delta.md",
    "app/services/appointment_status_product_adapter.py",
    "orchestration/continuity/raisa-provider-free-unmounted-status-confirm-product-adapter-rehearsal/product-adapter-rehearsal-contract.json",
    "orchestration/continuity/raisa-provider-free-unmounted-status-confirm-product-adapter-rehearsal/product-adapter-rehearsal-evidence.schema.json",
    "orchestration/continuity/raisa-provider-free-unmounted-status-confirm-product-adapter-rehearsal/product-adapter-rehearsal-evidence.json",
    "scripts/raisa_provider_free_unmounted_status_confirm_product_adapter_rehearsal.py",
    "tests/test_raisa_provider_free_unmounted_status_confirm_product_adapter.py",
    "tests/test_raisa_provider_free_unmounted_status_confirm_product_adapter_plan.py",
    "docs/raisa-provider-free-unmounted-status-confirm-product-adapter-rehearsal-closeout.md",
    "orchestration/agent_inbox/codex/raisa-status-confirm-product-adapter-rehearsal-sol-acceptance.md",
    "orchestration/human_inbox/yuri/2026-08-13--status-confirm-product-adapter-rehearsal.md",
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def update(graph: dict[str, Any], compass: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    if graph["graph_revision"] != 270 or compass["map_revision"] != 252:
        raise ValueError("unexpected continuity baseline")
    if any(node["id"] == NODE_ID for node in graph["nodes"]):
        raise ValueError("product-adapter node already exists")
    graph["graph_revision"] = 271
    graph["updated_at"] = UPDATED_AT
    graph["nodes"].append(
        {
            "id": NODE_ID,
            "title": "Provider-free unmounted status-confirm product-adapter rehearsal",
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
                    "node_id": "raisa-provider-free-read-only-status-confirm-route-mounting-readiness-rereview",
                    "relation": "builds_on",
                }
            ],
            "authority": {
                "authorized_openings": [],
                "notes": [
                    "Authored-synthetic, provider-free and unmounted adapter only.",
                    "No route, database, product data, provider, command, deployment or protected-ref authority.",
                ],
            },
            "decisions": [
                {
                    "id": "accept-status-confirm-product-adapter",
                    "source": EVIDENCE[9],
                    "status": "accepted",
                    "summary": "Accept the four coupled adapters and the opaque proposal-version binding; continue off-route to disposable PostgreSQL integration.",
                }
            ],
            "claim_scope": [
                "Server-session/current-authority, status-only admission, locked policy and atomic effect/audit adapters pass together.",
                "A signed proposal-version binding preserves exact lost-response replay and locked-generation checks.",
                "All thirteen source hashes, 84 hostile mutations, 118 focused checks and 193 canonical fast-profile tests pass.",
            ],
            "contract_evidence": [],
            "evidence": {
                "plans": EVIDENCE[:2],
                "findings": [],
                "closeouts": [EVIDENCE[9], EVIDENCE[11]],
                "acceptances": [EVIDENCE[10]],
                "receipts": [],
                "tests": EVIDENCE[7:9],
                "artifacts": EVIDENCE[2:7],
            },
            "unresolved_gates": [
                "Real PostgreSQL/RLS integration of the product adapter remains unproved.",
                "Route dependency wiring, proposal-version carriage and exact stored-byte HTTP delivery remain closed.",
            ],
        }
    )

    compass["map_revision"] = 253
    compass["source_graph_revision"] = 271
    compass["updated_at"] = UPDATED_AT
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 271 / Compass 253. The unmounted status-confirm "
        "product adapter passes; disposable PostgreSQL integration and route wiring remain closed."
    )
    compass["journey"].append(
        {
            "node_id": NODE_ID,
            "lineage_parent": "raisa-provider-free-read-only-status-confirm-route-mounting-readiness-rereview",
            "strategic_role": "Close the application-owned bridge between authenticated product facts and the accepted physical command seam",
            "outcome": "All four product-adapter blockers pass authored-synthetic rehearsal with exact response-loss replay.",
            "evidence": EVIDENCE,
        }
    )
    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": "The off-route application adapter is ready for disposable database integration",
        "why_now": "The physical seam and product translation now pass separately; their real PostgreSQL behavior must be composed before route wiring.",
        "outcome": "Four coupled adapters and proposal-version recovery pass without mounting or calling a route.",
        "unlocks": [
            "Freeze one provider-free disposable PostgreSQL-16 product-adapter integration rehearsal."
        ],
        "does_not_solve": [
            "Real PostgreSQL/RLS behavior or cleanup.",
            "HTTP route wiring, proposal-version transport or stored-byte delivery.",
            "Product/patient data, UI behavior, deployment, production or release.",
        ],
        "evidence": EVIDENCE,
    }
    for item in compass["programme_support_horizon"]:
        if item["id"] == "raisa-practice-context-fabric":
            item["prerequisites"] = [
                "Preserve the accepted physical, composition and product-adapter proofs.",
                "Rehearse the exact adapter against disposable PostgreSQL while remaining off-route.",
                "Keep route transport/mounting, product data, providers and protected integration separately gated.",
            ]
            for path in EVIDENCE:
                if path not in item["evidence"]:
                    item["evidence"].append(path)
            break
    else:
        raise ValueError("Context Fabric horizon missing")
    compass["map_limits"].append(
        "The accepted product adapter is unmounted and authored-synthetic; real PostgreSQL and HTTP behavior remain unproved."
    )
    return graph, compass


def update_agents(text: str) -> str:
    required_marker = (
        "must preserve the accepted unmounted status-confirm route-convergence composition"
    )
    if required_marker not in text:
        raise ValueError("required Git relation baseline missing")
    text = text.replace(
        required_marker,
        "must preserve the accepted unmounted status-confirm product adapter at exact source "
        f"`{SOURCE_HEAD}`, the accepted unmounted status-confirm route-convergence composition",
        1,
    )
    product_old = (
        "The accepted Context Fabric and status-confirm durability descendants now culminate in an "
        "unmounted status-confirm composition plus a read-only readiness re-review: the physical seam "
        "and closed outcome mapping pass, but route mounting remains blocked on four application-owned adapters."
    )
    product_new = (
        "The accepted Context Fabric and status-confirm durability descendants now culminate in an "
        "unmounted composition and application-owned product adapter: server-session/current-authority "
        "ingress, status-only admission, locked policy and atomic effect/audit staging pass authored-synthetic "
        "rehearsal, while real PostgreSQL adapter integration and route wiring remain closed."
    )
    if product_old not in text:
        raise ValueError("active product-track baseline missing")
    text = text.replace(product_old, product_new, 1)

    acceptance_row = (
        "| Provider-free unmounted status-confirm product-adapter rehearsal acceptance | "
        "`docs/raisa-provider-free-unmounted-status-confirm-product-adapter-rehearsal-plan.md`, "
        "`docs/security/raisa-provider-free-unmounted-status-confirm-product-adapter-rehearsal-threat-model-delta.md`, "
        "`app/services/appointment_status_product_adapter.py`, the matching continuity directory, rehearsal script, "
        "two focused tests, receipt-state pairs, closeout, Sol acceptance, Yuri summary and continuity updater/test. |"
    )
    lines = text.splitlines()
    current_indexes = [i for i, line in enumerate(lines) if line.startswith("| Current result |")]
    next_indexes = [i for i, line in enumerate(lines) if line.startswith("| Next implementation |")]
    if len(current_indexes) != 1 or len(next_indexes) != 1:
        raise ValueError("current baton result/next rows are not unique")
    current_index = current_indexes[0]
    lines.insert(current_index, acceptance_row)
    current_index += 1
    next_index = next_indexes[0] + 1
    lines[current_index] = (
        f"| Current result | At Continuity 271 / Compass 253, `{RESULT}` is accepted at exact source "
        f"`{SOURCE_HEAD}`. The four coupled application blockers pass together: HMAC-minimized authenticated "
        "session and two fresh current-authority checks, exact status-only admission, signed proposal plus opaque "
        "proposal-version binding with locked policy reconstruction, and atomic status/audit/adjacent-version staging "
        "into the accepted canonical private receipt. All thirteen frozen hashes, 84 hostile mutations, 118 focused "
        "checks and the 193-test canonical fast profile pass. A lost-response retry releases byte-identical stored "
        "bytes with one effect. The current route remains unchanged and unmounted; no real database, provider, "
        "product/patient data or command was used. |"
    )
    lines[next_index] = (
        f"| Next implementation | Freeze one provider-free disposable PostgreSQL-16 integration rehearsal for the "
        f"exact accepted status-confirm product adapter at source `{SOURCE_HEAD}`. It must remain off-route and use "
        "only owned authored-synthetic rows to prove transaction-local practice context, both fresh actor checks, "
        "exact one-mutation/one-audit/private-receipt completion, adjacent version, rollback and byte-identical replay "
        "with complete cleanup. It authorizes only disposable authored-synthetic database write/readback/cleanup; "
        "no product/runtime command/write is opened. It grants no route edit/mount/call, patient/clinical or operational product data, "
        "provider/ADC/credential/IAM/browser/network, deployment, production, release, Pages or protected-ref movement. "
        "Preserve `docs/branding/` and all unrelated untracked files and use explicit-path staging only. |"
    )
    return "\n".join(lines) + "\n"


def compact_current_agents(text: str) -> str:
    """Keep the live handover below its enforced compactness ceiling."""
    lines = text.splitlines()
    active_row = (
        "| Active product track | Yuri accepted the provider-free supervised appointment foundation, "
        "backend-owned intent-projected Diary and tablet-first `RECEPTION ONE™` projection-console UX. "
        "The typed meta-grid, responsive native Diary and key read/proposal, booking-context, cue and reconciliation "
        "proofs pass. Stage 3A/3B readiness passes; participant work still awaits Yuri's voluntary Australian "
        "general-practice reception-staff cohort. "
        "The Context Fabric/status-confirm line now has an accepted physical seam, unmounted composition and product "
        "adapter; real PostgreSQL adapter integration and route wiring remain closed. `RECEPTION ONE™` is the leading "
        "provisional user-facing name, meta-grid the architectural term and EMR4 internal. No rename, artwork, trademark, "
        "voice, further event family, external worker/transport, new product write, patient/product data, production, "
        "deployment, release, Pages or protected-ref authority is granted. |"
    )
    acceptance_row = (
        "| Provider-free unmounted status-confirm product-adapter rehearsal acceptance | "
        "Plan, threat delta, adapter, continuity evidence, rehearsal/tests, receipts, closeout, Sol/Yuri summaries "
        "and updater/test under the matching named paths. |"
    )
    active_matches = [i for i, line in enumerate(lines) if line.startswith("| Active product track |")]
    acceptance_matches = [
        i
        for i, line in enumerate(lines)
        if line.startswith(
            "| Provider-free unmounted status-confirm product-adapter rehearsal acceptance |"
        )
    ]
    if len(active_matches) != 1 or len(acceptance_matches) != 1:
        raise ValueError("compact current AGENTS rows are not unique")
    lines[active_matches[0]] = active_row
    lines[acceptance_matches[0]] = acceptance_row
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--compact-agents-only", action="store_true")
    args = parser.parse_args()
    if args.compact_agents_only:
        AGENTS_PATH.write_text(
            compact_current_agents(AGENTS_PATH.read_text(encoding="utf-8")),
            encoding="utf-8",
        )
        return 0
    graph, compass = update(read_json(GRAPH_PATH), read_json(COMPASS_PATH))
    write_json(GRAPH_PATH, graph)
    write_json(COMPASS_PATH, compass)
    old = (
        "> EMR4 is at Continuity 270 / Compass 252. The status-confirm readiness re-review passes "
        "with four remaining product-adapter blockers. Route mounting and product execution remain closed."
    )
    new = (
        "> EMR4 is at Continuity 271 / Compass 253. The unmounted status-confirm product adapter "
        "passes. Disposable PostgreSQL integration and route wiring remain closed."
    )
    compass_text = COMPASS_DOC_PATH.read_text(encoding="utf-8")
    if old not in compass_text:
        raise ValueError("Compass current orientation baseline missing")
    COMPASS_DOC_PATH.write_text(compass_text.replace(old, new, 1), encoding="utf-8")
    AGENTS_PATH.write_text(update_agents(AGENTS_PATH.read_text(encoding="utf-8")), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
