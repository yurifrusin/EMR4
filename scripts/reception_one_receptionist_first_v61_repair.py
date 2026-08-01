#!/usr/bin/env python3
"""Run the v6.1 targeted repair cohort over the 15 closed v6 misses."""

from __future__ import annotations

import argparse
import copy
from contextlib import contextmanager
import hashlib
import json
from pathlib import Path
import sys
from typing import Any, Iterator

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import reception_one_bureau_model_text_lane as lane
from scripts import reception_one_bureau_model_text_lane_broker as broker
from scripts import reception_one_bureau_typed_plan_protocol as typed_plan
from scripts import reception_one_preprinted_form_v5_live as parent_live
from scripts import reception_one_preprinted_form_v5_multicase as v5_cohort
from scripts import reception_one_receptionist_first_v6_cohort as v6_cohort
from scripts import reception_one_receptionist_first_v61 as v61
from scripts import reception_one_structured_source_plan_language as structured


ARTIFACT_DIR = v61.ARTIFACT_DIR
FRAMES_DIR = ARTIFACT_DIR / "frames"
PROVIDER_BLOCKED_PATH = ARTIFACT_DIR / "provider-blocked-evidence.json"
OCCUPIED_PATH = ARTIFACT_DIR / "occupied-repair-cohort-evidence.json"
NOTEBOOK_PATH = ARTIFACT_DIR / "running-repair-notebook.md"
AUTHORITY_PATH = ARTIFACT_DIR / "occupied-authority.json"
V6_DIR = v6_cohort.ARTIFACT_DIR
V6_OCCUPIED_PATH = v6_cohort.OCCUPIED_PATH
TARGET_CASE_CODES = (
    "b-create-correct",
    "b-move-resched",
    "b-move-shift",
    "b-move-change",
    "b-move-correct",
    "b-resize-long",
    "b-resize-short",
    "b-resize-give",
    "b-resize-explicit",
    "b-cancel-remove",
    "b-cancel-calloff",
    "b-cancel-takeout",
    "b-status-complete",
    "b-status-arrived",
    "b-clarify-details",
)
ABSOLUTE_CALL_CEILING = len(TARGET_CASE_CODES) * 2


