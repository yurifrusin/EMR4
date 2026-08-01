#!/usr/bin/env python3
"""Retry the sole pre-schema v6.1 cohort failure without contract changes."""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import reception_one_bureau_model_text_lane as lane
from scripts import reception_one_bureau_model_text_lane_broker as broker
from scripts import reception_one_preprinted_form_v5_live as parent_live
from scripts import reception_one_receptionist_first_v6_cohort as v6_cohort
from scripts import reception_one_receptionist_first_v61 as v61
from scripts import reception_one_receptionist_first_v61_repair as repair


CASE_CODE = "b-move-shift"
ATTEMPT_CASE_CODE = "b-move-shift-continuation"
ARTIFACT_DIR = v61.ARTIFACT_DIR / "continuation-b-move-shift"
FRAME_PATH = v61.ARTIFACT_DIR / "continuation-b-move-shift-frame.json"
EVIDENCE_PATH = v61.ARTIFACT_DIR / "occupied-continuation-evidence.json"
NOTEBOOK_PATH = v61.ARTIFACT_DIR / "continuation-notebook.md"
AUTHORITY_PATH = v61.ARTIFACT_DIR / "continuation-authority.json"


class ContinuationError(RuntimeError):
    """A bounded continuation contract or lifecycle rejection."""


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _ids() -> tuple[tuple[str, str], tuple[str, str]]:
    attempts = tuple(
        "reception-one-receptionist-first-v61-repair-"
        f"{ATTEMPT_CASE_CODE}-turn-{index:03d}"
        for index in (1, 2)
    )
    ledgers = tuple(
        "reception-one-receptionist-first-v61-repair-"
        f"{ATTEMPT_CASE_CODE}-ledger-{index:03d}"
        for index in (1, 2)
    )
    for attempt_id, ledger_id in zip(attempts, ledgers, strict=True):
        broker.validate_attempt_ledger_pair(attempt_id, ledger_id)
    return attempts, ledgers


def _case() -> dict[str, Any]:
    _, cases = v6_cohort.load_source_manifest()
    return next(case for case in cases if case["case_code"] == CASE_CODE)


