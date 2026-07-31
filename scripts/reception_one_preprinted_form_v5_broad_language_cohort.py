#!/usr/bin/env python3
"""Run the frozen Reception One v5 broad authored-synthetic language cohort."""

from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import reception_one_preprinted_form_v5_multicase as cohort


ARTIFACT_DIR = (
    ROOT
    / "orchestration"
    / "continuity"
    / "reception-one-preprinted-form-v5-broad-language-cohort"
)
MANIFEST_PATH = ARTIFACT_DIR / "evaluation-manifest.json"
AUTHORITY_PATH = ARTIFACT_DIR / "occupied-authority.json"
FRAMES_DIR = ARTIFACT_DIR / "frames"
PROVIDER_BLOCKED_PATH = ARTIFACT_DIR / "provider-blocked-evidence.json"
OCCUPIED_PATH = ARTIFACT_DIR / "occupied-cohort-evidence.json"

EXPECTED_CASES = (
    ("b-create-arrange", None, "create", "create", True),
    ("b-create-alias", None, "create", "create", True),
    ("b-create-preface", None, "create", "create", True),
    ("b-create-correct", None, "create", "create", True),
    ("b-move-resched", None, "move", "move", True),
    ("b-move-shift", None, "move", "move", True),
    ("b-move-change", None, "move", "move", True),
    ("b-move-correct", None, "move", "move", True),
    ("b-resize-long", None, "resize", "resize", True),
    ("b-resize-short", None, "resize", "resize", True),
    ("b-resize-give", None, "resize", "resize", True),
    ("b-resize-explicit", None, "resize", "resize", True),
    ("b-cancel-remove", None, "cancel", "cancel", True),
    ("b-cancel-calloff", None, "cancel", "cancel", True),
    ("b-cancel-takeout", None, "cancel", "cancel", True),
    (
        "b-status-complete",
        None,
        "status_change",
        "status_change",
        True,
    ),
    (
        "b-status-arrived",
        None,
        "status_change",
        "status_change",
        True,
    ),
    ("b-status-noshow-gap", None, "clarification", "clarification", False),
    (
        "b-squeeze-without",
        None,
        "squeeze_in_assessment",
        "squeeze_in_assessment",
        True,
    ),
    (
        "b-squeeze-negated-move",
        None,
        "squeeze_in_assessment",
        "squeeze_in_assessment",
        True,
    ),
    ("b-clarify-sort", None, "clarification", "clarification", False),
    (
        "b-clarify-different",
        None,
        "clarification",
        "clarification",
        False,
    ),
    (
        "b-clarify-details",
        None,
        "clarification",
        "clarification",
        False,
    ),
    ("b-clarify-fit", None, "clarification", "clarification", False),
)


def _configure_base() -> None:
    cohort.ARTIFACT_DIR = ARTIFACT_DIR
    cohort.MANIFEST_PATH = MANIFEST_PATH
    cohort.AUTHORITY_PATH = AUTHORITY_PATH
    cohort.FRAMES_DIR = FRAMES_DIR
    cohort.PROVIDER_BLOCKED_PATH = PROVIDER_BLOCKED_PATH
    cohort.OCCUPIED_PATH = OCCUPIED_PATH
    cohort.EXPECTED_CASES = EXPECTED_CASES
    cohort.MANIFEST_SCHEMA_VERSION = (
        "reception.one.preprinted_form_v5.broad_language_manifest.v1"
    )
    cohort.PROVIDER_BLOCKED_SCHEMA_VERSION = (
        "reception.one.preprinted_form_v5.broad_language_provider_blocked.v1"
    )
    cohort.PROVIDER_BLOCKED_RESULT = (
        "reception_one_preprinted_form_v5_broad_language_provider_blocked_pass"
    )
    cohort.OCCUPIED_SCHEMA_VERSION = (
        "reception.one.preprinted_form_v5.broad_language_occupied.v1"
    )
    cohort.OCCUPIED_PASS_RESULT = (
        "reception_one_preprinted_form_v5_broad_language_occupied_pass"
    )
    cohort.OCCUPIED_FAIL_RESULT = (
        "reception_one_preprinted_form_v5_broad_language_occupied_fail"
    )
    cohort.BLOCKED_RESULT = (
        "reception_one_preprinted_form_v5_broad_language_blocked"
    )
    cohort.HISTORICAL_ANCHOR = {
        "case_id": "reception-one-preprinted-form-v5-multicase-active",
        "source_result": (
            "reception_one_preprinted_form_v5_multicase_occupied_pass"
        ),
        "replayed": False,
    }
    cohort.EXPECTED_PRIMARY_CALLS = len(EXPECTED_CASES)
    cohort.EXPECTED_CORRECTION_CALLS = len(EXPECTED_CASES)
    cohort.EXPECTED_ABSOLUTE_CALL_CEILING = len(EXPECTED_CASES) * 2
    cohort.CANDID_LIMIT = (
        "This cohort measures only twenty-four frozen authored-synthetic "
        "language variants through the configured and observed Sydney Vertex "
        "locational request path. It does not prove Australian physical or "
        "sovereign processing, exhaustive language coverage, production "
        "fitness or safety for real, product, patient, health, clinical or "
        "historical data."
    )


