window.META_GRID_FIXTURES = {
  "schema_version": "bernie.meta-grid-concept-fixtures.v0",
  "authored_synthetic": true,
  "contains_real_patient_or_practice_data": false,
  "projections": {
    "overview": {
      "contract_version": "bernie.meta-grid-projection.v0",
      "projection_id": "projection-overview",
      "projection_revision": 1,
      "root_intent_id": "intent-overview",
      "family": "ordinary_overview",
      "state": "overview",
      "scope": {
        "practice_id": "synthetic-practice-brisbane",
        "timezone": "Australia/Brisbane",
        "patient_ids": [],
        "practitioner_ids": [],
        "date_from": "2026-07-31",
        "date_to": "2026-07-31",
        "time_from": "08:00",
        "time_to": "17:00",
        "location_ids": ["synthetic-location-brisbane"],
        "room_ids": [],
        "waiting_area_ids": [],
        "status_allowlist": ["booked", "confirmed", "available", "break"],
        "appointment_type_ids": [],
        "duration_minutes": null,
        "result_limit": 50
      },
      "scope_summary": "Ordinary overview · Friday 31 July 2026 · Brisbane Clinic",
      "omissions": ["This concept overview contains authored synthetic data only"],
      "freshness": {
        "source": "concept_overview",
        "observed_at": "2026-07-20T04:00:00Z",
        "expires_at": null,
        "stale": false,
        "reason": "Authored synthetic overview for reversible fallback"
      },
      "items": [
        {
          "item_id": "overview-shera",
          "kind": "overview_entry",
          "display": "Dr Shera · 3 appointments",
          "date": "2026-07-31",
          "starts_at": "2026-07-31T03:00:00Z",
          "ends_at": "2026-07-31T06:00:00Z",
          "patient_display": null,
          "practitioner_display": "Dr Michael Shera",
          "location_display": "Brisbane Clinic",
          "status": "summary",
          "warnings": [],
          "selectable": false,
          "changed": false,
          "comparison_group": null
        },
        {
          "item_id": "overview-patel",
          "kind": "overview_entry",
          "display": "Dr Patel · 2 appointments",
          "date": "2026-07-31",
          "starts_at": "2026-07-31T00:30:00Z",
          "ends_at": "2026-07-31T04:00:00Z",
          "patient_display": null,
          "practitioner_display": "Dr Anika Patel",
          "location_display": "Brisbane Clinic",
          "status": "summary",
          "warnings": [],
          "selectable": false,
          "changed": false,
          "comparison_group": null
        }
      ],
      "layout_hint": "overview_grid",
      "affordances": ["refine", "back", "explain"],
      "parent_projection_id": null,
      "transition": {
        "operation": "reset",
        "trigger": "keyboard",
        "reason": "User requested the ordinary Diary overview",
        "changed_dimensions": ["projection_family", "transient_state"]
      },
      "action_boundary": {
        "posture": "none",
        "appointment_write_authority": false,
        "operational_command_available": false,
        "required_backend_pattern": null
      },
      "evidence_mode": "authored_synthetic_local_static_prototype"
    },
    "sheraFocus": {
      "contract_version": "bernie.meta-grid-projection.v0",
      "projection_id": "projection-shera-friday-afternoon",
      "projection_revision": 1,
      "root_intent_id": "intent-shera-friday-afternoon",
      "family": "focused_schedule_lane",
      "state": "answer",
      "scope": {
        "practice_id": "synthetic-practice-brisbane",
        "timezone": "Australia/Brisbane",
        "patient_ids": [],
        "practitioner_ids": ["synthetic-practitioner-shera"],
        "date_from": "2026-07-31",
        "date_to": "2026-07-31",
        "time_from": "12:00",
        "time_to": "17:00",
        "location_ids": ["synthetic-location-brisbane"],
        "room_ids": [],
        "waiting_area_ids": [],
        "status_allowlist": ["booked", "available", "break"],
        "appointment_type_ids": [],
        "duration_minutes": null,
        "result_limit": 20
      },
      "scope_summary": "Dr Shera · Friday 31 July 2026 · 12 pm–5 pm · Brisbane Clinic",
      "omissions": ["Other practitioners hidden", "Times outside 12 pm–5 pm hidden"],
      "freshness": {
        "source": "authorised_diary_read",
        "observed_at": "2026-07-20T04:00:00Z",
        "expires_at": "2026-07-20T04:05:00Z",
        "stale": false,
        "reason": "Fresh authored synthetic Diary read for the requested practitioner window"
      },
      "items": [
        {
          "item_id": "appointment-john-1300",
          "kind": "appointment",
          "display": "John Ellis · 1:00 pm–1:30 pm",
          "date": "2026-07-31",
          "starts_at": "2026-07-31T03:00:00Z",
          "ends_at": "2026-07-31T03:30:00Z",
          "patient_display": "John Ellis",
          "practitioner_display": "Dr Michael Shera",
          "location_display": "Brisbane Clinic",
          "status": "booked",
          "warnings": [],
          "selectable": false,
          "changed": false,
          "comparison_group": null
        },
        {
          "item_id": "appointment-margaret-1415",
          "kind": "appointment",
          "display": "Margaret Thompson · 2:15 pm–2:45 pm",
          "date": "2026-07-31",
          "starts_at": "2026-07-31T04:15:00Z",
          "ends_at": "2026-07-31T04:45:00Z",
          "patient_display": "Margaret Thompson",
          "practitioner_display": "Dr Michael Shera",
          "location_display": "Brisbane Clinic",
          "status": "booked",
          "warnings": [],
          "selectable": false,
          "changed": false,
          "comparison_group": null
        },
        {
          "item_id": "appointment-amy-1530",
          "kind": "appointment",
          "display": "Amy Wright · 3:30 pm–4:00 pm",
          "date": "2026-07-31",
          "starts_at": "2026-07-31T05:30:00Z",
          "ends_at": "2026-07-31T06:00:00Z",
          "patient_display": "Amy Wright",
          "practitioner_display": "Dr Michael Shera",
          "location_display": "Brisbane Clinic",
          "status": "booked",
          "warnings": [],
          "selectable": false,
          "changed": false,
          "comparison_group": null
        }
      ],
      "layout_hint": "time_lane",
      "affordances": ["inspect", "refine", "broaden", "compare", "back", "reset", "explain"],
      "parent_projection_id": null,
      "transition": {
        "operation": "project",
        "trigger": "conversation",
        "reason": "User requested one practitioner's Friday-week afternoon view",
        "changed_dimensions": ["practitioner", "date", "time", "location"]
      },
      "action_boundary": {
        "posture": "none",
        "appointment_write_authority": false,
        "operational_command_available": false,
        "required_backend_pattern": null
      },
      "evidence_mode": "authored_synthetic_local_static_prototype"
    },
    "margaretTimeline": {
      "contract_version": "bernie.meta-grid-projection.v0",
      "projection_id": "projection-margaret-upcoming",
      "projection_revision": 1,
      "root_intent_id": "intent-margaret-upcoming",
      "family": "patient_timeline",
      "state": "answer",
      "scope": {
        "practice_id": "synthetic-practice-brisbane",
        "timezone": "Australia/Brisbane",
        "patient_ids": ["synthetic-patient-margaret"],
        "practitioner_ids": [],
        "date_from": "2026-07-20",
        "date_to": "2027-07-20",
        "time_from": null,
        "time_to": null,
        "location_ids": ["synthetic-location-brisbane"],
        "room_ids": [],
        "waiting_area_ids": [],
        "status_allowlist": ["booked", "confirmed"],
        "appointment_type_ids": [],
        "duration_minutes": null,
        "result_limit": 20
      },
      "scope_summary": "Margaret Thompson · upcoming appointments · Brisbane Clinic · next 12 months",
      "omissions": ["Cancelled appointments hidden", "Past appointments hidden"],
      "freshness": {
        "source": "authorised_patient_read",
        "observed_at": "2026-07-20T04:00:00Z",
        "expires_at": "2026-07-20T04:05:00Z",
        "stale": false,
        "reason": "Fresh authored synthetic patient appointment read"
      },
      "items": [
        {
          "item_id": "margaret-20260731",
          "kind": "appointment",
          "display": "Friday 31 July 2026 · 2:15 pm · Dr Shera",
          "date": "2026-07-31",
          "starts_at": "2026-07-31T04:15:00Z",
          "ends_at": "2026-07-31T04:45:00Z",
          "patient_display": "Margaret Thompson",
          "practitioner_display": "Dr Michael Shera",
          "location_display": "Brisbane Clinic",
          "status": "booked",
          "warnings": [],
          "selectable": false,
          "changed": false,
          "comparison_group": null
        },
        {
          "item_id": "margaret-20260814",
          "kind": "appointment",
          "display": "Friday 14 August 2026 · 10:00 am · Dr Patel",
          "date": "2026-08-14",
          "starts_at": "2026-08-14T00:00:00Z",
          "ends_at": "2026-08-14T00:30:00Z",
          "patient_display": "Margaret Thompson",
          "practitioner_display": "Dr Anika Patel",
          "location_display": "Brisbane Clinic",
          "status": "confirmed",
          "warnings": [],
          "selectable": false,
          "changed": false,
          "comparison_group": null
        },
        {
          "item_id": "margaret-20270120",
          "kind": "appointment",
          "display": "Wednesday 20 January 2027 · 2:30 pm · Dr Shera",
          "date": "2027-01-20",
          "starts_at": "2027-01-20T04:30:00Z",
          "ends_at": "2027-01-20T05:00:00Z",
          "patient_display": "Margaret Thompson",
          "practitioner_display": "Dr Michael Shera",
          "location_display": "Brisbane Clinic",
          "status": "booked",
          "warnings": [],
          "selectable": false,
          "changed": false,
          "comparison_group": null
        }
      ],
      "layout_hint": "timeline",
      "affordances": ["inspect", "refine", "broaden", "back", "reset", "explain"],
      "parent_projection_id": null,
      "transition": {
        "operation": "project",
        "trigger": "conversation",
        "reason": "User requested one patient's future appointments",
        "changed_dimensions": ["patient", "date_range", "status"]
      },
      "action_boundary": {
        "posture": "none",
        "appointment_write_authority": false,
        "operational_command_available": false,
        "required_backend_pattern": null
      },
      "evidence_mode": "authored_synthetic_local_static_prototype"
    },
    "availability": {
      "contract_version": "bernie.meta-grid-projection.v0",
      "projection_id": "projection-shera-availability",
      "projection_revision": 1,
      "root_intent_id": "intent-shera-availability",
      "family": "availability_slots",
      "state": "answer",
      "scope": {
        "practice_id": "synthetic-practice-brisbane",
        "timezone": "Australia/Brisbane",
        "patient_ids": [],
        "practitioner_ids": ["synthetic-practitioner-shera"],
        "date_from": "2026-07-31",
        "date_to": "2026-07-31",
        "time_from": "14:00",
        "time_to": "17:00",
        "location_ids": ["synthetic-location-brisbane"],
        "room_ids": [],
        "waiting_area_ids": [],
        "status_allowlist": ["available"],
        "appointment_type_ids": [],
        "duration_minutes": 30,
        "result_limit": 10
      },
      "scope_summary": "Dr Shera · available 30-minute slots · Friday 31 July 2026 · after 2 pm",
      "omissions": ["Booked time hidden except where needed to explain gaps", "Other practitioners hidden"],
      "freshness": {
        "source": "deterministic_availability_read",
        "observed_at": "2026-07-20T04:01:00Z",
        "expires_at": "2026-07-20T04:03:00Z",
        "stale": false,
        "reason": "Deterministic authored synthetic availability read"
      },
      "items": [
        {
          "item_id": "slot-shera-1445",
          "kind": "available_slot",
          "display": "2:45 pm–3:15 pm",
          "date": "2026-07-31",
          "starts_at": "2026-07-31T04:45:00Z",
          "ends_at": "2026-07-31T05:15:00Z",
          "patient_display": null,
          "practitioner_display": "Dr Michael Shera",
          "location_display": "Brisbane Clinic",
          "status": "available_at_read_time",
          "warnings": ["Availability must be revalidated before confirmation"],
          "selectable": true,
          "changed": false,
          "comparison_group": null
        },
        {
          "item_id": "slot-shera-1600",
          "kind": "available_slot",
          "display": "4:00 pm–4:30 pm",
          "date": "2026-07-31",
          "starts_at": "2026-07-31T06:00:00Z",
          "ends_at": "2026-07-31T06:30:00Z",
          "patient_display": null,
          "practitioner_display": "Dr Michael Shera",
          "location_display": "Brisbane Clinic",
          "status": "available_at_read_time",
          "warnings": ["Availability must be revalidated before confirmation"],
          "selectable": true,
          "changed": false,
          "comparison_group": null
        }
      ],
      "layout_hint": "slot_list",
      "affordances": ["refine", "broaden", "compare", "select", "back", "reset", "explain"],
      "parent_projection_id": null,
      "transition": {
        "operation": "project",
        "trigger": "conversation",
        "reason": "User requested deterministic availability after 2 pm",
        "changed_dimensions": ["practitioner", "date", "time", "duration", "availability"]
      },
      "action_boundary": {
        "posture": "selection_only",
        "appointment_write_authority": false,
        "operational_command_available": false,
        "required_backend_pattern": "Future slot selection may prepare an existing appointment proposal; confirmation remains a separate REST command"
      },
      "evidence_mode": "authored_synthetic_local_static_prototype"
    },
    "comparison": {
      "contract_version": "bernie.meta-grid-projection.v0",
      "projection_id": "projection-shera-patel-comparison",
      "projection_revision": 1,
      "root_intent_id": "intent-shera-patel-comparison",
      "family": "aligned_comparison",
      "state": "answer",
      "scope": {
        "practice_id": "synthetic-practice-brisbane",
        "timezone": "Australia/Brisbane",
        "patient_ids": [],
        "practitioner_ids": ["synthetic-practitioner-shera", "synthetic-practitioner-patel"],
        "date_from": "2026-07-21",
        "date_to": "2026-07-21",
        "time_from": "08:00",
        "time_to": "12:00",
        "location_ids": ["synthetic-location-brisbane"],
        "room_ids": [],
        "waiting_area_ids": [],
        "status_allowlist": ["available"],
        "appointment_type_ids": [],
        "duration_minutes": 30,
        "result_limit": 20
      },
      "scope_summary": "Dr Shera compared with Dr Patel · Tuesday 21 July 2026 · 8 am–12 pm · 30 minutes",
      "omissions": ["Other practitioners hidden", "Only aligned availability shown"],
      "freshness": {
        "source": "authorised_comparison_read",
        "observed_at": "2026-07-20T04:02:00Z",
        "expires_at": "2026-07-20T04:04:00Z",
        "stale": false,
        "reason": "Both practitioner scopes share the same authored synthetic temporal and location basis"
      },
      "items": [
        {
          "item_id": "comparison-shera-0900",
          "kind": "comparison_slot",
          "display": "9:00 am–9:30 am",
          "date": "2026-07-21",
          "starts_at": "2026-07-20T23:00:00Z",
          "ends_at": "2026-07-20T23:30:00Z",
          "patient_display": null,
          "practitioner_display": "Dr Michael Shera",
          "location_display": "Brisbane Clinic",
          "status": "available_at_read_time",
          "warnings": [],
          "selectable": true,
          "changed": false,
          "comparison_group": "Dr Michael Shera"
        },
        {
          "item_id": "comparison-patel-0930",
          "kind": "comparison_slot",
          "display": "9:30 am–10:00 am",
          "date": "2026-07-21",
          "starts_at": "2026-07-20T23:30:00Z",
          "ends_at": "2026-07-21T00:00:00Z",
          "patient_display": null,
          "practitioner_display": "Dr Anika Patel",
          "location_display": "Brisbane Clinic",
          "status": "available_at_read_time",
          "warnings": [],
          "selectable": true,
          "changed": false,
          "comparison_group": "Dr Anika Patel"
        },
        {
          "item_id": "comparison-shera-1100",
          "kind": "comparison_slot",
          "display": "11:00 am–11:30 am",
          "date": "2026-07-21",
          "starts_at": "2026-07-21T01:00:00Z",
          "ends_at": "2026-07-21T01:30:00Z",
          "patient_display": null,
          "practitioner_display": "Dr Michael Shera",
          "location_display": "Brisbane Clinic",
          "status": "available_at_read_time",
          "warnings": [],
          "selectable": true,
          "changed": false,
          "comparison_group": "Dr Michael Shera"
        }
      ],
      "layout_hint": "aligned_lanes",
      "affordances": ["refine", "broaden", "select", "back", "reset", "explain"],
      "parent_projection_id": null,
      "transition": {
        "operation": "compare",
        "trigger": "conversation",
        "reason": "User requested aligned morning availability for two practitioners",
        "changed_dimensions": ["practitioner_set", "comparison_basis"]
      },
      "action_boundary": {
        "posture": "selection_only",
        "appointment_write_authority": false,
        "operational_command_available": false,
        "required_backend_pattern": "Selection may become proposal input only after a fresh backend read"
      },
      "evidence_mode": "authored_synthetic_local_static_prototype"
    },
    "clarification": {
      "contract_version": "bernie.meta-grid-projection.v0",
      "projection_id": "projection-clarify-alex",
      "projection_revision": 1,
      "root_intent_id": "intent-clarify-alex",
      "family": "clarification",
      "state": "clarification_required",
      "scope": {
        "practice_id": "synthetic-practice-brisbane",
        "timezone": "Australia/Brisbane",
        "patient_ids": [],
        "practitioner_ids": [],
        "date_from": "2026-07-31",
        "date_to": "2026-07-31",
        "time_from": null,
        "time_to": null,
        "location_ids": ["synthetic-location-brisbane"],
        "room_ids": [],
        "waiting_area_ids": [],
        "status_allowlist": [],
        "appointment_type_ids": [],
        "duration_minutes": null,
        "result_limit": 5
      },
      "scope_summary": "Clarification needed · ‘Alex’ matches more than one authored synthetic person",
      "omissions": ["No Diary projection displayed until identity is clarified"],
      "freshness": {
        "source": "authorised_diary_read",
        "observed_at": "2026-07-20T04:03:00Z",
        "expires_at": "2026-07-20T04:05:00Z",
        "stale": false,
        "reason": "Minimum synthetic candidate information only"
      },
      "items": [],
      "layout_hint": "clarification_list",
      "affordances": ["clarify", "back", "reset", "explain"],
      "parent_projection_id": null,
      "transition": {
        "operation": "clarify",
        "trigger": "conversation",
        "reason": "Identity reference is ambiguous",
        "changed_dimensions": ["identity_resolution"]
      },
      "action_boundary": {
        "posture": "none",
        "appointment_write_authority": false,
        "operational_command_available": false,
        "required_backend_pattern": null
      },
      "evidence_mode": "authored_synthetic_local_static_prototype"
    },
    "changeContext": {
      "contract_version": "bernie.meta-grid-projection.v0",
      "projection_id": "projection-margaret-change-context",
      "projection_revision": 2,
      "root_intent_id": "intent-margaret-change-context",
      "family": "change_context",
      "state": "committed_change_notice",
      "scope": {
        "practice_id": "synthetic-practice-brisbane",
        "timezone": "Australia/Brisbane",
        "patient_ids": ["synthetic-patient-margaret"],
        "practitioner_ids": ["synthetic-practitioner-shera"],
        "date_from": "2026-07-31",
        "date_to": "2026-07-31",
        "time_from": "12:00",
        "time_to": "17:00",
        "location_ids": ["synthetic-location-brisbane"],
        "room_ids": [],
        "waiting_area_ids": [],
        "status_allowlist": ["booked"],
        "appointment_type_ids": [],
        "duration_minutes": 30,
        "result_limit": 5
      },
      "scope_summary": "Margaret Thompson · Dr Shera · Friday 31 July 2026 · Brisbane Clinic",
      "omissions": ["Event payload facts not displayed", "Current authorised read supplies the appointment details"],
      "freshness": {
        "source": "fresh_read_after_event_fixture",
        "observed_at": "2026-07-20T04:07:00Z",
        "expires_at": "2026-07-20T04:09:00Z",
        "stale": false,
        "reason": "Fresh synthetic read after one relevant committed reschedule fixture"
      },
      "items": [
        {
          "item_id": "margaret-rescheduled-1445",
          "kind": "appointment",
          "display": "Margaret Thompson · now 2:45 pm–3:15 pm",
          "date": "2026-07-31",
          "starts_at": "2026-07-31T04:45:00Z",
          "ends_at": "2026-07-31T05:15:00Z",
          "patient_display": "Margaret Thompson",
          "practitioner_display": "Dr Michael Shera",
          "location_display": "Brisbane Clinic",
          "status": "booked",
          "warnings": [],
          "selectable": false,
          "changed": true,
          "comparison_group": null
        }
      ],
      "layout_hint": "change_diff",
      "affordances": ["inspect", "reconcile", "back", "reset", "explain"],
      "parent_projection_id": null,
      "transition": {
        "operation": "reconcile",
        "trigger": "event_fixture",
        "reason": "Relevant committed typed fixture confirmed by a fresh scoped synthetic read",
        "changed_dimensions": ["start_time", "end_time", "projection_revision"]
      },
      "action_boundary": {
        "posture": "none",
        "appointment_write_authority": false,
        "operational_command_available": false,
        "required_backend_pattern": null
      },
      "evidence_mode": "authored_synthetic_event_fixture"
    },
    "proposal": {
      "contract_version": "bernie.meta-grid-projection.v0",
      "projection_id": "projection-margaret-proposal",
      "projection_revision": 1,
      "root_intent_id": "intent-shera-availability",
      "family": "proposal_review",
      "state": "proposal_not_committed",
      "scope": {
        "practice_id": "synthetic-practice-brisbane",
        "timezone": "Australia/Brisbane",
        "patient_ids": ["synthetic-patient-margaret"],
        "practitioner_ids": ["synthetic-practitioner-shera"],
        "date_from": "2026-07-31",
        "date_to": "2026-07-31",
        "time_from": "14:45",
        "time_to": "15:15",
        "location_ids": ["synthetic-location-brisbane"],
        "room_ids": [],
        "waiting_area_ids": [],
        "status_allowlist": ["available_at_read_time"],
        "appointment_type_ids": ["synthetic-appointment-type-standard"],
        "duration_minutes": 30,
        "result_limit": 1
      },
      "scope_summary": "Proposal · Margaret Thompson · Dr Shera · Friday 31 July 2026 · 2:45 pm",
      "omissions": ["No appointment has been created", "Confirmation is disabled in this concept lab"],
      "freshness": {
        "source": "deterministic_availability_read",
        "observed_at": "2026-07-20T04:01:00Z",
        "expires_at": "2026-07-20T04:03:00Z",
        "stale": false,
        "reason": "Authored proposal review based on selected synthetic slot"
      },
      "items": [
        {
          "item_id": "proposal-margaret-1445",
          "kind": "proposal_summary",
          "display": "Add Margaret Thompson with Dr Shera at 2:45 pm for 30 minutes",
          "date": "2026-07-31",
          "starts_at": "2026-07-31T04:45:00Z",
          "ends_at": "2026-07-31T05:15:00Z",
          "patient_display": "Margaret Thompson",
          "practitioner_display": "Dr Michael Shera",
          "location_display": "Brisbane Clinic",
          "status": "proposal_not_committed",
          "warnings": ["Backend revalidation and explicit staff confirmation are still required"],
          "selectable": false,
          "changed": false,
          "comparison_group": null
        }
      ],
      "layout_hint": "proposal_summary",
      "affordances": ["back", "reset", "explain"],
      "parent_projection_id": "projection-shera-availability-selection-slot-shera-1445",
      "transition": {
        "operation": "prepare_proposal",
        "trigger": "touch",
        "reason": "Staff selected the synthetic slot and identified Margaret Thompson",
        "changed_dimensions": ["patient", "state", "action_boundary"]
      },
      "action_boundary": {
        "posture": "proposal_only",
        "appointment_write_authority": false,
        "operational_command_available": false,
        "required_backend_pattern": "Existing REST proposal and explicit confirmation command with revalidation, idempotency, audit and receipt"
      },
      "evidence_mode": "authored_synthetic_local_static_prototype"
    }
  },
  "event_fixtures": [
    {
      "event_id": "fixture-relevant-reschedule-1",
      "event_type": "diary.appointment_rescheduled",
      "aggregate_revision": 2,
      "practice_id": "synthetic-practice-brisbane",
      "classification": "relevant_committed",
      "expected_effect": "concise_notice_then_fresh_read"
    },
    {
      "event_id": "fixture-unrelated-roster-1",
      "event_type": "diary.roster_changed",
      "aggregate_revision": 1,
      "practice_id": "synthetic-practice-brisbane",
      "classification": "unrelated",
      "expected_effect": "silent_suppression"
    },
    {
      "event_id": "fixture-relevant-reschedule-1",
      "event_type": "diary.appointment_rescheduled",
      "aggregate_revision": 2,
      "practice_id": "synthetic-practice-brisbane",
      "classification": "replay",
      "expected_effect": "duplicate_suppression"
    },
    {
      "event_id": "fixture-older-reschedule-1",
      "event_type": "diary.appointment_rescheduled",
      "aggregate_revision": 1,
      "practice_id": "synthetic-practice-brisbane",
      "classification": "stale_revision",
      "expected_effect": "stale_suppression"
    }
  ]
};
