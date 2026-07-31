# Reception One v6.2 Full-Cohort Test Notebook

Status: complete
Cases closed: 24 / 24
Provider calls consumed: 30 / 48

This is a sanitized authored-synthetic comparison notebook, not a raw provider log. It includes all original v6 requests. Raw provider packets, credentials, API-key information and hidden chain-of-thought are excluded.

## 1. b-create-arrange

```json
{
  "actual_provider_calls": 1,
  "admitted_operator_ids": [
    "resolve_patient_reference",
    "resolve_practitioner_reference",
    "resolve_date_expression",
    "search_available_slots",
    "prepare_create_proposal"
  ],
  "case_code": "b-create-arrange",
  "cleanup_passed": true,
  "context_frame_review": {
    "command_authority": false,
    "desk_context_sha256": "sha256:48490e382ccd71f1b90944ff4255d973e05175711390e75031bfe1762823ffd8",
    "disposition": "admit",
    "reviewed_context_revision": 62,
    "same_packet_seen_by_model_and_proofreader": true,
    "source_labels": [
      "fixture_intercepted",
      "staff_selected",
      "staff_selected"
    ],
    "task_sha256": "sha256:bf7f7452ee789444f7a9c35452359f86c6691208d3491148a7ccd6361d73f696"
  },
  "correction_used": false,
  "exact_binding": {
    "api_key_authentication_used": false,
    "authentication": "keyless_impersonated_service_account_adc",
    "endpoint_hostname": "australia-southeast1-aiplatform.googleapis.com",
    "location": "australia-southeast1",
    "model_id": "gemini-2.5-flash",
    "project": "bernie-emr4-dev",
    "provider": "google_vertex_ai",
    "service_account": "emr4-bernie-ai-dev@bernie-emr4-dev.iam.gserviceaccount.com"
  },
  "expected_goal": "create",
  "expected_proposal_family": "create",
  "expected_proposal_release": true,
  "expected_safe_outcome": true,
  "final_proofreader_disposition": "admit",
  "final_violation_codes": [],
  "operator_note": {
    "audit_only": true,
    "disposition": "admit",
    "note_sha256": "sha256:d0bde6f469f2dc67f76be9f46670e7eb4b523d2294cad67b9ff0a57c8c7206df",
    "operator_note": "Proposal for review: no booking was changed.",
    "parsed_into_plan": false,
    "product_delivered": false,
    "reason_codes": [],
    "retained_utf8_bytes": 44
  },
  "parent_audit_chain": {
    "event_count": 4,
    "terminal_hash": "sha256:11899d5c1bfe0207507e7f5f0751aa06c8b4dd716fd5e336949028bafdc1d394",
    "valid": true
  },
  "primary_exact_body_accepted": true,
  "primary_proofreader_disposition": "admit",
  "primary_violation_codes": [],
  "provider_outcomes": [
    {
      "bounded_completion_metadata": {
        "candidate_count": 1,
        "candidate_count_truncated": false,
        "finish_reasons": [
          "STOP"
        ],
        "part_counts": [
          1
        ],
        "provider_text_inspected_for_diagnosis": false,
        "provider_text_retained": false
      },
      "bounded_error": null,
      "http_status": 200,
      "latency_ms": 7026,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 863,
        "promptTokenCount": 3728,
        "thoughtsTokenCount": 1041,
        "totalTokenCount": 5632
      }
    }
  ],
  "receptionist_output": {
    "decision_note": "Intent create: All necessary information for creating an appointment is present.",
    "disposition": "admit",
    "evidence_utterance_indices": [
      0
    ],
    "hidden_reasoning": false,
    "natural_response_parsed_into_form": false,
    "product_delivered": false,
    "raw_provider_response": false,
    "receptionist_response": "I am preparing a proposal to arrange an appointment for Margaret Thompson with Dr Shera tomorrow at 2:30 pm for 15 minutes. This will be reviewed for confirmation; no booking was changed.",
    "violations": []
  },
  "release": {
    "api_spine_operation_id": "proposeAppointmentCreate",
    "appointment_ref": null,
    "candidate_slot_ids": [
      "synthetic-slot-july28-1430"
    ],
    "duration_minutes": 15,
    "kind": "proposal_candidate",
    "patient_ref": "synthetic-patient-margaret",
    "practitioner_ref": "synthetic-practitioner-shera",
    "proposal_family": "create",
    "requires_human_confirmation": true,
    "status": null,
    "warning_codes": [
      "no_reservation",
      "staff_confirmation_required",
      "staff_selection_required"
    ],
    "write_performed": false
  },
  "source_case_id": null,
  "terminal_second_call_reason": null,
  "terminal_status": "admitted",
  "typed_program": {
    "explicit_source_form": {
      "goal_code": 0,
      "steps": [
        {
          "operator_code": 0,
          "source_refs": [
            {
              "binding_code": 5,
              "kind": "binding",
              "prior_output_name": "none",
              "prior_step_index": -1
            }
          ]
        },
        {
          "operator_code": 1,
          "source_refs": [
            {
              "binding_code": 6,
              "kind": "binding",
              "prior_output_name": "none",
              "prior_step_index": -1
            }
          ]
        },
        {
          "operator_code": 2,
          "source_refs": [
            {
              "binding_code": 0,
              "kind": "binding",
              "prior_output_name": "none",
              "prior_step_index": -1
            }
          ]
        },
        {
          "operator_code": 6,
          "source_refs": [
            {
              "binding_code": -1,
              "kind": "prior_output",
              "prior_output_name": "practitioner",
              "prior_step_index": 1
            },
            {
              "binding_code": -1,
              "kind": "prior_output",
              "prior_output_name": "date",
              "prior_step_index": 2
            },
            {
              "binding_code": 3,
              "kind": "binding",
              "prior_output_name": "none",
              "prior_step_index": -1
            },
            {
              "binding_code": 4,
              "kind": "binding",
              "prior_output_name": "none",
              "prior_step_index": -1
            },
            {
              "binding_code": 2,
              "kind": "binding",
              "prior_output_name": "none",
              "prior_step_index": -1
            }
          ]
        },
        {
          "operator_code": 8,
          "source_refs": [
            {
              "binding_code": -1,
              "kind": "prior_output",
              "prior_output_name": "patient",
              "prior_step_index": 0
            },
            {
              "binding_code": -1,
              "kind": "prior_output",
              "prior_output_name": "practitioner",
              "prior_step_index": 1
            },
            {
              "binding_code": -1,
              "kind": "prior_output",
              "prior_output_name": "candidates",
              "prior_step_index": 3
            },
            {
              "binding_code": 2,
              "kind": "binding",
              "prior_output_name": "none",
              "prior_step_index": -1
            }
          ]
        }
      ],
      "version_code": 3
    },
    "operator_note_excluded": true,
    "program_hash": "sha256:c5e500f4c4aeca5551f1c6331d8be821b6db642dca7d57a49aa708a259d16ad6",
    "raw_provider_response": false
  }
}
```

## 2. b-create-alias

```json
{
  "actual_provider_calls": 2,
  "admitted_operator_ids": [],
  "case_code": "b-create-alias",
  "cleanup_passed": true,
  "context_frame_review": {
    "desk_context_sha256": "sha256:ba08144d5519f4ffb55d0d745e10ce177abe2eb2d9978be26bede5e6a0d3bdd8",
    "disposition": "not_reached",
    "reason": "provider_response_rejected_before_candidate",
    "release": null,
    "same_packet_seen_by_model_and_proofreader": false
  },
  "correction_used": true,
  "exact_binding": {
    "api_key_authentication_used": false,
    "authentication": "keyless_impersonated_service_account_adc",
    "endpoint_hostname": "australia-southeast1-aiplatform.googleapis.com",
    "location": "australia-southeast1",
    "model_id": "gemini-2.5-flash",
    "project": "bernie-emr4-dev",
    "provider": "google_vertex_ai",
    "service_account": "emr4-bernie-ai-dev@bernie-emr4-dev.iam.gserviceaccount.com"
  },
  "expected_goal": "create",
  "expected_proposal_family": "create",
  "expected_proposal_release": true,
  "expected_safe_outcome": false,
  "final_proofreader_disposition": null,
  "final_violation_codes": [
    "provider_text_not_json"
  ],
  "operator_note": null,
  "parent_audit_chain": {
    "event_count": 4,
    "terminal_hash": "sha256:a948e77ba66630390ffbbb806346569b325d11894a3ea4ada01fb8389040f629",
    "valid": true
  },
  "primary_exact_body_accepted": false,
  "primary_proofreader_disposition": null,
  "primary_violation_codes": [
    "provider_text_not_json"
  ],
  "provider_outcomes": [
    {
      "bounded_completion_metadata": {
        "candidate_count": 1,
        "candidate_count_truncated": false,
        "finish_reasons": [
          "MAX_TOKENS"
        ],
        "part_counts": [
          1
        ],
        "provider_text_inspected_for_diagnosis": false,
        "provider_text_retained": false
      },
      "bounded_error": {
        "field_paths": [],
        "reason_code": "provider_text_not_json"
      },
      "http_status": 200,
      "latency_ms": 7931,
      "status": "response_rejected_before_candidate",
      "usage": {
        "candidatesTokenCount": 660,
        "promptTokenCount": 3705,
        "thoughtsTokenCount": 1374,
        "totalTokenCount": 5739
      }
    },
    {
      "bounded_completion_metadata": {
        "candidate_count": 1,
        "candidate_count_truncated": false,
        "finish_reasons": [
          "MAX_TOKENS"
        ],
        "part_counts": [
          1
        ],
        "provider_text_inspected_for_diagnosis": false,
        "provider_text_retained": false
      },
      "bounded_error": {
        "field_paths": [],
        "reason_code": "provider_text_not_json"
      },
      "http_status": 200,
      "latency_ms": 7908,
      "status": "response_rejected_before_candidate",
      "usage": {
        "candidatesTokenCount": 660,
        "promptTokenCount": 3705,
        "thoughtsTokenCount": 1374,
        "totalTokenCount": 5739
      }
    }
  ],
  "receptionist_output": null,
  "release": null,
  "source_case_id": null,
  "terminal_second_call_reason": "exact_pre_schema_replay",
  "terminal_status": "terminal_no_release",
  "typed_program": null
}
```

## 3. b-create-preface

```json
{
  "actual_provider_calls": 1,
  "admitted_operator_ids": [
    "resolve_patient_reference",
    "resolve_practitioner_reference",
    "resolve_date_expression",
    "search_available_slots",
    "prepare_create_proposal"
  ],
  "case_code": "b-create-preface",
  "cleanup_passed": true,
  "context_frame_review": {
    "command_authority": false,
    "desk_context_sha256": "sha256:9c6f33f842c90f5bd801b413bc353e2fa8956aeb9403eb10f05264c63d362b9f",
    "disposition": "admit",
    "reviewed_context_revision": 62,
    "same_packet_seen_by_model_and_proofreader": true,
    "source_labels": [
      "fixture_intercepted",
      "staff_selected",
      "staff_selected"
    ],
    "task_sha256": "sha256:f9b58d11f1e7ab154e124360ecba7d7a9d2a69fd14a2c97252919552fbb45fd7"
  },
  "correction_used": false,
  "exact_binding": {
    "api_key_authentication_used": false,
    "authentication": "keyless_impersonated_service_account_adc",
    "endpoint_hostname": "australia-southeast1-aiplatform.googleapis.com",
    "location": "australia-southeast1",
    "model_id": "gemini-2.5-flash",
    "project": "bernie-emr4-dev",
    "provider": "google_vertex_ai",
    "service_account": "emr4-bernie-ai-dev@bernie-emr4-dev.iam.gserviceaccount.com"
  },
  "expected_goal": "create",
  "expected_proposal_family": "create",
  "expected_proposal_release": true,
  "expected_safe_outcome": true,
  "final_proofreader_disposition": "admit",
  "final_violation_codes": [],
  "operator_note": {
    "audit_only": true,
    "disposition": "admit",
    "note_sha256": "sha256:8e29ae1d1471b111e6a2c2befc54feb4292764830feb09811635ae6c66bb53d0",
    "operator_note": "Proposal for review; no booking was changed.",
    "parsed_into_plan": false,
    "product_delivered": false,
    "reason_codes": [],
    "retained_utf8_bytes": 44
  },
  "parent_audit_chain": {
    "event_count": 4,
    "terminal_hash": "sha256:38b6b4f05fb97694beab748a6dda6eb672cdd65758909179e090c8e42e19dc91",
    "valid": true
  },
  "primary_exact_body_accepted": true,
  "primary_proofreader_disposition": "admit",
  "primary_violation_codes": [],
  "provider_outcomes": [
    {
      "bounded_completion_metadata": {
        "candidate_count": 1,
        "candidate_count_truncated": false,
        "finish_reasons": [
          "STOP"
        ],
        "part_counts": [
          1
        ],
        "provider_text_inspected_for_diagnosis": false,
        "provider_text_retained": false
      },
      "bounded_error": null,
      "http_status": 200,
      "latency_ms": 4425,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 863,
        "promptTokenCount": 3763,
        "thoughtsTokenCount": 221,
        "totalTokenCount": 4847
      }
    }
  ],
  "receptionist_output": {
    "decision_note": "Intent create: all necessary information for creating an appointment is present.",
    "disposition": "admit",
    "evidence_utterance_indices": [
      1
    ],
    "hidden_reasoning": false,
    "natural_response_parsed_into_form": false,
    "product_delivered": false,
    "raw_provider_response": false,
    "receptionist_response": "I am preparing a proposal to schedule an appointment for Margaret Thompson with Dr Shera tomorrow at 2:30 pm for 15 minutes. This will be reviewed for confirmation; no booking was changed.",
    "violations": []
  },
  "release": {
    "api_spine_operation_id": "proposeAppointmentCreate",
    "appointment_ref": null,
    "candidate_slot_ids": [
      "synthetic-slot-july28-1430"
    ],
    "duration_minutes": 15,
    "kind": "proposal_candidate",
    "patient_ref": "synthetic-patient-margaret",
    "practitioner_ref": "synthetic-practitioner-shera",
    "proposal_family": "create",
    "requires_human_confirmation": true,
    "status": null,
    "warning_codes": [
      "no_reservation",
      "staff_confirmation_required",
      "staff_selection_required"
    ],
    "write_performed": false
  },
  "source_case_id": null,
  "terminal_second_call_reason": null,
  "terminal_status": "admitted",
  "typed_program": {
    "explicit_source_form": {
      "goal_code": 0,
      "steps": [
        {
          "operator_code": 0,
          "source_refs": [
            {
              "binding_code": 5,
              "kind": "binding",
              "prior_output_name": "none",
              "prior_step_index": -1
            }
          ]
        },
        {
          "operator_code": 1,
          "source_refs": [
            {
              "binding_code": 6,
              "kind": "binding",
              "prior_output_name": "none",
              "prior_step_index": -1
            }
          ]
        },
        {
          "operator_code": 2,
          "source_refs": [
            {
              "binding_code": 0,
              "kind": "binding",
              "prior_output_name": "none",
              "prior_step_index": -1
            }
          ]
        },
        {
          "operator_code": 6,
          "source_refs": [
            {
              "binding_code": -1,
              "kind": "prior_output",
              "prior_output_name": "practitioner",
              "prior_step_index": 1
            },
            {
              "binding_code": -1,
              "kind": "prior_output",
              "prior_output_name": "date",
              "prior_step_index": 2
            },
            {
              "binding_code": 3,
              "kind": "binding",
              "prior_output_name": "none",
              "prior_step_index": -1
            },
            {
              "binding_code": 4,
              "kind": "binding",
              "prior_output_name": "none",
              "prior_step_index": -1
            },
            {
              "binding_code": 2,
              "kind": "binding",
              "prior_output_name": "none",
              "prior_step_index": -1
            }
          ]
        },
        {
          "operator_code": 8,
          "source_refs": [
            {
              "binding_code": -1,
              "kind": "prior_output",
              "prior_output_name": "patient",
              "prior_step_index": 0
            },
            {
              "binding_code": -1,
              "kind": "prior_output",
              "prior_output_name": "practitioner",
              "prior_step_index": 1
            },
            {
              "binding_code": -1,
              "kind": "prior_output",
              "prior_output_name": "candidates",
              "prior_step_index": 3
            },
            {
              "binding_code": 2,
              "kind": "binding",
              "prior_output_name": "none",
              "prior_step_index": -1
            }
          ]
        }
      ],
      "version_code": 3
    },
    "operator_note_excluded": true,
    "program_hash": "sha256:b5f9933763ed99c1126d7a4b229e776da2a8cfc6ba613d709b5d8197fa6d815d",
    "raw_provider_response": false
  }
}
```

