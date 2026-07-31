#!/usr/bin/env python3
"""Run the sealed receptionist-first v6.9 untouched synthetic holdout."""

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

from scripts import reception_one_preprinted_form_v5_broad_language_cohort as broad
from scripts import reception_one_receptionist_first_v6_cohort as v6_cohort
from scripts import reception_one_receptionist_first_v62_cohort as base
from scripts import reception_one_receptionist_first_v68 as frozen

_BASE_BUILD_PROVIDER_BLOCKED = base.build_provider_blocked_evidence

ARTIFACT_DIR = (
    ROOT
    / "orchestration"
    / "continuity"
    / "reception-one-receptionist-first-v69"
)
MANIFEST_PATH = ARTIFACT_DIR / "evaluation-manifest.json"
FRAMES_DIR = ARTIFACT_DIR / "frames"
PROVIDER_BLOCKED_PATH = ARTIFACT_DIR / "provider-blocked-evidence.json"
OCCUPIED_PATH = ARTIFACT_DIR / "occupied-cohort-evidence.json"
NOTEBOOK_PATH = ARTIFACT_DIR / "running-test-notebook.md"
AUTHORITY_PATH = ARTIFACT_DIR / "occupied-authority.json"


def _manifest() -> dict[str, Any]:
    value = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    if not isinstance(value, dict) or not isinstance(value.get("cases"), list):
        raise base.V62CohortError("holdout_manifest_invalid")
    return value


def _case_contracts() -> tuple[tuple[Any, ...], ...]:
    return tuple(
        (
            case["case_code"],
            case.get("source_case_id"),
            case["expected_goal"],
            case["expected_proposal_family"],
            case["expected_proposal_release"],
        )
        for case in _manifest()["cases"]
    )


@contextmanager
def _configured() -> Iterator[None]:
    manifest = _manifest()
    case_contracts = _case_contracts()
    case_codes = tuple(item[0] for item in case_contracts)
    call_ceiling = len(case_codes) * 2
    overrides = {
        "v62": frozen,
        "ARTIFACT_DIR": ARTIFACT_DIR,
        "VERSION_TAG": "v68",
        "VERSION_LABEL": "v6.9 untouched holdout",
        "FRAMES_DIR": FRAMES_DIR,
        "PROVIDER_BLOCKED_PATH": PROVIDER_BLOCKED_PATH,
        "OCCUPIED_PATH": OCCUPIED_PATH,
        "NOTEBOOK_PATH": NOTEBOOK_PATH,
        "AUTHORITY_PATH": AUTHORITY_PATH,
        "SOURCE_MANIFEST_PATH": MANIFEST_PATH,
        "EXPECTED_CASE_CODES": case_codes,
        "ABSOLUTE_CALL_CEILING": call_ceiling,
        "OCCUPIED_RESULT_PASS": (
            "reception_one_receptionist_first_v69_untouched_holdout_pass"
        ),
        "OCCUPIED_RESULT_FAIL": (
            "reception_one_receptionist_first_v69_untouched_holdout_fail_closed"
        ),
        "PAIRED_DEVELOPMENT_NOT_HOLDOUT": False,
        "ALL_ORIGINAL_V6_CASES_INCLUDED": False,
    }
    v6_overrides = {
        "SOURCE_MANIFEST_PATH": MANIFEST_PATH,
        "EXPECTED_CASE_CODES": case_codes,
        "ABSOLUTE_CALL_CEILING": call_ceiling,
    }
    broad_overrides = {
        "ARTIFACT_DIR": ARTIFACT_DIR,
        "MANIFEST_PATH": MANIFEST_PATH,
        "AUTHORITY_PATH": AUTHORITY_PATH,
        "FRAMES_DIR": FRAMES_DIR,
        "PROVIDER_BLOCKED_PATH": PROVIDER_BLOCKED_PATH,
        "OCCUPIED_PATH": OCCUPIED_PATH,
        "EXPECTED_CASES": case_contracts,
    }
    previous = {name: getattr(base, name) for name in overrides}
    previous_v6 = {name: getattr(v6_cohort, name) for name in v6_overrides}
    previous_broad = {name: getattr(broad, name) for name in broad_overrides}
    for name, value in overrides.items():
        setattr(base, name, value)
    for name, value in v6_overrides.items():
        setattr(v6_cohort, name, value)
    for name, value in broad_overrides.items():
        setattr(broad, name, value)
    try:
        if manifest.get("absolute_call_ceiling") != call_ceiling:
            raise base.V62CohortError("holdout_call_ceiling_invalid")
        yield
    finally:
        for name, value in previous.items():
            setattr(base, name, value)
        for name, value in previous_v6.items():
            setattr(v6_cohort, name, value)
        for name, value in previous_broad.items():
            setattr(broad, name, value)


def load_source_manifest() -> tuple[dict[str, Any], list[dict[str, Any]]]:
    with _configured():
        return base.load_source_manifest()


def frame_for_case(case: dict[str, Any]) -> dict[str, Any]:
    with _configured():
        return base.frame_for_case(case)


