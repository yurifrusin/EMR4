"""Read-only inspection of local Deep Code notify events."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="List local Deep Code mailbox events.")
    parser.add_argument("--outbox", type=Path, default=Path("local_data/ariadne-harness/deepcode-outbox"))
    parser.add_argument("--event", type=Path, help="Print one local event, including its untrusted body.")
    args = parser.parse_args()
    if args.event:
        print(args.event.read_text(encoding="utf-8"))
        return 0
    events = []
    if args.outbox.is_dir():
        for path in sorted(args.outbox.glob("*.json")):
            payload = json.loads(path.read_text(encoding="utf-8"))
            events.append({
                "path": str(path),
                "recorded_at": payload.get("recorded_at"),
                "status": payload.get("status"),
                "duration_seconds": payload.get("duration_seconds"),
                "title": payload.get("title"),
            })
    print(json.dumps({"schema_version": "ariadne.deepcode_mailbox_index.v1", "events": events}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
