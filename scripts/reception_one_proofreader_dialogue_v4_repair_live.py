#!/usr/bin/env python3
"""Run the sole request-contract repair call for the closed v4 primary."""

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


ATTEMPT_ID = (
    "reception-one-proofreader-dialogue-v4-request-repair-002"
)
LEDGER_ID = (
    "reception-one-proofreader-dialogue-v4-request-repair-ledger-002"
)
ZERO_HASH = "sha256:" + "0" * 64
OLD_SCHEMA_HASH = (
    "sha256:9a51825464fa4e1e7c6e21d4c70754b29db7672be9ae2dc867811df0d76b7550"
)


class RepairLiveError(RuntimeError):
    """A bounded request-repair lifecycle rejection."""


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _append_event(
    path: Path,
    events: list[dict[str, Any]],
    event_type: str,
    fields: dict[str, Any],
) -> None:
    event = {
        "schema_version": (
            "reception.one.proofreader_dialogue_v4."
            "request_repair_parent_event.v1"
        ),
        "sequence": len(events) + 1,
        "previous_hash": (
            events[-1]["event_hash"] if events else ZERO_HASH
        ),
        "event_type": event_type,
        "fields": fields,
    }
    event["event_hash"] = lane.canonical_hash(event)
    events.append(event)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(event, sort_keys=True) + "\n")


def _validate_closed_primary(artifact_dir: Path) -> dict[str, Any]:
    parent = lane.load_object(
        artifact_dir / "occupied-dialogue-evidence.json"
    )
    external = lane.load_object(
        artifact_dir / "occupied-turn-001-external-audit.json"
    )
    ledger = lane.load_object(
        artifact_dir / "occupied-turn-001-ledger.json"
    )
    if (
        parent.get("actual_provider_call_count") != 1
        or parent.get("release") is not None
        or parent.get("terminal_status") != "terminal_no_release"
        or ledger.get("status") != "consumed"
        or ledger.get("provider_calls_consumed") != 1
        or external.get("schema_hash") != OLD_SCHEMA_HASH
        or external.get("provider_outcome", {}).get("http_status") != 400
        or external.get("provider_outcome", {}).get("bounded_error", {}).get(
            "normalized_status"
        )
        != "INVALID_ARGUMENT"
        or external.get("durable_hash_chain", {}).get("valid") is not True
    ):
        raise RepairLiveError("closed_primary_not_exact")
    return {
        "parent_evidence_hash": parent["evidence_hash"],
        "primary_turn_audit_terminal_hash": external[
            "durable_hash_chain"
        ]["terminal_hash"],
        "primary_parent_audit_terminal_hash": parent[
            "parent_audit_chain"
        ]["terminal_hash"],
        "old_request_hash": external["request_hash"],
        "old_schema_hash": external["schema_hash"],
    }


