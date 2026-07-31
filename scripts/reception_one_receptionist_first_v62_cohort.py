#!/usr/bin/env python3
"""Run the full 24-case receptionist-first v6.2 desk-context cohort."""

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
from scripts import reception_one_bureau_model_text_lane_audit as turn_audit
from scripts import reception_one_bureau_model_text_lane_broker as broker
from scripts import reception_one_bureau_model_text_lane_live as turn_live
from scripts import reception_one_bureau_typed_plan_protocol as typed_plan
from scripts import reception_one_preprinted_form_v5_live as parent_live
from scripts import reception_one_preprinted_form_v5_multicase as v5_cohort
from scripts import reception_one_receptionist_first_v6_cohort as v6_cohort
from scripts import reception_one_receptionist_first_v61_repair as v61_repair
from scripts import reception_one_receptionist_first_v62 as v62
from scripts import reception_one_structured_source_plan_language as structured


ARTIFACT_DIR = v62.ARTIFACT_DIR
VERSION_TAG = "v62"
VERSION_LABEL = "v6.2"
FRAMES_DIR = ARTIFACT_DIR / "frames"
PROVIDER_BLOCKED_PATH = ARTIFACT_DIR / "provider-blocked-evidence.json"
OCCUPIED_PATH = ARTIFACT_DIR / "occupied-cohort-evidence.json"
NOTEBOOK_PATH = ARTIFACT_DIR / "running-test-notebook.md"
AUTHORITY_PATH = ARTIFACT_DIR / "occupied-authority.json"
SOURCE_MANIFEST_PATH = v6_cohort.SOURCE_MANIFEST_PATH
V6_OCCUPIED_PATH = v6_cohort.OCCUPIED_PATH
V61_PROVIDER_BLOCKED_PATH = v61_repair.PROVIDER_BLOCKED_PATH
EXPECTED_CASE_CODES = v6_cohort.EXPECTED_CASE_CODES
ABSOLUTE_CALL_CEILING = len(EXPECTED_CASE_CODES) * 2
PAIRED_DEVELOPMENT_NOT_HOLDOUT = True
ALL_ORIGINAL_V6_CASES_INCLUDED = True
OCCUPIED_RESULT_PASS = (
    f"reception_one_receptionist_first_{VERSION_TAG}_full_cohort_pass"
)
OCCUPIED_RESULT_FAIL = (
    f"reception_one_receptionist_first_{VERSION_TAG}_full_cohort_fail_closed"
)


class V62CohortError(RuntimeError):
    """A v6.2 cohort contract, lifecycle or audit rejection."""


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
        raise V62CohortError("json_object_unreadable") from error
    if not isinstance(value, dict):
        raise V62CohortError("json_object_required")
    return value


