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
UPDATED_AT = "2026-08-03T00:30:00Z"
BRANCH = "codex/raisa-provider-free-office-practitioner-directory-consumer"
SOURCE_HEAD = "95381fc12da2e6a6bb8301bb7974c53e61c3c096"
PARENT = "raisa-provider-free-session-practitioner-directory-read-bridge"
NODE = "raisa-provider-free-office-practitioner-directory-consumer"

ARTIFACTS = {
    "plan": "docs/raisa-provider-free-office-practitioner-directory-consumer-plan.md",
    "design": "docs/raisa-provider-free-office-practitioner-directory-consumer-design.md",
    "threat": "docs/security/raisa-provider-free-office-practitioner-directory-consumer-threat-model-delta.md",
    "harness": "scripts/raisa_provider_free_office_practitioner_directory_consumer.py",
    "tests": "tests/test_raisa_provider_free_office_practitioner_directory_consumer.py",
    "browser": "orchestration/continuity/raisa-provider-free-office-practitioner-directory-consumer/browser-preview-evidence.json",
    "live": "orchestration/continuity/raisa-provider-free-office-practitioner-directory-consumer/live-office-backend-postgres-evidence.json",
    "proxy_failure": "orchestration/continuity/raisa-provider-free-office-practitioner-directory-consumer/real-office-pre-repair-evidence.json",
    "icon_failure": "orchestration/continuity/raisa-provider-free-office-practitioner-directory-consumer/real-office-icon-route-repair-evidence.json",
    "frame_failure": "orchestration/continuity/raisa-provider-free-office-practitioner-directory-consumer/real-office-word-online-frame-ancestor-repair-evidence.json",
    "desktop_manifest": "orchestration/continuity/raisa-provider-free-office-practitioner-directory-consumer/word-desktop-manifest.xml",
    "online_manifest": "orchestration/continuity/raisa-provider-free-office-practitioner-directory-consumer/word-online-manifest.xml",
    "closeout": "docs/raisa-provider-free-office-practitioner-directory-consumer-closeout.md",
    "acceptance": "orchestration/agent_inbox/codex/raisa-provider-free-office-practitioner-directory-consumer-sol-acceptance.md",
    "rehydration": "orchestration/agent_inbox/codex/raisa-provider-free-office-practitioner-directory-consumer-rehydration-receipt.json",
    "postcompaction": "orchestration/agent_inbox/codex/raisa-provider-free-office-practitioner-directory-consumer-postcompaction-receipt.json",
    "resume": "orchestration/agent_inbox/codex/raisa-provider-free-office-practitioner-directory-consumer-word-online-resume-receipt.json",
    "preacceptance": "orchestration/agent_inbox/codex/raisa-provider-free-office-practitioner-directory-consumer-preacceptance-receipt.json",
    "precommit": "orchestration/agent_inbox/codex/raisa-provider-free-office-practitioner-directory-consumer-precommit-receipt.json",
    "continuity_runner": "scripts/raisa_provider_free_office_practitioner_directory_consumer_continuity_update.py",
    "continuity_tests": "tests/test_raisa_provider_free_office_practitioner_directory_consumer_continuity.py",
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
            ARTIFACTS["harness"],
            ARTIFACTS["browser"],
            ARTIFACTS["live"],
            ARTIFACTS["proxy_failure"],
            ARTIFACTS["icon_failure"],
            ARTIFACTS["frame_failure"],
            ARTIFACTS["desktop_manifest"],
            ARTIFACTS["online_manifest"],
        ],
        "closeouts": [ARTIFACTS["closeout"]],
        "acceptances": [ARTIFACTS["acceptance"]],
        "receipts": [
            ARTIFACTS["rehydration"],
            ARTIFACTS["postcompaction"],
            ARTIFACTS["resume"],
            ARTIFACTS["preacceptance"],
            ARTIFACTS["precommit"],
        ],
        "tests": [
            ARTIFACTS["tests"],
            ARTIFACTS["continuity_runner"],
            ARTIFACTS["continuity_tests"],
        ],
    }


