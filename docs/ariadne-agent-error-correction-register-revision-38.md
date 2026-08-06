# Ariadne agent-error register revision 38

Date: 2026-08-06

Status: observation-to-signal worker veto preserved; recovery pending fresh veto

## AER-0046 open

The first observation-to-temporal-signal implementation passed its complete
153-test deterministic packet but failed fresh independent semantic review in
two related ways. Admission accepted alternate contract-valid raw identifiers,
backend timestamps and prior seen-ID sets that the downstream mapper rejected
because it reconstructed the canonical fixture. It also exported low-level
admission and mapping functions that could yield signal material without the
deterministic proofreader.

The worker had already consumed its one bounded correction. Sol therefore
preserved the exact veto and invoked the named recovery lease. The repair makes
admission and mapping internal, retains a single proofreader-gated public packet
builder, reconstructs the observation and temporal signal from the actual
validated trusted inputs, and adds alternate-domain and public-export tests.
The incident remains open until a fresh exact-head independent veto passes.

Revision 38 contains 46 bounded incidents: 34 agent-behaviour observations,
three harness failures, two repository defects and seven transport timeouts.
One incident remains open. Counts remain workflow-improvement signals only and
do not establish model, provider, transport or role causation.
