from __future__ import annotations

import json
from pathlib import Path
from typing import Any

try:
    from scripts import ariadne_compass
except ModuleNotFoundError:
    import ariadne_compass  # type: ignore[no-redef]


ROOT = Path(__file__).resolve().parents[1]
GRAPH = ROOT / "orchestration/continuity/emr4-continuity-graph.json"
COMPASS = ROOT / "orchestration/continuity/emr4-compass.json"
REPORT = ROOT / "docs/ariadne-compass-current.md"
UPDATED_AT = "2026-08-03T04:00:00Z"
BRANCH = "codex/raisa-provider-free-office-directory-lifecycle-descendants"
SOURCE_HEAD = "53d160ec4c7cf7d6a39d068e7fda4e46b592a431"
PARENT = "raisa-provider-free-office-practitioner-directory-consumer"
THREAT = "docs/security/raisa-provider-free-office-directory-lifecycle-descendants-threat-model-delta.md"
RUNNER = "scripts/raisa_provider_free_office_directory_lifecycle_descendants_acceptance.py"
TESTS = "tests/test_raisa_provider_free_office_directory_lifecycle_descendants.py"
EVIDENCE = "orchestration/continuity/raisa-provider-free-office-directory-lifecycle-descendants/provider-free-acceptance-evidence.json"
ACCEPTANCE = "orchestration/agent_inbox/codex/raisa-provider-free-office-directory-lifecycle-descendants-sol-acceptance.md"
RECEIPT = "orchestration/agent_inbox/codex/raisa-provider-free-office-directory-lifecycle-descendants-postcompaction-receipt.json"
PREACCEPTANCE = "orchestration/agent_inbox/codex/raisa-provider-free-office-directory-lifecycle-descendants-preacceptance-receipt.json"
PRECOMMIT = "orchestration/agent_inbox/codex/raisa-provider-free-office-directory-lifecycle-descendants-precommit-receipt.json"
ADAPTER = "app/services/application_auth_office_consumer.py"
HARNESS = "scripts/raisa_provider_free_office_practitioner_directory_consumer.py"
TASKPANE = "orchestration/continuity/raisa-provider-free-office-practitioner-directory-consumer/taskpane.js"

SPECS = [
    {
        "id": "raisa-provider-free-office-reload-terminal-reconciliation",
        "title": "Raisa Provider-Free Office Reload and Terminal Reconciliation",
        "result": "provider_free_office_reload_terminal_reconciliation_pass",
        "slug": "office-reload-terminal-reconciliation",
        "role": "Make repeated and restored Office taskpane navigation explicitly inert",
        "outcome": "Repeated delivery revokes surviving session authority once, clears task cookies, omits endpoint and launch material, and denies the stale DOM.",
    },
    {
        "id": "raisa-provider-free-office-session-loss-reconciliation",
        "title": "Raisa Provider-Free Office Session-Loss Reconciliation",
        "result": "provider_free_office_session_loss_reconciliation_pass",
        "slug": "office-session-loss-reconciliation",
        "role": "Converge expired and revoked sessions on one safe taskpane state",
        "outcome": "Expired and revoked sessions release no rows or raw errors and show one fixed close-and-reopen instruction.",
    },
    {
        "id": "raisa-provider-free-office-cross-surface-replay-isolation",
        "title": "Raisa Provider-Free Office Cross-Surface Replay Isolation",
        "result": "provider_free_office_cross_surface_replay_isolation_pass",
        "slug": "office-cross-surface-replay-isolation",
        "role": "Prove independent installed Word and Word Online authority partitions",
        "outcome": "Cookie/surface, CSRF and nonce swaps plus consumed-nonce replay are denied with zero product reads.",
    },
    {
        "id": "raisa-provider-free-office-lifecycle-observability",
        "title": "Raisa Provider-Free Office Lifecycle Observability",
        "result": "provider_free_office_lifecycle_observability_pass",
        "slug": "office-lifecycle-observability",
        "role": "Expose only bounded identifier-free lifecycle reason counts",
        "outcome": "A versioned ten-reason ledger contains no identifier, correlation or opaque launch value and routes nothing.",
    },
    {
        "id": "raisa-provider-free-default-off-office-consumer-adapter",
        "title": "Raisa Provider-Free Default-Off Office Consumer Adapter",
        "result": "provider_free_default_off_office_consumer_adapter_pass",
        "slug": "default-off-office-consumer-adapter",
        "role": "Extract reusable one-use Office lifecycle decisions without product wiring",
        "outcome": "The route-free adapter owns only fixed surface decisions, nonce admission and sanitized counters and remains absent from app.main.",
    },
]


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _paths(spec: dict[str, str]) -> tuple[str, str]:
    return (
        f"docs/raisa-provider-free-{spec['slug']}-plan.md",
        f"docs/raisa-provider-free-{spec['slug']}-closeout.md",
    )


