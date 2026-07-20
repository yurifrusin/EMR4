# Reception One committed-event vertical — baseline regression comparison

**Candidate:** `705582b7719bce6f1c5fe5833c1703354b5fa1a3`
**Untouched baton baseline:** `be5e01d00b23ef43f7aab8b30f6dbdfa6e858c45`
**Disposition:** no candidate regression in the observed historical nodes

The accepted current populations passed, but one deliberately broader sweep
included historical tests whose expectations predate already accepted source
changes. Sol reproduced every such observation serially in a detached clean
worktree at the untouched baton baseline:

- the Sprint 139 update-confirm preflight already rejects the later accepted
  delete-confirm `Idempotency-Key` header;
- the confirmation-family integration file already imports the removed
  uppercase `_BERNIE_SESSION_STORE` symbol and fails collection;
- `tests/test_appointment_audit.py`,
  `tests/test_appointment_audit_warning_summary.py`, and
  `tests/test_slot_selection_proposal.py` reproduce the same 14 failures as the
  candidate: two pre-idempotency delete calls, eleven pre-raw-compat audit
  expectations, and one old slot fixture.

No product or historical-test source was changed to conceal these results.
The exact current update-confirm contract, committed-event, API Spine,
functional/live-local/combined-scope, accessibility, handover, continuity and
Diary populations are the acceptance gates for this tranche. The disposable
baseline worktree was verified clean and removed after comparison.
