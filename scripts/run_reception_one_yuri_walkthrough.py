"""Launch the provider-free Yuri-only Reception One walkthrough locally.

The runner reuses the accepted marker-locked authored-synthetic Reception One
fixture. It starts only IPv6 loopback services, keeps the model provider
disabled, and removes the owned disposable database on exit.
"""

from __future__ import annotations

import argparse
import json
import os
import secrets
import sys
import webbrowser
from urllib.error import URLError
from urllib.request import urlopen

from bernie_reception_one_combined_scope_harness import (
    LOCKED_DATABASE,
    cleanup_database,
    create_database,
    create_schema_and_seed,
    database_readback,
    launch_runtime,
    stop_runtime,
)


LOCAL_DEV_DATABASE_URL = (
    "postgresql://postgres:postgres@127.0.0.1:5434/gp_pms_dev"
)
WALKTHROUGH_URL = "http://[::1]:3000/diary/stage3b/yuri.html"


def _probe_walkthrough() -> None:
    try:
        with urlopen(WALKTHROUGH_URL, timeout=3) as response:  # nosec B310 - exact loopback
            if response.status != 200:
                raise RuntimeError("walkthrough page did not return HTTP 200")
            body = response.read(32768).decode("utf-8")
    except (OSError, URLError) as exc:
        raise RuntimeError("walkthrough page was not reachable on IPv6 loopback") from exc
    if "Reception One - Yuri internal walkthrough" not in body:
        raise RuntimeError("walkthrough page identity did not match")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the local authored-synthetic Yuri walkthrough."
    )
    parser.add_argument(
        "--no-open",
        action="store_true",
        help="Print the URL without opening the default browser.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Start, probe and clean up immediately without waiting for input.",
    )
    args = parser.parse_args()

    os.environ.setdefault("DATABASE_URL", LOCAL_DEV_DATABASE_URL)
    processes = []
    database_created = False
    before: dict[str, object] | None = None
    unchanged = False
    cleanup_complete = False

    try:
        create_database()
        database_created = True
        create_schema_and_seed(f"YuriWalkthrough-{secrets.token_urlsafe(24)}!")
        before = database_readback()
        runtime, processes = launch_runtime()
        _probe_walkthrough()

        print(
            json.dumps(
                {
                    "status": "ready",
                    "url": WALKTHROUGH_URL,
                    "database": LOCKED_DATABASE,
                    "evidence_mode": "authored_synthetic_yuri_internal_formative",
                    "provider": runtime["provider"],
                    "loopback_family": runtime["loopback_family"],
                    "appointment_write_available": False,
                },
                indent=2,
                sort_keys=True,
            ),
            flush=True,
        )
        if not args.no_open and not args.check:
            webbrowser.open(WALKTHROUGH_URL, new=2)
        if not args.check:
            print(
                "\nComplete the walkthrough in the browser. "
                "Download the review JSON before returning here.",
                flush=True,
            )
            input("Press Enter to stop the local runtime and clean up: ")
    except KeyboardInterrupt:
        print("\nStopping the local walkthrough.", flush=True)
    except Exception as exc:
        print(
            json.dumps(
                {
                    "status": "failed",
                    "error_type": type(exc).__name__,
                    "external_provider_contacted": False,
                },
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return_code = 1
    else:
        return_code = 0
    finally:
        if processes:
            stop_runtime(processes)
        if database_created:
            try:
                after = database_readback()
                unchanged = (
                    before is not None
                    and before["counts"] == after["counts"]
                    and before["sha256"] == after["sha256"]
                )
                cleanup_database()
                cleanup_complete = True
            except Exception:
                return_code = 1
        print(
            json.dumps(
                {
                    "status": "closed",
                    "database_truth_unchanged": unchanged,
                    "owned_database_cleanup_complete": cleanup_complete,
                    "provider_used": False,
                },
                sort_keys=True,
            ),
            flush=True,
        )
        if database_created and (not unchanged or not cleanup_complete):
            return_code = 1

    return return_code


if __name__ == "__main__":
    raise SystemExit(main())
