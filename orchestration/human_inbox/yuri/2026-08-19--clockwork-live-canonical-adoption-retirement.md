# Clockwork live canonical adoption and retirement

Date: 2026-08-19

Timestamp: 2026-08-19T14:03:19.0323770+10:00 (Australia/Brisbane)

Status: **accepted**

## Lay summary

The clockwork is live for EMR4's repository record-keeping. From now on, one
mechanism takes the closeout reading and updates the linked canonical records;
the old one-off updater programs can still be inspected as history but cannot
quietly publish a competing version.

The first live tick succeeded on its first publication attempt. It needed no
manual hash, revision, count or output-path repair, and it left no mixed state.
An independent Gemini review passed after executing all nine permitted checks,
including 743 governance tests. No product feature, patient data, deployment,
Pages build or protected branch was touched.

The build work was not cost-free: before activation we recorded eight
implementation correction cycles and three verification-shape corrections.
One of those caught a real Windows-versus-clean-checkout line-ending problem
that could otherwise have produced a false drift alarm. The live publication
itself succeeded once. The post-publication suite then required one validation
rerun because three old assertions still expected the shadow-rehearsal node;
they now explicitly read pre- versus post-pointer state. The canonical
generation was not republished or manually repaired. The next three qualifying
closeouts will publish the same readings so we can judge whether the mechanism
actually reduces recurring administrative mistakes.

## Technical summary

- Exact reviewed source:
  `9014e08a3fb4e3253759e0133d93c5aaf99a7ace`.
- Active generation/bundle:
  `f3b629e6cbe28061d1340c8ee75fb11e46847a9343338608a780ff3b4240885c`.
- Previous immutable Git generation:
  `git-9014e08a3fb4e3253759e0133d93c5aaf99a7ace`.
- Ownership: 10 clockwork surfaces, 0 dual-owned, 4 retired writer classes.
- Historical inventory: 145 updater programs preserved; 137 centrally guarded
  and 8 explicitly guarded.
- Safety proof: 15/15 pre-pointer fault points restore exact bytes; post-pointer
  classification requires full reread; disposable rollback/re-adoption is
  byte-exact; manual drift is denied.
- Verification: 7 focused tests, 743 portable manifest tests, 10/10 complete
  Compass evidence tests, Ruff lint, compilation and exact diff checks; fresh
  Gemini 3.7 Flash/high decision `pass` with a clean postcondition.
- Live efficacy reading: 1 publication, 1 validation rerun for stale
  shadow-node assertions, 0 canonical republications, 0 live rollbacks,
  0 live guard trips, 0 manual derived-field edits, 0 bespoke updater runs.
- Protected refs: local/origin `master` and `handoff/current` remain
  `2e34bdad732fdab32fbf778280b3d3c70d66d602`.

The new latch proceeds read-only to resolve the true next check-in successor.
It cannot repeat the accepted route tranche or enable ordinary practice.
