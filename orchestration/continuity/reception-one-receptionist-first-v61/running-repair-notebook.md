# Reception One v6.1 Targeted Repair Notebook

Status: complete
Cases closed: 15 / 15
Provider calls consumed: 17 / 30
Usage: 46668 prompt, 7884 visible candidate, 10778 thinking, 65330 total tokens

This notebook retains sanitized natural receptionist text, typed forms, proofreader findings and usage counts. It excludes raw provider packets, credentials, API-key information and hidden chain-of-thought.

## 1. b-create-correct

Authored-synthetic input:

- Book an appointment for Margaret Thompson with Dr Shera tomorrow at 2:30 pm for 15 minutes.
- Actually, make it 3 pm instead.

### Turn 1 - completed

```json
{
  "proofreader": {
    "admitted_operator_ids": [
      "resolve_patient_reference",
      "resolve_practitioner_reference",
      "resolve_date_expression",
      "search_available_slots",
      "prepare_create_proposal"
    ],
    "disposition": "admit",
    "safe_repairs": [],
    "violations": [],
    "wire_safe_repairs": []
  },
  "receptionist_output": {
    "decision_note": "Intent create: The time was corrected in the latest utterance.",
    "disposition": "admit",
    "evidence_utterance_indices": [
      0,
      1
    ],
    "hidden_reasoning": false,
    "natural_response_parsed_into_form": false,
    "product_delivered": false,
    "raw_provider_response": false,
    "receptionist_response": "I am preparing a proposal to book an appointment for Margaret Thompson with Dr Shera tomorrow at 3:00 PM for 15 minutes. This will be sent for your review.",
    "violations": []
  },
  "release": {
    "atomic_release": true,
    "human_gate": true,
    "released_field_manifest": [
      "$.final_output.api_spine_operation_id",
      "$.final_output.appointment_ref",
      "$.final_output.candidate_slot_ids",
      "$.final_output.duration_minutes",
      "$.final_output.kind",
      "$.final_output.patient_ref",
      "$.final_output.practitioner_ref",
      "$.final_output.proposal_family",
      "$.final_output.requires_human_confirmation",
      "$.final_output.status",
      "$.final_output.warning_codes",
      "$.final_output.write_performed"
    ],
    "released_values": {
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
    "write_performed": false
  },
  "typed_form": {
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
  "usage": {
    "candidatesTokenCount": 862,
    "promptTokenCount": 2949,
    "thoughtsTokenCount": 855,
    "totalTokenCount": 4666
  }
}
```

Result:

```json
{
  "correction_used": false,
  "exact_expected_outcome": true,
  "v61_terminal_status": "admitted",
  "v6_terminal_status": "terminal_no_release"
}
```

## 2. b-move-resched

Authored-synthetic input:

- Reschedule Margaret Thompson's appointment to tomorrow at 3 pm.

### Turn 1 - completed

```json
{
  "proofreader": {
    "admitted_operator_ids": [
      "resolve_patient_reference",
      "read_selected_appointment",
      "resolve_date_expression",
      "search_available_slots",
      "prepare_move_proposal"
    ],
    "disposition": "admit",
    "safe_repairs": [],
    "violations": [],
    "wire_safe_repairs": []
  },
  "receptionist_output": {
    "decision_note": "Intent move: All necessary information for rescheduling the appointment is present.",
    "disposition": "admit",
    "evidence_utterance_indices": [
      0
    ],
    "hidden_reasoning": false,
    "natural_response_parsed_into_form": false,
    "product_delivered": false,
    "raw_provider_response": false,
    "receptionist_response": "I am preparing a proposal to reschedule Margaret Thompson's appointment for review. No booking was changed.",
    "violations": []
  },
  "release": {
    "atomic_release": true,
    "human_gate": true,
    "released_field_manifest": [
      "$.final_output.api_spine_operation_id",
      "$.final_output.appointment_ref",
      "$.final_output.candidate_slot_ids",
      "$.final_output.duration_minutes",
      "$.final_output.kind",
      "$.final_output.patient_ref",
      "$.final_output.practitioner_ref",
      "$.final_output.proposal_family",
      "$.final_output.requires_human_confirmation",
      "$.final_output.status",
      "$.final_output.warning_codes",
      "$.final_output.write_performed"
    ],
    "released_values": {
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
    "write_performed": false
  },
  "typed_form": {
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
  "usage": {
    "candidatesTokenCount": 796,
    "promptTokenCount": 2886,
    "thoughtsTokenCount": 997,
    "totalTokenCount": 4679
  }
}
```

