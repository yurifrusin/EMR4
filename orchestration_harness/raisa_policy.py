"""Raisa recovery policy adapter; shared precedence and declared configuration.

Historical compatibility callers and bounded admission use the same precedence
function. This module imports no controller, historical loader, or repository
runtime. Fixed schemas below cover every nested field of the ten captured
policy documents; semantic checks and typed reference edges add domain rules.
Legacy defaults are data beneath recovery authority, never dispatch permission.
"""
from __future__ import annotations

import copy
import json
from types import MappingProxyType
from typing import Any

from orchestration_harness import configuration_core as core


class RaisaPolicyError(ValueError):
    def __init__(self, reason_code: str):
        super().__init__(reason_code)
        self.reason_code = reason_code


def _exact_keys(value, expected, reason):
    if not isinstance(value, dict) or set(value) != expected:
        raise RaisaPolicyError(reason)


G1B_PROFILE = "G1B_COMPLETION_ACTIVE"
G1C_PROFILE = "G1C_GOVERNOR_ACTIVE"
G1D_PROFILE = "G1D_PROVENANCE_ACTIVE"
G1E_PROFILE = "G1E_CONFIGURATION_CORE_ACTIVE"
G1B_PREAMBLE = "Gate G1B is active only for bounded persistence, recovery, stale-lease protection and derived narrative"
G1C_PREAMBLE = "Gate G1C is active only for the bounded recovery governor and its versioned persistence integration"
G1D_PREAMBLE = "Gate G1D is active only for bounded observed provenance and independent local verification"
G1E_PREAMBLE = "Gate G1E is active only for read-only configuration and installed controller assessment"
BOUNDED_PROFILE_PREAMBLES = MappingProxyType({
    G1B_PROFILE: G1B_PREAMBLE, G1C_PROFILE: G1C_PREAMBLE,
    G1D_PROFILE: G1D_PREAMBLE, G1E_PROFILE: G1E_PREAMBLE,
})

ADMITTED_PROGRAMME_GATE = 'G0.8'
G1A3_ACTIVE_PROFILE = 'G1A.3_ACTIVE'
G1A3_ENABLEMENT_PENDING_PROFILE = 'G1A.3-E0_REVIEW_PENDING'
G1A3_R0_REVIEW_PENDING_PROFILE = 'G1A.3-R0_REVIEW_PENDING'
G1A3_R1_ACTIVE_PROFILE = 'G1A.3-R1_REVIEW_BINDING_ACTIVE'
G1A_CLOSEOUT_REPLACEMENT_TASK_GENERATION = 'g1a-closeout-g1b-enablement-lineage-totality-replacement-20260902-v1'
G1A_CLOSEOUT_REVIEW_PENDING_PROFILE = 'G1A_CLOSEOUT_G1B_ENABLEMENT_REVIEW_PENDING'
G1B1_ACTIVE_PROFILE = 'G1B.1_PURE_STATE_EVENT_KERNEL_ACTIVE'
G1B1_CLOSEOUT_REVIEW_PENDING_PROFILE = 'G1B1_CLOSEOUT_G1B2_ENABLEMENT_REVIEW_PENDING'
G1B1_CLOSEOUT_TASK_GENERATION = 'g1b1-closeout-g1b2-enablement-field-protocol-closure-replacement-20260903-v1'
G1B2_ACTIVE_PROFILE = 'G1B.2_PURE_JOURNAL_REPLAY_KERNEL_ACTIVE'
SUBGATE_TRANSITION_TO_GATE = 'G1A.2'


def validate_precedence(
    project: dict[str, Any],
    continuation: dict[str, Any],
    agents_text: str,
    state: dict[str, Any],
) -> None:
    _exact_keys(
        project,
        {
            "schema_version",
            "project_id",
            "master_authority",
            "allocation",
            "operating_model",
            "secure_sdlc",
            "direction_collaboration",
            "autonomous_continuation",
            "cost_controls",
        },
        "project_settings_schema_invalid",
    )
    _exact_keys(
        continuation,
        {
            "schema_version",
            "default_posture",
            "emergency_programme_overlay",
            "applies_when",
            "policy_decision",
            "standing_programme_authority",
            "architecture_strengthening_choice_policy",
            "failure_loop",
            "authority",
            "execution_limits",
            "pause_for_user_only_when",
            "must_not_pause_for",
            "evidence",
            "task_lifecycle",
            "resume_checkpoint",
            "document_metadata",
        },
        "continuation_settings_schema_invalid",
    )
    project_overlay = project.get("autonomous_continuation", {}).get(
        "emergency_overlay", {}
    )
    continuation_overlay = continuation.get("emergency_programme_overlay", {})
    if project_overlay != {
        "settings_file": "programme_recovery.yaml",
        "required": True,
        "precedence": "higher_than_standing_continuation",
        "missing_or_invalid": "hard_stop",
    } or continuation_overlay != {
        "status": "active",
        "settings_file": "programme_recovery.yaml",
        "precedence": "higher_than_default_posture_and_standing_programme_authority",
        "required_before_task_selection": True,
        "missing_or_invalid": "hard_stop",
    }:
        raise RaisaPolicyError("recovery_precedence_invalid")
    phase_token = (
        BOUNDED_PROFILE_PREAMBLES[state["active_profile"]]
        if state["active_profile"] in BOUNDED_PROFILE_PREAMBLES
        else
        "Gate G1B.1 implementation is externally accepted; its closeout and G1B.2 transition enablement are review-pending, and G1B.2 remains closed."
        if state["active_profile"] == G1B1_CLOSEOUT_REVIEW_PENDING_PROFILE
        else (
            "Gate G1B.2 is active only for the pure versioned journal and deterministic replay kernel"
            if state["active_profile"] == G1B2_ACTIVE_PROFILE
            else "Gate G1A.3 implementation is externally accepted. G1A closeout and G1B transition enablement are review-pending; G1B remains closed."
            if state["active_profile"] == G1A_CLOSEOUT_REVIEW_PENDING_PROFILE
            else (
                "Gate G1B.1 is active only for the bounded pure state/event kernel"
                if state["active_profile"] == G1B1_ACTIVE_PROFILE
                else (
                    f"Gate {ADMITTED_PROGRAMME_GATE} is the only authorised correction; G1A is"
                    if state["active_correction"] == ADMITTED_PROGRAMME_GATE
                    else (
                        "Gate G1A.2 implementation is externally accepted. G1A.3 transition enablement"
                        if state["active_profile"] == G1A3_ENABLEMENT_PENDING_PROFILE
                        else (
                            "Gate G1A.3-R0 is review-pending with no eligible implementation task"
                            if state["active_profile"] == G1A3_R0_REVIEW_PENDING_PROFILE
                            else (
                                "Gate G1A.3-R1 is active only for complete review-byte binding"
                                if state["active_profile"] == G1A3_R1_ACTIVE_PROFILE
                                else (
                                    "Gate G1A.3 is active only for its bounded integration-authority consumer"
                                    if state["active_profile"] == G1A3_ACTIVE_PROFILE
                                    else (
                                        "Gate G1A.2 is active only for its bounded verdict adapter; provider invocation"
                                        if state["active_correction"]
                                        == SUBGATE_TRANSITION_TO_GATE
                                        else "Gate G1A.1 is owner-accepted with residual risk; G1A.2"
                                    )
                                )
                            )
                        )
                    )
                )
            )
        )
    )
    required_header = (
        "# EMERGENCY RAISA/ARIADNE RECOVERY PRECEDENCE",
        phase_token,
        "Missing, malformed, stale, or contradictory programme state is a hard stop.",
    )
    if not agents_text.startswith(required_header[0]) or any(
        token not in agents_text[:1200] for token in required_header[1:]
    ):
        raise RaisaPolicyError("agents_recovery_precedence_missing")
    if (
        state["active_profile"] == G1A_CLOSEOUT_REVIEW_PENDING_PROFILE
        and f"Task generation `{G1A_CLOSEOUT_REPLACEMENT_TASK_GENERATION}`"
        not in agents_text
    ):
        raise RaisaPolicyError("agents_recovery_operation_identity_invalid")
    if (
        state["active_profile"] == G1B1_CLOSEOUT_REVIEW_PENDING_PROFILE
        and f"Task generation `{G1B1_CLOSEOUT_TASK_GENERATION}`" not in agents_text
    ):
        raise RaisaPolicyError("agents_recovery_operation_identity_invalid")


# Fixed declarations authored from captured ordinary inputs; no runtime schema inference.
_SHAPE_0 = ('literal', 'ariadne.autonomous_continuation.v5')

_SHAPE_1 = ('string', False)

_SHAPE_2 = ('boolean',)

_SHAPE_3 = ("object", (
    ('status', _SHAPE_1),
    ('settings_file', _SHAPE_1),
    ('precedence', _SHAPE_1),
    ('required_before_task_selection', _SHAPE_2),
    ('missing_or_invalid', _SHAPE_1),
), ())

_SHAPE_4 = ("array", (_SHAPE_1,))

_SHAPE_5 = ("object", (
    ('owner', _SHAPE_1),
    ('recorded_date', _SHAPE_1),
    ('status', _SHAPE_1),
), ())

