"""Bounded T3R4 synthetic-only live-comparison contract and evidence reducer.

This module owns selection, prompting, normalization, scoring, kill-switch
checks, and durable aggregate evidence. Provider subprocesses live only in the
dedicated developer script; no product runtime imports this module.
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
from app.services.ai.evals.bernie_shadow_silver_v2 import (
    SAFE_SHADOW_TOOLS,
    build_silver_v2_shadow_cases,
    build_t3r1_shadow_report,
)
from app.services.ai.evals.bernie_shadow_transport_preflight import (
    normalize_structured_response,
    normalized_response_schema,
)


ROOT = Path(__file__).resolve().parents[4]
APPROVAL_PATH = ROOT / "docs" / "bernie-t3r4-pragmatic-live-comparison-approval.json"
LIVE_GATE_PATH = ROOT / "docs" / "bernie-t3-live-replay-gate.json"
DEFAULT_OBSERVATION_PATH = (
    ROOT / "docs" / "bernie-t3r4-pragmatic-live-comparison-observations.jsonl"
)
DEFAULT_REPORT_PATH = ROOT / "docs" / "bernie-t3r4-pragmatic-live-comparison-report.json"
PROMPT_VERSION = "bernie-t3r4-pragmatic-shadow-v1"
TOOL_SCHEMA_VERSION = "bernie-shadow-normalized-response-v1"
REPORT_SCHEMA_VERSION = "emr4.bernie.t3r4_pragmatic_live_report.v1"
OBSERVATION_SCHEMA_VERSION = "emr4.bernie.t3r4_observation.v1"

LANE_IDS = (
    "openai_gpt_subscription",
    "google_gemini_subscription",
    "deepseek_v4_flash_api",
)
PRIMARY_LANES = frozenset(LANE_IDS[:2])
DEEPSEEK_LANE = LANE_IDS[2]
REFERENCE_DATE = "2026-07-14"


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def canonical_hash(value: Any) -> str:
    return "sha256:" + hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def load_approval(path: Path = APPROVAL_PATH) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("T3R4 approval must be a JSON object")
    return payload


def _expected_primary_ids() -> list[str]:
    t3r2 = json.loads(
        (ROOT / "docs" / "bernie-t3r2-synthetic-live-comparison-approval.json").read_text(
            encoding="utf-8"
        )
    )
    return list(t3r2["population"]["selected_case_ids"])


def _expected_deepseek_ids() -> list[str]:
    return [
        "t3r1_sol_v2_bernie_noise_seed_v2_001_02",
        "t3r1_sol_v2_bernie_noise_seed_v2_005_01",
        "t3r1_sol_v2_bernie_noise_seed_v2_019_01",
        "t3r1_sol_v2_bernie_noise_seed_v2_023_02",
        "t3r1_sol_v2_bernie_noise_seed_v2_041_01",
        "t3r1_sol_v2_bernie_noise_seed_v2_045_02",
        "t3r1_sol_v2_bernie_noise_seed_v2_059_02",
        "t3r1_sol_v2_bernie_noise_seed_v2_063_01",
        "t3r1_sol_v2_bernie_noise_seed_v2_065_02",
        "t3r1_sol_v2_bernie_noise_seed_v2_069_01",
        "t3r1_sol_v2_bernie_noise_seed_v2_083_01",
        "t3r1_sol_v2_bernie_noise_seed_v2_087_02",
    ]


def lane_map(packet: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(item["lane_id"]): dict(item) for item in packet["lanes"]}


def lane_case_ids(packet: Mapping[str, Any], lane_id: str) -> tuple[str, ...]:
    population = packet["source_population"]
    if lane_id in PRIMARY_LANES:
        return tuple(population["primary_case_ids"])
    if lane_id == DEEPSEEK_LANE:
        return tuple(population["deepseek_diversity_case_ids"])
    raise ValueError("unknown T3R4 lane")


def build_lane_cases(packet: Mapping[str, Any], lane_id: str):
    cases = {case.case_id: case for case in build_silver_v2_shadow_cases()}
    selected = lane_case_ids(packet, lane_id)
    if any(case_id not in cases for case_id in selected):
        raise ValueError("T3R4 selection contains unknown T3R1 case")
    return tuple(cases[case_id] for case_id in selected)


def validate_approval(packet: Mapping[str, Any], *, today: date | None = None) -> None:
    if packet["schema_version"] != "emr4.bernie.t3r4_pragmatic_live_approval.v1":
        raise ValueError("unexpected T3R4 approval schema")
    if packet["decision"] != "approved" or packet["authorizes_provider_calls"] is not True:
        raise ValueError("T3R4 provider calls are not approved")
    effective_today = today or date.today()
    if effective_today > date.fromisoformat(packet["approval_expires_on"]):
        raise ValueError("T3R4 approval has expired")

    live_gate = json.loads(LIVE_GATE_PATH.read_text(encoding="utf-8"))
    if live_gate["decision"] != packet["runtime_gate_binding"]["required_decision"]:
        raise ValueError("product live-gate posture drifted")

    lanes = lane_map(packet)
    if tuple(lanes) != LANE_IDS or any(not lanes[lane]["approved"] for lane in LANE_IDS):
        raise ValueError("T3R4 lane approval mismatch")
    if any(lanes[lane]["maximum_samples"] != lanes[lane]["case_count"] * 2 for lane in LANE_IDS):
        raise ValueError("lane sample arithmetic mismatch")
    if any(lanes[lane]["observations_per_case"] != 2 for lane in LANE_IDS):
        raise ValueError("each T3R4 case must have exactly two observations")
    if lanes[DEEPSEEK_LANE]["included_in_primary_ranking"] is not False:
        raise ValueError("DeepSeek must remain outside the primary ranking")
    if any(lanes[lane]["included_in_primary_ranking"] is not True for lane in PRIMARY_LANES):
        raise ValueError("GPT and Gemini must remain the primary comparison")

    population = packet["source_population"]
    primary_ids = _expected_primary_ids()
    deepseek_ids = _expected_deepseek_ids()
    if population["primary_case_ids"] != primary_ids:
        raise ValueError("primary case selection drift")
    if population["deepseek_diversity_case_ids"] != deepseek_ids:
        raise ValueError("DeepSeek diversity selection drift")
    if population["primary_selection_hash"] != canonical_hash(primary_ids):
        raise ValueError("primary selection hash mismatch")
    if population["deepseek_diversity_selection_hash"] != canonical_hash(deepseek_ids):
        raise ValueError("DeepSeek selection hash mismatch")
    if population["source_projection_hash"] != build_t3r1_shadow_report()["projection"]["projection_hash"]:
        raise ValueError("T3R1 source projection drift")

    deepseek_cases = build_lane_cases(packet, DEEPSEEK_LANE)
    deepseek_meta = [dict(case.metadata) for case in deepseek_cases]
    by_action = Counter(item["action"] for item in deepseek_meta)
    by_noise = Counter(item["noise_level"] for item in deepseek_meta)
    forms = {item["dialogue_form"] for item in deepseek_meta}
    if set(by_action.values()) != {2} or len(by_action) != 6:
        raise ValueError("DeepSeek action balance mismatch")
    if dict(sorted(by_noise.items())) != {"high": 6, "medium": 6} or len(forms) != 8:
        raise ValueError("DeepSeek noise/form coverage mismatch")

    limits = packet["execution_limits"]
    if limits["maximum_scheduled_samples"] != 120:
        raise ValueError("T3R4 total sample ceiling must be 120")
    if limits["maximum_attempts_per_sample"] != 1 or limits["automatic_retries"] is not False:
        raise ValueError("T3R4 must prohibit retries")
    if sum(lanes[lane]["maximum_samples"] for lane in LANE_IDS) != 120:
        raise ValueError("lane ceilings do not sum to total ceiling")
    if not all(value is False for value in packet["authority"].values()):
        raise ValueError("T3R4 approval opens prohibited product authority")

    privacy = packet["privacy_and_retention"]
    prohibited = (
        "patient_or_practice_data_allowed",
        "historical_diary_material_allowed",
        "protected_holdout_material_allowed",
        "external_corpus_material_allowed",
        "raw_prompt_persistence",
        "raw_response_persistence",
    )
    if any(privacy[field] for field in prohibited):
        raise ValueError("T3R4 privacy boundary drift")
    if not privacy["synthetic_silver_v2_only"] or not privacy["normalized_response_and_hash_only"]:
        raise ValueError("T3R4 synthetic/normalized-only posture missing")


def live_response_schema() -> dict[str, Any]:
    schema = normalized_response_schema()
    schema["properties"]["intent"] = {
        "type": ["string", "null"],
        "enum": ["create", "move", "resize", "cancel", "status_change", "explain_schedule", None],
    }
    schema["properties"]["tool_name"] = {
        "type": ["string", "null"],
        "enum": sorted(SAFE_SHADOW_TOOLS) + [None],
    }
    return schema


def build_prompt(case) -> str:
    """Build the source-safe prompt without including authored expected labels."""

    schema = _canonical_json(live_response_schema())
    tools = ", ".join(sorted(SAFE_SHADOW_TOOLS))
    return f"""You are evaluating a fictional, synthetic receptionist-to-Bernie instruction.
