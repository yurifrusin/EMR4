# Attempt 005 readiness historical test selection

Date: 2026-08-21
Timestamp: 2026-08-21T18:19:12.1575248+10:00 (Australia/Brisbane)
Status: `frozen_applicability_boundary`

The widened attempt-005 readiness packet excludes exactly these immutable
historical-equality selectors:

- `test_deterministic_evidence_launches_no_subprocess`
- `test_contract_evidence_and_report_are_current`

Both belong to
`test_raisa_provider_free_authored_synthetic_native_harness_structured_diagnostic_bounded_worker_controller_convergence_rehearsal.py`.
They intentionally require controller digest
`43e47f244728449f4476431b8d32e3b110c2239025d286a2a5075c477648d9bb`.
The current controller digest is
`e64b6c7f6b13bae69dd910963620e03e292b5262c5b05029305d6097f3e6191b`
because the accepted profile-relative-specifier and sentinel-source repairs
changed that controller after the convergence rehearsal. The structured
diagnostic and legacy-terminal digests remain exactly equal.

This is an applicability exclusion, not regeneration or reinterpretation of
the immutable rehearsal. All other selectors in that file remain in the
widened packet. The current attempt-005 gate directly binds the repaired
controller digest, every accepted repair artifact and the successful inert-task
readiness terminal, so excluding the two pre-repair equality selectors removes
no current safety property.
