# DeepSeek native Harness diagnostic incident-category vocabulary recovery

Date: 2026-08-22

Timestamp: 2026-08-22T03:42:19.3682524+10:00 (Australia/Brisbane)

The third prospective clockwork check rejected before commands or canonical
publication with `tick_incident_category`. Two observations used descriptive
labels—`test_setup_error` and `protected_evidence_boundary_violation`—rather
than categories from the finite register vocabulary.

Direct inspection of `EXPECTED_ORIGIN_BY_CATEGORY` identified
`operator_error` as the admitted coordinate for both observations. The intent
now uses that exact value. Future incident-category selection is a typed lookup
against the runtime category map, not a free-form writing task.
