"""Send a compact non-PHI Pushover notification for an EMR4 sprint closeout."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.notify_yuri import main as notify_yuri_main


def build_closeout_message(
    *, sprint: str, checks: str, engine_state: str, next_or_reason: str
) -> str:
    state_label = "continuing with" if engine_state == "continuing" else "paused for"
    return (
        f"{sprint} closed. Checks: {checks}. Sprint engine {state_label} "
        f"{next_or_reason}. Open Codex for details."
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sprint", required=True, help="Short non-sensitive sprint name.")
    parser.add_argument("--checks", required=True, help="Compact verification summary.")
    state = parser.add_mutually_exclusive_group(required=True)
    state.add_argument("--continuing", metavar="NEXT", help="Brief next sprint or workstream.")
    state.add_argument("--paused", metavar="REASON", help="Concrete reason the engine paused.")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    engine_state = "continuing" if args.continuing is not None else "paused"
    next_or_reason = args.continuing if args.continuing is not None else args.paused
    notify_args = [
        "--provider",
        "pushover",
        "--title",
        "EMR4 sprint closeout",
        "--message",
        build_closeout_message(
            sprint=args.sprint,
            checks=args.checks,
            engine_state=engine_state,
            next_or_reason=next_or_reason,
        ),
    ]
    if args.dry_run:
        notify_args.append("--dry-run")
    return notify_yuri_main(notify_args)


if __name__ == "__main__":
    raise SystemExit(main())