_SHAPE_6 = ("object", (
    ('exact_descendant_plan_already_exists', _SHAPE_1),
    ('exact_descendant_plan_does_not_yet_exist', _SHAPE_1),
    ('material_gate_classification_alone_is_never_a_pause_condition', _SHAPE_2),
    ('fresh_authority_language_in_older_plans_is_satisfied_by_standing_authority', _SHAPE_2),
), ())

_SHAPE_7 = ("object", (
    ('gate_transition_permission', _SHAPE_1),
    ('applies_to', _SHAPE_4),
    ('planned_gate_boundary_rule', _SHAPE_6),
    ('conductor_boundary_derivation_must_fix', _SHAPE_4),
    ('conductor_boundary_derivation_defaults', _SHAPE_4),
    ('authorizes', _SHAPE_4),
    ('does_not_self_authorize', _SHAPE_4),
), ())

_SHAPE_8 = ("object", (
    ('reasoning_posture', _SHAPE_1),
    ('typed_output_headroom_required', _SHAPE_2),
    ('thinking_off_is', _SHAPE_1),
), ())

_SHAPE_9 = ("object", (
    ('owner', _SHAPE_1),
    ('applies_only_inside_frozen_material_boundary', _SHAPE_2),
    ('choose_without_user_pause', _SHAPE_1),
    ('model_required_cognitive_cell_default', _SHAPE_8),
    ('cannot_expand', _SHAPE_4),
), ())

_SHAPE_10 = ("object", (
    ('orchestrator_may', _SHAPE_4),
    ('orchestrator_may_not', _SHAPE_4),
    ('conductor_exclusive', _SHAPE_4),
), ())

_SHAPE_11 = ("object", (
    ('enforcement', _SHAPE_1),
    ('retry_counts', _SHAPE_1),
    ('wall_clock_deadlines', _SHAPE_1),
    ('progress_observation_preferred', _SHAPE_2),
), ())

_SHAPE_12 = ("object", (
    ('record_every_attempt', _SHAPE_2),
    ('preserve_failed_artifacts_and_receipts', _SHAPE_2),
    ('final_closeout_includes_continuation_history', _SHAPE_2),
), ())

_SHAPE_13 = ("object", (
    ('timing', _SHAPE_1),
    ('audience_style', _SHAPE_1),
    ('durable_mailbox', _SHAPE_1),
    ('filename_pattern', _SHAPE_1),
    ('must_name', _SHAPE_4),
    ('conversation_closeout_links_mailbox_message', _SHAPE_2),
    ('mailbox_is_authority_source', _SHAPE_2),
    ('acknowledgement_required', _SHAPE_2),
    ('permission_gate', _SHAPE_2),
), ())

_SHAPE_14 = ("object", (
    ('state_file', _SHAPE_1),
    ('required_at_every_configured_continuation_event', _SHAPE_2),
    ('chronological_last_prompt_is_controlling_authority', _SHAPE_2),
    ('side_question_behavior', _SHAPE_1),
    ('status_request_behavior', _SHAPE_1),
    ('scope_addition_behavior', _SHAPE_1),
    ('replacement_requires_explicit_pause_or_redirect', _SHAPE_2),
    ('in_progress_terminal_response_permitted', _SHAPE_2),
), ())

_SHAPE_15 = ("object", (
    ('required_at_every_configured_continuation_event', _SHAPE_2),
    ('required_lanes', _SHAPE_4),
    ('solo_serial_is_never_implicit', _SHAPE_2),
    ('decline_or_reserve_requires_bounded_rationale', _SHAPE_2),
    ('carry_forward_across_new_session_compaction_and_restoration', _SHAPE_2),
    ('reassess_at', _SHAPE_4),
    ('closeout_must_compare_expected_and_actual_worker_mix', _SHAPE_2),
), ())

_SHAPE_16 = ("object", (
    ('internal_checkpoint_message_channel', _SHAPE_1),
    ('successful_tranche_closeout_report', _SHAPE_13),
    ('terminal_handback_prohibited_when_no_user_decision_required', _SHAPE_2),
    ('continue_tools_in_same_task', _SHAPE_2),
    ('terminal_handback_allowed_only_when', _SHAPE_4),
    ('awaiting_worker_or_verifier_is_not_terminal', _SHAPE_2),
    ('committed_internal_plan_is_not_terminal', _SHAPE_2),
    ('next_step_known_is_not_terminal', _SHAPE_2),
    ('single_gate_closeout_is_not_terminal', _SHAPE_2),
    ('accepted_gate_with_dependency_satisfied_successor_is_not_terminal', _SHAPE_2),
    ('active_operation_latch', _SHAPE_14),
    ('parallelism_assessment', _SHAPE_15),
), ())

_SHAPE_17 = ("object", (
    ('required_for_platform_interruption', _SHAPE_2),
    ('must_name', _SHAPE_4),
    ('automatic_resume_preferred', _SHAPE_2),
), ())

_SHAPE_18 = ("object", (
    ('new_tranche_documents_require_date', _SHAPE_2),
    ('new_tranche_documents_require_australia_brisbane_iso8601_timestamp', _SHAPE_2),
    ('applies_to', _SHAPE_4),
), ())

_SHAPE_19 = ("object", (
    ('schema_version', _SHAPE_0),
    ('default_posture', _SHAPE_1),
    ('emergency_programme_overlay', _SHAPE_3),
    ('applies_when', _SHAPE_4),
    ('policy_decision', _SHAPE_5),
    ('standing_programme_authority', _SHAPE_7),
    ('architecture_strengthening_choice_policy', _SHAPE_9),
    ('failure_loop', _SHAPE_4),
    ('authority', _SHAPE_10),
    ('execution_limits', _SHAPE_11),
    ('pause_for_user_only_when', _SHAPE_4),
    ('must_not_pause_for', _SHAPE_4),
    ('evidence', _SHAPE_12),
    ('task_lifecycle', _SHAPE_16),
    ('resume_checkpoint', _SHAPE_17),
    ('document_metadata', _SHAPE_18),
), ())

_SHAPE_20 = ('literal', 'ariadne.cost_controls.v1')

_SHAPE_21 = ("object", (
    ('accounting_mode', _SHAPE_1),
    ('monetary_budget_enforcement', _SHAPE_1),
    ('estimated_cost_reporting', _SHAPE_1),
    ('deepseek_adapter_estimate_calibration', _SHAPE_1),
    ('pass_cli_max_budget_usd', _SHAPE_2),
), ())

_SHAPE_22 = ("object", (
    ('requires_explicit_user_override', _SHAPE_2),
    ('settings_field', _SHAPE_1),
    ('active_value', _SHAPE_1),
), ())

_SHAPE_23 = ("object", (
    ('estimated_cost_or_local_cap_exceeded_triggers_fallback', _SHAPE_2),
    ('actual_provider_usage_limit_triggers_fallback', _SHAPE_2),
    ('provider_model_unavailable_triggers_fallback', _SHAPE_2),
    ('authentication_or_transport_unavailable_triggers_fallback', _SHAPE_2),
), ())

_SHAPE_24 = ("object", (
    ('schema_version', _SHAPE_20),
    ('feature_available', _SHAPE_2),
    ('current_profile', _SHAPE_21),
    ('activation', _SHAPE_22),
    ('fallback_semantics', _SHAPE_23),
    ('routine_conductor_order', _SHAPE_4),
    ('claude_escalation_order', _SHAPE_4),
    ('actual_limit_evidence', _SHAPE_4),
    ('prohibited_in_current_profile', _SHAPE_4),
), ())

_SHAPE_25 = ('literal', 'ariadne.deepseek_cost_calibration.v1')

_SHAPE_26 = ('integer',)

_SHAPE_27 = ('number',)

_SHAPE_28 = ("object", (
    ('exact', _SHAPE_27),
    ('source', _SHAPE_1),
), ())

_SHAPE_29 = ("object", (
    ('exact', _SHAPE_27),
), ())

_SHAPE_30 = ("object", (
    ('calibration_id', _SHAPE_1),
    ('model', _SHAPE_1),
    ('transport', _SHAPE_1),
    ('reasoning', _SHAPE_1),
    ('sample_count', _SHAPE_26),
    ('confidence', _SHAPE_1),
    ('adapter_estimate_usd', _SHAPE_27),
    ('provider_billed_usd', _SHAPE_28),
    ('actual_from_adapter_multiplier', _SHAPE_29),
    ('adapter_estimate_divisor', _SHAPE_29),
    ('restrictions', _SHAPE_4),
), ())

_SHAPE_31 = ("object", (
    ('low', _SHAPE_27),
    ('midpoint', _SHAPE_27),
    ('high', _SHAPE_27),
    ('source', _SHAPE_1),
), ())

_SHAPE_32 = ("object", (
    ('low', _SHAPE_27),
    ('midpoint', _SHAPE_27),
    ('high', _SHAPE_27),
), ())

_SHAPE_33 = ("object", (
    ('calibration_id', _SHAPE_1),
    ('model', _SHAPE_1),
    ('transport', _SHAPE_1),
    ('reasoning', _SHAPE_1),
    ('sample_count', _SHAPE_26),
    ('confidence', _SHAPE_1),
    ('adapter_estimate_usd', _SHAPE_27),
    ('provider_billed_usd', _SHAPE_31),
    ('actual_from_adapter_multiplier', _SHAPE_32),
    ('adapter_estimate_divisor', _SHAPE_32),
    ('restrictions', _SHAPE_4),
), ())

