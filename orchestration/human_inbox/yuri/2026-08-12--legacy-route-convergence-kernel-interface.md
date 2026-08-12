# Legacy appointment routes and the common command kernel

Date: 2026-08-12

## Lay summary

We now have the blueprint for bringing the four old appointment write routes
and the newer proposal/confirm routes through one backend referee. Nothing has
been rewired yet.

The important result is that the old routes do not receive a free pass merely
because a logged-in person called them. Before any of them can enter the common
kernel, the backend must have separate confirmation where required, a genuine
precondition tied to what the user saw, a durable retry identity, current
authority and attributable audit. This preserves your intended rule: stale
context may invite an attempt, but only current source truth decides the winner
and only a committed transaction receives the ribbon.

Create is deliberately last. Update, status and cancel have an existing row to
lock; create needs a separately selected database-owned schedule fence so two
contenders for the same time cannot both win.

## Technical summary

- Accepted result:
  `raisa_provider_free_unmounted_legacy_route_convergence_kernel_interface_pass`.
- Exact source: `47e08eada878d8f6dd2a9b100e706404d3594e5a`.
- Mapped 4 raw, 6 proposal and 5 confirm routes across create/update/status/delete.
- All raw routes are `not_kernel_eligible_now`; there is no implicit-confirmation
  compatibility bypass.
- Frozen 8 typed outcomes, authority-before-replay disclosure and canonical
  practice/schedule/appointment/idempotency ordering.
- Frozen migration: inert adapter proof, optional non-enforcing shadow,
  client parity, status, delete, update, create-fence proof, create, then only
  later deprecation and retirement decisions.
- 48 hostile mutations, 110 focused tests, the full error-register suite and
  191 canonical repository tests pass.
- AER-0290 records and corrects one rejected receipt-event spelling recurrence;
  no planning or runtime action occurred under it.
- No route, database/source, event, watcher, provider, patient/product data,
  command, deployment, Pages or protected ref was opened.
- Next: provider-free unmounted pure route-adapter differential rehearsal.
  Yuri's attention is not required.
