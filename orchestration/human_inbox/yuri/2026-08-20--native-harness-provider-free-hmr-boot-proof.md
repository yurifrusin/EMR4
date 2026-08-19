# Native Harness provider-free HMR boot proof

Date: 2026-08-20

## Plain-language summary

The Harness startup problem is fixed and proved in the real pinned Harness,
without calling DeepSeek. The stock headless launcher started with the missing
Node prerequisite, announced that its own live configuration watchers were
ready, accepted a watched configuration change, loaded our local runner, and
let that runner close the process successfully.

That is the useful conclusion we needed: the previous failure was a specific
startup prerequisite, not an unexplained disappearance. We can now attribute
whether a later worker reached the custom runner instead of losing the trail
before the session begins.

One initial controller check rejected before the Harness process started
because it looked for the documented `headless` text in the wrong formatting.
It started zero native runs, called no provider, and cleaned up. The check was
narrowly corrected and covered by a regression test before the one real native
attempt. Nothing was erased or silently retried.

## Technical summary

- Exact package: `@deepseek-ai/dsh@0.1.0-rc.7`
- Reviewed candidate: `5c3325e9213afc5690453812e2078c61135c8a38`
- Native attempts: 1
- Native result: exit 0 in 10,597 ms
- Lifecycle events: 4/4 exact and ordered
- Network/model/broker/provider/session counts: 0/0/0/0/0
- Focused deterministic tests: 39/39 passed
- Gemini: fresh 3.7 Flash/high pass, ten commands, no P0-P2 finding
- Native/review worktrees and processes: absent
- Source-inspection directory: moved to the Windows Recycle Bin
- Protected refs: all four remain
  `2e34bdad732fdab32fbf778280b3d3c70d66d602`

This proves startup/HMR traceability, not DeepSeek's coding performance or
production readiness. It opens no model call or product/practice authority by
itself.

## Next tranche

The prerequisites are now satisfied to freeze the separately named provider-
free relay-free recovery attempt 004. That next tranche begins with a fresh
plan and exact one-run admission; it does not inherit permission to improvise a
Docker/database run or DeepSeek call. Attempts 001-003 remain immutable. Your
attention is not required under the standing authority.
