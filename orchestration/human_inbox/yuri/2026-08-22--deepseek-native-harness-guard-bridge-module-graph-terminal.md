# DeepSeek native Harness guard–bridge module-graph terminal

Date: 2026-08-22

Timestamp: 2026-08-22T10:27:17.1698176+10:00 (Australia/Brisbane)

Yuri attention required: **no**

## Lay summary

The one authorised test failed safely before the guard could do useful work.
The reason is precise: the guard asked for the bridge under one filename, while
the disposable test folder supplied the correct bridge under another filename.
Nothing contacted DeepSeek, a provider, the product or any data; the temporary
folder was removed and the failed attempt will not be retried.

This is a genuine step toward control rather than a reason to widen the
clockwork. It exposed one missing mechanical gear—checking that every module
import has an exact file target. The next attempt will add that deterministic
check and repeat the graph as a new, separately bounded attempt. If it passes,
we go straight to the complete package-unloaded runner rather than creating
more speculative intermediate rehearsals.

## Technical summary

- implementation source:
  `3b4fa92c737fe40990a513afa246948f1fd956a8`;
- process result: exit 1, stdout 0 bytes, stderr 938 bytes;
- retained process evidence: byte counts and SHA-256 digests only;
- root cause: guard specifier
  `./preset-mount-sanitizer-runner-bridge.mjs` did not resolve to the longer
  materialized source basename;
- process count: one Node, zero native Harness/worker/model/provider;
- retry/resume count: zero;
- focused tests before process: 23 passed;
- exact broader collection before process: 149 passed;
- register: revision 612, AER-0923 through AER-0933;
- protected refs: unchanged at
  `2e34bdad732fdab32fbf778280b3d3c70d66d602`.

## Deliberately closed

No guard-behavior, runner, installed-package, native-Harness, DeepSeek-worker,
model/provider, product/data, production, deployment, release, Pages or
protected-ref claim or authority is opened.

## Planned next tranche

`deepseek-native-harness-provider-free-guard-bridge-import-closure-recovery-rehearsal`

It will derive every relative import, require complete target closure, place
the accepted bridge bytes at the guard-owned target, and permit exactly one new
Node graph attempt with no retry.
