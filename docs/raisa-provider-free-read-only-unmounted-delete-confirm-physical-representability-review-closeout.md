# Provider-free read-only unmounted delete-confirm physical representability review closeout

Date: 2026-08-15

Timestamp: 2026-08-15T14:44:52+10:00 (Australia/Brisbane)

Status: accepted

Accepted reviewed source: `bc066a1b639c5c57cc72f2697c063c5842511840`

Result: `raisa_provider_free_read_only_unmounted_delete_confirm_physical_representability_review_pass`

## Lay summary

The repository can faithfully support the safe cancellation kernel without
weakening it. The appointment record already carries the essential truth:
practice ownership, status, waiting area, both cancellation reasons and a
positive monotonic version. The remaining work is not a fundamental database
obstacle. It is a careful additive design problem: stabilise current staff
authority inside the transaction, complete the private retry receipt, bind the
audit to exact before-and-after state, put the locks and checks in the accepted
order, and authorise the later readback separately.

This review deliberately does **not** approve the current mounted cancellation
route as safe. That route presently claims its idempotency record before it
locks appointment truth, does not perform the accepted in-transaction authority
checks, and does not advance or preserve all required private receipt evidence.
The old compatibility delete and status-fallback paths remain separate and gain
no authority from this result.

The next tranche may therefore design the smallest unmounted physical changes.
It may not yet alter or run the application, database, route or Reception One
client.

## Technical result

The source-bound evidence admits six closed domain verdicts:

- `appointment_truth_and_lock`: `already_represented`;
- `practice_authority_fence`: `representable_with_additive_change`;
- `operation_scoped_idempotency_private_receipt`:
  `representable_with_additive_change`;
- `attributable_audit_and_exact_reasons`:
  `representable_with_additive_change`;
- `ordered_atomic_boundary`: `representable_with_additive_change`; and
- `fresh_readback_separation`: `representable_with_additive_change`.

The conclusion is calibrated as `implementation_not_admitted`. Existing
principal-generation structures prove a lockable authored-synthetic pattern,
not a product UUID cancellation capability. Existing idempotency and audit
structures prove representability, not complete delete-confirm receipts or
before/after correlation. Existing practice-scoped GET proves a read surface,
not the required explicit current appointment-read authorization decision.

## Evidence and independent review

- Thirteen exact source hashes cover the three accepted contract inputs and
  ten physical/API sources.
- Twenty-six line-bound observations support the six verdicts.
- All 52 hostile mutations fail closed.
- The deterministic validator, focused review/plan packet and API Spine packet
  pass.
- DeepSeek's bounded source-inventory attempt timed out with no owned artifact,
  no tracked change and no source adoption; AER-0326 closes that transport lane.
- Sol completed the literal-allowlist inventory and synthesis.
- Gemini 3.6 Flash/high independently passed the exact candidate after all five
  bound commands exited zero, confirming all hashes, observations, verdicts,
  overclaim refusals and the next closed gate.
- Gemini left named review branch
  `codex/review-delete-confirm-representability-bc066a1b` clean and unchanged at
  the exact reviewed source.
- The canonical fast profile passes Ruff, 209 maintained Python compilations,
  196 tests, Diary JavaScript syntax and Git whitespace.
- The non-PHI continuing Pushover notification succeeded with request
  `d26a8961-362c-421b-a269-1594e60dfafe` and status `1`.

## Workflow evidence

AER-0325 records and contains one overbroad filename-metadata query that
surfaced two protected path names but opened no protected content; those names
were discarded and barred from evidence. AER-0327 records a detached verifier
worktree rejected locally before any model call. AER-0328 records lowercase
command-manifest identifiers rejected locally before any model call. The
corrected named-branch preflight, exact manifest evidence gate and revision-289
incident-register suite all pass before the single occupied Gemini review.

These incidents changed no candidate claim. They do reinforce the workflow
lesson: local packet grammar and worktree checks belong before provider
dispatch, while substantive representability remains a narrow evidence-led
question.

## API Spine finding

The accepted architecture remains one explicit REST/OpenAPI cancellation
command family with backend-owned authority, locking, confirmation,
idempotency, audit, receipt and readback. GraphQL remains read-only and events
remain acceleration hints. The OpenAPI delete reason shape requires later
alignment to mandatory structured reason plus nullable bounded free text, but
this review grants no OpenAPI edit.

## Deliberately closed

No model, ORM, migration, service, router, OpenAPI, GraphQL, database, SQL,
runtime, watcher, event source, product client, Reception One UI, provider
product call, patient/product/clinical data, credential/IAM, command/write,
deployment, production, release, Pages or protected ref changed. The one
Gemini call reviewed repository-local authored-synthetic evidence only.

## Next tranche

Begin the provider-free unmounted delete-confirm physical-design architecture.
Freeze the smallest additive practice-authority fence, private receipt and
audit correlation representation; exact transaction lock/check order; reason
shape; version advance; and separately authorised readback boundary. The
tranche remains declarative and unmounted. Yuri attention is not required.