## 4. b-create-correct

```json
{
  "actual_provider_calls": 1,
  "admitted_operator_ids": [
    "resolve_patient_reference",
    "resolve_practitioner_reference",
    "resolve_date_expression",
    "search_available_slots",
    "prepare_create_proposal"
  ],
  "case_code": "b-create-correct",
  "cleanup_passed": true,
  "context_frame_review": {
    "command_authority": false,
    "desk_context_sha256": "sha256:5847affa8f130839462c3323612fd9c9b4b991e77fc0496f739601c59640ba12",
    "disposition": "admit",
    "reviewed_context_revision": 62,
    "same_packet_seen_by_model_and_proofreader": true,
    "source_labels": [
      "fixture_intercepted",
      "staff_selected",
      "staff_selected"
    ],
    "task_sha256": "sha256:da4dd542ac40d255c1a1db69319cd6ebb4c5e8221a43dd2ff05d27221dca4272"
  },
  "correction_used": false,
  "exact_binding": {
    "api_key_authentication_used": false,
    "authentication": "keyless_impersonated_service_account_adc",
    "endpoint_hostname": "australia-southeast1-aiplatform.googleapis.com",
    "location": "australia-southeast1",
    "model_id": "gemini-2.5-flash",
    "project": "bernie-emr4-dev",
    "provider": "google_vertex_ai",
    "service_account": "emr4-bernie-ai-dev@bernie-emr4-dev.iam.gserviceaccount.com"
  },
  "expected_goal": "create",
  "expected_proposal_family": "create",
  "expected_proposal_release": true,
  "expected_safe_outcome": true,
  "final_proofreader_disposition": "admit",
  "final_violation_codes": [],
  "operator_note": {
    "audit_only": true,
    "disposition": "admit",
    "note_sha256": "sha256:d0bde6f469f2dc67f76be9f46670e7eb4b523d2294cad67b9ff0a57c8c7206df",
    "operator_note": "Proposal for review: no booking was changed.",
    "parsed_into_plan": false,
    "product_delivered": false,
    "reason_codes": [],
    "retained_utf8_bytes": 44
  },
  "parent_audit_chain": {
    "event_count": 4,
    "terminal_hash": "sha256:8831b45e2fea2f68a198fed04971f79b56b1666f906d8a14a3d7faf98e973333",
    "valid": true
  },
  "primary_exact_body_accepted": true,
  "primary_proofreader_disposition": "admit",
  "primary_violation_codes": [],
  "provider_outcomes": [
    {
      "bounded_completion_metadata": {
        "candidate_count": 1,
        "candidate_count_truncated": false,
        "finish_reasons": [
          "STOP"
        ],
        "part_counts": [
          1
        ],
        "provider_text_inspected_for_diagnosis": false,
        "provider_text_retained": false
      },
      "bounded_error": null,
      "http_status": 200,
      "latency_ms": 7766,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 871,
        "promptTokenCount": 3758,
        "thoughtsTokenCount": 1018,
        "totalTokenCount": 5647
      }
    }
  ],
  "receptionist_output": {
    "decision_note": "Intent create: The staff member requested to book an appointment and then corrected the time.",
    "disposition": "admit",
    "evidence_utterance_indices": [
      0,
      1
    ],
    "hidden_reasoning": false,
    "natural_response_parsed_into_form": false,
    "product_delivered": false,
    "raw_provider_response": false,
    "receptionist_response": "I am preparing a proposal to book an appointment for Margaret Thompson with Dr Shera tomorrow at 3:00 PM for 15 minutes. This will be reviewed for confirmation; no booking was changed.",
    "violations": []
  },
  "release": {
    "api_spine_operation_id": "proposeAppointmentCreate",
    "appointment_ref": null,
    "candidate_slot_ids": [
      "synthetic-slot-july28-1500"
    ],
    "duration_minutes": 15,
    "kind": "proposal_candidate",
    "patient_ref": "synthetic-patient-margaret",
    "practitioner_ref": "synthetic-practitioner-shera",
    "proposal_family": "create",
    "requires_human_confirmation": true,
    "status": null,
    "warning_codes": [
      "no_reservation",
      "staff_confirmation_required",
      "staff_selection_required"
    ],
    "write_performed": false
  },
  "source_case_id": null,
  "terminal_second_call_reason": null,
  "terminal_status": "admitted",
  "typed_program": {
    "explicit_source_form": {
      "goal_code": 0,
      "steps": [
        {
          "operator_code": 0,
          "source_refs": [
            {
              "binding_code": 5,
              "kind": "binding",
              "prior_output_name": "none",
              "prior_step_index": -1
            }
          ]
        },
        {
          "operator_code": 1,
          "source_refs": [
            {
              "binding_code": 6,
              "kind": "binding",
              "prior_output_name": "none",
              "prior_step_index": -1
            }
          ]
        },
        {
          "operator_code": 2,
          "source_refs": [
            {
              "binding_code": 0,
              "kind": "binding",
              "prior_output_name": "none",
              "prior_step_index": -1
            }
          ]
        },
        {
          "operator_code": 6,
          "source_refs": [
            {
              "binding_code": -1,
              "kind": "prior_output",
              "prior_output_name": "practitioner",
              "prior_step_index": 1
            },
            {
              "binding_code": -1,
              "kind": "prior_output",
              "prior_output_name": "date",
              "prior_step_index": 2
            },
            {
              "binding_code": 3,
              "kind": "binding",
              "prior_output_name": "none",
              "prior_step_index": -1
            },
            {
              "binding_code": 4,
              "kind": "binding",
              "prior_output_name": "none",
              "prior_step_index": -1
            },
            {
              "binding_code": 2,
              "kind": "binding",
              "prior_output_name": "none",
              "prior_step_index": -1
            }
          ]
        },
        {
          "operator_code": 8,
          "source_refs": [
            {
              "binding_code": -1,
              "kind": "prior_output",
              "prior_output_name": "patient",
              "prior_step_index": 0
            },
            {
              "binding_code": -1,
              "kind": "prior_output",
              "prior_output_name": "practitioner",
              "prior_step_index": 1
            },
            {
              "binding_code": -1,
              "kind": "prior_output",
              "prior_output_name": "candidates",
              "prior_step_index": 3
            },
            {
              "binding_code": 2,
              "kind": "binding",
              "prior_output_name": "none",
              "prior_step_index": -1
            }
          ]
        }
      ],
      "version_code": 3
    },
    "operator_note_excluded": true,
    "program_hash": "sha256:c5e500f4c4aeca5551f1c6331d8be821b6db642dca7d57a49aa708a259d16ad6",
    "raw_provider_response": false
  }
}
```

## 5. b-move-resched

```json
{
  "actual_provider_calls": 1,
  "admitted_operator_ids": [
    "resolve_patient_reference",
    "read_selected_appointment",
    "resolve_date_expression",
    "search_available_slots",
    "prepare_move_proposal"
  ],
  "case_code": "b-move-resched",
  "cleanup_passed": true,
  "context_frame_review": {
    "command_authority": false,
    "desk_context_sha256": "sha256:215cd4983fe8a0b8b499a786557b559de5ceac27b001468f048b3f50e6c394c7",
    "disposition": "admit",
    "reviewed_context_revision": 62,
    "same_packet_seen_by_model_and_proofreader": true,
    "source_labels": [
      "fixture_intercepted",
      "staff_selected",
      "staff_selected"
    ],
    "task_sha256": "sha256:9c0ed10f48e165c61b3f0fe8c236db1c6b4f9ad0b76071aaaced0bd7d7570a8c"
  },
  "correction_used": false,
  "exact_binding": {
    "api_key_authentication_used": false,
    "authentication": "keyless_impersonated_service_account_adc",
    "endpoint_hostname": "australia-southeast1-aiplatform.googleapis.com",
    "location": "australia-southeast1",
    "model_id": "gemini-2.5-flash",
    "project": "bernie-emr4-dev",
    "provider": "google_vertex_ai",
    "service_account": "emr4-bernie-ai-dev@bernie-emr4-dev.iam.gserviceaccount.com"
  },
  "expected_goal": "move",
  "expected_proposal_family": "move",
  "expected_proposal_release": true,
  "expected_safe_outcome": true,
  "final_proofreader_disposition": "admit",
  "final_violation_codes": [],
  "operator_note": {
    "audit_only": true,
    "disposition": "admit",
    "note_sha256": "sha256:d0bde6f469f2dc67f76be9f46670e7eb4b523d2294cad67b9ff0a57c8c7206df",
    "operator_note": "Proposal for review: no booking was changed.",
    "parsed_into_plan": false,
    "product_delivered": false,
    "reason_codes": [],
    "retained_utf8_bytes": 44
  },
  "parent_audit_chain": {
    "event_count": 4,
    "terminal_hash": "sha256:7bbfd7b40544b79a628f173e5f0f85341eded5faa850cbb599e64baae136bc01",
    "valid": true
  },
  "primary_exact_body_accepted": true,
  "primary_proofreader_disposition": "admit",
  "primary_violation_codes": [],
  "provider_outcomes": [
    {
      "bounded_completion_metadata": {
        "candidate_count": 1,
        "candidate_count_truncated": false,
        "finish_reasons": [
          "STOP"
        ],
        "part_counts": [
          1
        ],
        "provider_text_inspected_for_diagnosis": false,
        "provider_text_retained": false
      },
      "bounded_error": null,
      "http_status": 200,
      "latency_ms": 6682,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 807,
        "promptTokenCount": 3610,
        "thoughtsTokenCount": 838,
        "totalTokenCount": 5255
      }
    }
  ],
  "receptionist_output": {
    "decision_note": "Intent move: All necessary information for moving an appointment is present.",
    "disposition": "admit",
    "evidence_utterance_indices": [
      0
    ],
    "hidden_reasoning": false,
    "natural_response_parsed_into_form": false,
    "product_delivered": false,
    "raw_provider_response": false,
    "receptionist_response": "I am preparing a proposal to reschedule Margaret Thompson's appointment for tomorrow at 3 PM. This will be reviewed for confirmation; no booking was changed.",
    "violations": []
  },
  "release": {
    "api_spine_operation_id": "proposeAppointmentUpdate",
    "appointment_ref": "synthetic-appointment-margaret",
    "candidate_slot_ids": [
      "synthetic-slot-july28-1500"
    ],
    "duration_minutes": 15,
    "kind": "proposal_candidate",
    "patient_ref": "synthetic-patient-margaret",
    "practitioner_ref": "synthetic-practitioner-shera",
    "proposal_family": "move",
    "requires_human_confirmation": true,
    "status": null,
    "warning_codes": [
      "no_reservation",
      "staff_confirmation_required",
      "staff_selection_required"
    ],
    "write_performed": false
  },
  "source_case_id": null,
  "terminal_second_call_reason": null,
  "terminal_status": "admitted",
  "typed_program": {
    "explicit_source_form": {
      "goal_code": 1,
      "steps": [
        {
          "operator_code": 0,
          "source_refs": [
            {
              "binding_code": 4,
              "kind": "binding",
              "prior_output_name": "none",
              "prior_step_index": -1
            }
          ]
        },
        {
          "operator_code": 3,
          "source_refs": [
            {
              "binding_code": -1,
              "kind": "prior_output",
              "prior_output_name": "patient",
              "prior_step_index": 0
            },
            {
              "binding_code": 5,
              "kind": "binding",
              "prior_output_name": "none",
              "prior_step_index": -1
            }
          ]
        },
        {
          "operator_code": 2,
          "source_refs": [
            {
              "binding_code": 0,
              "kind": "binding",
              "prior_output_name": "none",
              "prior_step_index": -1
            }
          ]
        },
        {
          "operator_code": 6,
          "source_refs": [
            {
              "binding_code": -1,
              "kind": "prior_output",
              "prior_output_name": "practitioner",
              "prior_step_index": 1
            },
            {
              "binding_code": -1,
              "kind": "prior_output",
              "prior_output_name": "date",
              "prior_step_index": 2
            },
            {
              "binding_code": 2,
              "kind": "binding",
              "prior_output_name": "none",
              "prior_step_index": -1
            },
            {
              "binding_code": 3,
              "kind": "binding",
              "prior_output_name": "none",
              "prior_step_index": -1
            },
            {
              "binding_code": -1,
              "kind": "prior_output",
              "prior_output_name": "duration_minutes",
              "prior_step_index": 1
            }
          ]
        },
        {
          "operator_code": 9,
          "source_refs": [
            {
              "binding_code": -1,
              "kind": "prior_output",
              "prior_output_name": "appointment",
              "prior_step_index": 1
            },
            {
              "binding_code": -1,
              "kind": "prior_output",
              "prior_output_name": "candidates",
              "prior_step_index": 3
            }
          ]
        }
      ],
      "version_code": 3
    },
    "operator_note_excluded": true,
    "program_hash": "sha256:fb9af521a12b39f2923c2a0bee07806e674689a66963abf5ca13387716d34a62",
    "raw_provider_response": false
  }
}
```

## 6. b-move-shift

