# DeepSeek native Harness authored-synthetic traceability micro-rehearsal closeout

Date: 2026-08-18

Timestamp: 2026-08-18T14:37:03.9470128+10:00 (Australia/Brisbane)

Status: accepted bounded no-call traceability result

Reasoning level: high

Accepted evidence source: `ed044625b6f1e59d323c21ced6ec6e2372a11d3f`

Result:
`deepseek_native_harness_authored_synthetic_traceability_micro_rehearsal_bounded_no_call`

## Outcome

The official pinned `@deepseek-ai/dsh@0.1.0-rc.7` package was bootstrapped in
an isolated disposable workspace with its own npm cache and Harness home. The
package version and registry shasum/integrity were exact. The headless profile
was restricted to DeepSeek V4 Flash/high, 64 output tokens, zero retries,
disabled telemetry, no auxiliary title-model call and zero enabled
model-facing tool registrations.

The sole provider-capable process started at
`2026-08-18T14:23:57.1352788+10:00` and exited 1 after 2002 ms. It emitted zero
stdout bytes and 5302 stderr bytes. Its exact local failure was
`llm-deepseek: retryPolicy.retryableCodes must not be empty`: the static config
dump accepted an empty list, but the adapter runtime rejected it during
plugin-tree load. A credential-absent diagnostic reproduced the same pre-I/O
failure. No provider request, retry, fallback, auxiliary model request, tool or
subagent started; no sessions directory or session/trace file was created and
provider cost was zero.

The empty-list admission mistake is preserved as AER-0443 and contained
without retry. AER-0439 through AER-0445 also preserve the bounded discovery,
output, workspace-classification, exact-SHA and cleanup corrections. The exact
disposable directory and cache were sent to the Windows Recycle Bin after
their safe metadata was reduced; independent readback confirmed absence.

## Assessment

The native Harness provided a materially clearer local failure than the recent
Claude Code non-result: nonzero exit, exact failing invariant and a stable
pre-provider stage. That is positive traceability evidence for the launcher,
not model-performance evidence. Because no inference request occurred, this
tranche cannot compare DeepSeek reasoning, coding quality, latency, provider
reliability or cost, and it cannot select the native Harness as EMR4's default
worker transport.

## Parallelism closeout

- DeepSeek lane: completed as a bounded no-provider-call process result. It
  owns only the exact terminal and trace-absence metadata.
- Gemini lane: declined, neutral. No product/runtime source changed and a
  second external model could not validate a provider call that never began.
- Native-subagent lane: declined, neutral. Current developer policy prohibited
  proactive delegation and no parallel work package existed.

All work remained serial and Sol alone admitted the outcome.

## Protected boundaries

No EMR4 source or untracked file entered the Harness workspace. No product,
patient, clinical, historical-diary or protected data was used. No raw
reasoning, request/response body, credential or environment dump was
persisted. No default transport, product route, feature flag, ordinary-practice
authority, deployment, production, release, Pages or protected ref changed.
`docs/branding/` and every unrelated untracked file remained excluded.

## Next tranche

Resume product work with the narrow read-only
`raisa-provider-free-read-only-canonical-check-in-ordinary-admission-and-atomic-two-client-cutover-orientation`.
It may map the fail-closed gates for later ordinary admission and one atomic
Diary/Reception One cutover, but it authorises no admission, client change,
generic-status `Arrived`, waiting-area movement, data, provider, runtime,
deployment or protected-ref movement.
