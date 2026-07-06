# Action Grammar Replay Boundary

The R30 replay consumer is intentionally separate from
`tests/bernie_scenarios/`.

The existing Bernie scenario replay harness exercises live backend routes,
database row-count effects, and provider guards. The R29 action grammar is not
wired into routes, prompts, UI, or database writes, so forcing it through that
route-level harness would create a fake dispatch layer before the product has
one.

This harness therefore tests a narrower contract:

- hand-authored synthetic fixture scripts only;
- no `local_data`, H-series profile, or full-trove input;
- no provider, route, model, migration, or database imports;
- consumer-side action resolution, dispatch refusal, and confirm-affordance
  pre-check behavior over the committed grammar contract.

When a future sprint wires grammar verbs into real backend routes, that sprint
must either extend `tests/bernie_scenarios/` or replace this pure harness with a
route-level replay that restores auth, provider, and database row-count checks.
