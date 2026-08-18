# DeepSeek native Harness — first monitored EMR4 worker admission

Date: 2026-08-18

Timestamp: 2026-08-18T17:41:39.5012901+10:00 (Australia/Brisbane)

Yuri attention required: no

## Lay summary

The new Harness gave us the greater control and traceability we wanted, but
the first real EMR4 worker attempt did not reach DeepSeek. The Harness tried to
offer the model seven file tools when our safety contract allowed only three.
Our separate broker caught that mismatch and stopped the request before any
provider call or code change. We can now say exactly what failed, in under a
second, with no mystery process and no wasted model run.

This is not a successful worker result, but it is a useful systems result: the
outer Ariadne controls successfully constrained the inner Harness. We have not
weakened the broker to make the run pass. The next step is to use the Harness's
own scoped-tool mechanism so the model genuinely sees only the three intended
tools, prove that without contacting DeepSeek, and then run one fresh monitored
worker attempt.

## Technical summary

At evidence source `af1a79f93024a7186849e550b4d529c8c601c93f`, the exact
rc.7 session produced four Zstandard frames and 17 logical rows. Its single
request header declared `edit`, `glob`, `grep`, `read`, `read_image`,
`str_replace_editor` and `write`. The broker allowlisted only `edit`, `glob`
and `read`, returned `tool-not-allowlisted` / HTTP 400, and emitted zero
provider-call-started events. The worker exited 1 after 761 ms with zero model
usage, zero tool calls, zero candidate diff and neither owned file created.

AER-0459 corrects the incomplete tool-inventory claim; AER-0460 corrects the
first overlong precommit latch checkpoint; AER-0461 and AER-0462 correct the
Continuity path and typed evidence inventories; AER-0463 corrects the
pre-existing stale Compass current-node sentinel. Register revision 402 passes
with 463 incidents, none open. All containers, volumes, networks, raw-session
storage, worker worktree and worker branch are absent; the disposable profile
root is in the Recycle Bin.

## Deliberately closed

No patient, clinical, product, historical or protected data; no application
source or behavior; no ordinary-practice enablement; no product runtime,
deployment, release, Pages or protected-ref movement. `docs/branding/` and all
unrelated untracked files remain untouched.

## Programme position and next work

This closes the first monitored native-Harness EMR4 admission as attributable
negative evidence at Continuity 320 / Compass 302. The next tranche is
`deepseek-native-harness-exact-tool-view-recovery-and-second-monitored-development-admission`:
prove an exact provider-free `read`/`glob`/`edit` model tool view, then permit
one fresh second monitored attempt over the same two owned validator paths.
No decision or action is required from Yuri.
