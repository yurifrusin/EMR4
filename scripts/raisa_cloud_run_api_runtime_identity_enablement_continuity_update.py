from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GRAPH = ROOT / "orchestration" / "continuity" / "emr4-continuity-graph.json"
COMPASS = ROOT / "orchestration" / "continuity" / "emr4-compass.json"
NODE_ID = "raisa-cloud-run-api-runtime-identity-enablement"
PARENT_ID = "raisa-cloud-run-public-https-dev-host-readiness"
UPDATED_AT = "2026-07-31T08:26:36Z"


def update_graph() -> None:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] != 176:
        raise SystemExit("Unexpected continuity graph predecessor revision.")
    if any(node["id"] == NODE_ID for node in graph["nodes"]):
        raise SystemExit("Continuity node already exists.")

    graph["nodes"].append(
        {
            "id": NODE_ID,
            "title": "Raisa Cloud Run API and Runtime Identity Enablement",
            "kind": "integration",
            "status": "accepted",
            "created_at": UPDATED_AT,
            "updated_at": UPDATED_AT,
            "coordinates": {
                "git_ref": "codex/ariadne-terra-gemini-comparative-rehearsal",
                "source_head": "5b1ea7952fb08eea333da0e63f166d3895ccea32",
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
                "authorized_openings": [
                    {
                        "boundary": "api-change",
                        "scope": (
                            "Enable exactly run.googleapis.com and "
                            "artifactregistry.googleapis.com in bernie-emr4-dev; "
                            "create exactly the dedicated Raisa runtime service "
                            "account with zero project roles; then repeat read-only "
                            "Sydney resource checks."
                        ),
                        "source": (
                            "docs/raisa-cloud-run-api-runtime-identity-enablement-plan.md"
                        ),
                    }
                ],
                "notes": [
                    (
                        "Yuri explicitly authorised the two API enablements, the "
                        "exact zero-project-role runtime identity and repeated "
                        "read-only resource checks."
                    ),
                    (
                        "Repository creation, Cloud Run service creation, public "
                        "IAM, image push and deployment remained closed."
                    ),
                    (
                        "Provider, backend, patient data, production and release "
                        "remained closed."
                    ),
                ],
            },
            "decisions": [
                {
                    "id": "accept-raisa-cloud-run-api-runtime-identity-177",
                    "source": (
                        "docs/raisa-cloud-run-api-runtime-identity-enablement-plan.md"
                    ),
                    "status": "accepted",
                    "summary": (
                        "Accept the exact two API enablements and dedicated "
                        "zero-project-role runtime identity; retain the repository "
                        "and service creation boundary."
                    ),
                }
            ],
            "claim_scope": [
                (
                    "Cloud Run Admin and Artifact Registry APIs are enabled in "
                    "bernie-emr4-dev."
                ),
                (
                    "The exact dedicated Raisa runtime identity exists, is active, "
                    "has zero project roles and has no user-managed key."
                ),
                (
                    "The repeated read-only Sydney checks establish that the "
                    "frozen Artifact Registry repository and Cloud Run service "
                    "are absent."
                ),
                (
                    "No repository, service, image, public invoker binding or "
                    "deployment was created."
                ),
            ],
            "contract_evidence": [
                {
                    "contract_id": "combined-patient-practitioner-time-duration-intent",
                    "status": "satisfied",
                    "evidence": [
                        (
                            "orchestration/continuity/"
                            "raisa-cloud-run-api-runtime-identity-enablement/evidence.json"
                        ),
                        "tests/test_raisa_cloud_run_api_runtime_identity_enablement.py",
                    ],
                    "note": (
                        "The control-plane change contains no appointment data, "
                        "proposal, confirmation or command."
                    ),
                },
                {
                    "contract_id": "committed-reschedule-availability-reconciliation",
                    "status": "satisfied",
                    "evidence": [
                        (
                            "docs/raisa-cloud-run-api-runtime-identity-enablement-"
                            "closeout.md"
                        ),
                        "tests/test_raisa_cloud_run_api_runtime_identity_enablement.py",
                    ],
                    "note": (
                        "No backend, database, event, availability or Diary path "
                        "was contacted or changed."
                    ),
                },
            ],
            "evidence": {
                "plans": [
                    "docs/raisa-cloud-run-api-runtime-identity-enablement-plan.md",
                    "docs/raisa-cloud-run-public-https-dev-host-operator-packet.md",
                ],
                "findings": [
                    (
                        "orchestration/continuity/"
                        "raisa-cloud-run-api-runtime-identity-enablement/evidence.json"
                    )
                ],
                "closeouts": [
                    (
                        "docs/raisa-cloud-run-api-runtime-identity-enablement-"
                        "closeout.md"
                    )
                ],
                "acceptances": [
                    (
                        "orchestration/agent_inbox/codex/"
                        "raisa-cloud-run-api-runtime-identity-enablement-sol-"
                        "acceptance.md"
                    )
                ],
                "receipts": [
                    (
                        "orchestration/agent_inbox/codex/"
                        "raisa-cloud-run-api-runtime-identity-enablement-receipt.json"
                    )
                ],
                "tests": [
                    "tests/test_raisa_cloud_run_api_runtime_identity_enablement.py"
                ],
            },
            "unresolved_gates": [
                (
                    "The Sydney Artifact Registry repository raisa-office-web-dev "
                    "is absent and requires separate creation authority."
                ),
                (
                    "The Sydney Cloud Run service raisa-office-web-dev is absent; "
                    "image push, service creation, public IAM and deployment remain "
                    "separately closed."
                ),
                (
                    "Authenticated Word Online behavior, Office identity and "
                    "clinician-role authorization remain unproven."
                ),
                (
                    "Real, product-derived, patient, health, clinical and "
                    "historical data remain closed."
                ),
                (
                    "Provider, backend, database, microphone, document write, "
                    "production and release remain closed."
                ),
            ],
        }
    )
    graph["graph_revision"] = 177
    graph["updated_at"] = UPDATED_AT
    GRAPH.write_text(
        json.dumps(graph, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def update_compass() -> None:
    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    if compass["map_revision"] != 157 or compass["source_graph_revision"] != 176:
        raise SystemExit("Unexpected Compass predecessor revision.")
    if compass["journey"][-1]["node_id"] != PARENT_ID:
        raise SystemExit("Unexpected Compass journey predecessor.")

    evidence = [
        "docs/raisa-cloud-run-api-runtime-identity-enablement-plan.md",
        (
            "orchestration/continuity/"
            "raisa-cloud-run-api-runtime-identity-enablement/evidence.json"
        ),
        "docs/raisa-cloud-run-api-runtime-identity-enablement-closeout.md",
        (
            "orchestration/agent_inbox/codex/"
            "raisa-cloud-run-api-runtime-identity-enablement-sol-acceptance.md"
        ),
    ]
    compass["journey"].append(
        {
            "node_id": NODE_ID,
            "lineage_parent": PARENT_ID,
            "strategic_role": (
                "Accepted minimal Cloud Run API and zero-role runtime identity "
                "foundation"
            ),
            "outcome": (
                "The two exact Google Cloud APIs are enabled and the dedicated "
                "Raisa runtime identity exists with zero project roles and no "
                "user-managed key. The repeated read-only check establishes that "
                "the frozen Sydney repository and Cloud Run service are absent."
            ),
            "evidence": evidence,
        }
    )
    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": (
            "Accepted minimal Cloud Run API and zero-role runtime identity "
            "foundation"
        ),
        "why_now": (
            "The repository-local public host was ready, and the authorised "
            "preflight found two disabled APIs and a missing runtime identity. "
            "Yuri authorised exactly those prerequisites and a repeated read-only "
            "resource check."
        ),
        "outcome": (
            "Both APIs are enabled, the dedicated identity is active with zero "
            "project roles and no user-managed key, and both frozen Sydney "
            "resources are authoritatively absent. No repository, service, image, "
            "public IAM binding or deployment exists from this tranche."
        ),
        "unlocks": [
            (
                "A separately authorised creation of the exact Docker-format "
                "Sydney Artifact Registry repository."
            ),
            (
                "A separately authorised immutable image push and bounded public "
                "Cloud Run development deployment."
            ),
            (
                "After deployment verification, one supervised authenticated "
                "Word Online authored-synthetic check."
            ),
        ],
        "does_not_solve": [
            "Artifact Registry repository or Cloud Run service creation.",
            "Image push, revision deployment or public invocation.",
            "Organisation-policy or public-IAM compatibility.",
            "Authenticated Word Online interoperability or Office identity.",
            "Clinician-role authorization or production document grants.",
            (
                "Safety for real, product-derived, patient, health, clinical or "
                "historical text."
            ),
            "Microsoft or Google physical or sovereign processing location.",
            "Provider, backend, database, microphone, command or document write.",
            "Production or release readiness.",
        ],
        "evidence": evidence,
    }

    deployment_item = next(
        (
            item
            for item in compass["decision_horizon"]
            if item["id"] == "authorize-raisa-cloud-run-public-https-dev-host-deployment"
        ),
        None,
    )
    if deployment_item is None:
        raise SystemExit("Expected Cloud Run deployment decision is missing.")
    deployment_item.update(
        {
            "status": "candidate",
            "strategic_question": (
                "Should an authorised operator now create the frozen Sydney "
                "repository and public Cloud Run development service, push the "
                "immutable image and deploy it?"
            ),
            "why_it_matters": (
                "The required APIs and zero-role runtime identity are ready, and "
                "the exact repository and service are confirmed absent. Creating "
                "them, granting public static invocation and deploying the image "
                "would be the next external and potentially billable boundary."
            ),
            "prerequisites": [
                (
                    "Obtain explicit authority for the exact repository, image "
                    "push, Cloud Run service, public invoker binding and deployment."
                ),
                (
                    "Use project bernie-emr4-dev, region australia-southeast1, "
                    "service and repository raisa-office-web-dev, and the existing "
                    "dedicated zero-project-role runtime identity."
                ),
                (
                    "Keep authored-synthetic, backend-free, provider-free, "
                    "credential-free, no-write and non-production boundaries."
                ),
                (
                    "Deploy an immutable digest with min zero, max one and no "
                    "secret, VPC, volume or custom domain."
                ),
                (
                    "Repeat post-deployment runtime identity, public IAM, route, "
                    "browser and cleanup gates before Word Online use."
                ),
            ],
            "boundary_changes": [
                "api-change",
                "deployment",
            ],
            "evidence": evidence,
        }
    )
    compass["map_limits"].insert(
        0,
        (
            "The API and runtime-identity descendant proves only that the two "
            "exact services are enabled, the dedicated runtime identity has zero "
            "project roles and no user-managed key, and the frozen Sydney "
            "repository and service are absent. It does not prove deployment, "
            "public IAM compatibility, authenticated Word Online behavior, "
            "processing geography, real-data safety, production or release."
        ),
    )
    compass["map_revision"] = 158
    compass["source_graph_revision"] = 177
    compass["updated_at"] = UPDATED_AT
    COMPASS.write_text(
        json.dumps(compass, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    update_graph()
    update_compass()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
