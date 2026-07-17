"""Deterministic candidate generation and admission for synthetic Silver v2.

Candidates are generated only from the independently accepted dialogue-free
v2 anchors. Admission is based on mechanical and surfaced-coherence rules; the
product interpreter, replay, and scorer are deliberately not imported.
"""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
from datetime import date
import hashlib
import json
from pathlib import Path
import re
from typing import Any, Iterable

from app.services.bernie.synthetic_noise_corpus import ALLOWED_NOISE_OPERATIONS
from app.services.bernie.synthetic_noise_v2 import (
    ACTIONS_V2,
    ANCHOR_COUNT_V2,
    DEFAULT_SEED_PATH_V2,
    FORMS_V2,
    build_v2_anchor_manifest,
    validate_v2_anchor_manifest,
)


CANDIDATE_SCHEMA_VERSION_V2 = "emr4.bernie.synthetic_noise_candidate.v2"
ADMISSION_SCHEMA_VERSION_V2 = "emr4.bernie.synthetic_noise_admission.v2"
CANDIDATE_COUNT_V2 = ANCHOR_COUNT_V2 * 2
DEFAULT_CANDIDATE_PATH_V2 = Path(
    "tests/fixtures/bernie_synthetic_noise/candidates_sol_v2.jsonl"
)
DEFAULT_ADMISSION_PATH_V2 = Path(
    "tests/fixtures/bernie_synthetic_noise/admission_v2.json"
)
GENERATOR_IDENTITY_V2 = {
    "provider_id": "openai",
    "model_id": "gpt-sol-v2-deterministic",
    "lane_id": "synthetic-silver-v2-sol",
}
AUTHORITY_ALL_FALSE = {
    "provider_write": False,
    "diary_write": False,
    "confirmation": False,
    "override_authority": False,
}
_TOP_LEVEL_KEYS = {
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
_CONTACT_OR_CLINICAL = re.compile(
    r"(?:\b\d{8,}\b|@|https?://|\b(?:diagnos|symptom|medication|medicare|dob)\w*\b)",
    re.I,
)


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def _sha256(value: Any) -> str:
    return "sha256:" + hashlib.sha256(
        _canonical_json(value).encode("utf-8")
    ).hexdigest()


def candidate_records_hash(records: list[dict[str, Any]]) -> str:
    return _sha256(records)


def candidate_file_hash(records: list[dict[str, Any]]) -> str:
    payload = "".join(_canonical_json(record) + "\n" for record in records)
    return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _format_time(value: str) -> str:
    hour, minute = (int(part) for part in value.split(":"))
    suffix = "am" if hour < 12 else "pm"
    display_hour = hour % 12 or 12
    return f"{display_hour}{suffix}" if minute == 0 else f"{display_hour}:{minute:02d}{suffix}"


def _date_phrase(contract: dict[str, Any]) -> str:
    reference = date.fromisoformat(contract["reference_date"])
    appointment = date.fromisoformat(contract["normalized_values"]["appointment_date"])
    delta = (appointment - reference).days
    if delta == 0:
        return "today"
    if delta == 1:
        return "tomorrow"
    return appointment.strftime("%d %B %Y").lstrip("0")


def _time_phrase(contract: dict[str, Any]) -> str:
    relation = contract["temporal_relation"]
    earliest = contract.get("earliest_time")
    latest = contract.get("latest_time")
    if relation == "exact" and earliest:
        return _format_time(earliest)
    if relation == "not_before" and earliest:
        return f"{_format_time(earliest)} or later"
    if relation == "not_after" and latest:
        return f"by {_format_time(latest)}"
    if relation == "approximate" and earliest and latest:
        midpoint_minutes = (
            (int(earliest[:2]) * 60 + int(earliest[3:]))
            + (int(latest[:2]) * 60 + int(latest[3:]))
        ) // 2
        return f"around {_format_time(f'{midpoint_minutes // 60:02d}:{midpoint_minutes % 60:02d}')}"
    if relation == "interval" and earliest and latest:
        return f"between {_format_time(earliest)} and {_format_time(latest)}"
    return "any time"


def _entity_surfaces(anchor: dict[str, Any]) -> tuple[str | None, str]:
    contract = anchor["semantic_contract"]
    form_contract = anchor["dialogue_form_contract"]
    if contract["patient_semantics"] == "omitted":
        patient = None
    elif contract["patient_semantics"] == "ambiguous":
        patient = "either Margaret Thompson or Robert Johnson"
    else:
        patient = "Margaret Thompson"

    if contract["practitioner_semantics"] == "ambiguous":
        practitioner = "either Dr Shera or Dr Patel"
    else:
        practitioner = form_contract.get("final_value") or "Dr Shera"
    return patient, practitioner


def _operational_opener(anchor: dict[str, Any]) -> str:
    ordinal = int(anchor["seed_id"].rsplit("_", 1)[-1]) - 1
    prefixes = (
        "Quick", "Routine", "Morning", "Afternoon", "Front-desk", "Diary",
        "Booking", "Practice", "Reception", "Follow-up", "Same-day", "Standard",
    )
    suffixes = (
        "note", "task", "request", "item", "update", "check", "instruction", "job",
    )
    return f"{prefixes[ordinal // len(suffixes)]} {suffixes[ordinal % len(suffixes)]}"


def _request_parts(
    anchor: dict[str, Any], *, high_noise: bool
) -> tuple[str, dict[str, str]]:
    contract = anchor["semantic_contract"]
    action = contract["intended_action"]
    patient, practitioner = _entity_surfaces(anchor)
    appointment_date = _date_phrase(contract)
    temporal = _time_phrase(contract)
    duration = f"{contract.get('duration_minutes') or 15} mins"
    status = "arrived"

    action_phrases = {
        "create": "book an appt",
        "move": "move the appt",
        "resize": "resize the appt",
        "cancel": "cancel the appt",
        "status_change": "mark the appt as arrived",
        "explain_schedule": "show the diary schedule",
    }
    action_phrase = action_phrases[action]
    opener = _operational_opener(anchor)

    if action == "explain_schedule":
        details = f"for {practitioner} {appointment_date}, {temporal}"
    elif action == "resize":
        details = (
            f"for {patient} with {practitioner} {appointment_date} at {temporal}; "
            f"make it {duration}"
        )
    elif action == "status_change":
        details = f"for {patient} with {practitioner} {appointment_date} {temporal}"
    elif action == "create":
        details = (
            f"for {patient} with {practitioner} {appointment_date} at {temporal} "
            f"for {duration}"
        )
    else:
        details = f"for {patient} with {practitioner} {appointment_date} at {temporal}"

    request = (
        f"{opener}—right, uh, {details}; {action_phrase}."
        if high_noise
        else f"{opener}: {details}; please {action_phrase}."
    )
    evidence = {
        "intended_action": action_phrase,
        "appointment_date": appointment_date,
        "temporal_relation": temporal,
        "practitioner": practitioner,
        "duration_minutes": duration,
        "status": status,
    }
    if patient is not None:
        evidence["patient"] = patient
    return request, evidence


def _context_text(anchor: dict[str, Any], evidence: dict[str, str]) -> str:
    action = anchor["semantic_contract"]["intended_action"]
    patient = evidence.get("patient")
    subject = "Diary reference" if action == "explain_schedule" else f"Appointment reference for {patient}"
    pieces = [subject, evidence["practitioner"], evidence["appointment_date"]]
    if "temporal_relation" in anchor["required_evidence_keys"]:
        pieces.append(evidence["temporal_relation"])
    if "duration_minutes" in anchor["required_evidence_keys"]:
        pieces.append(evidence["duration_minutes"])
    if "status" in anchor["required_evidence_keys"]:
        pieces.append(evidence["status"])
    return f"{_operational_opener(anchor)}: " + "; ".join(pieces) + "."


def _turns_and_evidence(
    anchor: dict[str, Any], *, variant_index: int
) -> tuple[list[dict[str, Any]], dict[str, tuple[int, str]]]:
    high = variant_index == 2
    request, evidence = _request_parts(anchor, high_noise=high)
    form = anchor["dialogue_form_contract"]["dialogue_form"]
    action = anchor["semantic_contract"]["intended_action"]

    if form == "one_shot":
        utterances = [request]
        locations = {key: (0, value) for key, value in evidence.items()}
    elif form == "clarification":
        target = anchor["dialogue_form_contract"]["ambiguity_target"]
        marker = f"The {target} is unclear—ask me to clarify before doing anything."
        utterances = [request, marker]
        locations = {key: (0, value) for key, value in evidence.items()}
        locations["dialogue_transition"] = (1, "ask me to clarify")
    elif form == "correction":
        prior = request.replace("Dr Shera", "Dr Patel")
        final = f"Correction—replace Dr Patel with Dr Shera. {request}"
        utterances = [prior, final]
        locations = {key: (1, value) for key, value in evidence.items()}
        locations["dialogue_transition"] = (1, "Correction")
    elif form == "reversal":
        marker = f"Actually, disregard that {action.replace('_', ' ')} request; do not carry it out."
        utterances = [request, marker]
        locations = {key: (0, value) for key, value in evidence.items()}
        locations["dialogue_transition"] = (1, "disregard that")
    elif form in {"ellipsis", "anaphora"}:
        context = _context_text(anchor, evidence)
        if high:
            context += " Dictated in short fragments."
        referent = "that diary request" if action == "explain_schedule" else "that appointment"
        marker = "Use that" if form == "anaphora" else "With those details"
        prefix = "Uh—" if high else ""
        final = f"{prefix}{marker}, {evidence['intended_action']} {referent}."
        utterances = [context, final]
        locations = {
            key: (0, value)
            for key, value in evidence.items()
            if key != "intended_action"
        }
        locations["intended_action"] = (1, evidence["intended_action"])
        locations["dialogue_transition"] = (1, marker)
    elif form == "repeated_request":
        utterances = [request, request]
        locations = {key: (1, value) for key, value in evidence.items()}
        locations["dialogue_transition"] = (1, evidence["intended_action"])
    elif form == "session_restart":
        marker = "Start over—abandon the earlier draft."
        utterances = ["I began a diary request, but abandon that incomplete draft.", f"{marker} {request}"]
        locations = {key: (1, value) for key, value in evidence.items()}
        locations["dialogue_transition"] = (1, "Start over")
    else:
        raise ValueError(f"unsupported v2 dialogue form: {form}")

    turns = [
        {"turn": index + 1, "speaker": "receptionist", "utterance": utterance}
        for index, utterance in enumerate(utterances)
    ]
    return turns, locations


def _spans(
    anchor: dict[str, Any],
    turns: list[dict[str, Any]],
    locations: dict[str, tuple[int, str]],
) -> dict[str, list[dict[str, Any]]]:
    result: dict[str, list[dict[str, Any]]] = {}
    for key in anchor["required_evidence_keys"]:
        turn_index, text = locations[key]
        utterance = turns[turn_index]["utterance"]
        start = utterance.rfind(text)
        if start < 0:
            raise ValueError(f"missing generated evidence {anchor['seed_id']}:{key}")
        result[key] = [
            {
                "turn_index": turn_index,
                "start": start,
                "end": start + len(text),
                "text": text,
            }
        ]
    return result


def _noise_operations(anchor: dict[str, Any], variant_index: int) -> list[str]:
    operations = (
        ["staff_shorthand", "reordered_slots"]
        if variant_index == 1
        else ["speech_disfluency", "dictation_artifact", "reordered_slots"]
    )
    form = anchor["dialogue_form_contract"]["dialogue_form"]
    if form in {"correction", "reversal", "ellipsis", "anaphora"}:
        operations.append(form)
    return operations


def build_v2_candidates(
    manifest: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    manifest = manifest or build_v2_anchor_manifest()
    errors = validate_v2_anchor_manifest(manifest)
    if errors:
        raise ValueError("invalid v2 anchors: " + "; ".join(errors))
    records: list[dict[str, Any]] = []
    for anchor in manifest["anchors"]:
        for variant_index in (1, 2):
            turns, locations = _turns_and_evidence(anchor, variant_index=variant_index)
            records.append(
                {
                    "schema_version": CANDIDATE_SCHEMA_VERSION_V2,
                    "candidate_id": f"sol_v2_{anchor['seed_id']}_{variant_index:02d}",
                    "source_seed_id": anchor["seed_id"],
                    "source_seed_hash": anchor["seed_hash"],
                    "generator_identity": dict(GENERATOR_IDENTITY_V2),
                    "variant_index": variant_index,
                    "noise_level": "medium" if variant_index == 1 else "high",
                    "noise_operations": _noise_operations(anchor, variant_index),
                    "dialogue_turns": turns,
                    "evidence_spans": _spans(anchor, turns, locations),
                    "semantic_change": "none",
                    "provenance": "silver",
                    "adjudication": "pending",
                    "authority_grant": dict(AUTHORITY_ALL_FALSE),
                }
            )
    return records


def _dialogue(record: dict[str, Any]) -> list[str]:
    return [turn["utterance"] for turn in record.get("dialogue_turns", [])]


def validate_v2_candidates(
    records: list[dict[str, Any]], manifest: dict[str, Any]
) -> list[str]:
    errors: list[str] = []
    anchors = {anchor["seed_id"]: anchor for anchor in manifest["anchors"]}
    if len(records) != CANDIDATE_COUNT_V2:
        errors.append(f"candidate count must be {CANDIDATE_COUNT_V2}")
    seen_ids: set[str] = set()
    seen_dialogues: set[str] = set()
    per_seed: Counter[str] = Counter()
    per_action: Counter[str] = Counter()
    per_form: Counter[str] = Counter()

    for record in records:
        candidate_id = record.get("candidate_id")
        if set(record) != _TOP_LEVEL_KEYS:
            errors.append(f"{candidate_id}: candidate schema mismatch")
        if not isinstance(candidate_id, str) or candidate_id in seen_ids:
            errors.append(f"{candidate_id}: duplicate or invalid candidate ID")
        else:
            seen_ids.add(candidate_id)
        anchor = anchors.get(record.get("source_seed_id"))
        if anchor is None:
            errors.append(f"{candidate_id}: unknown source seed")
            continue
        per_seed[anchor["seed_id"]] += 1
        action = anchor["semantic_contract"]["intended_action"]
        form = anchor["dialogue_form_contract"]["dialogue_form"]
        per_action[action] += 1
        per_form[form] += 1
        variant = record.get("variant_index")
        expected_id = f"sol_v2_{anchor['seed_id']}_{variant:02d}" if variant in {1, 2} else None
        if candidate_id != expected_id:
            errors.append(f"{candidate_id}: candidate ID/variant mismatch")
        if record.get("source_seed_hash") != anchor["seed_hash"]:
            errors.append(f"{candidate_id}: source seed hash mismatch")
        if record.get("schema_version") != CANDIDATE_SCHEMA_VERSION_V2:
            errors.append(f"{candidate_id}: schema version mismatch")
        if record.get("generator_identity") != GENERATOR_IDENTITY_V2:
            errors.append(f"{candidate_id}: generator identity mismatch")
        expected_level = "medium" if variant == 1 else "high" if variant == 2 else None
        if record.get("noise_level") != expected_level:
            errors.append(f"{candidate_id}: noise level mismatch")
        operations = record.get("noise_operations")
        minimum = 2 if variant == 1 else 3
        if (
            not isinstance(operations, list)
            or len(operations) < minimum
            or len(operations) != len(set(operations))
            or not set(operations).issubset(ALLOWED_NOISE_OPERATIONS)
        ):
            errors.append(f"{candidate_id}: invalid noise operations")

        turns = record.get("dialogue_turns")
        if not isinstance(turns, list) or len(turns) < anchor["dialogue_form_contract"]["minimum_turns"]:
            errors.append(f"{candidate_id}: insufficient dialogue turns")
            turns = []
        utterances: list[str] = []
        for index, turn in enumerate(turns):
            if not isinstance(turn, dict) or set(turn) != {"turn", "speaker", "utterance"}:
                errors.append(f"{candidate_id}: invalid turn schema")
                continue
            if turn["turn"] != index + 1 or turn["speaker"] != "receptionist":
                errors.append(f"{candidate_id}: invalid turn identity")
            if not isinstance(turn["utterance"], str) or not turn["utterance"].strip():
                errors.append(f"{candidate_id}: empty utterance")
            else:
                utterances.append(turn["utterance"])
        dialogue_key = _canonical_json(utterances)
        if dialogue_key in seen_dialogues:
            errors.append(f"{candidate_id}: duplicate dialogue")
        seen_dialogues.add(dialogue_key)
        if _CONTACT_OR_CLINICAL.search(" ".join(utterances)):
            errors.append(f"{candidate_id}: identifying or clinical content")

        spans = record.get("evidence_spans")
        required = set(anchor["required_evidence_keys"])
        if not isinstance(spans, dict) or set(spans) != required:
            errors.append(f"{candidate_id}: evidence keys mismatch")
            spans = {}
        for key, items in spans.items():
            if not isinstance(items, list) or len(items) != 1:
                errors.append(f"{candidate_id}: invalid evidence list for {key}")
                continue
            span = items[0]
            if not isinstance(span, dict) or set(span) != {"turn_index", "start", "end", "text"}:
                errors.append(f"{candidate_id}: invalid evidence span for {key}")
                continue
            ti, start, end, text = (
                span.get("turn_index"), span.get("start"), span.get("end"), span.get("text")
            )
            if (
                not isinstance(ti, int)
                or not 0 <= ti < len(utterances)
                or not isinstance(start, int)
                or not isinstance(end, int)
                or not isinstance(text, str)
                or not 0 <= start < end <= len(utterances[ti])
                or utterances[ti][start:end] != text
            ):
                errors.append(f"{candidate_id}: evidence span mismatch for {key}")

        lowered = " ".join(utterances).lower()
        if form == "one_shot" and len(utterances) != 1:
            errors.append(f"{candidate_id}: one-shot must have one turn")
        if form == "clarification" and "ask me to clarify" not in lowered:
            errors.append(f"{candidate_id}: clarification not surfaced")
        if form == "correction" and not all(
            token.lower() in lowered for token in ("Correction", "Dr Patel", "Dr Shera", "replace")
        ):
            errors.append(f"{candidate_id}: correction replacement not surfaced")
        if form == "reversal" and not all(
            token in lowered for token in ("disregard that", "do not carry it out")
        ):
            errors.append(f"{candidate_id}: whole-action reversal not surfaced")
        if form in {"ellipsis", "anaphora"} and len(utterances) < 2:
            errors.append(f"{candidate_id}: local recovery lacks antecedent")
        if form == "repeated_request" and (
            len(utterances) != 2 or utterances[0] != utterances[1]
        ):
            errors.append(f"{candidate_id}: repeated request is not exact")
        if form == "session_restart" and "start over" not in lowered:
            errors.append(f"{candidate_id}: session restart not surfaced")
        if record.get("semantic_change") != "none":
            errors.append(f"{candidate_id}: semantic change must be none")
        if record.get("provenance") != "silver" or record.get("adjudication") != "pending":
            errors.append(f"{candidate_id}: invalid evidence tier")
        if record.get("authority_grant") != AUTHORITY_ALL_FALSE:
            errors.append(f"{candidate_id}: authority grant must be false")

    for anchor_id, count in per_seed.items():
        if count != 2:
            errors.append(f"{anchor_id}: expected two candidates")
    if set(per_seed) != set(anchors):
        errors.append("candidate population does not cover every v2 anchor")
    for action in ACTIONS_V2:
        if per_action[action] != 32:
            errors.append(f"{action}: expected 32 candidates")
    for form in FORMS_V2:
        if per_form[form] != 24:
            errors.append(f"{form}: expected 24 candidates")
    return errors


def build_v2_admission(
    records: list[dict[str, Any]], manifest: dict[str, Any]
) -> dict[str, Any]:
    errors = validate_v2_candidates(records, manifest)
    if errors:
        raise ValueError("invalid v2 candidates: " + "; ".join(errors))
    ids = sorted(record["candidate_id"] for record in records)
    without_hash = {
        "schema_version": ADMISSION_SCHEMA_VERSION_V2,
        "decision": "v2_admission_pass",
        "anchor_manifest_hash": manifest["manifest_hash"],
        "candidate_path": DEFAULT_CANDIDATE_PATH_V2.as_posix(),
        "candidate_count": len(records),
        "accepted_count": len(records),
        "quarantine_count": 0,
        "rejected_count": 0,
        "canonical_candidate_hash": candidate_records_hash(records),
        "file_payload_hash": candidate_file_hash(records),
        "accepted_candidate_ids": ids,
        "accepted_selection_hash": _sha256(ids),
        "evidence_tier": "silver",
        "protected_holdout_access": False,
        "historical_diary_access": False,
        "external_corpus_access": False,
        "product_parser_used_for_admission": False,
        "authority_grant": dict(AUTHORITY_ALL_FALSE),
    }
    return {**without_hash, "admission_hash": _sha256(without_hash)}


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def write_jsonl(path: Path, records: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(_canonical_json(record) + "\n" for record in records),
        encoding="utf-8",
        newline="\n",
    )


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def build_v2_candidate_artifacts() -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, Any]]:
    manifest = build_v2_anchor_manifest()
    committed = json.loads(DEFAULT_SEED_PATH_V2.read_text(encoding="utf-8"))
    if manifest != committed:
        raise ValueError("committed v2 anchors do not regenerate exactly")
    records = build_v2_candidates(manifest)
    admission = build_v2_admission(records, manifest)
    return manifest, records, admission


