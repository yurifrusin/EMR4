# Attempt-004 Readiness and Preexecution Decision Threat-Model Delta

Date: 2026-08-21
Timestamp: 2026-08-21T11:48:44+10:00
Status: `frozen`

## Scope

This delta covers only provider-free deterministic readiness for a possible
fourth authored-synthetic native-Harness bounded-worker attempt. It introduces
no product or occupied runtime surface.

## Threats and controls

| Threat | Fail-closed control |
|---|---|
| A consumed attempt is silently reused | Exact identities 001-003 must each be `consumed`, non-resumable and byte-bound to the accepted immutable inventory. Attempt 004 has a disjoint identity and absent outputs. |
| A short or manually copied Git ID binds the work | The checker resolves the full 40-character object from Git. Static caller-authored object IDs are rejected at orchestration receipt boundaries. |
| Readiness accidentally starts the Harness or provider | Tests forbid `subprocess.run`, `subprocess.Popen` and network entry points. The evidence requires zero Node, Harness, broker, worker, session, prompt, tool, model, provider and network counts. |
| Attempt 004 reuses a stale clockwork lease | Readiness records the current clockwork parent read-only. The occupied successor must take a fresh post-closeout reading and derive its work order from that newer acknowledged tip. |
| Preset or tool authority widens | Exact preset digest and the ordered tool set `edit`, `glob`, `read` are bound. Shell, test, Git and database tools remain unavailable to the worker. |
| Startup failure becomes untraceable again | The converged wrapper writes a bounded canonical structured diagnostic inside the disposable root; exactly one selected terminal is written outside the root before cleanup. Absent or invalid diagnostics fail closed to the legacy terminal with an explicit classification reason. |
| Readiness is misread as occupied authority | The result says `occupied_attempt_authorized: false`. A separately latched operation and fresh preexecution checkpoint are mandatory before one execution. |
| Retained evidence leaks raw output or data | No raw prompt, response, reasoning, credentials or startup streams are retained. Only bounded hashes, counters, coordinates and allowlisted synthetic values may be recorded. |
| Scope drifts into EMR4 product behavior | `no_ordinary_practice_enablement_feature_flag_allowlist_or_command_mounting`; no generic-status `Arrived`, route, adapter, grammar, client, waiting-area, product, patient, clinical or database change. |
| Cleanup obscures the terminal | Terminal selection and exclusive external write precede exact-root removal. Ambiguous cleanup is a failed terminal, not success. |
| Retrying conceals a failure | Zero retry, resume, fallback and second-worker authority. Any failed gate ends this readiness decision as `not_ready`. |

## Residual risk

A passing provider-free gate cannot prove provider availability or that the
occupied request will succeed. It proves that one fresh, bounded and traceable
attempt can be represented without reusing consumed identities or stale
clockwork time. The occupied result must be judged from its own terminal
evidence.
