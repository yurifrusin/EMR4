#!/usr/bin/env python3
"""Credential-free fixture cell for one receptionist-first v6.4 turn."""

from __future__ import annotations

import errno
import hashlib
import json
import os
from pathlib import Path
import socket
from typing import Any


ROOT = Path("/workspace")
EXPECTED_FILES = {
    "Dockerfile",
    "cell.py",
    "turn-input.json",
    "model-form-body.json",
}
CREDENTIAL_ENV_NAMES = {
    "GEMINI_API_KEY",
    "GOOGLE_API_KEY",
    "GOOGLE_APPLICATION_CREDENTIALS",
    "GOOGLE_CLOUD_PROJECT",
    "CLOUDSDK_CONFIG",
    "OPENAI_API_KEY",
}


class CellError(ValueError):
    """A bounded fixture-cell failure."""


def _object(name: str) -> dict[str, Any]:
    value = json.loads((ROOT / name).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise CellError("object_required")
    return value


def _hash(value: Any) -> str:
    encoded = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def run() -> dict[str, Any]:
    if os.getuid() != 65532 or os.getgid() != 65532:
        raise CellError("identity_not_non_root")
    if CREDENTIAL_ENV_NAMES.intersection(os.environ):
        raise CellError("credential_environment_present")
    interfaces = sorted(name for _, name in socket.if_nameindex())
    if interfaces != ["lo"]:
        raise CellError("network_not_isolated")
    actual_files = {
        path.relative_to(ROOT).as_posix()
        for path in ROOT.rglob("*")
        if path.is_file()
    }
    if actual_files != EXPECTED_FILES:
        raise CellError("file_set_not_exact")
    probe = ROOT / ".write-probe"
    blocked_errno = None
    try:
        probe.write_text("forbidden", encoding="utf-8")
    except OSError as error:
        blocked_errno = error.errno
    if blocked_errno != errno.EROFS or probe.exists():
        raise CellError("root_filesystem_not_read_only")

    turn = _object("turn-input.json")
    task = turn.get("task")
    context = task.get("desk_context") if isinstance(task, dict) else None
    ticket = turn.get("correction_ticket")
    if (
        set(turn)
        != {
            "contract_version",
            "data_class",
            "effect_ceiling",
            "turn_code",
            "task_sha256",
            "desk_context_sha256",
            "bureau_packet",
            "task",
            "correction_ticket",
        }
        or turn.get("contract_version")
        != "reception.one.bureau.receptionist-first.v6.4"
        or turn.get("data_class") != "authored_synthetic"
        or turn.get("effect_ceiling") != "proposal_only"
        or turn.get("bureau_packet")
        != {
            "broker_owned_fields": {"version_code": 3},
            "model_authored_sections": [
                "receptionist_response",
                "decision_note",
                "evidence_utterance_indices",
                "typed_form",
            ],
        }
        or turn.get("turn_code") not in {1, 2}
        or (turn["turn_code"] == 1 and ticket is not None)
        or (turn["turn_code"] == 2 and not isinstance(ticket, dict))
        or not isinstance(task, dict)
        or not isinstance(context, dict)
        or turn.get("task_sha256") != _hash(task)
        or turn.get("desk_context_sha256") != _hash(context)
        or context.get("authority") != "context_only_no_command_authority"
        or context.get("effect_ceiling") != "proposal_only"
    ):
        raise CellError("turn_input_boundary_invalid")
    serialized = json.dumps(turn, sort_keys=True).casefold()
    if any(
        forbidden in serialized
        for forbidden in (
            "bernie-emr4-dev",
            "service_account",
            "access_token",
            "oauth",
            "api_key",
            "google_application_credentials",
        )
    ):
        raise CellError("turn_input_secret_or_identity_surface")

    body = _object("model-form-body.json")
    if set(body) != {
        "receptionist_response",
        "decision_note",
        "evidence_utterance_indices",
        "typed_form",
    } or set(body.get("typed_form", {})) != {
        "operator_note",
        "goal_code",
        "steps",
    }:
        raise CellError("model_form_body_shape_invalid")
    if "version_code" in json.dumps(body, sort_keys=True):
        raise CellError("broker_owned_field_in_model_body")
    return {
        "schema_version": (
            "reception.one.receptionist_first_v64.fixture_cell_result.v1"
        ),
        "status": "completed",
        "turn_code": turn["turn_code"],
        "task_sha256": turn["task_sha256"],
        "desk_context_sha256": turn["desk_context_sha256"],
        "correction_ticket_sha256": (
            _hash(ticket) if isinstance(ticket, dict) else None
        ),
        "model_form_body": body,
        "isolation": {
            "uid": os.getuid(),
            "gid": os.getgid(),
            "network_interfaces": interfaces,
            "loopback_only": True,
            "read_only_root_filesystem": True,
            "credential_environment_present": False,
        },
    }


def main() -> int:
    try:
        print(json.dumps(run(), ensure_ascii=False, sort_keys=True), end="")
        return 0
    except (CellError, OSError, json.JSONDecodeError):
        print(
            json.dumps(
                {
                    "schema_version": (
                        "reception.one.receptionist_first_v64."
                        "fixture_cell_result.v1"
                    ),
                    "status": "edge_aborted",
                },
                sort_keys=True,
            ),
            end="",
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
