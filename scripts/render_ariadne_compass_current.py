#!/usr/bin/env python3
"""Render the validated current Ariadne Compass report as UTF-8 Markdown."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import ariadne_compass as compass
from scripts import ariadne_continuity as continuity


DEFAULT_OUTPUT = ROOT / "docs" / "ariadne-compass-current.md"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    graph = continuity.load_json(
        continuity.default_graph_path(ROOT),
        label="graph",
    )
    current = compass._load_object(
        compass.default_compass_path(ROOT),
        label="compass",
    )
    report = compass.build_compass_report(current, graph, repo_root=ROOT)
    if report["status"] != "passed":
        return 2
    args.output.write_text(
        compass.render_markdown(report),
        encoding="utf-8",
        newline="\n",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
