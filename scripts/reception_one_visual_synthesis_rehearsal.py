"""Run the isolated Reception One Vertex design-synthesis lifecycle."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import ariadne_vertex_sydney_gemini_25_rehearsal as rehearsal
from scripts import reception_one_visual_synthesis_contracts as contracts
from scripts import reception_one_visual_synthesis_launcher as launcher


def main() -> int:
    rehearsal.contracts = contracts
    rehearsal.launcher = launcher
    rehearsal.BROKER_MODULE = "scripts.reception_one_visual_synthesis_broker"
    rehearsal.SCHEMA_VERSION = (
        "ariadne.reception_one_visual_synthesis_isolation_evidence.v1"
    )
    rehearsal.DRY_RESULT = (
        "reception_one_visual_synthesis_real_isolation_dry_run_pass"
    )
    rehearsal.LIVE_PASS = (
        "reception_one_visual_synthesis_vertex_candidate_pass"
    )
    rehearsal.LIVE_FAILED = (
        "reception_one_visual_synthesis_vertex_candidate_revision_required"
    )
    return rehearsal.main()


if __name__ == "__main__":
    raise SystemExit(main())