def _file_hash(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _content_hash(value: dict[str, Any]) -> str:
    clean = copy.deepcopy(value)
    clean.pop("evidence_hash", None)
    return v62.canonical_hash(clean)


@contextmanager
def _v62_contract() -> Iterator[None]:
    old_cohort = v5_cohort.preprinted
    old_parent = parent_live.preprinted
    old_v6_module = v6_cohort.v6
    v5_cohort.preprinted = v62
    parent_live.preprinted = v62
    v6_cohort.v6 = v62
    try:
        yield
    finally:
        v5_cohort.preprinted = old_cohort
        parent_live.preprinted = old_parent
        v6_cohort.v6 = old_v6_module


def load_source_manifest() -> tuple[dict[str, Any], list[dict[str, Any]]]:
    document, cases = v6_cohort.load_source_manifest()
    if tuple(case["case_code"] for case in cases) != EXPECTED_CASE_CODES:
        raise V62CohortError("source_case_order_changed")
    return document, cases


def frame_for_case(case: dict[str, Any]) -> dict[str, Any]:
    return v6_cohort.frame_for_case(case)


def _case_ids(case_code: str) -> tuple[tuple[str, str], tuple[str, str]]:
    attempts = tuple(
        f"reception-one-receptionist-first-{VERSION_TAG}-eval-"
        f"{case_code}-turn-{index:03d}"
        for index in (1, 2)
    )
    ledgers = tuple(
        f"reception-one-receptionist-first-{VERSION_TAG}-eval-"
        f"{case_code}-ledger-{index:03d}"
        for index in (1, 2)
    )
    for attempt_id, ledger_id in zip(attempts, ledgers, strict=True):
        broker.validate_attempt_ledger_pair(attempt_id, ledger_id)
    return attempts, ledgers


def _oracle(case: dict[str, Any], frame: dict[str, Any]) -> dict[str, Any]:
    plan = typed_plan.deterministic_plan(frame)
    if plan["goal"] != case["expected_goal"]:
        raise V62CohortError("oracle_goal_mismatch")
    program = structured.program_from_plan(
        frame,
        plan,
        operator_note=v6_cohort.v5_cohort._operator_note(plan["goal"]),
    )
    body = v62.model_form_body(program, frame=frame)
    assembled = v62.assemble_program(body)
    turn_input = v62.build_turn_input(frame)
    evaluation = v62.evaluate_output(
        frame,
        assembled,
        body,
        turn_code=1,
        turn_input=turn_input,
    )
    if (
        evaluation["disposition"] != "admit"
        or evaluation["context_frame_review"]["disposition"] != "admit"
    ):
        raise V62CohortError("provider_free_oracle_not_admitted")
    release = typed_plan.execute_plan(
        frame,
        evaluation["normalized_plan"],
        evaluation["semantic_review"],
    )["final_output"]
    return {
        "case_code": case["case_code"],
        "frame_sha256": v62.canonical_hash(frame),
        "turn_input_sha256": v62.canonical_hash(turn_input),
        "task_sha256": turn_input["task_sha256"],
        "desk_context_sha256": turn_input["desk_context_sha256"],
        "provider_request_sha256": v62.canonical_hash(
            v62.build_vertex_request(turn_input)
        ),
        "provider_response_schema_sha256": v62.canonical_hash(
            v62.vertex_response_schema()
        ),
        "oracle_goal": plan["goal"],
        "oracle_program_sha256": v62.canonical_hash(program),
        "oracle_typed_form_sha256": v62.canonical_hash(body["typed_form"]),
        "proofreader_disposition": evaluation["disposition"],
        "context_frame_review": evaluation["context_frame_review"],
        "expected_proposal_release": case["expected_proposal_release"],
        "expected_final_output": release,
    }


def build_provider_blocked_evidence(*, write_frames: bool) -> dict[str, Any]:
    manifest, cases = load_source_manifest()
    v61_recorded = _load(V61_PROVIDER_BLOCKED_PATH)
    v61_expected = v61_repair.build_provider_blocked_evidence(
        write_frames=False
    )
    if v61_recorded != v61_expected:
        raise V62CohortError("v61_historical_assertion_binding_changed")
    historical_rejections = [
        row
        for row in v61_recorded["historical_v6_assertions"]
        if row["v61_rejection_required"]
    ]
    if (
        len(historical_rejections) != 14
        or not all(
            row["v61_disposition"] == "revision_required"
            and row["v61_violation_codes"]
            == ["recognized_intent_goal_mismatch"]
            for row in historical_rejections
        )
    ):
        raise V62CohortError("v61_historical_rejections_invalid")
    v6_occupied = _load(V6_OCCUPIED_PATH)
    v6_pass_codes = [
        row["case_code"]
        for row in v6_occupied["cases"]
        if row["expected_safe_outcome"]
    ]
    if len(v6_pass_codes) != 9:
        raise V62CohortError("v6_pass_non_regression_set_invalid")
    oracles: list[dict[str, Any]] = []
    identifiers: list[dict[str, Any]] = []
    for case in cases:
        frame = frame_for_case(case)
        if write_frames:
            _write_json(FRAMES_DIR / f"{case['case_code']}.json", frame)
        oracles.append(_oracle(case, frame))
        attempts, ledgers = _case_ids(case["case_code"])
        identifiers.append(
            {
                "case_code": case["case_code"],
                "attempt_ids": list(attempts),
                "ledger_ids": list(ledgers),
            }
        )
    module_gate = v62.build_provider_blocked_evidence()
    result: dict[str, Any] = {
        "schema_version": (
            f"reception.one.receptionist_first_{VERSION_TAG}."
            "cohort_provider_blocked.v1"
        ),
        "result": (
            f"reception_one_receptionist_first_{VERSION_TAG}_"
            "cohort_provider_blocked_pass"
        ),
        "provider_contacted": False,
        "provider_calls_performed": 0,
        "credential_reads_performed": 0,
        "data_class": "authored_synthetic",
        "effect_ceiling": "proposal_only",
        "paired_development_not_holdout": PAIRED_DEVELOPMENT_NOT_HOLDOUT,
        "all_original_v6_cases_included": ALL_ORIGINAL_V6_CASES_INCLUDED,
        "source_manifest_file_sha256": _file_hash(SOURCE_MANIFEST_PATH),
        "source_manifest_content_sha256": v62.canonical_hash(manifest),
        "source_case_count": len(cases),
        "source_case_codes": list(EXPECTED_CASE_CODES),
        "contract": {
            "system_instruction_sha256": v62.canonical_hash(
                {"text": v62.SYSTEM_INSTRUCTION}
            ),
            "model_output_schema_file_sha256": _file_hash(
                v62.MODEL_FORM_BODY_SCHEMA_PATH
            ),
            "turn_input_schema_file_sha256": _file_hash(
                v62.TURN_INPUT_SCHEMA_PATH
            ),
            "desk_context_schema_file_sha256": _file_hash(
                v62.DESK_CONTEXT_SCHEMA_PATH
            ),
            "correction_ticket_schema_file_sha256": _file_hash(
                v62.CORRECTION_TICKET_SCHEMA_PATH
            ),
            "provider_response_schema_sha256": v62.canonical_hash(
                v62.vertex_response_schema()
            ),
            "temperature": v62.TEMPERATURE,
            "thinking_budget": v62.THINKING_BUDGET,
            "include_thoughts": v62.INCLUDE_THOUGHTS,
            "maximum_output_tokens": v62.MAX_OUTPUT_TOKENS,
            "prompt_or_schema_change_within_cohort": False,
            "natural_response_parsed_into_form": False,
            "broker_judgement_repair": False,
        },
        "module_provider_blocked_gate": module_gate,
        "case_oracles": oracles,
        "single_use_identifiers": identifiers,
        "non_regression": {
            "v61_historical_wrong_forms_revalidated": len(
                historical_rejections
            ),
            "v61_historical_assertion_file_sha256": _file_hash(
                V61_PROVIDER_BLOCKED_PATH
            ),
            "v6_prior_pass_case_count": len(v6_pass_codes),
            "v6_prior_pass_case_codes": v6_pass_codes,
            "v6_occupied_evidence_file_sha256": _file_hash(
                V6_OCCUPIED_PATH
            ),
        },
        "call_budget": {
            "primary_call_per_case": 1,
            "maximum_terminal_second_call_per_case": 1,
            "absolute_provider_call_ceiling": ABSOLUTE_CALL_CEILING,
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
    result["evidence_hash"] = _content_hash(result)
    return result


def _validate_provider_blocked() -> dict[str, dict[str, Any]]:
    recorded = _load(PROVIDER_BLOCKED_PATH)
    expected = build_provider_blocked_evidence(write_frames=False)
    if (
        recorded != expected
        or recorded.get("evidence_hash") != _content_hash(recorded)
    ):
        raise V62CohortError("provider_blocked_binding_changed")
    return {row["case_code"]: row for row in recorded["case_oracles"]}


def _replay_paths(case_dir: Path) -> tuple[Path, Path]:
    return (
        case_dir / "occupied-exact-replay-parent-audit.jsonl",
        case_dir / "occupied-exact-replay-evidence.json",
    )


def _load_exact_replay(
    *,
    case_dir: Path,
    attempt_ids: tuple[str, str],
    ledger_ids: tuple[str, str],
    graph_revision: int,
    compass_revision: int,
) -> dict[str, Any] | None:
    audit_path, evidence_path = _replay_paths(case_dir)
    if not evidence_path.exists():
        if audit_path.exists():
            raise V62CohortError("partial_exact_replay_evidence")
        return None
    evidence = _load(evidence_path)
    unhashed = copy.deepcopy(evidence)
    retained_hash = unhashed.pop("evidence_hash", None)
    expected_files = {
        "occupied-dialogue-parent-audit.jsonl",
        "occupied-dialogue-evidence.json",
        "occupied-turn-001-evidence.json",
        "occupied-turn-001-ledger.json",
        "occupied-turn-001-audit.jsonl",
        "occupied-turn-001-external-audit.json",
        "occupied-turn-002-evidence.json",
        "occupied-turn-002-ledger.json",
        "occupied-turn-002-audit.jsonl",
        "occupied-turn-002-external-audit.json",
        "occupied-exact-replay-parent-audit.jsonl",
        "occupied-exact-replay-evidence.json",
    }
    actual_files = {
        path.name for path in case_dir.iterdir() if path.is_file()
    }
    if (
        retained_hash != lane.canonical_hash(unhashed)
        or evidence.get("schema_version")
        != v62.PARENT_EVIDENCE_SCHEMA_VERSION
        or evidence.get("dialogue_protocol") != v62.DIALOGUE_PROTOCOL
        or evidence.get("actual_provider_call_count") != 2
        or evidence.get("attempt_ids") != list(attempt_ids)
        or evidence.get("ledger_ids") != list(ledger_ids)
        or actual_files != expected_files
    ):
        raise V62CohortError("closed_exact_replay_binding_invalid")
    for index in (1, 2):
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
            or ledger.get("status") != "consumed"
            or ledger.get("provider_calls_consumed") != 1
            or not all(
                value
                for key, value in turn.get("cleanup", {}).items()
                if key != "daemon_wide_prune_performed"
            )
        ):
            raise V62CohortError("closed_exact_replay_binding_invalid")
    return evidence


def _run_exact_replay(
    *,
    case_dir: Path,
    preflight_path: Path,
    authority_path: Path,
    frame_path: Path,
    attempt_ids: tuple[str, str],
    ledger_ids: tuple[str, str],
    graph_revision: int,
    compass_revision: int,
) -> dict[str, Any]:
    replay_audit_path, replay_evidence_path = _replay_paths(case_dir)
    second_paths = [
        case_dir / "occupied-turn-002-evidence.json",
        case_dir / "occupied-turn-002-ledger.json",
        case_dir / "occupied-turn-002-audit.jsonl",
        case_dir / "occupied-turn-002-external-audit.json",
        replay_audit_path,
        replay_evidence_path,
    ]
    if any(path.exists() for path in second_paths):
        raise V62CohortError("exact_replay_output_already_exists")
    first = _load(case_dir / "occupied-turn-001-evidence.json")
    first_external = _load(
        case_dir / "occupied-turn-001-external-audit.json"
    )
    first_outcome = first_external.get("provider_outcome") or {}
    if (
        first.get("provider_call_count") != 1
        or first.get("exchange", {}).get("release") is not None
        or first.get("exchange", {}).get("correction_ticket") is not None
        or first_outcome.get("status")
        != "response_rejected_before_candidate"
        or (first_outcome.get("bounded_error") or {}).get("reason_code")
        != "provider_text_not_json"
    ):
        raise V62CohortError("exact_replay_not_eligible")
    second_evidence_path = second_paths[0]
    second_ledger_path = second_paths[1]
    second_audit_path = second_paths[2]
    second_external_path = second_paths[3]
    second = turn_live.run_live(
        evidence_path=second_evidence_path,
        ledger_path=second_ledger_path,
        audit_path=second_audit_path,
        attempt_id=attempt_ids[1],
        ledger_id=ledger_ids[1],
        preflight_path=preflight_path,
        authority_path=authority_path,
        expected_graph_revision=graph_revision,
        expected_compass_revision=compass_revision,
        frame_path=frame_path,
        contract_mode=v62.CONTRACT_MODE,
        correction_ticket_path=None,
    )
    second_external = turn_audit.build_external_audit(
        second_evidence_path,
        second_audit_path,
        preflight_path,
    )
    _write_json(second_external_path, second_external)
    parent_events: list[dict[str, Any]] = []
    parent_live._append_parent_event(
        replay_audit_path,
        parent_events,
        "dialogue_opened",
        {
            "dialogue_protocol": v62.DIALOGUE_PROTOCOL,
            "maximum_actual_provider_calls": 2,
            "incremental_cost_ceiling_usd": 1,
            "exact_pre_schema_replay": True,
            "prompt_or_schema_change": False,
        },
    )
    for index, turn in enumerate((first, second), start=1):
        parent_live._append_parent_event(
            replay_audit_path,
            parent_events,
            "turn_closed",
            {
                "turn_code": index,
                "attempt_id": turn["attempt_id"],
                "ledger_id": turn["ledger_id"],
                "result": turn["result"],
                "audit_terminal_hash": turn["exchange"][
                    "audit_terminal_hash"
                ],
                "proofreader_disposition": (
                    turn["exchange"].get("proofreader") or {}
                ).get("disposition"),
                "released": turn["exchange"].get("release") is not None,
                "cleanup_passed": all(
                    value
                    for key, value in turn["cleanup"].items()
                    if key != "daemon_wide_prune_performed"
                ),
                "exact_request_replay": index == 2,
            },
        )
    parent_live._append_parent_event(
        replay_audit_path,
        parent_events,
        "dialogue_closed",
        {
            "status": (
                "admitted_after_correction"
                if second["exchange"].get("release") is not None
                else "terminal_no_release"
            ),
            "actual_provider_calls": 2,
            "third_call_performed": False,
            "fallback_performed": False,
            "exact_pre_schema_replay": True,
        },
    )
    combined = parent_live.build_parent_evidence(
        turns=[first, second],
        external_audits=[first_external, second_external],
        parent_events=parent_events,
        attempt_ids=attempt_ids,
        ledger_ids=ledger_ids,
    )
    combined["evidence_hash"] = lane.canonical_hash(combined)
    _write_json(replay_evidence_path, combined)
    return combined


def _load_dialogue(
    *,
    case_dir: Path,
    attempt_ids: tuple[str, str],
    ledger_ids: tuple[str, str],
    graph_revision: int,
    compass_revision: int,
) -> dict[str, Any] | None:
    replay = _load_exact_replay(
        case_dir=case_dir,
        attempt_ids=attempt_ids,
        ledger_ids=ledger_ids,
        graph_revision=graph_revision,
        compass_revision=compass_revision,
    )
    if replay is not None:
        return replay
    return v6_cohort._load_closed_dialogue(
        case_dir=case_dir,
        attempt_ids=attempt_ids,
        ledger_ids=ledger_ids,
        expected_graph_revision=graph_revision,
        expected_compass_revision=compass_revision,
    )


def _render_notebook(
    rows: list[dict[str, Any]],
    *,
    status: str,
) -> None:
    calls = sum(row["actual_provider_calls"] for row in rows)
    lines = [
        f"# Reception One {VERSION_LABEL} Full-Cohort Test Notebook",
        "",
        f"Status: {status}  ",
        f"Cases closed: {len(rows)} / {len(EXPECTED_CASE_CODES)}  ",
        f"Provider calls consumed: {calls} / {ABSOLUTE_CALL_CEILING}  ",
        "",
        (
            "This is a sanitized authored-synthetic comparison notebook, not "
            "a raw provider log. It includes all original v6 requests. Raw "
            "provider packets, credentials, API-key information and hidden "
            "chain-of-thought are excluded."
        ),
        "",
    ]
    for index, row in enumerate(rows, start=1):
        lines.extend(
            [
                f"## {index}. {row['case_code']}",
                "",
                "```json",
                json.dumps(row, indent=2, ensure_ascii=False, sort_keys=True),
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
    _, cases = load_source_manifest()
    oracles = _validate_provider_blocked()
    if OCCUPIED_PATH.exists():
        raise V62CohortError("occupied_cohort_output_already_exists")
    observations: list[dict[str, Any]] = []
    total_calls = 0
    with _v62_contract():
        for case in cases:
            code = case["case_code"]
            case_dir = ARTIFACT_DIR / "cases" / code
            attempts, ledgers = _case_ids(code)
            dialogue = _load_dialogue(
                case_dir=case_dir,
                attempt_ids=attempts,
                ledger_ids=ledgers,
                graph_revision=graph_revision,
                compass_revision=compass_revision,
            )
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
            first_external = _load(
                case_dir / "occupied-turn-001-external-audit.json"
            )
            first_outcome = first_external.get("provider_outcome") or {}
            exact_replay_eligible = (
                dialogue.get("actual_provider_call_count") == 1
                and dialogue.get("release") is None
                and dialogue.get("terminal_status") == "terminal_no_release"
                and first_outcome.get("status")
                == "response_rejected_before_candidate"
                and (first_outcome.get("bounded_error") or {}).get(
                    "reason_code"
                )
                == "provider_text_not_json"
            )
            if exact_replay_eligible:
                dialogue = _run_exact_replay(
                    case_dir=case_dir,
                    preflight_path=preflight_path,
                    authority_path=authority_path,
                    frame_path=FRAMES_DIR / f"{code}.json",
                    attempt_ids=attempts,
                    ledger_ids=ledgers,
                    graph_revision=graph_revision,
                    compass_revision=compass_revision,
                )
            observation = v6_cohort._case_observation(
                case=case,
                oracle=oracles[code],
                case_dir=case_dir,
                dialogue=dialogue,
            )
            turn_evidence = [
                _load(
                    case_dir / f"occupied-turn-{index:03d}-evidence.json"
                )
                for index in range(
                    1, dialogue["actual_provider_call_count"] + 1
                )
            ]
            context_review = next(
                (
                    proofreader["context_frame_review"]
                    for turn in reversed(turn_evidence)
                    if isinstance(
                        proofreader := (
                            turn.get("exchange", {}).get("proofreader")
                        ),
                        dict,
                    )
                    and isinstance(
                        proofreader.get("context_frame_review"), dict
                    )
                ),
                None,
            )
            if context_review is None:
                model_input_hashes = [
                    turn["exchange"]["model_input_hash"]
                    for turn in turn_evidence
                ]
                if (
                    dialogue.get("release") is not None
                    or any(
                        value != oracles[code]["turn_input_sha256"]
                        for value in model_input_hashes
                    )
                ):
                    raise V62CohortError(
                        "occupied_context_hash_binding_invalid"
                    )
                context_review = {
                    "disposition": "not_reached",
                    "reason": "provider_response_rejected_before_candidate",
                    "desk_context_sha256": oracles[code][
                        "desk_context_sha256"
                    ],
                    "same_packet_seen_by_model_and_proofreader": False,
                    "release": None,
                }
            elif (
                context_review.get(
                    "same_packet_seen_by_model_and_proofreader"
                )
                is not True
                or context_review.get("desk_context_sha256")
                != oracles[code]["desk_context_sha256"]
            ):
                raise V62CohortError("occupied_context_hash_binding_invalid")
            observation["context_frame_review"] = context_review
            observation["terminal_second_call_reason"] = (
                "exact_pre_schema_replay"
                if exact_replay_eligible
                else "proofreader_correction"
                if observation["actual_provider_calls"] == 2
                else None
            )
            observations.append(observation)
            total_calls += observation["actual_provider_calls"]
            if total_calls > ABSOLUTE_CALL_CEILING:
                raise V62CohortError("cohort_call_ceiling_exceeded")
            _render_notebook(
                observations,
                status=f"running - closed {code}",
            )
            print(
                json.dumps(
                    {
                        "case_closed": code,
                        "cases_closed": len(observations),
                        "provider_calls": total_calls,
                        "expected_safe_outcome": observation[
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
            f"reception.one.receptionist_first_{VERSION_TAG}.full_cohort.v1"
        ),
        "result": OCCUPIED_RESULT_PASS if passed else OCCUPIED_RESULT_FAIL,
        "capability_threshold_passed": passed,
        "paired_development_not_holdout": PAIRED_DEVELOPMENT_NOT_HOLDOUT,
        "all_original_v6_cases_included": ALL_ORIGINAL_V6_CASES_INCLUDED,
        "data_class": "authored_synthetic",
        "effect_ceiling": "proposal_only",
        "case_count": len(observations),
        "total_actual_provider_calls": total_calls,
        "absolute_provider_call_ceiling": ABSOLUTE_CALL_CEILING,
        "incremental_cost_ceiling_usd": 1,
        "continuity_binding": {
            "graph_revision": graph_revision,
            "compass_revision": compass_revision,
            "prompt_or_schema_change_within_cohort": False,
        },
        "generation": {
            "temperature": v62.TEMPERATURE,
            "thinking_budget": v62.THINKING_BUDGET,
            "include_thoughts": v62.INCLUDE_THOUGHTS,
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
            "full_diary_exposed": False,
            "unselected_appointments_exposed": False,
            "product_or_database_access": False,
            "appointment_write": False,
            "human_or_product_delivery": False,
            "provider_or_regional_fallback": False,
        },
    }
    result["evidence_hash"] = _content_hash(result)
    _write_json(OCCUPIED_PATH, result)
    _render_notebook(observations, status="complete")
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
        V62CohortError,
        v6_cohort.ReceptionistCohortError,
        parent_live.PreprintedLiveError,
        lane.ModelLaneError,
        ValueError,
    ) as error:
        print(
            json.dumps(
                {
                    "result": (
                        f"reception_one_receptionist_first_{VERSION_TAG}_blocked"
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
