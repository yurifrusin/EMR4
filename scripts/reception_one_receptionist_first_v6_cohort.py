#!/usr/bin/env python3
"""Run the receptionist-first v6 paired development cohort and notebook."""

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
from scripts import reception_one_preprinted_form_v5_broad_language_cohort as v5_broad
from scripts import reception_one_preprinted_form_v5_live as parent_live
from scripts import reception_one_preprinted_form_v5_multicase as v5_cohort
from scripts import reception_one_receptionist_first_v6 as v6
from scripts import reception_one_structured_source_plan_language as structured


ARTIFACT_DIR = v6.ARTIFACT_DIR
SOURCE_MANIFEST_PATH = v5_broad.MANIFEST_PATH
SOURCE_OCCUPIED_PATH = v5_broad.OCCUPIED_PATH
FRAMES_DIR = ARTIFACT_DIR / "frames"
PROVIDER_BLOCKED_PATH = ARTIFACT_DIR / "provider-blocked-evidence.json"
OCCUPIED_PATH = ARTIFACT_DIR / "occupied-cohort-evidence.json"
NOTEBOOK_PATH = ARTIFACT_DIR / "running-test-notebook.md"
AUTHORITY_PATH = ARTIFACT_DIR / "occupied-authority.json"
EXPECTED_CASE_CODES = tuple(item[0] for item in v5_broad.EXPECTED_CASES)
ABSOLUTE_CALL_CEILING = len(EXPECTED_CASE_CODES) * 2
OCCUPIED_RESULT_PASS = (
    "reception_one_receptionist_first_v6_paired_development_pass"
)
OCCUPIED_RESULT_FAIL = (
    "reception_one_receptionist_first_v6_paired_development_fail_closed"
)


class ReceptionistCohortError(RuntimeError):
    """A v6 cohort contract, lifecycle or notebook rejection."""


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _load_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ReceptionistCohortError("json_object_unreadable") from error
    if not isinstance(value, dict):
        raise ReceptionistCohortError("json_object_required")
    return value


