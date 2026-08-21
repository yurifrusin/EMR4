# Harness post-sentinel exit diagnosis — lay and technical closeout

Date: 2026-08-21

## Lay summary

We found the reason the repaired sentinel started and then the harness stopped.
It was not an inexplicable DeepSeek or harness failure. Our deliberately tiny
test started the headless profile without the task text that this profile always
requires. The sentinel had enough time to report that it was alive; the
headless startup logic then correctly rejected the missing task and shut the
process down before the readiness marker.

That is good news. The custom sentinel loading is sound, and the remaining test
shape correction is very narrow. The next rehearsal will add one inert
authored-synthetic task solely to satisfy startup while keeping the actual
headless worker disabled. It will still make no model or provider request.

## Technical summary

- Accepted source: `07b371090e0f8efe045f9ff39aab409c74244c1b`.
- Coordinate:
  `headless_startup.apply.missing_task_program_error_to_app_exit_one`.
- Static chain: `8 / 8` exact links passed.
- Terminal: `sentinel_activated`, exit `1`, readiness false, retry zero.
- Verification: 37 applicable tests, Ruff, `py_compile` and diff checks passed;
  four immutable pre-repair selectors are explicitly excluded.
- Activity: zero Node, Harness, broker, worker, model, provider, network and raw
  stream reconstruction.
- Protected refs remain fixed at
  `2e34bdad732fdab32fbf778280b3d3c70d66d602`; no Pages or product surface
  opened.
- The usual non-PHI Pushover notification passed.

The clockwork will allocate three contained observations: one helper-count
predicate, one overbroad prose-vocabulary assertion, and one historical-selector
applicability lapse. None reached canonical evidence and none remains open.
