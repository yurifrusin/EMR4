"""Exact disposable runtime for Reception One availability reconciliation."""

from __future__ import annotations

import argparse
import json
import secrets
import sys
from pathlib import Path

import bernie_meta_grid_live_local_harness as fixture_base
import reception_one_committed_event_harness as event_base


LOCKED_DATABASE = "gp_pms_reception_one_availability_reconcile_7c8e4f21_20260721"
RUNTIME_TAG = "reception-one-availability-reconcile-7c8e4f21"
PROBE_ROLE = "emr4_reception_one_availability_probe_7c8e4f21"
AVAILABILITY_TARGET_ID = fixture_base.fixed_id("appointment-billy-shera-1430")
OTHER_PRACTITIONER_ID = fixture_base.fixed_id("appointment-margaret-patel-1000")


def _configure() -> None:
    """Bind the accepted event harness to this tranche's exact disposable target."""

    event_base.LOCKED_DATABASE = LOCKED_DATABASE
    event_base.RUNTIME_TAG = RUNTIME_TAG
    event_base.PROBE_ROLE = PROBE_ROLE
    event_base.IN_SCOPE_APPOINTMENT_ID = AVAILABILITY_TARGET_ID
    event_base.OUT_OF_SCOPE_APPOINTMENT_ID = OTHER_PRACTITIONER_ID
    fixture_base.LOCKED_DATABASE = LOCKED_DATABASE


def create_database() -> None:
    _configure()
    event_base.create_database()


def create_schema_and_seed(password: str) -> None:
    _configure()
    event_base.create_schema_and_seed(password)


def readiness_report() -> dict[str, object]:
    _configure()
    report = event_base.readiness_report()
    return {
        **report,
        "schema_version": "reception-one.availability-reconciliation.readiness.v1",
        "database": LOCKED_DATABASE,
    }


def database_readback() -> dict[str, object]:
    _configure()
    report = event_base.database_readback()
    return {
        **report,
        "schema_version": "reception-one.availability-reconciliation.database-readback.v1",
        "database": LOCKED_DATABASE,
        "target_windows": {
            "availability_target": report["target_windows"]["in_scope_target"],
            "other_practitioner_target": report["target_windows"]["out_of_scope_target"],
        },
    }


def database_security_probes() -> dict[str, object]:
    _configure()
    report = event_base.database_security_probes()
    return {
        **report,
        "schema_version": "reception-one.availability-reconciliation.database-security.v1",
    }


def launch_runtime() -> tuple[dict[str, object], list[object]]:
    _configure()
    return event_base.launch_runtime()


def stop_runtime(processes: list[object]) -> None:
    event_base.stop_runtime(processes)


def cleanup_database() -> dict[str, object]:
    _configure()
    report = event_base.cleanup_database()
    return {
        **report,
        "schema_version": "reception-one.availability-reconciliation.database-cleanup.v1",
        "database": LOCKED_DATABASE,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("setup")
    subparsers.add_parser("status")
    subparsers.add_parser("readback")
    subparsers.add_parser("serve-runtime")
    cleanup_parser = subparsers.add_parser("cleanup")
    cleanup_parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()
    try:
        if args.command == "setup":
            create_database()
            create_schema_and_seed(
                f"ReceptionOneAvailability-{secrets.token_urlsafe(24)}!"
            )
            if not readiness_report()["ready"]:
                raise RuntimeError("Availability reconciliation database did not pass readiness")
        elif args.command == "status":
            if not readiness_report()["ready"]:
                raise RuntimeError("Availability reconciliation database did not pass readiness")
        elif args.command == "readback":
            database_readback()
        elif args.command == "serve-runtime":
            runtime, processes = launch_runtime()
            print(
                json.dumps(
                    {
                        "event": "runtime_ready",
                        "database": runtime["database"],
                        "loopback_family": runtime["loopback_family"],
                    }
                ),
                flush=True,
            )
            try:
                event_base.time_module.sleep(10**9)
            finally:
                stop_runtime(processes)
        elif args.command == "cleanup":
            report = cleanup_database()
            if args.output is not None:
                target = args.output.resolve()
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(
                    json.dumps(report, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8",
                )
    except Exception as exc:
        print(json.dumps({"ready": False, "error_type": type(exc).__name__}), file=sys.stderr)
        return 1
    print(
        json.dumps(
            {
                "schema_version": "reception-one.availability-reconciliation.cli-status.v1",
                "command": args.command,
                "completed": True,
                "report_values_recorded": False,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