Result:

```json
{
  "correction_used": false,
  "exact_expected_outcome": true,
  "v61_terminal_status": "admitted",
  "v6_terminal_status": "admitted"
}
```

## 3. b-move-shift

Authored-synthetic input:

- Shift Margaret's appointment to tomorrow at 2:30 pm.

### Turn 1 - response_rejected_before_candidate

```json
{
  "proofreader": {
    "admitted_operator_ids": [],
    "disposition": "not_reached",
    "safe_repairs": [],
    "violations": [],
    "wire_safe_repairs": []
  },
  "receptionist_output": null,
  "release": null,
  "typed_form": null,
  "usage": {}
}
```

Result:

```json
{
  "correction_used": false,
  "exact_expected_outcome": false,
  "v61_terminal_status": "terminal_no_release",
  "v6_terminal_status": "admitted_after_correction"
}
```

## 4. b-move-change

Authored-synthetic input:

- Change the time of Margaret Thompson's appointment to tomorrow at 3 pm.

### Turn 1 - completed

```json
{
  "proofreader": {
    "admitted_operator_ids": [],
    "disposition": "revision_required",
    "safe_repairs": [],
    "violations": [
      {
        "code": "receptionist_response_goal_mismatch",
        "path": "$.receptionist_response"
      }
    ],
    "wire_safe_repairs": []
  },
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
  "typed_form": {
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
  "usage": {
    "candidatesTokenCount": 798,
    "promptTokenCount": 2892,
    "thoughtsTokenCount": 985,
    "totalTokenCount": 4675
  }
}
```

### Turn 2 - completed

```json
{
  "proofreader": {
    "admitted_operator_ids": [
      "resolve_patient_reference",
      "read_selected_appointment",
      "resolve_date_expression",
      "search_available_slots",
      "prepare_move_proposal"
    ],
    "disposition": "admit",
    "safe_repairs": [],
    "violations": [],
    "wire_safe_repairs": []
  },
  "receptionist_output": {
    "decision_note": "Intent move: The user explicitly requested to change the time of an appointment.",
    "disposition": "admit",
    "evidence_utterance_indices": [
      0
    ],
    "hidden_reasoning": false,
    "natural_response_parsed_into_form": false,
    "product_delivered": false,
    "raw_provider_response": false,
    "receptionist_response": "I'm preparing a proposal to move Margaret Thompson's appointment to tomorrow at 3 pm for review.",
    "violations": []
  },
  "release": {
    "atomic_release": true,
    "human_gate": true,
    "released_field_manifest": [
      "$.final_output.api_spine_operation_id",
      "$.final_output.appointment_ref",
      "$.final_output.candidate_slot_ids",
      "$.final_output.duration_minutes",
      "$.final_output.kind",
      "$.final_output.patient_ref",
      "$.final_output.practitioner_ref",
      "$.final_output.proposal_family",
      "$.final_output.requires_human_confirmation",
      "$.final_output.status",
      "$.final_output.warning_codes",
      "$.final_output.write_performed"
    ],
    "released_values": {
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
    "write_performed": false
  },
  "typed_form": {
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
  "usage": {
    "candidatesTokenCount": 800,
    "promptTokenCount": 3423,
    "thoughtsTokenCount": 917,
    "totalTokenCount": 5140
  }
}
```

Result:

```json
{
  "correction_used": true,
  "exact_expected_outcome": true,
  "v61_terminal_status": "admitted_after_correction",
  "v6_terminal_status": "admitted"
}
```

## 5. b-move-correct

Authored-synthetic input:

- Move Margaret Thompson's appointment to tomorrow at 2:30 pm.
- Actually, make it 3 pm instead.

### Turn 1 - completed

