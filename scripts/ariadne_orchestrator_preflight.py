"""Emit an advisory generic Ariadne orchestrator receipt from supplied state."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from orchestration_harness.orchestrator_preflight import build_orchestrator_receipt
from orchestration_harness.settings_fingerprint import settings_fingerprint

SETTINGS_DIR = REPO_ROOT / "orchestration" / "harness_settings"


def _yaml(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a YAML object")
    return payload


def configured_continuation_events(
    settings_dir: Path = SETTINGS_DIR,
) -> tuple[str, ...]:
    """Return the exact configured receipt-event vocabulary in policy order."""
    requirements = _yaml(settings_dir / "orchestrator_requirements.yaml")
    events = requirements.get("continuation_events")
    if (
        not isinstance(events, list)
        or not events
        or any(not isinstance(event, str) or not event for event in events)
        or len(set(events)) != len(events)
    ):
        raise ValueError("configured continuation_events must be unique text values")
    return tuple(events)


def build_receipt(
    *, runtime_state_path: Path, settings_dir: Path = SETTINGS_DIR
) -> dict[str, Any]:
    runtime_state = json.loads(runtime_state_path.read_text(encoding="utf-8"))
    if not isinstance(runtime_state, dict):
        raise ValueError("runtime state must be a JSON object")
    return build_orchestrator_receipt(
        requirements=_yaml(settings_dir / "orchestrator_requirements.yaml"),
        adapters=_yaml(settings_dir / "transport_adapters.yaml"),
        worker_pool=_yaml(settings_dir / "worker_pool.yaml"),
        runtime_state=runtime_state,
        settings_fingerprint=settings_fingerprint(settings_dir),
    )


def write_json_lf(path: Path, payload: dict[str, Any]) -> None:
    """Write canonical UTF-8 JSON with LF bytes on every platform."""
    rendered = json.dumps(payload, indent=2, sort_keys=True)
    path.write_bytes((rendered + "\n").encode("utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build an advisory generic Ariadne orchestrator receipt."
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--runtime-state", type=Path)
    source.add_argument(
        "--list-continuation-events",
        action="store_true",
        help="List the exact configured continuation-event vocabulary and exit.",
    )
    parser.add_argument("--settings-dir", type=Path, default=SETTINGS_DIR)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        if args.list_continuation_events:
            events = configured_continuation_events(args.settings_dir)
            print("\n".join(events))
            return 0
        receipt = build_receipt(
            runtime_state_path=args.runtime_state, settings_dir=args.settings_dir
        )
    except (OSError, ValueError, json.JSONDecodeError, yaml.YAMLError) as error:
        print(f"ariadne orchestrator preflight failed: {error}", file=sys.stderr)
        return 2
    if args.output:
        write_json_lf(args.output, receipt)
    else:
        print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if receipt["status"] == "passed" else 2


if __name__ == "__main__":
    raise SystemExit(main())
