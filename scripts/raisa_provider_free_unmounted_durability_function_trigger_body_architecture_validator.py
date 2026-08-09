"""Deterministic semantic validation for the durability typed body IR.

This module is deliberately offline.  It accepts an already parsed contract
dictionary, derives body effects and graph facts from typed operands, and never
renders SQL or contacts a database, source, provider, or network service.

The builder-facing API is intentionally small:

``derive_contract_semantics(contract)``
    Derive canonical summaries and the call graph.  Stored summaries are not
    trusted or compared by this function.

``validate_contract(contract)``
    Return a :class:`ValidationReport`, including deterministic issues, after
    comparing stored summaries and call edges with the derived values.

``assert_contract_valid(contract)``
    Return the passing report or raise :class:`ContractValidationError`.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
import hashlib
import json
import re
from typing import Any, Iterable, Mapping, Sequence


EXACT_ENTRY_POINTS = (
    "emr4_context_fabric.project_update_confirm_reschedule_v1",
    "emr4_context_fabric.admit_proofread_observation_v1",
    "emr4_context_fabric.apply_durability_transition_v1",
    "emr4_context_fabric.register_observer_generation_v1",
    "emr4_context_fabric.append_recovery_anchor_v1",
    "emr4_context_fabric.rotate_observation_key_v1",
    "emr4_context_fabric.consume_observer_generation_v1",
    "emr4_context_fabric.evaluate_source_retention_v1",
    "emr4_context_fabric.purge_source_rows_v1",
)

EXACT_TRIGGER_FUNCTIONS = (
    "emr4_context_fabric.cf_guard_claim_v1",
    "emr4_context_fabric.cf_fence_claim_v1",
    "emr4_context_fabric.cf_fence_appointment_update_v1",
    "emr4_context_fabric.cf_guard_audit_v1",
    "emr4_context_fabric.cf_fence_audit_v1",
    "emr4_context_fabric.cf_guard_event_v1",
    "emr4_context_fabric.cf_fence_event_v1",
    "emr4_context_fabric.cf_guard_alias_v1",
    "emr4_context_fabric.cf_fence_alias_v1",
    "emr4_context_fabric.cf_guard_stream_head_v1",
    "emr4_context_fabric.cf_fence_stream_head_v1",
    "emr4_context_fabric.cf_guard_outbox_v1",
    "emr4_context_fabric.cf_fence_outbox_v1",
)

EXACT_SUPPORT_FUNCTION = "emr4_context_fabric.session_binding_allows_v1"

EXACT_SIGNATURE_FIELD_MAP: tuple[Mapping[str, Any], ...] = tuple(
    json.loads(
        r"""
[
    {
        "group":  "support",
        "position":  0,
        "id":  "emr4_context_fabric.session_binding_allows_v1",
        "inputs":  [
                       {
                           "name":  "authenticated_login",
                           "mode":  "IN",
                           "type":  "pg_catalog.name"
                       },
                       {
                           "name":  "allowed_capabilities",
                           "mode":  "IN",
                           "type":  "emr4_context_fabric.logical_capability[]"
                       },
                       {
                           "name":  "requested_practice_id",
                           "mode":  "IN",
                           "type":  "pg_catalog.uuid"
                       },
                       {
                           "name":  "requested_source_contract_id",
                           "mode":  "IN",
                           "type":  "emr4_context_fabric.source_contract_code"
                       },
                       {
                           "name":  "requested_stream_id",
                           "mode":  "IN",
                           "type":  "pg_catalog.uuid"
                       },
                       {
                           "name":  "observed_at",
                           "mode":  "IN",
                           "type":  "pg_catalog.timestamptz"
                       }
                   ],
        "output":  {
                       "type":  "pg_catalog.boolean",
                       "cardinality":  "EXACTLY_ONE"
                   },
        "executor_field":  "executor_roles",
        "executor":  [
                         "emr4_context_fabric.context_schema_owner",
                         "emr4_context_fabric.context_admission_receiver",
                         "emr4_context_fabric.context_observer",
                         "emr4_context_fabric.context_producer",
                         "emr4_context_fabric.context_coordinator",
                         "emr4_context_fabric.context_lifecycle",
                         "emr4_context_fabric.context_retention",
                         "emr4_context_fabric.context_application_read"
                     ],
        "language":  "sql",
        "owner":  "emr4_context_fabric.context_schema_owner",
        "strict":  true,
        "volatility":  "STABLE",
        "parallel_safety":  "RESTRICTED",
        "security_definer":  true,
        "search_path":  [
                            "pg_catalog",
                            "emr4_context_fabric"
                        ],
        "public_execute":  false,
        "invariant_ids":  [

                          ]
    },
    {
        "group":  "entry_points",
        "position":  0,
        "id":  "emr4_context_fabric.project_update_confirm_reschedule_v1",
        "inputs":  [
                       {
                           "name":  "command_id",
                           "mode":  "IN",
                           "type":  "pg_catalog.uuid"
                       }
                   ],
        "output":  {
                       "type":  "emr4_context_fabric.diary_context_observation_outbox_v1",
                       "cardinality":  "EXACTLY_ONE"
                   },
        "executor_field":  "executor",
        "executor":  "emr4_context_fabric.context_producer",
        "language":  "plpgsql",
        "owner":  "emr4_context_fabric.context_schema_owner",
        "strict":  true,
        "volatility":  "VOLATILE",
        "parallel_safety":  "UNSAFE",
        "security_definer":  true,
        "search_path":  [
                            "pg_catalog",
                            "emr4_context_fabric"
                        ],
        "public_execute":  false,
        "invariant_ids":  [
                              "current_xid_provenance_v1",
                              "producer_temporal_bijection_v1",
                              "event_outbox_transaction_binding_v1",
                              "alias_immutable_bijection_v1",
                              "producer_stream_head_monotonic_v1"
                          ]
    },
    {
        "group":  "entry_points",
        "position":  1,
        "id":  "emr4_context_fabric.admit_proofread_observation_v1",
        "inputs":  [
                       {
                           "name":  "generation_locator",
                           "mode":  "IN",
                           "type":  "emr4_context_fabric.generation_locator_v1"
                       },
                       {
                           "name":  "source_position",
                           "mode":  "IN",
                           "type":  "pg_catalog.bigint"
                       },
                       {
                           "name":  "proofread_packet",
                           "mode":  "IN",
                           "type":  "emr4_context_fabric.proofread_packet_v1"
                       }
                   ],
        "output":  {
                       "type":  "emr4_context_fabric.context_proofread_observation_admission",
                       "cardinality":  "EXACTLY_ONE"
                   },
        "executor_field":  "executor",
        "executor":  "emr4_context_fabric.context_observer",
        "language":  "plpgsql",
        "owner":  "emr4_context_fabric.context_admission_receiver",
        "strict":  true,
        "volatility":  "VOLATILE",
        "parallel_safety":  "UNSAFE",
        "security_definer":  true,
        "search_path":  [
                            "pg_catalog",
                            "emr4_context_fabric"
                        ],
        "public_execute":  false,
        "invariant_ids":  [
                              "admission_bounded_immutable_v1",
                              "binding_one_active_v1"
                          ]
    },
    {
        "group":  "entry_points",
        "position":  2,
        "id":  "emr4_context_fabric.apply_durability_transition_v1",
        "inputs":  [
                       {
                           "name":  "admission_locator",
                           "mode":  "IN",
                           "type":  "emr4_context_fabric.admission_locator_v1"
                       }
                   ],
        "output":  {
                       "type":  "emr4_context_fabric.durability_transition_result_v1",
                       "cardinality":  "EXACTLY_ONE"
                   },
        "executor_field":  "executor",
        "executor":  "emr4_context_fabric.context_coordinator",
        "language":  "plpgsql",
        "owner":  "emr4_context_fabric.context_schema_owner",
        "strict":  true,
        "volatility":  "VOLATILE",
        "parallel_safety":  "UNSAFE",
        "security_definer":  true,
        "search_path":  [
                            "pg_catalog",
                            "emr4_context_fabric"
                        ],
        "public_execute":  false,
        "invariant_ids":  [
                              "admission_primary_receipt_binding_v1",
                              "anchor_fences_next_transition_v1",
                              "checkpoint_monotonic_terminal_v1",
                              "watermark_monotonic_bounded_v1",
                              "frame_one_way_retirement_v1",
                              "obligation_coalesced_derived_v1",
                              "lifecycle_gap_free_append_only_v1",
                              "audit_decision_only_append_v1"
                          ]
    },
    {
        "group":  "entry_points",
        "position":  3,
        "id":  "emr4_context_fabric.register_observer_generation_v1",
        "inputs":  [
                       {
                           "name":  "registration",
                           "mode":  "IN",
                           "type":  "emr4_context_fabric.generation_registration_v1"
                       }
                   ],
        "output":  {
                       "type":  "emr4_context_fabric.context_observer_generation",
                       "cardinality":  "EXACTLY_ONE"
                   },
        "executor_field":  "executor",
        "executor":  "emr4_context_fabric.context_lifecycle",
        "language":  "plpgsql",
        "owner":  "emr4_context_fabric.context_schema_owner",
        "strict":  true,
        "volatility":  "VOLATILE",
        "parallel_safety":  "UNSAFE",
        "security_definer":  true,
        "search_path":  [
                            "pg_catalog",
                            "emr4_context_fabric"
                        ],
        "public_execute":  false,
        "invariant_ids":  [
                              "registry_barrier_serialization_v1",
                              "generation_lifecycle_one_way_v1",
                              "key_partition_future_fenced_v1",
                              "anchor_append_only_v1"
                          ]
    },
    {
        "group":  "entry_points",
        "position":  4,
        "id":  "emr4_context_fabric.append_recovery_anchor_v1",
        "inputs":  [
                       {
                           "name":  "generation_locator",
                           "mode":  "IN",
                           "type":  "emr4_context_fabric.generation_locator_v1"
                       },
                       {
                           "name":  "lifecycle_revision",
                           "mode":  "IN",
                           "type":  "pg_catalog.bigint"
                       }
                   ],
        "output":  {
                       "type":  "emr4_context_fabric.context_recovery_anchor",
                       "cardinality":  "EXACTLY_ONE"
                   },
        "executor_field":  "executor",
        "executor":  "emr4_context_fabric.context_lifecycle",
        "language":  "plpgsql",
        "owner":  "emr4_context_fabric.context_schema_owner",
        "strict":  true,
        "volatility":  "VOLATILE",
        "parallel_safety":  "UNSAFE",
        "security_definer":  true,
        "search_path":  [
                            "pg_catalog",
                            "emr4_context_fabric"
                        ],
        "public_execute":  false,
        "invariant_ids":  [
                              "anchor_append_only_v1",
                              "anchor_fences_next_transition_v1"
                          ]
    },
    {
        "group":  "entry_points",
        "position":  5,
        "id":  "emr4_context_fabric.rotate_observation_key_v1",
        "inputs":  [
                       {
                           "name":  "generation_locator",
                           "mode":  "IN",
                           "type":  "emr4_context_fabric.generation_locator_v1"
                       },
                       {
                           "name":  "future_interval",
                           "mode":  "IN",
                           "type":  "emr4_context_fabric.future_key_interval_v1"
                       }
                   ],
        "output":  {
                       "type":  "emr4_context_fabric.context_observation_key_interval",
                       "cardinality":  "EXACTLY_ONE"
                   },
        "executor_field":  "executor",
        "executor":  "emr4_context_fabric.context_lifecycle",
        "language":  "plpgsql",
        "owner":  "emr4_context_fabric.context_schema_owner",
        "strict":  true,
        "volatility":  "VOLATILE",
        "parallel_safety":  "UNSAFE",
        "security_definer":  true,
        "search_path":  [
                            "pg_catalog",
                            "emr4_context_fabric"
                        ],
        "public_execute":  false,
        "invariant_ids":  [
                              "anchor_fences_next_transition_v1",
                              "key_partition_future_fenced_v1",
                              "lifecycle_gap_free_append_only_v1"
                          ]
    },
    {
        "group":  "entry_points",
        "position":  6,
        "id":  "emr4_context_fabric.consume_observer_generation_v1",
        "inputs":  [
                       {
                           "name":  "generation_locator",
                           "mode":  "IN",
                           "type":  "emr4_context_fabric.generation_locator_v1"
                       },
                       {
                           "name":  "closed_reason",
                           "mode":  "IN",
                           "type":  "emr4_context_fabric.generation_terminal_reason"
                       }
                   ],
        "output":  {
                       "type":  "emr4_context_fabric.context_observer_generation",
                       "cardinality":  "EXACTLY_ONE"
                   },
        "executor_field":  "executor",
        "executor":  "emr4_context_fabric.context_lifecycle",
        "language":  "plpgsql",
        "owner":  "emr4_context_fabric.context_schema_owner",
        "strict":  true,
        "volatility":  "VOLATILE",
        "parallel_safety":  "UNSAFE",
        "security_definer":  true,
        "search_path":  [
                            "pg_catalog",
                            "emr4_context_fabric"
                        ],
        "public_execute":  false,
        "invariant_ids":  [
                              "generation_lifecycle_one_way_v1"
                          ]
    },
    {
        "group":  "entry_points",
        "position":  7,
        "id":  "emr4_context_fabric.evaluate_source_retention_v1",
        "inputs":  [
                       {
                           "name":  "practice_source_stream",
                           "mode":  "IN",
                           "type":  "emr4_context_fabric.practice_source_stream_v1"
                       }
                   ],
        "output":  {
                       "type":  "emr4_context_fabric.context_source_retention_eligibility_v1",
                       "cardinality":  "EXACTLY_ONE"
                   },
        "executor_field":  "executor",
        "executor":  "emr4_context_fabric.context_retention",
        "language":  "plpgsql",
        "owner":  "emr4_context_fabric.context_schema_owner",
        "strict":  true,
        "volatility":  "VOLATILE",
        "parallel_safety":  "UNSAFE",
        "security_definer":  true,
        "search_path":  [
                            "pg_catalog",
                            "emr4_context_fabric"
                        ],
        "public_execute":  false,
        "invariant_ids":  [
                              "registry_barrier_serialization_v1",
                              "retention_complete_census_v1"
                          ]
    },
    {
        "group":  "entry_points",
        "position":  8,
        "id":  "emr4_context_fabric.purge_source_rows_v1",
        "inputs":  [
                       {
                           "name":  "practice_source_stream",
                           "mode":  "IN",
                           "type":  "emr4_context_fabric.practice_source_stream_v1"
                       },
                       {
                           "name":  "through_position",
                           "mode":  "IN",
                           "type":  "pg_catalog.bigint"
                       }
                   ],
        "output":  {
                       "type":  "emr4_context_fabric.context_source_purge_result_v1",
                       "cardinality":  "EXACTLY_ONE"
                   },
        "executor_field":  "executor",
        "executor":  "emr4_context_fabric.context_retention",
        "language":  "plpgsql",
        "owner":  "emr4_context_fabric.context_schema_owner",
        "strict":  true,
        "volatility":  "VOLATILE",
        "parallel_safety":  "UNSAFE",
        "security_definer":  true,
        "search_path":  [
                            "pg_catalog",
                            "emr4_context_fabric"
                        ],
        "public_execute":  false,
        "invariant_ids":  [
                              "registry_barrier_serialization_v1",
                              "retention_complete_census_v1",
                              "event_retention_independence_v1"
                          ]
    },
    {
        "group":  "trigger_functions",
        "position":  0,
        "id":  "emr4_context_fabric.cf_guard_claim_v1",
        "inputs":  [

                   ],
        "output":  {
                       "type":  "pg_catalog.trigger",
                       "cardinality":  "EXACTLY_ONE_OR_RAISE"
                   },
        "executor_field":  "executor",
        "executor":  "OWNER_INTERNAL",
        "language":  "plpgsql",
        "owner":  "emr4_context_fabric.context_schema_owner",
        "strict":  false,
        "volatility":  "VOLATILE",
        "parallel_safety":  "UNSAFE",
        "security_definer":  true,
        "search_path":  [
                            "pg_catalog",
                            "emr4_context_fabric"
                        ],
        "public_execute":  false,
        "invariant_ids":  [
                              "current_xid_provenance_v1"
                          ]
    },
    {
        "group":  "trigger_functions",
        "position":  1,
        "id":  "emr4_context_fabric.cf_fence_claim_v1",
        "inputs":  [

                   ],
        "output":  {
                       "type":  "pg_catalog.trigger",
                       "cardinality":  "EXACTLY_ONE_OR_RAISE"
                   },
        "executor_field":  "executor",
        "executor":  "OWNER_INTERNAL",
        "language":  "plpgsql",
        "owner":  "emr4_context_fabric.context_schema_owner",
        "strict":  false,
        "volatility":  "VOLATILE",
        "parallel_safety":  "UNSAFE",
        "security_definer":  true,
        "search_path":  [
                            "pg_catalog",
                            "emr4_context_fabric"
                        ],
        "public_execute":  false,
        "invariant_ids":  [
                              "current_xid_provenance_v1",
                              "producer_temporal_bijection_v1"
                          ]
    },
    {
        "group":  "trigger_functions",
        "position":  2,
        "id":  "emr4_context_fabric.cf_fence_appointment_update_v1",
        "inputs":  [

                   ],
        "output":  {
                       "type":  "pg_catalog.trigger",
                       "cardinality":  "EXACTLY_ONE_OR_RAISE"
                   },
        "executor_field":  "executor",
        "executor":  "OWNER_INTERNAL",
        "language":  "plpgsql",
        "owner":  "emr4_context_fabric.context_schema_owner",
        "strict":  false,
        "volatility":  "VOLATILE",
        "parallel_safety":  "UNSAFE",
        "security_definer":  true,
        "search_path":  [
                            "pg_catalog",
                            "emr4_context_fabric"
                        ],
        "public_execute":  false,
        "invariant_ids":  [
                              "producer_temporal_bijection_v1"
                          ]
    },
    {
        "group":  "trigger_functions",
        "position":  3,
        "id":  "emr4_context_fabric.cf_guard_audit_v1",
        "inputs":  [

                   ],
        "output":  {
                       "type":  "pg_catalog.trigger",
                       "cardinality":  "EXACTLY_ONE_OR_RAISE"
                   },
        "executor_field":  "executor",
        "executor":  "OWNER_INTERNAL",
        "language":  "plpgsql",
        "owner":  "emr4_context_fabric.context_schema_owner",
        "strict":  false,
        "volatility":  "VOLATILE",
        "parallel_safety":  "UNSAFE",
        "security_definer":  true,
        "search_path":  [
                            "pg_catalog",
                            "emr4_context_fabric"
                        ],
        "public_execute":  false,
        "invariant_ids":  [
                              "current_xid_provenance_v1"
                          ]
    },
    {
        "group":  "trigger_functions",
        "position":  4,
        "id":  "emr4_context_fabric.cf_fence_audit_v1",
        "inputs":  [

                   ],
        "output":  {
                       "type":  "pg_catalog.trigger",
                       "cardinality":  "EXACTLY_ONE_OR_RAISE"
                   },
        "executor_field":  "executor",
        "executor":  "OWNER_INTERNAL",
        "language":  "plpgsql",
        "owner":  "emr4_context_fabric.context_schema_owner",
        "strict":  false,
        "volatility":  "VOLATILE",
        "parallel_safety":  "UNSAFE",
        "security_definer":  true,
        "search_path":  [
                            "pg_catalog",
                            "emr4_context_fabric"
                        ],
        "public_execute":  false,
        "invariant_ids":  [
                              "producer_temporal_bijection_v1"
                          ]
    },
    {
        "group":  "trigger_functions",
        "position":  5,
        "id":  "emr4_context_fabric.cf_guard_event_v1",
        "inputs":  [

                   ],
        "output":  {
                       "type":  "pg_catalog.trigger",
                       "cardinality":  "EXACTLY_ONE_OR_RAISE"
                   },
        "executor_field":  "executor",
        "executor":  "OWNER_INTERNAL",
        "language":  "plpgsql",
        "owner":  "emr4_context_fabric.context_schema_owner",
        "strict":  false,
        "volatility":  "VOLATILE",
        "parallel_safety":  "UNSAFE",
        "security_definer":  true,
        "search_path":  [
                            "pg_catalog",
                            "emr4_context_fabric"
                        ],
        "public_execute":  false,
        "invariant_ids":  [
                              "current_xid_provenance_v1",
                              "event_retention_independence_v1"
                          ]
    },
    {
        "group":  "trigger_functions",
        "position":  6,
        "id":  "emr4_context_fabric.cf_fence_event_v1",
        "inputs":  [

                   ],
        "output":  {
                       "type":  "pg_catalog.trigger",
                       "cardinality":  "EXACTLY_ONE_OR_RAISE"
                   },
        "executor_field":  "executor",
        "executor":  "OWNER_INTERNAL",
        "language":  "plpgsql",
        "owner":  "emr4_context_fabric.context_schema_owner",
        "strict":  false,
        "volatility":  "VOLATILE",
        "parallel_safety":  "UNSAFE",
        "security_definer":  true,
        "search_path":  [
                            "pg_catalog",
                            "emr4_context_fabric"
                        ],
        "public_execute":  false,
        "invariant_ids":  [
                              "producer_temporal_bijection_v1",
                              "event_outbox_transaction_binding_v1"
                          ]
    },
    {
        "group":  "trigger_functions",
        "position":  7,
        "id":  "emr4_context_fabric.cf_guard_alias_v1",
        "inputs":  [

                   ],
        "output":  {
                       "type":  "pg_catalog.trigger",
                       "cardinality":  "EXACTLY_ONE_OR_RAISE"
                   },
        "executor_field":  "executor",
        "executor":  "OWNER_INTERNAL",
        "language":  "plpgsql",
        "owner":  "emr4_context_fabric.context_schema_owner",
        "strict":  false,
        "volatility":  "VOLATILE",
        "parallel_safety":  "UNSAFE",
        "security_definer":  true,
        "search_path":  [
                            "pg_catalog",
                            "emr4_context_fabric"
                        ],
        "public_execute":  false,
        "invariant_ids":  [
                              "alias_immutable_bijection_v1"
                          ]
    },
    {
        "group":  "trigger_functions",
        "position":  8,
        "id":  "emr4_context_fabric.cf_fence_alias_v1",
        "inputs":  [

                   ],
        "output":  {
                       "type":  "pg_catalog.trigger",
                       "cardinality":  "EXACTLY_ONE_OR_RAISE"
                   },
        "executor_field":  "executor",
        "executor":  "OWNER_INTERNAL",
        "language":  "plpgsql",
        "owner":  "emr4_context_fabric.context_schema_owner",
        "strict":  false,
        "volatility":  "VOLATILE",
        "parallel_safety":  "UNSAFE",
        "security_definer":  true,
        "search_path":  [
                            "pg_catalog",
                            "emr4_context_fabric"
                        ],
        "public_execute":  false,
        "invariant_ids":  [
                              "producer_temporal_bijection_v1"
                          ]
    },
    {
        "group":  "trigger_functions",
        "position":  9,
        "id":  "emr4_context_fabric.cf_guard_stream_head_v1",
        "inputs":  [

                   ],
        "output":  {
                       "type":  "pg_catalog.trigger",
                       "cardinality":  "EXACTLY_ONE_OR_RAISE"
                   },
        "executor_field":  "executor",
        "executor":  "OWNER_INTERNAL",
        "language":  "plpgsql",
        "owner":  "emr4_context_fabric.context_schema_owner",
        "strict":  false,
        "volatility":  "VOLATILE",
        "parallel_safety":  "UNSAFE",
        "security_definer":  true,
        "search_path":  [
                            "pg_catalog",
                            "emr4_context_fabric"
                        ],
        "public_execute":  false,
        "invariant_ids":  [
                              "producer_stream_head_monotonic_v1"
                          ]
    },
    {
        "group":  "trigger_functions",
        "position":  10,
        "id":  "emr4_context_fabric.cf_fence_stream_head_v1",
        "inputs":  [

                   ],
        "output":  {
                       "type":  "pg_catalog.trigger",
                       "cardinality":  "EXACTLY_ONE_OR_RAISE"
                   },
        "executor_field":  "executor",
        "executor":  "OWNER_INTERNAL",
        "language":  "plpgsql",
        "owner":  "emr4_context_fabric.context_schema_owner",
        "strict":  false,
        "volatility":  "VOLATILE",
        "parallel_safety":  "UNSAFE",
        "security_definer":  true,
        "search_path":  [
                            "pg_catalog",
                            "emr4_context_fabric"
                        ],
        "public_execute":  false,
        "invariant_ids":  [
                              "producer_temporal_bijection_v1",
                              "producer_stream_head_monotonic_v1"
                          ]
    },
    {
        "group":  "trigger_functions",
        "position":  11,
        "id":  "emr4_context_fabric.cf_guard_outbox_v1",
        "inputs":  [

                   ],
        "output":  {
                       "type":  "pg_catalog.trigger",
                       "cardinality":  "EXACTLY_ONE_OR_RAISE"
                   },
        "executor_field":  "executor",
        "executor":  "OWNER_INTERNAL",
        "language":  "plpgsql",
        "owner":  "emr4_context_fabric.context_schema_owner",
        "strict":  false,
        "volatility":  "VOLATILE",
        "parallel_safety":  "UNSAFE",
        "security_definer":  true,
        "search_path":  [
                            "pg_catalog",
                            "emr4_context_fabric"
                        ],
        "public_execute":  false,
        "invariant_ids":  [
                              "outbox_immutable_v1"
                          ]
    },
    {
        "group":  "trigger_functions",
        "position":  12,
        "id":  "emr4_context_fabric.cf_fence_outbox_v1",
        "inputs":  [

                   ],
        "output":  {
                       "type":  "pg_catalog.trigger",
                       "cardinality":  "EXACTLY_ONE_OR_RAISE"
                   },
        "executor_field":  "executor",
        "executor":  "OWNER_INTERNAL",
        "language":  "plpgsql",
        "owner":  "emr4_context_fabric.context_schema_owner",
        "strict":  false,
        "volatility":  "VOLATILE",
        "parallel_safety":  "UNSAFE",
        "security_definer":  true,
        "search_path":  [
                            "pg_catalog",
                            "emr4_context_fabric"
                        ],
        "public_execute":  false,
        "invariant_ids":  [
                              "producer_temporal_bijection_v1",
                              "event_outbox_transaction_binding_v1"
                          ]
    }
]
"""
    )
)

EXACT_TRIGGER_DECLARATION_FIELD_MAP: tuple[Mapping[str, Any], ...] = tuple(
    json.loads(
        r"""