_SHAPE_34 = ("array", (_SHAPE_30, _SHAPE_33,))

_SHAPE_35 = ("object", (
    ('schema_version', _SHAPE_25),
    ('calibrations', _SHAPE_34),
), ())

_SHAPE_36 = ('literal', 'ariadne.direction_collaboration.v1')

_SHAPE_37 = ("object", (
    ('may', _SHAPE_4),
    ('may_not', _SHAPE_4),
), ())

_SHAPE_38 = ("object", (
    ('exclusive_authority', _SHAPE_4),
), ())

_SHAPE_39 = ("object", (
    ('orchestrator', _SHAPE_37),
    ('conductor', _SHAPE_38),
), ())

_SHAPE_40 = ("object", (
    ('orchestrator_initial_proposal', _SHAPE_1),
    ('conductor_response_when_proposal_exists', _SHAPE_4),
    ('orchestrator_rejoinder_when_no_agreement', _SHAPE_1),
    ('maximum_orchestrator_rejoinders', _SHAPE_26),
    ('conductor_final_say', _SHAPE_2),
    ('final_output', _SHAPE_1),
), ())

_SHAPE_41 = ("object", (
    ('enabled', _SHAPE_2),
    ('agreement_ends_direction_dialogue', _SHAPE_2),
    ('conductor_may_plan_directly_when_direction_is_obvious', _SHAPE_2),
    ('orchestrator_may_decline_to_propose', _SHAPE_2),
), ())

_SHAPE_42 = ("object", (
    ('preserve_dissent_in_plan', _SHAPE_2),
    ('user_input_required_only_for_mandate_boundary_or_material_product_choice', _SHAPE_2),
), ())

_SHAPE_43 = ("object", (
    ('final_plan_must_be_authored_by_conductor', _SHAPE_2),
    ('orchestrator_assignment_language_prohibited', _SHAPE_2),
    ('deterministic_check_confirms_no_allocation_authority_transfer', _SHAPE_2),
    ('independent_verifier_only_on_material_disagreement_or_drift_signal', _SHAPE_2),
), ())

_SHAPE_44 = ("object", (
    ('schema_version', _SHAPE_36),
    ('mode', _SHAPE_1),
    ('participants', _SHAPE_39),
    ('dialogue', _SHAPE_40),
    ('early_exit', _SHAPE_41),
    ('disagreement', _SHAPE_42),
    ('verification', _SHAPE_43),
), ())

_SHAPE_45 = ('literal', 'ariadne.evidence_led_workflow.v1')

_SHAPE_46 = ("object", (
    ('active_boundary_artifacts', _SHAPE_1),
    ('external_review', _SHAPE_1),
    ('intermediate_deterministic_failure', _SHAPE_1),
    ('qualifying_harness_defect', _SHAPE_1),
    ('harness_repair_scope', _SHAPE_1),
    ('harness_repair_user_pause', _SHAPE_1),
    ('receipt_rule', _SHAPE_1),
    ('same_coordinate_after_correction', _SHAPE_1),
    ('side_question_during_active_operation', _SHAPE_1),
    ('status_request_during_active_operation', _SHAPE_1),
), ())

_SHAPE_47 = ("object", (
    ('coordinate_is_not_assertion', _SHAPE_2),
    ('claim_levels', _SHAPE_4),
    ('exclusive_cause_requires_exactly_one_viable_hypothesis', _SHAPE_2),
    ('diagnostic_requires_distinct_observation_for_every_viable_hypothesis', _SHAPE_2),
    ('multi_hypothesis_correction_requires', _SHAPE_4),
    ('otherwise', _SHAPE_1),
), ())

_SHAPE_48 = ("object", (
    ('representation', _SHAPE_1),
    ('stable_command_ids', _SHAPE_1),
    ('shell_wrappers', _SHAPE_1),
    ('compound_shell_commands', _SHAPE_1),
    ('repository_python_scripts', _SHAPE_1),
    ('result_ids_and_argv_must_equal_manifest', _SHAPE_2),
    ('pass_requires_every_exit_code_zero', _SHAPE_2),
    ('manifest_digest_in_receipt', _SHAPE_1),
    ('provider_free_database_closed_test_entrypoint', _SHAPE_1),
    ('admitted_local_runner', _SHAPE_1),
    ('local_runner_shell', _SHAPE_1),
    ('local_runner_stops_on_first_nonzero', _SHAPE_2),
    ('local_runner_receipt', _SHAPE_1),
    ('direct_pytest', _SHAPE_1),
    ('serial_pytest_entrypoint', _SHAPE_1),
    ('serial_pytest_noconftest', _SHAPE_1),
    ('selected_test_paths', _SHAPE_1),
), ())

_SHAPE_49 = ("object", (
    ('configured_event_discovery_command', _SHAPE_1),
    ('inferred_or_abbreviated_event_names', _SHAPE_1),
), ())

_SHAPE_50 = ("object", (
    ('full_commit_ids', _SHAPE_1),
    ('manual_short_sha_expansion', _SHAPE_1),
    ('verifier_worktree', _SHAPE_1),
    ('continuation_receipt_snapshot', _SHAPE_1),
), ())

_SHAPE_51 = ("object", (
    ('package_or_environment_mutation', _SHAPE_1),
    ('inherited_virtual_environment_and_package_indexes', _SHAPE_1),
    ('dependency_installers', _SHAPE_1),
), ())

_SHAPE_52 = ("object", (
    ('schema_version', _SHAPE_45),
    ('purpose', _SHAPE_1),
    ('hard_controls', _SHAPE_4),
    ('adaptive_flow', _SHAPE_46),
    ('diagnostic_decision', _SHAPE_47),
    ('review_command_evidence', _SHAPE_48),
    ('receipt_authoring', _SHAPE_49),
    ('git_identity', _SHAPE_50),
    ('worker_environment', _SHAPE_51),
    ('closed_surfaces', _SHAPE_4),
), ())

_SHAPE_53 = ('literal', 'ariadne.operating_model.v3')

_SHAPE_54 = ("object", (
    ('exclusive_authority', _SHAPE_4),
    ('planning_modes', _SHAPE_4),
    ('default_planning_mode', _SHAPE_1),
), ())

_SHAPE_55 = ("object", (
    ('resource_id', _SHAPE_1),
    ('may', _SHAPE_4),
    ('evidence_posture', _SHAPE_1),
    ('use_when', _SHAPE_4),
    ('deepseek_pro_consultation', _SHAPE_1),
), ())

_SHAPE_56 = ("object", (
    ('allowed_when', _SHAPE_1),
    ('must_match', _SHAPE_4),
    ('stop_on', _SHAPE_4),
), ())

_SHAPE_57 = ("object", (
    ('preferred_resource', _SHAPE_1),
    ('fallback_resource', _SHAPE_1),
    ('use_when', _SHAPE_4),
    ('may', _SHAPE_4),
    ('may_not', _SHAPE_4),
    ('protected_master_execution', _SHAPE_56),
), ())

_SHAPE_58 = ("object", (
    ('mode', _SHAPE_1),
    ('consultation_triggers', _SHAPE_4),
    ('authority_when_selected', _SHAPE_4),
    ('may_not', _SHAPE_4),
), ())

_SHAPE_59 = ("object", (
    ('orchestrator', _SHAPE_54),
    ('sol_direct_routine', _SHAPE_55),
    ('routine_delegated_executor', _SHAPE_57),
    ('conductor', _SHAPE_58),
), ())

_SHAPE_60 = ("object", (
    ('executive_role', _SHAPE_1),
    ('conductor_reentry_only_when', _SHAPE_4),
    ('conductor_reentry_not_required_for', _SHAPE_4),
), ())

_SHAPE_61 = ("object", (
    ('mode', _SHAPE_1),
    ('execution_policy_file', _SHAPE_1),
    ('deterministic_plan_checks_always_run', _SHAPE_2),
    ('external_dispatch_only_after_deterministic_pass', _SHAPE_2),
    ('deterministic_failure_action', _SHAPE_1),
    ('independent_llm_required_when', _SHAPE_4),
    ('independent_llm_not_required_for', _SHAPE_4),
), ())

_SHAPE_62 = ("object", (
    ('protocol_file', _SHAPE_1),
    ('material_sprint_security_delta', _SHAPE_1),
    ('security_sensitive_sprint_reviews', _SHAPE_4),
    ('asymmetric_packets_required', _SHAPE_2),
    ('purple_synthesis_owner', _SHAPE_1),
    ('pre_dispatch_gate', _SHAPE_1),
    ('pre_integration_gate', _SHAPE_1),
), ())

_SHAPE_63 = ("object", (
    ('wall_clock_deadlines', _SHAPE_1),
    ('monetary_caps', _SHAPE_1),
    ('prefer_progress_observation_over_elapsed_time', _SHAPE_2),
    ('worker_may_continue_while_progress_is_observable', _SHAPE_2),
    ('stalled_worker_intervention_is_orchestrator_judgment', _SHAPE_2),
), ())

