#!/usr/bin/env python3
"""Credential-free provider-free fixture cell for the Bureau model text lane."""

from __future__ import annotations

import errno
import json
import os
from pathlib import Path
import socket
from typing import Any


ROOT = Path("/workspace")
INPUT_PATH = ROOT / "model-input.json"
OUTPUT_PATH = ROOT / "model-output-fixture.json"
WRITE_PROBE = ROOT / ".write-probe"
EXPECTED_FILES = {
    "Dockerfile",
    "cell.py",
    "model-input.json",
    "model-output-fixture.json",
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
        "available_bindings",
        "operator_catalog",
    }:
        raise CellError("model_input_shape_invalid")
    if (
        model_input.get("data_class") != "authored_synthetic"
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

    candidate = load_object(OUTPUT_PATH)
    if set(candidate) != {"contract_version", "goal", "steps"}:
        raise CellError("candidate_shape_invalid")
    return {
        "schema_version": "reception.one.bureau.fixture_cell_result.v1",
        "status": "completed",
        "candidate": candidate,
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
                        "reception.one.bureau.fixture_cell_result.v1"
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
