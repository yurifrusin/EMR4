# Status transaction-kernel protocol — lay and technical closeout

Date: 2026-08-12

## Lay summary

The status-change safety choreography now works on paper and in a closed
simulator. Before changing an appointment, the future kernel must lock the
practice and appointment in one order, recheck the user's current authority,
verify the separate confirmation, reject stale information and settle repeated
requests consistently. The appointment change, audit record and completion
receipt then either all happen or none happen.

The rehearsal also covers the awkward case where the database commits but the
reply is lost: retrying returns the original receipt without changing the
appointment twice. Nothing was connected to the product or a database.

One policy remains intentionally deferred: whether a terminal appointment may
ever return to a non-terminal status. Today's product is fail-closed. The next
unmounted adapter contract will preserve that behavior while making the signed
confirmation-to-kernel translation exact.

## Technical summary

- accepted source: `bd381de83bc0b5d4b6b43b4bbb4e1e70a68d7f62`;
- result: `raisa_provider_free_unmounted_status_transaction_kernel_protocol_rehearsal_pass`;
- lock order: global `practice -> schedule_domain -> appointment ->
  idempotency_record`; status subset `practice -> appointment ->
  idempotency_record`;
- evidence: 15 decision scenarios, 11 schedules and 37 rejected hostile
  mutations;
- verification: 9 focused, 106 dependency/API, 308 mounted compatibility and
  191 canonical fast-profile tests pass;
- application tree and all pre-existing tests are unchanged by the source
  commit; and
- the prior live citation for compatibility source `48c1821a` is corrected to
  actual Git object `48c1821ad8b28c68204e70dea9972b6ba27e4dc1` without rewriting
  its historical closeout.

No patient/product data, provider call, runtime, database, route, event,
watcher, tool, command, deployment, release, Pages or protected-ref authority
opened.

Next: provider-free unmounted status-confirm kernel adapter contract. It remains
pure and non-executing.
