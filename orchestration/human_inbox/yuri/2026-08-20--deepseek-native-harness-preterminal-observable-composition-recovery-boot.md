# DeepSeek native Harness observable recovery boot — paired closeout

Date: 2026-08-20

## Lay summary

The single permitted rehearsal did exactly what the new recorder was designed
to make possible: instead of failing mysteriously, it reported the precise
bounded point `SERVICES_UNAVAILABLE`, kept a credible 10-second boot reading,
then shut down cleanly. There was no model/provider call, network attempt,
agent session or retry, and all temporary resources were removed.

This is not yet a successful `read`/`glob`/`edit` composition proof. It tells us
the runner loaded, but the Harness context had not exposed one or both of the
required preset/tool services. I will not rerun the consumed attempt. The next
step is a deterministic, no-Harness-process inspection and correction of the
exact rc.7 service-injection declaration before any separately named future
execution is considered.

## Technical summary

- Candidate `e4dddfcb48cd236e147bca2560e54f42d84017df` passed 12 focused and
  97 combined provider-free tests, Ruff, compile and cache-only checks before
  launch; the postterminal Harness/latch/clockwork/baton suite passed 170
  tests.
- Attempt
  `preterminal-observable-composition-recovery-boot-attempt-001` started one
  native process with zero retries.
- Exact readiness:
  `sentinel_activated -> stock_headless_hmr_ready`.
- Exact activation:
  `BOOTSTRAP_APPLY_ENTERED -> SERVICES_UNAVAILABLE -> EXIT_REQUESTED`.
- Terminal `SERVICES_UNAVAILABLE`; exit `2`; reliable duration `10025 ms`.
- Offline materialisation passed in `119731 ms`; all six installed packages
  were exact rc.7.
- Network, session, turn, broker, model, provider, occupied-worker, Docker and
  database counts are zero.
- Process wait, process absence and disposable-root absence all passed.
- Gemini was not dispatched because the frozen gate required a passing native
  composition terminal; DeepSeek/model and native-subagent lanes remained
  declined.
- Next:
  `deepseek-native-harness-provider-free-required-service-injection-recovery`,
  deterministic/provider-free with no native process.
- The required non-PHI Pushover closeout notification succeeded with request
  `b9600422-e6c6-4c94-8cc6-faf1949e3fd9`.

Yuri attention is not required. No product, ordinary-practice, data,
deployment, Pages or protected-ref authority changed. `docs/branding/` and all
unrelated untracked files remain preserved.
