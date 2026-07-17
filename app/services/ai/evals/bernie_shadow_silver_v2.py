"""Source-safe T3 shadow projection of admitted synthetic Silver v2 dialogue."""

from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path
from typing import Any, Sequence

from app.services.ai.evals.bernie_shadow_eval import (
    ExpectedDecision,
    ModelVersion,
    NormalizedShadowResponse,
    ShadowCase,
)
from app.services.ai.evals.bernie_shadow_runner import (
    AdapterSample,
    ShadowEvaluationRunner,
    ShadowRunnerConfig,
    summarize_shadow_run,
)
from app.services.bernie.synthetic_noise_v2_candidates import (
    DEFAULT_ADMISSION_PATH_V2,
    DEFAULT_CANDIDATE_PATH_V2,
    build_v2_candidate_artifacts,
    load_jsonl,
)


T3R1_REPORT_SCHEMA_VERSION = "emr4.bernie.t3r1_shadow_refresh.v1"
DEFAULT_T3R1_REPORT_PATH = Path("docs/bernie-t3r1-synthetic-shadow-baseline.json")
T3R1_REPEATS = 2

SAFE_SHADOW_TOOLS = frozenset(
    {
        "explain_schedule",
        "no_action",
        "propose_cancel",
        "propose_create",
        "propose_move",
        "propose_resize",
        "propose_status_change",
        "request_clarification",
    }
)
_MUTATING_PRODUCT_TOOLS = frozenset(
    {
        "cancel_booking",
        "change_appointment_status",
        "create_booking",
        "move_booking",
        "resize_booking",
    }
)


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def _sha256(value: Any) -> str:
    return "sha256:" + hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _load_bound_population() -> tuple[
    dict[str, Any], list[dict[str, Any]], dict[str, Any]
]:
    manifest, expected_candidates, expected_admission = build_v2_candidate_artifacts()
    candidates = load_jsonl(DEFAULT_CANDIDATE_PATH_V2)
    admission = json.loads(DEFAULT_ADMISSION_PATH_V2.read_text(encoding="utf-8"))
    if candidates != expected_candidates:
        raise ValueError("committed Silver v2 candidates do not regenerate exactly")
    if admission != expected_admission:
        raise ValueError("committed Silver v2 admission does not regenerate exactly")
    if admission["decision"] != "v2_admission_pass":
        raise ValueError("Silver v2 admission is not accepted")
    if any(
        admission[field]
        for field in (
            "protected_holdout_access",
            "historical_diary_access",
            "external_corpus_access",
            "product_parser_used_for_admission",
        )
    ):
        raise ValueError("Silver v2 admission crosses a closed evidence boundary")
    if any(admission["authority_grant"].values()):
        raise ValueError("Silver v2 admission grants prohibited authority")
    selected = set(admission["accepted_candidate_ids"])
    accepted = [item for item in candidates if item["candidate_id"] in selected]
    if len(accepted) != admission["accepted_count"] or len(accepted) != len(selected):
        raise ValueError("Silver v2 accepted population does not match admission")
    return manifest, accepted, admission


def _synthetic_ref(kind: str, value: str) -> str:
    return f"synthetic-{kind}-{value.replace('_', '-')}"


def _expected_entities(contract: dict[str, Any]) -> tuple[tuple[str, str], ...]:
    entities: list[tuple[str, str]] = []
    patient_semantics = contract["patient_semantics"]
    if patient_semantics == "ambiguous":
        entities.append(("patient_ref", "synthetic-patient-ambiguous"))
    elif patient_semantics != "omitted":
        entities.append(("patient_ref", _synthetic_ref("patient", "p-001")))

    practitioner_semantics = contract["practitioner_semantics"]
    if practitioner_semantics == "ambiguous":
        entities.append(("practitioner_ref", "synthetic-practitioner-ambiguous"))
    elif practitioner_semantics != "omitted":
        entities.append(("practitioner_ref", _synthetic_ref("practitioner", "pr-001")))

    seeded = contract["initial_diary_state"]["seeded_appointments"]
    if contract["intended_action"] not in {"create", "explain_schedule"} and seeded:
        entities.append(
            ("appointment_ref", _synthetic_ref("appointment", seeded[0]["appointment_id"]))
        )
    return tuple(sorted(entities))


def _expected_date_time(contract: dict[str, Any]) -> tuple[tuple[str, str], ...]:
    values = {
        key: str(value)
        for key, value in contract["normalized_values"].items()
        if value is not None
    }
    values["temporal_relation"] = contract["temporal_relation"]
    return tuple(sorted(values.items()))


def _expected_shadow_tool(contract: dict[str, Any]) -> str:
    if contract["expected_clarification"] is not None:
        return "request_clarification"
    if contract["action_withdrawn"]:
        return "no_action"
    action = contract["intended_action"]
    if action == "explain_schedule":
        return "explain_schedule"
    return f"propose_{action}"