[
    {
        "position":  0,
        "id":  "trg_cf_claim_guard",
        "function":  "emr4_context_fabric.cf_guard_claim_v1",
        "relation":  "public.appointment_command_idempotency",
        "timing":  "BEFORE",
        "row_level":  true,
        "events":  [
                       "UPDATE",
                       "DELETE"
                   ],
        "deferrable":  false,
        "initially_deferred":  false,
        "invariant_ids":  [
                              "current_xid_provenance_v1"
                          ]
    },
    {
        "position":  1,
        "id":  "trg_cf_claim_fence",
        "function":  "emr4_context_fabric.cf_fence_claim_v1",
        "relation":  "public.appointment_command_idempotency",
        "timing":  "AFTER",
        "row_level":  true,
        "events":  [
                       "INSERT",
                       "UPDATE",
                       "DELETE"
                   ],
        "deferrable":  true,
        "initially_deferred":  true,
        "invariant_ids":  [
                              "current_xid_provenance_v1",
                              "producer_temporal_bijection_v1"
                          ]
    },
    {
        "position":  2,
        "id":  "trg_cf_appointment_fence",
        "function":  "emr4_context_fabric.cf_fence_appointment_update_v1",
        "relation":  "public.appointments",
        "timing":  "AFTER",
        "row_level":  true,
        "events":  [
                       "UPDATE"
                   ],
        "deferrable":  true,
        "initially_deferred":  true,
        "invariant_ids":  [
                              "producer_temporal_bijection_v1"
                          ]
    },
    {
        "position":  3,
        "id":  "trg_cf_audit_guard",
        "function":  "emr4_context_fabric.cf_guard_audit_v1",
        "relation":  "public.appointment_audit_log",
        "timing":  "BEFORE",
        "row_level":  true,
        "events":  [
                       "UPDATE",
                       "DELETE"
                   ],
        "deferrable":  false,
        "initially_deferred":  false,
        "invariant_ids":  [
                              "current_xid_provenance_v1"
                          ]
    },
    {
        "position":  4,
        "id":  "trg_cf_audit_fence",
        "function":  "emr4_context_fabric.cf_fence_audit_v1",
        "relation":  "public.appointment_audit_log",
        "timing":  "AFTER",
        "row_level":  true,
        "events":  [
                       "INSERT",
                       "UPDATE",
                       "DELETE"
                   ],
        "deferrable":  true,
        "initially_deferred":  true,
        "invariant_ids":  [
                              "producer_temporal_bijection_v1"
                          ]
    },
    {
        "position":  5,
        "id":  "trg_cf_event_guard",
        "function":  "emr4_context_fabric.cf_guard_event_v1",
        "relation":  "public.diary_committed_events",
        "timing":  "BEFORE",
        "row_level":  true,
        "events":  [
                       "UPDATE",
                       "DELETE"
                   ],
        "deferrable":  false,
        "initially_deferred":  false,
        "invariant_ids":  [
                              "current_xid_provenance_v1",
                              "event_retention_independence_v1"
                          ]
    },
    {
        "position":  6,
        "id":  "trg_cf_event_fence",
        "function":  "emr4_context_fabric.cf_fence_event_v1",
        "relation":  "public.diary_committed_events",
        "timing":  "AFTER",
        "row_level":  true,
        "events":  [
                       "INSERT",
                       "UPDATE",
                       "DELETE"
                   ],
        "deferrable":  true,
        "initially_deferred":  true,
        "invariant_ids":  [
                              "producer_temporal_bijection_v1",
                              "event_outbox_transaction_binding_v1"
                          ]
    },
    {
        "position":  7,
        "id":  "trg_cf_alias_guard",
        "function":  "emr4_context_fabric.cf_guard_alias_v1",
        "relation":  "emr4_context_fabric.diary_context_aggregate_aliases_v1",
        "timing":  "BEFORE",
        "row_level":  true,
        "events":  [
                       "UPDATE",
                       "DELETE"
                   ],
        "deferrable":  false,
        "initially_deferred":  false,
        "invariant_ids":  [
                              "alias_immutable_bijection_v1"
                          ]
    },
    {
        "position":  8,
        "id":  "trg_cf_alias_fence",
        "function":  "emr4_context_fabric.cf_fence_alias_v1",
        "relation":  "emr4_context_fabric.diary_context_aggregate_aliases_v1",
        "timing":  "AFTER",
        "row_level":  true,
        "events":  [
                       "INSERT",
                       "UPDATE",
                       "DELETE"
                   ],
        "deferrable":  true,
        "initially_deferred":  true,
        "invariant_ids":  [
                              "producer_temporal_bijection_v1"
                          ]
    },
    {
        "position":  9,
        "id":  "trg_cf_head_guard",
        "function":  "emr4_context_fabric.cf_guard_stream_head_v1",
        "relation":  "emr4_context_fabric.context_observation_stream_head",
        "timing":  "BEFORE",
        "row_level":  true,
        "events":  [
                       "UPDATE",
                       "DELETE"
                   ],
        "deferrable":  false,
        "initially_deferred":  false,
        "invariant_ids":  [
                              "producer_stream_head_monotonic_v1"
                          ]
    },
    {
        "position":  10,
        "id":  "trg_cf_head_fence",
        "function":  "emr4_context_fabric.cf_fence_stream_head_v1",
        "relation":  "emr4_context_fabric.context_observation_stream_head",
        "timing":  "AFTER",
        "row_level":  true,
        "events":  [
                       "INSERT",
                       "UPDATE",
                       "DELETE"
                   ],
        "deferrable":  true,
        "initially_deferred":  true,
        "invariant_ids":  [
                              "producer_temporal_bijection_v1",
                              "producer_stream_head_monotonic_v1"
                          ]
    },
    {
        "position":  11,
        "id":  "trg_cf_outbox_guard",
        "function":  "emr4_context_fabric.cf_guard_outbox_v1",
        "relation":  "emr4_context_fabric.diary_context_observation_outbox_v1",
        "timing":  "BEFORE",
        "row_level":  true,
        "events":  [
                       "UPDATE",
                       "DELETE"
                   ],
        "deferrable":  false,
        "initially_deferred":  false,
        "invariant_ids":  [
                              "outbox_immutable_v1"
                          ]
    },
    {
        "position":  12,
        "id":  "trg_cf_outbox_fence",
        "function":  "emr4_context_fabric.cf_fence_outbox_v1",
        "relation":  "emr4_context_fabric.diary_context_observation_outbox_v1",
        "timing":  "AFTER",
        "row_level":  true,
        "events":  [
                       "INSERT",
                       "UPDATE",
                       "DELETE"
                   ],
        "deferrable":  true,
        "initially_deferred":  true,
        "invariant_ids":  [
                              "producer_temporal_bijection_v1",
                              "event_outbox_transaction_binding_v1"
                          ]
    }
]
"""
    )
)


EXACT_PARENT_BINDING = {
    "path": (
        "orchestration/continuity/raisa-provider-free-unmounted-durability-"
        "migration-transaction-architecture/migration-transaction-architecture-"
        "contract.json"
    ),
    "contract_sha256": (
        "sha256:a79be2598a3e3c5a8636ab8a1c16c06523ce9716d2387764cfecc1004ff5d14e"
    ),
    "relation_signature_trigger_and_role_authority": (
        "RETAINED_EXCEPT_EXPLICIT_RECOVERY_OPERATIONS"
    ),
}

EXACT_ENUM_VALUES: dict[str, tuple[str, ...]] = {
    "emr4_context_fabric.admission_entry_kind": ("PRIMARY", "CONFLICT"),
    "emr4_context_fabric.observation_decision": (
        "ADMIT_SELECTIVE",
        "ADMIT_NO_INTERSECTION",
        "ADMIT_FULL_INVALIDATION",
        "REBASE_REQUIRED",
    ),
    "emr4_context_fabric.observation_reason": (
        "RELEVANT_INTERSECTION",
        "NO_INTERSECTION",
        "FULL_SCOPE",
        "COVERAGE_GAP",
        "SAME_POSITION_MISMATCH",
        "DIGEST_REUSE",
        "WRONG_PREDECESSOR",
        "WRONG_EPOCH",
        "MISSING_ADMISSION",
        "KEY_UNAVAILABLE",
        "MALFORMED_OR_FOREIGN",
    ),
    "emr4_context_fabric.checkpoint_disposition": (
        "ADVANCE",
        "HOLD_REBASE",
        "STOP_GENERATION",
    ),
    "emr4_context_fabric.admission_conflict_reason": (
        "POSITION_DIGEST_MISMATCH",
        "OBSERVATION_DIGEST_REUSE",
    ),
    "emr4_context_fabric.generation_state": (
        "ACTIVE",
        "REBASE_REQUIRED",
        "REVOKED",
        "CONSUMED",
    ),
    "emr4_context_fabric.checkpoint_state": (
        "ACTIVE",
        "REBASE_REQUIRED",
        "REVOKED",
        "CONSUMED",
    ),
    "emr4_context_fabric.frame_type": (
        "CURRENT_DIARY_PROJECTION",
        "CURRENT_WAITING_ROOM_PROJECTION",
    ),
    "emr4_context_fabric.frame_lifecycle": ("CURRENT", "RETIRED"),
    "emr4_context_fabric.obligation_count_bucket": (
        "ONE",
        "TWO_TO_FOUR",
        "FIVE_PLUS",
    ),
    "emr4_context_fabric.obligation_state": ("PENDING", "COMPLETED"),
    "emr4_context_fabric.lifecycle_entry_kind": ("DECISION", "KEY_ROTATION"),
    "emr4_context_fabric.retention_family": (
        "SOURCE",
        "RECEIPT_CHECKPOINT",
        "AUDIT",
    ),
    "emr4_context_fabric.recovery_pin_reason": (
        "RECOVERY",
        "AUDIT_REVIEW",
        "KEY_OVERLAP",
        "LEGAL_HOLD",
    ),
    "emr4_context_fabric.recovery_pin_state": ("ACTIVE", "RELEASED"),
    "emr4_context_fabric.logical_capability": (
        "PRODUCER",
        "OBSERVER",
        "COORDINATOR",
        "LIFECYCLE",
        "RETENTION",
        "APPLICATION_READ",
    ),
    "emr4_context_fabric.generation_terminal_reason": (
        "REVOKED",
        "CONTINUITY_LOSS",
        "KEY_LOSS",
        "DISABLED",
    ),
    "emr4_context_fabric.durability_transition_result_kind": (
        "RECEIPT_APPLIED",
        "RECEIPT_REPLAYED",
        "REBASE_APPLIED",
        "TERMINAL_REPLAYED",
    ),
    "emr4_context_fabric.source_retention_reason": (
        "ELIGIBLE",
        "EXECUTION_DISABLED",
        "CHECKPOINT_LAG",
        "ACTIVE_PIN",
        "KEY_OVERLAP",
        "GRACE_PENDING",
        "AMBIGUOUS_CENSUS",
        "NO_NON_CONSUMED_GENERATION",
    ),
}

EXACT_NORMATIVE_SECTION_SHA256 = {
    "structural_feasibility_recovery_v1": (
        "46b228799ed3aa07bad5011f9e3bf5c6c5b772b2984fa1531a0a9655b2a8793e"
    ),
    "effective_parent_summary": (
        "f60fdeefb4a6ffd14baa3a5f2ad8398d6dd492715b8967cae580c884c5fa317e"
    ),
    "qualified_identifier_catalogue": (
        "e2d0dda1b69f16e5f1b5fe84e3ce236e6daf4ec00fd83d39871ca2b1a7dc5a5c"
    ),
    "typed_ir_contract": (
        "8fe96965938bb91a34720a0b65672488d308c3b6df8267f368939c4ee8d7b3ff"
    ),
    "trigger_applicability_return_matrix": (
        "03a9f8aacbdbf7ed9eabc3b58d5f90beea5fe8fb64e6b36b1c373672a3735906"
    ),
    "renderer_order": (
        "ee78010dfee3a56bcf19f7d0348b4f52ac1e534b5a48098ca9cfb441915954cd"
    ),
    "artifact_boundary": (
        "0b313c144ebef5c90f804acb3b10bedc6ef5643c7857887cc4785ae3d21d9a1d"
    ),
}

_EXACT_PRODUCER_EVENT_PROOF_SHA256 = (
    "b0f5cb5144b5a1d03457a4eafcc536a67440ceeede0a1dd343c4b094d0ea2867"
)


def _canonical_sha256(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


INSTRUCTION_OPCODES = frozenset(
    {
        "ASSERT_ISOLATION",
        "DERIVE_BINDING",
        "SELECT_EXACT",
        "SELECT_SET",
        "LOCK_EXACT",
        "LET",
        "ASSERT",
        "IF",
        "SWITCH_TG_OP",
        "FOR_EACH",
        "INSERT",
        "INSERT_OR_RELOAD_COMPARE",
        "UPDATE",
        "DELETE_SOURCE",
        "CALL_SUPPORT",
        "RETURN_ROW",
        "RETURN_COMPOSITE",
        "RETURN_NEW",
        "RETURN_OLD",
        "RETURN_NULL",
        "RAISE",
        "PROPAGATE_RETRYABLE",
    }
)

EXPRESSION_OPCODES = frozenset(
    {
        "REF",
        "CONST",
        "ARRAY_CONST",
        "FIELD",
        "COMPOSITE_CONSTRUCT",
        "SESSION_USER",
        "TRANSACTION_TIMESTAMP",
        "CURRENT_XID32",
        "SYSTEM_XMIN",
        "GEN_RANDOM_UUID",
        "NOT",
        "IS_NULL",
        "IS_NOT_NULL",
        "COUNT",
        "MIN_FIELD",
        "SET_CONTAINS_KEY",
        "SET_COVERS_KEYS",
        "EQ",
        "NE",
        "LT",
        "LTE",
        "GT",
        "GTE",
        "IS_DISTINCT_FROM",
        "ADD",
        "SUBTRACT",
        "TIMESTAMP_ADD_MINUTES",
        "TIMESTAMP_ADD_SECONDS",
        "AND",
        "OR",
        "JSON_GET_CAST",
        "JSON_KEYS_EXACT",
        "CANONICAL_DIGEST",
        "CASE",
    }
)

_BANNED_OPS = frozenset(
    {
        "PROFILE_EVAL",
        "DERIVE_COLUMN_VALUE",
        "EXECUTE",
        "EXECUTE_SQL",
        "RAW_SQL",
        "DYNAMIC_SQL",
        "TRANSACTION_CONTROL",
        "BEGIN",
        "COMMIT",
        "ROLLBACK",
        "SAVEPOINT",
        "DDL",
        "CREATE",
        "ALTER",
        "DROP",
        "GRANT",
        "REVOKE",
    }
)

_BANNED_NODE_KEYS = frozenset(
    {
        "effect",
        "effects",
        "semantic_id",
        "profile_ref",
        "predicate_ref",
        "statement",
        "sql",
        "raw_sql",
        "dynamic_sql",
        "query",
        "template",
        "transaction_control",
        "ddl",
    }
)

_RETRYABLE_SQLSTATES = ("40001", "40P01")
_BOOLEAN_TYPE = "pg_catalog.boolean"
_BIGINT_TYPE = "pg_catalog.bigint"
_INTEGER_TYPES = frozenset(
    {"pg_catalog.smallint", "pg_catalog.integer", "pg_catalog.bigint"}
)
_TIMESTAMP_TYPE = "pg_catalog.timestamptz"
_UUID_TYPE = "pg_catalog.uuid"
_XID_TYPE = "pg_catalog.xid"

_GENERATION_SET_RELATION = "emr4_context_fabric.context_observer_generation"
_GENERATION_COORDINATE_PAIRS = (
    ("practice_id", "practice_id"),
    ("source_contract_id", "source_contract_id"),
    ("stream_id", "stream_id"),
    ("stream_epoch", "stream_epoch"),
    ("observer_id", "observer_id"),
    ("observer_generation", "observer_generation"),
)
_PIN_GENERATION_COORDINATE_PAIRS = (
    ("practice_id", "practice_id"),
    ("source_contract_id", "source_contract_id"),
    ("stream_id", "stream_id"),
    ("observer_id", "observer_id"),
    ("observer_generation", "observer_generation"),
)
_EXACT_SET_CONTAINS_KEY_PAIRS = {
    "emr4_context_fabric.context_durability_checkpoint": (_GENERATION_COORDINATE_PAIRS),
    "emr4_context_fabric.context_recovery_anchor": (_GENERATION_COORDINATE_PAIRS),
    "emr4_context_fabric.context_observation_key_interval": (
        _GENERATION_COORDINATE_PAIRS
    ),
    "emr4_context_fabric.context_classified_observation_receipt": (
        _GENERATION_COORDINATE_PAIRS
    ),
    "emr4_context_fabric.context_durability_audit": (_GENERATION_COORDINATE_PAIRS),
    "emr4_context_fabric.context_recovery_pin": (_PIN_GENERATION_COORDINATE_PAIRS),
}
_COVERAGE_EVIDENCE_RELATION = "emr4_context_fabric.context_observation_key_interval"

_SQL_TEXT = re.compile(
    r"(?:;|\$\$|--|/\*|\b(?:CREATE|ALTER|DROP|GRANT|REVOKE|EXECUTE|"
    r"BEGIN|COMMIT|ROLLBACK|SAVEPOINT)\b)",
    re.IGNORECASE,
)


@dataclass(frozen=True, order=True)
class ValidationIssue:
    """One deterministic contract error."""

    path: str
    code: str
    message: str


class ContractValidationError(ValueError):
    """Raised by builder-facing assertion/derivation helpers."""

    def __init__(self, issues: Sequence[ValidationIssue]) -> None:
        self.issues = tuple(sorted(set(issues)))
        rendered = "; ".join(
            f"{issue.path}: {issue.code}: {issue.message}" for issue in self.issues
        )
        super().__init__(rendered or "contract validation failed")


@dataclass(frozen=True)
class BodyAnalysis:
    """Canonical derived evidence for one body."""

    body_id: str
    summary: dict[str, Any]
    path_summaries: tuple[dict[str, Any], ...]
    call_edges: tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class ValidationReport:
    """Result returned by :func:`validate_contract`."""

    valid: bool
    issues: tuple[ValidationIssue, ...]
    body_summaries: dict[str, dict[str, Any]]
    path_summaries: dict[str, tuple[dict[str, Any], ...]]
    call_edges: tuple[dict[str, str], ...]


@dataclass
class _Effects:
    reads: dict[str, set[str]] = field(default_factory=dict)
    locks: list[dict[str, Any]] = field(default_factory=list)
    inserts: dict[str, set[str]] = field(default_factory=dict)
    updates: dict[str, set[str]] = field(default_factory=dict)
    deletes: dict[str, set[str]] = field(default_factory=dict)
    calls: set[str] = field(default_factory=set)
    failures: set[str] = field(default_factory=set)
    terminals: set[str] = field(default_factory=set)
    row_images: dict[tuple[str, str, str], set[str]] = field(default_factory=dict)

    def clone(self) -> _Effects:
        return deepcopy(self)

    def merge(self, other: _Effects) -> None:
        for relation, columns in other.reads.items():
            self.reads.setdefault(relation, set()).update(columns)
        for relation, columns in other.inserts.items():
            self.inserts.setdefault(relation, set()).update(columns)
        for relation, columns in other.updates.items():
            self.updates.setdefault(relation, set()).update(columns)
        for relation, columns in other.deletes.items():
            self.deletes.setdefault(relation, set()).update(columns)
        for lock in other.locks:
            if lock not in self.locks:
                self.locks.append(deepcopy(lock))
        self.calls.update(other.calls)
        self.failures.update(other.failures)
        self.terminals.update(other.terminals)
        for key, columns in other.row_images.items():
            self.row_images.setdefault(key, set()).update(columns)


@dataclass
class _FlowState:
    assigned: set[str]
    row_columns: dict[str, tuple[str, set[str]]]
    tg_ops: frozenset[str]
    trigger_relation: str | None = None
    effects: _Effects = field(default_factory=_Effects)
    terminal: str | None = None
    output: dict[str, str] | None = None
    trail: tuple[str, ...] = ()

    def clone(self, suffix: str | None = None) -> _FlowState:
        trail = self.trail if suffix is None else (*self.trail, suffix)
        return _FlowState(
            assigned=set(self.assigned),
            row_columns={
                symbol: (relation, set(columns))
                for symbol, (relation, columns) in self.row_columns.items()
            },
            tg_ops=self.tg_ops,
            trigger_relation=self.trigger_relation,
            effects=self.effects.clone(),
            terminal=self.terminal,
            output=deepcopy(self.output),
            trail=trail,
        )


@dataclass(frozen=True)
class _ExprResult:
    type_name: str | None
    source_reads: tuple[tuple[str, str], ...] = ()
    row_images: tuple[tuple[str, str, str, str], ...] = ()


class _SemanticValidator:
    def __init__(self, contract: Mapping[str, Any], *, compare_stored: bool) -> None:
        self.contract = contract
        self.compare_stored = compare_stored
        self.issues: list[ValidationIssue] = []
        self.relations: dict[str, tuple[str, ...]] = {}
        self.column_types: dict[str, dict[str, str]] = {}
        self.composite_fields: dict[str, dict[str, str]] = {}
        self.types: set[str] = set()
        self.failures: set[str] = set()
        self.signatures: dict[str, Mapping[str, Any]] = {}
        self.support_ids: set[str] = set()
        self.entry_ids: set[str] = set()
        self.trigger_ids: set[str] = set()
        self.declarations: dict[str, Mapping[str, Any]] = {}
        self.trigger_matrix: dict[str, Mapping[str, Any]] = {}
        self.body_analyses: dict[str, BodyAnalysis] = {}
        self._body_kind: dict[str, str] = {}
        self._program_node_ids: set[str] = set()

    def issue(self, path: str, code: str, message: str) -> None:
        self.issues.append(ValidationIssue(path, code, message))

    def run(self) -> ValidationReport:
        if not isinstance(self.contract, Mapping):
            self.issue("$", "contract_type", "contract must be an object")
            return self.report()
        self._validate_normative_envelope()
        self._load_catalogue()
        self._load_failures()
        self._load_signatures()
        self._load_triggers()
        self._validate_typed_ir_declarations()
        self._validate_program_population()
        self._validate_programs()
        self._validate_graph()
        return self.report()

    def _validate_normative_envelope(self) -> None:
        """Bind R4 normative authority without whole-candidate byte equality."""

        if (
            "parent_binding" not in self.contract
            and "structural_feasibility_recovery_v1" not in self.contract
        ):
            return
        if self.contract.get("schema_version") != (
            "raisa.context_fabric.function_trigger_body_architecture.v3"
        ):
            self.issue(
                "$.schema_version",
                "normative_schema_version",
                "the exact v3 typed-body schema version is required",
            )
        if self.contract.get("status") != "architecture_only_unmounted_typed_ir":
            self.issue(
                "$.status",
                "normative_status",
                "the exact unmounted architecture-only status is required",
            )
        if self.contract.get("parent_binding") != EXACT_PARENT_BINDING:
            self.issue(
                "$.parent_binding",
                "parent_binding_mismatch",
                "parent path, immutable digest, and retained-authority rule must be exact",
            )
        for section, expected_digest in EXACT_NORMATIVE_SECTION_SHA256.items():
            actual_digest = _canonical_sha256(self.contract.get(section))
            if actual_digest != expected_digest:
                self.issue(
                    f"$.{section}",
                    "normative_section_mismatch",
                    f"{section} differs from its independently frozen scalar envelope",
                )

        recovery = self.contract.get("structural_feasibility_recovery_v1")
        operations = (
            recovery.get("operations") if isinstance(recovery, Mapping) else None
        )
        expected_ids = [f"REC{index:02d}" for index in range(1, 27)]
        if (
            not isinstance(operations, list)
            or [
                operation.get("id") if isinstance(operation, Mapping) else None
                for operation in operations
            ]
            != expected_ids
        ):
            self.issue(
                "$.structural_feasibility_recovery_v1.operations",
                "recovery_operation_order",
                "recovery must contain exact ordered REC01 through REC26",
            )
        elif operations[18] != {
            "id": "REC19",
            "kind": "ADD_ENUM",
            "target": "emr4_context_fabric.source_retention_reason",
            "values": list(
                EXACT_ENUM_VALUES["emr4_context_fabric.source_retention_reason"]
            ),
        }:
            self.issue(
                "$.structural_feasibility_recovery_v1.operations[18]",
                "retention_reason_vocabulary",
                "REC19 must equal the exact ordered retention-reason vocabulary",
            )

        parent = self.contract.get("effective_parent_summary")
        signatures = (
            parent.get("effective_signatures") if isinstance(parent, Mapping) else None
        )
        signature_rows: list[Any] = []
        if isinstance(signatures, Mapping):
            signature_rows.append(signatures.get("support"))
            for group in ("entry_points", "trigger_functions"):
                rows = signatures.get(group)
                if isinstance(rows, list):
                    signature_rows.extend(rows)
        if len(signature_rows) != 23 or any(
            not isinstance(row, Mapping) or row.get("public_execute") is not False
            for row in signature_rows
        ):
            self.issue(
                "$.effective_parent_summary.effective_signatures",
                "public_execute_denial",
                "support and all twenty-two full signatures must deny PUBLIC execute",
            )

        roles = parent.get("effective_roles") if isinstance(parent, Mapping) else None
        if not isinstance(roles, list):
            self.issue(
                "$.effective_parent_summary.effective_roles",
                "effective_roles",
                "the exact effective role matrix is required",
            )
        else:
            outbox = "emr4_context_fabric.diary_context_observation_outbox_v1"
            product_prefix = "public."
            trigger_ids = set(EXACT_TRIGGER_FUNCTIONS)
            for index, role in enumerate(roles):
                if not isinstance(role, Mapping):
                    continue
                role_path = f"$.effective_parent_summary.effective_roles[{index}]"
                for grant in role.get("direct_table_dml", []):
                    if not isinstance(grant, Mapping):
                        continue
                    privileges = grant.get("privileges")
                    relation = grant.get("relation")
                    if (
                        relation == outbox
                        and isinstance(privileges, list)
                        and ("DELETE" in privileges)
                    ):
                        self.issue(
                            role_path,
                            "outbox_delete_privilege",
                            "no effective role receives direct outbox DELETE",
                        )
                    if (
                        isinstance(relation, str)
                        and relation.startswith(product_prefix)
                        and privileges
                    ):
                        self.issue(
                            role_path,
                            "product_dml_privilege",
                            "no effective role receives product DML",
                        )
                if role.get("runtime_role") is True:
                    direct_select = role.get("direct_table_select")
                    if isinstance(direct_select, list) and any(
                        isinstance(relation, str)
                        and relation.startswith(product_prefix)
                        for relation in direct_select
                    ):
                        self.issue(
                            role_path,
                            "runtime_product_read",
                            "runtime roles receive no direct product-table read",
                        )
                    execute = role.get("execute_entry_points")
                    if isinstance(execute, list) and trigger_ids.intersection(execute):
                        self.issue(
                            role_path,
                            "runtime_trigger_execute",
                            "runtime roles receive no trigger-function execute authority",
                        )

        programs = self.contract.get("body_programs")
        producer = None
        if isinstance(programs, list):
            producer = next(
                (
                    program
                    for program in programs
                    if isinstance(program, Mapping)
                    and program.get("id") == EXACT_ENTRY_POINTS[0]
                ),
                None,
            )
        ast = producer.get("ast") if isinstance(producer, Mapping) else None
        nodes = ast.get("nodes") if isinstance(ast, Mapping) else None
        event_proof = None
        if isinstance(nodes, list):
            event_proof = next(
                (
                    node
                    for node in nodes
                    if isinstance(node, Mapping)
                    and node.get("node_id")
                    == ("emr4_context_fabric.project_update_confirm_reschedule_v1.p12")
                ),
                None,
            )
        if _canonical_sha256(event_proof) != _EXACT_PRODUCER_EVENT_PROOF_SHA256:
            self.issue(
                "$.body_programs[0].ast.nodes",
                "producer_event_membership_proof",
                "the exact central producer event-membership assertion is required",
            )

    def report(self) -> ValidationReport:
        issues = tuple(sorted(set(self.issues)))
        summaries = {
            body_id: deepcopy(analysis.summary)
            for body_id, analysis in sorted(self.body_analyses.items())
        }
        paths = {
            body_id: analysis.path_summaries
            for body_id, analysis in sorted(self.body_analyses.items())
        }
        edges = sorted(
            {
                edge
                for analysis in self.body_analyses.values()
                for edge in analysis.call_edges
            }
        )
        return ValidationReport(
            valid=not issues,
            issues=issues,
            body_summaries=summaries,
            path_summaries=paths,
            call_edges=tuple(
                {"from": source, "to": target} for source, target in edges
            ),
        )

    def _load_catalogue(self) -> None:
        path = "$.qualified_identifier_catalogue"
        catalogue = self.contract.get("qualified_identifier_catalogue")
        if not isinstance(catalogue, Mapping):
            self.issue(
                path, "catalogue_missing", "qualified catalogue must be an object"
            )
            return
        relations = catalogue.get("relations")
        columns = catalogue.get("column_types")
        composite_fields = catalogue.get("composite_fields")
        types = catalogue.get("types")
        if not isinstance(relations, Mapping):
            self.issue(
                f"{path}.relations", "relations_type", "relations must be an object"
            )
            relations = {}
        if not isinstance(columns, Mapping):
            self.issue(
                f"{path}.column_types",
                "column_types_type",
                "column_types must be an object",
            )
            columns = {}
        if not isinstance(types, list) or not all(
            isinstance(item, str) for item in types
        ):
            self.issue(f"{path}.types", "types_type", "types must be a string array")
            types = []
        if not isinstance(composite_fields, Mapping):
            self.issue(
                f"{path}.composite_fields",
                "composite_fields_type",
                "composite_fields must be an object",
            )
            composite_fields = {}
        self.types = set(types)
        for index, type_name in enumerate(types):
            if not self._qualified(type_name):
                self.issue(
                    f"{path}.types[{index}]",
                    "unqualified_type",
                    f"type {type_name!r} is not qualified",
                )
        for relation, relation_columns in relations.items():
            relation_path = f"{path}.relations[{relation!r}]"
            if not isinstance(relation, str) or not self._qualified(relation):
                self.issue(
                    relation_path, "unqualified_relation", "relation must be qualified"
                )
                continue
            if not isinstance(relation_columns, list) or not all(
                isinstance(column, str) and column for column in relation_columns
            ):
                self.issue(
                    relation_path,
                    "relation_columns",
                    "columns must be non-empty strings",
                )
                continue
            if len(set(relation_columns)) != len(relation_columns):
                self.issue(
                    relation_path, "duplicate_column", "relation columns must be unique"
                )
            self.relations[relation] = tuple(relation_columns)
            typed = columns.get(relation)
            if not isinstance(typed, Mapping):
                self.issue(
                    relation_path,
                    "missing_column_types",
                    "relation needs a column type map",
                )
                continue
            self.column_types[relation] = {}
            if set(typed) != set(relation_columns):
                self.issue(
                    relation_path,
                    "column_type_closure",
                    "column type keys must exactly equal relation columns",
                )
            for column, type_name in typed.items():
                if not isinstance(type_name, str) or not self._known_type(type_name):
                    self.issue(
                        f"{relation_path}.{column}",
                        "unknown_column_type",
                        f"unknown type {type_name!r}",
                    )
                else:
                    self.column_types[relation][column] = type_name
        for composite_type, fields in composite_fields.items():
            composite_path = f"{path}.composite_fields[{composite_type!r}]"
            if not isinstance(composite_type, str) or not self._known_type(
                composite_type
            ):
                self.issue(
                    composite_path,
                    "composite_type_unknown",
                    "composite type must be qualified and catalogued",
                )
                continue
            if not isinstance(fields, Mapping) or not fields:
                self.issue(
                    composite_path,
                    "composite_fields",
                    "composite field map must be a non-empty object",
                )
                continue
            typed_fields: dict[str, str] = {}
            for field_name, field_type in fields.items():
                field_path = f"{composite_path}.{field_name}"
                if not isinstance(field_name, str) or not field_name:
                    self.issue(
                        field_path,
                        "composite_field_name",
                        "field name must be non-empty",
                    )
                    continue
                if not self._known_type(field_type):
                    self.issue(
                        field_path,
                        "composite_field_type_unknown",
                        f"field type {field_type!r} is not catalogued",
                    )
                    continue
                typed_fields[field_name] = field_type
            self.composite_fields[composite_type] = typed_fields

    def _load_failures(self) -> None:
        registry = self.contract.get("failure_registry")
        if not isinstance(registry, list):
            self.issue(
                "$.failure_registry",
                "failure_registry_type",
                "registry must be an array",
            )
            return
        sqlstates: set[str] = set()
        for index, failure in enumerate(registry):
            path = f"$.failure_registry[{index}]"
            if not isinstance(failure, Mapping):
                self.issue(path, "failure_type", "failure must be an object")
                continue
            failure_id = failure.get("id") or failure.get("failure_id")
            sqlstate = failure.get("sqlstate")
            reason = failure.get("reason_code")
            if not isinstance(failure_id, str) or not failure_id:
                self.issue(path, "failure_id", "failure needs a non-empty id")
            elif failure_id in self.failures:
                self.issue(path, "failure_duplicate", f"duplicate failure {failure_id}")
            else:
                self.failures.add(failure_id)
            if not isinstance(sqlstate, str) or not re.fullmatch(
                r"[A-Z0-9]{5}", sqlstate
            ):
                self.issue(
                    path,
                    "failure_sqlstate",
                    "SQLSTATE must be five uppercase alphanumerics",
                )
            elif sqlstate in sqlstates:
                self.issue(
                    path, "failure_sqlstate_duplicate", "SQLSTATE must be unique"
                )
            else:
                sqlstates.add(sqlstate)
            if not isinstance(reason, str) or not reason:
                self.issue(path, "failure_reason", "failure needs a stable reason code")
            if any(
                key in failure
                for key in (
                    "practice_id",
                    "appointment_id",
                    "patient_id",
                    "actor_id",
                    "uuid",
                    "digest",
                    "credential",
                    "packet",
                    "row",
                )
            ):
                self.issue(
                    path, "failure_value_leak", "failure metadata must be value-free"
                )

    def _load_signatures(self) -> None:
        root = self.contract.get("effective_parent_summary")
        signatures = (
            root.get("effective_signatures") if isinstance(root, Mapping) else None
        )
        if not isinstance(signatures, Mapping):
            self.issue(
                "$.effective_parent_summary.effective_signatures",
                "signature_catalogue",
                "effective signatures must be an object",
            )
            return
        if self._has_normative_envelope():
            self._validate_exact_signature_fields(signatures)
        support = signatures.get("support")
        support_items = [support] if isinstance(support, Mapping) else support
        if not isinstance(support_items, list):
            support_items = []
        self._add_signatures(support_items, "support", self.support_ids)
        entry_points = signatures.get("entry_points")
        trigger_functions = signatures.get("trigger_functions")
        self._add_signatures(
            entry_points if isinstance(entry_points, list) else [],
            "entry_points",
            self.entry_ids,
        )
        self._add_signatures(
            trigger_functions if isinstance(trigger_functions, list) else [],
            "trigger_functions",
            self.trigger_ids,
        )
        if self.entry_ids != set(EXACT_ENTRY_POINTS):
            self.issue(
                "$.effective_parent_summary.effective_signatures.entry_points",
                "entry_population",
                "entry-point signatures must equal the frozen nine-body population",
            )
        if self.trigger_ids != set(EXACT_TRIGGER_FUNCTIONS):
            self.issue(
                "$.effective_parent_summary.effective_signatures.trigger_functions",
                "trigger_population",
                "trigger signatures must equal the frozen thirteen-body population",
            )
        if self.support_ids != {EXACT_SUPPORT_FUNCTION}:
            self.issue(
                "$.effective_parent_summary.effective_signatures.support",
                "support_population",
                "the stream-scoped existing support helper is the only support function",
            )

    def _validate_exact_signature_fields(self, signatures: Mapping[str, Any]) -> None:
        """Compare every R5D signature field with literal validator authority."""

        for expected in EXACT_SIGNATURE_FIELD_MAP:
            group = expected["group"]
            position = expected["position"]
            group_value = signatures.get(group)
            if group == "support":
                candidate = group_value
                path = "$.effective_parent_summary.effective_signatures.support"
            else:
                rows = group_value if isinstance(group_value, list) else []
                candidate = rows[position] if position < len(rows) else None
                path = (
                    "$.effective_parent_summary.effective_signatures."
                    f"{group}[{position}]"
                )
            if not isinstance(candidate, Mapping):
                self.issue(
                    path,
                    "signature_position_mismatch",
                    "the exact signature must occupy this frozen position",
                )
                continue

            comparisons = (
                ("id", "signature_id_mismatch"),
                ("inputs", "signature_inputs_mismatch"),
                ("language", "signature_language_mismatch"),
                ("owner", "signature_owner_mismatch"),
                ("strict", "signature_strictness_mismatch"),
                ("volatility", "signature_volatility_mismatch"),
                ("parallel_safety", "signature_parallel_safety_mismatch"),
                ("security_definer", "signature_security_definer_mismatch"),
                ("search_path", "signature_search_path_mismatch"),
                ("public_execute", "signature_public_execute_mismatch"),
                ("invariant_ids", "signature_invariant_ids_mismatch"),
            )
            for field_name, issue_code in comparisons:
                if candidate.get(field_name) != expected[field_name]:
                    self.issue(
                        f"{path}.{field_name}",
                        issue_code,
                        f"{field_name} must equal its frozen R5D value",
                    )

            output = candidate.get("output")
            expected_output = expected["output"]
            output = output if isinstance(output, Mapping) else {}
            if output.get("type") != expected_output["type"]:
                self.issue(
                    f"{path}.output.type",
                    "signature_output_type_mismatch",
                    "output type must equal its frozen R5D value",
                )
            if output.get("cardinality") != expected_output["cardinality"]:
                self.issue(
                    f"{path}.output.cardinality",
                    "signature_output_cardinality_mismatch",
                    "output cardinality must equal its frozen R5D value",
                )

            executor_field = expected["executor_field"]
            if candidate.get(executor_field) != expected["executor"]:
                self.issue(
                    f"{path}.{executor_field}",
                    "signature_executor_mismatch",
                    "executor authority must equal its frozen R5D value",
                )

    def _add_signatures(
        self,
        signatures: Sequence[Any],
        group: str,
        destination: set[str],
    ) -> None:
        for index, signature in enumerate(signatures):
            path = f"$.effective_parent_summary.effective_signatures.{group}[{index}]"
            if not isinstance(signature, Mapping):
                self.issue(path, "signature_type", "signature must be an object")
                continue
            signature_id = signature.get("id")
            if not isinstance(signature_id, str) or not self._qualified(signature_id):
                self.issue(path, "signature_id", "signature id must be qualified")
                continue
            if signature_id in self.signatures:
                self.issue(
                    path, "signature_duplicate", f"duplicate signature {signature_id}"
                )
                continue
            destination.add(signature_id)
            self.signatures[signature_id] = signature
            inputs = signature.get("inputs")
            output = signature.get("output")
            if not isinstance(inputs, list):
                self.issue(path, "signature_inputs", "inputs must be an ordered array")
            else:
                for input_index, item in enumerate(inputs):
                    item_path = f"{path}.inputs[{input_index}]"
                    if not isinstance(item, Mapping):
                        self.issue(
                            item_path, "signature_input", "input must be an object"
                        )
                        continue
                    if item.get("mode") != "IN":
                        self.issue(
                            item_path,
                            "signature_mode",
                            "only exact IN inputs are admitted",
                        )
                    if not self._known_type(item.get("type")):
                        self.issue(
                            item_path, "signature_type", "input type is not catalogued"
                        )
            if not isinstance(output, Mapping) or not self._known_type(
                output.get("type")
            ):
                self.issue(path, "signature_output", "output type must be catalogued")
            if signature_id in self.trigger_ids and (
                not isinstance(output, Mapping)
                or output.get("type") != "pg_catalog.trigger"
            ):
                self.issue(
                    path,
                    "trigger_signature_output",
                    "trigger functions return pg_catalog.trigger",
                )

    def _load_triggers(self) -> None:
        root = self.contract.get("effective_parent_summary")
        declarations = (
            root.get("trigger_declarations") if isinstance(root, Mapping) else None
        )
        if not isinstance(declarations, list):
            self.issue(
                "$.effective_parent_summary.trigger_declarations",
                "trigger_declarations",
                "trigger declarations must be an array",
            )
            declarations = []
        if self._has_normative_envelope():
            self._validate_exact_trigger_declaration_fields(declarations)
        for index, declaration in enumerate(declarations):
            path = f"$.effective_parent_summary.trigger_declarations[{index}]"
            if not isinstance(declaration, Mapping):
                self.issue(path, "trigger_declaration", "declaration must be an object")
                continue
            function = declaration.get("function")
            relation = declaration.get("relation")
            events = declaration.get("events")
            if function not in self.trigger_ids or function in self.declarations:
                self.issue(
                    path,
                    "trigger_function_binding",
                    "function must bind one frozen trigger",
                )
                continue
            self.declarations[function] = declaration
            self._relation(relation, path)
            if (
                not isinstance(events, list)
                or not events
                or any(event not in {"INSERT", "UPDATE", "DELETE"} for event in events)
            ):
                self.issue(
                    path,
                    "trigger_events",
                    "events must be a non-empty closed TG_OP array",
                )
            elif len(set(events)) != len(events):
                self.issue(
                    path, "trigger_events_duplicate", "trigger events must be unique"
                )
            if declaration.get("row_level") is not True:
                self.issue(
                    path, "trigger_row_level", "only row-level triggers are admitted"
                )
        if set(self.declarations) != self.trigger_ids:
            self.issue(
                "$.effective_parent_summary.trigger_declarations",
                "trigger_declaration_population",
                "every frozen trigger needs exactly one declaration",
            )

        matrix = self.contract.get("trigger_applicability_return_matrix")
        if not isinstance(matrix, list):
            self.issue(
                "$.trigger_applicability_return_matrix",
                "trigger_matrix",
                "trigger matrix must be an array",
            )
            return
        for index, row in enumerate(matrix):
            path = f"$.trigger_applicability_return_matrix[{index}]"
            if not isinstance(row, Mapping):
                self.issue(path, "trigger_matrix_row", "matrix row must be an object")
                continue
            function = row.get("function")
            if function not in self.trigger_ids or function in self.trigger_matrix:
                self.issue(
                    path,
                    "trigger_matrix_function",
                    "matrix must bind one frozen trigger",
                )
                continue
            self.trigger_matrix[function] = row
        if set(self.trigger_matrix) != self.trigger_ids:
            self.issue(
                "$.trigger_applicability_return_matrix",
                "trigger_matrix_population",
                "every frozen trigger needs one return-matrix row",
            )

    def _validate_exact_trigger_declaration_fields(
        self, declarations: Sequence[Any]
    ) -> None:
        """Compare each R5D trigger declaration field at its frozen position."""

        comparisons = (
            ("id", "trigger_declaration_id_mismatch"),
            ("function", "trigger_declaration_function_mismatch"),
            ("relation", "trigger_declaration_relation_mismatch"),
            ("timing", "trigger_declaration_timing_mismatch"),
            ("row_level", "trigger_declaration_row_level_mismatch"),
            ("events", "trigger_declaration_events_mismatch"),
            ("deferrable", "trigger_declaration_deferrable_mismatch"),
            (
                "initially_deferred",
                "trigger_declaration_initially_deferred_mismatch",
            ),
            ("invariant_ids", "trigger_declaration_invariant_ids_mismatch"),
        )
        for expected in EXACT_TRIGGER_DECLARATION_FIELD_MAP:
            position = expected["position"]
            path = f"$.effective_parent_summary.trigger_declarations[{position}]"
            candidate = declarations[position] if position < len(declarations) else None
            if not isinstance(candidate, Mapping):
                self.issue(
                    path,
                    "trigger_declaration_position_mismatch",
                    "the exact trigger declaration must occupy this frozen position",
                )
                continue
            for field_name, issue_code in comparisons:
                if candidate.get(field_name) != expected[field_name]:
                    self.issue(
                        f"{path}.{field_name}",
                        issue_code,
                        f"{field_name} must equal its frozen R5D value",
                    )

    def _validate_typed_ir_declarations(self) -> None:
        typed_ir = self.contract.get("typed_ir_contract")
        path = "$.typed_ir_contract"
        if not isinstance(typed_ir, Mapping):
            self.issue(
                path, "typed_ir_contract", "typed IR declaration must be an object"
            )
            return
        declared_instructions = typed_ir.get("instruction_opcodes")
        declared_expressions = typed_ir.get("expression_opcodes")
        if not isinstance(declared_instructions, list) or set(
            declared_instructions
        ) != set(INSTRUCTION_OPCODES):
            self.issue(
                f"{path}.instruction_opcodes",
                "instruction_vocabulary",
                "instruction vocabulary must exactly equal the closed validator vocabulary",
            )
        if not isinstance(declared_expressions, list) or set(
            declared_expressions
        ) != set(EXPRESSION_OPCODES):
            self.issue(
                f"{path}.expression_opcodes",
                "expression_vocabulary",
                "expression vocabulary must exactly equal the closed validator vocabulary",
            )

    def _validate_program_population(self) -> None:
        programs = self.contract.get("body_programs")
        if not isinstance(programs, list):
            self.issue(
                "$.body_programs", "programs_type", "body programs must be an array"
            )
            return
        seen: list[str] = []
        for index, program in enumerate(programs):
            if isinstance(program, Mapping) and isinstance(program.get("id"), str):
                seen.append(program["id"])
            else:
                self.issue(
                    f"$.body_programs[{index}]", "program_id", "program needs an id"
                )
        expected = (*EXACT_ENTRY_POINTS, *EXACT_TRIGGER_FUNCTIONS)
        if tuple(seen) != expected:
            self.issue(
                "$.body_programs",
                "program_population_order",
                "programs must be the frozen nine entry points then thirteen triggers in order",
            )

    def _validate_programs(self) -> None:
        programs = self.contract.get("body_programs")
        if not isinstance(programs, list):
            return
        for index, program in enumerate(programs):
            if not isinstance(program, Mapping):
                continue
            self._program_node_ids = set()
            analysis = self._validate_program(program, index)
            if analysis is not None:
                self.body_analyses[analysis.body_id] = analysis

    def _validate_program(
        self, program: Mapping[str, Any], index: int
    ) -> BodyAnalysis | None:
        path = f"$.body_programs[{index}]"
        body_id = program.get("id")
        if not isinstance(body_id, str) or body_id not in self.signatures:
            self.issue(
                path, "program_signature", "program id must bind a frozen signature"
            )
            return None
        expected_kind = (
            "ENTRY_POINT" if body_id in self.entry_ids else "TRIGGER_FUNCTION"
        )
        if program.get("kind") != expected_kind:
            self.issue(path, "program_kind", f"program kind must be {expected_kind}")
        self._body_kind[body_id] = expected_kind
        if program.get("signature_id") != body_id:
            self.issue(path, "signature_binding", "signature_id must equal program id")
        for forbidden in ("branch_outcomes", "effect", "effects", "semantic_steps"):
            if forbidden in program:
                self.issue(path, "authored_semantics", f"{forbidden} is not admitted")

        symbols, assigned, row_columns = self._validate_symbols(program, body_id, path)
        ast = program.get("ast")
        if not isinstance(ast, Mapping) or ast.get("op") != "SEQUENCE":
            self.issue(f"{path}.ast", "ast_root", "AST root must be SEQUENCE")
            return None
        if set(ast) != {"op", "nodes"}:
            self.issue(f"{path}.ast", "ast_fields", "AST root admits only op and nodes")
        nodes = ast.get("nodes")
        if not isinstance(nodes, list) or not nodes:
            self.issue(
                f"{path}.ast.nodes", "ast_nodes", "AST needs ordered typed nodes"
            )
            return None
        self._scan_nodes(nodes, f"{path}.ast.nodes")

        declaration = self.declarations.get(body_id)
        tg_ops = (
            frozenset(declaration.get("events", [])) if declaration else frozenset()
        )
        initial = _FlowState(
            assigned=assigned,
            row_columns=row_columns,
            tg_ops=tg_ops,
            trigger_relation=(
                declaration.get("relation")
                if isinstance(declaration, Mapping)
                and isinstance(declaration.get("relation"), str)
                else None
            ),
            trail=(body_id,),
        )
        flows = self._execute_nodes(
            nodes,
            [initial],
            symbols=symbols,
            body_id=body_id,
            declaration=declaration,
            path=f"{path}.ast.nodes",
        )
        if len(flows) > 4096:
            self.issue(
                path, "path_bound", "typed control flow exceeds 4096 terminal paths"
            )
            flows = flows[:4096]
        for flow in flows:
            if flow.terminal is None:
                self.issue(
                    path, "terminal_incomplete", f"path {flow.trail!r} has no terminal"
                )

        self._validate_outputs(flows, body_id, path)
        if declaration is not None:
            self._validate_trigger_semantics(flows, program, body_id, declaration, path)

        aggregate = _Effects()
        outputs: list[dict[str, str]] = []
        for flow in flows:
            self._validate_lock_order(flow.effects.locks, body_id)
            aggregate.merge(flow.effects)
            if flow.output is not None:
                outputs.append(flow.output)
        summary = self._canonical_summary(aggregate, outputs, body_id)
        paths = tuple(
            sorted(
                (self._canonical_path(flow, body_id) for flow in flows),
                key=lambda item: item["path"],
            )
        )
        edges = tuple(sorted((body_id, target) for target in aggregate.calls))
        if self.compare_stored:
            stored = program.get("derived_effect_summary")
            if stored != summary:
                self.issue(
                    f"{path}.derived_effect_summary",
                    "summary_mismatch",
                    "stored body summary does not equal operand-derived summary",
                )
        return BodyAnalysis(body_id, summary, paths, edges)

    def _validate_symbols(
        self, program: Mapping[str, Any], body_id: str, path: str
    ) -> tuple[dict[str, Mapping[str, Any]], set[str], dict[str, tuple[str, set[str]]]]:
        symbols_raw = program.get("symbols")
        symbols: dict[str, Mapping[str, Any]] = {}
        assigned: set[str] = set()
        row_columns: dict[str, tuple[str, set[str]]] = {}
        if not isinstance(symbols_raw, list):
            self.issue(
                f"{path}.symbols", "symbols_type", "symbols must be an ordered array"
            )
            return symbols, assigned, row_columns
        for index, symbol in enumerate(symbols_raw):
            symbol_path = f"{path}.symbols[{index}]"
            if not isinstance(symbol, Mapping):
                self.issue(symbol_path, "symbol_type", "symbol must be an object")
                continue
            symbol_id = symbol.get("id")
            type_name = symbol.get("type")
            source = symbol.get("source")
            if not isinstance(symbol_id, str) or not symbol_id:
                self.issue(symbol_path, "symbol_id", "symbol needs an id")
                continue
            if symbol_id in symbols:
                self.issue(
                    symbol_path, "symbol_duplicate", f"duplicate symbol {symbol_id}"
                )
                continue
            if not self._known_type(type_name):
                self.issue(
                    symbol_path, "symbol_type_unknown", f"unknown type {type_name!r}"
                )
            if not isinstance(source, Mapping) or source.get("kind") not in {
                "INPUT",
                "LOCAL",
                "SYSTEM",
            }:
                self.issue(
                    symbol_path,
                    "symbol_source",
                    "source kind must be INPUT, LOCAL, or SYSTEM",
                )
                source = {}
            symbols[symbol_id] = symbol
            if source.get("kind") in {"INPUT", "SYSTEM"}:
                assigned.add(symbol_id)
                relation = source.get("relation")
                source_columns = source.get("columns")
                if relation is not None:
                    relation_columns = self._columns(
                        relation, source_columns, symbol_path
                    )
                    row_columns[symbol_id] = (relation, set(relation_columns))

        signature = self.signatures.get(body_id, {})
        signature_inputs = signature.get("inputs")
        expected_inputs = (
            [
                (item.get("name"), item.get("type"))
                for item in signature_inputs
                if isinstance(item, Mapping)
            ]
            if isinstance(signature_inputs, list)
            else []
        )
        actual_inputs = [
            (symbol_id, symbol.get("type"))
            for symbol_id, symbol in symbols.items()
            if isinstance(symbol.get("source"), Mapping)
            and symbol["source"].get("kind") == "INPUT"
        ]
        if actual_inputs != expected_inputs:
            self.issue(
                f"{path}.symbols",
                "input_symbol_binding",
                "INPUT symbols must exactly match ordered signature inputs",
            )
        return symbols, assigned, row_columns

    def _scan_nodes(self, nodes: list[Any], path: str) -> None:
        for index, node in enumerate(nodes):
            node_path = f"{path}[{index}]"
            if not isinstance(node, Mapping):
                self.issue(node_path, "node_type", "instruction node must be an object")
                continue
            if set(node) != {"node_id", "op", "operands"}:
                self.issue(
                    node_path,
                    "node_fields",
                    "instruction admits exactly node_id, op, and operands",
                )
            for key in node:
                if key in _BANNED_NODE_KEYS:
                    self.issue(
                        node_path,
                        "authored_node_fact",
                        f"node key {key!r} is forbidden",
                    )
            node_id = node.get("node_id")
            if not isinstance(node_id, str) or not node_id:
                self.issue(node_path, "node_id", "node needs a non-empty id")
            elif node_id in self._program_node_ids:
                self.issue(node_path, "node_duplicate", f"duplicate node id {node_id}")
            else:
                self._program_node_ids.add(node_id)
            op = node.get("op")
            if op in _BANNED_OPS or op not in INSTRUCTION_OPCODES:
                self.issue(
                    node_path,
                    "instruction_opcode",
                    f"unknown or forbidden opcode {op!r}",
                )
            operands = node.get("operands")
            if not isinstance(operands, Mapping):
                self.issue(node_path, "operands_type", "operands must be an object")
                continue
            if any(key in _BANNED_NODE_KEYS for key in operands):
                self.issue(
                    node_path,
                    "authored_operand_fact",
                    "opaque/effect operands are forbidden",
                )
            if op == "IF":
                for key in ("then", "else"):
                    child = operands.get(key)
                    if isinstance(child, list):
                        self._scan_nodes(child, f"{node_path}.operands.{key}")
            elif op == "SWITCH_TG_OP":
                arms = operands.get("arms")
                if isinstance(arms, list):
                    for arm_index, arm in enumerate(arms):
                        if isinstance(arm, Mapping) and isinstance(
                            arm.get("nodes"), list
                        ):
                            self._scan_nodes(
                                arm["nodes"],
                                f"{node_path}.operands.arms[{arm_index}].nodes",
                            )
                default = operands.get("default")
                if isinstance(default, list):
                    self._scan_nodes(default, f"{node_path}.operands.default")
            elif op == "FOR_EACH":
                child = operands.get("nodes")
                if isinstance(child, list):
                    self._scan_nodes(child, f"{node_path}.operands.nodes")

    def _execute_nodes(
        self,
        nodes: list[Any],
        states: list[_FlowState],
        *,
        symbols: Mapping[str, Mapping[str, Any]],
        body_id: str,
        declaration: Mapping[str, Any] | None,
        path: str,
    ) -> list[_FlowState]:
        current = states
        for index, node in enumerate(nodes):
            node_path = f"{path}[{index}]"
            if not isinstance(node, Mapping) or not isinstance(
                node.get("operands"), Mapping
            ):
                continue
            active = [state for state in current if state.terminal is None]
            terminal = [state for state in current if state.terminal is not None]
            if not active:
                self.issue(
                    node_path,
                    "unreachable_node",
                    "node is unreachable because every incoming path is terminal",
                )
                continue
            next_states: list[_FlowState] = []
            next_states.extend(terminal)
            for state in active:
                next_states.extend(
                    self._execute_node(
                        node,
                        state,
                        symbols=symbols,
                        body_id=body_id,
                        declaration=declaration,
                        path=node_path,
                    )
                )
            current = next_states
            if len(current) > 4096:
                self.issue(path, "path_bound", "typed control flow exceeds 4096 paths")
                return current[:4096]
        return current

    def _execute_node(
        self,
        node: Mapping[str, Any],
        state: _FlowState,
        *,
        symbols: Mapping[str, Mapping[str, Any]],
        body_id: str,
        declaration: Mapping[str, Any] | None,
        path: str,
    ) -> list[_FlowState]:
        op = node.get("op")
        operands = node.get("operands")
        if op not in INSTRUCTION_OPCODES or not isinstance(operands, Mapping):
            return [state]
        node_id = node.get("node_id") if isinstance(node.get("node_id"), str) else path
        state = state.clone(str(node_id))

        if op == "ASSERT_ISOLATION":
            self._keys(operands, {"required"}, set(), path)
            if operands.get("required") not in {"READ_COMMITTED", "SERIALIZABLE"}:
                self.issue(
                    path,
                    "isolation",
                    "isolation must be READ_COMMITTED or SERIALIZABLE",
                )
            return [state]

        if op == "DERIVE_BINDING":
            self._keys(
                operands,
                {
                    "support_function",
                    "capability",
                    "arguments",
                    "relation",
                    "columns",
                    "predicate",
                    "output_symbol",
                    "cardinality",
                },
                set(),
                path,
            )
            relation = operands.get("relation")
            columns = self._columns(relation, operands.get("columns"), path)
            self._add_read(state.effects, relation, columns)
            self._expression(
                operands.get("predicate"), state, symbols, path, expected=_BOOLEAN_TYPE
            )
            arguments = operands.get("arguments")
            if isinstance(arguments, list):
                for index, argument in enumerate(arguments):
                    self._expression(
                        argument, state, symbols, f"{path}.arguments[{index}]"
                    )
            else:
                self.issue(path, "call_arguments", "arguments must be an ordered array")
            target = operands.get("support_function")
            self._call(state, body_id, target, path)
            if operands.get("cardinality") != "EXACTLY_ONE":
                self.issue(
                    path, "binding_cardinality", "binding derivation is exactly one"
                )
            self._assign_row(
                state,
                symbols,
                operands.get("output_symbol"),
                relation,
                columns,
                path,
            )
            return [state]

        if op in {"SELECT_EXACT", "SELECT_SET"}:
            required = {
                "relation",
                "columns",
                "predicate",
                "output_symbol",
                "cardinality",
                "order_by",
            }
            self._keys(operands, required, set(), path)
            relation = operands.get("relation")
            columns = self._columns(relation, operands.get("columns"), path)
            predicate = self._expression(
                operands.get("predicate"),
                state,
                symbols,
                path,
                expected=_BOOLEAN_TYPE,
                selection_relation=(relation if isinstance(relation, str) else None),
            )
            self._merge_expression_effects(state.effects, predicate)
            order_columns = self._order_by(relation, operands.get("order_by"), path)
            self._add_read(state.effects, relation, (*columns, *order_columns))
            expected_cardinality = (
                "EXACTLY_ONE" if op == "SELECT_EXACT" else "COMPLETE_SET"
            )
            if operands.get("cardinality") != expected_cardinality:
                self.issue(
                    path, "select_cardinality", f"{op} requires {expected_cardinality}"
                )
            self._assign_row(
                state,
                symbols,
                operands.get("output_symbol"),
                relation,
                columns,
                path,
                assigned_type=(
                    f"{relation}[]"
                    if op == "SELECT_SET" and isinstance(relation, str)
                    else relation
                ),
            )
            return [state]

        if op == "LOCK_EXACT":
            self._keys(
                operands,
                {"relation", "key_columns", "predicate", "mode", "ordinal"},
                {"output_symbol", "columns"},
                path,
            )
            relation = operands.get("relation")
            key_columns = self._columns(relation, operands.get("key_columns"), path)
            predicate = self._expression(
                operands.get("predicate"), state, symbols, path, expected=_BOOLEAN_TYPE
            )
            self._merge_expression_effects(state.effects, predicate)
            self._add_read(state.effects, relation, key_columns)
            mode = operands.get("mode")
            ordinal = operands.get("ordinal")
            if mode not in {
                "FOR_UPDATE",
                "FOR_NO_KEY_UPDATE",
                "FOR_SHARE",
                "FOR_KEY_SHARE",
            }:
                self.issue(path, "lock_mode", "lock mode is not allowlisted")
            if not isinstance(ordinal, int) or isinstance(ordinal, bool) or ordinal < 1:
                self.issue(
                    path, "lock_ordinal", "lock ordinal must be a positive integer"
                )
            state.effects.locks.append(
                {
                    "relation": relation,
                    "columns": sorted(set(key_columns)),
                    "mode": mode,
                    "ordinal": ordinal,
                }
            )
            if "output_symbol" in operands:
                columns = self._columns(relation, operands.get("columns"), path)
                self._add_read(state.effects, relation, columns)
                self._assign_row(
                    state,
                    symbols,
                    operands.get("output_symbol"),
                    relation,
                    columns,
                    path,
                )
            return [state]

        if op == "LET":
            self._keys(operands, {"output_symbol", "expression"}, set(), path)
            expression = self._expression(
                operands.get("expression"), state, symbols, path
            )
            self._merge_expression_effects(state.effects, expression)
            self._assign_scalar(
                state,
                symbols,
                operands.get("output_symbol"),
                expression.type_name,
                path,
            )
            return [state]

        if op == "ASSERT":
            self._keys(operands, {"predicate", "failure_id"}, set(), path)
            predicate = self._expression(
                operands.get("predicate"), state, symbols, path, expected=_BOOLEAN_TYPE
            )
            self._merge_expression_effects(state.effects, predicate)
            failure_id = operands.get("failure_id")
            self._failure(failure_id, path)
            accepted = state.clone("true")
            rejected = state.clone("false")
            if isinstance(failure_id, str):
                rejected.effects.failures.add(failure_id)
            rejected.effects.terminals.add("RAISE")
            rejected.terminal = "RAISE"
            return [accepted, rejected]

        if op == "IF":
            self._keys(
                operands, {"condition", "then", "else", "convergence"}, set(), path
            )
            condition = self._expression(
                operands.get("condition"), state, symbols, path, expected=_BOOLEAN_TYPE
            )
            self._merge_expression_effects(state.effects, condition)
            then_nodes = operands.get("then")
            else_nodes = operands.get("else")
            if not isinstance(then_nodes, list) or not isinstance(else_nodes, list):
                self.issue(
                    path, "if_children", "IF requires inline then and else arrays"
                )
                return [state]
            then_flows = self._execute_nodes(
                then_nodes,
                [state.clone("then")],
                symbols=symbols,
                body_id=body_id,
                declaration=declaration,
                path=f"{path}.operands.then",
            )
            else_flows = self._execute_nodes(
                else_nodes,
                [state.clone("else")],
                symbols=symbols,
                body_id=body_id,
                declaration=declaration,
                path=f"{path}.operands.else",
            )
            flows = [*then_flows, *else_flows]
            self._convergence(operands.get("convergence"), flows, path)
            return flows

        if op == "SWITCH_TG_OP":
            self._keys(operands, {"arms", "default", "convergence"}, set(), path)
            if declaration is None:
                self.issue(path, "switch_non_trigger", "SWITCH_TG_OP is trigger-only")
                return [state]
            arms = operands.get("arms")
            default = operands.get("default")
            if not isinstance(arms, list) or not isinstance(default, list):
                self.issue(
                    path,
                    "switch_children",
                    "switch requires arms and an inline default",
                )
                return [state]
            arm_ops: list[str] = []
            flows: list[_FlowState] = []
            for arm_index, arm in enumerate(arms):
                arm_path = f"{path}.operands.arms[{arm_index}]"
                if not isinstance(arm, Mapping) or set(arm) != {"tg_op", "nodes"}:
                    self.issue(
                        arm_path, "switch_arm", "arm admits exactly tg_op and nodes"
                    )
                    continue
                tg_op = arm.get("tg_op")
                child = arm.get("nodes")
                if not isinstance(tg_op, str) or tg_op not in {
                    "INSERT",
                    "UPDATE",
                    "DELETE",
                }:
                    self.issue(arm_path, "switch_tg_op", "arm TG_OP is invalid")
                    continue
                if not isinstance(child, list):
                    self.issue(arm_path, "switch_nodes", "arm nodes must be an array")
                    continue
                arm_ops.append(tg_op)
                arm_state = state.clone(f"TG_OP={tg_op}")
                arm_state.tg_ops = frozenset({tg_op})
                flows.extend(
                    self._execute_nodes(
                        child,
                        [arm_state],
                        symbols=symbols,
                        body_id=body_id,
                        declaration=declaration,
                        path=f"{arm_path}.nodes",
                    )
                )
            expected_events = declaration.get("events", [])
            if arm_ops != expected_events:
                self.issue(
                    path,
                    "switch_totality",
                    "switch arms must exactly match declared events in order",
                )
            default_state = state.clone("TG_OP=DEFAULT")
            default_state.tg_ops = frozenset({"__DEFAULT__"})
            default_flows = self._execute_nodes(
                default,
                [default_state],
                symbols=symbols,
                body_id=body_id,
                declaration=declaration,
                path=f"{path}.operands.default",
            )
            if not default_flows or any(
                flow.terminal != "RAISE" for flow in default_flows
            ):
                self.issue(
                    path, "switch_default", "unexpected TG_OP default must always RAISE"
                )
            flows.extend(default_flows)
            self._convergence(operands.get("convergence"), flows, path)
            return flows

        if op == "FOR_EACH":
            self._keys(
                operands,
                {
                    "set_symbol",
                    "row_symbol",
                    "nodes",
                    "complete_set",
                    "order_by",
                    "convergence",
                },
                set(),
                path,
            )
            set_symbol = operands.get("set_symbol")
            row_symbol = operands.get("row_symbol")
            if set_symbol not in state.assigned:
                self.issue(
                    path,
                    "loop_set_unassigned",
                    "complete-set input is not definitely assigned",
                )
            if operands.get("complete_set") is not True:
                self.issue(
                    path, "loop_completeness", "FOR_EACH must consume a complete set"
                )
            nodes = operands.get("nodes")
            if not isinstance(nodes, list):
                self.issue(path, "loop_nodes", "loop nodes must be an array")
                return [state]
            iteration = state.clone("iteration")
            if isinstance(row_symbol, str):
                row_type = symbols.get(row_symbol, {}).get("type")
                set_row = state.row_columns.get(str(set_symbol))
                if row_type is None or set_row is None or row_type != set_row[0]:
                    self.issue(
                        path,
                        "loop_row_type",
                        "row symbol must match complete-set relation type",
                    )
                else:
                    iteration.assigned.add(row_symbol)
                    iteration.row_columns[row_symbol] = (set_row[0], set(set_row[1]))
            body_flows = self._execute_nodes(
                nodes,
                [iteration],
                symbols=symbols,
                body_id=body_id,
                declaration=declaration,
                path=f"{path}.operands.nodes",
            )
            if any(flow.terminal is not None for flow in body_flows):
                self.issue(
                    path,
                    "loop_terminal",
                    "complete-set loop body must converge, not terminate",
                )
            if operands.get("convergence") != "REJOIN":
                self.issue(
                    path, "loop_convergence", "FOR_EACH convergence must be REJOIN"
                )
            zero = state.clone("empty")
            results = [zero]
            for flow in body_flows:
                flowed = state.clone("nonempty")
                flowed.effects = flow.effects.clone()
                results.append(flowed)
            return results

        if op in {"INSERT", "INSERT_OR_RELOAD_COMPARE"}:
            required = {"relation", "bindings"}
            optional = {"output_symbol", "returning_columns"}
            if op == "INSERT_OR_RELOAD_COMPARE":
                required |= {
                    "conflict_key_columns",
                    "winner_columns",
                    "winner_predicate",
                    "cardinality",
                }
            self._keys(operands, required, optional, path)
            relation = operands.get("relation")
            bindings = self._bindings(
                relation, operands.get("bindings"), state, symbols, path
            )
            state.effects.inserts.setdefault(str(relation), set()).update(bindings)
            if op == "INSERT_OR_RELOAD_COMPARE":
                keys = self._columns(
                    relation, operands.get("conflict_key_columns"), path
                )
                winner = self._columns(relation, operands.get("winner_columns"), path)
                predicate = self._expression(
                    operands.get("winner_predicate"),
                    state,
                    symbols,
                    path,
                    expected=_BOOLEAN_TYPE,
                )
                self._merge_expression_effects(state.effects, predicate)
                self._add_read(state.effects, relation, (*keys, *winner))
                if operands.get("cardinality") != "EXACTLY_ONE":
                    self.issue(
                        path, "winner_cardinality", "winner reload must be exactly one"
                    )
            if "output_symbol" in operands:
                returning = self._columns(
                    relation, operands.get("returning_columns"), path
                )
                self._assign_row(
                    state,
                    symbols,
                    operands.get("output_symbol"),
                    relation,
                    returning,
                    path,
                )
            return [state]

        if op == "UPDATE":
            self._keys(
                operands,
                {
                    "relation",
                    "key_columns",
                    "predicate",
                    "set_bindings",
                    "affected_cardinality",
                },
                {"output_symbol", "returning_columns"},
                path,
            )
            relation = operands.get("relation")
            keys = self._columns(relation, operands.get("key_columns"), path)
            predicate = self._expression(
                operands.get("predicate"), state, symbols, path, expected=_BOOLEAN_TYPE
            )
            self._merge_expression_effects(state.effects, predicate)
            self._add_read(state.effects, relation, keys)
            updated = self._bindings(
                relation, operands.get("set_bindings"), state, symbols, path
            )
            state.effects.updates.setdefault(str(relation), set()).update(updated)
            if operands.get("affected_cardinality") != "EXACTLY_ONE":
                self.issue(path, "update_cardinality", "UPDATE affects exactly one row")
            if "output_symbol" in operands:
                returning = self._columns(
                    relation, operands.get("returning_columns"), path
                )
                self._assign_row(
                    state,
                    symbols,
                    operands.get("output_symbol"),
                    relation,
                    returning,
                    path,
                )
            return [state]

        if op == "DELETE_SOURCE":
            self._keys(
                operands,
                {
                    "relation",
                    "key_columns",
                    "predicate",
                    "max_rows",
                    "cascade",
                    "output_symbol",
                    "output_type",
                },
                set(),
                path,
            )
            relation = operands.get("relation")
            keys = self._columns(relation, operands.get("key_columns"), path)
            predicate = self._expression(
                operands.get("predicate"), state, symbols, path, expected=_BOOLEAN_TYPE
            )
            self._merge_expression_effects(state.effects, predicate)
            self._add_read(state.effects, relation, keys)
            if relation != "emr4_context_fabric.diary_context_observation_outbox_v1":
                self.issue(
                    path,
                    "delete_relation",
                    "DELETE_SOURCE is limited to payload-free outbox",
                )
            if body_id != "emr4_context_fabric.purge_source_rows_v1":
                self.issue(
                    path,
                    "delete_body",
                    "DELETE_SOURCE is limited to purge_source_rows_v1",
                )
            if operands.get("cascade") is not False:
                self.issue(
                    path, "delete_cascade", "source deletion must set cascade false"
                )
            max_rows = operands.get("max_rows")
            if (
                not isinstance(max_rows, int)
                or isinstance(max_rows, bool)
                or max_rows < 1
            ):
                self.issue(
                    path, "delete_bound", "source deletion needs a positive exact bound"
                )
            state.effects.deletes.setdefault(str(relation), set()).update(keys)
            output_type = operands.get("output_type")
            if output_type != _BIGINT_TYPE:
                self.issue(
                    path,
                    "delete_output_type",
                    "DELETE_SOURCE output_type must be pg_catalog.bigint",
                )
            self._assign_scalar(
                state,
                symbols,
                operands.get("output_symbol"),
                output_type,
                path,
            )
            return [state]

        if op == "CALL_SUPPORT":
            self._keys(operands, {"function", "arguments"}, {"output_symbol"}, path)
            arguments = operands.get("arguments")
            if isinstance(arguments, list):
                for index, argument in enumerate(arguments):
                    result = self._expression(
                        argument, state, symbols, f"{path}.arguments[{index}]"
                    )
                    self._merge_expression_effects(state.effects, result)
            else:
                self.issue(path, "call_arguments", "arguments must be an ordered array")
            target = operands.get("function")
            self._call(state, body_id, target, path)
            if "output_symbol" in operands and isinstance(target, str):
                output = self.signatures.get(target, {}).get("output")
                output_type = (
                    output.get("type") if isinstance(output, Mapping) else None
                )
                self._assign_scalar(
                    state, symbols, operands.get("output_symbol"), output_type, path
                )
            return [state]

        if op in {"RETURN_ROW", "RETURN_COMPOSITE"}:
            self._keys(operands, {"source_symbol", "type", "cardinality"}, set(), path)
            source_symbol = operands.get("source_symbol")
            type_name = operands.get("type")
            if source_symbol not in state.assigned:
                self.issue(
                    path,
                    "return_unassigned",
                    "return source is not definitely assigned",
                )
            elif symbols.get(str(source_symbol), {}).get("type") != type_name:
                self.issue(
                    path,
                    "return_type",
                    "return source type does not match terminal type",
                )
            if not self._known_type(type_name):
                self.issue(path, "return_type_unknown", "return type is not catalogued")
            cardinality = operands.get("cardinality")
            if cardinality not in {"EXACTLY_ONE", "ZERO_OR_ONE", "COMPLETE_SET"}:
                self.issue(
                    path, "return_cardinality", "return cardinality is not allowlisted"
                )
            state.output = {"type": type_name, "cardinality": cardinality}
            state.terminal = op
            state.effects.terminals.add(op)
            return [state]

        if op in {"RETURN_NEW", "RETURN_OLD", "RETURN_NULL"}:
            self._keys(operands, set(), set(), path)
            if declaration is None:
                self.issue(path, "trigger_return_non_trigger", f"{op} is trigger-only")
            legal = {
                "RETURN_NEW": {"INSERT", "UPDATE"},
                "RETURN_OLD": {"UPDATE", "DELETE"},
                "RETURN_NULL": {"INSERT", "UPDATE", "DELETE"},
            }[op]
            if not state.tg_ops or not state.tg_ops.issubset(legal):
                self.issue(
                    path,
                    "trigger_return_image",
                    f"{op} is illegal for {sorted(state.tg_ops)}",
                )
            state.terminal = op
            state.effects.terminals.add(op)
            return [state]

        if op == "RAISE":
            self._keys(operands, {"failure_id"}, set(), path)
            failure_id = operands.get("failure_id")
            self._failure(failure_id, path)
            if isinstance(failure_id, str):
                state.effects.failures.add(failure_id)
            state.effects.terminals.add("RAISE")
            state.terminal = "RAISE"
            return [state]

        if op == "PROPAGATE_RETRYABLE":
            self._keys(operands, {"sqlstates", "internal_retry"}, set(), path)
            if operands.get("sqlstates") != list(_RETRYABLE_SQLSTATES):
                self.issue(
                    path, "retry_sqlstates", "only 40001 and 40P01 propagate in order"
                )
            if operands.get("internal_retry") is not False:
                self.issue(path, "internal_retry", "internal retry is forbidden")
            state.effects.terminals.add("PROPAGATE_RETRYABLE")
            state.terminal = "PROPAGATE_RETRYABLE"
            return [state]

        return [state]

    def _expression(
        self,
        expression: Any,
        state: _FlowState,
        symbols: Mapping[str, Mapping[str, Any]],
        path: str,
        *,
        expected: str | None = None,
        selection_relation: str | None = None,
    ) -> _ExprResult:
        expression_path = f"{path}.expression"
        if not isinstance(expression, Mapping):
            self.issue(
                expression_path, "expression_type", "expression must be an object"
            )
            return _ExprResult(None)
        op = expression.get("op")
        if op in _BANNED_OPS or op not in EXPRESSION_OPCODES:
            self.issue(
                expression_path,
                "expression_opcode",
                f"unknown or forbidden opcode {op!r}",
            )
            return _ExprResult(None)
        if any(key in _BANNED_NODE_KEYS for key in expression):
            self.issue(
                expression_path,
                "expression_opaque",
                "opaque expression fields are forbidden",
            )

        result = self._expression_inner(
            expression,
            state,
            symbols,
            expression_path,
            selection_relation=selection_relation,
        )
        if expected is not None and result.type_name != expected:
            self.issue(
                expression_path,
                "expression_expected_type",
                f"expected {expected}, derived {result.type_name}",
            )
        return result

    def _expression_inner(
        self,
        expression: Mapping[str, Any],
        state: _FlowState,
        symbols: Mapping[str, Mapping[str, Any]],
        path: str,
        *,
        selection_relation: str | None,
    ) -> _ExprResult:
        op = expression.get("op")
        if op == "REF":
            kind = expression.get("kind")
            type_name = expression.get("type")
            if kind in {"INPUT", "LOCAL", "ITERATOR"}:
                self._expression_keys(
                    expression, {"op", "kind", "symbol", "type"}, path
                )
                symbol = expression.get("symbol")
                if symbol not in state.assigned:
                    self.issue(
                        path,
                        "symbol_unassigned",
                        f"symbol {symbol!r} is not definitely assigned",
                    )
                declared = symbols.get(str(symbol), {}).get("type")
                if declared != type_name:
                    self.issue(
                        path,
                        "symbol_type_mismatch",
                        "reference type differs from symbol type",
                    )
                return _ExprResult(type_name)
            if kind == "ROW_COLUMN":
                self._expression_keys(
                    expression,
                    {"op", "kind", "symbol", "relation", "column", "type"},
                    path,
                )
                symbol = expression.get("symbol")
                relation = expression.get("relation")
                column = expression.get("column")
                row = state.row_columns.get(str(symbol))
                if symbol not in state.assigned or row is None:
                    self.issue(
                        path,
                        "row_symbol_unassigned",
                        "row symbol is not definitely assigned",
                    )
                elif row[0] != relation or column not in row[1]:
                    self.issue(
                        path,
                        "source_column_not_selected",
                        "row column must belong to the symbol's explicitly selected columns",
                    )
                self._column_type(relation, column, type_name, path)
                return _ExprResult(type_name)
            if kind == "SOURCE_COLUMN":
                self._expression_keys(
                    expression, {"op", "kind", "relation", "column", "type"}, path
                )
                relation = expression.get("relation")
                column = expression.get("column")
                self._column_type(relation, column, type_name, path)
                return _ExprResult(type_name, ((str(relation), str(column)),))
            if kind == "TRIGGER_COLUMN":
                self._expression_keys(
                    expression,
                    {"op", "kind", "image", "relation", "column", "type"},
                    path,
                )
                image = expression.get("image")
                relation = expression.get("relation")
                column = expression.get("column")
                legal = {"OLD": {"UPDATE", "DELETE"}, "NEW": {"INSERT", "UPDATE"}}
                if (
                    image not in legal
                    or not state.tg_ops
                    or not state.tg_ops.issubset(legal[image])
                ):
                    self.issue(
                        path,
                        "row_image_illegal",
                        f"{image} is illegal for {sorted(state.tg_ops)}",
                    )
                if relation != state.trigger_relation:
                    self.issue(
                        path,
                        "row_image_relation",
                        "trigger row image relation must equal its exact declaration",
                    )
                self._column_type(relation, column, type_name, path)
                return _ExprResult(
                    type_name,
                    (),
                    (
                        (
                            str(image),
                            str(relation),
                            str(column),
                            self._tg_key(state.tg_ops),
                        ),
                    ),
                )
            if kind == "SYSTEM":
                self._expression_keys(expression, {"op", "kind", "field", "type"}, path)
                field_name = expression.get("field")
                system_types = {
                    "TG_OP": "pg_catalog.text",
                    "TG_TABLE_SCHEMA": "pg_catalog.name",
                    "TG_TABLE_NAME": "pg_catalog.name",
                    "TG_WHEN": "pg_catalog.text",
                    "TG_LEVEL": "pg_catalog.text",
                    "SESSION_USER": "pg_catalog.name",
                }
                if system_types.get(field_name) != type_name:
                    self.issue(
                        path, "system_ref", "system field/type pair is not allowlisted"
                    )
                return _ExprResult(type_name)
            self.issue(path, "reference_kind", f"unknown reference kind {kind!r}")
            return _ExprResult(type_name)

        if op in {"CONST", "ARRAY_CONST"}:
            required = (
                {"op", "type", "value"} if op == "CONST" else {"op", "type", "values"}
            )
            self._expression_keys(expression, required, path)
            type_name = expression.get("type")
            if not self._known_type(type_name):
                self.issue(
                    path, "constant_type", f"unknown constant type {type_name!r}"
                )
            values = (
                [expression.get("value")] if op == "CONST" else expression.get("values")
            )
            if op == "ARRAY_CONST" and not isinstance(values, list):
                self.issue(
                    path, "array_constant", "array constant values must be an array"
                )
            if isinstance(values, list):
                for value in values:
                    if isinstance(value, str) and _SQL_TEXT.search(value):
                        self.issue(
                            path, "raw_sql_text", "SQL/DDL/control text is forbidden"
                        )
            enum_type = (
                type_name.removesuffix("[]")
                if isinstance(type_name, str) and type_name.endswith("[]")
                else type_name
            )
            allowed_enum_values = EXACT_ENUM_VALUES.get(str(enum_type))
            if allowed_enum_values is not None:
                if op == "CONST":
                    enum_values = [expression.get("value")]
                else:
                    enum_values = values if isinstance(values, list) else []
                for value in enum_values:
                    # A typed SQL NULL is not an enum label.  Nullable enum
                    # fields use it legitimately, while every non-null scalar
                    # remains closed against the effective catalogue.
                    if value is not None and value not in allowed_enum_values:
                        self.issue(
                            path,
                            "enum_constant_membership",
                            f"{value!r} is not a member of {enum_type}",
                        )
            return _ExprResult(type_name)

        if op == "FIELD":
            self._expression_keys(expression, {"op", "source", "field", "type"}, path)
            source = self._expression(
                expression.get("source"),
                state,
                symbols,
                path,
                selection_relation=selection_relation,
            )
            field_name = expression.get("field")
            declared_type = expression.get("type")
            fields = self.composite_fields.get(str(source.type_name))
            if fields is None:
                self.issue(
                    path,
                    "field_source_type",
                    "FIELD source type must have a closed composite_fields catalogue entry",
                )
            elif not isinstance(field_name, str) or field_name not in fields:
                self.issue(
                    path,
                    "composite_field_unknown",
                    f"field {field_name!r} is not declared for {source.type_name}",
                )
            elif fields[field_name] != declared_type:
                self.issue(
                    path,
                    "composite_field_type_mismatch",
                    f"field {field_name!r} requires {fields[field_name]}, found {declared_type}",
                )
            if not self._known_type(declared_type):
                self.issue(
                    path,
                    "field_result_type",
                    "FIELD result type must be catalogued",
                )
            return _ExprResult(declared_type, source.source_reads, source.row_images)

        if op == "MIN_FIELD":
            self._expression_keys(expression, {"op", "source", "field", "type"}, path)
            source_expression = expression.get("source")
            source = self._expression(
                source_expression,
                state,
                symbols,
                path,
                selection_relation=selection_relation,
            )
            field_name = expression.get("field")
            result_type = expression.get("type")
            symbol: Any = None
            if not isinstance(source_expression, Mapping) or (
                source_expression.get("op") != "REF"
                or source_expression.get("kind") != "LOCAL"
            ):
                self.issue(
                    path,
                    "min_field_source",
                    "MIN_FIELD source must be a LOCAL reference to an assigned SELECT_SET row-set",
                )
            else:
                symbol = source_expression.get("symbol")
            selected = state.row_columns.get(str(symbol))
            if selected is None:
                self.issue(
                    path,
                    "min_field_source",
                    "MIN_FIELD source must be assigned by SELECT_SET on this path",
                )
            else:
                relation, selected_columns = selected
                if source.type_name != f"{relation}[]":
                    self.issue(
                        path,
                        "min_field_source_type",
                        "MIN_FIELD source type must be the selected relation array type",
                    )
                if (
                    not isinstance(field_name, str)
                    or field_name not in selected_columns
                ):
                    self.issue(
                        path,
                        "min_field_not_selected",
                        "MIN_FIELD field must be among the SELECT_SET columns",
                    )
                expected_type = self.column_types.get(relation, {}).get(str(field_name))
                if expected_type != result_type:
                    self.issue(
                        path,
                        "min_field_result_type",
                        f"MIN_FIELD result must equal catalogue type {expected_type}",
                    )
            return _ExprResult(result_type, source.source_reads, source.row_images)

        if op == "SET_CONTAINS_KEY":
            self._expression_keys(
                expression,
                {"op", "set", "source_relation", "key_pairs", "type"},
                path,
            )
            set_relation, selected_columns = self._set_operand(
                expression.get("set"), state, symbols, f"{path}.set"
            )
            source_relation = expression.get("source_relation")
            self._relation(source_relation, f"{path}.source_relation")
            if source_relation != selection_relation:
                self.issue(
                    f"{path}.source_relation",
                    "set_contains_source_relation_mismatch",
                    "source_relation must equal the current typed selection source",
                )

            pairs = expression.get("key_pairs")
            reads: set[tuple[str, str]] = set()
            seen_pairs: set[tuple[str, str]] = set()
            actual_pairs: list[tuple[Any, Any]] = []
            if not isinstance(pairs, list) or not pairs:
                self.issue(
                    f"{path}.key_pairs",
                    "set_key_pairs_empty",
                    "SET_CONTAINS_KEY requires a non-empty ordered key-pair array",
                )
                pairs = []
            for index, pair in enumerate(pairs):
                pair_path = f"{path}.key_pairs[{index}]"
                if not isinstance(pair, Mapping) or set(pair) != {
                    "source_column",
                    "set_column",
                }:
                    self.issue(
                        pair_path,
                        "set_key_pair_shape",
                        "contains key pairs admit exactly source_column and set_column",
                    )
                    continue
                source_column = pair.get("source_column")
                set_column = pair.get("set_column")
                actual_pairs.append((source_column, set_column))
                pair_key = (str(source_column), str(set_column))
                if pair_key in seen_pairs:
                    self.issue(
                        pair_path,
                        "set_key_pair_duplicate",
                        "set key pairs must be duplicate-free",
                    )
                seen_pairs.add(pair_key)
                source_type = self.column_types.get(str(source_relation), {}).get(
                    str(source_column)
                )
                set_type = self.column_types.get(str(set_relation), {}).get(
                    str(set_column)
                )
                if source_type is None:
                    self.issue(
                        pair_path,
                        "set_source_column_unknown",
                        "source key column must exist in source_relation",
                    )
                elif isinstance(source_relation, str) and isinstance(
                    source_column, str
                ):
                    reads.add((source_relation, source_column))
                if set_type is None:
                    self.issue(
                        pair_path,
                        "set_member_column_unknown",
                        "set key column must exist in the complete-set relation",
                    )
                elif set_column not in selected_columns:
                    self.issue(
                        pair_path,
                        "set_member_column_not_selected",
                        "set key column must be bound by the prior complete-set read",
                    )
                if (
                    source_type is not None
                    and set_type is not None
                    and (source_type != set_type)
                ):
                    self.issue(
                        pair_path,
                        "set_key_pair_type_mismatch",
                        "paired source and set key columns must have identical types",
                    )
            if set_relation != _GENERATION_SET_RELATION:
                self.issue(
                    f"{path}.set.type",
                    "set_contains_member_relation_mismatch",
                    "SET_CONTAINS_KEY requires the frozen generation complete set",
                )
            expected_pairs = _EXACT_SET_CONTAINS_KEY_PAIRS.get(str(source_relation))
            if expected_pairs is None or tuple(actual_pairs) != expected_pairs:
                self.issue(
                    f"{path}.key_pairs",
                    "set_contains_generation_identity_mismatch",
                    "key pairs must equal the exact ordered generation identity",
                )
            if expression.get("type") != _BOOLEAN_TYPE:
                self.issue(
                    f"{path}.type",
                    "set_operator_result_type",
                    "SET_CONTAINS_KEY returns pg_catalog.boolean",
                )
            return _ExprResult(_BOOLEAN_TYPE, tuple(sorted(reads)))

        if op == "SET_COVERS_KEYS":
            self._expression_keys(
                expression,
                {"op", "required", "evidence", "key_pairs", "type"},
                path,
            )
            required_relation, required_columns = self._set_operand(
                expression.get("required"),
                state,
                symbols,
                f"{path}.required",
            )
            evidence_relation, evidence_columns = self._set_operand(
                expression.get("evidence"),
                state,
                symbols,
                f"{path}.evidence",
            )
            pairs = expression.get("key_pairs")
            seen_pairs: set[tuple[str, str]] = set()
            actual_pairs: list[tuple[Any, Any]] = []
            if not isinstance(pairs, list) or not pairs:
                self.issue(
                    f"{path}.key_pairs",
                    "set_key_pairs_empty",
                    "SET_COVERS_KEYS requires a non-empty ordered key-pair array",
                )
                pairs = []
            for index, pair in enumerate(pairs):
                pair_path = f"{path}.key_pairs[{index}]"
                if not isinstance(pair, Mapping) or set(pair) != {
                    "required_column",
                    "evidence_column",
                }:
                    self.issue(
                        pair_path,
                        "set_key_pair_shape",
                        "coverage key pairs admit required_column and evidence_column",
                    )
                    continue
                required_column = pair.get("required_column")
                evidence_column = pair.get("evidence_column")
                actual_pairs.append((required_column, evidence_column))
                pair_key = (str(required_column), str(evidence_column))
                if pair_key in seen_pairs:
                    self.issue(
                        pair_path,
                        "set_key_pair_duplicate",
                        "set key pairs must be duplicate-free",
                    )
                seen_pairs.add(pair_key)
                required_type = self.column_types.get(str(required_relation), {}).get(
                    str(required_column)
                )
                evidence_type = self.column_types.get(str(evidence_relation), {}).get(
                    str(evidence_column)
                )
                if required_type is None:
                    self.issue(
                        pair_path,
                        "set_required_column_unknown",
                        "required key column must exist in its complete-set relation",
                    )
                elif required_column not in required_columns:
                    self.issue(
                        pair_path,
                        "set_required_column_not_selected",
                        "required key column must be bound by its complete-set read",
                    )
                if evidence_type is None:
                    self.issue(
                        pair_path,
                        "set_evidence_column_unknown",
                        "evidence key column must exist in its complete-set relation",
                    )
                elif evidence_column not in evidence_columns:
                    self.issue(
                        pair_path,
                        "set_evidence_column_not_selected",
                        "evidence key column must be bound by its complete-set read",
                    )
                if (
                    required_type is not None
                    and evidence_type is not None
                    and (required_type != evidence_type)
                ):
                    self.issue(
                        pair_path,
                        "set_key_pair_type_mismatch",
                        "paired required and evidence key columns must have identical types",
                    )
            if required_relation != _GENERATION_SET_RELATION:
                self.issue(
                    f"{path}.required.type",
                    "set_coverage_required_relation_mismatch",
                    "coverage requires the frozen generation complete set",
                )
            if evidence_relation != _COVERAGE_EVIDENCE_RELATION:
                self.issue(
                    f"{path}.evidence.type",
                    "set_coverage_evidence_relation_mismatch",
                    "coverage evidence must be the frozen key-interval complete set",
                )
            if tuple(actual_pairs) != _GENERATION_COORDINATE_PAIRS:
                self.issue(
                    f"{path}.key_pairs",
                    "set_coverage_generation_identity_mismatch",
                    "coverage pairs must equal exact ordered generation coordinates",
                )
            if expression.get("type") != _BOOLEAN_TYPE:
                self.issue(
                    f"{path}.type",
                    "set_operator_result_type",
                    "SET_COVERS_KEYS returns pg_catalog.boolean",
                )
            return _ExprResult(_BOOLEAN_TYPE)

        if op == "COMPOSITE_CONSTRUCT":
            self._expression_keys(expression, {"op", "type", "fields"}, path)
            composite_type = expression.get("type")
            fields = self.composite_fields.get(str(composite_type))
            bindings = expression.get("fields")
            if fields is None:
                self.issue(
                    path,
                    "composite_construct_type",
                    "COMPOSITE_CONSTRUCT type must have a closed composite_fields entry",
                )
                fields = {}
            if not isinstance(bindings, list):
                self.issue(
                    path,
                    "composite_construct_fields",
                    "COMPOSITE_CONSTRUCT fields must be an ordered array",
                )
                bindings = []
            actual_names: list[str] = []
            results: list[_ExprResult] = []
            for index, binding in enumerate(bindings):
                binding_path = f"{path}.fields[{index}]"
                if not isinstance(binding, Mapping) or set(binding) != {
                    "field",
                    "value",
                }:
                    self.issue(
                        binding_path,
                        "composite_construct_binding",
                        "composite field binding admits exactly field and value",
                    )
                    continue
                field_name = binding.get("field")
                if isinstance(field_name, str):
                    actual_names.append(field_name)
                value = self._expression(
                    binding.get("value"),
                    state,
                    symbols,
                    binding_path,
                    selection_relation=selection_relation,
                )
                results.append(value)
                expected_type = fields.get(str(field_name))
                if expected_type is None:
                    self.issue(
                        binding_path,
                        "composite_construct_field_unknown",
                        f"field {field_name!r} is not declared for {composite_type}",
                    )
                elif value.type_name != expected_type:
                    self.issue(
                        binding_path,
                        "composite_construct_field_type",
                        f"field {field_name!r} requires {expected_type}, found {value.type_name}",
                    )
            if actual_names != list(fields):
                self.issue(
                    path,
                    "composite_construct_population",
                    "composite fields must exactly match catalogue order and population",
                )
            return self._combine_expr(str(composite_type), *results)

        primitive_types = {
            "SESSION_USER": "pg_catalog.name",
            "TRANSACTION_TIMESTAMP": _TIMESTAMP_TYPE,
            "CURRENT_XID32": _XID_TYPE,
            "GEN_RANDOM_UUID": _UUID_TYPE,
        }
        if op in primitive_types:
            self._expression_keys(expression, {"op", "type"}, path)
            if expression.get("type") != primitive_types[op]:
                self.issue(path, "primitive_type", f"{op} has a fixed result type")
            return _ExprResult(expression.get("type"))

        if op == "SYSTEM_XMIN":
            self._expression_keys(expression, {"op", "row", "type"}, path)
            row_expression = expression.get("row")
            row = self._expression(
                row_expression,
                state,
                symbols,
                path,
                selection_relation=selection_relation,
            )
            if row.type_name not in self.relations:
                self.issue(
                    path, "xmin_row", "SYSTEM_XMIN requires an assigned relation row"
                )
            local_row = (
                isinstance(row_expression, Mapping)
                and row_expression.get("op") == "REF"
                and row_expression.get("kind") == "LOCAL"
            )
            if not local_row:
                self.issue(
                    path,
                    "xmin_source",
                    "SYSTEM_XMIN requires a LOCAL exact-read record source",
                )
            if local_row:
                symbol = row_expression.get("symbol")
                selected = (
                    state.row_columns.get(symbol) if isinstance(symbol, str) else None
                )
                if selected is None or "xmin" not in selected[1]:
                    self.issue(
                        path,
                        "xmin_not_selected",
                        "SYSTEM_XMIN on a LOCAL row requires an exact read that projects xmin",
                    )
            if expression.get("type") != _XID_TYPE:
                self.issue(path, "xmin_type", "SYSTEM_XMIN returns pg_catalog.xid")
            return _ExprResult(_XID_TYPE, row.source_reads, row.row_images)

        if op in {"NOT", "IS_NULL", "IS_NOT_NULL", "COUNT"}:
            self._expression_keys(expression, {"op", "operand", "type"}, path)
            operand = self._expression(
                expression.get("operand"),
                state,
                symbols,
                path,
                selection_relation=selection_relation,
            )
            result_type = expression.get("type")
            if op == "NOT" and (
                operand.type_name != _BOOLEAN_TYPE or result_type != _BOOLEAN_TYPE
            ):
                self.issue(path, "not_type", "NOT accepts and returns Boolean")
            if op in {"IS_NULL", "IS_NOT_NULL"} and result_type != _BOOLEAN_TYPE:
                self.issue(path, "null_test_type", "null tests return Boolean")
            if op == "COUNT" and result_type != _BIGINT_TYPE:
                self.issue(path, "count_type", "COUNT returns bigint")
            return _ExprResult(result_type, operand.source_reads, operand.row_images)

        if op in {
            "EQ",
            "NE",
            "LT",
            "LTE",
            "GT",
            "GTE",
            "IS_DISTINCT_FROM",
            "ADD",
            "SUBTRACT",
            "TIMESTAMP_ADD_MINUTES",
            "TIMESTAMP_ADD_SECONDS",
        }:
            self._expression_keys(expression, {"op", "left", "right", "type"}, path)
            left = self._expression(
                expression.get("left"),
                state,
                symbols,
                path,
                selection_relation=selection_relation,
            )
            right = self._expression(
                expression.get("right"),
                state,
                symbols,
                path,
                selection_relation=selection_relation,
            )
            result_type = expression.get("type")
            if op in {"EQ", "NE", "LT", "LTE", "GT", "GTE", "IS_DISTINCT_FROM"}:
                if left.type_name != right.type_name or result_type != _BOOLEAN_TYPE:
                    self.issue(
                        path,
                        "comparison_type",
                        "comparison operands match and return Boolean",
                    )
            elif op in {"ADD", "SUBTRACT"}:
                if (
                    left.type_name not in _INTEGER_TYPES
                    or right.type_name != left.type_name
                    or result_type != left.type_name
                ):
                    self.issue(
                        path,
                        "arithmetic_type",
                        "integer arithmetic preserves exact type",
                    )
            elif (
                left.type_name != _TIMESTAMP_TYPE
                or right.type_name not in _INTEGER_TYPES
                or result_type != _TIMESTAMP_TYPE
            ):
                self.issue(
                    path,
                    "timestamp_interval_type",
                    f"{op} accepts timestamptz and an integer interval",
                )
            return self._combine_expr(result_type, left, right)

        if op in {"AND", "OR"}:
            self._expression_keys(expression, {"op", "operands", "type"}, path)
            operands = expression.get("operands")
            if not isinstance(operands, list) or len(operands) < 2:
                self.issue(path, "boolean_arity", f"{op} needs at least two operands")
                operands = []
            results = [
                self._expression(
                    item,
                    state,
                    symbols,
                    f"{path}.operands[{index}]",
                    selection_relation=selection_relation,
                )
                for index, item in enumerate(operands)
            ]
            if expression.get("type") != _BOOLEAN_TYPE or any(
                result.type_name != _BOOLEAN_TYPE for result in results
            ):
                self.issue(path, "boolean_type", f"{op} accepts and returns Boolean")
            return self._combine_expr(_BOOLEAN_TYPE, *results)

        if op == "JSON_GET_CAST":
            self._expression_keys(
                expression, {"op", "source", "key", "target_type", "type"}, path
            )
            source = self._expression(
                expression.get("source"),
                state,
                symbols,
                path,
                selection_relation=selection_relation,
            )
            target = expression.get("target_type")
            if source.type_name not in {"pg_catalog.json", "pg_catalog.jsonb"}:
                self.issue(
                    path, "json_source_type", "JSON_GET_CAST requires json/jsonb source"
                )
            if not isinstance(expression.get("key"), str) or not expression.get("key"):
                self.issue(
                    path, "json_fixed_key", "JSON key must be a fixed non-empty string"
                )
            if not self._known_type(target) or expression.get("type") != target:
                self.issue(
                    path,
                    "json_cast_type",
                    "target and result types must be catalogued/equal",
                )
            return _ExprResult(target, source.source_reads, source.row_images)

        if op == "JSON_KEYS_EXACT":
            self._expression_keys(expression, {"op", "source", "keys", "type"}, path)
            source = self._expression(
                expression.get("source"),
                state,
                symbols,
                path,
                selection_relation=selection_relation,
            )
            keys = expression.get("keys")
            if source.type_name not in {"pg_catalog.json", "pg_catalog.jsonb"}:
                self.issue(
                    path,
                    "json_keys_source_type",
                    "JSON_KEYS_EXACT requires a json/jsonb source",
                )
            if (
                not isinstance(keys, list)
                or not keys
                or any(not isinstance(key, str) or not key for key in keys)
            ):
                self.issue(
                    path,
                    "json_keys_closed",
                    "JSON_KEYS_EXACT requires a non-empty ordered string-key array",
                )
            elif len(set(keys)) != len(keys):
                self.issue(
                    path,
                    "json_keys_duplicate",
                    "JSON_KEYS_EXACT keys must be unique",
                )
            if expression.get("type") != _BOOLEAN_TYPE:
                self.issue(
                    path,
                    "json_keys_result_type",
                    "JSON_KEYS_EXACT returns pg_catalog.boolean",
                )
            return _ExprResult(_BOOLEAN_TYPE, source.source_reads, source.row_images)

        if op == "CANONICAL_DIGEST":
            self._expression_keys(
                expression, {"op", "profile", "operands", "type"}, path
            )
            profile = expression.get("profile")
            if not isinstance(profile, str) or not profile.startswith(
                "emr4_context_fabric."
            ):
                self.issue(
                    path,
                    "digest_profile",
                    "digest profile must be a fixed qualified id",
                )
            operands = expression.get("operands")
            if not isinstance(operands, list) or not operands:
                self.issue(
                    path, "digest_operands", "digest needs ordered typed operands"
                )
                operands = []
            results = [
                self._expression(
                    item,
                    state,
                    symbols,
                    f"{path}.operands[{index}]",
                    selection_relation=selection_relation,
                )
                for index, item in enumerate(operands)
            ]
            result_type = expression.get("type")
            if result_type != "emr4_context_fabric.digest_sha256":
                self.issue(
                    path, "digest_type", "canonical digest returns digest_sha256"
                )
            return self._combine_expr(result_type, *results)

        if op == "CASE":
            self._expression_keys(expression, {"op", "arms", "else", "type"}, path)
            arms = expression.get("arms")
            result_type = expression.get("type")
            results: list[_ExprResult] = []
            if not isinstance(arms, list) or not arms:
                self.issue(path, "case_arms", "CASE needs ordered arms")
                arms = []
            for index, arm in enumerate(arms):
                arm_path = f"{path}.arms[{index}]"
                if not isinstance(arm, Mapping) or set(arm) != {"when", "then"}:
                    self.issue(arm_path, "case_arm", "CASE arm admits when and then")
                    continue
                condition = self._expression(
                    arm.get("when"),
                    state,
                    symbols,
                    arm_path,
                    expected=_BOOLEAN_TYPE,
                    selection_relation=selection_relation,
                )
                value = self._expression(
                    arm.get("then"),
                    state,
                    symbols,
                    arm_path,
                    selection_relation=selection_relation,
                )
                if value.type_name != result_type:
                    self.issue(arm_path, "case_type", "CASE arm type must match result")
                results.extend((condition, value))
            else_result = self._expression(
                expression.get("else"),
                state,
                symbols,
                path,
                selection_relation=selection_relation,
            )
            if else_result.type_name != result_type:
                self.issue(path, "case_else_type", "CASE else type must match result")
            results.append(else_result)
            return self._combine_expr(result_type, *results)

        return _ExprResult(None)

    def _validate_outputs(
        self, flows: list[_FlowState], body_id: str, path: str
    ) -> None:
        signature = self.signatures.get(body_id, {})
        expected = signature.get("output") if isinstance(signature, Mapping) else None
        expected_type = expected.get("type") if isinstance(expected, Mapping) else None
        expected_cardinality = (
            expected.get("cardinality") if isinstance(expected, Mapping) else None
        )
        normalized_cardinality = (
            expected_cardinality.removesuffix("_OR_RAISE")
            if isinstance(expected_cardinality, str)
            else expected_cardinality
        )
        outputs = [flow.output for flow in flows if flow.output is not None]
        if body_id in self.entry_ids:
            if not outputs:
                self.issue(
                    path,
                    "entry_output_absent",
                    "entry point needs a reachable typed return",
                )
            for output in outputs:
                if output != {
                    "type": expected_type,
                    "cardinality": normalized_cardinality,
                }:
                    self.issue(
                        path,
                        "entry_output_mismatch",
                        "return does not match full signature",
                    )
        else:
            if expected_type != "pg_catalog.trigger":
                self.issue(
                    path,
                    "trigger_output_type",
                    "trigger signature must return pg_catalog.trigger",
                )

    def _validate_trigger_semantics(
        self,
        flows: list[_FlowState],
        program: Mapping[str, Any],
        body_id: str,
        declaration: Mapping[str, Any],
        path: str,
    ) -> None:
        matrix = self.trigger_matrix.get(body_id, {})
        relation = declaration.get("relation")
        if matrix.get("relation") != relation or matrix.get(
            "events"
        ) != declaration.get("events"):
            self.issue(
                path,
                "trigger_matrix_binding",
                "matrix relation/events must equal declaration",
            )
        by_op: dict[str, set[str]] = {}
        for flow in flows:
            tg_key = self._trail_tg_op(flow.trail)
            if tg_key is not None and flow.terminal is not None:
                by_op.setdefault(tg_key, set()).add(flow.terminal)
        expected_returns = matrix.get("returns")
        if not isinstance(expected_returns, Mapping):
            self.issue(path, "trigger_returns", "matrix returns must be an object")
            expected_returns = {}
        for tg_op in declaration.get("events", []):
            actual = by_op.get(tg_op, set())
            expected_token = expected_returns.get(tg_op)
            expected_terminals = self._expected_trigger_terminals(expected_token)
            if actual != expected_terminals:
                self.issue(
                    path,
                    "trigger_terminal_matrix",
                    f"{tg_op} terminals {sorted(actual)} != {sorted(expected_terminals)}",
                )
        if by_op.get("DEFAULT", set()) != {"RAISE"}:
            self.issue(
                path,
                "trigger_default_terminal",
                "default TG_OP must terminate only by RAISE",
            )

        aggregate = _Effects()
        for flow in flows:
            aggregate.merge(flow.effects)
        if declaration.get("deferrable") is True:
            if aggregate.locks:
                self.issue(path, "deferred_lock", "deferred fence must be lock-free")
            if aggregate.inserts or aggregate.updates or aggregate.deletes:
                self.issue(path, "deferred_write", "deferred fence must be read-only")
        if matrix.get("read_only") is True and (
            aggregate.inserts or aggregate.updates or aggregate.deletes
        ):
            self.issue(
                path, "matrix_read_only", "derived writes contradict read_only matrix"
            )
        if matrix.get("lock_free") is True and aggregate.locks:
            self.issue(
                path, "matrix_lock_free", "derived locks contradict lock_free matrix"
            )

    def _validate_graph(self) -> None:
        edges = sorted(
            {
                edge
                for analysis in self.body_analyses.values()
                for edge in analysis.call_edges
            }
        )
        for source, target in edges:
            if source in self.entry_ids and target in self.entry_ids:
                self.issue(
                    "$.call_graph",
                    "entry_sibling_call",
                    f"{source} calls sibling {target}",
                )
            if source in self.trigger_ids and target in self.trigger_ids:
                self.issue(
                    "$.call_graph",
                    "trigger_sibling_call",
                    f"{source} calls sibling {target}",
                )
        graph: dict[str, set[str]] = {
            node: set()
            for node in (*self.support_ids, *self.entry_ids, *self.trigger_ids)
        }
        for source, target in edges:
            graph.setdefault(source, set()).add(target)
            graph.setdefault(target, set())
        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(node: str) -> bool:
            if node in visiting:
                return False
            if node in visited:
                return True
            visiting.add(node)
            if any(not visit(target) for target in graph.get(node, ())):
                return False
            visiting.remove(node)
            visited.add(node)
            return True

        if any(not visit(node) for node in sorted(graph)):
            self.issue(
                "$.call_graph", "call_cycle", "derived call graph must be acyclic"
            )
        canonical = {
            "nodes": sorted(graph),
            "edges": [{"from": source, "to": target} for source, target in edges],
        }
        if self.compare_stored and self.contract.get("call_graph") != canonical:
            self.issue(
                "$.call_graph",
                "call_graph_mismatch",
                "stored graph must contain only exact derived nodes and edges",
            )

    def _canonical_summary(
        self, effects: _Effects, outputs: list[dict[str, str]], body_id: str
    ) -> dict[str, Any]:
        unique_outputs = sorted(
            {tuple(sorted(output.items())) for output in outputs}, key=lambda item: item
        )
        output: dict[str, str] | None
        if body_id in self.trigger_ids:
            signature_output = self.signatures.get(body_id, {}).get("output")
            output = (
                deepcopy(signature_output)
                if isinstance(signature_output, Mapping)
                else None
            )
        elif len(unique_outputs) == 1:
            output = dict(unique_outputs[0])
        else:
            output = None
            if len(unique_outputs) > 1:
                self.issue(
                    f"$.body_programs[{body_id!r}]",
                    "output_inconsistent",
                    "reachable output terminals disagree",
                )
        return {
            "reads": self._canonical_relation_columns(effects.reads),
            "locks": sorted(
                effects.locks,
                key=lambda lock: (
                    lock.get("ordinal")
                    if isinstance(lock.get("ordinal"), int)
                    else 10**9,
                    str(lock.get("relation")),
                ),
            ),
            "inserts": self._canonical_relation_columns(effects.inserts),
            "updates": self._canonical_relation_columns(effects.updates),
            "deletes": self._canonical_relation_columns(effects.deletes),
            "calls": [{"function": function} for function in sorted(effects.calls)],
            "failures": sorted(effects.failures),
            "terminals": sorted(effects.terminals),
            "row_image_access": [
                {
                    "image": image,
                    "relation": relation,
                    "tg_op": tg_op,
                    "columns": sorted(columns),
                }
                for (image, relation, tg_op), columns in sorted(
                    effects.row_images.items()
                )
            ],
            "output": output,
        }

    def _canonical_path(self, flow: _FlowState, body_id: str) -> dict[str, Any]:
        summary = self._canonical_summary(
            flow.effects, [flow.output] if flow.output else [], body_id
        )
        return {
            "path": "/".join(flow.trail),
            "terminal": flow.terminal,
            "summary": summary,
        }

    def _validate_lock_order(self, locks: list[dict[str, Any]], body_id: str) -> None:
        ordinals = [lock.get("ordinal") for lock in locks]
        integer_ordinals = [
            item
            for item in ordinals
            if isinstance(item, int) and not isinstance(item, bool)
        ]
        if len(integer_ordinals) != len(set(integer_ordinals)):
            self.issue(
                f"$.body_programs[{body_id!r}]",
                "lock_ordinal_duplicate",
                "lock ordinals must be unique per body",
            )
        if integer_ordinals != sorted(integer_ordinals):
            self.issue(
                f"$.body_programs[{body_id!r}]",
                "lock_acquisition_order",
                "AST lock acquisition order must follow increasing ordinals",
            )
        if integer_ordinals and sorted(integer_ordinals) != list(
            range(1, len(integer_ordinals) + 1)
        ):
            self.issue(
                f"$.body_programs[{body_id!r}]",
                "lock_ordinal_sequence",
                "lock ordinals must form one stable contiguous sequence",
            )

    def _canonical_relation_columns(
        self, payload: Mapping[str, set[str]]
    ) -> list[dict[str, Any]]:
        return [
            {"relation": relation, "columns": sorted(columns)}
            for relation, columns in sorted(payload.items())
        ]

    def _keys(
        self,
        operands: Mapping[str, Any],
        required: set[str],
        optional: set[str],
        path: str,
    ) -> None:
        actual = set(operands)
        if actual != required | (actual & optional):
            missing = sorted(required - actual)
            unknown = sorted(actual - required - optional)
            if missing:
                self.issue(path, "operand_missing", f"missing operands {missing}")
            if unknown:
                self.issue(path, "operand_unknown", f"unknown operands {unknown}")

    def _expression_keys(
        self, expression: Mapping[str, Any], expected: set[str], path: str
    ) -> None:
        if set(expression) != expected:
            self.issue(
                path,
                "expression_fields",
                f"expression fields must equal {sorted(expected)}",
            )

    def _set_operand(
        self,
        operand: Any,
        state: _FlowState,
        symbols: Mapping[str, Mapping[str, Any]],
        path: str,
    ) -> tuple[str | None, set[str]]:
        """Bind one closed set operand to a prior definitely assigned SELECT_SET."""

        if not isinstance(operand, Mapping) or set(operand) != {
            "kind",
            "symbol",
            "type",
        }:
            self.issue(
                path,
                "set_operand_shape",
                "set operands admit exactly kind, symbol and type",
            )
            return None, set()
        if operand.get("kind") != "LOCAL":
            self.issue(
                path,
                "set_operand_kind",
                "set operands must reference a declared LOCAL",
            )
        symbol_id = operand.get("symbol")
        symbol = symbols.get(str(symbol_id))
        if not isinstance(symbol, Mapping):
            self.issue(
                path,
                "set_operand_symbol",
                "set operand symbol must be declared",
            )
            return None, set()
        source = symbol.get("source")
        if not isinstance(source, Mapping) or source.get("kind") != "LOCAL":
            self.issue(
                path,
                "set_operand_symbol_source",
                "set operand symbol must be declared as LOCAL",
            )
        if symbol_id not in state.assigned:
            self.issue(
                path,
                "set_operand_unassigned",
                "set operand LOCAL must be definitely assigned on this path",
            )

        operand_type = operand.get("type")
        declared_type = symbol.get("type")
        relation: str | None = None
        if (
            not isinstance(operand_type, str)
            or not operand_type.endswith("[]")
            or operand_type[:-2] not in self.relations
        ):
            self.issue(
                path,
                "set_operand_relation_array_type",
                "set operand type must be exactly a catalogued qualified relation array",
            )
        else:
            relation = operand_type[:-2]
        if declared_type != operand_type:
            self.issue(
                path,
                "set_operand_type_mismatch",
                "set operand type must equal the LOCAL's declared type",
            )

        selected = state.row_columns.get(str(symbol_id))
        if selected is None or relation is None or selected[0] != relation:
            self.issue(
                path,
                "set_operand_not_complete_set",
                "set operand must bind a previously selected complete relation set",
            )
            return relation, set()
        return relation, set(selected[1])

    def _relation(self, relation: Any, path: str) -> bool:
        if not isinstance(relation, str) or not self._qualified(relation):
            self.issue(
                path, "unqualified_relation", f"relation {relation!r} is not qualified"
            )
            return False
        if relation not in self.relations:
            self.issue(
                path, "unknown_relation", f"relation {relation!r} is not catalogued"
            )
            return False
        return True

    def _columns(self, relation: Any, columns: Any, path: str) -> tuple[str, ...]:
        if not self._relation(relation, path):
            return ()
        if (
            not isinstance(columns, list)
            or not columns
            or any(not isinstance(column, str) or not column for column in columns)
        ):
            self.issue(
                path,
                "explicit_columns",
                "a non-empty explicit column array is required",
            )
            return ()
        if len(set(columns)) != len(columns):
            self.issue(path, "duplicate_columns", "explicit columns must be unique")
        unknown = [
            column for column in columns if column not in self.relations[str(relation)]
        ]
        if unknown:
            self.issue(
                path, "unknown_column", f"unknown columns {unknown} for {relation}"
            )
        return tuple(
            column for column in columns if column in self.relations[str(relation)]
        )

    def _column_type(
        self, relation: Any, column: Any, type_name: Any, path: str
    ) -> None:
        if not self._relation(relation, path):
            return
        expected = self.column_types.get(str(relation), {}).get(str(column))
        if expected is None:
            self.issue(path, "unknown_column", f"column {column!r} is not catalogued")
        elif expected != type_name:
            self.issue(
                path, "column_type_mismatch", f"expected {expected}, found {type_name}"
            )

    def _order_by(self, relation: Any, order_by: Any, path: str) -> tuple[str, ...]:
        if not isinstance(order_by, list) or not order_by:
            self.issue(path, "stable_order", "reads need a non-empty stable ordering")
            return ()
        columns: list[str] = []
        for index, item in enumerate(order_by):
            item_path = f"{path}.order_by[{index}]"
            if not isinstance(item, Mapping) or set(item) != {"column", "direction"}:
                self.issue(
                    item_path, "order_item", "order item admits column and direction"
                )
                continue
            column = item.get("column")
            if item.get("direction") not in {"ASC", "DESC"}:
                self.issue(
                    item_path, "order_direction", "direction must be ASC or DESC"
                )
            if (
                relation in self.relations
                and column not in self.relations[str(relation)]
            ):
                self.issue(
                    item_path, "order_column", f"unknown order column {column!r}"
                )
            elif isinstance(column, str):
                columns.append(column)
        return tuple(columns)

    def _bindings(
        self,
        relation: Any,
        bindings: Any,
        state: _FlowState,
        symbols: Mapping[str, Mapping[str, Any]],
        path: str,
    ) -> tuple[str, ...]:
        if not self._relation(relation, path):
            return ()
        if not isinstance(bindings, list) or not bindings:
            self.issue(path, "bindings", "ordered column bindings are required")
            return ()
        columns: list[str] = []
        for index, binding in enumerate(bindings):
            binding_path = f"{path}.bindings[{index}]"
            if not isinstance(binding, Mapping) or set(binding) != {"column", "value"}:
                self.issue(
                    binding_path, "binding_fields", "binding admits column and value"
                )
                continue
            column = binding.get("column")
            expected = self.column_types.get(str(relation), {}).get(str(column))
            if expected is None:
                self.issue(
                    binding_path, "binding_column", f"unknown target column {column!r}"
                )
            value = self._expression(binding.get("value"), state, symbols, binding_path)
            self._merge_expression_effects(state.effects, value)
            if expected is not None and value.type_name != expected:
                self.issue(
                    binding_path,
                    "binding_type",
                    f"target {expected} != value {value.type_name}",
                )
            if isinstance(column, str):
                columns.append(column)
        if len(set(columns)) != len(columns):
            self.issue(path, "binding_duplicate", "target columns must be unique")
        return tuple(columns)

    def _assign_row(
        self,
        state: _FlowState,
        symbols: Mapping[str, Mapping[str, Any]],
        symbol: Any,
        relation: Any,
        columns: Iterable[str],
        path: str,
        *,
        assigned_type: Any | None = None,
    ) -> None:
        self._assign_scalar(
            state,
            symbols,
            symbol,
            relation if assigned_type is None else assigned_type,
            path,
        )
        if isinstance(symbol, str) and isinstance(relation, str):
            state.row_columns[symbol] = (relation, set(columns))

    def _assign_scalar(
        self,
        state: _FlowState,
        symbols: Mapping[str, Mapping[str, Any]],
        symbol: Any,
        type_name: Any,
        path: str,
    ) -> None:
        if not isinstance(symbol, str) or symbol not in symbols:
            self.issue(
                path, "output_symbol", f"output symbol {symbol!r} is not declared"
            )
            return
        if symbol in state.assigned:
            self.issue(
                path, "symbol_reassignment", f"symbol {symbol!r} is already assigned"
            )
        if symbols[symbol].get("type") != type_name:
            self.issue(
                path, "output_type", "output type differs from declared symbol type"
            )
        state.assigned.add(symbol)

    def _failure(self, failure_id: Any, path: str) -> None:
        if not isinstance(failure_id, str) or failure_id not in self.failures:
            self.issue(
                path, "failure_unknown", f"failure {failure_id!r} is not registered"
            )

    def _call(self, state: _FlowState, body_id: str, target: Any, path: str) -> None:
        if not isinstance(target, str) or not self._qualified(target):
            self.issue(path, "call_target", "call target must be qualified")
            return
        if target not in self.support_ids:
            self.issue(
                path,
                "call_not_support",
                "only the allowlisted support helper may be called",
            )
        if target == body_id:
            self.issue(path, "recursion", "recursive body call is forbidden")
        state.effects.calls.add(target)

    def _merge_expression_effects(self, effects: _Effects, result: _ExprResult) -> None:
        for relation, column in result.source_reads:
            effects.reads.setdefault(relation, set()).add(column)
        for image, relation, column, tg_op in result.row_images:
            effects.row_images.setdefault((image, relation, tg_op), set()).add(column)

    def _add_read(
        self, effects: _Effects, relation: Any, columns: Iterable[str]
    ) -> None:
        if isinstance(relation, str):
            effects.reads.setdefault(relation, set()).update(columns)

    def _convergence(self, declared: Any, flows: list[_FlowState], path: str) -> None:
        all_terminal = bool(flows) and all(flow.terminal is not None for flow in flows)
        expected = "ALL_TERMINAL" if all_terminal else "REJOIN"
        if declared != expected:
            self.issue(path, "convergence", f"convergence must be {expected}")

    def _known_type(self, type_name: Any) -> bool:
        if not isinstance(type_name, str) or not self._qualified(type_name):
            return False
        if type_name in self.types or type_name in self.relations:
            return True
        if type_name.endswith("[]") and type_name[:-2] in self.types:
            return True
        return False

    def _has_normative_envelope(self) -> bool:
        return (
            "parent_binding" in self.contract
            or "structural_feasibility_recovery_v1" in self.contract
        )

    @staticmethod
    def _qualified(identifier: str) -> bool:
        return bool(
            re.fullmatch(
                r"(?:pg_catalog|public|emr4_context_fabric)\.[a-z][a-z0-9_]*(?:\[\])?",
                identifier,
            )
        )

    @staticmethod
    def _combine_expr(type_name: str | None, *results: _ExprResult) -> _ExprResult:
        reads = tuple(
            sorted({item for result in results for item in result.source_reads})
        )
        images = tuple(
            sorted({item for result in results for item in result.row_images})
        )
        return _ExprResult(type_name, reads, images)

    @staticmethod
    def _tg_key(tg_ops: frozenset[str]) -> str:
        return "|".join(sorted(tg_ops))

    @staticmethod
    def _trail_tg_op(trail: tuple[str, ...]) -> str | None:
        for item in reversed(trail):
            if item.startswith("TG_OP="):
                value = item.removeprefix("TG_OP=")
                return "DEFAULT" if value == "DEFAULT" else value
        return None

    @staticmethod
    def _expected_trigger_terminals(token: Any) -> set[str]:
        if not isinstance(token, str):
            return set()
        if token.endswith("_OR_RAISE"):
            return {token.removesuffix("_OR_RAISE"), "RAISE"}
        return {token}


def assert_normative_envelope(
    contract: Mapping[str, Any],
) -> tuple[ValidationIssue, ...]:
    """Reject drift in the independent R4 authority/scalar envelope."""

    validator = _SemanticValidator(contract, compare_stored=False)
    validator._validate_normative_envelope()
    issues = tuple(sorted(set(validator.issues)))
    if issues:
        raise ContractValidationError(issues)
    return issues


def derive_contract_semantics(contract: Mapping[str, Any]) -> dict[str, Any]:
    """Derive canonical body summaries and call graph without trusting storage.

    Structural or semantic errors raise :class:`ContractValidationError`.
    Missing or stale ``derived_effect_summary``/``call_graph`` values do not
    affect this builder-facing derivation pass.
    """

    validator = _SemanticValidator(contract, compare_stored=False)
    report = validator.run()
    if not report.valid:
        raise ContractValidationError(report.issues)
    nodes = sorted(
        {
            *validator.support_ids,
            *validator.entry_ids,
            *validator.trigger_ids,
        }
    )
    return {
        "body_summaries": deepcopy(report.body_summaries),
        "path_summaries": deepcopy(report.path_summaries),
        "call_graph": {
            "nodes": nodes,
            "edges": [dict(edge) for edge in report.call_edges],
        },
    }


def validate_contract(contract: Mapping[str, Any]) -> ValidationReport:
    """Validate a contract and compare all stored evidence with derivation."""

    return _SemanticValidator(contract, compare_stored=True).run()


def assert_contract_valid(contract: Mapping[str, Any]) -> ValidationReport:
    """Return a passing validation report or raise deterministically."""

    report = validate_contract(contract)
    if not report.valid:
        raise ContractValidationError(report.issues)
    return report


__all__ = [
    "BodyAnalysis",
    "ContractValidationError",
    "EXACT_ENTRY_POINTS",
    "EXACT_ENUM_VALUES",
    "EXACT_NORMATIVE_SECTION_SHA256",
    "EXACT_PARENT_BINDING",
    "EXACT_SUPPORT_FUNCTION",
    "EXACT_TRIGGER_FUNCTIONS",
    "EXPRESSION_OPCODES",
    "INSTRUCTION_OPCODES",
    "ValidationIssue",
    "ValidationReport",
    "assert_contract_valid",
    "assert_normative_envelope",
    "derive_contract_semantics",
    "validate_contract",
]
