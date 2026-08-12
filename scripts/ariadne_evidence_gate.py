"""Pure evidence-led gates for Ariadne diagnostics and verifier commands."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


COMMAND_MANIFEST_SCHEMA_VERSION = "ariadne.verifier-command-manifest.v1"
DIAGNOSTIC_PACKET_SCHEMA_VERSION = "ariadne.diagnostic-decision-packet.v1"
DECISION_SCHEMA_VERSION = "ariadne.evidence-gate-decision.v1"
COMMAND_ID_PATTERN = re.compile(r"^[A-Z][A-Z0-9_-]{0,31}$")
HYPOTHESIS_ID_PATTERN = re.compile(r"^[a-z][a-z0-9_.-]{0,79}$")
SHELL_WRAPPERS = {
    "bash",
    "cmd",
    "cmd.exe",
    "powershell",
    "powershell.exe",
    "pwsh",
    "pwsh.exe",
    "sh",
}
COMPOUND_TOKENS = {";", "&&", "||", "|"}


def _object(value: object, *, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a JSON object")
    return value


def _exact_keys(value: dict[str, Any], expected: set[str], *, label: str) -> None:
    if set(value) != expected:
        raise ValueError(
            f"{label} keys must be exact: expected={sorted(expected)!r} "
            f"observed={sorted(value)!r}"
        )


def _load_json(path: Path, *, label: str) -> dict[str, Any]:
    try:
        return _object(json.loads(path.read_text(encoding="utf-8")), label=label)
    except json.JSONDecodeError as error:
        raise ValueError(f"{label} must be valid JSON") from error


def _canonical_bytes(value: object) -> bytes:
    return (
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    ).encode("utf-8")


def _is_python_executable(token: str) -> bool:
    name = Path(token).name.casefold()
    return name in {
        "python",
        "python.exe",
        "python3",
        "python3.exe",
    } or name.startswith("python3.")


def _looks_like_repository_script(token: str) -> bool:
    normalized = token.replace("\\", "/").casefold()
    return normalized.startswith("scripts/") and normalized.endswith(".py")


def validate_command_manifest(value: object) -> dict[str, Any]:
    manifest = _object(value, label="command manifest")
    _exact_keys(
        manifest,
        {"schema_version", "commands"},
        label="command manifest",
    )
    if manifest["schema_version"] != COMMAND_MANIFEST_SCHEMA_VERSION:
        raise ValueError("command manifest schema version is not admitted")
    commands = manifest["commands"]
    if not isinstance(commands, list) or not 1 <= len(commands) <= 64:
        raise ValueError("command manifest must contain 1..64 commands")

    normalized: list[dict[str, Any]] = []
    observed_ids: set[str] = set()
    for index, raw_command in enumerate(commands):
        command = _object(raw_command, label=f"command[{index}]")
        _exact_keys(command, {"id", "argv"}, label=f"command[{index}]")
        command_id = command["id"]
        if (
            not isinstance(command_id, str)
            or COMMAND_ID_PATTERN.fullmatch(command_id) is None
            or command_id in observed_ids
        ):
            raise ValueError(f"command[{index}] id is invalid or duplicated")
        observed_ids.add(command_id)

        argv = command["argv"]
        if not isinstance(argv, list) or not 1 <= len(argv) <= 128:
            raise ValueError(f"command[{index}] argv must contain 1..128 tokens")
        if any(
            not isinstance(token, str)
            or not token
            or len(token) > 4096
            or "\n" in token
            or "\r" in token
            for token in argv
        ):
            raise ValueError(f"command[{index}] argv contains an invalid token")
        if Path(argv[0]).name.casefold() in SHELL_WRAPPERS:
            raise ValueError(f"command[{index}] shell wrappers are forbidden")
        if any(token in COMPOUND_TOKENS for token in argv):
            raise ValueError(f"command[{index}] compound shell tokens are forbidden")
        if _is_python_executable(argv[0]) and len(argv) > 1:
            if _looks_like_repository_script(argv[1]):
                raise ValueError(
                    f"command[{index}] repository scripts must use python -m"
                )
            if argv[1] == "-m" and len(argv) < 3:
                raise ValueError(f"command[{index}] python -m requires a module")

        normalized.append({"id": command_id, "argv": list(argv)})

    return {
        "schema_version": COMMAND_MANIFEST_SCHEMA_VERSION,
        "commands": normalized,
    }


def load_command_manifest(path: Path) -> dict[str, Any]:
    return validate_command_manifest(_load_json(path, label="command manifest"))


def command_manifest_sha256(manifest: dict[str, Any]) -> str:
    admitted = validate_command_manifest(manifest)
    return hashlib.sha256(_canonical_bytes(admitted)).hexdigest()


def admit_command_results(
    *,
    manifest: dict[str, Any],
    results: object,
    decision: str,
) -> list[dict[str, Any]]:
    admitted = validate_command_manifest(manifest)
    if decision not in {"pass", "revision_required"}:
        raise ValueError("review decision is not admitted")
    if not isinstance(results, list) or len(results) != len(admitted["commands"]):
        raise ValueError("command results must exactly match manifest length")

    normalized: list[dict[str, Any]] = []
    for index, (expected, raw_result) in enumerate(
        zip(admitted["commands"], results, strict=True)
    ):
        result = _object(raw_result, label=f"command_result[{index}]")
        _exact_keys(
            result,
            {"id", "argv", "exit_code"},
            label=f"command_result[{index}]",
        )
        if result["id"] != expected["id"] or result["argv"] != expected["argv"]:
            raise ValueError(f"command_result[{index}] does not exactly match manifest")
        exit_code = result["exit_code"]
        if isinstance(exit_code, bool) or not isinstance(exit_code, int):
            raise ValueError(f"command_result[{index}] exit_code must be an integer")
        normalized.append(
            {"id": expected["id"], "argv": expected["argv"], "exit_code": exit_code}
        )

    if decision == "pass" and any(row["exit_code"] != 0 for row in normalized):
        raise ValueError("pass decision requires every command exit code to be zero")
    return normalized


def _observation_map(viable: list[dict[str, Any]]) -> tuple[list[str], bool]:
    observations = [row["next_observation"] for row in viable]
    usable = all(isinstance(value, str) and value.strip() for value in observations)
    if not usable:
        return [], False
    normalized = [value.strip() for value in observations]
    return normalized, len(set(normalized)) == len(normalized)


def assess_diagnostic_packet(value: object) -> dict[str, Any]:
    packet = _object(value, label="diagnostic packet")
    _exact_keys(
        packet,
        {
            "schema_version",
            "coordinate",
            "hypotheses",
            "proposed_claim",
            "proposed_action",
            "remaining_diagnostic_attempts",
            "remaining_corrections",
        },
        label="diagnostic packet",
    )
    if packet["schema_version"] != DIAGNOSTIC_PACKET_SCHEMA_VERSION:
        raise ValueError("diagnostic packet schema version is not admitted")
    coordinate = packet["coordinate"]
    if (
        not isinstance(coordinate, str)
        or not coordinate.strip()
        or len(coordinate) > 160
    ):
        raise ValueError("diagnostic coordinate is invalid")
    claim = packet["proposed_claim"]
    if claim not in {"observation_only", "necessary_defect", "exclusive_cause"}:
        raise ValueError("diagnostic proposed_claim is not admitted")
    action = packet["proposed_action"]
    if action not in {"diagnostic", "correction", "stop"}:
        raise ValueError("diagnostic proposed_action is not admitted")
    remaining_attempts = packet["remaining_diagnostic_attempts"]
    remaining_corrections = packet["remaining_corrections"]
    if (
        isinstance(remaining_attempts, bool)
        or not isinstance(remaining_attempts, int)
        or remaining_attempts < 0
        or isinstance(remaining_corrections, bool)
        or not isinstance(remaining_corrections, int)
        or remaining_corrections < 0
    ):
        raise ValueError("remaining budgets must be nonnegative integers")

    hypotheses = packet["hypotheses"]
    if not isinstance(hypotheses, list) or not 1 <= len(hypotheses) <= 64:
        raise ValueError("diagnostic packet must contain 1..64 hypotheses")
    normalized: list[dict[str, Any]] = []
    observed_ids: set[str] = set()
    for index, raw_hypothesis in enumerate(hypotheses):
        hypothesis = _object(raw_hypothesis, label=f"hypothesis[{index}]")
        _exact_keys(
            hypothesis,
            {"id", "status", "next_observation"},
            label=f"hypothesis[{index}]",
        )
        hypothesis_id = hypothesis["id"]
        if (
            not isinstance(hypothesis_id, str)
            or HYPOTHESIS_ID_PATTERN.fullmatch(hypothesis_id) is None
            or hypothesis_id in observed_ids
        ):
            raise ValueError(f"hypothesis[{index}] id is invalid or duplicated")
        observed_ids.add(hypothesis_id)
        status = hypothesis["status"]
        if status not in {"viable", "eliminated"}:
            raise ValueError(f"hypothesis[{index}] status is not admitted")
        observation = hypothesis["next_observation"]
        if observation is not None and (
            not isinstance(observation, str)
            or not observation.strip()
            or len(observation) > 500
        ):
            raise ValueError(f"hypothesis[{index}] next_observation is invalid")
        if status == "eliminated" and observation is not None:
            raise ValueError("eliminated hypotheses cannot carry next observations")
        normalized.append(
            {
                "id": hypothesis_id,
                "status": status,
                "next_observation": observation,
            }
        )

    viable = [row for row in normalized if row["status"] == "viable"]
    viable_ids = [row["id"] for row in viable]
    observations, observations_are_distinct = _observation_map(viable)
    reasons: list[str] = []

    if action == "stop":
        status = "stop"
    else:
        if not viable:
            reasons.append("no_viable_hypothesis")
        if claim == "exclusive_cause" and len(viable) != 1:
            reasons.append("exclusive_cause_not_isolated")
        if action == "diagnostic":
            if remaining_attempts < 1:
                reasons.append("diagnostic_attempt_budget_exhausted")
            if not observations_are_distinct:
                reasons.append("diagnostic_outcomes_do_not_discriminate")
        if action == "correction":
            if remaining_corrections < 1:
                reasons.append("correction_budget_exhausted")
            if claim == "observation_only":
                reasons.append("correction_requires_defect_claim")
            if len(viable) > 1:
                if claim != "necessary_defect":
                    reasons.append("multi_hypothesis_correction_must_be_necessary_only")
                if remaining_attempts < 1:
                    reasons.append("post_correction_diagnostic_budget_exhausted")
                if not observations_are_distinct:
                    reasons.append(
                        "correction_would_not_create_discriminating_evidence"
                    )
        status = "revision_required" if reasons else "proceed"

    return {
        "schema_version": DECISION_SCHEMA_VERSION,
        "status": status,
        "coordinate": coordinate,
        "viable_hypothesis_ids": viable_ids,
        "distinct_observations": observations if observations_are_distinct else [],
        "reasons": reasons,
    }


def write_json_lf(path: Path, payload: dict[str, Any]) -> None:
    path.write_bytes(_canonical_bytes(payload))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate an Ariadne diagnostic decision or command manifest."
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--diagnostic-packet", type=Path)
    source.add_argument("--command-manifest", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        if args.diagnostic_packet is not None:
            payload = assess_diagnostic_packet(
                _load_json(args.diagnostic_packet, label="diagnostic packet")
            )
        else:
            manifest = load_command_manifest(args.command_manifest)
            payload = {
                "schema_version": DECISION_SCHEMA_VERSION,
                "status": "passed",
                "command_count": len(manifest["commands"]),
                "command_manifest_sha256": command_manifest_sha256(manifest),
                "reasons": [],
            }
    except (OSError, ValueError) as error:
        print(f"ariadne evidence gate failed: {error}", file=sys.stderr)
        return 2
    if args.output:
        write_json_lf(args.output, payload)
    else:
        print(json.dumps(payload, indent=2, sort_keys=True))
    return 2 if payload["status"] == "revision_required" else 0


if __name__ == "__main__":
    raise SystemExit(main())