_SHAPE_64 = ("object", (
    ('standing_programme_authority_file', _SHAPE_1),
    ('only_for', _SHAPE_4),
), ())

_SHAPE_65 = ("object", (
    ('enabled', _SHAPE_2),
    ('cycle', _SHAPE_4),
    ('conversational_handback_between_sprints', _SHAPE_2),
    ('conversational_handback_between_dependency_satisfied_gates', _SHAPE_2),
    ('stop_only_for', _SHAPE_4),
), ())

_SHAPE_66 = ("object", (
    ('authorization_owner', _SHAPE_1),
    ('execution_owner', _SHAPE_1),
    ('commit_and_push_regularly', _SHAPE_2),
    ('advance_handoff_current_after_accepted_checkpoint', _SHAPE_2),
    ('checkpoint_after', _SHAPE_4),
    ('workers_may_push_master', _SHAPE_2),
    ('executor_may_push_master_without_authorization', _SHAPE_2),
), ())

_SHAPE_67 = ("object", (
    ('classify_before_redispatch', _SHAPE_4),
    ('mechanical_same_lane_revision_limit', _SHAPE_26),
    ('conceptual_same_lane_revision_limit', _SHAPE_26),
    ('conceptual_triggers', _SHAPE_4),
    ('any_failed_revision_ends_external_correction_loop', _SHAPE_2),
    ('next_action', _SHAPE_1),
    ('capability_inference_may_not_use_alone', _SHAPE_4),
), ())

_SHAPE_68 = ("object", (
    ('fresh_context_gemini_veto_when_risk_triggered', _SHAPE_2),
    ('inherit_failed_worker_acceptance_framing', _SHAPE_2),
), ())

_SHAPE_69 = ("object", (
    ('supervisor', _SHAPE_1),
    ('preferred_routine_planner', _SHAPE_1),
    ('deepseek_pro_planning_role', _SHAPE_1),
    ('preferred_coding_worker', _SHAPE_1),
    ('preferred_workers', _SHAPE_4),
    ('deepseek_flash_preferred_for', _SHAPE_4),
    ('sol_retained_surfaces', _SHAPE_4),
    ('rejected_flash_candidate', _SHAPE_67),
    ('recovered_material_change_review', _SHAPE_68),
    ('worker_allocation_rule', _SHAPE_1),
    ('gemini_preferred_for', _SHAPE_4),
    ('openai_terra_use_when', _SHAPE_4),
    ('evidence_policy', _SHAPE_1),
), ())

_SHAPE_70 = ("object", (
    ('schema_version', _SHAPE_53),
    ('purpose', _SHAPE_1),
    ('sprint_boundary', _SHAPE_59),
    ('within_sprint', _SHAPE_60),
    ('verifier', _SHAPE_61),
    ('secure_sdlc', _SHAPE_62),
    ('execution_controls', _SHAPE_63),
    ('user_pause', _SHAPE_64),
    ('continuous_sprint_engine', _SHAPE_65),
    ('integration_checkpoints', _SHAPE_66),
    ('economical_execution', _SHAPE_69),
), ())

_SHAPE_71 = ('literal', 'ariadne.programme_recovery.v14')

_SHAPE_72 = ("object", (
    ('profile_kind', _SHAPE_1),
    ('expected_programme_mode', _SHAPE_1),
    ('expected_current_gate', _SHAPE_1),
    ('expected_gate_status', _SHAPE_1),
    ('active_correction', _SHAPE_1),
    ('programme_gate', _SHAPE_1),
    ('admitted_task_classes', _SHAPE_4),
    ('allowed_effects', _SHAPE_4),
    ('forbidden_effects', _SHAPE_4),
    ('closed_entrypoints', _SHAPE_4),
    ('scope_behavior', _SHAPE_1),
    ('allowed_paths', _SHAPE_4),
    ('autonomous_task_selection', _SHAPE_2),
    ('out_of_gate_result', _SHAPE_1),
    ('feature_work_eligible', _SHAPE_2),
    ('product_work_eligible', _SHAPE_2),
    ('provider_calls_eligible', _SHAPE_2),
    ('deployment_eligible', _SHAPE_2),
    ('protected_ref_movement_eligible', _SHAPE_2),
    ('g1a_eligible', _SHAPE_2),
), ())

_SHAPE_73 = ("object", (
    ('antigravity_allowed_mutation', _SHAPE_1),
    ('antigravity_runtime_source_parsing_contract', _SHAPE_1),
    ('run_worker_first_admission_contract', _SHAPE_1),
    ('integration_allowed_mutation', _SHAPE_1),
    ('record_integration_first_admission_contract', _SHAPE_1),
), ())

_SHAPE_74 = ("object", (
    ('profile_kind', _SHAPE_1),
    ('expected_programme_mode', _SHAPE_1),
    ('expected_current_gate', _SHAPE_1),
    ('expected_gate_status', _SHAPE_1),
    ('active_correction', _SHAPE_1),
    ('programme_gate', _SHAPE_1),
    ('admitted_task_classes', _SHAPE_4),
    ('allowed_effects', _SHAPE_4),
    ('forbidden_effects', _SHAPE_4),
    ('closed_entrypoints', _SHAPE_4),
    ('scope_behavior', _SHAPE_1),
    ('allowed_paths', _SHAPE_4),
    ('autonomous_task_selection', _SHAPE_2),
    ('out_of_gate_result', _SHAPE_1),
    ('feature_work_eligible', _SHAPE_2),
    ('product_work_eligible', _SHAPE_2),
    ('provider_calls_eligible', _SHAPE_2),
    ('deployment_eligible', _SHAPE_2),
    ('protected_ref_movement_eligible', _SHAPE_2),
    ('g1a_eligible', _SHAPE_2),
    ('source_contract', _SHAPE_73),
), ())

_SHAPE_75 = ("object", (
    ('profile_kind', _SHAPE_1),
    ('expected_programme_mode', _SHAPE_1),
    ('expected_current_gate', _SHAPE_1),
    ('expected_gate_status', _SHAPE_1),
    ('active_correction', _SHAPE_1),
    ('programme_gate', _SHAPE_1),
    ('admitted_task_classes', _SHAPE_4),
    ('allowed_effects', _SHAPE_4),
    ('forbidden_effects', _SHAPE_4),
    ('allowed_paths', _SHAPE_4),
    ('autonomous_task_selection', _SHAPE_2),
    ('feature_work_eligible', _SHAPE_2),
    ('product_work_eligible', _SHAPE_2),
    ('provider_calls_eligible', _SHAPE_2),
    ('deployment_eligible', _SHAPE_2),
    ('protected_ref_movement_eligible', _SHAPE_2),
    ('g1c_eligible', _SHAPE_2),
    ('scope_behavior', _SHAPE_1),
    ('scope_file', _SHAPE_1),
    ('closed_entrypoints', _SHAPE_4),
), ())

_SHAPE_76 = ("object", (
    ('profile_kind', _SHAPE_1),
    ('expected_programme_mode', _SHAPE_1),
    ('expected_current_gate', _SHAPE_1),
    ('expected_gate_status', _SHAPE_1),
    ('active_correction', _SHAPE_1),
    ('programme_gate', _SHAPE_1),
    ('admitted_task_classes', _SHAPE_4),
    ('allowed_effects', _SHAPE_4),
    ('forbidden_effects', _SHAPE_4),
    ('allowed_paths', _SHAPE_4),
    ('autonomous_task_selection', _SHAPE_2),
    ('feature_work_eligible', _SHAPE_2),
    ('product_work_eligible', _SHAPE_2),
    ('provider_calls_eligible', _SHAPE_2),
    ('deployment_eligible', _SHAPE_2),
    ('protected_ref_movement_eligible', _SHAPE_2),
    ('g1d_eligible', _SHAPE_2),
    ('scope_behavior', _SHAPE_1),
    ('scope_file', _SHAPE_1),
    ('recovery_envelope_limits_required', _SHAPE_2),
    ('global_execution_defaults_unchanged', _SHAPE_2),
    ('closed_entrypoints', _SHAPE_4),
), ())

_SHAPE_77 = ("object", (
    ('profile_kind', _SHAPE_1),
    ('expected_programme_mode', _SHAPE_1),
    ('expected_current_gate', _SHAPE_1),
    ('expected_gate_status', _SHAPE_1),
    ('active_correction', _SHAPE_1),
    ('programme_gate', _SHAPE_1),
    ('admitted_task_classes', _SHAPE_4),
    ('allowed_effects', _SHAPE_4),
    ('forbidden_effects', _SHAPE_4),
    ('allowed_paths', _SHAPE_4),
    ('autonomous_task_selection', _SHAPE_2),
    ('feature_work_eligible', _SHAPE_2),
    ('product_work_eligible', _SHAPE_2),
    ('provider_calls_eligible', _SHAPE_2),
    ('deployment_eligible', _SHAPE_2),
    ('protected_ref_movement_eligible', _SHAPE_2),
    ('g1e_eligible', _SHAPE_2),
    ('scope_behavior', _SHAPE_1),
    ('scope_file', _SHAPE_1),
    ('reviewed_local_authored_verification_only', _SHAPE_2),
    ('global_execution_defaults_unchanged', _SHAPE_2),
    ('closed_entrypoints', _SHAPE_4),
), ())