```json
{
  "actual_provider_calls": 2,
  "admitted_operator_ids": [],
  "case_code": "b-move-shift",
  "cleanup_passed": true,
  "context_frame_review": {
    "command_authority": false,
    "desk_context_sha256": "sha256:cadf3d491c63d466836b4239eb69fe0e49c6391f4138a6ece472befec23854af",
    "disposition": "admit",
    "reviewed_context_revision": 62,
    "same_packet_seen_by_model_and_proofreader": true,
    "source_labels": [
      "fixture_intercepted",
      "staff_selected",
      "staff_selected"
    ],
    "task_sha256": "sha256:6684100cc695663b90b672124f85ccf0a424f7f100f0e110f769f6f54543b6a7"
  },
  "correction_used": true,
  "exact_binding": {
    "api_key_authentication_used": false,
    "authentication": "keyless_impersonated_service_account_adc",
    "endpoint_hostname": "australia-southeast1-aiplatform.googleapis.com",
    "location": "australia-southeast1",
    "model_id": "gemini-2.5-flash",
    "project": "bernie-emr4-dev",
    "provider": "google_vertex_ai",
    "service_account": "emr4-bernie-ai-dev@bernie-emr4-dev.iam.gserviceaccount.com"
  },
  "expected_goal": "move",
  "expected_proposal_family": "move",
  "expected_proposal_release": true,
  "expected_safe_outcome": false,
  "final_proofreader_disposition": "edge_abort",
  "final_violation_codes": [
    "source_type_mismatch"
  ],
  "operator_note": {
    "audit_only": true,
    "disposition": "admit",
    "note_sha256": "sha256:d5f7f9ddae7a66d7394337f714ea470a4d3decdda0f53bfbf22fbe9ad803325e",
    "operator_note": "Proposal for review, no booking was changed.",
    "parsed_into_plan": false,
    "product_delivered": false,
    "reason_codes": [],
    "retained_utf8_bytes": 44
  },
  "parent_audit_chain": {
    "event_count": 6,
    "terminal_hash": "sha256:28758d2cdff6328d3ccd476d74a1dade3aa2369993a2d4ac9498bf960d5e3f58",
    "valid": true
  },
  "primary_exact_body_accepted": true,
  "primary_proofreader_disposition": "revision_required",
  "primary_violation_codes": [
    "required_source_omitted"
  ],
  "provider_outcomes": [
    {
      "bounded_completion_metadata": {
        "candidate_count": 1,
        "candidate_count_truncated": false,
        "finish_reasons": [
          "STOP"
        ],
        "part_counts": [
          1
        ],
        "provider_text_inspected_for_diagnosis": false,
        "provider_text_retained": false
      },
      "bounded_error": null,
      "http_status": 200,
      "latency_ms": 6407,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 660,
        "promptTokenCount": 3613,
        "thoughtsTokenCount": 890,
        "totalTokenCount": 5163
      }
    },
    {
      "bounded_completion_metadata": {
        "candidate_count": 1,
        "candidate_count_truncated": false,
        "finish_reasons": [
          "STOP"
        ],
        "part_counts": [
          1
        ],
        "provider_text_inspected_for_diagnosis": false,
        "provider_text_retained": false
      },
      "bounded_error": null,
      "http_status": 200,
      "latency_ms": 6719,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 651,
        "promptTokenCount": 4053,
        "thoughtsTokenCount": 1011,
        "totalTokenCount": 5715
      }
    }
  ],
  "receptionist_output": {
    "decision_note": null,
    "disposition": "revision_required",
    "evidence_utterance_indices": [],
    "hidden_reasoning": false,
    "natural_response_parsed_into_form": false,
    "product_delivered": false,
    "raw_provider_response": false,
    "receptionist_response": null,
    "violations": [
      {
        "code": "receptionist_response_goal_mismatch",
        "path": "$.receptionist_response"
      }
    ]
  },
  "release": null,
  "source_case_id": null,
  "terminal_second_call_reason": "proofreader_correction",
  "terminal_status": "terminal_no_release",
  "typed_program": {
    "explicit_source_form": {
      "goal_code": 1,
      "steps": [
        {
          "operator_code": 3,
          "source_refs": [
            {
              "binding_code": 4,
              "kind": "binding",
              "prior_output_name": "none",
              "prior_step_index": -1
            },
            {
              "binding_code": 5,
              "kind": "binding",
              "prior_output_name": "none",
              "prior_step_index": -1
            }
          ]
        },
        {
          "operator_code": 6,
          "source_refs": [
            {
              "binding_code": -1,
              "kind": "prior_output",
              "prior_output_name": "practitioner",
              "prior_step_index": 0
            },
            {
              "binding_code": 0,
              "kind": "binding",
              "prior_output_name": "none",
              "prior_step_index": -1
            },
            {
              "binding_code": 2,
              "kind": "binding",
              "prior_output_name": "none",
              "prior_step_index": -1
            },
            {
              "binding_code": 3,
              "kind": "binding",
              "prior_output_name": "none",
              "prior_step_index": -1
            },
            {
              "binding_code": -1,
              "kind": "prior_output",
              "prior_output_name": "duration_minutes",
              "prior_step_index": 0
            }
          ]
        },
        {
          "operator_code": 9,
          "source_refs": [
            {
              "binding_code": -1,
              "kind": "prior_output",
              "prior_output_name": "appointment",
              "prior_step_index": 0
            },
            {
              "binding_code": -1,
              "kind": "prior_output",
              "prior_output_name": "candidates",
              "prior_step_index": 1
            }
          ]
        }
      ],
      "version_code": 3
    },
    "operator_note_excluded": true,
    "program_hash": "sha256:77b09f6e259bab9c06d466073ada6df6b395bff3ae89fda2c8100392dd6926ad",
    "raw_provider_response": false
  }
}
```

## 7. b-move-change

```json
{
  "actual_provider_calls": 2,
  "admitted_operator_ids": [
    "resolve_patient_reference",
    "read_selected_appointment",
    "resolve_date_expression",
    "search_available_slots",
    "prepare_move_proposal"
  ],
  "case_code": "b-move-change",
  "cleanup_passed": true,
  "context_frame_review": {
    "command_authority": false,
    "desk_context_sha256": "sha256:7e915a283451467e85bda0412355fadd429dea2f82853f84164457b3ead49107",
    "disposition": "admit",
    "reviewed_context_revision": 62,
    "same_packet_seen_by_model_and_proofreader": true,
    "source_labels": [
      "fixture_intercepted",
      "staff_selected",
      "staff_selected"
    ],
    "task_sha256": "sha256:6584de21e1aceee72e3285a72830755aac5683d05ae624bce4230078b5dffbbc"
  },
  "correction_used": true,
  "exact_binding": {
    "api_key_authentication_used": false,
    "authentication": "keyless_impersonated_service_account_adc",
    "endpoint_hostname": "australia-southeast1-aiplatform.googleapis.com",
    "location": "australia-southeast1",
    "model_id": "gemini-2.5-flash",
    "project": "bernie-emr4-dev",
    "provider": "google_vertex_ai",
    "service_account": "emr4-bernie-ai-dev@bernie-emr4-dev.iam.gserviceaccount.com"
  },
  "expected_goal": "move",
  "expected_proposal_family": "move",
  "expected_proposal_release": true,
  "expected_safe_outcome": true,
  "final_proofreader_disposition": "admit",
  "final_violation_codes": [],
  "operator_note": {
    "audit_only": true,
    "disposition": "admit",
    "note_sha256": "sha256:d0bde6f469f2dc67f76be9f46670e7eb4b523d2294cad67b9ff0a57c8c7206df",
    "operator_note": "Proposal for review: no booking was changed.",
    "parsed_into_plan": false,
    "product_delivered": false,
    "reason_codes": [],
    "retained_utf8_bytes": 44
  },
  "parent_audit_chain": {
    "event_count": 6,
    "terminal_hash": "sha256:3440ea2cfd361fbe2ec7c14bb335a6f2690ca7e5f0871c47d66f9837ad48978a",
    "valid": true
  },
  "primary_exact_body_accepted": true,
  "primary_proofreader_disposition": "revision_required",
  "primary_violation_codes": [
    "receptionist_response_goal_mismatch"
  ],
  "provider_outcomes": [
    {
      "bounded_completion_metadata": {
        "candidate_count": 1,
        "candidate_count_truncated": false,
        "finish_reasons": [
          "STOP"
        ],
        "part_counts": [
          1
        ],
        "provider_text_inspected_for_diagnosis": false,
        "provider_text_retained": false
      },
      "bounded_error": null,
      "http_status": 200,
      "latency_ms": 5947,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 804,
        "promptTokenCount": 3610,
        "thoughtsTokenCount": 749,
        "totalTokenCount": 5163
      }
    },
    {
      "bounded_completion_metadata": {
        "candidate_count": 1,
        "candidate_count_truncated": false,
        "finish_reasons": [
          "STOP"
        ],
        "part_counts": [
          1
        ],
        "provider_text_inspected_for_diagnosis": false,
        "provider_text_retained": false
      },
      "bounded_error": null,
      "http_status": 200,
      "latency_ms": 6885,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 806,
        "promptTokenCount": 4140,
        "thoughtsTokenCount": 1011,
        "totalTokenCount": 5957
      }
    }
  ],
  "receptionist_output": {
    "decision_note": "Intent move: The user explicitly requested to change the time of an existing appointment.",
    "disposition": "admit",
    "evidence_utterance_indices": [
      0
    ],
    "hidden_reasoning": false,
    "natural_response_parsed_into_form": false,
    "product_delivered": false,
    "raw_provider_response": false,
    "receptionist_response": "I am preparing a proposal to move Margaret Thompson's appointment to tomorrow at 3 pm for your review. No booking was changed.",
    "violations": []
  },
  "release": {
    "api_spine_operation_id": "proposeAppointmentUpdate",
    "appointment_ref": "synthetic-appointment-margaret",
    "candidate_slot_ids": [
      "synthetic-slot-july28-1500"
    ],
    "duration_minutes": 15,
    "kind": "proposal_candidate",
    "patient_ref": "synthetic-patient-margaret",
    "practitioner_ref": "synthetic-practitioner-shera",
    "proposal_family": "move",
    "requires_human_confirmation": true,
    "status": null,
    "warning_codes": [
      "no_reservation",
      "staff_confirmation_required",
      "staff_selection_required"
    ],
    "write_performed": false
  },
  "source_case_id": null,
  "terminal_second_call_reason": "proofreader_correction",
  "terminal_status": "admitted_after_correction",
  "typed_program": {
    "explicit_source_form": {
      "goal_code": 1,
      "steps": [
        {
          "operator_code": 0,
          "source_refs": [
            {
              "binding_code": 4,
              "kind": "binding",
              "prior_output_name": "none",
              "prior_step_index": -1
            }
          ]
        },
        {
          "operator_code": 3,
          "source_refs": [
            {
              "binding_code": -1,
              "kind": "prior_output",
              "prior_output_name": "patient",
              "prior_step_index": 0
            },
            {
              "binding_code": 5,
              "kind": "binding",
              "prior_output_name": "none",
              "prior_step_index": -1
            }
          ]
        },
        {
          "operator_code": 2,
          "source_refs": [
            {
              "binding_code": 0,
              "kind": "binding",
              "prior_output_name": "none",
              "prior_step_index": -1
            }
          ]
        },
        {
          "operator_code": 6,
          "source_refs": [
            {
              "binding_code": -1,
              "kind": "prior_output",
              "prior_output_name": "practitioner",
              "prior_step_index": 1
            },
            {
              "binding_code": -1,
              "kind": "prior_output",
              "prior_output_name": "date",
              "prior_step_index": 2
            },
            {
              "binding_code": 2,
              "kind": "binding",
              "prior_output_name": "none",
              "prior_step_index": -1
            },
            {
              "binding_code": 3,
              "kind": "binding",
              "prior_output_name": "none",
              "prior_step_index": -1
            },
            {
              "binding_code": -1,
              "kind": "prior_output",
              "prior_output_name": "duration_minutes",
              "prior_step_index": 1
            }
          ]
        },
        {
          "operator_code": 9,
          "source_refs": [
            {
              "binding_code": -1,
              "kind": "prior_output",
              "prior_output_name": "appointment",
              "prior_step_index": 1
            },
            {
              "binding_code": -1,
              "kind": "prior_output",
              "prior_output_name": "candidates",
              "prior_step_index": 3
            }
          ]
        }
      ],
      "version_code": 3
    },
    "operator_note_excluded": true,
    "program_hash": "sha256:fb9af521a12b39f2923c2a0bee07806e674689a66963abf5ca13387716d34a62",
    "raw_provider_response": false
  }
}
```

## 8. b-move-correct

```json
{
  "actual_provider_calls": 1,
  "admitted_operator_ids": [
    "resolve_patient_reference",
    "read_selected_appointment",
    "resolve_date_expression",
    "search_available_slots",
    "prepare_move_proposal"
  ],
  "case_code": "b-move-correct",
  "cleanup_passed": true,
  "context_frame_review": {
    "command_authority": false,
    "desk_context_sha256": "sha256:f8f9034a29b32f0f971a0895ff0bc88780e9ff283d235b1e5050a66f5a780744",
    "disposition": "admit",
    "reviewed_context_revision": 62,
    "same_packet_seen_by_model_and_proofreader": true,
    "source_labels": [
      "fixture_intercepted",
      "staff_selected",
      "staff_selected"
    ],
    "task_sha256": "sha256:137d6b6136bed20b99cacd07dfb12340f3a47f83e6d924c0a250f37f437b29cb"
  },
  "correction_used": false,
  "exact_binding": {
    "api_key_authentication_used": false,
    "authentication": "keyless_impersonated_service_account_adc",
    "endpoint_hostname": "australia-southeast1-aiplatform.googleapis.com",
    "location": "australia-southeast1",
    "model_id": "gemini-2.5-flash",
    "project": "bernie-emr4-dev",
    "provider": "google_vertex_ai",
    "service_account": "emr4-bernie-ai-dev@bernie-emr4-dev.iam.gserviceaccount.com"
  },
  "expected_goal": "move",
  "expected_proposal_family": "move",
  "expected_proposal_release": true,
  "expected_safe_outcome": true,
  "final_proofreader_disposition": "admit",
  "final_violation_codes": [],
  "operator_note": {
    "audit_only": true,
    "disposition": "admit",
    "note_sha256": "sha256:d5f7f9ddae7a66d7394337f714ea470a4d3decdda0f53bfbf22fbe9ad803325e",
    "operator_note": "Proposal for review, no booking was changed.",
    "parsed_into_plan": false,
    "product_delivered": false,
    "reason_codes": [],
    "retained_utf8_bytes": 44
  },
  "parent_audit_chain": {
    "event_count": 4,
    "terminal_hash": "sha256:ffa038b36cf17b9962b9059b2024c98e4fed7f4016792552d34e517edf6c111a",
    "valid": true
  },
  "primary_exact_body_accepted": true,
  "primary_proofreader_disposition": "admit",
  "primary_violation_codes": [],
  "provider_outcomes": [
    {
      "bounded_completion_metadata": {
        "candidate_count": 1,
        "candidate_count_truncated": false,
        "finish_reasons": [
          "STOP"
        ],
        "part_counts": [
          1
        ],
        "provider_text_inspected_for_diagnosis": false,
        "provider_text_retained": false
      },
      "bounded_error": null,
      "http_status": 200,
      "latency_ms": 7059,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 814,
        "promptTokenCount": 3655,
        "thoughtsTokenCount": 999,
        "totalTokenCount": 5468
      }
    }
  ],
  "receptionist_output": {
    "decision_note": "Intent move: The latest utterance specifies a new time for the appointment.",
    "disposition": "admit",
    "evidence_utterance_indices": [
      0,
      1
    ],
    "hidden_reasoning": false,
    "natural_response_parsed_into_form": false,
    "product_delivered": false,
    "raw_provider_response": false,
    "receptionist_response": "I'm preparing a proposal to move Margaret Thompson's appointment to tomorrow at 3 PM. This will be sent for review, and no booking was changed.",
    "violations": []
  },
  "release": {
    "api_spine_operation_id": "proposeAppointmentUpdate",
    "appointment_ref": "synthetic-appointment-margaret",
    "candidate_slot_ids": [
      "synthetic-slot-july28-1500"
    ],
    "duration_minutes": 15,
    "kind": "proposal_candidate",
    "patient_ref": "synthetic-patient-margaret",
    "practitioner_ref": "synthetic-practitioner-shera",
    "proposal_family": "move",
    "requires_human_confirmation": true,
    "status": null,
    "warning_codes": [
      "no_reservation",
      "staff_confirmation_required",
      "staff_selection_required"
    ],
    "write_performed": false
  },
  "source_case_id": null,
  "terminal_second_call_reason": null,
  "terminal_status": "admitted",
  "typed_program": {
    "explicit_source_form": {
      "goal_code": 1,
      "steps": [
        {
          "operator_code": 0,
          "source_refs": [
            {
              "binding_code": 4,
              "kind": "binding",
              "prior_output_name": "none",
              "prior_step_index": -1
            }
          ]
        },
        {
          "operator_code": 3,
          "source_refs": [
            {
              "binding_code": -1,
              "kind": "prior_output",
              "prior_output_name": "patient",
              "prior_step_index": 0
            },
            {
              "binding_code": 5,
              "kind": "binding",
              "prior_output_name": "none",
              "prior_step_index": -1
            }
          ]
        },
        {
          "operator_code": 2,
          "source_refs": [
            {
              "binding_code": 0,
              "kind": "binding",
              "prior_output_name": "none",
              "prior_step_index": -1
            }
          ]
        },
        {
          "operator_code": 6,
          "source_refs": [
            {
              "binding_code": -1,
              "kind": "prior_output",
              "prior_output_name": "practitioner",
              "prior_step_index": 1
            },
            {
              "binding_code": -1,
              "kind": "prior_output",
              "prior_output_name": "date",
              "prior_step_index": 2
            },
            {
              "binding_code": 2,
              "kind": "binding",
              "prior_output_name": "none",
              "prior_step_index": -1
            },
            {
              "binding_code": 3,
              "kind": "binding",
              "prior_output_name": "none",
              "prior_step_index": -1
            },
            {
              "binding_code": -1,
              "kind": "prior_output",
              "prior_output_name": "duration_minutes",
              "prior_step_index": 1
            }
          ]
        },
        {
          "operator_code": 9,
          "source_refs": [
            {
              "binding_code": -1,
              "kind": "prior_output",
              "prior_output_name": "appointment",
              "prior_step_index": 1
            },
            {
              "binding_code": -1,
              "kind": "prior_output",
              "prior_output_name": "candidates",
              "prior_step_index": 3
            }
          ]
        }
      ],
      "version_code": 3
    },
    "operator_note_excluded": true,
    "program_hash": "sha256:05df0eb36f45dd19b6e56df746ae67056a491cb18e9b70a729472930b769aa4e",
    "raw_provider_response": false
  }
}
```

