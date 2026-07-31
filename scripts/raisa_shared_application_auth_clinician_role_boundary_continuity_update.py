from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GRAPH = ROOT / "orchestration" / "continuity" / "emr4-continuity-graph.json"
COMPASS = ROOT / "orchestration" / "continuity" / "emr4-compass.json"
NODE_ID = "raisa-shared-application-auth-clinician-role-boundary"
PARENT_ID = "raisa-word-online-authenticated-companion-verification"
UPDATED_AT = "2026-07-31T12:30:00Z"
SOURCE_HEAD = "8fa732592fbee4f57c322b13d9d8ff89fcc7fa33"

PLAN = "docs/raisa-shared-application-auth-clinician-role-boundary-plan.md"
DESIGN = "docs/raisa-shared-application-auth-clinician-role-boundary-design.md"
THREAT_MODEL = (
    "docs/security/"
    "raisa-shared-application-auth-clinician-role-boundary-threat-model-delta.md"
)
POLICY = (
    "orchestration/continuity/"
    "raisa-shared-application-auth-clinician-role-boundary/"
    "auth-boundary-policy.json"
)
CASES = (
    "orchestration/continuity/"
    "raisa-shared-application-auth-clinician-role-boundary/"
    "acceptance-cases.json"
)
EVIDENCE = (
    "orchestration/continuity/"
    "raisa-shared-application-auth-clinician-role-boundary/"
    "provider-free-acceptance-evidence.json"
)
CLOSEOUT = (
    "docs/raisa-shared-application-auth-clinician-role-boundary-closeout.md"
)
ACCEPTANCE = (
    "orchestration/agent_inbox/codex/"
    "raisa-shared-application-auth-clinician-role-boundary-sol-acceptance.md"
)
REHYDRATION_RECEIPT = (
    "orchestration/agent_inbox/codex/"
    "raisa-shared-application-auth-clinician-role-boundary-"
    "rehydration-receipt.json"
)
PREACCEPTANCE_RECEIPT = (
    "orchestration/agent_inbox/codex/"
    "raisa-shared-application-auth-clinician-role-boundary-"
    "preacceptance-receipt.json"
)
TEST = "tests/test_raisa_shared_application_auth_boundary.py"


