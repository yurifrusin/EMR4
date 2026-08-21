# DeepSeek native Harness inert-task sentinel-readiness proof

Date: 2026-08-21
Timestamp: 2026-08-21T17:44:30.1265992+10:00 (Australia/Brisbane)
Yuri attention required: **no**

## Lay summary

The Harness has now crossed the startup point that repeatedly stopped the
earlier DeepSeek worker attempts. One clean, non-repeated test supplied the
mandatory harmless task string; the repaired sentinel activated and the stock
Harness reported ready. It then shut down cleanly. No DeepSeek call was made and
no provider cost was incurred.

This is a meaningful positive result: the native Harness itself is no longer
stuck before readiness in our bounded configuration. It does not yet prove that
an actual DeepSeek worker can complete useful EMR4 development work. The next
step is a no-provider readiness decision for a fresh attempt 005, followed by a
separately controlled occupied attempt only if every gate passes.

The clockwork also did useful work here. It rejected my first receipt because I
had copied two full commit IDs into prose instead of taking the machine reading.
That mistake was contained before planning or execution, exactly as intended.

## Technical summary

- Exact executed source:
  `1b4b2b4f04ff29ace609f788fc9fb891d933bb24`.
- `@deepseek-ai/dsh@0.1.0-rc.7`, one Node/Harness process, one inert task,
  six argv elements, zero retries.
- Ordered events: `sentinel_activated`, `stock_headless_hmr_ready`.
- Runtime: 5,289 ms; controller-owned termination after readiness; exact
  process and disposable-root absence.
- Zero runner, broker, worker, prompt, tool, model, provider, network, Docker or
  database activity.
- Raw streams/environment destroyed; only bounded digests and terminal fields
  retained.
- 25 current/applicable tests plus Ruff, compilation, diff and protected-ref
  checks pass.
- Revision 593 records four contained workflow corrections; none is open and
  none caused another native process.

## Deliberately closed

No occupied worker or provider request, product or patient data, product source
change, ordinary-practice enablement, production runtime, deployment, release,
Pages or protected-ref movement occurred. `docs/branding/` and all unrelated
untracked files remain preserved.

## Next

The engine is continuing with the provider-free, process-free attempt-005
readiness and preexecution decision. Yuri's attention is not required.