_SHAPE_78 = ("object", (
    ('profile_kind', _SHAPE_1),
    ('expected_programme_mode', _SHAPE_1),
    ('expected_current_gate', _SHAPE_1),
    ('expected_gate_status', _SHAPE_1),
    ('active_correction', _SHAPE_1),
    ('programme_gate', _SHAPE_1),
    ('admitted_task_classes', _SHAPE_4),
    ('allowed_effects', _SHAPE_4),
    ('forbidden_effects', _SHAPE_4),
    ('allowed_paths', _SHAPE_4),
    ('autonomous_task_selection', _SHAPE_2),
    ('feature_work_eligible', _SHAPE_2),
    ('product_work_eligible', _SHAPE_2),
    ('provider_calls_eligible', _SHAPE_2),
    ('deployment_eligible', _SHAPE_2),
    ('protected_ref_movement_eligible', _SHAPE_2),
    ('g2_eligible', _SHAPE_2),
    ('scope_behavior', _SHAPE_1),
    ('scope_file', _SHAPE_1),
    ('installed_controller_assessment_only', _SHAPE_2),
    ('global_execution_defaults_unchanged', _SHAPE_2),
    ('closed_entrypoints', _SHAPE_4),
), ())

_SHAPE_79 = ("object", (
    ('G0.8_FSMONITOR_CLOSURE', _SHAPE_72),
    ('G0_TO_G1A_STATE_TRANSITION', _SHAPE_72),
    ('G1A.1_ACTIVE', _SHAPE_72),
    ('G1A.1_TO_G1A.2_STATE_TRANSITION', _SHAPE_72),
    ('G1A.2_ACTIVE', _SHAPE_72),
    ('G1A.3-E0_REVIEW_PENDING', _SHAPE_72),
    ('G1A.2_TO_G1A.3_STATE_TRANSITION', _SHAPE_72),
    ('G1A.3_ACTIVE', _SHAPE_72),
    ('G1A.3-R0_REVIEW_PENDING', _SHAPE_72),
    ('G1A.3-R0_TO_R1_STATE_TRANSITION', _SHAPE_72),
    ('G1A.3-R1_REVIEW_BINDING_ACTIVE', _SHAPE_74),
    ('G1A_CLOSEOUT_G1B_ENABLEMENT_REVIEW_PENDING', _SHAPE_72),
    ('G1A_TO_G1B1_STATE_TRANSITION', _SHAPE_72),
    ('G1B.1_PURE_STATE_EVENT_KERNEL_ACTIVE', _SHAPE_72),
    ('G1B1_CLOSEOUT_G1B2_ENABLEMENT_REVIEW_PENDING', _SHAPE_72),
    ('G1B1_TO_G1B2_STATE_TRANSITION', _SHAPE_72),
    ('G1B.2_PURE_JOURNAL_REPLAY_KERNEL_ACTIVE', _SHAPE_72),
    ('G1B_COMPLETION_ACTIVE', _SHAPE_75),
    ('G1C_GOVERNOR_ACTIVE', _SHAPE_76),
    ('G1D_PROVENANCE_ACTIVE', _SHAPE_77),
    ('G1E_CONFIGURATION_CORE_ACTIVE', _SHAPE_78),
), ('G1E_CONFIGURATION_CORE_ACTIVE',))

_SHAPE_80 = ("object", (
    ('expected_branch', _SHAPE_1),
    ('frozen_recovery_base', _SHAPE_1),
    ('authorized_parent_commit', _SHAPE_1),
    ('candidate_commit_limit', _SHAPE_26),
    ('allowed_paths', _SHAPE_4),
), ())

_SHAPE_81 = ("object", (
    ('manifest_schema_version', _SHAPE_1),
    ('task_class', _SHAPE_1),
    ('from_gate', _SHAPE_1),
    ('to_gate', _SHAPE_1),
    ('transition_status', _SHAPE_1),
    ('external_review_record_root', _SHAPE_1),
    ('transition_artifact_root', _SHAPE_1),
    ('candidate_commit_limit', _SHAPE_26),
    ('fixed_allowed_paths', _SHAPE_4),
    ('forbidden_effect_classes', _SHAPE_4),
), ())

_SHAPE_82 = ('literal', 'ariadne.owner_disposition_policy.v1')

_SHAPE_83 = ("object", (
    ('schema_version', _SHAPE_82),
    ('record_schema_version', _SHAPE_1),
    ('record_root', _SHAPE_1),
    ('current_disposition_id', _SHAPE_1),
    ('current_record_path', _SHAPE_1),
    ('subject_gate', _SHAPE_1),
    ('subject_commit', _SHAPE_1),
    ('subject_tree', _SHAPE_1),
    ('accepted_decisions', _SHAPE_4),
    ('append_only', _SHAPE_2),
    ('external_review_separation_required', _SHAPE_2),
    ('missing_malformed_rewritten_or_contradictory', _SHAPE_1),
), ())

_SHAPE_84 = ("object", (
    ('manifest_schema_version', _SHAPE_1),
    ('task_class', _SHAPE_1),
    ('transition_profile', _SHAPE_1),
    ('resulting_active_profile', _SHAPE_1),
    ('from_gate', _SHAPE_1),
    ('to_gate', _SHAPE_1),
    ('transition_status', _SHAPE_1),
    ('owner_disposition_record_root', _SHAPE_1),
    ('external_review_record_root', _SHAPE_1),
    ('transition_artifact_root', _SHAPE_1),
    ('external_review_schema_version', _SHAPE_1),
    ('transition_artifact_schema_version', _SHAPE_1),
    ('candidate_commit_limit', _SHAPE_26),
    ('fixed_allowed_paths', _SHAPE_4),
    ('forbidden_effect_classes', _SHAPE_4),
), ())

_SHAPE_85 = ("object", (
    ('manifest_schema_version', _SHAPE_1),
    ('task_class', _SHAPE_1),
    ('transition_profile', _SHAPE_1),
    ('resulting_active_profile', _SHAPE_1),
    ('from_gate', _SHAPE_1),
    ('to_gate', _SHAPE_1),
    ('transition_status', _SHAPE_1),
    ('implementation_review_record_root', _SHAPE_1),
    ('implementation_review_schema_version', _SHAPE_1),
    ('external_review_record_root', _SHAPE_1),
    ('external_review_schema_version', _SHAPE_1),
    ('transition_artifact_root', _SHAPE_1),
    ('transition_artifact_schema_version', _SHAPE_1),
    ('candidate_commit_limit', _SHAPE_26),
    ('fixed_allowed_paths', _SHAPE_4),
    ('forbidden_effect_classes', _SHAPE_4),
), ())

_SHAPE_86 = ("object", (
    ('manifest_schema_version', _SHAPE_1),
    ('task_class', _SHAPE_1),
    ('transition_profile', _SHAPE_1),
    ('resulting_active_profile', _SHAPE_1),
    ('from_profile', _SHAPE_1),
    ('to_profile', _SHAPE_1),
    ('transition_status', _SHAPE_1),
    ('rejected_review_id', _SHAPE_1),
    ('rejected_review_record_sha256', _SHAPE_1),
    ('external_review_record_root', _SHAPE_1),
    ('external_review_schema_version', _SHAPE_1),
    ('transition_artifact_root', _SHAPE_1),
    ('transition_artifact_schema_version', _SHAPE_1),
    ('candidate_commit_limit', _SHAPE_26),
    ('fixed_allowed_paths', _SHAPE_4),
    ('forbidden_effect_classes', _SHAPE_4),
), ())

_SHAPE_87 = ("object", (
    ('manifest_schema_version', _SHAPE_1),
    ('task_class', _SHAPE_1),
    ('transition_profile', _SHAPE_1),
    ('resulting_active_profile', _SHAPE_1),
    ('from_profile', _SHAPE_1),
    ('to_profile', _SHAPE_1),
    ('transition_status', _SHAPE_1),
    ('g1a3_r1_review_id', _SHAPE_1),
    ('g1a3_r1_review_record_sha256', _SHAPE_1),
    ('external_review_record_root', _SHAPE_1),
    ('external_review_schema_version', _SHAPE_1),
    ('transition_artifact_root', _SHAPE_1),
    ('transition_artifact_schema_version', _SHAPE_1),
    ('accepted_surface_path', _SHAPE_1),
    ('clockwork_scope_path', _SHAPE_1),
    ('candidate_commit_limit', _SHAPE_26),
    ('fixed_allowed_paths', _SHAPE_4),
    ('exact_transition_path_count', _SHAPE_26),
    ('forbidden_effect_classes', _SHAPE_4),
), ())

_SHAPE_88 = ("object", (
    ('manifest_schema_version', _SHAPE_1),
    ('task_class', _SHAPE_1),
    ('transition_profile', _SHAPE_1),
    ('resulting_active_profile', _SHAPE_1),
    ('from_profile', _SHAPE_1),
    ('to_profile', _SHAPE_1),
    ('transition_status', _SHAPE_1),
    ('g1b1_implementation_review_id', _SHAPE_1),
    ('g1b1_implementation_review_record_sha256', _SHAPE_1),
    ('external_review_record_root', _SHAPE_1),
    ('external_review_schema_version', _SHAPE_1),
    ('transition_artifact_root', _SHAPE_1),
    ('transition_artifact_schema_version', _SHAPE_1),
    ('accepted_surface_path', _SHAPE_1),
    ('journal_replay_scope_path', _SHAPE_1),
    ('candidate_commit_limit', _SHAPE_26),
    ('fixed_allowed_paths', _SHAPE_4),
    ('exact_transition_path_count', _SHAPE_26),
    ('forbidden_effect_classes', _SHAPE_4),
), ())

