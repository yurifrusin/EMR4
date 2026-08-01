#!/usr/bin/env python3
"""Provider-free real-isolation rehearsal for v6's two-channel dialogue."""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
import shutil
import sys
import tempfile
from typing import Any, Iterator
from contextlib import contextmanager

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import reception_one_bureau_typed_plan_protocol as typed_plan
from scripts import reception_one_preprinted_form_v5_isolation as base
from scripts import reception_one_preprinted_form_v5_multicase as multicase
from scripts import reception_one_receptionist_first_v6 as receptionist
from scripts import reception_one_receptionist_first_v6_cohort as cohort
from scripts import reception_one_structured_source_plan_language as structured


ARTIFACT_PATH = receptionist.ARTIFACT_DIR / "real-isolation-evidence.json"
IMAGES = (
    "reception-one-receptionist-first-v6-turn-1:v1",
    "reception-one-receptionist-first-v6-turn-2:v1",
)
CONTAINERS = (
    "reception-one-receptionist-first-v6-turn-1",
    "reception-one-receptionist-first-v6-turn-2",
)
CELL_SCRIPT = (
    ROOT / "scripts" / "reception_one_receptionist_first_v6_cell.py"
)


class IsolationError(RuntimeError):
    """A bounded v6 isolation failure."""


@contextmanager
def _configured_base() -> Iterator[None]:
    old_images = base.IMAGES
    old_containers = base.CONTAINERS
    old_cell = base.CELL_SCRIPT
    base.IMAGES = IMAGES
    base.CONTAINERS = CONTAINERS
    base.CELL_SCRIPT = CELL_SCRIPT
    try:
        yield
    finally:
        base.IMAGES = old_images
        base.CONTAINERS = old_containers
        base.CELL_SCRIPT = old_cell


def _fixture() -> tuple[dict[str, Any], dict[str, Any]]:
    _, cases = cohort.load_source_manifest()
    case = next(
        item for item in cases if item["case_code"] == "b-move-resched"
    )
    frame = cohort.frame_for_case(case)
    plan = typed_plan.deterministic_plan(frame)
    program = structured.program_from_plan(
        frame,
        plan,
        operator_note=multicase._operator_note(plan["goal"]),
    )
    return frame, receptionist.model_form_body(program, frame=frame)


