# Reception One v6.7 Full-Cohort Test Notebook

Status: complete
Cases closed: 24 / 24
Provider calls consumed: 25 / 48

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
    "terminal_hash": "sha256:cdc25a78c1992279a63f30d373da83b2d6c6c66d713607be15f7448c889395a3",
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
      "latency_ms": 5237,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 859,
        "promptTokenCount": 4696,
        "thoughtsTokenCount": 465,
        "totalTokenCount": 6020
      }
    }
  ],
  "receptionist_output": {
    "decision_note": "Intent create: all necessary information for a new appointment is present.",
    "disposition": "admit",
    "evidence_utterance_indices": [
      0
    ],
    "hidden_reasoning": false,
    "natural_response_parsed_into_form": false,
    "product_delivered": false,
    "raw_provider_response": false,
    "receptionist_response": "I am preparing a proposal to arrange an appointment for Margaret Thompson with Dr Shera tomorrow at 2:30 pm for 15 minutes for your review. No booking was changed.",
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
    "terminal_hash": "sha256:83b2fc20b01a651dfd1ad2cf982a1eb0d44008d2a17ef867e78072e93b5e061b",
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
      "latency_ms": 5868,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 854,
        "promptTokenCount": 4673,
        "thoughtsTokenCount": 548,
        "totalTokenCount": 6075
      }
    }
  ],
  "receptionist_output": {
    "decision_note": "Intent create: all necessary information for a new booking proposal is present.",
    "disposition": "admit",
    "evidence_utterance_indices": [
      0
    ],
    "hidden_reasoning": false,
    "natural_response_parsed_into_form": false,
    "product_delivered": false,
    "raw_provider_response": false,
    "receptionist_response": "I'm preparing a proposal to book Margaret with Dr Shera tomorrow at 3 pm for 15 minutes for your review. No booking was changed.",
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
    "note_sha256": "sha256:8e29ae1d1471b111e6a2c2befc54feb4292764830feb09811635ae6c66bb53d0",
    "operator_note": "Proposal for review; no booking was changed.",
    "parsed_into_plan": false,
    "product_delivered": false,
    "reason_codes": [],
    "retained_utf8_bytes": 44
  },
  "parent_audit_chain": {
    "event_count": 4,
    "terminal_hash": "sha256:a7a76725fa07b76ca412a8d6bce480ed9cb0b5932651d8ff8de36b51a8c75527",
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
      "latency_ms": 6904,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 864,
        "promptTokenCount": 4731,
        "thoughtsTokenCount": 906,
        "totalTokenCount": 6501
      }
    }
  ],
  "receptionist_output": {
    "decision_note": "Intent create: all necessary information for a create proposal was provided.",
    "disposition": "admit",
    "evidence_utterance_indices": [
      1
    ],
    "hidden_reasoning": false,
    "natural_response_parsed_into_form": false,
    "product_delivered": false,
    "raw_provider_response": false,
    "receptionist_response": "I'm preparing a proposal to schedule an appointment for Margaret Thompson with Dr Shera tomorrow at 2:30 PM for 15 minutes. This will be sent for review; no booking was changed.",
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
    "note_sha256": "sha256:56f450f88ac68427f96a395386a17eaba72c0fff2766d60921aa417cec0119b0",
    "operator_note": "Proposal for review. No booking was changed.",
    "parsed_into_plan": false,
    "product_delivered": false,
    "reason_codes": [],
    "retained_utf8_bytes": 44
  },
  "parent_audit_chain": {
    "event_count": 4,
    "terminal_hash": "sha256:5f5c27ea2632ffa53150bf3fddd96dfb00c560ddbd5f7ede1f066839fa59ba73",
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
      "latency_ms": 6758,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 865,
        "promptTokenCount": 4726,
        "thoughtsTokenCount": 920,
        "totalTokenCount": 6511
      }
    }
  ],
  "receptionist_output": {
    "decision_note": "Intent create: staff requested to book an appointment with a time correction.",
    "disposition": "admit",
    "evidence_utterance_indices": [
      0,
      1
    ],
    "hidden_reasoning": false,
    "natural_response_parsed_into_form": false,
    "product_delivered": false,
    "raw_provider_response": false,
    "receptionist_response": "I'm preparing a proposal to book an appointment for Margaret Thompson with Dr Shera tomorrow at 3:00 PM for 15 minutes for your review. No booking was changed.",
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
    "note_sha256": "sha256:d0bde6f469f2dc67f76be9f46670e7eb4b523d2294cad67b9ff0a57c8c7206df",
    "operator_note": "Proposal for review: no booking was changed.",
    "parsed_into_plan": false,
    "product_delivered": false,
    "reason_codes": [],
    "retained_utf8_bytes": 44
  },
  "parent_audit_chain": {
    "event_count": 4,
    "terminal_hash": "sha256:8fa458fc55b44671a5887ab3ddfc9e61a156915e2fc143223d8c939888fb2d48",
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
      "latency_ms": 5567,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 807,
        "promptTokenCount": 4578,
        "thoughtsTokenCount": 588,
        "totalTokenCount": 5973
      }
    }
  ],
  "receptionist_output": {
    "decision_note": "Intent move: staff requested to reschedule an appointment to a new date and time.",
    "disposition": "admit",
    "evidence_utterance_indices": [
      0
    ],
    "hidden_reasoning": false,
    "natural_response_parsed_into_form": false,
    "product_delivered": false,
    "raw_provider_response": false,
    "receptionist_response": "I'm preparing a proposal to move Margaret Thompson's appointment to tomorrow at 3 pm for your review. No booking was changed.",
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
    "receptionist_response_goal_mismatch"
  ],
  "operator_note": {
    "audit_only": true,
    "disposition": "admit",
    "note_sha256": "sha256:86f493c199dcfe330b6f28c75cc648d7cbc57071a6c14b82909ab7b874b2cb58",
    "operator_note": "Proposal for staff review; no booking was changed.",
    "parsed_into_plan": false,
    "product_delivered": false,
    "reason_codes": [],
    "retained_utf8_bytes": 50
  },
  "parent_audit_chain": {
    "event_count": 6,
    "terminal_hash": "sha256:23cc781b914425068f9d45200ac32f8b6e109bde143fc41bf622682aebebba84",
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
      "latency_ms": 6093,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 802,
        "promptTokenCount": 4581,
        "thoughtsTokenCount": 708,
        "totalTokenCount": 6091
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
      "latency_ms": 7159,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 802,
        "promptTokenCount": 5107,
        "thoughtsTokenCount": 1096,
        "totalTokenCount": 7005
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
    "program_hash": "sha256:c0eaee01dcf5eed4f1b36df678367636df5db3850ffc6a114d0c73c7a5157f10",
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
    "note_sha256": "sha256:d0bde6f469f2dc67f76be9f46670e7eb4b523d2294cad67b9ff0a57c8c7206df",
    "operator_note": "Proposal for review: no booking was changed.",
    "parsed_into_plan": false,
    "product_delivered": false,
    "reason_codes": [],
    "retained_utf8_bytes": 44
  },
  "parent_audit_chain": {
    "event_count": 4,
    "terminal_hash": "sha256:58ad37894bcf913c8becccd7b1e2bbca76ec92ad15aa197f351901950ebfde8a",
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
      "latency_ms": 5239,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 805,
        "promptTokenCount": 4578,
        "thoughtsTokenCount": 521,
        "totalTokenCount": 5904
      }
    }
  ],
  "receptionist_output": {
    "decision_note": "Intent move: staff requested to change the time of an existing appointment.",
    "disposition": "admit",
    "evidence_utterance_indices": [
      0
    ],
    "hidden_reasoning": false,
    "natural_response_parsed_into_form": false,
    "product_delivered": false,
    "raw_provider_response": false,
    "receptionist_response": "I'm preparing a proposal to move Margaret Thompson's appointment to tomorrow at 3 PM for your review. No booking was changed.",
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
    "note_sha256": "sha256:d0bde6f469f2dc67f76be9f46670e7eb4b523d2294cad67b9ff0a57c8c7206df",
    "operator_note": "Proposal for review: no booking was changed.",
    "parsed_into_plan": false,
    "product_delivered": false,
    "reason_codes": [],
    "retained_utf8_bytes": 44
  },
  "parent_audit_chain": {
    "event_count": 4,
    "terminal_hash": "sha256:9a3ce54b9f220662ac32b91c216a89ec9d9350c256826bc61b61f1542863e9ff",
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
      "latency_ms": 7048,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 802,
        "promptTokenCount": 4623,
        "thoughtsTokenCount": 845,
        "totalTokenCount": 6270
      }
    }
  ],
  "receptionist_output": {
    "decision_note": "Intent move: latest utterance corrects time for move.",
    "disposition": "admit",
    "evidence_utterance_indices": [
      0,
      1
    ],
    "hidden_reasoning": false,
    "natural_response_parsed_into_form": false,
    "product_delivered": false,
    "raw_provider_response": false,
    "receptionist_response": "I am preparing a proposal to move Margaret Thompson's appointment to tomorrow at 3:00 PM for your review.",
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
    "note_sha256": "sha256:8e29ae1d1471b111e6a2c2befc54feb4292764830feb09811635ae6c66bb53d0",
    "operator_note": "Proposal for review; no booking was changed.",
    "parsed_into_plan": false,
    "product_delivered": false,
    "reason_codes": [],
    "retained_utf8_bytes": 44
  },
  "parent_audit_chain": {
    "event_count": 4,
    "terminal_hash": "sha256:e6fc374a0b3b103e0ac5d2748694f1403dd5f2932a835cf9859f00f0b46c1a50",
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
      "latency_ms": 3913,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 444,
        "promptTokenCount": 4539,
        "thoughtsTokenCount": 405,
        "totalTokenCount": 5388
      }
    }
  ],
  "receptionist_output": {
    "decision_note": "Intent resize: staff requested to make an appointment longer.",
    "disposition": "admit",
    "evidence_utterance_indices": [
      0
    ],
    "hidden_reasoning": false,
    "natural_response_parsed_into_form": false,
    "product_delivered": false,
    "raw_provider_response": false,
    "receptionist_response": "I am preparing a proposal to make Margaret Thompson's appointment longer by 30 minutes for your review.",
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
    "terminal_hash": "sha256:355b0c74508eb579bef1b7727003b8a7ce3a6347fc2fd001f2f71f5551e367b0",
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
      "latency_ms": 3365,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 244,
        "promptTokenCount": 4527,
        "thoughtsTokenCount": 367,
        "totalTokenCount": 5138
      }
    }
  ],
  "receptionist_output": {
    "decision_note": "Intent resize: staff requested to shorten an appointment to a specific duration.",
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
    "terminal_hash": "sha256:014169f54d3e612a08adffa12bfa89125d58dd6aac88bfe85db5f283fa9f5a19",
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
      "latency_ms": 5875,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 448,
        "promptTokenCount": 4529,
        "thoughtsTokenCount": 1070,
        "totalTokenCount": 6047
      }
    }
  ],
  "receptionist_output": {
    "decision_note": "Intent resize: staff requested to resize an appointment.",
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
    "resolve_patient_reference",
    "read_selected_appointment",
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
    "note_sha256": "sha256:8e29ae1d1471b111e6a2c2befc54feb4292764830feb09811635ae6c66bb53d0",
    "operator_note": "Proposal for review; no booking was changed.",
    "parsed_into_plan": false,
    "product_delivered": false,
    "reason_codes": [],
    "retained_utf8_bytes": 44
  },
  "parent_audit_chain": {
    "event_count": 4,
    "terminal_hash": "sha256:326b75d963464a60ab93b377c24ab32bc88cba2532c85a5f0b2f794c1915cd33",
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
      "latency_ms": 4342,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 441,
        "promptTokenCount": 4534,
        "thoughtsTokenCount": 518,
        "totalTokenCount": 5493
      }
    }
  ],
  "receptionist_output": {
    "decision_note": "Intent resize: resize appointment as requested.",
    "disposition": "admit",
    "evidence_utterance_indices": [
      0
    ],
    "hidden_reasoning": false,
    "natural_response_parsed_into_form": false,
    "product_delivered": false,
    "raw_provider_response": false,
    "receptionist_response": "I'm preparing a proposal to resize Margaret Thompson's booking to 30 minutes for your review.",
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
    "note_sha256": "sha256:8e29ae1d1471b111e6a2c2befc54feb4292764830feb09811635ae6c66bb53d0",
    "operator_note": "Proposal for review; no booking was changed.",
    "parsed_into_plan": false,
    "product_delivered": false,
    "reason_codes": [],
    "retained_utf8_bytes": 44
  },
  "parent_audit_chain": {
    "event_count": 4,
    "terminal_hash": "sha256:cbe9565c4775ff5b9cee00e80cf23ecc5d4fd08e8d6af2450b92093ffb84f049",
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
      "latency_ms": 2905,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 191,
        "promptTokenCount": 4510,
        "thoughtsTokenCount": 381,
        "totalTokenCount": 5082
      }
    }
  ],
  "receptionist_output": {
    "decision_note": "Intent cancel: decisive language 'Remove appointment'.",
    "disposition": "admit",
    "evidence_utterance_indices": [
      0
    ],
    "hidden_reasoning": false,
    "natural_response_parsed_into_form": false,
    "product_delivered": false,
    "raw_provider_response": false,
    "receptionist_response": "I'm preparing a proposal to remove Margaret Thompson's appointment from the diary for your review.",
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
    "note_sha256": "sha256:8e29ae1d1471b111e6a2c2befc54feb4292764830feb09811635ae6c66bb53d0",
    "operator_note": "Proposal for review; no booking was changed.",
    "parsed_into_plan": false,
    "product_delivered": false,
    "reason_codes": [],
    "retained_utf8_bytes": 44
  },
  "parent_audit_chain": {
    "event_count": 4,
    "terminal_hash": "sha256:57482508f0451165388ea554fa9c37a5d4ccc24b456e5b02a602fffeed21d9eb",
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
      "latency_ms": 3893,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 389,
        "promptTokenCount": 4503,
        "thoughtsTokenCount": 396,
        "totalTokenCount": 5288
      }
    }
  ],
  "receptionist_output": {
    "decision_note": "Intent cancel: staff requested to cancel an appointment.",
    "disposition": "admit",
    "evidence_utterance_indices": [
      0
    ],
    "hidden_reasoning": false,
    "natural_response_parsed_into_form": false,
    "product_delivered": false,
    "raw_provider_response": false,
    "receptionist_response": "I'm preparing a proposal to cancel Margaret's appointment for your review.",
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
    "program_hash": "sha256:36f92c5acf1df73204ec4bebc2349860c4cd4056b5719e5d33ba34451c0ea653",
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
    "note_sha256": "sha256:8e29ae1d1471b111e6a2c2befc54feb4292764830feb09811635ae6c66bb53d0",
    "operator_note": "Proposal for review; no booking was changed.",
    "parsed_into_plan": false,
    "product_delivered": false,
    "reason_codes": [],
    "retained_utf8_bytes": 44
  },
  "parent_audit_chain": {
    "event_count": 4,
    "terminal_hash": "sha256:e51d761c8228dfb4c5bd777028ab473ca5d6f09f96891e4e8a2c6e87fb152ddf",
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
      "latency_ms": 3941,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 188,
        "promptTokenCount": 4504,
        "thoughtsTokenCount": 602,
        "totalTokenCount": 5294
      }
    }
  ],
  "receptionist_output": {
    "decision_note": "Intent cancel: decisive language 'Take ... out'.",
    "disposition": "admit",
    "evidence_utterance_indices": [
      0
    ],
    "hidden_reasoning": false,
    "natural_response_parsed_into_form": false,
    "product_delivered": false,
    "raw_provider_response": false,
    "receptionist_response": "I'm preparing a proposal to cancel Margaret Thompson's appointment for review.",
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
    "terminal_hash": "sha256:94a1a3c2531e329c51422aab996e98408421d70fabe6af4bb106e2aa2f85b919",
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
      "latency_ms": 3475,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 453,
        "promptTokenCount": 4528,
        "thoughtsTokenCount": 117,
        "totalTokenCount": 5098
      }
    }
  ],
  "receptionist_output": {
    "decision_note": "Intent status_change: status change requested for selected appointment.",
    "disposition": "admit",
    "evidence_utterance_indices": [
      0
    ],
    "hidden_reasoning": false,
    "natural_response_parsed_into_form": false,
    "product_delivered": false,
    "raw_provider_response": false,
    "receptionist_response": "I am preparing a proposal to change Margaret Thompson's appointment status to completed for your review. No booking was changed.",
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
    "note_sha256": "sha256:8e29ae1d1471b111e6a2c2befc54feb4292764830feb09811635ae6c66bb53d0",
    "operator_note": "Proposal for review; no booking was changed.",
    "parsed_into_plan": false,
    "product_delivered": false,
    "reason_codes": [],
    "retained_utf8_bytes": 44
  },
  "parent_audit_chain": {
    "event_count": 4,
    "terminal_hash": "sha256:604ab33eb060003eae3c199a43081d3b5e5e4d1f3fa64e8d4919568f5ae5a585",
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
      "latency_ms": 5269,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 245,
        "promptTokenCount": 4532,
        "thoughtsTokenCount": 881,
        "totalTokenCount": 5658
      }
    }
  ],
  "receptionist_output": {
    "decision_note": "Intent status_change: status update requested for selected appointment.",
    "disposition": "admit",
    "evidence_utterance_indices": [
      0
    ],
    "hidden_reasoning": false,
    "natural_response_parsed_into_form": false,
    "product_delivered": false,
    "raw_provider_response": false,
    "receptionist_response": "I am preparing a proposal to update Margaret Thompson's appointment status to arrived for your review. No booking was changed.",
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
    "program_hash": "sha256:5c4906d8b5fb987af0e68228d2e40904fe1911ad452df8a33dc215698f9461e7",
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
    "terminal_hash": "sha256:824f89ed50410d65f23d048057d3ce62bdda793439baa4f3cb36cebb250c2b75",
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
      "latency_ms": 5340,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 147,
        "promptTokenCount": 4509,
        "thoughtsTokenCount": 867,
        "totalTokenCount": 5523
      }
    }
  ],
  "receptionist_output": {
    "decision_note": "Intent clarification: requested status 'no-show' is not a recognized binding.",
    "disposition": "admit",
    "evidence_utterance_indices": [
      0
    ],
    "hidden_reasoning": false,
    "natural_response_parsed_into_form": false,
    "product_delivered": false,
    "raw_provider_response": false,
    "receptionist_response": "Could you clarify which status you would like to apply for 'no-show'? No booking was changed.",
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
    "note_sha256": "sha256:56f450f88ac68427f96a395386a17eaba72c0fff2766d60921aa417cec0119b0",
    "operator_note": "Proposal for review. No booking was changed.",
    "parsed_into_plan": false,
    "product_delivered": false,
    "reason_codes": [],
    "retained_utf8_bytes": 44
  },
  "parent_audit_chain": {
    "event_count": 4,
    "terminal_hash": "sha256:94d62f4e23e93742b17711e5c49d4e95803df0e8908acd4c1f0822cc76979145",
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
      "latency_ms": 4841,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 706,
        "promptTokenCount": 4639,
        "thoughtsTokenCount": 568,
        "totalTokenCount": 5913
      }
    }
  ],
  "receptionist_output": {
    "decision_note": "Intent squeeze_in_assessment: assess squeeze-in under frozen policy.",
    "disposition": "admit",
    "evidence_utterance_indices": [
      0
    ],
    "hidden_reasoning": false,
    "natural_response_parsed_into_form": false,
    "product_delivered": false,
    "raw_provider_response": false,
    "receptionist_response": "I'm preparing a proposal to assess if we can squeeze Margaret in with Dr Shera for 15 minutes today. No booking was changed.",
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
    "program_hash": "sha256:2ec82ef03d03a36895cd4f8b97ec24d7a5f1c93736a6cee1521c225f0815cf63",
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
    "note_sha256": "sha256:8e29ae1d1471b111e6a2c2befc54feb4292764830feb09811635ae6c66bb53d0",
    "operator_note": "Proposal for review; no booking was changed.",
    "parsed_into_plan": false,
    "product_delivered": false,
    "reason_codes": [],
    "retained_utf8_bytes": 44
  },
  "parent_audit_chain": {
    "event_count": 4,
    "terminal_hash": "sha256:6a3f91361802f71c563ea2602fb369d931068d7d3c615e8929c1b440dfe55d4c",
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
      "latency_ms": 5406,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 706,
        "promptTokenCount": 4643,
        "thoughtsTokenCount": 558,
        "totalTokenCount": 5907
      }
    }
  ],
  "receptionist_output": {
    "decision_note": "Intent squeeze_in_assessment: staff requested to squeeze in a patient.",
    "disposition": "admit",
    "evidence_utterance_indices": [
      0
    ],
    "hidden_reasoning": false,
    "natural_response_parsed_into_form": false,
    "product_delivered": false,
    "raw_provider_response": false,
    "receptionist_response": "I am preparing a squeeze-in proposal for Margaret Thompson with Dr Shera for 15 minutes today for your review. No booking was changed.",
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
    "program_hash": "sha256:3496f0f50766c32faf2f7b494b13d5cdea74add41a8a8bf8389c8b040c76da01",
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
    "terminal_hash": "sha256:2a2b51114cce0a98ef09ae45436e1d1a239c8ea6c36fdd0e69caf8d10decb6bf",
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
      "latency_ms": 3307,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 137,
        "promptTokenCount": 4514,
        "thoughtsTokenCount": 515,
        "totalTokenCount": 5166
      }
    }
  ],
  "receptionist_output": {
    "decision_note": "Intent clarification: ambiguous action.",
    "disposition": "admit",
    "evidence_utterance_indices": [
      0
    ],
    "hidden_reasoning": false,
    "natural_response_parsed_into_form": false,
    "product_delivered": false,
    "raw_provider_response": false,
    "receptionist_response": "Could you clarify what you would like to do with Margaret Thompson's appointment? No booking was changed.",
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
    "note_sha256": "sha256:8e29ae1d1471b111e6a2c2befc54feb4292764830feb09811635ae6c66bb53d0",
    "operator_note": "Proposal for review; no booking was changed.",
    "parsed_into_plan": false,
    "product_delivered": false,
    "reason_codes": [],
    "retained_utf8_bytes": 44
  },
  "parent_audit_chain": {
    "event_count": 4,
    "terminal_hash": "sha256:11bf3db9e1b5c064015d4e347ee163b69a1dbe1af01c896e47edfba30a344342",
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
      "latency_ms": 3265,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 150,
        "promptTokenCount": 4502,
        "thoughtsTokenCount": 397,
        "totalTokenCount": 5049
      }
    }
  ],
  "receptionist_output": {
    "decision_note": "Intent clarification: ambiguous action 'different appointment'.",
    "disposition": "admit",
    "evidence_utterance_indices": [
      0
    ],
    "hidden_reasoning": false,
    "natural_response_parsed_into_form": false,
    "product_delivered": false,
    "raw_provider_response": false,
    "receptionist_response": "Could you clarify: do you want to move Margaret's existing appointment, or are you looking to book a new one? No booking was changed.",
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
    "program_hash": "sha256:f0ca55bba06adbb951ae81a82ea1af31ec7c2d84dbc1e4cca610e3842cc0b3a5",
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
    "terminal_hash": "sha256:a2c2ed95b36e69bf8d04931fd5d1be567a1dbcdaceca08496a2f185cdf4fefd8",
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
      "latency_ms": 3559,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 136,
        "promptTokenCount": 4678,
        "thoughtsTokenCount": 561,
        "totalTokenCount": 5375
      }
    }
  ],
  "receptionist_output": {
    "decision_note": "Intent clarification: missing action verb.",
    "disposition": "admit",
    "evidence_utterance_indices": [
      0
    ],
    "hidden_reasoning": false,
    "natural_response_parsed_into_form": false,
    "product_delivered": false,
    "raw_provider_response": false,
    "receptionist_response": "Could you clarify what you would like to do with this appointment information? No booking was changed.",
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
    "terminal_hash": "sha256:bfe21485cfa10553d01495f101b709f1fe7d0813b1cc34cc873302961374ed9f",
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
      "latency_ms": 3172,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 142,
        "promptTokenCount": 4689,
        "thoughtsTokenCount": 437,
        "totalTokenCount": 5268
      }
    }
  ],
  "receptionist_output": {
    "decision_note": "Intent clarification: ambiguous 'fit in' under frozen policy.",
    "disposition": "admit",
    "evidence_utterance_indices": [
      0
    ],
    "hidden_reasoning": false,
    "natural_response_parsed_into_form": false,
    "product_delivered": false,
    "raw_provider_response": false,
    "receptionist_response": "Which do you mean: an ordinary booking or a squeeze-in assessment? No booking was changed.",
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
