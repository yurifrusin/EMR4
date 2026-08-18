# DeepSeek native Harness — exact tool view and second monitored EMR4 attempt

Date: 2026-08-18

Timestamp: 2026-08-18T20:37:23.2818490+10:00 (Australia/Brisbane)

Yuri attention required: no

## Lay summary

We proved the most important control improvement: the native Harness can be
made to show DeepSeek exactly the three file tools we choose—read, search and
edit—rather than the seven tools that caused the first attempt to be rejected.
That proof was completed without contacting DeepSeek.

The subsequent real worker attempt still did not reach DeepSeek. It stopped in
under one second because the Harness's own headless hot-reload component needs
a particular Node startup flag. The useful difference from the old Claude Code
failures is that nothing is mysterious: we know the exact component,
prerequisite, timestamps, zero provider-call count and zero changed files.

So the Harness remains interesting and demonstrably more traceable, but it has
not yet earned default-worker status. The failed attempt was not retried. We
will resume the planned check-in route work under Sol while keeping this exact
startup prerequisite as the gate before any future DeepSeek Harness worker.

## Technical summary

At exact evidence source `00d4f8d6065ab09b5faf5501c979edd2fa59943c`,
provider-free rc.7 composition exposed sorted `edit`, `glob`, `read` through
the native preset mount plus `ctx.tools.restrict` mechanism. It recorded one
local request, zero external/provider calls and complete cleanup.

The occupied container then exited 1 between
`2026-08-18T10:26:51.753301918Z` and
`2026-08-18T10:26:52.449169924Z`. `cordis-plugin-hmr` rejected startup because
Node lacked `--expose-internals`. The custom runner, session and broker request
path were not reached. Broker request/provider/response counts were 0/0/0;
candidate changed-path count was zero. Register revision 445 passes with 515
incidents and none open.

All containers, volumes, networks, raw-session storage, worker worktree and
worker branch are absent. The disposable root is in the Windows Recycle Bin.

## Deliberately closed

No patient, clinical, product, historical or protected data; no application
source or behavior; no ordinary-practice enablement; no runtime, deployment,
release, Pages or protected-ref movement. `docs/branding/` and all unrelated
untracked files remain untouched.

## Programme position and next work

This closes at Continuity 321 / Compass 303. Next is the already authorised
`raisa-provider-free-default-off-canonical-check-in-route-adapter-convergence-rehearsal`.
The native Harness is paused from occupied EMR4 work until a separate provider-
free HMR startup proof. No decision or action is required from Yuri.

The usual non-PHI Pushover closeout notification succeeded with request
`2585170d-71b3-40ee-a8bd-777da80a6d58`.
