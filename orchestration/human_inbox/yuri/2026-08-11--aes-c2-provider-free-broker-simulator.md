# AES-C2 provider-free inert broker simulator closeout

Date: 2026-08-11

Result: passed

Attention required: no

## Lay summary

Raisa can now rehearse the next step after a capability is approved: an
external broker, not the AI work cell, chooses one exact harmless operation and
checks that authority is still current immediately before it runs. The work
cell never sees a credential, destination, method or executable selector.

We exercised 26 authored-synthetic situations. Two exact harmless cases
returned simulated results, four were refused by admission, and 20 stopped.
The only adapter was an ordinary pure Python function with no external effect.
It was actually called three times, including once to prove that malformed
output is rejected rather than released. No real broker, provider, product,
patient record, network, database, filesystem, tool or command was touched.

## Technical summary

AES-C2 binds one immutable broker registry entry to the exact AES-C1 admission
result, current generation/authority/revocation/kill state, supply-chain
identity and cumulative budget-after commit. Adapter identity is broker-owned;
candidate content cannot select capability, adapter, destination, method,
implementation or executable. The synthetic noncredential fixture stays in
broker-private state and is absent from every invocation, result and evidence
surface.

Verification passed 95/95 focused C2/C1/C0/API tests, 155/155 final maintained
static tests and the 161/161 canonical fast profile. A fresh Gemini 3.6
Flash/high veto independently passed 95 tests with the reviewed HEAD unchanged.
All 18 hostile attempt/result mutations and 14 contract mutations failed
closed.

## Issues

The first worker candidate reported a pure-function call that an override had
actually bypassed and admitted an extra scenario-packet field. Sol rejected it.
The one permitted mechanical revision made the real call unconditional, closed
the packet exactly and added regressions that count the actual callable. Fresh
independent review passed. Two receipt/register drafting errors also failed
closed before they could affect source or acceptance and remain recorded.
The first final maintenance run additionally found and repaired a historical
AES-C1 test that incorrectly assumed no later continuity node could exist; the
full profile passed after that binding was made descendant-safe.

## Deliberately still closed

There is still no real broker, work-cell process, container, adapter or
credential. Provider calls, product or patient context, database/source or
watcher access, filesystem capability, generic network, executable tools,
commands/writes, deployment, production, release, Pages and protected refs
remain closed.

## Place in the Raisa direction

AES-C0 established the authority grammar; AES-C1 proved exact admission; AES-C2
now proves that the broker can retain operation identity and custody while
calling only one inert fixed function. This keeps model reasoning separate from
both authority and execution mechanics.

## Next tranche

AES-C3 is the provider-free hostile containment rehearsal. It will challenge
local-file references, templates/deserialization, metadata and credential
probing, arbitrary or encoded egress, cumulative probing, stale leases and
cross-generation replay without opening real runtime, provider, data,
credential, network, tool or command authority. No decision from Yuri is
presently required.