def build_provider_blocked_evidence(*, write_frames: bool) -> dict[str, Any]:
    with _configured():
        manifest, cases = base.load_source_manifest()
        oracles: list[dict[str, Any]] = []
        identifiers: list[dict[str, Any]] = []
        for case in cases:
            frame = base.frame_for_case(case)
            if write_frames:
                base._write_json(
                    FRAMES_DIR / f"{case['case_code']}.json", frame
                )
            oracles.append(base._oracle(case, frame))
            attempts, ledgers = base._case_ids(case["case_code"])
            identifiers.append(
                {
                    "case_code": case["case_code"],
                    "attempt_ids": list(attempts),
                    "ledger_ids": list(ledgers),
                }
            )
        evidence: dict[str, Any] = {
            "schema_version": (
                "reception.one.receptionist_first_v69."
                "holdout_provider_blocked.v1"
            ),
            "result": (
                "reception_one_receptionist_first_v69_"
                "holdout_provider_blocked_pass"
            ),
            "provider_contacted": False,
            "provider_calls_performed": 0,
            "credential_reads_performed": 0,
            "data_class": "authored_synthetic",
            "effect_ceiling": "proposal_only",
            "paired_development_not_holdout": False,
            "all_original_v6_cases_included": False,
            "source_manifest_file_sha256": base._file_hash(MANIFEST_PATH),
            "source_manifest_content_sha256": frozen.canonical_hash(manifest),
            "source_case_count": len(cases),
            "source_case_codes": [case["case_code"] for case in cases],
            "contract": {
                "system_instruction_sha256": frozen.canonical_hash(
                    {"text": frozen.SYSTEM_INSTRUCTION}
                ),
                "model_output_schema_file_sha256": base._file_hash(
                    frozen.MODEL_FORM_BODY_SCHEMA_PATH
                ),
                "turn_input_schema_file_sha256": base._file_hash(
                    frozen.TURN_INPUT_SCHEMA_PATH
                ),
                "desk_context_schema_file_sha256": base._file_hash(
                    frozen.DESK_CONTEXT_SCHEMA_PATH
                ),
                "correction_ticket_schema_file_sha256": base._file_hash(
                    frozen.CORRECTION_TICKET_SCHEMA_PATH
                ),
                "provider_response_schema_sha256": frozen.canonical_hash(
                    frozen.vertex_response_schema()
                ),
                "temperature": frozen.TEMPERATURE,
                "thinking_budget": frozen.THINKING_BUDGET,
                "include_thoughts": frozen.INCLUDE_THOUGHTS,
                "maximum_output_tokens": frozen.MAX_OUTPUT_TOKENS,
                "prompt_or_schema_change_within_cohort": False,
                "natural_response_parsed_into_form": False,
                "broker_judgement_repair": False,
            },
            "case_oracles": oracles,
            "single_use_identifiers": identifiers,
            "holdout": {
                "previously_sent_to_provider": False,
                "may_be_used_for_prompt_or_proofreader_tuning": False,
                "sealed_before_first_provider_call": True,
                "frozen_v68_contract": True,
            },
            "call_budget": {
                "primary_call_per_case": 1,
                "maximum_terminal_second_call_per_case": 1,
                "absolute_provider_call_ceiling": len(cases) * 2,
                "incremental_cost_ceiling_usd": 1,
            },
            "boundary": {
                "raw_authored_synthetic_requests_included": True,
                "raw_provider_request_retained": False,
                "raw_provider_response_retained": False,
                "credentials_or_tokens_retained": False,
                "api_key_information_retained": False,
                "chain_of_thought_retained": False,
                "thinking_token_count_only": True,
                "full_diary_exposed": False,
                "unselected_appointments_exposed": False,
                "product_or_database_access": False,
                "appointment_write": False,
                "product_delivery": False,
                "provider_tools": False,
                "fallback": False,
            },
        }
        evidence["evidence_hash"] = base._content_hash(evidence)
        return evidence


def run_occupied(
    *,
    preflight_path: Path,
    authority_path: Path,
    graph_revision: int,
    compass_revision: int,
) -> dict[str, Any]:
    with _configured():
        base.build_provider_blocked_evidence = build_provider_blocked_evidence
        try:
            evidence = base.run_occupied(
                preflight_path=preflight_path,
                authority_path=authority_path,
                graph_revision=graph_revision,
                compass_revision=compass_revision,
            )
            evidence["schema_version"] = (
                "reception.one.receptionist_first_v69."
                "untouched_holdout.v1"
            )
            evidence["paired_development_not_holdout"] = False
            evidence["all_original_v6_cases_included"] = False
            evidence["holdout"] = {
                "sealed_before_first_provider_call": True,
                "provider_exposure_before_this_run": False,
                "used_for_prompt_schema_proofreader_or_oracle_tuning": False,
                "evaluated_contract": "byte_frozen_v68",
            }
            evidence["evidence_hash"] = base._content_hash(evidence)
            base._write_json(OCCUPIED_PATH, evidence)
            return evidence
        finally:
            base.build_provider_blocked_evidence = _BASE_BUILD_PROVIDER_BLOCKED


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
    except Exception as error:
        print(
            json.dumps(
                {
                    "result": (
                        "reception_one_receptionist_first_v69_blocked"
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
                "case_count": evidence.get("case_count"),
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
