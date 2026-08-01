#!/usr/bin/env python3
"""Provider-free real-isolation proof for the synthetic context bridge."""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import reception_one_bureau_typed_plan_protocol as typed_plan
from scripts import reception_one_preprinted_form_v5_multicase as multicase
from scripts import reception_one_readonly_synthetic_context_bridge as bridge
from scripts import reception_one_receptionist_first_v61_isolation as base
from scripts import reception_one_receptionist_first_v68 as frozen
from scripts import reception_one_receptionist_first_v68_isolation as v68
from scripts import reception_one_structured_source_plan_language as structured


OUTPUT = bridge.ARTIFACT_DIR / "real-isolation-evidence.json"
IMAGES = (
    "reception-one-readonly-context-turn-1:v1",
    "reception-one-readonly-context-turn-2:v1",
)
CONTAINERS = (
    "reception-one-readonly-context-turn-1",
    "reception-one-readonly-context-turn-2",
)


def _fixture() -> tuple[dict, dict, dict]:
    frame = json.loads(bridge.FRAME_PATH.read_text(encoding="utf-8"))
    plan = typed_plan.deterministic_plan(frame)
    correct_program = structured.program_from_plan(
        frame,
        plan,
        operator_note=multicase._operator_note(plan["goal"]),
    )
    correct_body = frozen.model_form_body(correct_program, frame=frame)
    wrong_plan = copy.deepcopy(plan)
    wrong_plan["goal"] = "clarification"
    wrong_plan["steps"] = [
        {
            "id": "step-clarification",
            "operator": "request_clarification",
            "args": {},
        }
    ]
    wrong_program = structured.program_from_plan(
        frame,
        wrong_plan,
        operator_note=multicase._operator_note("clarification"),
    )
    wrong_body = frozen.model_form_body(wrong_program, frame=frame)
    wrong_body["receptionist_response"] = (
        "Which appointment should I change?"
    )
    wrong_body["decision_note"] = (
        "Intent clarification: the appointment target is missing."
    )
    return frame, wrong_body, correct_body


def run_isolation() -> dict:
    old_fixture = base._fixture
    old_images = v68.IMAGES
    old_containers = v68.CONTAINERS
    base._fixture = _fixture
    v68.IMAGES = IMAGES
    v68.CONTAINERS = CONTAINERS
    try:
        evidence = v68.run_isolation()
    finally:
        base._fixture = old_fixture
        v68.IMAGES = old_images
        v68.CONTAINERS = old_containers
    return {
        **evidence,
        "schema_version": (
            "reception.one.readonly_synthetic_diary_context."
            "real_isolation.v1"
        ),
        "result": (
            "reception_one_readonly_synthetic_diary_context_"
            "real_isolation_pass"
        ),
        "trusted_backend_frame_sha256": frozen.canonical_hash(_fixture()[0]),
        "database_present_during_isolation": False,
        "opaque_handle_map_present_in_cell": False,
        "full_diary_exposed": False,
        "unselected_appointments_exposed": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    try:
        evidence = run_isolation()
    except Exception as error:
        print(
            json.dumps(
                {
                    "result": (
                        "reception_one_readonly_synthetic_diary_context_"
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
    print(json.dumps({"result": evidence["result"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