def update_graph() -> None:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 201:
        if graph["nodes"][-1]["id"] != NODE:
            raise SystemExit("Revision 201 has an unexpected terminal node.")
        graph["nodes"][-1]["evidence"] = _evidence()
        _write(GRAPH, graph)
        return
    if graph["graph_revision"] != 200 or graph["nodes"][-1]["id"] != PARENT:
        raise SystemExit("Unexpected Office-consumer predecessor.")
    graph["nodes"].append(
        {
            "id": NODE,
            "title": "Raisa Provider-Free Office Practitioner-Directory Consumer",
            "kind": "implementation",
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
                        "scope": "Authorize one task-scoped provider-free authored-synthetic Office consumer of the active-practitioner-directory factory in supervised installed Word and Word Online.",
                    }
                ],
                "notes": [
                    "Yuri authorised this tranche and performed the exact supervised host actions.",
                    "No general mount, patient/clinical/document access, provider call, real identity, product write, deployment, production or release occurred.",
                    "The user-owned docs/branding directory remained untracked, unstaged and excluded.",
                ],
            },
            "decisions": [
                {
                    "id": "independent-office-surface-sessions-201",
                    "source": ARTIFACTS["design"],
                    "status": "accepted",
                    "summary": "Installed Word and Word Online receive independent surface-bound sessions, CSRF values, nonces and synthetic practices.",
                },
                {
                    "id": "fixed-directory-document-and-projection-201",
                    "source": ARTIFACTS["harness"],
                    "status": "accepted",
                    "summary": "The client can issue only one fixed active-directory query and render one closed display-safe projection.",
                },
                {
                    "id": "application-owned-proxy-and-exact-frame-admission-201",
                    "source": ARTIFACTS["frame_failure"],
                    "status": "accepted",
                    "summary": "Application code owns strict one-hop proxy interpretation and CSP admits only the observed Office plus personal OneDrive frame chain.",
                },
            ],
            "claim_scope": [
                "Supervised installed Word and Word Online each rendered exactly two active authored-synthetic practitioners, logged out and rejected session reuse.",
                "Two required authorization-allowed audits and four direct PostgreSQL privilege denials passed before complete database, role, process, listener, relay and desktop-registration cleanup.",
                "Provider, Microsoft identity, patient/clinical, document and product-write side effects remained zero.",
            ],
            "contract_evidence": [
                {
                    "contract_id": "combined-patient-practitioner-time-duration-intent",
                    "status": "satisfied",
                    "evidence": [
                        ARTIFACTS["plan"],
                        ARTIFACTS["threat"],
                        ARTIFACTS["live"],
                        ARTIFACTS["tests"],
                    ],
                    "note": "The task consumer contains no patient, appointment, availability, proposal or command context and leaves the accepted combined-intent contract unchanged.",
                },
                {
                    "contract_id": "committed-reschedule-availability-reconciliation",
                    "status": "satisfied",
                    "evidence": [
                        ARTIFACTS["live"],
                        ARTIFACTS["closeout"],
                        ARTIFACTS["tests"],
                    ],
                    "note": "No Diary event, availability, selection, proposal or appointment state was read or changed.",
                },
            ],
            "evidence": _evidence(),
            "unresolved_gates": [
                "Real identity mapping and live Microsoft/provider interoperability remain closed.",
                "Patient/clinical/document reads, broader product resources and every product command/write remain closed.",
                "General endpoint mounting, organisational Office deployment and product-table RLS claims remain closed.",
                "Production secret custody, distributed abuse resistance, monitoring/SIEM, deployment, protected integration, production, release and GitHub Pages remain closed.",
            ],
        }
    )
    graph["graph_revision"] = 201
    graph["updated_at"] = UPDATED_AT
    _write(GRAPH, graph)


def update_compass() -> None:
    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    if (
        compass["map_revision"] == 182
        and compass["source_graph_revision"] == 201
        and compass["current_position"]["node_id"] == NODE
    ):
        return
    if (
        compass["map_revision"] != 181
        or compass["source_graph_revision"] != 200
        or compass["current_position"]["node_id"] != PARENT
    ):
        raise SystemExit("Unexpected Office-consumer Compass predecessor.")
    evidence = [
        ARTIFACTS["plan"],
        ARTIFACTS["design"],
        ARTIFACTS["threat"],
        ARTIFACTS["harness"],
        ARTIFACTS["live"],
        ARTIFACTS["closeout"],
    ]
    compass["journey"].append(
        {
            "node_id": NODE,
            "lineage_parent": PARENT,
            "strategic_role": "Put the first least-sensitive authorized product read into both real Office hosts",
            "outcome": "Independent supervised installed Word and Word Online sessions each rendered the fixed active-practitioner directory, logged out and rejected reuse.",
            "evidence": evidence,
        }
    )
    compass["current_position"] = {
        "node_id": NODE,
        "strategic_role": "Provider-free Office practitioner-directory consumer",
        "why_now": "The unmounted session-backed directory factory had passed, making an exact supervised Office consumer the least-sensitive next product proof.",
        "outcome": "Two real Office hosts now prove the fixed display-safe GraphQL read, required authorization audit, logout, post-logout denial and complete disposable cleanup.",
        "unlocks": [
            "Review the result on its stacked draft pull request.",
            "The authorised next descendant may make reload, retry and stale taskpane navigation visibly inert without broadening product authority.",
        ],
        "does_not_solve": [
            "Real identity, live Microsoft/provider interoperability or real principal mapping.",
            "Patient/clinical/document reads, broader product resources, commands or writes.",
            "General endpoint mounting, organisational deployment, production security, deployment or release.",
        ],
        "evidence": evidence,
    }
    decisions = {item["id"]: item for item in compass["user_owned_decisions"]}
    completed = decisions["authorize-provider-free-office-directory-consumer"]
    completed["required_before"] = (
        "Satisfied on 2026-08-03: Yuri authorised and supervised the exact authored-synthetic installed Word and Word Online consumer; real identity, broader product authority and production remain closed."
    )
    completed["evidence"] = evidence
    next_id = "authorize-provider-free-office-directory-reload-reconciliation"
    if next_id not in decisions:
        compass["user_owned_decisions"].append(
            {
                "id": next_id,
                "question": "Should reload, retry and stale Office taskpane navigation be reconciled into an explicit inert terminal state?",
                "required_before": "Satisfied by Yuri's authority for five clear provider-free descendants; this is the first recommended descendant and grants no new product resource or command authority.",
                "evidence": evidence,
            }
        )
    compass["map_limits"].insert(
        0,
        "The Office practitioner-directory result is provider-free, authored-synthetic, active-only and task-scoped; it proves neither real identity nor patient/clinical/document or product-write safety.",
    )
    compass["orientation_statement"] = (
        "EMR4 now carries one fixed, authorized active-practitioner-directory read through independent supervised installed Word and Word Online sessions. Continuity 201 / Compass 182 bind exact host admission, display-safe projection, authorization audit, logout, post-logout denial and complete disposable cleanup. Real identity, patient/clinical/document access, broader product authority, deployment, production and release remain closed."
    )
    compass["map_revision"] = 182
    compass["source_graph_revision"] = 201
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
