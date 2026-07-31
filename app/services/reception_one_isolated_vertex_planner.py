"""Exact default-off isolated Vertex planner for authored-synthetic Reception One.

The trusted product route builds the frame. This adapter passes that frame to
the existing credential-free v6.8 runtime cell and one-use Bernie ADC broker.
Only the deterministic proofreader's typed release crosses back into the
product proposal adapter.
"""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
import hashlib
import json
from pathlib import Path
import threading
from typing import Any, Iterator


EXPECTED_BINDING = {
    "provider": "google_vertex_ai",
    "model_id": "gemini-2.5-flash",
    "project": "bernie-emr4-dev",
    "service_account": (
        "emr4-bernie-ai-dev@bernie-emr4-dev.iam.gserviceaccount.com"
    ),
    "authentication": "keyless_impersonated_service_account_adc",
    "location": "australia-southeast1",
    "endpoint_hostname": (
        "australia-southeast1-aiplatform.googleapis.com"
    ),
    "api_key_authentication_used": False,
}
GRAPH_PATH = Path("orchestration/continuity/emr4-continuity-graph.json")
COMPASS_PATH = Path("orchestration/continuity/emr4-compass.json")
_RUNTIME_LOCK = threading.Lock()
_LOCAL_FAILURE_CODES = frozenset(
    {
        "occupied_authority_missing",
        "occupied_authority_not_exact",
        "occupied_preflight_not_exact",
        "revision_binding_invalid",
        "occupied_output_already_exists",
        "task_scoped_runtime_name_collision",
        "provider_call_ceiling_invalid",
        "dialogue_identifier_budget_invalid",
    }
)


class IsolatedVertexPlannerError(RuntimeError):
    """A sanitized exact-boundary, lifecycle or proofreader failure."""


@dataclass(frozen=True)
class IsolatedVertexPlannerResult:
    final_output: dict[str, Any] | None
    review: dict[str, Any]
    normalized_plan: dict[str, Any]
    provider_calls: int
    runtime_audit_ref: str
    terminal_status: str
    receptionist_response: str | None = None


def _load_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise IsolatedVertexPlannerError(
            "isolated_vertex_control_artifact_invalid"
        ) from error
    if not isinstance(value, dict):
        raise IsolatedVertexPlannerError(
            "isolated_vertex_control_artifact_invalid"
        )
    return value


def _write_object(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _canonical_hash(value: dict[str, Any]) -> str:
    rendered = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(rendered).hexdigest()


def _canonical_timestamp(value: datetime) -> str:
    if value.tzinfo is None:
        raise IsolatedVertexPlannerError(
            "isolated_vertex_observed_at_timezone_required"
        )
    return value.isoformat().replace("+00:00", "Z")


def _bounded_local_failure_code(error: Exception) -> str:
    code = str(error).split(":", 1)[0]
    if code in _LOCAL_FAILURE_CODES:
        return code
    return "isolated_vertex_attempt_failed"


def _validate_frame(frame: dict[str, Any], observed_at: datetime) -> None:
    authority = frame.get("authority")
    if (
        frame.get("data_class") != "authored_synthetic"
        or frame.get("observed_at") != _canonical_timestamp(observed_at)
        or not isinstance(authority, dict)
        or authority.get("effect_ceiling") != "proposal_only"
        or authority.get("appointment_write_authority") is not False
        or authority.get("confirmation_authority") is not False
        or authority.get("provider_execution") is not False
        or authority.get("network_access") is not False
        or authority.get("database_access") is not False
        or authority.get("product_delivery") is not False
    ):
        raise IsolatedVertexPlannerError(
            "isolated_vertex_frame_boundary_invalid"
        )


def _resolve_control_path(raw_path: str, *, code: str) -> Path:
    value = (raw_path or "").strip()
    if not value:
        raise IsolatedVertexPlannerError(code)
    path = Path(value)
    if not path.is_file():
        raise IsolatedVertexPlannerError(code)
    return path


def _resolve_evidence_root(raw_path: str) -> Path:
    value = (raw_path or "").strip()
    if not value:
        raise IsolatedVertexPlannerError(
            "isolated_vertex_evidence_dir_required"
        )
    path = Path(value).resolve()
    cwd = Path.cwd().resolve()
    anchor = Path(path.anchor).resolve()
    if path in {cwd, anchor}:
        raise IsolatedVertexPlannerError(
            "isolated_vertex_evidence_dir_too_broad"
        )
    path.mkdir(parents=True, exist_ok=True)
    return path


def _continuity_binding() -> tuple[int, int]:
    graph = _load_object(GRAPH_PATH)
    compass = _load_object(COMPASS_PATH)
    graph_revision = graph.get("graph_revision")
    compass_revision = compass.get("map_revision")
    if (
        not isinstance(graph_revision, int)
        or not isinstance(compass_revision, int)
        or compass.get("source_graph_revision") != graph_revision
    ):
        raise IsolatedVertexPlannerError(
            "isolated_vertex_continuity_binding_invalid"
        )
    return graph_revision, compass_revision


def _request_slug(frame: dict[str, Any]) -> str:
    request_id = frame.get("request_id")
    if not isinstance(request_id, str) or not request_id:
        raise IsolatedVertexPlannerError(
            "isolated_vertex_request_id_invalid"
        )
    digest = hashlib.sha256(request_id.encode("utf-8")).hexdigest()[:16]
    return f"runtime-{digest}"


def _authority_call_ceiling(path: Path) -> int:
    authority = _load_object(path)
    value = authority.get("absolute_call_ceiling", 2)
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or value not in {1, 2}
    ):
        raise IsolatedVertexPlannerError(
            "isolated_vertex_call_ceiling_invalid"
        )
    return value


