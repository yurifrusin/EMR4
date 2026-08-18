# Provider-free default-off canonical check-in route-adapter convergence rehearsal closeout

Date: 2026-08-18

Timestamp: 2026-08-18T13:39:45.6642329+10:00 (Australia/Brisbane)

Status: accepted

Accepted reviewed source: `c82c3a741053a9c8da260aa62e1a968af22bb54e`

Result:
`raisa_provider_free_default_off_canonical_check_in_route_adapter_convergence_rehearsal_pass`

## Outcome

The existing A5.1 check-in confirmation route now delegates exactly once to
the accepted canonical `compose_product_check_in` adapter. Its unchanged
feature flag and exact authored-synthetic practice allowlist still deny the
route before database lookup, dependency construction or adapter invocation.
The request schema, response schema, status codes, idempotency codes/messages
and default-off posture remain unchanged.

The route-owned dependency binder reuses the existing practice-scoped command
claim, exact appointment and actor locks, in-transaction Receptionist
reauthorization, same-practice waiting-area lookup, HMAC evidence verifier,
`Booked|Confirmed -> Arrived` effect, one command-bound audit, one patient-free
committed event, one completion, commit/rollback and exact committed readback.
The route has no second write path or fallback composition.

Compatibility required one narrow adapter correction. A structurally valid
same-key request is classified as replay/conflict/in-progress/failed before
semantic confirmation-envelope validation, preserving the existing HTTP
contract. A newly claimed invalid envelope rolls back. Explicit request-body
evidence retains precedence over the proposal copy while both remain bound to
server practice, actor, appointment, state, area and freshness truth.

No practice was enabled. Generic-status `Arrived`, action grammar, either
first-party client and waiting-area move/removal remain unchanged and closed.
No product, patient or clinical data, provider, deployment, release, Pages or
protected ref was accessed or moved.

## Verification

- 103/103 self-contained adapter and route-convergence tests pass;
- 35/35 database-backed A5.1 runtime checks pass with the unrelated obsolete
  Alembic-head expectation excluded and preserved as baseline evidence;
- 85/85 API-Spine and predecessor-plan checks pass with the predecessor's
  intentionally completed-latch assertion excluded;
- Python compilation, Ruff, exact diff whitespace and the complete 435-entry
  Ariadne incident-register suite pass as independently captured processes;
- the fresh Gemini 3.7 Flash/high veto returns `pass`; all eight exact manifest
  commands succeed, including 103 tests, and its exact clean HEAD is unchanged.

The repository-static import of the removed `_BERNIE_SESSION_STORE`, the stale
Alembic-head expectation and predecessor live-latch assertion remain
explicitly out-of-tranche baseline failures. This closeout does not hide or
repair them.

## Parallelism outcome

DeepSeek V4 Flash/high received the bounded route/adapter/tests package through
Claude Code `--bare`. That process ended after the bounded observation window
with exit 1, no terminal worker result, no source and a clean exact worktree.
AER-0427 preserves the transport non-result; no same-lane retry or late source
adoption was allowed. Sol completed the exact frozen package under the declared
recovery lease. Gemini then supplied the required independent veto. Native
subagents were declined because current developer policy prohibited proactive
delegation for this tranche.

## Workflow corrections

AER-0426 through AER-0435 preserve short-SHA completion, DeepSeek transport,
parallel-disposition, chained-command, package-CLI, timestamp and resumed
readback corrections. All are corrected or contained, none is open, and the
product candidate was rerun through independent gates after the command-scope
corrections.

## Immediate successor

Yuri explicitly authorised a very short native DeepSeek Harness rehearsal.
After this latch closes, the sprint engine continues into a separate isolated
authored-synthetic operation pinned to the released developer-preview harness.
It may perform one trivial no-repository task and capture version, exit status,
stdout/stderr digests and durable session/trace evidence for comparison with
the Claude Code transport failure. It receives no EMR4 source, product data,
patient/clinical material or authority to make the native harness the default.

The next product decision remains separate: ordinary-practice admission,
generic-status `Arrived`, grammar and atomic two-client cutover all require
their own future plan and acceptance.

## Claim boundary

Passing proves provider-free, default-off convergence of the existing A5.1
HTTP route onto the accepted check-in adapter using authored-synthetic fakes
and the repository's disposable local test database. It does not prove an
ordinary product command, a real practice, external concurrency/restart or
unknown-commit recovery, a client cutover, deployment or production. Local and
origin `master` plus `handoff/current` remain protected at
`2e34bdad732fdab32fbf778280b3d3c70d66d602`; `docs/branding/` and unrelated
untracked files remain preserved.
