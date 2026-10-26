"""Pure typed goal-only projection for the existing Clockwork sole writer.

This module reads no files and performs no canonical write, admission, Git,
selection, recommendation, dispatch or execution. A new Clockwork event adapter
must separately bind its current predecessor, source/effect admission and lease.
Existing tooling closeouts and the consumed G4 orientation are not reused.
"""
from __future__ import annotations

import copy
from datetime import datetime
import hashlib
import json
from typing import Any

INTENT_VERSION = "ariadne.governance_goal_only_intent.v1"
OPERATION_ID = "compass-gpms-goal-update-v1"
HORIZON_ID = "commercial-gpms-goal-roadmap-v1"
PAYLOAD_SHA256 = "7041236ef65b70e77d12bd7112c7bd9da0a83c6e9bf61865fdfd6a3defff056c"
DISPOSITIONS_SHA256 = "e3329845dcdd49b0141c0fd1bbea5ca8749f8d3f68c713e9520c199688555e36"
PAYLOAD_REFERENCE = "orchestration/continuity/compass-gpms-goal-update/gpms-goal-update-payload-v2.json"
PLAN_LIMIT = (
    "Owner-goal and dependency roadmap only. The 18 original capability dispositions, "
    "maturity, unknowns and deferrals remain qualified navigation. G2/G3 acceptance "
    "is preserved; M1 remains partial and G5 blocked. No recommendation, selection, "
    "dispatch, gate transition, acceptance, model/provider, real-data, deployment, "
    "protected-ref, runtime or spending expansion follows."
)


class GoalUpdateRejection(ValueError):
    """Fixed rejection label; no caller paths or source material in errors."""


def _need(value: bool, reason: str) -> None:
    if not value:
        raise GoalUpdateRejection(reason)


def _load(raw: bytes) -> dict[str, Any]:
    def unique(pairs):
        value = {}
        for key, item in pairs:
            _need(key not in value, "goal_duplicate_json_key")
            value[key] = item
        return value
    try:
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=unique)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise GoalUpdateRejection("goal_json_invalid") from error
    _need(type(value) is dict, "goal_json_object_required")
    return value


def validate_goal_intent(value: object) -> dict[str, Any]:
    _need(type(value) is dict and set(value) == {
        "schema_version", "operation_id", "recorded_at", "payload_sha256",
        "capability_dispositions_sha256", "effect", "recommendation_selection_dispatch",
    }, "goal_intent_keys")
    row = copy.deepcopy(value)
    _need(row["schema_version"] == INTENT_VERSION and row["operation_id"] == OPERATION_ID,
          "goal_intent_identity")
    _need(row["payload_sha256"] == PAYLOAD_SHA256
          and row["capability_dispositions_sha256"] == DISPOSITIONS_SHA256,
          "goal_intent_source_pins")
    _need(row["effect"] == "goal_roadmap_only"
          and row["recommendation_selection_dispatch"] == "unchanged_not_enabled",
          "goal_intent_effect_scope")
    try:
        stamp = row["recorded_at"]
        instant = datetime.fromisoformat(stamp)
        _need(type(stamp) is str and instant.tzinfo is not None
              and instant.isoformat() == stamp, "goal_recorded_at")
    except (TypeError, ValueError) as error:
        raise GoalUpdateRejection("goal_recorded_at") from error
    return row


