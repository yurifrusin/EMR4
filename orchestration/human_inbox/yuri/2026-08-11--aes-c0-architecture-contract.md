# AES-C0 architecture contract closeout

Date: 2026-08-11

Result: passed

## Lay summary

Raisa now has a precise architectural rulebook for how a future AI Bureau may
be given a tightly limited ability without being handed the keys to the system.
The intelligent work cell may suggest a small, typed action, but a separate
deterministic broker would decide what exact operation is allowed. The work cell
cannot choose its destination, obtain a credential, browse the network, touch
the database or turn a suggestion into a product command.

The rulebook also separates thinking capacity from authority. Giving a model
more time or a larger thinking budget never gives it more data, network access,
tools or permission to act. If required intelligence is unavailable, Raisa
says so explicitly instead of quietly substituting a less capable mechanism.

We challenged 37 different ways these boundaries might be weakened; every one
was rejected. This is an important structural step toward giving Raisa a safe
body through which increasingly capable intelligence can work.

## Technical summary

AES-C0 freezes six closed JSON message types: `GenerationManifest`,
`CapabilityLease`, `BudgetState`, `BrokerDecision`, `RevocationRecord` and
`AuditEvidenceEnvelope`. It binds exact broker-resolved capability identity,
immutable per-generation authority, cumulative reasoning/information/egress/
action/denial/time budgets, SHA-256 supply-chain identity, external generation-
wide revocation and minimized audit evidence.

The work cell receives no lease or credential. Generic network, filesystem,
SQL/database, shell/process, metadata, repository/CI write, provider tools,
runtime control and product commands are non-leaseable. GraphQL remains
read-only, events remain fresh-read signals and mutations remain separately
authorized REST/OpenAPI commands.

Verification passed 37/37 hostile mutations, 45/45 focused AES/API tests,
105/105 static CI tests and 111/111 canonical fast-profile tests. There were no
provider calls, runtime starts or patient/product/protected-evidence accesses.

## Issues

The review corrected one subtle budget rule: a zero ceiling means a capability
is disabled, whereas reaching a positive ceiling means the generation is
exhausted. The orchestrator also demonstrated fail-closed receipt handling by
rejecting and repairing one incorrectly labelled preacceptance receipt.

## Deliberately still closed

No broker or work-cell runtime has been implemented. Providers, credentials,
product or patient context, database sources, tools, commands, deployment,
production, release, Pages and protected refs remain closed.

## Place in the Raisa direction

Context Fabric is how Raisa selects the right information; AES is how Raisa will
eventually use capabilities without confusing intelligence with authority.
Together they form a safer nervous system and body for the one Raisa
intelligence acting through many Bureaus.

## Next tranche

AES-C1 will rehearse admission decisions over authored-synthetic instances of
this exact contract, still with no runtime, provider, product data, tool or
command. Work pauses here at Yuri's request so AES-C1 can begin in a fresh task
window after complete five-source rehydration.