```json
{
  "proofreader": {
    "admitted_operator_ids": [
      "resolve_patient_reference",
      "read_selected_appointment",
      "resolve_date_expression",
      "search_available_slots",
      "prepare_move_proposal"
    ],
    "disposition": "admit",
    "safe_repairs": [],
    "violations": [],
    "wire_safe_repairs": []
  },
  "receptionist_output": {
    "decision_note": "Intent move: User requested to move an appointment and then corrected the time.",
    "disposition": "admit",
    "evidence_utterance_indices": [
      0,
      1
    ],
    "hidden_reasoning": false,
    "natural_response_parsed_into_form": false,
    "product_delivered": false,
    "raw_provider_response": false,
    "receptionist_response": "I understand you'd like to move Margaret Thompson's appointment to tomorrow at 3:00 PM. I am preparing that for review.",
    "violations": []
  },
  "release": {
    "atomic_release": true,
    "human_gate": true,
    "released_field_manifest": [
      "$.final_output.api_spine_operation_id",
      "$.final_output.appointment_ref",
      "$.final_output.candidate_slot_ids",
      "$.final_output.duration_minutes",
      "$.final_output.kind",
      "$.final_output.patient_ref",
      "$.final_output.practitioner_ref",
      "$.final_output.proposal_family",
      "$.final_output.requires_human_confirmation",
      "$.final_output.status",
      "$.final_output.warning_codes",
      "$.final_output.write_performed"
    ],
    "released_values": {
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
    "write_performed": false
  },
  "typed_form": {
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
  "usage": {
    "candidatesTokenCount": 813,
    "promptTokenCount": 2904,
    "thoughtsTokenCount": 826,
    "totalTokenCount": 4543
  }
}
```

Result:

```json
{
  "correction_used": false,
  "exact_expected_outcome": true,
  "v61_terminal_status": "admitted",
  "v6_terminal_status": "admitted"
}
```

## 6. b-resize-long

Authored-synthetic input:

- Make Margaret Thompson's appointment longer, 30 minutes.

### Turn 1 - completed

```json
{
  "proofreader": {
    "admitted_operator_ids": [
      "resolve_patient_reference",
      "read_selected_appointment",
      "prepare_resize_proposal"
    ],
    "disposition": "admit",
    "safe_repairs": [],
    "violations": [],
    "wire_safe_repairs": []
  },
  "receptionist_output": {
    "decision_note": "Intent resize: The user requested to change the duration of an appointment.",
    "disposition": "admit",
    "evidence_utterance_indices": [
      0
    ],
    "hidden_reasoning": false,
    "natural_response_parsed_into_form": false,
    "product_delivered": false,
    "raw_provider_response": false,
    "receptionist_response": "I'm preparing a proposal to make Margaret Thompson's appointment 30 minutes longer. This will be sent for your review; no booking was changed.",
    "violations": []
  },
  "release": {
    "atomic_release": true,
    "human_gate": true,
    "released_field_manifest": [
      "$.final_output.api_spine_operation_id",
      "$.final_output.appointment_ref",
      "$.final_output.candidate_slot_ids",
      "$.final_output.duration_minutes",
      "$.final_output.kind",
      "$.final_output.patient_ref",
      "$.final_output.practitioner_ref",
      "$.final_output.proposal_family",
      "$.final_output.requires_human_confirmation",
      "$.final_output.status",
      "$.final_output.warning_codes",
      "$.final_output.write_performed"
    ],
    "released_values": {
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
    "write_performed": false
  },
  "typed_form": {
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
  "usage": {
    "candidatesTokenCount": 457,
    "promptTokenCount": 2850,
    "thoughtsTokenCount": 734,
    "totalTokenCount": 4041
  }
}
```

Result:

```json
{
  "correction_used": false,
  "exact_expected_outcome": true,
  "v61_terminal_status": "admitted",
  "v6_terminal_status": "admitted"
}
```

## 7. b-resize-short

Authored-synthetic input:

- Shorten Margaret's appointment to 10 minutes.

### Turn 1 - completed

