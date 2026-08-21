# DeepSeek native Harness future-runner materialisation — paired closeout

Date: 2026-08-21

Timestamp: 2026-08-21T22:25:11.2517454+10:00 (Australia/Brisbane)

Yuri attention required: **no**

## Lay summary

We can now build the important control parts of a future DeepSeek Harness run
as a complete inspectable object before DeepSeek is allowed to start. The exact
runner and diagnostic helper are placed in a new disposable attempt directory,
the broker and diagnostic readings have fixed forms, and the controller writes
one fixed terminal result. It cannot freely describe an invented stage: it must
choose one of the registered outcomes from the two independent readings.

This is a modest but significant control gain. It turns another portion of a
DeepSeek run from an LLM-mediated narrative into deterministic machinery that
the orchestrator can prepare, inspect, reject and later monitor. It still does
not show that DeepSeek itself performs useful work or that the native Harness
can complete an occupied run.

## Technical summary

- Accepted task-branch source:
  `55906f55dfd82474f095acaa9dc436013db77411`.
- Exact materialiser SHA-256:
  `73ea743106ab07409c21d5d29f53b0b6845584fa41fe8125751dba63fe413c0c`.
- Exact six-path future-attempt roster with exclusive writes and complete
  readback.
- Exact accepted runner/helper/controller hashes remain separately bound.
- Terminal selection is closed over generic terminal, supported pre-request
  failure and unresolved request boundary.
- Completed verification: 38 focused, 149 inherited and 548 governance tests;
  generator, Ruff, compilation and diff checks pass.
- Seven technical workflow observations were corrected before closeout and
  enter revision 598 with none open.

## Deliberately closed

No Node, native Harness, broker, DeepSeek worker, model or provider ran. No
occupied attempt, retry, fallback, product/configuration/API/database change,
ordinary-practice enablement, patient/appointment/clinical data, production,
deployment, release, Pages or protected-ref movement occurred.

## Place in Raisa and next tranche

This supplies the deterministic “casing and gauges” around the future DeepSeek
worker process. The next tranche will replace the retained predecessor identity
and consumed authored-synthetic target with one fresh inert future-attempt
identity and target, while keeping execution disabled. After that, the already
named stock-headless-to-custom-runner boot proof can test the native Harness
under the assembled controls.
