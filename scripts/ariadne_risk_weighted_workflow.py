#!/usr/bin/env python3
"""Thin deterministic CLI for the Ariadne risk-weighted workflow core.

The CLI reads only explicitly supplied JSON files and provides the
validation, classification, rerun and admission operations defined by the
frozen plan. A render operation writes only to explicitly supplied output
paths for closeout, Sol acceptance, Yuri summary, Continuity payload and
Compass payload. It executes no command, opens no database, contacts no
provider and applies no authority update.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import orchestration_harness.risk_weighted_workflow as rw

BRISBANE = ZoneInfo("Australia/Brisbane")


def _load_json(path: Path, *, label: str) -> dict[str, Any]:
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as error:
        raise ValueError(f"{label} could not be read: {error}") from error
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as error:
        raise ValueError(f"{label} must be valid JSON") from error
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a JSON object")
    return value


def _canonical_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def _now_brisbane(timestamp: str | None) -> datetime:
    if timestamp is None:
        return datetime.now(tz=BRISBANE)
    # Deterministic override used by tests and replay; must carry an explicit
    # UTC offset in the +10:00 Australia/Brisbane timezone.
    parsed = datetime.fromisoformat(timestamp)
    if parsed.tzinfo is None:
        raise ValueError("--timestamp must carry an explicit UTC offset")
    return parsed.astimezone(BRISBANE)


def _render_markdown_header(title: str, rendered_at: datetime) -> str:
    date_line = rendered_at.date().isoformat()
    iso_line = rendered_at.isoformat(timespec="seconds")
    return (
        f"# {title}\n\n"
        f"Date: {date_line}\n\n"
        f"Generated at: {iso_line} (Australia/Brisbane)\n\n"
    )


def render_packet(
    profile_value: dict[str, Any],
    result_value: dict[str, Any],
    *,
    timestamp: str | None = None,
) -> dict[str, str]:
    """Render the closeout packet to strings keyed by artifact name.

    Deterministic for a fixed ``timestamp``. Never writes, executes or mutates
    any authority source; callers supply explicit output paths.
    """
    profile = rw.validate_profile(profile_value)
    result = rw.validate_result(result_value)
    admission = rw.admit_result(profile_value, result_value)
    rendered_at = _now_brisbane(timestamp)
    tranche_id = profile["tranche_id"]
    tier = profile["derived_tier"]
    decision = admission["decision"]
    profile_sha256 = admission["profile_sha256"]

    technical = (
        _render_markdown_header("Ariadne risk-weighted tranche closeout", rendered_at)
        + f"- Tranche: {tranche_id}\n"
        + f"- Profile SHA-256: {profile_sha256}\n"
        + f"- Classified tier: {tier}\n"
        + f"- Deterministic admission: {decision}\n"
        + f"- Source HEAD: {profile['source_head']}\n"
        + f"- Source tree: {profile['source_tree']}\n\n"
        + "This document is generated evidence only. It does not decide "
        + "acceptance, does not modify AGENTS, Continuity, Compass, Git, the "
        + "latch or any protected ref, and executes no command.\n"
    )

    sol = (
        _render_markdown_header("Sol acceptance summary", rendered_at)
        + f"- Tranche: {tranche_id}\n"
        + f"- Classified tier: {tier}\n"
        + f"- Deterministic admission: {decision}\n"
        + f"- Profile SHA-256: {profile_sha256}\n\n"
        + "Sol alone owns acceptance and integration. This generated summary "
        + "is candidate evidence and never acceptance.\n"
    )

    yuri = (
        _render_markdown_header("Yuri lay/technical mailbox summary", rendered_at)
        + f"- Tranche: {tranche_id}\n"
        + f"- Classified tier: {tier}\n"
        + f"- Deterministic admission: {decision}\n\n"
        + "The risk-weighted workflow reform retains hard controls while "
        + "removing redundant receipts, full-suite reruns, external-review "
        + "stacking, volatile hash cascades and mutation-count ceremony.\n"
    )

    continuity = {
        "schema_version": "ariadne.continuity_update.v1",
        "tranche_id": tranche_id,
        "profile_sha256": profile_sha256,
        "classified_tier": tier,
        "decision": decision,
        "generated_at": rendered_at.isoformat(timespec="seconds"),
        "timezone": "Australia/Brisbane",
        "authority_boundary": "generated_payload_applied_by_sol_only",
    }

    compass = {
        "schema_version": "ariadne.compass_update.v1",
        "tranche_id": tranche_id,
        "profile_sha256": profile_sha256,
        "classified_tier": tier,
        "decision": decision,
        "generated_at": rendered_at.isoformat(timespec="seconds"),
        "timezone": "Australia/Brisbane",
        "authority_boundary": "generated_payload_applied_by_sol_only",
    }

    return {
        "closeout": technical,
        "sol_acceptance": sol,
        "yuri_summary": yuri,
        "continuity_payload": _canonical_json(continuity),
        "compass_payload": _canonical_json(compass),
    }


def _run_validate(args: argparse.Namespace) -> int:
    payload: dict[str, Any] = {}
    if args.profile is not None:
        profile = rw.validate_profile(_load_json(args.profile, label="profile"))
        payload["profile"] = {
            "schema_version": profile["schema_version"],
            "tranche_id": profile["tranche_id"],
            "status": "passed",
            "derived_tier": profile["derived_tier"],
            "required_baseline": profile["required_baseline"],
            "required_final_vetoes": profile["required_final_vetoes"],
            "rerun_requirements": profile["rerun_requirements"],
        }
    if args.result is not None:
        result = rw.validate_result(_load_json(args.result, label="result"))
        payload["result"] = {
            "schema_version": result["schema_version"],
            "tranche_id": result["tranche_id"],
            "status": "passed",
            "classified_tier": result["classified_tier"],
            "decision": result["decision"],
        }
    if not payload:
        raise ValueError("validate requires --profile and/or --result")
    payload["status"] = "passed"
    _emit(payload, args.output)
    return 0


def _run_classify(args: argparse.Namespace) -> int:
    profile = rw.validate_profile(_load_json(args.profile, label="profile"))
    _emit(
        {
            "schema_version": rw.PROFILE_SCHEMA_VERSION,
            "tranche_id": profile["tranche_id"],
            "derived_tier": profile["derived_tier"],
            "required_baseline": profile["required_baseline"],
            "required_final_vetoes": profile["required_final_vetoes"],
        },
        args.output,
    )
    return 0


def _run_rerun(args: argparse.Namespace) -> int:
    profile = rw.validate_profile(_load_json(args.profile, label="profile"))
    rerun = profile["rerun_requirements"]
    _emit(
        {
            "schema_version": rw.PROFILE_SCHEMA_VERSION,
            "tranche_id": profile["tranche_id"],
            "derived_tier": profile["derived_tier"],
            "required_rerun": rerun,
        },
        args.output,
    )
    return 0


def _run_admit(args: argparse.Namespace) -> int:
    profile_value = _load_json(args.profile, label="profile")
    result_value = _load_json(args.result, label="result")
    admission = rw.admit_result(profile_value, result_value)
    _emit(admission, args.output)
    return 0 if admission["decision"] == "pass" else 2


def _run_render(args: argparse.Namespace) -> int:
    profile_value = _load_json(args.profile, label="profile")
    result_value = _load_json(args.result, label="result")
    packet = render_packet(profile_value, result_value, timestamp=args.timestamp)
    outputs = {
        "closeout": args.closeout,
        "sol_acceptance": args.sol_acceptance,
        "yuri_summary": args.yuri_summary,
        "continuity_payload": args.continuity_payload,
        "compass_payload": args.compass_payload,
    }
    written: list[str] = []
    for artifact, path_value in outputs.items():
        if path_value is None:
            continue
        _write(path_value, packet[artifact])
        written.append(artifact)
    _emit(
        {
            "schema_version": "ariadne.risk_weighted_render.v1",
            "tranche_id": profile_value.get("tranche_id"),
            "status": "rendered",
            "artifacts": written,
            "authority_boundary": "no_authority_source_modified",
        },
        args.output,
    )
    return 0


def _emit(payload: dict[str, Any], output: Path | None) -> None:
    rendered = _canonical_json(payload)
    if output is not None:
        _write(output, rendered)
    else:
        print(rendered, end="")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Deterministic Ariadne risk-weighted workflow CLI."
    )
    subparsers = parser.add_subparsers(dest="operation", required=True)

    validate = subparsers.add_parser("validate", help="Validate profile and/or result JSON.")
    validate.add_argument("--profile", type=Path)
    validate.add_argument("--result", type=Path)
    validate.add_argument("--output", type=Path)
    validate.set_defaults(func=_run_validate)

    classify = subparsers.add_parser("classify", help="Derive the highest risk tier.")
    classify.add_argument("--profile", type=Path, required=True)
    classify.add_argument("--output", type=Path)
    classify.set_defaults(func=_run_classify)

    rerun = subparsers.add_parser("rerun", help="Return the union rerun decision.")
    rerun.add_argument("--profile", type=Path, required=True)
    rerun.add_argument("--output", type=Path)
    rerun.set_defaults(func=_run_rerun)

    admit = subparsers.add_parser("admit", help="Admit a result against its profile.")
    admit.add_argument("--profile", type=Path, required=True)
    admit.add_argument("--result", type=Path, required=True)
    admit.add_argument("--output", type=Path)
    admit.set_defaults(func=_run_admit)

    render = subparsers.add_parser("render", help="Render the non-executing closeout packet.")
    render.add_argument("--profile", type=Path, required=True)
    render.add_argument("--result", type=Path, required=True)
    render.add_argument("--closeout", type=Path)
    render.add_argument("--sol-acceptance", type=Path)
    render.add_argument("--yuri-summary", type=Path)
    render.add_argument("--continuity-payload", type=Path)
    render.add_argument("--compass-payload", type=Path)
    render.add_argument("--timestamp", type=str)
    render.add_argument("--output", type=Path)
    render.set_defaults(func=_run_render)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except (OSError, ValueError) as error:
        print(f"ariadne risk-weighted workflow failed: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
