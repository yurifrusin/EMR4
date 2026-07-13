# Proposal Idempotency Syntactic Tranche Closeout

| Item | Result |
|---|---|
| Tranche | S19-S21 |
| Integration commit | `6a35d2f2` |
| Worker commit | `e8d9bee7` |
| Sol correction | `ae8dda5b` |
| Acceptance | 308 passed, 0 failed |
| Runtime authority | Syntactic proposal header only |

## Delivered

- Create, update, status, and delete proposal routes now require a nonblank
  `Idempotency-Key` through one proposal-only validator.
- Missing or blank keys fail with HTTP 400 and
  `idempotency_key_required`; the existing create error message is preserved.
- Dynamic tests cover missing, blank, and valid keys while checking that
  proposal evaluation leaves appointment state unchanged.
- Static contract tests prove proposal handlers do not claim or complete the
  durable appointment command replay ledger.
- The continuity index now distinguishes `syntactic_only` proposals from
  `ledger_wired` confirmations.
- Confirmation, raw compatibility, and waiting-area proposal behavior remain
  unchanged.

## Supervisory Correction

Sol found that the worker-updated continuity table still retained prose saying
proposal enforcement was deferred. The correction removed that contradiction,
kept durable replay explicitly closed, and converted internal update-proposal
calls to keyword arguments so route dependency positions cannot drift silently.

## Evidence

Final independent acceptance covered proposal integration, confirmation
contracts, OpenAPI drift, continuity parsing, and API Spine artifacts:

```text
308 passed, 0 failed
```

Two existing dependency deprecation warnings remain: Starlette `httpx` test
client compatibility and Google GenAI `_UnionGenericAlias` usage.

## Harness Observation

The DeepSeek Flash Claude-Code launcher exceeded the operator's 15-minute shell
wait, but its child process remained active, continued changing the isolated
worktree, and eventually wrote a successful receipt and commit. Elapsed time or
an outer-shell timeout must therefore not classify a worker as failed while the
child process, worktree delta, or receipt channel still shows progress.

The durable runner should eventually expose a run identifier, child-process
state, heartbeat or last-progress timestamp, and explicit cancellation. For
now, operators must inspect those signals after a launcher timeout before
retrying or terminating a worker.

The Claude adapter reported US$15.284927 for the Flash run. This is a
non-authoritative adapter estimate, not DeepSeek billing. The existing
Pro/high calibration must not be applied to Flash; an exact provider usage
delta is required before adding a Flash calibration.

## Remaining Boundaries

- `/proposals/waiting-area/{appointment_id}` remains outside the four canonical
  OpenAPI proposal paths and has no new header requirement.
- Raw compatibility writes still require a separate migration decision.
- No provider, schema/migration, external-client, GraphQL mutation,
  historical-diary/H-series, memory/RAG/GraphRAG, deployment, or new write
  authority gate was opened.