def _write(path: Path, value: dict) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def update_graph() -> None:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] != 180:
        raise SystemExit("Unexpected continuity graph predecessor revision.")
    if any(node["id"] == NODE_ID for node in graph["nodes"]):
        raise SystemExit("Continuity node already exists.")

    graph["nodes"].append(
        {
            "id": NODE_ID,
            "title": (
                "Raisa Shared Application Authentication and Clinician-Role "
                "Boundary"
            ),
            "kind": "foundation",
            "status": "accepted",
            "created_at": UPDATED_AT,
            "updated_at": UPDATED_AT,
            "coordinates": {
                "git_ref": "codex/ariadne-terra-gemini-comparative-rehearsal",
                "source_head": SOURCE_HEAD,
                "thread_id": None,
                "worktree_role": "integration",
            },
            "relationships": [
                {
                    "node_id": PARENT_ID,
                    "relation": "builds_on",
                }
            ],
            "authority": {
                "authorized_openings": [],
                "notes": [
                    (
                        "Yuri authorized the repository-local, provider-free "
                        "shared architecture defined in " + PLAN + "."
                    ),
                    (
                        "No runtime authentication, identity-provider, cloud, "
                        "IAM, deployment or production change was authorized."
                    ),
                    (
                        "Provider calls, product-derived data, clinical "
                        "authority, database reads or writes, appointment "
                        "commands, microphone capture and document mutation "
                        "remained closed."
                    ),
                    (
                        "Microsoft or Office identity is explicitly separate "
                        "from EMR4 application authority."
                    ),
                ],
            },
            "decisions": [
                {
                    "id": "accept-shared-backend-auth-boundary-181",
                    "source": POLICY,
                    "status": "accepted",
                    "summary": (
                        "Accept one backend-owned identity, session, clinician "
                        "role, practice-scope and required-audit decision across "
                        "all three surfaces."
                    ),
                },
                {
                    "id": "accept-bound-cross-surface-session-exchange-181",
                    "source": THREAT_MODEL,
                    "status": "accepted",
                    "summary": (
                        "Accept an opaque server-side session model and a "
                        "short-lived single-use origin, audience, state, nonce, "
                        "generation and PKCE-bound exchange without bearer or "
                        "clinical payload transport."
                    ),
                },
                {
                    "id": "keep-auth-runtime-and-product-reads-closed-181",
                    "source": CLOSEOUT,
                    "status": "accepted",
                    "summary": (
                        "Keep runtime authentication, external identity, product "
                        "reads, clinical authority, persistence, deployment, "
                        "production and release outside this architecture pass."
                    ),
                },
            ],
            "claim_scope": [
                (
                    "One typed backend-owned clinician-read policy is equivalent "
                    "across desktop Word, Word Online and the native Diary."
                ),
                (
                    "Microsoft or Office sign-in and client role, practice, "
                    "document or host claims cannot create or modify authority."
                ),
                (
                    "The initial clinician-read rule requires a fresh active GP, "
                    "an active same-practice practitioner link, same-practice "
                    "resource scope, current sessions and successful required "
                    "audit before data access."
                ),
                (
                    "Twenty-three authorization and thirteen cross-surface "
                    "exchange cases pass with all external and product side "
                    "effect counts zero."
                ),
            ],
            "contract_evidence": [
                {
                    "contract_id": (
                        "combined-patient-practitioner-time-duration-intent"
                    ),
                    "status": "satisfied",
                    "evidence": [POLICY, EVIDENCE, TEST],
                    "note": (
                        "The architecture adds no proposal, confirmation or "
                        "command authority; every later protected operation "
                        "must re-enter the same backend authorization boundary."
                    ),
                },
                {
                    "contract_id": (
                        "committed-reschedule-availability-reconciliation"
                    ),
                    "status": "satisfied",
                    "evidence": [DESIGN, EVIDENCE, CLOSEOUT],
                    "note": (
                        "No backend, database, committed event or Diary truth "
                        "path ran or changed in this architecture-only tranche."
                    ),
                },
            ],
            "evidence": {
                "plans": [PLAN, DESIGN, THREAT_MODEL],
                "findings": [POLICY, CASES, EVIDENCE],
                "closeouts": [CLOSEOUT],
                "acceptances": [ACCEPTANCE],
                "receipts": [REHYDRATION_RECEIPT, PREACCEPTANCE_RECEIPT],
                "tests": [TEST],
            },
            "unresolved_gates": [
                (
                    "No live EMR4 application session, secure cookie, "
                    "database-backed revocation or required-audit persistence "
                    "has been implemented."
                ),
                (
                    "External identity-provider and Microsoft or Office "
                    "federation remain unselected and unauthorized."
                ),
                (
                    "Product-derived, patient, health, clinical and historical "
                    "reads remain closed."
                ),
                (
                    "Database writes, appointment commands, microphone capture, "
                    "document mutation, organisational Office deployment, "
                    "production and release remain closed."
                ),
            ],
        }
    )
    graph["graph_revision"] = 181
    graph["updated_at"] = UPDATED_AT
    _write(GRAPH, graph)


