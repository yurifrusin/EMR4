# Ariadne agent error and correction register — revision 516

Date: 2026-08-19

Timestamp: 2026-08-19T04:21:58.9165592+10:00 (Australia/Brisbane)

Status: rejected before acceptance; superseded by revision 517

## Change from revision 515

AER-0597 records recurrence of the unadmitted `selected` parallelism
disposition in a pre-verifier runtime state. The fresh five-source preflight
returned `revision_required` with the exact Gemini-lane reason and did not
permit a provider or model call. The rejected attempt-002 state and receipt
remain preserved; attempt 003 uses the configured `reserved` value copied from
the last passing stage-equivalent receipt.

## Rejected register state

Draft revision 516 contained 597 bounded incidents but did not pass canonical
validation because AER-0597 named a planned attempt-003 runtime state before
that file existed. The generator stopped before pattern projection,
acceptance, provider dispatch or publication. Revision 517 replaces the future
path with materialized evidence and records the rejected draft as AER-0598.

## Clockwork consequence

Parallelism disposition is a typed continuation-state projection, not prose
for the orchestrator to improvise. A future shared Ariadne/DeepSeek clock must
derive it from the event stage and configured enum before either harness can
advance or call a provider.

No product, patient, clinical, provider credential, deployment, release,
Pages, protected-evidence or protected-ref authority changed.