## 9. b-resize-long

```json
{
  "actual_provider_calls": 1,
  "admitted_operator_ids": [
    "prepare_resize_proposal"
  ],
  "case_code": "b-resize-long",
  "cleanup_passed": true,
  "context_frame_review": {
    "command_authority": false,
    "desk_context_sha256": "sha256:3428760c18f41cf37e2709c6be14543d639ec365855c6a10040e7f52f2f11f9b",
    "disposition": "admit",
    "reviewed_context_revision": 62,
    "same_packet_seen_by_model_and_proofreader": true,
    "source_labels": [
      "fixture_intercepted",
      "staff_selected",
      "staff_selected"
    ],
    "task_sha256": "sha256:07bc591a61766f74bc1d10c038dd67404aa7ddd813d5745a5938b59ed73f7e3b"
  },
  "correction_used": false,
  "exact_binding": {
    "api_key_authentication_used": false,
    "authentication": "keyless_impersonated_service_account_adc",
    "endpoint_hostname": "australia-southeast1-aiplatform.googleapis.com",
    "location": "australia-southeast1",
    "model_id": "gemini-2.5-flash",
    "project": "bernie-emr4-dev",
    "provider": "google_vertex_ai",
    "service_account": "emr4-bernie-ai-dev@bernie-emr4-dev.iam.gserviceaccount.com"
  },
  "expected_goal": "resize",
  "expected_proposal_family": "resize",
  "expected_proposal_release": true,
  "expected_safe_outcome": true,
  "final_proofreader_disposition": "admit",
  "final_violation_codes": [],
  "operator_note": {
    "audit_only": true,
    "disposition": "admit",
    "note_sha256": "sha256:d0bde6f469f2dc67f76be9f46670e7eb4b523d2294cad67b9ff0a57c8c7206df",
    "operator_note": "Proposal for review: no booking was changed.",
    "parsed_into_plan": false,
    "product_delivered": false,
    "reason_codes": [],
    "retained_utf8_bytes": 44
  },
  "parent_audit_chain": {
    "event_count": 4,
    "terminal_hash": "sha256:917134f164ac20eaa1ed4f18be5622254cca36ff4ccba0f4bda56d9ed269d99c",
    "valid": true
  },
  "primary_exact_body_accepted": true,
  "primary_proofreader_disposition": "admit",
  "primary_violation_codes": [],
  "provider_outcomes": [
    {
      "bounded_completion_metadata": {
        "candidate_count": 1,
        "candidate_count_truncated": false,
        "finish_reasons": [
          "STOP"
        ],
        "part_counts": [
          1
        ],
        "provider_text_inspected_for_diagnosis": false,
        "provider_text_retained": false
      },
      "bounded_error": null,
      "http_status": 200,
      "latency_ms": 2645,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 252,
        "promptTokenCount": 3571,
        "thoughtsTokenCount": 281,
        "totalTokenCount": 4104
      }
    }
  ],
  "receptionist_output": {
    "decision_note": "Intent resize: decisive language 'longer' and '30 minutes'.",
    "disposition": "admit",
    "evidence_utterance_indices": [
      0
    ],
    "hidden_reasoning": false,
    "natural_response_parsed_into_form": false,
    "product_delivered": false,
    "raw_provider_response": false,
    "receptionist_response": "I'm preparing a proposal to make Margaret Thompson's appointment longer by 30 minutes for your review. No booking was changed.",
    "violations": []
  },
  "release": {
    "api_spine_operation_id": "proposeAppointmentUpdate",
    "appointment_ref": "synthetic-appointment-margaret",
    "candidate_slot_ids": [],
    "duration_minutes": 30,
    "kind": "proposal_candidate",
    "patient_ref": "synthetic-patient-margaret",
    "practitioner_ref": "synthetic-practitioner-shera",
    "proposal_family": "resize",
    "requires_human_confirmation": true,
    "status": null,
    "warning_codes": [
      "staff_confirmation_required"
    ],
    "write_performed": false
  },
  "source_case_id": null,
  "terminal_second_call_reason": null,
  "terminal_status": "admitted",
  "typed_program": {
    "explicit_source_form": {
      "goal_code": 2,
      "steps": [
        {
          "operator_code": 10,
          "source_refs": [
            {
              "binding_code": 3,
              "kind": "binding",
              "prior_output_name": "none",
              "prior_step_index": -1
            },
            {
              "binding_code": 1,
              "kind": "binding",
              "prior_output_name": "none",
              "prior_step_index": -1
            }
          ]
        }
      ],
      "version_code": 3
    },
    "operator_note_excluded": true,
    "program_hash": "sha256:7b4ef6fd19d1304151dc044b1566b699b580264bda4de69b9c243334ea9e3cd0",
    "raw_provider_response": false
  }
}
```

## 10. b-resize-short

```json
{
  "actual_provider_calls": 1,
  "admitted_operator_ids": [
    "prepare_resize_proposal"
  ],
  "case_code": "b-resize-short",
  "cleanup_passed": true,
  "context_frame_review": {
    "command_authority": false,
    "desk_context_sha256": "sha256:3587c1bd1febae145cc432312ca6c8ac52c98ece54e37f5c9711767a7be80429",
    "disposition": "admit",
    "reviewed_context_revision": 62,
    "same_packet_seen_by_model_and_proofreader": true,
    "source_labels": [
      "fixture_intercepted",
      "staff_selected",
      "staff_selected"
    ],
    "task_sha256": "sha256:69ec57aed25cbca52511f67029c76553f9c9e37932a38cc210a6131ebbedbb34"
  },
  "correction_used": false,
  "exact_binding": {
    "api_key_authentication_used": false,
    "authentication": "keyless_impersonated_service_account_adc",
    "endpoint_hostname": "australia-southeast1-aiplatform.googleapis.com",
    "location": "australia-southeast1",
    "model_id": "gemini-2.5-flash",
    "project": "bernie-emr4-dev",
    "provider": "google_vertex_ai",
    "service_account": "emr4-bernie-ai-dev@bernie-emr4-dev.iam.gserviceaccount.com"
  },
  "expected_goal": "resize",
  "expected_proposal_family": "resize",
  "expected_proposal_release": true,
  "expected_safe_outcome": true,
  "final_proofreader_disposition": "admit",
  "final_violation_codes": [],
  "operator_note": {
    "audit_only": true,
    "disposition": "admit",
    "note_sha256": "sha256:8e29ae1d1471b111e6a2c2befc54feb4292764830feb09811635ae6c66bb53d0",
    "operator_note": "Proposal for review; no booking was changed.",
    "parsed_into_plan": false,
    "product_delivered": false,
    "reason_codes": [],
    "retained_utf8_bytes": 44
  },
  "parent_audit_chain": {
    "event_count": 4,
    "terminal_hash": "sha256:9cbe17645ff9fd8a29b38e255c6bc784cae2abff996f3bb340535c0e83931759",
    "valid": true
  },
  "primary_exact_body_accepted": true,
  "primary_proofreader_disposition": "admit",
  "primary_violation_codes": [],
  "provider_outcomes": [
    {
      "bounded_completion_metadata": {
        "candidate_count": 1,
        "candidate_count_truncated": false,
        "finish_reasons": [
          "STOP"
        ],
        "part_counts": [
          1
        ],
        "provider_text_inspected_for_diagnosis": false,
        "provider_text_retained": false
      },
      "bounded_error": null,
      "http_status": 200,
      "latency_ms": 3369,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 239,
        "promptTokenCount": 3559,
        "thoughtsTokenCount": 465,
        "totalTokenCount": 4263
      }
    }
  ],
  "receptionist_output": {
    "decision_note": "Intent resize: all necessary information is present.",
    "disposition": "admit",
    "evidence_utterance_indices": [
      0
    ],
    "hidden_reasoning": false,
    "natural_response_parsed_into_form": false,
    "product_delivered": false,
    "raw_provider_response": false,
    "receptionist_response": "I'm preparing a proposal to shorten Margaret's appointment to 10 minutes for your review.",
    "violations": []
  },
  "release": {
    "api_spine_operation_id": "proposeAppointmentUpdate",
    "appointment_ref": "synthetic-appointment-margaret",
    "candidate_slot_ids": [],
    "duration_minutes": 10,
    "kind": "proposal_candidate",
    "patient_ref": "synthetic-patient-margaret",
    "practitioner_ref": "synthetic-practitioner-shera",
    "proposal_family": "resize",
    "requires_human_confirmation": true,
    "status": null,
    "warning_codes": [
      "staff_confirmation_required"
    ],
    "write_performed": false
  },
  "source_case_id": null,
  "terminal_second_call_reason": null,
  "terminal_status": "admitted",
  "typed_program": {
    "explicit_source_form": {
      "goal_code": 2,
      "steps": [
        {
          "operator_code": 10,
          "source_refs": [
            {
              "binding_code": 3,
              "kind": "binding",
              "prior_output_name": "none",
              "prior_step_index": -1
            },
            {
              "binding_code": 1,
              "kind": "binding",
              "prior_output_name": "none",
              "prior_step_index": -1
            }
          ]
        }
      ],
      "version_code": 3
    },
    "operator_note_excluded": true,
    "program_hash": "sha256:b06fa07429e6f0d45762e135076b99b632f5422a58da4b84ee4b10c1baebfd2c",
    "raw_provider_response": false
  }
}
```

## 11. b-resize-give

```json
{
  "actual_provider_calls": 1,
  "admitted_operator_ids": [
    "prepare_resize_proposal"
  ],
  "case_code": "b-resize-give",
  "cleanup_passed": true,
  "context_frame_review": {
    "command_authority": false,
    "desk_context_sha256": "sha256:2283c3eacc5d09cecbba2860c406b29af21e46db2c5212ae00cbd4ba22d88834",
    "disposition": "admit",
    "reviewed_context_revision": 62,
    "same_packet_seen_by_model_and_proofreader": true,
    "source_labels": [
      "fixture_intercepted",
      "staff_selected",
      "staff_selected"
    ],
    "task_sha256": "sha256:afa1de959424c1db55553e0c1dbd01d52c19af9ad7b0777882660fc62875fb7a"
  },
  "correction_used": false,
  "exact_binding": {
    "api_key_authentication_used": false,
    "authentication": "keyless_impersonated_service_account_adc",
    "endpoint_hostname": "australia-southeast1-aiplatform.googleapis.com",
    "location": "australia-southeast1",
    "model_id": "gemini-2.5-flash",
    "project": "bernie-emr4-dev",
    "provider": "google_vertex_ai",
    "service_account": "emr4-bernie-ai-dev@bernie-emr4-dev.iam.gserviceaccount.com"
  },
  "expected_goal": "resize",
  "expected_proposal_family": "resize",
  "expected_proposal_release": true,
  "expected_safe_outcome": true,
  "final_proofreader_disposition": "admit",
  "final_violation_codes": [],
  "operator_note": {
    "audit_only": true,
    "disposition": "admit",
    "note_sha256": "sha256:8e29ae1d1471b111e6a2c2befc54feb4292764830feb09811635ae6c66bb53d0",
    "operator_note": "Proposal for review; no booking was changed.",
    "parsed_into_plan": false,
    "product_delivered": false,
    "reason_codes": [],
    "retained_utf8_bytes": 44
  },
  "parent_audit_chain": {
    "event_count": 4,
    "terminal_hash": "sha256:f2ebcbe58c33aa7afdb2dbde9b1e54d192ae19951f40c04eacb50159187c8d3e",
    "valid": true
  },
  "primary_exact_body_accepted": true,
  "primary_proofreader_disposition": "admit",
  "primary_violation_codes": [],
  "provider_outcomes": [
    {
      "bounded_completion_metadata": {
        "candidate_count": 1,
        "candidate_count_truncated": false,
        "finish_reasons": [
          "STOP"
        ],
        "part_counts": [
          1
        ],
        "provider_text_inspected_for_diagnosis": false,
        "provider_text_retained": false
      },
      "bounded_error": null,
      "http_status": 200,
      "latency_ms": 2921,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 250,
        "promptTokenCount": 3561,
        "thoughtsTokenCount": 340,
        "totalTokenCount": 4151
      }
    }
  ],
  "receptionist_output": {
    "decision_note": "Intent resize: The utterance specifies a new duration for an existing appointment.",
    "disposition": "admit",
    "evidence_utterance_indices": [
      0
    ],
    "hidden_reasoning": false,
    "natural_response_parsed_into_form": false,
    "product_delivered": false,
    "raw_provider_response": false,
    "receptionist_response": "I'm preparing a proposal to change Margaret Thompson's appointment to 30 minutes. This will be sent for your review.",
    "violations": []
  },
  "release": {
    "api_spine_operation_id": "proposeAppointmentUpdate",
    "appointment_ref": "synthetic-appointment-margaret",
    "candidate_slot_ids": [],
    "duration_minutes": 30,
    "kind": "proposal_candidate",
    "patient_ref": "synthetic-patient-margaret",
    "practitioner_ref": "synthetic-practitioner-shera",
    "proposal_family": "resize",
    "requires_human_confirmation": true,
    "status": null,
    "warning_codes": [
      "staff_confirmation_required"
    ],
    "write_performed": false
  },
  "source_case_id": null,
  "terminal_second_call_reason": null,
  "terminal_status": "admitted",
  "typed_program": {
    "explicit_source_form": {
      "goal_code": 2,
      "steps": [
        {
          "operator_code": 10,
          "source_refs": [
            {
              "binding_code": 3,
              "kind": "binding",
              "prior_output_name": "none",
              "prior_step_index": -1
            },
            {
              "binding_code": 1,
              "kind": "binding",
              "prior_output_name": "none",
              "prior_step_index": -1
            }
          ]
        }
      ],
      "version_code": 3
    },
    "operator_note_excluded": true,
    "program_hash": "sha256:b06fa07429e6f0d45762e135076b99b632f5422a58da4b84ee4b10c1baebfd2c",
    "raw_provider_response": false
  }
}
```

## 12. b-resize-explicit