def _file_hash(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _content_hash(value: dict[str, Any]) -> str:
    clean = copy.deepcopy(value)
    clean.pop("evidence_hash", None)
    return v6.canonical_hash(clean)


@contextmanager
def _v6_contract() -> Iterator[None]:
    old_cohort = v5_cohort.preprinted
    old_parent = parent_live.preprinted
    v5_cohort.preprinted = v6
    parent_live.preprinted = v6
    try:
        yield
    finally:
        v5_cohort.preprinted = old_cohort
        parent_live.preprinted = old_parent


def load_source_manifest() -> tuple[dict[str, Any], list[dict[str, Any]]]:
    with v5_broad._configured():
        document, cases = v5_cohort.load_manifest()
    if (
        document.get("schema_version")
        != "reception.one.preprinted_form_v5.broad_language_manifest.v1"
        or tuple(case.get("case_code") for case in cases)
        != EXPECTED_CASE_CODES
        or document.get("data_class") != "authored_synthetic"
        or document.get("effect_ceiling") != "proposal_only"
        or document.get("absolute_call_ceiling") != ABSOLUTE_CALL_CEILING
        or document.get("incremental_cost_ceiling_usd") != 1
    ):
        raise ReceptionistCohortError("source_manifest_boundary_invalid")
    return document, cases


def frame_for_case(case: dict[str, Any]) -> dict[str, Any]:
    return v5_broad.frame_for_case(case)


def _case_ids(case_code: str) -> tuple[tuple[str, str], tuple[str, str]]:
    attempts = tuple(
        "reception-one-receptionist-first-v6-eval-"
        f"{case_code}-turn-{index:03d}"
        for index in (1, 2)
    )
    ledgers = tuple(
        "reception-one-receptionist-first-v6-eval-"
        f"{case_code}-ledger-{index:03d}"
        for index in (1, 2)
    )
    for attempt_id, ledger_id in zip(attempts, ledgers, strict=True):
        broker.validate_attempt_ledger_pair(attempt_id, ledger_id)
    return attempts, ledgers


def _oracle_for_case(
    case: dict[str, Any],
    frame: dict[str, Any],
) -> dict[str, Any]:
    plan = typed_plan.deterministic_plan(frame)
    if plan["goal"] != case["expected_goal"]:
        raise ReceptionistCohortError("oracle_goal_mismatch")
    program = structured.program_from_plan(
        frame,
        plan,
        operator_note=v5_cohort._operator_note(plan["goal"]),
    )
    body = v6.model_form_body(program, frame=frame)
    assembled = v6.assemble_program(body)
    evaluation = v6.evaluate_output(
        frame,
        assembled,
        body,
        turn_code=1,
    )
    if evaluation["disposition"] != "admit":
        raise ReceptionistCohortError("provider_free_oracle_not_admitted")
    release = typed_plan.execute_plan(
        frame,
        evaluation["normalized_plan"],
        evaluation["semantic_review"],
    )["final_output"]
    return {
        "case_code": case["case_code"],
        "frame_sha256": v6.canonical_hash(frame),
        "task_sha256": v6.build_turn_input(frame)["task_sha256"],
        "provider_request_sha256": v6.canonical_hash(
            v6.build_vertex_request(v6.build_turn_input(frame))
        ),
        "provider_response_schema_sha256": v6.canonical_hash(
            v6.vertex_response_schema()
        ),
        "oracle_goal": plan["goal"],
        "oracle_program_sha256": v6.canonical_hash(program),
        "oracle_typed_form_sha256": v6.canonical_hash(body["typed_form"]),
        "proofreader_disposition": evaluation["disposition"],
        "expected_proposal_release": case["expected_proposal_release"],
        "expected_final_output": release,
    }


def build_provider_blocked_evidence(
    *,
    write_frames: bool,
) -> dict[str, Any]:
    manifest, cases = load_source_manifest()
    oracles: list[dict[str, Any]] = []
    identifiers: list[dict[str, Any]] = []
    for case in cases:
        frame = frame_for_case(case)
        if write_frames:
            _write_json(FRAMES_DIR / f"{case['case_code']}.json", frame)
        oracles.append(_oracle_for_case(case, frame))
        attempts, ledgers = _case_ids(case["case_code"])
        identifiers.append(
            {
                "case_code": case["case_code"],
                "attempt_ids": list(attempts),
                "ledger_ids": list(ledgers),
            }
        )
    module_gate = v6.build_provider_blocked_evidence()
    result: dict[str, Any] = {
        "schema_version": (
            "reception.one.receptionist_first_v6.cohort_provider_blocked.v1"
        ),
        "result": (
            "reception_one_receptionist_first_v6_cohort_provider_blocked_pass"
        ),
        "provider_contacted": False,
        "provider_calls_performed": 0,
        "credential_reads_performed": 0,
        "data_class": "authored_synthetic",
        "effect_ceiling": "proposal_only",
        "paired_development_not_holdout": True,
        "source_v5_manifest_file_sha256": _file_hash(
            SOURCE_MANIFEST_PATH
        ),
        "source_v5_manifest_content_sha256": v6.canonical_hash(manifest),
        "source_v5_case_count": len(cases),
        "source_v5_case_codes": list(EXPECTED_CASE_CODES),
        "contract": {
            "system_instruction_sha256": v6.canonical_hash(
                {"text": v6.SYSTEM_INSTRUCTION}
            ),
            "model_output_schema_file_sha256": _file_hash(
                v6.MODEL_FORM_BODY_SCHEMA_PATH
            ),
            "turn_input_schema_file_sha256": _file_hash(
                v6.TURN_INPUT_SCHEMA_PATH
            ),
            "correction_ticket_schema_file_sha256": _file_hash(
                v6.CORRECTION_TICKET_SCHEMA_PATH
            ),
            "provider_response_schema_sha256": v6.canonical_hash(
                v6.vertex_response_schema()
            ),
            "temperature": v6.TEMPERATURE,
            "thinking_budget": v6.THINKING_BUDGET,
            "include_thoughts": v6.INCLUDE_THOUGHTS,
            "maximum_output_tokens": v6.MAX_OUTPUT_TOKENS,
            "prompt_or_schema_change_within_cohort": False,
            "natural_response_parsed_into_form": False,
            "broker_judgement_repair": False,
        },
        "module_provider_blocked_gate": module_gate,
        "case_oracles": oracles,
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


def _validate_provider_blocked(
    recorded: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    expected = build_provider_blocked_evidence(write_frames=False)
    if (
        recorded != expected
        or recorded.get("evidence_hash") != _content_hash(recorded)
    ):
        raise ReceptionistCohortError("provider_blocked_binding_changed")
    return {
        item["case_code"]: item for item in recorded["case_oracles"]
    }


def _v5_observations() -> dict[str, dict[str, Any]]:
    source = _load_object(SOURCE_OCCUPIED_PATH)
    if source.get("case_count") != 24:
        raise ReceptionistCohortError("v5_comparison_evidence_invalid")
    return {item["case_code"]: item for item in source["cases"]}


def _turn_notebook_entry(
    case_dir: Path,
    index: int,
    dialogue: dict[str, Any],
) -> dict[str, Any]:
    audit = _load_object(
        case_dir / f"occupied-turn-{index:03d}-external-audit.json"
    )
    return {
        "turn": index,
        "provider_status": audit["provider_outcome"]["status"],
        "receptionist_output": audit.get("receptionist_output"),
        "typed_form": (
            (audit.get("typed_program") or {}).get("explicit_source_form")
        ),
        "operator_note": audit.get("operator_note"),
        "proofreader": audit.get("proofreader"),
        "usage": audit["provider_outcome"].get("usage", {}),
        "release": audit.get("release"),
        "attempt_id": dialogue["attempt_ids"][index - 1],
        "ledger_id": dialogue["ledger_ids"][index - 1],
    }


def _notebook_case(
    *,
    case: dict[str, Any],
    frame: dict[str, Any],
    observation: dict[str, Any],
    dialogue: dict[str, Any],
    v5_observation: dict[str, Any],
) -> dict[str, Any]:
    case_dir = ARTIFACT_DIR / "cases" / case["case_code"]
    turns = [
        _turn_notebook_entry(case_dir, index, dialogue)
        for index in range(1, dialogue["actual_provider_call_count"] + 1)
    ]
    return {
        "case_code": case["case_code"],
        "utterances": frame["utterances"],
        "turns": turns,
        "terminal_status": dialogue["terminal_status"],
        "expected_safe_outcome": observation["expected_safe_outcome"],
        "correction_used": observation["correction_used"],
        "v5": {
            "expected_safe_outcome": v5_observation[
                "expected_safe_outcome"
            ],
            "terminal_status": v5_observation["terminal_status"],
            "correction_used": v5_observation["correction_used"],
            "operator_note": v5_observation.get("operator_note"),
            "typed_program": v5_observation.get("typed_program"),
            "release": v5_observation.get("release"),
            "final_violation_codes": v5_observation.get(
                "final_violation_codes", []
            ),
        },
    }


def _render_notebook(
    entries: list[dict[str, Any]],
    *,
    status: str,
) -> None:
    total_calls = sum(len(entry["turns"]) for entry in entries)
    prompt_tokens = 0
    visible_tokens = 0
    thinking_tokens = 0
    total_tokens = 0
    for entry in entries:
        for turn in entry["turns"]:
            usage = turn["usage"]
            prompt_tokens += usage.get("promptTokenCount", 0)
            visible_tokens += usage.get("candidatesTokenCount", 0)
            thinking_tokens += usage.get("thoughtsTokenCount", 0)
            total_tokens += usage.get("totalTokenCount", 0)
    lines = [
        "# Reception One v6 Running Test Notebook",
        "",
        f"Status: {status}  ",
        "Study: receptionist-first v6 paired development comparison  ",
        f"Cases closed: {len(entries)} / 24  ",
        f"Provider calls consumed: {total_calls} / 48  ",
        (
            "Usage: "
            f"{prompt_tokens} prompt, {visible_tokens} visible candidate, "
            f"{thinking_tokens} thinking, {total_tokens} total tokens"
        ),
        "",
        "This is a sanitized comparison notebook, not a raw provider log. "
        "Full prompts, raw provider packets, credentials, API-key information "
        "and hidden chain-of-thought are excluded.",
        "",
    ]
    for number, entry in enumerate(entries, start=1):
        lines.extend(
            [
                f"## {number}. {entry['case_code']}",
                "",
                "### Authored-synthetic input",
                "",
            ]
        )
        for index, utterance in enumerate(entry["utterances"]):
            lines.append(f"- `{index}` — {utterance}")
        lines.extend(["", "### v6 turns", ""])
        for turn in entry["turns"]:
            lines.extend(
                [
                    (
                        f"#### Turn {turn['turn']} — "
                        f"{turn['provider_status']}"
                    ),
                    "",
                    "Natural receptionist output:",
                    "",
                    "```json",
                    json.dumps(
                        turn["receptionist_output"],
                        indent=2,
                        ensure_ascii=False,
                        sort_keys=True,
                    ),
                    "```",
                    "",
                    "Typed form:",
                    "",
                    "```json",
                    json.dumps(
                        turn["typed_form"],
                        indent=2,
                        ensure_ascii=False,
                        sort_keys=True,
                    ),
                    "```",
                    "",
                    "Proofreader and usage:",
                    "",
                    "```json",
                    json.dumps(
                        {
                            "proofreader": turn["proofreader"],
                            "usage": turn["usage"],
                            "release": turn["release"],
                        },
                        indent=2,
                        ensure_ascii=False,
                        sort_keys=True,
                    ),
                    "```",
                    "",
                ]
            )
        lines.extend(
            [
                "### Paired result",
                "",
                "```json",
                json.dumps(
                    {
                        "v6": {
                            "terminal_status": entry["terminal_status"],
                            "expected_safe_outcome": entry[
                                "expected_safe_outcome"
                            ],
                            "correction_used": entry["correction_used"],
                        },
                        "closed_v5": entry["v5"],
                    },
                    indent=2,
                    ensure_ascii=False,
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


def _case_observation(
    *,
    case: dict[str, Any],
    oracle: dict[str, Any],
    case_dir: Path,
    dialogue: dict[str, Any],
) -> dict[str, Any]:
    actual_calls = dialogue["actual_provider_call_count"]
    turns = dialogue["turns"]
    if (
        actual_calls not in {1, 2}
        or len(turns) != actual_calls
        or not all(
            v5_cohort._cleanup_passed(turn["cleanup"])
            for turn in turns
        )
    ):
        raise ReceptionistCohortError("case_lifecycle_invalid")
    audits: list[dict[str, Any]] = []
    violation_sets: list[list[str]] = []
    for index in range(1, actual_calls + 1):
        audit = _load_object(
            case_dir / f"occupied-turn-{index:03d}-external-audit.json"
        )
        outcome = audit.get("provider_outcome") or {}
        form = audit.get("preprinted_form")
        if (
            audit.get("durable_hash_chain", {}).get("valid") is not True
            or audit.get("api_key_authentication_used") is not False
            or (
                outcome.get("status") == "completed"
                and (
                    not isinstance(form, dict)
                    or form.get("broker_judgement_repair") is not False
                )
            )
            or (
                outcome.get("status") != "completed"
                and form is not None
            )
        ):
            raise ReceptionistCohortError(
                "case_external_audit_invalid"
            )
        violations = v5_cohort._violations_from_turn(
            case_dir / f"occupied-turn-{index:03d}-evidence.json"
        )
        bounded_reason = (outcome.get("bounded_error") or {}).get(
            "reason_code"
        )
        if isinstance(bounded_reason, str):
            violations = sorted({*violations, bounded_reason})
        audits.append(audit)
        violation_sets.append(violations)
    exact_binding = dialogue.get("exact_binding") or {}
    if (
        exact_binding.get("model_id") != broker.MODEL
        or exact_binding.get("project") != broker.PROJECT
        or exact_binding.get("service_account") != broker.SERVICE_ACCOUNT
        or exact_binding.get("location") != broker.LOCATION
        or exact_binding.get("endpoint_hostname") != broker.HOSTNAME
        or exact_binding.get("api_key_authentication_used") is not False
    ):
        raise ReceptionistCohortError("case_provider_binding_invalid")
    release = dialogue.get("release")
    expected_safe = v5_cohort._expected_safe_outcome(
        case=case,
        oracle=oracle,
        dialogue=dialogue,
    )
    primary_form = audits[0].get("preprinted_form")
    return {
        "case_code": case["case_code"],
        "source_case_id": case.get("source_case_id"),
        "expected_goal": case["expected_goal"],
        "expected_proposal_family": case["expected_proposal_family"],
        "expected_proposal_release": case["expected_proposal_release"],
        "expected_safe_outcome": expected_safe,
        "primary_exact_body_accepted": bool(
            audits[0]["provider_outcome"]["status"] == "completed"
            and isinstance(primary_form, dict)
            and primary_form.get("raw_model_form_body_recorded") is False
        ),
        "primary_proofreader_disposition": turns[0][
            "proofreader_disposition"
        ],
        "primary_violation_codes": violation_sets[0],
        "correction_used": actual_calls == 2,
        "final_proofreader_disposition": turns[-1][
            "proofreader_disposition"
        ],
        "final_violation_codes": violation_sets[-1],
        "terminal_status": dialogue["terminal_status"],
        "actual_provider_calls": actual_calls,
        "provider_outcomes": [
            audit["provider_outcome"] for audit in audits
        ],
        "admitted_operator_ids": (
            audits[-1].get("proofreader") or {}
        ).get("admitted_operator_ids", []),
        "operator_note": audits[-1].get("operator_note"),
        "receptionist_output": audits[-1].get("receptionist_output"),
        "typed_program": audits[-1].get("typed_program"),
        "release": release,
        "parent_audit_chain": dialogue["parent_audit_chain"],
        "cleanup_passed": all(
            v5_cohort._cleanup_passed(turn["cleanup"])
            for turn in turns
        ),
        "exact_binding": exact_binding,
    }


def _load_closed_dialogue(
    *,
    case_dir: Path,
    attempt_ids: tuple[str, str],
    ledger_ids: tuple[str, str],
    expected_graph_revision: int,
    expected_compass_revision: int,
) -> dict[str, Any] | None:
    parent_path = case_dir / "occupied-dialogue-evidence.json"
    if not parent_path.exists():
        if case_dir.exists() and any(case_dir.iterdir()):
            raise ReceptionistCohortError(
                "partial_case_requires_independent_closeout"
            )
        return None
    dialogue = _load_object(parent_path)
    retained_hash = dialogue.get("evidence_hash")
    unhashed = copy.deepcopy(dialogue)
    unhashed.pop("evidence_hash", None)
    actual_calls = dialogue.get("actual_provider_call_count")
    expected_files = {
        "occupied-dialogue-parent-audit.jsonl",
        "occupied-dialogue-evidence.json",
    }
    for index in range(1, actual_calls + 1 if isinstance(actual_calls, int) else 1):
        expected_files.update(
            {
                f"occupied-turn-{index:03d}-evidence.json",
                f"occupied-turn-{index:03d}-ledger.json",
                f"occupied-turn-{index:03d}-audit.jsonl",
                f"occupied-turn-{index:03d}-external-audit.json",
            }
        )
    if actual_calls == 2:
        expected_files.add("occupied-turn-001-correction-ticket.json")
    actual_files = {
        path.name for path in case_dir.iterdir() if path.is_file()
    }
    if (
        retained_hash != lane.canonical_hash(unhashed)
        or dialogue.get("schema_version")
        != v6.PARENT_EVIDENCE_SCHEMA_VERSION
        or dialogue.get("dialogue_protocol") != v6.DIALOGUE_PROTOCOL
        or dialogue.get("model_response_contract")
        != v6.MODEL_RESPONSE_CONTRACT
        or actual_calls not in {1, 2}
        or dialogue.get("attempt_ids")
        != list(attempt_ids[:actual_calls])
        or dialogue.get("ledger_ids") != list(ledger_ids[:actual_calls])
        or actual_files != expected_files
        or not all(
            _load_object(
                case_dir / f"occupied-turn-{index:03d}-ledger.json"
            ).get("status")
            == "consumed"
            for index in range(1, actual_calls + 1)
        )
    ):
        raise ReceptionistCohortError(
            "closed_case_resume_binding_invalid"
        )
    for index in range(1, actual_calls + 1):
        turn = _load_object(
            case_dir / f"occupied-turn-{index:03d}-evidence.json"
        )
        gate = turn.get("precall_gate") or {}
        if (
            gate.get("continuity_graph_revision")
            != expected_graph_revision
            or gate.get("compass_map_revision")
            != expected_compass_revision
            or gate.get("compass_source_graph_revision")
            != expected_graph_revision
            or turn.get("attempt_id") != attempt_ids[index - 1]
            or turn.get("ledger_id") != ledger_ids[index - 1]
            or turn.get("provider_call_count") != 1
            or not all(
                value
                for key, value in turn.get("cleanup", {}).items()
                if key != "daemon_wide_prune_performed"
            )
        ):
            raise ReceptionistCohortError(
                "closed_case_resume_binding_invalid"
            )
    return dialogue


def run_occupied(
    *,
    preflight_path: Path,
    authority_path: Path,
    expected_graph_revision: int,
    expected_compass_revision: int,
) -> dict[str, Any]:
    _, cases = load_source_manifest()
    recorded = _load_object(PROVIDER_BLOCKED_PATH)
    oracles = _validate_provider_blocked(recorded)
    v5_rows = _v5_observations()
    if OCCUPIED_PATH.exists():
        raise ReceptionistCohortError("occupied_cohort_output_already_exists")
    entries: list[dict[str, Any]] = []
    observations: list[dict[str, Any]] = []
    total_calls = 0
    with _v6_contract():
        for case in cases:
            case_code = case["case_code"]
            case_dir = ARTIFACT_DIR / "cases" / case_code
            attempts, ledgers = _case_ids(case_code)
            dialogue_evidence = _load_closed_dialogue(
                case_dir=case_dir,
                attempt_ids=attempts,
                ledger_ids=ledgers,
                expected_graph_revision=expected_graph_revision,
                expected_compass_revision=expected_compass_revision,
            )
            case_source = "resumed_closed_evidence"
            if dialogue_evidence is None:
                dialogue_evidence = parent_live.run_dialogue(
                    artifact_dir=case_dir,
                    preflight_path=preflight_path,
                    authority_path=authority_path,
                    expected_graph_revision=expected_graph_revision,
                    expected_compass_revision=expected_compass_revision,
                    frame_path=FRAMES_DIR / f"{case_code}.json",
                    attempt_ids=attempts,
                    ledger_ids=ledgers,
                )
                case_source = "new_occupied_dialogue"
            observation = _case_observation(
                case=case,
                oracle=oracles[case_code],
                case_dir=case_dir,
                dialogue=dialogue_evidence,
            )
            observations.append(observation)
            total_calls += observation["actual_provider_calls"]
            if total_calls > ABSOLUTE_CALL_CEILING:
                raise ReceptionistCohortError(
                    "cohort_call_ceiling_exceeded"
                )
            entries.append(
                _notebook_case(
                    case=case,
                    frame=frame_for_case(case),
                    observation=observation,
                    dialogue=dialogue_evidence,
                    v5_observation=v5_rows[case_code],
                )
            )
            _render_notebook(
                entries,
                status=f"running — closed {case_code}",
            )
            print(
                json.dumps(
                    {
                        "case_closed": case_code,
                        "cases_closed": len(entries),
                        "provider_calls": total_calls,
                        "case_source": case_source,
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
            "reception.one.receptionist_first_v6.paired_cohort.v1"
        ),
        "result": OCCUPIED_RESULT_PASS if passed else OCCUPIED_RESULT_FAIL,
        "capability_threshold_passed": passed,
        "paired_development_not_holdout": True,
        "data_class": "authored_synthetic",
        "effect_ceiling": "proposal_only",
        "case_count": len(observations),
        "total_actual_provider_calls": total_calls,
        "absolute_provider_call_ceiling": ABSOLUTE_CALL_CEILING,
        "incremental_cost_ceiling_usd": 1,
        "continuity_binding": {
            "graph_revision": expected_graph_revision,
            "compass_revision": expected_compass_revision,
            "prompt_or_schema_change_within_cohort": False,
        },
        "generation": {
            "temperature": v6.TEMPERATURE,
            "thinking_budget": v6.THINKING_BUDGET,
            "include_thoughts": v6.INCLUDE_THOUGHTS,
        },
        "cases": observations,
        "all_ledgers_consumed": all(
            all(
                _load_object(path).get("status") == "consumed"
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
    _render_notebook(entries, status="complete")
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
                expected_graph_revision=args.graph_revision,
                expected_compass_revision=args.compass_revision,
            )
    except (
        ReceptionistCohortError,
        parent_live.PreprintedLiveError,
        lane.ModelLaneError,
        ValueError,
    ) as error:
        print(
            json.dumps(
                {
                    "result": "reception_one_receptionist_first_v6_blocked",
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
