"""Content-blind validation, sealing, and aggregation primitives for LC4V7.

This module contains no certification utterances or Gold values.  The real
corpus is supplied only through explicit paths to the one-shot CLI.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence


ROOT = Path(__file__).resolve().parents[3]
REFERENCE_DATE = "2031-05-12"
CORPUS_SCHEMA = "bernie.lc4v7.corpus.v1"
MANIFEST_SCHEMA = "bernie.lc4v7.manifest.v1"
SEAL_SCHEMA = "bernie.lc4v7.seal.v1"
REPORT_SCHEMA = "bernie.lc4v7.aggregate-report.v1"
PROVENANCE = "fresh_sol_authored_synthetic_gold_certification"
CREATED_BY = "gpt_sol"

SCENARIO_COUNT = 288
SAMPLE_COUNT = 576
FAMILY_COUNT = 24
SCENARIOS_PER_FAMILY = 12
SAMPLES_PER_FAMILY = 24
MULTI_TURN_COUNT = 72
ONE_TURN_COUNT = 216
STYLE_SCENARIO_COUNT = 48
STYLE_SAMPLE_COUNT = 96
ACTION_SCENARIO_COUNT = 48

ACTIONS = (
    "create",
    "cancel",
    "move",
    "resize",
    "status_change",
    "explain_schedule",
)
LANGUAGE_STYLES = (
    "plain",
    "paraphrase",
    "speech_like",
    "word_order",
    "correction",
    "interval",
)
DIMENSIONS = (
    "intended_action",
    "action_semantics",
    "entity_semantics",
    "temporal_relation",
    "normalized_value",
    "source_span",
    "extraction_clarification",
    "policy_resolution",
    "policy_clarification",
    "clarification_composition",
    "interpretation_tool_contract",
    "replay_contract",
    "safety",
)

TOP_LEVEL_KEYS = {
    "schema_version",
    "corpus_id",
    "reference_date",
    "provenance",
    "scenarios",
}
SCENARIO_KEYS = {
    "scenario_id",
    "family_id",
    "action",
    "language_style",
    "turn_count",
    "coverage_cell",
    "utterances",
    "diary",
    "extraction_gold",
    "policy_gold",
    "composition_gold",
}
DIARY_KEYS = {"state", "appointments"}
EXTRACTION_GOLD_KEYS = {
    "intended_action",
    "action_semantics",
    "temporal_relation",
    "earliest_time",
    "latest_time",
    "normalized_values",
    "entity_semantics",
    "source_spans",
    "requires_clarification",
    "clarification_choices",
    "authority",
    "action_negated",
    "selected_tools",
}
POLICY_GOLD_KEYS = {
    "resolved_patient",
    "resolved_practitioner",
    "resolved_practitioner_id",
    "diary_relation",
    "conflicting_fields",
    "requires_clarification",
    "clarification_choices",
    "authority",
    "selected_tools",
    "downstream_outcome",
    "appointment_deltas",
    "audit_deltas",
    "simulated_write",
}
COMPOSITION_GOLD_KEYS = {"terminal_class", "semantic_lossless"}
MANIFEST_KEYS = {
    "schema_version",
    "attempt_id",
    "source_commit",
    "contract_hash",
    "acceptance_rule_hash",
    "framework_hashes",
    "corpus_hash",
    "corpus_population",
    "created_by",
}
SEAL_KEYS = {
    "schema_version",
    "attempt_id",
    "source_commit",
    "manifest_hash",
    "corpus_hash",
    "state",
    "consumed_at",
    "consumed_reason",
}
FRAMEWORK_FILES = (
    "app/services/bernie/lc4v7_content_blind_framework.py",
    "app/services/bernie/lc4v7_acceptance_rule.py",
    "scripts/run_bernie_lc4v7_certification.py",
    "tests/test_bernie_lc4v7_content_blind_framework.py",
    "tests/test_bernie_lc4v7_acceptance_rule.py",
)
CONTRACT_PATH = "orchestration/agent_inbox/codex/lc4v7-sol-contract.md"
ACCEPTANCE_RULE_PATH = (
    "orchestration/agent_inbox/codex/lc4v7-one-shot-acceptance-rule.md"
)

_PROTECTED_PRIOR_PATH = re.compile(r"lc4v[1-6](?:\D|$)", re.IGNORECASE)


def canonical_json_bytes(value: Any) -> bytes:
    """Return the only canonical JSON representation accepted by V7."""
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def canonical_sha256(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def file_sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def expected_framework_hashes() -> dict[str, str]:
    return {relative: file_sha256(ROOT / relative) for relative in FRAMEWORK_FILES}


def load_json_object(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path.name} must contain a JSON object")
    return payload


def reject_protected_prior_paths(paths: Sequence[Path]) -> None:
    """Reject prior-version paths before any caller opens them."""
    for path in paths:
        if _PROTECTED_PRIOR_PATH.search(str(path)):
            raise ValueError("protected prior-version input path refused")


def _is_string_list(value: Any) -> bool:
    return isinstance(value, list) and all(isinstance(item, str) for item in value)


def _is_object_list(value: Any) -> bool:
    return isinstance(value, list) and all(isinstance(item, Mapping) for item in value)


def _validate_source_spans(
    value: Any, utterances: list[str], label: str, errors: list[str]
) -> None:
    if not isinstance(value, list) or len(value) != len(utterances):
        errors.append(f"{label} source_spans must align one-to-one with turns")
        return
    for turn_index, spans in enumerate(value):
        if not isinstance(spans, Mapping):
            errors.append(f"{label} source_spans turn must be an object")
            continue
        for field, span in spans.items():
            if not isinstance(field, str) or not field:
                errors.append(f"{label} source span field must be a non-empty string")
            if (
                not isinstance(span, list)
                or len(span) != 2
                or any(not isinstance(offset, int) for offset in span)
                or span[0] < 0
                or span[1] < span[0]
                or span[1] > len(utterances[turn_index])
            ):
                errors.append(f"{label} source span offsets are invalid")


def _validate_scenario(case: Any, index: int, errors: list[str]) -> None:
    label = f"scenario[{index}]"
    if not isinstance(case, Mapping):
        errors.append(f"{label} must be an object")
        return
    if set(case) != SCENARIO_KEYS:
        errors.append(f"{label} field population is not exact")

    for field in ("scenario_id", "family_id", "coverage_cell"):
        if not isinstance(case.get(field), str) or not case.get(field):
            errors.append(f"{label} {field} must be a non-empty string")
    if case.get("action") not in ACTIONS:
        errors.append(f"{label} action is invalid")
    if case.get("language_style") not in LANGUAGE_STYLES:
        errors.append(f"{label} language_style is invalid")
    utterances = case.get("utterances")
    if (
        not isinstance(utterances, list)
        or not utterances
        or any(not isinstance(item, str) or not item.strip() for item in utterances)
    ):
        errors.append(f"{label} utterances must be non-empty strings")
        utterances = []
    if case.get("turn_count") != len(utterances):
        errors.append(f"{label} turn_count must equal the utterance population")

    diary = case.get("diary")
    if not isinstance(diary, Mapping) or set(diary) != DIARY_KEYS:
        errors.append(f"{label} diary field population is not exact")
    elif not isinstance(diary.get("state"), str) or not _is_object_list(
        diary.get("appointments")
    ):
        errors.append(f"{label} diary values are invalid")

    extraction = case.get("extraction_gold")
    if not isinstance(extraction, Mapping) or set(extraction) != EXTRACTION_GOLD_KEYS:
        errors.append(f"{label} extraction_gold field population is not exact")
    else:
        if not isinstance(extraction.get("normalized_values"), Mapping):
            errors.append(f"{label} normalized_values must be an object")
        if not isinstance(extraction.get("entity_semantics"), Mapping):
            errors.append(f"{label} entity_semantics must be an object")
        if not isinstance(extraction.get("requires_clarification"), bool):
            errors.append(f"{label} extraction clarification must be Boolean")
        for field in ("clarification_choices", "selected_tools"):
            if not _is_string_list(extraction.get(field)):
                errors.append(f"{label} extraction {field} must be a string list")
        if extraction.get("authority") not in {"read", "clarify", "refuse"}:
            errors.append(f"{label} extraction authority is invalid")
        if not isinstance(extraction.get("action_negated"), bool):
            errors.append(f"{label} action_negated must be Boolean")
        _validate_source_spans(extraction.get("source_spans"), utterances, label, errors)

    policy = case.get("policy_gold")
    if not isinstance(policy, Mapping) or set(policy) != POLICY_GOLD_KEYS:
        errors.append(f"{label} policy_gold field population is not exact")
    else:
        if not isinstance(policy.get("requires_clarification"), bool):
            errors.append(f"{label} policy clarification must be Boolean")
        for field in (
            "conflicting_fields",
            "clarification_choices",
            "selected_tools",
        ):
            if not _is_string_list(policy.get(field)):
                errors.append(f"{label} policy {field} must be a string list")
        if policy.get("authority") not in {"read", "clarify", "refuse"}:
            errors.append(f"{label} policy authority is invalid")
        if not _is_object_list(policy.get("appointment_deltas")) or not _is_object_list(
            policy.get("audit_deltas")
        ):
            errors.append(f"{label} policy deltas must be object lists")
        if not isinstance(policy.get("simulated_write"), bool):
            errors.append(f"{label} simulated_write must be Boolean")

    composition = case.get("composition_gold")
    if not isinstance(composition, Mapping) or set(composition) != COMPOSITION_GOLD_KEYS:
        errors.append(f"{label} composition_gold field population is not exact")
    elif composition.get("terminal_class") not in {
        "read_only",
        "clarification_required",
        "refused",
        "replay_only_change",
    } or not isinstance(composition.get("semantic_lossless"), bool):
        errors.append(f"{label} composition_gold values are invalid")


def population_summary(scenarios: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    turns = Counter("multi" if item.get("turn_count", 0) > 1 else "one" for item in scenarios)
    return {
        "scenarios": len(scenarios),
        "families": dict(Counter(str(item.get("family_id")) for item in scenarios)),
        "actions": dict(Counter(str(item.get("action")) for item in scenarios)),
        "language_styles": dict(
            Counter(str(item.get("language_style")) for item in scenarios)
        ),
        "turns": dict(turns),
        "unique_coverage_cells": len(
            {str(item.get("coverage_cell")) for item in scenarios}
        ),
    }


def validate_population_summary(summary: Mapping[str, Any]) -> tuple[str, ...]:
    errors: list[str] = []
    if summary.get("scenarios") != SCENARIO_COUNT:
        errors.append("scenario population must equal 288")
    families = summary.get("families")
    if (
        not isinstance(families, Mapping)
        or len(families) != FAMILY_COUNT
        or any(count != SCENARIOS_PER_FAMILY for count in families.values())
    ):
        errors.append("family population must be exactly 24 by 12")
    actions = summary.get("actions")
    if not isinstance(actions, Mapping) or dict(actions) != {
        action: ACTION_SCENARIO_COUNT for action in ACTIONS
    }:
        errors.append("action population must be exactly six by 48")
    styles = summary.get("language_styles")
    if not isinstance(styles, Mapping) or dict(styles) != {
        style: STYLE_SCENARIO_COUNT for style in LANGUAGE_STYLES
    }:
        errors.append("language-style population must be exactly six by 48")
    if summary.get("turns") != {"multi": MULTI_TURN_COUNT, "one": ONE_TURN_COUNT}:
        errors.append("turn population must be exactly 72 multi and 216 one")
    if summary.get("unique_coverage_cells") != SCENARIO_COUNT:
        errors.append("coverage cells must be unique across all 288 scenarios")
    return tuple(errors)


def validate_corpus(corpus: Any) -> tuple[str, ...]:
    """Validate exact schema and frozen balance without executing product code."""
    errors: list[str] = []
    if not isinstance(corpus, Mapping):
        return ("corpus must be an object",)
    if set(corpus) != TOP_LEVEL_KEYS:
        errors.append("top-level field population is not exact")
    if corpus.get("schema_version") != CORPUS_SCHEMA:
        errors.append("corpus schema_version is not exact")
    if not isinstance(corpus.get("corpus_id"), str) or not corpus.get("corpus_id"):
        errors.append("corpus_id must be a non-empty string")
    if corpus.get("reference_date") != REFERENCE_DATE:
        errors.append("reference_date is not exact")
    if corpus.get("provenance") != PROVENANCE:
        errors.append("provenance is not exact")
    scenarios = corpus.get("scenarios")
    if not isinstance(scenarios, list):
        return tuple(errors + ["scenarios must be a list"])
    for index, case in enumerate(scenarios):
        _validate_scenario(case, index, errors)

    ids = [item.get("scenario_id") for item in scenarios if isinstance(item, Mapping)]
    cells = [item.get("coverage_cell") for item in scenarios if isinstance(item, Mapping)]
    if len(ids) != len(set(ids)):
        errors.append("scenario IDs must be unique")
    if len(cells) != len(set(cells)):
        errors.append("coverage cells must be unique")
    errors.extend(validate_population_summary(population_summary(scenarios)))
    return tuple(dict.fromkeys(errors))


def validate_manifest(
    manifest: Any,
    *,
    corpus_hash: str,
    source_commit: str,
    population: Mapping[str, Any],
) -> tuple[str, ...]:
    errors: list[str] = []
    if not isinstance(manifest, Mapping):
        return ("manifest must be an object",)
    if set(manifest) != MANIFEST_KEYS:
        errors.append("manifest field population is not exact")
    if manifest.get("schema_version") != MANIFEST_SCHEMA:
        errors.append("manifest schema_version is not exact")
    if manifest.get("source_commit") != source_commit:
        errors.append("manifest source commit drift")
    if manifest.get("corpus_hash") != corpus_hash:
        errors.append("manifest corpus hash drift")
    if manifest.get("corpus_population") != population:
        errors.append("manifest corpus population drift")
    if manifest.get("created_by") != CREATED_BY:
        errors.append("manifest author is not exact")
    if manifest.get("contract_hash") != file_sha256(ROOT / CONTRACT_PATH):
        errors.append("manifest contract hash drift")
    if manifest.get("acceptance_rule_hash") != file_sha256(
        ROOT / ACCEPTANCE_RULE_PATH
    ):
        errors.append("manifest acceptance rule hash drift")
    for field in (
        "attempt_id",
        "contract_hash",
        "acceptance_rule_hash",
        "corpus_hash",
    ):
        if not isinstance(manifest.get(field), str) or not manifest.get(field):
            errors.append(f"manifest {field} must be non-empty")
    framework_hashes = manifest.get("framework_hashes")
    if not isinstance(framework_hashes, Mapping):
        errors.append("manifest framework_hashes are invalid")
    elif dict(framework_hashes) != expected_framework_hashes():
        errors.append("manifest framework hash drift")
    return tuple(dict.fromkeys(errors))


def validate_seal_envelope(seal: Any) -> tuple[str, ...]:
    errors: list[str] = []
    if not isinstance(seal, Mapping):
        return ("seal must be an object",)
    if set(seal) != SEAL_KEYS:
        errors.append("seal field population is not exact")
    if seal.get("schema_version") != SEAL_SCHEMA:
        errors.append("seal schema_version is not exact")
    if seal.get("state") not in {"unconsumed", "consumed"}:
        errors.append("seal state is invalid")
    if seal.get("state") == "unconsumed" and (
        seal.get("consumed_at") is not None or seal.get("consumed_reason") is not None
    ):
        errors.append("unconsumed seal has consumption metadata")
    for field in ("attempt_id", "source_commit", "manifest_hash", "corpus_hash"):
        if not isinstance(seal.get(field), str) or not seal.get(field):
            errors.append(f"seal {field} must be non-empty")
    return tuple(dict.fromkeys(errors))


def consume_seal(path: Path, seal: Mapping[str, Any], *, consumed_at: str) -> dict[str, Any]:
    """Irrevocably consume a minimally valid seal before corpus validation."""
    errors = validate_seal_envelope(seal)
    if errors:
        raise ValueError("; ".join(errors))
    if seal["state"] != "unconsumed":
        raise ValueError("seal is already consumed")
    consumed = dict(seal)
    consumed.update(
        state="consumed",
        consumed_at=consumed_at,
        consumed_reason="evaluation_started",
    )
    temporary = path.with_name(path.name + ".consuming")
    temporary.write_bytes(canonical_json_bytes(consumed) + b"\n")
    os.replace(temporary, path)
    return consumed


def validate_consumed_binding(
    seal: Mapping[str, Any],
    *,
    manifest: Mapping[str, Any],
    manifest_hash: str,
    corpus_hash: str,
    source_commit: str,
) -> tuple[str, ...]:
    errors: list[str] = []
    errors.extend(validate_seal_envelope(seal))
    if seal.get("state") != "consumed":
        errors.append("seal was not consumed before evaluation")
    if seal.get("attempt_id") != manifest.get("attempt_id"):
        errors.append("seal attempt drift")
    if seal.get("manifest_hash") != manifest_hash:
        errors.append("seal manifest hash drift")
    if seal.get("corpus_hash") != corpus_hash:
        errors.append("seal corpus hash drift")
    if seal.get("source_commit") != source_commit:
        errors.append("seal source commit drift")
    return tuple(dict.fromkeys(errors))


def empty_dimension_counts() -> dict[str, dict[str, int]]:
    return {dimension: {"passed": 0, "total": 0} for dimension in DIMENSIONS}


def terminal_class(policy: Any) -> str:
    if policy.authority == "refuse":
        return "refused"
    if policy.requires_clarification:
        return "clarification_required"
    if policy.is_simulated_confirmed_write:
        return "replay_only_change"
    return "read_only"


def normalized_source_spans(extraction: Any) -> list[dict[str, list[int]]]:
    return [
        {field: [span[0], span[1]] for field, span in turn.source_spans.items()}
        for turn in extraction.normalized_turns
    ]


def observation_fingerprint(extraction: Any, policy: Any) -> str:
    payload = {
        "extraction": {
            "intended_action": extraction.intended_action,
            "action_semantics": extraction.action_semantics,
            "temporal_relation": extraction.temporal_relation,
            "earliest_time": extraction.earliest_time,
            "latest_time": extraction.latest_time,
            "normalized_values": extraction.normalized_values,
            "entity_semantics": extraction.entity_semantics,
            "source_spans": normalized_source_spans(extraction),
            "requires_clarification": extraction.requires_clarification,
            "clarification_choices": list(extraction.clarification_choices),
            "authority": extraction.authority_claim,
            "action_negated": extraction.action_negated,
            "selected_tools": list(extraction.selected_tool_sequence),
            "claims_action_completed": extraction.claims_action_completed,
        },
        "policy": {
            "resolved_patient": policy.resolved_patient,
            "resolved_practitioner": policy.resolved_practitioner,
            "resolved_practitioner_id": policy.resolved_practitioner_id,
            "diary_relation": policy.diary_comparison.relation,
            "conflicting_fields": list(policy.diary_comparison.conflicting_fields),
            "requires_clarification": policy.requires_clarification,
            "clarification_choices": list(policy.clarification_choices),
            "authority": policy.authority,
            "selected_tools": list(policy.selected_tools),
            "downstream_outcome": policy.downstream_outcome,
            "appointment_deltas": list(policy.appointment_deltas),
            "audit_deltas": list(policy.audit_deltas),
            "simulated_write": policy.is_simulated_confirmed_write,
            "utterance_entity_semantics_unchanged": (
                policy.utterance_entity_semantics_unchanged
            ),
        },
    }
    return canonical_sha256(payload)


__all__ = [
    "ACTIONS",
    "CORPUS_SCHEMA",
    "CREATED_BY",
    "DIMENSIONS",
    "FAMILY_COUNT",
    "LANGUAGE_STYLES",
    "MANIFEST_SCHEMA",
    "PROVENANCE",
    "REFERENCE_DATE",
    "REPORT_SCHEMA",
    "SAMPLE_COUNT",
    "SCENARIO_COUNT",
    "SEAL_SCHEMA",
    "canonical_json_bytes",
    "canonical_sha256",
    "consume_seal",
    "empty_dimension_counts",
    "expected_framework_hashes",
    "file_sha256",
    "load_json_object",
    "normalized_source_spans",
    "observation_fingerprint",
    "population_summary",
    "reject_protected_prior_paths",
    "terminal_class",
    "validate_consumed_binding",
    "validate_corpus",
    "validate_manifest",
    "validate_population_summary",
    "validate_seal_envelope",
]
