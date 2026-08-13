from __future__ import annotations

from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs/raisa-post-status-action-compass-baton-orientation-plan.md"


def test_plan_freezes_truth_parity_orientation_without_product_authority() -> None:
    text = PLAN.read_text(encoding="utf-8")
    head = "\n".join(text.splitlines()[:16])
    assert "Date: 2026-08-13" in head
    assert "Timestamp: 2026-08-13T" in head
    assert "+10:00 (Australia/Brisbane)" in head
    assert "Reasoning level: Extra High" in text
    for phrase in (
        "**truth\n  parity**",
        "not yet feature parity",
        "kernel, not any visual",
        "projection-neutral truth-parity contract",
        "another already-existing Diary command",
        "representative Stage 3B",
        "external patient channel",
        "another event family",
        "general visual polish",
        "No product behavior, FastAPI, GraphQL, OpenAPI, database",
    ):
        assert phrase in text


def test_exact_accepted_orientation_source_remains_in_current_lineage() -> None:
    result = subprocess.run(
        [
            "git",
            "merge-base",
            "--is-ancestor",
            "4b6a060c6b1aab42e1062c41d48d109f683abe00",
            "HEAD",
        ],
        cwd=ROOT,
        check=False,
    )
    assert result.returncode == 0
