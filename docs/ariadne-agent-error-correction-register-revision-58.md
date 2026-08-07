# Ariadne agent-error register revision 58

Date: 2026-08-06

Status: eighth migration/transaction architecture recovery active

## Recovery-7 veto preserved

The candidate-independent exact-head veto of
`b9de77ce09ab36edc61e43aa5294a78180460660` passed the frozen 209-test packet
but correctly returned `revision_required` for two P1 defects:

1. nine entry points and thirteen trigger functions had signatures and
   invariant bindings but no bodies, so the claimed inert renderer would have
   to invent security-critical PL/pgSQL; and
2. semantic validation required the admission relation among the receiver
   owner's reads but did not require the complete read list to be exact, so a
   digest-resealed product-table read widening could pass.

The complete decision is preserved at
`orchestration/agent_inbox/codex/raisa-context-fabric-durability-migration-transaction-architecture-recovery-7-independent-veto.md`.
It grants no acceptance.

## Eighth recovery controls

The corrected architecture does not manufacture twenty-two security-critical
bodies merely to preserve a sequencing claim. It instead makes the boundary
explicit and fail-closed:

- the current catalogue is structural/signature-only;
- a structural renderer must omit the nine entry points, thirteen trigger
  functions, their trigger declarations and every corresponding execute grant;
- the exact binding-helper body is the sole exception and may render only with
  no runtime bindings;
- inert DDL rehearsal is blocked until a separate provider-free unmounted
  function-and-trigger-body architecture closes every executable body and
  passes independent veto; and
- the admission receiver now has an exact six-relation read list, sole
  admission INSERT, empty relation ownership and empty execute list in both
  validator and hostile digest-resealed mutation evidence.

AER-0051 remains open pending acceptance. No SQL, migration, database, source,
runtime, provider, patient/product data, command, deployment, release, Pages or
protected-ref boundary changed.

Revision 58 contains the same 55 bounded incidents: 43 agent-behaviour
observations, three harness failures, two repository defects and seven
transport timeouts. Counts are workflow-improvement signals, not model,
provider, transport or role causation.
