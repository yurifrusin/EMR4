#!/usr/bin/env python3
"""Generate the distinct provider-blocked gate for Bureau retry 002."""

from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import (  # noqa: E402
    reception_one_bureau_cost_bounded_provider_blocked as predecessor,
)


OUTPUT = (
    ROOT
    / "orchestration"
    / "continuity"
    / "reception-one-bureau-cost-bounded-occupied-retry-002"
    / "provider-blocked-evidence.json"
)
GRAPH_REVISION = 164
COMPASS_REVISION = 145


def main() -> int:
    predecessor.OUTPUT = OUTPUT
    predecessor.GRAPH_REVISION = GRAPH_REVISION
    predecessor.COMPASS_REVISION = COMPASS_REVISION
    return predecessor.main()


if __name__ == "__main__":
    raise SystemExit(main())
