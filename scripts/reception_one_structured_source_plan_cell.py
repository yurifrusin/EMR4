#!/usr/bin/env python3
"""Credential-free provider-free structured-source PlanProgram fixture cell."""

from __future__ import annotations

import errno
import json
import os
from pathlib import Path
import socket
from typing import Any


ROOT = Path("/workspace")
INPUT_PATH = ROOT / "model-input.json"
PROGRAM_PATH = ROOT / "plan-program-fixture.json"
WRITE_PROBE = ROOT / ".write-probe"
EXPECTED_FILES = {
    "Dockerfile",
    "cell.py",
    "model-input.json",
    "plan-program-fixture.json",
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

    model_input = load_object(INPUT_PATH)
    if set(model_input) != {
        "contract_version",
        "data_class",
        "utterances",
        "effect_ceiling",
        "source_reference_contract",
        "goal_table",
        "binding_table",
        "operator_table",
    }:
        raise CellError("model_input_shape_invalid")
    if (
        model_input.get("contract_version")
        != "reception.one.bureau.structured-source-model-input.v4"
        or model_input.get("data_class") != "authored_synthetic"
        or model_input.get("effect_ceiling") != "proposal_only"
    ):
        raise CellError("model_input_boundary_invalid")
    serialized = json.dumps(model_input, sort_keys=True).casefold()
    for forbidden in (
        "bernie-emr4-dev",
        "service_account",
        "access_token",
        "oauth",
        "api_key",
        "google_application_credentials",
    ):
        if forbidden in serialized:
            raise CellError("model_input_secret_or_identity_surface")

    program = load_object(PROGRAM_PATH)
    if set(program) != {
        "version_code",
        "operator_note",
        "goal_code",
        "steps",
    }:
        raise CellError("program_shape_invalid")
    return {
        "schema_version": (
            "reception.one.structured_source.fixture_cell_result.v1"
        ),
        "status": "completed",
        "program": program,
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
                        "reception.one.structured_source."
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
