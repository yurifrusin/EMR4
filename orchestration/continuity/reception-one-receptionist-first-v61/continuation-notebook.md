# Reception One v6.1 Pre-schema Continuation

The frozen first cohort returned HTTP 200 with non-JSON text for this case, so no candidate reached the proofreader. This continuation uses the identical prompt, schema and exact provider boundary with new single-use ledgers.

Authored-synthetic input:

- Shift Margaret's appointment to tomorrow at 2:30 pm.

```json
{
  "correction_used": false,
  "exact_expected_outcome": false,
  "terminal_status": "terminal_no_release",
  "turns": [
    {
      "proofreader": {
        "admitted_operator_ids": [],
        "disposition": "not_reached",
        "safe_repairs": [],
        "violations": [],
        "wire_safe_repairs": []
      },
      "provider_outcome": {
        "bounded_error": {
          "field_paths": [],
          "reason_code": "provider_text_not_json"
        },
        "http_status": 200,
        "latency_ms": 8023,
        "status": "response_rejected_before_candidate",
        "usage": {}
      },
      "receptionist_output": null,
      "release": null,
      "turn": 1,
      "typed_form": null
    }
  ]
}
```

Raw provider packets, credentials, API-key information and hidden chain-of-thought are excluded.
