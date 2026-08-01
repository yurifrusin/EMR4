"""Pure contracts for the bounded Reception One Vertex design work cell."""

from __future__ import annotations

import json
from pathlib import Path
import re
from typing import Any, Mapping

from scripts import ariadne_vertex_sydney_gemini_25_contracts as base


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_ROOT = (
    ROOT / "orchestration" / "continuity" / "reception-one-visual-synthesis"
)
POLICY_PATH = ARTIFACT_ROOT / "broker-policy.json"
CELL_REQUEST_PATH = ARTIFACT_ROOT / "occupied-cell-request.json"
RELEASE_SCHEMA_PATH = ARTIFACT_ROOT / "design-candidate.schema.json"

POLICY_ID = "reception-one-visual-synthesis-vertex-sydney-v1"
PROTOCOL_VERSION = "ariadne.reception_one_visual_synthesis_work_cell.v1"
TASK_TYPE = "authored_synthetic_scheduling_workspace_design"

ContractError = base.ContractError
canonical_bytes = base.canonical_bytes
canonical_hash = base.canonical_hash
bytes_hash = base.bytes_hash
load_object = base.load_object
extract_provider_draft = base.extract_provider_draft
sanitize_provider_error = base.sanitize_provider_error
audit_event = base.audit_event
validate_audit_chain = base.validate_audit_chain

RELEASE_FIELDS = [
    "design_thesis",
    "visual_direction",
    "composition",
    "density",
    "typography",
    "palette",
    "priority_order",
    "responsive_strategy",
    "state_treatments",
    "interaction_recommendations",
    "risk_ids",
    "evidence_ids",
    "authority_class",
]
EVIDENCE = {
    "authority_boundary": (
        "The fictional workspace may present answers, selections and proposals "
        "but never commits scheduling state."
    ),
    "one_source": (
        "Every focused view remains a temporary projection of one fictional "
        "authoritative schedule."
    ),
    "scope_visible": (
        "Scope, omissions, freshness and the route back remain visible in every "
        "focused view."
    ),
    "state_distinct": (
        "Answer, selection, proposal, notice, block and receipt require distinct "
        "plain-language states."
    ),
    "tablet_primary": (
        "Landscape and portrait tablet layouts are first-class workspaces, not "
        "compressed desktop screens."
    ),
    "quiet_change": (
        "A committed change uses restrained, nonmodal attention and fresh "
        "reconciliation."
    ),
    "privacy_resume": (
        "Sensitive display content can be masked immediately and resumption "
        "requires refreshed state."
    ),
    "ordinary_escape": (
        "An ordinary schedule view remains an immediate and reversible escape."
    ),
}
VISUAL_DIRECTIONS = {
    "editorial_clinical",
    "quiet_operations",
    "warm_institutional",
}
COMPOSITIONS = {
    "conversation_rail_plus_projection_canvas",
    "command_bar_over_projection_canvas",
    "balanced_split_workspace",
}
DENSITIES = {"restrained", "balanced", "compact"}
TYPOGRAPHIES = {
    "serif_wordmark_humanist_sans_ui",
    "humanist_sans_with_mono_metadata",
    "all_humanist_sans",
}
PALETTES = {
    "paper_ink_eucalyptus",
    "warm_white_navy_ochre",
    "white_charcoal_cobalt",
}
PRIORITY_ORDER = [
    "scope",
    "state",
    "projection",
    "primary_action",
    "history",
    "ordinary_diary",
]
RESPONSIVE_VALUES = {
    "tablet_landscape": {
        "rail_canvas",
        "balanced_split",
    },
    "tablet_portrait": {
        "stacked_composer_scope_canvas",
        "compact_header_then_canvas",
    },
    "phone": {
        "single_column_sequential",
        "single_column_cards",
    },
}
STATE_TREATMENTS = {
    "answer": "quiet",
    "selection": "accent",
    "proposal": "accent",
    "notice": "warning",
    "blocked": "warning",
    "receipt": "success",
}
RISK_IDS = {
    "dense_metadata_competes_with_task",
    "ordinary_diary_escape_becomes_secondary",
    "phone_comparison_loses_alignment",
    "proposal_state_could_resemble_commitment",
    "quiet_notice_becomes_invisible",
    "scope_ribbon_wraps_poorly",
}
AUTHORITY_CLASS = "design_candidate_only"
PROOFREADER_PASS_DISPOSITIONS = {"released"}
ADMITTED_ATTEMPT_LEDGER_PAIRS = {
    (
        "gemini-25-repair-dry-run-visual-001",
        "gemini-25-repair-dry-run-visual-ledger-001",
    ),
    (
        "gemini-25-repair-dry-run-visual-002",
        "gemini-25-repair-dry-run-visual-ledger-002",
    ),
    (
        "gemini-25-repair-dry-run-visual-003",
        "gemini-25-repair-dry-run-visual-ledger-003",
    ),
    (
        "gemini-25-repair-visual-001",
        "gemini-25-repair-visual-ledger-001",
    ),
    (
        "gemini-25-repair-visual-002",
        "gemini-25-repair-visual-ledger-002",
    ),
}
FORBIDDEN_CELL_KEYS = {
    "access_token",
    "api_key",
    "authentication",
    "credential",
    "oauth",
    "patient",
    "project",
    "provider",
    "refresh_token",
    "service_account",
}
FORBIDDEN_DRAFT_FRAGMENTS = {
    "autonomous",
    "database write",
    "deploy",
    "patient",
    "prescribe",
    "production",
    "service account",
}