def check_v2_candidate_artifacts() -> list[str]:
    errors: list[str] = []
    manifest, expected, expected_admission = build_v2_candidate_artifacts()
    if not DEFAULT_CANDIDATE_PATH_V2.is_file():
        return ["missing committed v2 candidate file"]
    actual = load_jsonl(DEFAULT_CANDIDATE_PATH_V2)
    errors.extend(validate_v2_candidates(actual, manifest))
    if actual != expected:
        errors.append("committed v2 candidates do not regenerate exactly")
    if not DEFAULT_ADMISSION_PATH_V2.is_file():
        errors.append("missing committed v2 admission")
    else:
        admission = json.loads(DEFAULT_ADMISSION_PATH_V2.read_text(encoding="utf-8"))
        if admission != expected_admission:
            errors.append("committed v2 admission does not regenerate exactly")
    return errors


__all__ = [
    "ADMISSION_SCHEMA_VERSION_V2",
    "CANDIDATE_COUNT_V2",
    "CANDIDATE_SCHEMA_VERSION_V2",
    "DEFAULT_ADMISSION_PATH_V2",
    "DEFAULT_CANDIDATE_PATH_V2",
    "GENERATOR_IDENTITY_V2",
    "build_v2_admission",
    "build_v2_candidate_artifacts",
    "build_v2_candidates",
    "candidate_file_hash",
    "candidate_records_hash",
    "check_v2_candidate_artifacts",
    "load_jsonl",
    "validate_v2_candidates",
    "write_json",
    "write_jsonl",
]
