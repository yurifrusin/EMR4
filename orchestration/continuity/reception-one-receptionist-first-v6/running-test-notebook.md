# Reception One v6 Running Test Notebook

Status: complete
Study: receptionist-first v6 paired development comparison
Cases closed: 24 / 24
Provider calls consumed: 27 / 48
Usage: 69776 prompt, 9368 visible candidate, 16699 thinking, 95843 total tokens

This is a sanitized comparison notebook, not a raw provider log. Full prompts, raw provider packets, credentials, API-key information and hidden chain-of-thought are excluded.

## 1. b-create-arrange

### Authored-synthetic input

- `0` — Arrange an appointment for Margaret Thompson with Dr Shera tomorrow at 2:30 pm for 15 minutes.

### v6 turns

#### Turn 1 — completed

Natural receptionist output:

```json
{
  "decision_note": "Intent create: All necessary information for creating an appointment is present.",
  "disposition": "admit",
  "evidence_utterance_indices": [
    0
  ],
  "hidden_reasoning": false,
  "natural_response_parsed_into_form": false,
  "product_delivered": false,
  "raw_provider_response": false,
  "receptionist_response": "I am preparing the details for an appointment for Margaret Thompson with Dr Shera tomorrow at 2:30 pm for 15 minutes for your review.",
  "violations": []
}
```

Typed form:

```json
{
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
}
```

Proofreader and usage:

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
    "write_performed": false
  },
  "usage": {
    "candidatesTokenCount": 853,
    "promptTokenCount": 2724,
    "thoughtsTokenCount": 780,
    "totalTokenCount": 4357
  }
}
```

### Paired result

```json
{
  "closed_v5": {
    "correction_used": false,
    "expected_safe_outcome": true,
    "final_violation_codes": [],
    "operator_note": {
      "audit_only": true,
      "disposition": "admit",
      "note_sha256": "sha256:4c2ff5e3a97af791f9f1cf237072133febbc20f13e9d3bf542a213db9d5f2ca1",
      "operator_note": "Review proposal for new appointment, no booking was changed.",
      "parsed_into_plan": false,
      "product_delivered": false,
      "reason_codes": [],
      "retained_utf8_bytes": 60
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
      "program_hash": "sha256:2a578b045adc5f217079b5d3025b3d66627ab37735ad643f6e1b5d9517d89e0b",
      "raw_provider_response": false
    }
  },
  "v6": {
    "correction_used": false,
    "expected_safe_outcome": true,
    "terminal_status": "admitted"
  }
}
```

## 2. b-create-alias

### Authored-synthetic input

- `0` — Could you book Margaret with Shera tomorrow at 3 pm for 15 minutes?

### v6 turns

#### Turn 1 — completed

Natural receptionist output:

```json
{
  "decision_note": "Intent create: All necessary information for creating an appointment proposal is present.",
  "disposition": "admit",
  "evidence_utterance_indices": [
    0
  ],
  "hidden_reasoning": false,
  "natural_response_parsed_into_form": false,
  "product_delivered": false,
  "raw_provider_response": false,
  "receptionist_response": "I am preparing a proposal for Margaret to see Shera tomorrow at 3 PM for 15 minutes. This will be sent for review; no booking was changed.",
  "violations": []
}
```

Typed form:

```json
{
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
}
```

Proofreader and usage:

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
  "usage": {
    "candidatesTokenCount": 856,
    "promptTokenCount": 2724,
    "thoughtsTokenCount": 679,
    "totalTokenCount": 4259
  }
}
```

### Paired result

```json
{
  "closed_v5": {
    "correction_used": false,
    "expected_safe_outcome": true,
    "final_violation_codes": [],
    "operator_note": {
      "audit_only": true,
      "disposition": "admit",
      "note_sha256": "sha256:6686661e508d2244fbc33fc0170228525746afad39e3a36f1822e0c28e6b93d8",
      "operator_note": "Reviewing proposal, no booking was changed.",
      "parsed_into_plan": false,
      "product_delivered": false,
      "reason_codes": [],
      "retained_utf8_bytes": 43
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
      "program_hash": "sha256:66d21473211dc9341fd6d4d362ec05b1c96335a6127c7769a5cca10d298f95b7",
      "raw_provider_response": false
    }
  },
  "v6": {
    "correction_used": false,
    "expected_safe_outcome": true,
    "terminal_status": "admitted"
  }
}
```

## 3. b-create-preface

### Authored-synthetic input

- `0` — Diary request; details may need clarifying.
- `1` — Please schedule an appointment for Margaret Thompson with Dr Shera tomorrow at 2:30 pm for 15 minutes.

### v6 turns

#### Turn 1 — completed

Natural receptionist output:

```json
{
  "decision_note": "Intent create: The user explicitly requested to schedule an appointment with all necessary details.",
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
}
```

Typed form:

```json
{
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
}
```

Proofreader and usage:

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
    "write_performed": false
  },
  "usage": {
    "candidatesTokenCount": 870,
    "promptTokenCount": 2742,
    "thoughtsTokenCount": 750,
    "totalTokenCount": 4362
  }
}
```

### Paired result

```json
{
  "closed_v5": {
    "correction_used": false,
    "expected_safe_outcome": false,
    "final_violation_codes": [],
    "operator_note": {
      "audit_only": true,
      "disposition": "admit",
      "note_sha256": "sha256:37effbe5d93f1bd0c3fa21472ff83c9e15bd267b06e934daed2c495178094287",
      "operator_note": "Reviewing proposal for new appointment, no booking was changed.",
      "parsed_into_plan": false,
      "product_delivered": false,
      "reason_codes": [],
      "retained_utf8_bytes": 63
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
      "program_hash": "sha256:709eea13dd08d1b2793b368ea7b098f249c3e0884e6d4df14518c099b4fb9662",
      "raw_provider_response": false
    }
  },
  "v6": {
    "correction_used": false,
    "expected_safe_outcome": true,
    "terminal_status": "admitted"
  }
}
```

## 4. b-create-correct

### Authored-synthetic input

- `0` — Book an appointment for Margaret Thompson with Dr Shera tomorrow at 2:30 pm for 15 minutes.
- `1` — Actually, make it 3 pm instead.

### v6 turns

#### Turn 1 — response_rejected_before_candidate

Natural receptionist output:

```json
null
```

Typed form:

```json
null
```

Proofreader and usage:

```json
{
  "proofreader": {
    "admitted_operator_ids": [],
    "disposition": "not_reached",
    "safe_repairs": [],
    "violations": [],
    "wire_safe_repairs": []
  },
  "release": null,
  "usage": {}
}
```

### Paired result

```json
{
  "closed_v5": {
    "correction_used": false,
    "expected_safe_outcome": true,
    "final_violation_codes": [],
    "operator_note": {
      "audit_only": true,
      "disposition": "admit",
      "note_sha256": "sha256:2dacbc9a92020e0a544da973fa35c4609fb7d9f186dca7af06b91f8ae12cb957",
      "operator_note": "Reviewing proposal for new booking, no booking was changed.",
      "parsed_into_plan": false,
      "product_delivered": false,
      "reason_codes": [],
      "retained_utf8_bytes": 59
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
      "program_hash": "sha256:3f11d2fec8081a46347dc844a4125bec645b7245decb385e42d2efbd6f539360",
      "raw_provider_response": false
    }
  },
  "v6": {
    "correction_used": false,
    "expected_safe_outcome": false,
    "terminal_status": "terminal_no_release"
  }
}
```

## 5. b-move-resched

### Authored-synthetic input

- `0` — Reschedule Margaret Thompson's appointment to tomorrow at 3 pm.

### v6 turns

#### Turn 1 — completed

Natural receptionist output:

```json
{
  "decision_note": "Intent clarification: The specific appointment to be moved is missing.",
  "disposition": "admit",
  "evidence_utterance_indices": [
    0
  ],
  "hidden_reasoning": false,
  "natural_response_parsed_into_form": false,
  "product_delivered": false,
  "raw_provider_response": false,
  "receptionist_response": "I need to know which specific appointment for Margaret Thompson you would like to reschedule. Please provide more details about the appointment.",
  "violations": []
}
```

Typed form:

```json
{
  "goal_code": 6,
  "steps": [
    {
      "operator_code": 13,
      "source_refs": []
    }
  ],
  "version_code": 3
}
```

Proofreader and usage:

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
  "usage": {
    "candidatesTokenCount": 149,
    "promptTokenCount": 2675,
    "thoughtsTokenCount": 293,
    "totalTokenCount": 3117
  }
}
```

