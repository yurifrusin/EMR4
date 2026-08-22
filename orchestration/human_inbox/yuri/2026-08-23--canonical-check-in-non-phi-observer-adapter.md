# Canonical check-in non-PHI observer adapter

Date: 2026-08-23

Timestamp: 2026-08-23T00:07:27.9299596+10:00 (Australia/Brisbane)

## Lay summary

The check-in work has moved from a list of measurements to a small executable
component. EMR4 now has a typed adapter that knows how future check-in decisions
could become five measurements and six critical alerts without carrying patient,
appointment, practice or staff identifiers.

It is deliberately unplugged and locked off. It cannot send a measurement,
deliver an alert, change a command or even inspect its input while disabled.
Ordinary practices remain denied and the product is unchanged.

The adapter also refused to disguise a real vocabulary difference: one denial
exists only in the current rehearsal kernel, while three outcomes belong only
to a future production kernel. They remain visibly separate rather than being
renamed to make the forms appear to match.

## Technical summary

- reviewed source: `1fb1db90e1fdbf73d4dcbaf7d51793f4320ba8b5`;
- new module: `orchestration_harness/check_in_observability.py`;
- evidence: 15 focused and 132 integrated checks pass;
- exact shape: five metric intents, six non-identifying/non-actuating alerts,
  twelve shared reasons, one rejected rehearsal-only reason and three
  unavailable future-only reasons;
- disabled behavior: zero supplier calls and the shared empty batch;
- cost: zero workers, providers, databases, Docker or product-runtime changes;
  and
- protected refs and `docs/branding/` remain untouched.

One brittle prose assertion required a local correction; the code and contract
did not. Fresh rehydration also noticed that the preceding three closeout
summaries lacked their required ISO timestamp. The next very small workflow
tranche will restore those timestamps and add one reusable current-node guard,
so future closeouts fail automatically instead of relying on memory. Yuri's
attention is not required.
