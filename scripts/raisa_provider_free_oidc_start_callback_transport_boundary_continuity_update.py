from __future__ import annotations

import json
from pathlib import Path
from typing import Any

try:
    from scripts import ariadne_compass
except ModuleNotFoundError:
    import ariadne_compass  # type: ignore[no-redef]


ROOT = Path(__file__).resolve().parents[1]
GRAPH = ROOT / "orchestration" / "continuity" / "emr4-continuity-graph.json"
COMPASS = ROOT / "orchestration" / "continuity" / "emr4-compass.json"
REPORT = ROOT / "docs" / "ariadne-compass-current.md"
UPDATED_AT = "2026-08-02T10:00:00Z"
BRANCH = "codex/raisa-provider-free-oidc-start-callback-transport-boundary"
SOURCE_HEAD = "686b035ec4aab62afa2a5e4df1238f65326f4e1b"
PARENT = "raisa-postgresql-oidc-operational-connection-boundary"
NODE = "raisa-provider-free-oidc-start-callback-transport-boundary"

ARTIFACTS = {
    "plan": "docs/raisa-provider-free-oidc-start-callback-transport-boundary-plan.md",
    "design": "docs/raisa-provider-free-oidc-start-callback-transport-boundary-design.md",
    "threat": "docs/security/raisa-provider-free-oidc-start-callback-transport-boundary-threat-model-delta.md",
    "schema": "app/schemas/application_identity_oidc_transport.py",
    "service": "app/services/application_identity_oidc_transport.py",
    "router": "app/routers/application_auth.py",
    "hardening": "app/services/application_auth_operational_hardening.py",
    "openapi": "docs/api-spine/openapi/application-identity-federation-session-bridge.yaml",
    "evidence": "orchestration/continuity/raisa-provider-free-oidc-start-callback-transport-boundary/live-local-http-backend-postgres-evidence.json",
    "closeout": "docs/raisa-provider-free-oidc-start-callback-transport-boundary-closeout.md",
    "acceptance": "orchestration/agent_inbox/codex/raisa-provider-free-oidc-start-callback-transport-boundary-sol-acceptance.md",
    "runtime_state": "orchestration/agent_inbox/codex/raisa-provider-free-oidc-start-callback-transport-boundary-rehydration-runtime-state.json",
    "rehydration": "orchestration/agent_inbox/codex/raisa-provider-free-oidc-start-callback-transport-boundary-rehydration-receipt.json",
    "preacceptance": "orchestration/agent_inbox/codex/raisa-provider-free-oidc-start-callback-transport-boundary-preacceptance-receipt.json",
    "prepush": "orchestration/agent_inbox/codex/raisa-provider-free-oidc-start-callback-transport-boundary-prepush-receipt.json",
    "runner": "scripts/raisa_provider_free_oidc_start_callback_transport_boundary_acceptance.py",
    "tests": "tests/test_raisa_provider_free_oidc_start_callback_transport_boundary.py",
    "continuity_runner": "scripts/raisa_provider_free_oidc_start_callback_transport_boundary_continuity_update.py",
    "continuity_tests": "tests/test_raisa_provider_free_oidc_start_callback_transport_boundary_continuity.py",
}


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _evidence() -> dict[str, list[str]]:
    return {
        "plans": [ARTIFACTS["plan"], ARTIFACTS["design"], ARTIFACTS["threat"]],
        "findings": [
            ARTIFACTS["schema"],
            ARTIFACTS["service"],
            ARTIFACTS["router"],
            ARTIFACTS["hardening"],
            ARTIFACTS["openapi"],
            ARTIFACTS["evidence"],
        ],
        "closeouts": [ARTIFACTS["closeout"]],
        "acceptances": [ARTIFACTS["acceptance"]],
        "receipts": [
            ARTIFACTS["runtime_state"],
            ARTIFACTS["rehydration"],
            ARTIFACTS["preacceptance"],
            ARTIFACTS["prepush"],
        ],
        "tests": [
            ARTIFACTS["runner"],
            ARTIFACTS["tests"],
            ARTIFACTS["continuity_runner"],
            ARTIFACTS["continuity_tests"],
        ],
    }


