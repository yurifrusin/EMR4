from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "scripts"
    / "raisa_provider_free_read_only_waiting_area_movement_command_family_readiness_review.py"
)
BASE = (
    ROOT
    / "orchestration"
    / "continuity"
    / "raisa-provider-free-read-only-waiting-area-movement-command-family-readiness-review"
)


def _module():
    spec = importlib.util.spec_from_file_location("waiting_area_readiness_review", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_review_returns_exact_fail_closed_matrix_without_app_import() -> None:
    before = set(sys.modules)
    evidence = _module().run_review()
    imported = set(sys.modules) - before

    assert evidence["result"].endswith("_pass")
    assert evidence["verdict"] == "waiting_area_command_family_not_ready"
    assert evidence["dimension_counts"] == {"satisfied": 5, "blocking_gap": 7}
    assert [item["order"] for item in evidence["dimensions"]] == list(range(1, 13))
    assert evidence["hostile_mutations_rejected"] == 76
    assert not any(name == "app" or name.startswith("app.") for name in imported)
    assert not any(evidence["closed_boundaries"].values())


def test_review_preserves_three_way_non_overlap_and_narrow_successor() -> None:
    evidence = _module().run_review()

    assert evidence["non_overlap"] == {
        "check_in": "booked_to_arrived_plus_initial_waiting_area_only_and_existing_area_move_rejected",
        "general_status": "status_transition_and_accepted_transition_side_effects_only",
        "waiting_area_movement": "waiting_area_id_only_with_status_and_arrival_unchanged",
    }
    assert evidence["next_tranche"] == (
        "raisa-provider-free-unmounted-waiting-area-confirm-command-family-architecture"
    )


def test_command_writes_deterministic_evidence_and_report(tmp_path: Path) -> None:
    evidence_path = tmp_path / "evidence.json"
    report_path = tmp_path / "report.md"
    completed = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--evidence",
            str(evidence_path),
            "--report",
            str(report_path),
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    assert evidence["source_head"] == "11317b69c6fcd0e97a002b4196ec92cc33f47110"
    assert len(evidence["source_bindings"]) == 16
    report = " ".join(report_path.read_text(encoding="utf-8").split())
    assert "Five reusable" in report
    assert "unmounted command-family architecture" in report
