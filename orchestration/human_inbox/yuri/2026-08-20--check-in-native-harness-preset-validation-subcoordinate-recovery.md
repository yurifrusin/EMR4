# Native Harness preset-validation subcoordinate recovery — paired closeout

Date: 2026-08-20

Timestamp: 2026-08-20T17:18:14.3713624+10:00 (Australia/Brisbane)

## Lay summary

We now know more precisely where the Harness is going wrong. Reading the pinned
preset package directly works: it finds exactly one healthy EMR4 worker preset
and its contents are exactly right. Running the same question through the
native Harness gets as far as entering preset-row discovery, but it does not
produce the expected exact row.

This is useful because it moves the mystery away from the preset file itself
and into the Harness service path that presents presets to a runner. The one
probe was deliberately unable to start an agent or contact DeepSeek. It made no
provider or network request, retried nothing, and cleaned up completely. So it
is a Harness diagnosis, not another expensive or untraceable worker failure.

Gemini independently reviewed the exact no-agent runner before it was admitted.
The workflow clock also caught that I had advanced the active latch directly
instead of through its exclusive writer. I restored the clock-owned state and
republished the same reading correctly; this is recorded as an incident rather
than hidden. Your attention is not required.

## Technical summary

- deterministic/package source: `e013bfc0725be62c30b1af2e3ab120a3ef820616`;
- reviewed native runner: `8b42760cf68bc2fcc09432de9bd42a8d80b50317`;
- immutable terminal evidence source: `9e4d13029e4ea3eb1b511602cf52cd1c863ea69e`;
- direct package result: one healthy row, 158 bytes, exact expected digest;
- native terminal: reached `PRESET_ROW_DISCOVERY_ENTERED`, first missing
  coordinate `PRESET_ROW_FOUND`;
- native processes/retries: `1/0`;
- agents, turns, broker/model/provider/network/Docker/database counts: all `0`;
- cleanup: process and disposable root absent;
- independent review: distinct Gemini 3.7 Flash/high `pass`, twelve commands
  zero, clean unchanged HEAD;
- workflow register: revision 573, four new contained/corrected incidents,
  none open; and
- protected refs: all remain
  `2e34bdad732fdab32fbf778280b3d3c70d66d602`.

Deliberately closed: retry of the consumed process, DeepSeek or any provider
request, agent creation/mount/turn, attempt 006, database/product/API/client
work, ordinary-practice check-in, production, deployment, release, Pages and
protected-ref movement.

Next tranche:
`raisa-provider-free-check-in-native-harness-preset-row-service-path-recovery`.

The non-PHI continuing Pushover closeout notification succeeded with request
`70300a0e-15b8-4de0-b3b0-179c62faebf1`.
