# Status-confirm off-route composition rehearsal — lay and technical closeout

Date: 2026-08-12

Result: **passed**

## Lay summary

The safer appointment-status machinery now has an assembled connector that can
be exercised beside the live doorway without attaching it. It checks the
current staff/session authority, checks the appointment again inside the locked
transaction, commits one coherent result, and gives an exact saved answer on a
retry. Revoked access, stale context, missing appointments, conflicting retries
and incomplete work all stop without leaking a success response.

The rehearsal also caught and resolved an important design mismatch: the live
doorway returns a fuller appointment result than the earlier five-field receipt
design could remember. The connector now freezes the full existing result for
replay and treats those five fields as a cross-check. That avoids reconstructing
an old success from newer database state.

Nothing is connected to the live route yet. The next safe step is a read-only
re-review to see exactly which plumbing pieces remain before mounting can even
be proposed.

## Technical summary

- source: `41f978ae9837cba50737cfb5f457ab62ac28dbdb`
- result: `raisa_provider_free_unmounted_status_confirm_route_convergence_composition_rehearsal_pass`
- evidence: 12/12 scenarios, 65/65 hostile mutations
- checks: 13/13 focused, 163/163 current status-confirm lineage, 191/191
  canonical
- response rule: complete current envelope stored as canonical bytes; five
  status fields validated as a projection; initial/replay bytes identical
- runtime state: service is unmounted and absent from the router
- next: provider-free read-only route-mounting readiness re-review

No route or database was executed. No product/patient data, provider,
credential, deployment, Pages or protected ref was touched. Yuri's attention
is not required.