_SHAPE_89 = ('literal', 'ariadne.pinned_programme_gatekeeper_policy.v7')

_SHAPE_90 = ("object", (
    ('schema_version', _SHAPE_89),
    ('module', _SHAPE_1),
    ('bootstrap', _SHAPE_1),
    ('cli', _SHAPE_1),
    ('operation_cli_module', _SHAPE_1),
    ('canonical_operations', _SHAPE_4),
    ('operation_receipt_schema', _SHAPE_1),
    ('source_binding', _SHAPE_1),
    ('clean_source_required', _SHAPE_2),
    ('target_is_data_only', _SHAPE_2),
    ('candidate_controller_execution_forbidden', _SHAPE_2),
    ('combined_operation_only', _SHAPE_2),
    ('receipt_sink_schema', _SHAPE_1),
    ('receipt_argument', _SHAPE_1),
    ('receipt_directory_policy', _SHAPE_1),
    ('receipt_reservation_policy', _SHAPE_1),
    ('operation_binding_fields', _SHAPE_4),
), ())

_SHAPE_91 = ('literal', 'ariadne.g1a_target_worktree_policy.v3')

_SHAPE_92 = ("object", (
    ('schema_version', _SHAPE_91),
    ('preserved_legacy_worktree', _SHAPE_1),
    ('preserved_legacy_worktree_forbidden_as_gatekeeper', _SHAPE_2),
    ('preserved_legacy_worktree_forbidden_as_target', _SHAPE_2),
    ('separate_clean_target_required', _SHAPE_2),
    ('activation_untracked_count_required', _SHAPE_26),
    ('development_allowed_untracked_paths', _SHAPE_4),
    ('g1a2_development_allowed_untracked_paths', _SHAPE_4),
    ('pre_push_untracked_count_required', _SHAPE_26),
    ('post_push_untracked_count_required', _SHAPE_26),
    ('root_import_hooks_forbidden', _SHAPE_4),
    ('nonregular_reparse_symlink_and_junction_forbidden', _SHAPE_2),
    ('ignored_and_untracked_inventory_required', _SHAPE_2),
    ('protected_path_aliases_forbidden', _SHAPE_2),
    ('inventory_command', _SHAPE_1),
    ('git_administrative_entry', _SHAPE_1),
    ('git_administrative_policy', _SHAPE_1),
), ())

_SHAPE_93 = ('literal', 'ariadne.remote_identity_policy.v1')

_SHAPE_94 = ("object", (
    ('schema_version', _SHAPE_93),
    ('mode', _SHAPE_1),
    ('remote_name', _SHAPE_1),
    ('normalized_fetch_url', _SHAPE_1),
    ('normalized_push_url', _SHAPE_1),
    ('fetch_url_count', _SHAPE_26),
    ('push_url_count', _SHAPE_26),
    ('explicit_push_url_count', _SHAPE_26),
    ('expected_repository_identity', _SHAPE_1),
    ('normalization_policy', _SHAPE_1),
    ('url_rewrite_policy', _SHAPE_1),
    ('url_rewrite_count', _SHAPE_26),
    ('remote_identity_sha256', _SHAPE_1),
), ())

_SHAPE_95 = ("object", (
    ('id', _SHAPE_1),
    ('path', _SHAPE_1),
    ('entrypoint', _SHAPE_1),
), ())

_SHAPE_96 = ("array", (_SHAPE_95,))

_SHAPE_97 = ("object", (
    ('removal_requires', _SHAPE_1),
    ('default_on_transition_error', _SHAPE_1),
), ())

_SHAPE_98 = ("object", (
    ('schema_version', _SHAPE_71),
    ('status', _SHAPE_1),
    ('authority_owner', _SHAPE_1),
    ('recorded_at', _SHAPE_1),
    ('state_file', _SHAPE_1),
    ('gates_file', _SHAPE_1),
    ('risk_file', _SHAPE_1),
    ('inventory_file', _SHAPE_1),
    ('g1a_scope_file', _SHAPE_1),
    ('g1a_accepted_surface_file', _SHAPE_1),
    ('g1b_clockwork_scope_file', _SHAPE_1),
    ('g1b1_accepted_surface_file', _SHAPE_1),
    ('g1b2_journal_replay_scope_file', _SHAPE_1),
    ('admission_command', _SHAPE_1),
    ('required_before', _SHAPE_4),
    ('missing_or_invalid_state', _SHAPE_1),
    ('active_profile', _SHAPE_1),
    ('profiles', _SHAPE_79),
    ('scope_policy', _SHAPE_80),
    ('transition_policy', _SHAPE_81),
    ('owner_disposition_policy', _SHAPE_83),
    ('subgate_transition_policy', _SHAPE_84),
    ('g1a3_transition_policy', _SHAPE_85),
    ('g1a3_r0_transition_policy', _SHAPE_86),
    ('g1a_to_g1b1_transition_policy', _SHAPE_87),
    ('g1b1_to_g1b2_transition_policy', _SHAPE_88),
    ('pinned_gatekeeper', _SHAPE_90),
    ('target_worktree_policy', _SHAPE_92),
    ('remote_identity_policy', _SHAPE_94),
    ('gated_entrypoints', _SHAPE_96),
    ('reversibility', _SHAPE_97),
), ())

_SHAPE_99 = ('literal', 'ariadne.project_settings.v1')

_SHAPE_100 = ("object", (
    ('exclusive_role', _SHAPE_1),
    ('conductor_can_commit', _SHAPE_2),
    ('verifier_can_commit', _SHAPE_2),
), ())

_SHAPE_101 = ("object", (
    ('user_override_required_to_change_verified_assignment', _SHAPE_2),
    ('conductor_revision_required_to_change_assignment', _SHAPE_2),
    ('conductor_replan_required_only_when_availability_forces_assignment_change', _SHAPE_2),
    ('live_agent_adapters_enabled', _SHAPE_2),
), ())

_SHAPE_102 = ("object", (
    ('settings_file', _SHAPE_1),
    ('within_sprint_executive_role', _SHAPE_1),
    ('independent_verifier_mode', _SHAPE_1),
), ())

_SHAPE_103 = ("object", (
    ('settings_file', _SHAPE_1),
    ('material_sprint_security_delta', _SHAPE_1),
    ('security_sensitive_review', _SHAPE_1),
    ('purple_review_maximum_material_sprint_interval', _SHAPE_26),
), ())

_SHAPE_104 = ("object", (
    ('settings_file', _SHAPE_1),
    ('optional', _SHAPE_2),
    ('conductor_retains_final_say', _SHAPE_2),
), ())

_SHAPE_105 = ("object", (
    ('settings_file', _SHAPE_1),
    ('required', _SHAPE_2),
    ('precedence', _SHAPE_1),
    ('missing_or_invalid', _SHAPE_1),
), ())

_SHAPE_106 = ("object", (
    ('settings_file', _SHAPE_1),
    ('default_posture', _SHAPE_1),
    ('reallocation_authority', _SHAPE_1),
    ('active_operation_latch', _SHAPE_1),
    ('emergency_overlay', _SHAPE_105),
), ())

_SHAPE_107 = ("object", (
    ('settings_file', _SHAPE_1),
    ('monetary_budget_enforcement', _SHAPE_1),
    ('activation_requires_explicit_user_override', _SHAPE_2),
), ())

_SHAPE_108 = ("object", (
    ('schema_version', _SHAPE_99),
    ('project_id', _SHAPE_1),
    ('master_authority', _SHAPE_100),
    ('allocation', _SHAPE_101),
    ('operating_model', _SHAPE_102),
    ('secure_sdlc', _SHAPE_103),
    ('direction_collaboration', _SHAPE_104),
    ('autonomous_continuation', _SHAPE_106),
    ('cost_controls', _SHAPE_107),
), ())

_SHAPE_109 = ('literal', 'ariadne.security_review_protocol.v1')

_SHAPE_110 = ("object", (
    ('security_delta_required', _SHAPE_2),
    ('classification_owner_resource_id', _SHAPE_1),
    ('non_material_requires_owner_and_rationale', _SHAPE_2),
    ('required_fields', _SHAPE_4),
), ())

_SHAPE_111 = ("object", (
    ('default_tier', _SHAPE_1),
    ('security_sensitive_tier', _SHAPE_1),
    ('security_sensitive_triggers', _SHAPE_4),
    ('purple_review_triggers', _SHAPE_4),
    ('maximum_material_sprints_between_purple', _SHAPE_26),
), ())

_SHAPE_112 = ("object", (
    ('ledger_path', _SHAPE_1),
    ('entry_schema_version', _SHAPE_1),
    ('no_prior_purple_count', _SHAPE_26),
), ())

