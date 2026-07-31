#!/usr/bin/env python3
"""Credential-free fixture cell for one v5 pre-printed-form turn."""

from __future__ import annotations

import errno
import hashlib
import json
import os
from pathlib import Path
import socket
from typing import Any


ROOT = Path("/workspace")
TURN_INPUT_PATH = ROOT / "turn-input.json"
FORM_BODY_PATH = ROOT / "model-form-body.json"
WRITE_PROBE = ROOT / ".write-probe"
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


def load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise CellError("object_required")
    return value


def canonical_hash(value: Any) -> str:
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
    blocked_errno = None
    try:
        WRITE_PROBE.write_text("forbidden", encoding="utf-8")
    except OSError as error:
        blocked_errno = error.errno
    if blocked_errno != errno.EROFS or WRITE_PROBE.exists():
        raise CellError("root_filesystem_not_read_only")

    turn_input = load_object(TURN_INPUT_PATH)
    if set(turn_input) != {
        "contract_version",
        "data_class",
        "effect_ceiling",
        "turn_code",
        "task_sha256",
        "preprinted_form",
        "task",
        "correction_ticket",
    }:
        raise CellError("turn_input_shape_invalid")
    turn_code = turn_input.get("turn_code")
    ticket = turn_input.get("correction_ticket")
    if (
        turn_input.get("contract_version")
        != "reception.one.bureau.preprinted-form.v5"
        or turn_input.get("data_class") != "authored_synthetic"
        or turn_input.get("effect_ceiling") != "proposal_only"
        or turn_input.get("preprinted_form")
        != {
            "version_code": 3,
            "model_authored_fields": [
                "operator_note",
                "goal_code",
                "steps",
            ],
        }
        or turn_code not in {1, 2}
        or (turn_code == 1 and ticket is not None)
        or (turn_code == 2 and not isinstance(ticket, dict))
    ):
        raise CellError("turn_input_boundary_invalid")
    serialized = json.dumps(turn_input, sort_keys=True).casefold()
    for forbidden in (
        "bernie-emr4-dev",
        "service_account",
        "access_token",
        "oauth",
        "api_key",
        "google_application_credentials",
    ):
        if forbidden in serialized:
            raise CellError("turn_input_secret_or_identity_surface")

    body = load_object(FORM_BODY_PATH)
    if set(body) != {"operator_note", "goal_code", "steps"}:
        raise CellError("model_form_body_shape_invalid")
    if "version_code" in body:
        raise CellError("broker_owned_field_in_model_body")
    return {
        "schema_version": (
            "reception.one.preprinted_form_v5.fixture_cell_result.v1"
        ),
        "status": "completed",
        "turn_code": turn_code,
        "task_sha256": turn_input["task_sha256"],
        "correction_ticket_sha256": (
            canonical_hash(ticket) if isinstance(ticket, dict) else None
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
                        "reception.one.preprinted_form_v5."
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
