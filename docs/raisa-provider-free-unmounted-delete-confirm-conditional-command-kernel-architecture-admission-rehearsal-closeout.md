# Provider-free unmounted delete-confirm conditional-command kernel architecture and admission rehearsal closeout

Date: 2026-08-15

Timestamp: 2026-08-15T12:56:41+10:00 (Australia/Brisbane)

Status: accepted

Accepted reviewed source: `356b28a1750e7a7b379406e864f2a3501606938a`

Result: `raisa_provider_free_unmounted_delete_confirm_conditional_command_kernel_architecture_admission_pass`

## Lay summary

Raisa now has a precise, fail-closed design for the final appointment
cancellation decision. Before a future cancellation can take effect, the
backend must lock the relevant practice authority and appointment truth,
confirm that the staff member still has cancellation authority, validate the
human confirmation and signed proposal, and publish the cancelled appointment,
audit record and receipt together or publish none of them.

The design also covers the awkward cases: two people acting on the same stale
appointment, a lost response after a successful commit, authority being revoked
while a request waits, an appointment already changed, and a later loss of
permission to read the result. In each case the outcome is deterministic and a
retry cannot create a second cancellation.

This is a tested abstract transaction contract, not yet a database or product
change. The next tranche will check whether the contract can be represented
faithfully in the existing PostgreSQL and application structures before any
route or Reception One cancellation control is mounted.

## Technical result

The closed contract freezes:

- exact `practice -> appointment -> idempotency_record` lock ordering;
- current actor activity, practice, role and `appointment.cancel.confirm`
  capability checks after target lock and again with all locks held;
- authority and target non-disclosure before replay or receipt disclosure;
- an exact 24-field signed-evidence contract with valid timestamp ordering;
- required current `Cancelled` structured reason plus nullable bounded
  free-text reason preserved across appointment, audit and receipt;
- atomic first effect, full pre-commit rollback and stored-byte replay after
  unknown delivery; and
- separately authorised fresh readback that cannot alter the command outcome.

The canonical evidence packet passes 46 decision scenarios, 15 transaction
schedules and 67 hostile mutations. It grants zero runtime, command, route,
database, UI or provider authority.

## Recovery and independent review

DeepSeek supplied a useful initial six-file scaffold, but its self-pass was
rejected because it confirmed after its own evidence expiry, lacked exact
authority and signed-evidence contracts, and omitted a successful null
cancellation-text path. AER-0324 preserves that conceptual failure. Under the
named Sol recovery lease the source was corrected, regenerated and admitted;
the same worker lane was not retried.

Gemini 3.6 Flash/high then independently passed all 15 exact-candidate
challenges, reproduced 457 tests, confirmed all 67 hostile mutations failed
closed, and left exact candidate `356b28a1750e7a7b379406e864f2a3501606938a`
clean and unchanged.

## Verification

- The admission script passed: 46 decisions, 15 schedules, 67 hostile
  mutations and zero admitted mutations.
- The focused protocol packet passed 24 tests.
- The combined cancellation/API packet passed 212 tests; Gemini independently
  reran its 188-test review subset.
- The agent-error register passed 245 tests at revision 285.
- The canonical fast profile passed Ruff, 209 maintained Python compilations,
  196 tests, Diary JavaScript syntax and Git whitespace.
- The non-PHI continuing Pushover notification succeeded with request
  `1c7333ac-0017-4945-ae1d-37d8cdf017e1` and status `1`.
- Evidence label: `authored_synthetic_provider_free_unmounted_protocol`.

## Architectural direction recorded during closeout

The accompanying
`docs/raisa-authority-kernel-reference-client-adapter-seam.md` records the
natural product seam now becoming visible: Raisa owns one typed authority
kernel and Reception One is its first-party reference client. Future email,
messaging, thin-web, voice or third-party assistants may become separately
gated adapters without creating new business-rule or command kernels.

This supports a narrower production path: complete the core kernel and native
Reception One client first instead of delaying initial release until every
possible client has been built. It does not open any external adapter or make
its identity, delegation, privacy or conformance work optional.

The same principle is recorded for Clinician One: the Word/Office workspace is
the first-party clinical reference client, while current clinical truth,
permissions, versioning, clinician attestation, audit and final commit remain
backend-owned. This creates no alternate clinical client or runtime.

My Health Record is separately classified as a future regulated integration
adapter: outbound translation begins from authorised Raisa truth; inbound
material remains source-labelled external evidence; and every external effect
stays behind explicit authority, audit and readback. Its Phase 10 gate is not
opened or reprioritised here.

At the highest level, this supports EMR4's emerging role as a provider-agnostic,
provider-qualified general-practice medical-management intelligence harness.
Safety is sought through the deterministic harness and evidence gates, not
claimed from any model brand. This is direction only, not a current safety,
accreditation or production claim.

## Parallelism efficacy

- DeepSeek delivered a useful mechanical scaffold, but its conceptual
  self-acceptance failed; the correction-loop rule correctly transferred
  recovery to Sol.
- Gemini delivered the planned independent veto with positive leverage after
  deterministic admission.
- Native subagents were declined because recovery and closeout were tightly
  coupled to one state machine and one serial acceptance sequence.
- Sol retained architecture, recovery, acceptance, continuity and Git.

## Deliberately closed

No application route, OpenAPI, GraphQL, schema, migration, database source,
watcher, event runtime, product client, Reception One UI, provider call,
patient/product/clinical data, credential/IAM, command/write, deployment,
production, release, Pages or protected ref changed. Raw delete and the native
status fallback remain separate and gain no authority from this result.

## Next tranche

Begin the provider-free unmounted delete-confirm physical representability
review. It will map the abstract authority fence, lock order, idempotency, audit
and receipt contract onto existing repository structures without mounting or
executing the route. Yuri attention is not required.