_SHAPE_113 = ("object", (
    ('required_for_tier', _SHAPE_1),
    ('preferred_resource_id', _SHAPE_1),
    ('owns', _SHAPE_1),
    ('may_not', _SHAPE_4),
), ())

_SHAPE_114 = ("object", (
    ('owner_resource_id', _SHAPE_1),
    ('owns', _SHAPE_1),
    ('may_not', _SHAPE_4),
), ())

_SHAPE_115 = ("object", (
    ('blue', _SHAPE_113),
    ('red', _SHAPE_113),
    ('purple', _SHAPE_114),
), ())

_SHAPE_116 = ("object", (
    ('asymmetric_packets_required', _SHAPE_2),
    ('red_fresh_context_required', _SHAPE_2),
    ('red_candidate_only_required', _SHAPE_2),
    ('red_prior_review_artifacts_excluded', _SHAPE_2),
    ('workers_cannot_self_certify', _SHAPE_2),
), ())

_SHAPE_117 = ("object", (
    ('required_decision', _SHAPE_1),
    ('blocking_unresolved_severities', _SHAPE_4),
    ('gate_phases', _SHAPE_4),
    ('artifact_sha256_required', _SHAPE_2),
    ('artifact_must_bind_candidate', _SHAPE_2),
    ('allowed_finding_severities', _SHAPE_4),
), ())

_SHAPE_118 = ("object", (
    ('allowed_disposition', _SHAPE_1),
    ('allowed_worker_decisions', _SHAPE_4),
    ('recovery_owner_resource_id', _SHAPE_1),
    ('exact_final_independent_pass_required', _SHAPE_2),
), ())

_SHAPE_119 = ("object", (
    ('schema_version', _SHAPE_109),
    ('purpose', _SHAPE_1),
    ('material_sprint', _SHAPE_110),
    ('risk_classification', _SHAPE_111),
    ('purple_cadence', _SHAPE_112),
    ('roles', _SHAPE_115),
    ('independence', _SHAPE_116),
    ('acceptance', _SHAPE_117),
    ('recovery', _SHAPE_118),
), ())

_SHAPE_120 = ('literal', 'ariadne.verifier_execution_policy.v1')

_SHAPE_121 = ("object", (
    ('verifier_worktree_preflight', _SHAPE_1),
    ('five_source_rehydration_receipt', _SHAPE_1),
    ('authority_and_scope_packet', _SHAPE_1),
    ('candidate_branch', _SHAPE_1),
    ('candidate_head', _SHAPE_1),
    ('settings_fingerprint', _SHAPE_1),
    ('focused_tests', _SHAPE_1),
    ('static_and_filesystem_checks', _SHAPE_1),
    ('candidate_worktree', _SHAPE_1),
), ())

_SHAPE_122 = ("object", (
    ('required_before_external_model_dispatch', _SHAPE_2),
    ('fail_closed_action', _SHAPE_1),
    ('required_results', _SHAPE_121),
), ())

_SHAPE_123 = ('literal', 'ariadne.verifier-command-manifest.v1')

_SHAPE_124 = ("object", (
    ('schema_version', _SHAPE_123),
    ('representation', _SHAPE_1),
    ('exact_results_required', _SHAPE_2),
    ('pass_requires_every_exit_code_zero', _SHAPE_2),
    ('manifest_digest_in_receipt', _SHAPE_2),
), ())

_SHAPE_125 = ("object", (
    ('allowed', _SHAPE_4),
    ('exact_terminal_decision_count', _SHAPE_26),
    ('envelope_format', _SHAPE_1),
    ('additional_properties', _SHAPE_1),
    ('legacy_terminal_line_default', _SHAPE_2),
    ('optional_command_manifest', _SHAPE_124),
), ())

_SHAPE_126 = ("object", (
    ('candidate_head', _SHAPE_1),
    ('candidate_worktree', _SHAPE_1),
), ())

_SHAPE_127 = ("object", (
    ('exact_existing_interpreter_required', _SHAPE_2),
    ('package_or_environment_bootstrap', _SHAPE_1),
    ('missing_dependency_action', _SHAPE_1),
), ())

_SHAPE_128 = ("object", (
    ('mode', _SHAPE_1),
    ('preferred_resource_id', _SHAPE_1),
    ('model', _SHAPE_1),
    ('reasoning', _SHAPE_1),
    ('project_context', _SHAPE_1),
    ('worktree_access', _SHAPE_1),
    ('candidate_prior_review_artifacts', _SHAPE_1),
    ('silent_model_fallback', _SHAPE_1),
    ('implementation_capability', _SHAPE_1),
    ('decision_contract', _SHAPE_125),
    ('postcondition', _SHAPE_126),
    ('environment_boundary', _SHAPE_127),
    ('triggers', _SHAPE_4),
), ())

_SHAPE_129 = ("object", (
    ('resource_id', _SHAPE_1),
    ('routine_reasoning', _SHAPE_1),
    ('material_reasoning', _SHAPE_1),
    ('owns', _SHAPE_4),
    ('material_triggers', _SHAPE_4),
), ())

_SHAPE_130 = ("object", (
    ('inherited_virtual_environment_and_package_indexes', _SHAPE_1),
    ('pip_and_uv_network_install', _SHAPE_1),
    ('package_manager_instruction', _SHAPE_1),
    ('missing_dependency_action', _SHAPE_1),
), ())

_SHAPE_131 = ("object", (
    ('resource_id', _SHAPE_1),
    ('model', _SHAPE_1),
    ('reasoning', _SHAPE_1),
    ('transport', _SHAPE_1),
    ('owns', _SHAPE_4),
    ('may_not', _SHAPE_4),
    ('environment_boundary', _SHAPE_130),
), ())

_SHAPE_132 = ("object", (
    ('resource_id', _SHAPE_1),
    ('model', _SHAPE_1),
    ('reasoning', _SHAPE_1),
    ('transport', _SHAPE_1),
    ('owns', _SHAPE_4),
    ('may_not', _SHAPE_4),
), ())

_SHAPE_133 = ("object", (
    ('sol', _SHAPE_129),
    ('deepseek_flash', _SHAPE_131),
    ('gemini_flash', _SHAPE_132),
), ())

_SHAPE_134 = ("object", (
    ('dispatch_is_optional', _SHAPE_2),
    ('require_leverage_greater_than_packet_monitoring_and_recovery_cost', _SHAPE_2),
    ('keep_serial_tightly_coupled_or_small_work_sol_owned', _SHAPE_2),
), ())

_SHAPE_135 = ("object", (
    ('policy', _SHAPE_1),
    ('one_active_boundary_and_one_final_risk_triggered_veto', _SHAPE_2),
    ('coordinate_is_not_assertion', _SHAPE_2),
    ('correction_requires_discriminating_next_observation', _SHAPE_2),
    ('continuation_event_values_are_cli_discoverable', _SHAPE_2),
    ('repeated_same_coordinate_after_correction', _SHAPE_1),
), ())

_SHAPE_136 = ("object", (
    ('repository_conftest_pytest', _SHAPE_1),
    ('shared_postgresql_schema', _SHAPE_1),
    ('required_validation_runner', _SHAPE_1),
    ('validation_runner_manifest', _SHAPE_1),
    ('validation_runner_lifecycle_receipt', _SHAPE_1),
    ('validation_runner_failure_behavior', _SHAPE_1),
    ('required_pytest_launcher', _SHAPE_1),
    ('conftest_enforcement', _SHAPE_1),
    ('direct_pytest', _SHAPE_1),
    ('serial_noconftest', _SHAPE_1),
    ('selected_test_paths', _SHAPE_1),
    ('direct_pytest_bypass', _SHAPE_1),
    ('parallel_allowed_only_for', _SHAPE_4),
), ())

_SHAPE_137 = ("object", (
    ('immutable_failure_evidence', _SHAPE_1),
    ('correction_linkage', _SHAPE_1),
    ('recurrence_threshold', _SHAPE_26),
    ('raw_prompts_secrets_and_sensitive_values', _SHAPE_1),
    ('model_provider_or_role_causal_claim_without_separate_evidence', _SHAPE_1),
    ('candidate_runtime_and_review_transport_claims', _SHAPE_1),
), ())

_SHAPE_138 = ("object", (
    ('register', _SHAPE_1),
    ('schema', _SHAPE_1),
    ('deterministic_report', _SHAPE_1),
    ('register_before_corrected_attempt_acceptance', _SHAPE_2),
    ('record_when', _SHAPE_4),
    ('origin_classes', _SHAPE_4),
    ('controls', _SHAPE_137),
), ())

_SHAPE_139 = ("object", (
    ('schema_version', _SHAPE_120),
    ('purpose', _SHAPE_1),
    ('execution_order', _SHAPE_4),
    ('deterministic_gate', _SHAPE_122),
    ('external_verifier', _SHAPE_128),
    ('lane_profile', _SHAPE_133),
    ('dispatch_economy', _SHAPE_134),
    ('evidence_led_flow', _SHAPE_135),
    ('test_execution', _SHAPE_136),
    ('incident_learning', _SHAPE_138),
), ())