```json
{
  "proofreader": {
    "admitted_operator_ids": [
      "resolve_patient_reference",
      "read_selected_appointment",
      "prepare_resize_proposal"
    ],
    "disposition": "admit",
    "safe_repairs": [],
    "violations": [],
    "wire_safe_repairs": []
  },
  "receptionist_output": {
    "decision_note": "Intent resize: User wants to change the duration of an existing appointment.",
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
    "atomic_release": true,
    "human_gate": true,
    "released_field_manifest": [
      "$.final_output.api_spine_operation_id",
      "$.final_output.appointment_ref",
      "$.final_output.candidate_slot_ids",
      "$.final_output.duration_minutes",
      "$.final_output.kind",
      "$.final_output.patient_ref",
      "$.final_output.practitioner_ref",
      "$.final_output.proposal_family",
      "$.final_output.requires_human_confirmation",
      "$.final_output.status",
      "$.final_output.warning_codes",
      "$.final_output.write_performed"
    ],
    "released_values": {
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
    "write_performed": false
  },
  "typed_form": {
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
  "usage": {
    "candidatesTokenCount": 451,
    "promptTokenCount": 2843,
    "thoughtsTokenCount": 622,
    "totalTokenCount": 3916
  }
}
```

Result:

```json
{
  "correction_used": false,
  "exact_expected_outcome": true,
  "v61_terminal_status": "admitted",
  "v6_terminal_status": "admitted"
}
```

## 8. b-resize-give

Authored-synthetic input:

- Give them 30 minutes for Margaret Thompson's appointment.

### Turn 1 - completed

```json
{
  "proofreader": {
    "admitted_operator_ids": [
      "resolve_patient_reference",
      "read_selected_appointment",
      "prepare_resize_proposal"
    ],
    "disposition": "admit",
    "safe_repairs": [],
    "violations": [],
    "wire_safe_repairs": []
  },
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
    "receptionist_response": "I'm preparing a proposal to change the duration of Margaret Thompson's appointment to 30 minutes for your review.",
    "violations": []
  },
  "release": {
    "atomic_release": true,
    "human_gate": true,
    "released_field_manifest": [
      "$.final_output.api_spine_operation_id",
      "$.final_output.appointment_ref",
      "$.final_output.candidate_slot_ids",
      "$.final_output.duration_minutes",
      "$.final_output.kind",
      "$.final_output.patient_ref",
      "$.final_output.practitioner_ref",
      "$.final_output.proposal_family",
      "$.final_output.requires_human_confirmation",
      "$.final_output.status",
      "$.final_output.warning_codes",
      "$.final_output.write_performed"
    ],
    "released_values": {
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
    "write_performed": false
  },
  "typed_form": {
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
  "usage": {
    "candidatesTokenCount": 449,
    "promptTokenCount": 2845,
    "thoughtsTokenCount": 587,
    "totalTokenCount": 3881
  }
}
```

Result:

```json
{
  "correction_used": false,
  "exact_expected_outcome": true,
  "v61_terminal_status": "admitted",
  "v6_terminal_status": "admitted_after_correction"
}
```

## 9. b-resize-explicit

Authored-synthetic input:

- Resize Margaret Thompson's booking to 30 minutes.

### Turn 1 - completed

```json
{
  "proofreader": {
    "admitted_operator_ids": [
      "prepare_resize_proposal"
    ],
    "disposition": "admit",
    "safe_repairs": [],
    "violations": [],
    "wire_safe_repairs": []
  },
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
    "receptionist_response": "I'm preparing a proposal to resize Margaret Thompson's booking to 30 minutes for your review.",
    "violations": []
  },
  "release": {
    "atomic_release": true,
    "human_gate": true,
    "released_field_manifest": [
      "$.final_output.api_spine_operation_id",
      "$.final_output.appointment_ref",
      "$.final_output.candidate_slot_ids",
      "$.final_output.duration_minutes",
      "$.final_output.kind",
      "$.final_output.patient_ref",
      "$.final_output.practitioner_ref",
      "$.final_output.proposal_family",
      "$.final_output.requires_human_confirmation",
      "$.final_output.status",
      "$.final_output.warning_codes",
      "$.final_output.write_performed"
    ],
    "released_values": {
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
    "write_performed": false
  },
  "typed_form": {
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
  "usage": {
    "candidatesTokenCount": 240,
    "promptTokenCount": 2842,
    "thoughtsTokenCount": 533,
    "totalTokenCount": 3615
  }
}
```