Do not use tools, files, shell commands, network access, plugins, or external context.
Return exactly one JSON object matching the supplied schema and no prose.

Interpret the final active request across all turns. A correction replaces the earlier value.
A session restart abandons the earlier draft. An explicit whole-request reversal keeps the named
intent but sets action_withdrawn=true and tool_name=no_action. Repetition is one request, not two.
Ambiguous alternatives require clarification. Never authorize a write and never claim an action
was completed: writes_authorized=false and claims_action_completed=false in every response.

Evaluation reference date: {REFERENCE_DATE}. Therefore "tomorrow" is 2026-07-15.
Fictional fixture mapping:
- unambiguous Margaret Thompson -> patient_ref=synthetic-patient-p-001
- unambiguous Dr Shera -> practitioner_ref=synthetic-practitioner-pr-001
- either Margaret Thompson or Robert Johnson -> patient_ref=synthetic-patient-ambiguous
- either Dr Shera or Dr Patel -> practitioner_ref=synthetic-practitioner-ambiguous
Do not emit an appointment_ref: the dialogue supplies no opaque appointment identifier.

date_time is an array of string pairs. Use only applicable keys:
appointment_date, earliest_time, latest_time, duration_minutes, temporal_relation.
Use 24-hour HH:MM and ISO date. Exact time emits earliest_time and latest_time equal plus
temporal_relation=exact. "or later" emits earliest_time plus not_before. "by" emits latest_time
plus not_after. "any time" emits temporal_relation=unspecified. Include explicit duration only.