def _keys(value: Any) -> set[str]:
    found: set[str] = set()
    if isinstance(value, dict):
        for key, child in value.items():
            found.add(str(key).casefold())
            found.update(_keys(child))
    elif isinstance(value, list):
        for child in value:
            found.update(_keys(child))
    return found


def validate_cell_request(value: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if set(value) != {
        "protocol_version",
        "policy_id",
        "attempt_id",
        "ledger_id",
        "task",
    }:
        errors.append("request_top_level_fields_invalid")
    if value.get("protocol_version") != PROTOCOL_VERSION:
        errors.append("protocol_version_invalid")
    if value.get("policy_id") != POLICY_ID:
        errors.append("policy_id_invalid")
    if (value.get("attempt_id"), value.get("ledger_id")) not in (
        ADMITTED_ATTEMPT_LEDGER_PAIRS
    ):
        errors.append("attempt_ledger_pair_invalid")
    task = value.get("task")
    if not isinstance(task, dict) or set(task) != {
        "task_type",
        "fictional_workspace_id",
        "evidence",
        "requested_fields",
    }:
        errors.append("task_fields_invalid")
        return sorted(set(errors))
    if task.get("task_type") != TASK_TYPE:
        errors.append("task_type_invalid")
    if task.get("fictional_workspace_id") != "project-lantern":
        errors.append("fictional_workspace_id_invalid")
    evidence = task.get("evidence")
    observed: dict[str, str] = {}
    if isinstance(evidence, list):
        for item in evidence:
            if (
                isinstance(item, dict)
                and set(item) == {"evidence_id", "statement"}
                and isinstance(item.get("evidence_id"), str)
                and isinstance(item.get("statement"), str)
            ):
                observed[item["evidence_id"]] = item["statement"]
    if observed != EVIDENCE or len(evidence) != len(EVIDENCE):
        errors.append("authored_synthetic_evidence_not_exact")
    if task.get("requested_fields") != RELEASE_FIELDS:
        errors.append("requested_fields_not_exact")
    forbidden = _keys(value) & FORBIDDEN_CELL_KEYS
    errors.extend(f"cell_forbidden_field:{name}" for name in sorted(forbidden))
    return sorted(set(errors))


def provider_response_schema() -> dict[str, Any]:
    state_properties = {
        state: {"type": "STRING", "enum": [emphasis]}
        for state, emphasis in STATE_TREATMENTS.items()
    }
    return {
        "type": "OBJECT",
        "properties": {
            "design_thesis": {
                "type": "STRING",
                "description": (
                    "One concise visual-design thesis grounded only in the "
                    "fictional evidence, at most 240 characters."
                ),
            },
            "visual_direction": {
                "type": "STRING",
                "enum": sorted(VISUAL_DIRECTIONS),
            },
            "composition": {
                "type": "STRING",
                "enum": sorted(COMPOSITIONS),
            },
            "density": {"type": "STRING", "enum": sorted(DENSITIES)},
            "typography": {
                "type": "STRING",
                "enum": sorted(TYPOGRAPHIES),
            },
            "palette": {"type": "STRING", "enum": sorted(PALETTES)},
            "priority_order": {
                "type": "ARRAY",
                "items": {"type": "STRING", "enum": PRIORITY_ORDER},
                "minItems": len(PRIORITY_ORDER),
                "maxItems": len(PRIORITY_ORDER),
            },
            "responsive_strategy": {
                "type": "OBJECT",
                "properties": {
                    key: {"type": "STRING", "enum": sorted(values)}
                    for key, values in RESPONSIVE_VALUES.items()
                },
                "required": list(RESPONSIVE_VALUES),
                "propertyOrdering": list(RESPONSIVE_VALUES),
            },
            "state_treatments": {
                "type": "OBJECT",
                "properties": state_properties,
                "required": list(STATE_TREATMENTS),
                "propertyOrdering": list(STATE_TREATMENTS),
            },
            "interaction_recommendations": {
                "type": "ARRAY",
                "items": {
                    "type": "STRING",
                    "description": (
                        "One concise non-command visual or interaction "
                        "recommendation grounded in the fictional evidence."
                    ),
                },
                "minItems": 3,
                "maxItems": 3,
            },
            "risk_ids": {
                "type": "ARRAY",
                "items": {"type": "STRING", "enum": sorted(RISK_IDS)},
                "minItems": 2,
                "maxItems": 4,
            },
            "evidence_ids": {
                "type": "ARRAY",
                "items": {"type": "STRING", "enum": sorted(EVIDENCE)},
                "minItems": len(EVIDENCE),
                "maxItems": len(EVIDENCE),
            },
            "authority_class": {
                "type": "STRING",
                "enum": [AUTHORITY_CLASS],
            },
        },
        "required": RELEASE_FIELDS,
        "propertyOrdering": RELEASE_FIELDS,
    }


def build_vertex_request(cell_request: Mapping[str, Any]) -> dict[str, Any]:
    errors = validate_cell_request(cell_request)
    if errors:
        raise ContractError("cell_request_invalid:" + ",".join(errors))
    task = cell_request["task"]
    evidence_text = "\n".join(
        f"{item['evidence_id']}: {item['statement']}"
        for item in task["evidence"]
    )
    user_text = (
        "Design a fictional scheduling workspace called Project Lantern using "
        "only the authored-synthetic evidence below. Select only schema-listed "
        "design values. Supply three concise interaction recommendations, two "
        "to four listed risk identifiers, every evidence identifier exactly "
        "once, and authority_class design_candidate_only. This is an untrusted "
        "design candidate for a deterministic human gate; do not issue commands "
        "or describe implementation steps.\n\n"
        f"{evidence_text}"
    )
    return {
        "systemInstruction": {
            "parts": [
                {
                    "text": (
                        "You are a bounded visual-design synthesizer for a "
                        "fictional scheduling workspace. Emit only the supplied "
                        "JSON schema. Use no tools, external facts, product data, "
                        "personal data, commands or hidden implementation."
                    )
                }
            ]
        },
        "contents": [{"role": "user", "parts": [{"text": user_text}]}],
        "generationConfig": {
            "temperature": 0,
            "maxOutputTokens": 1024,
            "responseMimeType": "application/json",
            "responseSchema": provider_response_schema(),
            "thinkingConfig": {"thinkingBudget": 0},
        },
    }


def _fixture_release() -> dict[str, Any]:
    return {
        "design_thesis": (
            "A calm editorial workspace keeps scope and state above a focused "
            "projection while actions remain explicit and reversible."
        ),
        "visual_direction": "editorial_clinical",
        "composition": "conversation_rail_plus_projection_canvas",
        "density": "balanced",
        "typography": "serif_wordmark_humanist_sans_ui",
        "palette": "paper_ink_eucalyptus",
        "priority_order": PRIORITY_ORDER,
        "responsive_strategy": {
            "tablet_landscape": "rail_canvas",
            "tablet_portrait": "stacked_composer_scope_canvas",
            "phone": "single_column_sequential",
        },
        "state_treatments": STATE_TREATMENTS,
        "interaction_recommendations": [
            "Keep the scope ribbon and state label anchored above the active projection.",
            "Let the primary action follow the selected item while the ordinary schedule escape stays persistent.",
            "Use restrained emphasis so proposal and changed-state cues remain unmistakable without dominating the work.",
        ],
        "risk_ids": [
            "dense_metadata_competes_with_task",
            "phone_comparison_loses_alignment",
            "proposal_state_could_resemble_commitment",
        ],
        "evidence_ids": sorted(EVIDENCE),
        "authority_class": AUTHORITY_CLASS,
    }


def provider_free_fixture_response() -> dict[str, Any]:
    fixture = _fixture_release()
    fixture["evidence_ids"] = list(reversed(fixture["evidence_ids"]))
    fixture["risk_ids"] = list(reversed(fixture["risk_ids"]))
    return {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {"text": json.dumps(fixture, ensure_ascii=False)}
                    ]
                }
            }
        ],
        "usageMetadata": {
            "promptTokenCount": 0,
            "candidatesTokenCount": 0,
            "totalTokenCount": 0,
        },
        "modelVersion": "provider-free-fixture",
    }


