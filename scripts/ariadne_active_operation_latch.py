"""Validate the durable Ariadne operation latch and interruption decision."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from orchestration_harness.active_operation import (
    PROMPT_CLASSES,
    assess_interruption,
    validate_active_operation,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_STATE = (
    REPO_ROOT
    / "orchestration"
    / "continuity"
    / "ariadne-active-operation-latch"
    / "current.json"
)


def _load(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate Ariadne unfinished-operation precedence."
    )
    parser.add_argument("--state", type=Path, default=DEFAULT_STATE)
    parser.add_argument(
        "--prompt-class", choices=sorted(PROMPT_CLASSES), default="none"
    )
    parser.add_argument("--terminal-intent", action="store_true")
    args = parser.parse_args()
    try:
        latch = validate_active_operation(_load(args.state))
        decision = assess_interruption(
            latch,
            prompt_class=args.prompt_class,
            terminal_intent=args.terminal_intent,
        )
    except (OSError, json.JSONDecodeError, ValueError) as error:
        print(f"ariadne active-operation latch failed: {error}", file=sys.stderr)
        return 2
    print(json.dumps(decision, indent=2, sort_keys=True))
    return 0 if decision["status"] == "passed" else 2


if __name__ == "__main__":
    raise SystemExit(main())
