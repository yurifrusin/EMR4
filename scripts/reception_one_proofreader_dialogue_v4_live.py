#!/usr/bin/env python3
"""Run the bounded one-or-two-call Reception One proofreader dialogue."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import reception_one_bureau_model_text_lane as lane
from scripts import reception_one_bureau_model_text_lane_audit as turn_audit
from scripts import reception_one_bureau_model_text_lane_live as live
from scripts import reception_one_proofreader_dialogue_v4 as dialogue


ATTEMPT_IDS = (
    "reception-one-proofreader-dialogue-v4-turn-001",
    "reception-one-proofreader-dialogue-v4-turn-002",
)
LEDGER_IDS = (
    "reception-one-proofreader-dialogue-v4-ledger-001",
    "reception-one-proofreader-dialogue-v4-ledger-002",
)
ZERO_HASH = "sha256:" + "0" * 64


class DialogueLiveError(RuntimeError):
    """A bounded parent-dialogue lifecycle rejection."""


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _append_parent_event(
    path: Path,
    events: list[dict[str, Any]],
    event_type: str,
    fields: dict[str, Any],
) -> None:
    previous = events[-1]["event_hash"] if events else ZERO_HASH
    event = {
        "schema_version": (
            "reception.one.proofreader_dialogue_v4.parent_audit_event.v1"
        ),
        "sequence": len(events) + 1,
        "previous_hash": previous,
        "event_type": event_type,
        "fields": fields,
    }
    event["event_hash"] = lane.canonical_hash(event)
    events.append(event)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(event, sort_keys=True) + "\n")


def decide_sequence(turns: list[dict[str, Any]]) -> dict[str, Any]:
    """Pure call-budget state machine used by live and provider-free tests."""

    if len(turns) > dialogue.MAX_PROVIDER_CALLS:
        raise DialogueLiveError("absolute_call_ceiling_exceeded")
    for index, turn in enumerate(turns, start=1):
        if turn.get("provider_call_count") != 1:
            raise DialogueLiveError("turn_call_count_invalid")
        if turn.get("attempt_id") != ATTEMPT_IDS[index - 1]:
            raise DialogueLiveError("turn_attempt_order_invalid")
        if turn.get("ledger_id") != LEDGER_IDS[index - 1]:
            raise DialogueLiveError("turn_ledger_order_invalid")
        if turn.get("ledger", {}).get("status") != "consumed":
            raise DialogueLiveError("turn_ledger_not_consumed")
    actual_calls = sum(turn["provider_call_count"] for turn in turns)
    if actual_calls > dialogue.MAX_PROVIDER_CALLS:
        raise DialogueLiveError("absolute_call_ceiling_exceeded")
    if not turns:
        return {
            "status": "ready",
            "next_turn_code": 1,
            "actual_provider_calls": 0,
            "terminal": False,
        }
    first = turns[0]
    first_release = first["exchange"].get("release")
    first_ticket = first["exchange"].get("correction_ticket")
    if first_release is not None and first_ticket is not None:
        raise DialogueLiveError("release_and_correction_ticket_conflict")
    if first_release is not None:
        if len(turns) != 1:
            raise DialogueLiveError("call_after_admission_forbidden")
        return {
            "status": "admitted",
            "next_turn_code": None,
            "actual_provider_calls": actual_calls,
            "terminal": True,
        }
    if len(turns) == 1:
        if first_ticket is None:
            return {
                "status": "terminal_no_release",
                "next_turn_code": None,
                "actual_provider_calls": 1,
                "terminal": True,
            }
        dialogue.validate_exact(
            first_ticket,
            dialogue.CORRECTION_TICKET_SCHEMA_PATH,
        )
        return {
            "status": "correction_authorised",
            "next_turn_code": 2,
            "actual_provider_calls": 1,
            "terminal": False,
            "correction_ticket_hash": dialogue.canonical_hash(first_ticket),
        }
    second = turns[1]
    if second["exchange"].get("correction_ticket") is not None:
        raise DialogueLiveError("second_correction_ticket_forbidden")
    second_release = second["exchange"].get("release")
    return {
        "status": "admitted_after_correction"
        if second_release is not None
        else "terminal_no_release",
        "next_turn_code": None,
        "actual_provider_calls": actual_calls,
        "terminal": True,
    }


def build_parent_evidence(
    *,
    turns: list[dict[str, Any]],
    external_audits: list[dict[str, Any]],
    parent_events: list[dict[str, Any]],
) -> dict[str, Any]:
    decision = decide_sequence(turns)
    if len(turns) != len(external_audits):
        raise DialogueLiveError("turn_audit_count_mismatch")
    for turn, audit in zip(turns, external_audits, strict=True):
        if (
            audit.get("attempt_id") != turn.get("attempt_id")
            or audit.get("ledger_id") != turn.get("ledger_id")
            or audit.get("durable_hash_chain", {}).get("valid") is not True
        ):
            raise DialogueLiveError("turn_external_audit_binding_invalid")
    release = next(
        (
            turn["exchange"]["release"]
            for turn in turns
            if turn["exchange"].get("release") is not None
        ),
        None,
    )
    return {
        "schema_version": (
            "reception.one.proofreader_dialogue_v4.parent_evidence.v1"
        ),
        "result": (
            "reception_one_proofreader_dialogue_v4_occupied_pass"
            if release is not None
            else "reception_one_proofreader_dialogue_v4_occupied_no_release"
        ),
        "dialogue_protocol": dialogue.DIALOGUE_PROTOCOL,
        "response_contract": "reception.one.bureau.plan-program.v3",
        "data_class": "authored_synthetic",
        "effect_ceiling": "proposal_only",
        "attempt_ids": [turn["attempt_id"] for turn in turns],
        "ledger_ids": [turn["ledger_id"] for turn in turns],
        "actual_provider_call_count": decision["actual_provider_calls"],
        "absolute_provider_call_ceiling": dialogue.MAX_PROVIDER_CALLS,
        "incremental_cost_ceiling_usd": 1,
        "no_call_after_admission": True,
        "request_contract_repair_competed_for_call_two": False,
        "turn_two_terminal": len(turns) == 2,
        "terminal_status": decision["status"],
        "correction_ticket_hash": (
            turns[0]["exchange"].get("correction_ticket_hash")
            if turns
            else None
        ),
        "turns": [
            {
                "turn_code": index,
                "attempt_id": turn["attempt_id"],
                "ledger_id": turn["ledger_id"],
                "result": turn["result"],
                "model_input_hash": turn["exchange"]["model_input_hash"],
                "schema_hash": turn["exchange"]["schema_hash"],
                "audit_terminal_hash": turn["exchange"][
                    "audit_terminal_hash"
                ],
                "proofreader_disposition": (
                    turn["exchange"].get("proofreader") or {}
                ).get("disposition"),
                "correction_ticket_issued": (
                    turn["exchange"].get("correction_ticket") is not None
                ),
                "released": turn["exchange"].get("release") is not None,
                "cleanup": turn["cleanup"],
            }
            for index, turn in enumerate(turns, start=1)
        ],
        "release": release,
        "parent_audit_chain": {
            "valid": bool(parent_events),
            "event_count": len(parent_events),
            "terminal_hash": (
                parent_events[-1]["event_hash"] if parent_events else None
            ),
        },
        "exact_binding": (
            turns[0]["exact_binding"] if turns else None
        ),
        "explicit_exclusions": {
            "raw_prompt_recorded": False,
            "raw_provider_response_recorded": False,
            "credential_or_token_recorded": False,
            "api_key_information_recorded": False,
            "rejected_operator_note_recorded": False,
            "chain_of_thought_recorded": False,
            "proofreader_selected_replacement": False,
            "product_or_database_access": False,
            "command_authority": False,
            "human_or_product_delivery": False,
            "fallback": False,
        },
        "candid_limit": (
            "This sequence can prove only bounded authored-synthetic form "
            "completion through the configured and observed Sydney Vertex "
            "locational request path. It cannot prove Australian physical or "
            "sovereign processing, general model reliability, production "
            "fitness or safety for real, product, patient, health, clinical "
            "or historical data."
        ),
    }


def run_dialogue(
    *,
    artifact_dir: Path,
    preflight_path: Path,
    authority_path: Path,
    expected_graph_revision: int,
    expected_compass_revision: int,
    frame_path: Path,
) -> dict[str, Any]:
    artifact_dir.mkdir(parents=True, exist_ok=True)
    parent_audit_path = artifact_dir / "occupied-dialogue-parent-audit.jsonl"
    parent_evidence_path = artifact_dir / "occupied-dialogue-evidence.json"
    ticket_path = artifact_dir / "occupied-turn-001-correction-ticket.json"
    all_paths = [parent_audit_path, parent_evidence_path, ticket_path]
    for index in (1, 2):
        all_paths.extend(
            [
                artifact_dir / f"occupied-turn-{index:03d}-evidence.json",
                artifact_dir / f"occupied-turn-{index:03d}-ledger.json",
                artifact_dir / f"occupied-turn-{index:03d}-audit.jsonl",
                artifact_dir
                / f"occupied-turn-{index:03d}-external-audit.json",
            ]
        )
    if any(path.exists() for path in all_paths):
        raise DialogueLiveError("dialogue_output_already_exists")
    turns: list[dict[str, Any]] = []
    external_audits: list[dict[str, Any]] = []
    parent_events: list[dict[str, Any]] = []
    _append_parent_event(
        parent_audit_path,
        parent_events,
        "dialogue_opened",
        {
            "dialogue_protocol": dialogue.DIALOGUE_PROTOCOL,
            "maximum_actual_provider_calls": dialogue.MAX_PROVIDER_CALLS,
            "incremental_cost_ceiling_usd": 1,
            "turn_two_terminal": True,
        },
    )
    for index in (1, 2):
        decision = decide_sequence(turns)
        if decision["terminal"]:
            break
        if decision["next_turn_code"] != index:
            raise DialogueLiveError("dialogue_state_machine_invalid")
        evidence_path = artifact_dir / f"occupied-turn-{index:03d}-evidence.json"
        ledger_path = artifact_dir / f"occupied-turn-{index:03d}-ledger.json"
        audit_path = artifact_dir / f"occupied-turn-{index:03d}-audit.jsonl"
        external_path = (
            artifact_dir / f"occupied-turn-{index:03d}-external-audit.json"
        )
        correction_path = ticket_path if index == 2 else None
        _append_parent_event(
            parent_audit_path,
            parent_events,
            "turn_opened",
            {
                "turn_code": index,
                "attempt_id": ATTEMPT_IDS[index - 1],
                "ledger_id": LEDGER_IDS[index - 1],
                "actual_call_ordinal": index,
                "correction_ticket_hash": (
                    decision.get("correction_ticket_hash")
                    if index == 2
                    else None
                ),
            },
        )
        turn = live.run_live(
            evidence_path=evidence_path,
            ledger_path=ledger_path,
            audit_path=audit_path,
            attempt_id=ATTEMPT_IDS[index - 1],
            ledger_id=LEDGER_IDS[index - 1],
            preflight_path=preflight_path,
            authority_path=authority_path,
            expected_graph_revision=expected_graph_revision,
            expected_compass_revision=expected_compass_revision,
            frame_path=frame_path,
            contract_mode=dialogue.CONTRACT_MODE,
            correction_ticket_path=correction_path,
        )
        external = turn_audit.build_external_audit(
            evidence_path,
            audit_path,
            preflight_path,
        )
        _write_json(external_path, external)
        turns.append(turn)
        external_audits.append(external)
        _append_parent_event(
            parent_audit_path,
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
                "correction_ticket_hash": turn["exchange"].get(
                    "correction_ticket_hash"
                ),
                "released": turn["exchange"].get("release") is not None,
                "cleanup_passed": all(
                    value
                    for key, value in turn["cleanup"].items()
                    if key != "daemon_wide_prune_performed"
                ),
            },
        )
        decision = decide_sequence(turns)
        if decision["next_turn_code"] == 2:
            ticket = turn["exchange"]["correction_ticket"]
            dialogue.validate_exact(
                ticket,
                dialogue.CORRECTION_TICKET_SCHEMA_PATH,
            )
            if dialogue.canonical_hash(ticket) != decision[
                "correction_ticket_hash"
            ]:
                raise DialogueLiveError("correction_ticket_hash_mismatch")
            _write_json(ticket_path, ticket)
    final_decision = decide_sequence(turns)
    if not final_decision["terminal"]:
        raise DialogueLiveError("dialogue_not_terminal")
    _append_parent_event(
        parent_audit_path,
        parent_events,
        "dialogue_closed",
        {
            "status": final_decision["status"],
            "actual_provider_calls": final_decision[
                "actual_provider_calls"
            ],
            "third_call_performed": False,
            "fallback_performed": False,
        },
    )
    evidence = build_parent_evidence(
        turns=turns,
        external_audits=external_audits,
        parent_events=parent_events,
    )
    evidence["evidence_hash"] = lane.canonical_hash(evidence)
    _write_json(parent_evidence_path, evidence)
    return evidence


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-dir", type=Path, required=True)
    parser.add_argument("--preflight", type=Path, required=True)
    parser.add_argument("--authority", type=Path, required=True)
    parser.add_argument("--graph-revision", type=int, required=True)
    parser.add_argument("--compass-revision", type=int, required=True)
    parser.add_argument("--frame", type=Path, required=True)
    args = parser.parse_args()
    try:
        evidence = run_dialogue(
            artifact_dir=args.artifact_dir,
            preflight_path=args.preflight,
            authority_path=args.authority,
            expected_graph_revision=args.graph_revision,
            expected_compass_revision=args.compass_revision,
            frame_path=args.frame,
        )
    except (DialogueLiveError, live.LiveError, ValueError) as error:
        print(
            json.dumps(
                {
                    "result": (
                        "reception_one_proofreader_dialogue_v4_occupied_blocked"
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
                "actual_provider_call_count": evidence[
                    "actual_provider_call_count"
                ],
                "terminal_status": evidence["terminal_status"],
            },
            sort_keys=True,
        )
    )
    return 0 if evidence["release"] is not None else 2


if __name__ == "__main__":
    raise SystemExit(main())
