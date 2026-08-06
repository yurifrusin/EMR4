# Ariadne agent-error register revision 44

Date: 2026-08-06

Status: durability state-machine plan recovery accepted by fresh veto

## AER-0049 corrected

AER-0049 preserves the rejected rehearsal plan at
`e07cb708bd1b36e01b22cae0911ee75829110681`. Under the named Sol recovery lease,
retention now requires an integrity-bound complete non-consumed-generation
census with an independent registry/census digest; restart adopts no coordinate
from missing or integrity-invalid state; and routine key rotation is atomic,
strictly future-position-fenced, history-preserving and holds predecessor-key
availability through dependency drain plus safety overlap.

A genuinely fresh exact-head review at
`d2b8e0c67218f3d6131e9141c9304caf2f9998df` passed 112 serial checks and found no
P0-P2 issue. AER-0049 therefore closes only through the recovery lease plus that
fresh veto. The plan now admits implementation of the pure unmounted authored-
synthetic rehearsal and grants no live database/source/provider/runtime/command
authority.

Revision 44 contains 49 bounded incidents: 37 agent-behaviour observations,
three harness failures, two repository defects and seven transport timeouts.
No incident remains open. Counts remain workflow-improvement signals and do not
establish model, provider, transport or role causation.
