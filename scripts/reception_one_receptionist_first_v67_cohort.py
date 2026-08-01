#!/usr/bin/env python3
"""Run the full 24-case receptionist-first v6.7 cohort."""

from __future__ import annotations

import argparse
from contextlib import contextmanager
import json
from pathlib import Path
import sys
from typing import Any, Iterator

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import reception_one_bureau_model_text_lane as lane
from scripts import reception_one_preprinted_form_v5_live as parent_live
from scripts import reception_one_receptionist_first_v6_cohort as v6_cohort
from scripts import reception_one_receptionist_first_v62_cohort as base
from scripts import reception_one_receptionist_first_v67 as v67


ARTIFACT_DIR = v67.ARTIFACT_DIR
FRAMES_DIR = ARTIFACT_DIR / "frames"
PROVIDER_BLOCKED_PATH = ARTIFACT_DIR / "provider-blocked-evidence.json"
OCCUPIED_PATH = ARTIFACT_DIR / "occupied-cohort-evidence.json"
NOTEBOOK_PATH = ARTIFACT_DIR / "running-test-notebook.md"
AUTHORITY_PATH = ARTIFACT_DIR / "occupied-authority.json"
EXPECTED_CASE_CODES = base.EXPECTED_CASE_CODES
ABSOLUTE_CALL_CEILING = base.ABSOLUTE_CALL_CEILING
OCCUPIED_RESULT_PASS = (
    "reception_one_receptionist_first_v67_full_cohort_pass"
)
OCCUPIED_RESULT_FAIL = (
    "reception_one_receptionist_first_v67_full_cohort_fail_closed"
)


class V67CohortError(RuntimeError):
    """A v6.7 cohort contract, lifecycle or audit rejection."""


@contextmanager
def _configured() -> Iterator[None]:
    overrides: dict[str, Any] = {
        "v62": v67,
        "ARTIFACT_DIR": ARTIFACT_DIR,
        "VERSION_TAG": "v67",
        "VERSION_LABEL": "v6.7",
        "FRAMES_DIR": FRAMES_DIR,
        "PROVIDER_BLOCKED_PATH": PROVIDER_BLOCKED_PATH,
        "OCCUPIED_PATH": OCCUPIED_PATH,
        "NOTEBOOK_PATH": NOTEBOOK_PATH,
        "AUTHORITY_PATH": AUTHORITY_PATH,
        "OCCUPIED_RESULT_PASS": OCCUPIED_RESULT_PASS,
        "OCCUPIED_RESULT_FAIL": OCCUPIED_RESULT_FAIL,
    }
    previous = {name: getattr(base, name) for name in overrides}
    for name, value in overrides.items():
        setattr(base, name, value)
    try:
        yield
    finally:
        for name, value in previous.items():
            setattr(base, name, value)


def load_source_manifest() -> tuple[dict[str, Any], list[dict[str, Any]]]:
    with _configured():
        return base.load_source_manifest()


def frame_for_case(case: dict[str, Any]) -> dict[str, Any]:
    return base.frame_for_case(case)


def case_ids(case_code: str) -> tuple[tuple[str, str], tuple[str, str]]:
    with _configured():
        return base._case_ids(case_code)


def build_provider_blocked_evidence(
    *,
    write_frames: bool,
) -> dict[str, Any]:
    with _configured():
        evidence = base.build_provider_blocked_evidence(
            write_frames=write_frames
        )
    if (
        evidence.get("source_case_count") != 24
        or evidence.get("contract", {}).get("maximum_output_tokens") != 3072
        or evidence.get("provider_calls_performed") != 0
    ):
        raise V67CohortError("v67_provider_blocked_boundary_invalid")
    return evidence


def run_occupied(
    *,
    preflight_path: Path,
    authority_path: Path,
    graph_revision: int,
    compass_revision: int,
) -> dict[str, Any]:
    with _configured():
        evidence = base.run_occupied(
            preflight_path=preflight_path,
            authority_path=authority_path,
            graph_revision=graph_revision,
            compass_revision=compass_revision,
        )
    if (
        evidence.get("case_count") != 24
        or evidence.get("total_actual_provider_calls", 0)
        > ABSOLUTE_CALL_CEILING
    ):
        raise V67CohortError("v67_occupied_boundary_invalid")
    return evidence


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("provider-blocked")
    occupied = subparsers.add_parser("occupied")
    occupied.add_argument("--preflight", type=Path, required=True)
    occupied.add_argument("--authority", type=Path, default=AUTHORITY_PATH)
    occupied.add_argument("--graph-revision", type=int, required=True)
    occupied.add_argument("--compass-revision", type=int, required=True)
    args = parser.parse_args()
    try:
        if args.command == "provider-blocked":
            evidence = build_provider_blocked_evidence(write_frames=True)
            base._write_json(PROVIDER_BLOCKED_PATH, evidence)
        else:
            evidence = run_occupied(
                preflight_path=args.preflight,
                authority_path=args.authority,
                graph_revision=args.graph_revision,
                compass_revision=args.compass_revision,
            )
    except (
        V67CohortError,
        base.V62CohortError,
        v6_cohort.ReceptionistCohortError,
        parent_live.PreprintedLiveError,
        lane.ModelLaneError,
        ValueError,
    ) as error:
        print(
            json.dumps(
                {
                    "result": (
                        "reception_one_receptionist_first_v67_blocked"
                    ),
                    "reason_code": str(error).split(":", 1)[0],
                },
                sort_keys=True,
            )
        )
        return 2
    print(
        json.dumps(
            {
                "result": evidence["result"],
                "case_count": evidence.get(
                    "case_count", len(EXPECTED_CASE_CODES)
                ),
                "provider_calls": evidence.get(
                    "total_actual_provider_calls", 0
                ),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