```json
{
  "actual_provider_calls": 1,
  "admitted_operator_ids": [
    "prepare_resize_proposal"
  ],
  "case_code": "b-resize-explicit",
  "cleanup_passed": true,
  "context_frame_review": {
    "command_authority": false,
    "desk_context_sha256": "sha256:cf9962c9a248df70e25a36a7419e7be8f043c5668dc51b7d6a38b2c44dace1a6",
    "disposition": "admit",
    "reviewed_context_revision": 62,
    "same_packet_seen_by_model_and_proofreader": true,
    "source_labels": [
      "fixture_intercepted",
      "staff_selected",
      "staff_selected"
    ],
    "task_sha256": "sha256:b6b6df41d38faa376ac0048687f9915fcf69b5f26842544db1b3fe62f2b4e4e2"
  },
  "correction_used": false,
  "exact_binding": {
    "api_key_authentication_used": false,
    "authentication": "keyless_impersonated_service_account_adc",
    "endpoint_hostname": "australia-southeast1-aiplatform.googleapis.com",
    "location": "australia-southeast1",
    "model_id": "gemini-2.5-flash",
    "project": "bernie-emr4-dev",
    "provider": "google_vertex_ai",
    "service_account": "emr4-bernie-ai-dev@bernie-emr4-dev.iam.gserviceaccount.com"
  },
  "expected_goal": "resize",
  "expected_proposal_family": "resize",
  "expected_proposal_release": true,
  "expected_safe_outcome": true,
  "final_proofreader_disposition": "admit",
  "final_violation_codes": [],
  "operator_note": {
    "audit_only": true,
    "disposition": "admit",
    "note_sha256": "sha256:d5f7f9ddae7a66d7394337f714ea470a4d3decdda0f53bfbf22fbe9ad803325e",
    "operator_note": "Proposal for review, no booking was changed.",
    "parsed_into_plan": false,
    "product_delivered": false,
    "reason_codes": [],
    "retained_utf8_bytes": 44
  },
  "parent_audit_chain": {
    "event_count": 4,
    "terminal_hash": "sha256:d45afa085e33c696c738484356137f689a88bbd161e4a70711a4ed59714e91d4",
    "valid": true
  },
  "primary_exact_body_accepted": true,
  "primary_proofreader_disposition": "admit",
  "primary_violation_codes": [],
  "provider_outcomes": [
    {
      "bounded_completion_metadata": {
        "candidate_count": 1,
        "candidate_count_truncated": false,
        "finish_reasons": [
          "STOP"
        ],
        "part_counts": [
          1
        ],
        "provider_text_inspected_for_diagnosis": false,
        "provider_text_retained": false
      },
      "bounded_error": null,
      "http_status": 200,
      "latency_ms": 3158,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 247,
        "promptTokenCount": 3566,
        "thoughtsTokenCount": 392,
        "totalTokenCount": 4205
      }
    }
  ],
  "receptionist_output": {
    "decision_note": "Intent resize: decisive language and all required bindings present.",
    "disposition": "admit",
    "evidence_utterance_indices": [
      0
    ],
    "hidden_reasoning": false,
    "natural_response_parsed_into_form": false,
    "product_delivered": false,
    "raw_provider_response": false,
    "receptionist_response": "I'm preparing a proposal to resize Margaret Thompson's appointment to 30 minutes for your review. No booking was changed.",
    "violations": []
  },
  "release": {
    "api_spine_operation_id": "proposeAppointmentUpdate",
    "appointment_ref": "synthetic-appointment-margaret",
    "candidate_slot_ids": [],
    "duration_minutes": 30,
    "kind": "proposal_candidate",
    "patient_ref": "synthetic-patient-margaret",
    "practitioner_ref": "synthetic-practitioner-shera",
    "proposal_family": "resize",
    "requires_human_confirmation": true,
    "status": null,
    "warning_codes": [
      "staff_confirmation_required"
    ],
    "write_performed": false
  },
  "source_case_id": null,
  "terminal_second_call_reason": null,
  "terminal_status": "admitted",
  "typed_program": {
    "explicit_source_form": {
      "goal_code": 2,
      "steps": [
        {
          "operator_code": 10,
          "source_refs": [
            {
              "binding_code": 3,
              "kind": "binding",
              "prior_output_name": "none",
              "prior_step_index": -1
            },
            {
              "binding_code": 1,
              "kind": "binding",
              "prior_output_name": "none",
              "prior_step_index": -1
            }
          ]
        }
      ],
      "version_code": 3
    },
    "operator_note_excluded": true,
    "program_hash": "sha256:32ac22683ca6e2b658d83e4036415e8a0da777f8da8f28a93267a1990db4f52f",
    "raw_provider_response": false
  }
}
```

## 13. b-cancel-remove

```json
{
  "actual_provider_calls": 1,
  "admitted_operator_ids": [
    "prepare_cancel_proposal"
  ],
  "case_code": "b-cancel-remove",
  "cleanup_passed": true,
  "context_frame_review": {
    "command_authority": false,
    "desk_context_sha256": "sha256:ce99f0f2bb57765960f9467bc1b462454622c3cecf2a3c89bb8a838d03156a88",
    "disposition": "admit",
    "reviewed_context_revision": 62,
    "same_packet_seen_by_model_and_proofreader": true,
    "source_labels": [
      "fixture_intercepted",
      "staff_selected",
      "staff_selected"
    ],
    "task_sha256": "sha256:275aa281d7d53a1cf7711c7abe8845293b89c01ab5a2f203f1ff8e37087fa0d4"
  },
  "correction_used": false,
  "exact_binding": {
    "api_key_authentication_used": false,
    "authentication": "keyless_impersonated_service_account_adc",
    "endpoint_hostname": "australia-southeast1-aiplatform.googleapis.com",
    "location": "australia-southeast1",
    "model_id": "gemini-2.5-flash",
    "project": "bernie-emr4-dev",
    "provider": "google_vertex_ai",
    "service_account": "emr4-bernie-ai-dev@bernie-emr4-dev.iam.gserviceaccount.com"
  },
  "expected_goal": "cancel",
  "expected_proposal_family": "cancel",
  "expected_proposal_release": true,
  "expected_safe_outcome": true,
  "final_proofreader_disposition": "admit",
  "final_violation_codes": [],
  "operator_note": {
    "audit_only": true,
    "disposition": "admit",
    "note_sha256": "sha256:d5f7f9ddae7a66d7394337f714ea470a4d3decdda0f53bfbf22fbe9ad803325e",
    "operator_note": "Proposal for review, no booking was changed.",
    "parsed_into_plan": false,
    "product_delivered": false,
    "reason_codes": [],
    "retained_utf8_bytes": 44
  },
  "parent_audit_chain": {
    "event_count": 4,
    "terminal_hash": "sha256:bdd87b2a35c8c776e5e272c558fff4e5ce352c6ff20d6a4070442df7112999d0",
    "valid": true
  },
  "primary_exact_body_accepted": true,
  "primary_proofreader_disposition": "admit",
  "primary_violation_codes": [],
  "provider_outcomes": [
    {
      "bounded_completion_metadata": {
        "candidate_count": 1,
        "candidate_count_truncated": false,
        "finish_reasons": [
          "STOP"
        ],
        "part_counts": [
          1
        ],
        "provider_text_inspected_for_diagnosis": false,
        "provider_text_retained": false
      },
      "bounded_error": null,
      "http_status": 200,
      "latency_ms": 2421,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 197,
        "promptTokenCount": 3542,
        "thoughtsTokenCount": 202,
        "totalTokenCount": 3941
      }
    }
  ],
  "receptionist_output": {
    "decision_note": "Intent cancel: decisive language 'Remove' and grounded appointment.",
    "disposition": "admit",
    "evidence_utterance_indices": [
      0
    ],
    "hidden_reasoning": false,
    "natural_response_parsed_into_form": false,
    "product_delivered": false,
    "raw_provider_response": false,
    "receptionist_response": "I am preparing a proposal to remove Margaret Thompson's appointment from the diary for your review. No booking was changed.",
    "violations": []
  },
  "release": {
    "api_spine_operation_id": "proposeAppointmentDelete",
    "appointment_ref": "synthetic-appointment-margaret",
    "candidate_slot_ids": [],
    "duration_minutes": 15,
    "kind": "proposal_candidate",
    "patient_ref": "synthetic-patient-margaret",
    "practitioner_ref": "synthetic-practitioner-shera",
    "proposal_family": "cancel",
    "requires_human_confirmation": true,
    "status": null,
    "warning_codes": [
      "staff_confirmation_required"
    ],
    "write_performed": false
  },
  "source_case_id": null,
  "terminal_second_call_reason": null,
  "terminal_status": "admitted",
  "typed_program": {
    "explicit_source_form": {
      "goal_code": 3,
      "steps": [
        {
          "operator_code": 11,
          "source_refs": [
            {
              "binding_code": 2,
              "kind": "binding",
              "prior_output_name": "none",
              "prior_step_index": -1
            }
          ]
        }
      ],
      "version_code": 3
    },
    "operator_note_excluded": true,
    "program_hash": "sha256:4f9d634b998a87c4108c4cced1d53b11298d55dccc7f3818aa3c9b7918702848",
    "raw_provider_response": false
  }
}
```

## 14. b-cancel-calloff

```json
{
  "actual_provider_calls": 1,
  "admitted_operator_ids": [
    "prepare_cancel_proposal"
  ],
  "case_code": "b-cancel-calloff",
  "cleanup_passed": true,
  "context_frame_review": {
    "command_authority": false,
    "desk_context_sha256": "sha256:b09695090c344af5b7ade94df8e378287d8c4a6762f194c76b232da7ee9f88b7",
    "disposition": "admit",
    "reviewed_context_revision": 62,
    "same_packet_seen_by_model_and_proofreader": true,
    "source_labels": [
      "fixture_intercepted",
      "staff_selected",
      "staff_selected"
    ],
    "task_sha256": "sha256:3c983d685d4dab4e56027317ed3473c5b12d22beb7c87ccda26c5081e24d3c5e"
  },
  "correction_used": false,
  "exact_binding": {
    "api_key_authentication_used": false,
    "authentication": "keyless_impersonated_service_account_adc",
    "endpoint_hostname": "australia-southeast1-aiplatform.googleapis.com",
    "location": "australia-southeast1",
    "model_id": "gemini-2.5-flash",
    "project": "bernie-emr4-dev",
    "provider": "google_vertex_ai",
    "service_account": "emr4-bernie-ai-dev@bernie-emr4-dev.iam.gserviceaccount.com"
  },
  "expected_goal": "cancel",
  "expected_proposal_family": "cancel",
  "expected_proposal_release": true,
  "expected_safe_outcome": true,
  "final_proofreader_disposition": "admit",
  "final_violation_codes": [],
  "operator_note": {
    "audit_only": true,
    "disposition": "admit",
    "note_sha256": "sha256:8e29ae1d1471b111e6a2c2befc54feb4292764830feb09811635ae6c66bb53d0",
    "operator_note": "Proposal for review; no booking was changed.",
    "parsed_into_plan": false,
    "product_delivered": false,
    "reason_codes": [],
    "retained_utf8_bytes": 44
  },
  "parent_audit_chain": {
    "event_count": 4,
    "terminal_hash": "sha256:0da9fc61a5919d4bcdcff114a979d606cda1bcfd30e0862981e82ca1e8ec1d77",
    "valid": true
  },
  "primary_exact_body_accepted": true,
  "primary_proofreader_disposition": "admit",
  "primary_violation_codes": [],
  "provider_outcomes": [
    {
      "bounded_completion_metadata": {
        "candidate_count": 1,
        "candidate_count_truncated": false,
        "finish_reasons": [
          "STOP"
        ],
        "part_counts": [
          1
        ],
        "provider_text_inspected_for_diagnosis": false,
        "provider_text_retained": false
      },
      "bounded_error": null,
      "http_status": 200,
      "latency_ms": 2959,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 196,
        "promptTokenCount": 3535,
        "thoughtsTokenCount": 335,
        "totalTokenCount": 4066
      }
    }
  ],
  "receptionist_output": {
    "decision_note": "Intent cancel: User explicitly requested to 'Call off' an appointment.",
    "disposition": "admit",
    "evidence_utterance_indices": [
      0
    ],
    "hidden_reasoning": false,
    "natural_response_parsed_into_form": false,
    "product_delivered": false,
    "raw_provider_response": false,
    "receptionist_response": "I'll prepare a proposal to cancel Margaret's appointment for your review. No booking was changed.",
    "violations": []
  },
  "release": {
    "api_spine_operation_id": "proposeAppointmentDelete",
    "appointment_ref": "synthetic-appointment-margaret",
    "candidate_slot_ids": [],
    "duration_minutes": 15,
    "kind": "proposal_candidate",
    "patient_ref": "synthetic-patient-margaret",
    "practitioner_ref": "synthetic-practitioner-shera",
    "proposal_family": "cancel",
    "requires_human_confirmation": true,
    "status": null,
    "warning_codes": [
      "staff_confirmation_required"
    ],
    "write_performed": false
  },
  "source_case_id": null,
  "terminal_second_call_reason": null,
  "terminal_status": "admitted",
  "typed_program": {
    "explicit_source_form": {
      "goal_code": 3,
      "steps": [
        {
          "operator_code": 11,
          "source_refs": [
            {
              "binding_code": 2,
              "kind": "binding",
              "prior_output_name": "none",
              "prior_step_index": -1
            }
          ]
        }
      ],
      "version_code": 3
    },
    "operator_note_excluded": true,
    "program_hash": "sha256:bd5a15660116fbd9efadbfbecce67df134665841d073da3f06c646a91a2857d7",
    "raw_provider_response": false
  }
}
```

## 15. b-cancel-takeout

```json
{
  "actual_provider_calls": 1,
  "admitted_operator_ids": [
    "prepare_cancel_proposal"
  ],
  "case_code": "b-cancel-takeout",
  "cleanup_passed": true,
  "context_frame_review": {
    "command_authority": false,
    "desk_context_sha256": "sha256:74735b1fbd36b48a95535ee0decf0da537ec70539be365e04f43fe5bf003219b",
    "disposition": "admit",
    "reviewed_context_revision": 62,
    "same_packet_seen_by_model_and_proofreader": true,
    "source_labels": [
      "fixture_intercepted",
      "staff_selected",
      "staff_selected"
    ],
    "task_sha256": "sha256:7434be1c912939d0919718b758369c0470ae3b310f40e1450eddadf75df5a360"
  },
  "correction_used": false,
  "exact_binding": {
    "api_key_authentication_used": false,
    "authentication": "keyless_impersonated_service_account_adc",
    "endpoint_hostname": "australia-southeast1-aiplatform.googleapis.com",
    "location": "australia-southeast1",
    "model_id": "gemini-2.5-flash",
    "project": "bernie-emr4-dev",
    "provider": "google_vertex_ai",
    "service_account": "emr4-bernie-ai-dev@bernie-emr4-dev.iam.gserviceaccount.com"
  },
  "expected_goal": "cancel",
  "expected_proposal_family": "cancel",
  "expected_proposal_release": true,
  "expected_safe_outcome": true,
  "final_proofreader_disposition": "admit",
  "final_violation_codes": [],
  "operator_note": {
    "audit_only": true,
    "disposition": "admit",
    "note_sha256": "sha256:d5f7f9ddae7a66d7394337f714ea470a4d3decdda0f53bfbf22fbe9ad803325e",
    "operator_note": "Proposal for review, no booking was changed.",
    "parsed_into_plan": false,
    "product_delivered": false,
    "reason_codes": [],
    "retained_utf8_bytes": 44
  },
  "parent_audit_chain": {
    "event_count": 4,
    "terminal_hash": "sha256:fb278724d71067c85d0ae97c44c6203819b425c30c11fe0b2a5c9b5cce282d3f",
    "valid": true
  },
  "primary_exact_body_accepted": true,
  "primary_proofreader_disposition": "admit",
  "primary_violation_codes": [],
  "provider_outcomes": [
    {
      "bounded_completion_metadata": {
        "candidate_count": 1,
        "candidate_count_truncated": false,
        "finish_reasons": [
          "STOP"
        ],
        "part_counts": [
          1
        ],
        "provider_text_inspected_for_diagnosis": false,
        "provider_text_retained": false
      },
      "bounded_error": null,
      "http_status": 200,
      "latency_ms": 2208,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 198,
        "promptTokenCount": 3536,
        "thoughtsTokenCount": 136,
        "totalTokenCount": 3870
      }
    }
  ],
  "receptionist_output": {
    "decision_note": "Intent cancel: The staff member explicitly requested to 'take out' an appointment.",
    "disposition": "admit",
    "evidence_utterance_indices": [
      0
    ],
    "hidden_reasoning": false,
    "natural_response_parsed_into_form": false,
    "product_delivered": false,
    "raw_provider_response": false,
    "receptionist_response": "I'm preparing a proposal to cancel Margaret Thompson's appointment for review. No booking was changed.",
    "violations": []
  },
  "release": {
    "api_spine_operation_id": "proposeAppointmentDelete",
    "appointment_ref": "synthetic-appointment-margaret",
    "candidate_slot_ids": [],
    "duration_minutes": 15,
    "kind": "proposal_candidate",
    "patient_ref": "synthetic-patient-margaret",
    "practitioner_ref": "synthetic-practitioner-shera",
    "proposal_family": "cancel",
    "requires_human_confirmation": true,
    "status": null,
    "warning_codes": [
      "staff_confirmation_required"
    ],
    "write_performed": false
  },
  "source_case_id": null,
  "terminal_second_call_reason": null,
  "terminal_status": "admitted",
  "typed_program": {
    "explicit_source_form": {
      "goal_code": 3,
      "steps": [
        {
          "operator_code": 11,
          "source_refs": [
            {
              "binding_code": 2,
              "kind": "binding",
              "prior_output_name": "none",
              "prior_step_index": -1
            }
          ]
        }
      ],
      "version_code": 3
    },
    "operator_note_excluded": true,
    "program_hash": "sha256:4f9d634b998a87c4108c4cced1d53b11298d55dccc7f3818aa3c9b7918702848",
    "raw_provider_response": false
  }
}
```