def _instruction(candidate: dict[str, Any]) -> str:
    return "\n".join(
        f"[Receptionist turn {turn['turn']}] {turn['utterance']}"
        for turn in candidate["dialogue_turns"]
    )


def build_silver_v2_shadow_cases() -> tuple[ShadowCase, ...]:
    """Project the exact admitted v2 population without copying its fixture."""

    manifest, candidates, _admission = _load_bound_population()
    anchors = {item["seed_id"]: item for item in manifest["anchors"]}
    allowed_tools = tuple(sorted(SAFE_SHADOW_TOOLS))
    cases: list[ShadowCase] = []
    for candidate in candidates:
        anchor = anchors[candidate["source_seed_id"]]
        contract = anchor["semantic_contract"]
        form = anchor["dialogue_form_contract"]["dialogue_form"]
        cases.append(
            ShadowCase(
                case_id=f"t3r1_{candidate['candidate_id']}",
                source=f"authored_synthetic:silver_v2:{candidate['candidate_id']}",
                instruction=_instruction(candidate),
                expected=ExpectedDecision(
                    intent=contract["intended_action"],
                    entities=_expected_entities(contract),
                    date_time=_expected_date_time(contract),
                    requires_clarification=contract["expected_clarification"] is not None,
                    tool_name=_expected_shadow_tool(contract),
                    action_withdrawn=contract["action_withdrawn"],
                ),
                allowed_tools=allowed_tools,
                metadata=(
                    ("action", contract["intended_action"]),
                    ("dialogue_form", form),
                    ("evidence_tier", "silver"),
                    ("noise_level", candidate["noise_level"]),
                    ("source_seed_id", anchor["seed_id"]),
                ),
            )
        )
    errors = validate_silver_v2_shadow_cases(cases)
    if errors:
        raise ValueError("invalid Silver v2 shadow projection: " + "; ".join(errors))
    return tuple(cases)


def validate_silver_v2_shadow_cases(cases: Sequence[ShadowCase]) -> list[str]:
    errors: list[str] = []
    ids = [case.case_id for case in cases]
    if len(cases) != 192:
        errors.append("projection must contain exactly 192 cases")
    if len(ids) != len(set(ids)):
        errors.append("projection case IDs must be unique")

    by_action: Counter[str] = Counter()
    by_form: Counter[str] = Counter()
    by_noise: Counter[str] = Counter()
    for case in cases:
        metadata = dict(case.metadata)
        by_action[metadata.get("action", "")] += 1
        by_form[metadata.get("dialogue_form", "")] += 1
        by_noise[metadata.get("noise_level", "")] += 1
        if metadata.get("evidence_tier") != "silver":
            errors.append(f"{case.case_id}: evidence tier must be silver")
        if set(case.allowed_tools) != SAFE_SHADOW_TOOLS:
            errors.append(f"{case.case_id}: safe shadow tool vocabulary drift")
        if set(case.allowed_tools) & _MUTATING_PRODUCT_TOOLS:
            errors.append(f"{case.case_id}: product mutation tool exposed")
        if case.expected.tool_name not in SAFE_SHADOW_TOOLS:
            errors.append(f"{case.case_id}: unsafe expected shadow tool")
        if case.expected.action_withdrawn is None:
            errors.append(f"{case.case_id}: withdrawal expectation must be explicit")
        if "[Receptionist turn " not in case.instruction:
            errors.append(f"{case.case_id}: dialogue turn identity missing")

    expected_actions = {
        "create": 32,
        "move": 32,
        "resize": 32,
        "cancel": 32,
        "status_change": 32,
        "explain_schedule": 32,
    }
    expected_forms = {
        "one_shot": 24,
        "clarification": 24,
        "correction": 24,
        "reversal": 24,
        "ellipsis": 24,
        "anaphora": 24,
        "repeated_request": 24,
        "session_restart": 24,
    }
    if dict(by_action) != expected_actions:
        errors.append("projection action balance mismatch")
    if dict(by_form) != expected_forms:
        errors.append("projection dialogue-form balance mismatch")
    if dict(by_noise) != {"medium": 96, "high": 96}:
        errors.append("projection noise balance mismatch")
    return errors


def _case_projection_record(case: ShadowCase) -> dict[str, Any]:
    return {
        "case_id": case.case_id,
        "source": case.source,
        "instruction_hash": _sha256(case.instruction),
        "expected": {
            "intent": case.expected.intent,
            "entities": case.expected.entities,
            "date_time": case.expected.date_time,
            "requires_clarification": case.expected.requires_clarification,
            "tool_name": case.expected.tool_name,
            "action_withdrawn": case.expected.action_withdrawn,
        },
        "allowed_tools": case.allowed_tools,
        "metadata": case.metadata,
    }