Result:

```json
{
  "correction_used": false,
  "exact_expected_outcome": true,
  "v61_terminal_status": "admitted",
  "v6_terminal_status": "admitted"
}
```

## 10. b-cancel-remove

Authored-synthetic input:

- Remove Margaret Thompson's appointment from the diary.

### Turn 1 - completed

```json
{
  "proofreader": {
    "admitted_operator_ids": [
      "resolve_patient_reference",
      "read_selected_appointment",
      "prepare_cancel_proposal"
    ],
    "disposition": "admit",
    "safe_repairs": [],
    "violations": [],
    "wire_safe_repairs": []
  },
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
    "receptionist_response": "I'm preparing the cancellation proposal for Margaret Thompson's appointment for your review.",
    "violations": []
  },
  "release": {
    "atomic_release": true,
    "human_gate": true,
    "released_field_manifest": [
      "$.final_output.api_spine_operation_id",
      "$.final_output.appointment_ref",
      "$.final_output.candidate_slot_ids",
      "$.final_output.duration_minutes",
      "$.final_output.kind",
      "$.final_output.patient_ref",
      "$.final_output.practitioner_ref",
      "$.final_output.proposal_family",
      "$.final_output.requires_human_confirmation",
      "$.final_output.status",
      "$.final_output.warning_codes",
      "$.final_output.write_performed"
    ],
    "released_values": {
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
    "write_performed": false
  },
  "typed_form": {
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
  "usage": {
    "candidatesTokenCount": 392,
    "promptTokenCount": 2827,
    "thoughtsTokenCount": 677,
    "totalTokenCount": 3896
  }
}
```

Result:

```json
{
  "correction_used": false,
  "exact_expected_outcome": true,
  "v61_terminal_status": "admitted",
  "v6_terminal_status": "admitted_after_correction"
}
```

## 11. b-cancel-calloff

Authored-synthetic input:

- Call off Margaret's appointment.

### Turn 1 - completed

```json
{
  "proofreader": {
    "admitted_operator_ids": [
      "resolve_patient_reference",
      "read_selected_appointment",
      "prepare_cancel_proposal"
    ],
    "disposition": "admit",
    "safe_repairs": [],
    "violations": [],
    "wire_safe_repairs": []
  },
  "receptionist_output": {
    "decision_note": "Intent cancel: The user requested to cancel an appointment.",
    "disposition": "admit",
    "evidence_utterance_indices": [
      0
    ],
    "hidden_reasoning": false,
    "natural_response_parsed_into_form": false,
    "product_delivered": false,
    "raw_provider_response": false,
    "receptionist_response": "I'm preparing the cancellation request for Margaret's appointment for review. No booking was changed.",
    "violations": []
  },
  "release": {
    "atomic_release": true,
    "human_gate": true,
    "released_field_manifest": [
      "$.final_output.api_spine_operation_id",
      "$.final_output.appointment_ref",
      "$.final_output.candidate_slot_ids",
      "$.final_output.duration_minutes",
      "$.final_output.kind",
      "$.final_output.patient_ref",
      "$.final_output.practitioner_ref",
      "$.final_output.proposal_family",
      "$.final_output.requires_human_confirmation",
      "$.final_output.status",
      "$.final_output.warning_codes",
      "$.final_output.write_performed"
    ],
    "released_values": {
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
    "write_performed": false
  },
  "typed_form": {
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
  "usage": {
    "candidatesTokenCount": 394,
    "promptTokenCount": 2820,
    "thoughtsTokenCount": 494,
    "totalTokenCount": 3708
  }
}
```

Result:

```json
{
  "correction_used": false,
  "exact_expected_outcome": true,
  "v61_terminal_status": "admitted",
  "v6_terminal_status": "admitted"
}
```

## 12. b-cancel-takeout

Authored-synthetic input:

- Take Margaret Thompson's appointment out.

### Turn 1 - completed

