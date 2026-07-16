"""Run the single sealed LC4V9 certification attempt."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services.bernie.lc4v9_certification_evaluator import evaluate
from app.services.bernie.lc4v9_content_blind_framework import run_certification


def main() -> int:
    outcome = run_certification(
        attempt_id="lc4v9-fresh-certification-001",
        fixture_path="tests/fixtures/bernie_lc4v9_fresh_certification.json",
        framework_path="app/services/bernie/lc4v9_content_blind_framework.py",
        evaluator=evaluate,
        threshold_path="tests/fixtures/bernie_lc4v9_thresholds.json",
        manifest_path="orchestration/agent_inbox/codex/lc4v9-source-manifest.json",
        seal_path="orchestration/agent_inbox/codex/lc4v9-seal.json",
        marker_path="orchestration/agent_inbox/codex/lc4v9-attempt-marker.json",
        report_path="orchestration/agent_inbox/codex/lc4v9-aggregate-report.json",
        repository_root=str(ROOT),
    )
    print(json.dumps(outcome.__dict__, sort_keys=True))
    return 0 if outcome.decision != "certification_invalid" else 2


if __name__ == "__main__":
    raise SystemExit(main())