def run_isolation() -> dict[str, Any]:
    docker = shutil.which("docker")
    if docker is None:
        raise IsolationError("docker_unavailable")
    with _configured_base():
        if any(
            base.exists(docker, kind, reference)
            for kind, references in (
                ("container", CONTAINERS),
                ("image", IMAGES),
            )
            for reference in references
        ):
            raise IsolationError("owned_residue_preexisted")

        frame, corrected_body = _fixture()
        first_body = copy.deepcopy(corrected_body)
        first_body["receptionist_response"] = (
            "I have moved the appointment and it is ready for review."
        )
        first_input = receptionist.build_turn_input(frame)
        packets: list[dict[str, Any]] = []
        inspections: list[dict[str, bool]] = []
        manifests: list[dict[str, str]] = []
        cleanup_errors: list[str] = []
        with tempfile.TemporaryDirectory(
            prefix="reception-one-receptionist-first-v6-"
        ) as raw:
            root = Path(raw)
            first_context = root / "turn-1"
            manifests.append(
                base._context(
                    first_context,
                    turn_input=first_input,
                    body=first_body,
                )
            )
            ticket: dict[str, Any] | None = None
            try:
                packet, checks = base._run_turn(
                    docker,
                    index=1,
                    context=first_context,
                )
                packets.append(packet)
                inspections.append(checks)
                first_program = receptionist.assemble_program(
                    packet["model_form_body"]
                )
                first_evaluation = receptionist.evaluate_output(
                    frame,
                    first_program,
                    packet["model_form_body"],
                    turn_code=1,
                )
                ticket = receptionist.build_correction_ticket(
                    packet["model_form_body"],
                    first_program,
                    first_evaluation,
                )
                second_input = receptionist.build_turn_input(
                    frame,
                    correction_ticket=ticket,
                )
                second_context = root / "turn-2"
                manifests.append(
                    base._context(
                        second_context,
                        turn_input=second_input,
                        body=corrected_body,
                    )
                )
                packet, checks = base._run_turn(
                    docker,
                    index=2,
                    context=second_context,
                )
                packets.append(packet)
                inspections.append(checks)
            finally:
                for container in CONTAINERS:
                    if base.exists(docker, "container", container):
                        result = base.run_command(
                            docker,
                            ["rm", "--force", container],
                            allowed=frozenset({0, 1}),
                        )
                        if result.returncode != 0:
                            cleanup_errors.append(
                                "container_cleanup_failed"
                            )
                for image in IMAGES:
                    if base.exists(docker, "image", image):
                        result = base.run_command(
                            docker,
                            ["image", "rm", image],
                            allowed=frozenset({0, 1}),
                        )
                        if result.returncode != 0:
                            cleanup_errors.append("image_cleanup_failed")

        if len(packets) != 2 or ticket is None:
            raise IsolationError("two_turn_packets_missing")
        residue = {
            "containers_present": any(
                base.exists(docker, "container", item)
                for item in CONTAINERS
            ),
            "images_present": any(
                base.exists(docker, "image", item) for item in IMAGES
            ),
            "temporary_context_present": False,
        }
        if cleanup_errors or any(residue.values()):
            raise IsolationError("cleanup_or_residue_failed")
        first_program = receptionist.assemble_program(
            packets[0]["model_form_body"]
        )
        second_program = receptionist.assemble_program(
            packets[1]["model_form_body"]
        )
        first_evaluation = receptionist.evaluate_output(
            frame,
            first_program,
            packets[0]["model_form_body"],
            turn_code=1,
        )
        second_evaluation = receptionist.evaluate_output(
            frame,
            second_program,
            packets[1]["model_form_body"],
            turn_code=2,
        )
        if (
            first_evaluation["disposition"] != "revision_required"
            or packets[1]["correction_ticket_sha256"]
            != receptionist.canonical_hash(ticket)
            or second_evaluation["disposition"] != "admit"
        ):
            raise IsolationError("isolated_dialogue_not_admitted")
        execution = typed_plan.execute_plan(
            frame,
            second_evaluation["normalized_plan"],
            second_evaluation["semantic_review"],
        )
        if execution["final_output"]["write_performed"] is not False:
            raise IsolationError("isolated_execution_effect_violation")
        return {
            "schema_version": (
                "reception.one.receptionist_first_v6."
                "isolation_evidence.v1"
            ),
            "result": (
                "reception_one_receptionist_first_v6_real_isolation_pass"
            ),
            "evidence_mode": (
                "authored_synthetic_provider_free_two_turn_fixture"
            ),
            "source_manifest_sha256": receptionist.canonical_hash(manifests),
            "task_sha256": first_input["task_sha256"],
            "broker_owned_fields": receptionist.PREPRINTED_FIELDS,
            "model_authored_fields": list(
                receptionist.MODEL_AUTHORED_FIELDS
            ),
            "first_model_form_body_sha256": receptionist.canonical_hash(
                packets[0]["model_form_body"]
            ),
            "first_disposition": first_evaluation["disposition"],
            "first_violation_codes": [
                item["code"] for item in first_evaluation["violations"]
            ],
            "correction_ticket_sha256": receptionist.canonical_hash(ticket),
            "second_model_form_body_sha256": receptionist.canonical_hash(
                packets[1]["model_form_body"]
            ),
            "second_disposition": second_evaluation["disposition"],
            "released_proposal_family": execution["final_output"][
                "proposal_family"
            ],
            "container_policy_checks": inspections,
            "cell_isolation_observations": [
                packet["isolation"] for packet in packets
            ],
            "residue": residue,
            "boundary": {
                "provider_calls_performed": 0,
                "credential_reads_performed": 0,
                "api_key_authentication_used": False,
                "network_access_performed": False,
                "database_access_performed": False,
                "appointment_writes_performed": 0,
                "confirmation_performed": False,
                "product_delivery_performed": False,
                "natural_response_parsed_into_form": False,
                "hidden_reasoning_retained": False,
                "proofreader_selected_replacement": False,
                "broker_judgement_repair": False,
            },
        }


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
                        "reception_one_receptionist_first_v6_"
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
