"""Purpose-built one-use broker for the Reception One design work cell."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import ariadne_vertex_sydney_gemini_25_broker as broker
from scripts import reception_one_visual_synthesis_contracts as contracts


def main() -> int:
    broker.contracts = contracts
    return broker.main()


if __name__ == "__main__":
    raise SystemExit(main())
