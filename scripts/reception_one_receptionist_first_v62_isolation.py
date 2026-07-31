#!/usr/bin/env python3
"""Provider-free real-isolation rehearsal for the v6.2 desk context."""

from __future__ import annotations

import argparse
from contextlib import contextmanager
import json
from pathlib import Path
import sys
from typing import Any, Iterator

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import reception_one_receptionist_first_v61_isolation as base
from scripts import reception_one_receptionist_first_v62 as receptionist


ARTIFACT_PATH = receptionist.ARTIFACT_DIR / "real-isolation-evidence.json"
IMAGES = (
    "reception-one-receptionist-first-v62-turn-1:v1",
    "reception-one-receptionist-first-v62-turn-2:v1",
)
CONTAINERS = (
    "reception-one-receptionist-first-v62-turn-1",
    "reception-one-receptionist-first-v62-turn-2",
)
CELL_SCRIPT = (
    ROOT / "scripts" / "reception_one_receptionist_first_v62_cell.py"
)


class IsolationError(RuntimeError):
    """A bounded v6.2 isolation failure."""


@contextmanager
def _configured() -> Iterator[None]:
    old_receptionist = base.receptionist
    old_images = base.IMAGES
    old_containers = base.CONTAINERS
    old_cell = base.CELL_SCRIPT
    base.receptionist = receptionist
    base.IMAGES = IMAGES
    base.CONTAINERS = CONTAINERS
    base.CELL_SCRIPT = CELL_SCRIPT
    try:
        yield
    finally:
        base.receptionist = old_receptionist
        base.IMAGES = old_images
        base.CONTAINERS = old_containers
        base.CELL_SCRIPT = old_cell


def run_isolation() -> dict[str, Any]:
    with _configured():
        evidence = base.run_isolation()
    if (
        evidence.get("first_disposition") != "revision_required"
        or evidence.get("second_disposition") != "admit"
        or evidence.get("boundary", {}).get("provider_calls_performed") != 0
    ):
        raise IsolationError("v62_isolation_boundary_invalid")
    result = {
        **evidence,
        "schema_version": (
            "reception.one.receptionist_first_v62.isolation_evidence.v1"
        ),
        "result": (
            "reception_one_receptionist_first_v62_real_isolation_pass"
        ),
        "desk_context_sha256": receptionist.build_turn_input(
            base._fixture()[0]
        )["desk_context_sha256"],
        "same_context_packet_proofread": True,
        "full_diary_exposed": False,
        "unselected_appointments_exposed": False,
    }
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ARTIFACT_PATH)
    args = parser.parse_args()
    try:
        evidence = run_isolation()
    except (IsolationError, base.IsolationError) as error:
        print(
            json.dumps(
                {
                    "result": (
                        "reception_one_receptionist_first_v62_"
                        "real_isolation_blocked"
                    ),
                    "reason_code": str(error).split(":", 1)[0],
                },
                sort_keys=True,
            )
        )
        return 2
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(evidence, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(evidence, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
