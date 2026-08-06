# Ariadne agent-error register revision 52

Date: 2026-08-06

Status: migration/transaction command-coupled alias recovery active

## AER-0051 remains open

The first three vetoes and recoveries remain preserved in revisions 49-51.
Candidate `62c78cba72c99b00a0087738b771d05f0adf2c06` correctly confined the
appointment UUID to one owner-private bridge, denied non-producer access, copied
only the opaque alias into durability evidence and separated the bridge from all
three durability retention families.

The fourth genuinely fresh veto found two further P1 defects. The producer still
had an independently invocable alias create-or-return path that did not
database-revalidate an exact signed update-confirm command, so a producer login
could persist an alias outside the intended mutation transaction. The bridge
also lacked reverse tenant/source alias uniqueness and allowed a future delete/
recreate to change identity or reuse an alias.

Sol preserved and rejected the candidate and extended the same recovery lease.
The fourth recovery removes every separately executable alias helper. The
producer may execute only one owner-mediated projection entry point, which
rederives `session_user` and the exact practice/source binding, then locks and
revalidates the exact `IN_PROGRESS` update-confirm operation/route/request
claim. It loads the sole event through the existing unique practice/command
foreign-key binding and verifies its appointment, audit and aggregate revision
against the claim and locked product state before any bridge, head or outbox
effect. The signed command and projection remain on one physical connection,
transaction, logical capability and session identity. Standalone, completed,
absent, foreign or mismatched invocation fails before effect. Appointment
truth, audit, event, alias, head, outbox and idempotency completion roll back
together.

The bridge key is now `(practice_id, source_contract_id,
product_appointment_uuid)` with reverse uniqueness on `(practice_id,
source_contract_id, opaque_aggregate_alias)`. The owner alone generates the
alias. Same-appointment races return the exact existing mapping; cross-
appointment collision fails the command. Rows and aliases are immutable and
non-deletable/non-reusable for the v1 epoch. Any later erasure/non-reuse design
requires a new reviewed contract, migration and source epoch.

A genuinely fresh exact-head veto remains required before plan acceptance or
the inert DDL rehearsal.

## AER-0052 corrected

The review environment control remains effective. The fourth veto used only the
proven absolute system interpreter with `--noconftest`, no cache and no bytecode,
passed 6/6 focused checks and left exact worktree `r26` unchanged.

Revision 52 contains 52 bounded incidents: 40 agent-behaviour observations,
three harness failures, two repository defects and seven transport timeouts.
AER-0051 is the sole open incident. Counts remain workflow-improvement signals
and do not establish model, provider, transport or role causation.