### Paired result

```json
{
  "closed_v5": {
    "correction_used": true,
    "expected_safe_outcome": false,
    "final_violation_codes": [
      "source_type_mismatch"
    ],
    "operator_note": {
      "audit_only": true,
      "disposition": "admit",
      "note_sha256": "sha256:b273e3a0c0280bd6c173fdae070611f5fa23c667ba1b472df09625eafe15afeb",
      "operator_note": "Review of proposed changes, no booking was changed.",
      "parsed_into_plan": false,
      "product_delivered": false,
      "reason_codes": [],
      "retained_utf8_bytes": 51
    },
    "release": null,
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
            "operator_code": 1,
            "source_refs": [
              {
                "binding_code": -1,
                "kind": "prior_output",
                "prior_output_name": "practitioner",
                "prior_step_index": 1
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
                "prior_step_index": 3
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
                "prior_step_index": 4
              }
            ]
          }
        ],
        "version_code": 3
      },
      "operator_note_excluded": true,
      "program_hash": "sha256:60c60879f7d8e057b5b35c8bb6a3f7ce747dd834b540db8a1c87190becacc044",
      "raw_provider_response": false
    }
  },
  "v6": {
    "correction_used": false,
    "expected_safe_outcome": false,
    "terminal_status": "admitted"
  }
}
```

## 6. b-move-shift

### Authored-synthetic input

- `0` — Shift Margaret's appointment to tomorrow at 2:30 pm.

### v6 turns

#### Turn 1 — completed

Natural receptionist output:

```json
{
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
      "code": "decision_note_goal_mismatch",
      "path": "$.decision_note"
    }
  ]
}
```

Typed form:

```json
{
  "goal_code": 6,
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
      "operator_code": 13,
      "source_refs": []
    }
  ],
  "version_code": 3
}
```

Proofreader and usage:

```json
{
  "proofreader": {
    "admitted_operator_ids": [],
    "disposition": "revision_required",
    "safe_repairs": [],
    "violations": [
      {
        "code": "decision_note_goal_mismatch",
        "path": "$.decision_note"
      }
    ],
    "wire_safe_repairs": []
  },
  "release": null,
  "usage": {
    "candidatesTokenCount": 212,
    "promptTokenCount": 2673,
    "thoughtsTokenCount": 447,
    "totalTokenCount": 3332
  }
}
```

#### Turn 2 — completed

Natural receptionist output:

```json
{
  "decision_note": "Intent clarification: The request is missing a specific appointment to move.",
  "disposition": "admit",
  "evidence_utterance_indices": [
    0
  ],
  "hidden_reasoning": false,
  "natural_response_parsed_into_form": false,
  "product_delivered": false,
  "raw_provider_response": false,
  "receptionist_response": "I can prepare a proposal to move an appointment for Margaret. Could you please specify which of her appointments you would like to move?",
  "violations": []
}
```

Typed form:

```json
{
  "goal_code": 6,
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
      "operator_code": 13,
      "source_refs": []
    }
  ],
  "version_code": 3
}
```

Proofreader and usage:

```json
{
  "proofreader": {
    "admitted_operator_ids": [
      "resolve_patient_reference",
      "request_clarification"
    ],
    "disposition": "admit",
    "safe_repairs": [],
    "violations": [],
    "wire_safe_repairs": []
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
  "usage": {
    "candidatesTokenCount": 226,
    "promptTokenCount": 2884,
    "thoughtsTokenCount": 898,
    "totalTokenCount": 4008
  }
}
```

### Paired result

```json
{
  "closed_v5": {
    "correction_used": true,
    "expected_safe_outcome": false,
    "final_violation_codes": [
      "required_source_omitted"
    ],
    "operator_note": {
      "audit_only": true,
      "disposition": "admit",
      "note_sha256": "sha256:a2ac24a8f7a9bc3d01ec3824023ff7e921f881a1676bc19c38eac3fe0df0493a",
      "operator_note": "Review of proposed change to an existing booking, no booking was changed.",
      "parsed_into_plan": false,
      "product_delivered": false,
      "reason_codes": [],
      "retained_utf8_bytes": 73
    },
    "release": null,
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
            "operator_code": 4,
            "source_refs": [
              {
                "binding_code": -1,
                "kind": "prior_output",
                "prior_output_name": "patient",
                "prior_step_index": 0
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
                "kind": "omit",
                "prior_output_name": "none",
                "prior_step_index": -1
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
                "binding_code": 1,
                "kind": "binding",
                "prior_output_name": "none",
                "prior_step_index": -1
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
      "program_hash": "sha256:03c38cd71978c7b6f9c4500139ee2d85b0b91680c3999f6ae2f80ca3f9797d43",
      "raw_provider_response": false
    }
  },
  "v6": {
    "correction_used": true,
    "expected_safe_outcome": false,
    "terminal_status": "admitted_after_correction"
  }
}
```

## 7. b-move-change

### Authored-synthetic input

- `0` — Change the time of Margaret Thompson's appointment to tomorrow at 3 pm.

### v6 turns

#### Turn 1 — completed

Natural receptionist output:

```json
{
  "decision_note": "Intent clarification: The specific appointment to be moved is not identified.",
  "disposition": "admit",
  "evidence_utterance_indices": [
    0
  ],
  "hidden_reasoning": false,
  "natural_response_parsed_into_form": false,
  "product_delivered": false,
  "raw_provider_response": false,
  "receptionist_response": "I can help change an appointment for Margaret Thompson to tomorrow at 3 PM. Could you please specify which appointment you would like to change?",
  "violations": []
}
```

Typed form:

```json
{
  "goal_code": 6,
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
      "operator_code": 4,
      "source_refs": [
        {
          "binding_code": -1,
          "kind": "prior_output",
          "prior_output_name": "patient",
          "prior_step_index": 0
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
}
```

