# A safe observation window beside the old appointment routes

Date: 2026-08-12

## Lay summary

We now have a design for watching how the old appointment routes compare with
the new common-command rules without allowing the watcher to referee the race.
The real route finishes first: its response and database outcome are sealed.
Only then may a one-way, best-effort diagnostic copy be considered.

The observer starts off in four separate locked positions: the generation,
whole-system switch, practice switch and exact route must all say yes. Any
missing, stale or unknown value means no observation, and the emergency switch
can only turn it off. If the observer is slow, full or broken, its note is
dropped; the user's result cannot change.

The copy contains digests and structural labels, not request bodies, patient
details, notes, direct identifiers or command receipts. It is deliberately a
lossy diagnostic notebook, not a medical record, audit log or source of truth.

Nothing is running yet. The gain is a precise safety envelope for rehearsing
the observer before any route instrumentation is considered.

## Technical summary

- Accepted result:
  `raisa_provider_free_unmounted_default_off_shadow_comparison_architecture_pass`.
- Exact source: `e1dca1c6dc5d3f3e241548f80a226e5bb776417f`.
- Scope: exactly 4 raw route adapters; no confirm/proposal route.
- Admission: immutable current generation AND global AND practice AND exact
  route allowlist AND not externally disabled; all defaults deny.
- Primary status/body/headers/transaction/audit disposition seal before a
  one-way best-effort handoff with no return channel.
- Data boundary: 24 digest-only projection fields and 15 lossy diagnostic
  record fields; no raw/direct/patient/free-text/source/receipt material.
- All observer capabilities are false; 12 feedback edges are forbidden.
- 46 hostile mutations, 133 focused tests and the canonical 191-test profile
  pass; lifecycle checks pass at Continuity 249 / Compass 231.
- No route, runtime observer, queue/sink, database/source, event, watcher,
  provider, patient/product data, command, deployment, Pages or protected ref
  was opened.
- Next: provider-free unmounted authored-synthetic shadow-comparison rehearsal.
  Your attention is not required.