MulticaseError = cohort.MulticaseError

_CONFIG_NAMES = (
    "ARTIFACT_DIR",
    "MANIFEST_PATH",
    "AUTHORITY_PATH",
    "FRAMES_DIR",
    "PROVIDER_BLOCKED_PATH",
    "OCCUPIED_PATH",
    "EXPECTED_CASES",
    "MANIFEST_SCHEMA_VERSION",
    "PROVIDER_BLOCKED_SCHEMA_VERSION",
    "PROVIDER_BLOCKED_RESULT",
    "OCCUPIED_SCHEMA_VERSION",
    "OCCUPIED_PASS_RESULT",
    "OCCUPIED_FAIL_RESULT",
    "BLOCKED_RESULT",
    "HISTORICAL_ANCHOR",
    "EXPECTED_PRIMARY_CALLS",
    "EXPECTED_CORRECTION_CALLS",
    "EXPECTED_ABSOLUTE_CALL_CEILING",
    "CANDID_LIMIT",
)


@contextmanager
def _configured() -> Any:
    previous = {name: getattr(cohort, name) for name in _CONFIG_NAMES}
    _configure_base()
    try:
        yield
    finally:
        for name, value in previous.items():
            setattr(cohort, name, value)


def load_manifest() -> tuple[dict[str, Any], list[dict[str, Any]]]:
    with _configured():
        return cohort.load_manifest()


def frame_for_case(
    case: dict[str, Any],
    cases_document: dict[str, Any] | None = None,
) -> dict[str, Any]:
    with _configured():
        return cohort.frame_for_case(case, cases_document)


def oracle_for_case(
    case: dict[str, Any],
    frame: dict[str, Any],
) -> dict[str, Any]:
    with _configured():
        return cohort.oracle_for_case(case, frame)


def build_provider_blocked_evidence(
    *,
    write_frames: bool,
) -> dict[str, Any]:
    with _configured():
        return cohort.build_provider_blocked_evidence(
            write_frames=write_frames
        )


def run_occupied(**kwargs: Any) -> dict[str, Any]:
    with _configured():
        return cohort.run_occupied(**kwargs)


def case_ids(case_code: str) -> tuple[tuple[str, str], tuple[str, str]]:
    with _configured():
        return cohort._case_ids(case_code)


def summarize_language_families(
    occupied: dict[str, Any],
) -> dict[str, dict[str, int]]:
    """Return deterministic family counts without inspecting raw responses."""

    families: dict[str, dict[str, int]] = {}
    for item in occupied["cases"]:
        parts = item["case_code"].split("-")
        family = parts[1] if len(parts) > 2 else "unknown"
        row = families.setdefault(
            family,
            {"cases": 0, "primary_admits": 0, "corrections": 0},
        )
        row["cases"] += 1
        row["primary_admits"] += int(
            item["primary_proofreader_disposition"] == "admit"
        )
        row["corrections"] += int(item["correction_used"])
    return families


def main() -> int:
    with _configured():
        return cohort.main()


if __name__ == "__main__":
    raise SystemExit(main())