Proofreader and usage:

```json
{
  "proofreader": {
    "admitted_operator_ids": [
      "resolve_patient_reference",
      "read_patient_appointment_timeline",
      "resolve_date_expression",
      "request_clarification"
    ],
    "disposition": "admit",
    "safe_repairs": [],
    "violations": [],
    "wire_safe_repairs": []
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
  "usage": {
    "candidatesTokenCount": 382,
    "promptTokenCount": 2681,
    "thoughtsTokenCount": 590,
    "totalTokenCount": 3653
  }
}
```

### Paired result

```json
{
  "closed_v5": {
    "correction_used": true,
    "expected_safe_outcome": true,
    "final_violation_codes": [],
    "operator_note": {
      "audit_only": true,
      "disposition": "admit",
      "note_sha256": "sha256:9a70a0f80266f4ec2ac481341cf329f69d6a59d7cbad131836aa7bd7ca362dd1",
      "operator_note": "Reviewing proposal for clarification, no booking was changed.",
      "parsed_into_plan": false,
      "product_delivered": false,
      "reason_codes": [],
      "retained_utf8_bytes": 61
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
      "program_hash": "sha256:0f8ddf330d80b5b11a4b751e4cf963d1ec81337b5db0f3137636c37e41f68dc9",
      "raw_provider_response": false
    }
  },
  "v6": {
    "correction_used": false,
    "expected_safe_outcome": false,
    "terminal_status": "admitted"
  }
}
```

## 8. b-move-correct

### Authored-synthetic input

- `0` — Move Margaret Thompson's appointment to tomorrow at 2:30 pm.
- `1` — Actually, make it 3 pm instead.

### v6 turns

#### Turn 1 — completed

Natural receptionist output:

```json
{
  "decision_note": "Intent clarification: The specific appointment to move is missing.",
  "disposition": "admit",
  "evidence_utterance_indices": [
    0,
    1
  ],
  "hidden_reasoning": false,
  "natural_response_parsed_into_form": false,
  "product_delivered": false,
  "raw_provider_response": false,
  "receptionist_response": "I can help with that. Could you please specify which of Margaret Thompson's appointments you would like to move?",
  "violations": []
}
```

Typed form:

```json
{
  "goal_code": 6,
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
      "operator_code": 13,
      "source_refs": []
    }
  ],
  "version_code": 3
}
```

Proofreader and usage:

```json
{
  "proofreader": {
    "admitted_operator_ids": [
      "resolve_patient_reference",
      "request_clarification"
    ],
    "disposition": "admit",
    "safe_repairs": [],
    "violations": [],
    "wire_safe_repairs": []
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
  "usage": {
    "candidatesTokenCount": 226,
    "promptTokenCount": 2693,
    "thoughtsTokenCount": 662,
    "totalTokenCount": 3581
  }
}
```

### Paired result

```json
{
  "closed_v5": {
    "correction_used": true,
    "expected_safe_outcome": false,
    "final_violation_codes": [
      "required_source_omitted"
    ],
    "operator_note": {
      "audit_only": true,
      "disposition": "admit",
      "note_sha256": "sha256:6686661e508d2244fbc33fc0170228525746afad39e3a36f1822e0c28e6b93d8",
      "operator_note": "Reviewing proposal, no booking was changed.",
      "parsed_into_plan": false,
      "product_delivered": false,
      "reason_codes": [],
      "retained_utf8_bytes": 43
    },
    "release": null,
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
            "operator_code": 4,
            "source_refs": [
              {
                "binding_code": -1,
                "kind": "prior_output",
                "prior_output_name": "patient",
                "prior_step_index": 0
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
            "operator_code": 1,
            "source_refs": [
              {
                "binding_code": -1,
                "kind": "omit",
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
                "prior_step_index": 4
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
                "prior_step_index": 3
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
                "prior_step_index": 3
              },
              {
                "binding_code": -1,
                "kind": "prior_output",
                "prior_output_name": "candidates",
                "prior_step_index": 5
              }
            ]
          }
        ],
        "version_code": 3
      },
      "operator_note_excluded": true,
      "program_hash": "sha256:c6ea701b27d9e0715a00b84c2c8e4c97976c5a52a17e74c6f83e44441c347d0f",
      "raw_provider_response": false
    }
  },
  "v6": {
    "correction_used": false,
    "expected_safe_outcome": false,
    "terminal_status": "admitted"
  }
}
```

## 9. b-resize-long

### Authored-synthetic input

- `0` — Make Margaret Thompson's appointment longer, 30 minutes.

### v6 turns

#### Turn 1 — completed

Natural receptionist output:

```json
{
  "decision_note": "Intent clarification: missing appointment identifier.",
  "disposition": "admit",
  "evidence_utterance_indices": [
    0
  ],
  "hidden_reasoning": false,
  "natural_response_parsed_into_form": false,
  "product_delivered": false,
  "raw_provider_response": false,
  "receptionist_response": "I can prepare a proposal to make Margaret Thompson's appointment longer. Could you please specify which appointment you would like to resize?",
  "violations": []
}
```

Typed form:

```json
{
  "goal_code": 6,
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
      "operator_code": 13,
      "source_refs": []
    }
  ],
  "version_code": 3
}
```

Proofreader and usage:

```json
{
  "proofreader": {
    "admitted_operator_ids": [
      "resolve_patient_reference",
      "request_clarification"
    ],
    "disposition": "admit",
    "safe_repairs": [],
    "violations": [],
    "wire_safe_repairs": []
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
  "usage": {
    "candidatesTokenCount": 218,
    "promptTokenCount": 2639,
    "thoughtsTokenCount": 323,
    "totalTokenCount": 3180
  }
}
```

### Paired result

```json
{
  "closed_v5": {
    "correction_used": false,
    "expected_safe_outcome": true,
    "final_violation_codes": [],
    "operator_note": {
      "audit_only": true,
      "disposition": "admit",
      "note_sha256": "sha256:b32bdd4edddc02974f715c51b049bb95e2cc95b6d98861a1e965e99495823636",
      "operator_note": "Review proposal for resize, no booking was changed.",
      "parsed_into_plan": false,
      "product_delivered": false,
      "reason_codes": [],
      "retained_utf8_bytes": 51
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
            "operator_code": 4,
            "source_refs": [
              {
                "binding_code": -1,
                "kind": "prior_output",
                "prior_output_name": "patient",
                "prior_step_index": 0
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
                "prior_step_index": 2
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
      "program_hash": "sha256:0164c88a444514712849a955ceaf7e30a3f5172f0d60999f9e8a683f733c0fcc",
      "raw_provider_response": false
    }
  },
  "v6": {
    "correction_used": false,
    "expected_safe_outcome": false,
    "terminal_status": "admitted"
  }
}
```

## 10. b-resize-short

### Authored-synthetic input

- `0` — Shorten Margaret's appointment to 10 minutes.

### v6 turns

#### Turn 1 — completed

Natural receptionist output:

