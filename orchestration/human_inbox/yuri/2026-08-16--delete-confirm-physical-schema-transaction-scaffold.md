# Delete-confirm physical schema-and-transaction scaffold — paired closeout

Date: 2026-08-16

Timestamp: 2026-08-16T00:24:19+10:00 (Australia/Brisbane)

Attention: `requested_pause_and_workflow_efficiency_review`

## Lay summary

Raisa's safe appointment-cancellation design now exists as real—but still
disconnected—backend source. The code can represent who currently has
permission to cancel, invalidate old authority when that permission changes,
store one exact private result for safe retry, keep a separate attributable
audit record, and arrange the future database work so one winner gets the
effect and partial results cannot quietly survive.

Nothing has been connected to a receptionist screen or live command. No
appointment, patient record or database was touched. This is the steelwork for
the cancellation path, not an opened doorway.

One independent review failed for a mundane workflow reason: its test runner
looked for a new test in the main checkout instead of the isolated candidate
checkout. That failed review was preserved, the command was corrected without
changing the product code, and the fresh review passed. This is directly
relevant to the requested review of whether Ariadne is paying too much
ceremonial overhead for the marginal defects it catches.

## Technical summary

Result:
`raisa_provider_free_unmounted_delete_confirm_physical_schema_transaction_scaffold_pass`.

The accepted source maps database-owned `users.authority_generation`, a closed
normalized `user_capability_grants` relation, the family-qualified delete v1
private receipt and seven attributable audit additions. Alembic revision
`x3y4z5a6b7c8` remains inert. Pure helpers bind six-field canonical bytes,
domain-separated HMAC-SHA-256 session identity and constant-time integrity.
The unmounted `READ COMMITTED` composition seam applies one monotonic 2000 ms
budget, exact lock order, two complete current-authority checks and a strict
appointment/audit/receipt completion barrier.

Evidence: 20 bindings; 117/117 hostile mutations; 57 focused/conformance
tests; 36 API Spine tests; 196/196 canonical fast-profile tests; clean Ruff,
compilation, Diary syntax and whitespace; and one clean corrected Gemini 3.7
Flash/high veto. AER-0341 preserves the rejected cross-checkout relative-path
manifest. The register is revision 302 with 341 closed or contained incidents.

## Deliberately closed

No executed migration or SQL, database/catalogue/trigger/lock behavior,
capability provisioning, route/schema/OpenAPI change, mounted command,
patient/product/clinical data, provider/ADC/credential/IAM/network activity,
watcher/event authority, deployment, production, release, Pages or protected
ref movement.

## Place in Raisa and next direction

This is the first source embodiment of the cancellation safety kernel, following
the same backend-truth principle already established for appointment creation,
status and rescheduling. The next planned tranche is the narrow disposable
PostgreSQL parse/catalogue proof of this exact migration.

Development is now paused before that next tranche, as requested. During the
pause Sol will review recent tranche latency and Ariadne controls, including the
supplied YouTube conversation as a devil's advocate against uncritical speed,
and report which controls are essential, which are duplicative, and which can
be deferred or automated without weakening Raisa's authority and data-safety
boundaries.
