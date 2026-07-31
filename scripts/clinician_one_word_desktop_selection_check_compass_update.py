from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COMPASS = ROOT / "orchestration" / "continuity" / "emr4-compass.json"
NODE_ID = "clinician-one-word-desktop-selection-check"
PARENT_ID = "clinician-one-readonly-document-context"


def main() -> int:
    data = json.loads(COMPASS.read_text(encoding="utf-8"))
    if data["map_revision"] != 155 or data["source_graph_revision"] != 174:
        raise SystemExit("Unexpected Compass predecessor revision.")
    if data["journey"][-1]["node_id"] != PARENT_ID:
        raise SystemExit("Unexpected Compass journey predecessor.")

    evidence = [
        "docs/raisa-clinician-one-word-desktop-selection-check-plan.md",
        "docs/security/raisa-clinician-one-word-desktop-selection-check-threat-model-delta.md",
        "orchestration/continuity/clinician-one-word-desktop-selection-check/manifest.xml",
        "orchestration/continuity/clinician-one-word-desktop-selection-check/desktop-selection-evidence.json",
        "orchestration/continuity/clinician-one-word-desktop-selection-check/final-residue-evidence.json",
        "docs/raisa-clinician-one-word-desktop-selection-check-closeout.md",
        "orchestration/agent_inbox/codex/clinician-one-word-desktop-selection-check-sol-acceptance.md",
        "tests/test_clinician_one_word_desktop_selection_check.py",
    ]
    data["journey"].append(
        {
            "node_id": NODE_ID,
            "lineage_parent": PARENT_ID,
            "strategic_role": (
                "Accepted provider-free installed-Word current-selection proof"
            ),
            "outcome": (
                "One disposable ReadDocument-only localhost sideload read one "
                "authored-synthetic exact current selection in installed Word "
                "desktop, emitted only the accepted typed in-memory frame and "
                "counts-only UI, and cleaned up without provider, backend, "
                "credential, microphone, command or write activity."
            ),
            "evidence": evidence,
        }
    )
    data["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": (
            "Accepted provider-free installed-Word current-selection proof"
        ),
        "why_now": (
            "The repository-local adapter and injected host fixtures had "
            "passed, so the next smallest uncertainty was the exact selection "
            "semantics of a real installed Word desktop taskpane."
        ),
        "outcome": (
            "The adapter now has one supervised installed-Word observation: "
            "a single authored-synthetic selection was admitted once, Word's "
            "terminal paragraph marker was preserved transparently, only "
            "typed metadata was displayed and all task-owned residue was "
            "removed. No public host or product authority was added."
        ),
        "unlocks": [
            (
                "A repository-local public-HTTPS development-host contract "
                "for the same compiled Office taskpane and native Diary assets."
            ),
            (
                "A later separately authorised authenticated Word Online "
                "synthetic-only host exercise."
            ),
            (
                "Further clinician context operations that continue to use "
                "explicit, minimal and non-authoritative document grants."
            ),
        ],
        "does_not_solve": [
            "Authenticated Word Online interoperability or Office identity.",
            "Clinician-role authorization or production document grants.",
            (
                "Safety for real, product-derived, patient, health, clinical "
                "or historical text."
            ),
            "Public HTTPS hosting, tenancy, custom domain or deployment.",
            (
                "Provider interpretation, microphone capture, clinical "
                "finalization, document write or any backend command."
            ),
            "Production or release readiness.",
        ],
        "evidence": evidence,
    }
    data["map_limits"][0] = (
        "The accepted Clinician One installed-Word descendant proves one "
        "provider-free authored-synthetic exact-current-selection read through "
        "a disposable local sideload and counts-only release. It does not "
        "prove authenticated Word Online, Office identity, clinician-role "
        "authorization, clinical-data safety, public hosting, provider "
        "readiness, production, deployment or release."
    )
    data["map_revision"] = 156
    data["source_graph_revision"] = 175
    data["updated_at"] = "2026-07-31T06:30:00Z"
    COMPASS.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