class _ExpectedDecisionEchoAdapter:
    """Offline plumbing oracle; deliberately not evidence of model quality."""

    def __init__(self, projection_hash: str) -> None:
        self._model_version = ModelVersion(
            provider="offline",
            model="expected-decision-echo",
            model_revision=projection_hash,
            prompt_version="t3r1-projection-v1",
            tool_schema_version="bernie-shadow-safe-proposals-v1",
            temperature=0.0,
        )

    @property
    def model_version(self) -> ModelVersion:
        return self._model_version

    def sample(self, case: ShadowCase, sample_index: int) -> AdapterSample:
        del sample_index
        expected = case.expected
        return AdapterSample(
            response=NormalizedShadowResponse(
                intent=expected.intent,
                entities=expected.entities,
                date_time=expected.date_time,
                requires_clarification=expected.requires_clarification,
                tool_name=expected.tool_name,
                writes_authorized=False,
                claims_action_completed=False,
                response_hash=_sha256(_case_projection_record(case)["expected"]),
                action_withdrawn=expected.action_withdrawn,
            )
        )


def build_t3r1_shadow_report() -> dict[str, Any]:
    _manifest, _candidates, admission = _load_bound_population()
    cases = build_silver_v2_shadow_cases()
    records = [_case_projection_record(case) for case in cases]
    projection_hash = _sha256(records)
    observations = ShadowEvaluationRunner(
        ShadowRunnerConfig(enabled=True, repeats=T3R1_REPEATS)
    ).run(cases, _ExpectedDecisionEchoAdapter(projection_hash))
    summary = summarize_shadow_run(observations)

    by_action = Counter(dict(case.metadata)["action"] for case in cases)
    by_form = Counter(dict(case.metadata)["dialogue_form"] for case in cases)
    by_noise = Counter(dict(case.metadata)["noise_level"] for case in cases)
    expected_samples = len(cases) * T3R1_REPEATS
    plumbing_passed = (
        len(cases) == 192
        and summary.sample_count == expected_samples
        and summary.safe_sample_count == expected_samples
        and summary.perfect_sample_count == expected_samples
        and summary.correctness_passes == summary.correctness_total
        and summary.correctness_total == expected_samples * 6
        and summary.variant_case_count == 0
    )
    without_hash = {
        "schema_version": T3R1_REPORT_SCHEMA_VERSION,
        "decision": (
            "provider_free_shadow_refresh_pass" if plumbing_passed else "revision_required"
        ),
        "input_bindings": {
            "anchor_manifest_hash": admission["anchor_manifest_hash"],
            "candidate_hash": admission["canonical_candidate_hash"],
            "admission_hash": admission["admission_hash"],
            "accepted_selection_hash": admission["accepted_selection_hash"],
        },
        "projection": {
            "projection_hash": projection_hash,
            "case_count": len(cases),
            "safe_tool_vocabulary": sorted(SAFE_SHADOW_TOOLS),
            "scored_dimensions": [
                "intent",
                "entities",
                "date_time",
                "clarification",
                "tool_selection",
                "whole_action_withdrawal",
            ],
            "by_action": dict(sorted(by_action.items())),
            "by_dialogue_form": dict(sorted(by_form.items())),
            "by_noise_level": dict(sorted(by_noise.items())),
        },
        "offline_plumbing_check": {
            "adapter": "expected-decision-echo",
            "repeats_per_case": T3R1_REPEATS,
            "sample_count": summary.sample_count,
            "safe_sample_count": summary.safe_sample_count,
            "perfect_sample_count": summary.perfect_sample_count,
            "correctness_passes": summary.correctness_passes,
            "correctness_total": summary.correctness_total,
            "variant_case_count": summary.variant_case_count,
            "provider_calls_performed": False,
            "establishes_model_quality": False,
        },
        "boundaries": {
            "protected_holdout_access": False,
            "historical_diary_access": False,
            "external_corpus_access": False,
            "provider_access": False,
            "raw_response_persistence": False,
            "provider_tools": False,
            "runtime_wiring": False,
            "api_or_database_change": False,
            "product_write": False,
            "confirmation_authority": False,
        },
    }
    return {**without_hash, "report_hash": _sha256(without_hash)}


def write_t3r1_shadow_report(
    path: Path = DEFAULT_T3R1_REPORT_PATH,
) -> dict[str, Any]:
    report = build_t3r1_shadow_report()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return report


def check_t3r1_shadow_report(path: Path = DEFAULT_T3R1_REPORT_PATH) -> list[str]:
    if not path.is_file():
        return ["missing T3R1 shadow refresh report"]
    actual = json.loads(path.read_text(encoding="utf-8"))
    expected = build_t3r1_shadow_report()
    return [] if actual == expected else ["T3R1 shadow refresh report drift"]


__all__ = [
    "DEFAULT_T3R1_REPORT_PATH",
    "SAFE_SHADOW_TOOLS",
    "T3R1_REPEATS",
    "build_silver_v2_shadow_cases",
    "build_t3r1_shadow_report",
    "check_t3r1_shadow_report",
    "validate_silver_v2_shadow_cases",
    "write_t3r1_shadow_report",
]