@contextmanager
def _runtime_contract() -> Iterator[tuple[Any, Any]]:
    from scripts import reception_one_preprinted_form_v5_live as parent_live
    from scripts import (
        reception_one_receptionist_first_v68_runtime as runtime_contract,
    )

    previous = parent_live.preprinted
    parent_live.preprinted = runtime_contract
    try:
        yield parent_live, runtime_contract
    finally:
        parent_live.preprinted = previous


def _goal_for_release(release: dict[str, Any] | None) -> str | None:
    if release is None:
        return None
    family = release.get("proposal_family")
    if family in {
        "create",
        "move",
        "resize",
        "cancel",
        "status_change",
        "squeeze_in_assessment",
        "clarification",
    }:
        return str(family)
    raise IsolatedVertexPlannerError(
        "isolated_vertex_release_family_invalid"
    )


def _review_from_turn(
    *,
    frame: dict[str, Any],
    turn: dict[str, Any],
    release: dict[str, Any] | None,
) -> tuple[dict[str, Any], str | None]:
    exchange = turn.get("exchange")
    if not isinstance(exchange, dict):
        raise IsolatedVertexPlannerError(
            "isolated_vertex_turn_evidence_invalid"
        )
    proofreader = exchange.get("proofreader")
    if not isinstance(proofreader, dict):
        raise IsolatedVertexPlannerError(
            "isolated_vertex_proofreader_evidence_missing"
        )
    disposition = proofreader.get("disposition")
    if release is not None:
        if disposition != "admit":
            raise IsolatedVertexPlannerError(
                "isolated_vertex_release_without_admission"
            )
        route_disposition = "admit"
    elif disposition == "revision_required":
        route_disposition = "revision_required"
    else:
        route_disposition = "reject"
    violations = proofreader.get("violations")
    safe_repairs = proofreader.get("safe_repairs")
    operator_ids = proofreader.get("admitted_operator_ids")
    if not all(
        isinstance(value, list)
        for value in (violations, safe_repairs, operator_ids)
    ):
        raise IsolatedVertexPlannerError(
            "isolated_vertex_proofreader_evidence_invalid"
        )
    receptionist_output = exchange.get("receptionist_output")
    receptionist_response = (
        receptionist_output.get("receptionist_response")
        if isinstance(receptionist_output, dict)
        and isinstance(
            receptionist_output.get("receptionist_response"),
            str,
        )
        else None
    )
    return (
        {
            "disposition": route_disposition,
            "normalized_plan_sha256": proofreader.get(
                "normalized_plan_sha256"
            ),
            "admitted_operator_ids": operator_ids,
            "safe_repairs": safe_repairs,
            "violations": violations,
            "reviewed_context_revision": frame["context_revision"],
        },
        receptionist_response,
    )


