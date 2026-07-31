from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COMPASS = ROOT / "orchestration" / "continuity" / "emr4-compass.json"
NODE_ID = "raisa-dual-host-foundation"


def main() -> int:
    data = json.loads(COMPASS.read_text(encoding="utf-8"))
    if data["map_revision"] != 152 or data["source_graph_revision"] != 171:
        raise SystemExit("Unexpected Compass predecessor revision.")
    if data["journey"][-1]["node_id"] != NODE_ID:
        raise SystemExit("Unexpected Compass journey predecessor.")

    evidence = [
        "docs/raisa-dual-host-foundation-plan.md",
        "docs/security/raisa-dual-host-foundation-threat-model-delta.md",
        "orchestration/continuity/raisa-dual-host-foundation/feature-inventory.json",
        "orchestration/continuity/raisa-dual-host-foundation/host-profile-matrix-evidence.json",
        "orchestration/continuity/raisa-dual-host-foundation/final-residue-evidence.json",
        "docs/raisa-dual-host-foundation-closeout.md",
        "orchestration/agent_inbox/codex/raisa-dual-host-foundation-sol-acceptance.md",
        "tests/test_raisa_dual_host_foundation.py",
    ]
    data["journey"][-1] = {
        "node_id": NODE_ID,
        "lineage_parent": "reception-one-word-desktop-authenticated-dialog-check",
        "strategic_role": (
            "Accepted provider-free shared Word host foundation, integrated "
            "Reception One direction and cloud-first delivery direction"
        ),
        "outcome": (
            "One pure immutable capability profile now underlies the "
            "clinician and Reception One taskpane surfaces without granting "
            "data or action authority. The earlier clinician and scribe paths "
            "are explicitly inventoried; Reception One is one role-scoped "
            "domain for staff, doctors and future online-booking and Rayleen "
            "surfaces; and cloud-first practice management as a service is "
            "the primary delivery direction, with any future local model "
            "restricted to a subordinate edge."
        ),
        "evidence": evidence,
    }
    data["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": (
            "Accepted provider-free shared Word host foundation, integrated "
            "Reception One direction and cloud-first delivery direction"
        ),
        "why_now": (
            "The installed-Word Reception One proof established the real "
            "desktop route, while the earlier clinician taskpane and scribe "
            "paths and the Word Online platform gap still needed one explicit "
            "host-neutral capability boundary before further product work."
        ),
        "outcome": (
            "The Word add-in now constructs one deeply immutable desktop, "
            "web, mobile or unknown host profile without invoking observed "
            "capabilities. It keeps host readiness separate from product "
            "authority, preserves existing Reception One contracts, and "
            "records one integrated reception domain spanning role-scoped "
            "staff, doctor and future patient surfaces. Cloud-first practice "
            "management as a service is the primary delivery direction, with "
            "any future local model restricted to a subordinate edge."
        ),
        "unlocks": [
            (
                "Incremental migration of clinician operations behind one "
                "tested host-neutral boundary."
            ),
            (
                "A consistent Reception One contract family for staff, doctor "
                "and future patient-facing online booking and Rayleen arrival "
                "surfaces."
            ),
            (
                "A cloud-first practice service in which Word and web clients "
                "share practice-scoped contracts without extensive local setup."
            ),
            (
                "Separate desktop and web evidence for each future capability "
                "without conflating technical support with authorization."
            ),
        ],
        "does_not_solve": [
            "Authenticated Word Online execution or its localhost platform gate.",
            "Microphone capture, medical-scribe correctness or Access AI migration.",
            (
                "Safety for real, product-derived, patient, health, clinical "
                "or historical data."
            ),
            (
                "Online booking, patient identity proofing, Rayleen arrival "
                "registration or any patient-facing write."
            ),
            (
                "Provider interpretation, clinical action, appointment "
                "command, production, deployment or release."
            ),
            (
                "Public adoption of Raisa or Clinician One, artwork, domain, "
                "ASIC or trade-mark action."
            ),
            (
                "Cloud tenancy, infrastructure, data residency, deployment, "
                "billing, production or a local-model edge."
            ),
        ],
        "evidence": evidence,
    }

    decision_id = "adopt-raisa-public-brand"
    if not any(item["id"] == decision_id for item in data["user_owned_decisions"]):
        data["user_owned_decisions"].insert(
            0,
            {
                "id": decision_id,
                "question": (
                    "Should Raisa become the public master brand and Clinician "
                    "One the public clinician-workspace name?"
                ),
                "required_before": (
                    "Any public manifest or UI rename, artwork publication, "
                    "domain purchase, ASIC registration, trade-mark action or release."
                ),
                "evidence": [
                    "docs/raisa-dual-host-foundation-plan.md",
                    "docs/raisa-dual-host-foundation-closeout.md",
                ],
            },
        )

    data["map_limits"][0] = (
        "The accepted Raisa dual-host foundation proves only a pure "
        "repository-local Office capability profile, source/published "
        "integration and authored fixture/browser/build evidence. Its "
        "cloud-first and integrated-reception statements are architecture "
        "direction, not cloud resource, tenancy, data-residency, local-model, "
        "patient-client or deployment authority. It does not prove "
        "authenticated Word Online, microphone or scribe behavior, "
        "patient-facing online booking or Rayleen, live backend or provider "
        "authorization, public branding, production, deployment or release."
    )
    data["map_revision"] = 153
    data["source_graph_revision"] = 172
    data["updated_at"] = "2026-07-31T06:45:00Z"
    COMPASS.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