def update_graph() -> None:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 197:
        if graph["nodes"][-1]["id"] != NODE:
            raise SystemExit("Revision 197 has an unexpected terminal node.")
        return
    if graph["graph_revision"] != 196 or graph["nodes"][-1]["id"] != PARENT:
        raise SystemExit("Unexpected OIDC transport predecessor.")
    graph["nodes"].append(
        {
            "id": NODE,
            "title": "Raisa Provider-Free OIDC Start/Callback Transport Boundary",
            "kind": "foundation",
            "status": "accepted",
            "created_at": UPDATED_AT,
            "updated_at": UPDATED_AT,
            "coordinates": {
                "git_ref": BRANCH,
                "source_head": SOURCE_HEAD,
                "thread_id": None,
                "worktree_role": "task",
            },
            "relationships": [{"node_id": PARENT, "relation": "builds_on"}],
            "authority": {
                "authorized_openings": [
                    {
                        "boundary": "api-change",
                        "source": ARTIFACTS["plan"],
                        "scope": "Mount the default-off provider-free Microsoft OIDC start/callback transport with exact origin/CSRF, strict form_post and a no-store exact-origin bridge, without binding, grant, session or product authority.",
                    }
                ],
                "notes": [
                    "Yuri authorised this fresh-authority gate and its next two logical descendants unless a material directional choice arises.",
                    "No live Microsoft call, real identity, binding, admission grant, application session, product read, deployment, production or release occurred.",
                    "The user-owned docs/branding directory remained untracked, unstaged and excluded.",
                ],
            },
            "decisions": [
                {
                    "id": "mount-provider-free-transport-default-off-197",
                    "source": ARTIFACTS["router"],
                    "status": "accepted",
                    "summary": "Mount start/callback routes behind a fail-closed default dependency so explicit runtime injection remains required.",
                },
                {
                    "id": "strict-start-and-form-post-admission-197",
                    "source": ARTIFACTS["service"],
                    "status": "accepted",
                    "summary": "Bind start to exact origin, pre-authentication CSRF and HMAC idempotency; byte-bound callback before unique allowlisted form parsing.",
                },
                {
                    "id": "release-fixed-bridge-with-zero-authority-197",
                    "source": ARTIFACTS["service"],
                    "status": "accepted",
                    "summary": "Discard verified provider identifiers and release only fixed enums through exact-origin postMessage with no grant, session, cookie or product value.",
                },
            ],
            "claim_scope": [
                "Real loopback HTTP plus disposable PostgreSQL proves the mounted provider-free start/callback lifecycle and one-use attempt consumption.",
                "Generic failure, restrictive bridge headers, zero response residue and complete server/database/two-role cleanup pass.",
                "Provider, real identity, binding, admission-grant, session and product counts remain zero.",
            ],
            "contract_evidence": [],
            "evidence": _evidence(),
            "unresolved_gates": [
                "The preauthorised provider-free HMAC-only binding resolver and short-lived admission-grant boundary requires a fresh five-source tranche rehydration.",
                "Atomic admission-grant redemption into the accepted application-session runtime is the following separately rehydrated descendant.",
                "Live Microsoft, real identity and product reads remain closed.",
                "Production secret custody, hosted connectivity, distributed abuse resistance and monitoring remain closed.",
                "Cloud/IAM, deployment, protected integration, production, release and GitHub Pages remain separately closed.",
            ],
        }
    )
    graph["graph_revision"] = 197
    graph["updated_at"] = UPDATED_AT
    _write(GRAPH, graph)


def update_compass() -> None:
    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    if (
        compass["map_revision"] == 178
        and compass["source_graph_revision"] == 197
        and compass["current_position"]["node_id"] == NODE
    ):
        return
    if (
        compass["map_revision"] != 177
        or compass["source_graph_revision"] != 196
        or compass["current_position"]["node_id"] != PARENT
    ):
        raise SystemExit("Unexpected OIDC transport Compass predecessor.")
    evidence = [
        ARTIFACTS["plan"],
        ARTIFACTS["design"],
        ARTIFACTS["threat"],
        ARTIFACTS["service"],
        ARTIFACTS["router"],
        ARTIFACTS["openapi"],
        ARTIFACTS["evidence"],
        ARTIFACTS["closeout"],
    ]
    compass["journey"].append(
        {
            "node_id": NODE,
            "lineage_parent": PARENT,
            "strategic_role": "Expose the dormant provider-free OIDC adapter through a strict default-off browser transport",
            "outcome": "Exact-origin start and strict callback routes now consume one encrypted attempt and release only a fixed no-authority bridge message.",
            "evidence": evidence,
        }
    )
    compass["current_position"] = {
        "node_id": NODE,
        "strategic_role": "Provider-free mounted OIDC start/callback transport boundary",
        "why_now": "The accepted operational attempt store remained route-free; Yuri authorised the exact default-off transport gap and two logical descendants.",
        "outcome": "Real loopback HTTP and disposable PostgreSQL prove exact origin/CSRF/idempotency, strict form_post, one-use consumption, generic denial and a restrictive fixed bridge with complete cleanup.",
        "unlocks": [
            "Review the transport result on its stacked draft pull request.",
            "Freshly rehydrate the preauthorised HMAC-only binding resolver and short-lived admission-grant descendant.",
        ],
        "does_not_solve": [
            "Live Microsoft/provider calls, real identities or binding resolution.",
            "Admission-grant persistence, application-session redemption or product access.",
            "Production secret custody, hosted connectivity, distributed abuse resistance, monitoring, deployment, production or release.",
        ],
        "evidence": evidence,
    }
    decisions = {item["id"]: item for item in compass["user_owned_decisions"]}
    completed = decisions["authorize-provider-free-oidc-start-callback-transport-boundary"]
    completed["required_before"] = (
        "Satisfied on 2026-08-02 only for the default-off provider-free authored-synthetic start/callback transport. Live Microsoft, real identity, binding, admission grant, session and product reads remain closed."
    )
    completed["evidence"] = evidence
    next_id = "authorize-provider-free-oidc-binding-admission-grant-boundary"
    if next_id not in decisions:
        compass["user_owned_decisions"].append(
            {
                "id": next_id,
                "question": "Should EMR4 add the provider-free HMAC-only binding resolver and short-lived admission-grant boundary?",
                "required_before": "Preauthorised by Yuri on 2026-08-02, but requires a fresh five-source tranche rehydration before binding resolution or admission-grant persistence. Application-session creation and product reads remain closed.",
                "evidence": evidence,
            }
        )
    compass["map_limits"].insert(
        0,
        "The mounted OIDC transport result is default-off and provider-free: it releases only fixed authored-synthetic bridge enums and proves no live Microsoft, real identity, binding, admission grant, application session or product readiness.",
    )
    compass["orientation_statement"] = (
        "EMR4 now has a default-off provider-free Microsoft OIDC start/callback transport over the accepted durable attempt runtime. Continuity 197 / Compass 178 bind exact origin/CSRF/idempotency, strict form_post, one-use consumption and a restrictive fixed bridge. Live Microsoft, real identity, binding/grant/session/product access, cloud/IAM, deployment, production and release remain closed."
    )
    compass["map_revision"] = 178
    compass["source_graph_revision"] = 197
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)


def render_report() -> None:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")


def main() -> int:
    update_graph()
    update_compass()
    render_report()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