def run_repair(
    *,
    artifact_dir: Path,
    preflight_path: Path,
    authority_path: Path,
    expected_graph_revision: int,
    expected_compass_revision: int,
    frame_path: Path,
) -> dict[str, Any]:
    binding = _validate_closed_primary(artifact_dir)
    evidence_path = artifact_dir / "occupied-request-repair-002-evidence.json"
    ledger_path = artifact_dir / "occupied-request-repair-002-ledger.json"
    audit_path = artifact_dir / "occupied-request-repair-002-audit.jsonl"
    external_path = (
        artifact_dir / "occupied-request-repair-002-external-audit.json"
    )
    parent_audit_path = (
        artifact_dir / "occupied-request-repair-parent-audit.jsonl"
    )
    consolidated_path = (
        artifact_dir / "occupied-request-repair-consolidated-evidence.json"
    )
    for path in (
        evidence_path,
        ledger_path,
        audit_path,
        external_path,
        parent_audit_path,
        consolidated_path,
    ):
        if path.exists():
            raise RepairLiveError("repair_output_already_exists")
    new_schema = dialogue.vertex_response_schema()
    new_schema_hash = dialogue.canonical_hash(new_schema)
    rendered_schema = dialogue.canonical_json(new_schema)
    if (
        new_schema_hash == OLD_SCHEMA_HASH
        or any(
            f'"{keyword}"' in rendered_schema
            for keyword in (
                "minimum",
                "maximum",
                "minLength",
                "maxLength",
                "minItems",
                "maxItems",
            )
        )
    ):
        raise RepairLiveError("provider_schema_repair_not_exact")
    events: list[dict[str, Any]] = []
    _append_event(
        parent_audit_path,
        events,
        "request_repair_opened",
        {
            **binding,
            "actual_call_ordinal": 2,
            "old_schema_hash": OLD_SCHEMA_HASH,
            "new_schema_hash": new_schema_hash,
            "semantic_correction_turn_available_after_repair": False,
            "third_call_allowed": False,
        },
    )
    turn = live.run_live(
        evidence_path=evidence_path,
        ledger_path=ledger_path,
        audit_path=audit_path,
        attempt_id=ATTEMPT_ID,
        ledger_id=LEDGER_ID,
        preflight_path=preflight_path,
        authority_path=authority_path,
        expected_graph_revision=expected_graph_revision,
        expected_compass_revision=expected_compass_revision,
        frame_path=frame_path,
        contract_mode=dialogue.CONTRACT_MODE,
    )
    external = turn_audit.build_external_audit(
        evidence_path,
        audit_path,
        preflight_path,
    )
    _write_json(external_path, external)
    if (
        turn.get("provider_call_count") != 1
        or turn.get("ledger", {}).get("status") != "consumed"
        or turn.get("ledger", {}).get("provider_calls_consumed") != 1
        or external.get("schema_hash") != new_schema_hash
    ):
        raise RepairLiveError("repair_call_or_ledger_invalid")
    release = turn["exchange"].get("release")
    _append_event(
        parent_audit_path,
        events,
        "request_repair_closed",
        {
            "attempt_id": ATTEMPT_ID,
            "ledger_id": LEDGER_ID,
            "turn_audit_terminal_hash": external[
                "durable_hash_chain"
            ]["terminal_hash"],
            "provider_status": external["provider_outcome"]["status"],
            "http_status": external["provider_outcome"]["http_status"],
            "proofreader_disposition": external["proofreader"][
                "disposition"
            ],
            "released": release is not None,
            "cleanup_passed": all(
                value
                for key, value in turn["cleanup"].items()
                if key != "daemon_wide_prune_performed"
            ),
        },
    )
    _append_event(
        parent_audit_path,
        events,
        "sequence_closed",
        {
            "actual_provider_call_count": 2,
            "absolute_provider_call_ceiling": 2,
            "third_call_performed": False,
            "fallback_performed": False,
            "terminal_status": (
                "admitted_after_request_contract_repair"
                if release is not None
                else "terminal_no_release_call_ceiling_exhausted"
            ),
        },
    )
    result = {
        "schema_version": (
            "reception.one.proofreader_dialogue_v4."
            "request_repair_consolidated_evidence.v1"
        ),
        "result": (
            "reception_one_proofreader_dialogue_v4_occupied_pass"
            if release is not None
            else "reception_one_proofreader_dialogue_v4_occupied_no_release"
        ),
        "actual_provider_call_count": 2,
        "absolute_provider_call_ceiling": 2,
        "request_contract_repair_consumed_call_two": True,
        "semantic_correction_turn_performed": False,
        "third_call_performed": False,
        "fallback_performed": False,
        "primary": binding,
        "repair": {
            "attempt_id": ATTEMPT_ID,
            "ledger_id": LEDGER_ID,
            "old_schema_hash": OLD_SCHEMA_HASH,
            "new_schema_hash": new_schema_hash,
            "new_request_hash": external["request_hash"],
            "provider_outcome": external["provider_outcome"],
            "proofreader": external["proofreader"],
            "operator_note": external["operator_note"],
            "typed_program": external["typed_program"],
            "release": external["release"],
            "cleanup": external["cleanup"],
            "turn_audit_terminal_hash": external[
                "durable_hash_chain"
            ]["terminal_hash"],
        },
        "parent_audit_chain": {
            "valid": True,
            "event_count": len(events),
            "terminal_hash": events[-1]["event_hash"],
        },
        "exact_binding": turn["exact_binding"],
        "release": release,
        "explicit_exclusions": {
            "raw_prompt_recorded": False,
            "raw_provider_response_recorded": False,
            "credential_or_token_recorded": False,
            "api_key_information_recorded": False,
            "chain_of_thought_recorded": False,
            "proofreader_selected_replacement": False,
            "product_or_database_access": False,
            "command_authority": False,
            "human_or_product_delivery": False,
            "fallback": False,
        },
        "candid_limit": (
            "The two-call sequence can prove only bounded authored-synthetic "
            "form completion through the configured and observed Sydney "
            "Vertex locational request path. It cannot prove Australian "
            "physical or sovereign processing, general model reliability, "
            "production fitness or safety for real or product data."
        ),
    }
    result["evidence_hash"] = lane.canonical_hash(result)
    _write_json(consolidated_path, result)
    return result


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
        evidence = run_repair(
            artifact_dir=args.artifact_dir,
            preflight_path=args.preflight,
            authority_path=args.authority,
            expected_graph_revision=args.graph_revision,
            expected_compass_revision=args.compass_revision,
            frame_path=args.frame,
        )
    except (RepairLiveError, live.LiveError, ValueError) as error:
        print(
            json.dumps(
                {
                    "result": (
                        "reception_one_proofreader_dialogue_v4_"
                        "request_repair_blocked"
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
                "proofreader_disposition": evidence["repair"][
                    "proofreader"
                ]["disposition"],
            },
            sort_keys=True,
        )
    )
    return 0 if evidence["release"] is not None else 2


if __name__ == "__main__":
    raise SystemExit(main())