def update_compass() -> None:
    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    if (
        compass["map_revision"] != 161
        or compass["source_graph_revision"] != 180
    ):
        raise SystemExit("Unexpected Compass predecessor revision.")

    evidence = [PLAN, DESIGN, THREAT_MODEL, POLICY, EVIDENCE, CLOSEOUT]
    strategic_role = (
        "Shared backend-owned application-authentication and clinician-role "
        "architecture"
    )
    outcome = (
        "Desktop Word, Word Online and the native Diary now share one frozen "
        "EMR4-backend authorization contract with separate Office identity, "
        "opaque bounded sessions, centralized revocation, short-lived "
        "cross-surface exchange, required audit and fail-closed semantics. The "
        "result is provider-free architecture evidence only; runtime and "
        "product reads remain closed."
    )
    compass["journey"].append(
        {
            "node_id": NODE_ID,
            "lineage_parent": PARENT_ID,
            "strategic_role": strategic_role,
            "outcome": outcome,
            "evidence": evidence,
        }
    )
    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": strategic_role,
        "why_now": (
            "The accepted Word Online companion proved the final bounded "
            "provider-free dual-host interaction, but explicitly left EMR4 "
            "application identity and clinician authorization unproven. Yuri "
            "authorized this architecture boundary before any product-derived "
            "read."
        ),
        "outcome": outcome,
        "unlocks": [
            (
                "Review a separately authorized server-side implementation of "
                "the frozen session, revocation, exchange and audit primitives "
                "using authored-synthetic test state only."
            ),
            (
                "Use the same backend decision contract when later evaluating "
                "desktop Word, Word Online and native Diary integration."
            ),
            (
                "Retire localStorage bearer transport and client-decoded role "
                "claims before any product-derived read can be considered."
            ),
        ],
        "does_not_solve": [
            "Live EMR4 login, secure cookies or database-backed revocation.",
            "External identity-provider or Microsoft/Office federation.",
            (
                "Safety or authority for product-derived, patient, health, "
                "clinical or historical data."
            ),
            (
                "Database writes, appointment commands, microphone capture or "
                "document mutation."
            ),
            "Organisational Office deployment, production or release readiness.",
        ],
        "evidence": evidence,
    }

    runtime_decision = {
        "id": "authorize-shared-application-auth-runtime-foundation",
        "question": (
            "Should EMR4 implement the frozen backend-owned session, revocation, "
            "cross-surface exchange and required-audit primitives using only "
            "authored-synthetic test state while product reads remain closed?"
        ),
        "required_before": (
            "Any runtime session or revocation persistence, authentication "
            "cookie, Word-to-Diary session exchange endpoint, required-audit "
            "write, external identity integration or product-derived read."
        ),
        "evidence": [PLAN, DESIGN, THREAT_MODEL, CLOSEOUT],
    }
    if not any(
        item["id"] == runtime_decision["id"]
        for item in compass["user_owned_decisions"]
    ):
        compass["user_owned_decisions"].append(runtime_decision)

    horizon = {
        "id": "shared-application-auth-runtime-foundation",
        "title": "Shared application-authentication runtime foundation",
        "status": "candidate",
        "strategic_question": runtime_decision["question"],
        "why_it_matters": (
            "No product-derived read can safely open until every surface uses "
            "one revocable backend session and clinician-role decision with "
            "required audit."
        ),
        "prerequisites": [
            "Fresh Yuri authority naming the exact repository-local runtime scope.",
            (
                "Authored-synthetic test identities and resources only; no "
                "product or patient data."
            ),
            (
                "No external identity provider, cloud/IAM, deployment or "
                "production change."
            ),
            (
                "Secure server-side session, revocation, exchange, audit and "
                "failure-closure acceptance before any surface integration."
            ),
        ],
        "boundary_changes": ["api-change"],
        "evidence": [PLAN, DESIGN, THREAT_MODEL, CLOSEOUT],
    }
    if not any(
        item["id"] == horizon["id"] for item in compass["decision_horizon"]
    ):
        compass["decision_horizon"].insert(0, horizon)

    compass["map_limits"].insert(
        0,
        (
            "The shared application-authentication descendant proves one "
            "provider-free typed backend authorization architecture across "
            "desktop Word, Word Online and the native Diary. It does not prove "
            "a live session, revocation store, external identity integration, "
            "product-derived read, real-data safety, deployment, production or "
            "release."
        ),
    )
    compass["orientation_statement"] = (
        "Raisa now has an accepted provider-free shared application-"
        "authentication and clinician-role architecture across desktop Word, "
        "Word Online and the native Diary. One EMR4-backend decision owns fresh "
        "identity, role, practice, session, revocation and required-audit checks; "
        "Microsoft or Office identity and client claims confer no application "
        "authority. Twenty-three authorization and thirteen cross-surface "
        "exchange cases pass with zero external or product side effects. "
        "Continuity 181 / Compass 162 bind the result. Runtime authentication, "
        "external identity, product-derived data, writes, deployment, production "
        "and release remain closed."
    )
    compass["map_revision"] = 162
    compass["source_graph_revision"] = 181
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)


def main() -> int:
    update_graph()
    update_compass()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