def validate_attempt_mode(attempt_id: str, mode: str) -> bool:
    pair = next(
        (
            pair
            for pair in ADMITTED_ATTEMPT_LEDGER_PAIRS
            if pair[0] == attempt_id
        ),
        None,
    )
    if pair is None:
        return False
    if "dry-run" in attempt_id:
        return mode == "dry-run"
    return mode == "live"


def _normalized_text(value: Any, *, limit: int) -> tuple[str | None, bool]:
    if not isinstance(value, str):
        return None, False
    normalized = re.sub(r"\s+", " ", value).strip()
    if not normalized or len(normalized) > limit:
        return None, False
    return normalized, normalized != value


def proofread(provider_value: Any) -> dict[str, Any]:
    findings: list[str] = []
    repairs: list[str] = []
    if not isinstance(provider_value, dict):
        return {
            "disposition": "edge_aborted",
            "findings": ["draft_not_object"],
            "safe_repairs": [],
            "release": None,
            "released_field_manifest": [],
            "human_gate": True,
        }
    if set(provider_value) != set(RELEASE_FIELDS):
        findings.append("draft_fields_not_exact")

    thesis, thesis_repaired = _normalized_text(
        provider_value.get("design_thesis"), limit=240
    )
    if thesis is None:
        findings.append("design_thesis_invalid")
    elif thesis_repaired:
        repairs.append("design_thesis_whitespace_normalized")

    exact_enums = {
        "visual_direction": VISUAL_DIRECTIONS,
        "composition": COMPOSITIONS,
        "density": DENSITIES,
        "typography": TYPOGRAPHIES,
        "palette": PALETTES,
    }
    normalized_enums: dict[str, str | None] = {}
    for field, allowed in exact_enums.items():
        raw = provider_value.get(field)
        if isinstance(raw, str) and raw.casefold() in allowed:
            normalized = raw.casefold()
            normalized_enums[field] = normalized
            if normalized != raw:
                repairs.append(f"{field}_enum_casing_normalized")
        else:
            normalized_enums[field] = None
            findings.append(f"{field}_invalid")

    priority = provider_value.get("priority_order")
    if priority != PRIORITY_ORDER:
        findings.append("priority_order_invalid")

    responsive = provider_value.get("responsive_strategy")
    if not isinstance(responsive, dict) or set(responsive) != set(
        RESPONSIVE_VALUES
    ):
        findings.append("responsive_strategy_fields_invalid")
    else:
        for field, allowed in RESPONSIVE_VALUES.items():
            if responsive.get(field) not in allowed:
                findings.append(f"responsive_strategy_{field}_invalid")

    states = provider_value.get("state_treatments")
    if states != STATE_TREATMENTS:
        findings.append("state_treatments_invalid")

    recommendations = provider_value.get("interaction_recommendations")
    normalized_recommendations: list[str] = []
    if not isinstance(recommendations, list) or len(recommendations) != 3:
        findings.append("interaction_recommendations_invalid")
    else:
        for index, value in enumerate(recommendations):
            normalized, repaired = _normalized_text(value, limit=180)
            if normalized is None:
                findings.append(
                    f"interaction_recommendation_{index}_invalid"
                )
                continue
            lowered = normalized.casefold()
            if any(fragment in lowered for fragment in FORBIDDEN_DRAFT_FRAGMENTS):
                findings.append(
                    f"interaction_recommendation_{index}_forbidden"
                )
            if repaired:
                repairs.append(
                    f"interaction_recommendation_{index}_whitespace_normalized"
                )
            normalized_recommendations.append(normalized)

    risk_ids = provider_value.get("risk_ids")
    normalized_risks: list[str] = []
    if (
        isinstance(risk_ids, list)
        and 2 <= len(risk_ids) <= 4
        and len(set(risk_ids)) == len(risk_ids)
        and set(risk_ids) <= RISK_IDS
    ):
        normalized_risks = sorted(risk_ids)
        if normalized_risks != risk_ids:
            repairs.append("risk_ids_deterministically_ordered")
    else:
        findings.append("risk_ids_invalid")

    evidence_ids = provider_value.get("evidence_ids")
    normalized_evidence: list[str] = []
    if (
        isinstance(evidence_ids, list)
        and len(evidence_ids) == len(EVIDENCE)
        and set(evidence_ids) == set(EVIDENCE)
    ):
        normalized_evidence = sorted(evidence_ids)
        if normalized_evidence != evidence_ids:
            repairs.append("evidence_ids_deterministically_ordered")
    else:
        findings.append("evidence_ids_invalid")

    if provider_value.get("authority_class") != AUTHORITY_CLASS:
        findings.append("authority_class_invalid")
    if thesis is not None and any(
        fragment in thesis.casefold()
        for fragment in FORBIDDEN_DRAFT_FRAGMENTS
    ):
        findings.append("design_thesis_forbidden")

    if findings:
        return {
            "disposition": "edge_aborted",
            "findings": sorted(set(findings)),
            "safe_repairs": sorted(set(repairs)),
            "release": None,
            "released_field_manifest": [],
            "human_gate": True,
        }

    release = {
        "design_thesis": thesis,
        **normalized_enums,
        "priority_order": PRIORITY_ORDER,
        "responsive_strategy": responsive,
        "state_treatments": STATE_TREATMENTS,
        "interaction_recommendations": normalized_recommendations,
        "risk_ids": normalized_risks,
        "evidence_ids": normalized_evidence,
        "authority_class": AUTHORITY_CLASS,
    }
    return {
        "disposition": "released",
        "findings": [],
        "safe_repairs": sorted(set(repairs)),
        "release": release,
        "released_field_manifest": RELEASE_FIELDS,
        "human_gate": True,
    }