def validate_goal_sources(payload_raw: bytes, dispositions_raw: bytes) -> dict[str, Any]:
    _need(type(payload_raw) is bytes and len(payload_raw) == 53679
          and hashlib.sha256(payload_raw).hexdigest() == PAYLOAD_SHA256,
          "goal_payload_pin")
    _need(type(dispositions_raw) is bytes and len(dispositions_raw) == 45104
          and hashlib.sha256(dispositions_raw).hexdigest() == DISPOSITIONS_SHA256,
          "goal_dispositions_pin")
    payload, original = _load(payload_raw), _load(dispositions_raw)
    _need(payload.get("schema") == "emr4.compass_gpms_goal_update_payload.v1"
          and payload.get("status") == "AUTHORED_PROPOSAL_NOT_ACCEPTED_NOT_ADMITTED",
          "goal_payload_identity")
    goal = payload.get("owner_confirmed_goal")
    _need(type(goal) is dict and goal.get("product")
          == "Commercial, self-service, multi-practice modular GPMSaaS"
          and goal.get("pilot") == "EXCLUDED", "goal_owner_outcome")
    roadmap = payload.get("roadmap")
    _need(type(roadmap) is list and len(roadmap) == 6
          and [step.get("step") for step in roadmap if type(step) is dict]
          == list(range(1, 7)), "goal_roadmap_order")
    domains = payload.get("capability_dispositions", {}).get("domains")
    source_domains = original.get("domains")
    _need(type(domains) is list and type(source_domains) is list
          and len(domains) == len(source_domains) == 18, "goal_domain_population")
    # Preserve every original field/value, ordered domain and qualification;
    # only the two explicitly proposed planning annotations may be added.
    additions = {"proposed_roadmap_classification", "proposed_roadmap_role"}
    for domain, source in zip(domains, source_domains):
        _need(type(domain) is dict and type(source) is dict
              and set(domain) == set(source) | additions
              and {k: v for k, v in domain.items() if k not in additions} == source,
              "goal_original_domain_fields_changed")
    _need(payload["capability_dispositions"].get("source_sha256") == DISPOSITIONS_SHA256
          and payload["capability_dispositions"].get("domain_count") == 18,
          "goal_domain_source_binding")
    return payload


def project_goal_update(compass: object, intent: object, *, payload_raw: bytes,
                        dispositions_raw: bytes) -> dict[str, Any]:
    """Return a deterministic candidate map; never admit or publish it.

    No continuity graph, active latch, baton or authority input is accepted.
    Full Compass/continuity validation and exact bytes/lease joins remain the
    existing Clockwork event adapter's obligation before canonical publication.
    """
    row = validate_goal_intent(intent)
    payload = validate_goal_sources(payload_raw, dispositions_raw)
    _need(type(compass) is dict and type(compass.get("map_revision")) is int
          and compass["map_revision"] > 0
          and type(compass.get("source_graph_revision")) is int
          and compass["source_graph_revision"] > 0,
          "goal_compass_revision")
    _need(type(compass.get("north_star")) is dict
          and type(compass["north_star"].get("evidence")) is list
          and type(compass.get("decision_horizon")) is list
          and type(compass.get("map_limits")) is list, "goal_compass_shape")
    _need(not any(type(item) is dict and item.get("id") == HORIZON_ID
                  for item in compass["decision_horizon"]), "goal_update_already_recorded")
    result = copy.deepcopy(compass)
    goal = payload["owner_confirmed_goal"]
    result["north_star"]["title"] = goal["product"]
    result["north_star"]["summary"] = (
        "Initial customer outcome: " + goal["initial_customer_outcome"] + ". "
        + " ".join(goal["product_principles"]) + " Pilot is excluded. " + goal["reuse_rule"]
    )
    prior_evidence = result["north_star"]["evidence"]
    if PAYLOAD_REFERENCE not in prior_evidence:
        prior_evidence.append(PAYLOAD_REFERENCE)
    result["orientation_statement"] = (
        goal["product"] + ": Reception One appointments and Diary first. "
        "G2 and G3 remain accepted with existing qualifications; G4 M1 remains partial. "
        "The roadmap records direction and dependencies only; current admission controls work."
    )
    prerequisites = []
    for step in payload["roadmap"]:
        prerequisite = (
            f"{step['step']}. {step['title']}: {step['outcome']} "
            + "Dependencies: " + "; ".join(step["depends_on"]) + ". "
            + "Qualification: " + step["qualification"]
        )
        pointer = step.get("sydney_plan_checkpoint_reference")
        if pointer is not None:
            # Copy the qualified navigation text only; never dereference it.
            prerequisite += (
                " Existing Sydney plan navigation: " + pointer["checkpoint_path"]
                + "#" + pointer["qualified_navigation_name"] + ". " + pointer["qualification"]
            )
        prerequisites.append(prerequisite)
    result["decision_horizon"].append({
        "id": HORIZON_ID,
        "title": "Confirmed commercial GPMSaaS goal and dependency roadmap",
        "status": "active",
        "strategic_question": "How does admitted Reception One work advance the confirmed commercial service goal while preserving current dependencies, maturity and deferrals?",
        "why_it_matters": PLAN_LIMIT,
        "prerequisites": prerequisites,
        "boundary_changes": [],
        "evidence": [PAYLOAD_REFERENCE],
    })
    result["map_limits"].append(PLAN_LIMIT)
    result["map_revision"] += 1
    result["updated_at"] = row["recorded_at"]
    return result