## 16. b-status-complete

```json
{
  "actual_provider_calls": 1,
  "admitted_operator_ids": [
    "prepare_status_proposal"
  ],
  "case_code": "b-status-complete",
  "cleanup_passed": true,
  "context_frame_review": {
    "command_authority": false,
    "desk_context_sha256": "sha256:8e69aacb634b26be49192e2b16a3dede78961a39d4ae562c127e0ac9eb1bd60c",
    "disposition": "admit",
    "reviewed_context_revision": 62,
    "same_packet_seen_by_model_and_proofreader": true,
    "source_labels": [
      "fixture_intercepted",
      "staff_selected",
      "staff_selected"
    ],
    "task_sha256": "sha256:dc361014718ba029bbf3a1732362e3d5119f7530092d44b8d38af27a81a87a44"
  },
  "correction_used": false,
  "exact_binding": {
    "api_key_authentication_used": false,
    "authentication": "keyless_impersonated_service_account_adc",
    "endpoint_hostname": "australia-southeast1-aiplatform.googleapis.com",
    "location": "australia-southeast1",
    "model_id": "gemini-2.5-flash",
    "project": "bernie-emr4-dev",
    "provider": "google_vertex_ai",
    "service_account": "emr4-bernie-ai-dev@bernie-emr4-dev.iam.gserviceaccount.com"
  },
  "expected_goal": "status_change",
  "expected_proposal_family": "status_change",
  "expected_proposal_release": true,
  "expected_safe_outcome": true,
  "final_proofreader_disposition": "admit",
  "final_violation_codes": [],
  "operator_note": {
    "audit_only": true,
    "disposition": "admit",
    "note_sha256": "sha256:d0bde6f469f2dc67f76be9f46670e7eb4b523d2294cad67b9ff0a57c8c7206df",
    "operator_note": "Proposal for review: no booking was changed.",
    "parsed_into_plan": false,
    "product_delivered": false,
    "reason_codes": [],
    "retained_utf8_bytes": 44
  },
  "parent_audit_chain": {
    "event_count": 4,
    "terminal_hash": "sha256:bdeb58fc863490a3e97dd536bd3ad331cdda32a0c975a5d12b870ac0ae6bcfd8",
    "valid": true
  },
  "primary_exact_body_accepted": true,
  "primary_proofreader_disposition": "admit",
  "primary_violation_codes": [],
  "provider_outcomes": [
    {
      "bounded_completion_metadata": {
        "candidate_count": 1,
        "candidate_count_truncated": false,
        "finish_reasons": [
          "STOP"
        ],
        "part_counts": [
          1
        ],
        "provider_text_inspected_for_diagnosis": false,
        "provider_text_retained": false
      },
      "bounded_error": null,
      "http_status": 200,
      "latency_ms": 2808,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 254,
        "promptTokenCount": 3560,
        "thoughtsTokenCount": 278,
        "totalTokenCount": 4092
      }
    }
  ],
  "receptionist_output": {
    "decision_note": "Intent status_change: The staff member explicitly requested to set the status of an appointment.",
    "disposition": "admit",
    "evidence_utterance_indices": [
      0
    ],
    "hidden_reasoning": false,
    "natural_response_parsed_into_form": false,
    "product_delivered": false,
    "raw_provider_response": false,
    "receptionist_response": "I'm preparing a proposal to change the status of Margaret Thompson's appointment to completed for your review. No booking was changed.",
    "violations": []
  },
  "release": {
    "api_spine_operation_id": "proposeAppointmentStatus",
    "appointment_ref": "synthetic-appointment-margaret",
    "candidate_slot_ids": [],
    "duration_minutes": 15,
    "kind": "proposal_candidate",
    "patient_ref": "synthetic-patient-margaret",
    "practitioner_ref": "synthetic-practitioner-shera",
    "proposal_family": "status_change",
    "requires_human_confirmation": true,
    "status": "completed",
    "warning_codes": [
      "staff_confirmation_required"
    ],
    "write_performed": false
  },
  "source_case_id": null,
  "terminal_second_call_reason": null,
  "terminal_status": "admitted",
  "typed_program": {
    "explicit_source_form": {
      "goal_code": 4,
      "steps": [
        {
          "operator_code": 12,
          "source_refs": [
            {
              "binding_code": 2,
              "kind": "binding",
              "prior_output_name": "none",
              "prior_step_index": -1
            },
            {
              "binding_code": 4,
              "kind": "binding",
              "prior_output_name": "none",
              "prior_step_index": -1
            }
          ]
        }
      ],
      "version_code": 3
    },
    "operator_note_excluded": true,
    "program_hash": "sha256:050e4d486e2a58f68854013bebfdf4c4d422f78c069fd4260679abda48f801d1",
    "raw_provider_response": false
  }
}
```

## 17. b-status-arrived

```json
{
  "actual_provider_calls": 1,
  "admitted_operator_ids": [
    "prepare_status_proposal"
  ],
  "case_code": "b-status-arrived",
  "cleanup_passed": true,
  "context_frame_review": {
    "command_authority": false,
    "desk_context_sha256": "sha256:b3f1e6576086b6d131243d44451650162bba42f3506d505e6a9d72733c13de9c",
    "disposition": "admit",
    "reviewed_context_revision": 62,
    "same_packet_seen_by_model_and_proofreader": true,
    "source_labels": [
      "fixture_intercepted",
      "staff_selected",
      "staff_selected"
    ],
    "task_sha256": "sha256:9ce5cbd816787e7a95b41ac02724e43f8c2ee8962d0640f6b33dcd76021928aa"
  },
  "correction_used": false,
  "exact_binding": {
    "api_key_authentication_used": false,
    "authentication": "keyless_impersonated_service_account_adc",
    "endpoint_hostname": "australia-southeast1-aiplatform.googleapis.com",
    "location": "australia-southeast1",
    "model_id": "gemini-2.5-flash",
    "project": "bernie-emr4-dev",
    "provider": "google_vertex_ai",
    "service_account": "emr4-bernie-ai-dev@bernie-emr4-dev.iam.gserviceaccount.com"
  },
  "expected_goal": "status_change",
  "expected_proposal_family": "status_change",
  "expected_proposal_release": true,
  "expected_safe_outcome": true,
  "final_proofreader_disposition": "admit",
  "final_violation_codes": [],
  "operator_note": {
    "audit_only": true,
    "disposition": "admit",
    "note_sha256": "sha256:d0bde6f469f2dc67f76be9f46670e7eb4b523d2294cad67b9ff0a57c8c7206df",
    "operator_note": "Proposal for review: no booking was changed.",
    "parsed_into_plan": false,
    "product_delivered": false,
    "reason_codes": [],
    "retained_utf8_bytes": 44
  },
  "parent_audit_chain": {
    "event_count": 4,
    "terminal_hash": "sha256:dd28a0a41c1ac03737faa55a4f198b15e412d47a96438447581c9547ca3316a6",
    "valid": true
  },
  "primary_exact_body_accepted": true,
  "primary_proofreader_disposition": "admit",
  "primary_violation_codes": [],
  "provider_outcomes": [
    {
      "bounded_completion_metadata": {
        "candidate_count": 1,
        "candidate_count_truncated": false,
        "finish_reasons": [
          "STOP"
        ],
        "part_counts": [
          1
        ],
        "provider_text_inspected_for_diagnosis": false,
        "provider_text_retained": false
      },
      "bounded_error": null,
      "http_status": 200,
      "latency_ms": 2582,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 250,
        "promptTokenCount": 3564,
        "thoughtsTokenCount": 230,
        "totalTokenCount": 4044
      }
    }
  ],
  "receptionist_output": {
    "decision_note": "Intent status_change: All necessary information for a status change proposal is present.",
    "disposition": "admit",
    "evidence_utterance_indices": [
      0
    ],
    "hidden_reasoning": false,
    "natural_response_parsed_into_form": false,
    "product_delivered": false,
    "raw_provider_response": false,
    "receptionist_response": "I'm preparing a proposal to update Margaret Thompson's appointment status to arrived for your review. No booking was changed.",
    "violations": []
  },
  "release": {
    "api_spine_operation_id": "proposeAppointmentStatus",
    "appointment_ref": "synthetic-appointment-margaret",
    "candidate_slot_ids": [],
    "duration_minutes": 15,
    "kind": "proposal_candidate",
    "patient_ref": "synthetic-patient-margaret",
    "practitioner_ref": "synthetic-practitioner-shera",
    "proposal_family": "status_change",
    "requires_human_confirmation": true,
    "status": "arrived",
    "warning_codes": [
      "staff_confirmation_required"
    ],
    "write_performed": false
  },
  "source_case_id": null,
  "terminal_second_call_reason": null,
  "terminal_status": "admitted",
  "typed_program": {
    "explicit_source_form": {
      "goal_code": 4,
      "steps": [
        {
          "operator_code": 12,
          "source_refs": [
            {
              "binding_code": 2,
              "kind": "binding",
              "prior_output_name": "none",
              "prior_step_index": -1
            },
            {
              "binding_code": 4,
              "kind": "binding",
              "prior_output_name": "none",
              "prior_step_index": -1
            }
          ]
        }
      ],
      "version_code": 3
    },
    "operator_note_excluded": true,
    "program_hash": "sha256:050e4d486e2a58f68854013bebfdf4c4d422f78c069fd4260679abda48f801d1",
    "raw_provider_response": false
  }
}
```

## 18. b-status-noshow-gap

```json
{
  "actual_provider_calls": 2,
  "admitted_operator_ids": [],
  "case_code": "b-status-noshow-gap",
  "cleanup_passed": true,
  "context_frame_review": {
    "command_authority": false,
    "desk_context_sha256": "sha256:daa0e7a1e413d09b12b1cc09b31d72345a2aa27b0684c8c91eb89ce6aefbca73",
    "disposition": "admit",
    "reviewed_context_revision": 62,
    "same_packet_seen_by_model_and_proofreader": true,
    "source_labels": [
      "fixture_intercepted",
      "staff_selected",
      "staff_selected"
    ],
    "task_sha256": "sha256:aba386a9d4631505cce96b9a5ee866d9974e0cf70be6101c89277a7293e4ab91"
  },
  "correction_used": true,
  "exact_binding": {
    "api_key_authentication_used": false,
    "authentication": "keyless_impersonated_service_account_adc",
    "endpoint_hostname": "australia-southeast1-aiplatform.googleapis.com",
    "location": "australia-southeast1",
    "model_id": "gemini-2.5-flash",
    "project": "bernie-emr4-dev",
    "provider": "google_vertex_ai",
    "service_account": "emr4-bernie-ai-dev@bernie-emr4-dev.iam.gserviceaccount.com"
  },
  "expected_goal": "clarification",
  "expected_proposal_family": "clarification",
  "expected_proposal_release": false,
  "expected_safe_outcome": false,
  "final_proofreader_disposition": "edge_abort",
  "final_violation_codes": [
    "external_binding_invalid"
  ],
  "operator_note": {
    "audit_only": true,
    "disposition": "admit",
    "note_sha256": "sha256:d0bde6f469f2dc67f76be9f46670e7eb4b523d2294cad67b9ff0a57c8c7206df",
    "operator_note": "Proposal for review: no booking was changed.",
    "parsed_into_plan": false,
    "product_delivered": false,
    "reason_codes": [],
    "retained_utf8_bytes": 44
  },
  "parent_audit_chain": {
    "event_count": 6,
    "terminal_hash": "sha256:50dcccf6a348b903476dd30c26f00afc963f0b887392d9a70e208ffa09d9bce9",
    "valid": true
  },
  "primary_exact_body_accepted": true,
  "primary_proofreader_disposition": "revision_required",
  "primary_violation_codes": [
    "external_binding_invalid"
  ],
  "provider_outcomes": [
    {
      "bounded_completion_metadata": {
        "candidate_count": 1,
        "candidate_count_truncated": false,
        "finish_reasons": [
          "STOP"
        ],
        "part_counts": [
          1
        ],
        "provider_text_inspected_for_diagnosis": false,
        "provider_text_retained": false
      },
      "bounded_error": null,
      "http_status": 200,
      "latency_ms": 5498,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 253,
        "promptTokenCount": 3541,
        "thoughtsTokenCount": 813,
        "totalTokenCount": 4607
      }
    },
    {
      "bounded_completion_metadata": {
        "candidate_count": 1,
        "candidate_count_truncated": false,
        "finish_reasons": [
          "STOP"
        ],
        "part_counts": [
          1
        ],
        "provider_text_inspected_for_diagnosis": false,
        "provider_text_retained": false
      },
      "bounded_error": null,
      "http_status": 200,
      "latency_ms": 5672,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 254,
        "promptTokenCount": 3762,
        "thoughtsTokenCount": 846,
        "totalTokenCount": 4862
      }
    }
  ],
  "receptionist_output": {
    "decision_note": "Intent status_change: The status 'no-show' was explicitly requested for the selected appointment.",
    "disposition": "admit",
    "evidence_utterance_indices": [
      0
    ],
    "hidden_reasoning": false,
    "natural_response_parsed_into_form": false,
    "product_delivered": false,
    "raw_provider_response": false,
    "receptionist_response": "I'm preparing the request to mark Margaret's appointment as a no-show for review. No booking was changed.",
    "violations": []
  },
  "release": null,
  "source_case_id": null,
  "terminal_second_call_reason": "proofreader_correction",
  "terminal_status": "terminal_no_release",
  "typed_program": {
    "explicit_source_form": {
      "goal_code": 4,
      "steps": [
        {
          "operator_code": 12,
          "source_refs": [
            {
              "binding_code": 2,
              "kind": "binding",
              "prior_output_name": "none",
              "prior_step_index": -1
            },
            {
              "binding_code": -1,
              "kind": "binding",
              "prior_output_name": "none",
              "prior_step_index": -1
            }
          ]
        }
      ],
      "version_code": 3
    },
    "operator_note_excluded": true,
    "program_hash": "sha256:52630e6f3a94dbad9f7be009fc18e5e3461a1465fcf3a70702bff03a5ca01f5f",
    "raw_provider_response": false
  }
}
```

