# Reception One v6.3 Full-Cohort Test Notebook

Status: complete
Cases closed: 24 / 24
Provider calls consumed: 29 / 48

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
    "note_sha256": "sha256:d5f7f9ddae7a66d7394337f714ea470a4d3decdda0f53bfbf22fbe9ad803325e",
    "operator_note": "Proposal for review, no booking was changed.",
    "parsed_into_plan": false,
    "product_delivered": false,
    "reason_codes": [],
    "retained_utf8_bytes": 44
  },
  "parent_audit_chain": {
    "event_count": 4,
    "terminal_hash": "sha256:5a20d709f4d8bd16db053b47c7da653123dcd0d46bfdc857095038a89466c421",
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
      "latency_ms": 7241,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 865,
        "promptTokenCount": 3950,
        "thoughtsTokenCount": 899,
        "totalTokenCount": 5714
      }
    }
  ],
  "receptionist_output": {
    "decision_note": "Intent create: User requested to arrange an appointment with specific details.",
    "disposition": "admit",
    "evidence_utterance_indices": [
      0
    ],
    "hidden_reasoning": false,
    "natural_response_parsed_into_form": false,
    "product_delivered": false,
    "raw_provider_response": false,
    "receptionist_response": "I'm preparing a proposal for a new appointment for Margaret Thompson with Dr Shera tomorrow at 2:30 pm for 15 minutes. This will be sent for review, and no booking was changed.",
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
    "program_hash": "sha256:01ca914c223e24334d15551fd3f91c29b57e6c9b6dd75b18752e5ac168e5a193",
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
    "note_sha256": "sha256:d5f7f9ddae7a66d7394337f714ea470a4d3decdda0f53bfbf22fbe9ad803325e",
    "operator_note": "Proposal for review, no booking was changed.",
    "parsed_into_plan": false,
    "product_delivered": false,
    "reason_codes": [],
    "retained_utf8_bytes": 44
  },
  "parent_audit_chain": {
    "event_count": 4,
    "terminal_hash": "sha256:75bf0f8185c9b4f22bdd95b16ab4dd94e3379f7032597ddf31a498477469b942",
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
      "latency_ms": 8190,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 864,
        "promptTokenCount": 3927,
        "thoughtsTokenCount": 872,
        "totalTokenCount": 5663
      }
    }
  ],
  "receptionist_output": {
    "decision_note": "Intent create: The request explicitly asks to 'book' an appointment with all necessary details.",
    "disposition": "admit",
    "evidence_utterance_indices": [
      0
    ],
    "hidden_reasoning": false,
    "natural_response_parsed_into_form": false,
    "product_delivered": false,
    "raw_provider_response": false,
    "receptionist_response": "I'm preparing a proposal to book Margaret with Dr. Shera tomorrow at 3 PM for 15 minutes. This will be sent for review, and no booking was changed.",
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
    "program_hash": "sha256:01ca914c223e24334d15551fd3f91c29b57e6c9b6dd75b18752e5ac168e5a193",
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
    "note_sha256": "sha256:d0bde6f469f2dc67f76be9f46670e7eb4b523d2294cad67b9ff0a57c8c7206df",
    "operator_note": "Proposal for review: no booking was changed.",
    "parsed_into_plan": false,
    "product_delivered": false,
    "reason_codes": [],
    "retained_utf8_bytes": 44
  },
  "parent_audit_chain": {
    "event_count": 4,
    "terminal_hash": "sha256:fcce503b53f8e7c955b3d41219b666ae27fcf07a562b2151220f126fe472f654",
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
      "latency_ms": 6837,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 859,
        "promptTokenCount": 3985,
        "thoughtsTokenCount": 797,
        "totalTokenCount": 5641
      }
    }
  ],
  "receptionist_output": {
    "decision_note": "Intent create: Staff explicitly requested to 'schedule an appointment'.",
    "disposition": "admit",
    "evidence_utterance_indices": [
      1
    ],
    "hidden_reasoning": false,
    "natural_response_parsed_into_form": false,
    "product_delivered": false,
    "raw_provider_response": false,
    "receptionist_response": "I'm preparing a proposal to schedule an appointment for Margaret Thompson with Dr Shera tomorrow at 2:30 pm for 15 minutes. This will be sent for review.",
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
  "expected_safe_outcome": false,
  "final_proofreader_disposition": "admit",
  "final_violation_codes": [],
  "operator_note": {
    "audit_only": true,
    "disposition": "admit",
    "note_sha256": "sha256:a5e3f8869d10f321408d16957975db3fefd18f13390a8f9f3b18736e5fc926e4",
    "operator_note": "A proposal for review is being prepared; no booking was changed.",
    "parsed_into_plan": false,
    "product_delivered": false,
    "reason_codes": [],
    "retained_utf8_bytes": 64
  },
  "parent_audit_chain": {
    "event_count": 4,
    "terminal_hash": "sha256:a78591d511375480cbfefaa12207cddea7634376d46ac3abcc44efed69762913",
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
      "latency_ms": 7412,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 859,
        "promptTokenCount": 3980,
        "thoughtsTokenCount": 932,
        "totalTokenCount": 5771
      }
    }
  ],
  "receptionist_output": {
    "decision_note": "Intent create: specific time changed.",
    "disposition": "admit",
    "evidence_utterance_indices": [
      0,
      1
    ],
    "hidden_reasoning": false,
    "natural_response_parsed_into_form": false,
    "product_delivered": false,
    "raw_provider_response": false,
    "receptionist_response": "I'm preparing a proposal to book an appointment for Margaret Thompson with Dr Shera tomorrow at 3:00 PM for 15 minutes. Please review the details.",
    "violations": []
  },
  "release": {
    "api_spine_operation_id": "proposeAppointmentCreate",
    "appointment_ref": null,
    "candidate_slot_ids": [
      "synthetic-slot-july28-1430",
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
              "binding_code": -1,
              "kind": "omit",
              "prior_output_name": "none",
              "prior_step_index": -1
            },
            {
              "binding_code": -1,
              "kind": "omit",
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
    "program_hash": "sha256:31fb7c419e6409252a7e254950ebdb9ac24c88566591ee9119ecaf0e2c1d53c3",
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
    "terminal_hash": "sha256:0249bb138679ed161dfbfb8a56fe8dd6794ef7260501542d38f2d144c23bf244",
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
      "latency_ms": 3928,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 557,
        "promptTokenCount": 3832,
        "thoughtsTokenCount": 141,
        "totalTokenCount": 4530
      }
    }
  ],
  "receptionist_output": {
    "decision_note": "Intent move: User wants to reschedule an existing appointment.",
    "disposition": "admit",
    "evidence_utterance_indices": [
      0
    ],
    "hidden_reasoning": false,
    "natural_response_parsed_into_form": false,
    "product_delivered": false,
    "raw_provider_response": false,
    "receptionist_response": "I am preparing a proposal to reschedule Margaret Thompson's appointment for tomorrow at 3 PM. This will be sent for review; no booking was changed.",
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
              "binding_code": 5,
              "kind": "binding",
              "prior_output_name": "none",
              "prior_step_index": -1
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
    "program_hash": "sha256:c225f7cf798ea638ae32cf37ae9e87ed63e8caf7535e4d0268f85cf14fc86a41",
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
    "note_sha256": "sha256:d0bde6f469f2dc67f76be9f46670e7eb4b523d2294cad67b9ff0a57c8c7206df",
    "operator_note": "Proposal for review: no booking was changed.",
    "parsed_into_plan": false,
    "product_delivered": false,
    "reason_codes": [],
    "retained_utf8_bytes": 44
  },
  "parent_audit_chain": {
    "event_count": 6,
    "terminal_hash": "sha256:fe0902584086e71744675ba6413bdf34bd9215a391ca4eb8636871ad7b53d93b",
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
      "latency_ms": 6964,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 806,
        "promptTokenCount": 3835,
        "thoughtsTokenCount": 792,
        "totalTokenCount": 5433
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
      "latency_ms": 9079,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 811,
        "promptTokenCount": 4365,
        "thoughtsTokenCount": 1246,
        "totalTokenCount": 6422
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
    "program_hash": "sha256:fb9af521a12b39f2923c2a0bee07806e674689a66963abf5ca13387716d34a62",
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
    "terminal_hash": "sha256:1c133e8d8d8194972b8574d2bc5f522670f31c6650fc478ec790b49149246b56",
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
      "latency_ms": 6898,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 803,
        "promptTokenCount": 3832,
        "thoughtsTokenCount": 790,
        "totalTokenCount": 5425
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
      "latency_ms": 7709,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 806,
        "promptTokenCount": 4359,
        "thoughtsTokenCount": 962,
        "totalTokenCount": 6127
      }
    }
  ],
  "receptionist_output": {
    "decision_note": "Intent move: The staff member explicitly requested to change the time of an appointment.",
    "disposition": "admit",
    "evidence_utterance_indices": [
      0
    ],
    "hidden_reasoning": false,
    "natural_response_parsed_into_form": false,
    "product_delivered": false,
    "raw_provider_response": false,
    "receptionist_response": "I am preparing a proposal to change the time of Margaret Thompson's appointment. This will be reviewed for you shortly; no booking was changed.",
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
              "binding_code": 5,
              "kind": "binding",
              "prior_output_name": "none",
              "prior_step_index": -1
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
    "program_hash": "sha256:c225f7cf798ea638ae32cf37ae9e87ed63e8caf7535e4d0268f85cf14fc86a41",
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
    "terminal_hash": "sha256:04a8ef4902457696c94264adf39e00070d13945caf824c633c6ac2f596e323b8",
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
      "latency_ms": 6944,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 810,
        "promptTokenCount": 3877,
        "thoughtsTokenCount": 807,
        "totalTokenCount": 5494
      }
    }
  ],
  "receptionist_output": {
    "decision_note": "Intent move: The latest utterance corrects the time for the move.",
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
    "note_sha256": "sha256:d0bde6f469f2dc67f76be9f46670e7eb4b523d2294cad67b9ff0a57c8c7206df",
    "operator_note": "Proposal for review: no booking was changed.",
    "parsed_into_plan": false,
    "product_delivered": false,
    "reason_codes": [],
    "retained_utf8_bytes": 44
  },
  "parent_audit_chain": {
    "event_count": 4,
    "terminal_hash": "sha256:a9365d49e778e99dc08cd44f2741caa17f1487933221f90c072ce86f3add601c",
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
      "latency_ms": 4960,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 450,
        "promptTokenCount": 3793,
        "thoughtsTokenCount": 454,
        "totalTokenCount": 4697
      }
    }
  ],
  "receptionist_output": {
    "decision_note": "Intent resize: All necessary information for resizing the appointment is present.",
    "disposition": "admit",
    "evidence_utterance_indices": [
      0
    ],
    "hidden_reasoning": false,
    "natural_response_parsed_into_form": false,
    "product_delivered": false,
    "raw_provider_response": false,
    "receptionist_response": "I am preparing a proposal to make Margaret Thompson's appointment 30 minutes long for your review. No booking was changed.",
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
    "program_hash": "sha256:f38fe6d789f85e7d8e9af1447fbb8259151073a03183ce00b13cf88850cf3fe0",
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
    "note_sha256": "sha256:d0bde6f469f2dc67f76be9f46670e7eb4b523d2294cad67b9ff0a57c8c7206df",
    "operator_note": "Proposal for review: no booking was changed.",
    "parsed_into_plan": false,
    "product_delivered": false,
    "reason_codes": [],
    "retained_utf8_bytes": 44
  },
  "parent_audit_chain": {
    "event_count": 4,
    "terminal_hash": "sha256:e923e13883c1c1547b33b276878d22c4e4702ed3d5685de8373d2c6bb1b92be5",
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
      "latency_ms": 3882,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 452,
        "promptTokenCount": 3781,
        "thoughtsTokenCount": 346,
        "totalTokenCount": 4579
      }
    }
  ],
  "receptionist_output": {
    "decision_note": "Intent resize: The staff member explicitly requested to shorten an appointment to a specific duration.",
    "disposition": "admit",
    "evidence_utterance_indices": [
      0
    ],
    "hidden_reasoning": false,
    "natural_response_parsed_into_form": false,
    "product_delivered": false,
    "raw_provider_response": false,
    "receptionist_response": "I am preparing a proposal to shorten Margaret's appointment to 10 minutes for review. No booking was changed.",
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
    "program_hash": "sha256:f38fe6d789f85e7d8e9af1447fbb8259151073a03183ce00b13cf88850cf3fe0",
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
    "note_sha256": "sha256:d0bde6f469f2dc67f76be9f46670e7eb4b523d2294cad67b9ff0a57c8c7206df",
    "operator_note": "Proposal for review: no booking was changed.",
    "parsed_into_plan": false,
    "product_delivered": false,
    "reason_codes": [],
    "retained_utf8_bytes": 44
  },
  "parent_audit_chain": {
    "event_count": 4,
    "terminal_hash": "sha256:75447ba5c3de2445d52393b1c38ae0f7d3c4166d391114254d0999dddab77e94",
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
      "latency_ms": 6215,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 457,
        "promptTokenCount": 3783,
        "thoughtsTokenCount": 862,
        "totalTokenCount": 5102
      }
    }
  ],
  "receptionist_output": {
    "decision_note": "Intent resize: The staff member explicitly requested to change the duration of an appointment.",
    "disposition": "admit",
    "evidence_utterance_indices": [
      0
    ],
    "hidden_reasoning": false,
    "natural_response_parsed_into_form": false,
    "product_delivered": false,
    "raw_provider_response": false,
    "receptionist_response": "I'm preparing a proposal to change the duration of Margaret Thompson's appointment to 30 minutes for your review. No booking was changed.",
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
    "program_hash": "sha256:f38fe6d789f85e7d8e9af1447fbb8259151073a03183ce00b13cf88850cf3fe0",
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
    "note_sha256": "sha256:8e29ae1d1471b111e6a2c2befc54feb4292764830feb09811635ae6c66bb53d0",
    "operator_note": "Proposal for review; no booking was changed.",
    "parsed_into_plan": false,
    "product_delivered": false,
    "reason_codes": [],
    "retained_utf8_bytes": 44
  },
  "parent_audit_chain": {
    "event_count": 4,
    "terminal_hash": "sha256:6c0b2569070795494f2f1823d7db6640201bd3ad70e6741e4d8f3da8baa960a3",
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
      "latency_ms": 5238,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 243,
        "promptTokenCount": 3788,
        "thoughtsTokenCount": 685,
        "totalTokenCount": 4716
      }
    }
  ],
  "receptionist_output": {
    "decision_note": "Intent resize: The user explicitly requested to resize an appointment.",
    "disposition": "admit",
    "evidence_utterance_indices": [
      0
    ],
    "hidden_reasoning": false,
    "natural_response_parsed_into_form": false,
    "product_delivered": false,
    "raw_provider_response": false,
    "receptionist_response": "I'm preparing a proposal to resize Margaret Thompson's appointment to 30 minutes for your review.",
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

## 13. b-cancel-remove

```json
{
  "actual_provider_calls": 1,
  "admitted_operator_ids": [
    "resolve_patient_reference",
    "read_selected_appointment",
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
    "terminal_hash": "sha256:30ea78610eff92dc3f772d0cc2269379828243b62d5664d9d7cb3465268f0296",
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
      "latency_ms": 4891,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 395,
        "promptTokenCount": 3764,
        "thoughtsTokenCount": 459,
        "totalTokenCount": 4618
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
    "receptionist_response": "I am preparing a proposal to remove Margaret Thompson's appointment. This will be sent for review.",
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
    "note_sha256": "sha256:d0bde6f469f2dc67f76be9f46670e7eb4b523d2294cad67b9ff0a57c8c7206df",
    "operator_note": "Proposal for review: no booking was changed.",
    "parsed_into_plan": false,
    "product_delivered": false,
    "reason_codes": [],
    "retained_utf8_bytes": 44
  },
  "parent_audit_chain": {
    "event_count": 4,
    "terminal_hash": "sha256:3e31998edf0c0bade3dea8b8db1bbefaf9d456a6963421787a22806526383d5e",
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
      "latency_ms": 2650,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 273,
        "promptTokenCount": 3757,
        "thoughtsTokenCount": 94,
        "totalTokenCount": 4124
      }
    }
  ],
  "receptionist_output": {
    "decision_note": "Intent cancel: The staff member explicitly requested to cancel an appointment.",
    "disposition": "admit",
    "evidence_utterance_indices": [
      0
    ],
    "hidden_reasoning": false,
    "natural_response_parsed_into_form": false,
    "product_delivered": false,
    "raw_provider_response": false,
    "receptionist_response": "I am preparing the cancellation for Margaret Thompson's appointment for review. No booking was changed.",
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
    "program_hash": "sha256:2e25aacab6fd47924c9fa4e7733f9941bb8fb16d0cbb3d1ffff5cae89f32ae1d",
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
    "note_sha256": "sha256:d5f7f9ddae7a66d7394337f714ea470a4d3decdda0f53bfbf22fbe9ad803325e",
    "operator_note": "Proposal for review, no booking was changed.",
    "parsed_into_plan": false,
    "product_delivered": false,
    "reason_codes": [],
    "retained_utf8_bytes": 44
  },
  "parent_audit_chain": {
    "event_count": 4,
    "terminal_hash": "sha256:10c6d9a65ef798fd35e57819a231ede42c24311d8061a77dd3da4c8bb7814e68",
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
      "latency_ms": 4095,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 391,
        "promptTokenCount": 3758,
        "thoughtsTokenCount": 405,
        "totalTokenCount": 4554
      }
    }
  ],
  "receptionist_output": {
    "decision_note": "Intent cancel: decisive language for cancellation.",
    "disposition": "admit",
    "evidence_utterance_indices": [
      0
    ],
    "hidden_reasoning": false,
    "natural_response_parsed_into_form": false,
    "product_delivered": false,
    "raw_provider_response": false,
    "receptionist_response": "I'm preparing the cancellation for Margaret Thompson's appointment for review. No booking was changed.",
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
    "program_hash": "sha256:634c092215a459b2d682a31153ccaba5e16cdb6397019673c5e6710eae07916d",
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
    "note_sha256": "sha256:ad3361c80bf50a05a670c83467ed7b4864d68f7d797ee462ff8966a5008e891a",
    "operator_note": "Proposal prepared for review; no booking was changed.",
    "parsed_into_plan": false,
    "product_delivered": false,
    "reason_codes": [],
    "retained_utf8_bytes": 53
  },
  "parent_audit_chain": {
    "event_count": 4,
    "terminal_hash": "sha256:64bb729444f1b21753c1320e2dad950652f0bb152faf889215fe0961ab284a3c",
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
      "latency_ms": 4804,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 456,
        "promptTokenCount": 3782,
        "thoughtsTokenCount": 520,
        "totalTokenCount": 4758
      }
    }
  ],
  "receptionist_output": {
    "decision_note": "Intent status_change: The request explicitly states to set the status of an appointment.",
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
    "program_hash": "sha256:5fb116436472153fb5f229d4122e12499e779e7778ec9c1d3d018b9c11061382",
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
    "note_sha256": "sha256:d0bde6f469f2dc67f76be9f46670e7eb4b523d2294cad67b9ff0a57c8c7206df",
    "operator_note": "Proposal for review: no booking was changed.",
    "parsed_into_plan": false,
    "product_delivered": false,
    "reason_codes": [],
    "retained_utf8_bytes": 44
  },
  "parent_audit_chain": {
    "event_count": 4,
    "terminal_hash": "sha256:d56f3eca0bc51662605cd4b8cab2ed5b80a288a6d6ebdaf99dacd8691b35ef53",
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
      "latency_ms": 3617,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 326,
        "promptTokenCount": 3786,
        "thoughtsTokenCount": 313,
        "totalTokenCount": 4425
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
    "program_hash": "sha256:95798febccfa21d956b562a2e159bd27a0b19276ff1d568714b7aab9a2fe9712",
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
    "note_sha256": "sha256:d0bde6f469f2dc67f76be9f46670e7eb4b523d2294cad67b9ff0a57c8c7206df",
    "operator_note": "Proposal for review: no booking was changed.",
    "parsed_into_plan": false,
    "product_delivered": false,
    "reason_codes": [],
    "retained_utf8_bytes": 44
  },
  "parent_audit_chain": {
    "event_count": 4,
    "terminal_hash": "sha256:525a007cf72f6dc17715c10b6738c3fc20f3c7e97345e0aed48bca6caf34cdb6",
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
      "latency_ms": 5108,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 151,
        "promptTokenCount": 3763,
        "thoughtsTokenCount": 592,
        "totalTokenCount": 4506
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
    "receptionist_response": "I can mark Margaret's appointment, but I need to confirm the exact status you'd like to apply for 'no-show'. Could you please clarify?",
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
    "program_hash": "sha256:cf6b9794dceadd304333d437626c7a7f298831ee4ea293c1729b3ea2d9a0f55c",
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
    "terminal_hash": "sha256:5eea72060b87b158be308a240b2154a7530c175a0c8c7523a746769648ec4c64",
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
      "latency_ms": 7734,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 726,
        "promptTokenCount": 3893,
        "thoughtsTokenCount": 836,
        "totalTokenCount": 5455
      }
    }
  ],
  "receptionist_output": {
    "decision_note": "Intent squeeze_in_assessment: The staff member explicitly requested to 'squeeze in' an appointment with a specific policy.",
    "disposition": "admit",
    "evidence_utterance_indices": [
      0
    ],
    "hidden_reasoning": false,
    "natural_response_parsed_into_form": false,
    "product_delivered": false,
    "raw_provider_response": false,
    "receptionist_response": "I'm preparing a proposal to see if we can squeeze Margaret in with Dr Shera for 15 minutes today without moving anyone. This will be sent for review, and no booking was changed.",
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
    "note_sha256": "sha256:d0bde6f469f2dc67f76be9f46670e7eb4b523d2294cad67b9ff0a57c8c7206df",
    "operator_note": "Proposal for review: no booking was changed.",
    "parsed_into_plan": false,
    "product_delivered": false,
    "reason_codes": [],
    "retained_utf8_bytes": 44
  },
  "parent_audit_chain": {
    "event_count": 6,
    "terminal_hash": "sha256:4a058293636e11ccbf32105357be5863a18743fe2f2e07cde2025079e25389ba",
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
      "latency_ms": 6518,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 717,
        "promptTokenCount": 3897,
        "thoughtsTokenCount": 702,
        "totalTokenCount": 5316
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
      "latency_ms": 6834,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 491,
        "promptTokenCount": 4360,
        "thoughtsTokenCount": 1011,
        "totalTokenCount": 5862
      }
    }
  ],
  "receptionist_output": {
    "decision_note": "Intent squeeze_in_assessment: User requested to squeeze in an appointment.",
    "disposition": "admit",
    "evidence_utterance_indices": [
      0
    ],
    "hidden_reasoning": false,
    "natural_response_parsed_into_form": false,
    "product_delivered": false,
    "raw_provider_response": false,
    "receptionist_response": "I am preparing the squeeze-in assessment for Margaret Thompson with Dr Shera for 15 minutes today. This will be reviewed shortly; no booking was changed.",
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
    "program_hash": "sha256:e018846f2d0f84bd75c77e6164c1aa7a7bf0a18568880e5ab245eab79f65cd54",
    "raw_provider_response": false
  }
}
```

## 21. b-clarify-sort

```json
{
  "actual_provider_calls": 1,
  "admitted_operator_ids": [
    "resolve_patient_reference",
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
    "note_sha256": "sha256:8e29ae1d1471b111e6a2c2befc54feb4292764830feb09811635ae6c66bb53d0",
    "operator_note": "Proposal for review; no booking was changed.",
    "parsed_into_plan": false,
    "product_delivered": false,
    "reason_codes": [],
    "retained_utf8_bytes": 44
  },
  "parent_audit_chain": {
    "event_count": 4,
    "terminal_hash": "sha256:97e01f5f786d8c5e7bb42d79087f57dd514db2e269620fde64e69c37b637cb06",
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
      "latency_ms": 3947,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 228,
        "promptTokenCount": 3768,
        "thoughtsTokenCount": 428,
        "totalTokenCount": 4424
      }
    }
  ],
  "receptionist_output": {
    "decision_note": "Intent clarification: The request \"sort out\" is too vague to determine a specific action.",
    "disposition": "admit",
    "evidence_utterance_indices": [
      0
    ],
    "hidden_reasoning": false,
    "natural_response_parsed_into_form": false,
    "product_delivered": false,
    "raw_provider_response": false,
    "receptionist_response": "I need more information to help with Margaret Thompson's appointment. Could you please tell me what you would like to do?",
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
          "operator_code": 13,
          "source_refs": []
        }
      ],
      "version_code": 3
    },
    "operator_note_excluded": true,
    "program_hash": "sha256:a647be13bb840b37d89f6c2842f487b1b5d9539fb0005eb71b91530c2302c28c",
    "raw_provider_response": false
  }
}
```

## 22. b-clarify-different

```json
{
  "actual_provider_calls": 1,
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
    "terminal_hash": "sha256:069979c3d7b5ac4018cbffffefa19999c8ed7aa2e00a89c215b927d131ebcee3",
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
      "latency_ms": 5592,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 335,
        "promptTokenCount": 3756,
        "thoughtsTokenCount": 635,
        "totalTokenCount": 4726
      }
    }
  ],
  "receptionist_output": {
    "decision_note": "Intent clarification: missing new appointment details.",
    "disposition": "admit",
    "evidence_utterance_indices": [
      0
    ],
    "hidden_reasoning": false,
    "natural_response_parsed_into_form": false,
    "product_delivered": false,
    "raw_provider_response": false,
    "receptionist_response": "I understand Margaret Thompson needs a different appointment. What date and time would she prefer?",
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
    "program_hash": "sha256:5ac870c2202b614fa780fa068730420c4a6946d016083fbc92577b9d4580aaa0",
    "raw_provider_response": false
  }
}
```

## 23. b-clarify-details

```json
{
  "actual_provider_calls": 2,
  "admitted_operator_ids": [
    "resolve_patient_reference",
    "resolve_practitioner_reference",
    "resolve_date_expression",
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
    "terminal_hash": "sha256:bdb1170f18ccc2ec820d6d9202eb69471933588492e343d2f3f11db38498413e",
    "valid": true
  },
  "primary_exact_body_accepted": true,
  "primary_proofreader_disposition": "revision_required",
  "primary_violation_codes": [
    "decision_note_goal_mismatch",
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
      "latency_ms": 7267,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 391,
        "promptTokenCount": 3932,
        "thoughtsTokenCount": 878,
        "totalTokenCount": 5201
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
      "latency_ms": 7366,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 381,
        "promptTokenCount": 4267,
        "thoughtsTokenCount": 821,
        "totalTokenCount": 5469
      }
    }
  ],
  "receptionist_output": {
    "decision_note": "Intent clarification: Missing explicit action verb.",
    "disposition": "admit",
    "evidence_utterance_indices": [
      0
    ],
    "hidden_reasoning": false,
    "natural_response_parsed_into_form": false,
    "product_delivered": false,
    "raw_provider_response": false,
    "receptionist_response": "I have details for an appointment for Margaret Thompson with Dr Shera tomorrow at 2:30 pm for 15 minutes. What would you like me to do with this information?",
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
          "operator_code": 13,
          "source_refs": []
        }
      ],
      "version_code": 3
    },
    "operator_note_excluded": true,
    "program_hash": "sha256:dd1ce39856607f5d76f20b2bca10284950fa0fbcd974d836b8261933a0cca964",
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
    "note_sha256": "sha256:8e29ae1d1471b111e6a2c2befc54feb4292764830feb09811635ae6c66bb53d0",
    "operator_note": "Proposal for review; no booking was changed.",
    "parsed_into_plan": false,
    "product_delivered": false,
    "reason_codes": [],
    "retained_utf8_bytes": 44
  },
  "parent_audit_chain": {
    "event_count": 6,
    "terminal_hash": "sha256:bacf2233de666c4242f4d63f7ed5ffb877736734106125cee2b9a19436095360",
    "valid": true
  },
  "primary_exact_body_accepted": true,
  "primary_proofreader_disposition": "revision_required",
  "primary_violation_codes": [
    "receptionist_response_goal_mismatch",
    "receptionist_response_missing_review_boundary"
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
      "latency_ms": 3096,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 177,
        "promptTokenCount": 3943,
        "thoughtsTokenCount": 300,
        "totalTokenCount": 4420
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
      "latency_ms": 4489,
      "status": "completed",
      "usage": {
        "candidatesTokenCount": 155,
        "promptTokenCount": 4163,
        "thoughtsTokenCount": 516,
        "totalTokenCount": 4834
      }
    }
  ],
  "receptionist_output": {
    "decision_note": "Intent clarification: The phrase 'fit in' is ambiguous.",
    "disposition": "admit",
    "evidence_utterance_indices": [
      0
    ],
    "hidden_reasoning": false,
    "natural_response_parsed_into_form": false,
    "product_delivered": false,
    "raw_provider_response": false,
    "receptionist_response": "I'm preparing this for review. Could you please clarify if you'd like to book a regular appointment or if this is an urgent squeeze-in request?",
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