def run_isolated_vertex_planner(
    *,
    frame: dict[str, Any],
    observed_at: datetime,
    authority_path: str,
    preflight_path: str,
    evidence_dir: str,
) -> IsolatedVertexPlannerResult:
    """Run one exact v6.8 runtime dialogue with no fallback."""

    _validate_frame(frame, observed_at)
    authority = _resolve_control_path(
        authority_path,
        code="isolated_vertex_authority_required",
    )
    call_ceiling = _authority_call_ceiling(authority)
    preflight = _resolve_control_path(
        preflight_path,
        code="isolated_vertex_preflight_required",
    )
    evidence_root = _resolve_evidence_root(evidence_dir)
    graph_revision, compass_revision = _continuity_binding()
    slug = _request_slug(frame)

    if not _RUNTIME_LOCK.acquire(blocking=False):
        raise IsolatedVertexPlannerError("isolated_vertex_runtime_busy")
    try:
        artifact_dir = evidence_root / slug
        if artifact_dir.exists():
            raise IsolatedVertexPlannerError(
                "isolated_vertex_runtime_audit_ref_reused"
            )
        artifact_dir.mkdir(parents=False, exist_ok=False)
        frame_path = artifact_dir / "runtime-frame.json"
        _write_object(frame_path, frame)
        frame_sha256 = _canonical_hash(frame)
        attempt_ids = (
            f"reception-one-receptionist-first-v68-eval-{slug}-turn-001",
            f"reception-one-receptionist-first-v68-eval-{slug}-turn-002",
        )
        ledger_ids = (
            f"reception-one-receptionist-first-v68-eval-{slug}-ledger-001",
            f"reception-one-receptionist-first-v68-eval-{slug}-ledger-002",
        )
        try:
            try:
                with _runtime_contract() as (parent_live, runtime_contract):
                    dialogue = parent_live.run_dialogue(
                        artifact_dir=artifact_dir,
                        preflight_path=preflight,
                        authority_path=authority,
                        expected_graph_revision=graph_revision,
                        expected_compass_revision=compass_revision,
                        frame_path=frame_path,
                        attempt_ids=attempt_ids,
                        ledger_ids=ledger_ids,
                        maximum_provider_calls=call_ceiling,
                    )
                    if dialogue.get("dialogue_protocol") != (
                        runtime_contract.DIALOGUE_PROTOCOL
                    ):
                        raise IsolatedVertexPlannerError(
                            "isolated_vertex_runtime_contract_mismatch"
                        )
            except IsolatedVertexPlannerError:
                raise
            except Exception as error:
                _write_object(
                    artifact_dir
                    / "runtime-local-failure-diagnostic.json",
                    {
                        "schema_version": (
                            "reception.one.isolated_vertex."
                            "local_failure_diagnostic.v1"
                        ),
                        "reason_code": _bounded_local_failure_code(
                            error
                        ),
                        "provider_ledger_opened": any(
                            artifact_dir.glob(
                                "occupied-turn-*-ledger.json"
                            )
                        ),
                        "provider_external_audit_present": any(
                            artifact_dir.glob(
                                "occupied-turn-*-external-audit.json"
                            )
                        ),
                        "raw_exception_retained": False,
                        "raw_prompt_retained": False,
                        "raw_provider_response_retained": False,
                        "credential_material_retained": False,
                    },
                )
                raise IsolatedVertexPlannerError(
                    "isolated_vertex_attempt_failed"
                ) from error
        finally:
            try:
                if frame_path.exists():
                    frame_path.unlink()
                _write_object(
                    artifact_dir / "runtime-frame-manifest.json",
                    {
                        "schema_version": (
                            "reception.one.isolated_vertex."
                            "runtime_frame_manifest.v1"
                        ),
                        "data_class": "authored_synthetic",
                        "request_sha256": frame_sha256,
                        "context_revision": frame["context_revision"],
                        "raw_frame_retained": False,
                        "raw_prompt_retained": False,
                    },
                )
            except OSError as error:
                raise IsolatedVertexPlannerError(
                    "isolated_vertex_frame_cleanup_failed"
                ) from error
    finally:
        _RUNTIME_LOCK.release()

    if dialogue.get("exact_binding") != EXPECTED_BINDING:
        raise IsolatedVertexPlannerError(
            "isolated_vertex_provider_binding_mismatch"
        )
    provider_calls = dialogue.get("actual_provider_call_count")
    turns = dialogue.get("turns")
    release = dialogue.get("release")
    if (
        not isinstance(provider_calls, int)
        or not 1 <= provider_calls <= call_ceiling
        or dialogue.get("absolute_provider_call_ceiling") != call_ceiling
        or not isinstance(turns, list)
        or len(turns) != provider_calls
        or release is not None
        and not isinstance(release, dict)
    ):
        raise IsolatedVertexPlannerError(
            "isolated_vertex_dialogue_evidence_invalid"
        )
    for index, turn in enumerate(turns, start=1):
        cleanup = turn.get("cleanup")
        if (
            not isinstance(cleanup, dict)
            or not all(
                value is True
                for key, value in cleanup.items()
                if key != "daemon_wide_prune_performed"
            )
        ):
            raise IsolatedVertexPlannerError(
                "isolated_vertex_cleanup_incomplete"
            )
        ledger = _load_object(
            artifact_dir / f"occupied-turn-{index:03d}-ledger.json"
        )
        if (
            ledger.get("status") != "consumed"
            or ledger.get("provider_calls_consumed") != 1
        ):
            raise IsolatedVertexPlannerError(
                "isolated_vertex_ledger_not_consumed"
            )
    final_turn = _load_object(
        artifact_dir
        / f"occupied-turn-{provider_calls:03d}-evidence.json"
    )
    review, receptionist_response = _review_from_turn(
        frame=frame,
        turn=final_turn,
        release=release,
    )
    return IsolatedVertexPlannerResult(
        final_output=release,
        review=review,
        normalized_plan={"goal": _goal_for_release(release)},
        provider_calls=provider_calls,
        runtime_audit_ref=slug,
        terminal_status=str(dialogue.get("terminal_status")),
        receptionist_response=receptionist_response,
    )