## 19. b-squeeze-without

```json
{
  "actual_provider_calls": 1,
  "admitted_operator_ids": [
    "resolve_patient_reference",
    "resolve_practitioner_reference",
    "resolve_date_expression",
    "read_practitioner_schedule",
    "assess_squeeze_in_options"
  ],
  "case_code": "b-squeeze-without",
  "cleanup_passed": true,
  "context_frame_review": {
    "command_authority": false,
    "desk_context_sha256": "sha256:c0d72d205466f19eb12f58102d862202dda672efde08b9dc7f7b560ba99f9614",
    "disposition": "admit",
    "reviewed_context_revision": 62,
    "same_packet_seen_by_model_and_proofreader": true,
    "source_labels": [
      "fixture_intercepted",
      "staff_selected",
      "staff_selected"
    ],
    "task_sha256": "sha256:8ab27136180da17817f662d953c33e052287d573e3b94751de5614c52ec2b9ca"
  },
  "correction_used": false,
  "exact_binding": {
    "api_key_authentication_used": false,
    "authentication": "keyless_impersonated_service_account_adc",
    "endpoint_hostname": "australia-southeast1-aiplatform.googleapis.com",
    "location": "australia-southeast1",
    "model_id": "gemini-2.5-flash",
    "project": "bernie-emr4-dev",
    "provider": "google_vertex_ai",
    "service_account": "emr4-bernie-ai-dev@bernie-emr4-dev.iam.gserviceaccount.com"
  },
  "expected_goal": "squeeze_in_assessment",
  "expected_proposal_family": "squeeze_in_assessment",
  "expected_proposal_release": true,
  "expected_safe_outcome": true,
  "final_proofreader_disposition": "admit",
  "final_violation_codes": [],
  "operator_note": {
    "audit_only": true,
    "disposition": "admit",
    "note_sha256": "sha256:d0bde6f469f2dc67f76be9f46670e7eb4b523d2294cad67b9ff0a57c8c7206df",
    "operator_note": "Proposal for review: no booking was changed.",
    "parsed_into_plan": false,
    "product_delivered": false,
    "reason_codes": [],
    "retained_utf8_bytes": 44
  },
  "parent_audit_chain": {
    "event_count": 4,
    "terminal_hash": "sha256:2945f406bddbf89d0b2bca716bf7e227f1f77473d671b27f26c0bce35b349ec9",
    "valid": true
  },
  "primary_exact_body_accepted": true,
  "primary_proofreader_disposition": "admit",
  "primary_violation_codes": [],
  "provider_outcomes": [
    {
      "bounded_completion_metadata": {
        "candidate_count": 1,
        "candidate_count_truncated": false,
        "finish_reasons": [
          "STOP"
        ],
        "part_counts": [
          1
        ],
        "provider_text_inspected_for_diagnosis": false,
        "provider_text_retained": false
      },
      "bounded_error": null,
      "http_status": 200,
      "latency_ms": 4541,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 723,
        "promptTokenCount": 3671,
        "thoughtsTokenCount": 374,
        "totalTokenCount": 4768
      }
    }
  ],
  "receptionist_output": {
    "decision_note": "Intent squeeze_in_assessment: Utterance explicitly requests to 'squeeze in' an appointment 'without moving anyone'.",
    "disposition": "admit",
    "evidence_utterance_indices": [
      0
    ],
    "hidden_reasoning": false,
    "natural_response_parsed_into_form": false,
    "product_delivered": false,
    "raw_provider_response": false,
    "receptionist_response": "I'm looking into options to squeeze Margaret in with Dr. Shera for 15 minutes today without moving anyone. I'll have some proposals for you to review shortly.",
    "violations": []
  },
  "release": {
    "api_spine_operation_id": null,
    "appointment_ref": null,
    "candidate_slot_ids": [
      "synthetic-slot-july27-1215"
    ],
    "duration_minutes": 15,
    "kind": "squeeze_in_assessment",
    "patient_ref": "synthetic-patient-margaret",
    "practitioner_ref": "synthetic-practitioner-shera",
    "proposal_family": "squeeze_in_assessment",
    "requires_human_confirmation": true,
    "status": null,
    "warning_codes": [
      "adjacent_to_break",
      "manual_squeeze_in_review",
      "no_reservation",
      "staff_confirmation_required",
      "staff_selection_required"
    ],
    "write_performed": false
  },
  "source_case_id": null,
  "terminal_second_call_reason": null,
  "terminal_status": "admitted",
  "typed_program": {
    "explicit_source_form": {
      "goal_code": 5,
      "steps": [
        {
          "operator_code": 0,
          "source_refs": [
            {
              "binding_code": 3,
              "kind": "binding",
              "prior_output_name": "none",
              "prior_step_index": -1
            }
          ]
        },
        {
          "operator_code": 1,
          "source_refs": [
            {
              "binding_code": 4,
              "kind": "binding",
              "prior_output_name": "none",
              "prior_step_index": -1
            }
          ]
        },
        {
          "operator_code": 2,
          "source_refs": [
            {
              "binding_code": 0,
              "kind": "binding",
              "prior_output_name": "none",
              "prior_step_index": -1
            }
          ]
        },
        {
          "operator_code": 5,
          "source_refs": [
            {
              "binding_code": -1,
              "kind": "prior_output",
              "prior_output_name": "practitioner",
              "prior_step_index": 1
            },
            {
              "binding_code": -1,
              "kind": "prior_output",
              "prior_output_name": "date",
              "prior_step_index": 2
            }
          ]
        },
        {
          "operator_code": 7,
          "source_refs": [
            {
              "binding_code": -1,
              "kind": "prior_output",
              "prior_output_name": "patient",
              "prior_step_index": 0
            },
            {
              "binding_code": -1,
              "kind": "prior_output",
              "prior_output_name": "schedule",
              "prior_step_index": 3
            },
            {
              "binding_code": 2,
              "kind": "binding",
              "prior_output_name": "none",
              "prior_step_index": -1
            },
            {
              "binding_code": 6,
              "kind": "binding",
              "prior_output_name": "none",
              "prior_step_index": -1
            }
          ]
        }
      ],
      "version_code": 3
    },
    "operator_note_excluded": true,
    "program_hash": "sha256:e018846f2d0f84bd75c77e6164c1aa7a7bf0a18568880e5ab245eab79f65cd54",
    "raw_provider_response": false
  }
}
```

## 20. b-squeeze-negated-move

```json
{
  "actual_provider_calls": 1,
  "admitted_operator_ids": [
    "resolve_patient_reference",
    "resolve_practitioner_reference",
    "resolve_date_expression",
    "read_practitioner_schedule",
    "assess_squeeze_in_options"
  ],
  "case_code": "b-squeeze-negated-move",
  "cleanup_passed": true,
  "context_frame_review": {
    "command_authority": false,
    "desk_context_sha256": "sha256:2219cb4af2e6d01efdf520adbb48620c240cf8f5fe14b798d57f5f968888dfd0",
    "disposition": "admit",
    "reviewed_context_revision": 62,
    "same_packet_seen_by_model_and_proofreader": true,
    "source_labels": [
      "fixture_intercepted",
      "staff_selected",
      "staff_selected"
    ],
    "task_sha256": "sha256:b2217697b7a8178aa07adc3e6e9bb71be84fcbdfe404a0e31b1b454be86f9f18"
  },
  "correction_used": false,
  "exact_binding": {
    "api_key_authentication_used": false,
    "authentication": "keyless_impersonated_service_account_adc",
    "endpoint_hostname": "australia-southeast1-aiplatform.googleapis.com",
    "location": "australia-southeast1",
    "model_id": "gemini-2.5-flash",
    "project": "bernie-emr4-dev",
    "provider": "google_vertex_ai",
    "service_account": "emr4-bernie-ai-dev@bernie-emr4-dev.iam.gserviceaccount.com"
  },
  "expected_goal": "squeeze_in_assessment",
  "expected_proposal_family": "squeeze_in_assessment",
  "expected_proposal_release": true,
  "expected_safe_outcome": true,
  "final_proofreader_disposition": "admit",
  "final_violation_codes": [],
  "operator_note": {
    "audit_only": true,
    "disposition": "admit",
    "note_sha256": "sha256:d5f7f9ddae7a66d7394337f714ea470a4d3decdda0f53bfbf22fbe9ad803325e",
    "operator_note": "Proposal for review, no booking was changed.",
    "parsed_into_plan": false,
    "product_delivered": false,
    "reason_codes": [],
    "retained_utf8_bytes": 44
  },
  "parent_audit_chain": {
    "event_count": 4,
    "terminal_hash": "sha256:d750d026b40e8b98f6d7d99d015649d9083750e16813e1ee4cfdb2168693950e",
    "valid": true
  },
  "primary_exact_body_accepted": true,
  "primary_proofreader_disposition": "admit",
  "primary_violation_codes": [],
  "provider_outcomes": [
    {
      "bounded_completion_metadata": {
        "candidate_count": 1,
        "candidate_count_truncated": false,
        "finish_reasons": [
          "STOP"
        ],
        "part_counts": [
          1
        ],
        "provider_text_inspected_for_diagnosis": false,
        "provider_text_retained": false
      },
      "bounded_error": null,
      "http_status": 200,
      "latency_ms": 7279,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 714,
        "promptTokenCount": 3675,
        "thoughtsTokenCount": 1083,
        "totalTokenCount": 5472
      }
    }
  ],
  "receptionist_output": {
    "decision_note": "Intent squeeze_in_assessment: staff requested to squeeze in an appointment with a specific policy.",
    "disposition": "admit",
    "evidence_utterance_indices": [
      0
    ],
    "hidden_reasoning": false,
    "natural_response_parsed_into_form": false,
    "product_delivered": false,
    "raw_provider_response": false,
    "receptionist_response": "I'm looking into options to squeeze Margaret Thompson in with Dr Shera for 15 minutes today without moving other appointments. I'll prepare this for review.",
    "violations": []
  },
  "release": {
    "api_spine_operation_id": null,
    "appointment_ref": null,
    "candidate_slot_ids": [
      "synthetic-slot-july27-1215"
    ],
    "duration_minutes": 15,
    "kind": "squeeze_in_assessment",
    "patient_ref": "synthetic-patient-margaret",
    "practitioner_ref": "synthetic-practitioner-shera",
    "proposal_family": "squeeze_in_assessment",
    "requires_human_confirmation": true,
    "status": null,
    "warning_codes": [
      "adjacent_to_break",
      "manual_squeeze_in_review",
      "no_reservation",
      "staff_confirmation_required",
      "staff_selection_required"
    ],
    "write_performed": false
  },
  "source_case_id": null,
  "terminal_second_call_reason": null,
  "terminal_status": "admitted",
  "typed_program": {
    "explicit_source_form": {
      "goal_code": 5,
      "steps": [
        {
          "operator_code": 0,
          "source_refs": [
            {
              "binding_code": 3,
              "kind": "binding",
              "prior_output_name": "none",
              "prior_step_index": -1
            }
          ]
        },
        {
          "operator_code": 1,
          "source_refs": [
            {
              "binding_code": 4,
              "kind": "binding",
              "prior_output_name": "none",
              "prior_step_index": -1
            }
          ]
        },
        {
          "operator_code": 2,
          "source_refs": [
            {
              "binding_code": 0,
              "kind": "binding",
              "prior_output_name": "none",
              "prior_step_index": -1
            }
          ]
        },
        {
          "operator_code": 5,
          "source_refs": [
            {
              "binding_code": -1,
              "kind": "prior_output",
              "prior_output_name": "practitioner",
              "prior_step_index": 1
            },
            {
              "binding_code": -1,
              "kind": "prior_output",
              "prior_output_name": "date",
              "prior_step_index": 2
            }
          ]
        },
        {
          "operator_code": 7,
          "source_refs": [
            {
              "binding_code": -1,
              "kind": "prior_output",
              "prior_output_name": "patient",
              "prior_step_index": 0
            },
            {
              "binding_code": -1,
              "kind": "prior_output",
              "prior_output_name": "schedule",
              "prior_step_index": 3
            },
            {
              "binding_code": 2,
              "kind": "binding",
              "prior_output_name": "none",
              "prior_step_index": -1
            },
            {
              "binding_code": 6,
              "kind": "binding",
              "prior_output_name": "none",
              "prior_step_index": -1
            }
          ]
        }
      ],
      "version_code": 3
    },
    "operator_note_excluded": true,
    "program_hash": "sha256:673dbdd11f57bdc06935e9e0fec43f4f9dd0d5c7baf53ccfd6572fad6efa88e1",
    "raw_provider_response": false
  }
}
```

## 21. b-clarify-sort

```json
{
  "actual_provider_calls": 2,
  "admitted_operator_ids": [
    "request_clarification"
  ],
  "case_code": "b-clarify-sort",
  "cleanup_passed": true,
  "context_frame_review": {
    "command_authority": false,
    "desk_context_sha256": "sha256:741ef917c4947b88405648836a7d7933c9a10efa94b59461a1240dd44be6815f",
    "disposition": "admit",
    "reviewed_context_revision": 62,
    "same_packet_seen_by_model_and_proofreader": true,
    "source_labels": [
      "fixture_intercepted",
      "staff_selected",
      "staff_selected"
    ],
    "task_sha256": "sha256:a1a10c1633851b93572a56645c145eb0604a05f525004c9079ff582c4e3a65a7"
  },
  "correction_used": true,
  "exact_binding": {
    "api_key_authentication_used": false,
    "authentication": "keyless_impersonated_service_account_adc",
    "endpoint_hostname": "australia-southeast1-aiplatform.googleapis.com",
    "location": "australia-southeast1",
    "model_id": "gemini-2.5-flash",
    "project": "bernie-emr4-dev",
    "provider": "google_vertex_ai",
    "service_account": "emr4-bernie-ai-dev@bernie-emr4-dev.iam.gserviceaccount.com"
  },
  "expected_goal": "clarification",
  "expected_proposal_family": "clarification",
  "expected_proposal_release": false,
  "expected_safe_outcome": true,
  "final_proofreader_disposition": "admit",
  "final_violation_codes": [],
  "operator_note": {
    "audit_only": true,
    "disposition": "admit",
    "note_sha256": "sha256:8e29ae1d1471b111e6a2c2befc54feb4292764830feb09811635ae6c66bb53d0",
    "operator_note": "Proposal for review; no booking was changed.",
    "parsed_into_plan": false,
    "product_delivered": false,
    "reason_codes": [],
    "retained_utf8_bytes": 44
  },
  "parent_audit_chain": {
    "event_count": 6,
    "terminal_hash": "sha256:25129663a33c463a9671d385700b7d943da40b49fed6b0374fe538f799f5b7cd",
    "valid": true
  },
  "primary_exact_body_accepted": true,
  "primary_proofreader_disposition": "revision_required",
  "primary_violation_codes": [
    "receptionist_response_ungrounded_person"
  ],
  "provider_outcomes": [
    {
      "bounded_completion_metadata": {
        "candidate_count": 1,
        "candidate_count_truncated": false,
        "finish_reasons": [
          "STOP"
        ],
        "part_counts": [
          1
        ],
        "provider_text_inspected_for_diagnosis": false,
        "provider_text_retained": false
      },
      "bounded_error": null,
      "http_status": 200,
      "latency_ms": 2209,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 125,
        "promptTokenCount": 3546,
        "thoughtsTokenCount": 238,
        "totalTokenCount": 3909
      }
    },
    {
      "bounded_completion_metadata": {
        "candidate_count": 1,
        "candidate_count_truncated": false,
        "finish_reasons": [
          "STOP"
        ],
        "part_counts": [
          1
        ],
        "provider_text_inspected_for_diagnosis": false,
        "provider_text_retained": false
      },
      "bounded_error": null,
      "http_status": 200,
      "latency_ms": 4911,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 150,
        "promptTokenCount": 3719,
        "thoughtsTokenCount": 791,
        "totalTokenCount": 4660
      }
    }
  ],
  "receptionist_output": {
    "decision_note": "Intent clarification: The request \"sort out\" is ambiguous and does not specify an action.",
    "disposition": "admit",
    "evidence_utterance_indices": [
      0
    ],
    "hidden_reasoning": false,
    "natural_response_parsed_into_form": false,
    "product_delivered": false,
    "raw_provider_response": false,
    "receptionist_response": "I can help with that. Could you please tell me what you'd like to do with the appointment?",
    "violations": []
  },
  "release": {
    "api_spine_operation_id": null,
    "appointment_ref": null,
    "candidate_slot_ids": [],
    "duration_minutes": null,
    "kind": "clarification",
    "patient_ref": null,
    "practitioner_ref": null,
    "proposal_family": "clarification",
    "requires_human_confirmation": false,
    "status": null,
    "warning_codes": [],
    "write_performed": false
  },
  "source_case_id": null,
  "terminal_second_call_reason": "proofreader_correction",
  "terminal_status": "admitted_after_correction",
  "typed_program": {
    "explicit_source_form": {
      "goal_code": 6,
      "steps": [
        {
          "operator_code": 13,
          "source_refs": []
        }
      ],
      "version_code": 3
    },
    "operator_note_excluded": true,
    "program_hash": "sha256:f0ca55bba06adbb951ae81a82ea1af31ec7c2d84dbc1e4cca610e3842cc0b3a5",
    "raw_provider_response": false
  }
}
```

