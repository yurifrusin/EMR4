# Ariadne agent-error register revision 53

Date: 2026-08-06

Status: migration/transaction provenance recovery active

## AER-0051 remains open

The first four vetoes and recoveries remain preserved in revisions 49-52.
Candidate `77ba83d5f1695ac58eddd0e96f6ec8003247e339` correctly removed the
alias-only helper, bound the sole event through the existing practice-scoped
command foreign key plus command uniqueness, froze one transaction/session
capability and made the owner-private alias mapping immutable and bijective.

The fifth genuinely fresh veto found that coherent row state did not itself
prove current-transaction provenance. A later transaction using the same login
could theoretically adopt a committed in-progress claim. It also found that
all six focused tests asserted documentation phrases rather than parsing model
constraints or rejecting adversarial architecture mutations.

Sol preserved and rejected the candidate under the same recovery lease. The
fifth recovery compares the claim, current appointment tuple, audit and event
`xmin` with database-derived `pg_current_xact_id()`, forbids any exact update-
confirm claim from committing `IN_PROGRESS`, rejects prior-transaction claim
adoption and adds bidirectional before/deferred fail-commit invariants over the
event, completed claim, alias, stream head and outbox. XID is ephemeral: it is
not caller-supplied, stored, retained, exposed, hashed or used as position.

A closed JSON contract and JSON Schema now freeze all 18 relations, current
model bindings, provenance/commit-fence invariants, alias keys/lifecycle and the
owned artifact surface. Focused tests validate that contract, parse the actual
idempotency/event model constraints and reject relation, provenance, atomic-
member, alias and forbidden-path mutations.

A genuinely fresh exact-head veto remains required before plan acceptance or
the inert DDL rehearsal.

Revision 53 still contains 52 bounded incidents: 40 agent-behaviour
observations, three harness failures, two repository defects and seven
transport timeouts. AER-0051 is the sole open incident. Counts remain workflow-
improvement signals and do not establish model, provider, transport or role
causation.
