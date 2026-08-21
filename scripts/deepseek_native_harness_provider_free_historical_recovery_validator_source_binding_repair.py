"""Verify immutable Git source binding for the historical startup recovery."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
from typing import Any
from unittest.mock import patch

import jsonschema

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts import (  # noqa: E402
    deepseek_native_harness_provider_free_pre_hmr_startup_terminal_recovery
    as recovery,
)


OPERATION_ID = (
    "deepseek-native-harness-provider-free-historical-recovery-validator-"
    "source-binding-repair"
)
CONTINUITY_ROOT = REPO_ROOT / "orchestration" / "continuity" / OPERATION_ID
CONTRACT_PATH = CONTINUITY_ROOT / "contract.json"
CONTRACT_SCHEMA_PATH = CONTINUITY_ROOT / "contract.schema.json"
EVIDENCE_PATH = CONTINUITY_ROOT / "provider-free-repair-evidence.json"
EVIDENCE_SCHEMA_PATH = CONTINUITY_ROOT / "evidence.schema.json"
REPORT_PATH = CONTINUITY_ROOT / "provider-free-repair-report.md"
HISTORICAL_ROOT = recovery.CONTINUITY_ROOT
FULL_OID = re.compile(r"^[0-9a-f]{40}$")


class SourceBindingRepairError(RuntimeError):
    """An immutable historical source-binding invariant failed closed."""


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SourceBindingRepairError(f"json_object_required:{path.name}")
    return value


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _file_sha256(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _git(*arguments: str, accepted_codes: tuple[int, ...] = (0,)) -> bytes:
    completed = subprocess.run(
        ["git", *arguments],
        cwd=REPO_ROOT,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if completed.returncode not in accepted_codes:
        raise SourceBindingRepairError(
            f"git_failed:{arguments[0]}:exit_{completed.returncode}"
        )
    return completed.stdout


def validate_contract(value: dict[str, Any]) -> dict[str, Any]:
    try:
        jsonschema.Draft202012Validator(_load_json(CONTRACT_SCHEMA_PATH)).validate(
            value
        )
    except jsonschema.ValidationError as error:
        raise SourceBindingRepairError("contract_schema_invalid") from error
    if value["historical_source_sha256"] != recovery.HISTORICAL_SOURCE_SHA256:
        raise SourceBindingRepairError("old_validator_projection_not_frozen")
    return value


def _validate_source_path(path: str) -> None:
    candidate = PurePosixPath(path)
    if (
        candidate.is_absolute()
        or not candidate.parts
        or any(part in {"", ".", ".."} for part in candidate.parts)
        or candidate.as_posix() != path
    ):
        raise SourceBindingRepairError("historical_source_path_invalid")


def resolve_historical_commit(source_commit: str) -> str:
    if FULL_OID.fullmatch(source_commit) is None:
        raise SourceBindingRepairError("historical_source_commit_not_full_oid")
    resolved = _git("rev-parse", "--verify", f"{source_commit}^{{commit}}").decode(
        "ascii"
    ).strip()
    if resolved != source_commit or FULL_OID.fullmatch(resolved) is None:
        raise SourceBindingRepairError("historical_source_commit_not_exact")
    _git("merge-base", "--is-ancestor", source_commit, "HEAD")
    return resolved


def verify_historical_sources(
    contract_value: dict[str, Any],
    *,
    source_commit: str | None = None,
    source_sha256: dict[str, str] | None = None,
) -> dict[str, Any]:
    frozen_commit = contract_value["historical_source_commit"]
    frozen_sources = contract_value["historical_source_sha256"]
    selected_commit = frozen_commit if source_commit is None else source_commit
    selected_sources = frozen_sources if source_sha256 is None else source_sha256
    if selected_commit != frozen_commit:
        raise SourceBindingRepairError("historical_source_commit_substituted")
    if selected_sources != frozen_sources:
        raise SourceBindingRepairError("historical_source_map_substituted")
    resolved = resolve_historical_commit(selected_commit)
    observed: dict[str, str] = {}
    for path, expected in selected_sources.items():
        _validate_source_path(path)
        actual = _sha256_bytes(_git("show", f"{resolved}:{path}"))
        if actual != expected:
            raise SourceBindingRepairError(f"historical_source_hash_mismatch:{path}")
        observed[path] = actual
    return {
        "historical_source_commit": resolved,
        "source_blob_count": len(observed),
        "source_blob_sha256_exact": observed == frozen_sources,
    }


def verify_immutable_historical_artifacts(
    contract_value: dict[str, Any],
) -> dict[str, Any]:
    expected = contract_value["immutable_historical_artifact_sha256"]
    for name, digest in expected.items():
        path = HISTORICAL_ROOT / name
        if not path.is_file() or _file_sha256(path) != digest:
            raise SourceBindingRepairError(f"historical_artifact_mismatch:{name}")
    return {
        "historical_artifact_count": len(expected),
        "historical_artifacts_unchanged": True,
    }


def verify_old_validator_without_subprocess(
    contract_value: dict[str, Any],
) -> dict[str, Any]:
    if recovery.HISTORICAL_SOURCE_COMMIT != contract_value["historical_source_commit"]:
        raise SourceBindingRepairError("old_validator_commit_binding_mismatch")
    if recovery.historical_source_sha256() != contract_value["historical_source_sha256"]:
        raise SourceBindingRepairError("old_validator_source_projection_mismatch")

    def forbidden(*args: object, **kwargs: object) -> object:
        del args, kwargs
        raise SourceBindingRepairError("old_validator_started_subprocess")

    with patch.object(subprocess, "run", forbidden), patch.object(
        subprocess, "Popen", forbidden
    ):
        value = recovery.validate_artifacts()
    if value["source_sha256"] != contract_value["historical_source_sha256"]:
        raise SourceBindingRepairError("old_validator_evidence_projection_mismatch")
    return {
        "contract_and_evidence_current_check": True,
        "subprocess_forbidden_check": True,
        "old_validator_subprocess_count": 0,
    }


def build_evidence() -> dict[str, Any]:
    contract_value = validate_contract(_load_json(CONTRACT_PATH))
    source = verify_historical_sources(contract_value)
    artifacts = verify_immutable_historical_artifacts(contract_value)
    predecessor = verify_old_validator_without_subprocess(contract_value)
    return {
        "schema_version": (
            "ariadne.native_harness_historical_recovery_source_binding_repair_"
            "evidence.v1"
        ),
        "operation_id": OPERATION_ID,
        "result": "pass",
        "provider_posture": contract_value["provider_posture"],
        **source,
        **artifacts,
        "old_validator_source_binding": contract_value[
            "old_validator_source_binding"
        ],
        "git_proof_owner": contract_value["git_proof_owner"],
        "predecessor_checks": predecessor,
        "boundary": {
            "local_git_subprocess_count": 2 + source["source_blob_count"],
            "native_harness_process_count": 0,
            "broker_process_count": 0,
            "worker_process_count": 0,
            "session_count": 0,
            "prompt_count": 0,
            "tool_count": 0,
            "model_request_count": 0,
            "provider_request_count": 0,
            "occupied_attempt_count": 0,
            "raw_stream_bytes_reconstructed_or_retained": 0,
        },
        "ordinary_practice_authority": contract_value[
            "ordinary_practice_authority"
        ],
        "protected_ref": contract_value["protected_ref"],
    }


def validate_evidence(value: dict[str, Any]) -> dict[str, Any]:
    try:
        jsonschema.Draft202012Validator(_load_json(EVIDENCE_SCHEMA_PATH)).validate(
            value
        )
    except jsonschema.ValidationError as error:
        raise SourceBindingRepairError("evidence_schema_invalid") from error
    current = build_evidence()
    if current != value:
        raise SourceBindingRepairError("evidence_not_current")
    return value


def validate_artifacts() -> dict[str, Any]:
    return validate_evidence(_load_json(EVIDENCE_PATH))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", required=True)
    parser.parse_args()
    try:
        value = validate_artifacts()
    except (SourceBindingRepairError, OSError, UnicodeError) as error:
        print(json.dumps({"result": "failed_closed", "error": str(error)}))
        return 1
    print(
        json.dumps(
            {
                "result": value["result"],
                "historical_source_commit": value["historical_source_commit"],
                "source_blob_count": value["source_blob_count"],
                "historical_artifact_count": value["historical_artifact_count"],
                "native_harness_process_count": value["boundary"][
                    "native_harness_process_count"
                ],
                "provider_request_count": value["boundary"][
                    "provider_request_count"
                ],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