```json
{
  "proofreader": {
    "admitted_operator_ids": [
      "resolve_patient_reference",
      "read_selected_appointment",
      "prepare_cancel_proposal"
    ],
    "disposition": "admit",
    "safe_repairs": [],
    "violations": [],
    "wire_safe_repairs": []
  },
  "receptionist_output": {
    "decision_note": "Intent cancel: User explicitly requested to 'take out' an appointment.",
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
    "atomic_release": true,
    "human_gate": true,
    "released_field_manifest": [
      "$.final_output.api_spine_operation_id",
      "$.final_output.appointment_ref",
      "$.final_output.candidate_slot_ids",
      "$.final_output.duration_minutes",
      "$.final_output.kind",
      "$.final_output.patient_ref",
      "$.final_output.practitioner_ref",
      "$.final_output.proposal_family",
      "$.final_output.requires_human_confirmation",
      "$.final_output.status",
      "$.final_output.warning_codes",
      "$.final_output.write_performed"
    ],
    "released_values": {
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
    "write_performed": false
  },
  "typed_form": {
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
  "usage": {
    "candidatesTokenCount": 393,
    "promptTokenCount": 2819,
    "thoughtsTokenCount": 641,
    "totalTokenCount": 3853
  }
}
```

Result:

```json
{
  "correction_used": false,
  "exact_expected_outcome": true,
  "v61_terminal_status": "admitted",
  "v6_terminal_status": "admitted"
}
```

## 13. b-status-complete

Authored-synthetic input:

- Set Margaret Thompson's appointment to completed.

### Turn 1 - completed

```json
{
  "proofreader": {
    "admitted_operator_ids": [
      "resolve_patient_reference",
      "read_selected_appointment",
      "prepare_status_proposal"
    ],
    "disposition": "admit",
    "safe_repairs": [],
    "violations": [],
    "wire_safe_repairs": []
  },
  "receptionist_output": {
    "decision_note": "Intent status_change: The user explicitly requested to set the status of an appointment.",
    "disposition": "admit",
    "evidence_utterance_indices": [
      0
    ],
    "hidden_reasoning": false,
    "natural_response_parsed_into_form": false,
    "product_delivered": false,
    "raw_provider_response": false,
    "receptionist_response": "I am preparing the request to change the status of Margaret Thompson's appointment to completed for review. No booking was changed.",
    "violations": []
  },
  "release": {
    "atomic_release": true,
    "human_gate": true,
    "released_field_manifest": [
      "$.final_output.api_spine_operation_id",
      "$.final_output.appointment_ref",
      "$.final_output.candidate_slot_ids",
      "$.final_output.duration_minutes",
      "$.final_output.kind",
      "$.final_output.patient_ref",
      "$.final_output.practitioner_ref",
      "$.final_output.proposal_family",
      "$.final_output.requires_human_confirmation",
      "$.final_output.status",
      "$.final_output.warning_codes",
      "$.final_output.write_performed"
    ],
    "released_values": {
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
    "write_performed": false
  },
  "typed_form": {
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
  "usage": {
    "candidatesTokenCount": 453,
    "promptTokenCount": 2841,
    "thoughtsTokenCount": 309,
    "totalTokenCount": 3603
  }
}
```

Result:

```json
{
  "correction_used": false,
  "exact_expected_outcome": true,
  "v61_terminal_status": "admitted",
  "v6_terminal_status": "admitted"
}
```

## 14. b-status-arrived

Authored-synthetic input:

- Update Margaret Thompson's status to arrived.

### Turn 1 - completed

```json
{
  "proofreader": {
    "admitted_operator_ids": [
      "prepare_status_proposal"
    ],
    "disposition": "admit",
    "safe_repairs": [],
    "violations": [],
    "wire_safe_repairs": []
  },
  "receptionist_output": {
    "decision_note": "Intent status_change: The user requested to update the status of an appointment.",
    "disposition": "admit",
    "evidence_utterance_indices": [
      0
    ],
    "hidden_reasoning": false,
    "natural_response_parsed_into_form": false,
    "product_delivered": false,
    "raw_provider_response": false,
    "receptionist_response": "I am preparing the proposal to update the status of the selected appointment to arrived for review. No booking was changed.",
    "violations": []
  },
  "release": {
    "atomic_release": true,
    "human_gate": true,
    "released_field_manifest": [
      "$.final_output.api_spine_operation_id",
      "$.final_output.appointment_ref",
      "$.final_output.candidate_slot_ids",
      "$.final_output.duration_minutes",
      "$.final_output.kind",
      "$.final_output.patient_ref",
      "$.final_output.practitioner_ref",
      "$.final_output.proposal_family",
      "$.final_output.requires_human_confirmation",
      "$.final_output.status",
      "$.final_output.warning_codes",
      "$.final_output.write_performed"
    ],
    "released_values": {
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
    "write_performed": false
  },
  "typed_form": {
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
  "usage": {
    "candidatesTokenCount": 248,
    "promptTokenCount": 2839,
    "thoughtsTokenCount": 688,
    "totalTokenCount": 3775
  }
}
```

