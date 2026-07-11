"""Deep Code notify-hook entry point. Writes local ignored outbox events only."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from orchestration_harness.deepcode_mailbox import write_notify_event


def main() -> int:
    parser = argparse.ArgumentParser(description="Persist one local Deep Code notify event.")
    parser.add_argument("--outbox", type=Path, required=True)
    args = parser.parse_args()
    try:
        write_notify_event(outbox=args.outbox)
    except (OSError, ValueError) as error:
        print(f"deepcode notify event failed: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