def _render_notebook(
    dialogue: dict[str, Any],
    observation: dict[str, Any],
) -> None:
    turns: list[dict[str, Any]] = []
    for index in range(1, dialogue["actual_provider_call_count"] + 1):
        audit = repair._load(
            ARTIFACT_DIR
            / f"occupied-turn-{index:03d}-external-audit.json"
        )
        turns.append(
            {
                "turn": index,
                "provider_outcome": audit["provider_outcome"],
                "receptionist_output": audit.get("receptionist_output"),
                "typed_form": (
                    (audit.get("typed_program") or {}).get(
                        "explicit_source_form"
                    )
                ),
                "proofreader": audit.get("proofreader"),
                "release": audit.get("release"),
            }
        )
    lines = [
        "# Reception One v6.1 Pre-schema Continuation",
        "",
        "The frozen first cohort returned HTTP 200 with non-JSON text for this "
        "case, so no candidate reached the proofreader. This continuation uses "
        "the identical prompt, schema and exact provider boundary with new "
        "single-use ledgers.",
        "",
        "Authored-synthetic input:",
        "",
        *[
            f"- {text}"
            for text in v6_cohort.frame_for_case(_case())["utterances"]
        ],
        "",
        "```json",
        json.dumps(
            {
                "turns": turns,
                "terminal_status": observation["terminal_status"],
                "exact_expected_outcome": observation[
                    "expected_safe_outcome"
                ],
                "correction_used": observation["correction_used"],
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        ),
        "```",
        "",
        "Raw provider packets, credentials, API-key information and hidden "
        "chain-of-thought are excluded.",
    ]
    NOTEBOOK_PATH.write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def run(
    *,
    preflight_path: Path,
    authority_path: Path,
    graph_revision: int,
    compass_revision: int,
) -> dict[str, Any]:
    if EVIDENCE_PATH.exists():
        raise ContinuationError("continuation_output_already_exists")
    case = _case()
    frame = v6_cohort.frame_for_case(case)
    _write_json(FRAME_PATH, frame)
    provider_blocked = repair._load(repair.PROVIDER_BLOCKED_PATH)
    if (
        provider_blocked
        != repair.build_provider_blocked_evidence(write_frames=False)
    ):
        raise ContinuationError("frozen_contract_binding_changed")
    oracle = next(
        row
        for row in provider_blocked["case_oracles"]
        if row["case_code"] == CASE_CODE
    )
    attempts, ledgers = _ids()
    with repair._v61_contract():
        dialogue = repair._load_closed_dialogue(
            case_dir=ARTIFACT_DIR,
            attempt_ids=attempts,
            ledger_ids=ledgers,
            graph_revision=graph_revision,
            compass_revision=compass_revision,
        )
        source = "resumed_closed_evidence"
        if dialogue is None:
            dialogue = parent_live.run_dialogue(
                artifact_dir=ARTIFACT_DIR,
                preflight_path=preflight_path,
                authority_path=authority_path,
                expected_graph_revision=graph_revision,
                expected_compass_revision=compass_revision,
                frame_path=FRAME_PATH,
                attempt_ids=attempts,
                ledger_ids=ledgers,
            )
            source = "new_occupied_dialogue"
    observation = v6_cohort._case_observation(
        case=case,
        oracle=oracle,
        case_dir=ARTIFACT_DIR,
        dialogue=dialogue,
    )
    result: dict[str, Any] = {
        "schema_version": (
            "reception.one.receptionist_first_v61."
            "pre_schema_continuation.v1"
        ),
        "result": (
            "reception_one_receptionist_first_v61_continuation_pass"
            if observation["expected_safe_outcome"]
            else "reception_one_receptionist_first_v61_"
            "continuation_fail_closed"
        ),
        "source": source,
        "historical_failure": {
            "case_code": CASE_CODE,
            "provider_status": "response_rejected_before_candidate",
            "reason_code": "provider_text_not_json",
            "release": None,
            "ledger_consumed": True,
        },
        "contract_changed": False,
        "provider_blocked_evidence_hash": provider_blocked[
            "evidence_hash"
        ],
        "continuity_binding": {
            "graph_revision": graph_revision,
            "compass_revision": compass_revision,
        },
        "actual_provider_calls": dialogue["actual_provider_call_count"],
        "absolute_continuation_call_ceiling": 2,
        "incremental_cost_ceiling_usd": 1,
        "observation": observation,
        "all_ledgers_consumed": all(
            repair._load(path).get("status") == "consumed"
            for path in ARTIFACT_DIR.glob("*-ledger.json")
        ),
        "all_cleanup_passed": observation["cleanup_passed"],
        "explicit_exclusions": {
            "raw_prompt_recorded": False,
            "raw_provider_response_recorded": False,
            "credential_or_token_recorded": False,
            "api_key_information_recorded": False,
            "chain_of_thought_recorded": False,
            "natural_response_parsed_into_form": False,
            "product_or_database_access": False,
            "appointment_write": False,
            "human_or_product_delivery": False,
            "provider_or_regional_fallback": False,
        },
    }
    unhashed = copy.deepcopy(result)
    result["evidence_hash"] = v61.canonical_hash(unhashed)
    _write_json(EVIDENCE_PATH, result)
    _render_notebook(dialogue, observation)
    return result


def main() -> int:
    global ATTEMPT_CASE_CODE
    global ARTIFACT_DIR
    global FRAME_PATH
    global EVIDENCE_PATH
    global NOTEBOOK_PATH
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preflight", type=Path, required=True)
    parser.add_argument("--authority", type=Path, default=AUTHORITY_PATH)
    parser.add_argument("--graph-revision", type=int, required=True)
    parser.add_argument("--compass-revision", type=int, required=True)
    parser.add_argument(
        "--attempt-case-code",
        default=ATTEMPT_CASE_CODE,
    )
    parser.add_argument("--artifact-dir", type=Path, default=ARTIFACT_DIR)
    parser.add_argument("--frame-output", type=Path, default=FRAME_PATH)
    parser.add_argument("--output", type=Path, default=EVIDENCE_PATH)
    parser.add_argument("--notebook", type=Path, default=NOTEBOOK_PATH)
    args = parser.parse_args()
    ATTEMPT_CASE_CODE = args.attempt_case_code
    ARTIFACT_DIR = args.artifact_dir
    FRAME_PATH = args.frame_output
    EVIDENCE_PATH = args.output
    NOTEBOOK_PATH = args.notebook
    try:
        evidence = run(
            preflight_path=args.preflight,
            authority_path=args.authority,
            graph_revision=args.graph_revision,
            compass_revision=args.compass_revision,
        )
    except (
        ContinuationError,
        repair.RepairCohortError,
        parent_live.PreprintedLiveError,
        lane.ModelLaneError,
        ValueError,
    ) as error:
        print(
            json.dumps(
                {
                    "result": (
                        "reception_one_receptionist_first_v61_"
                        "continuation_blocked"
                    ),
                    "reason_code": str(error).split(":", 1)[0],
                },
                sort_keys=True,
            )
        )
        return 2
    print(json.dumps(evidence, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