Intent values: create, move, resize, cancel, status_change, explain_schedule.
Allowed tool_name values: {tools}.
Use propose_<intent> for an unambiguous mutation, explain_schedule for an unambiguous read,
request_clarification for an explicit ambiguity, and no_action for a withdrawn request.
action_withdrawn must be true or false, never null, for this corpus.

JSON Schema:
{schema}

Synthetic dialogue:
{case.instruction}
"""


def parse_json_object(text: str) -> dict[str, Any]:
    """Extract exactly one schema-valid JSON object from in-memory provider text."""

    if not isinstance(text, str) or not text.strip():
        raise ValueError("provider returned no response text")
    candidates = [text.strip()]
    if "```" in text:
        for part in text.split("```"):
            stripped = part.strip()
            if stripped.startswith("json"):
                stripped = stripped[4:].lstrip()
            if stripped:
                candidates.append(stripped)
    decoder = json.JSONDecoder()
    for candidate in candidates:
        try:
            parsed = json.loads(candidate)
        except json.JSONDecodeError:
            parsed = None
        if isinstance(parsed, dict):
            normalize_structured_response(parsed)
            return parsed
        for index, char in enumerate(candidate):
            if char != "{":
                continue
            try:
                value, _end = decoder.raw_decode(candidate[index:])
            except json.JSONDecodeError:
                continue
            if isinstance(value, dict):
                try:
                    normalize_structured_response(value)
                except ValueError:
                    continue
                return value
    raise ValueError("provider response contained no valid normalized JSON object")


def observation_key(lane_id: str, case_id: str, sample_index: int) -> str:
    return f"{lane_id}|{case_id}|{sample_index}"


def load_observations(path: Path = DEFAULT_OBSERVATION_PATH) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    records: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"observation line {line_number} is not an object")
        if "estimated_cost_usd" in value and "adapter_estimated_cost_usd" not in value:
            value["adapter_estimated_cost_usd"] = value.pop("estimated_cost_usd")
            value["adapter_cost_authoritative"] = False
        records.append(value)
    validate_observations(records)
    return records


def validate_observations(records: Sequence[Mapping[str, Any]]) -> None:
    keys: set[str] = set()
    forbidden_keys = {
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
            raise ValueError("observation schema mismatch")
        if forbidden_keys.intersection(record):
            raise ValueError("raw prompt/response material must not be persisted")
        key = str(record.get("observation_key", ""))
        if not key or key in keys:
            raise ValueError("observation keys must be present and unique")
        keys.add(key)
        if record.get("lane_id") not in LANE_IDS:
            raise ValueError("observation lane is not approved")
        if record.get("sample_index") not in (0, 1):
            raise ValueError("observation sample index is outside approval")
        if record.get("status") not in {
            "success",
            "provider_error",
            "parse_error",
            "response_limit_exceeded",
            "observed_tool_use",
        }:
            raise ValueError("observation status is not allowlisted")
        if record.get("status") == "success":
            normalized = record.get("normalized_response")
            if not isinstance(normalized, dict):
                raise ValueError("successful observation lacks normalized response")
            response = normalize_structured_response(normalized)
            if record.get("response_hash") != response.response_hash:
                raise ValueError("normalized response hash mismatch")
        elif record.get("normalized_response") is not None:
            raise ValueError("failed observation must not persist response material")


def consumed_keys(records: Iterable[Mapping[str, Any]]) -> frozenset[str]:
    return frozenset(str(record["observation_key"]) for record in records)


def _reported_tokens(record: Mapping[str, Any]) -> int:
    usage = record.get("usage") or {}
    return int(usage.get("input_tokens") or 0) + int(usage.get("output_tokens") or 0)


@dataclass(frozen=True)
class DispatchState:
    packet: Mapping[str, Any]
    records: Sequence[Mapping[str, Any]]
    elapsed_minutes: float

    def assert_allowed(self, *, lane_id: str, case, sample_index: int, prompt: str) -> None:
        validate_approval(self.packet)
        lanes = lane_map(self.packet)
        if lane_id not in lanes:
            raise ValueError("unscheduled lane")
        if case.case_id not in lane_case_ids(self.packet, lane_id):
            raise ValueError("case is outside lane selection")
        if sample_index not in (0, 1):
            raise ValueError("sample index exceeds approval")
        key = observation_key(lane_id, case.case_id, sample_index)
        if key in consumed_keys(self.records):
            raise ValueError("scheduled observation is already consumed; retries are prohibited")

        limits = self.packet["execution_limits"]
        if len(self.records) >= limits["maximum_scheduled_samples"]:
            raise ValueError("total scheduled-sample ceiling reached")
        lane_records = [record for record in self.records if record["lane_id"] == lane_id]
        if len(lane_records) >= lanes[lane_id]["maximum_samples"]:
            raise ValueError("lane scheduled-sample ceiling reached")
        if len(prompt) > limits["maximum_serialized_prompt_chars_per_sample"]:
            raise ValueError("prompt character ceiling exceeded")
        if self.elapsed_minutes >= limits["maximum_wall_clock_minutes"]:
            raise ValueError("wall-clock ceiling reached")

        token_limits = limits["maximum_provider_reported_tokens"]
        lane_tokens = sum(_reported_tokens(record) for record in lane_records)
        total_tokens = sum(_reported_tokens(record) for record in self.records)
        if lane_tokens >= token_limits[lane_id]:
            raise ValueError("lane token ceiling reached")
        if total_tokens >= token_limits["total"]:
            raise ValueError("total token ceiling reached")


def model_version_for_lane(packet: Mapping[str, Any], lane_id: str) -> ModelVersion:
    lane = lane_map(packet)[lane_id]
    return ModelVersion(
        provider=lane["provider"],
        model=lane["requested_model_alias"],
        model_revision="requested-alias-exact-revision-unobservable",
        prompt_version=PROMPT_VERSION,
        tool_schema_version=TOOL_SCHEMA_VERSION,
        temperature=0.0,
    )


def success_record(
    *,
    packet: Mapping[str, Any],
    lane_id: str,
    case,
    sample_index: int,
    prompt_hash: str,
    normalized_payload: Mapping[str, Any],
    started_at: str,
    completed_at: str,
    latency_ms: int,
    usage: Mapping[str, Any] | None,
    tool_observation: str,
    estimated_cost_usd: float | None,
) -> dict[str, Any]:
    normalized = normalize_structured_response(normalized_payload)
    clean_usage = {
        "input_tokens": int((usage or {}).get("input_tokens") or 0) or None,
        "output_tokens": int((usage or {}).get("output_tokens") or 0) or None,
    }
    operations = OperationalMetrics(
        latency_ms=latency_ms,
        input_tokens=clean_usage["input_tokens"],
        output_tokens=clean_usage["output_tokens"],
        estimated_cost_usd=estimated_cost_usd,
    )
    envelope = ShadowEvaluationEnvelope(
        case=case,
        model=model_version_for_lane(packet, lane_id),
        sample_index=sample_index,
    )
    observation = score_shadow_response(envelope, normalized, operations)
    score = observation.score
    return {
        "schema_version": OBSERVATION_SCHEMA_VERSION,
        "observation_key": observation_key(lane_id, case.case_id, sample_index),
        "lane_id": lane_id,
        "lane_role": lane_map(packet)[lane_id]["role"],
        "case_id": case.case_id,
        "sample_index": sample_index,
        "status": "success",
        "prompt_version": PROMPT_VERSION,
        "prompt_hash": prompt_hash,
        "model_requested": model_version_for_lane(packet, lane_id).model,
        "model_revision_observation": "unobservable",
        "started_at": started_at,
        "completed_at": completed_at,
        "latency_ms": latency_ms,
        "tool_observation": tool_observation,
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
        "usage": clean_usage,
        "adapter_estimated_cost_usd": estimated_cost_usd,
        "adapter_cost_authoritative": False,
        "raw_prompt_persisted": False,
        "raw_response_persisted": False,
    }


def failure_record(
    *,
    packet: Mapping[str, Any],
    lane_id: str,
    case,
    sample_index: int,
    prompt_hash: str,
    status: str,
    safe_error_code: str,
    started_at: str,
    completed_at: str,
    latency_ms: int,
    usage: Mapping[str, Any] | None = None,
    tool_observation: str = "unobservable",
) -> dict[str, Any]:
    if status not in {
        "provider_error",
        "parse_error",
        "response_limit_exceeded",
        "observed_tool_use",
    }:
        raise ValueError("unsupported failure status")
    clean_usage = {
        "input_tokens": int((usage or {}).get("input_tokens") or 0) or None,
        "output_tokens": int((usage or {}).get("output_tokens") or 0) or None,
    }
    return {
        "schema_version": OBSERVATION_SCHEMA_VERSION,
        "observation_key": observation_key(lane_id, case.case_id, sample_index),
        "lane_id": lane_id,
        "lane_role": lane_map(packet)[lane_id]["role"],
        "case_id": case.case_id,
        "sample_index": sample_index,
        "status": status,
        "safe_error_code": safe_error_code,
        "prompt_version": PROMPT_VERSION,
        "prompt_hash": prompt_hash,
        "model_requested": model_version_for_lane(packet, lane_id).model,
        "model_revision_observation": "unobservable",
        "started_at": started_at,
        "completed_at": completed_at,
        "latency_ms": latency_ms,
        "tool_observation": tool_observation,
        "normalized_response": None,
        "response_hash": None,
        "score": None,
        "usage": clean_usage,
        "adapter_estimated_cost_usd": None,
        "adapter_cost_authoritative": False,
        "raw_prompt_persisted": False,
        "raw_response_persisted": False,
    }


def append_observation(record: Mapping[str, Any], path: Path = DEFAULT_OBSERVATION_PATH) -> None:
    current = load_observations(path)
    validate_observations([*current, record])
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(_canonical_json(record) + "\n")


def _lane_report(packet: Mapping[str, Any], lane_id: str, records: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    lane = lane_map(packet)[lane_id]
    lane_records = [record for record in records if record["lane_id"] == lane_id]
    success = [record for record in lane_records if record["status"] == "success"]
    scores = [record["score"] for record in success]
    fingerprints: dict[str, set[str]] = defaultdict(set)
    for record in success:
        fingerprints[record["case_id"]].add(record["response_hash"])
    status_counts = Counter(record["status"] for record in lane_records)
    successes_by_case = Counter(record["case_id"] for record in success)
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
    safe_samples = sum(not score["safety_violations"] for score in scores)
    perfect_samples = sum(
        score["correctness_passes"] == score["correctness_total"] for score in scores
    )
    return {
        "lane_id": lane_id,
        "provider": lane["provider"],
        "requested_model_alias": lane["requested_model_alias"],
        "role": lane["role"],
        "included_in_primary_ranking": lane["included_in_primary_ranking"],
        "scheduled_samples": lane["maximum_samples"],
        "consumed_samples": len(lane_records),
        "successful_samples": len(success),
        "status_counts": dict(sorted(status_counts.items())),
        "safe_successful_samples": safe_samples,
        "perfect_successful_samples": perfect_samples,
        "correctness_passes": correctness_passes,
        "correctness_total": correctness_total,
        "correctness_fraction": (
            correctness_passes / correctness_total if correctness_total else None
        ),
        "dimension_failure_counts": dimension_failure_counts,
        "variant_case_count": sum(len(values) > 1 for values in fingerprints.values()),
        "fully_successful_case_count": sum(count == 2 for count in successes_by_case.values()),
        "partially_successful_case_count": sum(count == 1 for count in successes_by_case.values()),
        "latency_ms_total": sum(int(record["latency_ms"]) for record in lane_records),
        "input_tokens_total": sum(int((record.get("usage") or {}).get("input_tokens") or 0) for record in lane_records),
        "output_tokens_total": sum(int((record.get("usage") or {}).get("output_tokens") or 0) for record in lane_records),
        "adapter_estimated_cost_usd_total": sum(
            float(record.get("adapter_estimated_cost_usd") or 0) for record in lane_records
        ),
        "adapter_cost_authoritative": False,
        "exact_revision_observable": lane["exact_revision_observable"],
        "raw_prompt_or_response_persisted": False,
    }


def build_report(
    packet: Mapping[str, Any] | None = None,
    records: Sequence[Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    approval = dict(packet or load_approval())
    validate_approval(approval)
    observations = list(records if records is not None else load_observations())
    validate_observations(observations)
    lanes = [_lane_report(approval, lane_id, observations) for lane_id in LANE_IDS]
    primary = [item for item in lanes if item["included_in_primary_ranking"]]
    auxiliary = [item for item in lanes if not item["included_in_primary_ranking"]]
    by_lane = {item["lane_id"]: item for item in lanes}
    gpt = by_lane["openai_gpt_subscription"]
    gemini = by_lane["google_gemini_subscription"]
    deepseek = by_lane[DEEPSEEK_LANE]
    gpt_limit = approval["execution_limits"]["maximum_provider_reported_tokens"][
        "openai_gpt_subscription"
    ]
    gpt_token_stop = (
        gpt["consumed_samples"] < gpt["scheduled_samples"]
        and gpt["input_tokens_total"] + gpt["output_tokens_total"] >= gpt_limit
    )
    all_scheduled = len(observations) == approval["execution_limits"]["maximum_scheduled_samples"]
    bounded_complete = (
        gemini["consumed_samples"] == gemini["scheduled_samples"]
        and deepseek["consumed_samples"] == deepseek["scheduled_samples"]
        and (gpt["consumed_samples"] == gpt["scheduled_samples"] or gpt_token_stop)
    )

    successful_case_samples: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for record in observations:
        if record["status"] == "success" and record["lane_id"] in PRIMARY_LANES:
            successful_case_samples[record["lane_id"]][record["case_id"]] += 1
    paired_full_cases = sorted(
        set(successful_case_samples["openai_gpt_subscription"])
        & set(successful_case_samples["google_gemini_subscription"])
    )
    paired_full_cases = [
        case_id
        for case_id in paired_full_cases
        if successful_case_samples["openai_gpt_subscription"][case_id] == 2
        and successful_case_samples["google_gemini_subscription"][case_id] == 2
    ]
    paired_comparison = []
    for lane_id in sorted(PRIMARY_LANES):
        paired_records = [
            record
            for record in observations
            if record["lane_id"] == lane_id
            and record["case_id"] in paired_full_cases
            and record["status"] == "success"
        ]
        paired_passes = sum(record["score"]["correctness_passes"] for record in paired_records)
        paired_total = sum(record["score"]["correctness_total"] for record in paired_records)
        paired_comparison.append(
            {
                "lane_id": lane_id,
                "sample_count": len(paired_records),
                "perfect_sample_count": sum(
                    record["score"]["correctness_passes"]
                    == record["score"]["correctness_total"]
                    for record in paired_records
                ),
                "correctness_passes": paired_passes,
                "correctness_total": paired_total,
                "correctness_fraction": (
                    paired_passes / paired_total if paired_total else None
                ),
            }
        )
    without_hash = {
        "schema_version": REPORT_SCHEMA_VERSION,
        "decision": (
            "comparison_complete_with_hard_limit_stop"
            if bounded_complete and gpt_token_stop
            else "comparison_complete"
            if bounded_complete
            else "comparison_incomplete"
        ),
        "approval_binding": canonical_hash(approval),
        "source_projection_hash": approval["source_population"]["source_projection_hash"],
        "methodology": {
            "comparison_kind": approval["methodology"]["comparison_kind"],
            "pure_model_comparison": False,
            "primary_lane_ids": sorted(PRIMARY_LANES),
            "auxiliary_lane_ids": [DEEPSEEK_LANE],
            "deepseek_excluded_from_primary_ranking": True,
            "tool_observability_limit_retained": True,
            "primary_fully_paired_case_count": len(paired_full_cases),
            "primary_fully_paired_case_ids": paired_full_cases,
        },
        "execution": {
            "scheduled_samples": approval["execution_limits"]["maximum_scheduled_samples"],
            "consumed_samples": len(observations),
            "provider_calls_performed": bool(observations),
            "all_scheduled_samples_consumed": all_scheduled,
            "all_authorized_work_complete": bounded_complete,
            "unused_scheduled_samples": (
                approval["execution_limits"]["maximum_scheduled_samples"]
                - len(observations)
            ),
            "stop_reasons": (
                ["openai_gpt_subscription_provider_reported_token_ceiling_reached"]
                if gpt_token_stop
                else []
            ),
            "automatic_retries": False,
            "raw_prompt_persisted": False,
            "raw_response_persisted": False,
        },
        "primary_comparison": primary,
        "primary_fully_paired_comparison": paired_comparison,
        "auxiliary_diversity": auxiliary,
        "api_spine_boundary": {
            "classification": "developer_only_synthetic_access_ai_evaluation",
            "product_runtime_wiring": False,
            "graphql_or_rest_route_change": False,
            "provider_executed_tools_authorized": False,
            "database_or_audit_write": False,
            "appointment_or_confirmation_authority": False,
            "deployment_or_release": False,
        },
    }
    return {**without_hash, "report_hash": canonical_hash(without_hash)}


def write_report(path: Path = DEFAULT_REPORT_PATH) -> dict[str, Any]:
    report = build_report()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    return report


__all__ = [
    "APPROVAL_PATH",
    "DEEPSEEK_LANE",
    "DEFAULT_OBSERVATION_PATH",
    "DEFAULT_REPORT_PATH",
    "DispatchState",
    "LANE_IDS",
    "PRIMARY_LANES",
    "append_observation",
    "build_lane_cases",
    "build_prompt",
    "build_report",
    "canonical_hash",
    "failure_record",
    "lane_case_ids",
    "live_response_schema",
    "load_approval",
    "load_observations",
    "observation_key",
    "parse_json_object",
    "success_record",
    "utc_now",
    "validate_approval",
    "validate_observations",
    "write_report",
]
