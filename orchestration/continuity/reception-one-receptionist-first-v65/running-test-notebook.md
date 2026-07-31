# Reception One v6.5 Full-Cohort Test Notebook

Status: complete
Cases closed: 24 / 24
Provider calls consumed: 28 / 48

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
    "note_sha256": "sha256:8e29ae1d1471b111e6a2c2befc54feb4292764830feb09811635ae6c66bb53d0",
    "operator_note": "Proposal for review; no booking was changed.",
    "parsed_into_plan": false,
    "product_delivered": false,
    "reason_codes": [],
    "retained_utf8_bytes": 44
  },
  "parent_audit_chain": {
    "event_count": 4,
    "terminal_hash": "sha256:d4efcab5d60a66192db4faf7813a7cedeae904dfb8f8652b745d79ba36a0840e",
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
      "latency_ms": 6455,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 852,
        "promptTokenCount": 4400,
        "thoughtsTokenCount": 744,
        "totalTokenCount": 5996
      }
    }
  ],
  "receptionist_output": {
    "decision_note": "Intent create: User requested to arrange a new appointment.",
    "disposition": "admit",
    "evidence_utterance_indices": [
      0
    ],
    "hidden_reasoning": false,
    "natural_response_parsed_into_form": false,
    "product_delivered": false,
    "raw_provider_response": false,
    "receptionist_response": "I am preparing a proposal for a new appointment for Margaret Thompson with Dr Shera tomorrow at 2:30 pm for 15 minutes for your review.",
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

## 2. b-create-alias

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
  "case_code": "b-create-alias",
  "cleanup_passed": true,
  "context_frame_review": {
    "command_authority": false,
    "desk_context_sha256": "sha256:ba08144d5519f4ffb55d0d745e10ce177abe2eb2d9978be26bede5e6a0d3bdd8",
    "disposition": "admit",
    "reviewed_context_revision": 62,
    "same_packet_seen_by_model_and_proofreader": true,
    "source_labels": [
      "fixture_intercepted",
      "staff_selected",
      "staff_selected"
    ],
    "task_sha256": "sha256:c84a20c4cbb40ccd96405c8cc6f7924b49bdd13cc76a0f989785513a3958b3dc"
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
    "note_sha256": "sha256:56f450f88ac68427f96a395386a17eaba72c0fff2766d60921aa417cec0119b0",
    "operator_note": "Proposal for review. No booking was changed.",
    "parsed_into_plan": false,
    "product_delivered": false,
    "reason_codes": [],
    "retained_utf8_bytes": 44
  },
  "parent_audit_chain": {
    "event_count": 4,
    "terminal_hash": "sha256:f16d0e81c4df514861e7c2d124007b825eba3af02b70b726f979d03bcada1f08",
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
      "latency_ms": 6778,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 855,
        "promptTokenCount": 4377,
        "thoughtsTokenCount": 909,
        "totalTokenCount": 6141
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
    "receptionist_response": "I am preparing a proposal to book an appointment for Margaret with Dr Shera tomorrow at 3 pm for 15 minutes for your review. No booking was changed.",
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
    "program_hash": "sha256:ac499694f9dd096ee6ff89999c0f5cd46e84583236260ea3b14cf27ffc918232",
    "raw_provider_response": false
  }
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
    "note_sha256": "sha256:56f450f88ac68427f96a395386a17eaba72c0fff2766d60921aa417cec0119b0",
    "operator_note": "Proposal for review. No booking was changed.",
    "parsed_into_plan": false,
    "product_delivered": false,
    "reason_codes": [],
    "retained_utf8_bytes": 44
  },
  "parent_audit_chain": {
    "event_count": 4,
    "terminal_hash": "sha256:f00a26bff405a952f5e34af308004aeae7982f267100fc7df71cb536646610ab",
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
      "latency_ms": 6832,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 860,
        "promptTokenCount": 4435,
        "thoughtsTokenCount": 990,
        "totalTokenCount": 6285
      }
    }
  ],
  "receptionist_output": {
    "decision_note": "Intent create: The staff member explicitly requested to schedule an appointment with all necessary details.",
    "disposition": "admit",
    "evidence_utterance_indices": [
      1
    ],
    "hidden_reasoning": false,
    "natural_response_parsed_into_form": false,
    "product_delivered": false,
    "raw_provider_response": false,
    "receptionist_response": "I am preparing a proposal to schedule an appointment for Margaret Thompson with Dr Shera tomorrow at 2:30 pm for 15 minutes. No booking was changed.",
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
    "program_hash": "sha256:ac499694f9dd096ee6ff89999c0f5cd46e84583236260ea3b14cf27ffc918232",
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
    "note_sha256": "sha256:56f450f88ac68427f96a395386a17eaba72c0fff2766d60921aa417cec0119b0",
    "operator_note": "Proposal for review. No booking was changed.",
    "parsed_into_plan": false,
    "product_delivered": false,
    "reason_codes": [],
    "retained_utf8_bytes": 44
  },
  "parent_audit_chain": {
    "event_count": 4,
    "terminal_hash": "sha256:035af3c3e2c9972d2a8857e5fc3bed2b805bb4800fe0edf4eb92a6242d4a9e1e",
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
      "latency_ms": 7609,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 871,
        "promptTokenCount": 4430,
        "thoughtsTokenCount": 978,
        "totalTokenCount": 6279
      }
    }
  ],
  "receptionist_output": {
    "decision_note": "Intent create: The staff member requested to book an appointment and provided all necessary details, including a correction to the time.",
    "disposition": "admit",
    "evidence_utterance_indices": [
      0,
      1
    ],
    "hidden_reasoning": false,
    "natural_response_parsed_into_form": false,
    "product_delivered": false,
    "raw_provider_response": false,
    "receptionist_response": "I am preparing a proposal to book an appointment for Margaret Thompson with Dr Shera tomorrow at 3:00 PM for 15 minutes. No booking was changed.",
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
    "program_hash": "sha256:ac499694f9dd096ee6ff89999c0f5cd46e84583236260ea3b14cf27ffc918232",
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
    "note_sha256": "sha256:d5f7f9ddae7a66d7394337f714ea470a4d3decdda0f53bfbf22fbe9ad803325e",
    "operator_note": "Proposal for review, no booking was changed.",
    "parsed_into_plan": false,
    "product_delivered": false,
    "reason_codes": [],
    "retained_utf8_bytes": 44
  },
  "parent_audit_chain": {
    "event_count": 4,
    "terminal_hash": "sha256:22f565bfac0e7a24aec9232f4e62406209fc2c9d559c8a75fa6ac2698ba68992",
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
      "latency_ms": 6615,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 804,
        "promptTokenCount": 4282,
        "thoughtsTokenCount": 866,
        "totalTokenCount": 5952
      }
    }
  ],
  "receptionist_output": {
    "decision_note": "Intent move: User explicitly requested to \"Reschedule\" an appointment.",
    "disposition": "admit",
    "evidence_utterance_indices": [
      0
    ],
    "hidden_reasoning": false,
    "natural_response_parsed_into_form": false,
    "product_delivered": false,
    "raw_provider_response": false,
    "receptionist_response": "I am preparing a proposal to reschedule Margaret Thompson's appointment to tomorrow at 3 pm for your review. No booking was changed.",
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

## 6. b-move-shift

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
    "terminal_hash": "sha256:fea9c75ef26f6d5530716e4f82849c2c1eba5027d7bdbb45a3cc2d44e7892bcc",
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
      "latency_ms": 6190,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 799,
        "promptTokenCount": 4285,
        "thoughtsTokenCount": 766,
        "totalTokenCount": 5850
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
      "latency_ms": 6945,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 811,
        "promptTokenCount": 4817,
        "thoughtsTokenCount": 1026,
        "totalTokenCount": 6654
      }
    }
  ],
  "receptionist_output": {
    "decision_note": "Intent move: The staff member explicitly requested to shift an appointment to a new date and time.",
    "disposition": "admit",
    "evidence_utterance_indices": [
      0
    ],
    "hidden_reasoning": false,
    "natural_response_parsed_into_form": false,
    "product_delivered": false,
    "raw_provider_response": false,
    "receptionist_response": "I am preparing a proposal to move Margaret's appointment to tomorrow at 2:30 PM for your review. No booking was changed.",
    "violations": []
  },
  "release": {
    "api_spine_operation_id": "proposeAppointmentUpdate",
    "appointment_ref": "synthetic-appointment-margaret",
    "candidate_slot_ids": [
      "synthetic-slot-july28-1430"
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

## 7. b-move-change

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
    "note_sha256": "sha256:56f450f88ac68427f96a395386a17eaba72c0fff2766d60921aa417cec0119b0",
    "operator_note": "Proposal for review. No booking was changed.",
    "parsed_into_plan": false,
    "product_delivered": false,
    "reason_codes": [],
    "retained_utf8_bytes": 44
  },
  "parent_audit_chain": {
    "event_count": 4,
    "terminal_hash": "sha256:8d83b9cdc82e18e680f12c48f49aebc6760eafcea357f1deb7ca72958ff512c3",
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
      "latency_ms": 6741,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 804,
        "promptTokenCount": 4282,
        "thoughtsTokenCount": 863,
        "totalTokenCount": 5949
      }
    }
  ],
  "receptionist_output": {
    "decision_note": "Intent move: User explicitly requested to change the time of an appointment.",
    "disposition": "admit",
    "evidence_utterance_indices": [
      0
    ],
    "hidden_reasoning": false,
    "natural_response_parsed_into_form": false,
    "product_delivered": false,
    "raw_provider_response": false,
    "receptionist_response": "I am preparing a proposal to move Margaret Thompson's appointment to tomorrow at 3 PM for your review. No booking was changed.",
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
    "program_hash": "sha256:78491192bc58958715c9db12e227f3fd7ceeab99577031c920ccce5ed651cd13",
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
    "terminal_hash": "sha256:993447b7e08d75977a691d34912b6032f83e93f433b6b7a9b506138950008d18",
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
      "latency_ms": 6124,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 815,
        "promptTokenCount": 4327,
        "thoughtsTokenCount": 735,
        "totalTokenCount": 5877
      }
    }
  ],
  "receptionist_output": {
    "decision_note": "Intent move: The staff member explicitly requested to move an appointment and then corrected the time.",
    "disposition": "admit",
    "evidence_utterance_indices": [
      0,
      1
    ],
    "hidden_reasoning": false,
    "natural_response_parsed_into_form": false,
    "product_delivered": false,
    "raw_provider_response": false,
    "receptionist_response": "I am preparing a proposal to move Margaret Thompson's appointment to tomorrow at 3:00 PM for your review. No booking was changed.",
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
    "resolve_patient_reference",
    "read_selected_appointment",
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
    "note_sha256": "sha256:56f450f88ac68427f96a395386a17eaba72c0fff2766d60921aa417cec0119b0",
    "operator_note": "Proposal for review. No booking was changed.",
    "parsed_into_plan": false,
    "product_delivered": false,
    "reason_codes": [],
    "retained_utf8_bytes": 44
  },
  "parent_audit_chain": {
    "event_count": 4,
    "terminal_hash": "sha256:59ebd0138ee5c92017bc8b74cb7be707163494e523832507462cbf2fe11dc7ae",
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
      "latency_ms": 4042,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 450,
        "promptTokenCount": 4243,
        "thoughtsTokenCount": 486,
        "totalTokenCount": 5179
      }
    }
  ],
  "receptionist_output": {
    "decision_note": "Intent resize: The staff requested to make an appointment longer with a specified duration.",
    "disposition": "admit",
    "evidence_utterance_indices": [
      0
    ],
    "hidden_reasoning": false,
    "natural_response_parsed_into_form": false,
    "product_delivered": false,
    "raw_provider_response": false,
    "receptionist_response": "I'm preparing a proposal to make Margaret Thompson's appointment longer by 30 minutes for your review.",
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
          "operator_code": 0,
          "source_refs": [
            {
              "binding_code": 2,
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
              "binding_code": 3,
              "kind": "binding",
              "prior_output_name": "none",
              "prior_step_index": -1
            }
          ]
        },
        {
          "operator_code": 10,
          "source_refs": [
            {
              "binding_code": -1,
              "kind": "prior_output",
              "prior_output_name": "appointment",
              "prior_step_index": 1
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
    "program_hash": "sha256:6cd9453c8a71a5af3b930017e03ee94e865694b301c6360c00042538d21fb8f9",
    "raw_provider_response": false
  }
}
```

## 10. b-resize-short

```json
{
  "actual_provider_calls": 1,
  "admitted_operator_ids": [
    "resolve_patient_reference",
    "read_selected_appointment",
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
    "terminal_hash": "sha256:de77106a23c89b2ec5073e65b7a6a099036ba6b6c96b1116b3cc01b7b31d343a",
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
      "latency_ms": 4320,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 318,
        "promptTokenCount": 4231,
        "thoughtsTokenCount": 676,
        "totalTokenCount": 5225
      }
    }
  ],
  "receptionist_output": {
    "decision_note": "Intent resize: The staff member requested to shorten an existing appointment to a new duration.",
    "disposition": "admit",
    "evidence_utterance_indices": [
      0
    ],
    "hidden_reasoning": false,
    "natural_response_parsed_into_form": false,
    "product_delivered": false,
    "raw_provider_response": false,
    "receptionist_response": "I'm preparing a proposal to shorten Margaret's appointment to 10 minutes for your review. No booking was changed.",
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
          "operator_code": 0,
          "source_refs": [
            {
              "binding_code": 2,
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
              "binding_code": 3,
              "kind": "binding",
              "prior_output_name": "none",
              "prior_step_index": -1
            }
          ]
        },
        {
          "operator_code": 10,
          "source_refs": [
            {
              "binding_code": -1,
              "kind": "prior_output",
              "prior_output_name": "appointment",
              "prior_step_index": 1
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
    "program_hash": "sha256:ff26289d7d6701443f94a2ad23c148081c52a180d9f141a70a172e217332b9c0",
    "raw_provider_response": false
  }
}
```

## 11. b-resize-give

```json
{
  "actual_provider_calls": 1,
  "admitted_operator_ids": [
    "resolve_patient_reference",
    "read_selected_appointment",
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
    "terminal_hash": "sha256:9cf30e426f1d092f06a91f94089c3c3d8eae497147cd8896ea3c6c5fb019efb2",
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
      "latency_ms": 4586,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 449,
        "promptTokenCount": 4233,
        "thoughtsTokenCount": 614,
        "totalTokenCount": 5296
      }
    }
  ],
  "receptionist_output": {
    "decision_note": "Intent resize: Staff requested a specific duration for a selected appointment.",
    "disposition": "admit",
    "evidence_utterance_indices": [
      0
    ],
    "hidden_reasoning": false,
    "natural_response_parsed_into_form": false,
    "product_delivered": false,
    "raw_provider_response": false,
    "receptionist_response": "I'm preparing a proposal to change the duration of Margaret Thompson's appointment to 30 minutes for your review.",
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
          "operator_code": 0,
          "source_refs": [
            {
              "binding_code": 2,
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
              "binding_code": 3,
              "kind": "binding",
              "prior_output_name": "none",
              "prior_step_index": -1
            }
          ]
        },
        {
          "operator_code": 10,
          "source_refs": [
            {
              "binding_code": -1,
              "kind": "prior_output",
              "prior_output_name": "appointment",
              "prior_step_index": 1
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
    "program_hash": "sha256:ff26289d7d6701443f94a2ad23c148081c52a180d9f141a70a172e217332b9c0",
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
    "terminal_hash": "sha256:02ddd44d03189ede64ae98db68de9c7412e9f1a62bc9c27fb667fe741266de40",
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
      "latency_ms": 4300,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 244,
        "promptTokenCount": 4238,
        "thoughtsTokenCount": 653,
        "totalTokenCount": 5135
      }
    }
  ],
  "receptionist_output": {
    "decision_note": "Intent resize: Staff requested to resize an appointment to a specific duration.",
    "disposition": "admit",
    "evidence_utterance_indices": [
      0
    ],
    "hidden_reasoning": false,
    "natural_response_parsed_into_form": false,
    "product_delivered": false,
    "raw_provider_response": false,
    "receptionist_response": "I am preparing a proposal to resize Margaret Thompson's booking to 30 minutes for your review.",
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
    "note_sha256": "sha256:56f450f88ac68427f96a395386a17eaba72c0fff2766d60921aa417cec0119b0",
    "operator_note": "Proposal for review. No booking was changed.",
    "parsed_into_plan": false,
    "product_delivered": false,
    "reason_codes": [],
    "retained_utf8_bytes": 44
  },
  "parent_audit_chain": {
    "event_count": 4,
    "terminal_hash": "sha256:6ff775da8ac64f66bb5ff8e3ed3e299a8adbc3aae20bf94d685646f0a3d17a89",
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
      "latency_ms": 4419,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 191,
        "promptTokenCount": 4214,
        "thoughtsTokenCount": 738,
        "totalTokenCount": 5143
      }
    }
  ],
  "receptionist_output": {
    "decision_note": "Intent cancel: The staff member requested to remove an appointment.",
    "disposition": "admit",
    "evidence_utterance_indices": [
      0
    ],
    "hidden_reasoning": false,
    "natural_response_parsed_into_form": false,
    "product_delivered": false,
    "raw_provider_response": false,
    "receptionist_response": "I am preparing a proposal to cancel Margaret Thompson's appointment. No booking was changed.",
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
    "program_hash": "sha256:e107ac4ce1ee065e8cf747fccd46d4395d4f6f152196f1a928e566a05f7e3016",
    "raw_provider_response": false
  }
}
```

## 14. b-cancel-calloff

```json
{
  "actual_provider_calls": 1,
  "admitted_operator_ids": [
    "resolve_patient_reference",
    "read_selected_appointment",
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
    "note_sha256": "sha256:56f450f88ac68427f96a395386a17eaba72c0fff2766d60921aa417cec0119b0",
    "operator_note": "Proposal for review. No booking was changed.",
    "parsed_into_plan": false,
    "product_delivered": false,
    "reason_codes": [],
    "retained_utf8_bytes": 44
  },
  "parent_audit_chain": {
    "event_count": 4,
    "terminal_hash": "sha256:800e6e8c864496e897b505faebace57e8eda0851f185cd51e09b729dd74ac57f",
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
      "latency_ms": 4369,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 397,
        "promptTokenCount": 4207,
        "thoughtsTokenCount": 586,
        "totalTokenCount": 5190
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
    "receptionist_response": "I am preparing a proposal to cancel Margaret's appointment for your review. No booking was changed.",
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
          "operator_code": 11,
          "source_refs": [
            {
              "binding_code": -1,
              "kind": "prior_output",
              "prior_output_name": "appointment",
              "prior_step_index": 1
            }
          ]
        }
      ],
      "version_code": 3
    },
    "operator_note_excluded": true,
    "program_hash": "sha256:058496eb0ca32c34173eeb318adecd8866a573243c10e58e58f8ccb0b4625622",
    "raw_provider_response": false
  }
}
```

## 15. b-cancel-takeout

```json
{
  "actual_provider_calls": 1,
  "admitted_operator_ids": [
    "resolve_patient_reference",
    "read_selected_appointment",
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
    "note_sha256": "sha256:56f450f88ac68427f96a395386a17eaba72c0fff2766d60921aa417cec0119b0",
    "operator_note": "Proposal for review. No booking was changed.",
    "parsed_into_plan": false,
    "product_delivered": false,
    "reason_codes": [],
    "retained_utf8_bytes": 44
  },
  "parent_audit_chain": {
    "event_count": 4,
    "terminal_hash": "sha256:df354b9711a739138dea3bf90054ff7b67eb4c725082ed21eb2b79d4fd7f7b97",
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
      "latency_ms": 3919,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 398,
        "promptTokenCount": 4208,
        "thoughtsTokenCount": 262,
        "totalTokenCount": 4868
      }
    }
  ],
  "receptionist_output": {
    "decision_note": "Intent cancel: Staff requested to 'Take ... out' an appointment.",
    "disposition": "admit",
    "evidence_utterance_indices": [
      0
    ],
    "hidden_reasoning": false,
    "natural_response_parsed_into_form": false,
    "product_delivered": false,
    "raw_provider_response": false,
    "receptionist_response": "I'm preparing a proposal to cancel Margaret Thompson's appointment. This will be sent for review.",
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
          "operator_code": 11,
          "source_refs": [
            {
              "binding_code": -1,
              "kind": "prior_output",
              "prior_output_name": "appointment",
              "prior_step_index": 1
            }
          ]
        }
      ],
      "version_code": 3
    },
    "operator_note_excluded": true,
    "program_hash": "sha256:058496eb0ca32c34173eeb318adecd8866a573243c10e58e58f8ccb0b4625622",
    "raw_provider_response": false
  }
}
```

## 16. b-status-complete

```json
{
  "actual_provider_calls": 1,
  "admitted_operator_ids": [
    "resolve_patient_reference",
    "read_selected_appointment",
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
    "note_sha256": "sha256:3f83253b417af31898d9a15ad784e50775677b3e9c94bda6f00f689a3df630c3",
    "operator_note": "Proposal for status change is being prepared for review; no booking was changed.",
    "parsed_into_plan": false,
    "product_delivered": false,
    "reason_codes": [],
    "retained_utf8_bytes": 80
  },
  "parent_audit_chain": {
    "event_count": 4,
    "terminal_hash": "sha256:2621cabe5a7e23d9953efaf3300dd8d7b863b32252202ae9ed1a4a3a0583eed4",
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
      "latency_ms": 3479,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 457,
        "promptTokenCount": 4232,
        "thoughtsTokenCount": 335,
        "totalTokenCount": 5024
      }
    }
  ],
  "receptionist_output": {
    "decision_note": "Intent status_change: Staff explicitly requested to set the appointment status to 'completed'.",
    "disposition": "admit",
    "evidence_utterance_indices": [
      0
    ],
    "hidden_reasoning": false,
    "natural_response_parsed_into_form": false,
    "product_delivered": false,
    "raw_provider_response": false,
    "receptionist_response": "I'm preparing a proposal to change the status of Margaret Thompson's appointment to completed for your review.",
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
          "operator_code": 12,
          "source_refs": [
            {
              "binding_code": -1,
              "kind": "prior_output",
              "prior_output_name": "appointment",
              "prior_step_index": 1
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
    "program_hash": "sha256:ae59b0f170092c5cdd0fb2e997e64917e32fc0d1cc66edc07ed02f40db22443c",
    "raw_provider_response": false
  }
}
```

## 17. b-status-arrived

```json
{
  "actual_provider_calls": 1,
  "admitted_operator_ids": [
    "resolve_patient_reference",
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
    "note_sha256": "sha256:02325560bc190e18381fb9105293df84a32302d39f4d8de818e57e759b526b8b",
    "operator_note": "Proposal for status change is being prepared for review. No booking was changed.",
    "parsed_into_plan": false,
    "product_delivered": false,
    "reason_codes": [],
    "retained_utf8_bytes": 80
  },
  "parent_audit_chain": {
    "event_count": 4,
    "terminal_hash": "sha256:c368e4b3a74ccf49edcd42d7beebd2a9295b1058e2d0bf65dc0f6601fc38edd6",
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
      "latency_ms": 6161,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 333,
        "promptTokenCount": 4236,
        "thoughtsTokenCount": 1066,
        "totalTokenCount": 5635
      }
    }
  ],
  "receptionist_output": {
    "decision_note": "Intent status_change: The staff member explicitly requested a status update for a selected appointment.",
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
    "program_hash": "sha256:375a4e8e91eb8b12b7c82f2be04db67f4630268cf03955ffd64b96dffdd41b07",
    "raw_provider_response": false
  }
}
```

## 18. b-status-noshow-gap

```json
{
  "actual_provider_calls": 1,
  "admitted_operator_ids": [
    "request_clarification"
  ],
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
    "terminal_hash": "sha256:5a326c785e2d33adb5430ca793a66832491acde1e374bf599f027b2444568646",
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
      "latency_ms": 5323,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 149,
        "promptTokenCount": 4213,
        "thoughtsTokenCount": 910,
        "totalTokenCount": 5272
      }
    }
  ],
  "receptionist_output": {
    "decision_note": "Intent clarification: Missing meaning for status.",
    "disposition": "admit",
    "evidence_utterance_indices": [
      0
    ],
    "hidden_reasoning": false,
    "natural_response_parsed_into_form": false,
    "product_delivered": false,
    "raw_provider_response": false,
    "receptionist_response": "I can prepare to mark Margaret's appointment, but could you please clarify which specific status 'no-show' refers to? No booking was changed.",
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

## 19. b-squeeze-without

```json
{
  "actual_provider_calls": 2,
  "admitted_operator_ids": [],
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
  "expected_goal": "squeeze_in_assessment",
  "expected_proposal_family": "squeeze_in_assessment",
  "expected_proposal_release": true,
  "expected_safe_outcome": false,
  "final_proofreader_disposition": "edge_abort",
  "final_violation_codes": [
    "decision_note_identifier"
  ],
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
    "terminal_hash": "sha256:16949dab5e13016d9d43da8e4bade15a205ec0a4af64e0e1b717850e65d7a572",
    "valid": true
  },
  "primary_exact_body_accepted": true,
  "primary_proofreader_disposition": "revision_required",
  "primary_violation_codes": [
    "decision_note_identifier"
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
      "latency_ms": 7162,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 712,
        "promptTokenCount": 4343,
        "thoughtsTokenCount": 976,
        "totalTokenCount": 6031
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
      "latency_ms": 6512,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 704,
        "promptTokenCount": 4804,
        "thoughtsTokenCount": 912,
        "totalTokenCount": 6420
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
        "code": "decision_note_identifier",
        "path": "$.decision_note"
      }
    ]
  },
  "release": null,
  "source_case_id": null,
  "terminal_second_call_reason": "proofreader_correction",
  "terminal_status": "terminal_no_release",
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
    "program_hash": "sha256:3496f0f50766c32faf2f7b494b13d5cdea74add41a8a8bf8389c8b040c76da01",
    "raw_provider_response": false
  }
}
```

## 20. b-squeeze-negated-move

```json
{
  "actual_provider_calls": 2,
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
  "expected_goal": "squeeze_in_assessment",
  "expected_proposal_family": "squeeze_in_assessment",
  "expected_proposal_release": true,
  "expected_safe_outcome": true,
  "final_proofreader_disposition": "admit",
  "final_violation_codes": [],
  "operator_note": {
    "audit_only": true,
    "disposition": "admit",
    "note_sha256": "sha256:56f450f88ac68427f96a395386a17eaba72c0fff2766d60921aa417cec0119b0",
    "operator_note": "Proposal for review. No booking was changed.",
    "parsed_into_plan": false,
    "product_delivered": false,
    "reason_codes": [],
    "retained_utf8_bytes": 44
  },
  "parent_audit_chain": {
    "event_count": 6,
    "terminal_hash": "sha256:d5382c3e7190c997f9719577b95faa912ad45a925989aeb96368c1fbf047e35e",
    "valid": true
  },
  "primary_exact_body_accepted": true,
  "primary_proofreader_disposition": "revision_required",
  "primary_violation_codes": [
    "decision_note_identifier"
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
      "latency_ms": 5247,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 735,
        "promptTokenCount": 4347,
        "thoughtsTokenCount": 523,
        "totalTokenCount": 5605
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
      "latency_ms": 6471,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 711,
        "promptTokenCount": 4811,
        "thoughtsTokenCount": 891,
        "totalTokenCount": 6413
      }
    }
  ],
  "receptionist_output": {
    "decision_note": "Intent squeeze_in_assessment: The staff member explicitly requested to 'squeeze in' an appointment.",
    "disposition": "admit",
    "evidence_utterance_indices": [
      0
    ],
    "hidden_reasoning": false,
    "natural_response_parsed_into_form": false,
    "product_delivered": false,
    "raw_provider_response": false,
    "receptionist_response": "I am preparing a proposal to assess squeeze-in options for Margaret Thompson with Dr Shera today for 15 minutes. No booking was changed.",
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
  "terminal_second_call_reason": "proofreader_correction",
  "terminal_status": "admitted_after_correction",
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
    "program_hash": "sha256:2ec82ef03d03a36895cd4f8b97ec24d7a5f1c93736a6cee1521c225f0815cf63",
    "raw_provider_response": false
  }
}
```

## 21. b-clarify-sort

```json
{
  "actual_provider_calls": 1,
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
    "terminal_hash": "sha256:9a9be73acdaddeda198fcefb2aac6d922708b16033a3116b90a507c9a42f9d90",
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
      "latency_ms": 3331,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 151,
        "promptTokenCount": 4218,
        "thoughtsTokenCount": 417,
        "totalTokenCount": 4786
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
    "receptionist_response": "I can help with Margaret Thompson's appointment. Could you please clarify what you would like to do with it?",
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

## 22. b-clarify-different

```json
{
  "actual_provider_calls": 1,
  "admitted_operator_ids": [
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
    "terminal_hash": "sha256:0a31f0f53c0afecf5a213841a520fa05871330106ca88050524f6912eaead7ef",
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
      "latency_ms": 4927,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 150,
        "promptTokenCount": 4206,
        "thoughtsTokenCount": 830,
        "totalTokenCount": 5186
      }
    }
  ],
  "receptionist_output": {
    "decision_note": "Intent clarification: Missing target date and time for the appointment.",
    "disposition": "admit",
    "evidence_utterance_indices": [
      0
    ],
    "hidden_reasoning": false,
    "natural_response_parsed_into_form": false,
    "product_delivered": false,
    "raw_provider_response": false,
    "receptionist_response": "I understand Margaret Thompson needs a different appointment. Could you please tell me the new date and time you would like to move her appointment to?",
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
    "terminal_hash": "sha256:f12dba0a5960bf77d6d791d23325fd4afe9a803734a1060e49d14c744a21f668",
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
      "latency_ms": 4621,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 161,
        "promptTokenCount": 4382,
        "thoughtsTokenCount": 790,
        "totalTokenCount": 5333
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
    "receptionist_response": "I have the details for Margaret Thompson's appointment with Dr Shera tomorrow at 2:30 pm for 15 minutes. What would you like me to do with this information?",
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
  "actual_provider_calls": 2,
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
    "note_sha256": "sha256:b88826fbc344d4f64bdd9540a8d17ae862fbae146fe8bd48673775bc836cbfed",
    "operator_note": "Clarification requested; no booking was changed.",
    "parsed_into_plan": false,
    "product_delivered": false,
    "reason_codes": [],
    "retained_utf8_bytes": 48
  },
  "parent_audit_chain": {
    "event_count": 6,
    "terminal_hash": "sha256:6ed68f25f09c3fdc06785ba1d43cfb135c76b2c02460bb435ea65424cff6fda0",
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
      "latency_ms": 2296,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 173,
        "promptTokenCount": 4393,
        "thoughtsTokenCount": 157,
        "totalTokenCount": 4723
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
      "latency_ms": 4264,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 178,
        "promptTokenCount": 4574,
        "thoughtsTokenCount": 685,
        "totalTokenCount": 5437
      }
    }
  ],
  "receptionist_output": {
    "decision_note": "Intent clarification: The phrase 'fit in' is ambiguous regarding a standard booking or a squeeze-in.",
    "disposition": "admit",
    "evidence_utterance_indices": [
      0
    ],
    "hidden_reasoning": false,
    "natural_response_parsed_into_form": false,
    "product_delivered": false,
    "raw_provider_response": false,
    "receptionist_response": "I understand you'd like to schedule an appointment for Margaret Thompson with Dr Shera tomorrow. Could you please clarify if this is a standard booking or if you'd like to assess a squeeze-in? No booking was changed.",
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
    "program_hash": "sha256:45c136df060094e299f214560952d073c74c98e8102fd239a7e85befdb3c5f5e",
    "raw_provider_response": false
  }
}
```