def _node_evidence(spec: dict[str, str]) -> dict[str, list[str]]:
    plan, closeout = _paths(spec)
    return {
        "plans": [plan, THREAT],
        "findings": [ADAPTER, HARNESS, TASKPANE, EVIDENCE],
        "closeouts": [closeout],
        "acceptances": [ACCEPTANCE],
        "receipts": [RECEIPT, PREACCEPTANCE, PRECOMMIT],
        "tests": [RUNNER, TESTS],
    }


def _node(spec: dict[str, str], parent: str) -> dict[str, Any]:
    plan, closeout = _paths(spec)
    evidence = _node_evidence(spec)
    return {
        "id": spec["id"],
        "title": spec["title"],
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
        "relationships": [{"node_id": parent, "relation": "builds_on"}],
        "authority": {
            "authorized_openings": [
                {
                    "boundary": "api-change",
                    "source": plan,
                    "scope": spec["role"],
                }
            ],
            "notes": [
                "Yuri authorised five clear provider-free descendants along Sol's recommended path.",
                "No new product resource, write, provider, real identity, deployment, production or release authority opened.",
                "The user-owned docs/branding directory remained excluded.",
            ],
        },
        "decisions": [
            {
                "id": f"{spec['id']}-decision",
                "source": plan,
                "status": "accepted",
                "summary": spec["outcome"],
            }
        ],
        "claim_scope": [
            spec["outcome"],
            "Evidence is provider-free, authored-synthetic and limited to the existing active-practitioner Office consumer.",
        ],
        "contract_evidence": [
            {
                "contract_id": "combined-patient-practitioner-time-duration-intent",
                "status": "satisfied",
                "evidence": [plan, EVIDENCE, TESTS],
                "note": "No patient, appointment, availability, proposal, time, duration or command context was introduced.",
            },
            {
                "contract_id": "committed-reschedule-availability-reconciliation",
                "status": "satisfied",
                "evidence": [EVIDENCE, closeout, TESTS],
                "note": "No Diary event, availability, appointment, selection or proposal state was read or changed.",
            },
        ],
        "evidence": evidence,
        "unresolved_gates": [
            "Live Microsoft/provider interoperability and real identity mapping remain closed.",
            "Patient/clinical/document access, broader product reads and every product command/write remain closed.",
            "Distributed abuse resistance, monitoring/SIEM, organisational deployment, protected integration, production and release remain closed.",
        ],
    }


def update_graph() -> None:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 206:
        if graph["nodes"][-1]["id"] != SPECS[-1]["id"]:
            raise SystemExit("Revision 206 has an unexpected terminal node.")
        parent = PARENT
        for index, spec in enumerate(SPECS):
            graph["nodes"][-5 + index] = _node(spec, parent)
            parent = spec["id"]
        _write(GRAPH, graph)
        return
    if graph["graph_revision"] != 201 or graph["nodes"][-1]["id"] != PARENT:
        raise SystemExit("Unexpected lifecycle-descendant predecessor.")
    parent = PARENT
    for spec in SPECS:
        graph["nodes"].append(_node(spec, parent))
        parent = spec["id"]
    graph["graph_revision"] = 206
    graph["updated_at"] = UPDATED_AT
    _write(GRAPH, graph)


