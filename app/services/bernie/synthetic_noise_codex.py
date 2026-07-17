"""Sol recovery of the rejected Codex noisy Bernie Silver generator.

The original worker source is preserved at commit f6383ca8. This recovery
reads only the corrected dialogue-free semantic seed manifest, records Sol as
the generator identity, and never changes an oracle, grants authority, or
accesses protected or external corpus material.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "emr4.bernie.synthetic_noise_candidate.v1"
GENERATOR_IDENTITY = {
    "provider_id": "openai",
    "model_id": "gpt-sol-recovery",
    "lane_id": "synthetic-noise-sol-recovery",
}
GENERATOR_SLUG = "openai/gpt-sol-recovery/synthetic-noise-sol-recovery"
ORIGINAL_WORKER_COMMIT = "f6383ca806ad3eb1e403d44394989dc8563e811d"
RECOVERY_SOURCE_HEAD = "960849f5cc359a2720e85e9bd283c62c6eb37978"
SEED_COUNT = 96
CANDIDATE_COUNT = 192
SEED_PATH = Path("tests/fixtures/bernie_synthetic_noise/semantic_seeds.json")
OUTPUT_PATH = Path(
    "tests/fixtures/bernie_synthetic_noise/candidates_sol_recovery.jsonl"
)

ALLOWED_NOISE_OPERATIONS = {
    "filler",
    "abbreviation",
    "typo",
    "punctuation_case",
    "speech_disfluency",
    "reordered_slots",
    "ellipsis",
    "anaphora",
    "correction",
    "reversal",
    "temporal_surface",
    "staff_shorthand",
    "dictation_artifact",
    "distractor",
}
TOP_LEVEL_FIELDS = {
    "schema_version",
    "candidate_id",
    "source_seed_id",
    "source_seed_hash",
    "generator_identity",
    "variant_index",
    "noise_level",
    "noise_operations",
    "dialogue_turns",
    "evidence_spans",
    "semantic_change",
    "provenance",
    "adjudication",
    "authority_grant",
}
AUTHORITY_GRANT = {
    "provider_write": False,
    "diary_write": False,
    "confirmation": False,
    "override_authority": False,
}
MEDIUM_OPERATIONS = [
    "filler",
    "abbreviation",
    "punctuation_case",
    "staff_shorthand",
]
HIGH_OPERATIONS = [
    "filler",
    "abbreviation",
    "speech_disfluency",
    "reordered_slots",
    "staff_shorthand",
    "dictation_artifact",
]
OPENERS = (
    "Quick one",
    "Next diary job",
    "When you're ready",
    "One for the list",
    "Small diary task",
    "This one next",
    "While I'm here",
    "Another diary item",
    "Before I forget",
    "A quick change",
    "Next item",
    "For the diary",
    "Just this one",
    "One more",
    "Here's the next",
    "Last thing",
)

CONTACT_PATTERNS = (
    re.compile(r"\b(?:\+?61|0)\s*\d(?:[\s-]*\d){7,9}\b"),
    re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I),
    re.compile(r"\b\d{10,16}\b"),
)
FORBIDDEN_CONTENT = re.compile(
    r"\b(?:diagnos(?:is|ed)|symptom|medication|medicare|date of birth|"
    r"phone number|email address|street address|triage|prescription|"
    r"blood pressure|allerg(?:y|ies)|bernie\s*:|assistant\s*:)\b",
    re.I,
)


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def _canonical_jsonl(records: list[dict[str, Any]]) -> str:
    return "".join(_canonical_json(record) + "\n" for record in records)


def _candidate_sha256(records: list[dict[str, Any]]) -> str:
    payload = _canonical_jsonl(records).encode("utf-8")
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def _load_manifest() -> dict[str, Any]:
    return json.loads(SEED_PATH.read_text(encoding="utf-8"))


def _clock(hour_minute: str) -> str:
    hour, minute = (int(part) for part in hour_minute.split(":"))
    suffix = "am" if hour < 12 else "pm"
    display_hour = hour % 12 or 12
    return f"{display_hour}{f':{minute:02d}' if minute else ''}{suffix}"


def _temporal_phrase(contract: dict[str, Any]) -> str:
    relation = contract["temporal_relation"]
    earliest = contract.get("earliest_time")
    latest = contract.get("latest_time")
    if relation == "exact":
        return f"at {_clock(earliest)}"
    if relation == "approximate":
        if earliest and latest and earliest != latest:
            start_minutes = int(earliest[:2]) * 60 + int(earliest[3:])
            end_minutes = int(latest[:2]) * 60 + int(latest[3:])
            midpoint = (start_minutes + end_minutes) // 2
            return f"around {_clock(f'{midpoint // 60:02d}:{midpoint % 60:02d}')}"
        return f"around {_clock(earliest or latest)}"
    if relation == "not_before":
        return f"{_clock(earliest)} or later"
    if relation == "not_after":
        return f"by {_clock(latest)}"
    if relation == "interval":
        return f"between {_clock(earliest)} and {_clock(latest)}"
    if relation == "unspecified":
        return "time not specified"
    raise ValueError(f"Unsupported temporal relation: {relation!r}")


def _surface_value(seed: dict[str, Any], key: str) -> str:
    values = seed["surface_evidence"].get(key)
    if not isinstance(values, list) or not values or not isinstance(values[-1], str):
        raise ValueError(f"Missing surface evidence for {seed['seed_id']}:{key}")
    return values[-1]


def _patient_phrase(seed: dict[str, Any]) -> str:
    semantics = seed["semantic_contract"]["patient_semantics"]
    if semantics == "ambiguous":
        return "someone"
    if semantics == "omitted":
        return ""
    return _surface_value(seed, "patient")


def _practitioner_phrase(seed: dict[str, Any]) -> str:
    contract = seed["semantic_contract"]
    semantics = contract["practitioner_semantics"]
    if semantics == "ambiguous":
        return "a doctor"
    if semantics == "omitted":
        return ""
    if semantics == "corrected" and contract["dialogue_form"] != "correction":
        return "a doctor—sorry, Dr Shera"
    return _surface_value(seed, "practitioner")


def _status_prefix(contract: dict[str, Any]) -> str:
    state = contract["entity_state"]
    if state == "negated":
        return "No new booking—status only; "
    if state == "mismatched":
        return "The diary match looks off; "
    return ""


def _explain_prefix(contract: dict[str, Any]) -> str:
    state = contract["entity_state"]
    if state == "negated":
        return "No diary change—view only; "
    if state == "mismatched":
        return "The roster view isn't matching; "
    return ""


def _status_value(contract: dict[str, Any]) -> str:
    values = {
        delta.get("new_status")
        for delta in contract.get("expected_appointment_deltas", [])
        if delta.get("change_type") == "status_changed"
    }
    if values != {"arrived"}:
        raise ValueError(f"Unsupported status semantic: {values!r}")
    return "arrived"


def _semantic_parts(seed: dict[str, Any]) -> dict[str, str]:
    contract = seed["semantic_contract"]
    normalized = contract["normalized_values"]
    parts: dict[str, str] = {
        "date": "tomorrow",
        "patient": "",
        "practitioner": "",
        "time": "",
        "duration": "",
    }
    practitioner = _practitioner_phrase(seed)
    if practitioner:
        parts["practitioner"] = practitioner
    if contract["patient_semantics"] != "omitted":
        parts["patient"] = _patient_phrase(seed)
    if "duration_minutes" in seed["required_evidence_keys"]:
        parts["duration"] = f"{normalized['duration_minutes']} mins"
    if "temporal_relation" in seed["required_evidence_keys"]:
        parts["time"] = _temporal_phrase(contract)
        temporal_values = seed["surface_evidence"].get("temporal_relation", [])
        if contract["entity_state"] == "corrected" and len(temporal_values) > 1:
            final_time = parts["time"]
            old_time = next(
                (value for value in temporal_values if value not in final_time),
                temporal_values[0],
            )
            parts["time"] = f"at {old_time}—sorry, {final_time}"
    if contract["intended_action"] == "status_change":
        parts["status"] = _status_value(contract)
    return parts


def _turns_for_dialogue_form(
    seed: dict[str, Any],
    utterance: str,
    *,
    prior_utterance: str | None = None,
) -> list[dict[str, Any]]:
    form = seed["semantic_contract"]["dialogue_form"]
    if form == "one_shot":
        texts = [utterance]
    elif form == "clarification":
        texts = [
            "I have a diary request, but the details may need clarifying.",
            utterance,
        ]
    elif form == "correction":
        if prior_utterance is None:
            raise ValueError(f"Missing correction prior for {seed['seed_id']}")
        texts = [prior_utterance, f"Correction—{utterance}"]
    elif form == "reversal":
        texts = [utterance, "Actually, stop there—leave the diary unchanged."]
    elif form == "ellipsis":
        texts = [utterance, "Same details—that one."]
    elif form == "anaphora":
        texts = [utterance, "Use that appointment for the request."]
    elif form == "repeated":
        texts = [utterance, utterance]
    elif form == "session_restart":
        texts = [utterance, f"Starting a fresh request—{utterance}"]
    else:
        raise ValueError(f"Unsupported dialogue form: {form!r}")
    return [
        {"turn": index, "speaker": "receptionist", "utterance": text}
        for index, text in enumerate(texts, start=1)
    ]


def _medium_utterance(
    seed: dict[str, Any], opener: str, p: dict[str, str], style: int
) -> str:
    action = seed["semantic_contract"]["intended_action"]
    if action == "create":
        options = (
            f"{opener}: book {p['patient']} with {p['practitioner']} {p['date']} {p['time']}; {p['duration']} appt, please.",
            f"{opener}—{p['patient']}, {p['date']} {p['time']}; book that {p['duration']} appt with {p['practitioner']}.",
            f"{opener}; appt for {p['patient']}: {p['duration']}, {p['practitioner']}, {p['date']} {p['time']}—book it, please.",
            f"{opener}, please—{p['date']} {p['time']}, {p['practitioner']}; book {p['patient']} for {p['duration']}.",
        )
        return options[style]
    if action == "move":
        options = (
            f"{opener}: {p['patient']} with {p['practitioner']}; move the appt to {p['date']}, {p['time']}.",
            f"{opener}—shift {p['patient']}'s {p['practitioner']} appt: {p['date']} {p['time']}.",
            f"{opener}; {p['date']} {p['time']} for {p['patient']} with {p['practitioner']}—move the appt there.",
            f"{opener}, please move {p['patient']}'s appt; {p['practitioner']}, {p['date']} {p['time']}.",
        )
        return options[style]
    if action == "resize":
        options = (
            f"{opener}: make {p['patient']}'s {p['date']} {p['time']} appt with {p['practitioner']} {p['duration']}.",
            f"{opener}—{p['duration']} for {p['patient']}'s appt; {p['practitioner']}, {p['date']} {p['time']}.",
            f"{opener}; resize the {p['date']} {p['time']} appt for {p['patient']} with {p['practitioner']} to {p['duration']}.",
            f"{opener}, {p['patient']} with {p['practitioner']}; {p['date']} {p['time']}, make that appt {p['duration']}.",
        )
        return options[style]
    if action == "cancel":
        options = (
            f"{opener}: {p['date']}, {p['time']}; cancel {p['patient']}'s appt with {p['practitioner']}, please.",
            f"{opener}—cancel the {p['date']} {p['time']} appt: {p['patient']} with {p['practitioner']}.",
            f"{opener}; {p['patient']}, {p['practitioner']}, {p['date']} {p['time']}—cancel that appt.",
            f"{opener}, please take out {p['patient']}'s appt; {p['date']} {p['time']}, {p['practitioner']}.",
        )
        return options[style]
    if action == "status_change":
        prefix = _status_prefix(seed["semantic_contract"])
        options = (
            f"{opener}: {prefix}{p['patient']}, {p['practitioner']}, {p['date']} {p['time']}; mark that appt {p['status']}.",
            f"{opener}—{prefix}set {p['patient']}'s {p['date']} {p['time']} appt with {p['practitioner']} to {p['status']}.",
            f"{opener}; {prefix}{p['date']} {p['time']}, {p['practitioner']}, {p['patient']}—status {p['status']}.",
            f"{opener}, {prefix}mark {p['patient']} {p['status']}; {p['practitioner']}, {p['date']} {p['time']}.",
        )
        return options[style]
    if action == "explain_schedule":
        prefix = _explain_prefix(seed["semantic_contract"])
        options = (
            f"{opener}: {prefix}can I get {p['practitioner']}'s diary rundown for {p['date']}, please?",
            f"{opener}—{prefix}what's {p['practitioner']}'s diary looking like {p['date']}?",
            f"{opener}; {prefix}{p['date']} for {p['practitioner']}—give me the diary rundown, please.",
            f"{opener}, {prefix}talk me through {p['practitioner']}'s {p['date']} diary, please.",
        )
        return options[style]
    raise ValueError(f"Unsupported action: {action!r}")


def _high_utterance(
    seed: dict[str, Any], opener: str, p: dict[str, str], style: int
) -> str:
    action = seed["semantic_contract"]["intended_action"]
    if action == "create":
        options = (
            f"{opener}—right, book—book this one / {p['date']} {p['time']} / {p['patient']} with {p['practitioner']} / {p['duration']} appt.",
            f"{opener}—uh, new appt / {p['patient']} / {p['duration']} / {p['date']} {p['time']} / with {p['practitioner']}—book that.",
            f"{opener}—pop—book an appt / {p['practitioner']} / {p['date']} {p['time']} / {p['patient']} / {p['duration']}.",
            f"{opener}—booking, sorry—booking / {p['duration']} / {p['patient']} / {p['practitioner']} / {p['date']} {p['time']}.",
        )
        return options[style]
    if action == "move":
        options = (
            f"{opener}—hold on, move—move this appt / {p['date']} {p['time']} / {p['practitioner']} / {p['patient']}.",
            f"{opener}—shift, uh, shift / {p['patient']} / {p['date']} {p['time']} / {p['practitioner']} appt.",
            f"{opener}—diary move—move / {p['practitioner']} / {p['patient']} / over to {p['date']} {p['time']}.",
            f"{opener}—move that one, sorry—move / {p['date']} {p['time']} / {p['patient']} / {p['practitioner']}.",
        )
        return options[style]
    if action == "resize":
        options = (
            f"{opener}—length change, uh / {p['date']} {p['time']} / {p['patient']}, {p['practitioner']} / {p['duration']} appt.",
            f"{opener}—resize—resize this one / {p['patient']} / {p['duration']} / {p['practitioner']} / {p['date']} {p['time']}.",
            f"{opener}—appt length, um / {p['practitioner']} / {p['date']} {p['time']} / {p['patient']} / make it {p['duration']}.",
            f"{opener}—make that—make the appt {p['duration']} / {p['patient']} / {p['date']} {p['time']} / {p['practitioner']}.",
        )
        return options[style]
    if action == "cancel":
        options = (
            f"{opener}—cancel—yep, cancel this diary line / {p['patient']} / {p['date']} {p['time']} / {p['practitioner']}.",
            f"{opener}—take out—cancel the appt / {p['date']} {p['time']} / {p['practitioner']} / {p['patient']}.",
            f"{opener}—cancel this one, uh / {p['practitioner']} / {p['patient']} / {p['date']} {p['time']}.",
            f"{opener}—diary cancel—cancel / {p['patient']} / with {p['practitioner']} / {p['date']} {p['time']}.",
        )
        return options[style]
    if action == "status_change":
        prefix = _status_prefix(seed["semantic_contract"])
        options = (
            f"{opener}—status one, uh / {prefix}{p['date']} {p['time']} / {p['practitioner']}, {p['patient']} / {p['status']}.",
            f"{opener}—mark—mark the status / {prefix}{p['patient']} / {p['status']} / {p['date']} {p['time']} / {p['practitioner']}.",
            f"{opener}—status update, um / {prefix}{p['practitioner']} / {p['date']} {p['time']} / {p['patient']} / {p['status']}.",
            f"{opener}—set this one—set status / {prefix}{p['status']} / {p['patient']} / {p['practitioner']} / {p['date']} {p['time']}.",
        )
        return options[style]
    if action == "explain_schedule":
        prefix = _explain_prefix(seed["semantic_contract"])
        options = (
            f"{opener}—quick diary check, um / {prefix}{p['date']} / {p['practitioner']} / give me the rundown.",
            f"{opener}—what's—what's the diary / {prefix}{p['practitioner']} / {p['date']} / talk me through it.",
            f"{opener}—rundown, uh / {prefix}{p['date']} / diary for {p['practitioner']} / what have we got.",
            f"{opener}—diary view—view only / {prefix}{p['practitioner']} / {p['date']} / run me through it.",
        )
        return options[style]
    raise ValueError(f"Unsupported action: {action!r}")


def _evidence_values(seed: dict[str, Any], dialogue_text: str) -> dict[str, str]:
    contract = seed["semantic_contract"]
    normalized = contract["normalized_values"]
    values: dict[str, str] = {}
    patient = _surface_value(seed, "patient") if "patient" in seed["required_evidence_keys"] else None
    practitioner = (
        _surface_value(seed, "practitioner")
        if "practitioner" in seed["required_evidence_keys"]
        else None
    )
    temporal = (
        _temporal_phrase(contract)
        if "temporal_relation" in seed["required_evidence_keys"]
        else None
    )
    for key in seed["required_evidence_keys"]:
        if key == "appointment_date":
            values[key] = "tomorrow"
        elif key == "patient" and patient:
            values[key] = patient
        elif key == "practitioner" and practitioner:
            values[key] = practitioner
        elif key == "duration_minutes":
            values[key] = f"{normalized['duration_minutes']} mins"
        elif key in {"earliest_time", "latest_time", "temporal_relation"} and temporal:
            values[key] = temporal
        else:
            raise ValueError(f"No generated evidence for {seed['seed_id']}:{key}")
        if values[key] not in dialogue_text:
            raise ValueError(
                f"Generated evidence not in utterance for {seed['seed_id']}:{key}"
            )
    return values


def _build_spans(
    seed: dict[str, Any], turns: list[dict[str, Any]]
) -> dict[str, list[dict[str, Any]]]:
    spans: dict[str, list[dict[str, Any]]] = {}
    dialogue_text = " ".join(turn["utterance"] for turn in turns)
    for key, text in _evidence_values(seed, dialogue_text).items():
        match: tuple[int, int] | None = None
        for turn_index in range(len(turns) - 1, -1, -1):
            start = turns[turn_index]["utterance"].rfind(text)
            if start >= 0:
                match = (turn_index, start)
                break
        if match is None:
            raise ValueError(f"Evidence text not found: {seed['seed_id']}:{key}")
        turn_index, start = match
        spans[key] = [
            {
                "turn_index": turn_index,
                "start": start,
                "end": start + len(text),
                "text": text,
            }
        ]
    return spans


def _operations(
    seed: dict[str, Any],
    variant_index: int,
    turns: list[dict[str, Any]],
) -> list[str]:
    operations = list(MEDIUM_OPERATIONS if variant_index == 1 else HIGH_OPERATIONS)
    contract = seed["semantic_contract"]
    if any("—sorry," in turn["utterance"] for turn in turns):
        operations.append("correction")
    dialogue_form = contract["dialogue_form"]
    if dialogue_form in {"correction", "reversal", "ellipsis", "anaphora"}:
        if dialogue_form not in operations:
            operations.append(dialogue_form)
    return operations


def build_candidates(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    seeds = manifest.get("seeds")
    if not isinstance(seeds, list) or len(seeds) != SEED_COUNT:
        raise ValueError(f"Seed manifest must contain exactly {SEED_COUNT} seeds")
    records: list[dict[str, Any]] = []
    for ordinal, seed in enumerate(seeds, start=1):
        expected_id = f"bernie_noise_seed_{ordinal:03d}"
        if seed.get("seed_id") != expected_id:
            raise ValueError(f"Unexpected seed order or ID: {seed.get('seed_id')!r}")
        parts = _semantic_parts(seed)
        opener = OPENERS[(ordinal - 1) % len(OPENERS)]
        style = (ordinal - 1) % 4
        for variant_index in (1, 2):
            utterance = (
                _medium_utterance(seed, opener, parts, style)
                if variant_index == 1
                else _high_utterance(seed, opener, parts, style)
            )
            prior_utterance = None
            if seed["semantic_contract"]["dialogue_form"] == "correction":
                prior_parts = dict(parts)
                prior_parts["practitioner"] = "a doctor"
                prior_utterance = (
                    _medium_utterance(seed, opener, prior_parts, style)
                    if variant_index == 1
                    else _high_utterance(seed, opener, prior_parts, style)
                )
            turns = _turns_for_dialogue_form(
                seed,
                utterance,
                prior_utterance=prior_utterance,
            )
            records.append(
                {
                    "schema_version": SCHEMA_VERSION,
                    "candidate_id": f"sol_{expected_id}_{variant_index:02d}",
                    "source_seed_id": expected_id,
                    "source_seed_hash": seed["seed_hash"],
                    "generator_identity": dict(GENERATOR_IDENTITY),
                    "variant_index": variant_index,
                    "noise_level": "medium" if variant_index == 1 else "high",
                    "noise_operations": _operations(seed, variant_index, turns),
                    "dialogue_turns": turns,
                    "evidence_spans": _build_spans(seed, turns),
                    "semantic_change": "none",
                    "provenance": "silver",
                    "adjudication": "pending",
                    "authority_grant": dict(AUTHORITY_GRANT),
                }
            )
    return records


def _validate_span(
    candidate_id: str,
    turns: list[dict[str, Any]],
    key: str,
    span: Any,
) -> str | None:
    if not isinstance(span, dict) or set(span) != {
        "turn_index",
        "start",
        "end",
        "text",
    }:
        return f"{candidate_id}: malformed span for {key}"
    turn_index = span.get("turn_index")
    start = span.get("start")
    end = span.get("end")
    text = span.get("text")
    if (
        not isinstance(turn_index, int)
        or not 0 <= turn_index < len(turns)
        or not isinstance(start, int)
        or not isinstance(end, int)
        or not isinstance(text, str)
        or start < 0
        or end <= start
    ):
        return f"{candidate_id}: invalid span coordinates for {key}"
    utterance = turns[turn_index]["utterance"]
    if end > len(utterance) or utterance[start:end] != text:
        return f"{candidate_id}: span does not slice utterance for {key}"
    return None


def validate_candidates(
    records: list[dict[str, Any]], manifest: dict[str, Any]
) -> list[str]:
    errors: list[str] = []
    seeds = {seed["seed_id"]: seed for seed in manifest.get("seeds", [])}
    if len(records) != CANDIDATE_COUNT:
        errors.append(f"candidate count must be {CANDIDATE_COUNT}, got {len(records)}")
    if len(seeds) != SEED_COUNT:
        errors.append(f"seed count must be {SEED_COUNT}, got {len(seeds)}")

    ids: set[str] = set()
    payloads: set[str] = set()
    per_seed: Counter[str] = Counter()
    variants: dict[str, set[int]] = {}
    for record in records:
        candidate_id = record.get("candidate_id")
        if not isinstance(candidate_id, str):
            errors.append("candidate_id must be a string")
            continue
        if set(record) != TOP_LEVEL_FIELDS:
            errors.append(f"{candidate_id}: top-level schema mismatch")
        if candidate_id in ids:
            errors.append(f"duplicate candidate_id: {candidate_id}")
        ids.add(candidate_id)
        seed_id = record.get("source_seed_id")
        seed = seeds.get(seed_id)
        if seed is None:
            errors.append(f"{candidate_id}: unknown source seed {seed_id!r}")
            continue
        per_seed[seed_id] += 1
        variant = record.get("variant_index")
        variants.setdefault(seed_id, set()).add(variant)
        if record.get("source_seed_hash") != seed.get("seed_hash"):
            errors.append(f"{candidate_id}: source seed hash mismatch")
        if record.get("schema_version") != SCHEMA_VERSION:
            errors.append(f"{candidate_id}: schema version mismatch")
        if record.get("generator_identity") != GENERATOR_IDENTITY:
            errors.append(
                f"{candidate_id}: generator identity must be {GENERATOR_SLUG}"
            )
        expected_level = "medium" if variant == 1 else "high" if variant == 2 else None
        if record.get("noise_level") != expected_level:
            errors.append(f"{candidate_id}: noise level/variant mismatch")
        operations = record.get("noise_operations")
        minimum = 2 if variant == 1 else 3
        if (
            not isinstance(operations, list)
            or len(operations) < minimum
            or len(operations) != len(set(operations))
            or any(operation not in ALLOWED_NOISE_OPERATIONS for operation in operations)
        ):
            errors.append(f"{candidate_id}: invalid noise operations")
        correction_allowed = any(
            seed["semantic_contract"][field] == "corrected"
            for field in ("entity_state", "patient_semantics", "practitioner_semantics")
        )
        if "correction" in (operations or []) and not correction_allowed:
            errors.append(f"{candidate_id}: correction not authorized by seed")
        reversal_allowed = seed["semantic_contract"]["dialogue_form"] == "reversal"
        if "reversal" in (operations or []) and not reversal_allowed:
            errors.append(f"{candidate_id}: reversal is not authorized by seed")

        turns = record.get("dialogue_turns")
        if not isinstance(turns, list) or not turns:
            errors.append(f"{candidate_id}: dialogue turns must be non-empty")
            continue
        dialogue_form = seed["semantic_contract"]["dialogue_form"]
        if dialogue_form == "one_shot" and len(turns) != 1:
            errors.append(f"{candidate_id}: one_shot requires one turn")
        elif dialogue_form != "one_shot" and len(turns) < 2:
            errors.append(f"{candidate_id}: {dialogue_form} requires two turns")
        for index, turn in enumerate(turns, start=1):
            if set(turn) != {"turn", "speaker", "utterance"}:
                errors.append(f"{candidate_id}: turn schema mismatch")
                continue
            if turn.get("turn") != index or turn.get("speaker") != "receptionist":
                errors.append(f"{candidate_id}: invalid turn number or speaker")
            utterance = turn.get("utterance")
            if not isinstance(utterance, str) or not utterance.strip():
                errors.append(f"{candidate_id}: empty utterance")
                continue
            if FORBIDDEN_CONTENT.search(utterance) or any(
                pattern.search(utterance) for pattern in CONTACT_PATTERNS
            ):
                errors.append(f"{candidate_id}: forbidden or identifying content")
        payload = _canonical_json(turns)
        if payload in payloads:
            errors.append(f"duplicate dialogue payload: {candidate_id}")
        payloads.add(payload)

        evidence = record.get("evidence_spans")
        required = set(seed["required_evidence_keys"])
        if not isinstance(evidence, dict) or set(evidence) != required:
            errors.append(f"{candidate_id}: evidence keys do not match seed")
        else:
            for key, spans in evidence.items():
                if not isinstance(spans, list) or not spans:
                    errors.append(f"{candidate_id}: empty evidence spans for {key}")
                    continue
                for span in spans:
                    error = _validate_span(candidate_id, turns, key, span)
                    if error:
                        errors.append(error)
        if record.get("semantic_change") != "none":
            errors.append(f"{candidate_id}: semantic_change must be none")
        if record.get("provenance") != "silver":
            errors.append(f"{candidate_id}: provenance must be silver")
        if record.get("adjudication") != "pending":
            errors.append(f"{candidate_id}: adjudication must be pending")
        if record.get("authority_grant") != AUTHORITY_GRANT:
            errors.append(f"{candidate_id}: authority grant must be all false")

    for seed_id in sorted(seeds):
        if per_seed[seed_id] != 2:
            errors.append(f"{seed_id}: expected two candidates")
        if variants.get(seed_id) != {1, 2}:
            errors.append(f"{seed_id}: expected medium/high variants 1 and 2")
    return errors


def _read_output() -> tuple[list[dict[str, Any]], list[str]]:
    errors: list[str] = []
    if not OUTPUT_PATH.is_file():
        return [], [f"missing output: {OUTPUT_PATH}"]
    records: list[dict[str, Any]] = []
    lines = OUTPUT_PATH.read_text(encoding="utf-8").splitlines()
    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            errors.append(f"blank JSONL line: {line_number}")
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"invalid JSONL line {line_number}: {exc}")
            continue
        if not isinstance(record, dict):
            errors.append(f"JSONL line {line_number} is not an object")
            continue
        if line != _canonical_json(record):
            errors.append(f"JSONL line {line_number} is not canonical")
        records.append(record)
    return records, errors


def write_candidates() -> tuple[list[dict[str, Any]], str]:
    manifest = _load_manifest()
    records = build_candidates(manifest)
    errors = validate_candidates(records, manifest)
    if errors:
        raise RuntimeError("\n".join(errors))
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        _canonical_jsonl(records),
        encoding="utf-8",
        newline="\n",
    )
    return records, _candidate_sha256(records)


def check_candidates() -> tuple[list[str], str | None]:
    manifest = _load_manifest()
    expected = build_candidates(manifest)
    records, errors = _read_output()
    errors.extend(validate_candidates(records, manifest))
    if records != expected:
        errors.append("output is not the deterministic Codex generation")
    return errors, _candidate_sha256(records) if records else None


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write:
        records, digest = write_candidates()
        print(f"wrote {len(records)} candidates to {OUTPUT_PATH}")
        print(f"CANDIDATE_SHA256: {digest}")
        return 0
    errors, digest = check_candidates()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"validated {CANDIDATE_COUNT} candidates from {SEED_COUNT} seeds")
    print(f"GENERATOR_IDENTITY: {GENERATOR_SLUG}")
    print(f"CANDIDATE_SHA256: {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