```json
{
  "decision_note": "Intent clarification: The specific appointment to be resized is missing.",
  "disposition": "admit",
  "evidence_utterance_indices": [
    0
  ],
  "hidden_reasoning": false,
  "natural_response_parsed_into_form": false,
  "product_delivered": false,
  "raw_provider_response": false,
  "receptionist_response": "I can help with that. Could you please specify which of Margaret's appointments you would like to shorten to 10 minutes?",
  "violations": []
}
```

Typed form:

```json
{
  "goal_code": 6,
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
      "operator_code": 13,
      "source_refs": []
    }
  ],
  "version_code": 3
}
```

Proofreader and usage:

```json
{
  "proofreader": {
    "admitted_operator_ids": [
      "resolve_patient_reference",
      "request_clarification"
    ],
    "disposition": "admit",
    "safe_repairs": [],
    "violations": [],
    "wire_safe_repairs": []
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
  "usage": {
    "candidatesTokenCount": 224,
    "promptTokenCount": 2632,
    "thoughtsTokenCount": 488,
    "totalTokenCount": 3344
  }
}
```

### Paired result

```json
{
  "closed_v5": {
    "correction_used": false,
    "expected_safe_outcome": true,
    "final_violation_codes": [],
    "operator_note": {
      "audit_only": true,
      "disposition": "admit",
      "note_sha256": "sha256:6686661e508d2244fbc33fc0170228525746afad39e3a36f1822e0c28e6b93d8",
      "operator_note": "Reviewing proposal, no booking was changed.",
      "parsed_into_plan": false,
      "product_delivered": false,
      "reason_codes": [],
      "retained_utf8_bytes": 43
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
            "operator_code": 4,
            "source_refs": [
              {
                "binding_code": -1,
                "kind": "prior_output",
                "prior_output_name": "patient",
                "prior_step_index": 0
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
                "prior_step_index": 2
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
      "program_hash": "sha256:4473477ccf9f78d6d643c1b9be5081128ecad20d8e9276ac17d07cc3f6cc827b",
      "raw_provider_response": false
    }
  },
  "v6": {
    "correction_used": false,
    "expected_safe_outcome": false,
    "terminal_status": "admitted"
  }
}
```

## 11. b-resize-give

### Authored-synthetic input

- `0` — Give them 30 minutes for Margaret Thompson's appointment.

### v6 turns

#### Turn 1 — completed

Natural receptionist output:

```json
{
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
      "code": "decision_note_goal_mismatch",
      "path": "$.decision_note"
    }
  ]
}
```

Typed form:

```json
{
  "goal_code": 6,
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
      "operator_code": 13,
      "source_refs": []
    }
  ],
  "version_code": 3
}
```

Proofreader and usage:

```json
{
  "proofreader": {
    "admitted_operator_ids": [],
    "disposition": "revision_required",
    "safe_repairs": [],
    "violations": [
      {
        "code": "decision_note_goal_mismatch",
        "path": "$.decision_note"
      }
    ],
    "wire_safe_repairs": []
  },
  "release": null,
  "usage": {
    "candidatesTokenCount": 222,
    "promptTokenCount": 2634,
    "thoughtsTokenCount": 632,
    "totalTokenCount": 3488
  }
}
```

#### Turn 2 — completed

Natural receptionist output:

```json
{
  "decision_note": "Intent clarification: missing appointment identifier.",
  "disposition": "admit",
  "evidence_utterance_indices": [
    0
  ],
  "hidden_reasoning": false,
  "natural_response_parsed_into_form": false,
  "product_delivered": false,
  "raw_provider_response": false,
  "receptionist_response": "I can prepare a proposal to change the duration of an appointment. Could you please specify which of Margaret Thompson's appointments you would like to change?",
  "violations": []
}
```

Typed form:

```json
{
  "goal_code": 6,
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
      "operator_code": 13,
      "source_refs": []
    }
  ],
  "version_code": 3
}
```

Proofreader and usage:

```json
{
  "proofreader": {
    "admitted_operator_ids": [
      "resolve_patient_reference",
      "request_clarification"
    ],
    "disposition": "admit",
    "safe_repairs": [],
    "violations": [],
    "wire_safe_repairs": []
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
  "usage": {
    "candidatesTokenCount": 222,
    "promptTokenCount": 2843,
    "thoughtsTokenCount": 803,
    "totalTokenCount": 3868
  }
}
```

### Paired result

```json
{
  "closed_v5": {
    "correction_used": false,
    "expected_safe_outcome": true,
    "final_violation_codes": [],
    "operator_note": {
      "audit_only": true,
      "disposition": "admit",
      "note_sha256": "sha256:6686661e508d2244fbc33fc0170228525746afad39e3a36f1822e0c28e6b93d8",
      "operator_note": "Reviewing proposal, no booking was changed.",
      "parsed_into_plan": false,
      "product_delivered": false,
      "reason_codes": [],
      "retained_utf8_bytes": 43
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
      "program_hash": "sha256:768224ce1778acb31c654b5a05be02b331489ecdfa71c67f656ae717486bfe86",
      "raw_provider_response": false
    }
  },
  "v6": {
    "correction_used": true,
    "expected_safe_outcome": false,
    "terminal_status": "admitted_after_correction"
  }
}
```

## 12. b-resize-explicit

### Authored-synthetic input

- `0` — Resize Margaret Thompson's booking to 30 minutes.

### v6 turns

#### Turn 1 — completed

Natural receptionist output:

```json
{
  "decision_note": "Intent clarification: missing specific appointment to resize.",
  "disposition": "admit",
  "evidence_utterance_indices": [
    0
  ],
  "hidden_reasoning": false,
  "natural_response_parsed_into_form": false,
  "product_delivered": false,
  "raw_provider_response": false,
  "receptionist_response": "I can help with that. I'm preparing the details for review, but I need to confirm which specific booking for Margaret Thompson you would like to resize.",
  "violations": []
}
```

Typed form:

```json
{
  "goal_code": 6,
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
      "operator_code": 13,
      "source_refs": []
    }
  ],
  "version_code": 3
}
```

Proofreader and usage:

```json
{
  "proofreader": {
    "admitted_operator_ids": [
      "resolve_patient_reference",
      "request_clarification"
    ],
    "disposition": "admit",
    "safe_repairs": [],
    "violations": [],
    "wire_safe_repairs": []
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
  "usage": {
    "candidatesTokenCount": 226,
    "promptTokenCount": 2631,
    "thoughtsTokenCount": 875,
    "totalTokenCount": 3732
  }
}
```

### Paired result

```json
{
  "closed_v5": {
    "correction_used": false,
    "expected_safe_outcome": true,
    "final_violation_codes": [],
    "operator_note": {
      "audit_only": true,
      "disposition": "admit",
      "note_sha256": "sha256:d7c1c8038ec869640a7d3c2c64333393433a6b36a8f49f013b37a3909d15bffa",
      "operator_note": "Review complete; no booking was changed.",
      "parsed_into_plan": false,
      "product_delivered": false,
      "reason_codes": [],
      "retained_utf8_bytes": 40
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
            "operator_code": 4,
            "source_refs": [
              {
                "binding_code": -1,
                "kind": "prior_output",
                "prior_output_name": "patient",
                "prior_step_index": 0
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
                "prior_step_index": 2
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
      "program_hash": "sha256:d611d0b285374e8615b7323795f84c394f1945ac6bddd625625d4750eecba6ea",
      "raw_provider_response": false
    }
  },
  "v6": {
    "correction_used": false,
    "expected_safe_outcome": false,
    "terminal_status": "admitted"
  }
}
```

