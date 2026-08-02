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
UPDATED_AT = "2026-08-02T02:00:00Z"
BRANCH = "codex/raisa-two-component-oidc-verifier-architecture"
SOURCE_HEAD = "805b32ef616daf3c904b8de698856ec211b17bec"
PARENT = "raisa-maintained-oidc-verifier-session-bridge-architecture"
NODE = "raisa-two-component-oidc-verifier-architecture-revision"

ARTIFACTS = {
    "plan": "docs/raisa-two-component-oidc-verifier-architecture-revision-plan.md",
    "design": "docs/raisa-two-component-oidc-verifier-architecture-revision-design.md",
    "threat": "docs/security/raisa-two-component-oidc-verifier-architecture-threat-model-delta.md",
    "review": "docs/security/raisa-oidc-verifier-dependency-review-2026-08-02.md",
    "diagnostic": "docs/security/raisa-msal-offline-adapter-admission-diagnostic-2026-08-02.md",
    "hardening": "docs/security/hardening/raisa-two-component-oidc-verifier/hardening.md",
    "openapi": "docs/api-spine/openapi/application-identity-federation-session-bridge.yaml",
    "policy": "orchestration/continuity/raisa-two-component-oidc-verifier-architecture-revision/architecture-policy.json",
    "cases": "orchestration/continuity/raisa-two-component-oidc-verifier-architecture-revision/acceptance-cases.json",
    "evidence": "orchestration/continuity/raisa-two-component-oidc-verifier-architecture-revision/provider-free-acceptance-evidence.json",
    "dependency_evidence": "orchestration/continuity/raisa-two-component-oidc-verifier-architecture-revision/dependency-review-evidence.json",
    "closeout": "docs/raisa-two-component-oidc-verifier-architecture-revision-closeout.md",
    "acceptance": "orchestration/agent_inbox/codex/raisa-two-component-oidc-verifier-architecture-sol-acceptance.md",
    "rehydration": "orchestration/agent_inbox/codex/raisa-two-component-oidc-verifier-architecture-rehydration-receipt.json",
    "preacceptance": "orchestration/agent_inbox/codex/raisa-two-component-oidc-verifier-architecture-preacceptance-receipt.json",
    "precommit": "orchestration/agent_inbox/codex/raisa-two-component-oidc-verifier-architecture-precommit-receipt.json",
    "diagnostic_receipt": "orchestration/agent_inbox/codex/raisa-msal-offline-adapter-admission-rehydration-receipt.json",
    "runner": "scripts/raisa_two_component_oidc_verifier_architecture_acceptance.py",
    "tests": "tests/test_raisa_two_component_oidc_verifier_architecture.py",
    "continuity_runner": "scripts/raisa_two_component_oidc_verifier_architecture_continuity_update.py",
    "continuity_tests": "tests/test_raisa_two_component_oidc_verifier_architecture_continuity.py",
}


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _evidence() -> dict[str, list[str]]:
    return {
        "plans": [ARTIFACTS["plan"], ARTIFACTS["design"], ARTIFACTS["threat"], ARTIFACTS["hardening"]],
        "findings": [ARTIFACTS["diagnostic"], ARTIFACTS["review"], ARTIFACTS["openapi"], ARTIFACTS["policy"], ARTIFACTS["cases"], ARTIFACTS["dependency_evidence"], ARTIFACTS["evidence"]],
        "closeouts": [ARTIFACTS["closeout"]],
        "acceptances": [ARTIFACTS["acceptance"]],
        "receipts": [ARTIFACTS["diagnostic_receipt"], ARTIFACTS["rehydration"], ARTIFACTS["preacceptance"], ARTIFACTS["precommit"]],
        "tests": [ARTIFACTS["runner"], ARTIFACTS["tests"], ARTIFACTS["continuity_runner"], ARTIFACTS["continuity_tests"]],
    }


