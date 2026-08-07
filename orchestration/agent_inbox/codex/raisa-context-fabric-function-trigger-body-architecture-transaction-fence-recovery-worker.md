# Current-transaction fence recovery worker result

Date: 2026-08-07

Source HEAD: `7ad40bd337ac6433bd6cc84653dd5883679ed13b`

## Rehydrated sources

The worker read the controlling packet, `AGENTS.md` sections 3-7, the active
function-and-trigger-body plan, all four normative recoveries, the exact veto,
the immutable parent contract and the complete current trigger-program source
before editing. The exact source HEAD was verified and the three owned paths
were clean.

## Exact implementation

- The non-temporal appointment fence first selects only current-XID committed
  events for the exact practice, appointment, reschedule event type and schema.
- With no such event, it accepts an older immutable exact alias and rejects
  only an exact practice/source/stream/appointment alias inserted by the
  current XID.
- If a current exact event exists, it reloads the exact alias without imposing
  current provenance, then identifies only a current-XID outbox row joined to
  that event UUID, alias UUID and aggregate revision under the exact
  practice/source/stream. Its predecessor is bound to its transaction
  position.
- The matching head is current-XID, exact practice/source/stream/epoch, at that
  outbox position and authored at the transaction timestamp. The head guard's
  separate legal `OLD`/`NEW` one-position movement proof remains unchanged;
  the appointment trigger does not invent foreign-relation trigger images.
- The temporal-update proof, same-top-level-transaction second-update
  rejection, credential-inert behavior and trigger terminals remain unchanged.
- Focused operand-level tests require every current-XID discriminator and exact
  relational join, distinguish historical aliases/outboxes from current
  effects, and preserve legal trigger-image/terminal behavior.

## Static checks

- `.venv\Scripts\python.exe -m py_compile` on the two owned Python paths:
  passed.
- `ruff check` on the two owned Python paths: passed.
- No pytest process was started, as required for parallel work.
- `git diff --check` is recorded after this artifact is added.

## Remaining integration work

Sol must reconcile this disjoint source with the coordinator/retention and
normative-closure lanes, regenerate only the authorized aggregate artifacts,
and run the repository tests serially. This worker makes no acceptance claim.

RESULT: candidate_ready
