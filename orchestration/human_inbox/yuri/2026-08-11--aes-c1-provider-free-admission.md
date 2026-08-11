# AES-C1 provider-free admission rehearsal closeout

Date: 2026-08-11

Result: passed

Attention required: no

## Lay summary

Raisa can now rehearse the exact decision that must happen before a future AI
work cell is allowed to use a narrowly defined capability. An operation is
admitted only when every independent permission agrees at the same moment: the
generation is current, the manifest explicitly grants it, a matching broker-
held lease is active, the user's current authority still matches, proofreading
has admitted the candidate, and every separate budget remains within bounds.

We exercised 45 authored-synthetic situations. Only two exact inert cases were
allowed; 25 were denied and 18 stopped the generation. We also generated 32
hostile mutations. None acquired authority. Even an allowed result remained a
paper decision: nothing ran, no provider was called, and no product or patient
information was touched.

## Technical summary

AES-C1 implements a pure, unmounted evaluator over the exact AES-C0
`GenerationManifest`, `CapabilityLease`, `BudgetState`, `BrokerDecision`,
`RevocationRecord` and `AuditEvidenceEnvelope` contract. It recomputes canonical
manifest, candidate and before/after budget digests; checks current generation
and current authority; enforces fixed stop/deny precedence; and accounts for all
19 cumulative reasoning, information, egress, action, denial and time counters.

Verification passed 59/59 focused AES/API tests, 129/129 final maintained static
tests and 135/135 canonical fast-profile tests. A fresh isolated Gemini 3.6 Flash/high
veto passed a separate 73-test review with the candidate HEAD unchanged. The
evidence records zero runtime starts, adapters, provider calls, network,
database/source, tools, commands and patient/product data.

## Issues

The blue implementation review found and closed two overly open input surfaces.
Sol then strengthened inherited AES-C0 hashes from merely valid digest strings
to exact frozen values. Three orchestration-receipt drafting errors also failed
closed before dispatch or integration and are now recorded in the error
register. The independent final veto found no unresolved defect.

## Deliberately still closed

There is still no runtime broker or work-cell process. Real adapters, provider
calls, credentials, product or patient context, database/source or watcher
access, network, executable tools, commands/writes, deployment, production,
release, Pages and protected refs remain closed.

## Place in the Raisa direction

AES-C0 established the authority grammar; AES-C1 proves that the grammar can be
applied deterministically and fail closed. This keeps Raisa's intelligence
separate from the authority and physical mechanisms through which it may
eventually act.

## Next tranche

AES-C2 is the provider-free broker simulator. It will freeze one inert
allowlisted authored-synthetic adapter with no external effect and prove that
the work cell never receives a credential or chooses the destination, method
or executable. The standing uninterrupted-development authority is sufficient;
no decision from Yuri is presently required.