Result:

```json
{
  "correction_used": false,
  "exact_expected_outcome": true,
  "v61_terminal_status": "admitted",
  "v6_terminal_status": "admitted"
}
```

## 15. b-clarify-details

Authored-synthetic input:

- Margaret Thompson with Dr Shera tomorrow at 2:30 pm for 15 minutes.

### Turn 1 - completed

```json
{
  "proofreader": {
    "admitted_operator_ids": [],
    "disposition": "revision_required",
    "safe_repairs": [],
    "violations": [
      {
        "code": "receptionist_response_missing_review_boundary",
        "path": "$.receptionist_response"
      },
      {
        "code": "receptionist_response_goal_mismatch",
        "path": "$.receptionist_response"
      }
    ],
    "wire_safe_repairs": []
  },
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
        "code": "receptionist_response_missing_review_boundary",
        "path": "$.receptionist_response"
      },
      {
        "code": "receptionist_response_goal_mismatch",
        "path": "$.receptionist_response"
      }
    ]
  },
  "release": null,
  "typed_form": {
    "goal_code": 6,
    "steps": [
      {
        "operator_code": 13,
        "source_refs": []
      }
    ],
    "version_code": 3
  },
  "usage": {
    "candidatesTokenCount": 165,
    "promptTokenCount": 2934,
    "thoughtsTokenCount": 438,
    "totalTokenCount": 3537
  }
}
```

### Turn 2 - completed

```json
{
  "proofreader": {
    "admitted_operator_ids": [
      "request_clarification"
    ],
    "disposition": "admit",
    "safe_repairs": [],
    "violations": [],
    "wire_safe_repairs": []
  },
  "receptionist_output": {
    "decision_note": "Intent clarification: Missing action verb.",
    "disposition": "admit",
    "evidence_utterance_indices": [
      0
    ],
    "hidden_reasoning": false,
    "natural_response_parsed_into_form": false,
    "product_delivered": false,
    "raw_provider_response": false,
    "receptionist_response": "I see the details for Margaret Thompson's appointment with Dr. Shera tomorrow at 2:30 PM for 15 minutes. Could you please clarify what you would like to do with this appointment? I'll prepare this for review; no booking was changed.",
    "violations": []
  },
  "release": {
    "atomic_release": true,
    "human_gate": true,
    "released_field_manifest": [
      "$.final_output.api_spine_operation_id",
      "$.final_output.appointment_ref",
      "$.final_output.candidate_slot_ids",
      "$.final_output.duration_minutes",
      "$.final_output.kind",
      "$.final_output.patient_ref",
      "$.final_output.practitioner_ref",
      "$.final_output.proposal_family",
      "$.final_output.requires_human_confirmation",
      "$.final_output.status",
      "$.final_output.warning_codes",
      "$.final_output.write_performed"
    ],
    "released_values": {
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
    "write_performed": false
  },
  "typed_form": {
    "goal_code": 6,
    "steps": [
      {
        "operator_code": 13,
        "source_refs": []
      }
    ],
    "version_code": 3
  },
  "usage": {
    "candidatesTokenCount": 173,
    "promptTokenCount": 3154,
    "thoughtsTokenCount": 475,
    "totalTokenCount": 3802
  }
}
```

Result:

```json
{
  "correction_used": true,
  "exact_expected_outcome": true,
  "v61_terminal_status": "admitted_after_correction",
  "v6_terminal_status": "admitted"
}
```
