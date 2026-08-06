"""Pure intent-shaped retrieval over accepted authored-synthetic Fabric packets."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any

from scripts.raisa_provider_free_practice_context_fabric_bureau_memory_contract import (
    build_contract_packet,
    canonical_json,
    canonical_sha256,
    seal,
    verify_seal,
)
from scripts.raisa_provider_free_practice_context_fabric_current_operational_weave import (
    build_authored_synthetic_packet as build_current_packet,
)
from scripts.raisa_provider_free_practice_context_fabric_patient_free_temporal_weave import (
    build_authored_synthetic_temporal_packet,
    derive_dependency_manifest,
    derive_watch_lease,
    process_signals,
)


SCHEMA_VERSION = (
    "emr4.practice_context_fabric_intent_shaped_temporal_retrieval.v1"
)
EVIDENCE_LABEL = (
    "provider_free_authored_synthetic_intent_shaped_temporal_retrieval"
)
DATA_CLASS = "authored_synthetic_patient_free_context_metadata"

CURRENT = "CURRENT_OPERATIONAL"
MEMORY = "BUREAU_MEMORY"
HISTORICAL = "HISTORICAL_OPERATIONAL"
COMPONENT_ORDER = [CURRENT, MEMORY, HISTORICAL]

INTENT_TEMPLATES: dict[str, dict[str, Any]] = {
    "CURRENT_OPERATIONAL_STATUS": {
        "required_components": [CURRENT],
        "field_profiles": ["CURRENT_MINIMAL"],
        "ambiguity_policy": "NONE",
    },
    "RECENT_PRACTICE_WORK": {
        "required_components": [MEMORY],
        "field_profiles": ["MEMORY_MINIMAL"],
        "ambiguity_policy": "NONE",
    },
    "HISTORICAL_OPERATIONAL_STATE": {
        "required_components": [HISTORICAL],
        "field_profiles": ["HISTORICAL_MINIMAL"],
        "ambiguity_policy": "NONE",
    },
    "CURRENT_AND_PRIOR_OPERATIONAL_COMPARISON": {
        "required_components": [CURRENT, HISTORICAL],
        "field_profiles": ["CURRENT_MINIMAL", "HISTORICAL_MINIMAL"],
        "ambiguity_policy": "NONE",
    },
    "RECENT_OPERATIONAL_REFERENCE": {
        "required_components": [MEMORY],
        "field_profiles": ["MEMORY_REFERENCE_MINIMAL"],
        "ambiguity_policy": "RETURN_ALTERNATIVES",
    },
}

# Accepted upstream vocabularies are intentionally explicit. Do not case-fold.
COMPONENT_VOCABULARY: dict[str, dict[str, Any]] = {
    CURRENT: {
        "canonical_bureau": "RAYLEEN",
        "upstream_bureau": "RAYLEEN",
        "upstream_purpose": "CURRENT_OPERATIONAL_AWARENESS",
        "shareability": "SAME_BUREAU_ONLY",
    },
    MEMORY: {
        "canonical_bureau": "RAYLEEN",
        "upstream_bureau": "rayleen",
        "upstream_purpose": "recent_practice_work",
        "shareability": "BILATERAL_ONLY",
    },
    HISTORICAL: {
        "canonical_bureau": "RAYLEEN",
        "upstream_bureau": "RAYLEEN",
        "upstream_purpose": "TEMPORAL_OPERATIONAL_RECALL",
        "shareability": "BILATERAL_ONLY",
    },
}

CANDIDATE_FIELDS = {
    "schema_version",
    "candidate_id",
    "requesting_bureau",
    "intent_code",
    "requested_components",
    "requested_field_profiles",
    "temporal_coordinate",
    "maximum_components",
    "maximum_facts",
    "maximum_bytes",
    "maximum_alternatives",
    "issued_at",
    "read_only",
    "provider_authority",
    "command_authority",
    "candidate_digest",
}

BINDING_FIELDS = {
    "schema_version",
    "binding_id",
    "principal_ref",
    "practice_id",
    "location_refs",
    "session_id",
    "session_generation",
    "allowed_requesting_bureaus",
    "allowed_intents",
    "allowed_components",
    "allowed_field_profiles",
    "bilateral_shares",
    "upstream_binding_digests",
    "allowed_catalog_digest",
    "authorized_time_window",
    "maximum_components",
    "maximum_facts",
    "maximum_bytes",
    "maximum_alternatives",
    "policy_version",
    "issued_at",
    "expires_at",
    "read_only",
    "provider_authority",
    "command_authority",
    "binding_digest",
}


class IntentRetrievalViolation(ValueError):
    """Raised when a closed deterministic retrieval contract is violated."""


def _instant(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise IntentRetrievalViolation("instant_timezone_required")
    return parsed.astimezone(timezone.utc)


def _closed(value: dict[str, Any], fields: set[str], label: str) -> None:
    if set(value) != fields:
        raise IntentRetrievalViolation(f"{label}_shape_invalid")


def _fact(
    *,
    fact_id: str,
    component_code: str,
    originating_bureau: str,
    purpose_code: str,
    frame_type: str,
    source_class: str,
    subject_ref: str,
    fact_code: str,
    value_kind: str,
    value: str | int,
    valid_at: str | None,
    known_at: str | None,
    upstream_digest: str,
) -> dict[str, Any]:
    return seal(
        {
            "schema_version": SCHEMA_VERSION,
            "fact_id": fact_id,
            "component_code": component_code,
            "originating_bureau": originating_bureau,
            "purpose_code": purpose_code,
            "frame_type": frame_type,
            "source_class": source_class,
            "subject_ref": subject_ref,
            "fact_code": fact_code,
            "value_kind": value_kind,
            "value": value,
            "valid_at": valid_at,
            "known_at": known_at,
            "upstream_digest": upstream_digest,
            "read_only": True,
            "command_authority": False,
        },
        "fact_digest",
    )


def build_intent_candidate(
    intent_code: str,
    *,
    requesting_bureau: str = "RAYLEEN",
    requested_components: list[str] | None = None,
    requested_field_profiles: list[str] | None = None,
    valid_at: str | None = "2026-08-06T00:30:00Z",
    known_at: str | None = "2026-08-06T02:30:00Z",
    maximum_components: int = 3,
    maximum_facts: int = 12,
    maximum_bytes: int = 16000,
    maximum_alternatives: int = 2,
) -> dict[str, Any]:
    if intent_code not in INTENT_TEMPLATES:
        raise IntentRetrievalViolation("intent_unknown")
    template = INTENT_TEMPLATES[intent_code]
    temporal_coordinate = None
    if HISTORICAL in template["required_components"]:
        if valid_at is None or known_at is None:
            raise IntentRetrievalViolation("temporal_coordinate_required")
        temporal_coordinate = {"valid_at": valid_at, "known_at": known_at}
    return seal(
        {
            "schema_version": SCHEMA_VERSION,
            "candidate_id": "synthetic:intent-candidate:" + intent_code.lower(),
            "requesting_bureau": requesting_bureau,
            "intent_code": intent_code,
            "requested_components": requested_components
            if requested_components is not None
            else list(template["required_components"]),
            "requested_field_profiles": requested_field_profiles
            if requested_field_profiles is not None
            else list(template["field_profiles"]),
            "temporal_coordinate": temporal_coordinate,
            "maximum_components": maximum_components,
            "maximum_facts": maximum_facts,
            "maximum_bytes": maximum_bytes,
            "maximum_alternatives": maximum_alternatives,
            "issued_at": "2026-08-06T03:00:30Z",
            "read_only": True,
            "provider_authority": False,
            "command_authority": False,
        },
        "candidate_digest",
    )


def _memory_source_packet() -> dict[str, Any]:
    selector = seal(
        {
            "originating_bureaus": ["rayleen"],
            "action_families": ["waiting_room_read"],
            "actor_relations": ["same_practice_staff"],
            "outcome_codes": ["completed"],
            "temporal_hint": "current_practice_day",
            "maximum_results": 2,
        },
        "selector_digest",
    )
    candidate = seal(
        {
            "schema_version": "emr4.practice_context_fabric_bureau_memory.v1",
            "need_id": "synthetic:need:intent-retrieval-memory",
            "requesting_bureau": "rayleen",
            "purpose_code": "recent_practice_work",
            "requested_frame_types": ["bureau_memory_item_set"],
            "entity_features": [],
            "temporal_hint": "current_practice_day",
            "requested_time_window": {
                "starts_at": "2026-08-06T02:00:00Z",
                "ends_at": "2026-08-06T03:02:00Z",
            },
            "source_classes": ["recent_collective_work"],
            "requested_fields": ["request_label_code", "opaque_target_ref"],
            "maximum_results": 2,
            "freshness_seconds": 120,
            "historical_state_required": False,
            "command_authority": False,
            "issued_at": "2026-08-06T02:59:00Z",
            "bureau_memory_selector": selector,
        },
        "candidate_digest",
    )
    binding = seal(
        {
            "schema_version": "emr4.practice_context_fabric_bureau_memory.v1",
            "binding_id": "synthetic:binding:intent-retrieval-memory",
            "principal_ref": "synthetic:principal:reception-one",
            "role_codes": ["receptionist"],
            "practice_ref": "synthetic:practice:one",
            "location_refs": ["synthetic:location:brisbane-one"],
            "session_ref": "synthetic:session:one",
            "consent_codes": [],
            "policy_version": "context-fabric-intent-retrieval-memory.v1",
            "allowed_bureaus": ["rayleen"],
            "allowed_purposes": ["recent_practice_work"],
            "allowed_frame_types": ["bureau_memory_item_set"],
            "allowed_source_classes": ["recent_collective_work"],
            "allowed_fields": ["request_label_code", "opaque_target_ref"],
            "allowed_action_families": ["waiting_room_read"],
            "allowed_actor_relations": ["same_practice_staff"],
            "allowed_outcome_codes": ["completed"],
            "maximum_results": 2,
            "maximum_bytes": 8192,
            "maximum_freshness_seconds": 120,
            "authorized_time_window": {
                "starts_at": "2026-08-06T02:30:00Z",
                "ends_at": "2026-08-06T03:02:00Z",
            },
            "issued_at": "2026-08-06T02:55:00Z",
            "expires_at": "2026-08-06T03:02:00Z",
        },
        "binding_digest",
    )

    def memory_item(item_id: str, target_ref: str, completed_at: str) -> dict[str, Any]:
        return seal(
            {
                "schema_version": "emr4.practice_context_fabric_bureau_memory.v1",
                "memory_item_id": item_id,
                "originating_bureau": "rayleen",
                "request_kind": "read_projection",
                "request_label_code": "recent_operational_read",
                "action_family": "waiting_room_read",
                "outcome_code": "completed",
                "initiator_relation": "same_practice_staff",
                "target_kind": "waiting_room_entry",
                "opaque_target_ref": target_ref,
                "started_at": completed_at,
                "completed_at": completed_at,
                "source_receipt_ref": "synthetic:receipt:" + item_id.rsplit(":", 1)[-1],
                "source_revision": "synthetic:memory-revision:1",
                "source_digest": canonical_sha256({"fixture": item_id}),
                "supersession_state": "CURRENT",
                "relevance_reason_codes": ["PURPOSE_MATCH", "TIME_MATCH"],
                "authority_ceiling": "read_context_only",
            },
            "memory_item_digest",
        )

    items = [
        memory_item(
            "synthetic:memory:reference-one",
            "synthetic:opaque-operational-ref:one",
            "2026-08-06T02:58:00Z",
        ),
        memory_item(
            "synthetic:memory:reference-two",
            "synthetic:opaque-operational-ref:two",
            "2026-08-06T02:59:00Z",
        ),
    ]
    return build_contract_packet(
        candidate,
        binding,
        items,
        assembled_at="2026-08-06T03:00:00Z",
        proofread_at="2026-08-06T03:00:01Z",
        source_revision="synthetic:memory-source-revision:1",
    )


def build_authored_synthetic_sources() -> dict[str, Any]:
    current = build_current_packet()
    manifest = derive_dependency_manifest(current)
    lease = derive_watch_lease(current, manifest)
    current_state, requirement, checkpoint, _, _, trace = process_signals(
        current, manifest, lease, []
    )
    if requirement is not None:
        raise IntentRetrievalViolation("unexpected_reassembly_requirement")
    return {
        "current_packet": current,
        "current_state": current_state,
        "current_checkpoint": checkpoint,
        "current_temporal_trace": trace,
        "memory_packet": _memory_source_packet(),
        "temporal_packet": build_authored_synthetic_temporal_packet(),
    }


def build_intent_authority_binding(
    sources: dict[str, Any], *, catalog: dict[str, Any] | None = None
) -> dict[str, Any]:
    current = sources["current_packet"]
    memory = sources["memory_packet"]
    temporal = sources["temporal_packet"]
    bound_catalog = catalog if catalog is not None else build_source_catalog(sources)
    verify_seal(bound_catalog, "catalog_digest")
    return seal(
        {
            "schema_version": SCHEMA_VERSION,
            "binding_id": "synthetic:binding:intent-shaped-retrieval",
            "principal_ref": current["authority_binding"]["principal_ref"],
            "practice_id": current["authority_binding"]["practice_id"],
            "location_refs": list(current["authority_binding"]["allowed_location_refs"]),
            "session_id": current["authority_binding"]["session_id"],
            "session_generation": current["authority_binding"]["session_generation"],
            "allowed_requesting_bureaus": ["BERNIE", "RAYLEEN"],
            "allowed_intents": sorted(INTENT_TEMPLATES),
            "allowed_components": list(COMPONENT_ORDER),
            "allowed_field_profiles": [
                "CURRENT_MINIMAL",
                "HISTORICAL_MINIMAL",
                "MEMORY_MINIMAL",
                "MEMORY_REFERENCE_MINIMAL",
            ],
            "bilateral_shares": [
                "BERNIE<-RAYLEEN:recent_practice_work",
            ],
            "upstream_binding_digests": sorted(
                [
                    current["authority_binding"]["binding_digest"],
                    memory["authority_binding"]["binding_digest"],
                    temporal["parent_binding"]["parent_binding_record_digest"],
                ]
            ),
            "allowed_catalog_digest": bound_catalog["catalog_digest"],
            "authorized_time_window": {
                "starts_at": "2026-08-06T00:00:00Z",
                "ends_at": "2026-08-06T03:02:00Z",
            },
            "maximum_components": 3,
            "maximum_facts": 12,
            "maximum_bytes": 14000,
            "maximum_alternatives": 2,
            "policy_version": "context-fabric-intent-shaped-retrieval.v1",
            "issued_at": "2026-08-06T03:00:00Z",
            "expires_at": "2026-08-06T03:02:00Z",
            "read_only": True,
            "provider_authority": False,
            "command_authority": False,
        },
        "binding_digest",
    )


def _current_facts(packet: dict[str, Any]) -> list[dict[str, Any]]:
    frames = {frame["frame_type"]: frame for frame in packet["frame_set"]["frames"]}
    diary = frames["current_diary_projection"]
    waiting = frames["current_waiting_room_projection"]
    directory = frames["active_practitioner_directory"]
    session = frames["private_application_session_state"]
    appointment = diary["content"]["appointments"][0]
    waiting_entry = waiting["content"]["entries"][0]
    practitioner = directory["content"]["practitioners"][0]
    return [
        _fact(
            fact_id="synthetic:fact:current-diary-status",
            component_code=CURRENT,
            originating_bureau="RAYLEEN",
            purpose_code="CURRENT_OPERATIONAL_AWARENESS",
            frame_type=diary["frame_type"],
            source_class=diary["source_class"],
            subject_ref=appointment["appointment_ref"],
            fact_code="CURRENT_APPOINTMENT_STATUS",
            value_kind="CODE",
            value=appointment["status"],
            valid_at=None,
            known_at=None,
            upstream_digest=diary["frame_digest"],
        ),
        _fact(
            fact_id="synthetic:fact:current-wait-minutes",
            component_code=CURRENT,
            originating_bureau="RAYLEEN",
            purpose_code="CURRENT_OPERATIONAL_AWARENESS",
            frame_type=waiting["frame_type"],
            source_class=waiting["source_class"],
            subject_ref=waiting_entry["appointment_ref"],
            fact_code="CURRENT_WAIT_MINUTES",
            value_kind="COUNT",
            value=waiting_entry["elapsed_wait_minutes"],
            valid_at=None,
            known_at=None,
            upstream_digest=waiting["frame_digest"],
        ),
        _fact(
            fact_id="synthetic:fact:current-practitioner-role",
            component_code=CURRENT,
            originating_bureau="RAYLEEN",
            purpose_code="CURRENT_OPERATIONAL_AWARENESS",
            frame_type=directory["frame_type"],
            source_class=directory["source_class"],
            subject_ref=practitioner["practitioner_ref"],
            fact_code="CURRENT_PRACTITIONER_ROLE",
            value_kind="CODE",
            value=practitioner["role_label"],
            valid_at=None,
            known_at=None,
            upstream_digest=directory["frame_digest"],
        ),
        _fact(
            fact_id="synthetic:fact:current-session-proposal-state",
            component_code=CURRENT,
            originating_bureau="RAYLEEN",
            purpose_code="CURRENT_OPERATIONAL_AWARENESS",
            frame_type=session["frame_type"],
            source_class=session["source_class"],
            subject_ref=packet["authority_binding"]["session_id"],
            fact_code="CURRENT_SESSION_PROPOSAL_STATE",
            value_kind="CODE",
            value=session["content"]["proposal_state"],
            valid_at=None,
            known_at=None,
            upstream_digest=session["frame_digest"],
        ),
    ]


def _memory_facts(packet: dict[str, Any]) -> list[dict[str, Any]]:
    frame = packet["frame_set"]["frames"][0]
    return [
        _fact(
            fact_id="synthetic:fact:" + item["memory_item_id"].rsplit(":", 1)[-1],
            component_code=MEMORY,
            originating_bureau="rayleen",
            purpose_code="recent_practice_work",
            frame_type=frame["frame_type"],
            source_class=frame["source_class"],
            subject_ref=item["opaque_target_ref"],
            fact_code="RECENT_REQUEST_LABEL",
            value_kind="CODE",
            value=item["request_label_code"],
            valid_at=None,
            known_at=item["completed_at"],
            upstream_digest=item["memory_item_digest"],
        )
        for item in frame["items"]
    ]


def _historical_facts(packet: dict[str, Any]) -> list[dict[str, Any]]:
    facts: list[dict[str, Any]] = []
    for result in packet["historical_results"]:
        for frame in result["frames"]:
            facts.append(
                _fact(
                    fact_id="synthetic:fact:historical-waiting:"
                    + result["known_at"],
                    component_code=HISTORICAL,
                    originating_bureau="RAYLEEN",
                    purpose_code="TEMPORAL_OPERATIONAL_RECALL",
                    frame_type="historical_waiting_room_projection",
                    source_class="historical_waiting_room",
                    subject_ref=frame["snapshot_id"],
                    fact_code="HISTORICAL_WAITING_COUNT",
                    value_kind="COUNT",
                    value=frame["content"]["waiting_count"],
                    valid_at=result["valid_at"],
                    known_at=result["known_at"],
                    upstream_digest=frame["historical_frame_digest"],
                )
            )
    return facts


def _component(
    *,
    component_code: str,
    upstream_packet_digest: str,
    upstream_binding_digest: str,
    upstream_proofreader_digest: str,
    upstream_frame_digests: list[str],
    source_revisions: list[str],
    expires_at: str,
    facts: list[dict[str, Any]],
    current_state_digest: str | None = None,
    current_state: str | None = None,
) -> dict[str, Any]:
    vocabulary = COMPONENT_VOCABULARY[component_code]
    return seal(
        {
            "schema_version": SCHEMA_VERSION,
            "component_id": "synthetic:retrieval-component:"
            + component_code.lower(),
            "component_code": component_code,
            "canonical_bureau": vocabulary["canonical_bureau"],
            "upstream_bureau": vocabulary["upstream_bureau"],
            "upstream_purpose": vocabulary["upstream_purpose"],
            "shareability": vocabulary["shareability"],
            "contains_private_session": component_code == CURRENT,
            "upstream_packet_digest": upstream_packet_digest,
            "upstream_binding_digest": upstream_binding_digest,
            "upstream_proofreader_digest": upstream_proofreader_digest,
            "upstream_frame_digests": sorted(upstream_frame_digests),
            "source_revisions": sorted(source_revisions),
            "current_state_digest": current_state_digest,
            "current_state": current_state,
            "expires_at": expires_at,
            "facts": facts,
            "read_only": True,
            "provider_authority": False,
            "command_authority": False,
        },
        "component_digest",
    )


def build_source_catalog(sources: dict[str, Any]) -> dict[str, Any]:
    current = sources["current_packet"]
    memory = sources["memory_packet"]
    temporal = sources["temporal_packet"]
    state = sources["current_state"]
    if current["proofreader_trace"]["release_decision"] != "RELEASE":
        raise IntentRetrievalViolation("current_upstream_not_released")
    if memory["proofreader_trace"]["release_decision"] != "RELEASE":
        raise IntentRetrievalViolation("memory_upstream_not_released")
    if temporal["proofreader_trace"]["release_decision"] != "RELEASE":
        raise IntentRetrievalViolation("temporal_upstream_not_released")
    verify_seal(state, "state_digest")
    if state["parent_frame_set_digest"] != current["frame_set"]["frame_set_digest"]:
        raise IntentRetrievalViolation("current_state_parent_mismatch")
    components = [
        _component(
            component_code=CURRENT,
            upstream_packet_digest=canonical_sha256(current),
            upstream_binding_digest=current["authority_binding"]["binding_digest"],
            upstream_proofreader_digest=current["proofreader_trace"][
                "proofreader_trace_digest"
            ],
            upstream_frame_digests=[
                frame["frame_digest"] for frame in current["frame_set"]["frames"]
            ],
            source_revisions=[
                frame["source_revision"] for frame in current["frame_set"]["frames"]
            ],
            expires_at=current["frame_set"]["expires_at"],
            facts=_current_facts(current),
            current_state_digest=state["state_digest"],
            current_state=state["state"],
        ),
        _component(
            component_code=MEMORY,
            upstream_packet_digest=memory["contract_digest"],
            upstream_binding_digest=memory["authority_binding"]["binding_digest"],
            upstream_proofreader_digest=memory["proofreader_trace"]["trace_digest"],
            upstream_frame_digests=[
                frame["content_digest"] for frame in memory["frame_set"]["frames"]
            ],
            source_revisions=list(memory["frame_set"]["source_revisions"]),
            expires_at=memory["frame_set"]["expires_at"],
            facts=_memory_facts(memory),
        ),
        _component(
            component_code=HISTORICAL,
            upstream_packet_digest=canonical_sha256(temporal),
            upstream_binding_digest=temporal["parent_binding"][
                "parent_binding_record_digest"
            ],
            upstream_proofreader_digest=temporal["proofreader_trace"][
                "proofreader_trace_digest"
            ],
            upstream_frame_digests=[
                frame["historical_frame_digest"]
                for result in temporal["historical_results"]
                for frame in result["frames"]
            ],
            source_revisions=[
                frame["snapshot_id"]
                for result in temporal["historical_results"]
                for frame in result["frames"]
            ],
            expires_at=temporal["historical_policy"]["expires_at"],
            facts=_historical_facts(temporal),
        ),
    ]
    return seal(
        {
            "schema_version": SCHEMA_VERSION,
            "catalog_id": "synthetic:intent-retrieval-catalog",
            "components": components,
            "component_vocabulary_digest": canonical_sha256(COMPONENT_VOCABULARY),
            "source_reads_executed": 0,
            "read_only": True,
            "command_authority": False,
        },
        "catalog_digest",
    )


def derive_intent_plan(
    candidate: dict[str, Any], binding: dict[str, Any], *, assembled_at: str
) -> dict[str, Any]:
    _closed(candidate, CANDIDATE_FIELDS, "candidate")
    _closed(binding, BINDING_FIELDS, "binding")
    verify_seal(candidate, "candidate_digest")
    verify_seal(binding, "binding_digest")
    if (
        candidate["read_only"] is not True
        or candidate["provider_authority"] is not False
        or candidate["command_authority"] is not False
        or binding["read_only"] is not True
        or binding["provider_authority"] is not False
        or binding["command_authority"] is not False
    ):
        raise IntentRetrievalViolation("authority_ceiling_invalid")
    if candidate["intent_code"] not in INTENT_TEMPLATES:
        raise IntentRetrievalViolation("intent_unknown")
    template = INTENT_TEMPLATES[candidate["intent_code"]]
    reductions: list[str] = []
    admitted = True
    if (
        candidate["requesting_bureau"] not in binding["allowed_requesting_bureaus"]
        or candidate["intent_code"] not in binding["allowed_intents"]
    ):
        admitted = False
    required = list(template["required_components"])
    requested = [
        code for code in COMPONENT_ORDER if code in candidate["requested_components"]
    ]
    if set(candidate["requested_components"]) - set(COMPONENT_ORDER):
        raise IntentRetrievalViolation("component_unknown")
    if not set(required).issubset(requested):
        admitted = False
    components = [
        code
        for code in required
        if code in requested and code in binding["allowed_components"]
    ]
    if components != required:
        admitted = False
    if set(requested) - set(required):
        reductions.append("COMPONENTS_NARROWED_TO_INTENT")
    profiles = [
        code
        for code in template["field_profiles"]
        if code in candidate["requested_field_profiles"]
        and code in binding["allowed_field_profiles"]
    ]
    if profiles != template["field_profiles"]:
        admitted = False
    start = max(
        _instant(candidate["issued_at"]),
        _instant(binding["authorized_time_window"]["starts_at"]),
    )
    end = min(
        _instant(binding["authorized_time_window"]["ends_at"]),
        _instant(binding["expires_at"]),
    )
    if not start < end or not start <= _instant(assembled_at) < end:
        admitted = False
    maxima = {
        "maximum_components": min(
            candidate["maximum_components"], binding["maximum_components"]
        ),
        "maximum_facts": min(candidate["maximum_facts"], binding["maximum_facts"]),
        "maximum_bytes": min(candidate["maximum_bytes"], binding["maximum_bytes"]),
        "maximum_alternatives": min(
            candidate["maximum_alternatives"], binding["maximum_alternatives"]
        ),
    }
    if len(components) > maxima["maximum_components"]:
        admitted = False
    if not admitted:
        components = []
        profiles = []
        reductions = ["SCOPE_NOT_AVAILABLE"]
    return seal(
        {
            "schema_version": SCHEMA_VERSION,
            "plan_id": "synthetic:intent-plan:" + candidate["candidate_id"],
            "candidate_digest": candidate["candidate_digest"],
            "binding_digest": binding["binding_digest"],
            "intent_code": candidate["intent_code"],
            "requesting_bureau": candidate["requesting_bureau"]
            if admitted
            else "NOT_AVAILABLE",
            "decision": "ADMIT" if admitted else "NOT_AVAILABLE",
            "required_components": components,
            "field_profiles": profiles,
            "ambiguity_policy": template["ambiguity_policy"],
            "temporal_coordinate": candidate["temporal_coordinate"],
            "maximum_components": maxima["maximum_components"] if admitted else 0,
            "maximum_facts": maxima["maximum_facts"] if admitted else 0,
            "maximum_bytes": maxima["maximum_bytes"] if admitted else 0,
            "maximum_alternatives": maxima["maximum_alternatives"] if admitted else 0,
            "reduction_reason_codes": sorted(set(reductions)),
            "policy_version": binding["policy_version"],
            "assembled_at": assembled_at,
            "expires_at": binding["expires_at"],
            "read_only": True,
            "provider_authority": False,
            "command_authority": False,
        },
        "plan_digest",
    )


def _bilateral_key(requesting: str, component: dict[str, Any]) -> str:
    return (
        requesting
        + "<-"
        + component["canonical_bureau"]
        + ":"
        + component["upstream_purpose"]
    )


def _select(
    candidate: dict[str, Any],
    binding: dict[str, Any],
    plan: dict[str, Any],
    catalog: dict[str, Any],
    *,
    assembled_at: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    verify_seal(catalog, "catalog_digest")
    by_code = {item["component_code"]: item for item in catalog["components"]}
    selected: list[dict[str, Any]] = []
    omissions: list[str] = []
    alternatives: list[dict[str, Any]] = []
    if binding["allowed_catalog_digest"] != catalog["catalog_digest"]:
        plan = deepcopy(plan)
        plan["decision"] = "NOT_AVAILABLE"
        plan["required_components"] = []
        plan["maximum_components"] = 0
        plan["maximum_facts"] = 0
        plan["maximum_bytes"] = 0
        plan["maximum_alternatives"] = 0
        omissions.append("CATALOG_BINDING_MISMATCH")
    if plan["decision"] == "ADMIT":
        for code in plan["required_components"]:
            component = by_code.get(code)
            if component is None:
                omissions.append("REQUIRED_COMPONENT_NOT_AVAILABLE")
                continue
            verify_seal(component, "component_digest")
            vocabulary = COMPONENT_VOCABULARY[code]
            if (
                component["canonical_bureau"] != vocabulary["canonical_bureau"]
                or component["upstream_bureau"] != vocabulary["upstream_bureau"]
                or component["upstream_purpose"] != vocabulary["upstream_purpose"]
            ):
                omissions.append("COMPONENT_VOCABULARY_MISMATCH")
                continue
            same_bureau = (
                plan["requesting_bureau"] == component["canonical_bureau"]
            )
            if not same_bureau:
                if component["contains_private_session"]:
                    omissions.append("PRIVATE_SESSION_NOT_SHAREABLE")
                    continue
                if _bilateral_key(plan["requesting_bureau"], component) not in binding[
                    "bilateral_shares"
                ]:
                    omissions.append("BILATERAL_SCOPE_NOT_AVAILABLE")
                    continue
            if _instant(assembled_at) >= _instant(component["expires_at"]):
                omissions.append("COMPONENT_EXPIRED")
                continue
            if code == CURRENT and component["current_state"] != "CURRENT":
                omissions.append("CURRENT_COMPONENT_REASSEMBLY_REQUIRED")
                continue
            facts = deepcopy(component["facts"])
            if code == HISTORICAL:
                coordinate = plan["temporal_coordinate"]
                facts = [
                    fact
                    for fact in facts
                    if fact["valid_at"] == coordinate["valid_at"]
                    and fact["known_at"] == coordinate["known_at"]
                ]
                if not facts:
                    omissions.append("HISTORICAL_NO_COVERAGE")
                    continue
            if (
                code == MEMORY
                and plan["ambiguity_policy"] == "RETURN_ALTERNATIVES"
                and len(facts) > 1
            ):
                limit = plan["maximum_alternatives"]
                alternatives = [
                    seal(
                        {
                            "schema_version": SCHEMA_VERSION,
                            "alternative_id": fact["fact_id"],
                            "opaque_subject_ref": fact["subject_ref"],
                            "discriminator_code": "OPAQUE_RECENT_WORK_REFERENCE",
                            "upstream_fact_digest": fact["fact_digest"],
                            "identity_asserted": False,
                            "read_only": True,
                            "command_authority": False,
                        },
                        "alternative_digest",
                    )
                    for fact in sorted(facts, key=lambda item: item["fact_id"])[
                        :limit
                    ]
                ]
                omissions.append("AMBIGUOUS_REFERENCE_REQUIRES_DISCRIMINATOR")
                continue
            selected.append(
                seal(
                    {
                        "schema_version": SCHEMA_VERSION,
                        "component_code": code,
                        "originating_bureau": component["canonical_bureau"],
                        "purpose_code": component["upstream_purpose"],
                        "upstream_component_digest": component["component_digest"],
                        "upstream_packet_digest": component["upstream_packet_digest"],
                        "upstream_binding_digest": component[
                            "upstream_binding_digest"
                        ],
                        "upstream_proofreader_digest": component[
                            "upstream_proofreader_digest"
                        ],
                        "upstream_frame_digests": component[
                            "upstream_frame_digests"
                        ],
                        "source_revisions": component["source_revisions"],
                        "facts": facts,
                        "expires_at": component["expires_at"],
                        "read_only": True,
                        "provider_authority": False,
                        "command_authority": False,
                    },
                    "selected_component_digest",
                )
            )
    selected.sort(key=lambda item: COMPONENT_ORDER.index(item["component_code"]))
    missing_required = set(plan["required_components"]) - {
        item["component_code"] for item in selected
    }
    ambiguity = "ALTERNATIVES" if alternatives else "NONE"
    if plan["decision"] != "ADMIT" or (missing_required and not alternatives):
        disposition = "NOT_AVAILABLE"
        selected = []
        alternatives = []
        ambiguity = "NOT_AVAILABLE"
        if not omissions:
            omissions = ["SCOPE_NOT_AVAILABLE"]
    elif alternatives:
        disposition = "ALTERNATIVES"
        selected = []
    else:
        disposition = "ADMIT"
    fact_count = sum(len(item["facts"]) for item in selected)
    disclosed_bytes = (
        len(canonical_json(selected).encode("utf-8"))
        + len(canonical_json(alternatives).encode("utf-8"))
        if selected or alternatives
        else 0
    )
    if (
        len(selected) > plan["maximum_components"]
        or fact_count > plan["maximum_facts"]
        or disclosed_bytes > plan["maximum_bytes"]
    ):
        disposition = "NOT_AVAILABLE"
        selected = []
        alternatives = []
        ambiguity = "NOT_AVAILABLE"
        omissions = ["DISCLOSURE_CEILING_EXCEEDED"]
        fact_count = 0
        disclosed_bytes = 0
    trace = seal(
        {
            "schema_version": SCHEMA_VERSION,
            "candidate_digest": candidate["candidate_digest"],
            "binding_digest": binding["binding_digest"],
            "plan_digest": plan["plan_digest"],
            "catalog_digest": catalog["catalog_digest"],
            "selected_component_digests": [
                item["selected_component_digest"] for item in selected
            ],
            "omission_reason_codes": sorted(set(omissions)),
            "fact_count": fact_count,
            "disclosed_bytes": disclosed_bytes,
            "ambiguity_state": ambiguity,
            "source_reads_executed": 0,
            "command_operations": 0,
        },
        "selection_trace_digest",
    )
    expires = min(
        [binding["expires_at"]]
        + [item["expires_at"] for item in selected]
    )
    frame_set = seal(
        {
            "schema_version": SCHEMA_VERSION,
            "frame_set_id": "synthetic:intent-frame-set:"
            + candidate["candidate_id"],
            "candidate_digest": candidate["candidate_digest"],
            "binding_digest": binding["binding_digest"],
            "plan_digest": plan["plan_digest"],
            "catalog_digest": catalog["catalog_digest"],
            "selection_trace_digest": trace["selection_trace_digest"],
            "disposition": disposition,
            "components": selected,
            "ambiguity_state": ambiguity,
            "alternatives": alternatives,
            "omission_reason_codes": trace["omission_reason_codes"],
            "assembled_at": assembled_at,
            "expires_at": expires,
            "maximum_disclosure_bytes": plan["maximum_bytes"],
            "read_only": True,
            "provider_authority": False,
            "command_authority": False,
        },
        "frame_set_digest",
    )
    return trace, frame_set


def _assemble_without_proofreader(
    candidate: dict[str, Any],
    binding: dict[str, Any],
    catalog: dict[str, Any],
    *,
    assembled_at: str,
) -> dict[str, Any]:
    plan = derive_intent_plan(candidate, binding, assembled_at=assembled_at)
    trace, frame_set = _select(
        candidate, binding, plan, catalog, assembled_at=assembled_at
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "evidence_label": EVIDENCE_LABEL,
        "data_class": DATA_CLASS,
        "candidate": candidate,
        "authority_binding": binding,
        "source_catalog": catalog,
        "intent_plan": plan,
        "selection_trace": trace,
        "frame_set": frame_set,
        "authority_ceiling": "read_context_only",
        "blocked_boundaries": [
            "patient_data",
            "product_data",
            "provider",
            "database",
            "persistence",
            "product_runtime",
            "api",
            "command",
            "clinical_authority",
            "prescribing",
            "referral",
            "billing",
            "deployment",
            "production",
            "release",
            "protected_refs",
        ],
        "assembled_at": assembled_at,
    }


def proofread_intent_packet(
    packet: dict[str, Any], *, checked_at: str
) -> dict[str, Any]:
    reasons: list[str] = []
    try:
        expected = _assemble_without_proofreader(
            packet["candidate"],
            packet["authority_binding"],
            packet["source_catalog"],
            assembled_at=packet["assembled_at"],
        )
        if packet != expected:
            reasons.append("PACKET_RECOMPUTATION_MISMATCH")
        for value, field in (
            (packet["candidate"], "candidate_digest"),
            (packet["authority_binding"], "binding_digest"),
            (packet["source_catalog"], "catalog_digest"),
            (packet["intent_plan"], "plan_digest"),
            (packet["selection_trace"], "selection_trace_digest"),
            (packet["frame_set"], "frame_set_digest"),
        ):
            verify_seal(value, field)
        for component in packet["source_catalog"]["components"]:
            verify_seal(component, "component_digest")
            for fact in component["facts"]:
                verify_seal(fact, "fact_digest")
        if _instant(checked_at) >= _instant(packet["frame_set"]["expires_at"]):
            reasons.append("FRAME_SET_EXPIRED")
        if packet["source_catalog"]["source_reads_executed"] != 0:
            reasons.append("SOURCE_READ_EXECUTED")
        if packet["selection_trace"]["command_operations"] != 0:
            reasons.append("COMMAND_EXECUTED")
    except (KeyError, TypeError, ValueError, IntentRetrievalViolation) as error:
        reasons.append("PACKET_INVALID:" + type(error).__name__)
    return seal(
        {
            "schema_version": SCHEMA_VERSION,
            "packet_digest": canonical_sha256(packet),
            "checked_at": checked_at,
            "checks": [
                "closed_candidate_and_binding",
                "explicit_component_vocabulary",
                "atomic_bureau_capability",
                "bilateral_sharing",
                "current_temporal_state",
                "bitemporal_coordinate",
                "minimal_disclosure",
                "ambiguity_without_identity_assertion",
                "upstream_provenance",
                "same_packet_recomputation",
                "authority_ceiling",
            ],
            "release_decision": "BLOCK" if reasons else "RELEASE",
            "reason_codes": sorted(set(reasons))
            if reasons
            else ["ALL_CHECKS_PASSED"],
            "read_only": True,
            "provider_authority": False,
            "command_authority": False,
        },
        "proofreader_trace_digest",
    )


def build_intent_packet(
    candidate: dict[str, Any],
    binding: dict[str, Any],
    catalog: dict[str, Any],
    *,
    assembled_at: str = "2026-08-06T03:01:00Z",
    checked_at: str = "2026-08-06T03:01:01Z",
) -> dict[str, Any]:
    packet = _assemble_without_proofreader(
        candidate, binding, catalog, assembled_at=assembled_at
    )
    packet["proofreader_trace"] = proofread_intent_packet(
        packet, checked_at=checked_at
    )
    return seal(packet, "contract_digest")


def build_authored_synthetic_intent_packet(
    intent_code: str = "CURRENT_AND_PRIOR_OPERATIONAL_COMPARISON",
    *,
    requesting_bureau: str = "RAYLEEN",
) -> dict[str, Any]:
    sources = build_authored_synthetic_sources()
    candidate = build_intent_candidate(
        intent_code, requesting_bureau=requesting_bureau
    )
    catalog = build_source_catalog(sources)
    binding = build_intent_authority_binding(sources, catalog=catalog)
    return build_intent_packet(candidate, binding, catalog)


__all__ = [
    "COMPONENT_ORDER",
    "COMPONENT_VOCABULARY",
    "CURRENT",
    "DATA_CLASS",
    "EVIDENCE_LABEL",
    "HISTORICAL",
    "INTENT_TEMPLATES",
    "IntentRetrievalViolation",
    "MEMORY",
    "SCHEMA_VERSION",
    "build_authored_synthetic_intent_packet",
    "build_authored_synthetic_sources",
    "build_intent_authority_binding",
    "build_intent_candidate",
    "build_intent_packet",
    "build_source_catalog",
    "derive_intent_plan",
    "proofread_intent_packet",
]