## 13. b-cancel-remove

### Authored-synthetic input

- `0` — Remove Margaret Thompson's appointment from the diary.

### v6 turns

#### Turn 1 — completed

Natural receptionist output:

```json
{
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
      "code": "decision_note_goal_mismatch",
      "path": "$.decision_note"
    }
  ]
}
```

Typed form:

```json
{
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
      "operator_code": 4,
      "source_refs": [
        {
          "binding_code": -1,
          "kind": "prior_output",
          "prior_output_name": "patient",
          "prior_step_index": 0
        }
      ]
    },
    {
      "operator_code": 13,
      "source_refs": []
    }
  ],
  "version_code": 3
}
```

Proofreader and usage:

```json
{
  "proofreader": {
    "admitted_operator_ids": [],
    "disposition": "revision_required",
    "safe_repairs": [],
    "violations": [
      {
        "code": "decision_note_goal_mismatch",
        "path": "$.decision_note"
      }
    ],
    "wire_safe_repairs": []
  },
  "release": null,
  "usage": {
    "candidatesTokenCount": 301,
    "promptTokenCount": 2616,
    "thoughtsTokenCount": 831,
    "totalTokenCount": 3748
  }
}
```

#### Turn 2 — completed

Natural receptionist output:

```json
{
  "decision_note": "Intent clarification: The specific appointment to cancel is missing.",
  "disposition": "admit",
  "evidence_utterance_indices": [
    0
  ],
  "hidden_reasoning": false,
  "natural_response_parsed_into_form": false,
  "product_delivered": false,
  "raw_provider_response": false,
  "receptionist_response": "I can help with that, but I need to know which of Margaret Thompson's appointments you'd like to remove. I'll prepare this for review.",
  "violations": []
}
```

Typed form:

```json
{
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
      "operator_code": 4,
      "source_refs": [
        {
          "binding_code": -1,
          "kind": "prior_output",
          "prior_output_name": "patient",
          "prior_step_index": 0
        }
      ]
    },
    {
      "operator_code": 13,
      "source_refs": []
    }
  ],
  "version_code": 3
}
```

Proofreader and usage:

```json
{
  "proofreader": {
    "admitted_operator_ids": [
      "resolve_patient_reference",
      "read_patient_appointment_timeline",
      "request_clarification"
    ],
    "disposition": "admit",
    "safe_repairs": [],
    "violations": [],
    "wire_safe_repairs": []
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
  "usage": {
    "candidatesTokenCount": 306,
    "promptTokenCount": 2861,
    "thoughtsTokenCount": 872,
    "totalTokenCount": 4039
  }
}
```

### Paired result

```json
{
  "closed_v5": {
    "correction_used": false,
    "expected_safe_outcome": true,
    "final_violation_codes": [],
    "operator_note": {
      "audit_only": true,
      "disposition": "admit",
      "note_sha256": "sha256:6686661e508d2244fbc33fc0170228525746afad39e3a36f1822e0c28e6b93d8",
      "operator_note": "Reviewing proposal, no booking was changed.",
      "parsed_into_plan": false,
      "product_delivered": false,
      "reason_codes": [],
      "retained_utf8_bytes": 43
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
      "program_hash": "sha256:f3bf45d97ae6d1b17dfe5ffc78ab9508e130efe869ce7b628d261e90ae2042b5",
      "raw_provider_response": false
    }
  },
  "v6": {
    "correction_used": true,
    "expected_safe_outcome": false,
    "terminal_status": "admitted_after_correction"
  }
}
```

## 14. b-cancel-calloff

### Authored-synthetic input

- `0` — Call off Margaret's appointment.

### v6 turns

#### Turn 1 — completed

Natural receptionist output:

```json
{
  "decision_note": "Intent clarification: Missing specific appointment.",
  "disposition": "admit",
  "evidence_utterance_indices": [
    0
  ],
  "hidden_reasoning": false,
  "natural_response_parsed_into_form": false,
  "product_delivered": false,
  "raw_provider_response": false,
  "receptionist_response": "I can help with that. Could you please specify which of Margaret's appointments you would like to cancel?",
  "violations": []
}
```

Typed form:

```json
{
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
}
```

Proofreader and usage:

```json
{
  "proofreader": {
    "admitted_operator_ids": [
      "resolve_patient_reference",
      "request_clarification"
    ],
    "disposition": "admit",
    "safe_repairs": [],
    "violations": [],
    "wire_safe_repairs": []
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
  "usage": {
    "candidatesTokenCount": 216,
    "promptTokenCount": 2609,
    "thoughtsTokenCount": 367,
    "totalTokenCount": 3192
  }
}
```

### Paired result

```json
{
  "closed_v5": {
    "correction_used": false,
    "expected_safe_outcome": false,
    "final_violation_codes": [],
    "operator_note": {
      "audit_only": true,
      "disposition": "admit",
      "note_sha256": "sha256:1c35c231cbbd67c23dbf6c11acc8e962e2f4ab2c4192b2a46627af3dc9f3ed8b",
      "operator_note": "Review of proposed change completed, no booking was changed.",
      "parsed_into_plan": false,
      "product_delivered": false,
      "reason_codes": [],
      "retained_utf8_bytes": 60
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
            "operator_code": 4,
            "source_refs": [
              {
                "binding_code": -1,
                "kind": "prior_output",
                "prior_output_name": "patient",
                "prior_step_index": 0
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
      "program_hash": "sha256:2cab9970533257e698ccf22b650a7232953804fd3455628b3f937ee0a9938b3a",
      "raw_provider_response": false
    }
  },
  "v6": {
    "correction_used": false,
    "expected_safe_outcome": false,
    "terminal_status": "admitted"
  }
}
```

## 15. b-cancel-takeout

### Authored-synthetic input

- `0` — Take Margaret Thompson's appointment out.

### v6 turns

#### Turn 1 — completed

Natural receptionist output:

```json
{
  "decision_note": "Intent clarification: The specific appointment to cancel is missing.",
  "disposition": "admit",
  "evidence_utterance_indices": [
    0
  ],
  "hidden_reasoning": false,
  "natural_response_parsed_into_form": false,
  "product_delivered": false,
  "raw_provider_response": false,
  "receptionist_response": "I can help with that. Could you please specify which of Margaret Thompson's appointments you would like to cancel?",
  "violations": []
}
```

Typed form:

```json
{
  "goal_code": 6,
  "steps": [
    {
      "operator_code": 13,
      "source_refs": []
    }
  ],
  "version_code": 3
}
```