class RepairCohortError(RuntimeError):
    """A targeted repair cohort contract or lifecycle rejection."""


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _load(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise RepairCohortError("json_object_unreadable") from error
    if not isinstance(value, dict):
        raise RepairCohortError("json_object_required")
    return value


def _file_hash(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _content_hash(value: dict[str, Any]) -> str:
    clean = copy.deepcopy(value)
    clean.pop("evidence_hash", None)
    return v61.canonical_hash(clean)


@contextmanager
def _v61_contract() -> Iterator[None]:
    old_cohort = v5_cohort.preprinted
    old_parent = parent_live.preprinted
    v5_cohort.preprinted = v61
    parent_live.preprinted = v61
    try:
        yield
    finally:
        v5_cohort.preprinted = old_cohort
        parent_live.preprinted = old_parent


def _source() -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    _, all_cases = v6_cohort.load_source_manifest()
    case_map = {case["case_code"]: case for case in all_cases}
    if not all(code in case_map for code in TARGET_CASE_CODES):
        raise RepairCohortError("target_case_missing")
    v6_evidence = _load(V6_OCCUPIED_PATH)
    misses = {
        row["case_code"]
        for row in v6_evidence.get("cases", [])
        if row.get("expected_safe_outcome") is False
    }
    if misses != set(TARGET_CASE_CODES):
        raise RepairCohortError("closed_v6_miss_set_changed")
    observations = {
        row["case_code"]: row for row in v6_evidence["cases"]
    }
    return [case_map[code] for code in TARGET_CASE_CODES], observations


def _case_ids(case_code: str) -> tuple[tuple[str, str], tuple[str, str]]:
    attempts = tuple(
        "reception-one-receptionist-first-v61-repair-"
        f"{case_code}-turn-{index:03d}"
        for index in (1, 2)
    )
    ledgers = tuple(
        "reception-one-receptionist-first-v61-repair-"
        f"{case_code}-ledger-{index:03d}"
        for index in (1, 2)
    )
    for attempt_id, ledger_id in zip(attempts, ledgers, strict=True):
        broker.validate_attempt_ledger_pair(attempt_id, ledger_id)
    return attempts, ledgers


def _oracle(
    case: dict[str, Any],
    frame: dict[str, Any],
) -> dict[str, Any]:
    plan = typed_plan.deterministic_plan(frame)
    if plan["goal"] != case["expected_goal"]:
        raise RepairCohortError("oracle_goal_mismatch")
    program = structured.program_from_plan(
        frame,
        plan,
        operator_note=v5_cohort._operator_note(plan["goal"]),
    )
    body = v61.model_form_body(program, frame=frame)
    evaluation = v61.evaluate_output(
        frame,
        v61.assemble_program(body),
        body,
        turn_code=1,
    )
    if evaluation["disposition"] != "admit":
        raise RepairCohortError("provider_free_oracle_not_admitted")
    release = typed_plan.execute_plan(
        frame,
        evaluation["normalized_plan"],
        evaluation["semantic_review"],
    )["final_output"]
    return {
        "case_code": case["case_code"],
        "frame_sha256": v61.canonical_hash(frame),
        "task_sha256": v61.build_turn_input(frame)["task_sha256"],
        "provider_request_sha256": v61.canonical_hash(
            v61.build_vertex_request(v61.build_turn_input(frame))
        ),
        "provider_response_schema_sha256": v61.canonical_hash(
            v61.vertex_response_schema()
        ),
        "oracle_goal": plan["goal"],
        "oracle_program_sha256": v61.canonical_hash(program),
        "oracle_typed_form_sha256": v61.canonical_hash(body["typed_form"]),
        "expected_final_output": release,
    }


def _closed_v6_body(
    case_code: str,
    v6_observation: dict[str, Any],
) -> dict[str, Any] | None:
    index = v6_observation["actual_provider_calls"]
    audit = _load(
        V6_DIR
        / "cases"
        / case_code
        / f"occupied-turn-{index:03d}-external-audit.json"
    )
    receptionist = audit.get("receptionist_output")
    program_wrapper = audit.get("typed_program")
    operator_note = audit.get("operator_note")
    if not (
        isinstance(receptionist, dict)
        and isinstance(receptionist.get("receptionist_response"), str)
        and isinstance(receptionist.get("decision_note"), str)
        and isinstance(program_wrapper, dict)
        and isinstance(program_wrapper.get("explicit_source_form"), dict)
        and isinstance(operator_note, dict)
        and isinstance(operator_note.get("operator_note"), str)
    ):
        return None
    program = program_wrapper["explicit_source_form"]
    return {
        "receptionist_response": receptionist["receptionist_response"],
        "decision_note": receptionist["decision_note"],
        "evidence_utterance_indices": receptionist[
            "evidence_utterance_indices"
        ],
        "typed_form": {
            "operator_note": operator_note["operator_note"],
            "goal_code": program["goal_code"],
            "steps": program["steps"],
        },
    }


def build_provider_blocked_evidence(
    *,
    write_frames: bool,
) -> dict[str, Any]:
    cases, v6_rows = _source()
    oracles: list[dict[str, Any]] = []
    historical_assertions: list[dict[str, Any]] = []
    identifiers: list[dict[str, Any]] = []
    for case in cases:
        case_code = case["case_code"]
        frame = v6_cohort.frame_for_case(case)
        if write_frames:
            _write_json(FRAMES_DIR / f"{case_code}.json", frame)
        oracles.append(_oracle(case, frame))
        old_body = _closed_v6_body(case_code, v6_rows[case_code])
        if old_body is None:
            historical_assertions.append(
                {
                    "case_code": case_code,
                    "historical_form_available": False,
                    "reason": "closed_v6_provider_text_not_json",
                    "v61_rejection_required": False,
                }
            )
        else:
            old_evaluation = v61.evaluate_output(
                frame,
                v61.assemble_program(old_body),
                old_body,
                turn_code=1,
            )
            codes = [
                item["code"] for item in old_evaluation["violations"]
            ]
            if (
                old_evaluation["disposition"] != "revision_required"
                or codes != [v61.RECOGNISED_INTENT_CODE]
            ):
                raise RepairCohortError(
                    "historical_wrong_form_not_rejected"
                )
            ticket = v61.build_correction_ticket(
                old_body,
                v61.assemble_program(old_body),
                old_evaluation,
            )
            historical_assertions.append(
                {
                    "case_code": case_code,
                    "historical_form_available": True,
                    "historical_form_sha256": v61.canonical_hash(old_body),
                    "v61_disposition": old_evaluation["disposition"],
                    "v61_violation_codes": codes,
                    "correction_ticket_sha256": v61.canonical_hash(ticket),
                    "v61_rejection_required": True,
                }
            )
        attempts, ledgers = _case_ids(case_code)
        identifiers.append(
            {
                "case_code": case_code,
                "attempt_ids": list(attempts),
                "ledger_ids": list(ledgers),
            }
        )
    result: dict[str, Any] = {
        "schema_version": (
            "reception.one.receptionist_first_v61."
            "repair_provider_blocked.v1"
        ),
        "result": (
            "reception_one_receptionist_first_v61_"
            "repair_provider_blocked_pass"
        ),
        "provider_contacted": False,
        "provider_calls_performed": 0,
        "credential_reads_performed": 0,
        "data_class": "authored_synthetic",
        "effect_ceiling": "proposal_only",
        "targeted_development_not_holdout": True,
        "closed_v6_evidence_file_sha256": _file_hash(V6_OCCUPIED_PATH),
        "target_case_codes": list(TARGET_CASE_CODES),
        "target_case_count": len(TARGET_CASE_CODES),
        "contract": {
            "system_instruction_sha256": v61.canonical_hash(
                {"text": v61.SYSTEM_INSTRUCTION}
            ),
            "model_output_schema_file_sha256": _file_hash(
                v61.MODEL_FORM_BODY_SCHEMA_PATH
            ),
            "turn_input_schema_file_sha256": _file_hash(
                v61.TURN_INPUT_SCHEMA_PATH
            ),
            "correction_ticket_schema_file_sha256": _file_hash(
                v61.CORRECTION_TICKET_SCHEMA_PATH
            ),
            "provider_response_schema_sha256": v61.canonical_hash(
                v61.vertex_response_schema()
            ),
            "temperature": v61.TEMPERATURE,
            "thinking_budget": v61.THINKING_BUDGET,
            "include_thoughts": v61.INCLUDE_THOUGHTS,
            "maximum_output_tokens": v61.MAX_OUTPUT_TOKENS,
            "prompt_or_schema_change_within_cohort": False,
            "natural_response_parsed_into_form": False,
            "broker_judgement_repair": False,
            "unknown_novel_composition_closed": False,
        },
        "module_provider_blocked_gate": (
            v61.build_provider_blocked_evidence()
        ),
        "case_oracles": oracles,
        "historical_v6_assertions": historical_assertions,
        "single_use_identifiers": identifiers,
        "boundary": {
            "raw_provider_request_retained": False,
            "raw_provider_response_retained": False,
            "credentials_or_tokens_retained": False,
            "api_key_information_retained": False,
            "chain_of_thought_retained": False,
            "thinking_token_count_only": True,
            "product_or_database_access": False,
            "appointment_write": False,
            "product_delivery": False,
            "provider_tools": False,
            "fallback": False,
        },
    }
    result["evidence_hash"] = _content_hash(result)
    return result


def _validate_provider_blocked() -> dict[str, dict[str, Any]]:
    recorded = _load(PROVIDER_BLOCKED_PATH)
    expected = build_provider_blocked_evidence(write_frames=False)
    if (
        recorded != expected
        or recorded.get("evidence_hash") != _content_hash(recorded)
    ):
        raise RepairCohortError("provider_blocked_binding_changed")
    return {
        item["case_code"]: item for item in recorded["case_oracles"]
    }


def _load_closed_dialogue(
    *,
    case_dir: Path,
    attempt_ids: tuple[str, str],
    ledger_ids: tuple[str, str],
    graph_revision: int,
    compass_revision: int,
) -> dict[str, Any] | None:
    parent_path = case_dir / "occupied-dialogue-evidence.json"
    if not parent_path.exists():
        if case_dir.exists() and any(case_dir.iterdir()):
            raise RepairCohortError(
                "partial_case_requires_independent_closeout"
            )
        return None
    dialogue = _load(parent_path)
    unhashed = copy.deepcopy(dialogue)
    retained_hash = unhashed.pop("evidence_hash", None)
    actual_calls = dialogue.get("actual_provider_call_count")
    if (
        retained_hash != lane.canonical_hash(unhashed)
        or dialogue.get("schema_version")
        != v61.PARENT_EVIDENCE_SCHEMA_VERSION
        or dialogue.get("dialogue_protocol") != v61.DIALOGUE_PROTOCOL
        or dialogue.get("model_response_contract")
        != v61.MODEL_RESPONSE_CONTRACT
        or actual_calls not in {1, 2}
        or dialogue.get("attempt_ids")
        != list(attempt_ids[:actual_calls])
        or dialogue.get("ledger_ids") != list(ledger_ids[:actual_calls])
    ):
        raise RepairCohortError("closed_case_resume_binding_invalid")
    expected_files = {
        "occupied-dialogue-parent-audit.jsonl",
        "occupied-dialogue-evidence.json",
    }
    for index in range(1, actual_calls + 1):
        expected_files.update(
            {
                f"occupied-turn-{index:03d}-evidence.json",
                f"occupied-turn-{index:03d}-ledger.json",
                f"occupied-turn-{index:03d}-audit.jsonl",
                f"occupied-turn-{index:03d}-external-audit.json",
            }
        )
        if index == 1 and actual_calls == 2:
            expected_files.add(
                "occupied-turn-001-correction-ticket.json"
            )
        turn = _load(
            case_dir / f"occupied-turn-{index:03d}-evidence.json"
        )
        gate = turn.get("precall_gate") or {}
        ledger = _load(
            case_dir / f"occupied-turn-{index:03d}-ledger.json"
        )
        if (
            turn.get("attempt_id") != attempt_ids[index - 1]
            or turn.get("ledger_id") != ledger_ids[index - 1]
            or turn.get("provider_call_count") != 1
            or gate.get("continuity_graph_revision") != graph_revision
            or gate.get("compass_map_revision") != compass_revision
            or gate.get("compass_source_graph_revision") != graph_revision
            or ledger.get("status") != "consumed"
        ):
            raise RepairCohortError("closed_case_resume_binding_invalid")
    actual_files = {
        path.name for path in case_dir.iterdir() if path.is_file()
    }
    if actual_files != expected_files:
        raise RepairCohortError("closed_case_resume_binding_invalid")
    return dialogue


def _turn_entry(
    case_dir: Path,
    index: int,
    dialogue: dict[str, Any],
) -> dict[str, Any]:
    audit = _load(
        case_dir / f"occupied-turn-{index:03d}-external-audit.json"
    )
    return {
        "turn": index,
        "provider_status": audit["provider_outcome"]["status"],
        "receptionist_output": audit.get("receptionist_output"),
        "typed_form": (
            (audit.get("typed_program") or {}).get(
                "explicit_source_form"
            )
        ),
        "proofreader": audit.get("proofreader"),
        "usage": audit["provider_outcome"].get("usage", {}),
        "release": audit.get("release"),
        "attempt_id": dialogue["attempt_ids"][index - 1],
        "ledger_id": dialogue["ledger_ids"][index - 1],
    }


def _render_notebook(
    entries: list[dict[str, Any]],
    *,
    status: str,
) -> None:
    calls = sum(len(entry["turns"]) for entry in entries)
    usage = {
        "promptTokenCount": 0,
        "candidatesTokenCount": 0,
        "thoughtsTokenCount": 0,
        "totalTokenCount": 0,
    }
    for entry in entries:
        for turn in entry["turns"]:
            for key in usage:
                usage[key] += turn["usage"].get(key, 0)
    lines = [
        "# Reception One v6.1 Targeted Repair Notebook",
        "",
        f"Status: {status}  ",
        f"Cases closed: {len(entries)} / {len(TARGET_CASE_CODES)}  ",
        f"Provider calls consumed: {calls} / {ABSOLUTE_CALL_CEILING}  ",
        (
            "Usage: "
            f"{usage['promptTokenCount']} prompt, "
            f"{usage['candidatesTokenCount']} visible candidate, "
            f"{usage['thoughtsTokenCount']} thinking, "
            f"{usage['totalTokenCount']} total tokens"
        ),
        "",
        "This notebook retains sanitized natural receptionist text, typed "
        "forms, proofreader findings and usage counts. It excludes raw "
        "provider packets, credentials, API-key information and hidden "
        "chain-of-thought.",
        "",
    ]
    for number, entry in enumerate(entries, start=1):
        lines.extend(
            [
                f"## {number}. {entry['case_code']}",
                "",
                "Authored-synthetic input:",
                "",
            ]
        )
        lines.extend(f"- {text}" for text in entry["utterances"])
        for turn in entry["turns"]:
            lines.extend(
                [
                    "",
                    (
                        f"### Turn {turn['turn']} - "
                        f"{turn['provider_status']}"
                    ),
                    "",
                    "```json",
                    json.dumps(
                        {
                            "receptionist_output": turn[
                                "receptionist_output"
                            ],
                            "typed_form": turn["typed_form"],
                            "proofreader": turn["proofreader"],
                            "usage": turn["usage"],
                            "release": turn["release"],
                        },
                        ensure_ascii=False,
                        indent=2,
                        sort_keys=True,
                    ),
                    "```",
                ]
            )
        lines.extend(
            [
                "",
                "Result:",
                "",
                "```json",
                json.dumps(
                    {
                        "v6_terminal_status": entry[
                            "v6_terminal_status"
                        ],
                        "v61_terminal_status": entry[
                            "v61_terminal_status"
                        ],
                        "exact_expected_outcome": entry[
                            "exact_expected_outcome"
                        ],
                        "correction_used": entry["correction_used"],
                    },
                    indent=2,
                    sort_keys=True,
                ),
                "```",
                "",
            ]
        )
    NOTEBOOK_PATH.write_text(
        "\n".join(lines).rstrip() + "\n",
        encoding="utf-8",
        newline="\n",
    )


def run_occupied(
    *,
    preflight_path: Path,
    authority_path: Path,
    graph_revision: int,
    compass_revision: int,
) -> dict[str, Any]:
    cases, v6_rows = _source()
    oracles = _validate_provider_blocked()
    if OCCUPIED_PATH.exists():
        raise RepairCohortError("occupied_cohort_output_already_exists")
    observations: list[dict[str, Any]] = []
    notebook: list[dict[str, Any]] = []
    total_calls = 0
    with _v61_contract():
        for case in cases:
            code = case["case_code"]
            case_dir = ARTIFACT_DIR / "cases" / code
            attempts, ledgers = _case_ids(code)
            dialogue = _load_closed_dialogue(
                case_dir=case_dir,
                attempt_ids=attempts,
                ledger_ids=ledgers,
                graph_revision=graph_revision,
                compass_revision=compass_revision,
            )
            source = "resumed_closed_evidence"
            if dialogue is None:
                dialogue = parent_live.run_dialogue(
                    artifact_dir=case_dir,
                    preflight_path=preflight_path,
                    authority_path=authority_path,
                    expected_graph_revision=graph_revision,
                    expected_compass_revision=compass_revision,
                    frame_path=FRAMES_DIR / f"{code}.json",
                    attempt_ids=attempts,
                    ledger_ids=ledgers,
                )
                source = "new_occupied_dialogue"
            observation = v6_cohort._case_observation(
                case=case,
                oracle=oracles[code],
                case_dir=case_dir,
                dialogue=dialogue,
            )
            total_calls += observation["actual_provider_calls"]
            if total_calls > ABSOLUTE_CALL_CEILING:
                raise RepairCohortError("cohort_call_ceiling_exceeded")
            observations.append(observation)
            turns = [
                _turn_entry(case_dir, index, dialogue)
                for index in range(
                    1, dialogue["actual_provider_call_count"] + 1
                )
            ]
            notebook.append(
                {
                    "case_code": code,
                    "utterances": v6_cohort.frame_for_case(case)[
                        "utterances"
                    ],
                    "turns": turns,
                    "v6_terminal_status": v6_rows[code][
                        "terminal_status"
                    ],
                    "v61_terminal_status": observation[
                        "terminal_status"
                    ],
                    "exact_expected_outcome": observation[
                        "expected_safe_outcome"
                    ],
                    "correction_used": observation["correction_used"],
                }
            )
            _render_notebook(
                notebook,
                status=f"running - closed {code}",
            )
            print(
                json.dumps(
                    {
                        "case_closed": code,
                        "cases_closed": len(notebook),
                        "provider_calls": total_calls,
                        "case_source": source,
                        "exact_expected_outcome": observation[
                            "expected_safe_outcome"
                        ],
                    },
                    sort_keys=True,
                ),
                flush=True,
            )
    passed = all(
        row["expected_safe_outcome"] and row["cleanup_passed"]
        for row in observations
    )
    result: dict[str, Any] = {
        "schema_version": (
            "reception.one.receptionist_first_v61."
            "targeted_repair_cohort.v1"
        ),
        "result": (
            "reception_one_receptionist_first_v61_targeted_repair_pass"
            if passed
            else "reception_one_receptionist_first_v61_"
            "targeted_repair_fail_closed"
        ),
        "capability_threshold_passed": passed,
        "targeted_development_not_holdout": True,
        "data_class": "authored_synthetic",
        "effect_ceiling": "proposal_only",
        "case_count": len(observations),
        "target_case_codes": list(TARGET_CASE_CODES),
        "total_actual_provider_calls": total_calls,
        "absolute_provider_call_ceiling": ABSOLUTE_CALL_CEILING,
        "incremental_cost_ceiling_usd": 1,
        "continuity_binding": {
            "graph_revision": graph_revision,
            "compass_revision": compass_revision,
            "prompt_or_schema_change_within_cohort": False,
        },
        "generation": {
            "temperature": v61.TEMPERATURE,
            "thinking_budget": v61.THINKING_BUDGET,
            "include_thoughts": v61.INCLUDE_THOUGHTS,
        },
        "cases": observations,
        "all_ledgers_consumed": all(
            all(
                _load(path).get("status") == "consumed"
                for path in (
                    ARTIFACT_DIR / "cases" / row["case_code"]
                ).glob("*-ledger.json")
            )
            for row in observations
        ),
        "all_cleanup_passed": all(
            row["cleanup_passed"] for row in observations
        ),
        "explicit_exclusions": {
            "raw_prompt_recorded": False,
            "raw_provider_response_recorded": False,
            "credential_or_token_recorded": False,
            "api_key_information_recorded": False,
            "chain_of_thought_recorded": False,
            "thought_summary_requested": False,
            "natural_response_parsed_into_form": False,
            "product_or_database_access": False,
            "appointment_write": False,
            "human_or_product_delivery": False,
            "provider_or_regional_fallback": False,
        },
    }
    result["evidence_hash"] = _content_hash(result)
    _write_json(OCCUPIED_PATH, result)
    _render_notebook(notebook, status="complete")
    return result


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
            _write_json(PROVIDER_BLOCKED_PATH, evidence)
        else:
            evidence = run_occupied(
                preflight_path=args.preflight,
                authority_path=args.authority,
                graph_revision=args.graph_revision,
                compass_revision=args.compass_revision,
            )
    except (
        RepairCohortError,
        parent_live.PreprintedLiveError,
        lane.ModelLaneError,
        ValueError,
    ) as error:
        print(
            json.dumps(
                {
                    "result": (
                        "reception_one_receptionist_first_v61_blocked"
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
                    "case_count", len(TARGET_CASE_CODES)
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