def update_compass() -> None:
    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    if (
        compass["map_revision"] == 187
        and compass["source_graph_revision"] == 206
        and compass["current_position"]["node_id"] == SPECS[-1]["id"]
    ):
        return
    if (
        compass["map_revision"] != 182
        or compass["source_graph_revision"] != 201
        or compass["current_position"]["node_id"] != PARENT
    ):
        raise SystemExit("Unexpected lifecycle-descendant Compass predecessor.")
    parent = PARENT
    for spec in SPECS:
        plan, closeout = _paths(spec)
        compass["journey"].append(
            {
                "node_id": spec["id"],
                "lineage_parent": parent,
                "strategic_role": spec["role"],
                "outcome": spec["outcome"],
                "evidence": [plan, THREAT, EVIDENCE, closeout, TESTS],
            }
        )
        parent = spec["id"]
    evidence = [
        _paths(SPECS[-1])[0],
        THREAT,
        ADAPTER,
        EVIDENCE,
        _paths(SPECS[-1])[1],
        ACCEPTANCE,
    ]
    compass["current_position"] = {
        "node_id": SPECS[-1]["id"],
        "strategic_role": "Provider-free default-off Office consumer lifecycle adapter",
        "why_now": "The supervised two-host read passed, making navigation, session-loss and replay lifecycle hardening the least-sensitive authorised follow-on.",
        "outcome": "Five provider-free descendants now make repeated delivery inert, reconcile lost sessions, isolate surface authority, expose only sanitized reason counts and extract an unmounted adapter.",
        "unlocks": [
            "Review the five lifecycle results on their stacked draft pull request.",
            "With fresh authority, review a default-off native Diary composition for the same active-practitioner read.",
        ],
        "does_not_solve": [
            "Live Microsoft/provider interoperability or real identity mapping.",
            "Patient/clinical/document access, broader product resources or any command/write.",
            "Distributed abuse resistance, organisational deployment, protected integration, production or release.",
        ],
        "evidence": evidence,
    }
    decisions = {item["id"]: item for item in compass["user_owned_decisions"]}
    reload_decision = decisions[
        "authorize-provider-free-office-directory-reload-reconciliation"
    ]
    reload_decision["required_before"] = (
        "Satisfied on 2026-08-03 under Yuri's authority for five clear provider-free descendants; all five lifecycle results passed without a material fork."
    )
    reload_decision["evidence"] = evidence
    next_id = "authorize-provider-free-native-diary-directory-composition-review"
    if next_id not in decisions:
        compass["user_owned_decisions"].append(
            {
                "id": next_id,
                "question": "Should EMR4 review a default-off native Diary composition for the same active-practitioner read?",
                "required_before": "Fresh Yuri authority is required because the six-tranche Office consumer and lifecycle sequence is now consumed.",
                "evidence": evidence,
            }
        )
    compass["map_limits"].insert(
        0,
        "The five Office lifecycle descendants are provider-free, authored-synthetic, active-practitioner-only and task-scoped; they add no real identity, broader product authority or production wiring.",
    )
    compass["orientation_statement"] = (
        "EMR4's fixed Office active-practitioner consumer now has explicit inert reload/history behaviour, safe expired/revoked-session reconciliation, cross-surface cookie/CSRF/nonce isolation, identifier-free lifecycle counts and a route-free default-off adapter. Continuity 206 / Compass 187 bind all five results. Fresh authority is required before a native Diary composition review; real identity, broader product reads, every write, deployment, production and release remain closed."
    )
    compass["map_revision"] = 187
    compass["source_graph_revision"] = 206
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