def update_graph() -> None:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 193:
        if graph["nodes"][-1]["id"] != NODE:
            raise SystemExit("Revision 193 has an unexpected terminal node.")
        return
    if graph["graph_revision"] != 192 or graph["nodes"][-1]["id"] != PARENT:
        raise SystemExit("Unexpected two-component verifier predecessor.")
    graph["nodes"].append({
        "id": NODE,
        "title": "Raisa Two-Component OIDC Verifier Architecture Revision",
        "kind": "foundation",
        "status": "accepted",
        "created_at": UPDATED_AT,
        "updated_at": UPDATED_AT,
        "coordinates": {"git_ref": BRANCH, "source_head": SOURCE_HEAD, "thread_id": None, "worktree_role": "task"},
        "relationships": [{"node_id": PARENT, "relation": "builds_on"}],
        "authority": {
            "authorized_openings": [{"boundary": "api-change", "source": ARTIFACTS["plan"], "scope": "Correct the verifier ownership contract, admit exact maintained packages and prove the seam provider-free."}],
            "notes": [
                "Yuri explicitly authorised the recommended two-component architecture revision and verifier dependency review.",
                "No application adapter, route, provider request, real identity, database change, application session, product read, deployment, production or release occurred.",
                "The user-owned docs/branding directory remained untracked, unstaged and excluded."
            ],
        },
        "decisions": [
            {"id": "separate-msal-protocol-from-authlib-verification-193", "source": ARTIFACTS["design"], "status": "accepted", "summary": "MSAL owns the Microsoft code flow; Authlib and JOSE RFC independently own ID-token signature, key and OIDC claim admission."},
            {"id": "admit-exact-verifier-dependencies-193", "source": ARTIFACTS["review"], "status": "accepted", "summary": "Pin MSAL 1.37.0, Authlib 1.7.2 and JOSE RFC 1.7.4 after licence, maintenance, compatibility, hash and advisory review."},
            {"id": "use-form-post-callback-193", "source": ARTIFACTS["openapi"], "status": "accepted", "summary": "Revise the non-mounted callback to POST form parameters so the authorization code is not carried in a URL."},
            {"id": "keep-runtime-identity-session-product-closed-193", "source": ARTIFACTS["closeout"], "status": "accepted", "summary": "Keep adapter wiring, live Microsoft, real identity, bindings, sessions, product access and deployment closed."}
        ],
        "claim_scope": [
            "Seventeen provider-free authored-synthetic cases prove the exact MSAL flow configuration and Authlib signed-token seam.",
            "Tampering, algorithm/claim/tenant failures, oversized tokens and exhausted key refresh deny admission.",
            "The architecture and exact package pins are accepted; no runtime adapter or live identity path exists."
        ],
        "contract_evidence": [],
        "evidence": _evidence(),
        "unresolved_gates": [
            "The provider-free application adapter requires fresh authority.",
            "Live Microsoft registration, tenant traffic and real identity require later separate authority.",
            "Identity binding, application sessions, product reads, deployment, production and release remain closed.",
            "Protected integration and GitHub Pages remain separately closed."
        ],
    })
    graph["graph_revision"] = 193
    graph["updated_at"] = UPDATED_AT
    _write(GRAPH, graph)


def update_compass() -> None:
    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    if compass["map_revision"] == 174 and compass["source_graph_revision"] == 193 and compass["current_position"]["node_id"] == NODE:
        return
    if compass["map_revision"] != 173 or compass["source_graph_revision"] != 192 or compass["current_position"]["node_id"] != PARENT:
        raise SystemExit("Unexpected two-component verifier Compass predecessor.")
    evidence = [ARTIFACTS["plan"], ARTIFACTS["design"], ARTIFACTS["threat"], ARTIFACTS["review"], ARTIFACTS["hardening"], ARTIFACTS["openapi"], ARTIFACTS["dependency_evidence"], ARTIFACTS["evidence"], ARTIFACTS["closeout"]]
    compass["journey"].append({
        "node_id": NODE,
        "lineage_parent": PARENT,
        "strategic_role": "Correct cryptographic identity-admission ownership before runtime implementation",
        "outcome": "The architecture now separates MSAL protocol mechanics from Authlib/JOSE RFC verification, admits exact reviewed pins, uses form_post and passes seventeen offline cases.",
        "evidence": evidence,
    })
    compass["current_position"] = {
        "node_id": NODE,
        "strategic_role": "Two-component Microsoft federation and signed-token verification architecture",
        "why_now": "Source inspection proved the parent MSAL-only verifier claim was incorrect and runtime implementation had to stop.",
        "outcome": "The corrected seam and exact dependencies pass offline without an adapter, provider call, real identity, database change, session, product read or deployment.",
        "unlocks": [
            "Review the architecture/dependency tranche on its stacked draft pull request.",
            "Seek fresh authority for a provider-free runtime adapter behind the frozen ports and fault matrix."
        ],
        "does_not_solve": [
            "Live Microsoft behavior, tenant configuration, real identity or key-service availability.",
            "Identity binding, application-session creation or product authorization.",
            "Distributed abuse resistance, secrets, deployment, production or release."
        ],
        "evidence": evidence,
    }
    decisions = {item["id"]: item for item in compass["user_owned_decisions"]}
    completed = decisions["authorize-msal-offline-adapter-dependency-tranche"]
    completed["required_before"] = "Satisfied on 2026-08-02 only for dependency review/admission and the corrected two-component architecture. Runtime adapter implementation and all live identity authority remain closed."
    completed["evidence"] = evidence
    next_id = "authorize-two-component-oidc-runtime-adapter"
    if next_id not in decisions:
        compass["user_owned_decisions"].append({
            "id": next_id,
            "question": "Should EMR4 implement the provider-free MSAL/Authlib adapter behind the frozen two-component seam?",
            "required_before": "Any import or use of the admitted packages in application code. Live Microsoft, routes, database changes, real identity, sessions and product reads remain separately closed.",
            "evidence": evidence,
        })
    compass["map_limits"].insert(0, "The two-component verifier result is architecture and offline dependency admission only; it proves no application adapter, live provider behavior or real identity.")
    compass["orientation_statement"] = "EMR4 now has a corrected two-component Microsoft federation architecture: MSAL owns code-flow mechanics and Authlib/JOSE RFC owns signed ID-token admission. Continuity 193 / Compass 174 bind the provider-free package and seam evidence. Runtime adapter, live identity, binding, session, product, deployment, production and release remain closed."
    compass["map_revision"] = 174
    compass["source_graph_revision"] = 193
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
