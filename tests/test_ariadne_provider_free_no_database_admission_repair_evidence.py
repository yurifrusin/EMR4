from __future__ import annotations

import json
from pathlib import Path

from scripts.ariadne_provider_free_no_database_manifest_runner_admission_repair import (
    build_evidence,
)


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "orchestration/continuity/ariadne-provider-free-no-database-manifest-runner-admission-repair"


def test_deterministic_no_database_evidence_is_exact() -> None:
    stored = json.loads(
        (BASE / "provider-free-no-database-admission-evidence.json").read_text(
            encoding="utf-8"
        )
    )
    assert build_evidence(ROOT) == stored
    assert stored["status"] == "passed"
    assert stored["hostile_mutations"] == {
        "named": 128,
        "rejected": 128,
        "escaped": [],
    }
    assert set(stored["invocations"].values()) == {0}