Proofreader and usage:

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
  "usage": {
    "candidatesTokenCount": 144,
    "promptTokenCount": 2608,
    "thoughtsTokenCount": 282,
    "totalTokenCount": 3034
  }
}
```

### Paired result

```json
{
  "closed_v5": {
    "correction_used": true,
    "expected_safe_outcome": false,
    "final_violation_codes": [],
    "operator_note": {
      "audit_only": true,
      "disposition": "admit",
      "note_sha256": "sha256:6686661e508d2244fbc33fc0170228525746afad39e3a36f1822e0c28e6b93d8",
      "operator_note": "Reviewing proposal, no booking was changed.",
      "parsed_into_plan": false,
      "product_delivered": false,
      "reason_codes": [],
      "retained_utf8_bytes": 43
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
    "terminal_status": "admitted_after_correction",
    "typed_program": {
      "explicit_source_form": {
        "goal_code": 1,
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
            "operator_code": 4,
            "source_refs": [
              {
                "binding_code": -1,
                "kind": "prior_output",
                "prior_output_name": "patient",
                "prior_step_index": 0
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
      "program_hash": "sha256:edafa743985b7c4d9eb9f7095b7a411006963166e5c4bb5c9af9f856eb6e1058",
      "raw_provider_response": false
    }
  },
  "v6": {
    "correction_used": false,
    "expected_safe_outcome": false,
    "terminal_status": "admitted"
  }
}
```

## 16. b-status-complete

### Authored-synthetic input

- `0` — Set Margaret Thompson's appointment to completed.

### v6 turns

#### Turn 1 — completed

Natural receptionist output:

```json
{
  "decision_note": "Intent clarification: missing meaning of appointment.",
  "disposition": "admit",
  "evidence_utterance_indices": [
    0
  ],
  "hidden_reasoning": false,
  "natural_response_parsed_into_form": false,
  "product_delivered": false,
  "raw_provider_response": false,
  "receptionist_response": "I can help with that. Which of Margaret Thompson's appointments would you like to set to completed?",
  "violations": []
}
```

Typed form:

```json
{
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
}
```

Proofreader and usage:

```json
{
  "proofreader": {
    "admitted_operator_ids": [
      "resolve_patient_reference",
      "request_clarification"
    ],
    "disposition": "admit",
    "safe_repairs": [],
    "violations": [],
    "wire_safe_repairs": []
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
  "usage": {
    "candidatesTokenCount": 214,
    "promptTokenCount": 2630,
    "thoughtsTokenCount": 834,
    "totalTokenCount": 3678
  }
}
```

### Paired result

```json
{
  "closed_v5": {
    "correction_used": false,
    "expected_safe_outcome": true,
    "final_violation_codes": [],
    "operator_note": {
      "audit_only": true,
      "disposition": "admit",
      "note_sha256": "sha256:5c2d921a149afc25d0dcbea6fe2e6ffe7f4c6704a9525e5d25ec01c673e65fbc",
      "operator_note": "Reviewing proposed status change, no booking was changed.",
      "parsed_into_plan": false,
      "product_delivered": false,
      "reason_codes": [],
      "retained_utf8_bytes": 57
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
      "program_hash": "sha256:22180c81a5008d00ed304ef72665df698813e33b2344e7d7ed606ff4cea153d1",
      "raw_provider_response": false
    }
  },
  "v6": {
    "correction_used": false,
    "expected_safe_outcome": false,
    "terminal_status": "admitted"
  }
}
```

## 17. b-status-arrived

### Authored-synthetic input

- `0` — Update Margaret Thompson's status to arrived.

### v6 turns

#### Turn 1 — completed

Natural receptionist output:

```json
{
  "decision_note": "Intent clarification: missing meaning.",
  "disposition": "admit",
  "evidence_utterance_indices": [
    0
  ],
  "hidden_reasoning": false,
  "natural_response_parsed_into_form": false,
  "product_delivered": false,
  "raw_provider_response": false,
  "receptionist_response": "I can help with that. I'll need to confirm which specific appointment for Margaret Thompson you'd like to update to 'arrived'.",
  "violations": []
}
```

Typed form:

```json
{
  "goal_code": 6,
  "steps": [
    {
      "operator_code": 13,
      "source_refs": []
    }
  ],
  "version_code": 3
}
```

Proofreader and usage:

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
  "usage": {
    "candidatesTokenCount": 146,
    "promptTokenCount": 2628,
    "thoughtsTokenCount": 656,
    "totalTokenCount": 3430
  }
}
```

### Paired result

```json
{
  "closed_v5": {
    "correction_used": true,
    "expected_safe_outcome": false,
    "final_violation_codes": [
      "source_type_mismatch"
    ],
    "operator_note": {
      "audit_only": true,
      "disposition": "admit",
      "note_sha256": "sha256:6f43bc5c50db989087bd236e4d5cdb962c3b978e9c3cc2b9e13a81303eb1da94",
      "operator_note": "Review of proposed change, no booking was changed.",
      "parsed_into_plan": false,
      "product_delivered": false,
      "reason_codes": [],
      "retained_utf8_bytes": 50
    },
    "release": null,
    "terminal_status": "terminal_no_release",
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
            "operator_code": 4,
            "source_refs": [
              {
                "binding_code": -1,
                "kind": "prior_output",
                "prior_output_name": "patient",
                "prior_step_index": 0
              }
            ]
          },
          {
            "operator_code": 12,
            "source_refs": [
              {
                "binding_code": -1,
                "kind": "prior_output",
                "prior_output_name": "appointments",
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
      "program_hash": "sha256:f74ddd042b852274b6edb692029efcad5b5dd85d9a801ea370b03182f85b2045",
      "raw_provider_response": false
    }
  },
  "v6": {
    "correction_used": false,
    "expected_safe_outcome": false,
    "terminal_status": "admitted"
  }
}
```

## 18. b-status-noshow-gap

### Authored-synthetic input

- `0` — Mark Margaret's appointment as a no-show.

### v6 turns

#### Turn 1 — completed

Natural receptionist output:

```json
{
  "decision_note": "Intent clarification: The specific appointment to be updated is missing.",
  "disposition": "admit",
  "evidence_utterance_indices": [
    0
  ],
  "hidden_reasoning": false,
  "natural_response_parsed_into_form": false,
  "product_delivered": false,
  "raw_provider_response": false,
  "receptionist_response": "I can help with that, but I need to know which specific appointment for Margaret you'd like to mark as a no-show. I'll prepare this for review.",
  "violations": []
}
```

Typed form:

```json
{
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
}
```

Proofreader and usage:

```json
{
  "proofreader": {
    "admitted_operator_ids": [
      "resolve_patient_reference",
      "request_clarification"
    ],
    "disposition": "admit",
    "safe_repairs": [],
    "violations": [],
    "wire_safe_repairs": []
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
  "usage": {
    "candidatesTokenCount": 233,
    "promptTokenCount": 2613,
    "thoughtsTokenCount": 748,
    "totalTokenCount": 3594
  }
}
```

### Paired result

```json
{
  "closed_v5": {
    "correction_used": true,
    "expected_safe_outcome": false,
    "final_violation_codes": [
      "external_binding_invalid"
    ],
    "operator_note": {
      "audit_only": true,
      "disposition": "admit",
      "note_sha256": "sha256:01550b3df6ee0b8114463ab05237cb957fa61b2d98ced45758e76cbe3d9338ea",
      "operator_note": "Reviewing proposal for status change, no booking was changed.",
      "parsed_into_plan": false,
      "product_delivered": false,
      "reason_codes": [],
      "retained_utf8_bytes": 61
    },
    "release": null,
    "terminal_status": "terminal_no_release",
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
            "operator_code": 4,
            "source_refs": [
              {
                "binding_code": -1,
                "kind": "prior_output",
                "prior_output_name": "patient",
                "prior_step_index": 0
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
      "program_hash": "sha256:614e2790e93bb84a448157e45c6e8b753b0cfcc0446b7572bd07ebfe9af7bc21",
      "raw_provider_response": false
    }
  },
  "v6": {
    "correction_used": false,
    "expected_safe_outcome": true,
    "terminal_status": "admitted"
  }
}
```

## 19. b-squeeze-without

### Authored-synthetic input

- `0` — Could we squeeze Margaret in with Shera today for 15 minutes without moving anyone?

### v6 turns

#### Turn 1 — completed

Natural receptionist output:

```json
{
  "decision_note": "Intent squeeze_in_assessment: User requested to 'squeeze in' a patient with a practitioner for a specific duration and date, with a specific squeeze policy.",
  "disposition": "admit",
  "evidence_utterance_indices": [
    0
  ],
  "hidden_reasoning": false,
  "natural_response_parsed_into_form": false,
  "product_delivered": false,
  "raw_provider_response": false,
  "receptionist_response": "I'm preparing the squeeze-in options for Margaret with Shera for 15 minutes today, without moving anyone, for your review. No booking was changed.",
  "violations": []
}
```

Typed form:

```json
{
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
}
```

Proofreader and usage:

```json
{
  "proofreader": {
    "admitted_operator_ids": [
      "resolve_patient_reference",
      "resolve_practitioner_reference",
      "resolve_date_expression",
      "read_practitioner_schedule",
      "assess_squeeze_in_options"
    ],
    "disposition": "admit",
    "safe_repairs": [],
    "violations": [],
    "wire_safe_repairs": []
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
    "write_performed": false
  },
  "usage": {
    "candidatesTokenCount": 727,
    "promptTokenCount": 2678,
    "thoughtsTokenCount": 962,
    "totalTokenCount": 4367
  }
}
```

### Paired result

```json
{
  "closed_v5": {
    "correction_used": false,
    "expected_safe_outcome": true,
    "final_violation_codes": [],
    "operator_note": {
      "audit_only": true,
      "disposition": "admit",
      "note_sha256": "sha256:c9598bcb776ff1fa085ce1b884b47ee87a5f7af20cb2a95fa4a42f6c4a9e9426",
      "operator_note": "Reviewing proposal for squeeze-in assessment, no booking was changed.",
      "parsed_into_plan": false,
      "product_delivered": false,
      "reason_codes": [],
      "retained_utf8_bytes": 69
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
      "program_hash": "sha256:892d55a9aab043b25caf3ba6f9283e46a3fa8d05fdcb461c240c5f6d7723ead5",
      "raw_provider_response": false
    }
  },
  "v6": {
    "correction_used": false,
    "expected_safe_outcome": true,
    "terminal_status": "admitted"
  }
}
```

## 20. b-squeeze-negated-move

### Authored-synthetic input

- `0` — Squeeze Margaret Thompson in with Dr Shera today for 15 minutes; do not move anyone else.

### v6 turns

#### Turn 1 — completed

Natural receptionist output:

```json
{
  "decision_note": "Intent squeeze_in_assessment: request to assess squeeze-in options.",
  "disposition": "admit",
  "evidence_utterance_indices": [
    0
  ],
  "hidden_reasoning": false,
  "natural_response_parsed_into_form": false,
  "product_delivered": false,
  "raw_provider_response": false,
  "receptionist_response": "I'm looking into options to squeeze Margaret Thompson in with Dr. Shera for 15 minutes today without moving other appointments. I'll have a proposal for you to review shortly.",
  "violations": []
}
```

Typed form:

```json
{
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
}
```

Proofreader and usage:

```json
{
  "proofreader": {
    "admitted_operator_ids": [
      "resolve_patient_reference",
      "resolve_practitioner_reference",
      "resolve_date_expression",
      "read_practitioner_schedule",
      "assess_squeeze_in_options"
    ],
    "disposition": "admit",
    "safe_repairs": [],
    "violations": [],
    "wire_safe_repairs": []
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
    "write_performed": false
  },
  "usage": {
    "candidatesTokenCount": 715,
    "promptTokenCount": 2687,
    "thoughtsTokenCount": 1149,
    "totalTokenCount": 4551
  }
}
```

### Paired result

```json
{
  "closed_v5": {
    "correction_used": false,
    "expected_safe_outcome": true,
    "final_violation_codes": [],
    "operator_note": {
      "audit_only": true,
      "disposition": "admit",
      "note_sha256": "sha256:3c9c8f33dd9e936bcf360aaf6c4bd9df6907f03691b5e38f530a30fd0ddb6b0a",
      "operator_note": "Review of proposed squeeze-in, no booking was changed.",
      "parsed_into_plan": false,
      "product_delivered": false,
      "reason_codes": [],
      "retained_utf8_bytes": 54
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
      "program_hash": "sha256:b2998d32cffc80c03bfb19ef11fb2b6f0f2e36dffc0df16a498d5262db8b10b8",
      "raw_provider_response": false
    }
  },
  "v6": {
    "correction_used": false,
    "expected_safe_outcome": true,
    "terminal_status": "admitted"
  }
}
```

## 21. b-clarify-sort

### Authored-synthetic input

- `0` — Please sort out Margaret Thompson's appointment.

### v6 turns

#### Turn 1 — completed

Natural receptionist output:

```json
{
  "decision_note": "Intent clarification: The requested action is underspecified.",
  "disposition": "admit",
  "evidence_utterance_indices": [
    0
  ],
  "hidden_reasoning": false,
  "natural_response_parsed_into_form": false,
  "product_delivered": false,
  "raw_provider_response": false,
  "receptionist_response": "I can help with Margaret Thompson's appointment. Could you please tell me what you would like to do with it?",
  "violations": []
}
```

Typed form:

```json
{
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
}
```

Proofreader and usage:

```json
{
  "proofreader": {
    "admitted_operator_ids": [
      "resolve_patient_reference",
      "request_clarification"
    ],
    "disposition": "admit",
    "safe_repairs": [],
    "violations": [],
    "wire_safe_repairs": []
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
  "usage": {
    "candidatesTokenCount": 223,
    "promptTokenCount": 2609,
    "thoughtsTokenCount": 258,
    "totalTokenCount": 3090
  }
}
```

### Paired result

```json
{
  "closed_v5": {
    "correction_used": true,
    "expected_safe_outcome": true,
    "final_violation_codes": [],
    "operator_note": {
      "audit_only": true,
      "disposition": "admit",
      "note_sha256": "sha256:2441482a5e7090924287e0dde95287f57005d0f76b9fb8d2625ddd402aa310c7",
      "operator_note": "Review complete, no booking was changed.",
      "parsed_into_plan": false,
      "product_delivered": false,
      "reason_codes": [],
      "retained_utf8_bytes": 40
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
            "operator_code": 13,
            "source_refs": []
          }
        ],
        "version_code": 3
      },
      "operator_note_excluded": true,
      "program_hash": "sha256:cec609701d061859adedeece995ed6539ebce84c8ecf553b3ede9a45972ce7b2",
      "raw_provider_response": false
    }
  },
  "v6": {
    "correction_used": false,
    "expected_safe_outcome": true,
    "terminal_status": "admitted"
  }
}
```

## 22. b-clarify-different

### Authored-synthetic input

- `0` — Margaret Thompson needs a different appointment.

### v6 turns

#### Turn 1 — completed

Natural receptionist output:

```json
{
  "decision_note": "Intent clarification: The request for a \"different appointment\" is underspecified.",
  "disposition": "admit",
  "evidence_utterance_indices": [
    0
  ],
  "hidden_reasoning": false,
  "natural_response_parsed_into_form": false,
  "product_delivered": false,
  "raw_provider_response": false,
  "receptionist_response": "I can help with that. Could you please tell me which appointment for Margaret Thompson you would like to change, and what changes you would like to make?",
  "violations": []
}
```

Typed form:

```json
{
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
}
```

Proofreader and usage:

```json
{
  "proofreader": {
    "admitted_operator_ids": [
      "resolve_patient_reference",
      "request_clarification"
    ],
    "disposition": "admit",
    "safe_repairs": [],
    "violations": [],
    "wire_safe_repairs": []
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
  "usage": {
    "candidatesTokenCount": 232,
    "promptTokenCount": 2607,
    "thoughtsTokenCount": 320,
    "totalTokenCount": 3159
  }
}
```

### Paired result

```json
{
  "closed_v5": {
    "correction_used": false,
    "expected_safe_outcome": true,
    "final_violation_codes": [],
    "operator_note": {
      "audit_only": true,
      "disposition": "admit",
      "note_sha256": "sha256:6686661e508d2244fbc33fc0170228525746afad39e3a36f1822e0c28e6b93d8",
      "operator_note": "Reviewing proposal, no booking was changed.",
      "parsed_into_plan": false,
      "product_delivered": false,
      "reason_codes": [],
      "retained_utf8_bytes": 43
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
            "operator_code": 4,
            "source_refs": [
              {
                "binding_code": -1,
                "kind": "prior_output",
                "prior_output_name": "patient",
                "prior_step_index": 0
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
      "program_hash": "sha256:e1aa6405b0b2200c58536dc6c6188c0d36c8951951db0419c4de220d94629355",
      "raw_provider_response": false
    }
  },
  "v6": {
    "correction_used": false,
    "expected_safe_outcome": true,
    "terminal_status": "admitted"
  }
}
```

## 23. b-clarify-details

### Authored-synthetic input

- `0` — Margaret Thompson with Dr Shera tomorrow at 2:30 pm for 15 minutes.

### v6 turns

#### Turn 1 — completed

Natural receptionist output:

```json
{
  "decision_note": "Intent create: User specified all necessary details for an appointment creation.",
  "disposition": "admit",
  "evidence_utterance_indices": [
    0
  ],
  "hidden_reasoning": false,
  "natural_response_parsed_into_form": false,
  "product_delivered": false,
  "raw_provider_response": false,
  "receptionist_response": "I'm preparing a proposal for Margaret Thompson's 15-minute appointment with Dr. Shera tomorrow at 2:30 PM for your review. No booking was changed.",
  "violations": []
}
```

Typed form:

```json
{
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
}
```

Proofreader and usage:

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
    "write_performed": false
  },
  "usage": {
    "candidatesTokenCount": 864,
    "promptTokenCount": 2723,
    "thoughtsTokenCount": 811,
    "totalTokenCount": 4398
  }
}
```

### Paired result

```json
{
  "closed_v5": {
    "correction_used": false,
    "expected_safe_outcome": false,
    "final_violation_codes": [],
    "operator_note": {
      "audit_only": true,
      "disposition": "admit",
      "note_sha256": "sha256:6686661e508d2244fbc33fc0170228525746afad39e3a36f1822e0c28e6b93d8",
      "operator_note": "Reviewing proposal, no booking was changed.",
      "parsed_into_plan": false,
      "product_delivered": false,
      "reason_codes": [],
      "retained_utf8_bytes": 43
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
      "program_hash": "sha256:66d21473211dc9341fd6d4d362ec05b1c96335a6127c7769a5cca10d298f95b7",
      "raw_provider_response": false
    }
  },
  "v6": {
    "correction_used": false,
    "expected_safe_outcome": false,
    "terminal_status": "admitted"
  }
}
```

## 24. b-clarify-fit

### Authored-synthetic input

- `0` — Can you fit Margaret Thompson in with Dr Shera tomorrow at 2:30 pm for 15 minutes?

### v6 turns

#### Turn 1 — completed

Natural receptionist output:

```json
{
  "decision_note": "Intent clarification: The phrase 'fit in' is ambiguous without further context.",
  "disposition": "admit",
  "evidence_utterance_indices": [
    0
  ],
  "hidden_reasoning": false,
  "natural_response_parsed_into_form": false,
  "product_delivered": false,
  "raw_provider_response": false,
  "receptionist_response": "I can check availability for Margaret Thompson with Dr. Shera, but could you please clarify if this is for a standard appointment or if you're requesting a squeeze-in?",
  "violations": []
}
```

Typed form:

```json
{
  "goal_code": 6,
  "steps": [
    {
      "operator_code": 13,
      "source_refs": []
    }
  ],
  "version_code": 3
}
```

Proofreader and usage:

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
  "usage": {
    "candidatesTokenCount": 161,
    "promptTokenCount": 2732,
    "thoughtsTokenCount": 389,
    "totalTokenCount": 3282
  }
}
```

### Paired result

```json
{
  "closed_v5": {
    "correction_used": false,
    "expected_safe_outcome": false,
    "final_violation_codes": [],
    "operator_note": {
      "audit_only": true,
      "disposition": "admit",
      "note_sha256": "sha256:60de516dcf1bdf444a5be93c19d3e873af82f5f0560ab79fdf4923dc49361049",
      "operator_note": "Review proposal complete; no booking was changed.",
      "parsed_into_plan": false,
      "product_delivered": false,
      "reason_codes": [],
      "retained_utf8_bytes": 49
    },
    "release": {
      "api_spine_operation_id": null,
      "appointment_ref": null,
      "candidate_slot_ids": [],
      "duration_minutes": 15,
      "kind": "squeeze_in_assessment",
      "patient_ref": "synthetic-patient-margaret",
      "practitioner_ref": "synthetic-practitioner-shera",
      "proposal_family": "squeeze_in_assessment",
      "requires_human_confirmation": true,
      "status": null,
      "warning_codes": [
        "manual_squeeze_in_review",
        "staff_confirmation_required"
      ],
      "write_performed": false
    },
    "terminal_status": "admitted",
    "typed_program": {
      "explicit_source_form": {
        "goal_code": 5,
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
                "binding_code": 8,
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
      "program_hash": "sha256:a3b5603e13e68461ba9296dbf8e0c2d9186bb433da4c97df987ea7ca795ed6a7",
      "raw_provider_response": false
    }
  },
  "v6": {
    "correction_used": false,
    "expected_safe_outcome": true,
    "terminal_status": "admitted"
  }
}
```