POLICY_SCHEMAS = {
    'autonomous_continuation.yaml': ('yaml', _SHAPE_19),
    'cost_controls.yaml': ('yaml', _SHAPE_24),
    'deepseek_cost_calibration.yaml': ('yaml', _SHAPE_35),
    'direction_collaboration.yaml': ('yaml', _SHAPE_44),
    'evidence_led_workflow.yaml': ('yaml', _SHAPE_52),
    'operating_model.yaml': ('yaml', _SHAPE_70),
    'programme_recovery.yaml': ('yaml', _SHAPE_98),
    'project.yaml': ('yaml', _SHAPE_108),
    'security_review_protocol.yaml': ('yaml', _SHAPE_119),
    'verifier_execution_policy.yaml': ('yaml', _SHAPE_139),
}

_CONFIGURATION_PROFILE = {'profile_kind': 'bounded_G1E_configuration_assessment',
 'expected_programme_mode': 'recovery',
 'expected_current_gate': 'G1E',
 'expected_gate_status': 'active',
 'active_correction': 'G1E',
 'programme_gate': 'G1E',
 'admitted_task_classes': ['g1e_configuration_core_assessment'],
 'allowed_effects': ['repository_read'],
 'forbidden_effects': ['autonomous_worker_dispatch',
                       'control_plane_edit',
                       'dependency_change',
                       'deployment',
                       'existing_clockwork_runtime_mutation',
                       'integration',
                       'migration_change',
                       'pages',
                       'product_behavior_change',
                       'protected_ref_movement',
                       'provider_invocation',
                       'real_data_access',
                       'task_branch_commit',
                       'task_branch_push'],
 'allowed_paths': [],
 'autonomous_task_selection': False,
 'feature_work_eligible': False,
 'product_work_eligible': False,
 'provider_calls_eligible': False,
 'deployment_eligible': False,
 'protected_ref_movement_eligible': False,
 'g2_eligible': False,
 'scope_behavior': 'bounded_g1e_configuration_assessment',
 'scope_file': 'orchestration/programme/g1e-configuration-core-scope.json',
 'installed_controller_assessment_only': True,
 'global_execution_defaults_unchanged': True,
 'closed_entrypoints': ['worker_dispatch',
                        'provider_invocation',
                        'clockwork_tick_mutation',
                        'clockwork_closeout_mutation',
                        'integration',
                        'protected_ref_operation',
                        'deployment',
                        'task_branch_commit',
                        'task_branch_push']}


def configuration_profile() -> dict:
    return copy.deepcopy(_CONFIGURATION_PROFILE)


POLICY_REFERENCES = (
    core.Reference("project.yaml", ("operating_model", "settings_file"), "operating_model.yaml"),
    core.Reference("project.yaml", ("secure_sdlc", "settings_file"), "security_review_protocol.yaml"),
    core.Reference("project.yaml", ("direction_collaboration", "settings_file"), "direction_collaboration.yaml"),
    core.Reference("project.yaml", ("autonomous_continuation", "settings_file"), "autonomous_continuation.yaml"),
    core.Reference("project.yaml", ("autonomous_continuation", "emergency_overlay", "settings_file"), "programme_recovery.yaml"),
    core.Reference("project.yaml", ("cost_controls", "settings_file"), "cost_controls.yaml"),
    core.Reference("operating_model.yaml", ("verifier", "execution_policy_file"), "verifier_execution_policy.yaml"),
    core.Reference("operating_model.yaml", ("secure_sdlc", "protocol_file"), "security_review_protocol.yaml"),
    core.Reference("operating_model.yaml", ("user_pause", "standing_programme_authority_file"), "autonomous_continuation.yaml"),
    core.Reference("autonomous_continuation.yaml", ("emergency_programme_overlay", "settings_file"), "programme_recovery.yaml"),
    core.Reference("verifier_execution_policy.yaml", ("evidence_led_flow", "policy"), "evidence_led_workflow.yaml"),
    core.Reference("cost_controls.yaml", ("current_profile", "deepseek_adapter_estimate_calibration"), "deepseek_cost_calibration.yaml"),
)
POLICY_PATHS = frozenset("orchestration/harness_settings/" + name for name in POLICY_SCHEMAS)


def validate_recovery_configuration(*, documents: dict[str, bytes], expected_sha256: dict[str, str],
                                    agents_text: str, state: dict) -> core.ValidatedConfiguration:
    snapshot = core.validate_configuration(documents=documents, expected_sha256=expected_sha256,
        schemas=POLICY_SCHEMAS, references=POLICY_REFERENCES, roots=("project.yaml",))
    values = {name: json.loads(raw) for name, raw in snapshot.documents}
    project, continuation = values["project.yaml"], values["autonomous_continuation.yaml"]
    validate_precedence(project, continuation, agents_text, state)
    operating, security = values["operating_model.yaml"], values["security_review_protocol.yaml"]
    verifier, cost = values["verifier_execution_policy.yaml"], values["cost_controls.yaml"]
    direction, workflow = values["direction_collaboration.yaml"], values["evidence_led_workflow.yaml"]
    overlay = values["programme_recovery.yaml"]
    checks = (
        project["project_id"] == "emr4",
        project["master_authority"] == {"exclusive_role": "orchestrator", "conductor_can_commit": False,
                                       "verifier_can_commit": False},
        project["allocation"]["live_agent_adapters_enabled"] is False,
        operating["verifier"]["deterministic_plan_checks_always_run"] is True,
        operating["verifier"]["external_dispatch_only_after_deterministic_pass"] is True,
        operating["verifier"]["deterministic_failure_action"] == "no_external_model_call",
        operating["integration_checkpoints"]["workers_may_push_master"] is False,
        operating["integration_checkpoints"]["executor_may_push_master_without_authorization"] is False,
        security["risk_classification"] == {
            "default_tier": "routine_delta", "security_sensitive_tier": "dual_review",
            "security_sensitive_triggers": ["authentication_authorization", "phi_sensitive_data",
                "api_or_write_authority", "confirmation_workflow", "provider_prompt_tool_execution",
                "database_schema_rls", "cryptography_key_or_randomness", "audit_logging", "deployment_release",
                "externally_reachable_ui", "ci_supply_chain", "security_control_change", "cross_layer_security_tranche"],
            "purple_review_triggers": ["deployment_release", "provider_prompt_tool_execution", "cross_layer_security_tranche"],
            "maximum_material_sprints_between_purple": 4},
        all(security["roles"][role]["required_for_tier"] == "dual_review" for role in ("blue", "red")),
        all(security["independence"][key] is True for key in
            ("asymmetric_packets_required", "red_fresh_context_required", "red_candidate_only_required",
             "red_prior_review_artifacts_excluded", "workers_cannot_self_certify")),
        security["acceptance"]["required_decision"] == "pass",
        security["acceptance"]["blocking_unresolved_severities"] == ["critical", "high"],
        security["acceptance"]["artifact_sha256_required"] is True,
        security["acceptance"]["artifact_must_bind_candidate"] is True,
        security["recovery"]["exact_final_independent_pass_required"] is True,
        verifier["deterministic_gate"]["required_before_external_model_dispatch"] is True,
        verifier["deterministic_gate"]["fail_closed_action"] == "no_external_model_call",
        verifier["external_verifier"]["silent_model_fallback"] == "forbidden",
        verifier["external_verifier"]["implementation_capability"] == "forbidden",
        verifier["external_verifier"]["decision_contract"]["allowed"] == ["pass", "revision_required"],
        verifier["external_verifier"]["decision_contract"]["exact_terminal_decision_count"] == 1,
        verifier["external_verifier"]["decision_contract"]["additional_properties"] == "forbidden",
        verifier["external_verifier"]["environment_boundary"]["package_or_environment_bootstrap"] == "forbidden",
        direction["mode"] == "optional_bounded_dialogue",
        direction["dialogue"]["maximum_orchestrator_rejoinders"] == 1,
        continuation["default_posture"] == "continue_without_user_permission",
        continuation["emergency_programme_overlay"]["missing_or_invalid"] == "hard_stop",
        cost["current_profile"]["accounting_mode"] == "subscription_usage_window",
        cost["current_profile"]["monetary_budget_enforcement"] == "inactive",
        cost["current_profile"]["pass_cli_max_budget_usd"] is False,
        cost["activation"]["requires_explicit_user_override"] is True,
        cost["fallback_semantics"]["estimated_cost_or_local_cap_exceeded_triggers_fallback"] is False,
        workflow["closed_surfaces"] == ["database_or_docker_runtime", "provider_or_external_retrieval",
            "real_product_patient_or_clinical_data", "protected_evidence", "credentials_or_iam",
            "executable_product_tool_or_command", "deployment_production_release_pages", "protected_refs"],
        overlay["active_profile"] == state["active_profile"],
        overlay["missing_or_invalid_state"] == "hard_stop",
    )
    if not all(checks):
        raise RaisaPolicyError("configuration_recovery_semantics_invalid")
    for item in values["deepseek_cost_calibration.yaml"]["calibrations"]:
        if item["sample_count"] < 1 or "do_not_treat_as_authoritative_billing" not in item["restrictions"]:
            raise RaisaPolicyError("configuration_calibration_semantics_invalid")
    if state["active_profile"] == G1E_PROFILE and overlay["profiles"][G1E_PROFILE] != configuration_profile():
        raise RaisaPolicyError("configuration_assessment_profile_invalid")
    return snapshot
