# Delete-confirm authority-counter recovery addendum

Date: 2026-08-16

Timestamp: 2026-08-16T13:28:31.5738356+10:00 (Australia/Brisbane)

Status: `explicitly_authorized_one_repair_one_final_attempt`

## Authority and diagnosis

After the fail-closed stop at `b4b772dd07a91e89db57fdd23bb1b4afb199a7e7`,
Yuri explicitly authorized the recommended continuation: one further narrow
AER-0353 harness-counter repair and one final occupied attempt.

The accepted contract's `authority_calls` field counts invocations of the
complete `_authority_valid` decision. The harness instead incremented that
field only when its SQL observer saw a downstream grant-table query. In
`TX-S06`, missing-grant reaches the query, while stale-generation and role
mismatch correctly fail before it. Three semantic checks therefore appeared as
one SQL-derived count. The product service is unchanged and correct.

## Exact repair

Only the behavior rehearsal harness, its focused test, AER-0353 metadata,
semantic-freeze/latch/receipt evidence and generated pass/failure evidence may
change.

The harness must:

1. save the exact private `physical._authority_valid` callable;
2. install a serial process-local wrapper that increments `authority_calls`
   once per semantic invocation and delegates without changing arguments or
   result;
3. stop deriving that counter from `grant_authority_check` SQL tokens;
4. retain the SQL token trace independently;
5. restore the exact saved callable in `finally` on every outcome; and
6. prove by focused tests that early denial counts one check, ordinary
   new/replay paths retain two checks per invocation, and the wrapper cannot
   survive the invocation boundary.

No migration, model, service, route, public contract or product source may
change.

## Attempt and stop rule

After focused tests, Ruff, compilation, schema validation, whitespace, the
canonical profile, final semantic freeze and fresh five-source receipt pass,
exactly one occupied attempt may run under the existing internal-only,
portless, tmpfs PostgreSQL 16 and fixed-loopback-relay boundary.

That attempt must pass all nine authority groups, all eleven transaction groups
and exact cleanup. Any failure or cleanup ambiguity stops with no further local
repair or retry. A pass proceeds to the already-required single Gemini 3.7
Flash/high veto.

## Reusable harness control

Evidence counters must attach to the semantic event named by their contract,
never merely to a downstream side effect that a legitimate early-return path
may skip. SQL traces and semantic counters remain independent evidence streams.

## Parallelism and protected boundaries

DeepSeek is not applicable because its worker lane is closed and the correction
is already fully diagnosed. Gemini remains reserved for one post-pass veto.
Native subagents remain declined because the wrapper and database lifecycle are
serial and native delegation is not authorized. All product/patient/clinical
data, mounted routes, providers/credentials, external networks, deployment,
release, Pages and protected refs remain closed. Preserve `docs/branding/` and
every unrelated untracked path; stage explicit paths only.
