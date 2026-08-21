"""One-shot attempt-005 adapter over the accepted structured-diagnostic controller."""

from __future__ import annotations

import argparse
from contextlib import contextmanager
import json
from pathlib import Path
from typing import Any, Iterator

from scripts import (
    raisa_authored_synthetic_check_in_native_harness_bounded_worker_attempt_004
    as accepted_attempt,
)
from scripts import (
    raisa_authored_synthetic_check_in_native_harness_bounded_worker_monitored_development_rehearsal
    as accepted_controller,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
OPERATION_ID = (
    "raisa-authored-synthetic-check-in-native-harness-bounded-worker-attempt-005"
)
ATTEMPT_ID = "deepseek-native-synthetic-window-worker-005"
WORK_ORDER_ID = "wo-synthetic-native-window-worker-005"
LEASE_ID = "lease-synthetic-native-window-worker-005"
EVIDENCE_ROOT = (
    REPO_ROOT
    / "orchestration"
    / "continuity"
    / "raisa-authored-synthetic-check-in-native-harness-bounded-worker-"
    "monitored-development-rehearsal"
    / "attempt-005"
)
ATTEMPT_ROOT = Path(f"C:/Users/sarashera/EMR4-worktrees/{ATTEMPT_ID}")
TERMINAL_SCHEMA_PATH = EVIDENCE_ROOT / "occupied-terminal.schema.json"

PATH_BINDINGS = {
    "CHECKPOINT_PATH": EVIDENCE_ROOT / "occupied-preexecution-checkpoint.json",
    "PREPARATION_PATH": EVIDENCE_ROOT / "occupied-attempt-preparation.json",
    "WORK_ORDER_PATH": EVIDENCE_ROOT / "work-order-v2.json",
    "AUTHORITY_PATH": EVIDENCE_ROOT / "worker-authority.json",
    "FORBIDDEN_PATH": EVIDENCE_ROOT / "forbidden-surfaces.json",
    "COMMAND_MANIFEST_PATH": EVIDENCE_ROOT / "command-manifest.json",
    "NO_DATABASE_ADMISSION_PATH": (
        EVIDENCE_ROOT / "provider-free-no-database-admission.json"
    ),
    "CONSUMED_PATH": EVIDENCE_ROOT / "occupied-attempt-consumed.json",
    "TERMINAL_PATH": EVIDENCE_ROOT / "occupied-terminal.json",
    "TERMINAL_SCHEMA_PATH": TERMINAL_SCHEMA_PATH,
    "NATIVE_REPORT_PATH": EVIDENCE_ROOT / "occupied-report.md",
    "PRE_HMR_TERMINAL_PATH": EVIDENCE_ROOT / "pre-hmr-startup-terminal.json",
}


def attempt_configuration() -> dict[str, Any]:
    return {
        "operation_id": OPERATION_ID,
        "attempt_id": ATTEMPT_ID,
        "work_order_id": WORK_ORDER_ID,
        "lease_id": LEASE_ID,
        "attempt_root": ATTEMPT_ROOT,
        "evidence_root": EVIDENCE_ROOT,
        **{name.lower(): path for name, path in PATH_BINDINGS.items()},
    }


@contextmanager
def configured_accepted_attempt() -> Iterator[None]:
    """Bind the already accepted one-shot controller to attempt 005 only."""

    bindings: dict[str, Any] = {
        "OPERATION_ID": OPERATION_ID,
        "ATTEMPT_ID": ATTEMPT_ID,
        "WORK_ORDER_ID": WORK_ORDER_ID,
        "LEASE_ID": LEASE_ID,
        "EVIDENCE_ROOT": EVIDENCE_ROOT,
        "ATTEMPT_ROOT": ATTEMPT_ROOT,
        "TERMINAL_SCHEMA_PATH": TERMINAL_SCHEMA_PATH,
        "PATH_BINDINGS": PATH_BINDINGS,
    }
    prior = {name: getattr(accepted_attempt, name) for name in bindings}
    for name, value in bindings.items():
        setattr(accepted_attempt, name, value)
    try:
        yield
    finally:
        for name, value in prior.items():
            setattr(accepted_attempt, name, value)


def provider_free_check() -> dict[str, Any]:
    with configured_accepted_attempt():
        value = dict(accepted_attempt.provider_free_check())
    value["schema_version"] = "ariadne.synthetic_native_worker_attempt_005_check.v1"
    return value


def prepare_attempt(review_receipt_path: Path) -> dict[str, Any]:
    with configured_accepted_attempt():
        return accepted_attempt.prepare_attempt(review_receipt_path)


def execute_native() -> dict[str, Any]:
    with configured_accepted_attempt():
        return accepted_attempt.execute_native()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--check", action="store_true")
    action.add_argument("--prepare-attempt", action="store_true")
    action.add_argument("--native", action="store_true")
    parser.add_argument("--review-receipt", type=Path)
    args = parser.parse_args()
    try:
        if args.check:
            if args.review_receipt is not None:
                raise accepted_controller.RehearsalError(
                    "review_receipt_only_valid_for_preparation"
                )
            value = provider_free_check()
        elif args.prepare_attempt:
            if args.review_receipt is None:
                raise accepted_controller.RehearsalError("review_receipt_required")
            value = prepare_attempt(args.review_receipt)
        else:
            if args.review_receipt is not None:
                raise accepted_controller.RehearsalError(
                    "review_receipt_only_valid_for_preparation"
                )
            value = execute_native()
        print(
            json.dumps(
                {
                    "result": value.get("result", value.get("status")),
                    "operation_id": OPERATION_ID,
                }
            )
        )
        return 0
    except (accepted_controller.RehearsalError, OSError) as error:
        print(json.dumps({"result": "failed_closed", "error": str(error)}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
