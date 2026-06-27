"""Run a non-mutating Bernie booking-instruction interpreter smoke check.

The default smoke uses the deterministic fake provider. Live Gemini/Vertex
requires both ``--provider gemini_vertex`` and ``--allow-live`` so a copied
command cannot accidentally send text to the model provider.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.schemas.appointments import BernieBookingInstructionInterpretIn
from app.services.bernie_booking_interpreter import get_booking_instruction_interpreter


DEFAULT_INSTRUCTION = (
    "practitioner_id:420fb926-750b-4914-910b-e9d3f804e0f0 "
    "tomorrow 15 minutes earliest_time:09:00 latest_time:12:00"
)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Smoke-check Bernie booking-instruction interpretation without "
            "searching slots, creating proposals, confirming bookings, or "
            "writing appointments."
        )
    )
    parser.add_argument(
        "--provider",
        choices=("disabled", "fake", "gemini_vertex"),
        default="fake",
        help="Interpreter provider to exercise. Default: fake.",
    )
    parser.add_argument(
        "--allow-live",
        action="store_true",
        help="Required with --provider gemini_vertex; may send instruction text to Gemini/Vertex.",
    )
    parser.add_argument(
        "--instruction",
        default=DEFAULT_INSTRUCTION,
        help="Non-PHI staff instruction to interpret. Avoid real patient details.",
    )
    parser.add_argument(
        "--reference-date",
        type=date.fromisoformat,
        default=None,
        help="Optional YYYY-MM-DD reference date for relative dates such as today/tomorrow.",
    )
    parser.add_argument(
        "--expect-result",
        choices=("interpreted", "clarification_required", "blocked"),
        default=None,
        help="Exit non-zero unless Bernie returns this result.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print the full structured envelope as JSON.",
    )
    return parser


def _redacted_command(command: dict[str, Any] | None) -> dict[str, Any] | None:
    if command is None:
        return None
    redacted = dict(command)
    for key in ("patient_id", "practitioner_id", "appointment_type_id", "location_id"):
        if redacted.get(key):
            redacted[key] = "[id-present]"
    return redacted


def _compact_payload(envelope: dict[str, Any]) -> dict[str, Any]:
    return {
        "provider": envelope["provider_metadata"]["provider"],
        "mode": envelope["provider_metadata"]["mode"],
        "live_provider": envelope["provider_metadata"]["live_provider"],
        "safe": envelope["safe"],
        "result": envelope["result"],
        "confidence": envelope["confidence"],
        "summary": envelope["summary"],
        "missing_fields": envelope["missing_fields"],
        "safety_flags": envelope["safety_flags"],
        "clarifying_question": envelope["clarifying_question"],
        "command_candidate": _redacted_command(envelope.get("command_candidate")),
        "block_codes": [block["code"] for block in envelope.get("blocks", [])],
        "warning_codes": [warning["code"] for warning in envelope.get("warnings", [])],
    }


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    if args.provider == "gemini_vertex" and not args.allow_live:
        print(
            "Refusing live Gemini/Vertex smoke without --allow-live. "
            "Use only non-PHI instruction text.",
            file=sys.stderr,
        )
        return 2

    body = BernieBookingInstructionInterpretIn(
        instruction=args.instruction,
        reference_date=args.reference_date,
    )
    interpreter = get_booking_instruction_interpreter(args.provider)
    envelope = interpreter.interpret(body).model_dump(mode="json")

    if args.expect_result and envelope["result"] != args.expect_result:
        print(
            f"Expected result {args.expect_result!r}, got {envelope['result']!r}.",
            file=sys.stderr,
        )
        print(json.dumps(_compact_payload(envelope), indent=2, sort_keys=True))
        return 1

    payload = envelope if args.json else _compact_payload(envelope)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
