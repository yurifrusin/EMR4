"""Pure T3R7 Sydney Vertex pilot contract, ledger validation, and reducer.

The provider SDK and cloud-control subprocesses live only in the developer
script.  This module is deterministic and imports no network, cloud, FastAPI,
database, or product-runtime surface.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from app.services.ai.evals.bernie_shadow_eval import (
    ModelVersion,
    OperationalMetrics,
    ShadowEvaluationEnvelope,
    score_shadow_response,
)
from app.services.ai.evals.bernie_shadow_live_comparison import (
    build_prompt as build_t3r4_prompt,
    live_response_schema,
    parse_json_object,
)
from app.services.ai.evals.bernie_shadow_silver_v2 import (
    build_silver_v2_shadow_cases,
    build_t3r1_shadow_report,
)
from app.services.ai.evals.bernie_shadow_transport_preflight import (
    normalize_structured_response,
)


ROOT = Path(__file__).resolve().parents[4]
APPROVAL_PATH = ROOT / "docs" / "bernie-t3r7-vertex-sydney-live-approval.json"
LIVE_GATE_PATH = ROOT / "docs" / "bernie-t3-live-replay-gate.json"
DEFAULT_OBSERVATION_PATH = (
    ROOT / "docs" / "bernie-t3r7-vertex-sydney-live-observations.jsonl"
)
DEFAULT_REPORT_PATH = ROOT / "docs" / "bernie-t3r7-vertex-sydney-live-report.json"

PROMPT_VERSION = "bernie-t3r7-vertex-sydney-shadow-v1"
TOOL_SCHEMA_VERSION = "bernie-shadow-normalized-response-v1"
OBSERVATION_SCHEMA_VERSION = "emr4.bernie.t3r7_vertex_sydney_observation.v1"
REPORT_SCHEMA_VERSION = "emr4.bernie.t3r7_vertex_sydney_report.v1"
LANE_ID = "google_vertex_gemini_2_5_flash_sydney"


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def canonical_hash(value: Any) -> str:
    material = value if isinstance(value, str) else _canonical_json(value)
    return "sha256:" + hashlib.sha256(material.encode("utf-8")).hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace(
        "+00:00", "Z"
    )


def load_approval(path: Path = APPROVAL_PATH) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("T3R7 approval must be a JSON object")
    return value


def build_cases(packet: Mapping[str, Any] | None = None):
    approval = packet or load_approval()
    cases = {case.case_id: case for case in build_silver_v2_shadow_cases()}
    selected = approval["source_population"]["selected_case_ids"]
    if any(case_id not in cases for case_id in selected):
        raise ValueError("T3R7 selection contains an unknown Silver v2 case")
    return tuple(cases[case_id] for case_id in selected)


def build_prompt(case) -> str:
    return build_t3r4_prompt(case)


def scheduled_keys(packet: Mapping[str, Any] | None = None) -> tuple[str, ...]:
    approval = packet or load_approval()
    return tuple(
        observation_key(case_id, sample_index)
        for sample_index in (0, 1)
        for case_id in approval["source_population"]["selected_case_ids"]
    )


def observation_key(case_id: str, sample_index: int) -> str:
    return f"{LANE_ID}|{case_id}|{sample_index}"


def _assert_all_false(values: Mapping[str, Any], message: str) -> None:
    if not values or any(value is not False for value in values.values()):
        raise ValueError(message)


def validate_approval(packet: Mapping[str, Any], *, today: date | None = None) -> None:
    if packet.get("schema_version") != "emr4.bernie.t3r7_vertex_sydney_live_approval.v1":
        raise ValueError("unexpected T3R7 approval schema")
    if packet.get("decision") != "approved" or packet.get("authorizes_provider_calls") is not True:
        raise ValueError("T3R7 provider calls are not approved")
    if (today or date.today()) > date.fromisoformat(packet["approval_expires_on"]):
        raise ValueError("T3R7 approval has expired")

    provider = packet["provider"]
    expected_provider = {
        "project": "bernie-emr4-dev",
        "provider": "Google Vertex AI",
        "model_id": "gemini-2.5-flash",
        "location": "australia-southeast1",
        "base_url": "https://australia-southeast1-aiplatform.googleapis.com",
        "automatic_location_fallback": False,
        "authentication": "keyless_impersonated_service_account_adc",
        "required_prediction_permission": "aiplatform.endpoints.predict",
        "exact_model_revision_observable": False,
    }
    if provider != expected_provider:
        raise ValueError("T3R7 provider, model, region, or authentication drift")

    population = packet["source_population"]
    t3r2 = json.loads(
        (ROOT / "docs" / "bernie-t3r2-synthetic-live-comparison-approval.json").read_text(
            encoding="utf-8"
        )
    )
    expected_ids = t3r2["population"]["selected_case_ids"]
    if population["selected_case_ids"] != expected_ids:
        raise ValueError("T3R7 selected-case drift")
    if population["selection_hash"] != canonical_hash(expected_ids):
        raise ValueError("T3R7 selection hash mismatch")
    if population["source_projection_hash"] != build_t3r1_shadow_report()["projection"][
        "projection_hash"
    ]:
        raise ValueError("T3R7 source projection drift")
    if (
        population["case_count"] != 24
        or population["observations_per_case"] != 2
        or population["maximum_calls"] != 48
        or population["schedule_order"] != "all_sample_index_0_then_all_sample_index_1"
    ):
        raise ValueError("T3R7 frozen population arithmetic or schedule drift")

    limits = packet["execution_limits"]
    if limits["maximum_attempts_per_sample"] != 1 or limits["automatic_retries"] is not False:
        raise ValueError("T3R7 retries must remain disabled")
    if limits["provider_error_consumes_sample_and_stops_run"] is not True:
        raise ValueError("T3R7 provider errors must consume and stop")
    if limits["requests_per_minute_ceiling"] > 6 or limits["minimum_start_interval_seconds"] < 10:
        raise ValueError("T3R7 Sydney throttle weakened")
    if limits["maximum_output_tokens_per_call"] * 48 > limits["maximum_output_tokens_total"]:
        raise ValueError("T3R7 output-token arithmetic exceeds the total ceiling")
    prompts = [build_prompt(case).encode("utf-8") for case in build_cases(packet)]
    if max(map(len, prompts)) > limits["maximum_serialized_prompt_chars_per_sample"]:
        raise ValueError("T3R7 prompt exceeds its per-sample ceiling")
    if 2 * sum(map(len, prompts)) > limits["maximum_input_tokens_total"]:
        raise ValueError("T3R7 conservative prompt-token reservation exceeds its ceiling")

    cost = packet["cost_control"]
    ceiling_estimate = (
        limits["maximum_input_tokens_total"]
        * cost["standard_input_price_per_million_tokens"]
        + limits["maximum_output_tokens_total"]
        * cost["standard_output_and_reasoning_price_per_million_tokens"]
    ) / 1_000_000
    if abs(ceiling_estimate - cost["maximum_token_ceiling_estimate"]) > 1e-12:
        raise ValueError("T3R7 price/token ceiling arithmetic mismatch")
    if ceiling_estimate > cost["maximum_estimated_cost"] or cost["application_hard_stop_required"] is not True:
        raise ValueError("T3R7 USD hard ceiling is not effective")
    if cost["trial_credit"]["credit_application_not_required_for_pilot_authority"] is not True:
        raise ValueError("T3R7 authority must not depend on promotional-credit eligibility")

    privacy = packet["privacy_and_retention"]
    prohibited = (
        "patient_or_practice_data_allowed",
        "historical_diary_material_allowed",
        "protected_holdout_material_allowed",
        "external_corpus_material_allowed",
        "raw_prompt_persistence",
        "raw_response_persistence",
        "grounding_tools_and_explicit_cache",
    )
    if any(privacy[field] is not False for field in prohibited):
        raise ValueError("T3R7 privacy or tool boundary drift")
    if not all(
        privacy[field] is True
        for field in (
            "synthetic_silver_v2_only",
            "normalized_response_and_hash_only",
            "request_response_logging_required_disabled",
            "google_abuse_monitoring_prompt_retention_accepted_for_synthetic_only_use",
        )
    ):
        raise ValueError("T3R7 privacy/retention acceptance is incomplete")
    controls = packet["required_pre_call_controls"]
    boolean_controls = {
        key: value
        for key, value in controls.items()
        if key != "automatic_sdk_retry_attempts"
    }
    if any(value is not True for value in boolean_controls.values()) or controls.get(
        "automatic_sdk_retry_attempts"
    ) != 1:
        raise ValueError("T3R7 pre-call control requirements drifted")
    _assert_all_false(packet["authority"], "T3R7 opens prohibited product authority")

    live_gate = json.loads(LIVE_GATE_PATH.read_text(encoding="utf-8"))
    if live_gate.get("decision") != "blocked":
        raise ValueError("product live-provider gate drifted open")


def estimate_cost_usd(
    packet: Mapping[str, Any], *, input_tokens: int, output_tokens: int
) -> float:
    prices = packet["cost_control"]
    return round(
        (
            input_tokens * prices["standard_input_price_per_million_tokens"]
            + output_tokens
            * prices["standard_output_and_reasoning_price_per_million_tokens"]
        )
        / 1_000_000,
        9,
    )


def _usage_totals(records: Sequence[Mapping[str, Any]]) -> tuple[int, int]:
    return (
        sum(int((record.get("usage") or {}).get("input_tokens") or 0) for record in records),
        sum(int((record.get("usage") or {}).get("output_tokens") or 0) for record in records),
    )


@dataclass(frozen=True)
class DispatchState:
    packet: Mapping[str, Any]
    records: Sequence[Mapping[str, Any]]
    elapsed_minutes: float

    def assert_allowed(self, *, case, sample_index: int, prompt: str) -> None:
        validate_approval(self.packet)
        if case.case_id not in self.packet["source_population"]["selected_case_ids"]:
            raise ValueError("case is outside the T3R7 selection")
        if sample_index not in (0, 1):
            raise ValueError("T3R7 sample index exceeds approval")
        if observation_key(case.case_id, sample_index) in consumed_keys(self.records):
            raise ValueError("T3R7 observation already consumed; retries are prohibited")
        if any(record.get("status") != "success" for record in self.records):
            raise ValueError("T3R7 stopped after a consumed provider failure")

        limits = self.packet["execution_limits"]
        if len(self.records) >= self.packet["source_population"]["maximum_calls"]:
            raise ValueError("T3R7 call ceiling reached")
        prompt_reservation = len(prompt.encode("utf-8"))
        if prompt_reservation > limits["maximum_serialized_prompt_chars_per_sample"]:
            raise ValueError("T3R7 prompt character ceiling exceeded")
        if self.elapsed_minutes >= limits["maximum_wall_clock_minutes"]:
            raise ValueError("T3R7 wall-clock ceiling reached")

        input_tokens, output_tokens = _usage_totals(self.records)
        reserved_input = input_tokens + prompt_reservation
        reserved_output = output_tokens + limits["maximum_output_tokens_per_call"]
        if reserved_input > limits["maximum_input_tokens_total"]:
            raise ValueError("T3R7 input-token ceiling would be exceeded")
        if reserved_output > limits["maximum_output_tokens_total"]:
            raise ValueError("T3R7 output-token ceiling would be exceeded")
        if estimate_cost_usd(
            self.packet, input_tokens=reserved_input, output_tokens=reserved_output
        ) > self.packet["cost_control"]["maximum_estimated_cost"]:
            raise ValueError("T3R7 USD application hard ceiling would be exceeded")


def consumed_keys(records: Iterable[Mapping[str, Any]]) -> frozenset[str]:
    return frozenset(str(record["observation_key"]) for record in records)


def load_observations(path: Path = DEFAULT_OBSERVATION_PATH) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    records: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"T3R7 observation line {line_number} is not an object")
        records.append(value)
    validate_observations(records)
    return records


def validate_observations(records: Sequence[Mapping[str, Any]]) -> None:
    keys: set[str] = set()
    allowed_keys = set(scheduled_keys())
    forbidden = {
        "raw_prompt",
        "raw_response",
        "prompt_text",
        "response_text",
        "stdout",
        "stderr",
        "instruction",
    }
    for record in records:
        if record.get("schema_version") != OBSERVATION_SCHEMA_VERSION:
            raise ValueError("T3R7 observation schema mismatch")
        if forbidden.intersection(record):
            raise ValueError("raw T3R7 prompt/response material must not be persisted")
        key = str(record.get("observation_key", ""))
        if key not in allowed_keys or key in keys:
            raise ValueError("T3R7 observation key is unscheduled or duplicated")
        keys.add(key)
        if record.get("status") not in {
            "success",
            "provider_error",
            "parse_error",
            "response_limit_exceeded",
        }:
            raise ValueError("T3R7 observation status is not allowlisted")
        if record.get("endpoint_location") != "australia-southeast1":
            raise ValueError("T3R7 observation location drift")
        if record.get("status") == "success":
            payload = record.get("normalized_response")
            if not isinstance(payload, dict):
                raise ValueError("successful T3R7 observation lacks normalized response")
            normalized = normalize_structured_response(payload)
            if record.get("response_hash") != normalized.response_hash:
                raise ValueError("T3R7 normalized response hash mismatch")
            usage = record.get("usage") or {}
            estimated = estimate_cost_usd(
                load_approval(),
                input_tokens=int(usage.get("input_tokens") or 0),
                output_tokens=int(usage.get("output_tokens") or 0),
            )
            if abs(float(record.get("estimated_cost_usd") or 0) - estimated) > 1e-9:
                raise ValueError("T3R7 observation cost mismatch")
        elif record.get("normalized_response") is not None:
            raise ValueError("failed T3R7 observation persisted response material")


def _model_version(packet: Mapping[str, Any], revision: str) -> ModelVersion:
    return ModelVersion(
        provider="Google Vertex AI",
        model=packet["provider"]["model_id"],
        model_revision=revision,
        prompt_version=PROMPT_VERSION,
        tool_schema_version=TOOL_SCHEMA_VERSION,
        temperature=0.0,
    )


def success_record(
    *,
    packet: Mapping[str, Any],
    case,
    sample_index: int,
    prompt_hash: str,
    normalized_payload: Mapping[str, Any],
    started_at: str,
    completed_at: str,
    latency_ms: int,
    input_tokens: int,
    output_tokens: int,
    model_version_observed: str | None,
) -> dict[str, Any]:
    normalized = normalize_structured_response(normalized_payload)
    revision = model_version_observed or "requested-alias-exact-revision-unobservable"
    estimated_cost = estimate_cost_usd(
        packet, input_tokens=input_tokens, output_tokens=output_tokens
    )
    envelope = ShadowEvaluationEnvelope(
        case=case,
        model=_model_version(packet, revision),
        sample_index=sample_index,
    )
    observation = score_shadow_response(
        envelope,
        normalized,
        OperationalMetrics(
            latency_ms=latency_ms,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            estimated_cost_usd=estimated_cost,
        ),
    )
    score = observation.score
    return {
        "schema_version": OBSERVATION_SCHEMA_VERSION,
        "observation_key": observation_key(case.case_id, sample_index),
        "lane_id": LANE_ID,
        "case_id": case.case_id,
        "sample_index": sample_index,
        "status": "success",
        "prompt_version": PROMPT_VERSION,
        "prompt_hash": prompt_hash,
        "model_requested": packet["provider"]["model_id"],
        "model_version_observed": model_version_observed,
        "endpoint_location": packet["provider"]["location"],
        "started_at": started_at,
        "completed_at": completed_at,
        "latency_ms": latency_ms,
        "tool_observation": "mechanically_disabled",
        "normalized_response": {
            "intent": normalized.intent,
            "entities": [list(item) for item in normalized.entities],
            "date_time": [list(item) for item in normalized.date_time],
            "requires_clarification": normalized.requires_clarification,
            "tool_name": normalized.tool_name,
            "writes_authorized": normalized.writes_authorized,
            "claims_action_completed": normalized.claims_action_completed,
            "action_withdrawn": normalized.action_withdrawn,
        },
        "response_hash": normalized.response_hash,
        "score": {
            "intent_correct": score.intent_correct,
            "entities_correct": score.entities_correct,
            "date_time_correct": score.date_time_correct,
            "clarification_correct": score.clarification_correct,
            "tool_selection_correct": score.tool_selection_correct,
            "withdrawal_correct": score.withdrawal_correct,
            "correctness_passes": score.correctness_passes,
            "correctness_total": score.correctness_total,
            "safety_violations": list(score.safety_violations),
        },
        "usage": {"input_tokens": input_tokens, "output_tokens": output_tokens},
        "estimated_cost_usd": estimated_cost,
        "cost_is_price_schedule_estimate": True,
        "raw_prompt_persisted": False,
        "raw_response_persisted": False,
    }


def failure_record(
    *,
    packet: Mapping[str, Any],
    case,
    sample_index: int,
    prompt_hash: str,
    status: str,
    safe_error_code: str,
    started_at: str,
    completed_at: str,
    latency_ms: int,
) -> dict[str, Any]:
    if status not in {"provider_error", "parse_error", "response_limit_exceeded"}:
        raise ValueError("unsupported T3R7 failure status")
    return {
        "schema_version": OBSERVATION_SCHEMA_VERSION,
        "observation_key": observation_key(case.case_id, sample_index),
        "lane_id": LANE_ID,
        "case_id": case.case_id,
        "sample_index": sample_index,
        "status": status,
        "safe_error_code": safe_error_code,
        "prompt_version": PROMPT_VERSION,
        "prompt_hash": prompt_hash,
        "model_requested": packet["provider"]["model_id"],
        "model_version_observed": None,
        "endpoint_location": packet["provider"]["location"],
        "started_at": started_at,
        "completed_at": completed_at,
        "latency_ms": latency_ms,
        "tool_observation": "mechanically_disabled",
        "normalized_response": None,
        "response_hash": None,
        "score": None,
        "usage": {"input_tokens": None, "output_tokens": None},
        "estimated_cost_usd": None,
        "cost_is_price_schedule_estimate": True,
        "raw_prompt_persisted": False,
        "raw_response_persisted": False,
    }


def append_observation(
    record: Mapping[str, Any], path: Path = DEFAULT_OBSERVATION_PATH
) -> None:
    current = load_observations(path)
    validate_observations([*current, record])
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(_canonical_json(record) + "\n")


def build_report(
    packet: Mapping[str, Any] | None = None,
    records: Sequence[Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    approval = dict(packet or load_approval())
    validate_approval(approval)
    observations = list(records if records is not None else load_observations())
    validate_observations(observations)
    successes = [record for record in observations if record["status"] == "success"]
    failures = [record for record in observations if record["status"] != "success"]
    scores = [record["score"] for record in successes]
    input_tokens, output_tokens = _usage_totals(observations)
    fingerprints: dict[str, set[str]] = defaultdict(set)
    for record in successes:
        fingerprints[record["case_id"]].add(record["response_hash"])
    status_counts = Counter(record["status"] for record in observations)
    correctness_passes = sum(score["correctness_passes"] for score in scores)
    correctness_total = sum(score["correctness_total"] for score in scores)
    dimension_failure_counts = {
        field.removesuffix("_correct"): sum(score[field] is False for score in scores)
        for field in (
            "intent_correct",
            "entities_correct",
            "date_time_correct",
            "clarification_correct",
            "tool_selection_correct",
            "withdrawal_correct",
        )
    }
    complete = len(observations) == 48 and not failures
    stopped = bool(failures)
    without_hash = {
        "schema_version": REPORT_SCHEMA_VERSION,
        "decision": (
            "pilot_complete" if complete else "pilot_stopped_on_consumed_failure" if stopped else "pilot_incomplete"
        ),
        "approval_binding": canonical_hash(approval),
        "source_projection_hash": approval["source_population"]["source_projection_hash"],
        "selection_hash": approval["source_population"]["selection_hash"],
        "provider": {
            "provider": approval["provider"]["provider"],
            "model_requested": approval["provider"]["model_id"],
            "location": approval["provider"]["location"],
            "observed_model_versions": sorted(
                {
                    record["model_version_observed"]
                    for record in successes
                    if record.get("model_version_observed")
                }
            ),
        },
        "execution": {
            "maximum_calls": 48,
            "consumed_calls": len(observations),
            "unused_calls": 48 - len(observations),
            "all_authorized_work_complete": complete or stopped,
            "status_counts": dict(sorted(status_counts.items())),
            "automatic_retries": False,
            "minimum_start_interval_seconds": approval["execution_limits"][
                "minimum_start_interval_seconds"
            ],
            "requests_per_minute_ceiling": approval["execution_limits"][
                "requests_per_minute_ceiling"
            ],
            "raw_prompt_persisted": False,
            "raw_response_persisted": False,
        },
        "quality": {
            "successful_samples": len(successes),
            "safe_successful_samples": sum(not score["safety_violations"] for score in scores),
            "perfect_successful_samples": sum(
                score["correctness_passes"] == score["correctness_total"] for score in scores
            ),
            "correctness_passes": correctness_passes,
            "correctness_total": correctness_total,
            "correctness_fraction": correctness_passes / correctness_total if correctness_total else None,
            "dimension_failure_counts": dimension_failure_counts,
            "variant_case_count": sum(len(values) > 1 for values in fingerprints.values()),
        },
        "usage_and_cost": {
            "input_tokens": input_tokens,
            "output_tokens_including_reasoning_when_reported": output_tokens,
            "estimated_cost_usd": round(
                sum(float(record.get("estimated_cost_usd") or 0) for record in observations), 9
            ),
            "application_hard_ceiling_usd": approval["cost_control"][
                "maximum_estimated_cost"
            ],
            "trial_credit_vertex_eligibility": approval["cost_control"]["trial_credit"][
                "vertex_gemini_sku_eligibility"
            ],
        },
        "api_spine_boundary": {
            "classification": "developer_only_synthetic_access_ai_evaluation",
            "product_runtime_wiring": False,
            "graphql_or_rest_route_change": False,
            "provider_executed_tools_authorized": False,
            "database_or_audit_write": False,
            "appointment_or_confirmation_authority": False,
            "deployment_or_release": False,
            "pii_or_production_authority": False,
        },
    }
    return {**without_hash, "report_hash": canonical_hash(without_hash)}


def write_report(path: Path = DEFAULT_REPORT_PATH) -> dict[str, Any]:
    report = build_report()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return report


__all__ = [
    "APPROVAL_PATH",
    "DEFAULT_OBSERVATION_PATH",
    "DEFAULT_REPORT_PATH",
    "DispatchState",
    "LANE_ID",
    "append_observation",
    "build_cases",
    "build_prompt",
    "build_report",
    "canonical_hash",
    "estimate_cost_usd",
    "failure_record",
    "live_response_schema",
    "load_approval",
    "load_observations",
    "observation_key",
    "parse_json_object",
    "scheduled_keys",
    "success_record",
    "utc_now",
    "validate_approval",
    "validate_observations",
    "write_report",
]
