"""Poll a detached Deep Code receipt without owning the worker lifecycle."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path


def wait_for_receipt(receipt: Path, timeout: float = 0, interval: float = 0.5) -> dict:
    deadline = float("inf") if timeout == 0 else time.monotonic() + timeout
    while time.monotonic() < deadline:
        if receipt.is_file():
            payload = json.loads(receipt.read_text(encoding="utf-8"))
            if not isinstance(payload, dict):
                raise ValueError("Deep Code receipt must be a JSON object")
            return payload
        time.sleep(interval)
    raise TimeoutError("receipt wait elapsed; detached worker lifecycle is unchanged")


def main() -> int:
    parser = argparse.ArgumentParser(description="Wait for a detached Deep Code receipt.")
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--timeout", type=float, default=0, help="Wait seconds; 0 waits indefinitely")
    parser.add_argument("--interval", type=float, default=0.5)
    args = parser.parse_args()
    if args.timeout < 0 or args.interval <= 0:
        parser.error("--timeout must be >= 0 and --interval must be > 0")
    try:
        payload = wait_for_receipt(args.receipt.resolve(), args.timeout, args.interval)
    except (OSError, ValueError, json.JSONDecodeError, TimeoutError) as error:
        print(json.dumps({"status": "waiting", "reason": str(error)}))
        return 4
    print(json.dumps(payload, indent=2))
    status = payload.get("status")
    return 0 if status == "completed" else 3 if status == "blocked" else 4


if __name__ == "__main__":
    raise SystemExit(main())