## 22. b-clarify-different

```json
{
  "actual_provider_calls": 2,
  "admitted_operator_ids": [
    "resolve_patient_reference",
    "read_selected_appointment",
    "request_clarification"
  ],
  "case_code": "b-clarify-different",
  "cleanup_passed": true,
  "context_frame_review": {
    "command_authority": false,
    "desk_context_sha256": "sha256:88460bd5573b57734e8f05ef490fbeb0874256f710ed2db57185d63e2d97fa15",
    "disposition": "admit",
    "reviewed_context_revision": 62,
    "same_packet_seen_by_model_and_proofreader": true,
    "source_labels": [
      "fixture_intercepted",
      "staff_selected",
      "staff_selected"
    ],
    "task_sha256": "sha256:2f75695b99e1b76816250a191434bdf0aa5d38ce12d28fb800debddbc1280756"
  },
  "correction_used": true,
  "exact_binding": {
    "api_key_authentication_used": false,
    "authentication": "keyless_impersonated_service_account_adc",
    "endpoint_hostname": "australia-southeast1-aiplatform.googleapis.com",
    "location": "australia-southeast1",
    "model_id": "gemini-2.5-flash",
    "project": "bernie-emr4-dev",
    "provider": "google_vertex_ai",
    "service_account": "emr4-bernie-ai-dev@bernie-emr4-dev.iam.gserviceaccount.com"
  },
  "expected_goal": "clarification",
  "expected_proposal_family": "clarification",
  "expected_proposal_release": false,
  "expected_safe_outcome": true,
  "final_proofreader_disposition": "admit",
  "final_violation_codes": [],
  "operator_note": {
    "audit_only": true,
    "disposition": "admit",
    "note_sha256": "sha256:d0bde6f469f2dc67f76be9f46670e7eb4b523d2294cad67b9ff0a57c8c7206df",
    "operator_note": "Proposal for review: no booking was changed.",
    "parsed_into_plan": false,
    "product_delivered": false,
    "reason_codes": [],
    "retained_utf8_bytes": 44
  },
  "parent_audit_chain": {
    "event_count": 6,
    "terminal_hash": "sha256:9c47ca033423804703b4b23c558db396d8764744d83d6170b6477a7d9f0d0a75",
    "valid": true
  },
  "primary_exact_body_accepted": true,
  "primary_proofreader_disposition": "revision_required",
  "primary_violation_codes": [
    "decision_note_goal_mismatch"
  ],
  "provider_outcomes": [
    {
      "bounded_completion_metadata": {
        "candidate_count": 1,
        "candidate_count_truncated": false,
        "finish_reasons": [
          "STOP"
        ],
        "part_counts": [
          1
        ],
        "provider_text_inspected_for_diagnosis": false,
        "provider_text_retained": false
      },
      "bounded_error": null,
      "http_status": 200,
      "latency_ms": 6395,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 341,
        "promptTokenCount": 3534,
        "thoughtsTokenCount": 1097,
        "totalTokenCount": 4972
      }
    },
    {
      "bounded_completion_metadata": {
        "candidate_count": 1,
        "candidate_count_truncated": false,
        "finish_reasons": [
          "STOP"
        ],
        "part_counts": [
          1
        ],
        "provider_text_inspected_for_diagnosis": false,
        "provider_text_retained": false
      },
      "bounded_error": null,
      "http_status": 200,
      "latency_ms": 5212,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 357,
        "promptTokenCount": 3814,
        "thoughtsTokenCount": 679,
        "totalTokenCount": 4850
      }
    }
  ],
  "receptionist_output": {
    "decision_note": "Intent clarification: The request is to clarify what kind of change is needed for the appointment.",
    "disposition": "admit",
    "evidence_utterance_indices": [
      0
    ],
    "hidden_reasoning": false,
    "natural_response_parsed_into_form": false,
    "product_delivered": false,
    "raw_provider_response": false,
    "receptionist_response": "I understand Margaret Thompson needs a different appointment. Could you please clarify if you'd like to move, resize, or cancel her existing appointment?",
    "violations": []
  },
  "release": {
    "api_spine_operation_id": null,
    "appointment_ref": null,
    "candidate_slot_ids": [],
    "duration_minutes": null,
    "kind": "clarification",
    "patient_ref": null,
    "practitioner_ref": null,
    "proposal_family": "clarification",
    "requires_human_confirmation": false,
    "status": null,
    "warning_codes": [],
    "write_performed": false
  },
  "source_case_id": null,
  "terminal_second_call_reason": "proofreader_correction",
  "terminal_status": "admitted_after_correction",
  "typed_program": {
    "explicit_source_form": {
      "goal_code": 6,
      "steps": [
        {
          "operator_code": 0,
          "source_refs": [
            {
              "binding_code": 1,
              "kind": "binding",
              "prior_output_name": "none",
              "prior_step_index": -1
            }
          ]
        },
        {
          "operator_code": 3,
          "source_refs": [
            {
              "binding_code": -1,
              "kind": "prior_output",
              "prior_output_name": "patient",
              "prior_step_index": 0
            },
            {
              "binding_code": 2,
              "kind": "binding",
              "prior_output_name": "none",
              "prior_step_index": -1
            }
          ]
        },
        {
          "operator_code": 13,
          "source_refs": []
        }
      ],
      "version_code": 3
    },
    "operator_note_excluded": true,
    "program_hash": "sha256:1e986eea5506a873814972ae93f4b8e00bd0b7e27d36fd5fb9ccd5e40bf00841",
    "raw_provider_response": false
  }
}
```

## 23. b-clarify-details

```json
{
  "actual_provider_calls": 1,
  "admitted_operator_ids": [
    "request_clarification"
  ],
  "case_code": "b-clarify-details",
  "cleanup_passed": true,
  "context_frame_review": {
    "command_authority": false,
    "desk_context_sha256": "sha256:c53142facbbc7a1ffb0a6a3747b4f314ffa9197615cbc21275cd002d2533f1f6",
    "disposition": "admit",
    "reviewed_context_revision": 62,
    "same_packet_seen_by_model_and_proofreader": true,
    "source_labels": [
      "fixture_intercepted",
      "staff_selected",
      "staff_selected"
    ],
    "task_sha256": "sha256:c6c54c3142349cc1bdc1ba6ff023b4527bb6123fbac0d9dfe32c17ed9e9d269b"
  },
  "correction_used": false,
  "exact_binding": {
    "api_key_authentication_used": false,
    "authentication": "keyless_impersonated_service_account_adc",
    "endpoint_hostname": "australia-southeast1-aiplatform.googleapis.com",
    "location": "australia-southeast1",
    "model_id": "gemini-2.5-flash",
    "project": "bernie-emr4-dev",
    "provider": "google_vertex_ai",
    "service_account": "emr4-bernie-ai-dev@bernie-emr4-dev.iam.gserviceaccount.com"
  },
  "expected_goal": "clarification",
  "expected_proposal_family": "clarification",
  "expected_proposal_release": false,
  "expected_safe_outcome": true,
  "final_proofreader_disposition": "admit",
  "final_violation_codes": [],
  "operator_note": {
    "audit_only": true,
    "disposition": "admit",
    "note_sha256": "sha256:b88826fbc344d4f64bdd9540a8d17ae862fbae146fe8bd48673775bc836cbfed",
    "operator_note": "Clarification requested; no booking was changed.",
    "parsed_into_plan": false,
    "product_delivered": false,
    "reason_codes": [],
    "retained_utf8_bytes": 48
  },
  "parent_audit_chain": {
    "event_count": 4,
    "terminal_hash": "sha256:fb07901d7fa6f8d87e9edcc21b8bb38f14f3533bc2c1aefdfd0d3f47e9bc1d89",
    "valid": true
  },
  "primary_exact_body_accepted": true,
  "primary_proofreader_disposition": "admit",
  "primary_violation_codes": [],
  "provider_outcomes": [
    {
      "bounded_completion_metadata": {
        "candidate_count": 1,
        "candidate_count_truncated": false,
        "finish_reasons": [
          "STOP"
        ],
        "part_counts": [
          1
        ],
        "provider_text_inspected_for_diagnosis": false,
        "provider_text_retained": false
      },
      "bounded_error": null,
      "http_status": 200,
      "latency_ms": 5079,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 157,
        "promptTokenCount": 3710,
        "thoughtsTokenCount": 939,
        "totalTokenCount": 4806
      }
    }
  ],
  "receptionist_output": {
    "decision_note": "Intent clarification: Missing explicit action verb for the described appointment.",
    "disposition": "admit",
    "evidence_utterance_indices": [
      0
    ],
    "hidden_reasoning": false,
    "natural_response_parsed_into_form": false,
    "product_delivered": false,
    "raw_provider_response": false,
    "receptionist_response": "I understand you're providing details for an appointment. Could you please clarify if you'd like to book a new appointment, or if this is for an existing one?",
    "violations": []
  },
  "release": {
    "api_spine_operation_id": null,
    "appointment_ref": null,
    "candidate_slot_ids": [],
    "duration_minutes": null,
    "kind": "clarification",
    "patient_ref": null,
    "practitioner_ref": null,
    "proposal_family": "clarification",
    "requires_human_confirmation": false,
    "status": null,
    "warning_codes": [],
    "write_performed": false
  },
  "source_case_id": null,
  "terminal_second_call_reason": null,
  "terminal_status": "admitted",
  "typed_program": {
    "explicit_source_form": {
      "goal_code": 6,
      "steps": [
        {
          "operator_code": 13,
          "source_refs": []
        }
      ],
      "version_code": 3
    },
    "operator_note_excluded": true,
    "program_hash": "sha256:45c136df060094e299f214560952d073c74c98e8102fd239a7e85befdb3c5f5e",
    "raw_provider_response": false
  }
}
```

## 24. b-clarify-fit

```json
{
  "actual_provider_calls": 1,
  "admitted_operator_ids": [
    "request_clarification"
  ],
  "case_code": "b-clarify-fit",
  "cleanup_passed": true,
  "context_frame_review": {
    "command_authority": false,
    "desk_context_sha256": "sha256:962266b62ccd2c1b52667b17424171606dd93d41b09708a85b92f2ebe64e6117",
    "disposition": "admit",
    "reviewed_context_revision": 62,
    "same_packet_seen_by_model_and_proofreader": true,
    "source_labels": [
      "fixture_intercepted",
      "staff_selected",
      "staff_selected"
    ],
    "task_sha256": "sha256:7bfe9d762cf283b8eced8047d23711747aa678d69bc542de45fe9f0dfeda7927"
  },
  "correction_used": false,
  "exact_binding": {
    "api_key_authentication_used": false,
    "authentication": "keyless_impersonated_service_account_adc",
    "endpoint_hostname": "australia-southeast1-aiplatform.googleapis.com",
    "location": "australia-southeast1",
    "model_id": "gemini-2.5-flash",
    "project": "bernie-emr4-dev",
    "provider": "google_vertex_ai",
    "service_account": "emr4-bernie-ai-dev@bernie-emr4-dev.iam.gserviceaccount.com"
  },
  "expected_goal": "clarification",
  "expected_proposal_family": "clarification",
  "expected_proposal_release": false,
  "expected_safe_outcome": true,
  "final_proofreader_disposition": "admit",
  "final_violation_codes": [],
  "operator_note": {
    "audit_only": true,
    "disposition": "admit",
    "note_sha256": "sha256:b88826fbc344d4f64bdd9540a8d17ae862fbae146fe8bd48673775bc836cbfed",
    "operator_note": "Clarification requested; no booking was changed.",
    "parsed_into_plan": false,
    "product_delivered": false,
    "reason_codes": [],
    "retained_utf8_bytes": 48
  },
  "parent_audit_chain": {
    "event_count": 4,
    "terminal_hash": "sha256:5d7cdcbf1e28cf7b8d888cf7ae47873e09a4b017571c25e20d57843442bef51a",
    "valid": true
  },
  "primary_exact_body_accepted": true,
  "primary_proofreader_disposition": "admit",
  "primary_violation_codes": [],
  "provider_outcomes": [
    {
      "bounded_completion_metadata": {
        "candidate_count": 1,
        "candidate_count_truncated": false,
        "finish_reasons": [
          "STOP"
        ],
        "part_counts": [
          1
        ],
        "provider_text_inspected_for_diagnosis": false,
        "provider_text_retained": false
      },
      "bounded_error": null,
      "http_status": 200,
      "latency_ms": 2325,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 162,
        "promptTokenCount": 3721,
        "thoughtsTokenCount": 230,
        "totalTokenCount": 4113
      }
    }
  ],
  "receptionist_output": {
    "decision_note": "Intent clarification: The phrase \"fit in\" requires clarification on whether it's a regular booking or a squeeze-in.",
    "disposition": "admit",
    "evidence_utterance_indices": [
      0
    ],
    "hidden_reasoning": false,
    "natural_response_parsed_into_form": false,
    "product_delivered": false,
    "raw_provider_response": false,
    "receptionist_response": "I need to clarify if you'd like to book a regular appointment or if you're asking for a squeeze-in appointment.",
    "violations": []
  },
  "release": {
    "api_spine_operation_id": null,
    "appointment_ref": null,
    "candidate_slot_ids": [],
    "duration_minutes": null,
    "kind": "clarification",
    "patient_ref": null,
    "practitioner_ref": null,
    "proposal_family": "clarification",
    "requires_human_confirmation": false,
    "status": null,
    "warning_codes": [],
    "write_performed": false
  },
  "source_case_id": null,
  "terminal_second_call_reason": null,
  "terminal_status": "admitted",
  "typed_program": {
    "explicit_source_form": {
      "goal_code": 6,
      "steps": [
        {
          "operator_code": 13,
          "source_refs": []
        }
      ],
      "version_code": 3
    },
    "operator_note_excluded": true,
    "program_hash": "sha256:45c136df060094e299f214560952d073c74c98e8102fd239a7e85befdb3c5f5e",
    "raw_provider_response": false
  }
}
```
