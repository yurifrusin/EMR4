# Delete-confirm physical representability review

Date: 2026-08-15

Timestamp: 2026-08-15T14:44:52+10:00 (Australia/Brisbane)

Status: accepted; development continuing

## Lay summary

The cancellation kernel fits the real repository. We do not need to retreat
from its safety guarantees or invent a different database architecture.

The appointment record already contains the core truth needed to decide a
cancellation: which practice owns it, its current status and waiting area, both
forms of cancellation reason, and a real monotonic version number. Five
surrounding safeguards need small, deliberate additions: locking current staff
authority, completing the retry receipt, showing exact before-and-after state in
the audit, composing the transaction in the safe order, and independently
authorising the readback.

Crucially, this does not mean the existing cancellation endpoint is safe enough
for Reception One. It currently claims a retry record before locking the
appointment and lacks several of the kernel's current-authority and evidence
steps. It remains outside the accepted envelope.

## Technical summary

At reviewed source `bc066a1b639c5c57cc72f2697c063c5842511840`:

- 13 exact source hashes and 26 line-bound observations pass;
- appointment truth and locking are `already_represented`;
- the practice authority fence, private receipt, audit correlation, ordered
  atomic boundary and separate readback are all
  `representable_with_additive_change`;
- all 52 hostile mutations fail closed;
- `implementation_authorized` remains false and the overall result is
  `implementation_not_admitted`;
- focused, API Spine, register and independent verifier gates pass; and
- Gemini 3.6 Flash/high independently passed all five exact commands at an
  unchanged clean candidate.

The canonical fast profile passes Ruff, 209 maintained Python compilations,
196 tests, Diary JavaScript syntax and Git whitespace. The required non-PHI
continuing Pushover notification succeeded with request
`d26a8961-362c-421b-a269-1594e60dfafe` and status `1`.

DeepSeek's mechanical inventory lane timed out without an artifact or source
change, so Sol completed the literal-file inventory. Three orchestration issues
were retained transparently: one overbroad path-metadata query whose protected
path names were discarded, one detached review worktree and one lowercase
manifest. Both verifier setup errors stopped locally before any model call; the
one actual Gemini review happened only after the corrected gates passed.

## What this means for Raisa

The authority-kernel/reference-client architecture is holding. Reception One
does not need to own cancellation semantics, and future email, messaging, voice
or clinical adapters do not need their own versions either. They may present
truth and relay intent, but one backend transaction remains responsible for
current authority, locked truth, confirmation, idempotency, audit and receipt.

This is the practical basis for the wider provider-agnostic,
provider-qualified medical-management intelligence idea: models and clients can
change, while the deterministic harness decides what information and actions
are admissible. It is not yet a safety certification or provider accreditation
claim.

## Deliberately closed

No application, database, route, OpenAPI, Reception One UI, patient or product
data, operational provider lane, deployment, production, release, Pages or
protected ref changed. Compatibility delete/status routes remain separate.

## Next

Development is continuing into the provider-free unmounted delete-confirm
physical-design architecture. It will select the smallest declarative additive
structures and exact transaction order, without yet changing or running the
product database or UI. Yuri attention is not required.

Formal closeout:
`docs/raisa-provider-free-read-only-unmounted-delete-confirm-physical-representability-review-closeout.md`.
