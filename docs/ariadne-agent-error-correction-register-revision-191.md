# Ariadne Agent Error and Correction Register — Revision 191

Date: 2026-08-08

Revision 191 appends `AER-0220` and does not rewrite any earlier incident.

`AER-0220` records two fail-closed receipt-drafting errors before the
receipt-lock behavior-parent candidate commit. The first state chose
`pre_commit` without the current required adapter and managed-worker
inventories. A distinct `pre_integration` state still copied an older sparse
inventory pattern. Both deterministic receipts returned `revision_required`;
nothing was staged, committed, dispatched or run.

The corrected distinct v2 state enumerates all six current transport adapters
with admitted observation methods and the required `deepseek-flash-workers`
slot with zero active or stale instances. Its receipt must pass before the
candidate can be explicitly staged and committed.
