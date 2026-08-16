# Delete-confirm HTTP route convergence — closeout

Date: 2026-08-17

Timestamp: 2026-08-17T06:42:01.5453490+10:00 (Australia/Brisbane)

Attention required: no

## Lay summary

Raisa now has one narrow, consistent doorway for a receptionist's confirmed
appointment cancellation request. The current and older route spellings both
lead to that same doorway, so they cannot quietly grow different behavior. The
doorway carries only server-proven identity and version evidence into the
already accepted cancellation machinery.

The reply is deliberately small: it confirms the cancellation result without
returning the patient, practitioner, diary slot, notes or a mutable appointment
record. The more sensitive internal command receipt remains private. Initial
success and retry use the same canonical public form.

This is a meaningful backend milestone but not yet a live cancellation through
a database. The next tranche will rehearse this exact doorway end-to-end against
a disposable authored-synthetic PostgreSQL database before any visible client
work. No patient data, provider call, deployment or production surface opened.

## Technical summary

- exact candidate: `c7a01edd96ebabf3ea2c07be89a5b405c9629853`;
- canonical `/proposals/delete/confirm` plus hidden historical alias over one
  handler and exactly one `compose_product_delete_confirm` call;
- server-minted signed-evidence/source-version binding and server-owned
  authentication/session/secret ingress;
- strict dedicated Pydantic/OpenAPI public envelope;
- reciprocal private-receipt invariant and canonical public-byte transport;
- 12/12 scenarios, 149 hostile rejections, 27 focused tests, 78 static API
  Spine/Diary tests, 274 register tests, a 439-test integrated closeout profile
  and 16/16 deterministic checks;
- fresh Gemini 3.7 Flash/high eight-command veto: `pass`, unchanged clean HEAD,
  tree and worktree; and
- AER-0366/0367 preserve the rejected worker/correction evidence; AER-0368
  records and corrects the pre-verifier tree-object evidence recurrence.

## Deliberately closed and next work

No route/database command was executed; no raw DELETE convergence, capability,
product/patient/clinical data, provider, credential/IAM, UI, deployment,
production, release, Pages or protected-ref movement was opened.
`docs/branding/` and every unrelated untracked file remain preserved.

Next: the narrowest provider-free disposable PostgreSQL delete-confirm HTTP
integration rehearsal, followed—if it passes—by the next dependency-satisfied
Reception One cancellation client boundary. Standing authority applies; no
decision from Yuri is presently needed.
