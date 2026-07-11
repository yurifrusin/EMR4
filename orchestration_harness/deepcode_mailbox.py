"""Local-only Deep Code notify-event validation and persistence."""

from __future__ import annotations

import json
import os
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Mapping


def build_notify_event(environ: Mapping[str, str]) -> dict[str, object]:
    """Build an untrusted local event from Deep Code's documented notify vars."""
    status = environ.get("STATUS", "")
    if status not in {"completed", "failed"}:
        raise ValueError("STATUS must be completed or failed")
    duration = environ.get("DURATION", "")
    if not duration.isdigit():
        raise ValueError("DURATION must be a non-negative integer")
    body = environ.get("BODY", "")
    if not isinstance(body, str):
        raise ValueError("BODY must be a string")
    return {
        "schema_version": "ariadne.deepcode_notify_event.v1",
        "event_id": str(uuid.uuid4()),
        "recorded_at": datetime.now(UTC).isoformat(),
        "source": "deepcode_notify",
        "status": status,
        "duration_seconds": int(duration),
        "title": environ.get("TITLE", ""),
        "fail_reason": environ.get("FAIL_REASON", ""),
        "body": body,
        "trust": "untrusted_worker_output_requires_packet_artifact_validation",
    }


def write_notify_event(*, outbox: Path, environ: Mapping[str, str] | None = None) -> Path:
    event = build_notify_event(os.environ if environ is None else environ)
    outbox.mkdir(parents=True, exist_ok=True)
    path = outbox / f"{event['recorded_at'].replace(':', '').replace('+', '_')}_{event['event_id']}.json"
    path.write_text(json.dumps(event, indent=2) + "\n", encoding="utf-8")
    return path
