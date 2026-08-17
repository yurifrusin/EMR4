# Ordinary Diary cancellation canonical consumer convergence

Date: 2026-08-18

Timestamp: 2026-08-18T01:54:51.4291281+10:00 (Australia/Brisbane)

Status: accepted and continuing

## Lay summary

The older ordinary Diary now cancels appointments according to the same truth
rules as Reception One. It cannot quietly turn a failed cancellation request
into a different status change, cannot treat its own screen state as proof that
an appointment disappeared, and cannot tell staff the outcome until it has
reloaded current Diary truth. If that reload fails, cancellation is disabled as
`Refresh Required` rather than making a potentially false claim.

This means both of Raisa's present first-party Diary views now speak the same
cancellation language even though they look different. That is an important
adapter milestone: future email, messaging, voice or third-party clients may
choose their own presentation, but they must obey the same proposal,
confirmation, receipt and truth-reconciliation rules.

## Technical summary

`docs/diary/diary.js` now shares strict delete-proposal admission between
Reception One and the ordinary booking editor, removes the 404-to-status and
raw-delete semantic fallbacks, posts only canonical
`/appointments/proposals/delete/confirm`, validates only
`raisa.delete_confirm_public_envelope.v1`, and performs one fresh authorised
Diary read after every terminal or uncertain outcome. Failed reconciliation
sets a disabled refresh-required state; no local optimistic deletion is
authoritative.

Accepted candidate `bfac65298e1d4aaca85d1c9dcb20329ef298c485` preserves product
source `cb6589437bce24c5680c590bc5cf4571435f1a7a` plus a narrow browser-harness
timing repair. Verification includes 170 combined browser tests, 85 focused/API
Spine checks, 303 register tests, 52 latch checks and one fresh nine-command
Gemini 3.7 Flash/high exact-candidate pass. Register revision 346 contains 397
closed incidents; AER-0391 through AER-0397 preserve the tranche's transport,
preflight, browser-timing, receipt, aggregate and Continuity corrections.

## Deliberately closed

No live backend/database behavior, raw compatibility DELETE, external adapter,
patient/product/clinical data, provider runtime, credentials/IAM, deployment,
production, release, Pages or protected-ref movement is claimed or opened.

## Next

The engine is continuing into a provider-free read-only post-cancellation
programme orientation. Its job is to compare the now-complete first-party
cancellation chain with the remaining Reception One/API Spine command families
and freeze the narrowest next tranche before any new product edit.

Yuri's attention is not required.
